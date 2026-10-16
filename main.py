import pygame
import sys
import os
import pytmx

# 1. Add the src folder to the path BEFORE importing from it
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from player import Player
from npc import NPC
from hud import HUD

pygame.init()
SCREEN_W, SCREEN_H = 960, 540
ZOOM = 2                                   # 1 = tiny pixels, 2 = chunky retro look, 3 = very close
VIEW_W, VIEW_H = SCREEN_W // ZOOM, SCREEN_H // ZOOM
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Wickham: Warrior Edition")
clock = pygame.time.Clock()
view = pygame.Surface((VIEW_W, VIEW_H))    # the game is drawn small, then scaled up

# ---------- load the Tiled map ----------
map_path = os.path.join(os.path.dirname(__file__), 'assets', 'maps', 'wickham_village.tmx')
tmx_data = pytmx.load_pygame(map_path)
MAP_W = tmx_data.width * tmx_data.tilewidth
MAP_H = tmx_data.height * tmx_data.tileheight

# ---------- read the object layers ----------
start_x, start_y = MAP_W // 2, MAP_H // 2
collision_rects = []
npc_list = [] # List to hold our wandering NPCs

for layer in tmx_data.layers:
    if not isinstance(layer, pytmx.TiledObjectGroup):
        continue
    if layer.name == 'spawns':
        for obj in layer:
            if obj.name == 'player_start':
                start_x, start_y = obj.x, obj.y
            
            # --- LOAD NPCS FROM TILED ---
            elif obj.type == 'npc':
                # Assign a color based on the NPC name
                if "rowan" in obj.name: npc_color = (200, 50, 50)       # Red
                elif "shop" in obj.name: npc_color = (50, 200, 50)      # Green
                elif "mira" in obj.name: npc_color = (200, 50, 200)     # Purple
                elif "black" in obj.name: npc_color = (100, 100, 100)   # Grey
                else: npc_color = (255, 255, 255)                       # White
                
                # Get dialogue from Tiled properties
                dialogue = obj.properties.get('dialogue', "Hello.")
                
                npc_list.append(NPC(obj.x, obj.y, npc_color, obj.name, dialogue))
            # ----------------------------
    elif layer.name == 'collision':
        for obj in layer:
            collision_rects.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
print(f"Loaded {len(collision_rects)} collision rects, {len(npc_list)} NPCs, player starts at ({start_x}, {start_y})")

warrior_player = Player(start_x, start_y)
hud = HUD((SCREEN_W, SCREEN_H))

# ---------- pre-render the whole map once ----------
map_surface = pygame.Surface((MAP_W, MAP_H)).convert()
map_surface.fill((20, 24, 32))
for layer in tmx_data.layers:
    if isinstance(layer, pytmx.TiledTileLayer):
        for x, y, image in layer.tiles():
            map_surface.blit(image, (x * tmx_data.tilewidth, y * tmx_data.tileheight))

show_debug = False   # F1 toggles collision boxes
running = True
while running:
    dt = clock.tick(60) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:
                show_debug = not show_debug
            elif event.key == pygame.K_r and warrior_player.dead:
                warrior_player.respawn(start_x, start_y)
            # --- test keys: remove once enemies/hazards exist ---
            elif event.key == pygame.K_h:
                warrior_player.take_damage(2)       # H = lose one heart
            elif event.key == pygame.K_g:
                warrior_player.heal(2)              # G = regain one heart
            # --- NPC Interaction ---
            elif event.key == pygame.K_e:
                for npc in npc_list:
                    # Check if player is touching the NPC (with a slightly forgiving hitbox)
                    if warrior_player.rect.colliderect(npc.rect.inflate(10, 10)):
                        print(f"{npc.name}: {npc.dialogue}")

    warrior_player.update(dt, collision_rects)

    # Update all NPCs
    for npc in npc_list:
        npc.update(dt, collision_rects)

    # camera: centre on the player, never show outside the map
    px, py = warrior_player.rect.center
    cam_x = max(0, min(px - VIEW_W // 2, MAP_W - VIEW_W))
    cam_y = max(0, min(py - VIEW_H // 2, MAP_H - VIEW_H))

    view.blit(map_surface, (0, 0), pygame.Rect(cam_x, cam_y, VIEW_W, VIEW_H))
    
    # Draw NPCs (so they appear under the player if the player walks above them)
    for npc in npc_list:
        npc.draw(view, (cam_x, cam_y))
        
    warrior_player.draw(view, (cam_x, cam_y))
    
    if show_debug:
        for r in collision_rects:
            pygame.draw.rect(view, (255, 0, 0), r.move(-cam_x, -cam_y), 1)
        pygame.draw.rect(view, (0, 255, 0), warrior_player.rect.move(-cam_x, -cam_y), 1)
        if warrior_player.attack_rect:
            pygame.draw.rect(view, (255, 255, 0), warrior_player.attack_rect.move(-cam_x, -cam_y), 1)
        # Draw NPC debug boxes too
        for npc in npc_list:
            pygame.draw.rect(view, (0, 0, 255), npc.rect.move(-cam_x, -cam_y), 1)

    pygame.transform.scale(view, (SCREEN_W, SCREEN_H), screen)

    # HUD is drawn on the full-size screen so the hearts stay crisp
    hud.update(dt, warrior_player.hp)
    hud.draw(screen, warrior_player.hp, warrior_player.max_hp)
    if warrior_player.dead:
        hud.draw_death(screen)
    pygame.display.flip()

pygame.quit()