import critter
import color
import random

class Partier(critter.Critter):
	def interact(self, oppInfo):
		return critter.PARTY

	def getColor(self):
		return color.RED

	def getMove(self, info):
		moves = [critter.NORTH, critter.SOUTH, critter.EAST, critter.WEST]
		rand = random.randint(0, len(moves)-1)
		return moves[rand]

	def getChar(self):
		return "P"

	# we don't learn, so no need for interactionOver
