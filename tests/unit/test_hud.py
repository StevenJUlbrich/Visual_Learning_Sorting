"""Phase 5g: HUD overlay text element tests.

Tests verify position formulas, color constants, and draw no-crash for all three
HUD classes. Uses Desktop preset panel_rect = pygame.Rect(19, 19, 611, 297).

TC against doc 04 §4.6.1 (BubbleHUD), doc 04 §4.3.2 / D-075 / D-076 (Heap labels).
"""

from __future__ import annotations

import pygame
import pytest

from visualizer.views.hud import (
    BOTTOM_MARGIN,
    BOUNDARY_LABEL_COLOR,
    HUD_TEXT_COLOR,
    LINE_SPACING,
    PHASE_LABEL_COLOR,
    BubbleHUD,
    HeapBoundaryLabel,
    HeapPhaseLabel,
)
from visualizer.views.limitline import LINE_COLOR
from visualizer.views.sprite import COLOR_MAP, ColorState

# ---------------------------------------------------------------------------
# Desktop preset constants
# ---------------------------------------------------------------------------

DESKTOP_RECT = pygame.Rect(19, 19, 611, 297)
INSET_X = max(int(611 * 0.03), 12)  # 18


@pytest.fixture
def body_font() -> pygame.font.Font:
    return pygame.font.SysFont("segoeui,arial", 16)


@pytest.fixture
def surface() -> pygame.Surface:
    return pygame.Surface((640, 480))


@pytest.fixture
def bubble_hud(body_font: pygame.font.Font) -> BubbleHUD:
    return BubbleHUD(DESKTOP_RECT, body_font, INSET_X)


@pytest.fixture
def heap_phase_label(body_font: pygame.font.Font) -> HeapPhaseLabel:
    return HeapPhaseLabel(DESKTOP_RECT, body_font)


@pytest.fixture
def heap_boundary_label(body_font: pygame.font.Font) -> HeapBoundaryLabel:
    return HeapBoundaryLabel(body_font)


# ---------------------------------------------------------------------------
# Color constants
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_hud_text_color_value() -> None:
    assert HUD_TEXT_COLOR == (190, 190, 200)


@pytest.mark.unit
def test_phase_label_color_value() -> None:
    assert PHASE_LABEL_COLOR == (255, 140, 0)


@pytest.mark.unit
def test_boundary_label_color_value() -> None:
    assert BOUNDARY_LABEL_COLOR == (150, 150, 160)


@pytest.mark.unit
def test_phase_label_color_matches_color_map() -> None:
    assert PHASE_LABEL_COLOR == COLOR_MAP[ColorState.ACTIVE]


@pytest.mark.unit
def test_boundary_label_color_matches_line_color() -> None:
    assert BOUNDARY_LABEL_COLOR == LINE_COLOR


# ---------------------------------------------------------------------------
# BubbleHUD — construction
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_bubble_hud_constructs(body_font: pygame.font.Font) -> None:
    hud = BubbleHUD(DESKTOP_RECT, body_font, INSET_X)
    assert hud is not None


@pytest.mark.unit
def test_bubble_hud_counter_x_uses_inset(bubble_hud: BubbleHUD) -> None:
    assert bubble_hud.counter_x == DESKTOP_RECT.x + INSET_X


@pytest.mark.unit
def test_bubble_hud_exchanges_y_uses_bottom_margin(bubble_hud: BubbleHUD) -> None:
    assert bubble_hud.exchanges_y == DESKTOP_RECT.bottom - BOTTOM_MARGIN


@pytest.mark.unit
def test_bubble_hud_comparisons_y_above_exchanges(
    bubble_hud: BubbleHUD, body_font: pygame.font.Font
) -> None:
    line_h = body_font.get_height()
    assert bubble_hud.comparisons_y == bubble_hud.exchanges_y - line_h - LINE_SPACING


@pytest.mark.unit
def test_bubble_hud_comparisons_y_strictly_above_exchanges(bubble_hud: BubbleHUD) -> None:
    assert bubble_hud.comparisons_y < bubble_hud.exchanges_y


