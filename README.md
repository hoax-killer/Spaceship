## Space Jam Game

This is a simple game where a spaceship needs to dodge space-rocks. This is a game that can be played on a bash terminal. 

## Tested On 

- Ubuntu 18.04 (using default gnome-terminal) or macOS Big Sur 11.4 (using Terminal app)
- Python 3.7+

## Running The Game

1. Clone or download the repository.
2. Navigate to the repository's folder.
3. Run the command:<br>
    `cd single-thread && python3 game.py`

Here is a [YouTube video](https://youtu.be/B9yT61-XaVc) of the game in action.

### Command-Line Arguments and Options

```
terminal$ python3 game.py -h
usage: game.py [-h] [-l CANVAS_HEIGHT] [-w CANVAS_WIDTH] [-b BORDER_FLAG]
               [-v SPEED] [-d DENSITY] [-m MODE]

The Space Jam Game options

optional arguments:
  -h, --help            show this help message and exit
  -l CANVAS_HEIGHT, --canvas_height CANVAS_HEIGHT
                        Height of the game's window (i.e. # of lines) >= 20
  -w CANVAS_WIDTH, --canvas_width CANVAS_WIDTH
                        Width of the game window (i.e. # of characters per line) >= 60.
  -b BORDER_FLAG, --border_flag BORDER_FLAG
                        Whether to use border or no border.
  -v SPEED, --speed SPEED
                        Speed of the incoming rocks, 1 (slow) to 5 (fast).
  -d DENSITY, --density DENSITY
                        The density of rocks, 1 (few) to 50 (many).
  -m MODE, --mode MODE  Game-mode. auto/static/windy*.
```

_\* not yet implemented!_

## Pending Improvements
- A windy mode where the spaceship's speed can increase and decrease based on space-winds.
- Reduce time drafts (see [Issue #1](https://github.com/hoax-killer/Spaceship/issues/1))
- If user (Q)uits while playing a game, prompt user if they wish to quit the game.
- Non-blocking version which can help reduce the impact of clock drifts.
- Use Object Oriented principles to refactor game.
- Make the program easily debugable (painful at the moment due to intricacies with Python's curses module)

