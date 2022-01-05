import critter
import color
import random

class Pouncer(critter.Critter):
	def interact(self, oppInfo):
		return critter.POUNCE

	def getColor(self):
		return color.GRAY

	def getMove(self, info):
		moves = [critter.NORTH, critter.SOUTH, critter.EAST, critter.WEST]
		rand = random.randint(0, len(moves)-1)
		return moves[rand]

	def getChar(self):
		return "P"

	# we don't learn, so no need for interactionOver
