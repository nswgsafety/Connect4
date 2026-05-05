import pygame
import sys
import random
import src.theme as T

BET_OPTIONS = [10, 25, 50, 100]

CARD_W = 72
CARD_H = 105


# ------------------------------------------------------------------ data classes

class Card:
    SUITS = ["♠", "♥", "♦", "♣"]
    RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

    def __init__(self, rank, suit, hidden=False):
        self.rank   = rank
        self.suit   = suit
        self.hidden = hidden

    def value(self):
        if self.rank in ("J", "Q", "K"):
            return 10
        if self.rank == "A":
            return 11
        return int(self.rank)

    def is_red(self):
        return self.suit in ("♥", "♦")


class Deck:
    def __init__(self):
        self.cards = [Card(r, s) for s in Card.SUITS for r in Card.RANKS]
        random.shuffle(self.cards)

    def draw(self):
        return self.cards.pop()


class BlackjackGame:
    def __init__(self):
        self.deck         = Deck()
        self.player_hand  = []
        self.dealer_hand  = []
        self.state        = "betting"   # betting | playing | done
        self.result       = None        # "win" | "blackjack" | "push" | "lose" | "bust"
        self.bet          = 0

    def start(self, bet):
        self.bet         = bet
        self.deck        = Deck()
        self.player_hand = [self.deck.draw(), self.deck.draw()]
        self.dealer_hand = [self.deck.draw(), self.deck.draw()]
        self.dealer_hand[1].hidden = True
        self.state       = "playing"
        self.result      = None

        if self._value(self.player_hand) == 21:
            self.dealer_hand[1].hidden = False
            self.state = "done"
            self.result = "push" if self._value(self.dealer_hand) == 21 else "blackjack"

    def hit(self):
        if self.state != "playing":
            return
        self.player_hand.append(self.deck.draw())
        if self._value(self.player_hand) > 21:
            self.state  = "done"
            self.result = "bust"

    def stand(self):
        if self.state != "playing":
            return
        self.dealer_hand[1].hidden = False
        while self._value(self.dealer_hand) < 17:
            self.dealer_hand.append(self.deck.draw())
        pv = self._value(self.player_hand)
        dv = self._value(self.dealer_hand)
        self.state = "done"
        if dv > 21 or pv > dv:
            self.result = "win"
        elif pv < dv:
            self.result = "lose"
        else:
            self.result = "push"

    def payout(self):
        if self.result == "blackjack": return int(self.bet * 2.5)
        if self.result == "win":       return self.bet * 2
        if self.result == "push":      return self.bet
        return 0

    def player_value(self):
        return self._value(self.player_hand)

    def dealer_value(self):
        return self._value(self.dealer_hand)

    def _value(self, hand):
        total = sum(c.value() for c in hand if not c.hidden)
        aces  = sum(1 for c in hand if c.rank == "A" and not c.hidden)
        while total > 21 and aces:
            total -= 10
            aces  -= 1
        return total


# ------------------------------------------------------------------ UI

