import pygame
import random

class NPC:
    def __init__(self, x, y, color, name="Villager", dialogue="..."):
        self.rect = pygame.Rect(x, y, 16, 16)
        self.speed = 40 # Walk slower than the player
        self.color = color
        self.name = name
        self.dialogue = dialogue
        
        # Wandering AI variables
        self.dir_x = 0
        self.dir_y = 0
        self.move_timer = random.uniform(1.0, 3.0)
        self.is_moving = False

    def update(self, dt, walls):
        self.move_timer -= dt
        
        # Timer ran out, pick a new action
        if self.move_timer <= 0:
            self.is_moving = random.choice([True, False])
            if self.is_moving:
                # Pick a random direction
                direction = random.choice(['up', 'down', 'left', 'right'])
                self.dir_x = 1 if direction == 'right' else -1 if direction == 'left' else 0
                self.dir_y = 1 if direction == 'down' else -1 if direction == 'up' else 0
            else:
                self.dir_x = 0
                self.dir_y = 0
            
            self.move_timer = random.uniform(1.0, 3.0)

        # Move and check collision
        if self.is_moving:
            # Move X
            old_x = self.rect.x
            self.rect.x += self.dir_x * self.speed * dt
            hit_wall = False
            for w in walls:
                if self.rect.colliderect(w):
                    self.rect.x = old_x
                    hit_wall = True
                    break
            
            # Move Y
            old_y = self.rect.y
            self.rect.y += self.dir_y * self.speed * dt
            for w in walls:
                if self.rect.colliderect(w):
                    self.rect.y = old_y
                    hit_wall = True
                    break

            if hit_wall:
                self.is_moving = False # Stop if they hit a wall

    def draw(self, surface, offset=(0, 0)):
        ox, oy = offset
        # Draw shadow
        shadow = pygame.Surface((12, 5), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 70), shadow.get_rect())
        surface.blit(shadow, (self.rect.centerx - 6 - ox, self.rect.bottom - 3 - oy))

        # Draw body
        pygame.draw.rect(surface, self.color, (self.rect.x - ox, self.rect.y - oy, 16, 16))
        # Draw simple head
        pygame.draw.rect(surface, (255, 200, 150), (self.rect.x + 3 - ox, self.rect.y - 4 - oy, 10, 8))