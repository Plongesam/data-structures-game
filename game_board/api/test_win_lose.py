from utils import win_state_llist
from utils import lose_state_llist
from game_board.llist.llist import doAction
from game_board.llist.llist import makeNewGame
from django.test import TestCase


class TestWinLose(TestCase):

    def testWin(self):
        startergraph = makeNewGame()
        starterboard = {'graph': startergraph, 'queen_at_head': True}
        """shouldn't be able to win at the start"""
        self.assertEqual(win_state_llist(starterboard), False)
        action = ['dig_chamber', None]
        startergraph = doAction(startergraph, action)
        action = ['dig_tunnel', 'chamber1', None]
        startergraph = doAction(startergraph, action)
        for i in range(2, 11):
            action = ['dig_chamber', 'chamber' + str(i - 1)]
            startergraph = doAction(startergraph, action)
            action = ['dig_tunnel', 'chamber' + str(i), None]
            startergraph = doAction(startergraph, action)
        """Even with 10 chambers, this shouldn't work because they have no food"""
        longboard = starterboard = {'graph': startergraph, 'queen_at_head': True}
        self.assertEqual(win_state_llist(longboard), False)
        for i in range(1, 11):
            chamber = 'chamber' + str(i)
            startergraph['food'][chamber]['crumb'] = 3
        """Now we should be able to win"""
        winboard = {'graph': startergraph, 'queen_at_head': True}
        self.assertEqual(win_state_llist(winboard), True)
        """but if we make one of the chambers under attack, it will be impossible again"""
        startergraph['under_attack']['chamber1'] = True
        winboard = {'graph': startergraph, 'queen_at_head': True}
        self.assertEqual(win_state_llist(winboard), False)

    def testLose(self):
        startergraph = makeNewGame()
        starterboard = {'graph': startergraph, 'queen_at_head': True}
        losingboard = {'graph': startergraph, 'queen_at_head': False}
        """shouldn't be able to lose at the start"""
        self.assertEqual(lose_state_llist(starterboard), False)
        """unless the queen gets yeeted somehow"""
        self.assertEqual(lose_state_llist(losingboard), True)
        action = ['dig_chamber', None]
        startergraph = doAction(startergraph, action)
        action = ['dig_tunnel', 'chamber1', None]
        startergraph = doAction(startergraph, action)
        action = ['dig_chamber', 'chamber1']
        startergraph = doAction(startergraph, action)
        """our chambers are connected so this won't cause a lose"""
        tunnelboard = {'graph': startergraph, 'queen_at_head': True}
        self.assertEqual(lose_state_llist(starterboard), False)
        """but now they will!"""
        startergraph['tunnels']['chamber1'][1][0] = None
        losetunnelboard = {'graph': startergraph, 'queen_at_head': True}
        self.assertEqual(lose_state_llist(losetunnelboard), True)
        startergraph['tunnels']['chamber1'][1][0] = 'Head'
        "should work for both top chamber and the connection from c1 to c2"
        action = ['fill_tunnel', 'chamber1']
        losebynoconnection = doAction(startergraph, action)
        self.assertEqual(lose_state_llist({'graph': losebynoconnection, 'queen_at_head': True}), True)
