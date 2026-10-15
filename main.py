import pygame
import sys
import os

# Add the src folder to the path so we can import our Player
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from player import Player

pygame.init()
screen = pygame.display.set_mode((960, 540))
pygame.display.set_caption("Wickham: Cat Launcher Edition")
clock = pygame.time.Clock()

# Create our cat player in the middle of the screen
cat_player = Player(480, 270)

running = True
while running:
    dt = clock.tick(60) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update the player
    cat_player.update(dt)

    # Draw everything
    screen.fill((20, 24, 32)) # Dark blue background
    cat_player.draw(screen)
    
    pygame.display.flip()

pygame.quit()