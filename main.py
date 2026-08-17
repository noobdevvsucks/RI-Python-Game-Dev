import os
import sys
from random import randint, uniform
import pygame


# =============================================================================
# HEADLESS / CODESPACES ENVIRONMENT FIXES
# =============================================================================

if not os.environ.get("DISPLAY"):
    os.environ["DISPLAY"] = ":99"

if not os.environ.get("XDG_RUNTIME_DIR"):
    os.environ["XDG_RUNTIME_DIR"] = "/tmp/runtime-vscode"
    os.makedirs("/tmp/runtime-vscode", exist_ok=True)

os.environ["SDL_AUDIODRIVER"] = "dummy"

pygame.init()


# =============================================================================
# CONSTANTS
# =============================================================================

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600

TITLE = "no game"

FPS = 60


# =============================================================================
# PLAYER
# =============================================================================

PLAYER_SIZE = 40

PLAYER_ACCELERATION = 0.25
PLAYER_DECELERATION = 0.12
PLAYER_MAX_SPEED = 10


# =============================================================================
# ENEMIES
# =============================================================================

# Half the size of the teleport marker
ENEMY_SIZE = 8

MIN_ENEMY_SPEED = 1.0
MAX_ENEMY_SPEED = 3.0

# How quickly enemy velocity changes
ENEMY_ACCELERATION = 0.025

# How much random jitter enemies receive
ENEMY_JITTER = 0.25


# =============================================================================
# TELEPORT
# =============================================================================

TELEPORT_SIZE = 15

# Cooldown after actually teleporting
TELEPORT_COOLDOWN = 10.0


# =============================================================================
# SCORE
# =============================================================================

# One point every 60 frames / approximately 1 second
SCORE_INTERVAL = 60

# One additional enemy every 2 points
ENEMY_SCORE_INTERVAL = 2


# =============================================================================
# COLOURS
# =============================================================================

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

RED = (255, 0, 0)

GRAY = (100, 100, 100)

GREEN = (0, 255, 0)


# =============================================================================
# FONTS
# =============================================================================

font = pygame.font.Font(None, 36)
medium_font = pygame.font.Font(None, 50)
big_font = pygame.font.Font(None, 80)


# =============================================================================
# SCREEN
# =============================================================================

screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT)
)

pygame.display.set_caption(TITLE)

clock = pygame.time.Clock()


# =============================================================================
# ENEMY CLASS
# =============================================================================

