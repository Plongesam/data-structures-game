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
        print(f"{BColors.OKGREEN}\t[api_overview]\tPass return code api_overview.{BColors.ENDC}")


class StartGame(TestCase):
    """Tests the API calls that is related to starting games."""

    def test_invalid_api_request(self):
        """Invalid API request fields"""

        # Test non existing difficulty level
        response = self.client.get('/game_board/llist_api/start_game/Super Easy/ID1/LLIST')

        self.assertEqual(response.status_code, 400, msg=f'{BColors.FAIL}\t[-]\tResponse was not 400!{BColors.ENDC}')
        print(f"{BColors.OKGREEN}\t[start_game]\tPass returning the correct response code.{BColors.ENDC}")

        self.assertEqual(response.data, {'error': 'Difficulty level not found!',
                                         'options': config.DIFFICULTY_LEVELS},
                         msg=f'{BColors.FAIL}\t[-]\tInvalid difficulty level got accepted!{BColors.ENDC}')
        print(f"{BColors.OKGREEN}\t[start_game]\tPass not accepting invalid difficulty level.{BColors.ENDC}")

        # Test requesting too many users
        response2 = self.client.get('/game_board/llist_api/start_game/Easy/ID1,ID2,ID3,ID4,ID5,ID6/LLIST')

        self.assertEqual(response2.data, {'error': 'Too many players requested!',
                                          'options': config.LLIST_MAX_NUM_PLAYERS},
                         msg=f'{BColors.FAIL}\t[-]\tAccepted a game with too many players!{BColors.ENDC}')
        print(f"{BColors.OKGREEN}\t[start_game]\tPass not accepting too many players.{BColors.ENDC}")

    def test_start_game(self):
        """Tests starting new games"""
        random.seed(42)
        fail = False

        print(f"{BColors.OKBLUE}\t[i]\tStarting 20 games and ending them...{BColors.ENDC}")
        for _ in range(20):
            try:
                # Create players
                difficulty = random.choice(config.DIFFICULTY_LEVELS)
                players = list()
                num_players = 1
                for _ in range(num_players):
                    name = random.choice(string.ascii_letters)
                    players.append("ID" + str(name))
                players = ','.join(players)

                # Start a new game
                url = "/game_board/llist_api/start_game/" + difficulty + '/' + players + '/LLIST'
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200, msg=f'{BColors.FAIL}\t[-]\tResponse was not 200!{BColors.ENDC}')
                self.assertIn('game_id', response.data.keys(), msg=f'{BColors.FAIL}\t[-]\tGame ID was not returned!{BColors.ENDC}')

                # Remove the test game from the database
                sleep(0.2)
                db.remove_game(response.data['game_id'])

            except Exception as err:
                print(f"{BColors.FAIL}\t[-]\tFail creating games: {BColors.ENDC}", str(err))
                fail = True
        if not fail:
            print(f"{BColors.OKGREEN}\t[start_game]\tPass generating games.{BColors.ENDC}")


    def test_game_board_state(self):
        """Tests if the game configured as requested. Also tests load"""

        # create a new game
        created_game = self.client.get('/game_board/llist_api/start_game/Easy/ID1lltest/LLIST')
        # load the game
        response = self.client.get('/game_board/llist_api/board/' + str(created_game.data['game_id']))

        board = response.data
        self.assertEqual(board['difficulty'], 'Easy', msg=f'{BColors.FAIL}\t[-]\tDifficulty does not match!{BColors.ENDC}')
        print(f"{BColors.OKGREEN}\t[load_board]\tPass choosing the difficulty level.{BColors.ENDC}")

        self.assertEqual(board['curr_data_structure'], 'LLIST', msg=f'{BColors.FAIL}\t[-]\tCurrent data structure is invalid!{BColors.ENDC}')
        print(f"{BColors.OKGREEN}\t[load_board]\tPass setting the data structure.{BColors.ENDC}")

        self.assertEqual(board['player_ids'], ['ID1lltest'], msg=f'{BColors.FAIL}\t[-]\tIncorrect user ID!{BColors.ENDC}')
        print(f"{BColors.OKGREEN}\t[load_board]\tPass choosing user ID.{BColors.ENDC}")

        self.assertEqual(board['total_food'], 6, msg=f'{BColors.FAIL}\t[-]\tStarting food is not 6!{BColors.ENDC}')
        print(f"{BColors.OKGREEN}\t[load_board]\tPass setting the starting food amount.{BColors.ENDC}")


        # remove the created game
        sleep(0.2)
        db.remove_game(created_game.data['game_id'])

