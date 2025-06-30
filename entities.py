import random
import pygame
from constants import Screen, Ball, Powerup, SlowPowerup
from utils import random_velocity

# Internal counter used to assign a unique ID to each ball we create.
_next_ball_id = 0


def create_ball(up: bool = False, pos: tuple[int, int] | None = None) -> dict:
    """Return a new ball dictionary.

    ``up`` flips the initial vertical direction so the ball moves upward
    instead of downward. ``pos`` allows explicitly setting the starting
    position; otherwise a random location is chosen.
    """
    global _next_ball_id

    # Create the rectangular hitbox for the ball
    rect = pygame.Rect(0, 0, Ball.SIZE, Ball.SIZE)
    rect.center = pos or (
        random.randint(40, Screen.WIDTH - 40),
        Screen.HEIGHT // 2,
    )

    # Pick a starting velocity for the ball
    vx, vy = random_velocity(up)

    # Store additional fields used for debugging/physics
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
    """Create either a duplicate or slow-down powerup."""

    kind = random.choice(["duplicate", "slow"])
    if kind == "duplicate":
        width, height, duration = (
            Powerup.WIDTH,
            Powerup.HEIGHT,
            Powerup.DURATION,
        )
    else:
        width, height, duration = (
            SlowPowerup.WIDTH,
            SlowPowerup.HEIGHT,
            SlowPowerup.DURATION,
        )

    # Position the powerup somewhere near the top half of the screen
    x = random.randint(20, Screen.WIDTH - width - 20)
    y = random.randint(80, Screen.HEIGHT // 2)
    rect = pygame.Rect(x, y, width, height)

    return {"rect": rect, "timer": duration, "collided": set(), "type": kind}
