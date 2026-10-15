import pygame

pygame.init()
screen = pygame.display.set_mode((960, 540))
pygame.display.set_caption("Wickham")
clock = pygame.time.Clock()

player = pygame.Rect(480, 270, 32, 32)
speed = 200  # pixels per second

running = True
while running:
    dt = clock.tick(60) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    player.x += (keys[pygame.K_d] - keys[pygame.K_a]) * speed * dt
    player.y += (keys[pygame.K_s] - keys[pygame.K_w]) * speed * dt

    screen.fill((20, 24, 32))
    pygame.draw.rect(screen, (240, 200, 90), player)
    pygame.display.flip()

pygame.quit()