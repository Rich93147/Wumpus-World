# Wumpus-World
A 4x4 dungeon themed game controlled by AI made with search and decision making algorithms. Made for a school project. Assets provided. Check README for more information

PROJECT STRUCTURE (When testing this code, confirm you have this same structure)
project-root/
│
├── main.py          # Entry point for running the game
├── ai.py            # AI logic and decision-making
├── wumpus.py        # Game environment and rendering logic
├── requirements.txt # Python dependencies
│
├── imgs/            # Image assets used by the game (sprites, tiles, UI)
└── font/            # Font files used for rendering text

REQUIREMENTS
Python 3.10+

DEPENDENCIES
Pygame (install with pip using: pip install pygame)

HOW TO RUN:
After confirming proper program structure, run Main.py. A window will open up

Game documentation:
The AI runs off of precepts provided to the player. Wumpus' give off "stink" precepts that are given to the player when they stand on an adjacent square to a Wumpus. There can only be one Wumpus on the board.
The pits all give off "breeze" precepts on adjacent squares, there can be a random amount of pits. 
Gold gives off a precept only on the square it resides on. There can only be one gold on the board at a time.
Wumpus' and pits cannot spawn on the spawning point (1,1) which is the bottom left square. 
Gold can spawn on the spawning point.
Gold can also spawn on the Wumpus square, forcing the player to seek out the wumpus after all safe squares have been explored to kill the wumpus, grabbing the gold and escaping.
The player can only escape at the spawning point (1,1)
The player will escape without grabbing the gold if the AI determines the board is unsolvable, or gets a start that it cannot determine a safe route on turn one.
An unsolveable board is a board where pits obscure gold, making it impossible to traverse to the gold.
Each movement costs a single point, only one arrow is provided, grabbing the gold and escaping grants 1000 points.

Other game information is also provided in the files.

CREDITS
Prof. Atkinson at St.Edward's University for developing Wumpus.py, providing assets, and assigning this project.
