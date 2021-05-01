import sys

""""handles all the stuff that happens inside the tunnels"""


class LList_Handler:
    def __init__(self):
        self.ants = {'Q': {'location': 'surface', 'food_type': None}} # {ant_id: {location:str, food_type:str}}
        self.num_ants = {'surface': 1, 'chamber1': 0} # not needed?
        self.chambers = {'surface': None, 'chamber1': None} # {chamber_id} not needed?
        self.tunnels = {'surface': {'entrance': True, 'exit': True, 'prev': 'chamber1', 'next': 'chamber1'},
                        'chamber1': {'entrance': True, 'exit': True, 'prev': 'surface', 'next': 'surface'}}
        # Do we need to keep track of food on surface? can't store stuff on the surface
        self.food = {'surface': {'crumb': 0, 'berry': 0, 'donut': 0}, 'chamber1': {'crumb': 3, 'berry': 0}}
        self.under_attack = {'chamber1': False} # {chamber_id: bool}
        self.num_chambers = 1 # doesn't include surface

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

        self.tunnels[chamber]['next'] = dest
        if dest is not None:
            self.tunnels[dest]['prev'] = chamber

    def digChamber(self, connecting_chbr):
        if connecting_chbr is not None:
            if connecting_chbr not in self.chambers and connecting_chbr != 'surface':
                raise ValueError
        self.num_chambers += 1
        newchamberID = "chamber" + str(len(self.chambers))
        self.chambers.append(newchamberID)
        self.num_ants[newchamberID] = 0
        self.tunnels[newchamberID] = {'entrance': True, 'exit': False, 'prev': connecting_chbr, 'next': None}
        self.tunnels[connecting_chbr]['next'] = newchamberID
        self.under_attack[newchamberID] = False
        self.food[newchamberID] = {'crumb': 0, 'berry': 0, 'donut': 0}

    def fillTunnel(self, chamber):
        if chamber in self.chambers:
            prev = self.tunnels[chamber]['prev']
            next = self.tunnels[chamber]['next']
            # self.tunnels[chamber][0] -= 1
            if next is not None:
                next['prev'] = None
                self.tunnels[chamber]['next'] = next
        else:
            raise ValueError

    def fillChamber(self, chamber):
        if chamber in self.chambers:
            self.tunnels[self.tunnels[chamber]['prev']]['next'] = None
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
