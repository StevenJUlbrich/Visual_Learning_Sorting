"""Window display initialization and 2x2 grid layout math.

See doc 04 §2 (grid layout), D-077 (no RESIZABLE flag), D-079 (no portrait).
"""

from __future__ import annotations

import tomllib
from pathlib import Path

import pygame

_PRESET_DIMS: dict[str, tuple[int, int]] = {
    "desktop": (1280, 720),
    "tablet": (1024, 768),
}


def load_preset(config_path: Path) -> tuple[int, int]:
    """Read config.toml and return (width, height) for the configured preset."""
    with config_path.open("rb") as f:
        cfg = tomllib.load(f)
    preset: str = cfg["window"]["preset"]
    if preset not in _PRESET_DIMS:
        raise ValueError(f"Unknown window preset: {preset!r}")
    return _PRESET_DIMS[preset]


class GridLayout:
    """Proportional spacing tokens computed from window dimensions.

    Constructable from (window_width, window_height) alone — no display
    required — so tests can verify grid math without calling init_display.
    """

    def __init__(self, window_width: int, window_height: int) -> None:
        self.window_width = window_width
        self.window_height = window_height
        self.PADDING = int(window_width * 0.015)
        self.CONTROL_BAR_HEIGHT = int(window_height * 0.07)
        self.grid_height = window_height - self.CONTROL_BAR_HEIGHT - self.PADDING
        self.panel_width = (window_width - self.PADDING * 3) // 2
        self.panel_height = (self.grid_height - self.PADDING * 3) // 2
        self.PANEL_RADIUS = 12
        self.ARRAY_X_PADDING = int(self.panel_width * 0.05)
        self.slot_width = (self.panel_width - self.ARRAY_X_PADDING * 2) / 7
        p = self.PADDING
        pw = self.panel_width
        ph = self.panel_height
        self.panel_rects: tuple[pygame.Rect, ...] = (
            pygame.Rect(p, p, pw, ph),
            pygame.Rect(p * 2 + pw, p, pw, ph),
            pygame.Rect(p, p * 2 + ph, pw, ph),
            pygame.Rect(p * 2 + pw, p * 2 + ph, pw, ph),
        )


def init_display(width: int, height: int) -> tuple[pygame.Surface, GridLayout]:
    """Initialize pygame display and return (surface, layout).

    No RESIZABLE flag per D-077.
    """
    surface = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Learn Visual - Expand Knowledge")
    return surface, GridLayout(width, height)
