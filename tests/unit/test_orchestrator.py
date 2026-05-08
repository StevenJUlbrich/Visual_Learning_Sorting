"""Phase 6a/6b: PanelState, duration constants, PanelContext, and Orchestrator tests."""

from __future__ import annotations

from collections.abc import Generator

import pytest

from visualizer.controllers.orchestrator import (
    FAILURE_DURATION,
    SIFT_DOWN_T1_DURATION,
    SIFT_DOWN_T2_DURATION,
    SIFT_DOWN_T3_DURATION,
    T1_COMPARE_DURATION,
    T2_WRITE_DURATION,
    T3_RANGE_DURATION,
    TERMINAL_DURATION,
    Orchestrator,
    PanelContext,
    PanelState,
    compute_sprite_moves,
    get_duration,
)
from visualizer.models.contracts import BaseSortAlgorithm, OpType, SortResult

# ---------------------------------------------------------------------------
# PanelState enum
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_panel_state_has_five_members() -> None:
    assert len(PanelState) == 5


@pytest.mark.unit
def test_panel_state_idle_paused_exists() -> None:
    assert PanelState.IDLE_PAUSED is not None


@pytest.mark.unit
def test_panel_state_all_values_unique() -> None:
    assert len({s.value for s in PanelState}) == 5


# ---------------------------------------------------------------------------
# Standard duration constants
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_t1_compare_duration() -> None:
    assert T1_COMPARE_DURATION == 150


@pytest.mark.unit
def test_t2_write_duration() -> None:
    assert T2_WRITE_DURATION == 400


@pytest.mark.unit
def test_t3_range_duration() -> None:
    assert T3_RANGE_DURATION == 200


@pytest.mark.unit
def test_terminal_duration_zero() -> None:
    assert TERMINAL_DURATION == 0


@pytest.mark.unit
def test_failure_duration_zero() -> None:
    assert FAILURE_DURATION == 0


# ---------------------------------------------------------------------------
# Sift-down cadence constants
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_sift_down_t1() -> None:
    assert SIFT_DOWN_T1_DURATION == 100


@pytest.mark.unit
def test_sift_down_t2() -> None:
    assert SIFT_DOWN_T2_DURATION == 250


@pytest.mark.unit
def test_sift_down_t3() -> None:
    assert SIFT_DOWN_T3_DURATION == 130


# ---------------------------------------------------------------------------
# get_duration function
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_get_duration_compare_standard() -> None:
    assert get_duration(OpType.COMPARE, False) == 150


@pytest.mark.unit
def test_get_duration_compare_cadence() -> None:
    assert get_duration(OpType.COMPARE, True) == 100


@pytest.mark.unit
def test_get_duration_swap_standard() -> None:
    assert get_duration(OpType.SWAP, False) == 400


@pytest.mark.unit
def test_get_duration_swap_cadence() -> None:
    assert get_duration(OpType.SWAP, True) == 250


@pytest.mark.unit
def test_get_duration_shift_always_standard() -> None:
    assert get_duration(OpType.SHIFT, True) == 400


@pytest.mark.unit
def test_get_duration_range_standard() -> None:
    assert get_duration(OpType.RANGE, False) == 200


@pytest.mark.unit
def test_get_duration_range_cadence() -> None:
    assert get_duration(OpType.RANGE, True) == 130


@pytest.mark.unit
def test_get_duration_terminal() -> None:
    assert get_duration(OpType.TERMINAL, False) == 0


@pytest.mark.unit
def test_get_duration_failure() -> None:
    assert get_duration(OpType.FAILURE, False) == 0


# ---------------------------------------------------------------------------
# PanelContext
# ---------------------------------------------------------------------------


@pytest.fixture
def ctx() -> PanelContext:
    return PanelContext("Bubble Sort", "O(n²)", 7)


@pytest.mark.unit
def test_panel_context_initial_state(ctx: PanelContext) -> None:
    assert ctx.state == PanelState.IDLE_PAUSED


@pytest.mark.unit
def test_panel_context_initial_timing(ctx: PanelContext) -> None:
    assert ctx.elapsed_time_ms == 0
    assert ctx.current_operation_remaining_ms == 0


@pytest.mark.unit
def test_panel_context_initial_counters(ctx: PanelContext) -> None:
    assert ctx.step_count == 0
    assert ctx.comparisons == 0
    assert ctx.writes == 0


@pytest.mark.unit
def test_panel_context_initial_cadence_false(ctx: PanelContext) -> None:
    assert ctx.sift_down_cadence is False


@pytest.mark.unit
def test_panel_context_initial_is_active(ctx: PanelContext) -> None:
    assert ctx.is_active is True


@pytest.mark.unit
def test_panel_context_stores_name_and_complexity(ctx: PanelContext) -> None:
    assert ctx.algorithm_name == "Bubble Sort"
    assert ctx.complexity == "O(n²)"


@pytest.mark.unit
def test_panel_context_reset_restores_defaults(ctx: PanelContext) -> None:
    ctx.state = PanelState.COMPLETED
    ctx.elapsed_time_ms = 3200
    ctx.current_operation_remaining_ms = 150
    ctx.step_count = 20
    ctx.comparisons = 20
    ctx.writes = 26
    ctx.sift_down_cadence = True
    ctx.is_active = False
    ctx.reset()
    assert ctx.state == PanelState.IDLE_PAUSED
    assert ctx.elapsed_time_ms == 0
    assert ctx.current_operation_remaining_ms == 0
    assert ctx.step_count == 0
    assert ctx.comparisons == 0
    assert ctx.writes == 0
    assert ctx.sift_down_cadence is False
    assert ctx.is_active is True


