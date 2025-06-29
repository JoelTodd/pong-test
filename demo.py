# Simple autoplay demonstration used for background animations in menus.

import random
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
        self.balls = [create_ball()]  # start with a single ball
        self.powerup = None

    def update(self, dt: float) -> None:
        """Advance the demo simulation by ``dt`` seconds."""
        # Autopilot: move the paddle toward the first ball
        if self.balls:
            target = self.balls[0]["rect"].centerx
            if target < self.paddle.centerx - Paddle.SPEED:
                self.paddle.x -= Paddle.SPEED
            elif target > self.paddle.centerx + Paddle.SPEED:
                self.paddle.x += Paddle.SPEED
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

            # Bounce off the paddle
            if rect.colliderect(self.paddle) and b["vy"] > 0:
                offset = (rect.centerx - self.paddle.centerx) / (Paddle.WIDTH / 2)
                b["vy"] *= -1
                b["vx"] += offset * Ball.ANGLE_INFLUENCE

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

