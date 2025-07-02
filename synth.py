"""Sound synthesis helpers for generating simple effects."""

import numpy as np
from pygame import mixer
import pygame

SAMPLE_RATE = 44100


def _enveloped_sine(
    freq: float,
    duration: float,
    volume: float,
) -> mixer.Sound:
    """Return a sine wave burst shaped by an exponential envelope.

    Parameters
    ----------
    freq:
        Frequency of the sine wave in Hz.
    duration:
        Length of the sound in seconds.
    volume:
        Peak volume as a multiplier between 0 and 1.
    """
    n_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)
    wave = np.sin(2 * np.pi * freq * t)
    # Simple exponential decay envelope for a percussive effect.
    envelope = np.exp(-6 * t)
    wave = wave * envelope * volume
    audio = (wave * 32767).astype(np.int16)

    init = pygame.mixer.get_init()
    channels = init[2] if init else 1
    if channels > 1 and audio.ndim == 1:
        # Duplicate the mono signal for stereo mixers.
        audio = np.repeat(audio[:, None], channels, axis=1)

    return pygame.sndarray.make_sound(audio)


SOUNDS: dict[str, mixer.Sound] = {}


def init_sounds() -> None:
    """Generate all game sound effects and store them in ``SOUNDS``."""
    SOUNDS["bounce"] = _enveloped_sine(880, 0.12, 0.5)
    SOUNDS["powerup"] = _enveloped_sine(1200, 0.15, 0.6)
    SOUNDS["menu_move"] = _enveloped_sine(660, 0.07, 0.4)
    SOUNDS["menu_select"] = _enveloped_sine(520, 0.15, 0.5)
