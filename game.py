"""Core gameplay loop for the Pong clone."""

import pygame
import sys
import random
import math

from constants import (
    Screen,
    Paddle,
    Ball,
    DuplicatePowerup,
    PaddleBigPowerup,
    PaddleSmallPowerup,
    SlowPowerup,
    PowerupType,
    POWERUP_COLOURS,
)
from utils import snappy_ease, duplicate_velocity
from entities import create_ball, spawn_powerup
from synth import SOUNDS


def run_game(screen, clock, font, debug_font) -> int:
    """Run one session of Pong and return the player's score."""

    debug_mode = False

    # Set up the player's paddle near the bottom of the screen.
    paddle = pygame.Rect(
        Screen.WIDTH // 2 - Paddle.WIDTH // 2,
        Screen.HEIGHT - 20 - Paddle.HEIGHT,
        Paddle.WIDTH,
        Paddle.HEIGHT,
    )

    balls = [create_ball()]  # List of active balls on the screen.
    powerup = None           # Active powerup, or ``None`` if none is present.
    score = 0
    slow_timer: float = 0.0  # Duration remaining for the slow effect.

    paddle_power_timer = 0.0
    paddle_power_effect: PowerupType | None = None

    # Pre-render the score label so it doesn't need to be recreated.
    score_label_surf = font.render("Score:", True, "white")
    # Track animation progress for the bouncing effect on the score number.
    score_bounce_t = 1.0

    paddle_vx: float = 0.0           # Current horizontal velocity.
    paddle_target_vx: float = 0.0    # Desired velocity based on input.
    paddle_start_vx: float = 0.0     # Velocity at the start of a transition.
    transition_t = 1.0      # Progress of velocity transition.

    while True:
        # ``dt`` is the time (in seconds) since the last loop iteration.
        dt = clock.tick(Screen.FPS) / 1000.0
        if slow_timer > 0:
            slow_timer = max(0.0, slow_timer - dt)
        speed_factor = SlowPowerup.SPEED_FACTOR if slow_timer > 0 else 1.0

        if paddle_power_timer > 0:
            paddle_power_timer -= dt
            if paddle_power_timer <= 0:
                # Restore paddle size.
                center = paddle.centerx
                paddle.width = Paddle.WIDTH
                paddle.centerx = center
                paddle_power_effect = None

        # Handle window events and toggle debug mode with the M key.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                debug_mode = not debug_mode

        # Read player input for left/right movement.
        keys = pygame.key.get_pressed()
        new_target_vx = 0
        if keys[pygame.K_LEFT] and paddle.left > 0:
            new_target_vx = -Paddle.SPEED
        if keys[pygame.K_RIGHT] and paddle.right < Screen.WIDTH:
            new_target_vx = Paddle.SPEED

        # Start a smooth transition whenever the target velocity changes.
        if new_target_vx != paddle_target_vx:
            paddle_target_vx = new_target_vx
            paddle_start_vx = paddle_vx
            transition_t = 0.0

        # Interpolate towards the target velocity using easing.
        if transition_t < 1.0:
            transition_t = min(transition_t + Paddle.TRANSITION_RATE * dt, 1.0)
            prog = snappy_ease(transition_t)
            paddle_vx = paddle_start_vx + (
                paddle_target_vx - paddle_start_vx
            ) * prog
        else:
            paddle_vx = paddle_target_vx

        # Move the paddle and keep it on screen.
        paddle.x = int(paddle.x + paddle_vx)
        paddle.clamp_ip(pygame.Rect(0, 0, Screen.WIDTH, Screen.HEIGHT))

        # Randomly spawn a powerup.
        spawn_prob = (
            DuplicatePowerup.CHANCE
            + PaddleBigPowerup.CHANCE
            + PaddleSmallPowerup.CHANCE
            + SlowPowerup.CHANCE
        )
        if powerup is None and random.random() < spawn_prob:
            powerup = spawn_powerup()
            SOUNDS["powerup"].play()

        # Update all balls.
        for b in balls[:]:
            rect = b["rect"]
            prev_vx, prev_vy = b["vx"], b["vy"]

            # Apply gravity then update position using sub-pixel accuracy.
            b["vy"] += Ball.GRAVITY * speed_factor
            b["x"] += b["vx"] * speed_factor
            b["y"] += b["vy"] * speed_factor
            rect.x = round(b["x"])
            rect.y = round(b["y"])

            # Bounce off the side walls.
            if rect.left <= 0 or rect.right >= Screen.WIDTH:
                b["vx"] *= -1
                SOUNDS["bounce"].play()
            if rect.top <= 0:
                # Bounce off the top and gradually speed up.
                b["vy"] *= -1
                SOUNDS["bounce"].play()
                speed = math.hypot(b["vx"], b["vy"])
                if speed < Ball.MAX_SPEED:
                    speed = min(speed * Ball.SPEED_INCREMENT, Ball.MAX_SPEED)
                    angle = math.atan2(b["vy"], b["vx"])
                    b["vx"] = math.cos(angle) * speed
                    b["vy"] = math.sin(angle) * speed

            # Bounce off the paddle and angle the ball based on where it hits.
            if rect.colliderect(paddle) and b["vy"] > 0:
                offset = (rect.centerx - paddle.centerx) / (Paddle.WIDTH / 2)
                b["vy"] *= -1
                SOUNDS["bounce"].play()
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
                # Restart the bounce animation whenever the score increases.
                score_bounce_t = 0.0

            # Handle collisions with the powerup bar.
            if powerup:
                p_rect = powerup["rect"]
                ball_id = b["id"]
                if powerup["type"] is PowerupType.SLOW:
                    if p_rect.colliderect(rect):
                        slow_timer = SlowPowerup.EFFECT_TIME
                        powerup = None
                else:
                    if (
                        p_rect.colliderect(rect)
                        and ball_id not in powerup["collided"]
                    ):
                        if powerup["type"] is PowerupType.DUPLICATE:
                            vx_new, vy_new = duplicate_velocity(b["vx"], b["vy"])
                            nb = create_ball(up=b["vy"] < 0, pos=rect.center)
                            nb["vx"], nb["vy"] = vx_new, vy_new
                            balls.append(nb)
                            powerup["collided"].update({ball_id, nb["id"]})
                            SOUNDS["powerup"].play()
                        else:
                            factor = (
                                PaddleBigPowerup.ENLARGE_FACTOR
                                if powerup["type"] is PowerupType.PADDLE_BIG
                                else PaddleSmallPowerup.SHRINK_FACTOR
                            )
                            center = paddle.centerx
                            paddle.width = int(Paddle.WIDTH * factor)
                            paddle.centerx = center
                            paddle_power_timer = PaddleBigPowerup.SIZE_DURATION
                            paddle_power_effect = powerup["type"]
                            powerup["collided"].add(ball_id)
                    elif not p_rect.colliderect(rect):
                        # Once a ball leaves, allow it to trigger again later.
                        powerup["collided"].discard(ball_id)

            # Compute acceleration for debug display.
            if dt > 0:
                b["ax"] = (b["vx"] - prev_vx) / dt
                b["ay"] = (b["vy"] - prev_vy) / dt
            else:
                b["ax"] = b["ay"] = 0.0

            # Remove balls that fall below the screen.
            if rect.top > Screen.HEIGHT:
                balls.remove(b)

        # Powerups expire after a set time.
        if powerup:
            powerup["timer"] -= dt
            if powerup["timer"] <= 0:
                powerup = None

        # End the round when there are no balls left.
        if not balls:
            return score

        screen.fill("black")
        pygame.draw.rect(screen, "white", paddle)
        for b in balls:
            pygame.draw.ellipse(screen, "white", b["rect"])
        if powerup:
            colour = POWERUP_COLOURS.get(powerup["type"], "yellow")
            pygame.draw.rect(screen, colour, powerup["rect"])

        # Update the bounce animation timer.
        if score_bounce_t < 1.0:
            score_bounce_t = min(score_bounce_t + dt / 0.3, 1.0)
            offset = -abs(math.sin(score_bounce_t * math.pi)) * 10
        else:
            offset = 0

        # Draw the current score in the top-right corner with bouncing digits.
        score_num_surf = font.render(str(score), True, "white")
        total_w = score_label_surf.get_width() + score_num_surf.get_width() + 5
        x = Screen.WIDTH - total_w - 10
        screen.blit(score_label_surf, (x, 10))
        screen.blit(
            score_num_surf,
            (x + score_label_surf.get_width() + 5, 10 + offset),
        )

        if debug_mode:
            # Display ball statistics on the left side of the screen.
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
