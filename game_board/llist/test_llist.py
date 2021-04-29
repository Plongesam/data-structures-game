from game_board.llist.llist import doAction
from game_board.llist.llist import makeNewGame
from django.test import TestCase

"""here's a comment to test the thing"""
class LlistTests(TestCase):

    def test_initialize(self):
        gamestate = makeNewGame()
        keys = ['chambers', 'food', 'under_attack', 'tunnels', 'num_ants', 'num_chambers',
                'ants']
        for key in keys:
            self.assertIn(key, gamestate.keys())

        self.assertEqual(gamestate['ants']['Q']['location'], 'surface')
        self.assertEqual(gamestate['ants']['Q']['food_type'], None)
        self.assertEqual(gamestate['num_ants']['surface'], 1)
        self.assertEqual(gamestate['food'], {'surface': {'crumb': 0, 'berry': 0, 'donut': 0}})
        self.assertEqual(gamestate['chambers'], [])
        self.assertEqual(gamestate['tunnels'], {'surface': [0, None, None]})
        self.assertEqual(gamestate['under_attack'], {})

    def test_inserts(self):
        """test some inserts, make sure they produce intended behavior"""
        gamestate = makeNewGame()
        action = ('dig_tunnel', 'surface', None)
        gamestate = doAction(gamestate, action)
        self.assertEqual(gamestate['num_ants']['surface'], 1)
        self.assertEqual(gamestate['num_chambers'], 0)
        self.assertEqual(gamestate['tunnels']['surface'][0], 1)

        action = ('dig_chamber', 'surface')
        gamestate = doAction(gamestate, action)
        self.assertEqual(gamestate['food']['chamber1']['crumb'], 0)
        self.assertEqual(gamestate['food']['chamber1']['berry'], 0)
        self.assertEqual(gamestate['food']['chamber1']['donut'], 0)
        self.assertEqual(len(gamestate['chambers']), 1)
        self.assertEqual(gamestate['tunnels']['chamber1'], [1, ['surface', None]])
        self.assertEqual(gamestate['under_attack']['chamber1'], False)

        action = ('dig_tunnel', 'chamber1', None)
        gamestate = doAction(gamestate, action)
        self.assertEqual(gamestate['tunnels']['chamber1'], [2, ['surface', None]])

        action = ('dig_chamber', 'chamber1')
        gamestate = doAction(gamestate, action)
        self.assertEqual(gamestate['num_chambers'], 2)
        self.assertEqual(gamestate['food']['chamber2']['crumb'], 0)
        self.assertEqual(gamestate['food']['chamber2']['berry'], 0)
        self.assertEqual(gamestate['food']['chamber2']['donut'], 0)
        self.assertEqual(len(gamestate['chambers']), 2)
        self.assertEqual(gamestate['tunnels']['chamber2'], [1, ['chamber1', None]])
        self.assertEqual(gamestate['under_attack']['chamber2'], False)

        """game state shouldn't change if I add a chamber connected to a nonexistent one"""
        action = ('dig_chamber', 'chamber4')
        self.assertRaises(ValueError, doAction(gamestate, action))

        """or if I add a tunnel to/from a nonexistent chamber"""
        action = ('dig_tunnel', 'chamber2', 'chamber4')
        self.assertRaises(ValueError, doAction(gamestate, action))

    def test_fills(self):
        """create a game with some tunnels and chambers already in"""
        gamestate = makeNewGame()
        action = ['dig_tunnel', 'surface', None]
        gamestate = doAction(gamestate, action)
        action = ['dig_chamber', 'surface']
        gamestate = doAction(gamestate, action)
        action = ['dig_tunnel', 'chamber1', None]
        gamestate = doAction(gamestate, action)
        action = ['dig_chamber', 'chamber1']
        gamestate = doAction(gamestate, action)
        action = ['dig_tunnel', 'chamber2', None]
        gamestate = doAction(gamestate, action)

        """do the fills"""
        action = ['fill_tunnel', 'chamber2']
        gamestate = doAction(gamestate, action)
        self.assertEqual(gamestate['tunnels']['chamber2'][0], 1)
        self.assertEqual(gamestate['tunnels']['chamber2'][1][1], None)
        action = ['fill_tunnel', 'chamber2']
        gamestate = doAction(gamestate, action)
        self.assertEqual(gamestate['tunnels']['chamber2'][0], 1)
        action = ['fill_chamber', 'chamber2']
        gamestate = doAction(gamestate, action)
        self.assertEqual(len(gamestate['chambers']), 1)
        self.assertEqual(gamestate['tunnels']['chamber1'][1][1], None)

        """game state shouldn't change if I remove a tunnel connected to a nonexistent one"""
        action = ['fill_tunnel', 'chamber3']
        self.assertRaises(ValueError, doAction(gamestate, action))

        """game state shouldn't change if I remove a nonexistent chamber"""
        action = ['fill_chamber', 'chamber3']
        self.assertRaises(ValueError, doAction(gamestate, action))

    def test_ants(self):
        gamestate = makeNewGame()
        action = ['dig_tunnel', 'surface', None]
        gamestate = doAction(gamestate, action)
        action = ['dig_chamber', 'surface']
        gamestate = doAction(gamestate, action)
        action = ['spawn_ant']
        gamestate = doAction(gamestate, action)
        self.assertIn('A1', gamestate['ants'].keys())
        action = ['move_ant', 'A1', 'chamber1']
        self.assertEqual(gamestate['ants']['A1']['location'], 'chamber1')
