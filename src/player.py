import os
import pygame

SHEET_PATH = os.path.join(os.path.dirname(__file__), '..', 'assets', 'sprites', 'warrior.png')
FRAME = 16
# sheet rows: 0-3 = walk (down, left, right, up), 4-7 = sword attack (same order)
DIR_ROW = {'down': 0, 'left': 1, 'right': 2, 'up': 3}


class Player:
    SPEED = 80          # pixels per second (map tiles are 16px)
    WALK_FPS = 8
    ATTACK_FPS = 12     # 4 frames -> about a third of a second

    def __init__(self, x, y):
        sheet = pygame.image.load(SHEET_PATH).convert_alpha()

        def frames(row0):
            return {d: [sheet.subsurface((f * FRAME, (row0 + r) * FRAME, FRAME, FRAME)) for f in range(4)]
                    for d, r in DIR_ROW.items()}

        self.walk_frames = frames(0)
        self.attack_frames = frames(4)

        # collision box = just the feet, so the player can walk close to trees and walls
        self.rect = pygame.Rect(0, 0, 10, 6)
        self.x, self.y = float(x), float(y)             # position of the feet (midbottom)
        self.rect.midbottom = (round(self.x), round(self.y))

        # health: 20 hp = 10 hearts (1 hp = half a heart)
        self.max_hp = 20
        self.hp = self.max_hp
        self.invuln_t = 0.0                             # brief invincibility after being hit

        self.facing = 'down'
        self.moving = False
        self.attacking = False
        self.anim_t = 0.0
        self.attack_t = 0.0

        self.shadow = pygame.Surface((12, 5), pygame.SRCALPHA)
        pygame.draw.ellipse(self.shadow, (0, 0, 0, 70), self.shadow.get_rect())

    # ---------- health ----------
    @property
    def dead(self):
        return self.hp <= 0

    def take_damage(self, amount):
        """Returns True if the hit landed (False while invincible or already dead)."""
        if self.dead or self.invuln_t > 0:
            return False
        self.hp = max(0, self.hp - amount)
        self.invuln_t = 0.8
        self.attacking = False
        return True

    def heal(self, amount):
        if not self.dead:
            self.hp = min(self.max_hp, self.hp + amount)

    def respawn(self, x, y):
        self.hp = self.max_hp
        self.invuln_t = 1.0
        self.x, self.y = float(x), float(y)
        self.rect.midbottom = (round(self.x), round(self.y))
        self.attacking = False
        self.facing = 'down'

    # ---------- movement ----------
    def _move_axis(self, dx, dy, walls):
        self.x += dx
        self.y += dy
        self.rect.midbottom = (round(self.x), round(self.y))
        for w in walls:
            if self.rect.colliderect(w):
                if dx > 0:   self.rect.right = w.left
                elif dx < 0: self.rect.left = w.right
                if dy > 0:   self.rect.bottom = w.top
                elif dy < 0: self.rect.top = w.bottom
                self.x, self.y = self.rect.midbottom

    def update(self, dt, walls):
        dt = min(dt, 0.05)                              # avoid big jumps after a lag spike
        self.invuln_t = max(0.0, self.invuln_t - dt)
        if self.dead:
            self.moving = False
            return
        keys = pygame.key.get_pressed()

        if self.attacking:
            self.attack_t += dt * self.ATTACK_FPS
            if self.attack_t >= 4:
                self.attacking = False
                self.attack_t = 0.0
            self.moving = False
            return

        if keys[pygame.K_SPACE] or keys[pygame.K_j]:
            self.attacking = True
            self.attack_t = 0.0
            self.moving = False
            return

        dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
        self.moving = bool(dx or dy)

        if self.moving:
            if dx:
                self.facing = 'right' if dx > 0 else 'left'
            else:
                self.facing = 'down' if dy > 0 else 'up'
            if dx and dy:                               # same speed on diagonals
                dx *= 0.7071
                dy *= 0.7071
            self._move_axis(dx * self.SPEED * dt, 0, walls)
            self._move_axis(0, dy * self.SPEED * dt, walls)
            self.anim_t += dt * self.WALK_FPS
        else:
            self.anim_t = 0.0

    # ---------- combat helper ----------
    @property
    def attack_rect(self):
        """Hit area in front of the player, only active during the swing frames."""
        if not self.attacking or int(self.attack_t) not in (1, 2):
            return None
        r = pygame.Rect(0, 0, 16, 16)
        cx, cy = self.rect.centerx, self.rect.bottom - 6
        if self.facing == 'down':    r.midtop = (cx, cy)
        elif self.facing == 'up':    r.midbottom = (cx, cy)
        elif self.facing == 'left':  r.midright = (cx - 2, cy)
        else:                        r.midleft = (cx + 2, cy)
        return r

    # ---------- drawing ----------
    def draw(self, surface, offset=(0, 0)):
        ox, oy = offset
        if self.attacking:
            img = self.attack_frames[self.facing][min(int(self.attack_t), 3)]
        else:
            img = self.walk_frames[self.facing][int(self.anim_t) % 4 if self.moving else 0]
        surface.blit(self.shadow, (self.rect.centerx - 6 - ox, self.rect.bottom - 3 - oy))
        if self.invuln_t > 0 and not self.dead and int(self.invuln_t * 14) % 2 == 0:
            return                                      # flicker while invincible
        if self.dead:
            img = img.copy()
            img.set_alpha(110)
        spr = img.get_rect(midbottom=(self.rect.centerx - ox, self.rect.bottom + 1 - oy))
        surface.blit(img, spr)
