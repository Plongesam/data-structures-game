import sys

""""handles all the stuff that happens inside the tunnels"""


class LList_Handler:
    def __init__(self):
        self.ants = {'Q': {'location': 'surface', 'food_type': None}}
        self.num_ants = {'surface': 1}
        self.chambers = []
        self.tunnels = {'surface': [0, None, None]}
        self.food = {'surface': {'crumb': 0, 'berry': 0, 'donut': 0}}
        self.under_attack = {}
        self.num_chambers = 0

    @classmethod
    def from_gamestate(cls, gamestate):
        handler = cls()
        handler.ants = gamestate['ants']
        handler.chambers = gamestate['chambers']
        handler.tunnels = gamestate['tunnels']
        handler.food = gamestate['food']
        handler.under_attack = gamestate['under_attack']
        handler.num_chambers = gamestate['num_chambers']
        handler.num_ants = gamestate['num_ants']
        return handler

    def digTunnel(self, chamber, dest=None):
        if chamber != 'surface' and chamber not in self.chambers:
            raise ValueError
        if dest is not None and dest not in self.chambers and dest != 'surface':
            raise ValueError
        if self.tunnels[chamber][0] < 2:
            self.tunnels[chamber][0] += 1
        self.tunnels[chamber][2] = dest
        if dest is not None:
            self.tunnels[dest][1] = chamber

    def digChamber(self, connecting_chbr):
        if connecting_chbr is not None:
            if connecting_chbr not in self.chambers and connecting_chbr != 'surface':
                raise ValueError
        self.num_chambers += 1
        newchamberID = "chamber" + str(len(self.chambers)+1)
        self.chambers.append(newchamberID)
        self.num_ants[newchamberID] = 0
        self.tunnels[newchamberID] = [1, connecting_chbr, None]
        self.tunnels[connecting_chbr][2] = newchamberID
        self.under_attack[newchamberID] = False
        self.food[newchamberID] = {'crumb': 0, 'berry': 0, 'donut': 0}

    def fillTunnel(self, chamber):
        if chamber in self.chambers:
            self.tunnels[chamber][0] -= 1
            if self.tunnels[chamber][2] is not None:
                self.tunnels[self.tunnels[chamber][2]][1] = None
                self.tunnels[self.tunnels[chamber][2]][0] -= 1
                self.tunnels[chamber][2] = None
        else:
            raise ValueError

    def fillChamber(self, chamber):
        if chamber in self.chambers:
            self.tunnels[self.tunnels[chamber][1]][2] = None
            self.tunnels.pop(chamber)
            self.num_ants.pop(chamber)
            self.chambers.remove(chamber)
            self.food.pop(chamber)
            self.num_chambers -= 1
        else:
            raise ValueError

    def to_gamestate(self):
        outdict = {'ants': self.ants, 'num_ants': self.num_ants, 'chambers': self.chambers, 'tunnels': self.tunnels,
                   'food': self.food, 'under_attack': self.under_attack, 'num_chambers': self.num_chambers}
        return outdict

    def spawnAnt(self):
        ant = 'A'+str(len(self.ants.keys()))
        self.ants[ant] = {'location': 'surface', 'food_type': None}

    def moveAnt(self, ant, destination):
        if ant not in self.ants.keys():
            raise ValueError
        self.num_ants[self.ants[ant]['location']] -= 1
        self.ants[ant]['location'] = destination
        self.num_ants[destination] += 1

    def antPickup(self, ant, food):
        if (ant not in self.ants.keys()) or (ant == 'Q'):
            raise ValueError
        if self.ants[ant]['location'] != 'surface':
            if self.food[self.ants[ant]['location']][food] > 0:
                self.food[self.ants[ant]['location']][food] -= 1
                self.ants[ant]['food_type'] = food

    def antDrop(self, ant, food):
        if (ant not in self.ants.keys()) or (ant == 'Q'):
            raise ValueError
        if self.ants[ant]['location'] != 'surface':
            if self.ants[ant][food] > 0:
                self.food[self.ants[ant]['location']][food] += 1
                self.ants[ant]['food_type'] = None


"""API callable function, makes a new 'linked list' structure for a game"""


def makeNewGame():
    handler = LList_Handler()
    return handler.to_gamestate()


"""API callable function; given a game state and an action (string), returns the game state
with the action performed"""


def doAction(game, action):
    a = ('dig_tunnel', 'fill_tunnel', 'dig_chamber', 'fill_chamber', 'spawn_ant', 'move_ant', 'ant_pickup', 'ant_drop')
    actionable = LList_Handler.from_gamestate(game)
    if action[0] == a[0]:
        actionable.digTunnel(action[1], action[2])
        return actionable.to_gamestate()
    elif action[0] == a[1]:
        actionable.fillTunnel(action[1])
        return actionable.to_gamestate()
    elif action[0] == a[2]:
        actionable.digChamber(action[1])
        return actionable.to_gamestate()
    elif action[0] == a[3]:
        actionable.fillChamber(action[1])
        return actionable.to_gamestate()
    elif action[0] == a[4]:
        actionable.spawnAnt()
        return actionable.to_gamestate()
    elif action[0] == a[5]:
        actionable.moveAnt(action[1], action[2])
        return actionable.to_gamestate()
    elif action[0] == a[6]:
        actionable.antPickup(action[1], action[2])
        return actionable.to_gamestate()
    elif action[0] == a[7]:
        actionable.antDrop(action[1], action[2])
        return actionable.to_gamestate()
    else:
        raise ValueError
