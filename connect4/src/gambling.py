import pygame
import sys
import src.theme as T
from src.game import Game
from src.ui import UI
from src.ai import AI

BET_OPTIONS = [10, 25, 50, 100, 250]


class GamblingUI:
    def __init__(self, screen, clock, wallet):
        self.screen = screen
        self.clock  = clock
        self.wallet = wallet

        self.font_xl = pygame.font.SysFont("arial", 40, bold=True)
        self.font_lg = pygame.font.SysFont("arial", 28, bold=True)
        self.font_md = pygame.font.SysFont("arial", 20, bold=True)
        self.font_sm = pygame.font.SysFont("arial", 16)

    def run(self):
        while True:
            if self.wallet.is_broke():
                self._broke_screen()
                return

            bet = self._bet_screen()
            if bet is None:
                return

            winner = self._play_game(bet)
            self._payout_screen(bet, winner)

    def _play_game(self, bet):
        game = Game()
        ui   = UI(game, "gambling", ai_depth=AI.MEDIUM, wallet=self.wallet, bet=bet)
        return ui.run_single()

    # ---------------------------------------------------------------- screens

    def _bet_screen(self):
        btn_w  = 100
        btn_h  = 60
        gap    = 14
        total  = len(BET_OPTIONS) * btn_w + (len(BET_OPTIONS) - 1) * gap
        start_x = T.WIN_W // 2 - total // 2
        btn_y  = T.WIN_H // 2 + 10

        back_w, back_h = 140, 44
        back_x = T.WIN_W // 2 - back_w // 2
        back_y = btn_y + btn_h + 30

        bet_rects = [
            pygame.Rect(start_x + i * (btn_w + gap), btn_y, btn_w, btn_h)
            for i in range(len(BET_OPTIONS))
        ]

        while True:
            self.clock.tick(60)
            mouse = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for rect, amount in zip(bet_rects, BET_OPTIONS):
                        if rect.collidepoint(mouse) and self.wallet.can_bet(amount):
                            self.wallet.place_bet(amount)
                            return amount
                    if pygame.Rect(back_x, back_y, back_w, back_h).collidepoint(mouse):
                        return None

            T.draw_bg(self.screen)

            title = self.font_xl.render("Place Your Bet", True, T.TEXT)
            self.screen.blit(title, (T.WIN_W // 2 - title.get_width() // 2, T.WIN_H // 2 - 120))

            bal = self.font_md.render(f"Wallet: ${self.wallet.balance}", True, T.NEON_CYN)
            self.screen.blit(bal, (T.WIN_W // 2 - bal.get_width() // 2, T.WIN_H // 2 - 60))

            for rect, amount in zip(bet_rects, BET_OPTIONS):
                can     = self.wallet.can_bet(amount)
                hov     = rect.collidepoint(mouse) and can
                bg      = T.BTN_HOV if hov else (T.BTN if can else (8, 12, 30))
                border  = T.BTN_BDR if can else T.DIM
                T.draw_panel(self.screen, rect, bg, border)
                lbl = self.font_md.render(f"${amount}", True, T.TEXT if can else T.DIM)
                self.screen.blit(lbl, (rect.centerx - lbl.get_width() // 2,
                                       rect.centery - lbl.get_height() // 2))

            T.draw_btn(self.screen, back_x, back_y, back_w, back_h, "Back", mouse, self.font_md)
            pygame.display.flip()

    def _payout_screen(self, bet, winner):
        if winner == 0:
            winnings = bet * 2
            self.wallet.payout(winnings)
            color = T.WIN_GRN
            line1 = "You win!"
            line2 = f"+${winnings}  |  Wallet: ${self.wallet.balance}"
        elif winner == 1:
            color = T.P1_RED
            line1 = "CPU wins."
            line2 = f"-${bet}  |  Wallet: ${self.wallet.balance}"
        else:
            self.wallet.payout(bet)
            color = T.TEXT
            line1 = "Draw."
            line2 = f"Bet returned  |  Wallet: ${self.wallet.balance}"

        deadline = pygame.time.get_ticks() + 2800
        while pygame.time.get_ticks() < deadline:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    return

            T.draw_bg(self.screen)
            t1 = self.font_xl.render(line1, True, color)
            t2 = self.font_md.render(line2, True, T.TEXT)
            self.screen.blit(t1, (T.WIN_W // 2 - t1.get_width() // 2, T.WIN_H // 2 - 40))
            self.screen.blit(t2, (T.WIN_W // 2 - t2.get_width() // 2, T.WIN_H // 2 + 20))
            hint = self.font_sm.render("Press anything to continue", True, T.DIM)
            self.screen.blit(hint, (T.WIN_W // 2 - hint.get_width() // 2, T.WIN_H // 2 + 70))
            pygame.display.flip()

    def _broke_screen(self):
        btn_w, btn_h = 200, 52
        btn_x = T.WIN_W // 2 - btn_w // 2
        btn_y = T.WIN_H // 2 + 60

        while True:
            self.clock.tick(60)
            mouse = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pygame.Rect(btn_x, btn_y, btn_w, btn_h).collidepoint(mouse):
                        self.wallet.reset()
                        return

            T.draw_bg(self.screen)
            t1 = self.font_xl.render("You're Broke.", True, T.P1_RED)
            t2 = self.font_md.render("The house always wins.", True, T.DIM)
            self.screen.blit(t1, (T.WIN_W // 2 - t1.get_width() // 2, T.WIN_H // 2 - 50))
            self.screen.blit(t2, (T.WIN_W // 2 - t2.get_width() // 2, T.WIN_H // 2 + 10))
            T.draw_btn(self.screen, btn_x, btn_y, btn_w, btn_h, "Reset Wallet ($500)", mouse, self.font_md)
            pygame.display.flip()