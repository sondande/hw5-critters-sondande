import critter
import color
import random

class Scratcher(critter.Critter):
	def interact(self, oppInfo):
		return critter.SCRATCH

	def getColor(self):
		return color.GRAY

	def getMove(self, info):
		moves = [critter.NORTH, critter.SOUTH, critter.EAST, critter.WEST]
		rand = random.randint(0, len(moves)-1)
		return moves[rand]

	def getChar(self):
		return "S"

	# we don't learn, so no need for interactionOver
