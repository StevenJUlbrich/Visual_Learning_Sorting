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
    assert ctx.comparisons =