"""Constants used throughout the game.

The values are organised into small classes to keep related settings
together.  This module contains screen dimensions, paddle movement
parameters, ball physics and power-up configuration.
"""

from enum import Enum


class Screen:
    """Dimensions of the window and desired frame rate."""

    WIDTH = 512
    HEIGHT = 640
    FPS = 60


class Paddle:
    """Paddle size and movement tuning constants."""

    WIDTH = 80
    HEIGHT = 6
    SPEED = 8
    TRANSITION_RATE = 12
    VEL_INFLUENCE = 0.5


class Ball:
    """Physical parameters controlling ball behaviour."""

    SIZE = 10
    SPEED_X_RANGE = (-3, 3)
    SPEED_Y_RANGE = (3, 5)
    SPEED_INCREMENT = 1.05
    MAX_SPEED = 15
    ANGLE_INFLUENCE = 5
    GRAVITY = 0.02


class PowerupType(str, Enum):
    """String values identifying the different power-up effects."""

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
    """Common dimensions and timing shared by power-ups."""

    WIDTH = 100
    HEIGHT = 4
    DURATION = 8.0


class DuplicatePowerup(BasePowerup):
    """Parameters for the ball duplication power-up."""

    CHANCE = 0.005


class PaddleBigPowerup(BasePowerup):
    """Settings for the paddle-enlarging power-up."""

    CHANCE = 0.005
    SIZE_DURATION = 6.0
    ENLARGE_FACTOR = 1.5


class PaddleSmallPowerup(BasePowerup):
    """Settings for the paddle-shrinking power-up."""

    CHANCE = 0.005
    SIZE_DURATION = 6.0
    SHRINK_FACTOR = 0.6


class SlowPowerup:
    """Configuration for the temporary slow-motion power-up."""

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
