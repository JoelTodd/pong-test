"""Helpers for creating balls and power-up rectangles."""

import random
import pygame
from constants import (
    Screen,
    Ball,
    DuplicatePowerup,
    PaddleBigPowerup,
    PaddleSmallPowerup,
    SlowPowerup,
    PowerupType,
)
from utils import random_velocity

# Internal counter used to assign a unique ID to each ball we create.
_next_ball_id = 0


def create_ball(up: bool = False, pos: tuple[int, int] | None = None) -> dict:
    """Return a new ball dictionary.

    Parameters
    ----------
    up:
        If ``True`` the ball initially travels upward instead of downward.
    pos:
        Optional starting position for the ball's centre.  When omitted a
        random location is chosen.
    """
    global _next_ball_id

    # Create the rectangular hitbox for the ball.
    rect = pygame.Rect(0, 0, Ball.SIZE, Ball.SIZE)
    rect.center = pos or (
        random.randint(40, Screen.WIDTH - 40),
        Screen.HEIGHT // 2,
    )

    # Pick a starting velocity for the ball.
    vx, vy = random_velocity(up)

    # Store additional fields used for debugging and physics.
    ball = {
        "rect": rect,
        "x": float(rect.x),
        "y": float(rect.y),
        "vx": vx,
        "vy": vy,
        "ax": 0.0,
        "ay": 0.0,
        "id": _next_ball_id,
    }
    _next_ball_id += 1
    return ball


def spawn_powerup() -> dict:
    """Return a randomly positioned power-up dictionary.

    A random type is chosen between ball duplication, paddle resizing and
    slow motion.  The returned dictionary includes a ``rect`` for collision,
    a countdown ``timer`` and a ``type`` key describing the effect.
    """

    p_type = random.choice(
        [
            PowerupType.DUPLICATE,
            PowerupType.PADDLE_BIG,
            PowerupType.PADDLE_SMALL,
            PowerupType.SLOW,
        ]
    )

    if p_type is PowerupType.SLOW:
        width, height, duration = (
            SlowPowerup.WIDTH,
            SlowPowerup.HEIGHT,
            SlowPowerup.DURATION,
        )
    elif p_type is PowerupType.DUPLICATE:
        width, height, duration = (
            DuplicatePowerup.WIDTH,
            DuplicatePowerup.HEIGHT,
            DuplicatePowerup.DURATION,
        )
    elif p_type is PowerupType.PADDLE_BIG:
        width, height, duration = (
            PaddleBigPowerup.WIDTH,
            PaddleBigPowerup.HEIGHT,
            PaddleBigPowerup.DURATION,
        )
    else:
        width, height, duration = (
            PaddleSmallPowerup.WIDTH,
            PaddleSmallPowerup.HEIGHT,
            PaddleSmallPowerup.DURATION,
        )

    # Position the powerup somewhere near the top half of the screen.
    x = random.randint(20, Screen.WIDTH - width - 20)
    y = random.randint(80, Screen.HEIGHT // 2)
    rect = pygame.Rect(x, y, width, height)

    return {"rect": rect, "timer": duration, "collided": set(), "type": p_type}
