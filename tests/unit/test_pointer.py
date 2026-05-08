"""Phase 5e: PointerSet position, coalescing, and draw tests (TC-A23).

Tests verify arrow geometry, slot center formula, and D-068 coalescing behavior.
Draw no-crash tests use off-screen surfaces.
"""

from __future__ import annotations

import pygame
import pytest

from visualizer.views.pointer import (
    I_ARROW_GAP,
    JMIN_ARROW_GAP,
    JMIN_ARROW_HEIGHT,
    LABEL_GAP,
    POINTER_I_COLOR,
    POINTER_J_COLOR,
    POINTER_MIN_COLOR,
    PointerSet,
)
from visualizer.views.sprite import RING_DIAMETER_RATIO

# ---------------------------------------------------------------------------
# Desktop preset constants
# ---------------------------------------------------------------------------

DESKTOP_RECT = pygame.Rect(19, 19, 611, 297)
ARRAY_X_PADDING = int(611 * 0.05)  # 30
SLOT_WIDTH = (611 - ARRAY_X_PADDING * 2) / 7  # 551/7
RING_RADIUS = int(SLOT_WIDTH * RING_DIAMETER_RATIO) // 2  # int(78.714 * 0.65) // 2 = 25
HOME_Y = DESKTOP_RECT.y + DESKTOP_RECT.height // 2  # 19 + 148 = 167


@pytest.fixture
def body_font() -> pygame.font.Font:
    return pygame.font.SysFont("segoeui,arial", 16)


@pytest.fixture
def pointer_set(body_font: pygame.font.Font) -> PointerSet:
    return PointerSet(DESKTOP_RECT, ARRAY_X_PADDING, SLOT_WIDTH, RING_RADIUS, body_font)


# ---------------------------------------------------------------------------
# Arrow position invariants
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_i_arrow_y_below_jmin(pointer_set: PointerSet) -> None:
    assert pointer_set.i_arrow_y() > pointer_set.jmin_arrow_y()


@pytest.mark.unit
def test_jmin_arrow_y_below_baseline(pointer_set: PointerSet) -> None:
    assert pointer_set.jmin_arrow_y() > HOME_Y


@pytest.mark.unit
def test_i_arrow_y_formula(pointer_set: PointerSet, body_font: pygame.font.Font) -> None:
    jmin_tip = HOME_Y + RING_RADIUS + JMIN_ARROW_GAP
    jmin_label_bottom = jmin_tip + JMIN_ARROW_HEIGHT + LABEL_GAP + body_font.get_height()
    expected = jmin_label_bottom + I_ARROW_GAP
    assert pointer_set.i_arrow_y() == pytest.approx(expected)


@pytest.mark.unit
def test_jmin_arrow_y_formula(pointer_set: PointerSet) -> None:
    expected = HOME_Y + RING_RADIUS + JMIN_ARROW_GAP
    assert pointer_set.jmin_arrow_y() == pytest.approx(expected)


# ---------------------------------------------------------------------------
# slot_center_x — matches sprite home_x formula
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_slot_center_x_slot_0(pointer_set: PointerSet) -> None:
    expected = DESKTOP_RECT.x + ARRAY_X_PADDING + 0 * SLOT_WIDTH + SLOT_WIDTH / 2
    assert pointer_set.slot_center_x(0) == pytest.approx(expected)


@pytest.mark.unit
def test_slot_center_x_slot_3(pointer_set: PointerSet) -> None:
    expected = DESKTOP_RECT.x + ARRAY_X_PADDING + 3 * SLOT_WIDTH + SLOT_WIDTH / 2
    assert pointer_set.slot_center_x(3) == pytest.approx(expected)


@pytest.mark.unit
def test_slot_center_x_slot_6(pointer_set: PointerSet) -> None:
    expected = DESKTOP_RECT.x + ARRAY_X_PADDING + 6 * SLOT_WIDTH + SLOT_WIDTH / 2
    assert pointer_set.slot_center_x(6) == pytest.approx(expected)


@pytest.mark.unit
def test_i_arrow_x_matches_slot_center(pointer_set: PointerSet) -> None:
    expected = DESKTOP_RECT.x + ARRAY_X_PADDING + 2 * SLOT_WIDTH + SLOT_WIDTH / 2
    assert pointer_set.slot_center_x(2) == pytest.approx(expected)


