"""Autoplay simulation used as a backdrop for the menu screens."""

import random
import math
import pygame

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
from entities import create_ball, spawn_powerup
from utils import duplicate_velocity


class DemoGame:
    """Lightweight game loop that runs automatically on menu screens."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        """Reset the demo to its initial state."""
        self.paddle = pygame.Rect(
            Screen.WIDTH // 2 - Paddle.WIDTH // 2,
            Screen.HEIGHT - 20 - Paddle.HEIGHT,
            Paddle.WIDTH,
            Paddle.HEIGHT,
        )
        self._paddle_center = float(self.paddle.centerx)
        self.paddle_vx: float = 0.0
        self.balls = [create_ball()]  # Start with a single ball.
        self.powerup: dict | None = None
        self.paddle_power_timer = 0.0
        self.slow_timer: float = 0.0

    def update(self, dt: float) -> None:
        """Advance the simulation by ``dt`` seconds."""

        if self.paddle_power_timer > 0:
            self.paddle_power_timer -= dt
            if self.paddle_power_timer <= 0:
                center = self.paddle.centerx
                self.paddle.width = Paddle.WIDTH
                self.paddle.centerx = center

        if self.slow_timer > 0:
            self.slow_timer = max(0.0, self.slow_timer - dt)
        speed_factor = SlowPowerup.SPEED_FACTOR if self.slow_timer > 0 else 1.0

        # Autopilot: track the ball that will strike the paddle next.
        # A small random offset keeps the motion from looking too mechanical.
        if self.balls:
            target_x: float | None = None
            frames_left: int | None = None
            for ball in self.balls:
                tx, fl = self._predict_intercept(ball)
                if frames_left is None or fl < frames_left:
                    target_x, frames_left = tx, fl
            assert target_x is not None and frames_left is not None
            # Add a tiny offset each frame so the paddle motion is not perfectly straight.
            assert target_x is not None
            target_x += random.uniform(-2, 2)

            # Determine when to start moving so the paddle reaches the target.
            dist = abs(target_x - self._paddle_center)
            move_frames = math.ceil(dist / Paddle.SPEED)
            # Aim to arrive a few frames before impact.
            assert frames_left is not None
            start_moving = frames_left <= move_frames + 3

            if start_moving:
                if dist <= Paddle.SPEED:
                    self._paddle_center = target_x
                    self.paddle_vx = 0
                else:
                    direction = 1 if target_x > self._paddle_center else -1
                    self.paddle_vx = direction * Paddle.SPEED
                    self._paddle_center += self.paddle_vx
            else:
                self.paddle_vx = 0

            self.paddle.centerx = int(round(self._paddle_center))
            self.paddle.clamp_ip(
                pygame.Rect(0, 0, Screen.WIDTH, Screen.HEIGHT)
            )

        # Occasionally spawn a powerup.
        spawn_prob = (
            DuplicatePowerup.CHANCE
            + PaddleBigPowerup.CHANCE
            + PaddleSmallPowerup.CHANCE
            + SlowPowerup.CHANCE
        )
        if self.powerup is None and random.random() < spawn_prob:
            self.powerup = spawn_powerup()

        for b in self.balls[:]:
            rect = b["rect"]

            b["vy"] += Ball.GRAVITY * speed_factor
            rect.x += b["vx"] * speed_factor
            rect.y += b["vy"] * speed_factor

            if rect.left <= 0 or rect.right >= Screen.WIDTH:
                b["vx"] *= -1
            if rect.top <= 0:
                b["vy"] *= -1
                speed = math.hypot(b["vx"], b["vy"])
                if speed < Ball.MAX_SPEED:
                    speed = min(speed * Ball.SPEED_INCREMENT, Ball.MAX_SPEED)
                    angle = math.atan2(b["vy"], b["vx"])
                    b["vx"] = int(round(math.cos(angle) * speed))
                    b["vy"] = int(round(math.sin(angle) * speed))

            # Bounce off the paddle.
            if rect.colliderect(self.paddle) and b["vy"] > 0:
                offset = (
                    rect.centerx - self.paddle.centerx
                ) / (Paddle.WIDTH / 2)
                b["vy"] *= -1
                b["vx"] += (
                    offset * Ball.ANGLE_INFLUENCE
                    + self.paddle_vx * Paddle.VEL_INFLUENCE
                )
                b["vx"] = max(
                    min(b["vx"] * Ball.SPEED_INCREMENT, Ball.MAX_SPEED),
                    -Ball.MAX_SPEED,
                )
                b["vy"] = max(
                    min(b["vy"] * Ball.SPEED_INCREMENT, Ball.MAX_SPEED),
                    -Ball.MAX_SPEED,
                )

            # Handle powerup collisions.
            if self.powerup:
                p_rect = self.powerup["rect"]
                ball_id = b["id"]
                if self.powerup["type"] is PowerupType.SLOW:
                    if p_rect.colliderect(rect):
                        self.slow_timer = SlowPowerup.EFFECT_TIME
                        self.powerup = None
                else:
                    if (
                        p_rect.colliderect(rect)
                        and ball_id not in self.powerup["collided"]
                    ):
                        if self.powerup["type"] is PowerupType.DUPLICATE:
                            vx_new, vy_new = duplicate_velocity(
                                b["vx"],
                                b["vy"],
                            )
                            nb = create_ball(up=b["vy"] < 0, pos=rect.center)
                            nb["vx"], nb["vy"] = vx_new, vy_new
                            self.balls.append(nb)
                            self.powerup["collided"].update(
                                {ball_id, nb["id"]}
                            )
                        else:
                            is_big = (
                                self.powerup["type"]
                                is PowerupType.PADDLE_BIG
                            )
                            factor = (
                                PaddleBigPowerup.ENLARGE_FACTOR
                                if is_big
                                else PaddleSmallPowerup.SHRINK_FACTOR
                            )
                            center = self.paddle.centerx
                            self.paddle.width = int(Paddle.WIDTH * factor)
                            self.paddle.centerx = center
                            self.paddle_power_timer = (
                                PaddleBigPowerup.SIZE_DURATION
                            )
                            self.powerup["collided"].add(ball_id)
                    elif not p_rect.colliderect(rect):
                        self.powerup["collided"].discard(ball_id)

            if rect.top > Screen.HEIGHT:
                self.balls.remove(b)

        if self.powerup:
            self.powerup["timer"] -= dt
            if self.powerup["timer"] <= 0:
                self.powerup = None

        if not self.balls:
            # Always keep at least one ball in play.
            self.balls.append(create_ball())

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, "white", self.paddle)
        for b in self.balls:
            pygame.draw.ellipse(surface, "white", b["rect"])
        if self.powerup:
            colour = POWERUP_COLOURS.get(self.powerup["type"], "yellow")
            pygame.draw.rect(surface, colour, self.powerup["rect"])

    def _predict_intercept(self, ball: dict) -> tuple[float, int]:
        """Return the predicted x-position and frames until impact."""
        rect = ball["rect"].copy()
        vx, vy = ball["vx"], ball["vy"]

        for frame in range(2000):
            rect.x += vx
            rect.y += vy
            vy += Ball.GRAVITY

            if rect.left <= 0 or rect.right >= Screen.WIDTH:
                vx *= -1
            if rect.top <= 0:
                vy *= -1
                speed = math.hypot(vx, vy)
                if speed < Ball.MAX_SPEED:
                    speed = min(speed * Ball.SPEED_INCREMENT, Ball.MAX_SPEED)
                    angle = math.atan2(vy, vx)
                    vx = int(round(math.cos(angle) * speed))
                    vy = int(round(math.sin(angle) * speed))

            if rect.bottom >= self.paddle.top:
                return rect.centerx, frame

        return rect.centerx, 2000
