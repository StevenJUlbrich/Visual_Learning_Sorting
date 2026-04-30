"""Tree layout geometry for Heap Sort binary tree visualization.

Computes node positions, parent-child edge endpoints, and sorted row slot positions.
PURE GEOMETRY — no pygame.draw calls. All outputs are float coordinates or int radii.

See doc 04 §4.3.2 (tree layout formula), D-034 (float coordinates).
"""

from __future__ import annotations

import math

import pygame

# ---------------------------------------------------------------------------
# Constants (doc 04 §4.3.2)
# ---------------------------------------------------------------------------

SORTED_ROW_MARGIN_RATIO: float = 0.18
TREE_NODE_DIAMETER_RATIO: float = 0.55
TREE_HEADER_GAP: int = 10
TREE_SORTED_GAP: int = 20
EDGE_WIDTH: int = 2
DEFAULT_EDGE_COLOR: tuple[int, int, int] = (120, 120, 130)
ACTIVE_EDGE_COLOR: tuple[int, int, int] = (255, 140, 0)
PLACEHOLDER_COLOR: tuple[int, int, int] = (60, 60, 68)


class TreeLayout:
    """Computes Heap Sort binary tree node positions, edges, and sorted row slots.

    All x/y coordinates are floats (D-034). Constructable without a live display.
    """

    def __init__(
        self,
        panel_rect: pygame.Rect,
        header_total: int,
        array_x_padding: int,
        slot_width: float,
    ) -> None:
        self._panel_rect = panel_rect
        self._array_x_padding = array_x_padding
        self._slot_width = slot_width

        panel_height = panel_rect.height
        self.tree_top: float = panel_rect.y + header_total + TREE_HEADER_GAP
        self.sorted_row_y: float = (
            panel_rect.y + panel_height - int(panel_height * SORTED_ROW_MARGIN_RATIO)
        )
        self.tree_area_height: float = self.sorted_row_y - self.tree_top - TREE_SORTED_GAP
        self.tree_node_diameter: float = min(
            slot_width * TREE_NODE_DIAMETER_RATIO, self.tree_area_height / 4
        )

    @property
    def tree_node_radius(self) -> int:
        return int(self.tree_node_diameter) // 2

    def _level_y(self, depth: int, level_spacing: float) -> float:
        return self.tree_top + depth * level_spacing

    def node_positions(self, heap_size: int) -> list[tuple[float, float]]:
        """Return (x, y) for each tree node at index 0..heap_size-1."""
        if heap_size <= 0:
            return []

        panel_rect = self._panel_rect
        array_x_padding = self._array_x_padding
        usable_width = float(panel_rect.width - 2 * array_x_padding)

        max_depth = math.floor(math.log2(heap_size))
        level_spacing = self.tree_area_height / max_depth if max_depth > 0 else 0.0

        positions: list[tuple[float, float]] = []
        for i in range(heap_size):
            depth = math.floor(math.log2(i + 1))
            position_in_level = i - (2**depth - 1)
            total_at_level = 2**depth
            x = (
                panel_rect.x
                + array_x_padding
                + (position_in_level + 0.5) * usable_width / total_at_level
            )
            y = self._level_y(depth, level_spacing)
            positions.append((x, y))
        return positions

    def edges(self, heap_size: int) -> list[tuple[tuple[float, float], tuple[float, float]]]:
        """Return ((parent_x, parent_y), (child_x, child_y)) for all edges within heap_size."""
        if heap_size <= 1:
            return []

        positions = self.node_positions(heap_size)
        result: list[tuple[tuple[float, float], tuple[float, float]]] = []
        for i in range(1, heap_size):
            parent_index = (i - 1) // 2
            result.append((positions[parent_index], positions[i]))
        return result

    def sorted_row_x(self, slot_index: int) -> float:
        """Horizontal center for a sorted-row slot (same formula as flat-row panels)."""
        return (
            self._panel_rect.x
            + self._array_x_padding
            + slot_index * self._slot_width
            + self._slot_width / 2
        )