# ---------------------------------------------------------------------------
# TC-A23: Coalescing behavior (D-068)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_coalesce_j_equals_min_hides_j(pointer_set: PointerSet) -> None:
    _, eff_j, _ = pointer_set.coalesced_pointers(0, 3, 3)
    assert eff_j is None


@pytest.mark.unit
def test_coalesce_j_equals_min_keeps_min(pointer_set: PointerSet) -> None:
    _, _, eff_min = pointer_set.coalesced_pointers(0, 3, 3)
    assert eff_min == 3


@pytest.mark.unit
def test_coalesce_j_different_from_min_both_visible(pointer_set: PointerSet) -> None:
    _, eff_j, eff_min = pointer_set.coalesced_pointers(0, 2, 4)
    assert eff_j == 2
    assert eff_min == 4


@pytest.mark.unit
def test_coalesce_j_none_min_visible(pointer_set: PointerSet) -> None:
    _, eff_j, eff_min = pointer_set.coalesced_pointers(0, None, 4)
    assert eff_j is None
    assert eff_min == 4


@pytest.mark.unit
def test_coalesce_min_none_j_visible(pointer_set: PointerSet) -> None:
    _, eff_j, eff_min = pointer_set.coalesced_pointers(0, 2, None)
    assert eff_j == 2
    assert eff_min is None


@pytest.mark.unit
def test_coalesce_i_not_affected_by_coalescing(pointer_set: PointerSet) -> None:
    eff_i, _, _ = pointer_set.coalesced_pointers(1, 3, 3)
    assert eff_i == 1


@pytest.mark.unit
def test_coalesce_all_different_all_visible(pointer_set: PointerSet) -> None:
    eff_i, eff_j, eff_min = pointer_set.coalesced_pointers(0, 2, 4)
    assert eff_i == 0
    assert eff_j == 2
    assert eff_min == 4


@pytest.mark.unit
def test_coalesce_all_none(pointer_set: PointerSet) -> None:
    eff_i, eff_j, eff_min = pointer_set.coalesced_pointers(None, None, None)
    assert eff_i is None
    assert eff_j is None
    assert eff_min is None


# ---------------------------------------------------------------------------
# Color constants
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_pointer_i_color_is_cyan() -> None:
    assert POINTER_I_COLOR == (80, 200, 220)


@pytest.mark.unit
def test_pointer_j_color_is_active_orange() -> None:
    assert POINTER_J_COLOR == (255, 140, 0)


@pytest.mark.unit
def test_pointer_min_color_matches_j() -> None:
    assert POINTER_MIN_COLOR == POINTER_J_COLOR


# ---------------------------------------------------------------------------
# Draw no-crash
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_draw_all_valid_no_crash(pointer_set: PointerSet) -> None:
    surface = pygame.Surface((DESKTOP_RECT.width + 40, DESKTOP_RECT.height + 40))
    pointer_set.draw(surface, 0, 3, 5)


@pytest.mark.unit
def test_draw_all_none_no_crash(pointer_set: PointerSet) -> None:
    surface = pygame.Surface((DESKTOP_RECT.width + 40, DESKTOP_RECT.height + 40))
    pointer_set.draw(surface, None, None, None)


@pytest.mark.unit
def test_draw_coalescing_j_equals_min_no_crash(pointer_set: PointerSet) -> None:
    surface = pygame.Surface((DESKTOP_RECT.width + 40, DESKTOP_RECT.height + 40))
    pointer_set.draw(surface, 0, 3, 3)


@pytest.mark.unit
def test_draw_edge_slot_0_no_crash(pointer_set: PointerSet) -> None:
    surface = pygame.Surface((DESKTOP_RECT.width + 40, DESKTOP_RECT.height + 40))
    pointer_set.draw(surface, 0, 0, 0)


@pytest.mark.unit
def test_draw_edge_slot_6_no_crash(pointer_set: PointerSet) -> None:
    surface = pygame.Surface((DESKTOP_RECT.width + 40, DESKTOP_RECT.height + 40))
    pointer_set.draw(surface, 6, 6, 6)


@pytest.mark.unit
def test_draw_i_only_no_crash(pointer_set: PointerSet) -> None:
    surface = pygame.Surface((DESKTOP_RECT.width + 40, DESKTOP_RECT.height + 40))
    pointer_set.draw(surface, 2, None, None)
