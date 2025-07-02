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


from enum import Enum


class PowerupType(str, Enum):
    """Identifier strings for power-up behaviours."""

    DUPLICATE = "duplicate"
    PADDLE_BIG = "paddle_big"
    PADDLE_SMALL = "paddle_small"
    SLOW = "slow"


POWERUP_COLOURS = {
    PowerupType.DUPLICATE: "yellow",
    PowerupType.PADDLE_BIG: "blue",
    PowerupType.PADDLE_SMALL: "red",
    PowerupType.SLOW: "blue",
}


class BasePowerup:
    """Base values shared across power-ups."""

    WIDTH = 100
    HEIGHT = 4
    DURATION = 8.0


class DuplicatePowerup(BasePowerup):
    """Ball-duplicating power-up settings."""

    CHANCE = 0.005


class PaddleBigPowerup(BasePowerup):
    """Temporarily enlarge the paddle."""

    CHANCE = 0.005
    SIZE_DURATION = 6.0
    ENLARGE_FACTOR = 1.5


class PaddleSmallPowerup(BasePowerup):
    """Temporarily shrink the paddle."""

    CHANCE = 0.005
    SIZE_DURATION = 6.0
    SHRINK_FACTOR = 0.6


class SlowPowerup:
    """Power-up that temporarily slows all balls."""

    WIDTH = 100
    HEIGHT = 4
    DURATION = 8.0
    CHANCE = 0.003
    EFFECT_TIME = 4.0
    SPEED_FACTOR = 0.5


__all__ = [
    "Screen",
    "Paddle",
    "Ball",
    "PowerupType",
    "POWERUP_COLOURS",
    "BasePowerup",
    "DuplicatePowerup",
    "PaddleBigPowerup",
    "PaddleSmallPowerup",
    "SlowPowerup",
]
