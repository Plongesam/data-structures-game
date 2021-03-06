"""
    Helper functions for the Game Board API.
"""
import json
import math
import random
import uuid
from datetime import datetime
from bson import json_util

from llist_gameboard import config
from game_board import rules
from game_board.avl import avl_handler as avl
from llist_gameboard.database import game_board_db as db
from profile_page.database import profile_page_db as profile_db
from llist_gameboard.llist.llist import makeNewGame


def create_board_db(new_board):
    """
    Creates a new game board instance in the database.
    Returns the error information if fails, or the game board ID.
    If
    :param new_board: dictionary for that represents the game board state.
    :return result, {'error': bool, 'reason': string, 'game_id': string}:
    """
    result = {'error': False, 'reason': '', 'game_id': ''}

    try:
        game_id = db.create_game(new_board)

        if game_id == "nah bro idk about it":
            result['error'] = True
            result['reason'] = "Game Already Exist!"
            return result

        result['game_id'] = json.loads(json_util.dumps(game_id))

    except Exception as err:
        result['error'] = True
        result['reason'] = str(err)

        return result

    return result


def update_board_db(board, user_id='-1', token='-1'):
    """
    Update the game board in the database with the new state.
    Returns the board itself unless the game ended.
    If the game ended, then it changes the <end_game> field,
    and deletes the game from database. Otherwise, changes
    turn to the next player.
    :param board: game board
    :param user_id: username
    :param token: authentication token
    :return result, {'error': bool, 'reason': string, 'game_board': dict}:
    """
    result = {'error': False, 'reason': '', 'game_board': board}

    try:

        if board['curr_data_structure'] == 'AVL':
            # Game ended
            if (board['graph']['root_node'] == board['graph']['gold_node'] or
                    len(board['deck']) == 0):

                # update the board
                board['end_game'] = True
                board['turn'] = max(board['player_points'], key=board['player_points'].get)  # get player w/ max points
                result['game_board'] = board

                # if user is authenticated
                if user_id not in ['-1', -1, ''] and token not in ['-1', -1, '']:

                    # check if the game is being loaded from profile page
                    if 'profile_load' in list(board.keys()) and board['profile_load'] is False:

                        # Here check if user_id matches the token with the database
                        if profile_db.check_user(user_id, token):
                            # Currently error return if user is not authenticated is disabled
                            # It just not updates the score
                            #result['error'] = True
                            #result['reason'] = "User is not authenticated"
                            #return result

                            # if the user is in part of the players (paranoid check)
                            if str(user_id) in board['player_ids']:

                                # if not negative points
                                if board['player_points'][str(user_id)] > 0:

                                    # get user's current points
                                    curr_points = profile_db.get_points(str(user_id))

                                    # get the target points
                                    if user_id == board['turn']:
                                        # if the user is the winner, double the points
                                        target_points = curr_points + (math.log(board['player_points'][str(user_id)]) * 2)
                                    else:
                                        # don't double the points if the user is not the winner
                                        target_points = curr_points + math.log(board['player_points'][str(user_id)])

                                    # set the new points
                                    profile_db.set_points(str(user_id), target_points)

                # remove the game from the database
                db.remove_game(board['game_id'])

            # Game continues
            else:
                _ = db.update_game(board['game_id'], board)

                # hide the UID used by data structure backend from user
                # del board['graph']['uid']

                # Update
                result['game_board'] = board

        else:
            _ = db.update_game(board['game_id'], board)

            # hide the UID used by data structure backend from user
            # del board['graph']['uid']

            # Update
            result['game_board'] = board

    except Exception as err:
        result['error'] = True
        result['reason'] = str(err)
        return result

    return result


