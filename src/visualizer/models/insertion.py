"""Insertion Sort generator — emits SortResult ticks per 00_PSEUDOCODE.md §3.

Three-phase pass structure:

1. **Key Selection.** Single T1 with ``highlight_indices=(i,)``.  Does NOT
   increment ``self.comparisons`` — visual tick only (D-071, doc 03 §153).
2. **Compare-and-shift loop.** One T1 compare + one T2 shift per element, never
   batched (D-060, D-064).  Each shift writes one array position
   (``writes += 1``).
3. **Terminating Compare (conditional).** Fires only if the while-loop exits by
   the condition ``arr[j] <= key``, NOT by ``j < 0``.  Gate: ``if j >= 0`` at
   loop exit.  This is the control-flow rule TC-A14 pins down.
4. **Placement.** ``arr[j+1] = key``, ``writes += 1``, single-index highlight
   ``(j+1,)``.

Counter targets for ``[4, 7, 2, 6, 1, 5, 3]``: comparisons = 17, writes = 19.
Breakdown: 13 shift-loop compares + 4 terminating compares = 17; 13 shifts + 6
placements = 19.

Message format source of truth:

- Doc 03 §Tick Taxonomy prescribes key-selection and compare-during-shift text.
- Pseudocode §3 supplies shift and placement text (doc 03 is silent on T2).
"""

from collections.abc import Generator

from visualizer.models.contracts import BaseSortAlgorithm, OpType, SortResult


class InsertionSort(BaseSortAlgorithm):
    def __init__(self, data: list[int]) -> None:
        super().__init__(data, name="Insertion Sort", complexity="O(n²)")

    def sort_generator(self) -> Generator[SortResult]:
        arr = self.data
        n = self.size

        if n == 0:
            yield SortResult(
                success=False,
                message="Empty input",
                operation_type=OpType.FAILURE,
            )
            return

        if n == 1:
            yield SortResult(
                success=True,
                message="Single element — already sorted",
                operation_type=OpType.TERMINAL,
                is_complete=True,
                array_state=list(arr),
                highlight_indices=(0,),
            )
            return

        for i in range(1, n):
            key = arr[i]

            # Phase 1 — Key Selection.  COMPARE type for view-layer timing, but
            # does NOT increment self.comparisons (doc 03 §153).
            yield SortResult(
                success=True,
                message=f"Selecting key: {arr[i]} at index {i}",
                operation_type=OpType.COMPARE,
                array_state=list(arr),
                highlight_indices=(i,),
            )

            j = i - 1

            # Phase 2 — Compare-and-shift loop.  Each iteration: T1 compare,
            # then T2 shift.  Never batch.
            while j >= 0 and arr[j] > key:
                self.comparisons += 1
                yield SortResult(
                    success=True,
                    message=f"Comparing index {j} (value {arr[j]}) with key {key}",
                    operation_type=OpType.COMPARE,
                    array_state=list(arr),
                    highlight_indices=(j, j + 1),
                )

                arr[j + 1] = arr[j]
                self.writes += 1
                yield SortResult(
                    success=True,
                    message=f"Shift arr[{j}]={arr[j]} right to slot {j + 1}",
                    operation_type=OpType.SHIFT,
                    array_state=list(arr),
                    highlight_indices=(j, j + 1),
                )

                j -= 1

            # Phase 2b — Terminating Compare.  Only when loop exited by
            # arr[j] <= key (j still >= 0), not when j fell below 0.
            if j >= 0:
                self.comparisons += 1
                yield SortResult(
                    success=True,
                    message=f"Comparing index {j} (value {arr[j]}) with key {key}",
                    operation_type=OpType.COMPARE,
                    array_state=list(arr),
                    highlight_indices=(j, j + 1),
                )

            # Phase 3 — Placement.  Single-index highlight on the landing slot.
            arr[j + 1] = key
            self.writes += 1
            yield SortResult(
                success=True,
                message=f"Place key={key} at slot {j + 1}",
                operation_type=OpType.SHIFT,
                array_state=list(arr),
                highlight_indices=(j + 1,),
            )

        yield SortResult(
            success=True,
            message="Sort complete",
            operation_type=OpType.TERMINAL,
            is_complete=True,
            array_state=list(arr),
            highlight_indices=tuple(range(n)),
        )
