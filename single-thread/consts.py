#!/usr/bin/env python3
import enum

class GameStatus(enum.Enum):
  PLAYING = 1,
  PAUSED = 2,
  OVER = 3,
  HOME = 4,
  QUIT = 5

GAME_NAME = 'The Spaceship Game'
SPACE_SHIP_SYMBOL = 'Y'
SPACE_ROCK_SYMBOL = chr(0x2593)

MIN_HEIGHT = 20
MIN_WIDTH = 35