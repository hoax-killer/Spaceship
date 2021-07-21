#!/usr/bin/env python3
import curses
import argparse
import signal
import sys
import time
from game_utils import *

class GameStatus(enum.Enum):
  PLAYING = 1,
  PAUSED = 2,
  OVER = 3,
  HOME = 4,
  QUIT = 5

def signal_handler(sig, frame):
  curses.endwin()
  print('You pressed Control+C')
  sys.exit(0)

def init_window(window_params):
  window = curses.newwin(window_params.canvas_height, window_params.canvas_width, window_params.begin_y, window_params.begin_x)
  window.nodelay(True)
  window.keypad(True)
  return window


parser = argparse.ArgumentParser(description='{} options'.format(GAME_NAME))
parser.add_argument('--canvas_height', type=int, default='10', help='a number to specify your game window height')
parser.add_argument('--canvas_width', type=int, default='50', help='a number to specify your game window width')
parser.add_argument('--begin_y', type=int, default='0')
parser.add_argument('--begin_x', type=int, default='0')

state = dict()
global window

game_config, unknown = parser.parse_known_args()

def initGameState(s, config):
  s['lines'] = config.canvas_height - 1
  s['width'] = config.canvas_width
  s['rows'] = collections.deque(maxlen=s['lines'])
  s['user_position'] = 0
  s['game_quit'] = False
  s['game_screen'] = GameStatus.HOME # PLAYING, HOME
  s['game_running'] = False
  s['game_paused'] = False
  s['score'] = 0
  s['scroll_speed'] = 1000 # in ms
  s['note'] = ''

  for n in range(s['lines']):
    s['rows'].append([' '] * s['width'])

SPACE_SHIP_SYMBOL = 'Y'
SPACE_ROCK_SYMBOL = chr(0x2593)



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
    s['note'] = 'Game over! Score: {} Level: {}'.format(state['score'], state['scroll_speed'])
  s['score'] = s['score'] + 1
  if s['score'] % 5 == 0:
    changeScrollSpeed(s)

def renderTextCenter(window, text, s, x_offset=0, y_offset=0, text_options = curses.A_NORMAL):
  window.addstr(int(int(s['lines']) / 2) + y_offset, int(s['width'] / 2) - int(len(text) / 2) + x_offset, text, text_options)

def renderScreen(s):
  if s['game_screen'] == GameStatus.PLAYING and not state['game_paused']:
    for n in range(s['lines']):
      window.addstr(n, 0, ''.join(state['rows'][s['lines']-n-1]))
    window.addstr(s['lines']-1, s['user_position'], SPACE_SHIP_SYMBOL,
                  curses.A_BOLD)
    window.addstr(s['lines'], 0, '(P) Pause  |  (Q) Quit',
                  curses.A_REVERSE)
    window.addstr(s['lines'], 30, ' Score: {}'.format(str(s['score']).zfill(3)),
                  curses.A_BOLD)
  if s['game_paused']:
    window.erase()
    msg = 'Game paused! (Press <P> to continue)'
    renderTextCenter(window, msg, s)
  elif s['game_screen'] == GameStatus.HOME:
    window.erase()
    renderTextCenter(window, 'The Spaceship Game!', s, y_offset=-2, text_options=curses.A_STANDOUT)
    renderTextCenter(window, 'Press space-bar or <N> to start a new game!', s)
  updateNote(s)
  window.refresh()

def printToScreen(txt='Nothing'):
  window.addstr(0, 0, txt, curses.A_BLINK)
  window.refresh()

def updateNote(s, last_line=True, center_align=True):
  x_pos = int(s['width'] / 2) - int(len(s['note']) / 2) if center_align else 0
  y_pos = s['lines'] if last_line else 0

  window.addstr(y_pos, x_pos, s['note'], curses.A_BLINK)
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
  # get terminal dimensions (height,width)
  term_dimensions = scr.getmaxyx()

  if term_dimensions[0] < game_config.canvas_height and term_dimensions[1] < game_config.canvas_width:
    return False
  return True

def updateDimensions(scr, s):
  s['screen_dimensions'] = scr.getmaxyx()
  return True

if __name__ == "__main__":
  try:

    scr = curses.initscr()
    curses.beep()
    curses.noecho()
    curses.cbreak()
    curses.start_color()
    curses.curs_set(0)

    ## initialize the state of the game
    initGameState(state, game_config)

    state['screen_dimensions'] = scr.getmaxyx()

    ## start window
    window = init_window(game_config)

    signal.signal(signal.SIGINT, signal_handler)
    print('Press Ctrl+C')

    renderScreen(state)

    start = time.time()

    # Game app. is running
    while not state['game_quit']:

      # get keystroke
      c = window.getch()

      # Did user just resize the terminal? How do we handle this?
      if c == curses.KEY_RESIZE:
        # Pause the game!
        if not state['game_paused']:
          state['game_paused'] = not state['game_paused']
          window.nodelay(not state['game_paused'])

        # Check if the resized terminal dimensions is compatible
        if checkDimensions(scr, game_config):
          state['note'] = 'Press (P) to resume'
        else:
          state['note'] = 'Term dim incompatible'

      # User intends to pause or resume the game.
      if c == ord('p'):
        state['game_paused'] = not state['game_paused']
        window.nodelay(not state['game_paused'])

      # update the game's state
      if (time.time() - start)*1000 >= state['scroll_speed'] and not state['game_paused']:
        start = time.time()
        updateGameState(state)

      # User intends to start a new game
      if state['game_screen'] == GameStatus.HOME and (c == ord('n') or c == ord(' ')):
        resetGameState(state)
        state['game_screen'] = GameStatus.PLAYING
        window.nodelay(True)

      # Quit game?
      if c == ord('q'):
        state['game_quit'] = False
        # state['game_status'] = GameStatus.OVER

      # User playing the game
      if c == curses.KEY_RIGHT:
        state['user_position'] = min(state['user_position']+1, state['width'])
      elif c == curses.KEY_LEFT:
        state['user_position'] = max(state['user_position'] - 1, 0)
      else:
        curses.beep()

      # render the screen
      renderScreen(state)


      if state['game_screen'] == GameStatus.HOME:
        window.nodelay(False)

    window.refresh()
    signal.pause()
    # rt.stop()
  except:
    print('Raised Exception')
  finally:
    print('Closing')
    curses.nocbreak()
    curses.echo()
    curses.curs_set(1)
    scr.keypad(0)
    curses.endwin()
    print('\n\nThank you for playing {}!\n\n'.format(GAME_NAME))