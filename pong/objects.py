import pygame
import random
from .constants import (
    BALL_SIZE,
    WIDTH,
    HEIGHT,
    POWERUP_WIDTH,
    POWERUP_HEIGHT,
    POWERUP_DURATION,
)
from .utils import random_velocity

next_ball_id = 0


def create_ball(up: bool = False, pos: tuple[int, int] | None = None) -> dict:
    """Create a new ball dictionary with a unique id."""
    global next_ball_id
    rect = pygame.Rect(0, 0, BALL_SIZE, BALL_SIZE)
    if pos is None:
        rect.center = (random.randint(40, WIDTH - 40), HEIGHT // 2)
    else:
        rect.center = pos
    vx, vy = random_velocity(up)
    ball = {"rect": rect, "vx": vx, "vy": vy, "ax": 0.0, "ay": 0.0, "id": next_ball_id}
    next_ball_id += 1
    return ball


def spawn_powerup() -> dict:
    """Return a new powerup dictionary."""
    x = random.randint(20, WIDTH - POWERUP_WIDTH - 20)
    y = random.randint(80, HEIGHT // 2)
    rect = pygame.Rect(x, y, POWERUP_WIDTH, POWERUP_HEIGHT)
    return {"rect": rect, "timer": POWERUP_DURATION, "collided": set()}
