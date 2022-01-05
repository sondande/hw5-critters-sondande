import critter
import color
import random

class Randomizer(critter.Critter):
	def interact(self, oppInfo):
		actions = [critter.POUNCE, critter.SCRATCH, critter.ROAR, critter.PARTY, critter.HEAL]
		rand = random.randint(0, len(actions)-1)
		return actions[rand]


	def getColor(self):
		return color.GRAY

	def getMove(self, info):
		moves = [critter.NORTH, critter.SOUTH, critter.EAST, critter.WEST]
		rand = random.randint(0, len(moves)-1)
		return moves[rand]

	def getChar(self):
		return "R"

	# we don't learn, so no need for interactionOver
