"""Phase 5d: TreeLayout geometry tests (TC-A20, TC-A21, TC-A22).

Coordinate-math only — no rendering. Tests verify node positions, edge connectivity,
tree shrinking behaviour, and sorted row slot positions for both presets.
"""

from __future__ import annotations

import itertools

import pytest
from pygame import Rect

from visualizer.views.tree_layout import TreeLayout

# ---------------------------------------------------------------------------
# Desktop preset  (panel_width=611, panel_height=297)
# ---------------------------------------------------------------------------

DESKTOP_RECT = Rect(19, 19, 611, 297)
DESKTOP_ARRAY_X_PADDING = int(611 * 0.05)  # 30
DESKTOP_SLOT_WIDTH = (611 - DESKTOP_ARRAY_X_PADDING * 2) / 7  # 551/7

HEADER_TOTAL = 78  # approximate, from doc 04 §4.1.1

# ---------------------------------------------------------------------------
# Tablet preset  (panel_width=489, panel_height=327)
# ---------------------------------------------------------------------------

TABLET_RECT = Rect(15, 15, 489, 327)
TABLET_ARRAY_X_PADDING = int(489 * 0.05)  # 24
TABLET_SLOT_WIDTH = (489 - TABLET_ARRAY_X_PADDING * 2) / 7  # 441/7


@pytest.fixture
def desktop() -> TreeLayout:
    return TreeLayout(DESKTOP_RECT, HEADER_TOTAL, DESKTOP_ARRAY_X_PADDING, DESKTOP_SLOT_WIDTH)


@pytest.fixture
def tablet() -> TreeLayout:
    return TreeLayout(TABLET_RECT, HEADER_TOTAL, TABLET_ARRAY_X_PADDING, TABLET_SLOT_WIDTH)


# ---------------------------------------------------------------------------
# Geometry invariants — Desktop
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_tree_area_height_positive_desktop(desktop: TreeLayout) -> None:
    assert desktop.tree_area_height > 0


@pytest.mark.unit
def test_tree_node_diameter_positive_desktop(desktop: TreeLayout) -> None:
    assert desktop.tree_node_diameter > 0


@pytest.mark.unit
def test_tree_node_diameter_at_most_quarter_area_desktop(desktop: TreeLayout) -> None:
    assert desktop.tree_node_diameter <= desktop.tree_area_height / 4


@pytest.mark.unit
def test_sorted_row_below_tree_desktop(desktop: TreeLayout) -> None:
    assert desktop.sorted_row_y > desktop.tree_top


@pytest.mark.unit
def test_tree_node_radius_is_int_desktop(desktop: TreeLayout) -> None:
    assert isinstance(desktop.tree_node_radius, int)


# ---------------------------------------------------------------------------
# TC-A20: Node Positioning — Desktop
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_tc_a20_all_nodes_within_panel_bounds_desktop(desktop: TreeLayout) -> None:
    positions = desktop.node_positions(7)
    assert len(positions) == 7
    for x, y in positions:
        assert DESKTOP_RECT.x <= x <= DESKTOP_RECT.right
        assert desktop.tree_top <= y <= desktop.sorted_row_y


@pytest.mark.unit
def test_tc_a20_root_centered_desktop(desktop: TreeLayout) -> None:
    positions = desktop.node_positions(7)
    root_x, _ = positions[0]
    assert abs(root_x - DESKTOP_RECT.centerx) <= 1.0


@pytest.mark.unit
def test_tc_a20_level1_symmetric_desktop(desktop: TreeLayout) -> None:
    positions = desktop.node_positions(7)
    center_x = DESKTOP_RECT.x + DESKTOP_RECT.width / 2
    dist_left = abs(center_x - positions[1][0])
    dist_right = abs(positions[2][0] - center_x)
    assert dist_left == pytest.approx(dist_right)


@pytest.mark.unit
def test_tc_a20_level2_symmetric_3_6_desktop(desktop: TreeLayout) -> None:
    positions = desktop.node_positions(7)
    center_x = DESKTOP_RECT.x + DESKTOP_RECT.width / 2
    dist_3 = abs(center_x - positions[3][0])
    dist_6 = abs(positions[6][0] - center_x)
    assert dist_3 == pytest.approx(dist_6)


@pytest.mark.unit
def test_tc_a20_level2_symmetric_4_5_desktop(desktop: TreeLayout) -> None:
    positions = desktop.node_positions(7)
    center_x = DESKTOP_RECT.x + DESKTOP_RECT.width / 2
    dist_4 = abs(center_x - positions[4][0])
    dist_5 = abs(positions[5][0] - center_x)
    assert dist_4 == pytest.approx(dist_5)


@pytest.mark.unit
def test_tc_a20_no_adjacent_overlap_level2_desktop(desktop: TreeLayout) -> None:
    positions = desktop.node_positions(7)
    level2 = [positions[i] for i in [3, 4, 5, 6]]
    for a, b in itertools.pairwise(level2):
        assert abs(b[0] - a[0]) >= desktop.tree_node_diameter


