#!/usr/bin/env python3
import argparse
import signal
import sys
import time
from game_utils import *

def init_window(window_params):
  window = curses.newwin(window_params.canvas_height, window_params.canvas_width, window_params.begin_y,
                         window_params.begin_x)
  window.nodelay(True)
  window.keypad(True)
  return window


parser = argparse.ArgumentParser(description='{} options'.format(GAME_NAME))
parser.add_argument('-l', '--canvas_height', type=int, default='10', help='Height of the game\'s window (i.e. # of lines) >= {}'.format(MIN_HEIGHT))
parser.add_argument('-w', '--canvas_width', type=int, default='50', help='Width of the game window (i.e. # of characters per line) >= {}'.format(MIN_WIDTH))
parser.add_argument('-b', '--border_flag', type=int, default='1', help='Whether to use border or no border')
parser.add_argument('-g', '--game-level', type=int, default='0', help='Game window\'s X-Axis offset (i.e. number of characters to leave as padding on the left')

# Game window's offsets (both are hidden args)
#  Y-Axis offset (i.e. number of lines to leave as margin on top) or X-Axis
#  X-Axis offset (i.e. number of characters to leave as padding on the left
parser.add_argument('-y', '--begin_y', type=int, default='0', help=argparse.SUPPRESS)
parser.add_argument('-x', '--begin_x', type=int, default='0', help=argparse.SUPPRESS)

# Populate game configuration by parsing the known command-line arguments
game_config, unknown = parser.parse_known_args()

# Game's state is maintained as a simple Python dictonary
state = dict()

if __name__ == "__main__":
  try:

    scr = curses.initscr()
    curses.beep()
    curses.noecho()
    curses.cbreak()
    curses.start_color()
    curses.curs_set(0)

    state['screen_dimensions'] = scr.getmaxyx()

    # check if terminal can fit the game window
    if not checkDimensions(scr, game_config):
      curses.endwin()
      print()
      print('Please read the following and take steps to re-size and play the game.')
      if game_config.canvas_height < MIN_HEIGHT:
        print(
          "\n# The --canvas-height/-l argument should have a minimum value of {}. Currently, it's set to {}.".format(
            MIN_HEIGHT, game_config.canvas_height))
      if game_config.canvas_width < MIN_WIDTH:
        print(
          "\n# The --canvas-width/-w argument should have a minimum value of {}. Currently, it's set to {}.".format(
            MIN_WIDTH, game_config.canvas_width))
      if state['screen_dimensions'][0] < game_config.canvas_height:
        print("\n# Your terminal's height is {} but is configured to run with {} rows. Please resize and increase the terminal's height.".format(state['screen_dimensions'][0], game_config.canvas_height))
      if state['screen_dimensions'][1] < game_config.canvas_width:
        print("\n# Your terminal's width is {} but is configured to run with {} characters. Please resize and increase the terminal's width.".format(state['screen_dimensions'][1], game_config.canvas_width))
      print()

      sys.exit(0)
      quit()

    ## initialize the state of the game
    initGameState(state, game_config)

    state['screen_dimensions'] = scr.getmaxyx()

    ## start window
    state['window'] = init_window(game_config)

    renderScreen(state)

    start = time.time()

    # Game app. is running
    while not state['game_quit']:

      # get keystroke
      keystroke = state['window'].getch()

      # Did user just resize the terminal? How do we handle this?
      if keystroke == curses.KEY_RESIZE:
        # Pause the game!
        if not state['game_paused']:
          state['game_paused'] = not state['game_paused']
          state['window'].nodelay(not state['game_paused'])

        # Check if the resized terminal dimensions is compatible
        if checkDimensions(scr, game_config):
          state['note'] = 'Terminal resized. Press <P> to continue.'
        else:
          state['note'] = 'Term dim incompatible'

      # User intends to pause or resume the game.
      if keystroke == ord('p'):
        state['game_paused'] = not state['game_paused']
        state['window'].nodelay(not state['game_paused'])
        state['note'] = ''

      # update the game's state
      if (time.time() - start)*1000 >= state['scroll_speed'] and not state['game_paused']:
        start = time.time()
        updateGameState(state)

      # User intends to start a new game
      if state['game_screen'] == GameStatus.HOME and (keystroke == ord('n') or keystroke == ord(' ')):
        resetGameState(state)
        state['game_screen'] = GameStatus.PLAYING
        state['window'].nodelay(True)

      # Quit game?
      if keystroke == ord('q'):
        state['game_quit'] = True
        state['game_screen'] = GameStatus.HOME

      # User moving the spaceship in left or right directions
      if keystroke == curses.KEY_RIGHT:
        state['user_position'] = min(state['user_position']+1, state['width']-1)
      elif keystroke == curses.KEY_LEFT:
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
    print('\n\nThank you for trying out {}!\n\n'.format(GAME_NAME))