@pytest.mark.unit
def test_panel_context_reset_preserves_identity(ctx: PanelContext) -> None:
    ctx.reset()
    assert ctx.algorithm_name == "Bubble Sort"
    assert ctx.complexity == "O(n²)"


# ---------------------------------------------------------------------------
# Phase 6b helpers
# ---------------------------------------------------------------------------


class MockAlgorithm(BaseSortAlgorithm):
    """Test helper: algorithm with a predetermined tick sequence."""

    def __init__(
        self,
        ticks: list[SortResult],
        name: str = "Mock Sort",
        complexity: str = "O(1)",
        data: list[int] | None = None,
    ) -> None:
        super().__init__(data or [1, 2, 3], name, complexity)
        self._ticks = ticks

    def sort_generator(self) -> Generator[SortResult]:
        yield from self._ticks


def _progress_tick(
    op_type: OpType,
    array_state: list[int] | None = None,
    highlight: tuple[int, ...] | None = None,
    message: str = "test",
) -> SortResult:
    return SortResult(
        success=True,
        message=message,
        operation_type=op_type,
        array_state=array_state or [1, 2, 3],
        highlight_indices=highlight,
    )


def _terminal_tick() -> SortResult:
    return SortResult(
        success=True,
        message="Sort complete",
        operation_type=OpType.TERMINAL,
        is_complete=True,
        array_state=[1, 2, 3],
        highlight_indices=(0, 1, 2),
    )


def _failure_tick() -> SortResult:
    return SortResult(
        success=False,
        message="Error",
        operation_type=OpType.FAILURE,
    )


# ---------------------------------------------------------------------------
# Group 6 — Orchestrator construction
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_orchestrator_creates_panels_per_algorithm() -> None:
    algos = [MockAlgorithm([_terminal_tick()]), MockAlgorithm([_terminal_tick()])]
    orch = Orchestrator(algos, [1, 2, 3])
    assert len(orch.panels) == 2


@pytest.mark.unit
def test_orchestrator_all_panels_start_idle() -> None:
    algos = [MockAlgorithm([_terminal_tick()]), MockAlgorithm([_terminal_tick()])]
    orch = Orchestrator(algos, [1, 2, 3])
    assert all(p.state == PanelState.IDLE_PAUSED for p in orch.panels)


