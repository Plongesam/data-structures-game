"""
Allows the game data to be stored, and interacted with through the Pandamic game API
"""

import os
import datetime as dt
from pymongo import MongoClient

# Gets database & it's authorization from the environment
DATABASE_URL1 = os.environ.get('DATABASE_URL1')
client = MongoClient(DATABASE_URL1)

def create_game(board):
    """
    Saves a new game into the database after being passed through the Django API

    Parameters:
    board (dictionary): cornicopia of game information such as current graph, players,
                    turn data, and time data

    Returns:
    On Success:
        str: unique identification for the game
    On Fail:
        str: friendly response to inform of an error
    """
    game_id = board["game_id"]
    user_list = board["player_ids"]
    returned_data = client.InitialDB.Active_Games.find_one({"game_id": game_id})
    
    if returned_data is None:

        #Remove the players from the lobby
        for curr_id in user_list:
            client.InitialDB.Lobby.find_one_and_delete({"user_id": curr_id})

        client.InitialDB.Active_Games.insert_one(board)
        return game_id

    return 'nah bro idk about it'

def update_game(game_id: str, board):
    """
    Finds an active game in the Database and updates the values to reflect players'
    in-game decisions

    Parameters:
    game_id (str): unique identification for the game
    board (dictionary): cornicopia of game information such as current graph, players,
                    turn data, and time data
    Returns:
    On Success:
        dictionary: original game document
    On Fail:
        str: friendly response to infrom of an error
    """
    value_returned = client.InitialDB.Active_Games.find_one_and_replace({"game_id": game_id}, board)

    if value_returned is None:
        return 'nah bro idk about it'

    return value_returned

def read_game(game_id: str):
    """
    Allows an active game to be extracted from the database and passed back to the API

    Parameters:
    game_id (str): unique identification for the game

    Returns:
    On Success:
        dictionary: an active game document
    On Fail:
        str: friendly response to inform of an error
    """

    value_returned = client.InitialDB.Active_Games.find_one({"game_id": game_id})

    if value_returned is None:
        return 'nah bro idk about it'

    return value_returned

def remove_game(game_id: str):
    """
    Allows an active game to be located and then deleted from the database

    Parameters:
    game_id (str): unique identification for the game

    Returns:
    On Success:
        int: number of deleted game documents
    On Fail:
        str: friendly response to inform of an error
    """
    value_returned = client.InitialDB.Active_Games.delete_one({"game_id": game_id}).deleted_count

    if value_returned == 0:
        return 'nah bro idk about it'

    return value_returned

def list_games():
    """
    Allows unique ids of all active games to be passed back to the API

    Parameters:
    None

    Returns:
        cursor: to iterate game ids
    """
    return client.InitialDB.Active_Games.find({},{'_id':0, 'game_id': 1})

def purge_old_games():
    """
    Checks the datetime of games, deletes anything older than 1 day

    Parameters:
    None

    Returns:
        int: 0
    """
    yesterday = (dt.datetime.now() - dt.timedelta(days=1))

    mongo_cursor = client.InitialDB.Active_Games.find({},{'_id':0, 'game_id': 1, 'time_created':1})

    for game in mongo_cursor:
        try:
            game_date = game['time_created']
            game_datetime_obj = dt.datetime.strptime(game_date,"%d/%m/%Y %H:%M:%S")
            if game_datetime_obj < yesterday:
                remove_game(game['game_id'])
        except:
            pass
    return 0
