import critter
import critter_main
import collections
import color
import inspect
import random
import os
import pprint

# some constants to help us
ATTACK_DAMAGE = 25
HEAL_RESTORE = 50
DEFEND_KARMA = 1
PARTY_KARMA = 3
HEAL_KARMA = 5
ATTACK_PARTY_KARMA = -PARTY_KARMA
ATTACK_HEAL_KARMA = -HEAL_KARMA

# Just an (x, y) pair, but more readable.
Point = collections.namedtuple('Point', ['x', 'y'])

# Again, we don't really need a whole class just to store this info.
CritterInfo = collections.namedtuple('CritterInfo', ['x', 'y', 'width', 'height', 'char', 'color', 'getNeighbor', 'getNeighborHealth'])

class CritterModel():
    """
    The main Critter simulation. Takes care of all the logic of
    Critter interactions.
    """
    
    def __init__(self, width, height, list_lock):
        self.width = width
        self.height = height
        self.critters = []
        self.move_count = 0
        # A map of critters to (x, y) positions.
        self.critter_positions = {}
        # A map of critter classes to the number alive of that class.
        self.critter_class_states = {}
        self.grid = [[None for x in range(height)] for y in range(width)]
        # Make sure nothing bad happens due to concurrent list access.
        self.list_lock = list_lock

    def add(self, critter, num):
        """
        Adds a particular critter type num times. The critter should
        be a class, not an instantiated critter.
        """
        if critter not in self.critter_class_states:
            self.critter_class_states[critter] = ClassInfo(initial_count=num)
        self.critter_class_states[critter].alive += num
        self.critter_class_states[critter].health += num * 100
        for i in range(num):
            args = CritterModel.create_parameters(critter)
            c = critter(*args)
            self.critters.append(c)
            pos = self.random_location()
            self.critter_positions[c] = pos
            self.grid[pos.x][pos.y] = c
    
    def reset(self, num_critters):
        '''
        Resets the model, clearing out the whole board and
        repopulating it with num_critters of the same Critter types.
        '''
        self.grid = [[None for x in range(self.height)] for y in range(self.width)]
        self.critter_positions = {}
        self.critters = []
        self.move_count = 0
        new_states = {}
        for critter_class in self.critter_class_states.keys():
            new_states[critter_class] = ClassInfo(initial_count=num_critters)
            new_states[critter_class].alive += num_critters
            for i in range(num_critters):
                args = CritterModel.create_parameters(critter_class)
                c = critter_class(*args)
                self.critters.append(c)
                pos = self.random_location()
                self.critter_positions[c] = pos
                self.grid[pos.x][pos.y] = c
        self.critter_class_states = new_states

    def update(self):
        """
        Takes care of updating all Critters. For each Critter, it
        firsts moves. If the position it moves to is occupied, the two
        critters interact.  If one runs out of health, it loses and is removed
        and the other moves into the position.
        """
        self.move_count += 1
        random.shuffle(self.critters)
        # Unclean while loop, because we'll be removing any losing critters
        # as we iterate through the list.
        i = 0
        l = len(self.critters)
        while i < l:
            critter1 = self.critters[i]
            # Move the critter
            old_position = self.critter_positions[critter1]
            direction = critter1.getMove(CritterInfo(old_position.x, old_position.y,
                                                     self.width, self.height,
                                                     critter1.getChar(),
                                                     critter1.getColor(),
                                                     self.get_neighbor_func(old_position),
                                                     self.get_neighbor_health_func(old_position)))

            CritterModel.verify_move(direction)
            position = self.move(direction, old_position)

            # Interact, if necessary
            winner = critter1
            loser = None
            critter2 = self.grid[position.x][position.y]
            if critter2 and position != old_position and critter1 != critter2: # Save each stone from fighting itself
                winner = self.interact(critter1, critter2)

                # NOTE: most updates happen in interact method called above
                # such as health and karma

                loser = critter1 if winner == critter2 else critter2

                # here, we remove a critter if it no longer has health
                if loser.health <= 0:
                    self.critter_positions[winner] = position

                    # Get the loser out of here
                    with self.list_lock:
                        index = self.critters.index(loser)
                        if index <= i:
                            # the loser was earlier in the list, so the
                            # winner's index decreases
                            i -= 1

                           
                        self.critter_positions.pop(loser)
                        self.critters.remove(loser)
                        l -= 1 # we have one fewer total critter

                        # Make sure we've got an accurate wins/alive count
                        self.critter_class_states[loser.__class__].alive -= 1
                        self.critter_class_states[winner.__class__].wins += 1

                        # this loser no longer exists
                        loser = None
                        
            # Update positions
            self.grid[old_position.x][old_position.y] = loser
            self.grid[position.x][position.y] = winner
            self.critter_positions[winner] = position
            if loser is not None:
                self.critter_positions[loser] = old_position
                    
            i += 1
            
    def move(self, direction, pos):
        """
        Returns the new position after moving in direction. This
        assumes that (0, 0) is the top-left.
        """
        if direction == critter.NORTH:
            return Point(pos.x, (pos.y - 1) % self.height)
        elif direction == critter.SOUTH:
            return Point(pos.x, (pos.y + 1) % self.height)
        elif direction == critter.EAST:
            return Point((pos.x + 1) % self.width, pos.y)
        elif direction == critter.WEST:
            return Point((pos.x - 1) % self.width, pos.y)
        elif direction == critter.NORTHEAST:
            return Point((pos.x + 1) % self.width, (pos.y - 1) % self.height)
        elif direction == critter.NORTHWEST:
            return Point((pos.x - 1) % self.width, (pos.y - 1) % self.height)
        elif direction == critter.SOUTHWEST:
            return Point((pos.x + 1) % self.width, (pos.y + 1) % self.height)
        elif direction == critter.SOUTHEAST:
            return Point((pos.x - 1) % self.width, (pos.y + 1) % self.height)
        else:
            return pos
    
    def interact(self, critter1, critter2):
        """
        Force poor innocent Critters to interact and possibly risk death for
        the entertainment of Oberlin students. Returns the glorious
        victor.
        """
        position = self.critter_positions[critter2]
        action1 = critter1.interact(CritterInfo(position.x, position.y,
                                                     self.width, self.height,
                                                     critter2.getChar(),
                                                     critter2.getColor(),
                                                     self.get_neighbor_func(position),
                                                     self.get_neighbor_health_func(position)))
        position = self.critter_positions[critter1]
        action2 = critter2.interact(CritterInfo(position.x, position.y,
                                                     self.width, self.height,
                                                     critter1.getChar(),
                                                     critter1.getColor(),
                                                     self.get_neighbor_func(position),
                                                     self.get_neighbor_health_func(position))) 
        CritterModel.verify_action(action1)
        CritterModel.verify_action(action2)

        # did the first critter fight?
        fight1 = action1 == critter.ROAR or action1 == critter.SCRATCH or action1 == critter.POUNCE
            
        # did the second critter fight?
        fight2 = action2 == critter.ROAR or action2 == critter.SCRATCH or action2 == critter.POUNCE

        # find the "winner"
        critter2won = True

        if (fight1 and fight2):            
            if (action1 == critter.ROAR and action2 == critter.SCRATCH or
                    action1 == critter.SCRATCH and action2 == critter.POUNCE or
                    action1 == critter.POUNCE and action2 == critter.ROAR):
                # critter 1 won
                
                # update critter 2's health
                critter2.health = max(0, critter2.health - ATTACK_DAMAGE)
                self.critter_class_states[critter2.__class__].health -= ATTACK_DAMAGE

                # update critter 1's karma
                critter1.karma += DEFEND_KARMA
                self.critter_class_states[critter1.__class__].karma += DEFEND_KARMA

                # update the winner
                critter2won = False
            elif action1 == action2:
                if random.random() > .5:
                    # critter 1 won
                
                    # update critter 2's health
                    critter2.health = max(0, critter2.health - ATTACK_DAMAGE)
                    self.critter_class_states[critter2.__class__].health -= ATTACK_DAMAGE
                    
                    # update critter 1's karma
                    critter1.karma += DEFEND_KARMA
                    self.critter_class_states[critter1.__class__].karma += DEFEND_KARMA

                    # update the winner
                    critter2won = False
                else:
                    # critter 2 won
                
                    # update critter 1's health
                    critter1.health = max(0, critter1.health - ATTACK_DAMAGE)
                    self.critter_class_states[critter1.__class__].health -= ATTACK_DAMAGE

                    # update critter 2's karma
                    critter2.karma += DEFEND_KARMA
                    self.critter_class_states[critter2.__class__].karma += DEFEND_KARMA

                    # update the winner
                    critter2won = True
            else:
                # critter 2 won
                
                # update critter 1's health
                critter1.health = max(0, critter1.health - ATTACK_DAMAGE)                
                self.critter_class_states[critter1.__class__].health -= ATTACK_DAMAGE

                # update critter 2's karma
                critter2.karma += DEFEND_KARMA
                self.critter_class_states[critter2.__class__].karma += DEFEND_KARMA

                # update the winner
                critter2won = True
        elif (fight1):
            # only critter 1 chose to fight, so they win by default

            # update critter2's health
            critter2.health = max(0, critter2.health - ATTACK_DAMAGE)
            self.critter_class_states[critter2.__class__].health -= ATTACK_DAMAGE
            
            if (action2 == critter.PARTY):
                # update critter1's karma
                critter1.karma += ATTACK_PARTY_KARMA
                self.critter_class_states[critter1.__class__].karma += ATTACK_PARTY_KARMA
            elif (action2 == critter.HEAL):
                critter1.karma += ATTACK_HEAL_KARMA
                self.critter_class_states[critter1.__class__].karma += ATTACK_HEAL_KARMA

            # update the winner
            critter2won = False
        elif (fight2):
             # only critter 2 chose to fight, so they win by default

            # update critter1's health
            critter1.health = max(0, critter1.health - ATTACK_DAMAGE)
            self.critter_class_states[critter1.__class__].health -= ATTACK_DAMAGE
            
            if (action1 == critter.PARTY):
                # update critter2's karma
                critter2.karma += ATTACK_PARTY_KARMA
                self.critter_class_states[critter2.__class__].karma += ATTACK_PARTY_KARMA
            elif (action1 == critter.HEAL):
                critter2.karma += ATTACK_HEAL_KARMA
                self.critter_class_states[critter2.__class__].karma += ATTACK_HEAL_KARMA

            # update the winner
            critter2won = True
        else:
            # did anyone try to heal?
            # note: nothing happens if you try to heal a critter
            # with perfect health
            if (action1 == critter.HEAL and critter2.health < 100):
                # update critter2's health
                oldHealth = critter2.health
                critter2.health = min(100, critter2.health + HEAL_RESTORE)
                self.critter_class_states[critter2.__class__].health += critter2.health - oldHealth

                # update critter1's karma
                critter1.karma += HEAL_KARMA
                self.critter_class_states[critter1.__class__].karma += HEAL_KARMA
            elif (action1 == critter.PARTY):
                # update critter1's karma
                critter1.karma += PARTY_KARMA
                self.critter_class_states[critter1.__class__].karma += PARTY_KARMA

            if (action2 == critter.HEAL and critter1.health < 100):
                # update critter1's health
                oldHealth = critter1.health
                critter1.health = min(100, critter1.health + HEAL_RESTORE)
                self.critter_class_states[critter1.__class__].health += critter1.health - oldHealth

                # update critter2's karma
                critter2.karma += HEAL_KARMA
                self.critter_class_states[critter2.__class__].karma += HEAL_KARMA
            elif (action2 == critter.PARTY):
                # update critter2's karma
                critter2.karma += PARTY_KARMA
                self.critter_class_states[critter2.__class__].karma += PARTY_KARMA
            
            # pick a winner at random
            critter2won = True
            if random.random() > .5:
                critter2won = False

        # alert the critters about the interaction
        critter1.interactionOver(not critter2won, action2)
        critter2.interactionOver(critter2won, action1)

        # return the "winner"
        if (critter2won):
            return critter2
        else:
            return critter1

    def verify_action(action):
        """
        Make sure students are using the right actions. If not, throws
        an exception.
        """
        if action not in (critter.ROAR, critter.POUNCE, critter.SCRATCH, critter.PARTY, critter.HEAL):
            raise ActionException("Critter action must be ROAR, POUNCE, SCRATCH, PARTY, or HEAL!")
    
    def verify_move(move):
        "Make sure they don't move diagonally."
        if move not in (critter.NORTH, critter.SOUTH, critter.EAST, critter.WEST, critter.CENTER):
            raise LocationException("Don't move diagonally! %s" % move)

    def verify_location(location):
        """
        Make sure students are using the right locations. If not,
        throws an exception.
        """
        if location not in (critter.NORTH, critter.NORTHEAST, critter.NORTHWEST,
                            critter.SOUTH, critter.SOUTHEAST, critter.SOUTHWEST,
                            critter.EAST, critter.WEST, critter.CENTER):
            raise LocationException("That is not a real direction!")

    def random_location(self):
        """
        Calculate a random location for a Critter to be placed. This
        is not guaranteed to terminate by any means, but practically
        we (probably) don't need to be concerned.

        Returns a 2-tuple of integers.
        """
        x = random.randint(0, self.width-1)
        y = random.randint(0, self.height-1)
        while self.grid[x][y] is not None:
            x = random.randint(0, self.width-1)
            y = random.randint(0, self.height-1)
        return Point(x, y)
    
    def create_parameters(critter):
        """
        This is a bit funky. Because not all Critters take the same
        arguments in their constructor (for example, a Mouse gets a
        color while an Elephant gets an int), we need to check the
        classname and return appropriate things based on that. The
        Java version is a bit nicer because it has access to type
        information for each parameter, but c'est la vie.
        
        Return value is a tuple, which will be passed as *args to
        the critter's constructor.
        """
        if critter.__name__ == 'Mouse':
            return (color.Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),)
        elif critter.__name__ == 'Elephant':
            return (random.randint(1, 15),)
        # No other class needs parameters
        else:
            return ()
    
    def get_neighbor_func(self, position):
        "Returns the getNeighbor function for a particular position."
        def get_neighbor(direction):
            neighbor_pos = self.move(direction, position)
            neighbor = self.grid[neighbor_pos.x][neighbor_pos.y]
            #print( neighbor, type(neighbor) )
            return neighbor.__class__.__name__ if neighbor else '.'
        return get_neighbor

    def get_neighbor_health_func(self, position):
        "Returns the getNeighborHealth function for a particular position."
        def get_neighbor_health(direction):
            neighbor_pos = self.move(direction, position)
            neighbor = self.grid[neighbor_pos.x][neighbor_pos.y]
            #print( neighbor, type(neighbor) )
            return neighbor.health if neighbor else 0
        return get_neighbor_health

    def results(self):
        """
        Returns the critters in the simulation, sorted by karma
        results()[0] is (overall winner, karma of winner)
        """
        return sorted(self.critter_class_states.items(),
                      key=lambda state: -(state[1].karma))
        
            
class ClassInfo():
    """
    This would be a named tuple, but they're immutable and that's
    somewhat unwieldy for this particular case.
    """
    def __init__(self, wins=0, alive=0, initial_count=0, karma=0):
        self.wins = wins
        self.alive = alive
        self.count = initial_count
        self.health = 0
        self.karma = karma
    
    def __repr__(self):
        return '%s %s %s %s %s' % (self.wins, self.alive, self.count, self.health, self.karma)

# These exceptions don't really need fancy names
class ActionException(Exception):
    pass

class LocationException(Exception):
    pass
