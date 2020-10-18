from rest_framework.decorators import api_view
from rest_framework.response import Response

from game_board.api import utils
from game_board.avl import avl_handler as avl

from rest_framework.throttling import AnonRateThrottle
from rest_framework.throttling import UserRateThrottle
from rest_framework.decorators import throttle_classes

from .. import config

import json


@api_view(['GET'])
def api_overview(request):
    '''
    Overview of the API calls exist.

    :param request:
    :return: Response, list of API URLs.
    '''
    api_urls = {
        'Start Game'      : '/start_game/<str:difficulty>/<str:player_ids>/<str:data_structures>',
        'Game Board'      : '/board/<str:id>',
        'Re-balance Tree' : '/rebalance/<str:game_id>',
        'Action'          : '/action/<str:card>/<str:game_id>'
    }
    return Response(api_urls)


@api_view(['GET'])
@throttle_classes([AnonRateThrottle])
@throttle_classes([UserRateThrottle])
def start_game(request, difficulty, player_ids, data_structures):
    '''
    Creates a new game board.

    :param request:
    :param difficulty: game difficulty level
    :param player_ids: string of player IDs, comma seperated if more than one
    :param data_structures: string of data structures, comma seperated if more than one
    :return game board id:
    '''

    # Chosen difficulty does not exist
    if difficulty not in config.DIFFICULTY_LEVELS:
        return Response({'error': 'Difficulty level not found!',
                         'options': config.DIFFICULTY_LEVELS})

    # Convert the string fields into list. Separate by comma if provided
    player_ids = player_ids.split(',')
    data_structures = data_structures.split(',')

    # Create new game board JSON (dict), and store it in the database
    new_board = utils.new_board(difficulty, player_ids, data_structures)
    status = utils.create_board_db(new_board)

    if status['error']:
        return Response({'error': status['reason']})

    return Response({'game_id': status['game_id']})


@api_view(['GET'])
def board(request, game_id):
    '''
    Returns the current game board state.

    :param request:
    :param game_id: unique identifier of the board
    :return game board JSON:
    '''

    status = utils.load_board_db(game_id)
    if status['error']:
        return Response({'error': status['reason']})

    # hide the UID used by data structure backend from user
    del status['game_board']['graph']['uid']

    return Response(status['game_board'])


@api_view(['POST'])
def rebalance(request, game_id):
    '''
    Re-balance a un-balanced AVL tree.

    :param request:
    :param game_id: unique identifier of the board
    :return game board JSON:
    '''

    # Get the POST request
    post_request = json.loads(request.body)
    try:
        adjacency_list = post_request['adjacency_list']
    except Exception as e:
        return Response({'error': str(e)})

    # Load the game board from database
    status = utils.load_board_db(game_id)
    if status['error']:
        return Response({'error': status['reason']})
    board = status['game_board']

    #  Check for invalid action
    if board['curr_data_structure'] != 'AVL':
        return Response({'invalid_action': 'Re-balance can be performed for an AVL!'})

    check = utils.cheat_check(game_board=board, rebalance=True)
    if check['cheat']:
        return Response({'invalid_action': check['reason']})

    # Do the re-balance action and get the new state of the graph
    if board['curr_data_structure'] == 'AVL':
        graph = avl.avlRebalance(board['graph'])
    board['graph'] = graph

    # If not correct lose points
    if board['graph']['adjacency_list'] != adjacency_list:
        board['player_points'][board['turn']] -= config.LOSS[str(board['difficulty'])]

    # Change turn to next player
    next_player_index = (board['player_ids'].index(board['turn']) + 1) % len(board['player_ids'])
    board['turn'] = board['player_ids'][next_player_index]

    # Update board
    status = utils.update_board_db(board)
    if status['error']:
        return Response({'error': status['reason']})

    board = status['game_board']

    return Response(board)


@api_view(['GET'])
def action(request, card, game_id):
    '''
    Perform action on the Data Structure using a card

    :param request:
    :param card: what action to be performed
    :param game_id: unique identifier of the board
    :return game board JSON:
    '''

    # Load the game board from database
    status = utils.load_board_db(game_id)
    if status['error']:
        return Response({'error': status['reason']})
    board = status['game_board']

    # Check for invalid action
    check = utils.cheat_check(game_board=board, card=card)
    if check['cheat']:
        return Response({'invalid_action': check['reason']})

    # Give the points
    if card in config.GAIN_TIMES[board['curr_data_structure']]:
        point = board['graph']['node_points'][card.split()[1]]
        board['player_points'][board['turn']] += point

    # Perform the action on the data structure
    if board['curr_data_structure'] == 'AVL':
        graph = avl.avlAction(card, board['graph'])
    # Currently only AVL supported
    else:
        graph = avl.avlAction(card, board['graph'])

    # Update the graph with the new graph state
    board['graph'] = graph
    # Remove the played card
    board['cards'][board['turn']].remove(card)
    # Pick a new card
    board['cards'][board['turn']].append(utils.pick_a_card(board))

    # Update the board on database
    status = utils.update_board_db(board)
    if status['error']:
        return Response({'error': status['reason']})

    board = status['game_board']

    return Response(board)