# ---------------------------------------------------------------------------
# TC-A20: Node Positioning — Tablet
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_tc_a20_all_nodes_within_panel_bounds_tablet(tablet: TreeLayout) -> None:
    positions = tablet.node_positions(7)
    assert len(positions) == 7
    for x, y in positions:
        assert TABLET_RECT.x <= x <= TABLET_RECT.right
        assert tablet.tree_top <= y <= tablet.sorted_row_y


@pytest.mark.unit
def test_tc_a20_root_centered_tablet(tablet: TreeLayout) -> None:
    positions = tablet.node_positions(7)
    root_x, _ = positions[0]
    assert abs(root_x - TABLET_RECT.centerx) <= 1.0


@pytest.mark.unit
def test_tc_a20_level1_symmetric_tablet(tablet: TreeLayout) -> None:
    positions = tablet.node_positions(7)
    center_x = TABLET_RECT.x + TABLET_RECT.width / 2
    dist_left = abs(center_x - positions[1][0])
    dist_right = abs(positions[2][0] - center_x)
    assert dist_left == pytest.approx(dist_right)


# ---------------------------------------------------------------------------
# TC-A21: Edge Connectivity
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_tc_a21_six_edges_for_heap7(desktop: TreeLayout) -> None:
    assert len(desktop.edges(7)) == 6


@pytest.mark.unit
def test_tc_a21_edge_parent_child_indices_heap7(desktop: TreeLayout) -> None:
    positions = desktop.node_positions(7)
    edges = desktop.edges(7)
    # Expected edges: i=1..6, parent=(i-1)//2
    expected = [(positions[(i - 1) // 2], positions[i]) for i in range(1, 7)]
    assert edges == expected


@pytest.mark.unit
def test_tc_a21_edge_endpoints_match_node_positions(desktop: TreeLayout) -> None:
    positions = desktop.node_positions(7)
    for parent_pos, child_pos in desktop.edges(7):
        assert parent_pos in positions
        assert child_pos in positions


@pytest.mark.unit
def test_tc_a21_leaf_nodes_not_in_outgoing_edges(desktop: TreeLayout) -> None:
    positions = desktop.node_positions(7)
    leaf_positions = {positions[i] for i in [3, 4, 5, 6]}
    parent_positions = {e[0] for e in desktop.edges(7)}
    assert leaf_positions.isdisjoint(parent_positions)


# ---------------------------------------------------------------------------
# TC-A22: Tree Shrinking
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize("heap_size", [7, 6, 5, 4, 3, 2, 1])
def test_tc_a22_node_count_equals_heap_size(desktop: TreeLayout, heap_size: int) -> None:
    assert len(desktop.node_positions(heap_size)) == heap_size


@pytest.mark.unit
@pytest.mark.parametrize("heap_size", [7, 6, 5, 4, 3, 2])
def test_tc_a22_edges_within_heap_size(desktop: TreeLayout, heap_size: int) -> None:
    positions = desktop.node_positions(heap_size)
    position_set = set(positions)
    for parent_pos, child_pos in desktop.edges(heap_size):
        assert parent_pos in position_set
        assert child_pos in position_set


@pytest.mark.unit
def test_tc_a22_heap_size_1_zero_edges(desktop: TreeLayout) -> None:
    assert desktop.edges(1) == []


@pytest.mark.unit
def test_tc_a22_heap_size_1_one_node(desktop: TreeLayout) -> None:
    positions = desktop.node_positions(1)
    assert len(positions) == 1


@pytest.mark.unit
def test_tc_a22_heap_size_1_root_at_tree_top(desktop: TreeLayout) -> None:
    positions = desktop.node_positions(1)
    _, y = positions[0]
    assert y == pytest.approx(desktop.tree_top)


@pytest.mark.unit
def test_tc_a22_heap_size_3_two_edges(desktop: TreeLayout) -> None:
    positions = desktop.node_positions(3)
    edges = desktop.edges(3)
    assert len(edges) == 2
    assert edges[0] == (positions[0], positions[1])
    assert edges[1] == (positions[0], positions[2])


@pytest.mark.unit
def test_tc_a22_heap_size_0_empty(desktop: TreeLayout) -> None:
    assert desktop.node_positions(0) == []
    assert desktop.edges(0) == []


# ---------------------------------------------------------------------------
# Sorted row positions
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_sorted_row_x_matches_flat_row_formula_desktop(desktop: TreeLayout) -> None:
    for slot in range(7):
        expected = (
            DESKTOP_RECT.x
            + DESKTOP_ARRAY_X_PADDING
            + slot * DESKTOP_SLOT_WIDTH
            + DESKTOP_SLOT_WIDTH / 2
        )
        assert desktop.sorted_row_x(slot) == pytest.approx(expected)


@pytest.mark.unit
def test_sorted_row_x_seven_distinct_positions(desktop: TreeLayout) -> None:
    xs = [desktop.sorted_row_x(i) for i in range(7)]
    assert len(set(xs)) == 7
