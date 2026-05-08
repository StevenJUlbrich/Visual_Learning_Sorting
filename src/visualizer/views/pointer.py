"""Selection Sort pointer arrow geometry and rendering.

Three labeled pointer arrows for Selection Sort:
  i   — downward triangle ABOVE baseline, marks sorted boundary
  j   — upward triangle BELOW baseline, marks scan cursor
  min — upward triangle BELOW baseline, marks minimum tracker

Coalescing (D-068): when j and min occupy the same slot, only min is shown.

See doc 05 §4.2, D-068.
"""

from __future__ import annotations

import pygame

from visualizer.views.panel import PRIMARY_TEXT
from visualizer.views.sprite import COLOR_MAP, ColorState

# ---------------------------------------------------------------------------
# Arrow geometry constants
# ---------------------------------------------------------------------------

ARROW_HEIGHT: int = 12
ARROW_HALF_WIDTH: int = 5
ARROW_GAP: int = 5  # clearance between ring edge and arrow tip
LABEL_GAP: int = 2  # gap between arrow base and label text

# ---------------------------------------------------------------------------
# Pointer colors
# ---------------------------------------------------------------------------

POINTER_I_COLOR: tuple[int, int, int] = PRIMARY_TEXT  # (240, 240, 245)
POINTER_J_COLOR: tuple[int, int, int] = COLOR_MAP[ColorState.ACTIVE]  # (255, 140, 0)
POINTER_MIN_COLOR: tuple[int, int, int] = COLOR_MAP[ColorState.ACTIVE]  # (255, 140, 0)


class PointerSet:
    """Manages the three Selection Sort pointer arrows (i, j, min).

    Arrow rendering:
    - i: downward triangle ABOVE baseline; label above arrow
    - j, min: upward triangles BELOW baseline; labels below arrows

    Coalescing (D-068): j is hidden when j_index == min_index.
    """

    def __init__(
        self,
        panel_rect: pygame.Rect,
        array_x_padding: int,
        slot_width: float,
        ring_radius: int,
        body_font: pygame.font.Font,
    ) -> None:
        self._panel_rect = panel_rect
        self._array_x_padding = array_x_padding
        self._slot_width = slot_width
        self._ring_radius = ring_radius
        self._body_font = body_font
        self._home_y: float = panel_rect.y + panel_rect.height // 2

    def slot_center_x(self, slot_index: int) -> float:
        """Horizontal center for a given slot (same formula as sprite home_x)."""
        return (
            self._panel_rect.x
            + self._array_x_padding
            + slot_index * self._slot_width
            + self._slot_width / 2
        )

    def i_arrow_y(self) -> float:
        """Tip y for the i pointer arrow (above baseline, tip points toward ring)."""
        return self._home_y - self._ring_radius - ARROW_GAP

    def jmin_arrow_y(self) -> float:
        """Tip y for j and min pointer arrows (below baseline, tip points toward ring)."""
        return self._home_y + self._ring_radius + ARROW_GAP

    def coalesced_pointers(
        self,
        i_index: int | None,
        j_index: int | None,
        min_index: int | None,
    ) -> tuple[int | None, int | None, int | None]:
        """Apply D-068 coalescing: return (eff_i, eff_j, eff_min).

        When j == min (both not None), j is hidden so only min is shown.
        """
        eff_j = None if (j_index is not None and j_index == min_index) else j_index
        return i_index, eff_j, min_index

    def draw(
        self,
        surface: pygame.Surface,
        i_index: int | None,
        j_index: int | None,
        min_index: int | None,
    ) -> None:
        """Draw visible pointer arrows; coalescing applied automatically."""
        eff_i, eff_j, eff_min = self.coalesced_pointers(i_index, j_index, min_index)
        if eff_i is not None:
            self._draw_i_pointer(surface, eff_i)
        if eff_j is not None:
            self._draw_jmin_pointer(surface, eff_j, "j", POINTER_J_COLOR)
        if eff_min is not None:
            self._draw_jmin_pointer(surface, eff_min, "min", POINTER_MIN_COLOR)

    def _draw_i_pointer(self, surface: pygame.Surface, slot_index: int) -> None:
        cx = self.slot_center_x(slot_index)
        tip_y = self.i_arrow_y()
        base_y = tip_y - ARROW_HEIGHT
        points: list[tuple[int, int]] = [
            (round(cx), round(tip_y)),
            (round(cx - ARROW_HALF_WIDTH), round(base_y)),
            (round(cx + ARROW_HALF_WIDTH), round(base_y)),
        ]
        pygame.draw.polygon(surface, POINTER_I_COLOR, points)
        label_surf = self._body_font.render("i", True, POINTER_I_COLOR)
        label_rect = label_surf.get_rect()
        label_rect.centerx = round(cx)
        label_rect.bottom = round(base_y) - LABEL_GAP
        surface.blit(label_surf, label_rect)

    def _draw_jmin_pointer(
        self,
        surface: pygame.Surface,
        slot_index: int,
        label: str,
        color: tuple[int, int, int],
    ) -> None:
        cx = self.slot_center_x(slot_index)
        tip_y = self.jmin_arrow_y()
        base_y = tip_y + ARROW_HEIGHT
        points: list[tuple[int, int]] = [
            (round(cx), round(tip_y)),
            (round(cx - ARROW_HALF_WIDTH), round(base_y)),
            (round(cx + ARROW_HALF_WIDTH), round(base_y)),
        ]
        pygame.draw.polygon(surface, color, points)
        label_surf = self._body_font.render(label, True, color)
        label_rect = label_surf.get_rect()
        label_rect.centerx = round(cx)
        label_rect.top = round(base_y) + LABEL_GAP
        surface.blit(label_surf, label_rect)