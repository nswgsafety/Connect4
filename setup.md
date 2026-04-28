# THIS IS GOING TO BE THE FILE THAT INTRODUCES THE OUTLINE FOR THE PROJECT'

PROJECT STRUCTURE

connect4/
  src/
    cell.py     # One slot on the board.
    board.py    # 6x7 grid of cells. Drops pieces. Checks if columns are full.
    player.py   # Stores name, symbol, color, and score.
    game.py     # Manages turns, win detection across 4 directions, and state.
    ai.py       # Minimax AI with alpha-beta pruning.
    menu.py     # Main menu screen (mode selection).
    ui.py       # Pygame game screen, animations, and result overlay.
  main.py       # Entry point. Runs menu -> game loop.
  requirements.txt