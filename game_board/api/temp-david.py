"""
    API for Game Board that allows interaction with boards.
"""
import json
import random
from time import sleep
import uuid
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle
from rest_framework.throttling import UserRateThrottle
from rest_framework.decorators import throttle_classes
from game_board.api import utils
from .. import config



@api_view(['GET'])
def api_overview(request):
    """
    Overview of the API calls exist.

    :param request:
    :return: Response, list of API URLs.
    """
    api_urls = {
        'Start Game': '/start_game/<str:difficulty>/<str:player_ids>/<str:data_structures>',
        'Game Board': '/board/<str:id>',
        'Spawn Ant': '/spawn_ant/<str:game_id>',
    }
    return Response(api_urls)


@api_view(['GET'])
@throttle_classes([AnonRateThrottle])
@throttle_classes([UserRateThrottle])
def start_game(request, difficulty, player_ids, data_structures):
    """
    Creates a new game board.

    :param request:
    :param difficulty: game difficulty level
    :param player_ids: string of player IDs, comma seperated if more than one
    :param data_structures: string of data structures, comma seperated if more than one
    :return game board id:
    """

    # Chosen difficulty does not exist
    if difficulty not in config.DIFFICULTY_LEVELS:
        return Response({'error': 'Difficulty level not found!',
                         'options': config.DIFFICULTY_LEVELS},
                        status=status.HTTP_400_BAD_REQUEST)

    # Convert the string fields into list. Separate by comma if provided
    player_ids_temp = player_ids.split(',')
    data_structures = data_structures.split(',')

    player_ids = list()
    for pl_id in player_ids_temp:
        pl_id = str(pl_id).strip()

        # If empty player_ids is passed
        if len(pl_id) == 0:
            random_player = 'RedPanda_' + str(uuid.uuid1())[:5]
            while random_player in player_ids:
                random_player = 'RedPanda_' + str(uuid.uuid1())[:5]
            player_ids.append(random_player)
        else:
            player_ids.append(pl_id)


    # Check if the number of players request is valid
    if len(player_ids) > config.LLIST_MAX_NUM_PLAYERS:
        return Response({'error': 'Too many players requested!',
                         'options': config.LLIST_MAX_NUM_PLAYERS},
                        status=status.HTTP_400_BAD_REQUEST)

    # Create new game board JSON (dict), and store it in the database
    new_board = utils.new_board(difficulty, player_ids, data_structures)
    response_status = utils.create_board_db(new_board)

    if response_status['error']:
        return Response({'error': response_status['reason']},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'game_id': response_status['game_id']})




@api_view(['GET'])
def board(request, game_id):
    """
    Returns the current game board state. 

    :param request:
    :param game_id: unique identifier of the board
    :return game board JSON:
    """

    response_status = utils.load_board_db(game_id)
    if response_status['error']:
        return Response({'error': response_status['reason']},
                        status=status.HTTP_400_BAD_REQUEST)

    # hide the UID used by data structure backend from user
    # del response_status['game_board']['graph']['uid']

    return Response(response_status['game_board'])

