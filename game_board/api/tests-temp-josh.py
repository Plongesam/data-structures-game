from time import sleep
import random
import string
import json
from django.test import TestCase
from game_board import config
from game_board.database import game_board_db as db


class BColors:
    """Colors for printing"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class APIOverview(TestCase):
    """Tests calls related to the overview of the API."""

    def test_index_loads_properly(self):
        """The index page loads properly"""

        response = self.client.get('')
        self.assertEqual(response.status_code, 200, msg=f'{BColors.FAIL}\t[-]\tResponse was not 200!{BColors.ENDC}')
        print(f"{BColors.OKGREEN}\t[+]\tPass return code api_overview.{BColors.ENDC}")


class GameActions(TestCase):
    """Tests the API calls that is related to starting games."""

    def test_spwan_ant(self):
        # create a new game
        created_game = self.client.get('/game_board/llist_api/start_game/Easy/ID1lltest/LLIST')
        # load the game
        response = self.client.get('/game_board/llist_api/board/' + str(created_game.data['game_id']))
        # call spawn ant function THIS WILL FAIL UNTIL I MEET WITH DAVID
        response = self.client.get('/game_board/llist_api/spawn_ant/' + str(response.data['game_id']))

        board = response.data
        # make sure there was no error
        self.assertNotEqual(response.status_code, 400, msg=f'{BColors.FAIL}\t[-]\tResponse was 400!{BColors.ENDC}')
        print(f"{BColors.OKGREEN}\t[+]\tPass returning the correct response code.{BColors.ENDC}")

        # Check to make sure first spawn worked
        self.assertEqual(board['total_food'], 3, msg=f'{BColors.FAIL}\t[-]\tFood was '+board['total_food']+' not 3!{BColors.ENDC}')
        self.assertEqual(board['total_food_types']['crumb'], 1, msg=f'{BColors.FAIL}\t[-]\tcrumb was not 1!{BColors.ENDC}')
        self.assertEqual(board['total_food_types']['berry'], 1, msg=f'{BColors.FAIL}\t[-]\tberry was not 1!{BColors.ENDC}')
        self.assertEqual(board['total_food_types']['donut'], 0, msg=f'{BColors.FAIL}\t[-]\tdonut was not 0!{BColors.ENDC}')
        print(f"{BColors.OKGREEN}\t[+]\tPass spawning first ant.{BColors.ENDC}")


        response = self.client.get('/game_board/llist_api/spawn_ant/' + str(response.data['game_id']))

        board = response.data
        # make sure there was no error
        self.assertNotEqual(response.status_code, 400, msg=f'{BColors.FAIL}\t[-]\tResponse was 400!{BColors.ENDC}')
        print(f"{BColors.OKGREEN}\t[+]\tPass returning the correct response code.{BColors.ENDC}")

        # Check to make sure first spawn worked
        self.assertEqual(board['total_food'], 0, msg=f'{BColors.FAIL}\t[-]\tFood was '+board['total_food']+' not 0!{BColors.ENDC}')
        self.assertEqual(board['total_food_types']['crumb'], 0, msg=f'{BColors.FAIL}\t[-]\tcrumb was not 0!{BColors.ENDC}')
        self.assertEqual(board['total_food_types']['berry'], 0, msg=f'{BColors.FAIL}\t[-]\tberry was not 0!{BColors.ENDC}')
        self.assertEqual(board['total_food_types']['donut'], 0, msg=f'{BColors.FAIL}\t[-]\tdonut was not 0!{BColors.ENDC}')
        print(f"{BColors.OKGREEN}\t[+]\tPass spawning second ant.{BColors.ENDC}")


        response = self.client.get('/game_board/llist_api/spawn_ant/' + str(response.data['game_id']))

        board = response.data
        # make sure there was no error
        self.assertEqual(response.status_code, 400, msg=f'{BColors.FAIL}\t[-]\tResponse was not 400!{BColors.ENDC}')
        print(f"{BColors.OKGREEN}\t[+]\tPass not making an ant when out of food.{BColors.ENDC}")

        # remove the created game
        sleep(0.2)
        db.remove_game(created_game.data['game_id'])
