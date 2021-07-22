## Space Jam Game

This is a simple game where a spaceship needs to dodge space-rocks. This is a game that can be played on a bash terminal. 

## Tested on 

- Ubuntu 18.04 (using default gnome-terminal)
- Python 3.7+

## Running the game

1. Clone or download the repository.
2. Navigate to the repository's folder.
3. Run the command:<br>
    `cd single-thread && python3 game.py`

Here is a YouTube video (TODO) of the game in action.

## Pending Improvements
- A windy mode where the spaceship's speed can increase and decrease based on space-winds.
- If user (Q)uits while playing a game, prompt user if they wish to quit the game.
- Non-blocking version which can help reduce the impact of clock drifts.
- Use Object Oriented principles to refactor game.
- Make the program easily debugable (painful at the moment due to intricacies with Python's curses module)

