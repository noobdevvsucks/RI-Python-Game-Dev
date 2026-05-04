import os
import sys
from random import randint

# ── Headless / Codespaces environment fixes ───────────────────────────────────
if not os.environ.get("DISPLAY"):
    os.environ["DISPLAY"] = ":99"

if not os.environ.get("XDG_RUNTIME_DIR"):
    os.environ["XDG_RUNTIME_DIR"] = "/tmp/runtime-vscode"
    os.makedirs("/tmp/runtime-vscode", exist_ok=True)

os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame

pygame.init()

SCREEN_WIDTH  = 900
SCREEN_HEIGHT = 600
TITLE         = "no game"
player = pygame.Rect(100,100,40,40)

PLAYER_SPEED = 5
game_over = False
score = 0
collectibles = [pygame.Rect(300,100,20,20),pygame.Rect(500,300,20,20)]
hazard = pygame.Rect(400,200,20,20)
font = pygame.font.Font(None, 36)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(TITLE)

# ─────────────────────────────────────────
#  CLOCK  (controls frames-per-second)
# ─────────────────────────────────────────
clock = pygame.time.Clock()
FPS = 60

# ─────────────────────────────────────────
#  COLOURS  (R, G, B)
# ─────────────────────────────────────────
BLACK  = (  0,   0,   0)
WHITE  = (255, 255, 255)
RED    = (255,   0,   0)
GREEN = (0, 255, 0)
GRAY   = ( 100,  100,  100)

# ─────────────────────────────────────────
#  GAME LOOP
# ─────────────────────────────────────────
running = True

while running:
    # ── EVENT HANDLING ───────────────────s
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # ── UPDATE ───────────────────────────
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        player.x -= PLAYER_SPEED
    if keys[pygame.K_RIGHT]:
        player.x += PLAYER_SPEED
    if keys[pygame.K_UP]:
        player.y -= PLAYER_SPEED
    if keys[pygame.K_DOWN]:
        player.y += PLAYER_SPEED
    
    if player.x < -40:
        player.x = SCREEN_WIDTH + 39
    elif player.x > SCREEN_WIDTH + 40:
        player.x = -39
    elif player.y < -40:
        player.y = SCREEN_HEIGHT+39
    elif player.y > SCREEN_HEIGHT +40:
        player.y = -39
    
    if hazard.x < player.x:
        hazard.x += 3
    if hazard.x > player.x:
        hazard.x -= 3
    if hazard.y < player.y:
        hazard.y += 3
    if hazard.y > player.y:
        hazard.y -= 3

    if player.colliderect(h):
            player.x, player.y = 100,200
            game_over = True
    
    if hazard.x < -40:
        hazard.x = SCREEN_WIDTH + 39
    elif hazard.x > SCREEN_WIDTH + 40:
        hazard.x = -39
    elif hazard.y < -40:
        hazard.y = SCREEN_HEIGHT+39
    elif hazard.y > SCREEN_HEIGHT +40:
        hazard.y = -39

    for c in collectibles[:]:
        if player.colliderect(c):
            collectibles.remove(c)
            score += 1

    if game_over:
        screen.fill(RED)
        pygame.display.flip()
        pygame.time.delay(500)
        score = 0
        collectibles = [pygame.Rect(300,100,20,20),pygame.Rect(500,300,20,20)]
        game_over = False
        

    # ── RENDER ───────────────────────────

    screen.fill(BLACK)
    for c in collectibles:
        pygame.draw.rect(screen, GREEN, c)
    pygame.draw.rect(screen, RED, hazard)
    pygame.draw.rect(screen, WHITE, player)
    score_text = font.render(f"Score: {score}", True, (255,255,255))
    screen.blit(score_text, (10,10))
    
    pygame.display.flip()
    clock.tick(FPS)

# ─────────────────────────────────────────
#  CLEAN UP
# ─────────────────────────────────────────
pygame.quit()
sys.exit()
