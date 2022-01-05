import critter
import color
import random

class Roarer(critter.Critter):
	def interact(self, oppInfo):
		return critter.ROAR

	def getColor(self):
		return color.GRAY

	def getMove(self, info):
		moves = [critter.NORTH, critter.SOUTH, critter.EAST, critter.WEST]
		rand = random.randint(0, len(moves)-1)
		return moves[rand]

	def getChar(self):
		return "R"

	# we don't learn, so no need for interactionOver
