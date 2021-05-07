from game_board.llist.llist import doAction
from game_board.llist.llist import makeNewGame
from django.test import TestCase



"""here's a comment to test the thing"""


class LlistTests(TestCase):

    def test_initialize(self):
        gamestate = makeNewGame()
        keys = ['chambers', 'ants']
        starter_chambers = ['surface', 'chamber1']
        chamber_keys = ['num_ants', 'tunnels', 'food', 'under_attack']
        for key in keys:
            self.assertIn(key, gamestate)
        for chamber in starter_chambers:
            self.assertIn(chamber, gamestate['chambers'])
            for chamber_key in chamber_keys:
                self.assertIn(chamber_key, gamestate['chambers'][chamber])

    def test_inserts(self):
        """test some inserts, make sure they produce intended behavior"""
        gamestate = makeNewGame()
        action = ('dig_tunnel', 'chamber1', None)
        gamestate = doAction(gamestate, action)
        self.assertEqual(True, gamestate['chambers']['chamber1']['tunnels']['exit'])
        action = ('dig_chamber', 'chamber1')
        gamestate = doAction(gamestate, action)
        self.assertIn('chamber2', gamestate['chambers'])

        """game state shouldn't change if I add a chamber connected to a nonexistent one"""
        action = ('dig_chamber', 'chamber4')
        with self.assertRaises(ValueError):
            doAction(gamestate, action)

        """or if I add a tunnel to/from a nonexistent chamber"""
        action = ('dig_tunnel', 'chamber2', 'chamber4')
        with self.assertRaises(ValueError):
            doAction(gamestate, action)

    def test_fills(self):
        """create a game with some tunnels and chambers already in"""
        gamestate = makeNewGame()
        action = ['dig_tunnel', 'chamber1', None]
        gamestate = doAction(gamestate, action)
        action = ['dig_chamber', 'chamber1']
        gamestate = doAction(gamestate, action)
        action = ['dig_tunnel', 'chamber2', None]
        gamestate = doAction(gamestate, action)

        """do the fills"""
        action = ['fill_tunnel', 'chamber2']
        gamestate = doAction(gamestate, action)
        self.assertEqual(False, gamestate['chambers']['chamber2']['tunnels']['exit'])

        action = ['fill_chamber', 'chamber2']
        gamestate = doAction(gamestate, action)
        self.assertEqual(2, len(gamestate['chambers'].keys()))

        """game state shouldn't change if I remove a nonexistent tunnel"""
        action = ['fill_tunnel', 'chamber3']
        with self.assertRaises(ValueError):
            doAction(gamestate, action)

        """game state shouldn't change if I remove a nonexistent chamber"""
        action = ['fill_chamber', 'chamber3']
        with self.assertRaises(ValueError):
            doAction(gamestate, action)

    def test_ants(self):
        gamestate = makeNewGame()
        action = ['spawn_ant']
        gamestate = doAction(gamestate, action)
        self.assertEqual(2, gamestate['chambers']['surface']['num_ants'])
        action = ['move_ant', 'A1', 'chamber1']
        gamestate = doAction(gamestate, action)
        self.assertEqual(1, gamestate['chambers']['chamber1']['num_ants'])