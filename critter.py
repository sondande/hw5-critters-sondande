#!/usr/bin/env python3

# Constants for movement.
NORTH = -2
NORTHEAST = 27
NORTHWEST = 102
SOUTH = 4
SOUTHEAST = 99
SOUTHWEST = -31
EAST = 3
WEST = 19
CENTER = 11

# Constants for attack
ROAR = 28
POUNCE = -10
SCRATCH = 55
PARTY = 12345
HEAL = 54321

DAMAGE_ATTACKED = 25
    
class Critter():
    """
    The base Critter class.
    """

    def __init__(self):
        self.health = 100
        self.karma = 0
        pass
        
    # @param oppInfo The critter info of the current opponent.
    # @returns Your action: ROAR, POUNCE, SCRATCH, PARTY, or HEAL
    def interact(self, oppInfo):
        pass
    
    # Give your color.
    # @returns Your current color.
    def getColor(self):
        pass
    
    # Give your direction.
    # @param info your critter info
    # @returns A cardinal direction, in the form of a constant (NORTH, SOUTH)
    def getMove(self, info):
        pass
    
    # Give your character.
    # @returns Whichever character represents this critter.
    def getChar(self):
        pass
    
    # End of interaction shenanigans.
    # @param won Boolean; true if won the interaction, false otherwise.
    # @param oppFight Opponent's choide of fight strategy (ROAR, etc)
    # @returns Nothing.
    def interactionOver(self, won, oppFight):
        pass
    
    def __str__(self):
        return '%s' % (self.__class__.__qualname__)
