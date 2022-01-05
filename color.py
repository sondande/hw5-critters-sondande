import collections

# Python doesn't have a color object, so it's just an (r, g, b) tuple.

Color = collections.namedtuple('Color', ['r', 'g', 'b'])

GRAY = Color(128, 128, 128)
BLACK = Color(0, 0, 0)
ORANGE = Color(255, 165, 0)
RED = Color(255, 0, 0)
GREEN = Color(0, 255, 0)
BLUE = Color(0, 0, 255)
PURPLE = Color(186, 85, 211)
YELLOW = Color(255, 255, 0)
