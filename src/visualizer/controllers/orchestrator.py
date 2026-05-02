"""Controller / Orchestrator -- Phases 6a-6b.

This module is built in sub-phases:
  6a — PanelState enum, duration constants, PanelContext container, get_duration()
  6b — Orchestrator class: update(dt) core loop, state machine, cadence lifecycle
  6c — Sprite identity delta computation
  6d — Play/Pause/Step/Restart

References:
  doc 02 — MVC structure, module boundaries, Panel Runtime State Machine
  doc 06 — Behavior spec: play/pause/step/restart, operation timing
  doc 12 — Animation foundation: duration constants §2.2/§2.3, sprite identity §1
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from enum import Enum, auto

from visualizer.models.contracts import BaseSortAlgorithm, OpType, SortResult

# ---------------------------------------------------------------------------
# Panel state machine
# ---------------------------------------------------------------------------


class PanelState(Enum):
    """Per-panel runtime state (doc 02 §Panel Runtime State Machine)."""

    IDLE_PAUSED = auto()
    WAITING_FOR_NEXT_TICK = auto()
    ANIMATING_OPERATION = auto()
    COMPLETED = auto()
    FAILED = auto()


# ---------------------------------------------------------------------------
# Duration constants — standard cadence (doc 12 §2.2)
# ---------------------------------------------------------------------------

T1_COMPARE_DURATION: int = 150  # ms — OpType.COMPARE
T2_WRITE_DURATION: int = 400  # ms — OpType.SWAP and OpType.SHIFT
T3_RANGE_DURATION: int = 200  # ms — OpType.RANGE
TERMINAL_DURATION: int = 0  # ms — no animation
FAILURE_DURATION: int = 0  # ms — no animation

# ---------------------------------------------------------------------------
# Duration constants — sift-down cadence override (doc 12 §2.3)
# Applied after extraction swap in Heap Sort; reset on next boundary T3.
# ---------------------------------------------------------------------------

SIFT_DOWN_T1_DURATION: int = 100  # ms
SIFT_DOWN_T2_DURATION: int = 250  # ms
SIFT_DOWN_T3_DURATION: int = 130  # ms


# ---------------------------------------------------------------------------
# Duration lookup
# ---------------------------------------------------------------------------


def get_duration(op_type: OpType, sift_down_cadence: bool = False) -> int:
    """Return operation duration in milliseconds.

    SHIFT is never under sift-down cadence — Heap Sort uses SWAP, not SHIFT.
    """
    match op_type:
        case OpType.COMPARE:
            return SIFT_DOWN_T1_DURATION if sift_down_cadence else T1_COMPARE_DURATION
        case OpType.SWAP:
            return SIFT_DOWN_T2_DURATION if sift_down_cadence else T2_WRITE_DURATION
        case OpType.SHIFT:
            return T2_WRITE_DURATION
        case OpType.RANGE:
            return SIFT_DOWN_T3_DURATION if sift_down_cadence else T3_RANGE_DURATION
        case OpType.TERMINAL:
            return TERMINAL_DURATION
        case OpType.FAILURE:
            return FAILURE_DURATION


# ---------------------------------------------------------------------------
# Per-panel state container
# ---------------------------------------------------------------------------


class PanelContext:
    """Mutable per-panel runtime state for the Orchestrator.

    Plain class (not dataclass) — consistent with GridLayout in window.py.
    The Orchestrator mutates these fields directly each frame.
    algorithm_name and complexity are preserved across reset().
    """

    def __init__(self, algorithm_name: str, complexity: str) -> None:
        self.algorithm_name: str = algorithm_name
        self.complexity: str = complexity
        self.state: PanelState = PanelState.IDLE_PAUSED
        self.current_operation_remaining_ms: int = 0
        self.elapsed_time_ms: int = 0
        self.step_count: int = 0
        self.comparisons: int = 0
        self.writes: int = 0
        self.sift_down_cadence: bool = False
        self.is_active: bool = True
        self.current_tick: SortResult | None = None
        self.previous_array_state: list[int] | None = None
        self.extraction_pending: bool = False

    def reset(self) -> None:
        """Restore all