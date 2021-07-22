#!/usr/bin/env python3
import curses
import random
import collections
from consts import *


def initGameState(s, config):
  if config.border_flag == 1:
    s['border'] = 1
  else:
    s['border'] = 0

  s['lines'] = config.canvas_height - 1 - s['border']
  s['width'] = config.canvas_width - (2*s['border'])

  s['rows'] = collections.deque(maxlen=s['lines'])
  s['user_position'] = 0
  s['game_quit'] = False
  s['game_screen'] = GameStatus.HOME # PLAYING, HOME
  s['game_running'] = False
  s['game_paused'] = False
  s['score'] = 0
  s['scroll_speed'] = 1000 # in ms
  s['note'] = ''
  s['window'] = None

  # all rows are initialized with no rocks
  for n in range(s['lines']):
    s['rows'].append([' '] * s['width'])

def changeScrollSpeed(s, mode='increase', by_ms=100, min=200):
  if mode == 'increase':
    s['scroll_speed'] = max(s['scroll_speed'] - by_ms, min)
  elif mode == 'decrease':
    s['scroll_speed'] += by_ms

def updateGameState(s):
  rs = random.sample(range(0, s['width']), random.sample(range(3, int(0.3*s['width'])), 1)[0])
  s['rows'].append([' '] * s['width'])

  for r in rs:
    s['rows'][-1][r] = SPACE_ROCK_SYMBOL

  if s['rows'][0][s['user_position']] == SPACE_ROCK_SYMBOL:
    s['game_screen'] = GameStatus.HOME
    s['game_running'] = False
    s['note'] = 'Game over! Score: {} Level: {}'.format(s['score'], s['scroll_speed'])
  s['score'] = s['score'] + 1
  if s['score'] % 5 == 0:
    changeScrollSpeed(s)

def renderTextCenter(window, text, s, x_offset=0, y_offset=0, text_options = curses.A_NORMAL):
  window.addstr(int(int(s['lines']) / 2) + y_offset, int(s['width'] / 2) - int(len(text) / 2) + x_offset, text, text_options)

def renderScreen(s):
  if s['game_screen'] == GameStatus.PLAYING and not s['game_paused']:
    for n in range(s['lines']):
      s['window'].addstr(n, s['border'], ''.join(s['rows'][s['lines']-n-1]))
    s['window'].addstr(s['lines']-1, s['user_position'] + s['border'], SPACE_SHIP_SYMBOL,
                  curses.A_BOLD)
    menu_opts = ' (P) Pause | (Q) Quit '
    current_score = ' Score: {0: <5}'.format(str(s['score']))
    menu_opts = '{}{}'.format(menu_opts, ' ' * int(s['width'] - len(menu_opts) - len(current_score)))

    s['window'].addstr(s['lines'], s['border'], menu_opts, curses.A_REVERSE)
    s['window'].addstr(s['lines'], len(menu_opts)-1, current_score, curses.A_BOLD)
  if s['game_paused']:
    s['window'].erase()
    msg = 'Game paused! (Press <P> to continue)'
    renderTextCenter(s['window'], msg, s)
  elif s['game_screen'] == GameStatus.HOME:
    s['window'].erase()
    renderTextCenter(s['window'], '{}!'.format(GAME_NAME), s, y_offset=-2, text_options=curses.A_STANDOUT)
    renderTextCenter(s['window'], 'Press space-bar or <N> to start a new game!', s)
  updateNote(s)
  if s['border']: s['window'].border()
  s['window'].refresh()

def printToScreen(s, txt='Nothing'):
  s['window'].addstr(0, 0, txt, curses.A_BLINK)
  s['window'].refresh()

def updateNote(s, last_line=True, center_align=True):
  x_pos = int(s['width'] / 2) - int(len(s['note']) / 2) if center_align else 0
  y_pos = s['lines'] if last_line else 0

  s['window'].addstr(y_pos, x_pos, s['note'], curses.A_BLINK)
  return

def resetGameState(s):
  s['score'] = 0
  s['scroll_speed'] = 1000  # in ms
  s['note'] = ''
  s['user_position'] = 0
  s['game_paused'] = False
  s['game_running'] = True

  for n in range(s['lines']):
    s['rows'].append([' '] * s['width'])

def checkDimensions(scr, game_config):
  term_dimensions = scr.getmaxyx()

  if term_dimensions[0] < game_config.canvas_height or game_config.canvas_height < MIN_HEIGHT:
    return False

  if term_dimensions[1] < game_config.canvas_width or game_config.canvas_width < MIN_WIDTH:
    return False
  return True

def updateDimensions(scr, s):
  s['screen_dimensions'] = scr.getmaxyx()
  return True