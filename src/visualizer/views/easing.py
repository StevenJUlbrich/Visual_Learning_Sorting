"""Easing functions for sprite interpolation.

Pure math module — no Pygame dependency. All functions take a normalized
progress value t in [0.0, 1.0] and return a mapped output value. Values
outside [0.0, 1.0] are clamped before computation.

See doc 10 §2 (interpolation rules) for usage context.
"""

import math


def ease_in_out_quad(t: float) -> float:
    """Quadratic ease-in-out: slow start, fast middle, slow end."""
    t = max(0.0, min(1.0, t))
    if t < 0.5:
        return 2.0 * t * t
    return 1.0 - (-2.0 * t + 2.0) ** 2 / 2.0


def ease_out_cubic(t: float) -> float:
    """Cubic ease-out: fast start, decelerates to end."""
    t = max(0.0, min(1.0, t))
    return 1.0 - (1.0 - t) ** 3


def sine_arc(t: float) -> float:
    """Sine arc: rises from 0 to peak at t=0.5, falls back to 0.

    Not monotonic — used for vertical lift arcs during sprite swaps.
    """
    t = max(0.0, min(1.0, t))
    return math.sin(math.pi * t)
