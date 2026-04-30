"""Phase 5c: PanelRenderer coordinate math, color constants, and state tests.

TC against doc 04 §4.1.1 (header vertical rhythm), §2.4 (panel geometry), D-078.
All tests are coordinate/math/no-render or lightweight pixel-check on off-screen surfaces.
"""

from __future__ import annotations

import pygame
import pytest

from visualizer.views.panel import (
    COMPLETION_BG,
    ERROR_BORDER,
    ERROR_BORDER_WIDTH,
    MESSAGE_GAP,
    METRICS_GAP,
    PANEL_BG,
    PanelRenderer,
    PanelState,
    compute_header_inset_x,
    compute_header_inset_y,
    compute_header_total,
    truncate_text,
)

# ---------------------------------------------------------------------------
# Desktop preset  (panel_width=611, panel_height=297)
# ---------------------------------------------------------------------------

DESKTOP_W, DESKTOP_H = 611, 297
DESKTOP_RECT = pygame.Rect(19, 19, DESKTOP_W, DESKTOP_H)

# ---------------------------------------------------------------------------
# Tablet preset  (panel_width=489, panel_height=327)
# ---------------------------------------------------------------------------

TABLET_W, TABLET_H = 489, 327
TABLET_RECT = pygame.Rect(15, 15, TABLET_W, TABLET_H)


@pytest.fixture
def title_font() -> pygame.font.Font:
    return pygame.font.SysFont("segoeui,arial", 24)


@pytest.fixture
def body_font() -> pygame.font.Font:
    return pygame.font.SysFont("segoeui,arial", 16)


@pytest.fixture
def desktop_renderer(title_font: pygame.font.Font, body_font: pygame.font.Font) -> PanelRenderer:
    return PanelRenderer(DESKTOP_RECT, title_font, body_font)


@pytest.fixture
def tablet_renderer(title_font: pygame.font.Font, body_font: pygame.font.Font) -> PanelRenderer:
    return PanelRenderer(TABLET_RECT, title_font, body_font)


# ---------------------------------------------------------------------------
# Header spacing tokens — Desktop
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_desktop_header_inset_x_minimum() -> None:
    assert compute_header_inset_x(DESKTOP_W) >= 12


@pytest.mark.unit
def test_desktop_header_inset_x_proportional() -> None:
    assert compute_header_inset_x(DESKTOP_W) == max(int(DESKTOP_W * 0.03), 12)


@pytest.mark.unit
def test_desktop_header_inset_y_minimum() -> None:
    assert compute_header_inset_y(DESKTOP_H) >= 10


@pytest.mark.unit
def test_desktop_header_inset_y_proportional() -> None:
    assert compute_header_inset_y(DESKTOP_H) == max(int(DESKTOP_H * 0.04), 10)


# ---------------------------------------------------------------------------
# Header spacing tokens — Tablet
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_tablet_header_inset_x_minimum() -> None:
    assert compute_header_inset_x(TABLET_W) >= 12


@pytest.mark.unit
def test_tablet_header_inset_x_proportional() -> None:
    assert compute_header_inset_x(TABLET_W) == max(int(TABLET_W * 0.03), 12)


@pytest.mark.unit
def test_tablet_header_inset_y_minimum() -> None:
    assert compute_header_inset_y(TABLET_H) >= 10


@pytest.mark.unit
def test_tablet_header_inset_y_proportional() -> None:
    assert compute_header_inset_y(TABLET_H) == max(int(TABLET_H * 0.04), 10)


# ---------------------------------------------------------------------------
# Fixed-gap constants
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_metrics_gap_value() -> None:
    assert METRICS_GAP == 4


@pytest.mark.unit
def test_message_gap_value() -> None:
    assert MESSAGE_GAP == 6


# ---------------------------------------------------------------------------
# PanelRenderer stores correct inset values at construction
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_renderer_inset_x_desktop(desktop_renderer: PanelRenderer) -> None:
    assert desktop_renderer.inset_x == compute_header_inset_x(DESKTOP_W)


@pytest.mark.unit
def test_renderer_inset_y_desktop(desktop_renderer: PanelRenderer) -> None:
    assert desktop_renderer.inset_y == compute_header_inset_y(DESKTOP_H)


# ---------------------------------------------------------------------------
# Anchor positions
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_title_anchor_x(desktop_renderer: PanelRenderer) -> None:
    expected = DESKTOP_RECT.x + desktop_renderer.inset_x
    assert expected == DESKTOP_RECT.x + compute_header_inset_x(DESKTOP_W)


@pytest.mark.unit
def test_title_anchor_y(desktop_renderer: PanelRenderer) -> None:
    expected = DESKTOP_RECT.y + desktop_renderer.inset_y
    assert expected == DESKTOP_RECT.y + compute_header_inset_y(DESKTOP_H)


@pytest.mark.unit
def test_metrics_anchor_y_formula() -> None:
    inset_y = compute_header_inset_y(DESKTOP_H)
    title_y = DESKTOP_RECT.y + inset_y
    title_height = 28
    assert title_y + title_height + METRICS_GAP == title_y + title_height + 4


