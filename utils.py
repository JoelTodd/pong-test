import random
import math
from constants import BALL_SPEED_X_RANGE, BALL_SPEED_Y_RANGE

def cubic_bezier(t, p0, p1, p2, p3):
    """Simple cubic Bézier curve used for easing."""

    return (
        (1 - t) ** 3 * p0
        + 3 * (1 - t) ** 2 * t * p1
        + 3 * (1 - t) * t ** 2 * p2
        + t ** 3 * p3
    )


def snappy_ease(t: float) -> float:
    """Clamp ``t`` into [0, 1] then apply a Bézier easing curve."""

    t = max(0.0, min(1.0, t))
    return cubic_bezier(t, 0.0, 0.1, 0.9, 1.0)


def random_velocity(up: bool = False) -> tuple[int, int]:
    """Return a random starting velocity for a ball."""

    # Choose a horizontal component first. "range" is inclusive/exclusive
    # so we convert it to a list before picking a value.
    vx = random.choice(list(range(*BALL_SPEED_X_RANGE)))

    # Vertical speed is always positive; we flip it if the ball should move up.
    vy = random.choice(range(*BALL_SPEED_Y_RANGE))
    if up:
        vy *= -1
    return vx, vy


def duplicate_velocity(vx_current: int, vy_current: int) -> tuple[int, int]:
    """Same speed, different direction (avoid perfectly horizontal)."""

    speed = math.hypot(vx_current, vy_current)
    while True:
        # Pick a random direction but avoid angles close to 0 or π, which would
        # result in a horizontal trajectory that is less interesting.
        ang = random.uniform(0.1, 3.04)
        vx = speed * math.cos(ang)

        # If we accidentally picked an almost horizontal angle, try again.
        if abs(vx) < 1e-3:
            continue

        vy = speed * math.sin(ang)
        if vy_current < 0:
            vy *= -1
        return int(round(vx)), int(round(vy))