# ---------------------------------------------------------------------------
# Group 7 — State machine transitions
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_update_skips_idle_paused() -> None:
    mock = MockAlgorithm([_progress_tick(OpType.COMPARE), _terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    orch.update(16)
    assert orch.panels[0].state == PanelState.IDLE_PAUSED


@pytest.mark.unit
def test_waiting_fetches_tick_transitions_to_animating() -> None:
    mock = MockAlgorithm([_progress_tick(OpType.COMPARE), _terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    orch.play()
    orch.update(1)
    assert orch.panels[0].state == PanelState.ANIMATING_OPERATION


@pytest.mark.unit
def test_animating_decrements_remaining() -> None:
    mock = MockAlgorithm([_progress_tick(OpType.COMPARE), _terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    orch.play()
    ctx = orch.panels[0]
    ctx.state = PanelState.ANIMATING_OPERATION
    ctx.current_operation_remaining_ms = 150
    orch.update(50)
    assert ctx.current_operation_remaining_ms == 100


@pytest.mark.unit
def test_animating_to_waiting_when_remaining_zero() -> None:
    mock = MockAlgorithm([_progress_tick(OpType.COMPARE), _terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    orch.play()
    ctx = orch.panels[0]
    ctx.state = PanelState.ANIMATING_OPERATION
    ctx.current_operation_remaining_ms = 33
    orch.update(33)
    assert ctx.state == PanelState.WAITING_FOR_NEXT_TICK


@pytest.mark.unit
def test_animating_to_waiting_on_overshoot() -> None:
    mock = MockAlgorithm([_progress_tick(OpType.COMPARE), _terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    orch.play()
    ctx = orch.panels[0]
    ctx.state = PanelState.ANIMATING_OPERATION
    ctx.current_operation_remaining_ms = 33
    orch.update(50)
    assert ctx.state == PanelState.WAITING_FOR_NEXT_TICK


@pytest.mark.unit
def test_terminal_tick_transitions_to_completed() -> None:
    mock = MockAlgorithm([_terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    ctx = orch.panels[0]
    orch.play()
    orch.update(1)
    assert ctx.state == PanelState.COMPLETED
    assert ctx.is_active is False


@pytest.mark.unit
def test_failure_tick_transitions_to_failed() -> None:
    mock = MockAlgorithm([_failure_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    ctx = orch.panels[0]
    orch.play()
    orch.update(1)
    assert ctx.state == PanelState.FAILED
    assert ctx.is_active is False


@pytest.mark.unit
def test_completed_panel_skipped() -> None:
    mock = MockAlgorithm([_terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    ctx = orch.panels[0]
    ctx.state = PanelState.COMPLETED
    ctx.is_active = False
    orch.update(16)
    assert ctx.state == PanelState.COMPLETED


# ---------------------------------------------------------------------------
# Group 8 — Elapsed time (integer arithmetic, TC-A4)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_elapsed_time_accumulates_compare_duration() -> None:
    mock = MockAlgorithm([_progress_tick(OpType.COMPARE), _terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    ctx = orch.panels[0]
    orch.play()
    orch.update(1)  # fetch compare → elapsed += 150
    assert ctx.elapsed_time_ms == 150


@pytest.mark.unit
def test_elapsed_time_accumulates_multiple_ticks() -> None:
    ticks = [
        _progress_tick(OpType.COMPARE),
        _progress_tick(OpType.COMPARE),
        _progress_tick(OpType.SWAP),
        _terminal_tick(),
    ]
    mock = MockAlgorithm(ticks)
    orch = Orchestrator([mock], [1, 2, 3])
    ctx = orch.panels[0]
    orch.play()
    orch.update(1)  # fetch compare → elapsed=150
    assert ctx.elapsed_time_ms == 150
    orch.update(200)  # drain → WAITING
    orch.update(1)  # fetch compare → elapsed=300
    assert ctx.elapsed_time_ms == 300
    orch.update(200)  # drain → WAITING
    orch.update(1)  # fetch swap → elapsed=700
    assert ctx.elapsed_time_ms == 700


@pytest.mark.unit
def test_elapsed_time_freezes_on_completion() -> None:
    mock = MockAlgorithm([_progress_tick(OpType.COMPARE), _terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    ctx = orch.panels[0]
    orch.play()
    orch.update(1)  # fetch compare → elapsed=150
    orch.update(200)  # drain → WAITING
    orch.update(1)  # fetch terminal → COMPLETED
    assert ctx.elapsed_time_ms == 150
    orch.update(1000)  # panel inactive — skipped
    assert ctx.elapsed_time_ms == 150


@pytest.mark.unit
def test_elapsed_time_freezes_on_failure() -> None:
    mock = MockAlgorithm([_progress_tick(OpType.COMPARE), _failure_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    ctx = orch.panels[0]
    orch.play()
    orch.update(1)  # fetch compare → elapsed=150
    orch.update(200)  # drain → WAITING
    orch.update(1)  # fetch failure → FAILED
    assert ctx.elapsed_time_ms == 150
    orch.update(1000)  # panel inactive — skipped
    assert ctx.elapsed_time_ms == 150


# ---------------------------------------------------------------------------
# Group 9 — Step counter (D-041)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_step_increments_on_compare() -> None:
    mock = MockAlgorithm([_progress_tick(OpType.COMPARE), _terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    ctx = orch.panels[0]
    orch.play()
    orch.update(1)
    assert ctx.step_count == 1


@pytest.mark.unit
def test_step_increments_on_swap() -> None:
    mock = MockAlgorithm([_progress_tick(OpType.SWAP), _terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    ctx = orch.panels[0]
    orch.play()
    orch.update(1)
    assert ctx.step_count == 1


@pytest.mark.unit
def test_step_excludes_range() -> None:
    mock = MockAlgorithm([_progress_tick(OpType.RANGE), _terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    ctx = orch.panels[0]
    orch.play()
    orch.update(1)
    assert ctx.step_count == 0


@pytest.mark.unit
def test_step_excludes_terminal() -> None:
    mock = MockAlgorithm([_terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    ctx = orch.panels[0]
    orch.play()
    orch.update(1)
    assert ctx.step_count == 0


# ---------------------------------------------------------------------------
# Group 10 — Counter sync from algorithm instance
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_comparisons_synced_from_algorithm() -> None:
    mock = MockAlgorithm([_progress_tick(OpType.COMPARE), _terminal_tick()])
    mock.comparisons = 5
    orch = Orchestrator([mock], [1, 2, 3])
    ctx = orch.panels[0]
    orch.play()
    orch.update(1)
    assert ctx.comparisons == 5


@pytest.mark.unit
def test_writes_synced_from_algorithm() -> None:
    mock = MockAlgorithm([_progress_tick(OpType.SWAP), _terminal_tick()])
    mock.writes = 7
    orch = Orchestrator([mock], [1, 2, 3])
    ctx = orch.panels[0]
    orch.play()
    orch.update(1)
    assert ctx.writes == 7


# ---------------------------------------------------------------------------
# Group 11 — Sift-down cadence lifecycle (Heap Sort)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_cadence_initially_false() -> None:
    mock = MockAlgorithm([_terminal_tick()], name="Heap Sort")
    orch = Orchestrator([mock], [1, 2, 3])
    assert orch.panels[0].sift_down_cadence is False


@pytest.mark.unit
def test_boundary_t3_sets_extraction_pending() -> None:
    boundary = _progress_tick(OpType.RANGE, message="Active heap region: 0-6")
    mock = MockAlgorithm([boundary, _terminal_tick()], name="Heap Sort")
    orch = Orchestrator([mock], [1, 2, 3])
    ctx = orch.panels[0]
    orch.play()
    orch.update(1)  # fetch boundary T3
    assert ctx.extraction_pending is True
    assert ctx.sift_down_cadence is False


@pytest.mark.unit
def test_swap_after_boundary_sets_cadence() -> None:
    ticks = [
        _progress_tick(OpType.RANGE, message="Active heap region: 0-5"),
        _progress_tick(OpType.SWAP),
        _terminal_tick(),
    ]
    mock = MockAlgorithm(ticks, name="Heap Sort")
    orch = Orchestrator([mock], [1, 2, 3])
    ctx = orch.panels[0]
    orch.play()
    orch.update(1)  # fetch boundary T3 → extraction_pending=True
    orch.update(500)  # drain → WAITING
    orch.update(1)  # fetch swap → cadence=True, extraction_pending=False
    assert ctx.sift_down_cadence is True
    assert ctx.extraction_pending is False


@pytest.mark.unit
def test_next_boundary_resets_cadence() -> None:
    ticks = [
        _progress_tick(OpType.RANGE, message="Active heap region: 0-5"),
        _progress_tick(OpType.SWAP),
        _progress_tick(OpType.COMPARE),
        _progress_tick(OpType.RANGE, message="Active heap region: 0-4"),
        _terminal_tick(),
    ]
    mock = MockAlgorithm(ticks, name="Heap Sort")
    orch = Orchestrator([mock], [1, 2, 3])
    ctx = orch.panels[0]
    orch.play()
    orch.update(1)  # fetch boundary T3 → extraction_pending=True
    orch.update(500)  # drain
    orch.update(1)  # fetch swap → cadence=True
    orch.update(500)  # drain
    orch.update(1)  # fetch compare (cadence active → 100ms)
    orch.update(500)  # drain
    orch.update(1)  # fetch second boundary T3 → cadence=False
    assert ctx.sift_down_cadence is False


@pytest.mark.unit
def test_cadence_not_set_during_phase1() -> None:
    ticks = [
        _progress_tick(OpType.RANGE, message="Evaluating tree level 0"),
        _progress_tick(OpType.COMPARE),
        _progress_tick(OpType.SWAP),
        _terminal_tick(),
    ]
    mock = MockAlgorithm(ticks, name="Heap Sort")
    orch = Orchestrator([mock], [1, 2, 3])
    ctx = orch.panels[0]
    orch.play()
    orch.update(1)  # fetch logical-tree T3 (no extraction_pending set)
    orch.update(500)  # drain
    orch.update(1)  # fetch compare
    orch.update(500)  # drain
    orch.update(1)  # fetch swap (extraction_pending=False → cadence stays False)
    assert ctx.sift_down_cadence is False


@pytest.mark.unit
def test_cadence_affects_duration_of_subsequent_ticks() -> None:
    ticks = [
        _progress_tick(OpType.RANGE, message="Active heap region: 0-5"),
        _progress_tick(OpType.SWAP),
        _progress_tick(OpType.COMPARE),
        _terminal_tick(),
    ]
    mock = MockAlgorithm(ticks, name="Heap Sort")
    orch = Orchestrator([mock], [1, 2, 3])
    ctx = orch.panels[0]
    orch.play()
    orch.update(1)  # fetch boundary T3 → 200ms, extraction_pending=True
    orch.update(500)  # drain → WAITING
    orch.update(1)  # fetch swap → 400ms (cadence False at call), cadence=True
    orch.update(500)  # drain → WAITING
    orch.update(1)  # fetch compare → cadence=True → 100ms
    assert ctx.current_operation_remaining_ms == 100


# ---------------------------------------------------------------------------
# Group 12 — Failure isolation
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_failure_isolation_other_panels_continue() -> None:
    mock_fail = MockAlgorithm([_failure_tick()], name="Mock Fail")
    mock_ok = MockAlgorithm([_progress_tick(OpType.COMPARE), _terminal_tick()], name="Mock OK")
    orch = Orchestrator([mock_fail, mock_ok], [1, 2, 3])
    ctx_fail = orch.panels[0]
    ctx_ok = orch.panels[1]
    orch.play()
    orch.update(1)  # fail→FAILED, ok→ANIMATING
    assert ctx_fail.state == PanelState.FAILED
    assert ctx_ok.state == PanelState.ANIMATING_OPERATION
    orch.update(200)  # ok drains → WAITING
    orch.update(1)  # ok fetches terminal → COMPLETED
    assert ctx_fail.state == PanelState.FAILED
    assert ctx_ok.state == PanelState.COMPLETED


# ---------------------------------------------------------------------------
# Group 13 — compute_sprite_moves unit tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_no_change_returns_empty_dict() -> None:
    slot_mapping = [0, 1, 2]
    result = compute_sprite_moves([1, 2, 3], [1, 2, 3], slot_mapping)
    assert result == {}
    assert slot_mapping == [0, 1, 2]


@pytest.mark.unit
def test_swap_two_adjacent_indices() -> None:
    # Swap indices 1 and 2: [4,7,2] → [4,2,7]
    old_state = [4, 7, 2, 6, 1, 5, 3]
    new_state = [4, 2, 7, 6, 1, 5, 3]
    slot_mapping = list(range(7))
    result = compute_sprite_moves(old_state, new_state, slot_mapping)
    assert result == {1: 2, 2: 1}
    assert slot_mapping == [0, 2, 1, 3, 4, 5, 6]


@pytest.mark.unit
def test_swap_non_adjacent_indices() -> None:
    # Swap indices 0 and 5: [4,...,5,...] → [5,...,4,...]
    old_state = [4, 7, 2, 6, 1, 5, 3]
    new_state = [5, 7, 2, 6, 1, 4, 3]
    slot_mapping = list(range(7))
    result = compute_sprite_moves(old_state, new_state, slot_mapping)
    assert result == {0: 5, 5: 0}
    assert slot_mapping == [5, 1, 2, 3, 4, 0, 6]


@pytest.mark.unit
def test_shift_single_element_rightward() -> None:
    # Rightward shift: arr[3] = arr[2] (value 5 at index 2 copied to index 3)
    old_state = [1, 2, 5, 3, 4]
    new_state = [1, 2, 5, 5, 4]  # only index 3 changed: 3 → 5
    slot_mapping = list(range(5))
    result = compute_sprite_moves(old_state, new_state, slot_mapping)
    assert result == {2: 3, 3: 2}
    assert slot_mapping == [0, 1, 3, 2, 4]


@pytest.mark.unit
def test_sequential_swaps_cumulative_mapping() -> None:
    # First swap: indices 0,1 → [2,1,3]
    slot_mapping = [0, 1, 2]
    compute_sprite_moves([1, 2, 3], [2, 1, 3], slot_mapping)
    assert slot_mapping == [1, 0, 2]
    # Second swap: indices 1,2 → [2,3,1]
    compute_sprite_moves([2, 1, 3], [2, 3, 1], slot_mapping)
    assert slot_mapping == [1, 2, 0]


@pytest.mark.unit
def test_full_sort_identity_preserved() -> None:
    from visualizer.models.bubble import BubbleSort

    algo = BubbleSort([4, 7, 2, 6, 1, 5, 3])
    slot_mapping = list(range(7))
    prev = [4, 7, 2, 6, 1, 5, 3]
    for tick in algo.sort_generator():
        if tick.array_state is not None:
            compute_sprite_moves(prev, tick.array_state, slot_mapping)
            prev = tick.array_state
    assert sorted(slot_mapping) == list(range(7))
    assert len(set(slot_mapping)) == 7


@pytest.mark.unit
def test_slot_to_sprite_id_mutated_in_place() -> None:
    slot_mapping = [0, 1, 2]
    original_id = id(slot_mapping)
    compute_sprite_moves([1, 2, 3], [2, 1, 3], slot_mapping)
    assert id(slot_mapping) == original_id


@pytest.mark.unit
def test_shift_duplicate_values_detected() -> None:
    """When a shift copies value X to a slot already holding X, changed is empty.
    The function must use highlight_indices to detect the movement."""
    # Simulates: arr[2] = arr[1] where both hold value 3.
    # old_state and new_state are identical — value delta is empty.
    old_state = [1, 3, 3, 3, 1, 2, 3]
    new_state = [1, 3, 3, 3, 1, 2, 3]  # identical
    slot_mapping = [0, 1, 2, 3, 4, 5, 6]
    result = compute_sprite_moves(
        old_state,
        new_state,
        slot_mapping,
        operation_type=OpType.SHIFT,
        highlight_indices=(1, 2),
    )
    # Sprite at slot 1 moves to slot 2, sprite at slot 2 moves to slot 1.
    assert result == {1: 2, 2: 1}
    assert slot_mapping == [0, 2, 1, 3, 4, 5, 6]


@pytest.mark.unit
def test_swap_duplicate_values_detected() -> None:
    """When a swap exchanges two equal values, changed is empty.
    The function must use highlight_indices to detect the movement."""
    # Simulates: heap extraction swap of arr[0] and arr[2] where both hold 3.
    old_state = [3, 1, 3]
    new_state = [3, 1, 3]  # identical
    slot_mapping = [0, 1, 2]
    result = compute_sprite_moves(
        old_state,
        new_state,
        slot_mapping,
        operation_type=OpType.SWAP,
        highlight_indices=(0, 2),
    )
    assert result == {0: 2, 2: 0}
    assert slot_mapping == [2, 1, 0]


@pytest.mark.unit
def test_placement_duplicate_value_no_spurious_move() -> None:
    """Placement tick where key value equals the value already in the target slot.
    old_state and new_state are identical (key=3 placed into slot already holding 3).
    highlight_indices has 1 element (placement slot). The fallback must NOT fire
    because len(highlight_indices) != 2."""
    old_state = [1, 3, 3, 3, 1, 2, 3]
    new_state = [1, 3, 3, 3, 1, 2, 3]  # identical — placement of same value
    slot_mapping = [0, 1, 2, 3, 4, 5, 6]
    result = compute_sprite_moves(
        old_state,
        new_state,
        slot_mapping,
        operation_type=OpType.SHIFT,
        highlight_indices=(1,),  # single-element: placement
    )
    # changed is empty, highlight has 1 element -> guard rejects -> returns {}
    assert result == {}
    assert slot_mapping == [0, 1, 2, 3, 4, 5, 6]  # unchanged


@pytest.mark.unit
def test_full_sort_duplicates_identity_preserved() -> None:
    """Run Insertion Sort on a duplicate-heavy array. Every sprite ID must appear
    exactly once in the final slot_mapping."""
    from visualizer.models.insertion import InsertionSort

    arr = [3, 1, 3, 2, 1, 2, 3]
    algo = InsertionSort(list(arr))
    slot_mapping = list(range(len(arr)))
    prev = list(arr)
    for tick in algo.sort_generator():
        if tick.array_state is not None:
            compute_sprite_moves(
                prev,
                tick.array_state,
                slot_mapping,
                operation_type=tick.operation_type,
                highlight_indices=tick.highlight_indices,
            )
            prev = tick.array_state
    # All 7 sprite IDs present exactly once
    assert sorted(slot_mapping) == list(range(len(arr)))
    assert len(set(slot_mapping)) == len(arr)


@pytest.mark.unit
def test_full_sort_bubble_duplicates_identity_preserved() -> None:
    """Run Bubble Sort on a duplicate-heavy array. Every sprite ID must appear
    exactly once in the final slot_mapping."""
    from visualizer.models.bubble import BubbleSort

    arr = [3, 1, 3, 2, 1, 2, 3]
    algo = BubbleSort(list(arr))
    slot_mapping = list(range(len(arr)))
    prev = list(arr)
    for tick in algo.sort_generator():
        if tick.array_state is not None:
            compute_sprite_moves(
                prev,
                tick.array_state,
                slot_mapping,
                operation_type=tick.operation_type,
                highlight_indices=tick.highlight_indices,
            )
            prev = tick.array_state
    assert sorted(slot_mapping) == list(range(len(arr)))
    assert len(set(slot_mapping)) == len(arr)


@pytest.mark.unit
def test_full_sort_heap_duplicates_identity_preserved() -> None:
    """Run Heap Sort on a duplicate-heavy array. Every sprite ID must appear
    exactly once in the final slot_mapping."""
    from visualizer.models.heap import HeapSort

    arr = [3, 1, 3, 2, 1, 2, 3]
    algo = HeapSort(list(arr))
    slot_mapping = list(range(len(arr)))
    prev = list(arr)
    for tick in algo.sort_generator():
        if tick.array_state is not None:
            compute_sprite_moves(
                prev,
                tick.array_state,
                slot_mapping,
                operation_type=tick.operation_type,
                highlight_indices=tick.highlight_indices,
            )
            prev = tick.array_state
    assert sorted(slot_mapping) == list(range(len(arr)))
    assert len(set(slot_mapping)) == len(arr)


# ---------------------------------------------------------------------------
# Group 14 — PanelContext new fields
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_context_has_slot_mapping() -> None:
    ctx = PanelContext("Test", "O(n)", 7)
    assert ctx.slot_to_sprite_id == list(range(7))


@pytest.mark.unit
def test_context_has_sprite_moves() -> None:
    ctx = PanelContext("Test", "O(n)", 7)
    assert ctx.sprite_moves == {}


@pytest.mark.unit
def test_context_reset_restores_slot_mapping() -> None:
    ctx = PanelContext("Test", "O(n)", 3)
    ctx.slot_to_sprite_id = [2, 0, 1]
    ctx.reset()
    assert ctx.slot_to_sprite_id == [0, 1, 2]


@pytest.mark.unit
def test_context_reset_clears_sprite_moves() -> None:
    ctx = PanelContext("Test", "O(n)", 3)
    ctx.sprite_moves = {0: 2, 2: 0}
    ctx.reset()
    assert ctx.sprite_moves == {}


# ---------------------------------------------------------------------------
# Group 15 — Integration with update(dt)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_swap_tick_populates_sprite_moves() -> None:
    # SWAP: indices 0 and 1 exchange in a 3-element array
    swap_tick = SortResult(
        success=True,
        message="swap",
        operation_type=OpType.SWAP,
        array_state=[2, 1, 3],
        highlight_indices=(0, 1),
    )
    mock = MockAlgorithm([swap_tick, _terminal_tick()], data=[1, 2, 3])
    orch = Orchestrator([mock], [1, 2, 3])
    ctx = orch.panels[0]
    orch.play()
    orch.update(1)
    assert len(ctx.sprite_moves) == 2
    assert ctx.sprite_moves[0] == 1
    assert ctx.sprite_moves[1] == 0


@pytest.mark.unit
def test_range_tick_empty_sprite_moves() -> None:
    # RANGE tick has same array_state as previous → no delta
    range_tick = _progress_tick(OpType.RANGE, array_state=[1, 2, 3])
    mock = MockAlgorithm([range_tick, _terminal_tick()], data=[1, 2, 3])
    orch = Orchestrator([mock], [1, 2, 3])
    ctx = orch.panels[0]
    orch.play()
    orch.update(1)
    assert ctx.sprite_moves == {}


@pytest.mark.unit
def test_terminal_tick_no_sprite_moves() -> None:
    mock = MockAlgorithm([_terminal_tick()], data=[1, 2, 3])
    orch = Orchestrator([mock], [1, 2, 3])
    ctx = orch.panels[0]
    orch.play()
    orch.update(1)
    assert ctx.sprite_moves == {}


@pytest.mark.unit
def test_failure_tick_no_sprite_moves() -> None:
    mock = MockAlgorithm([_failure_tick()], data=[1, 2, 3])
    orch = Orchestrator([mock], [1, 2, 3])
    ctx = orch.panels[0]
    orch.play()
    orch.update(1)
    assert ctx.sprite_moves == {}


@pytest.mark.unit
def test_sprite_moves_reflects_only_current_tick() -> None:
    # Two SWAP ticks: second tick's moves should not accumulate first tick's moves
    tick1 = SortResult(
        success=True,
        message="swap1",
        operation_type=OpType.SWAP,
        array_state=[2, 1, 3],
        highlight_indices=(0, 1),
    )
    tick2 = SortResult(
        success=True,
        message="swap2",
        operation_type=OpType.SWAP,
        array_state=[2, 3, 1],
        highlight_indices=(1, 2),
    )
    mock = MockAlgorithm([tick1, tick2, _terminal_tick()], data=[1, 2, 3])
    orch = Orchestrator([mock], [1, 2, 3])
    ctx = orch.panels[0]
    orch.play()
    orch.update(1)  # fetch tick1 → sprite_moves for indices 0,1
    orch.update(500)  # drain
    orch.update(1)  # fetch tick2 → sprite_moves for indices 1,2 only
    # After tick2: slot_mapping is [1, 2, 0] (cumulative)
    # tick2 delta: old=[2,1,3] new=[2,3,1] → changed indices 1,2
    # sprite at slot 1 in current mapping = slot_mapping[1] = 2 (sprite 2 from tick1 exchange)
    # sprite at slot 2 in current mapping = slot_mapping[2] = 0 (sprite 0, unchanged from tick1)
    # So sprite_moves = {2: 2, 0: 1}  ← only 2 entries, not 4
    assert len(ctx.sprite_moves) == 2


# ---------------------------------------------------------------------------
# Phase 6d helpers
# ---------------------------------------------------------------------------


class SimpleAlgorithm(BaseSortAlgorithm):
    """Minimal concrete algorithm for restart tests — takes only data."""

    def __init__(self, data: list[int]) -> None:
        super().__init__(data, "Simple Sort", "O(n)")

    def sort_generator(self) -> Generator[SortResult]:
        yield SortResult(
            success=True,
            message="compare",
            operation_type=OpType.COMPARE,
            array_state=list(self.data),
        )
        yield SortResult(
            success=True,
            message="done",
            operation_type=OpType.TERMINAL,
            is_complete=True,
            array_state=list(self.data),
        )


# ---------------------------------------------------------------------------
# Group 16 — play()
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_play_sets_running_true() -> None:
    mock = MockAlgorithm([_progress_tick(OpType.COMPARE), _terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    orch.play()
    assert orch.is_running is True


@pytest.mark.unit
def test_play_transitions_idle_panels_to_waiting() -> None:
    mock = MockAlgorithm([_progress_tick(OpType.COMPARE), _terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    orch.play()
    assert orch.panels[0].state == PanelState.WAITING_FOR_NEXT_TICK


@pytest.mark.unit
def test_play_does_not_affect_completed_panel() -> None:
    mock = MockAlgorithm([_terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    ctx = orch.panels[0]
    ctx.state = PanelState.COMPLETED
    ctx.is_active = False
    orch.play()
    assert ctx.state == PanelState.COMPLETED


@pytest.mark.unit
def test_play_ignored_while_stepping() -> None:
    mock = MockAlgorithm([_progress_tick(OpType.COMPARE), _terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    orch.step()  # enter stepping mode
    orch.play()
    assert orch.is_running is False
    assert orch.is_stepping is True


# ---------------------------------------------------------------------------
# Group 17 — pause()
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_pause_clears_running() -> None:
    mock = MockAlgorithm([_progress_tick(OpType.COMPARE), _terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    orch.play()
    orch.pause()
    assert orch.is_running is False


@pytest.mark.unit
def test_pause_preserves_animating_state() -> None:
    mock = MockAlgorithm([_progress_tick(OpType.COMPARE), _terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    orch.play()
    orch.update(1)  # fetch tick → ANIMATING
    orch.pause()
    assert orch.panels[0].state == PanelState.ANIMATING_OPERATION


@pytest.mark.unit
def test_paused_update_does_not_advance() -> None:
    mock = MockAlgorithm([_progress_tick(OpType.COMPARE), _terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    orch.play()
    orch.update(1)  # fetch tick → ANIMATING, 149ms remaining
    orch.pause()
    remaining_before = orch.panels[0].current_operation_remaining_ms
    orch.update(100)  # should be a no-op
    assert orch.panels[0].current_operation_remaining_ms == remaining_before


@pytest.mark.unit
def test_pause_then_play_resumes() -> None:
    mock = MockAlgorithm([_progress_tick(OpType.COMPARE), _terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    orch.play()
    orch.update(1)
    orch.pause()
    orch.play()
    assert orch.is_running is True


# ---------------------------------------------------------------------------
# Group 18 — step()
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_step_sets_stepping_true() -> None:
    mock = MockAlgorithm([_progress_tick(OpType.COMPARE), _terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    orch.step()
    assert orch.is_stepping is True


@pytest.mark.unit
def test_step_transitions_idle_to_waiting() -> None:
    mock = MockAlgorithm([_progress_tick(OpType.COMPARE), _terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    orch.step()
    assert orch.panels[0].state == PanelState.WAITING_FOR_NEXT_TICK


@pytest.mark.unit
def test_step_ignored_while_running() -> None:
    mock = MockAlgorithm([_progress_tick(OpType.COMPARE), _terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    orch.play()
    orch.step()
    assert orch.is_stepping is False
    assert orch.is_running is True


@pytest.mark.unit
def test_step_ignored_while_already_stepping() -> None:
    mock = MockAlgorithm([_progress_tick(OpType.COMPARE), _terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    orch.step()
    orch.step()  # second call ignored
    assert orch.is_stepping is True


@pytest.mark.unit
def test_step_animating_drains_to_idle_paused() -> None:
    mock = MockAlgorithm([_progress_tick(OpType.COMPARE), _terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    orch.step()
    orch.update(1)  # fetch tick → ANIMATING
    assert orch.panels[0].state == PanelState.ANIMATING_OPERATION
    orch.update(200)  # drain → should go to IDLE_PAUSED (not WAITING)
    assert orch.panels[0].state == PanelState.IDLE_PAUSED


@pytest.mark.unit
def test_step_clears_stepping_after_animation_drains() -> None:
    mock = MockAlgorithm([_progress_tick(OpType.COMPARE), _terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    orch.step()
    orch.update(1)  # fetch tick
    orch.update(200)  # drain → IDLE_PAUSED → stepping clears
    assert orch.is_stepping is False


@pytest.mark.unit
def test_step_two_panels_both_drain_before_stepping_clears() -> None:
    m1 = MockAlgorithm([_progress_tick(OpType.COMPARE), _terminal_tick()], name="A")
    m2 = MockAlgorithm([_progress_tick(OpType.SWAP), _terminal_tick()], name="B")
    orch = Orchestrator([m1, m2], [1, 2, 3])
    orch.step()
    orch.update(1)  # both fetch their ticks
    orch.update(50)  # partial drain — COMPARE(150ms) has 99ms left, SWAP(400ms) has 349ms left
    assert orch.is_stepping is True  # still animating
    orch.update(500)  # fully drain both
    assert orch.is_stepping is False


@pytest.mark.unit
def test_step_multiple_calls_advance_one_tick_each() -> None:
    tick1 = _progress_tick(OpType.COMPARE)
    tick2 = _progress_tick(OpType.COMPARE)
    mock = MockAlgorithm([tick1, tick2, _terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    # First step
    orch.step()
    orch.update(1)
    orch.update(200)
    assert orch.is_stepping is False
    assert orch.panels[0].state == PanelState.IDLE_PAUSED
    # Second step
    orch.step()
    orch.update(1)
    orch.update(200)
    assert orch.is_stepping is False
    assert orch.panels[0].step_count == 2


# ---------------------------------------------------------------------------
# Group 19 — restart()
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_restart_clears_running() -> None:
    algo = SimpleAlgorithm([1, 2, 3])
    orch = Orchestrator([algo], [1, 2, 3])
    orch.play()
    orch.restart()
    assert orch.is_running is False


@pytest.mark.unit
def test_restart_clears_stepping() -> None:
    algo = SimpleAlgorithm([1, 2, 3])
    orch = Orchestrator([algo], [1, 2, 3])
    orch.step()
    orch.restart()
    assert orch.is_stepping is False


@pytest.mark.unit
def test_restart_resets_panel_state_to_idle_paused() -> None:
    algo = SimpleAlgorithm([1, 2, 3])
    orch = Orchestrator([algo], [1, 2, 3])
    orch.play()
    orch.update(1)
    orch.restart()
    assert orch.panels[0].state == PanelState.IDLE_PAUSED


@pytest.mark.unit
def test_restart_resets_elapsed_time() -> None:
    algo = SimpleAlgorithm([1, 2, 3])
    orch = Orchestrator([algo], [1, 2, 3])
    orch.play()
    orch.update(1)
    orch.update(200)
    orch.restart()
    assert orch.panels[0].elapsed_time_ms == 0


@pytest.mark.unit
def test_restart_restores_fresh_generator() -> None:
    algo = SimpleAlgorithm([1, 2, 3])
    orch = Orchestrator([algo], [1, 2, 3])
    # Run to completion
    orch.play()
    orch.update(1)
    orch.update(200)
    orch.update(1)
    assert orch.panels[0].state == PanelState.COMPLETED
    # Restart and verify panel can run again
    orch.restart()
    orch.play()
    orch.update(1)
    assert orch.panels[0].state == PanelState.ANIMATING_OPERATION


@pytest.mark.unit
def test_restart_resets_slot_to_sprite_id() -> None:
    algo = SimpleAlgorithm([3, 1, 2])
    orch = Orchestrator([algo], [3, 1, 2])
    orch.play()
    orch.update(1)
    orch.update(200)
    orch.restart()
    assert orch.panels[0].slot_to_sprite_id == [0, 1, 2]


@pytest.mark.unit
def test_restart_restores_previous_array_state() -> None:
    algo = SimpleAlgorithm([4, 7, 2])
    orch = Orchestrator([algo], [4, 7, 2])
    orch.restart()
    assert orch.panels[0].previous_array_state == [4, 7, 2]


# ---------------------------------------------------------------------------
# Group 20 — initial state properties
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_initial_is_running_false() -> None:
    mock = MockAlgorithm([_terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    assert orch.is_running is False


@pytest.mark.unit
def test_initial_is_stepping_false() -> None:
    mock = MockAlgorithm([_terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    assert orch.is_stepping is False


@pytest.mark.unit
def test_update_noop_when_not_running_or_stepping() -> None:
    mock = MockAlgorithm([_progress_tick(OpType.COMPARE), _terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    ctx = orch.panels[0]
    ctx.state = PanelState.WAITING_FOR_NEXT_TICK
    orch.update(1)  # neither running nor stepping — should not fetch tick
    assert ctx.current_tick is None
