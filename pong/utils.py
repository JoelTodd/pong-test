import math
import random
from .constants import (
    BALL_SPEED_X_RANGE,
    BALL_SPEED_Y_RANGE,
)


def cubic_bezier(t: float, p0: float, p1: float, p2: float, p3: float) -> float:
    """Evaluate a cubic Bézier curve."""
    return (
        (1 - t) ** 3 * p0
        + 3 * (1 - t) ** 2 * t * p1
        + 3 * (1 - t) * t ** 2 * p2
        + t ** 3 * p3
    )


def snappy_ease(t: float) -> float:
    """Return a smooth yet quick easing value for 0<=t<=1."""
    t = max(0.0, min(1.0, t))
    return cubic_bezier(t, 0.0, 0.1, 0.9, 1.0)


def random_velocity(up: bool = False) -> tuple[int, int]:
    """Return a random ball velocity."""
    vx = random.choice(list(range(*BALL_SPEED_X_RANGE)))
    vy = random.choice(range(*BALL_SPEED_Y_RANGE))
    if up:
        vy *= -1
    return vx, vy


def duplicate_velocity(vx_current: int, vy_current: int) -> tuple[int, int]:
    """Create a new velocity with the same speed but random direction."""
    speed = math.hypot(vx_current, vy_current)
    while True:
        angle = random.uniform(0.1, 3.04)
        vx = speed * math.cos(angle)
        if abs(vx) < 1e-3:
            continue
        vy = speed * math.sin(angle)
        if vy_current < 0:
            vy *= -1
        return int(round(vx)), int(round(vy))
