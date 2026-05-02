"""Unit tests for HeapSort generator — TC-A1, TC-A2, TC-A3, TC-A7, TC-A8, TC-A10, TC-A13, TC-A19."""

import pytest

from visualizer.models.contracts import OpType, SortResult
from visualizer.models.heap import HeapSort

# ---------------------------------------------------------------------------
# Helpers (TC-A7, TC-A8, TC-A13, TC-A19)
# ---------------------------------------------------------------------------


def _is_logical_tree_t3(tick: SortResult) -> bool:
    """Classify a T3 tick as Logical Tree (True) or Boundary (False).

    Uses message prefix per D-081. Do NOT use highlight_indices contiguity —
    Logical Tree T3 at parent=0 produces contiguous tuples (0, 1, 2) or (0, 1)
    that collide with Boundary T3 shape.
    """
    return tick.operation_type is OpType.RANGE and tick.message.startswith("Evaluating tree level")


def _is_max_heap(arr: list[int]) -> bool:
    """Return True iff arr satisfies the max-heap property."""
    n = len(arr)
    for i in range(n // 2):
        left = 2 * i + 1
        right = 2 * i + 2
        if left < n and arr[i] < arr[left]:
            return False
        if right < n and arr[i] < arr[right]:
            return False
    return True


def extract_sift_down_levels(ticks: list[SortResult]) -> list[list[SortResult]]:
    """Group ticks into sift-down levels, each starting with a Logical Tree T3."""
    levels: list[list[SortResult]] = []
    current_level: list[SortResult] = []
    for tick in ticks:
        if _is_logical_tree_t3(tick):
            if current_level:
                levels.append(current_level)
            current_level = [tick]
        elif current_level:
            current_level.append(tick)
            if tick.operation_type is OpType.SWAP:
                levels.append(current_level)
                current_level = []
    if current_level:
        levels.append(current_level)
    return levels


def assert_sift_down_level_contract(level_ticks: list[SortResult]) -> None:
    """Assert T3 -> T1{1,2} -> T2{0,1} ordering for a single sift-down level."""
    assert level_ticks[0].operation_type is OpType.RANGE, "Level must start with T3"
    assert _is_logical_tree_t3(level_ticks[0]), "Must be tree highlight, not boundary"

    compare_count = 0
    write_count = 0
    for tick in level_ticks[1:]:
        if tick.operation_type is OpType.COMPARE:
            assert write_count == 0, "T1 compare must not follow T2 write within same level"
            compare_count += 1
        elif tick.operation_type is OpType.SWAP:
            assert compare_count >= 1, "T2 write must follow at least one T1 compare"
            write_count += 1

    assert 1 <= compare_count <= 2, f"Expected 1-2 compares, got {compare_count}"
    assert write_count <= 1, f"Expected 0-1 writes, got {write_count}"


# ---------------------------------------------------------------------------
# TC-A1 — Final sortedness
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_tc_a1_final_sortedness(default_7: list[int]) -> None:
    sorter = HeapSort(default_7)
    ticks = list(sorter.sort_generator())
    terminal = next(t for t in ticks if t.operation_type is OpType.TERMINAL)
    assert terminal.array_state == [1, 2, 3, 4, 5, 6, 7]


# ---------------------------------------------------------------------------
# TC-A2 — Completion tick contract
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_tc_a2_completion_tick(default_7: list[int]) -> None:
    sorter = HeapSort(default_7)
    ticks = list(sorter.sort_generator())
    terminals = [t for t in ticks if t.operation_type is OpType.TERMINAL]
    assert len(terminals) == 1
    t = terminals[0]
    assert t.success is True
    assert t.is_complete is True
    assert t.highlight_indices == tuple(range(7))


# ---------------------------------------------------------------------------
# TC-A3 — Empty input
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_tc_a3_empty_input(empty_0: list[int]) -> None:
    sorter = HeapSort(empty_0)
    ticks = list(sorter.sort_generator())
    assert len(ticks) == 1
    assert ticks[0].success is False
    assert ticks[0].operation_type is OpType.FAILURE


# ---------------------------------------------------------------------------
# TC-A10 — Counter accuracy
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_tc_a10_counter_accuracy(default_7: list[int]) -> None:
    sorter = HeapSort(default_7)
    list(sorter.sort_generator())
    assert sorter.comparisons == 20
    assert sorter.writes == 30


# ---------------------------------------------------------------------------
# Single-element guard
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_single_element_terminal_only(single_1: list[int]) -> None:
    sorter = HeapSort(single_1)
    ticks = list(sorter.sort_generator())
    assert len(ticks) == 1
    assert ticks[0].operation_type is OpType.TERMINAL
    assert ticks[0].is_complete is True
    assert not any(t.operation_type in (OpType.COMPARE, OpType.SWAP, OpType.RANGE) for t in ticks)


# ---------------------------------------------------------------------------
# TC-A7 — Heap Sort phase contract
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_tc_a7_heap_phase_contract(default_7: list[int]) -> None:
    sorter = HeapSort(default_7)
    ticks = list(sorter.sort_generator())

    # Split at first boundary T3 — everything before it is Phase 1.
    first_boundary_idx = next(
        i
        for i, t in enumerate(ticks)
        if t.operation_type is OpType.RANGE and t.message.startswith("Active heap")
    )
    phase1_ticks = ticks[:first_boundary_idx]
    phase2_ticks = ticks[first_boundary_idx:]

    # Phase 1: at least one Logical Tree T3 and at least one T2 swap.
    logical_t3_p1 = [t for t in phase1_ticks if _is_logical_tree_t3(t)]
    swaps_p1 = [t for t in phase1_ticks if t.operation_type is OpType.SWAP]
    assert len(logical_t3_p1) >= 1, "Phase 1 must emit at least one Logical Tree T3"
    assert len(swaps_p1) >= 1, "Phase 1 must produce at least one T2 swap for default_7"

    # Phase 2: exactly 6 boundary T3 ticks with strictly decreasing k values.
    boundary_t3_p2 = [
        t
        for t in phase2_ticks
        if t.operation_type is OpType.RANGE and t.message.startswith("Active heap")
    ]
    assert len(boundary_t3_p2) == 6, "Phase 2 must emit exactly 6 boundary T3 ticks for n=7"

    k_values = [len(t.highlight_indices) for t in boundary_t3_p2 if t.highlight_indices is not None]
    assert len(k_values) == 6
    for i in range(len(k_values) - 1):
        assert k_values[i + 1] == k_values[i] - 1, (
            f"Boundary T3 k must decrease by 1: got {k_values[i]} -> {k_values[i + 1]}"
        )
    assert k_values[0] == 7
    assert k_values[-1] == 2

    # Phase 2: Logical Tree T3 ticks emitted during post-extraction sift-down repairs.
    logical_t3_p2 = [t for t in phase2_ticks if _is_logical_tree_t3(t)]
    assert len(logical_t3_p2) >= 1, "Phase 2 must emit at least one Logical Tree T3"


# ---------------------------------------------------------------------------
# TC-A8 — Sift-down correctness
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_tc_a8_sift_down_correctness(default_7: list[int]) -> None:
    sorter = HeapSort(default_7)
    ticks = list(sorter.sort_generator())

    # The tick immediately before the first boundary T3 is the last Phase 1 tick.
    # After all Phase 1 sift-downs complete, the array must satisfy max-heap.
    first_boundary_idx = next(
        i
        for i, t in enumerate(ticks)
        if t.operation_type is OpType.RANGE and t.message.startswith("Active heap")
    )
    last_phase1_tick = ticks[first_boundary_idx - 1]
    assert last_phase1_tick.array_state is not None
    assert _is_max_heap(last_phase1_tick.array_state), (
        "Array state immediately before Phase 2 must satisfy max-heap property"
    )

    # Final array is fully sorted (also TC-A1).
    terminal = next(t for t in ticks if t.operation_type is OpType.TERMINAL)
    assert terminal.array_state == sorted(default_7)


# ---------------------------------------------------------------------------
# TC-A13 — T3 step counter exclusion
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_tc_a13_t3_step_counter_exclusion(default_7: list[int]) -> None:
    sorter = HeapSort(default_7)
    ticks = list(sorter.sort_generator())

    # Steps: success=True, is_complete=False, op_type != RANGE.
    step_ticks = [
        t for t in ticks if t.success and not t.is_complete and t.operation_type is not OpType.RANGE
    ]
    assert len(step_ticks) == 35

    # T3 total: 6 boundary + 11 logical tree = 17.
    t3_ticks = [t for t in ticks if t.operation_type is OpType.RANGE]
    assert len(t3_ticks) == 17

    boundary_t3 = [t for t in t3_ticks if t.message.startswith("Active heap")]
    logical_t3 = [t for t in t3_ticks if t.message.startswith("Evaluating tree level")]
    assert len(boundary_t3) == 6
    assert len(logical_t3) == 11


# ---------------------------------------------------------------------------
# TC-A19 — Sift-down tick sequence contract (visual trace)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_tc_a19_sift_down_tick_sequence(default_7: list[int]) -> None:
    sorter = HeapSort(default_7)
    ticks = list(sorter.sort_generator())

    # D-058: parent must be the first element of every Logical Tree T3 highlight.
    # In a zero-indexed binary heap, child indices are always > parent index.
    for t in ticks:
        if _is_logical_tree_t3(t):
            assert t.highlight_indices is not None
            assert len(t.highlight_indices) >= 2, (
                "Logical Tree T3 must include at least (parent, left_child)"
            )
            parent = t.highlight_indices[0]
            for child in t.highlight_indices[1:]:
                assert child > parent, (
                    f"D-058: parent index {parent} must precede child index {child}"
                )

    # Each sift-down level must satisfy T3 -> T1{{1,2}} -> T2{{0,1}}.
    levels = extract_sift_down_levels(ticks)
    assert len(levels) == 11, (
        f"Expected 11 sift-down levels (4 Phase 1 + 7 Phase 2), got {len(levels)}"
    )

    for level in levels:
        assert_sift_down_level_contract(level)