@pytest.mark.unit
def test_message_anchor_y_formula() -> None:
    inset_y = compute_header_inset_y(DESKTOP_H)
    title_y = DESKTOP_RECT.y + inset_y
    title_height = 28
    metrics_y = title_y + title_height + METRICS_GAP
    metrics_height = 20
    assert metrics_y + metrics_height + MESSAGE_GAP == metrics_y + metrics_height + 6


# ---------------------------------------------------------------------------
# Header height budget <= 35% of panel_height
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_header_budget_desktop_within_35pct(
    title_font: pygame.font.Font, body_font: pygame.font.Font
) -> None:
    title_h = title_font.get_linesize()
    body_h = body_font.get_linesize()
    total = compute_header_total(DESKTOP_H, title_h, body_h, body_h)
    assert total <= int(DESKTOP_H * 0.35)


@pytest.mark.unit
def test_header_budget_tablet_within_35pct(
    title_font: pygame.font.Font, body_font: pygame.font.Font
) -> None:
    title_h = title_font.get_linesize()
    body_h = body_font.get_linesize()
    total = compute_header_total(TABLET_H, title_h, body_h, body_h)
    assert total <= int(TABLET_H * 0.35)


# ---------------------------------------------------------------------------
# Color constants
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_panel_bg_imported_from_sprite() -> None:
    assert PANEL_BG == (45, 45, 53)


@pytest.mark.unit
def test_completion_bg_color() -> None:
    assert COMPLETION_BG == (35, 55, 42)


@pytest.mark.unit
def test_error_border_color() -> None:
    assert ERROR_BORDER == (235, 80, 80)


@pytest.mark.unit
def test_error_border_width() -> None:
    assert ERROR_BORDER_WIDTH == 3


# ---------------------------------------------------------------------------
# Panel state affects background color (pixel check)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_running_background_draws_panel_bg(desktop_renderer: PanelRenderer) -> None:
    surface = pygame.Surface((DESKTOP_W + 40, DESKTOP_H + 40))
    surface.fill((0, 0, 0))
    desktop_renderer.draw_background(surface, PanelState.RUNNING)
    cx = DESKTOP_RECT.x + DESKTOP_RECT.width // 2
    cy = DESKTOP_RECT.y + DESKTOP_RECT.height // 2
    pixel = surface.get_at((cx, cy))
    assert (pixel.r, pixel.g, pixel.b) == PANEL_BG


@pytest.mark.unit
def test_completed_background_draws_green(desktop_renderer: PanelRenderer) -> None:
    surface = pygame.Surface((DESKTOP_W + 40, DESKTOP_H + 40))
    surface.fill((0, 0, 0))
    desktop_renderer.draw_background(surface, PanelState.COMPLETED)
    cx = DESKTOP_RECT.x + DESKTOP_RECT.width // 2
    cy = DESKTOP_RECT.y + DESKTOP_RECT.height // 2
    pixel = surface.get_at((cx, cy))
    assert (pixel.r, pixel.g, pixel.b) == COMPLETION_BG


# ---------------------------------------------------------------------------
# Error state draws border (no-crash)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_error_background_no_crash(desktop_renderer: PanelRenderer) -> None:
    surface = pygame.Surface((DESKTOP_W + 40, DESKTOP_H + 40))
    desktop_renderer.draw_background(surface, PanelState.FAILED)  # must not raise


# ---------------------------------------------------------------------------
# draw_header no-crash
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_draw_header_running_no_crash(desktop_renderer: PanelRenderer) -> None:
    surface = pygame.Surface((DESKTOP_W + 40, DESKTOP_H + 40))
    metrics = "O(n²) | 03.45s | Steps: 35 | Comps: 21 | Writes: 30"
    desktop_renderer.draw_header(surface, "Bubble Sort", metrics, "Swapping 0↔0")


@pytest.mark.unit
def test_draw_header_failed_state_no_crash(desktop_renderer: PanelRenderer) -> None:
    surface = pygame.Surface((DESKTOP_W + 40, DESKTOP_H + 40))
    desktop_renderer.draw_header(
        surface,
        "Heap Sort",
        "O(n log n) | 00.00s | Steps: 0",
        "Error: empty input",
        PanelState.FAILED,
    )


@pytest.mark.unit
def test_draw_header_returns_positive_height(desktop_renderer: PanelRenderer) -> None:
    surface = pygame.Surface((DESKTOP_W + 40, DESKTOP_H + 40))
    h = desktop_renderer.draw_header(surface, "Insertion Sort", "O(n²)", "Placing key")
    assert h > 0


# ---------------------------------------------------------------------------
# Metrics truncation
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_truncate_short_string_unchanged(body_font: pygame.font.Font) -> None:
    short = "O(n²)"
    assert truncate_text(body_font, short, 999) == short


@pytest.mark.unit
def test_truncate_long_string_ends_with_ellipsis(body_font: pygame.font.Font) -> None:
    long_str = "O(n²) | 03.45s | Steps: 35 | Comps: 21 | Writes: 30 | extra padding text here"
    result = truncate_text(body_font, long_str, 200)
    assert result.endswith("…")


@pytest.mark.unit
def test_truncate_respects_max_width(body_font: pygame.font.Font) -> None:
    long_str = "A" * 200
    max_w = 100
    result = truncate_text(body_font, long_str, max_w)
    assert body_font.size(result)[0] <= max_w
