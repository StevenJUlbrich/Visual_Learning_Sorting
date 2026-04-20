"""Selection Sort generator — emits SortResult ticks per 00_PSEUDOCODE.md §2.

Control flow: outer loop selects sorted boundary ``i``; inner loop scans
``i+1..n-1`` tracking the running minimum.  Single swap per pass, skipped when
``min_idx == i`` (no T2 emitted).

T1 highlight tuple is always ``(min_idx, j)`` with ``min_idx`` first (D-068).
The yield fires *before* the ``min_idx`` update (matching pseudocode §2 exactly),
so ``highlight_indices`` is never ``(j, j)`` — the update happens silently after
the yield and the next T1 naturally shows the updated minimum.

Counter targets for ``[4, 7, 2, 6, 1, 5, 3]``: comparisons = 21, writes = 10.
``comparisons`` = sum of inner-loop iterations = 6+5+4+3+2+1 = 21.
``writes`` = 5 swap passes x 2 positions = 10.
"""

from collections.abc import Generator

from visualizer.models.contracts import BaseSortAlgorithm, OpType, SortResult


class SelectionSort(BaseSortAlgorithm):
    def __init__(self, data: list[int]) -> None:
        super().__init__(data, name="Selection Sort", complexity="O(n²)")

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

        for i in range(n - 1):
            min_idx = i

            for j in range(i + 1, n):
                self.comparisons += 1
                yield SortResult(
                    success=True,
                    message=(
                        f"Comparing index {j} (value {arr[j]})"
                        f" with current min {arr[min_idx]} at index {min_idx}"
                    ),
                    operation_type=OpType.COMPARE,
                    array_state=list(arr),
                    highlight_indices=(min_idx, j),
                )
                if arr[j] < arr[min_idx]:
                    min_idx = j

            if min_idx != i:
                arr[i], arr[min_idx] = arr[min_idx], arr[i]
                self.writes += 2
                yield SortResult(
                    success=True,
                    message=f"Swap arr[{i}] and arr[{min_idx}]",
                    operation_type=OpType.SWAP,
                    array_state=list(arr),
                    highlight_indices=(i, min_idx),
                )

        yield SortResult(
            success=True,
            message="Sort complete",
            operation_type=OpType.TERMINAL,
            is_complete=True,
            array_state=list(arr),
            highlight_indices=tuple(range(n)),
        )
