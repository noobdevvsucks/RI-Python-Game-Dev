import os
import sys
from random import randint, uniform
import math
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

PLAYER_ACCELERATION = 0.12
PLAYER_DECELERATION = 0.24
PLAYER_MAX_SPEED = 10


# =============================================================================
# ENEMIES
# =============================================================================

ENEMY_SIZE = 8

MIN_ENEMY_SPEED = 1.0
MAX_ENEMY_SPEED = 3.0

ENEMY_ACCELERATION = 0.025

ENEMY_JITTER = 0.25


# =============================================================================
# BEAMS
# =============================================================================

BEAM_WIDTH = 10

BEAM_WARNING_DURATION = 1.0

BEAM_DURATION = 1.0

BEAM_COUNT = 3

SCREEN_SHAKE_AMOUNT = 12

SCREEN_SHAKE_DURATION = 0.25

BEAM_COLOUR = (255, 0, 0)


# =============================================================================
# TELEPORT
# =============================================================================

TELEPORT_SIZE = 15

TELEPORT_COOLDOWN = 10.0


# =============================================================================
# SCORE
# =============================================================================

SCORE_INTERVAL = 60

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

        self.position = pygame.Vector2(
            x,
            y
        )

        self.velocity = pygame.Vector2(
            0,
            0
        )

        self.speed = uniform(
            MIN_ENEMY_SPEED,
            MAX_ENEMY_SPEED
        )

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

        self.jitter_timer = randint(
            30,
            70
        )

        self.speed_timer = randint(
            120,
            300
        )

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

            self.jitter_timer = randint(
                30,
                70
            )


        self.speed_timer -= 1

        if self.speed_timer <= 0:

            self.speed = uniform(
                MIN_ENEMY_SPEED,
                MAX_ENEMY_SPEED
            )

            self.speed_timer = randint(
                120,
                300
            )


        direction = (
            player_position -
            self.position
        )

        if direction.length_squared() > 0:

            direction = direction.normalize()

            direction += self.jitter

            if direction.length_squared() > 0:

                direction = direction.normalize()


        target_velocity = (
            direction *
            self.speed
        )

        self.velocity = self.velocity.lerp(
            target_velocity,
            ENEMY_ACCELERATION
        )

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

        self.teleport_available = True

        self.teleport_marker = None

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
        # BEAMS
        # ---------------------------------------------------------------------

        self.beam_active = False

        self.beam_number = 0

        self.beam_phase = "warning"

        self.beam_timer = 0.0

        self.beam_angle = 0.0

        self.beam_start = None

        self.beam_end = None

        self.beam_wave_count = 0


        # ---------------------------------------------------------------------
        # SCREEN SHAKE
        # ---------------------------------------------------------------------

        self.screen_shake_timer = 0.0


        # ---------------------------------------------------------------------
        # INITIALIZE
        # ---------------------------------------------------------------------

        self.reset()

        self.state = "menu"


    # =========================================================================
    # RESET
    # =========================================================================

    def reset(self):

        self.player_position.update(
            100,
            100
        )

        self.player_velocity.update(
            0,
            0
        )


        self.score = 0

        self.score_counter = 0


        self.teleport_available = True

        self.teleport_marker = None

        self.teleport_cooldown = 0.0


        self.enemies.clear()


        # ---------------------------------------------------------------------
        # BEAMS
        # ---------------------------------------------------------------------

        self.beam_active = False

        self.beam_number = 0

        self.beam_phase = "warning"

        self.beam_timer = 0.0

        self.beam_angle = 0.0

        self.beam_start = None

        self.beam_end = None

        self.beam_wave_count = 0


        # ---------------------------------------------------------------------
        # SCREEN SHAKE
        # ---------------------------------------------------------------------

        self.screen_shake_timer = 0.0


        # Start with two enemies.
        # These are also spawned at the center.

        self.add_enemy()

        self.add_enemy()


    # =========================================================================
    # ADD ENEMY
    # =========================================================================

    def add_enemy(self, x=None, y=None):

        # All new enemies spawn at the center of the screen.

        x = (
            SCREEN_WIDTH // 2 -
            ENEMY_SIZE // 2
        )

        y = (
            SCREEN_HEIGHT // 2 -
            ENEMY_SIZE // 2
        )

        self.enemies.append(
            Enemy(
                x,
                y
            )
        )


    # =========================================================================
    # CREATE BEAM
    # =========================================================================

    def create_beam(self):

        self.beam_angle = uniform(
            0,
            math.pi
        )

        direction = pygame.Vector2(
            math.cos(self.beam_angle),
            math.sin(self.beam_angle)
        )

        center = pygame.Vector2(
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2
        )

        length = math.hypot(
            SCREEN_WIDTH,
            SCREEN_HEIGHT
        ) * 2

        self.beam_start = (
            center -
            direction * length
        )

        self.beam_end = (
            center +
            direction * length
        )


    # =========================================================================
    # START BEAM WAVE
    # =========================================================================

    def start_beam_wave(self):

        self.beam_active = True

        self.beam_number = 1

        self.beam_phase = "warning"

        self.beam_timer = (
            BEAM_WARNING_DURATION
        )

        self.create_beam()


    # =========================================================================
    # BEAM HITS PLAYER
    # =========================================================================

    def beam_hits_player(self):

        if (
            self.beam_start is None
            or self.beam_end is None
        ):
            return False


        # ---------------------------------------------------------------------
        # CREATE THE EXACT SAME BEAM USED FOR DRAWING
        # ---------------------------------------------------------------------

        beam_length = math.hypot(
            SCREEN_WIDTH,
            SCREEN_HEIGHT
        ) * 2


        beam_surface = pygame.Surface(
            (
                int(beam_length),
                BEAM_WIDTH
            ),
            pygame.SRCALPHA
        )


        beam_surface.fill(
            (
                255,
                0,
                0,
                255
            )
        )


        rotated_beam = pygame.transform.rotate(
            beam_surface,
            -math.degrees(
                self.beam_angle
            )
        )


        beam_rect = rotated_beam.get_rect(
            center=(
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2
            )
        )


        # ---------------------------------------------------------------------
        # CREATE BEAM MASK
        # ---------------------------------------------------------------------

        beam_mask = pygame.mask.from_surface(
            rotated_beam
        )


        # ---------------------------------------------------------------------
        # CREATE PLAYER MASK
        # ---------------------------------------------------------------------

        player_surface = pygame.Surface(
            (
                PLAYER_SIZE,
                PLAYER_SIZE
            ),
            pygame.SRCALPHA
        )

        player_surface.fill(
            WHITE
        )


        player_mask = pygame.mask.from_surface(
            player_surface
        )


        # ---------------------------------------------------------------------
        # PLAYER POSITION
        # ---------------------------------------------------------------------

        player_rect = pygame.Rect(
            round(self.player_position.x),
            round(self.player_position.y),
            PLAYER_SIZE,
            PLAYER_SIZE
        )


        # ---------------------------------------------------------------------
        # CONVERT PLAYER POSITION INTO BEAM-SURFACE SPACE
        # ---------------------------------------------------------------------

        offset = (
            player_rect.x - beam_rect.x,
            player_rect.y - beam_rect.y
        )


        # ---------------------------------------------------------------------
        # PIXEL-PERFECT COLLISION
        # ---------------------------------------------------------------------

        return (
            beam_mask.overlap(
                player_mask,
                offset
            )
            is not None
        )


    # =========================================================================
    # UPDATE BEAM
    # =========================================================================

    def update_beam(self, dt):

        if not self.beam_active:

            return


        self.beam_timer -= dt


        # ---------------------------------------------------------------------
        # CURRENT PHASE FINISHED
        # ---------------------------------------------------------------------

        if self.beam_timer <= 0:

            # -----------------------------------------------------------------
            # WARNING -> ACTUAL BEAM
            # -----------------------------------------------------------------

            if self.beam_phase == "warning":

                self.beam_phase = "beam"

                self.beam_timer = (
                    BEAM_DURATION
                )


            # -----------------------------------------------------------------
            # ACTUAL BEAM -> NEXT WARNING
            # -----------------------------------------------------------------

            else:

                self.beam_number += 1


                # All three beams finished
                if self.beam_number > BEAM_COUNT:

                    self.beam_active = False

                    self.beam_number = 0

                    self.beam_timer = 0.0

                    self.beam_start = None

                    self.beam_end = None


                else:

                    self.create_beam()

                    self.beam_phase = "warning"

                    self.beam_timer = (
                        BEAM_WARNING_DURATION
                    )


        # ---------------------------------------------------------------------
        # PLAYER COLLISION
        # ---------------------------------------------------------------------

        # Warning beams do not hurt the player.

        if (
            self.beam_active
            and self.beam_phase == "beam"
        ):

            if self.beam_hits_player():

                self.screen_shake_timer = (
                    SCREEN_SHAKE_DURATION
                )

                self.state = "game_over"

                return


    # =========================================================================
    # SCREEN SHAKE
    # =========================================================================

    def update_screen_shake(self, dt):

        if self.screen_shake_timer > 0:

            self.screen_shake_timer -= dt

            if self.screen_shake_timer < 0:

                self.screen_shake_timer = 0


    # =========================================================================
    # GET SCREEN SHAKE
    # =========================================================================

    def get_screen_shake(self):

        if self.screen_shake_timer <= 0:

            return 0, 0


        strength = (
            SCREEN_SHAKE_AMOUNT *
            (
                self.screen_shake_timer /
                SCREEN_SHAKE_DURATION
            )
        )


        return (
            randint(
                -int(strength),
                int(strength)
            ),
            randint(
                -int(strength),
                int(strength)
            )
        )


    # =========================================================================
    # TELEPORT
    # =========================================================================

    def teleport(self):

        if (
            self.teleport_available
            and self.teleport_marker is None
        ):

            self.teleport_marker = pygame.Vector2(
                self.player_position
            )

            self.teleport_available = False

            return


        if self.teleport_marker is not None:

            self.player_position.update(
                self.teleport_marker
            )

            self.player_velocity.update(
                0,
                0
            )

            self.teleport_marker = None

            self.teleport_cooldown = (
                TELEPORT_COOLDOWN
            )

            self.teleport_available = False


    # =========================================================================
    # TELEPORT COOLDOWN
    # =========================================================================

    def update_teleport(self, dt):

        if self.teleport_cooldown > 0:

            self.teleport_cooldown -= dt


            if self.teleport_cooldown <= 0:

                self.teleport_cooldown = 0

                self.teleport_available = True


    # =========================================================================
    # PLAYER UPDATE
    # =========================================================================

    def update_player(self):

        keys = pygame.key.get_pressed()


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
        # SCREEN BOUNDARIES
        # ---------------------------------------------------------------------

        if self.player_position.x < 0:

            self.player_position.x = 0

            self.player_velocity.x = 0

        elif (
            self.player_position.x >
            SCREEN_WIDTH - PLAYER_SIZE
        ):

            self.player_position.x = (
                SCREEN_WIDTH -
                PLAYER_SIZE
            )

            self.player_velocity.x = 0


        if self.player_position.y < 0:

            self.player_position.y = 0

            self.player_velocity.y = 0

        elif (
            self.player_position.y >
            SCREEN_HEIGHT - PLAYER_SIZE
        ):

            self.player_position.y = (
                SCREEN_HEIGHT -
                PLAYER_SIZE
            )

            self.player_velocity.y = 0


    # =========================================================================
    # ENEMY COUNT
    # =========================================================================

    def update_enemy_count(self):

        desired_count = (
            2 +
            self.score // ENEMY_SCORE_INTERVAL
        )


        # ---------------------------------------------------------------------
        # START LASER WAVE AT EVERY 10-ENEMY THRESHOLD
        # ---------------------------------------------------------------------

        reached_waves = (
            desired_count // 10
        )


        if reached_waves > self.beam_wave_count:

            self.start_beam_wave()

            self.beam_wave_count += 1

            return


        # ---------------------------------------------------------------------
        # DON'T SPAWN ENEMIES DURING LASER
        # ---------------------------------------------------------------------

        if self.beam_active:

            return


        # ---------------------------------------------------------------------
        # SPAWN MISSING ENEMIES
        # ---------------------------------------------------------------------

        while len(self.enemies) < desired_count:

            self.add_enemy()


    # =========================================================================
    # GAME UPDATE
    # =========================================================================

    def update(self, dt):

        if self.state != "playing":

            self.update_screen_shake(
                dt
            )

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
        # BEAMS
        # ---------------------------------------------------------------------

        self.update_beam(
            dt
        )


        # ---------------------------------------------------------------------
        # SCREEN SHAKE
        # ---------------------------------------------------------------------

        self.update_screen_shake(
            dt
        )


        # ---------------------------------------------------------------------
        # SCORE
        # ---------------------------------------------------------------------

        self.score_counter += 1


        if self.score_counter >= SCORE_INTERVAL:

            self.score += 1

            self.score_counter = 0

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
            "ARENA",
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

        game_surface = pygame.Surface(
            (
                SCREEN_WIDTH,
                SCREEN_HEIGHT
            )
        )

        game_surface.fill(
            BLACK
        )


        # ---------------------------------------------------------------------
        # BEAM
        # ---------------------------------------------------------------------

        if self.beam_active:

            beam_length = math.hypot(
                SCREEN_WIDTH,
                SCREEN_HEIGHT
            ) * 2


            beam_surface = pygame.Surface(
                (
                    int(beam_length),
                    BEAM_WIDTH
                ),
                pygame.SRCALPHA
            )


            # -----------------------------------------------------------------
            # WARNING
            # -----------------------------------------------------------------

            if self.beam_phase == "warning":

                beam_surface.fill(
                    (
                        255,
                        0,
                        0,
                        70
                    )
                )


            # -----------------------------------------------------------------
            # ACTUAL BEAM
            # -----------------------------------------------------------------

            else:

                beam_surface.fill(
                    (
                        255,
                        0,
                        0,
                        255
                    )
                )


            rotated_beam = pygame.transform.rotate(
                beam_surface,
                -math.degrees(
                    self.beam_angle
                )
            )


            beam_rect = rotated_beam.get_rect(
                center=(
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2
                )
            )


            game_surface.blit(
                rotated_beam,
                beam_rect
            )


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
                game_surface,
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
            game_surface,
            WHITE,
            player_rect
        )


        # ---------------------------------------------------------------------
        # ENEMIES
        # ---------------------------------------------------------------------

        for enemy in self.enemies:

            enemy.draw(
                game_surface
            )


        # ---------------------------------------------------------------------
        # SCORE
        # ---------------------------------------------------------------------

        score_text = font.render(
            f"Score: {self.score}",
            True,
            WHITE
        )

        game_surface.blit(
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

        game_surface.blit(
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

        game_surface.blit(
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

        game_surface.blit(
            speed_text,
            (10, 115)
        )


        # ---------------------------------------------------------------------
        # BEAM STATUS
        # ---------------------------------------------------------------------

        if self.beam_active:

            if self.beam_phase == "warning":

                beam_status = (
                    f"WARNING "
                    f"{self.beam_number}/{BEAM_COUNT}"
                )

            else:

                beam_status = (
                    f"BEAM "
                    f"{self.beam_number}/{BEAM_COUNT}"
                )


            beam_text = font.render(
                beam_status,
                True,
                RED
            )

            game_surface.blit(
                beam_text,
                (
                    SCREEN_WIDTH - 190,
                    10
                )
            )


        # ---------------------------------------------------------------------
        # SCREEN SHAKE
        # ---------------------------------------------------------------------

        shake_x, shake_y = self.get_screen_shake()


        screen.fill(
            BLACK
        )

        screen.blit(
            game_surface,
            (
                shake_x,
                shake_y
            )
        )

        pygame.display.flip()


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


        pygame.display.flip()


    # =========================================================================
    # DRAW
    # =========================================================================

    def draw(self):

        if self.state == "menu":

            screen.fill(
                BLACK
            )

            self.draw_menu()

            pygame.display.flip()


        elif self.state == "playing":

            self.draw_game()


        elif self.state == "game_over":

            self.draw_game_over()


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