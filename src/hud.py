import random
import pygame

# 9x9 pixel heart:  O = outline, x = fill, w = highlight, d = shade
HEART = [
    "..OO.OO..",
    ".OxxOxxO.",
    "OxwxxxxxO",
    "OxwxxxxdO",
    "OxxxxxxdO",
    ".OxxxxdO.",
    "..OxxdO..",
    "...OdO...",
    "....O....",
]
RED   = {'O': (0, 0, 0), 'x': (226, 36, 44), 'w': (255, 170, 170), 'd': (160, 18, 30)}
EMPTY = {'O': (0, 0, 0), 'x': (58, 52, 56), 'w': (92, 86, 90), 'd': (40, 36, 40)}


def _heart(kind, scale, blink=False):
    """kind: 'full', 'half' or 'empty'. Half hearts are red on the left, empty on the right."""
    surf = pygame.Surface((9, 9), pygame.SRCALPHA)
    for y, row in enumerate(HEART):
        for x, ch in enumerate(row):
            if ch == '.':
                continue
            if ch == 'O':
                col = (255, 255, 255) if blink else RED['O']
            else:
                red = kind == 'full' or (kind == 'half' and x <= 4)
                col = (RED if red else EMPTY)[ch]
            surf.set_at((x, y), col)
    return pygame.transform.scale(surf, (9 * scale, 9 * scale))


class HUD:
    def __init__(self, screen_size, scale=3):
        self.w, self.h = screen_size
        self.scale = scale
        self.icons = {(k, b): _heart(k, scale, b) for k in ('full', 'half', 'empty') for b in (False, True)}
        self.last_hp = None
        self.blink_t = 0.0          # hearts flash white after hp changes
        self.hurt_t = 0.0           # red screen edge flash after damage
        self.shake_t = 0.0
        self.jitter = []
        self.font = pygame.font.Font(None, 28)
        self.big_font = pygame.font.Font(None, 96)

        # pre-render a red vignette (strong at the edges, clear in the middle)
        self.vignette = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        steps = 70
        for i in range(steps):
            a = int(150 * (1 - i / steps) ** 2)
            pygame.draw.rect(self.vignette, (200, 0, 0, a), (i, i, self.w - 2 * i, self.h - 2 * i), 1)

    def update(self, dt, hp):
        if self.last_hp is not None and hp != self.last_hp:
            self.blink_t = 0.5
            if hp < self.last_hp:
                self.hurt_t = 0.4
        self.last_hp = hp
        self.blink_t = max(0.0, self.blink_t - dt)
        self.hurt_t = max(0.0, self.hurt_t - dt)
        self.shake_t -= dt
        if self.shake_t <= 0:        # re-roll the shake every ~80ms so it jitters, not flickers
            self.shake_t = 0.08
            self.jitter = [random.choice((-2, 0, 2)) for _ in range(30)]

    def draw(self, screen, hp, max_hp):
        if self.hurt_t > 0:
            self.vignette.set_alpha(int(255 * min(1.0, self.hurt_t / 0.4)))
            screen.blit(self.vignette, (0, 0))

        hearts = (max_hp + 1) // 2
        low = 0 < hp <= 6
        blink = self.blink_t > 0 and int(self.blink_t * 14) % 2 == 0
        step = 8 * self.scale                       # hearts overlap by one pixel, like Minecraft
        x0, y0 = 16, 14
        for i in range(hearts):
            if hp >= 2 * i + 2:   kind = 'full'
            elif hp == 2 * i + 1: kind = 'half'
            else:                 kind = 'empty'
            dy = self.jitter[i % len(self.jitter)] if low and self.jitter else 0
            screen.blit(self.icons[(kind, blink)], (x0 + i * step, y0 + dy))

    def draw_death(self, screen):
        shade = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        shade.fill((120, 0, 0, 140))
        screen.blit(shade, (0, 0))
        title = self.big_font.render("YOU DIED", True, (255, 255, 255))
        sub = self.font.render("Press R to respawn", True, (230, 230, 230))
        screen.blit(title, title.get_rect(center=(self.w // 2, self.h // 2 - 20)))
        screen.blit(sub, sub.get_rect(center=(self.w // 2, self.h // 2 + 40)))
