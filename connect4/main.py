import pygame
from src.game import Game
from src.ui import UI
from src.menu import Menu

WIN_W = 700
WIN_H = 720


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Connect Four")
    clock = pygame.time.Clock()

    menu = Menu(screen, clock)

    while True:
        mode = menu.run()
        if mode == "quit":
            break

        game = Game()
        ui = UI(game, mode)
        result = ui.run()

        if result == "quit":
            break

    pygame.quit()


if __name__ == "__main__":
    main()