class Enemy:

    def __init__(self, x, y):

        # Position
        self.position = pygame.Vector2(
            x,
            y
        )

        # Velocity
        self.velocity = pygame.Vector2(
            0,
            0
        )

        # Current target speed
        self.speed = uniform(
            MIN_ENEMY_SPEED,
            MAX_ENEMY_SPEED
        )

        # Random movement offset
        self.jitter = pygame.Vector2(
            uniform(
                -ENEMY_JITTER,
                ENEMY_JITTER
            ),
            uniform(
                -ENEMY_JITTER,
                ENEMY_JITTER
            )
        )

        # How often the jitter changes
        self.jitter_timer = randint(
            30,
            70
        )

        # How often the enemy's speed changes
        self.speed_timer = randint(
            120,
            300
        )

        # Collision rectangle
        self.rect = pygame.Rect(
            int(x),
            int(y),
            ENEMY_SIZE,
            ENEMY_SIZE
        )


    # =========================================================================
    # UPDATE
    # =========================================================================

    def update(self, player_position):

        # ---------------------------------------------------------------------
        # CHANGE JITTER OCCASIONALLY
        # ---------------------------------------------------------------------

        self.jitter_timer -= 1

        if self.jitter_timer <= 0:

            self.jitter.x = uniform(
                -ENEMY_JITTER,
                ENEMY_JITTER
            )

            self.jitter.y = uniform(
                -ENEMY_JITTER,
                ENEMY_JITTER
            )

            # Higher number = less frequent jitter
            self.jitter_timer = randint(
                30,
                70
            )


        # ---------------------------------------------------------------------
        # CHANGE SPEED OCCASIONALLY
        # ---------------------------------------------------------------------

        self.speed_timer -= 1

        if self.speed_timer <= 0:

            self.speed = uniform(
                MIN_ENEMY_SPEED,
                MAX_ENEMY_SPEED
            )

            # Speed changes every 2–5 seconds
            self.speed_timer = randint(
                120,
                300
            )


        # ---------------------------------------------------------------------
        # FIND DIRECTION TO PLAYER
        # ---------------------------------------------------------------------

        direction = (
            player_position -
            self.position
        )

        if direction.length_squared() > 0:

            direction = direction.normalize()

            # Add subtle random movement
            direction += self.jitter

            if direction.length_squared() > 0:

                direction = direction.normalize()


        # ---------------------------------------------------------------------
        # TARGET VELOCITY
        # ---------------------------------------------------------------------

        target_velocity = (
            direction *
            self.speed
        )


        # ---------------------------------------------------------------------
        # ACCELERATE TOWARD TARGET VELOCITY
        # ---------------------------------------------------------------------

        self.velocity = self.velocity.lerp(
            target_velocity,
            ENEMY_ACCELERATION
        )


        # ---------------------------------------------------------------------
        # MOVE
        # ---------------------------------------------------------------------

        self.position += self.velocity


        # ---------------------------------------------------------------------
        # SCREEN WRAPPING
        # ---------------------------------------------------------------------

        if self.position.x < -ENEMY_SIZE:

            self.position.x = SCREEN_WIDTH

        elif self.position.x > SCREEN_WIDTH:

            self.position.x = -ENEMY_SIZE


        if self.position.y < -ENEMY_SIZE:

            self.position.y = SCREEN_HEIGHT

        elif self.position.y > SCREEN_HEIGHT:

            self.position.y = -ENEMY_SIZE


        # ---------------------------------------------------------------------
        # UPDATE COLLISION RECTANGLE
        # ---------------------------------------------------------------------

        self.rect.topleft = (
            round(self.position.x),
            round(self.position.y)
        )


    # =========================================================================
    # DRAW
    # =========================================================================

    def draw(self, surface):

        pygame.draw.rect(
            surface,
            RED,
            self.rect
        )


# =============================================================================
# GAME CLASS
# =============================================================================

