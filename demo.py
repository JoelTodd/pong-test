# Simple autoplay demonstration used for background animations in menus.

import random
import math
import pygame

from constants import Screen, Paddle, Ball, Powerup
from entities import create_ball, spawn_powerup
from utils import duplicate_velocity


class DemoGame:
    """Lightweight, non-interactive gameplay used on menu screens."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.paddle = pygame.Rect(
            Screen.WIDTH // 2 - Paddle.WIDTH // 2,
            Screen.HEIGHT - 20 - Paddle.HEIGHT,
            Paddle.WIDTH,
            Paddle.HEIGHT,
        )
        self._paddle_center = float(self.paddle.centerx)
        self.paddle_vx = 0
        self.balls = [create_ball()]  # start with a single ball
        self.powerup = None

    def update(self, dt: float) -> None:
        """Advance the demo simulation by one frame."""

        # Autopilot: track whichever ball will hit the paddle next. A small
        # random offset keeps the motion from looking too mechanical.
        if self.balls:
            target_x = None
            frames_left = None
            for ball in self.balls:
                tx, fl = self._predict_intercept(ball)
                if frames_left is None or fl < frames_left:
                    target_x, frames_left = tx, fl
            # Add a tiny offset each frame to avoid perfectly straight movement
            target_x += random.uniform(-2, 2)

            # Determine when we need to start moving so we reach the target
            dist = abs(target_x - self._paddle_center)
            move_frames = math.ceil(dist / Paddle.SPEED)
            # Aim to arrive a handful of frames before impact
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
            self.paddle.clamp_ip(pygame.Rect(0, 0, Screen.WIDTH, Screen.HEIGHT))

        # Occasionally spawn a powerup
        if self.powerup is None and random.random() < Powerup.CHANCE:
            self.powerup = spawn_powerup()

        for b in self.balls[:]:
            rect = b["rect"]

            b["vy"] += Ball.GRAVITY
            rect.x += b["vx"]
            rect.y += b["vy"]

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

            # Bounce off the paddle
            if rect.colliderect(self.paddle) and b["vy"] > 0:
                offset = (rect.centerx - self.paddle.centerx) / (Paddle.WIDTH / 2)
                b["vy"] *= -1
                b["vx"] += offset * Ball.ANGLE_INFLUENCE + self.paddle_vx * Paddle.VEL_INFLUENCE
                b["vx"] = max(min(b["vx"] * Ball.SPEED_INCREMENT, Ball.MAX_SPEED), -Ball.MAX_SPEED)
                b["vy"] = max(min(b["vy"] * Ball.SPEED_INCREMENT, Ball.MAX_SPEED), -Ball.MAX_SPEED)

            # Handle powerup
            if self.powerup:
                p_rect = self.powerup["rect"]
                ball_id = b["id"]
                if p_rect.colliderect(rect) and ball_id not in self.powerup["collided"]:
                    vx_new, vy_new = duplicate_velocity(b["vx"], b["vy"])
                    nb = create_ball(up=b["vy"] < 0, pos=rect.center)
                    nb["vx"], nb["vy"] = vx_new, vy_new
                    self.powerup["collided"].update({ball_id, nb["id"]})
                    self.balls.append(nb)
                elif not p_rect.colliderect(rect):
                    self.powerup["collided"].discard(ball_id)

            if rect.top > Screen.HEIGHT:
                self.balls.remove(b)

        if self.powerup:
            self.powerup["timer"] -= dt
            if self.powerup["timer"] <= 0:
                self.powerup = None

        if not self.balls:
            self.balls.append(create_ball())

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, "white", self.paddle)
        for b in self.balls:
            pygame.draw.ellipse(surface, "white", b["rect"])
        if self.powerup:
            pygame.draw.rect(surface, "yellow", self.powerup["rect"])

    def _predict_intercept(self, ball: dict) -> tuple[float, int]:
        """Return where and in how many frames ``ball`` will hit the paddle."""
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

