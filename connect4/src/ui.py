import pygame
import sys
import math
import src.theme as T
from src.board import Board
from src.ai import AI

ROWS = Board.ROWS
COLS = Board.COLS

CELL   = 88
RADIUS = 34

BOARD_W = COLS * CELL
BOARD_H = ROWS * CELL
BOARD_X = (T.WIN_W - BOARD_W) // 2
BOARD_Y = 118

ANIM_SPEED = 24


class UI:
    def __init__(self, game, mode, ai_depth=AI.HARD, wallet=None, bet=0):
        self.game   = game
        self.mode   = mode
        self.ai     = AI("O", "X", depth=ai_depth) if mode in ("pvai", "story", "gambling") else None
        self.wallet = wallet
        self.bet    = bet
        self.screen = pygame.display.get_surface()
        self.clock  = pygame.time.Clock()

        self.font_xl = pygame.font.SysFont("arial", 38, bold=True)
        self.font_lg = pygame.font.SysFont("arial", 28, bold=True)
        self.font_md = pygame.font.SysFont("arial", 20, bold=True)
        self.font_sm = pygame.font.SysFont("arial", 15)

        # Animation
        self.animating     = False
        self.anim_col      = 0
        self.anim_x        = 0.0
        self.anim_y        = 0.0
        self.anim_target_y = 0.0
        self.anim_color    = T.P1_RED

        self.hover_col      = None
        self.pending_result = False
        self.win_anim_start = None

        # Particles
        self.particles = [T.Particle() for _ in range(55)]

    # ─── public ──────────────────────────────────────────────────────────────

    def run(self):
        while True:
            self._tick()
            action = self._check_result()
            if action:
                return action
        return "quit"

    def run_single(self):
        """One game, no result screen. Returns winner_index or None."""
        while True:
            self._tick(single=True)
            if self.pending_result and not self.animating:
                self.pending_result = False
                return self.game.current_index if self.game.state == "won" else None

    # ─── core loop ───────────────────────────────────────────────────────────

    def _tick(self, single=False):
        self.clock.tick(60)
        self._handle_events(single)
        self._ai_turn()
        if self.animating:
            self._tick_animation()
        self._render()

    def _check_result(self):
        if self.pending_result and not self.animating:
            self.pending_result = False
            action = self._result_screen()
            if action == "replay":
                self.game.reset()
                self.hover_col      = None
                self.win_anim_start = None
            else:
                return action
        return None

    # ─── events ──────────────────────────────────────────────────────────────

    def _handle_events(self, single=False):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if not single and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # Trigger exit via result screen flow
                pass
            if not self.animating and self.game.state == "playing" and self._is_human_turn():
                if event.type == pygame.MOUSEMOTION:
                    self.hover_col = self._col_at(event.pos[0])
                if event.type == pygame.MOUSEBUTTONDOWN:
                    col = self._col_at(event.pos[0])
                    if col is not None:
                        self._start_drop(col)

    def _is_human_turn(self):
        return self.mode == "pvp" or self.game.current_index == 0

    def _col_at(self, x):
        if not (BOARD_X <= x <= BOARD_X + BOARD_W):
            return None
        col = (x - BOARD_X) // CELL
        if 0 <= col < COLS and not self.game.board.is_column_full(col):
            return col
        return None

    def _ai_turn(self):
        if (not self.animating
                and self.game.state == "playing"
                and not self._is_human_turn()):
            self._start_drop(self.ai.get_move(self.game.board))

    # ─── animation ───────────────────────────────────────────────────────────

    def _start_drop(self, col):
        target_row = next(
            (r for r in range(ROWS - 1, -1, -1) if self.game.board.get_cell(r, col).is_empty()),
            None
        )
        if target_row is None:
            return

        self.animating     = True
        self.anim_col      = col
        self.anim_x        = float(BOARD_X + col * CELL + CELL // 2)
        self.anim_y        = float(BOARD_Y - RADIUS - 12)
        self.anim_target_y = float(BOARD_Y + target_row * CELL + CELL // 2)
        self.anim_color    = T.P1_RED if self.game.current_index == 0 else T.P2_GOLD

    def _tick_animation(self):
        # Ease-in: accelerate as it falls
        dist = self.anim_target_y - self.anim_y
        self.anim_y += max(ANIM_SPEED, dist * 0.18)
        if self.anim_y >= self.anim_target_y:
            self.anim_y    = self.anim_target_y
            self.animating = False
            self.game.move(self.anim_col)
            if self.game.state != "playing":
                self.pending_result = True
                if self.game.state == "won":
                    self.win_anim_start = pygame.time.get_ticks()

    # ─── render ──────────────────────────────────────────────────────────────

    def _render(self):
        T.draw_bg_full(self.screen)

        for p in self.particles:
            p.update()
            p.draw(self.screen)

        self._draw_header()
        self._draw_column_hints()
        self._draw_board()

        if self.animating:
            T.draw_chip(self.screen, int(self.anim_x), int(self.anim_y),
                        RADIUS, self.anim_color, glow=True)

        self._draw_footer()
        pygame.display.flip()

    def _draw_header(self):
        title = self.font_xl.render("CONNECT  FOUR", True, T.TEXT)
        self.screen.blit(title, (T.WIN_W // 2 - title.get_width() // 2, 10))

        # Decorative line under title
        lw = title.get_width() + 40
        lx = T.WIN_W // 2 - lw // 2
        pygame.draw.line(self.screen, T.BTN_BDR, (lx, 56), (lx + lw, 56), 1)

        p1, p2   = self.game.players
        p2_label = "CPU" if self.mode in ("pvai", "gambling", "story") else p2.name

        s1 = self.font_md.render(f"{p1.name}   {p1.score}", True, T.P1_RED)
        vs = self.font_md.render("vs", True, T.DIM)
        s2 = self.font_md.render(f"{p2.score}   {p2_label}", True, T.P2_GOLD)

        tw = s1.get_width() + 30 + vs.get_width() + 30 + s2.get_width()
        x  = T.WIN_W // 2 - tw // 2
        y  = 65
        self.screen.blit(s1, (x, y))
        x += s1.get_width() + 15
        self.screen.blit(vs, (x, y + 3))
        x += vs.get_width() + 15
        self.screen.blit(s2, (x, y))

        if self.wallet is not None:
            wal = self.font_sm.render(
                f"Wallet: ${self.wallet.balance}   Bet: ${self.bet}", True, T.NEON_CYN)
            self.screen.blit(wal, (T.WIN_W // 2 - wal.get_width() // 2, 94))

    def _draw_column_hints(self):
        # Column numbers
        for c in range(COLS):
            cx  = BOARD_X + c * CELL + CELL // 2
            num = self.font_sm.render(str(c + 1), True, T.DIM)
            self.screen.blit(num, (cx - num.get_width() // 2, BOARD_Y - 22))

        if (self.hover_col is not None
                and not self.animating
                and self.game.state == "playing"
                and self._is_human_turn()):
            # Glowing column indicator bar
            hx    = BOARD_X + self.hover_col * CELL
            color = T.P1_RED if self.game.current_index == 0 else T.P2_GOLD

            bar_surf = pygame.Surface((CELL, 4), pygame.SRCALPHA)
            bar_surf.fill((*color, 200))
            self.screen.blit(bar_surf, (hx, BOARD_Y - 8))

            # Arrow
            cx  = hx + CELL // 2
            pts = [(cx, BOARD_Y - 12), (cx - 7, BOARD_Y - 22), (cx + 7, BOARD_Y - 22)]
            pygame.draw.polygon(self.screen, color, pts)

    def _draw_board(self):
        # Board panel with glow border
        board_rect = pygame.Rect(BOARD_X - 8, BOARD_Y - 8, BOARD_W + 16, BOARD_H + 16)
        T.draw_glow_rect(self.screen, board_rect, T.NEON_BLU, passes=3, base_alpha=10)
        T.draw_panel(self.screen, board_rect, T.BOARD_BG, T.BOARD_EDGE, radius=14)

        # Hover column highlight
        if (self.hover_col is not None
                and not self.animating
                and self.game.state == "playing"
                and self._is_human_turn()):
            hs = pygame.Surface((CELL, BOARD_H), pygame.SRCALPHA)
            hs.fill((255, 255, 255, 12))
            self.screen.blit(hs, (BOARD_X + self.hover_col * CELL, BOARD_Y))

        win_set = set(self.game.win_cells)

        # Win pulse value
        pulse = 0.0
        if self.win_anim_start:
            t     = (pygame.time.get_ticks() - self.win_anim_start) / 350
            pulse = 0.5 + 0.5 * math.sin(t * math.pi * 2.5)

        for r in range(ROWS):
            for c in range(COLS):
                cx   = BOARD_X + c * CELL + CELL // 2
                cy   = BOARD_Y + r * CELL + CELL // 2
                cell = self.game.board.get_cell(r, c)

                T.draw_slot(self.screen, cx, cy, RADIUS)

                if not cell.is_empty():
                    color  = T.P1_RED if cell.value == "X" else T.P2_GOLD
                    is_win = (r, c) in win_set

                    if is_win:
                        T.draw_glow_circle(self.screen, cx, cy, RADIUS + int(pulse * 8),
                                           T.WIN_GRN, passes=5, base_alpha=22)
                        T.draw_chip(self.screen, cx, cy, RADIUS, color, glow=False, pulse=pulse)
                        # Win ring
                        pygame.draw.circle(self.screen, T.WIN_GRN, (cx, cy), RADIUS + 5, 2)
                    else:
                        T.draw_chip(self.screen, cx, cy, RADIUS, color)

    def _draw_footer(self):
        if not self.animating and self.game.state == "playing":
            color  = T.P1_RED if self.game.current_index == 0 else T.P2_GOLD
            is_cpu = self.mode in ("pvai", "gambling", "story") and self.game.current_index == 1
            msg    = "CPU is thinking..." if is_cpu else f"{self.game.current.name}'s turn"
            text   = self.font_sm.render(msg, True, color)
            self.screen.blit(text, (T.WIN_W // 2 - text.get_width() // 2,
                                    BOARD_Y + BOARD_H + 18))

        hint = self.font_sm.render("ESC = menu", True, T.DIM)
        self.screen.blit(hint, (T.WIN_W - hint.get_width() - 12, T.WIN_H - 20))

    # ─── result screen ────────────────────────────────────────────────────────

    def _result_screen(self):
        bg      = self.screen.copy()
        overlay = pygame.Surface((T.WIN_W, T.WIN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 175))

        if self.game.state == "won":
            color  = T.P1_RED if self.game.current_index == 0 else T.P2_GOLD
            is_cpu = self.mode in ("pvai", "gambling", "story") and self.game.current_index == 1
            name   = "CPU" if is_cpu else self.game.current.name
            msg    = f"{name} wins!"
        else:
            color = T.TEXT
            msg   = "It's a draw."

        msg_surf = self.font_xl.render(msg, True, color)

        btn_w, btn_h = 190, 52
        gap    = 18
        btn_x1 = T.WIN_W // 2 - btn_w - gap // 2
        btn_x2 = T.WIN_W // 2 + gap // 2
        btn_y  = T.WIN_H // 2 + 25

        start  = pygame.time.get_ticks()

        while True:
            self.clock.tick(60)
            mouse = pygame.mouse.get_pos()
            t     = (pygame.time.get_ticks() - start) / 600

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return "menu"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pygame.Rect(btn_x1, btn_y, btn_w, btn_h).collidepoint(mouse):
                        return "replay"
                    if pygame.Rect(btn_x2, btn_y, btn_w, btn_h).collidepoint(mouse):
                        return "menu"

            # Expanding ring effect on win
            self.screen.blit(bg, (0, 0))
            self.screen.blit(overlay, (0, 0))

            if self.game.state == "won":
                ring_r = int(80 * min(1.0, t))
                ring_s = pygame.Surface((ring_r * 2 + 4, ring_r * 2 + 4), pygame.SRCALPHA)
                alpha  = max(0, int(160 * (1 - t)))
                pygame.draw.circle(ring_s, (*color[:3], alpha),
                                   (ring_r + 2, ring_r + 2), ring_r, 3)
                self.screen.blit(ring_s, (T.WIN_W // 2 - ring_r - 2,
                                          T.WIN_H // 2 - 60 - ring_r - 2))

            self.screen.blit(msg_surf, (T.WIN_W // 2 - msg_surf.get_width()  // 2,
                                        T.WIN_H // 2 - 65))

            T.draw_btn(self.screen, btn_x1, btn_y, btn_w, btn_h,
                       "Play Again", mouse, self.font_md, T.NEON_BLU)
            T.draw_btn(self.screen, btn_x2, btn_y, btn_w, btn_h,
                       "Main Menu",  mouse, self.font_md, T.NEON_PUR)
            pygame.display.flip()