class GameActions(TestCase):
    """Tests the API calls that is related to game actions."""
    """Tests will be expanded upon once create chamber function is implemented"""

    def test_spawn(self):
        # create a new game
        created_game = self.client.get('/game_board/llist_api/start_game/Easy/ID1lltest/LLIST')
        # load the game
        response = self.client.get('/game_board/llist_api/board/' + str(created_game.data['game_id']))
        # call spawn ant function
        response = self.client.get('/game_board/llist_api/spawn_ant/' + str(response.data['game_id']))

        board = response.data

        # make sure there is no error
        self.assertNotEqual(response.status_code, 400, msg=f'{BColors.FAIL}\t[-]\tCould not spawn ant!{BColors.ENDC}')
        print(f"{BColors.OKGREEN}\t[spawn_ant]\tPass spawn ant api.{BColors.ENDC}")

        # make sure food was taken
        self.assertEqual(board['total_food'], 3, msg=f'{BColors.FAIL}\t[-]\tTotal food is off!{BColors.ENDC}')
        print(f"{BColors.OKGREEN}\t[spawn_ant]\tPass taking food after spawn.{BColors.ENDC}")

        # make sure ant total was updated
        self.assertEqual(board['total_ants'], 2, msg=f'{BColors.FAIL}\t[-]\tTotal ants are off!{BColors.ENDC}')
        print(f"{BColors.OKGREEN}\t[spawn_ant]\tPass creating a new ant.{BColors.ENDC}")

        # make sure ant was placed on surface
        self.assertEqual(board['total_surface_ants'], 2, msg=f'{BColors.FAIL}\t[-]\tNew ant not on surface!{BColors.ENDC}')
        self.assertEqual(board['graph']['num_ants']['surface'], 2, msg=f'{BColors.FAIL}\t[-]\tnum_ants.surface not updated!{BColors.ENDC}')
        print(f"{BColors.OKGREEN}\t[spawn_ant]\tPass placing ant on surface.{BColors.ENDC}")

        # make sure donut was taken
        self.assertEqual(board['total_food_types']['donut'], 0, msg=f'{BColors.FAIL}\t[-]\tDonut not taken!{BColors.ENDC}')
        print(f"{BColors.OKGREEN}\t[spawn_ant]\tPass taking a donut.{BColors.ENDC}")


        # remove the created game
        sleep(0.2)
        db.remove_game(created_game.data['game_id'])



    def test_dig_tunnel(self):
        # create a new game
        created_game = self.client.get('/game_board/llist_api/start_game/Easy/ID1lltest/LLIST')
        # load the game
        response = self.client.get('/game_board/llist_api/board/' + str(created_game.data['game_id']))
        # call spawn ant function 
        response = self.client.get('/game_board/llist_api/spawn_ant/' + str(response.data['game_id']))
        # call move ant function, from surface -> chamber1 so that we can test digging a tunnel after chamber1
        response = self.client.get('/game_board/llist_api/move_ant/' + str(response.data['game_id']) + '/surface/chamber1')
        # call dig tunnel
        response = self.client.get('/game_board/llist_api/dig_tunnel/' + str(response.data['game_id']) + '/chamber1/None')

        # make sure there was no error since we can now dig a tunnel
        self.assertNotEqual(response.status_code, 400, msg=f'{BColors.FAIL}\t[-]\tResponse was 400!{BColors.ENDC}')
        self.assertNotEqual(response.status_code, 500, msg=f'{BColors.FAIL}\t[-]\tResponse was 500!{BColors.ENDC}')
        self.assertNotEqual(response.status_code, 404, msg=f'{BColors.FAIL}\t[-]\tResponse was 404!{BColors.ENDC}')
        print(f"{BColors.OKGREEN}\t[dig_tunnel]\tPass returning the correct response code.{BColors.ENDC}")

        board = response.data

        # remove the created game
        sleep(0.2)
        db.remove_game(created_game.data['game_id'])

    # def test_dig_chamber(self):
    #     # create a new game
    #     created_game = self.client.get('/game_board/llist_api/start_game/Easy/ID1lltest/LLIST')
    #     # load the game
    #     response = self.client.get('/game_board/llist_api/board/' + str(created_game.data['game_id']))
    #     # call spawn ant function
    #     response = self.client.get(
    #         '/game_board/llist_api/dig_chamber/' + str(response.data['game_id']) + '/node1/no')

    #     board = response.data

    #     # make sure there was an error because selected node does not exist
    #     self.assertEqual(response.status_code, 400, msg=f'{BColors.FAIL}\t[-]\tResponse was not 400!{BColors.ENDC}')
    #     print(f"{BColors.OKGREEN}\t[+]\tPass returning the correct response code.{BColors.ENDC}")

    #     # remove the created game
    #     sleep(0.2)
    #     db.remove_game(created_game.data['game_id'])

    # def test_fill_chamber(self):
    #     # create a new game
    #     created_game = self.client.get('/game_board/llist_api/start_game/Easy/ID1lltest/LLIST')
    #     # load the game
    #     response = self.client.get('/game_board/llist_api/board/' + str(created_game.data['game_id']))
    #     # call spawn ant function
    #     response = self.client.get(
    #         '/game_board/llist_api/fill_chamber/' + str(response.data['game_id']) + '/node1')

    #     board = response.data

    #     # make sure there was an error because selected node does not exist
    #     self.assertEqual(response.status_code, 400, msg=f'{BColors.FAIL}\t[-]\tResponse was not 400!{BColors.ENDC}')
    #     print(f"{BColors.OKGREEN}\t[+]\tPass returning the correct response code.{BColors.ENDC}")

    #     # remove the created game
    #     sleep(0.2)
    #     db.remove_game(created_game.data['game_id'])

    def test_forage(self):
        # create a new game
        created_game = self.client.get('/game_board/llist_api/start_game/Easy/ID1lltest/LLIST')
        # load the game
        response = self.client.get('/game_board/llist_api/board/' + str(created_game.data['game_id']))
        # call spawn ant function so that we can test foraging with it
        response = self.client.get('/game_board/llist_api/spawn_ant/' + str(response.data['game_id']))
        # call spawn ant function THIS WILL FAIL UNTIL I MEET WITH DAVID
        response = self.client.get('/game_board/llist_api/forage/' + str(response.data['game_id']) + '/Easy/chamber1')

        # make sure there was no error since we can now forage
        self.assertNotEqual(response.status_code, 400, msg=f'{BColors.FAIL}\t[-]\tResponse was 400!{BColors.ENDC}')
        self.assertNotEqual(response.status_code, 500, msg=f'{BColors.FAIL}\t[-]\tResponse was 500!{BColors.ENDC}')
        self.assertNotEqual(response.status_code, 404, msg=f'{BColors.FAIL}\t[-]\tResponse was 404!{BColors.ENDC}')
        print(f"{BColors.OKGREEN}\t[forage]\tPass returning the correct response code.{BColors.ENDC}")

        board = response.data

        # make sure time track was updated
        self.assertEqual(board['time_tracks']['move/forage'], 35, msg=f'{BColors.FAIL}\t[-]\tTimetrack was not decremented!{BColors.ENDC}')
        print(f"{BColors.OKGREEN}\t[forage]\tPass updating time tracks.{BColors.ENDC}")

        # make sure number of surface ants were updated (only queen should on surface)
        self.assertEqual(board['total_surface_ants'], 1, msg=f'{BColors.FAIL}\t[-]\tAnt still on surface!{BColors.ENDC}')
        self.assertEqual(board['graph']['num_ants']['surface'], 1, msg=f'{BColors.FAIL}\t[-]\tnum_ants.surface not updated!{BColors.ENDC}')
        print(f"{BColors.OKGREEN}\t[forage]\tPass taking ant off of surface.{BColors.ENDC}")

        # make sure ant was placed in chamber1
        self.assertEqual(board['graph']['num_ants']['chamber1'], 1, msg=f'{BColors.FAIL}\t[-]\tAnt was not placed in chamber1!{BColors.ENDC}')
        print(f"{BColors.OKGREEN}\t[forage]\tPass placing ant in chamber1.{BColors.ENDC}")

        # make sure that we can assert the correct things if under attack
        if board['graph']['under_attack']['chamber1']:
            # make sure number of surface ants were updated (only queen should on surface)
            self.assertTrue(board['graph']['under_attack']['chamber1'], msg=f'{BColors.FAIL}\t[-]\tUnder attack was not updated!{BColors.ENDC}')
            print(f"{BColors.OKGREEN}\t[forage]\tPass being able to come under attack.{BColors.ENDC}")

        elif board['graph']['food']['chamber1']['crumb'] >= 2:
            # make sure number of surface ants were updated (only queen should on surface)
            self.assertEqual(board['graph']['food']['chamber1']['crumb'], 2, msg=f'{BColors.FAIL}\t[-]\tcrumb was placed in chamber but too many crumbs!{BColors.ENDC}')
            self.assertEqual(board['total_food_types']['crumb'], 2, msg=f'{BColors.FAIL}\t[-]\ttotal_food_types was not updated!{BColors.ENDC}')
            print(f"{BColors.OKGREEN}\t[forage]\tPass being able to forage for a crumb.{BColors.ENDC}")

            # make sure total_food was updated
            self.assertEqual(board['total_food'], 4, msg=f'{BColors.FAIL}\t[-]\ttotal_food is off!{BColors.ENDC}')
            print(f"{BColors.OKGREEN}\t[forage]\tPass updating total_food.{BColors.ENDC}")

        elif board['graph']['food']['chamber1']['berry'] >= 2:
            # make sure number of surface ants were updated (only queen should on surface)
            self.assertEqual(board['graph']['food']['chamber1']['berry'], 2, msg=f'{BColors.FAIL}\t[-]\tberry was placed in chamber but too many berries!{BColors.ENDC}')
            self.assertEqual(board['total_food_types']['berry'], 2, msg=f'{BColors.FAIL}\t[-]\ttotal_food_types was not updated!{BColors.ENDC}')
            print(f"{BColors.OKGREEN}\t[forage]\tPass being able to forage for a berry.{BColors.ENDC}")

            # make sure total_food was updated
            self.assertEqual(board['total_food'], 5, msg=f'{BColors.FAIL}\t[-]\ttotal_food is off!{BColors.ENDC}')
            print(f"{BColors.OKGREEN}\t[forage]\tPasss updating total_food.{BColors.ENDC}")

        elif board['graph']['food']['chamber1']['donut'] >= 1:
            # make sure number of surface ants were updated (only queen should on surface)
            self.assertEqual(board['graph']['food']['chamber1']['donut'], 1, msg=f'{BColors.FAIL}\t[-]\tdonut was placed in chamber but too many crumbs!{BColors.ENDC}')
            self.assertEqual(board['total_food_types']['donut'], 2, msg=f'{BColors.FAIL}\t[-]\ttotal_food_types was not updated!{BColors.ENDC}')
            print(f"{BColors.OKGREEN}\t[forage]\tPass being able to forage for a donut.{BColors.ENDC}")

            # make sure total_food was updated
            self.assertEqual(board['total_food'], 6, msg=f'{BColors.FAIL}\t[-]\ttotal_food is off!{BColors.ENDC}')
            print(f"{BColors.OKGREEN}\t[forage]\tPasss updating total_food.{BColors.ENDC}")



        # remove the created game
        sleep(0.2)
        db.remove_game(created_game.data['game_id'])

    def test_move_food(self):
        # create a new game
        created_game = self.client.get('/game_board/llist_api/start_game/Easy/ID1lltest/LLIST')
        # load the game
        response = self.client.get('/game_board/llist_api/board/' + str(created_game.data['game_id']))
        # call move food function
        response = self.client.get('/game_board/llist_api/move_food/' + str(response.data['game_id']) + '/chamber1/chamber2')

        board = response.data

        # make sure there was an error since there is no chamber 2
        # more tests will be implemented once ants can move, thus allowing them to create more chambers
        self.assertEqual(response.status_code, 400, msg=f'{BColors.FAIL}\t[-]\tResponse was not 400!{BColors.ENDC}')
        print(f"{BColors.OKGREEN}\t[move_food]\tPass returning the correct response code.{BColors.ENDC}")


        # remove the created game
        sleep(0.2)
        db.remove_game(created_game.data['game_id'])

    def test_move_ant(self):
        # create a new game
        created_game = self.client.get('/game_board/llist_api/start_game/Easy/ID1lltest/LLIST')
        # load the game
        response = self.client.get('/game_board/llist_api/board/' + str(created_game.data['game_id']))

        # call spawn ant function so that we can test moving it
        response = self.client.get('/game_board/llist_api/spawn_ant/' + str(response.data['game_id']))

        # call move ant function, from surface -> chamber1
        response = self.client.get('/game_board/llist_api/move_ant/' + str(response.data['game_id']) + '/surface/chamber1')

        board = response.data

        # make sure time track was updated
        self.assertEqual(board['time_tracks']['move/forage'], 35, msg=f'{BColors.FAIL}\t[-]\tTimetrack was not decremented!{BColors.ENDC}')
        print(f"{BColors.OKGREEN}\t[move_ant]\tPass updating time tracks.{BColors.ENDC}")

        # make sure no error, bc you should be able to move the ant from surface to the chamber1
        self.assertNotEqual(response.status_code, 400, msg=f'{BColors.FAIL}\t[-]\tResponse was not 400!{BColors.ENDC}')
        self.assertNotEqual(response.status_code, 500, msg=f'{BColors.FAIL}\t[-]\tResponse was not 500!{BColors.ENDC}')
        print(f"{BColors.OKGREEN}\t[move_ant]\tPass returning the correct response code.{BColors.ENDC}")

        # make sure number of surface ants were updated (only queen on surface)
        self.assertEqual(board['total_surface_ants'], 1, msg=f'{BColors.FAIL}\t[-]\tAnt still on surface!{BColors.ENDC}')
        self.assertEqual(board['graph']['num_ants']['surface'], 1, msg=f'{BColors.FAIL}\t[-]\tnum_ants.surface not updated!{BColors.ENDC}')
        print(f"{BColors.OKGREEN}\t[move_ant]\tPass taking ant off of surface.{BColors.ENDC}")

        # make sure ant was placed in chamber1
        self.assertEqual(board['graph']['num_ants']['chamber1'], 1, msg=f'{BColors.FAIL}\t[-]\tAnt was not placed in chamber1!{BColors.ENDC}')
        print(f"{BColors.OKGREEN}\t[move_ant]\tPass placing ant in the cmahber.{BColors.ENDC}")


        # remove the created game
        sleep(0.2)
        db.remove_game(created_game.data['game_id'])