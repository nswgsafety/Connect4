import pygame
import sys

WIN_W = 700
WIN_H = 720

# Colors (must match ui.py)
BG       = (8,   12,  28)
P1_COL   = (220, 55,  55)
P2_COL   = (240, 195, 20)
TEXT_COL = (210, 225, 255)
DIM_COL  = (80,  100, 150)
BTN_COL  = (25,  45,  120)
BTN_HOV  = (40,  70,  180)
BTN_BDR  = (55,  90,  200)


class Menu:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.font_xl = pygame.font.SysFont("arial", 52, bold=True)
        self.font_lg = pygame.font.SysFont("arial", 30, bold=True)
        self.font_md = pygame.font.SysFont("arial", 20, bold=True)
        self.font_sm = pygame.font.SysFont("arial", 15)

    def run(self):
        # Returns "pvp", "pvai", or "quit"
        btn_w, btn_h = 280, 60
        gap = 24
        pvp_x  = WIN_W // 2 - btn_w // 2
        pvp_y  = WIN_H // 2 - btn_h - gap // 2
        pvai_x = WIN_W // 2 - btn_w // 2
        pvai_y = WIN_H // 2 + gap // 2

        while True:
            self.clock.tick(60)
            mouse = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pygame.Rect(pvp_x, pvp_y, btn_w, btn_h).collidepoint(mouse):
                        return "pvp"
                    if pygame.Rect(pvai_x, pvai_y, btn_w, btn_h).collidepoint(mouse):
                        return "pvai"

            self.screen.fill(BG)
            self._draw_title()
            self._draw_button(pvp_x,  pvp_y,  btn_w, btn_h, "Player vs Player", mouse)
            self._draw_button(pvai_x, pvai_y, btn_w, btn_h, "Player vs AI",    mouse)
            self._draw_footer()
            pygame.display.flip()

    def _draw_title(self):
        title = self.font_xl.render("CONNECT FOUR", True, TEXT_COL)
        self.screen.blit(title, (WIN_W // 2 - title.get_width() // 2, WIN_H // 4 - 40))

        # Two decorative discs
        pygame.draw.circle(self.screen, P1_COL, (WIN_W // 2 - 55, WIN_H // 4 + 42), 20)
        pygame.draw.circle(self.screen, (255, 125, 85), (WIN_W // 2 - 48, WIN_H // 4 + 34), 7)
        pygame.draw.circle(self.screen, P2_COL, (WIN_W // 2 + 55, WIN_H // 4 + 42), 20)
        pygame.draw.circle(self.screen, (255, 230, 100), (WIN_W // 2 + 62, WIN_H // 4 + 34), 7)

        sub = self.font_sm.render("select a game mode", True, DIM_COL)
        self.screen.blit(sub, (WIN_W // 2 - sub.get_width() // 2, WIN_H // 4 + 80))

    def _draw_button(self, x, y, w, h, label, mouse):
        rect = pygame.Rect(x, y, w, h)
        color = BTN_HOV if rect.collidepoint(mouse) else BTN_COL
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        pygame.draw.rect(self.screen, BTN_BDR, rect, 2, border_radius=10)
        text = self.font_md.render(label, True, TEXT_COL)
        self.screen.blit(
            text,
            (x + w // 2 - text.get_width() // 2, y + h // 2 - text.get_height() // 2),
        )