class BlackjackUI:
    def __init__(self, screen, clock, wallet):
        self.screen = screen
        self.clock  = clock
        self.wallet = wallet
        self.game   = BlackjackGame()

        self.font_xl = pygame.font.SysFont("arial", 36, bold=True)
        self.font_lg = pygame.font.SysFont("arial", 26, bold=True)
        self.font_md = pygame.font.SysFont("arial", 20, bold=True)
        self.font_sm = pygame.font.SysFont("arial", 15)

    def run(self):
        while True:
            if self.wallet.is_broke():
                self._broke_screen()
                return

            bet = self._bet_screen()
            if bet is None:
                return

            self.game.start(bet)
            result = self._play_screen(bet)
            if result == "quit":
                return

    # ---------------------------------------------------------------- screens

    def _bet_screen(self):
        btn_w   = 110
        btn_h   = 65
        gap     = 14
        total   = len(BET_OPTIONS) * btn_w + (len(BET_OPTIONS) - 1) * gap
        start_x = T.WIN_W // 2 - total // 2
        btn_y   = T.WIN_H // 2 + 20

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

            self._draw_table()

            title = self.font_xl.render("Blackjack", True, T.TEXT)
            self.screen.blit(title, (T.WIN_W // 2 - title.get_width() // 2, T.WIN_H // 2 - 120))

            bal = self.font_md.render(f"Wallet: ${self.wallet.balance}", True, T.NEON_CYN)
            self.screen.blit(bal, (T.WIN_W // 2 - bal.get_width() // 2, T.WIN_H // 2 - 60))

            for rect, amount in zip(bet_rects, BET_OPTIONS):
                can    = self.wallet.can_bet(amount)
                hov    = rect.collidepoint(mouse) and can
                bg     = T.BTN_HOV if hov else (T.BTN if can else (8, 12, 30))
                border = T.BTN_BDR if can else T.DIM
                T.draw_panel(self.screen, rect, bg, border)
                lbl = self.font_md.render(f"${amount}", True, T.TEXT if can else T.DIM)
                self.screen.blit(lbl, (rect.centerx - lbl.get_width() // 2,
                                       rect.centery - lbl.get_height() // 2))

            T.draw_btn(self.screen, back_x, back_y, back_w, back_h, "Back", mouse, self.font_md)
            pygame.display.flip()

    def _play_screen(self, bet):
        hit_w, hit_h = 150, 54
        std_w, std_h = 150, 54
        gap   = 20
        hit_x = T.WIN_W // 2 - hit_w - gap // 2
        std_x = T.WIN_W // 2 + gap // 2
        btn_y = T.WIN_H - 90

        cont_w, cont_h = 200, 52
        cont_x = T.WIN_W // 2 - cont_w // 2
        cont_y = T.WIN_H - 80

        while True:
            self.clock.tick(60)
            mouse = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return "quit"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game.state == "playing":
                        if pygame.Rect(hit_x, btn_y, hit_w, hit_h).collidepoint(mouse):
                            self.game.hit()
                        if pygame.Rect(std_x, btn_y, std_w, std_h).collidepoint(mouse):
                            self.game.stand()
                    elif self.game.state == "done":
                        if pygame.Rect(cont_x, cont_y, cont_w, cont_h).collidepoint(mouse):
                            payout = self.game.payout()
                            if payout > 0:
                                self.wallet.payout(payout)
                            return "continue"

            self._draw_table()
            self._draw_header(bet)
            self._draw_dealer_hand()
            self._draw_player_hand()

            if self.game.state == "playing":
                T.draw_btn(self.screen, hit_x, btn_y, hit_w, hit_h, "Hit",   mouse, self.font_md)
                T.draw_btn(self.screen, std_x, btn_y, std_w, std_h, "Stand", mouse, self.font_md)
            elif self.game.state == "done":
                self._draw_result()
                T.draw_btn(self.screen, cont_x, cont_y, cont_w, cont_h, "Continue", mouse, self.font_md)

            pygame.display.flip()

    def _draw_table(self):
        # Green felt background
        self.screen.fill(T.TABLE_GRN)
        # Darker center oval decoration
        oval = pygame.Rect(T.WIN_W // 2 - 280, T.WIN_H // 2 - 200, 560, 400)
        pygame.draw.ellipse(self.screen, T.TABLE_GRN_LT, oval, 3)

    def _draw_header(self, bet):
        bal  = self.font_sm.render(f"Wallet: ${self.wallet.balance}   Bet: ${bet}", True, T.NEON_CYN)
        self.screen.blit(bal, (T.WIN_W // 2 - bal.get_width() // 2, 14))

        title = self.font_md.render("BLACKJACK", True, T.TEXT)
        self.screen.blit(title, (T.WIN_W // 2 - title.get_width() // 2, 38))

    def _draw_dealer_hand(self):
        label = self.font_sm.render(
            f"Dealer: {self.game.dealer_value()}" if not any(c.hidden for c in self.game.dealer_hand) else "Dealer",
            True, T.TEXT
        )
        self.screen.blit(label, (T.WIN_W // 2 - label.get_width() // 2, 75))

        self._draw_hand(self.game.dealer_hand, 100)

    def _draw_player_hand(self):
        val   = self.game.player_value()
        color = T.P1_RED if val > 21 else T.TEXT
        label = self.font_sm.render(f"You: {val}", True, color)
        self.screen.blit(label, (T.WIN_W // 2 - label.get_width() // 2, T.WIN_H // 2 + 40))

        self._draw_hand(self.game.player_hand, T.WIN_H // 2 + 60)

    def _draw_hand(self, hand, top_y):
        total_w = len(hand) * CARD_W + (len(hand) - 1) * 10
        start_x = T.WIN_W // 2 - total_w // 2

        for i, card in enumerate(hand):
            x = start_x + i * (CARD_W + 10)
            T.draw_card(self.screen, x, top_y, CARD_W, CARD_H,
                        card.rank, card.suit, card.hidden)

    def _draw_result(self):
        result_msgs = {
            "win":       ("You Win!",    T.WIN_GRN),
            "blackjack": ("Blackjack!",  T.P2_GOLD),
            "push":      ("Push.",       T.TEXT),
            "lose":      ("Dealer Wins.", T.P1_RED),
            "bust":      ("Bust!",       T.P1_RED),
        }
        msg, color = result_msgs.get(self.game.result, ("", T.TEXT))

        payout = self.game.payout()
        if payout > 0:
            detail = f"+${payout}"
        elif self.game.result in ("lose", "bust"):
            detail = f"-${self.game.bet}"
        else:
            detail = ""

        overlay = pygame.Surface((T.WIN_W, 80), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, T.WIN_H // 2 - 10))

        surf  = self.font_xl.render(msg, True, color)
        surf2 = self.font_md.render(detail, True, color)
        self.screen.blit(surf,  (T.WIN_W // 2 - surf.get_width()  // 2, T.WIN_H // 2 - 5))
        self.screen.blit(surf2, (T.WIN_W // 2 - surf2.get_width() // 2, T.WIN_H // 2 + 38))

    def _broke_screen(self):
        btn_w, btn_h = 220, 52
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

            self._draw_table()
            t1 = self.font_xl.render("You're Broke.", True, T.P1_RED)
            t2 = self.font_md.render("Better luck next time.", True, T.DIM)
            self.screen.blit(t1, (T.WIN_W // 2 - t1.get_width() // 2, T.WIN_H // 2 - 50))
            self.screen.blit(t2, (T.WIN_W // 2 - t2.get_width() // 2, T.WIN_H // 2 + 10))
            T.draw_btn(self.screen, btn_x, btn_y, btn_w, btn_h, "Reset Wallet ($500)", mouse, self.font_md)
            pygame.display.flip()