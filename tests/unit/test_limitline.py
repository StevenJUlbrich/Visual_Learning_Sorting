"""Phase 5f: LimitLine position, visibility, advance/reset, and draw tests.

Tests verify boundary position formula, visibility states, advance/reset behavior,
and draw no-crash. Uses Desktop preset constants.
"""

from __future__ import annotations

import pytest
from pygame import Rect

from visualizer.views.limitline import LINE_COLOR, LINE_MARGIN, LimitLine
from visualizer.views.sprite import RING_DIAMETER_RATIO

# ---------------------------------------------------------------------------
# Desktop preset constants
# ---------------------------------------------------------------------------

DESKTOP_RECT = Rect(19, 19, 611, 297)
ARRAY_X_PADDING = int(611 * 0.05)  # 30
SLOT_WIDTH = (611 - ARRAY_X_PADDING * 2) / 7  # 551/7
RING_RADIUS = int(SLOT_WIDTH * RING_DIAMETER_RATIO) // 2  # 25
HOME_Y = float(DESKTOP_RECT.y + DESKTOP_RECT.height // 2)  # 167.0
ARRAY_SIZE = 7


@pytest.fixture
def ll() -> LimitLine:
    return LimitLine(DESKTOP_RECT, ARRAY_X_PADDING, SLOT_WIDTH, HOME_Y, RING_RADIUS, ARRAY_SIZE)


# ---------------------------------------------------------------------------
# Initial state
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_initial_boundary_index(ll: LimitLine) -> None:
    assert ll.boundary_index == ARRAY_SIZE


@pytest.mark.unit
def test_initial_x_position(ll: LimitLine) -> None:
    expected = DESKTOP_RECT.x + ARRAY_X_PADDING + ARRAY_SIZE * SLOT_WIDTH
    assert ll.x_position == pytest.approx(expected)


@pytest.mark.unit
def test_initial_not_visible(ll: LimitLine) -> None:
    assert ll.is_visible is False


# ---------------------------------------------------------------------------
# advance()
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_advance_decrements_boundary(ll: LimitLine) -> None:
    ll.advance()
    assert ll.boundary_index == ARRAY_SIZE - 1


@pytest.mark.unit
def test_advance_twice_boundary(ll: LimitLine) -> None:
    ll.advance()
    ll.advance()
    assert ll.boundary_index == ARRAY_SIZE - 2


@pytest.mark.unit
def test_x_position_after_advance(ll: LimitLine) -> None:
    ll.advance()
    expected = DESKTOP_RECT.x + ARRAY_X_PADDING + (ARRAY_SIZE - 1) * SLOT_WIDTH
    assert ll.x_position == pytest.approx(expected)


@pytest.mark.unit
def test_x_position_formula_consistency(ll: LimitLine) -> None:
    for _ in range(3):
        ll.advance()
    expected = DESKTOP_RECT.x + ARRAY_X_PADDING + ll.boundary_index * SLOT_WIDTH
    assert ll.x_position == pytest.approx(expected)


@pytest.mark.unit
def test_advance_guard_no_below_zero(ll: LimitLine) -> None:
    for _ in range(20):
        ll.advance()
    assert ll.boundary_index == 0


# ---------------------------------------------------------------------------
# Visibility
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_is_visible_after_advance(ll: LimitLine) -> None:
    ll.advance()
    assert ll.is_visible is True


@pytest.mark.unit
def test_is_visible_boundary_1(ll: LimitLine) -> None:
    for _ in range(ARRAY_SIZE - 1):
        ll.advance()
    assert ll.boundary_index == 1
    assert ll.is_visible is True


@pytest.mark.unit
def test_is_not_visible_boundary_0(ll: LimitLine) -> None:
    for _ in range(ARRAY_SIZE):
        ll.advance()
    assert ll.boundary_index == 0
    assert ll.is_visible is False


@pytest.mark.unit
def test_is_visible_mid_range(ll: LimitLine) -> None:
    for _ in range(3):
        ll.advance()
    assert ll.boundary_index == ARRAY_SIZE - 3
    assert ll.is_visible is True


# ---------------------------------------------------------------------------
# reset()
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_reset_restores_array_size(ll: LimitLine) -> None:
    ll.advance()
    ll.advance()
    ll.reset()
    assert ll.boundary_index == ARRAY_SIZE


@pytest.mark.unit
def test_reset_restores_not_visible(ll: LimitLine) -> None:
    ll.advance()
    ll.reset()
    assert ll.is_visible is False


@pytest.mark.unit
def test_reset_after_full_cycle(ll: LimitLine) -> None:
    for _ in range(ARRAY_SIZE):
        ll.advance()
    ll.reset()
    assert ll.boundary_index == ARRAY_SIZE


# ---------------------------------------------------------------------------
# x_position between adjacent slot centers (sanity)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_x_between_slot_5_and_6_centers_after_advance(ll: LimitLine) -> None:
    ll.advance()  # boundary_index=6
    slot5_center = DESKTOP_RECT.x + ARRAY_X_PADDING + 5 * SLOT_WIDTH + SLOT_WIDTH / 2
    slot6_center = DESKTOP_RECT.x + ARRAY_X_PADDING + 6 * SLOT_WIDTH + SLOT_WIDTH / 2
    assert slot5_center < ll.x_position < slot6_center


# ---------------------------------------------------------------------------
# Line extent invariant
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_line_spans_array_region() -> None:
    top_y = HOME_Y - RING_RADIUS - LINE_MARGIN
    bottom_y = HOME_Y + RING_RADIUS + LINE_MARGIN
    assert top_y < HOME_Y < bottom_y


# ---------------------------------------------------------------------------
# Color constant
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_line_color_constant() -> None:
    assert LINE_COLOR == (150, 150, 160)


# ---------------------------------------------------------------------------
# Draw no-crash
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_draw_visible_no_crash(ll: LimitLine) -> None:
    import pygame

    ll.advance()
    surface = pygame.Surface((DESKTOP_RECT.width + 40, DESKTOP_RECT.height + 40))
    ll.draw(surface)


@pytest.mark.unit
def test_draw_invisible_initial_no_crash(ll: LimitLine) -> None:
    import pygame

    surface = pygame.Surface((DESKTOP_RECT.width + 40, DESKTOP_RECT.height + 40))
    ll.draw(surface)  # boundary_index == array_size, is_visible=False


@pytest.mark.unit
def test_draw_boundary_zero_no_crash(ll: LimitLine) -> None:
    import pygame

    for _ in range(ARRAY_SIZE):
        ll.advance()
    surface = pygame.Surface((DESKTOP_RECT.width + 40, DESKTOP_RECT.height + 40))
    ll.draw(surface)  # boundary_index == 0, is_visible=False