def load_board_db(game_id):
    """
    Loads the game board state from the database by its ID.
    :param game_id: board's ID
    :return: game board
    """
    result = {'error': False, 'reason': '', 'game_board': {}}

    try:
        game_board = db.read_game(str(game_id))
        if game_board == "nah bro idk about it":
            result['error'] = True
            result['reason'] = "Game Not Found!"
            return result

        # Serialize the JSON object
        game_board = json.loads(json_util.dumps(game_board))
        result['game_board'] = game_board

        # Remove the database entry ID from user's view
        del game_board['_id']

    except Exception as err:
        result['error'] = True
        result['reason'] = str(err)
        return result

    return result


def new_board(difficulty, player_ids, data_structures):
    """
    Forms the JSON format for the game board state.
    :param difficulty: difficulty of the game
    :param player_ids: list of player ids
    :param data_structures: list of data structures
    :return: game board dict
    """

    # if it is an AVL
    if data_structures[0] == 'AVL':
        graph = avl.avlNew(config.HEIGHT[str(difficulty)], config.POINTS[str(difficulty)]['max'])
        deck = create_card_deck(list(graph['node_points'].keys()), data_structures[0], difficulty, graph['gold_node'])
        cards, deck = distribute_cards(player_ids, deck)
        # real_players = [player for player in player_ids if not player.lower().startswith(config.BOT_NAME_PREFIX)]
        board = {
            'game_id': str(uuid.uuid1()),
            'graph': graph,
            'player_ids': player_ids,
            'player_names': [''],
            'player_points': {str(id): 0 for id in player_ids},
            'turn': random.choice(player_ids),
            'deck': deck,
            'cards': cards,
            'difficulty': difficulty,
            'num_players': len(player_ids),
            'curr_data_structure': data_structures[0],
            'end_game': False,
            'time_created': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            # Below features are left out for future sprints
            # 'selected_data_structures': data_structures,
            # 'timed_game': False,
            # 'seconds_until_next_ds': 60,
            'online': False,
            'profile_load': False
        }
    # Currently only gives AVL however, this will be for linked list game mode
    else:
        # graph = avl.avlNew(config.HEIGHT[str(difficulty)], config.POINTS[str(difficulty)])
        # this will be replaced when I have the llist_handler class

        graph = makeNewGame()

        board = {
            'game_id': str(uuid.uuid1()),
            'graph': graph,
            'queen_at_head': True,
            'colony_exit': False,
            'colony_entrance': False,
            'total_chambers': 1,
            'total_tunnels': 0,
            'total_food': config.INIT_NUM_FOOD,
            'total_food_types': {
                'crumb': 1,
                'berry': 1,
                'donut': 1,
            },
            'time_tracks': {
                'move/forage': 36,
                'dig_tunnel_track': 36, #changing to 36 so that we can make more moves in the demo
                'dig/fill_chamber': 36,
            },
            'total_ants': 1,
            'total_surface_ants': 1,
            'total_under_attack': 0,
            'curr_day': 1,
            'player_ids': player_ids,
            'difficulty': difficulty,
            'num_players': 1,
            'curr_data_structure': data_structures[0],
            'end_game': False,
            'time_created': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'online': False,
            'profile_load': False,
        }

    return board


def cheat_check(game_board, card=-1, rebalance=False):
    """
    Validates the attempted action by the rules defined in rules.py
    :param game_board: game board JSON (dict), game state
    :param card: string that represents the action that is attempted to play
    :param rebalance: True if check is being done for re-balance attempt
    :return: {'cheat': bool, 'reason': string}
    """
    # General game rules
    check = rules.general(game_board, card)
    if check['cheat']:
        return check

    # AVL specific game rules
    if game_board['curr_data_structure'] == 'AVL':
        check = rules.AVL(game_board, rebalance)
        if check['cheat']:
            return check

    # No cheat detected
    return {'cheat': False}


