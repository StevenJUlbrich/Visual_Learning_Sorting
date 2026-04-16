"""Canonical type surface for the sorting visualizer model layer.

This module defines the three exports that every algorithm generator, test,
controller, and view consumes:

- ``OpType``: the six tick classes a generator can yield.
- ``SortResult``: the dataclass returned on every yield.
- ``BaseSortAlgorithm``: the abstract base each of the four algorithm
  implementations extends.

Contract source of truth: ``docs/design_docs/03_DATA_CONTRACTS.md``.
Binding decisions consumed here: D-002 (MVC structure), D-011 (array copies
on every tick), D-020 (no exceptions from generators), D-041 (T3 RANGE ticks
do not increment the step counter).

This module must not import Pygame or any rendering library. It is consumed
by tests that run headlessly per ``docs/design_docs/08_TEST_PLAN.md`` §4.4.
"""

from abc import ABC, abstractmethod
from collections.abc import Generator
from dataclasses import dataclass
from enum import Enum, auto


class OpType(Enum):
    """Tick classes yielded by algorithm generators.

    Each member maps to a simulated display time (in milliseconds) that
    the orchestrator uses for queue timing. The timing constants live in
    the controller layer rather than here, because Heap Sort applies a
    rapid-cadence override after extraction swaps (CLAUDE.md Critical
    Rule #6).
    """

    COMPARE = auto()  # T1 — data comparison between highlighted indices.
    SWAP = auto()  # T2 — two-position mutation (writes += 2).
    SHIFT = auto()  # T2 — single-position mutation (writes += 1).
    RANGE = auto()  # T3 — non-mutating visual aid; excluded from step count (D-041).
    TERMINAL = auto()  # Completion tick; yielded exactly once on successful sort.
    FAILURE = auto()  # Explicit failure tick per D-020; generators never raise.


@dataclass(slots=True)
class SortResult:
    """A single tick yielded by an algorithm generator.

    Field order matches ``docs/design_docs/03_DATA_CONTRACTS.md`` §SortResult
    (Definitive) exactly. ``slots=True`` per CLAUDE.md's SortResult Contract
    section — prevents attribute-dict allocation per tick and catches typos
    at assignment time.

    Contract invariants (enforced by generators, not by this dataclass):

    - Progress tick: ``success=True``, ``is_complete=False``, ``array_state``
      is not ``None``.
    - Completion tick: ``success=True``, ``is_complete=True``, ``array_state``
      is not ``None``.
    - Failure tick: ``success=False``, ``is_complete=False``, ``array_state``
      optional.
    - ``array_state`` must be an independent snapshot copy (D-011), not a
      reference to the algorithm's mutable working array. Use
      ``self.data.copy()`` at yield time. The dataclass does not enforce
      the copy — that is the generator's responsibility.
    - ``highlight_indices`` entries must be unique and in-bounds for
      ``array_state``. For Heap Sort Logical Tree Highlights the sift-down
      parent is always the first element (D-058); for other tick types
      tuple order carries no rendering semantics.
    """

    success: bool
    message: str
    operation_type: OpType
    is_complete: bool = False
    array_state: list[int] | None = None
    highlight_indices: tuple[int, ...] | None = None


class BaseSortAlgorithm(ABC):
    """Abstract base class for every v1 sorting algorithm.

    Consumers:

    - The four concrete algorithms under ``visualizer.models`` (Phase 2:
      ``bubble.py``, ``selection.py``, ``insertion.py``, ``heap.py``).
    - The orchestrator (Phase 6) — consumes ``sort_generator()`` and reads
      ``comparisons``, ``writes``, and ``size`` for HUD display.

    Subclass contract:

    - ``__init__`` must call ``super().__init__(data, name, complexity)``.
    - ``sort_generator`` is the only abstract method; it must yield
      ``SortResult`` objects per the tick taxonomy in doc 03.
    - On empty input, the generator yields exactly one ``FAILURE`` tick
      and terminates (D-020, doc 03 §Generator Contract). Generators must
      never ``raise`` — all domain errors travel via ``FAILURE``.
    """

    def __init__(self, data: list[int], name: str, complexity: str) -> None:
        self.name: str = name
        self.complexity: str = complexity
        self.data: list[int] = data.copy()
        self.size: int = len(self.data)
        self.comparisons: int = 0
        self.writes: int = 0

    @abstractmethod
    def sort_generator(self) -> Generator[SortResult]:
        """Yield the tick sequence that performs the sort.

        Subclasses implement this as a Python generator function. The
        generator must:

        - Increment ``self.comparisons`` before yielding each compare tick
          that corresponds to an actual data comparison. Insertion Sort's
          key-selection ``COMPARE`` tick does NOT increment the counter —
          see doc 03 §Secondary Counters.
        - Increment ``self.writes`` before yielding each mutation tick,
          per the increment table in doc 03 §Per-Operation Increment Rules.
        - Copy the working array into ``array_state`` on every success tick
          (``array_state=self.data.copy()``).
        - Yield exactly one terminal tick on successful completion.
        - Yield exactly one ``FAILURE`` tick on empty input and terminate
          without yielding a terminal tick.
        - Never ``raise`` — all error paths use ``FAILURE``.
        """
        ...
