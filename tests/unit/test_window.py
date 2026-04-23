"""Phase 5a: GridLayout coordinate-math tests (TC against doc 04 §2.6)."""

from pathlib import Path

import pytest
from pygame import Rect

from visualizer.views.window import GridLayout, load_preset

# ---------------------------------------------------------------------------
# Desktop preset (1280x720) — exact computed values, not spec-table approximations
# ---------------------------------------------------------------------------

DESKTOP_W, DESKTOP_H = 1280, 720


@pytest.mark.unit
def test_desktop_padding() -> None:
    assert GridLayout(DESKTOP_W, DESKTOP_H).PADDING == 19  # int(1280 * 0.015)


@pytest.mark.unit
def test_desktop_control_bar_height() -> None:
    assert GridLayout(DESKTOP_W, DESKTOP_H).CONTROL_BAR_HEIGHT == 50  # int(720 * 0.07)


@pytest.mark.unit
def test_desktop_grid_height() -> None:
    assert GridLayout(DESKTOP_W, DESKTOP_H).grid_height == 651  # 720 - 50 - 19


@pytest.mark.unit
def test_desktop_panel_width() -> None:
    assert GridLayout(DESKTOP_W, DESKTOP_H).panel_width == 611  # (1280 - 57) // 2


@pytest.mark.unit
def test_desktop_panel_height() -> None:
    # (651 - 57) // 2 = 297; spec table says 296 but formula is authoritative
    assert GridLayout(DESKTOP_W, DESKTOP_H).panel_height == 297


@pytest.mark.unit
def test_desktop_rect_top_left() -> None:
    layout = GridLayout(DESKTOP_W, DESKTOP_H)
    assert layout.panel_rects[0] == Rect(19, 19, 611, layout.panel_height)


@pytest.mark.unit
def test_desktop_rect_top_right() -> None:
    layout = GridLayout(DESKTOP_W, DESKTOP_H)
    assert layout.panel_rects[1] == Rect(649, 19, 611, layout.panel_height)


@pytest.mark.unit
def test_desktop_rect_bottom_left() -> None:
    layout = GridLayout(DESKTOP_W, DESKTOP_H)
    assert layout.panel_rects[2] == Rect(19, 19 * 2 + layout.panel_height, 611, layout.panel_height)


@pytest.mark.unit
def test_desktop_rect_bottom_right() -> None:
    layout = GridLayout(DESKTOP_W, DESKTOP_H)
    assert layout.panel_rects[3] == Rect(
        649, 19 * 2 + layout.panel_height, 611, layout.panel_height
    )


@pytest.mark.unit
def test_panel_radius() -> None:
    assert GridLayout(DESKTOP_W, DESKTOP_H).PANEL_RADIUS == 12


@pytest.mark.unit
def test_desktop_array_x_padding() -> None:
    assert GridLayout(DESKTOP_W, DESKTOP_H).ARRAY_X_PADDING == 30  # int(611 * 0.05)


@pytest.mark.unit
def test_desktop_slot_width() -> None:
    layout = GridLayout(DESKTOP_W, DESKTOP_H)
    assert layout.slot_width == pytest.approx((611 - 60) / 7)


# ---------------------------------------------------------------------------
# Tablet preset (1024x768)
# ---------------------------------------------------------------------------

TABLET_W, TABLET_H = 1024, 768


@pytest.mark.unit
def test_tablet_padding() -> None:
    assert GridLayout(TABLET_W, TABLET_H).PADDING == 15  # int(1024 * 0.015)


@pytest.mark.unit
def test_tablet_control_bar_height() -> None:
    assert GridLayout(TABLET_W, TABLET_H).CONTROL_BAR_HEIGHT == 53  # int(768 * 0.07)


@pytest.mark.unit
def test_tablet_grid_height() -> None:
    assert GridLayout(TABLET_W, TABLET_H).grid_height == 700  # 768 - 53 - 15


@pytest.mark.unit
def test_tablet_panel_width() -> None:
    assert GridLayout(TABLET_W, TABLET_H).panel_width == 489  # (1024 - 45) // 2


@pytest.mark.unit
def test_tablet_panel_height() -> None:
    assert GridLayout(TABLET_W, TABLET_H).panel_height == 327  # (700 - 45) // 2


@pytest.mark.unit
def test_tablet_panel_radius() -> None:
    assert GridLayout(TABLET_W, TABLET_H).PANEL_RADIUS == 12


# ---------------------------------------------------------------------------
# Grid invariants — both presets
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize("w,h", [(DESKTOP_W, DESKTOP_H), (TABLET_W, TABLET_H)])
def test_panels_non_overlapping(w: int, h: int) -> None:
    rects = GridLayout(w, h).panel_rects
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            assert not rects[i].colliderect(rects[j])


@pytest.mark.unit
@pytest.mark.parametrize("w,h", [(DESKTOP_W, DESKTOP_H), (TABLET_W, TABLET_H)])
def test_panels_fit_within_window(w: int, h: int) -> None:
    layout = GridLayout(w, h)
    bounds = Rect(0, 0, w, h - layout.CONTROL_BAR_HEIGHT)
    for rect in layout.panel_rects:
        assert bounds.contains(rect)


@pytest.mark.unit
@pytest.mark.parametrize("w,h", [(DESKTOP_W, DESKTOP_H), (TABLET_W, TABLET_H)])
def test_panel_width_minimum(w: int, h: int) -> None:
    assert GridLayout(w, h).panel_width >= 489


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_unknown_preset_raises(tmp_path: Path) -> None:
    config = tmp_path / "config.toml"
    config.write_text('[window]\npreset = "ultrawide"\n')
    with pytest.raises(ValueError, match="Unknown window preset"):
        load_preset(config)
