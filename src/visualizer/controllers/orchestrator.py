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
        """Restore all runtime fields to initial defaults; preserve identity."""
        self.state = PanelState.IDLE_PAUSED
        self.current_operation_remaining_ms = 0
        self.elapsed_time_ms = 0
        self.step_count = 0
        self.comparisons = 0
        self.writes = 0
        self.sift_down_cadence = False
        self.is_active = True
        self.current_tick = None
        self.previous_array_state = None
        self.extraction_pending = False


# ---------------------------------------------------------------------------
# Orchestrator — independent-queue controller
# ---------------------------------------------------------------------------


class Orchestrator:
    """Independent-queue controller for four algorithm panels.

    Each panel has its own PanelContext, generator, and timing state.
    update(dt) is called once per frame by the event loop.

    Phase 6b scope: core loop only. Play/Pause/Step/Restart (6d) and
    sprite identity delta (6c) are added in subsequent sub-phases.

    Spec: doc 02 (state machine), doc 06 (timing), doc 12 §2 (durations).
    """

    def __init__(
        self,
        algorithms: Sequence[BaseSortAlgorithm],
        initial_array: list[int],
    ) -> None:
        self._initial_array: list[int] = initial_array.copy()
        self._panels: list[PanelContext] = []
        self._generators: list[Iterator[SortResult] | None] = []
        self._algorithms: list[BaseSortAlgorithm] = list(algorithms)

        for algo in algorithms:
            ctx = PanelContext(algo.name, algo.complexity)
            ctx.previous_array_state = algo.data.copy()
            self._panels.append(ctx)
            self._generators.append(algo.sort_generator())

    @property
    def panels(self) -> list[PanelContext]:
        """Read-only view of all panel contexts."""
        return self._panels

    def update(self, dt: int) -> None:
        """Advance all active panels by dt milliseconds.

        Each panel is processed independently — one state transition per call.
        ANIMATING counts down; WAITING fetches the next tick. Never both in
        the same frame (the `continue` after ANIMATING enforces this).
        """
        for i, ctx in enumerate(self._panels):
            if not ctx.is_active:
                continue
            if ctx.state == PanelState.IDLE_PAUSED:
                continue

            if ctx.state == PanelState.ANIMATING_OPERATION:
                ctx.current_operation_remaining_ms -= dt
                if ctx.current_operation_remaining_ms <= 0:
                    ctx.state = PanelState.WAITING_FOR_NEXT_TICK
                continue  # Don't also fetch in the same frame

            if ctx.state == PanelState.WAITING_FOR_NEXT_TICK:
                gen = self._generators[i]
                if gen is None:
                    continue

                tick = next(gen, None)
                if tick is None:
                    # Generator exhausted without TERMINAL — implicit completion
                    ctx.state = PanelState.COMPLETED
                    ctx.is_active = False
                    continue

                ctx.current_tick = tick

                if tick.operation_type == OpType.TERMINAL:
                    ctx.state = PanelState.COMPLETED
                    ctx.is_active = False
                    self._generators[i] = None
                    continue

                if tick.operation_type == OpType.FAILURE:
                    ctx.state = PanelState.FAILED
                    ctx.is_active = False
                    self._generators[i] = None
                    continue

                # Normal progress tick
                duration = get_duration(tick.operation_type, ctx.sift_down_cadence)
                ctx.current_operation_remaining_ms = duration
                ctx.elapsed_time_ms += duration
                ctx.state = PanelState.ANIMATING_OPERATION

                # Step counter: exclude RANGE ticks (D-041)
                if tick.success and not tick.is_complete and tick.operation_type != OpType.RANGE:
                    ctx.step_count += 1

                # Sync counters from algorithm instance
                algo = self._algorithms[i]
                ctx.comparisons = algo.comparisons
                ctx.writes = algo.writes

                # Store array snapshot for delta computation (used by 6c)
                if tick.array_state is not None:
                    ctx.previous_array_state = tick.array_state

                # Sift-down cadence lifecycle (Heap Sort only)
                if ctx.algorithm_name == "Heap Sort":
                    self._update_heap_cadence(ctx, tick)

    def _update_heap_cadence(self, ctx: PanelContext, tick: SortResult) -> None:
        """Update sift-down cadence flag based on Heap Sort tick type.

        Two-step protocol:
          1. Boundary T3 (RANGE, "Active heap" prefix): reset cadence, arm extraction.
          2. SWAP while extraction armed: enable cadence, disarm.

        get_duration is called BEFORE this method, so the extraction SWAP itself
        always runs at standard 400ms (doc 12 §2.3: "extraction swap — always 400ms").
        """
        if tick.operation_type == OpType.RANGE and tick.message.startswith("Active heap"):
            ctx.sift_down_cadence = False
            ctx.extraction_pending = True
        elif tick.operation_type == OpType.SWAP and ctx.extraction_pending:
            ctx.sift_down_cadence = True
            ctx.extraction_pending = False
