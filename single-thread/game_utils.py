#!/usr/bin/env python3
import curses
import random
import collections
from consts import *


def initGameState(s, config):
  '''Allocates data structures for the game's state and initializes them to default values'''

  if config.border_flag == 1:
    s['border'] = 1
  else:
    s['border'] = 0

  # based on the border-config/canvas size, etc. adjust the game window's renderable area
  s['lines'] = config.canvas_height - 1 - s['border']
  s['width'] = config.canvas_width - (2 * s['border'])

  # if valid, set rock density to configured value else set it to default
  # TODO: hardcoded default value
  s['density'] = config.density if 1 <= config.density <= 50 else 20

  s['mode'] = config.mode

  # Data structures to store rock data
  s['rows'] = collections.deque(maxlen=s['lines'])
  s['rocks'] = collections.deque(maxlen=s['lines'])
  s['window'] = None

  # initialize the state to default values
  resetGameState(s, config)


def changeScrollSpeed(s, mode='increase', by_ms=200, min=200):
  '''Called to change the scroll speed of the rocks'''
  if mode == 'increase':
    s['scroll_speed'] = max(s['scroll_speed'] - by_ms, min)
  elif mode == 'decrease':
    s['scroll_speed'] += by_ms


def updateGameState(s):
  '''Updates the state periodically. E.g., adding a new row with rocks on top, checking if user is hit by rock'''

  # randomly generate rocks
  rs = random.sample(range(0, s['width']), random.sample(range(3, int((s['density'] / 100) * s['width'])), 1)[0])

  # NOTE: deque's append also rotate's the data structure.
  s['rows'].append([' '] * s['width'])
  s['rocks'].append(len(rs))

  for r in rs:
    s['rows'][-1][r] = SPACE_ROCK_SYMBOL

  # check if user hit the rock!
  if s['rows'][0][s['user_position']] == SPACE_ROCK_SYMBOL:
    s['game_screen'] = ScreenType.HOME
    s['game_running'] = False
    s['note'] = 'Game over!'
    s['note'] += '\nWoW! Successfully dodging a total of {} space rocks,'.format(s['rocks_dodged'])
    s['note'] += '\nyou space-traveled a distance of {} rows '.format(s['score'])
    s['note'] += '\nin {:.2f} space-seconds (ss) '.format(s['time_played'] / 1000)
    s['note'] += '\nat a maximum speed of {} rows/ss!'.format(6 - int(s['scroll_speed'] / 200))
  else:
    # user is safe, update scores
    s['score'] = s['score'] + 1
    s['rocks_dodged'] = s['rocks_dodged'] + s['rocks'][0]
    s['time_played'] = s['time_played'] + s['scroll_speed']
    if s['mode'] != 'static' and s['score'] % int(s['lines']) == 0:
      changeScrollSpeed(s)


def renderTextCenter(window, text, s, x_offset=0, y_offset=0, text_options=curses.A_NORMAL):
  '''helper function to add text to screen relative to the center of the game's window'''
  window.addstr(int(int(s['lines']) / 2) + y_offset, int(s['width'] / 2) - int(len(text) / 2) + x_offset, text,
                text_options)

def renderScreen(s):
  '''use game's state to render the game's screen'''

  if not s['dim_not_compatible']:
    if s['game_screen'] == ScreenType.PLAYING and not s['game_paused']:
      # render an active game's screen

      for n in range(s['lines']):
        s['window'].addstr(n, s['border'], ''.join(s['rows'][s['lines'] - n - 1]))
      s['window'].addstr(s['lines'] - 1, s['user_position'] + s['border'], SPACE_SHIP_SYMBOL,
                         curses.A_BOLD)
      menu_opts = ' (P)ause | (Q)uit '
      current_score = ' Distance: {0: <4} | Speed: {1: <1} | Rocks: {2: <4}'.format(str(s['score']),
                                                                                    6 - int(s['scroll_speed'] / 200),
                                                                                    s['rocks_dodged'])
      menu_opts = '{}{}'.format(menu_opts, ' ' * int(s['width'] - len(menu_opts) - len(current_score)))

      s['window'].addstr(s['lines'], s['border'], menu_opts, curses.A_REVERSE)
      s['window'].addstr(s['lines'], len(menu_opts) - 1, current_score, curses.A_BOLD)
    elif s['game_paused']:
      s['window'].erase()
      msg = 'Game paused! (Press <P> to continue)'
      renderTextCenter(s['window'], msg, s)
    elif s['game_screen'] == ScreenType.HOME:
      s['window'].erase()
      renderTextCenter(s['window'], '{}!'.format(GAME_NAME), s, y_offset=-5, text_options=curses.A_STANDOUT)
      renderTextCenter(s['window'], 'Press space-bar or <N> to start a new game!', s, y_offset=-2)
      renderTextCenter(s['window'], 'Use <LEFT> or <RIGHT> keys to move either sides.', s, y_offset=0)
      renderTextCenter(s['window'], 'Use <UP> key to accelerate.', s, y_offset=1)

    updateNote(s)
    if s['border']: s['window'].border(0)
  else:
    s['window'].clear()
    s['window'].addstr(1, 1, s['note'], curses.A_BLINK)
  s['window'].refresh()

def printToScreen(s, txt='Nothing'):
  s['window'].addstr(0, 0, txt, curses.A_BLINK)
  s['window'].refresh()

def updateNote(s, last_line=True, center_align=True):
  '''a function to display note in the last line of screen's dimensions'''
  txts = s['note'].split('\n')[::-1]
  for line, txt in enumerate(txts):
    x_pos = int(s['width'] / 2) - int(len(txt) / 2) if center_align else 0
    y_pos = s['lines'] - line if last_line else 0

    s['window'].addstr(y_pos, x_pos, txt, curses.A_BLINK)
  return


def resetGameState(s, config):
  '''reset the game's state'''
  s['user_position'] = int(s['width'] / 2)
  s['game_quit'] = False
  s['game_screen'] = ScreenType.HOME  # PLAYING, HOME
  s['game_running'] = False
  s['game_paused'] = False
  s['score'] = 0
  s['rocks_dodged'] = 0
  s['time_played'] = 0

  if config.mode == 'static' and config.speed >= 1 and config.speed <= 5:
    s['scroll_speed'] = 1200 - (int(config.speed) * 200)
  else:
    s['scroll_speed'] = 1000  # in ms

  s['note'] = ''
  s['dim_not_compatible'] = False

  # all rows are initialized with no rocks
  for n in range(s['lines']):
    s['rows'].append([' '] * s['width'])
    s['rocks'].append(0)


def checkDimensions(scr, game_config):
  '''check if the screen's dimensions match the user-given canvas dimension parameters'''
  term_dimensions = scr.getmaxyx()

  if term_dimensions[0] < game_config.canvas_height or game_config.canvas_height < MIN_HEIGHT:
    return False

  if term_dimensions[1] < game_config.canvas_width or game_config.canvas_width < MIN_WIDTH:
    return False
  return True