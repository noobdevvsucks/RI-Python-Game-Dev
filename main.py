import os
import sys

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
PLAYER_SPEED = 3
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
    

    # ── RENDER ───────────────────────────

    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, player)
    pygame.display.flip()
    clock.tick(FPS)

# ─────────────────────────────────────────
#  CLEAN UP
# ─────────────────────────────────────────
pygame.quit()
sys.exit()
