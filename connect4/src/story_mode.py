import pygame
import sys
import src.theme as T
from src.game import Game
from src.ui import UI

STAGES = [
    {"name": "The Rookie",      "depth": 2, "desc": "Barely knows the rules. A warm-up."},
    {"name": "The Thinker",     "depth": 3, "desc": "Starting to plan ahead. Stay sharp."},
    {"name": "The Schemer",     "depth": 4, "desc": "Thinks several moves ahead. Watch out."},
    {"name": "The Tactician",   "depth": 4, "desc": "Reads the board carefully. Dangerous."},
    {"name": "The Expert",      "depth": 5, "desc": "Near-perfect play. Most players lose here."},
    {"name": "The Grandmaster", "depth": 5, "desc": "Almost flawless. You have been warned."},
    {"name": "The Machine",     "depth": 6, "desc": "Cold. Calculated. It does not forgive mistakes."},
]


class StoryMode:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock  = clock
        self.stage  = 0

        self.font_xl = pygame.font.SysFont("arial", 42, bold=True)
        self.font_lg = pygame.font.SysFont("arial", 28, bold=True)
        self.font_md = pygame.font.SysFont("arial", 20, bold=True)
        self.font_sm = pygame.font.SysFont("arial", 16)

    def run(self):
        self.stage = 0

        while self.stage < len(STAGES):
            action = self._intro_screen()
            if action == "quit":
                return

            winner = self._play_stage()

            if winner == 0:
                self.stage += 1
                if self.stage >= len(STAGES):
                    self._victory_screen()
                    return
                self._stage_clear_screen()
            elif winner == 1:
                action = self._defeat_screen()
                if action == "quit":
                    return
                # retry same stage

    def _play_stage(self):
        stage = STAGES[self.stage]
        game  = Game()
        game.players[1].name = stage["name"]

        ui = UI(game, "story", ai_depth=stage["depth"])
        return ui.run_single()

    # ---------------------------------------------------------------- screens

    def _intro_screen(self):
        stage    = STAGES[self.stage]
        btn_w    = 200
        btn_h    = 52
        btn_x    = T.WIN_W // 2 - btn_w // 2
        btn_y    = T.WIN_H // 2 + 100

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
                    if pygame.Rect(btn_x, btn_y, btn_w, btn_h).collidepoint(mouse):
                        return "play"

            T.draw_bg(self.screen)

            stage_lbl = self.font_sm.render(
                f"STAGE {self.stage + 1} OF {len(STAGES)}", True, T.DIM
            )
            self.screen.blit(stage_lbl, (T.WIN_W // 2 - stage_lbl.get_width() // 2, 200))

            name_surf = self.font_xl.render(stage["name"], True, T.TEXT)
            self.screen.blit(name_surf, (T.WIN_W // 2 - name_surf.get_width() // 2, 240))

            desc_surf = self.font_md.render(f'"{stage["desc"]}"', True, T.DIM)
            self.screen.blit(desc_surf, (T.WIN_W // 2 - desc_surf.get_width() // 2, 310))

            self._draw_progress()

            T.draw_btn(self.screen, btn_x, btn_y, btn_w, btn_h, "Battle!", mouse, self.font_md)

            esc = self.font_sm.render("ESC = quit story", True, T.DIM)
            self.screen.blit(esc, (T.WIN_W - esc.get_width() - 12, T.WIN_H - 20))

            pygame.display.flip()

    def _draw_progress(self):
        bar_w = 420
        bar_h = 8
        bar_x = T.WIN_W // 2 - bar_w // 2
        bar_y = T.WIN_H // 2 + 30

        T.draw_panel(self.screen, pygame.Rect(bar_x, bar_y, bar_w, bar_h), T.BTN, radius=4)

        if self.stage > 0:
            filled = int(bar_w * (self.stage / len(STAGES)))
            T.draw_panel(self.screen, pygame.Rect(bar_x, bar_y, filled, bar_h), T.NEON_CYAN, radius=4)

        for i in range(len(STAGES)):
            cx    = bar_x + int(bar_w * i / (len(STAGES) - 1))
            cy    = bar_y + bar_h // 2
            color = T.NEON_CYAN if i < self.stage else (T.WIN_GREEN if i == self.stage else T.BTN_BDR)
            pygame.draw.circle(self.screen, color, (cx, cy), 7)

    def _stage_clear_screen(self):
        deadline = pygame.time.get_ticks() + 2200
        while pygame.time.get_ticks() < deadline:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    return

            T.draw_bg(self.screen)
            text = self.font_xl.render("Stage Clear!", True, T.WIN_GREEN)
            self.screen.blit(text, (T.WIN_W // 2 - text.get_width() // 2, T.WIN_H // 2 - 30))
            hint = self.font_sm.render("Press anything to continue", True, T.DIM)
            self.screen.blit(hint, (T.WIN_W // 2 - hint.get_width() // 2, T.WIN_H // 2 + 30))
            pygame.display.flip()

    def _defeat_screen(self):
        btn_w  = 180
        btn_h  = 50
        gap    = 20
        rx     = T.WIN_W // 2 - btn_w - gap // 2
        qx     = T.WIN_W // 2 + gap // 2
        btn_y  = T.WIN_H // 2 + 50

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
                    if pygame.Rect(rx, btn_y, btn_w, btn_h).collidepoint(mouse):
                        return "retry"
                    if pygame.Rect(qx, btn_y, btn_w, btn_h).collidepoint(mouse):
                        return "quit"

            T.draw_bg(self.screen)
            text = self.font_xl.render("Defeated...", True, T.P1_RED)
            self.screen.blit(text, (T.WIN_W // 2 - text.get_width() // 2, T.WIN_H // 2 - 50))
            T.draw_btn(self.screen, rx, btn_y, btn_w, btn_h, "Retry",     mouse, self.font_md)
            T.draw_btn(self.screen, qx, btn_y, btn_w, btn_h, "Quit Story", mouse, self.font_md)
            pygame.display.flip()

    def _victory_screen(self):
        deadline = pygame.time.get_ticks() + 5000
        while pygame.time.get_ticks() < deadline:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    return

            T.draw_bg(self.screen)

            title = self.font_xl.render("You are the Champion!", True, T.P2_GOLD)
            sub   = self.font_md.render("All 7 opponents defeated.", True, T.DIM)
            self.screen.blit(title, (T.WIN_W // 2 - title.get_width() // 2, T.WIN_H // 2 - 40))
            self.screen.blit(sub,   (T.WIN_W // 2 - sub.get_width()   // 2, T.WIN_H // 2 + 20))

            hint = self.font_sm.render("Press anything to return", True, T.DIM)
            self.screen.blit(hint, (T.WIN_W // 2 - hint.get_width() // 2, T.WIN_H // 2 + 70))
            pygame.display.flip()