from enum import Enum

class Color(tuple, Enum):
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GOLD = (11, 152, 222)
    RED = (0, 0, 255)
    BLUE = (255, 0, 0)
    GREEN = (0, 255, 0)
    YELLOW = (0, 255, 255)
    AQUA = (255, 255, 0)
    PINK = (147, 20, 255)
    TRANSPARENT = (0, 0, 0, 0)


    BACKGROUND_COLOR = TRANSPARENT
    PANEL_COLOR = (70, 70, 70)

