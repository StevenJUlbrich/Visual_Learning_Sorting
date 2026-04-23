"""Heap Sort generator — emits SortResult ticks per 00_PSEUDOCODE.md §4.

Two phases driven by ``sort_generator``:

1. **Build Max-Heap.**  Sift down from ``floor(n/2) - 1`` to ``0``.
2. **Extraction.**  Swap root with current end, shrink ``heap_size``, sift the
   new root down within the reduced heap.

``_sift_down`` is a private generator method called via ``yield from`` from
both phases.  It emits the TC-A19 sift-down grammar per level:
Logical-Tree T3 → T1 compare(s) (1 or 2) → T2 swap (0 or 1), repeating until
the heap property holds or the left child is out of range.

Two T3 RANGE variants, distinguished by **message prefix** (D-081):

- **Boundary T3** — message starts with ``"Active heap"``.
  ``tuple(range(0, heap_size))``, emitted once per extraction before the root
  swap.  Shows the active heap region.
- **Logical Tree T3** — message starts with ``"Evaluating tree level"``.
  ``(parent, left, right)`` or ``(parent, left)``, emitted at the start of
  every sift-down level.  Parent is always the first element per D-058.

**Do not classify by contiguity** — Logical Tree T3 at parent=0 produces
contiguous tuples ``(0, 1, 2)`` or ``(0, 1)`` that collide with Boundary T3
shape.  This affects every Phase 2 sift-down and the last Phase 1 sift-down.

T3 ticks do NOT increment any counters per D-041.

Counter targets for ``[4, 7, 2, 6, 1, 5, 3]``: comparisons = 20, writes = 30,
steps = 35 (T1 + T2 only; 6 boundary T3 + 11 logical-tree T3 are excluded).

Message-format authority:

- T1 compares — doc 03 §Tick Taxonomy line 125.
- T2 swap and both T3 variants — pseudocode §4 (doc 03 is silent on these).
"""

from collections.abc import Generator

from visualizer.models.contracts import BaseSortAlgorithm, OpType, SortResult


class HeapSort(BaseSortAlgorithm):
    def __init__(self, data: list[int]) -> None:
        super().__init__(data, name="Heap Sort", complexity="O(n log n)")

    def _sift_down(self, start: int, end: int) -> Generator[SortResult]:
        """Sift ``self.data[start]`` down within ``self.data[start..end-1]``.

        ``end`` is the exclusive upper bound.  Emits at most ``log_2(end-start)``
        levels of ticks; each level: one Logical-Tree T3, one or two T1
        compares, and at most one T2 swap.  Returns when either the left child
        is out of range or the heap property holds at the current parent.
        """
        arr = self.data
        parent = start
        while True:
            left = 2 * parent + 1
            right = 2 * parent + 2

            # Gate: at least the left child must be in range.
            if left >= end:
                return

            # Logical-Tree T3 — non-contiguous, parent first per D-058.
            if right < end:
                yield SortResult(
                    success=True,
                    message=f"Evaluating tree level at parent {parent}",
                    operation_type=OpType.RANGE,
                    array_state=list(arr),
                    highlight_indices=(parent, left, right),
                )
            else:
                yield SortResult(
                    success=True,
                    message=f"Evaluating tree level at parent {parent}",
                    operation_type=OpType.RANGE,
                    array_state=list(arr),
                    highlight_indices=(parent, left),
                )

            # T1 compare — parent vs left (always).
            largest = left
            self.comparisons += 1
            yield SortResult(
                success=True,
                message=(
                    f"Comparing index {parent} (value {arr[parent]})"
                    f" and index {left} (value {arr[left]})"
                ),
                operation_type=OpType.COMPARE,
                array_state=list(arr),
                highlight_indices=(parent, left),
            )

            # T1 compare — parent vs right (if right child exists).
            if right < end:
                self.comparisons += 1
                yield SortResult(
                    success=True,
                    message=(
                        f"Comparing index {parent} (value {arr[parent]})"
                        f" and index {right} (value {arr[right]})"
                    ),
                    operation_type=OpType.COMPARE,
                    array_state=list(arr),
                    highlight_indices=(parent, right),
                )
                # Internal decision — not yielded as a tick.
                if arr[right] > arr[left]:
                    largest = right

            # T2 swap (conditional).
            if arr[largest] > arr[parent]:
                arr[parent], arr[largest] = arr[largest], arr[parent]
                self.writes += 2
                yield SortResult(
                    success=True,
                    message=f"Swap arr[{parent}] and arr[{largest}]",
                    operation_type=OpType.SWAP,
                    array_state=list(arr),
                    highlight_indices=(parent, largest),
                )
                parent = largest
            else:
                return

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

        # Phase 1 — Build Max-Heap.  Process nodes floor(n/2)-1 down to 0.
        for start in range(n // 2 - 1, -1, -1):
            yield from self._sift_down(start, n)

        # Phase 2 — Extraction.
        heap_size = n
        while heap_size > 1:
            end = heap_size - 1

            # Boundary T3 — contiguous range(0, heap_size).
            yield SortResult(
                success=True,
                message=f"Active heap: indices 0..{end}",
                operation_type=OpType.RANGE,
                array_state=list(arr),
                highlight_indices=tuple(range(heap_size)),
            )

            # Extraction swap — root with current end.
            arr[0], arr[end] = arr[end], arr[0]
            self.writes += 2
            yield SortResult(
                success=True,
                message=f"Extract root={arr[end]} to slot {end}",
                operation_type=OpType.SWAP,
                array_state=list(arr),
                highlight_indices=(0, end),
            )

            # Shrink active heap, then repair the new root.
            heap_size -= 1
            yield from self._sift_down(0, heap_size)

        yield SortResult(
            success=True,
            message="Sort complete",
            operation_type=OpType.TERMINAL,
            is_complete=True,
            array_state=list(arr),
            highlight_indices=tuple(range(n)),
        )
