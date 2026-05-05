import pygame
from src.game import Game
from src.ui import UI
from src.menu import Menu
from src.story_mode import StoryMode
from src.gambling import GamblingUI
from src.blackjack import BlackjackUI
from src.wallet import Wallet
import src.theme as T


def main():
    pygame.init()
    screen = pygame.display.set_mode((T.WIN_W, T.WIN_H))
    pygame.display.set_caption("Connect Four")
    clock  = pygame.time.Clock()

    wallet = Wallet()
    menu   = Menu(screen, clock, wallet)

    while True:
        result = menu.run()

        if result is None or result == "quit":
            break

        # pvai returns a tuple ("pvai", depth) from difficulty screen
        if isinstance(result, tuple) and result[0] == "pvai":
            _, depth = result
            game = Game()
            ui   = UI(game, "pvai", ai_depth=depth)
            ui.run()

        elif result == "pvp":
            game = Game()
            ui   = UI(game, "pvp")
            ui.run()

        elif result == "story":
            StoryMode(screen, clock).run()

        elif result == "gambling":
            GamblingUI(screen, clock, wallet).run()

        elif result == "blackjack":
            BlackjackUI(screen, clock, wallet).run()

    pygame.quit()


if __name__ == "__main__":
    main()