@api_view(['GET'])
def dig_tunnel(request, game_id, origin, destination):
    """
    Attempts to dig a tunnel from the requested chamber to a requested destination
    :param game_id: unique identifier of the board
    :param origin: the chamber that the player wishes to dig from
    :param destination: the place that the player wishes to dig to (chamber name, 'surface', or 'none'
    """
    # Game must exist
    # Load the game board from database
    response_status = utils.load_board_db(game_id)
    if response_status['error']:
        return Response({'error': response_status['reason']},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    board = response_status['game_board']

    # origin and destination MUST be different
    if origin is destination:
        return Response({'invalid_action': 'origin cannot match destination'},
                        status=status.HTTP_400_BAD_REQUEST)

    # Player must still have dig 'energy' for that day
    if board['time_tracks']['dig_tunnel_track'] == 0:
        return Response({'invalid_action': 'no more dig tunnel moves left!'},
                        status=status.HTTP_400_BAD_REQUEST)
    # Origin must exist
    if origin is not 'surface' and origin not in board['graph']['chamber_list']:
        return Response({'invalid_action': 'origin does not exist'},
                        status=status.HTTP_400_BAD_REQUEST)

    # If destination is NOT 'none', it must exist (chamber OR surface)
    if destination is not 'none' and destination not in board['graph']['chamber_list']:
        return Response({'invalid_action': 'destination does not exist'},
                        status=status.HTTP_400_BAD_REQUEST)

    # If Origin is surface, colony_entrance MUST be False
    if origin is 'surface' and board['colony_entrance'] is True:
        return Response({'invalid_action': 'colony_entrance already exists'},
                        status=status.HTTP_400_BAD_REQUEST)

    # There must be at least one ant at origin
    if origin is 'surface' and board['total_surface_ants'] == 0:
        return Response({'invalid_action': 'no ants on surface'},
                        status=status.HTTP_400_BAD_REQUEST)
    if board['graph']['num_ants'][origin] == 0:
        return Response({'invalid_action': 'no ants at origin'},
                        status=status.HTTP_400_BAD_REQUEST)

    # If destination is NOT none, there must be an ant at the destination
    if destination is not 'none' and board['graph']['num_ants'][destination] == 0:
        return Response({'invalid_action': 'no ants at destination'},
                        status=status.HTTP_400_BAD_REQUEST)

    # Origin chamber must NOT already have an exit tunnel
    if board['graph']['num_tunnels'][origin]['exit'] is True:
        return Response({'invalid_action': 'exit tunnel exists'},
                            status=status.HTTP_400_BAD_REQUEST)

    # destination must NOT already have an entrance tunnel
    if destination is not 'none' and board['graph']['num_tunnels'][destination]['entrance'] is True:
        return Response({'invalid_action': 'exit tunnel exists'},
                            status=status.HTTP_400_BAD_REQUEST)

    # if ALL checks are passed, create new tunnel and update ALL relevant gameboard parameters

    # num_tunnels
    board['graph']['num_tunnels'][origin]['exit'] = True
    board['graph']['num_tunnels'][origin]['next'] = destination
    if destination is not 'none':
        board['graph']['num_tunnels'][destination]['entrance'] = True


    if origin is 'surface':
        board['colony_entrance'] = True
    if destination is 'surface':
        board['colony_exit'] = True

    board['time_tracks']['dig_tunnel_track'] -= 1

    user_id = board['player_ids']
    token = -1

    # Update the board on database
    response_status = utils.update_board_db(board, user_id, token)
    if response_status['error']:
        return Response({'error': response_status['reason']},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    board_response = response_status['game_board']
    return Response(board_response)

@api_view(['GET'])
def dig_chamber(request, game_id, origin, move_ant):
    """
    Attempts to dig a new chamber off of a current dead-end tunnel
    :param game_id: unique identifier of the board
    :param origin: the chamber that the player wishes to dig from
    :param move_ant: whether the player wishes to move the ant into the new chamber
    """
    # checklist

    # Check if game exists
    response_status = utils.load_board_db(game_id)
    if response_status['error']:
        return Response({'error': response_status['reason']},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    board = response_status['game_board']

    # Check for dig chamber energy
    if board['time_tracks']['dig/fill_chamber'] == 0:
        return Response({'invalid_action': 'no more dig chamber moves left!'},
                        status=status.HTTP_400_BAD_REQUEST)

    # Check if move_ant is a valid input
    if move_ant is not 'yes':
        if move_ant is not 'no':
            return Response({'invalid_action': 'invalid free move request!'},
                            status=status.HTTP_400_BAD_REQUEST)

    # Check if origin exists
    if origin is not 'surface' and origin not in board['graph']['chamber_list']:
        return Response({'invalid_action': 'origin does not exist'},
                        status=status.HTTP_400_BAD_REQUEST)

    # check if origin contains at least one ant
    if origin is 'surface' and board['total_surface_ants'] == 0:
        return Response({'invalid_action': 'no ants on surface'},
                        status=status.HTTP_400_BAD_REQUEST)
    if board['graph']['num_ants'][origin] == 0:
        return Response({'invalid_action': 'no ants at origin'},
                        status=status.HTTP_400_BAD_REQUEST)

    # Check if origin contains an exit tunnel
    if board['graph']['num_tunnels'][origin]['exit'] is False:
        return Response({'invalid_action': 'no available tunnel from origin'},
                        status=status.HTTP_400_BAD_REQUEST)
    # if origin contains a next tunnel, check if current next is 'none'
    if board['graph']['num_tunnels'][origin]['next'] is not 'none':
        return Response({'invalid_action': 'no available tunnel from origin'},
                        status=status.HTTP_400_BAD_REQUEST)


    # if at this point, dig request is valid: update ALL relevant game board variables
    board['total_chambers'] += 1
    chamber_number = str(board['total_chambers'])
    chamber_id = "chamber" + chamber_number

    board['graph']['chamber_list'].append(chamber_id)

    board['graph']['num_tunnels'][chamber_id]['entrance'] = True
    board['graph']['num_tunnels'][chamber_id]['exit'] = False
    board['graph']['num_tunnels'][chamber_id]['next'] = 'none'
    board['graph']['num_tunnels'][chamber_id]['prev'] = origin

    board['graph']['num_food'][chamber_id] = 0

    if move_ant is 'yes':
        board['graph']['num_ants'][chamber_id] = 1
        if origin is not 'surface':
            board['graph']['num_ants'][origin] -= 1
        else:
            board['total_surface_ants'] -= 1

    board['time_tracks']['dig/fill_chamber'] -= 1


    user_id = board['player_ids']
    token = -1
    # Update the board on database
    response_status = utils.update_board_db(board, user_id, token)
    if response_status['error']:
        return Response({'error': response_status['reason']},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    board_response = response_status['game_board']
    return Response(board_response)


@api_view(['GET'])
def fill_chamber(request, game_id, to_fill):
    """
    Attempts to 'fill' (delete) a chamber and all associated tunnels
    :param game_id: unique identifier of the board
    :param to_fill: the chamber that the player wishes to delete
    :return game board JSON:
    """

    # Check if game exists
    # Load the game board from database
    response_status = utils.load_board_db(game_id)
    if response_status['error']:
        return Response({'error': response_status['reason']},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    board = response_status['game_board']

    # Check if to_fill is surface (cannot fill in surface)
    if to_fill is 'surface':
        return Response({'invalid_action': 'cannot fill in surface'},
                        status=status.HTTP_400_BAD_REQUEST)
    # Check if to_fill exists
    if to_fill not in board['graph']['chamber_list']:
        return Response({'invalid_action': 'chamber does not exist'},
                        status=status.HTTP_400_BAD_REQUEST)

    # Check for fill chamber energy
    if board['time_tracks']['dig/fill_chamber'] == 0:
        return Response({'invalid_action': 'no more fill chamber moves left!'},
                        status=status.HTTP_400_BAD_REQUEST)

    # Check if to_fill has any food in it
    if board['graph']['num_food'][to_fill] != 0:
        return Response({'invalid_action': 'There is food in this chamber!'},
                        status=status.HTTP_400_BAD_REQUEST)
    # Check if there is at least one ant at the prev chamber
    previous = board['graph']['num_tunnels'][to_fill]['prev']
    if board['graph']['num_ants'][previous] == 0:
        return Response({'invalid_action': 'No ant in previous chamber!'},
                        status=status.HTTP_400_BAD_REQUEST)

    # Check if there is a next chamber, and if so, if there is at least one ant in it
    if board['graph']['num_tunnels'][to_fill]['next'] is not 'none':
        next_chamber = board['graph']['num_tunnels'][to_fill]['next']
        if board['graph']['num_ants'][next_chamber] == 0:
            return Response({'invalid_action': 'No ant in next chamber!'},
                            status=status.HTTP_400_BAD_REQUEST)

    # If at this point, all checks are made. Update gameboard
    # link up prev and next
    if board['graph']['num_tunnels'][to_fill]['next'] is not 'none':
        next_chamber = board['graph']['num_tunnels'][to_fill]['next']
        board['graph']['num_tunnels'][previous]['next'] = next_chamber
        board['graph']['num_tunnels'][next_chamber]['prev'] = previous
    else:
        board['graph']['num_tunnels'][previous]['next'] = 'none'
    # Delete to_fill
    board['graph']['chamber_list'].remove(to_fill);
    del board['graph']['num_tunnels'][to_fill]
    del board['graph']['num_food'][to_fill]
    del board['graph']['num_ants'][to_fill]
    del board['graph']['under_attack'][to_fill]

    board['total_chambers'] -= 1
    board['time_tracks']['dig/fill_chamber'] -= 1

    user_id = board['player_ids']
    token = -1
    # Update the board on database
    response_status = utils.update_board_db(board, user_id, token)
    if response_status['error']:
        return Response({'error': response_status['reason']},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    board_response = response_status['game_board']
    return Response(board_response)

##### NOTE: THIS IMPLEMENTATION WILL LIKELY CHANGE IN THE NEAR FUTURE
    #       HOWEVER, GENERAL LOGIC SHOULD STAY THE SAME
# @api_view(['GET'])
# def move_ant(request, game_id, origin):
    """
    Spawns an ant given the game ID
    :param game_id: unique identifier of the board
    :param origin: identifier of an ant on the board
    :return game board JSON:
    """

    # Checklist
    # Check if game exists
    # Check if origin exists
    # Check if ant exists in origin
    # Check if origin has an exit tunnel
    #   if so, check if origin's exit tunnel leads to a valid destination
    # Check if destination chamber is under attack
    #   if so, check to see if ant is carrying food (cannot bring food into attacked chamber)

    # At this point, requested move is valid. Update ALL related gameboard values and return

@api_view(['GET'])
def spawn_ant(request, game_id):
    """
    Spawns an ant given the game ID
    :param game_id: unique identifier of the board
    :return game board JSON:
    """

    # Load the game board from database
    response_status = utils.load_board_db(game_id)
    if response_status['error']:
        return Response({'error': response_status['reason']},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    board = response_status['game_board']


    if not board['queen_at_head']:
        return Response({'invalid_action': 'lost queen'},
                        status=status.HTTP_400_BAD_REQUEST)

    # Make sure there is enough food to spawn a new ant
    if board['total_food'] < config.ANT_SPAWN_VAL:
        return Response({'invalid_action': 'not enough food'},
                        status=status.HTTP_400_BAD_REQUEST)


    # Take away food, if they have food that can be
    curr_food_types = board['total_food_types']

    # If player has a donut take it
    if curr_food_types[config.FORAGE_TYPES[2]] > 0:
        board['total_food_types'][config.FORAGE_TYPES[2]] -= 1
        board['total_food'] -= config.ANT_SPAWN_VAL
    # If player has at least one berry and one crumb, take one of each
    elif curr_food_types[config.FORAGE_TYPES[1]] > 0 and curr_food_types[config.FORAGE_TYPES[0]] > 0:
        board['total_food_types'][config.FORAGE_TYPES[1]] -= 1
        board['total_food_types'][config.FORAGE_TYPES[0]] -= 1
        board['total_food'] -= config.ANT_SPAWN_VAL
    # If player only has crumbs take it
    elif curr_food_types[config.FORAGE_TYPES[0]] >= config.ANT_SPAWN_VAL:
        board['total_food_types'][config.FORAGE_TYPES[0]] -= config.ANT_SPAWN_VAL
    # If this case is reached, the player has enough food, but only in berry form (not divisible by 3)
    elif curr_food_types[config.FORAGE_TYPES[1]] >= 2:
        board['total_food_types'][config.FORAGE_TYPES[1]] -= 2
        board['total_food_types'][config.FORAGE_TYPES[0]] += 1;
        board['total_food'] -= config.ANT_SPAWN_VAL
    else:
        return Response({'invalid_action': 'error occurred'},
                        status=status.HTTP_400_BAD_REQUEST)

    # if control reaches here, then spawning an ant is successful. Update both total and surface ant values.
    board['total_ants'] += 1
    board['total_surface_ants'] += 1

    user_id = board['player_ids']
    token = -1
    # Update the board on database
    response_status = utils.update_board_db(board, user_id, token)
    if response_status['error']:
        return Response({'error': response_status['reason']},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    board_response = response_status['game_board']
    return Response(board_response)

