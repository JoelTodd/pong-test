"""Core gameplay loop for the Pong clone."""

import pygame
import sys
import random
import math

from constants import Screen, Paddle, Ball, Powerup
from utils import snappy_ease, duplicate_velocity
from entities import create_ball, spawn_powerup


def run_game(screen, clock, font, debug_font) -> int:
    """Run one session of Pong and return the player's score."""

    debug_mode = False

    # Set up the player's paddle near the bottom of the screen
    paddle = pygame.Rect(
        Screen.WIDTH // 2 - Paddle.WIDTH // 2,
        Screen.HEIGHT - 20 - Paddle.HEIGHT,
        Paddle.WIDTH,
        Paddle.HEIGHT,
    )

    balls = [create_ball()]  # list of active balls on the screen
    powerup = None           # there may or may not be a powerup present
    score = 0

    paddle_vx: float = 0.0           # current horizontal velocity
    paddle_target_vx: float = 0.0    # desired velocity based on input
    paddle_start_vx: float = 0.0     # velocity at the start of a transition
    transition_t = 1.0      # progress of velocity transition

    while True:
        # ``dt`` is the time (in seconds) since the last loop iteration
        dt = clock.tick(Screen.FPS) / 1000.0

        # Handle window events and toggle debug mode with the M key
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                debug_mode = not debug_mode

        # Read player input for left/right movement
        keys = pygame.key.get_pressed()
        new_target_vx = 0
        if keys[pygame.K_LEFT] and paddle.left > 0:
            new_target_vx = -Paddle.SPEED
        if keys[pygame.K_RIGHT] and paddle.right < Screen.WIDTH:
            new_target_vx = Paddle.SPEED

        # Start a smooth transition whenever the target velocity changes
        if new_target_vx != paddle_target_vx:
            paddle_target_vx = new_target_vx
            paddle_start_vx = paddle_vx
            transition_t = 0.0

        # Interpolate towards the target velocity using easing
        if transition_t < 1.0:
            transition_t = min(transition_t + Paddle.TRANSITION_RATE * dt, 1.0)
            prog = snappy_ease(transition_t)
            paddle_vx = paddle_start_vx + (
                paddle_target_vx - paddle_start_vx
            ) * prog
        else:
            paddle_vx = paddle_target_vx

        # Move the paddle and keep it on screen
        paddle.x = int(paddle.x + paddle_vx)
        paddle.clamp_ip(pygame.Rect(0, 0, Screen.WIDTH, Screen.HEIGHT))

        # Randomly spawn a powerup
        if powerup is None and random.random() < Powerup.CHANCE:
            powerup = spawn_powerup()

        # Update all balls
        for b in balls[:]:
            rect = b["rect"]
            prev_vx, prev_vy = b["vx"], b["vy"]

            # Apply gravity then update position using sub-pixel accuracy
            b["vy"] += Ball.GRAVITY
            b["x"] += b["vx"]
            b["y"] += b["vy"]
            rect.x = round(b["x"])
            rect.y = round(b["y"])

            # Bounce off the side walls
            if rect.left <= 0 or rect.right >= Screen.WIDTH:
                b["vx"] *= -1
            if rect.top <= 0:
                # Bounce off the top and gradually speed up
                b["vy"] *= -1
                speed = math.hypot(b["vx"], b["vy"])
                if speed < Ball.MAX_SPEED:
                    speed = min(speed * Ball.SPEED_INCREMENT, Ball.MAX_SPEED)
                    angle = math.atan2(b["vy"], b["vx"])
                    b["vx"] = math.cos(angle) * speed
                    b["vy"] = math.sin(angle) * speed

            # Bounce off the paddle and angle the ball based on where it hits
            if rect.colliderect(paddle) and b["vy"] > 0:
                offset = (rect.centerx - paddle.centerx) / (Paddle.WIDTH / 2)
                b["vy"] *= -1
                b["vx"] += (
                    offset * Ball.ANGLE_INFLUENCE
                    + paddle_vx * Paddle.VEL_INFLUENCE
                )
                b["vx"] = max(
                    min(b["vx"] * Ball.SPEED_INCREMENT, Ball.MAX_SPEED),
                    -Ball.MAX_SPEED,
                )
                b["vy"] = max(
                    min(b["vy"] * Ball.SPEED_INCREMENT, Ball.MAX_SPEED),
                    -Ball.MAX_SPEED,
                )
                score += 1

            # Handle collisions with the powerup bar
            if powerup:
                p_rect = powerup["rect"]
                ball_id = b["id"]
                if (
                    p_rect.colliderect(rect)
                    and ball_id not in powerup["collided"]
                ):
                    # Duplicate the ball in a new random direction
                    vx_new, vy_new = duplicate_velocity(b["vx"], b["vy"])
                    nb = create_ball(up=b["vy"] < 0, pos=rect.center)
                    nb["vx"], nb["vy"] = vx_new, vy_new
                    powerup["collided"].update({ball_id, nb["id"]})
                    balls.append(nb)
                elif not p_rect.colliderect(rect):
                    # Once a ball leaves, allow it to trigger again later
                    powerup["collided"].discard(ball_id)

            # Compute acceleration for debug display
            if dt > 0:
                b["ax"] = (b["vx"] - prev_vx) / dt
                b["ay"] = (b["vy"] - prev_vy) / dt
            else:
                b["ax"] = b["ay"] = 0.0

            # Remove balls that fall below the screen
            if rect.top > Screen.HEIGHT:
                balls.remove(b)

        # Powerups expire after a set time
        if powerup:
            powerup["timer"] -= dt
            if powerup["timer"] <= 0:
                powerup = None

        # End the round when there are no balls left
        if not balls:
            return score

        screen.fill("black")
        pygame.draw.rect(screen, "white", paddle)
        for b in balls:
            pygame.draw.ellipse(screen, "white", b["rect"])
        if powerup:
            pygame.draw.rect(screen, "yellow", powerup["rect"])

        # Draw the current score in the top-right corner
        score_surf = font.render(f"Score: {score}", True, "white")
        screen.blit(
            score_surf, (Screen.WIDTH - score_surf.get_width() - 10, 10)
        )

        if debug_mode:
            # Display ball statistics on the left side of the screen
            lines = [f"Balls: {len(balls)}"]
            for b in balls:
                speed = math.hypot(b["vx"], b["vy"])
                accel = math.hypot(b["ax"], b["ay"])
                lines.append(f"id {b['id']} spd {speed:.2f} acc {accel:.2f}")
            y = 10
            for line in lines:
                surf = debug_font.render(line, True, "green")
                screen.blit(surf, (10, y))
                y += surf.get_height() + 2

        pygame.display.flip()
