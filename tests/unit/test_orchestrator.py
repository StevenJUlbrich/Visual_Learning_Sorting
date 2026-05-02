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
    return PanelContext("Bubble Sort", "O(n²)")


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
    orch.panels[0].state = PanelState.WAITING_FOR_NEXT_TICK
    orch.update(1)
    assert orch.panels[0].state == PanelState.ANIMATING_OPERATION


@pytest.mark.unit
def test_animating_decrements_remaining() -> None:
    mock = MockAlgorithm([_progress_tick(OpType.COMPARE), _terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    ctx = orch.panels[0]
    ctx.state = PanelState.ANIMATING_OPERATION
    ctx.current_operation_remaining_ms = 150
    orch.update(50)
    assert ctx.current_operation_remaining_ms == 100


@pytest.mark.unit
def test_animating_to_waiting_when_remaining_zero() -> None:
    mock = MockAlgorithm([_progress_tick(OpType.COMPARE), _terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    ctx = orch.panels[0]
    ctx.state = PanelState.ANIMATING_OPERATION
    ctx.current_operation_remaining_ms = 33
    orch.update(33)
    assert ctx.state == PanelState.WAITING_FOR_NEXT_TICK


@pytest.mark.unit
def test_animating_to_waiting_on_overshoot() -> None:
    mock = MockAlgorithm([_progress_tick(OpType.COMPARE), _terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
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
    ctx.state = PanelState.WAITING_FOR_NEXT_TICK
    orch.update(1)
    assert ctx.state == PanelState.COMPLETED
    assert ctx.is_active is False


@pytest.mark.unit
def test_failure_tick_transitions_to_failed() -> None:
    mock = MockAlgorithm([_failure_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    ctx = orch.panels[0]
    ctx.state = PanelState.WAITING_FOR_NEXT_TICK
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
    ctx.state = PanelState.WAITING_FOR_NEXT_TICK
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
    ctx.state = PanelState.WAITING_FOR_NEXT_TICK
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
    ctx.state = PanelState.WAITING_FOR_NEXT_TICK
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
    ctx.state = PanelState.WAITING_FOR_NEXT_TICK
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
    ctx.state = PanelState.WAITING_FOR_NEXT_TICK
    orch.update(1)
    assert ctx.step_count == 1


@pytest.mark.unit
def test_step_increments_on_swap() -> None:
    mock = MockAlgorithm([_progress_tick(OpType.SWAP), _terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    ctx = orch.panels[0]
    ctx.state = PanelState.WAITING_FOR_NEXT_TICK
    orch.update(1)
    assert ctx.step_count == 1


@pytest.mark.unit
def test_step_excludes_range() -> None:
    mock = MockAlgorithm([_progress_tick(OpType.RANGE), _terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    ctx = orch.panels[0]
    ctx.state = PanelState.WAITING_FOR_NEXT_TICK
    orch.update(1)
    assert ctx.step_count == 0


@pytest.mark.unit
def test_step_excludes_terminal() -> None:
    mock = MockAlgorithm([_terminal_tick()])
    orch = Orchestrator([mock], [1, 2, 3])
    ctx = orch.panels[0]
    ctx.state = PanelState.WAITING_FOR_NEXT_TICK
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
    ctx.state = PanelState.WAITING_FOR_NEXT_TICK
    orch.update(1)
    assert ctx.comparisons == 5


@pytest.mark.unit
def test_writes_synced_from_algorithm() -> None:
    mock = MockAlgorithm([_progress_tick(OpType.SWAP), _terminal_tick()])
    mock.writes = 7
    orch = Orchestrator([mock], [1, 2, 3])
    ctx = orch.panels[0]
    ctx.state = PanelState.WAITING_FOR_NEXT_TICK
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
    ctx.state = PanelState.WAITING_FOR_NEXT_TICK
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
    ctx.state = PanelState.WAITING_FOR_NEXT_TICK
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
    ctx.state = PanelState.WAITING_FOR_NEXT_TICK
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
    ctx.state = PanelState.WAITING_FOR_NEXT_TICK
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
    ctx.state = PanelState.WAITING_FOR_NEXT_TICK
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
    ctx_fail.state = PanelState.WAITING_FOR_NEXT_TICK
    ctx_ok.state = PanelState.WAITING_FOR_NEXT_TICK
    orch.update(1)  # fail→FAILED, ok→ANIMATING
    assert ctx_fail.state == PanelState.FAILED
    assert ctx_ok.state == PanelState.ANIMATING_OPERATION
    orch.update(200)  # ok drains → WAITING
    orch.update(1)  # ok fetches terminal → COMPLETED
    assert ctx_fail.state == PanelState.FAILED
    assert ctx_ok.state == PanelState.COMPLETED
