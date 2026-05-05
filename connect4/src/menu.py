import pygame
import sys
import math
import src.theme as T
from src.ai import AI

MODES = [
    {"key": "pvp",       "label": "Player vs Player",  "desc": "Two humans. No mercy.",                "color": T.P1_RED},
    {"key": "pvai",      "label": "Player vs CPU",     "desc": "Pick your difficulty and fight.",       "color": T.P2_GOLD},
    {"key": "story",     "label": "Story Mode",        "desc": "7 opponents. Each one harder.",         "color": T.NEON_CYN},
    {"key": "gambling",  "label": "Gambling Mode",     "desc": "Bet money. Win big. Lose bigger.",      "color": T.WIN_GRN},
    {"key": "blackjack", "label": "Blackjack",         "desc": "21 or bust. A casino classic.",         "color": T.NEON_PUR},
]

CARD_W = 540
CARD_H = 72
CARD_X = T.WIN_W // 2 - CARD_W // 2
CARD_GAP = 10
CARD_START_Y = 200


class Menu:
    def __init__(self, screen, clock, wallet):
        self.screen    = screen
        self.clock     = clock
        self.wallet    = wallet
        self.particles = [T.Particle() for _ in range(70)]

        self.font_xl  = pygame.font.SysFont("arial", 46, bold=True)
        self.font_lg  = pygame.font.SysFont("arial", 28, bold=True)
        self.font_md  = pygame.font.SysFont("arial", 18, bold=True)
        self.font_sm  = pygame.font.SysFont("arial", 14)
        self.font_xs  = pygame.font.SysFont("arial", 12)

    def run(self):
        rects = [
            pygame.Rect(CARD_X, CARD_START_Y + i * (CARD_H + CARD_GAP), CARD_W, CARD_H)
            for i in range(len(MODES))
        ]

        while True:
            self.clock.tick(60)
            mouse  = pygame.mouse.get_pos()
            ticks  = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i, rect in enumerate(rects):
                        if rect.collidepoint(mouse):
                            key = MODES[i]["key"]
                            if key == "pvai":
                                return self._difficulty_screen()
                            return key

            T.draw_bg_full(self.screen)

            for p in self.particles:
                p.update()
                p.draw(self.screen)

            self._draw_title(ticks)
            self._draw_wallet()

            for i, (rect, mode) in enumerate(zip(rects, MODES)):
                self._draw_mode_card(rect, mode, mouse)

            self._draw_footer()
            pygame.display.flip()

    # ─── difficulty sub-screen ────────────────────────────────────────────────

    def _difficulty_screen(self):
        options = [
            {"label": "Easy",   "depth": AI.EASY,   "desc": "Makes random mistakes.     Depth 2"},
            {"label": "Medium", "depth": AI.MEDIUM,  "desc": "Thinks 4 moves ahead.      Depth 4"},
            {"label": "Hard",   "depth": AI.HARD,    "desc": "Near-perfect. Good luck.   Depth 6"},
        ]
        btn_w, btn_h = 320, 72
        gap   = 12
        bx    = T.WIN_W // 2 - btn_w // 2
        ys    = [T.WIN_H // 2 - 55 + i * (btn_h + gap) for i in range(3)]
        bk_w, bk_h = 150, 46
        bk_x  = T.WIN_W // 2 - bk_w // 2
        bk_y  = ys[-1] + btn_h + 28

        colors = [T.WIN_GRN, T.P2_GOLD, T.P1_RED]

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
                    for opt, y in zip(options, ys):
                        if pygame.Rect(bx, y, btn_w, btn_h).collidepoint(mouse):
                            return ("pvai", opt["depth"])
                    if pygame.Rect(bk_x, bk_y, bk_w, bk_h).collidepoint(mouse):
                        return None

            T.draw_bg_full(self.screen)
            for p in self.particles:
                p.update()
                p.draw(self.screen)

            title = self.font_lg.render("Choose Difficulty", True, T.TEXT)
            self.screen.blit(title, (T.WIN_W // 2 - title.get_width() // 2,
                                     T.WIN_H // 2 - 155))

            for opt, y, col in zip(options, ys, colors):
                rect = pygame.Rect(bx, y, btn_w, btn_h)
                hov  = rect.collidepoint(mouse)

                if hov:
                    T.draw_glow_rect(self.screen, rect, col, passes=3, base_alpha=14)
                bg = T.BTN_HOV if hov else T.BTN
                T.draw_panel(self.screen, rect, bg, col if hov else T.BTN_BDR)

                # Left accent bar
                pygame.draw.rect(self.screen, col,
                                 (bx, y, 4, btn_h), border_radius=4)

                lbl  = self.font_md.render(opt["label"], True, T.TEXT)
                desc = self.font_xs.render(opt["desc"],  True, T.DIM)
                self.screen.blit(lbl,  (bx + 18, y + 16))
                self.screen.blit(desc, (bx + 18, y + 42))

            T.draw_btn(self.screen, bk_x, bk_y, bk_w, bk_h, "Back", mouse, self.font_md)
            pygame.display.flip()

    # ─── drawing ─────────────────────────────────────────────────────────────

    def _draw_title(self, ticks):
        # Animated color cycle on title
        t     = ticks / 2200
        r     = int(195 + 60 * abs(math.sin(t * math.pi)))
        g     = int(220 + 35 * abs(math.sin(t * math.pi + 1.1)))
        b     = 255
        color = (min(255, r), min(255, g), b)

        title = self.font_xl.render("CONNECT FOUR", True, color)
        tx    = T.WIN_W // 2 - title.get_width() // 2
        ty    = 30

        # Glow behind title
        T.draw_glow_circle(self.screen, T.WIN_W // 2, ty + 25,
                           title.get_width() // 3, color, passes=4, base_alpha=8)

        self.screen.blit(title, (tx, ty))

        # Decorative chips flanking subtitle
        T.draw_chip(self.screen, T.WIN_W // 2 - 130, 140, 22, T.P1_RED,  glow=True)
        T.draw_chip(self.screen, T.WIN_W // 2 + 130, 140, 22, T.P2_GOLD, glow=True)

        sub = self.font_sm.render("choose a mode to play", True, T.DIM)
        self.screen.blit(sub, (T.WIN_W // 2 - sub.get_width() // 2, 155))

    def _draw_wallet(self):
        # Wallet badge top-right
        bal_text = f"${self.wallet.balance}"
        lbl      = self.font_xs.render("WALLET", True, T.DIM)
        bal      = self.font_md.render(bal_text, True, T.NEON_CYN)
        pad      = 10
        bw       = max(lbl.get_width(), bal.get_width()) + pad * 2
        bh       = lbl.get_height() + bal.get_height() + 8
        bx       = T.WIN_W - bw - 12
        by       = 10

        badge_rect = pygame.Rect(bx - 4, by - 4, bw + 8, bh + 8)
        T.draw_glow_rect(self.screen, badge_rect, T.NEON_CYN, passes=2, base_alpha=10)
        T.draw_panel(self.screen, badge_rect, T.BTN, T.NEON_CYN, radius=8)

        self.screen.blit(lbl, (bx + bw // 2 - lbl.get_width() // 2, by + 2))
        self.screen.blit(bal, (bx + bw // 2 - bal.get_width() // 2,
                                by + lbl.get_height() + 5))

    def _draw_mode_card(self, rect, mode, mouse):
        hov   = rect.collidepoint(mouse)
        color = mode["color"]

        if hov:
            T.draw_glow_rect(self.screen, rect, color, passes=3, base_alpha=12)

        bg = T.BTN_HOV if hov else T.BTN
        T.draw_panel(self.screen, rect, bg, color if hov else T.BTN_BDR)

        # Left accent bar (always visible, mode color)
        pygame.draw.rect(self.screen, color,
                         (rect.x, rect.y, 5, rect.height), border_radius=4)

        # Disc
        disc_cx = rect.x + 36
        disc_cy = rect.centery
        T.draw_chip(self.screen, disc_cx, disc_cy, 20, color, glow=hov)

        # Labels
        lbl  = self.font_md.render(mode["label"], True, T.TEXT)
        desc = self.font_sm.render(mode["desc"],  True, T.DIM)
        self.screen.blit(lbl,  (rect.x + 72, rect.y + 16))
        self.screen.blit(desc, (rect.x + 72, rect.y + 42))

        # Chevron on right when hovered
        if hov:
            cx = rect.right - 28
            cy = rect.centery
            pts = [(cx, cy), (cx - 10, cy - 8), (cx - 10, cy + 8)]
            pygame.draw.polygon(self.screen, color, pts)

    def _draw_footer(self):
        hint = self.font_xs.render("made with pygame", True, T.DIM)
        self.screen.blit(hint, (T.WIN_W // 2 - hint.get_width() // 2, T.WIN_H - 20))