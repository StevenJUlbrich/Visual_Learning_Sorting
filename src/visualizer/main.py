"""Entry point for the Sorting Algorithm Visualizer.

Wires the Pygame event loop to the Orchestrator (Phase 6) and View layer (Phase 5).
Keyboard bindings per doc 06 §Keyboard Bindings: Space, Right Arrow, R, Escape.
dt clamp: min(raw_dt, 33) per CLAUDE.md Critical Rule #7.
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

import pygame

from visualizer.controllers.orchestrator import Orchestrator, PanelContext, PanelState
from visualizer.models.bubble import BubbleSort
from visualizer.models.heap import HeapSort
from visualizer.models.insertion import InsertionSort
from visualizer.models.selection import SelectionSort
from visualizer.views.panel import PanelRenderer
from visualizer.views.panel import PanelState as ViewPanelState
from visualizer.views.sprite_manager import SpriteManager
from visualizer.views.window import GridLayout, init_display, load_preset

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

INITIAL_ARRAY: list[int] = [4, 7, 2, 6, 1, 5, 3]

_DEFAULT_WIDTH: int = 1280
_DEFAULT_HEIGHT: int = 720

_CONFIG_PATH: Path = Path(__file__).resolve().parents[2] / "config.toml"
_FONTS_DIR: Path = Path(__file__).resolve().parents[2] / "assets" / "fonts"

APP_BG_COLOR: tuple[int, int, int] = (30, 30, 35)


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------


def _load_config() -> tuple[int, int]:
    """Load config.toml and return (width, height); default to desktop on any error."""
    try:
        dims = load_preset(_CONFIG_PATH)
        return dims
    except FileNotFoundError:
        print("WARNING: config.toml not found — using desktop preset (1280x720).", file=sys.stderr)
    except (KeyError, ValueError, tomllib.TOMLDecodeError) as exc:
        print(
            f"WARNING: config.toml error ({exc}) — using desktop preset (1280x720).",
            file=sys.stderr,
        )
    return _DEFAULT_WIDTH, _DEFAULT_HEIGHT


# ---------------------------------------------------------------------------
# Font loading
# ---------------------------------------------------------------------------


def _load_fonts() -> tuple[pygame.font.Font, pygame.font.Font, pygame.font.Font]:
    """Load (title_font, body_font, number_font) with SysFont fallback per doc 04 §3.3."""
    title_font: pygame.font.Font
    body_font: pygame.font.Font
    number_font: pygame.font.Font

    try:
        title_font = pygame.font.Font(str(_FONTS_DIR / "Inter-Bold.ttf"), 24)
    except (FileNotFoundError, OSError):
        title_font = pygame.font.SysFont("segoeui, arial", 24)

    try:
        body_font = pygame.font.Font(str(_FONTS_DIR / "Inter-Regular.ttf"), 16)
    except (FileNotFoundError, OSError):
        body_font = pygame.font.SysFont("segoeui, arial", 16)

    try:
        number_font = pygame.font.Font(str(_FONTS_DIR / "FiraCode-Regular.ttf"), 28)
    except (FileNotFoundError, OSError):
        number_font = pygame.font.SysFont("consolas, courier", 28)

    return title_font, body_font, number_font


# ---------------------------------------------------------------------------
# Render helpers
# ---------------------------------------------------------------------------


def _map_panel_state(ctx: PanelContext) -> ViewPanelState:
    """Map orchestrator PanelState to view PanelState."""
    if ctx.state is PanelState.COMPLETED:
        return ViewPanelState.COMPLETED
    if ctx.state is PanelState.FAILED:
        return ViewPanelState.FAILED
    return ViewPanelState.RUNNING


def _elapsed_str(elapsed_ms: int) -> str:
    """Format elapsed milliseconds as 'SS.DDs' (e.g. 8200 → '08.20s')."""
    total_hundredths = elapsed_ms // 10
    seconds = total_hundredths // 100
    hundredths = total_hundredths % 100
    return f"{seconds:02d}.{hundredths:02d}s"


def _build_metrics(ctx: PanelContext) -> str:
    """Build the metrics header string from a PanelContext."""
    return (
        f"{ctx.complexity} | {_elapsed_str(ctx.elapsed_time_ms)} | "
        f"Steps: {ctx.step_count} | Cmp: {ctx.comparisons} | Wr: {ctx.writes}"
    )


def _build_message(ctx: PanelContext) -> str:
    """Return the current tick message, or empty string when no tick is active."""
    if ctx.current_tick is not None:
        return ctx.current_tick.message
    return ""


# ---------------------------------------------------------------------------
# Setup helpers
# ---------------------------------------------------------------------------


def _build_orchestrator() -> Orchestrator:
    """Instantiate the four algorithms and return a configured Orchestrator."""
    algorithms = [
        BubbleSort(INITIAL_ARRAY),
        SelectionSort(INITIAL_ARRAY),
        InsertionSort(INITIAL_ARRAY),
        HeapSort(INITIAL_ARRAY),
    ]
    return Orchestrator(algorithms, INITIAL_ARRAY)


def _build_panel_renderers(
    layout: GridLayout,
    title_font: pygame.font.Font,
    body_font: pygame.font.Font,
) -> list[PanelRenderer]:
    """Build one PanelRenderer per panel rect from the grid layout."""
    return [PanelRenderer(rect, title_font, body_font) for rect in layout.panel_rects]


# ---------------------------------------------------------------------------
# Main event loop
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the Sorting Algorithm Visualizer event loop."""
    pygame.init()

    width, height = _load_config()
    surface, layout = init_display(width, height)
    title_font, body_font, number_font = _load_fonts()

    panel_renderers = _build_panel_renderers(layout, title_font, body_font)
    sprite_managers = [
        SpriteManager(
            panel_rect=layout.panel_rects[i],
            array_x_padding=layout.ARRAY_X_PADDING,
            slot_width=layout.slot_width,
            font=number_font,
            initial_array=INITIAL_ARRAY,
        )
        for i in range(4)
    ]
    orchestrator = _build_orchestrator()

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if orchestrator.is_running:
                        orchestrator.pause()
                    else:
                        orchestrator.play()
                elif event.key == pygame.K_RIGHT:
                    orchestrator.step()
                elif event.key == pygame.K_r:
                    orchestrator.restart()
                    for sm in sprite_managers:
                        sm.reset(INITIAL_ARRAY)
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return

        raw_dt = clock.tick(60)
        dt = min(raw_dt, 33)

        orchestrator.update(dt)

        surface.fill(APP_BG_COLOR)

        for i, renderer in enumerate(panel_renderers):
            ctx = orchestrator.panels[i]
            view_state = _map_panel_state(ctx)
            renderer.draw_background(surface, view_state)
            renderer.draw_header(
                surface,
                ctx.algorithm_name,
                _build_metrics(ctx),
                _build_message(ctx),
                view_state,
            )
            sprite_managers[i].update(dt, ctx)
            sprite_managers[i].draw(surface)

        pygame.display.flip()


if __name__ == "__main__":
    main()
