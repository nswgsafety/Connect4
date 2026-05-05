import pygame
import math
import random

WIN_W = 700
WIN_H = 720

# ── Palette ──────────────────────────────────────────────────────────────────
BG_TOP   = (8,   5,  22)
BG_BOT   = (16, 10,  45)

BOARD_BG  = (16, 12,  68)
BOARD_EDGE= (28, 22, 100)
EMPTY     = (9,   7,  42)
EMPTY_RIM = (28, 24,  80)

P1_RED   = (255,  60,  60)
P2_GOLD  = (255, 210,  25)

WIN_GRN  = (0,  255, 140)
NEON_BLU = (55, 155, 255)
NEON_CYN = (0,  225, 255)
NEON_PUR = (200,  75, 255)

TEXT     = (220, 232, 255)
DIM      = (85,   90, 145)

BTN      = (20,  16,  80)
BTN_HOV  = (36,  28, 130)
BTN_BDR  = (60,  52, 185)

TABLE_GRN    = (8,  52,  26)
TABLE_GRN_LT = (13, 72,  36)

CARD_BG   = (248, 248, 250)
CARD_BACK = (22,  42, 115)
CARD_RED  = (200,  22,  22)
CARD_BLK  = (12,   12,  22)

# ── Background cache ─────────────────────────────────────────────────────────
_bg_cache   = None
_vign_cache = None


