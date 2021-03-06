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
def forage(request, game_id, difficulty, dest):
    """
    Spawns an ant given the game ID

    :param game_id: unique identifier of the board
    :param difficulty: game difficulty
    :param ant_loc: the chamber in which the ant is located
    :param dest: the chamber where the food should be placed
    :return game board JSON:
    """

    # Load the game board from database
    response_status = utils.load_board_db(game_id)
    if response_status['error']:
        return Response({'error': response_status['reason']},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    board = response_status['game_board']

    # If there are no chambers player can't forage
    if board['total_chambers'] == 0:
        return Response({'invalid_action': 'no chambers'},
                        status=status.HTTP_400_BAD_REQUEST)

    # If there is no queen then game over actually
    if !board['queen_at_head']:
        return Response({'invalid_action': 'lost queen'},
                        status=status.HTTP_400_BAD_REQUEST)

    # If there are no worker ants on the surface.
    if board['total_surface_ants'] == 1:
        return Response({'invalid_action': 'no surface ants'},
                        status=status.HTTP_400_BAD_REQUEST)

    # If the requested chamber is under attack return error
    if board['graph']['under_attack'][dest]:
        return Response({'invalid_action': 'under attack'},
                        status=status.HTTP_400_BAD_REQUEST)

    # If the player can't make a forage move, return error
    if board['time_tracks']['move/forage'] == 0:
        return Response({'invalid_action': 'cant forage'},
                        status=status.HTTP_400_BAD_REQUEST)

    # choose a random number then choose the forage type that will be returned
    rand_food = random.randint(0, 100)
    crumb_chance = config.FORAGE_CHANCE[difficulty][config.FORAGE_TYPES[0]]
    berry_chance = config.FORAGE_CHANCE[difficulty][config.FORAGE_TYPES[1]]
    donut_chance = config.FORAGE_CHANCE[difficulty][config.FORAGE_TYPES[2]]
    attack_chance = config.FORAGE_CHANCE[difficulty][config.FORAGE_TYPES[3]]

    # Check if crumb was chosen
    if rand_food >= 0 and rand_food < crumb_chance:
        forage_result = config.FORAGE_TYPES[0]

    # Check if berry was chosen
    if rand_food >= crumb_chance and rand_food < berry_chance:
        forage_result = config.FORAGE_TYPES[1]

    # Check if donut was chosen
    if rand_food >= berry_chance and rand_food < donut_chance:
        forage_result = config.FORAGE_TYPES[2]

    # Check if attack was chosen
    if rand_food >= donut_chance and rand_food < attack_chance:
        forage_result = config.FORAGE_TYPES[3]

    # If the forage resulted in the chamber coming under attack,
    # Then reflect the change in the board
    if forage_result == config.FORAGE_TYPES[3]:
        board['graph']['under_attack'][dest] = True
        board['total_under_attack'] += 1
        board['total_surface_ants'] -= 1
        board['graph']['num_ants'][dest] += 1

    # Otherwise, put the food in the requested chamber, move the ant, and update the board
    else:
        # Change food in requested chamber
        board['graph']['num_food'][dest][forage_result] += 1
        board['graph']['num_food'][dest]['total'] += config.FOOD_VALUE[forage_result]

        # Change food stats on for the game board
        board['total_food_types'][forage_result] += 1
        board['total_food'] += config.FOOD_VALUE[forage_result]

        # Move the ant from og spot to new spot
        board['total_surface_ants'] -= 1
        board['graph']['num_ants'][dest] += 1

    # Decrement Move/Forage time track
    board['time_tracks']['move/forage'] -= 1

    user_id = board['player_ids']
    token = -1
    # Update the board on database
    response_status = utils.update_board_db(board, user_id, token)
    if response_status['error']:
        return Response({'error': response_status['reason']},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    board_response = response_status['game_board']
    return Response(board_response)


