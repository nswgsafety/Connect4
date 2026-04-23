from src.game import Game
from src.ui import UI

def main():
    game = Game()
    ui = UI(game)
    ui.start()

if __name__ == "__main__":
    main()