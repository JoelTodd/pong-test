"""Utility functions for easing curves and velocity helpers."""

import random
import math
from constants import Ball


def cubic_bezier(t, p0, p1, p2, p3):
    """Evaluate a cubic Bézier curve."""

    return (
        (1 - t) ** 3 * p0
        + 3 * (1 - t) ** 2 * t * p1
        + 3 * (1 - t) * t ** 2 * p2
        + t ** 3 * p3
    )


def snappy_ease(t: float) -> float:
    """Clamp ``t`` to ``[0, 1]`` and apply a snappy Bézier easing."""

    t = max(0.0, min(1.0, t))
    return cubic_bezier(t, 0.0, 0.1, 0.9, 1.0)


def random_velocity(up: bool = False) -> tuple[float, float]:
    """Return a random starting velocity for a ball.

    Parameters
    ----------
    up:
        When ``True`` the vertical component is negated so the ball travels
        upward.
    """

    # Choose a horizontal component first. The ``range`` is inclusive/exclusive
    # so we convert it to a list before picking a value.
    vx = float(random.choice(list(range(*Ball.SPEED_X_RANGE))))

    # Vertical speed is always positive; flip it if the ball should move up.
    vy = float(random.choice(range(*Ball.SPEED_Y_RANGE)))
    if up:
        vy *= -1
    return vx, vy


def duplicate_velocity(
    vx_current: float, vy_current: float
) -> tuple[float, float]:
    """Generate a velocity of equal speed in a new random direction.

    Parameters
    ----------
    vx_current:
        Current horizontal velocity of the ball.
    vy_current:
        Current vertical velocity of the ball; its sign is preserved.
    """

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
        return vx, vy
