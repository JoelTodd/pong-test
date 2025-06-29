"""Collection of gameplay constants split into logical categories."""


class Screen:
    """Window dimensions and framerate."""

    WIDTH = 512
    HEIGHT = 640
    FPS = 60


class Paddle:
    """Paddle dimensions and movement settings."""

    WIDTH = 80
    HEIGHT = 6
    SPEED = 8
    TRANSITION_RATE = 12
    VEL_INFLUENCE = 0.5


class Ball:
    """Ball size and physics related constants."""

    SIZE = 12
    SPEED_X_RANGE = (-4, 4)
    SPEED_Y_RANGE = (4, 6)
    SPEED_INCREMENT = 1.08
    MAX_SPEED = 15
    ANGLE_INFLUENCE = 5
    GRAVITY = 0.01


class Powerup:
    """Power-up behaviour and appearance."""

    WIDTH = 100
    HEIGHT = 4
    DURATION = 8.0
    CHANCE = 0.005


__all__ = ["Screen", "Paddle", "Ball", "Powerup"]