class Game:

    def __init__(self):

        self.state = "menu"


        # ---------------------------------------------------------------------
        # PLAYER
        # ---------------------------------------------------------------------

        self.player_position = pygame.Vector2(
            100,
            100
        )

        self.player_velocity = pygame.Vector2(
            0,
            0
        )


        # ---------------------------------------------------------------------
        # TELEPORT
        # ---------------------------------------------------------------------

        # True means there is a teleport ready to place
        self.teleport_available = True

        # Vector2 means a teleport marker currently exists
        self.teleport_marker = None

        # Seconds remaining on cooldown
        self.teleport_cooldown = 0.0


        # ---------------------------------------------------------------------
        # SCORE
        # ---------------------------------------------------------------------

        self.score = 0

        self.score_counter = 0


        # ---------------------------------------------------------------------
        # ENEMIES
        # ---------------------------------------------------------------------

        self.enemies = []


        # ---------------------------------------------------------------------
        # INITIALIZE
        # ---------------------------------------------------------------------

        self.reset()

        # Start at menu
        self.state = "menu"


    # =========================================================================
    # RESET
    # =========================================================================

    def reset(self):

        # Player
        self.player_position.update(
            100,
            100
        )

        self.player_velocity.update(
            0,
            0
        )


        # Score
        self.score = 0

        self.score_counter = 0


        # Teleport
        self.teleport_available = True

        self.teleport_marker = None

        self.teleport_cooldown = 0.0


        # Enemies
        self.enemies.clear()


        # Start with two enemies
        self.add_enemy(
            300,
            200
        )

        self.add_enemy(
            600,
            500
        )


    # =========================================================================
    # ADD ENEMY
    # =========================================================================

    def add_enemy(self, x=None, y=None):

        # If no position is provided, find a random safe position
        if x is None or y is None:

            while True:

                x = randint(
                    0,
                    SCREEN_WIDTH - ENEMY_SIZE
                )

                y = randint(
                    0,
                    SCREEN_HEIGHT - ENEMY_SIZE
                )

                spawn_position = pygame.Vector2(
                    x,
                    y
                )

                distance = (
                    spawn_position.distance_to(
                        self.player_position
                    )
                )

                # Don't spawn directly next to player
                if distance > 200:
                    break


        self.enemies.append(
            Enemy(
                x,
                y
            )
        )


    # =========================================================================
    # TELEPORT
    # =========================================================================

    def teleport(self):

        # ---------------------------------------------------------------------
        # PLACE TELEPORT
        # ---------------------------------------------------------------------

        if (
            self.teleport_available
            and self.teleport_marker is None
        ):

            # Store player's current location
            self.teleport_marker = pygame.Vector2(
                self.player_position
            )

            # Teleport is no longer in inventory
            self.teleport_available = False

            return


        # ---------------------------------------------------------------------
        # USE TELEPORT
        # ---------------------------------------------------------------------

        if self.teleport_marker is not None:

            # Move player to marker
            self.player_position.update(
                self.teleport_marker
            )

            # Remove all player momentum
            self.player_velocity.update(
                0,
                0
            )

            # Remove teleport marker
            self.teleport_marker = None

            # Start the 10-second cooldown
            self.teleport_cooldown = (
                TELEPORT_COOLDOWN
            )

            # Teleport is unavailable during cooldown
            self.teleport_available = False


    # =========================================================================
    # TELEPORT COOLDOWN
    # =========================================================================

    def update_teleport(self, dt):

        # Only run if the teleport is cooling down
        if self.teleport_cooldown > 0:

            self.teleport_cooldown -= dt


            # Cooldown finished
            if self.teleport_cooldown <= 0:

                self.teleport_cooldown = 0

                self.teleport_available = True


    # =========================================================================
    # PLAYER UPDATE
    # =========================================================================

    def update_player(self):

        keys = pygame.key.get_pressed()


        # Current acceleration
        acceleration = pygame.Vector2(
            0,
            0
        )


        # ---------------------------------------------------------------------
        # INPUT
        # ---------------------------------------------------------------------

        if keys[pygame.K_LEFT]:

            acceleration.x -= PLAYER_ACCELERATION


        if keys[pygame.K_RIGHT]:

            acceleration.x += PLAYER_ACCELERATION


        if keys[pygame.K_UP]:

            acceleration.y -= PLAYER_ACCELERATION


        if keys[pygame.K_DOWN]:

            acceleration.y += PLAYER_ACCELERATION


        # ---------------------------------------------------------------------
        # ACCELERATE
        # ---------------------------------------------------------------------

        if acceleration.length_squared() > 0:

            self.player_velocity += acceleration


        # ---------------------------------------------------------------------
        # DECELERATE
        # ---------------------------------------------------------------------

        else:

            speed = self.player_velocity.length()

            if speed > 0:

                new_speed = max(
                    0,
                    speed - PLAYER_DECELERATION
                )

                self.player_velocity.scale_to_length(
                    new_speed
                )


        # ---------------------------------------------------------------------
        # LIMIT PLAYER SPEED
        # ---------------------------------------------------------------------

        speed = self.player_velocity.length()

        if speed > PLAYER_MAX_SPEED:

            self.player_velocity.scale_to_length(
                PLAYER_MAX_SPEED
            )


        # ---------------------------------------------------------------------
        # MOVE PLAYER
        # ---------------------------------------------------------------------

        self.player_position += self.player_velocity


        # ---------------------------------------------------------------------
        # SCREEN WRAP
        # ---------------------------------------------------------------------

        self.player_position.x %= SCREEN_WIDTH
        self.player_position.y %= SCREEN_HEIGHT


    # =========================================================================
    # ENEMY COUNT
    # =========================================================================

    def update_enemy_count(self):

        # Start with 2 enemies.
        #
        # Every 2 points adds another enemy.
        #
        # Score 0  -> 2 enemies
        # Score 2  -> 3 enemies
        # Score 4  -> 4 enemies
        # Score 6  -> 5 enemies
        # Score 8  -> 6 enemies
        # etc.

        desired_count = (
            2 +
            self.score // ENEMY_SCORE_INTERVAL
        )


        while len(self.enemies) < desired_count:

            self.add_enemy()


    # =========================================================================
    # GAME UPDATE
    # =========================================================================

    def update(self, dt):

        # Don't update gameplay while in menu/game over
        if self.state != "playing":

            return


        # ---------------------------------------------------------------------
        # TELEPORT COOLDOWN
        # ---------------------------------------------------------------------

        self.update_teleport(
            dt
        )


        # ---------------------------------------------------------------------
        # PLAYER
        # ---------------------------------------------------------------------

        self.update_player()


        # ---------------------------------------------------------------------
        # ENEMIES
        # ---------------------------------------------------------------------

        for enemy in self.enemies:

            enemy.update(
                self.player_position
            )


        # ---------------------------------------------------------------------
        # SCORE
        # ---------------------------------------------------------------------

        self.score_counter += 1


        if self.score_counter >= SCORE_INTERVAL:

            self.score += 1

            self.score_counter = 0


            # Add enemies if necessary
            self.update_enemy_count()


        # ---------------------------------------------------------------------
        # PLAYER COLLISION RECTANGLE
        # ---------------------------------------------------------------------

        player_rect = pygame.Rect(
            round(self.player_position.x),
            round(self.player_position.y),
            PLAYER_SIZE,
            PLAYER_SIZE
        )


        # ---------------------------------------------------------------------
        # ENEMY COLLISION
        # ---------------------------------------------------------------------

        for enemy in self.enemies:

            if player_rect.colliderect(
                enemy.rect
            ):

                self.state = "game_over"

                break


    # =========================================================================
    # CENTERED TEXT
    # =========================================================================

    def centered_text(
        self,
        text,
        text_font,
        colour,
        y
    ):

        surface = text_font.render(
            text,
            True,
            colour
        )

        rect = surface.get_rect(
            center=(
                SCREEN_WIDTH // 2,
                y
            )
        )

        screen.blit(
            surface,
            rect
        )


    # =========================================================================
    # MENU
    # =========================================================================

    def draw_menu(self):

        self.centered_text(
            "NO GAME",
            big_font,
            WHITE,
            120
        )

        self.centered_text(
            "Press ENTER to start",
            medium_font,
            GREEN,
            240
        )

        self.centered_text(
            "Arrow keys = accelerate",
            font,
            WHITE,
            320
        )

        self.centered_text(
            "Release arrows = decelerate",
            font,
            WHITE,
            355
        )

        self.centered_text(
            "SHIFT = place / use teleport",
            font,
            GREEN,
            400
        )

        self.centered_text(
            "Teleport recharges 10 seconds after use",
            font,
            GREEN,
            440
        )

        self.centered_text(
            "A new enemy appears every 2 points",
            font,
            GRAY,
            480
        )

        self.centered_text(
            "ESC = quit",
            font,
            GRAY,
            520
        )


    # =========================================================================
    # GAME DRAW
    # =========================================================================

    def draw_game(self):

        # ---------------------------------------------------------------------
        # TELEPORT MARKER
        # ---------------------------------------------------------------------

        if self.teleport_marker is not None:

            marker_rect = pygame.Rect(
                0,
                0,
                TELEPORT_SIZE,
                TELEPORT_SIZE
            )

            marker_rect.center = (
                round(self.teleport_marker.x),
                round(self.teleport_marker.y)
            )

            pygame.draw.rect(
                screen,
                GREEN,
                marker_rect
            )


        # ---------------------------------------------------------------------
        # PLAYER
        # ---------------------------------------------------------------------

        player_rect = pygame.Rect(
            round(self.player_position.x),
            round(self.player_position.y),
            PLAYER_SIZE,
            PLAYER_SIZE
        )

        pygame.draw.rect(
            screen,
            WHITE,
            player_rect
        )


        # ---------------------------------------------------------------------
        # ENEMIES
        # ---------------------------------------------------------------------

        for enemy in self.enemies:

            enemy.draw(
                screen
            )


        # ---------------------------------------------------------------------
        # SCORE
        # ---------------------------------------------------------------------

        score_text = font.render(
            f"Score: {self.score}",
            True,
            WHITE
        )

        screen.blit(
            score_text,
            (10, 10)
        )


        # ---------------------------------------------------------------------
        # ENEMY COUNT
        # ---------------------------------------------------------------------

        enemy_text = font.render(
            f"Enemies: {len(self.enemies)}",
            True,
            RED
        )

        screen.blit(
            enemy_text,
            (10, 45)
        )


        # ---------------------------------------------------------------------
        # TELEPORT STATUS
        # ---------------------------------------------------------------------

        if self.teleport_marker is not None:

            teleport_status = "TELEPORT ACTIVE"

        elif self.teleport_available:

            teleport_status = "TELEPORT READY"

        else:

            teleport_status = (
                f"Teleport: "
                f"{self.teleport_cooldown:.1f}s"
            )


        teleport_text = font.render(
            teleport_status,
            True,
            GREEN
        )

        screen.blit(
            teleport_text,
            (10, 80)
        )


        # ---------------------------------------------------------------------
        # PLAYER SPEED
        # ---------------------------------------------------------------------

        speed_text = font.render(
            f"Speed: {self.player_velocity.length():.1f}",
            True,
            WHITE
        )

        screen.blit(
            speed_text,
            (10, 115)
        )


    # =========================================================================
    # GAME OVER
    # =========================================================================

    def draw_game_over(self):

        screen.fill(
            (50, 0, 0)
        )


        self.centered_text(
            "GAME OVER",
            big_font,
            RED,
            170
        )


        self.centered_text(
            f"Final Score: {self.score}",
            medium_font,
            WHITE,
            270
        )


        self.centered_text(
            f"Enemies: {len(self.enemies)}",
            font,
            RED,
            320
        )


        self.centered_text(
            "Press ENTER to play again",
            font,
            GREEN,
            380
        )


        self.centered_text(
            "Press M for menu",
            font,
            WHITE,
            430
        )


        self.centered_text(
            "Press ESC to quit",
            font,
            GRAY,
            480
        )


    # =========================================================================
    # DRAW
    # =========================================================================

    def draw(self):

        screen.fill(
            BLACK
        )


        if self.state == "menu":

            self.draw_menu()


        elif self.state == "playing":

            self.draw_game()


        elif self.state == "game_over":

            self.draw_game_over()


        pygame.display.flip()


