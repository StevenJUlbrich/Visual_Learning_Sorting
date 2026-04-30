"""PanelRenderer — per-algorithm panel frame rendering.

Renders background, header text stack (title → metrics → message), and state overlays.
Draws directly to the main display surface (doc 04 §4.4).
Does NOT own sprites, tree layout, pointers, limitline, or HUD counters.

See doc 04 §4.1.1 (header vertical rhythm), §2.4 (panel geometry), D-078 (completion BG).
"""

from __future__ import annotations

from enum import Enum

import pygame

from visualizer.views.sprite import PANEL_BG_COLOR

# ---------------------------------------------------------------------------
# Color constants
# ---------------------------------------------------------------------------

PRIMARY_TEXT: tuple[int, int, int] = (240, 240, 245)
SECONDARY_TEXT: tuple[int, int, int] = (190, 190, 200)
PANEL_BG: tuple[int, int, int] = PANEL_BG_COLOR  # (45, 45, 53) — imported from sprite.py
COMPLETION_BG: tuple[int, int, int] = (35, 55, 42)  # D-078
ERROR_TEXT: tuple[int, int, int] = (255, 120, 120)
ERROR_BORDER: tuple[int, int, int] = (235, 80, 80)
ERROR_BORDER_WIDTH: int = 3
PANEL_RADIUS: int = 12

# ---------------------------------------------------------------------------
# Header spacing tokens (doc 04 §4.1.1)
# ---------------------------------------------------------------------------

METRICS_GAP: int = 4
MESSAGE_GAP: int = 6


def compute_header_inset_x(panel_width: int) -> int:
    """Left margin from panel edge; minimum 12px (doc 04 §4.1.1)."""
    return max(int(panel_width * 0.03), 12)


def compute_header_inset_y(panel_height: int) -> int:
    """Top margin from panel edge; minimum 10px (doc 04 §4.1.1)."""
    return max(int(panel_height * 0.04), 10)


def compute_header_total(
    panel_height: int,
    title_height: int,
    metrics_height: int,
    message_height: int,
) -> int:
    """Total header height budget from panel top through message bottom."""
    inset_y = compute_header_inset_y(panel_height)
    return inset_y + title_height + METRICS_GAP + metrics_height + MESSAGE_GAP + message_height


# ---------------------------------------------------------------------------
# Panel state
# ---------------------------------------------------------------------------


class PanelState(Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# ---------------------------------------------------------------------------
# Text helper
# ---------------------------------------------------------------------------


def truncate_text(font: pygame.font.Font, text: str, max_width: int) -> str:
    """Return text truncated with an ellipsis if wider than max_width pixels."""
    if font.size(text)[0] <= max_width:
        return text
    ellipsis = "…"
    while text and font.size(text + ellipsis)[0] > max_width:
        text = text[:-1]
    return text + ellipsis


# ---------------------------------------------------------------------------
# PanelRenderer
# ---------------------------------------------------------------------------


class PanelRenderer:
    """Renders background, header stack, and state overlays for one algorithm panel.

    Draw order expected by callers: draw_background → draw_header → sprite layer.
    """

    def __init__(
        self,
        rect: pygame.Rect,
        title_font: pygame.font.Font,
        body_font: pygame.font.Font,
    ) -> None:
        self.rect = rect
        self.title_font = title_font
        self.body_font = body_font
        self.inset_x: int = compute_header_inset_x(rect.width)
        self.inset_y: int = compute_header_inset_y(rect.height)

    def draw_background(
        self,
        surface: pygame.Surface,
        state: PanelState = PanelState.RUNNING,
    ) -> None:
        """Draw panel background; green tint for completed, error border for failed (D-078)."""
        color = COMPLETION_BG if state is PanelState.COMPLETED else PANEL_BG
        pygame.draw.rect(surface, color, self.rect, border_radius=PANEL_RADIUS)
        if state is PanelState.FAILED:
            pygame.draw.rect(
                surface,
                ERROR_BORDER,
                self.rect,
                width=ERROR_BORDER_WIDTH,
                border_radius=PANEL_RADIUS,
            )

    def draw_header(
        self,
        surface: pygame.Surface,
        title: str,
        metrics: str,
        message: str,
        state: PanelState = PanelState.RUNNING,
    ) -> int:
        """Draw title → metrics → message header stack (doc 04 §4.1.1).

        Returns total header height (HEADER_INSET_Y through message bottom),
        which callers use to anchor the array rendering region.
        """
        max_text_w = self.rect.width - self.inset_x * 2
        anchor_x = self.rect.x + self.inset_x
        title_y = self.rect.y + self.inset_y

        title_surf = self.title_font.render(title, True, PRIMARY_TEXT)
        surface.blit(title_surf, (anchor_x, title_y))
        title_h = title_surf.get_height()

        metrics_y = title_y + title_h + METRICS_GAP
        metrics_surf = self.body_font.render(
            truncate_text(self.body_font, metrics, max_text_w),
            True,
            SECONDARY_TEXT,
        )
        surface.blit(metrics_surf, (anchor_x, metrics_y))
        metrics_h = metrics_surf.get_height()

        message_y = metrics_y + metrics_h + MESSAGE_GAP
        msg_color = ERROR_TEXT if state is PanelState.FAILED else SECONDARY_TEXT
        message_surf = self.body_font.render(
            truncate_text(self.body_font, message, max_text_w),
            True,
            msg_color,
        )
        surface.blit(message_surf, (anchor_x, message_y))
        message_h = message_surf.get_height()

        return self.inset_y + title_h + METRICS_GAP + metrics_h + MESSAGE_GAP + message_h
