
import sys

""""handles all the stuff that happens inside the tunnels"""


class LList_Handler:
    def __init__(self):
        self.ants = {'Q': {'location': 'surface', 'food_type': None}}  # {ant_id: {location:str, food_type:str}}
        self.chambers = {'surface': {'num_ants': 1,
                                     'tunnels': {'entrance': True, 'exit': True, 'prev': 'chamber1',
                                                 'next': 'chamber1'},
                                     'food': {'total': 0, 'crumb': 0, 'berry': 0, 'donut': 0},
                                     'under_attack': False},
                         'chamber1': {'num_ants': 0,
                                      'tunnels': {'entrance': True, 'exit': True, 'prev': 'surface',
                                                  'next': 'surface'},
                                      'food': {'total': 6, 'crumb': 1, 'berry': 1, 'donut': 1},
                                      'under_attack': False}}  # {chamber_id} not needed?
        # Do we need to keep track of food on surface? can't store stuff on the surface

    @classmethod
    def fromGamestate(cls, gamestate):
        handler = cls()
        handler.ants = gamestate['ants']
        handler.chambers = gamestate['chambers']
        return handler

    def digTunnel(self, chamber, dest=None):
        if chamber not in self.chambers:
            raise ValueError
        if (dest is not None) and (dest not in self.chambers):
            raise ValueError
        self.chambers[chamber]['tunnels']['next'] = dest
        if dest is not None:
            self.chambers[dest]['tunnels']['prev'] = chamber

    def digChamber(self, connecting_chbr):
        if connecting_chbr is not None:
            if connecting_chbr not in self.chambers:
                raise ValueError
        newchamberID = "chamber" + str(len(self.chambers.keys()))
        self.chambers[connecting_chbr]['tunnels']['next'] = newchamberID
        self.chambers[connecting_chbr]['tunnels']['exit'] = True
        self.chambers[newchamberID] = {'num_ants': 0,
                                       'tunnels': {'entrance': True, 'exit': False, 'prev': connecting_chbr,
                                                   'next': None},
                                       'food': {'total': 0, 'crumb': 0, 'berry': 0, 'donut': 0},
                                       'under_attack': False}

    def fillTunnel(self, chamber):
        if chamber in self.chambers:
            # self.tunnels[chamber][0] -= 1
            if self.chambers[chamber]['tunnels']['next'] is not None:
                self.chambers[chamber]['tunnels']['next'] = None
            self.chambers[chamber]['tunnels']['exit'] = False
        else:
            raise ValueError

    def fillChamber(self, chamber):
        if chamber in self.chambers:
            self.chambers[self.chambers[chamber]['tunnels']['prev']]['tunnels']['next'] = None
            self.chambers[self.chambers[chamber]['tunnels']['prev']]['tunnels']['exit'] = False
            if self.chambers[chamber]['tunnels']['next'] is not None:
                self.chambers[self.chambers[chamber]['tunnels']['next']]['tunnels']['entrance'] = False
                self.chambers[self.chambers[chamber]['tunnels']['next']]['tunnels']['prev'] = None
            del self.chambers[chamber]
        else:
            raise ValueError

    def toGamestate(self):
        outdict = {'ants': self.ants, 'chambers': self.chambers}
        return outdict

    def spawnAnt(self):
        ant = 'A' + str(len(self.ants.keys()))
        self.ants[ant] = {'location': 'surface', 'food_type': None}
        self.chambers['surface']['num_ants'] += 1

    def moveAnt(self, ant, destination):
        if (ant not in self.ants) or (destination not in self.chambers):
            raise ValueError
        elif self.chambers[self.ants[ant]['location']]['num_ants'] <= 0:
            raise ValueError
        else:
            self.chambers[self.ants[ant]['location']]['num_ants'] -= 1
            self.chambers[destination]['num_ants'] += 1
            self.ants[ant]['location'] = destination

    def antPickup(self, ant, food):
        if (ant not in self.ants) or (ant == 'Q'):
            raise ValueError

    def antDrop(self, ant, food):
        if (ant not in self.ants) or (ant == 'Q'):
            raise ValueError


"""API callable function, makes a new 'linked list' structure for a game"""


def makeNewGame():
    handler = LList_Handler()
    return handler.toGamestate()


"""API callable function; given a game state and an action (string), returns the game state
with the action performed"""


def doAction(game, action):
    a = ('dig_tunnel', 'fill_tunnel', 'dig_chamber', 'fill_chamber', 'spawn_ant', 'move_ant')
    actionable = LList_Handler.fromGamestate(game)
    if action[0] == a[0]:
        actionable.digTunnel(action[1], action[2])
        return actionable.toGamestate()
    elif action[0] == a[1]:
        actionable.fillTunnel(action[1])
        return actionable.toGamestate()
    elif action[0] == a[2]:
        actionable.digChamber(action[1])
        return actionable.toGamestate()
    elif action[0] == a[3]:
        actionable.fillChamber(action[1])
        return actionable.toGamestate()
    elif action[0] == a[4]:
        actionable.spawnAnt()
        return actionable.toGamestate()
    elif action[0] == a[5]:
        actionable.moveAnt(action[1], action[2])
        return actionable.toGamestate()
    else:
        raise ValueError