"""Phase 5b: NumberSprite coordinate math and color state tests (TC against doc 04 §4.3, doc 12 §1)."""

from __future__ import annotations

import pygame
import pytest

from visualizer.views.sprite import ColorState, NumberSprite

# ---------------------------------------------------------------------------
# Desktop preset layout constants (matching Phase 5a GridLayout Desktop values)
# ---------------------------------------------------------------------------

PANEL_RECT = pygame.Rect(19, 19, 611, 297)
ARRAY_X_PADDING = 30  # int(611 * 0.05)
SLOT_WIDTH = (611 - 60) / 7  # == 551/7, approx 78.714...


@pytest.fixture
def font() -> pygame.font.Font:
    return pygame.font.SysFont("consolas,courier", 28)


@pytest.fixture
def sprite(font: pygame.font.Font) -> NumberSprite:
    return NumberSprite(0, 4, 0, PANEL_RECT, ARRAY_X_PADDING, SLOT_WIDTH, font)


# ---------------------------------------------------------------------------
# Initial position
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_initial_position(sprite: NumberSprite) -> None:
    assert sprite.exact_x == pytest.approx(sprite.home_x)
    assert sprite.exact_y == pytest.approx(sprite.home_y)


@pytest.mark.unit
def test_home_x_slot_0(font: pygame.font.Font) -> None:
    s = NumberSprite(0, 4, 0, PANEL_RECT, ARRAY_X_PADDING, SLOT_WIDTH, font)
    expected = PANEL_RECT.x + ARRAY_X_PADDING + (0 * SLOT_WIDTH) + (SLOT_WIDTH / 2)
    assert s.home_x == pytest.approx(expected)


@pytest.mark.unit
def test_home_x_slot_3(font: pygame.font.Font) -> None:
    s = NumberSprite(1, 6, 3, PANEL_RECT, ARRAY_X_PADDING, SLOT_WIDTH, font)
    expected = PANEL_RECT.x + ARRAY_X_PADDING + (3 * SLOT_WIDTH) + (SLOT_WIDTH / 2)
    assert s.home_x == pytest.approx(expected)


@pytest.mark.unit
def test_home_x_slot_6(font: pygame.font.Font) -> None:
    s = NumberSprite(2, 3, 6, PANEL_RECT, ARRAY_X_PADDING, SLOT_WIDTH, font)
    expected = PANEL_RECT.x + ARRAY_X_PADDING + (6 * SLOT_WIDTH) + (SLOT_WIDTH / 2)
    assert s.home_x == pytest.approx(expected)


@pytest.mark.unit
def test_home_y(sprite: NumberSprite) -> None:
    expected = PANEL_RECT.y + PANEL_RECT.height // 2
    assert sprite.home_y == pytest.approx(expected)


# ---------------------------------------------------------------------------
# Ring radius
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_ring_radius(sprite: NumberSprite) -> None:
    expected = int(SLOT_WIDTH * 0.65) // 2
    assert sprite.ring_radius == expected


# ---------------------------------------------------------------------------
# Color state
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_initial_color_state(sprite: NumberSprite) -> None:
    assert sprite.color_state is ColorState.DEFAULT


@pytest.mark.unit
def test_set_color_state(sprite: NumberSprite) -> None:
    for state in ColorState:
        sprite.set_color_state(state)
        assert sprite.color_state is state


# ---------------------------------------------------------------------------
# is_lifted property
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_is_lifted_at_rest(sprite: NumberSprite) -> None:
    assert sprite.is_lifted is False


@pytest.mark.unit
def test_is_lifted_when_above(sprite: NumberSprite) -> None:
    sprite.exact_y = sprite.home_y - 10
    assert sprite.is_lifted is True


@pytest.mark.unit
def test_is_lifted_when_below(sprite: NumberSprite) -> None:
    sprite.exact_y = sprite.home_y + 10
    assert sprite.is_lifted is False


# ---------------------------------------------------------------------------
# Surface cache
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_surface_cache_has_all_states(sprite: NumberSprite) -> None:
    assert len(sprite.surface_cache) == len(ColorState)


@pytest.mark.unit
def test_surface_cache_entries_not_none(sprite: NumberSprite) -> None:
    for state in ColorState:
        assert sprite.surface_cache[state] is not None


# ---------------------------------------------------------------------------
# update_home
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_update_home_changes_home_x(sprite: NumberSprite) -> None:
    original_home_x = sprite.home_x
    sprite.update_home(3)
    expected = PANEL_RECT.x + ARRAY_X_PADDING + (3 * SLOT_WIDTH) + (SLOT_WIDTH / 2)
    assert sprite.home_x == pytest.approx(expected)
    assert sprite.home_x != pytest.approx(original_home_x)


@pytest.mark.unit
def test_update_home_preserves_exact(sprite: NumberSprite) -> None:
    original_exact_x = sprite.exact_x
    original_exact_y = sprite.exact_y
    sprite.update_home(3)
    assert sprite.exact_x == pytest.approx(original_exact_x)
    assert sprite.exact_y == pytest.approx(original_exact_y)


@pytest.mark.unit
def test_update_home_preserves_home_y(sprite: NumberSprite) -> None:
    original_home_y = sprite.home_y
    sprite.update_home(3)
    assert sprite.home_y == pytest.approx(original_home_y)


# ---------------------------------------------------------------------------
# draw
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_draw_no_error(sprite: NumberSprite) -> None:
    surface = pygame.Surface((611, 297))
    sprite.draw(surface)  # must not raise


# ---------------------------------------------------------------------------
# Sprite identity
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_sprite_id_immutable_by_convention(sprite: NumberSprite) -> None:
    assert sprite.sprite_id == 0


@pytest.mark.unit
def test_different_slots_different_home_x(font: pygame.font.Font) -> None:
    s0 = NumberSprite(0, 4, 0, PANEL_RECT, ARRAY_X_PADDING, SLOT_WIDTH, font)
    s6 = NumberSprite(6, 3, 6, PANEL_RECT, ARRAY_X_PADDING, SLOT_WIDTH, font)
    assert s0.home_x != pytest.approx(s6.home_x)
