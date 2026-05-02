"""Bubble Sort LimitLine — vertical dashed boundary between unsorted and sorted regions.

The line sits between two adjacent slots, marking the right-side boundary of the
unsorted region. After each Bubble Sort pass it advances (moves one slot left).

LINE_COLOR is shared with the Heap Sort boundary marker (doc 04 §4.3.2) — import
it from here rather than redefining it in hud.py.

See doc 04 §4.3.1, doc 05 §4.1.
"""

from __future__ import annotations

import pygame

# ---------------------------------------------------------------------------
# Visual constants
# ---------------------------------------------------------------------------

LINE_COLOR: tuple[int, int, int] = (150, 150, 160)
LINE_WIDTH: int = 2
LINE_DASH_LEN: int = 6
LINE_GAP_LEN: int = 4
LINE_MARGIN: int = 12  # px above/below ring edges — keeps line inside array region


class LimitLine:
    """Vertical dashed boundary line for Bubble Sort.

    boundary_index tracks the next slot to be filled by a settled element.
    The line's x coordinate is the left edge of that slot — i.e. the gap
    between slot [boundary_index-1] and slot [boundary_index].

    Lifecycle:
      initial  → boundary_index = array_size  (line off right edge, not visible)
      advance  → boundary_index decrements by 1 each pass
      visible  → 0 < boundary_index < array_size
    """

    def __init__(
        self,
        panel_rect: pygame.Rect,
        array_x_padding: int,
        slot_width: float,
        home_y: float,
        ring_radius: int,
        array_size: int = 7,
    ) -> None:
        self._panel_rect = panel_rect
        self._array_x_padding = array_x_padding
        self._slot_width = slot_width
        self._home_y = home_y
        self._ring_radius = ring_radius
        self._array_size = array_size
        self._boundary_index: int = array_size

    @property
    def boundary_index(self) -> int:
        """Current boundary slot index."""
        return self._boundary_index

    @property
    def x_position(self) -> float:
        """Horizontal position of the dashed line (left edge of boundary slot)."""
        return self._panel_rect.x + self._array_x_padding + self._boundary_index * self._slot_width

    @property
    def is_visible(self) -> bool:
        """True when the line marks a meaningful boundary within the array."""
        return 0 < self._boundary_index < self._array_size

    def advance(self) -> None:
        """Move boundary one slot left (call after each completed pass)."""
        if self._boundary_index > 0:
            self._boundary_index -= 1

    def reset(self) -> None:
        """Restore initial state (call on restart)."""
        self._boundary_index = self._array_size

    def draw(self, surface: pygame.Surface) -> None:
        """Draw vertical dashed line at current position if visible."""
        if not self.is_visible:
            return
        x = round(self.x_position)
        top_y = round(self._home_y) - self._ring_radius - LINE_MARGIN
        bottom_y = round(self._home_y) + self._ring_radius + LINE_MARGIN
        y = top_y
        drawing = True
        while y < bottom_y:
            segment_len = LINE_DASH_LEN if drawing else LINE_GAP_LEN
            end_y = min(y + segment_len, bottom_y)
            if drawing:
                pygame.draw.line(surface, LINE_COLOR, (x, y), (x, end_y), LINE_WIDTH)
            y += segment_len
            drawing = not drawing
