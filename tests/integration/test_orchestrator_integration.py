"""Integration tests for Orchestrator — TC-A4, A6, A15, A16, A17, A18.

Uses real algorithm generators (no mocks). Timing assertions use exact integer
millisecond arithmetic; no pytest.approx required.
"""

from __future__ import annotations

from collections.abc import Generator

import pytest

from visualizer.controllers.orchestrator import Orchestrator, PanelState
from visualizer.models.bubble import BubbleSort
from visualizer.models.contracts import BaseSortAlgorithm, OpType, SortResult
from visualizer.models.heap import HeapSort
from visualizer.models.insertion import InsertionSort
from visualizer.models.selection import SelectionSort

# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


class FailingAlgorithm(BaseSortAlgorithm):
    """Algorithm that immediately yields a FAILURE tick."""

    def __init__(self, data: list[int]) -> None:
        super().__init__(data, "Failing Sort", "O(n)")

    def sort_generator(self) -> Generator[SortResult]:
        yield SortResult(
            success=False,
            message="Simulated failure",
            operation_type=OpType.FAILURE,
        )


def _run_to_completion(orch: Orchestrator, max_frames: int = 10_000, dt: int = 1_000) -> None:
    """Start play and drive update(dt) until all panels are inactive."""
    orch.play()
    for _ in range(max_frames):
        if all(not ctx.is_active for ctx in orch.panels):
            break
        orch.update(dt)


# ---------------------------------------------------------------------------
# TC-A4 — Independent queues and integer timing
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_tc_a4_independent_queues_integer_timing(default_7: list[int]) -> None:
    """TC-A4: Bubble Sort elapsed_time_ms == 8200 (20x150ms + 13x400ms).

    No RANGE ticks in Bubble Sort, so timing is purely COMPARE + SWAP costs.
    """
    bubble = BubbleSort(default_7)
    orch = Orchestrator([bubble], default_7)

    _run_to_completion(orch)

    ctx = orch.panels[0]
    assert ctx.state == PanelState.COMPLETED
    assert ctx.elapsed_time_ms == 8_200  # 20*150 + 13*400


# ---------------------------------------------------------------------------
# TC-A6 — Fairness: all 4 generators complete without starvation
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_tc_a6_fairness_all_complete_no_starvation(default_7: list[int]) -> None:
    """TC-A6: All 4 algorithms reach COMPLETED; each accumulates comparisons and steps."""
    algos = [
        BubbleSort(default_7),
        SelectionSort(default_7),
        InsertionSort(default_7),
        HeapSort(default_7),
    ]
    orch = Orchestrator(algos, default_7)

    _run_to_completion(orch)

    for ctx in orch.panels:
        assert ctx.state == PanelState.COMPLETED
        assert not ctx.is_active
        assert ctx.comparisons > 0
        assert ctx.step_count > 0


# ---------------------------------------------------------------------------
# TC-A15 — Panel state machine happy path
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_tc_a15_state_machine_happy_path() -> None:
    """TC-A15: IDLE_PAUSED → play → WAITING → ANIMATING → drain → WAITING → COMPLETED."""
    # [2, 1]: yields COMPARE(150ms), SWAP(400ms), TERMINAL
    bubble = BubbleSort([2, 1])
    orch = Orchestrator([bubble], [2, 1])
    ctx = orch.panels[0]

    assert ctx.state == PanelState.IDLE_PAUSED

    orch.play()
    assert ctx.state == PanelState.WAITING_FOR_NEXT_TICK

    # Fetch COMPARE(150ms) → ANIMATING; dt not consumed on fetch frame
    orch.update(1)
    assert ctx.state == PanelState.ANIMATING_OPERATION
    assert ctx.current_operation_remaining_ms == 150

    # Drain COMPARE animation
    orch.update(150)
    assert ctx.state == PanelState.WAITING_FOR_NEXT_TICK

    # Fetch SWAP(400ms) → ANIMATING
    orch.update(1)
    assert ctx.state == PanelState.ANIMATING_OPERATION
    assert ctx.current_operation_remaining_ms == 400

    # Drain SWAP animation
    orch.update(400)
    assert ctx.state == PanelState.WAITING_FOR_NEXT_TICK

    # Fetch TERMINAL → COMPLETED
    orch.update(1)
    assert ctx.state == PanelState.COMPLETED
    assert not ctx.is_active
    assert ctx.elapsed_time_ms == 550  # 150 + 400

    # elapsed_time_ms frozen after completion
    orch.update(1_000)
    assert ctx.elapsed_time_ms == 550


