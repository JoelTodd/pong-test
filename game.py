import pygame
import sys
import random
import math

from constants import (
    WIDTH,
    HEIGHT,
    FPS,
    PADDLE_WIDTH,
    PADDLE_HEIGHT,
    PADDLE_SPEED,
    POWERUP_CHANCE,
    TRANSITION_RATE,
    GRAVITY,
    ANGLE_INFLUENCE,
    PADDLE_VEL_INFLUENCE,
    SPEED_INCREMENT,
    MAX_BALL_SPEED,
)
from utils import snappy_ease, duplicate_velocity
from entities import create_ball, spawn_powerup


def run_game(screen, clock, font, debug_font) -> int:
    debug_mode = False

    paddle = pygame.Rect(
        WIDTH // 2 - PADDLE_WIDTH // 2,
        HEIGHT - 20 - PADDLE_HEIGHT,
        PADDLE_WIDTH,
        PADDLE_HEIGHT,
    )

    balls = [create_ball()]
    powerup = None
    score = 0

    paddle_vx = 0
    paddle_target_vx = 0
    paddle_start_vx = 0
    transition_t = 1.0

    while True:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                debug_mode = not debug_mode

        keys = pygame.key.get_pressed()
        new_target_vx = 0
        if keys[pygame.K_LEFT] and paddle.left > 0:
            new_target_vx = -PADDLE_SPEED
        if keys[pygame.K_RIGHT] and paddle.right < WIDTH:
            new_target_vx = PADDLE_SPEED

        if new_target_vx != paddle_target_vx:
            paddle_target_vx = new_target_vx
            paddle_start_vx = paddle_vx
            transition_t = 0.0

        if transition_t < 1.0:
            transition_t = min(transition_t + TRANSITION_RATE * dt, 1.0)
            prog = snappy_ease(transition_t)
            paddle_vx = paddle_start_vx + (paddle_target_vx - paddle_start_vx) * prog
        else:
            paddle_vx = paddle_target_vx

        paddle.x += paddle_vx
        paddle.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

        if powerup is None and random.random() < POWERUP_CHANCE:
            powerup = spawn_powerup()

        for b in balls[:]:
            rect = b["rect"]
            prev_vx, prev_vy = b["vx"], b["vy"]

            b["vy"] += GRAVITY
            rect.x += b["vx"]
            rect.y += b["vy"]

            if rect.left <= 0 or rect.right >= WIDTH:
                b["vx"] *= -1
            if rect.top <= 0:
                b["vy"] *= -1
                speed = math.hypot(b["vx"], b["vy"])
                if speed < MAX_BALL_SPEED:
                    speed = min(speed * SPEED_INCREMENT, MAX_BALL_SPEED)
                    angle = math.atan2(b["vy"], b["vx"])
                    b["vx"] = int(round(math.cos(angle) * speed))
                    b["vy"] = int(round(math.sin(angle) * speed))

            if rect.colliderect(paddle) and b["vy"] > 0:
                offset = (rect.centerx - paddle.centerx) / (PADDLE_WIDTH / 2)
                b["vy"] *= -1
                b["vx"] += offset * ANGLE_INFLUENCE + paddle_vx * PADDLE_VEL_INFLUENCE
                b["vx"] = max(
                    min(b["vx"] * SPEED_INCREMENT, MAX_BALL_SPEED),
                    -MAX_BALL_SPEED,
                )
                b["vy"] = max(
                    min(b["vy"] * SPEED_INCREMENT, MAX_BALL_SPEED),
                    -MAX_BALL_SPEED,
                )
                score += 1

            if powerup:
                p_rect = powerup["rect"]
                ball_id = b["id"]
                if p_rect.colliderect(rect) and ball_id not in powerup["collided"]:
                    vx_new, vy_new = duplicate_velocity(b["vx"], b["vy"])
                    nb = create_ball(up=b["vy"] < 0, pos=rect.center)
                    nb["vx"], nb["vy"] = vx_new, vy_new
                    powerup["collided"].update({ball_id, nb["id"]})
                    balls.append(nb)
                elif not p_rect.colliderect(rect):
                    powerup["collided"].discard(ball_id)

            if dt > 0:
                b["ax"] = (b["vx"] - prev_vx) / dt
                b["ay"] = (b["vy"] - prev_vy) / dt
            else:
                b["ax"] = b["ay"] = 0.0

            if rect.top > HEIGHT:
                balls.remove(b)

        if powerup:
            powerup["timer"] -= dt
            if powerup["timer"] <= 0:
                powerup = None

        if not balls:
            return score

        screen.fill("black")
        pygame.draw.rect(screen, "white", paddle)
        for b in balls:
            pygame.draw.ellipse(screen, "white", b["rect"])
        if powerup:
            pygame.draw.rect(screen, "yellow", powerup["rect"])

        score_surf = font.render(f"Score: {score}", True, "white")
        screen.blit(score_surf, (WIDTH - score_surf.get_width() - 10, 10))

        if debug_mode:
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

