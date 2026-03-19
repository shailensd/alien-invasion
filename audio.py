import math
from array import array
from dataclasses import dataclass
from typing import Optional

import pygame


@dataclass(frozen=True)
class SoundSpec:
    freq_hz: float
    duration_ms: int
    volume: float = 0.35


def _make_tone(spec: SoundSpec, sample_rate: int = 44100) -> pygame.mixer.Sound:
    """Generate a simple sine-wave tone as a pygame Sound.

    Keeps the project asset-free (no wav/mp3 files required).
    """
    n_samples = max(1, int(sample_rate * (spec.duration_ms / 1000.0)))
    amplitude = int(32767 * max(0.0, min(1.0, spec.volume)))

    buf = array("h")
    two_pi_f = 2.0 * math.pi * float(spec.freq_hz)
    for i in range(n_samples):
        t = i / sample_rate
        buf.append(int(amplitude * math.sin(two_pi_f * t)))

    return pygame.mixer.Sound(buffer=buf.tobytes())


class SFX:
    """Small sound-effects manager with graceful fallback."""

    def __init__(self, enabled: bool = True, volume: float = 0.35):
        self.enabled = enabled
        self.volume = max(0.0, min(1.0, volume))

        self._ok = False
        self.shoot: Optional[pygame.mixer.Sound] = None
        self.hit: Optional[pygame.mixer.Sound] = None
        self.ship_hit: Optional[pygame.mixer.Sound] = None
        self.level_up: Optional[pygame.mixer.Sound] = None
        self.game_over: Optional[pygame.mixer.Sound] = None
        self.start: Optional[pygame.mixer.Sound] = None

    def init(self) -> None:
        if not self.enabled:
            return

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            # Distinct "arcade" tones
            self.shoot = _make_tone(SoundSpec(880, 60, self.volume))
            self.hit = _make_tone(SoundSpec(220, 90, self.volume))
            self.ship_hit = _make_tone(SoundSpec(140, 160, self.volume))
            self.level_up = _make_tone(SoundSpec(660, 140, self.volume))
            self.game_over = _make_tone(SoundSpec(110, 350, self.volume))
            self.start = _make_tone(SoundSpec(520, 120, self.volume))

            self._ok = True
        except Exception:
            # Web/audio environments can fail to init mixer; game should still run.
            self._ok = False

    def toggle(self) -> None:
        self.enabled = not self.enabled

    def play(self, sound: Optional[pygame.mixer.Sound]) -> None:
        if not self.enabled or not self._ok or sound is None:
            return
        try:
            sound.play()
        except Exception:
            pass