@pytest.mark.unit
def test_bubble_hud_comparisons_y_within_panel(bubble_hud: BubbleHUD) -> None:
    assert DESKTOP_RECT.y <= bubble_hud.comparisons_y < DESKTOP_RECT.bottom


@pytest.mark.unit
def test_bubble_hud_exchanges_y_within_panel(bubble_hud: BubbleHUD) -> None:
    assert DESKTOP_RECT.y <= bubble_hud.exchanges_y < DESKTOP_RECT.bottom


@pytest.mark.unit
def test_bubble_hud_counter_x_within_panel(bubble_hud: BubbleHUD) -> None:
    assert DESKTOP_RECT.x <= bubble_hud.counter_x < DESKTOP_RECT.right


# ---------------------------------------------------------------------------
# BubbleHUD — draw no-crash
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_bubble_hud_draw_zero_counts(bubble_hud: BubbleHUD, surface: pygame.Surface) -> None:
    bubble_hud.draw(surface, comparisons=0, exchanges=0)


@pytest.mark.unit
def test_bubble_hud_draw_nonzero_counts(bubble_hud: BubbleHUD, surface: pygame.Surface) -> None:
    bubble_hud.draw(surface, comparisons=20, exchanges=13)


@pytest.mark.unit
def test_bubble_hud_draw_large_counts(bubble_hud: BubbleHUD, surface: pygame.Surface) -> None:
    bubble_hud.draw(surface, comparisons=999, exchanges=999)


# ---------------------------------------------------------------------------
# HeapPhaseLabel — construction
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_heap_phase_label_constructs(body_font: pygame.font.Font) -> None:
    label = HeapPhaseLabel(DESKTOP_RECT, body_font)
    assert label is not None


@pytest.mark.unit
def test_heap_phase_label_center_x_uses_panel_center(heap_phase_label: HeapPhaseLabel) -> None:
    assert heap_phase_label.center_x == DESKTOP_RECT.centerx


# ---------------------------------------------------------------------------
# HeapPhaseLabel — draw no-crash
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_heap_phase_label_draw_build_max_heap(
    heap_phase_label: HeapPhaseLabel, surface: pygame.Surface
) -> None:
    heap_phase_label.draw(surface, phase="BUILD MAX-HEAP", label_y=80.0)


@pytest.mark.unit
def test_heap_phase_label_draw_extraction(
    heap_phase_label: HeapPhaseLabel, surface: pygame.Surface
) -> None:
    heap_phase_label.draw(surface, phase="EXTRACTION", label_y=80.0)


@pytest.mark.unit
def test_heap_phase_label_draw_uses_integer_y(
    heap_phase_label: HeapPhaseLabel, surface: pygame.Surface
) -> None:
    heap_phase_label.draw(surface, phase="BUILD MAX-HEAP", label_y=83.7)


# ---------------------------------------------------------------------------
# HeapBoundaryLabel — construction
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_heap_boundary_label_constructs(body_font: pygame.font.Font) -> None:
    label = HeapBoundaryLabel(body_font)
    assert label is not None


@pytest.mark.unit
def test_heap_boundary_label_text_constant() -> None:
    assert HeapBoundaryLabel.LABEL_TEXT == "heap boundary"


# ---------------------------------------------------------------------------
# HeapBoundaryLabel — draw no-crash
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_heap_boundary_label_draw_no_crash(
    heap_boundary_label: HeapBoundaryLabel, surface: pygame.Surface
) -> None:
    heap_boundary_label.draw(surface, boundary_x=320.0, label_y=200.0)


@pytest.mark.unit
def test_heap_boundary_label_draw_at_origin(
    heap_boundary_label: HeapBoundaryLabel, surface: pygame.Surface
) -> None:
    heap_boundary_label.draw(surface, boundary_x=0.0, label_y=0.0)


@pytest.mark.unit
def test_heap_boundary_label_draw_fractional_coords(
    heap_boundary_label: HeapBoundaryLabel, surface: pygame.Surface
) -> None:
    heap_boundary_label.draw(surface, boundary_x=157.4, label_y=234.8)