def create_card_deck(nodes, data_structure, difficulty, gold_node):
    """ Creates a deck of cards that will be drawn from for the duration of the game.
    :param nodes: nodes in the data structure
    :param data_structure: type of data structure
    :param difficulty: difficulty level of the game
    :param gold_node: which node is the golden node
    :return: list of cards that can be played in the current game
    """
    # Minimum and maximum possible node value
    min_point = config.POINTS[str(difficulty)]['min']
    max_point = config.POINTS[str(difficulty)]['max']
    card_diversity = list(range(min_point, max_point + 1))

    # Card types for the DS
    card_types = config.CARDS[str(data_structure)]

    # Remove the golden node from node options so it doesn't get deleted
    nodes.remove(gold_node)

    # generate the deck of cards
    cards = list()
    for _ in range(config.CARDS_IN_DECK[str(difficulty)]):

        # can not pick node dependent action anymore (run out of all nodes)
        if len(nodes) == 0:
            card_types = [action for action in card_types if "node#" not in action]

        # pick a new card
        picked_card = random.choice(card_types)

        # node specific action (For example: Delete node#)
        if 'node#' in picked_card:

            # choose from existing nodes
            node_choice = str(random.choice(nodes))
            cards.append(picked_card.replace('node#', node_choice))

            # remove the node from options
            nodes.remove(node_choice)

        # point dependent action (For example: Insert #)
        else:
            if card_diversity:  # try to make the cards a little more distinct
                selected_value = random.choice(card_diversity)
                card_diversity.remove(selected_value)
                cards.append(picked_card.replace('#', str(selected_value)))
            else:
                cards.append(picked_card.replace('#', str(random.randint(min_point, max_point))))

    # Shuffle the deck of cards
    random.shuffle(cards)
    return cards


def distribute_cards(player_ids, deck):
    """
    Simulates the distribution of deck of cards to the players.
    :param player_ids: list of players in the game by their ID
    :param deck: the deck of available cards
    :return: dictionary of cards assigned to each player
    :return: updated deck
    """
    board_cards = dict()

    # pick cards for each player
    for player in player_ids:

        # assign the cards to the player
        player_cards = list()
        for _ in range(config.CARDS_PER_PLAYER):
            player_cards.append(deck.pop())

        board_cards[str(player)] = player_cards

    return board_cards, deck


def ai_format_hands(board):
    """ Create a formatted version of board[cards] that the AI can use.
    Order is preserved such that player of key '0' is the maximizer and key '1' through 'num_players - 1'
    are players that will go next (in order)
    :param board: the game board as given by database
    :return ordered_hands: the ordered dict (starting from the current player, ie the maximizer)
    """

    ordered_hands = dict()
    next_player_index = board['player_ids'].index(board['turn'])
    next_player = board['player_ids'][next_player_index]

    count = 0
    while True:
        if count == len(board['player_ids']):
            break
        ordered_hands[count] = board['cards'][next_player]
        next_player_index = (next_player_index + 1) % len(board['player_ids'])
        next_player = board['player_ids'][next_player_index]
        count += 1

    return ordered_hands


def win_state_llist(board):
    """Takes the state of the current linked list game and determines if the player has won. Returns true if the game
    has been won, and false otherwise."""
    if len(board['graph']['chambers']) >= 10 and enough_food_to_win(board['graph']) and \
            (True not in board['graph']['under_attack'].values()):
        return not lose_state_llist(board)
    else:
        return False


def lose_state_llist(board):
    """Takes the state of the current linked list game and determines if the player has lost. Returns true if the game
    is lost and false otherwise"""
    if not board['queen_at_head']:
        return True
    else:
        for chamber in board['graph']['chambers']:
            if (board['graph']['tunnels'][chamber][1] != 'surface') or (board['graph']['tunnels'][chamber][1]
                                                                        not in board['graph']['chambers']):
                return True
        return False


def enough_food_to_win(graph):
    if len(graph['chambers']) < 10:
        return False
    else:
        full_chambers = 0
        for i in graph['chambers']:
            foodcount = 1 * graph['food'][i]['crumb'] + 2 * graph['food'][i]['berry'] + 3 * graph['food'][i]['donut']
            if foodcount >= 3:
                full_chambers += 1
        return full_chambers >= 10