# =============================================================================
# MAIN
# =============================================================================

game = Game()

running = True


while running:

    # =========================================================================
    # EVENTS
    # =========================================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False


        elif event.type == pygame.KEYDOWN:

            # -----------------------------------------------------------------
            # ESCAPE
            # -----------------------------------------------------------------

            if event.key == pygame.K_ESCAPE:

                running = False


            # -----------------------------------------------------------------
            # MENU
            # -----------------------------------------------------------------

            elif game.state == "menu":

                if event.key == pygame.K_RETURN:

                    game.reset()

                    game.state = "playing"


            # -----------------------------------------------------------------
            # PLAYING
            # -----------------------------------------------------------------

            elif game.state == "playing":

                if event.key in (
                    pygame.K_LSHIFT,
                    pygame.K_RSHIFT
                ):

                    game.teleport()


            # -----------------------------------------------------------------
            # GAME OVER
            # -----------------------------------------------------------------

            elif game.state == "game_over":

                if event.key == pygame.K_RETURN:

                    game.reset()

                    game.state = "playing"


                elif event.key == pygame.K_m:

                    game.state = "menu"


    # =========================================================================
    # DELTA TIME
    # =========================================================================

    # Convert milliseconds to seconds.
    #
    # This allows the teleport cooldown to use actual seconds rather
    # than relying on the game's FPS.

    dt = clock.tick(FPS) / 1000.0


    # =========================================================================
    # UPDATE
    # =========================================================================

    game.update(
        dt
    )


    # =========================================================================
    # DRAW
    # =========================================================================

    game.draw()


# =============================================================================
# CLEAN UP
# =============================================================================

pygame.quit()
sys.exit()