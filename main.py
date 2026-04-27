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
enemy = pygame.Rect(300,200,40,40)
enemy2 = pygame.Rect(600,500,40,40)
PLAYER_SPEED = 5
ENEMY_SPEED = 3
game_over = False
font = pygame.font.Font(None, 36)

score = 0
counter = 0
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
    
    if enemy.x < player.x:
        enemy.x += ENEMY_SPEED
    if enemy.x > player.x:
        enemy.x -= ENEMY_SPEED
    if enemy.y < player.y:
        enemy.y += ENEMY_SPEED
    if enemy.y > player.y:
        enemy.y -= ENEMY_SPEED


    
    if enemy.x < -40:
        enemy.x = SCREEN_WIDTH + 39
    elif enemy.x > SCREEN_WIDTH + 40:
        enemy.x = -39
    elif enemy.y < -40:
        enemy.y = SCREEN_HEIGHT+39
    elif enemy.y > SCREEN_HEIGHT +40:
        enemy.y = -39

    if enemy2.x < player.x:
        enemy2.x += ENEMY_SPEED+1
    if enemy2.x > player.x:
        enemy2.x -= ENEMY_SPEED+1
    if enemy2.y < player.y:
        enemy2.y += ENEMY_SPEED+1
    if enemy2.y > player.y:
        enemy2.y -= ENEMY_SPEED+1


    
    if enemy2.x < -40:
        enemy2.x = SCREEN_WIDTH + 39
    elif enemy2.x > SCREEN_WIDTH + 40:
        enemy2.x = -39
    elif enemy2.y < -40:
        enemy2.y = SCREEN_HEIGHT+39
    elif enemy2.y > SCREEN_HEIGHT +40:
        enemy2.y = -39
        
    counter += 1
    if counter == 60:
        score += 1
        counter = 0
        PLAYER_SPEED = randint(5,10)
        ENEMY_SPEED = randint(5,8)

    if player.colliderect(enemy) or player.colliderect(enemy2):
        screen.fill((255,0,0))
        pygame.display.flip()
        pygame.time.delay(100)
        game_over = True

    if game_over:
        player.x,player.y = SCREEN_WIDTH//2,SCREEN_HEIGHT//2
        enemy.x,enemy.y = randint(0,SCREEN_WIDTH),randint(0,SCREEN_HEIGHT)
        enemy2.x,enemy2.y = randint(0,SCREEN_WIDTH),randint(0,SCREEN_HEIGHT)
        score = 0
        game_over = False

    # ── RENDER ───────────────────────────

    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, player)
    pygame.draw.rect(screen, RED, enemy)
    pygame.draw.rect(screen, GRAY, enemy2)
    score_text = font.render(f"Score: {score}", True, (255,255,255))
    screen.blit(score_text, (10,10))
    pygame.display.flip()
    clock.tick(FPS)

# ─────────────────────────────────────────
#  CLEAN UP
# ─────────────────────────────────────────
pygame.quit()
sys.exit()