def _build_bg(size):
    w, h = size
    surf = pygame.Surface(size)
    for y in range(h):
        t = y / h
        r = int(BG_TOP[0] + (BG_BOT[0] - BG_TOP[0]) * t)
        g = int(BG_TOP[1] + (BG_BOT[1] - BG_TOP[1]) * t)
        b = int(BG_TOP[2] + (BG_BOT[2] - BG_TOP[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (w, y))
    return surf


def _build_vignette(size):
    w, h = size
    surf = pygame.Surface(size, pygame.SRCALPHA)
    cx, cy = w // 2, h // 2
    max_d  = math.hypot(cx, cy)
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            d = math.hypot(x - cx, y - cy) / max_d
            a = int(min(180, d ** 2.2 * 220))
            pygame.draw.rect(surf, (0, 0, 0, a), (x, y, 2, 2))
    return surf


def get_bg(size=(WIN_W, WIN_H)):
    global _bg_cache
    if _bg_cache is None or _bg_cache.get_size() != size:
        _bg_cache = _build_bg(size)
    return _bg_cache


def get_vignette(size=(WIN_W, WIN_H)):
    global _vign_cache
    if _vign_cache is None or _vign_cache.get_size() != size:
        _vign_cache = _build_vignette(size)
    return _vign_cache


def draw_bg(surface):
    surface.blit(get_bg(surface.get_size()), (0, 0))


def draw_bg_full(surface):
    """Background + vignette for premium look."""
    surface.blit(get_bg(surface.get_size()),      (0, 0))
    surface.blit(get_vignette(surface.get_size()), (0, 0))


# ── Particles ─────────────────────────────────────────────────────────────────
class Particle:
    COLORS = [(100, 120, 255), (155, 95, 255), (60, 210, 255), (200, 80, 255)]

    def __init__(self, w=WIN_W, h=WIN_H):
        self.w = w
        self.h = h
        self._spawn()

    def _spawn(self):
        self.x     = random.uniform(0, self.w)
        self.y     = random.uniform(0, self.h)
        self.vy    = random.uniform(0.25, 1.0)
        self.vx    = random.uniform(-0.15, 0.15)
        self.r     = random.randint(1, 2)
        self.alpha = random.randint(20, 75)
        self.color = random.choice(self.COLORS)

    def update(self):
        self.y -= self.vy
        self.x += self.vx
        if self.y < -4:
            self.y = self.h + 4
            self.x = random.uniform(0, self.w)

    def draw(self, surface):
        s = pygame.Surface((self.r * 2 + 2, self.r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, self.alpha), (self.r + 1, self.r + 1), self.r)
        surface.blit(s, (int(self.x) - self.r - 1, int(self.y) - self.r - 1))


# ── Glow helpers ──────────────────────────────────────────────────────────────
def draw_glow_circle(surface, cx, cy, radius, color, passes=5, base_alpha=22):
    for i in range(passes, 0, -1):
        r = radius + i * 5
        s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        a = base_alpha * i
        pygame.draw.circle(s, (*color[:3], a), (r, r), r)
        surface.blit(s, (cx - r, cy - r))


def draw_glow_rect(surface, rect, color, passes=3, base_alpha=18):
    for i in range(passes, 0, -1):
        inf = i * 4
        r   = rect.inflate(inf * 2, inf * 2)
        s   = pygame.Surface(r.size, pygame.SRCALPHA)
        pygame.draw.rect(s, (*color[:3], base_alpha * i), s.get_rect(), border_radius=14)
        surface.blit(s, r.topleft)


# ── Chip ─────────────────────────────────────────────────────────────────────
def draw_chip(surface, cx, cy, radius, color, glow=False, pulse=0.0):
    dark   = tuple(max(0,   c - 85) for c in color)
    mid    = tuple(min(255, c + 35) for c in color)
    bright = tuple(min(255, c + 130) for c in color)

    if glow:
        glow_r = radius + int(pulse * 10)
        draw_glow_circle(surface, cx, cy, glow_r, color, passes=5, base_alpha=20)

    # Drop shadow
    pygame.draw.circle(surface, (1, 0, 8), (cx + 2, cy + 4), radius)

    # Bottom-lit base (darker = depth illusion)
    pygame.draw.circle(surface, dark, (cx, cy + 3), radius)

    # Main body
    pygame.draw.circle(surface, color, (cx, cy), radius)

    # Upper directional lighting (soft lighter region on top half)
    lit = pygame.Surface((radius * 2, radius), pygame.SRCALPHA)
    pygame.draw.ellipse(lit, (*mid, 55), (0, 0, radius * 2, radius))
    surface.blit(lit, (cx - radius, cy - radius))

    # Outer metallic ring
    pygame.draw.circle(surface, mid, (cx, cy), radius, 2)

    # Inner detail rings
    pygame.draw.circle(surface, dark, (cx, cy), int(radius * 0.78), 1)
    pygame.draw.circle(surface, mid,  (cx, cy), int(radius * 0.63), 1)

    # 8 edge notch marks
    for i in range(8):
        angle = i * math.pi / 4
        nx = cx + int((radius - 4) * math.cos(angle))
        ny = cy + int((radius - 4) * math.sin(angle))
        pygame.draw.circle(surface, dark, (nx, ny), 2)

    # Center disc
    pygame.draw.circle(surface, mid, (cx, cy), max(3, radius // 6))

    # Soft specular blob
    spec_r = radius // 3
    spec_s = pygame.Surface((spec_r * 2, spec_r * 2), pygame.SRCALPHA)
    pygame.draw.circle(spec_s, (*bright, 160), (spec_r, spec_r), spec_r)
    surface.blit(spec_s, (cx - radius // 2 - spec_r // 2,
                           cy - radius // 2 - spec_r // 2))

    # Sharp specular point
    pygame.draw.circle(surface, (255, 255, 255),
                       (cx - radius // 3, cy - radius // 3), max(2, radius // 8))


# ── Slot (empty board cell) ───────────────────────────────────────────────────
def draw_slot(surface, cx, cy, radius):
    # Dark well
    pygame.draw.circle(surface, (2, 1, 8), (cx, cy + 2), radius)
    pygame.draw.circle(surface, EMPTY, (cx, cy), radius)
    # Subtle rim highlight
    pygame.draw.circle(surface, EMPTY_RIM, (cx, cy), radius, 2)


# ── Button ───────────────────────────────────────────────────────────────────
def draw_btn(surface, x, y, w, h, label, mouse, font, accent_color=None):
    rect    = pygame.Rect(x, y, w, h)
    hovered = rect.collidepoint(mouse)

    if hovered:
        draw_glow_rect(surface, rect, accent_color or NEON_BLU, passes=3, base_alpha=14)
        bg     = BTN_HOV
        border = accent_color or (90, 130, 255)
    else:
        bg     = BTN
        border = BTN_BDR

    pygame.draw.rect(surface, bg, rect, border_radius=10)

    # Top highlight line (subtle 3D depth)
    top_hi = tuple(min(255, c + 28) for c in bg)
    pygame.draw.line(surface, top_hi, (x + 8, y + 1), (x + w - 8, y + 1))

    pygame.draw.rect(surface, border, rect, 2, border_radius=10)

    text = font.render(label, True, TEXT)
    surface.blit(text, (x + w // 2 - text.get_width()  // 2,
                        y + h // 2 - text.get_height() // 2))
    return hovered


# ── Panel ─────────────────────────────────────────────────────────────────────
def draw_panel(surface, rect, color, border=None, radius=12):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border:
        pygame.draw.rect(surface, border, rect, 2, border_radius=radius)


# ── Card ─────────────────────────────────────────────────────────────────────
def draw_card(surface, x, y, w, h, rank, suit, hidden=False):
    rect = pygame.Rect(x, y, w, h)

    if hidden:
        pygame.draw.rect(surface, CARD_BACK, rect, border_radius=8)
        pygame.draw.rect(surface, (40, 70, 165), rect, 2, border_radius=8)
        for i in range(0, w + h, 12):
            pygame.draw.line(surface, (32, 58, 148),
                             (x + i, y), (x, y + i), 1)
            pygame.draw.line(surface, (32, 58, 148),
                             (x + w - i, y + h), (x + w, y + h - i), 1)
        return

    pygame.draw.rect(surface, CARD_BG,       rect, border_radius=8)
    pygame.draw.rect(surface, (190, 190, 200), rect, 1, border_radius=8)

    is_red = suit in ("♥", "♦")
    color  = CARD_RED if is_red else CARD_BLK

    fsm = pygame.font.SysFont("arial", 15, bold=True)
    flg = pygame.font.SysFont("arial", 34)

    rank_s = fsm.render(rank, True, color)
    suit_s = fsm.render(suit, True, color)
    suit_l = flg.render(suit, True, color)

    surface.blit(rank_s, (x + 5, y + 4))
    surface.blit(suit_s, (x + 5, y + 20))
    surface.blit(suit_l, (x + w // 2 - suit_l.get_width() // 2,
                           y + h // 2 - suit_l.get_height() // 2))

    # Rotated rank/suit at bottom-right
    rank_r = pygame.transform.rotate(rank_s, 180)
    suit_r = pygame.transform.rotate(suit_s, 180)
    surface.blit(rank_r, (x + w - rank_r.get_width() - 5, y + h - rank_r.get_height() - 4))
    surface.blit(suit_r, (x + w - suit_r.get_width() - 5, y + h - suit_r.get_height() - 20))