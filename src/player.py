import pygame

class Player:
    def __init__(self, x, y):
        # The cat's physical body (a rectangle)
        self.rect = pygame.Rect(x, y, 32, 32)
        self.speed = 200  # pixels per second
        self.color = (50, 50, 50) # Dark grey for our Cat character

    def update(self, dt):
        keys = pygame.key.get_pressed()
        
        # Calculate movement direction
        dx = keys[pygame.K_d] - keys[pygame.K_a]
        dy = keys[pygame.K_s] - keys[pygame.K_w]
        
        # Normalize diagonal movement so we don't move faster diagonally
        if dx != 0 and dy != 0:
            # Math trick to keep speed consistent
            dx *= 0.7071
            dy *= 0.7071
            
        self.rect.x += dx * self.speed * dt
        self.rect.y += dy * self.speed * dt

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)