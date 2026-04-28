import pygame
import sys
from src.board import Board
from src.ai import AI

ROWS = Board.ROWS
COLS = Board.COLS

WIN_W = 700
WIN_H = 720

CELL = 88
RADIUS = 34

BOARD_W = COLS * CELL
BOARD_H = ROWS * CELL
BOARD_X = (WIN_W - BOARD_W) // 2
BOARD_Y = 118

# Colors
BG       = (8,   12,  28)
BOARD_BG = (16,  32,  90)
EMPTY    = (10,  20,  55)
P1_COL   = (220, 55,  55)
P2_COL   = (240, 195, 20)
WIN_COL  = (60,  230, 120)
TEXT_COL = (210, 225, 255)
DIM_COL  = (80,  100, 150)
BTN_COL  = (25,  45,  120)
BTN_HOV  = (40,  70,  180)
BTN_BDR  = (55,  90,  200)

ANIM_SPEED = 22


class UI:
    def __init__(self, game, mode):
        self.game = game
        self.mode = mode
        self.ai = AI("O", "X") if mode == "pvai" else None
        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()

        self.font_xl = pygame.font.SysFont("arial", 38, bold=True)
        self.font_lg = pygame.font.SysFont("arial", 28, bold=True)
        self.font_md = pygame.font.SysFont("arial", 20, bold=True)
        self.font_sm = pygame.font.SysFont("arial", 16)

        # Animation state
        self.animating = False
        self.anim_col = 0
        self.anim_x = 0
        self.anim_y = 0.0
        self.anim_target_y = 0.0
        self.anim_color = P1_COL

        self.hover_col = None
        self.pending_result = False

    # ------------------------------------------------------------------ run

    def run(self):
        while True:
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return "menu"
                if not self.animating and self.game.state == "playing":
                    if self._is_human_turn():
                        if event.type == pygame.MOUSEMOTION:
                            self.hover_col = self._col_at(event.pos[0])
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            col = self._col_at(event.pos[0])
                            if col is not None:
                                self._start_drop(col)

            # AI takes its turn automatically
            if (
                not self.animating
                and self.game.state == "playing"
                and not self._is_human_turn()
            ):
                col = self.ai.get_move(self.game.board)
                self._start_drop(col)

            if self.animating:
                self._tick_animation()

            self._render()

            if self.pending_result and not self.animating:
                self.pending_result = False
                action = self._result_screen()
                if action == "replay":
                    self.game.reset()
                    self.hover_col = None
                else:
                    return action

        return "quit"

    # --------------------------------------------------------- helpers

    def _is_human_turn(self):
        if self.mode == "pvp":
            return True
        return self.game.current_index == 0

    def _col_at(self, x):
        if x < BOARD_X or x > BOARD_X + BOARD_W:
            return None
        col = (x - BOARD_X) // CELL
        if 0 <= col < COLS and not self.game.board.is_column_full(col):
            return col
        return None

    def _start_drop(self, col):
        # Find the row the piece will land on before the move is committed
        target_row = None
        for row in range(ROWS - 1, -1, -1):
            if self.game.board.get_cell(row, col).is_empty():
                target_row = row
                break
        if target_row is None:
            return

        color = P1_COL if self.game.current_index == 0 else P2_COL
        self.animating = True
        self.anim_col = col
        self.anim_x = float(BOARD_X + col * CELL + CELL // 2)
        self.anim_y = float(BOARD_Y - RADIUS - 10)
        self.anim_target_y = float(BOARD_Y + target_row * CELL + CELL // 2)
        self.anim_color = color

    def _tick_animation(self):
        self.anim_y += ANIM_SPEED
        if self.anim_y >= self.anim_target_y:
            self.anim_y = self.anim_target_y
            self.animating = False
            self.game.move(self.anim_col)
            if self.game.state != "playing":
                self.pending_result = True

    # --------------------------------------------------------- rendering

    def _render(self):
        self.screen.fill(BG)
        self._draw_header()
        self._draw_column_hints()
        self._draw_board()
        if self.animating:
            self._draw_piece(int(self.anim_x), int(self.anim_y), self.anim_color)
        self._draw_footer()
        pygame.display.flip()

    def _draw_header(self):
        title = self.font_xl.render("CONNECT  FOUR", True, TEXT_COL)
        self.screen.blit(title, (WIN_W // 2 - title.get_width() // 2, 12))

        p1, p2 = self.game.players
        p2_label = "CPU" if self.mode == "pvai" else p2.name

        s1  = self.font_md.render(f"{p1.name}   {p1.score}", True, P1_COL)
        vs  = self.font_md.render("vs", True, DIM_COL)
        s2  = self.font_md.render(f"{p2.score}   {p2_label}", True, P2_COL)

        total_w = s1.get_width() + 30 + vs.get_width() + 30 + s2.get_width()
        x = WIN_W // 2 - total_w // 2
        y = 68
        self.screen.blit(s1, (x, y))
        x += s1.get_width() + 15
        self.screen.blit(vs, (x, y + 3))
        x += vs.get_width() + 15
        self.screen.blit(s2, (x, y))

    def _draw_column_hints(self):
        # Column numbers above the board
        for c in range(COLS):
            cx = BOARD_X + c * CELL + CELL // 2
            num = self.font_sm.render(str(c + 1), True, DIM_COL)
            self.screen.blit(num, (cx - num.get_width() // 2, BOARD_Y - 22))

        # Hover arrow
        if (
            self.hover_col is not None
            and not self.animating
            and self.game.state == "playing"
            and self._is_human_turn()
        ):
            cx = BOARD_X + self.hover_col * CELL + CELL // 2
            color = P1_COL if self.game.current_index == 0 else P2_COL
            pts = [(cx, BOARD_Y - 28), (cx - 8, BOARD_Y - 40), (cx + 8, BOARD_Y - 40)]
            pygame.draw.polygon(self.screen, color, pts)

    def _draw_board(self):
        board_rect = pygame.Rect(BOARD_X - 6, BOARD_Y - 6, BOARD_W + 12, BOARD_H + 12)
        pygame.draw.rect(self.screen, BOARD_BG, board_rect, border_radius=14)

        win_set = set(self.game.win_cells)

        # Hover column highlight
        if (
            self.hover_col is not None
            and not self.animating
            and self.game.state == "playing"
            and self._is_human_turn()
        ):
            surf = pygame.Surface((CELL, BOARD_H), pygame.SRCALPHA)
            surf.fill((255, 255, 255, 15))
            self.screen.blit(surf, (BOARD_X + self.hover_col * CELL, BOARD_Y))

        for r in range(ROWS):
            for c in range(COLS):
                cx = BOARD_X + c * CELL + CELL // 2
                cy = BOARD_Y + r * CELL + CELL // 2
                cell = self.game.board.get_cell(r, c)

                pygame.draw.circle(self.screen, EMPTY, (cx, cy), RADIUS)

                if not cell.is_empty():
                    color = P1_COL if cell.value == "X" else P2_COL
                    if (r, c) in win_set:
                        pygame.draw.circle(self.screen, WIN_COL, (cx, cy), RADIUS + 5)
                    self._draw_piece(cx, cy, color)

    def _draw_piece(self, cx, cy, color):
        pygame.draw.circle(self.screen, color, (cx, cy), RADIUS - 1)
        light = tuple(min(255, v + 70) for v in color)
        pygame.draw.circle(self.screen, light, (cx - RADIUS // 3, cy - RADIUS // 3), RADIUS // 4)

    def _draw_footer(self):
        if not self.animating and self.game.state == "playing":
            color = P1_COL if self.game.current_index == 0 else P2_COL
            if self.mode == "pvai" and self.game.current_index == 1:
                msg = "CPU is thinking..."
            else:
                msg = f"{self.game.current.name}'s turn"
            text = self.font_sm.render(msg, True, color)
            self.screen.blit(text, (WIN_W // 2 - text.get_width() // 2, BOARD_Y + BOARD_H + 18))

        hint = self.font_sm.render("ESC = menu", True, DIM_COL)
        self.screen.blit(hint, (WIN_W - hint.get_width() - 12, WIN_H - 20))

    # --------------------------------------------------------- result screen

    def _result_screen(self):
        bg = self.screen.copy()
        overlay = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))

        if self.game.state == "won":
            color = P1_COL if self.game.current_index == 0 else P2_COL
            name = "CPU" if (self.mode == "pvai" and self.game.current_index == 1) else self.game.current.name
            msg = f"{name} wins!"
        else:
            color = TEXT_COL
            msg = "It's a draw."

        msg_surf = self.font_xl.render(msg, True, color)

        btn_w, btn_h = 180, 50
        gap = 20
        btn_x1 = WIN_W // 2 - btn_w - gap // 2
        btn_x2 = WIN_W // 2 + gap // 2
        btn_y  = WIN_H // 2 + 20

        while True:
            self.clock.tick(60)
            mouse = pygame.mouse.get_pos()

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

            self.screen.blit(bg, (0, 0))
            self.screen.blit(overlay, (0, 0))
            self.screen.blit(msg_surf, (WIN_W // 2 - msg_surf.get_width() // 2, WIN_H // 2 - 60))
            self._draw_btn(btn_x1, btn_y, btn_w, btn_h, "Play Again", mouse)
            self._draw_btn(btn_x2, btn_y, btn_w, btn_h, "Main Menu", mouse)
            pygame.display.flip()

    def _draw_btn(self, x, y, w, h, label, mouse):
        rect = pygame.Rect(x, y, w, h)
        color = BTN_HOV if rect.collidepoint(mouse) else BTN_COL
        pygame.draw.rect(self.screen, color, rect, border_radius=9)
        pygame.draw.rect(self.screen, BTN_BDR, rect, 2, border_radius=9)
        text = self.font_md.render(label, True, TEXT_COL)
        self.screen.blit(text, (x + w // 2 - text.get_width() // 2, y + h // 2 - text.get_height() // 2))