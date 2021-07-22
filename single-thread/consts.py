#!/usr/bin/env python3
import enum

class ScreenType(enum.Enum):
  PLAYING = 1,
  HOME = 2

GAME_NAME = 'The Space Jam Game'
SPACE_SHIP_SYMBOL = 'Y'
SPACE_ROCK_SYMBOL = chr(0x2593)

MIN_HEIGHT = 20
MIN_WIDTH = 60