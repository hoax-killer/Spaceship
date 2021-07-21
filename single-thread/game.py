#!/usr/bin/env python3
import argparse
import signal
import sys
import time
from game_utils import *


def signal_handler(sig, frame):
  curses.endwin()
  sys.exit(0)

def init_window(window_params):
  window = curses.newwin(window_params.canvas_height, window_params.canvas_width, window_params.begin_y,
                         window_params.begin_x)
  window.nodelay(True)
  window.keypad(True)
  return window


parser = argparse.ArgumentParser(description='{} options'.format(GAME_NAME))
parser.add_argument('--canvas_height', type=int, default='10', help='a number to specify your game window height')
parser.add_argument('--canvas_width', type=int, default='50', help='a number to specify your game window width')
parser.add_argument('--begin_y', type=int, default='0')
parser.add_argument('--begin_x', type=int, default='0')

state = dict()

game_config, unknown = parser.parse_known_args()

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
    state['window'] = init_window(game_config)

    signal.signal(signal.SIGINT, signal_handler)
    print('Press Ctrl+C')

    renderScreen(state)

    start = time.time()

    # Game app. is running
    while not state['game_quit']:

      # get keystroke
      c = state['window'].getch()

      # Did user just resize the terminal? How do we handle this?
      if c == curses.KEY_RESIZE:
        # Pause the game!
        if not state['game_paused']:
          state['game_paused'] = not state['game_paused']
          state['window'].nodelay(not state['game_paused'])

        # Check if the resized terminal dimensions is compatible
        if checkDimensions(scr, game_config):
          state['note'] = 'Press (P) to resume'
        else:
          state['note'] = 'Term dim incompatible'

      # User intends to pause or resume the game.
      if c == ord('p'):
        state['game_paused'] = not state['game_paused']
        state['window'].nodelay(not state['game_paused'])

      # update the game's state
      if (time.time() - start)*1000 >= state['scroll_speed'] and not state['game_paused']:
        start = time.time()
        updateGameState(state)

      # User intends to start a new game
      if state['game_screen'] == GameStatus.HOME and (c == ord('n') or c == ord(' ')):
        resetGameState(state)
        state['game_screen'] = GameStatus.PLAYING
        state['window'].nodelay(True)

      # Quit game?
      if c == ord('q'):
        state['game_quit'] = True
        state['game_screen'] = GameStatus.HOME

      # User moving the spaceship in left or right directions
      if c == curses.KEY_RIGHT:
        state['user_position'] = min(state['user_position']+1, state['width'])
      elif c == curses.KEY_LEFT:
        state['user_position'] = max(state['user_position'] - 1, 0)

      # render the screen
      renderScreen(state)

      if state['game_screen'] == GameStatus.HOME:
        state['window'].nodelay(False)

    state['window'].refresh()
    # signal.pause()
  except SystemExit as e:
    pass
  except:
    print("Unexpected error:", sys.exc_info()[0])
  finally:
    # restore terminal settings
    curses.nocbreak()
    curses.echo()
    curses.curs_set(1)
    scr.keypad(0)
    curses.endwin()
    print('\n\nThank you for playing {}!\n\n'.format(GAME_NAME))