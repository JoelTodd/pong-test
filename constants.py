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

    SIZE = 10
    SPEED_X_RANGE = (-3, 3)
    SPEED_Y_RANGE = (3, 5)
    SPEED_INCREMENT = 1.05
    MAX_SPEED = 15
    ANGLE_INFLUENCE = 5
    GRAVITY = 0.02


class Powerup:
    """Power-up behaviour and appearance."""

    WIDTH = 100
    HEIGHT = 4
    DURATION = 8.0
    CHANCE = 0.005


class SlowPowerup:
    """Power-up that temporarily slows all balls."""

    WIDTH = 100
    HEIGHT = 4
    DURATION = 8.0
    CHANCE = 0.003
    EFFECT_TIME = 4.0
    SPEED_FACTOR = 0.5


__all__ = ["Screen", "Paddle", "Ball", "Powerup", "SlowPowerup"]
