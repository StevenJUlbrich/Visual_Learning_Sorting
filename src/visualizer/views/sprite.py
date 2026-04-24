"""NumberSprite — circular ring sprite representing one array value.

See doc 04 §4.3 (ring shape), doc 04 §3.5 (font caching), doc 12 §1 (identity),
D-069 (ring shape, 3px stroke), D-034 (float coordinates).
"""

from __future__ import annotations

from enum import Enum

import pygame


class ColorState(Enum):
    DEFAULT = "default"
    ACTIVE = "active"
    SETTLED = "settled"
    COMPLETE = "complete"
    ERROR = "error"


COLOR_MAP: dict[ColorState, tuple[int, int, int]] = {
    ColorState.DEFAULT: (100, 150, 255),  # doc 04 §5.1 — default array value blue
    ColorState.ACTIVE: (255, 140, 0),  # doc 04 §5.2 — universal active highlight (D-067)
    ColorState.SETTLED: (130, 150, 190),  # doc 04 §5.3 — settled/extracted steel-blue
    ColorState.COMPLETE: (80, 220, 120),  # doc 04 §5.1 — completion green
    ColorState.ERROR: (255, 120, 120),  # doc 04 §5.1 — error text
}

PANEL_BG_COLOR: tuple[int, int, int] = (45, 45, 53)
RING_STROKE_WIDTH: int = 3
RING_DIAMETER_RATIO: float = 0.65


class NumberSprite:
    """Circular ring sprite for one value in the sort array.

    sprite_id is permanent and never changes — identity is by ID, never by value
    (doc 12 §1.1). Color-state decisions and animation are Controller responsibilities.
    """

    def __init__(
        self,
        sprite_id: int,
        value: int,
        slot_index: int,
        panel_rect: pygame.Rect,
        array_x_padding: int,
        slot_width: float,
        font: pygame.font.Font,
    ) -> None:
        self.sprite_id = sprite_id
        self.value = value
        self.panel_rect = panel_rect
        self.array_x_padding = array_x_padding
        self.slot_width = slot_width
        self.font = font

        self.ring_radius: int = int(slot_width * RING_DIAMETER_RATIO) // 2

        self.home_x: float = (
            panel_rect.x + array_x_padding + (slot_index * slot_width) + (slot_width / 2)
        )
        self.home_y: float = panel_rect.y + panel_rect.height // 2

        self.exact_x: float = self.home_x
        self.exact_y: float = self.home_y

        self.color_state: ColorState = ColorState.DEFAULT
        self.surface_cache: dict[ColorState, pygame.Surface] = {}
        self._build_surface_cache()

    def _build_surface_cache(self) -> None:
        for state in ColorState:
            self.surface_cache[state] = self.font.render(str(self.value), True, COLOR_MAP[state])

    @property
    def is_lifted(self) -> bool:
        return self.exact_y < self.home_y

    def update_home(self, new_slot_index: int) -> None:
        self.home_x = (
            self.panel_rect.x
            + self.array_x_padding
            + (new_slot_index * self.slot_width)
            + (self.slot_width / 2)
        )

    def set_color_state(self, state: ColorState) -> None:
        self.color_state = state

    def draw(self, surface: pygame.Surface) -> None:
        cx = round(self.exact_x)
        cy = round(self.exact_y)
        color = COLOR_MAP[self.color_state]
        pygame.draw.circle(surface, PANEL_BG_COLOR, (cx, cy), self.ring_radius)
        pygame.draw.circle(surface, color, (cx, cy), self.ring_radius, RING_STROKE_WIDTH)
        text_surf = self.surface_cache[self.color_state]
        surface.blit(text_surf, text_surf.get_rect(center=(cx, cy)))
