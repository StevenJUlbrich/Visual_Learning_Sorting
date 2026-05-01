"""HUD overlay text elements drawn on top of panel content.

Three independent components:
- BubbleHUD: comparison/exchange counters at panel bottom-left (doc 04 §4.6.1)
- HeapPhaseLabel: "BUILD MAX-HEAP" / "EXTRACTION" centered in panel (D-075, doc 04 §4.3.2)
- HeapBoundaryLabel: "heap boundary" marker below sorted row (D-076, doc 04 §4.3.2)

Each class is usable standalone; none imports the others.
"""

from __future__ import annotations

import pygame

from visualizer.views.limitline import LINE_COLOR
from visualizer.views.sprite import COLOR_MAP, ColorState

# ---------------------------------------------------------------------------
# Color constants
# ---------------------------------------------------------------------------

HUD_TEXT_COLOR: tuple[int, int, int] = (190, 190, 200)  # secondary text, doc 04 §5.1
PHASE_LABEL_COLOR: tuple[int, int, int] = COLOR_MAP[ColorState.ACTIVE]  # (255, 140, 0)
BOUNDARY_LABEL_COLOR: tuple[int, int, int] = LINE_COLOR  # (150, 150, 160)

# ---------------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------------

BOTTOM_MARGIN: int = 22  # px above panel bottom edge
LINE_SPACING: int = 4  # px between the two counter lines


class BubbleHUD:
    """Bubble Sort comparison/exchange counter overlay at panel bottom-left.

    Visible in all panel states; values freeze at final counts on completion.
    """

    def __init__(
        self,
        panel_rect: pygame.Rect,
        body_font: pygame.font.Font,
        inset_x: int,
    ) -> None:
        self._font = body_font
        line_h = body_font.get_height()
        self._counter_x: int = panel_rect.x + inset_x
        self._exchanges_y: int = panel_rect.bottom - BOTTOM_MARGIN
        self._comparisons_y: int = self._exchanges_y - line_h - LINE_SPACING

    @property
    def counter_x(self) -> int:
        """Left edge of counter text (panel.x + inset_x)."""
        return self._counter_x

    @property
    def comparisons_y(self) -> int:
        """Top y of the Comparisons line."""
        return self._comparisons_y

    @property
    def exchanges_y(self) -> int:
        """Top y of the Exchanges line (bottom line)."""
        return self._exchanges_y

    def draw(
        self,
        surface: pygame.Surface,
        comparisons: int,
        exchanges: int,
    ) -> None:
        """Draw counter text at bottom-left of panel."""
        comp_surf = self._font.render(f"Comparisons: {comparisons}", True, HUD_TEXT_COLOR)
        exch_surf = self._font.render(f"Exchanges: {exchanges}", True, HUD_TEXT_COLOR)
        surface.blit(comp_surf, (self._counter_x, self._comparisons_y))
        surface.blit(exch_surf, (self._counter_x, self._exchanges_y))


class HeapPhaseLabel:
    """Heap Sort phase label (BUILD MAX-HEAP / EXTRACTION) centered horizontally.

    The caller passes label_y so the Controller can position it relative to
    the tree root node (doc 04 §4.3.2, D-075).
    """

    def __init__(
        self,
        panel_rect: pygame.Rect,
        body_font: pygame.font.Font,
    ) -> None:
        self._font = body_font
        self._center_x: int = panel_rect.centerx

    @property
    def center_x(self) -> int:
        """Horizontal center used for text centering (panel.centerx)."""
        return self._center_x

    def draw(
        self,
        surface: pygame.Surface,
        phase: str,
        label_y: float,
    ) -> None:
        """Draw phase label centered horizontally in panel at label_y."""
        text_surf = self._font.render(phase, True, PHASE_LABEL_COLOR)
        x = self._center_x - text_surf.get_width() // 2
        surface.blit(text_surf, (x, round(label_y)))


class HeapBoundaryLabel:
    """Heap Sort boundary marker label below the sorted row.

    Only drawn when heap_size < array_size (caller is responsible for the guard).
    Text is centered on boundary_x (D-076).
    """

    LABEL_TEXT: str = "heap boundary"

    def __init__(self, body_font: pygame.font.Font) -> None:
        self._font = body_font

    def draw(
        self,
        surface: pygame.Surface,
        boundary_x: float,
        label_y: float,
    ) -> None:
        """Draw 'heap boundary' text centered on boundary_x at label_y."""
        text_surf = self._font.render(self.LABEL_TEXT, True, BOUNDARY_LABEL_COLOR)
        x = round(boundary_x) - text_surf.get_width() // 2
        surface.blit(text_surf, (x, round(label_y)))