# ---------------------------------------------------------------------------
# TC-A16 — Failure isolation
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_tc_a16_failure_isolation() -> None:
    """TC-A16: One failed panel enters FAILED; the healthy panel still reaches COMPLETED."""
    failing = FailingAlgorithm([1])
    healthy = BubbleSort([2, 1])  # COMPARE, SWAP, TERMINAL
    orch = Orchestrator([failing, healthy], [1])

    _run_to_completion(orch)

    assert orch.panels[0].state == PanelState.FAILED
    assert not orch.panels[0].is_active
    assert orch.panels[1].state == PanelState.COMPLETED
    assert not orch.panels[1].is_active


# ---------------------------------------------------------------------------
# TC-A17 — Pause freezes interpolation state
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_tc_a17_pause_freezes_state() -> None:
    """TC-A17: pause() preserves remaining_ms and elapsed_time_ms across updates."""
    # [2, 1]: first tick is COMPARE at 150ms
    bubble = BubbleSort([2, 1])
    orch = Orchestrator([bubble], [2, 1])
    ctx = orch.panels[0]

    orch.play()

    # Fetch COMPARE(150ms) → ANIMATING; remaining=150
    orch.update(1)
    assert ctx.state == PanelState.ANIMATING_OPERATION
    assert ctx.current_operation_remaining_ms == 150

    # Advance halfway through the animation
    orch.update(100)
    assert ctx.current_operation_remaining_ms == 50

    # Pause
    orch.pause()
    remaining_before = ctx.current_operation_remaining_ms
    elapsed_before = ctx.elapsed_time_ms

    # 100 update calls while paused — guard returns immediately
    for _ in range(100):
        orch.update(100)

    assert ctx.current_operation_remaining_ms == remaining_before
    assert ctx.elapsed_time_ms == elapsed_before
    assert ctx.state == PanelState.ANIMATING_OPERATION

    # Resume and drain remaining 50ms
    orch.play()
    orch.update(50)
    assert ctx.state == PanelState.WAITING_FOR_NEXT_TICK


# ---------------------------------------------------------------------------
# TC-A18 — Restart resets all state
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_tc_a18_restart_resets_state(default_7: list[int]) -> None:
    """TC-A18: restart() zeroes all counters/state; re-run yields correct counters."""
    bubble = BubbleSort(default_7)
    orch = Orchestrator([bubble], default_7)
    ctx = orch.panels[0]

    # Advance through several ticks
    orch.play()
    for _ in range(10):
        orch.update(1_000)

    assert ctx.step_count > 0  # confirms progress before restart

    # Restart
    orch.restart()
    ctx = orch.panels[0]  # re-bind (same object, but re-confirm)

    assert ctx.state == PanelState.IDLE_PAUSED
    assert ctx.elapsed_time_ms == 0
    assert ctx.comparisons == 0
    assert ctx.writes == 0
    assert ctx.step_count == 0
    assert not orch.is_running

    # Run to completion and verify counter accuracy
    _run_to_completion(orch)
    assert ctx.state == PanelState.COMPLETED
    assert ctx.comparisons == 20
    assert ctx.writes == 26


# ---------------------------------------------------------------------------
# Counter accuracy (all 4 algorithms via Orchestrator)
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_counter_accuracy_all_algorithms(default_7: list[int]) -> None:
    """All 4 algorithms match CLAUDE.md counter table after full Orchestrator run."""
    algos = [
        BubbleSort(default_7),
        SelectionSort(default_7),
        InsertionSort(default_7),
        HeapSort(default_7),
    ]
    orch = Orchestrator(algos, default_7)

    _run_to_completion(orch)

    bubble_ctx, selection_ctx, insertion_ctx, heap_ctx = orch.panels

    assert bubble_ctx.comparisons == 20
    assert bubble_ctx.writes == 26

    assert selection_ctx.comparisons == 21
    assert selection_ctx.writes == 10

    assert insertion_ctx.comparisons == 17
    assert insertion_ctx.writes == 19

    assert heap_ctx.comparisons == 20
    assert heap_ctx.writes == 30
    assert heap_ctx.step_count == 35
