"""Bubble Sort generator — emits SortResult ticks per 00_PSEUDOCODE.md §1.

Control flow: classic two-loop with ``swapped`` early-exit.  Inner limit
shrinks by one slot per pass (``n - pass_idx - 1``), which is the boundary
the LimitLine visualizes.

Counter targets for ``[4, 7, 2, 6, 1, 5, 3]``: comparisons = 20, writes = 26.
``writes`` is always ``2 * swap_count`` because each swap writes two slots.
"""

from collections.abc import Generator

from visualizer.models.contracts import BaseSortAlgorithm, OpType, SortResult


class BubbleSort(BaseSortAlgorithm):
    def __init__(self, data: list[int]) -> None:
        super().__init__(data, name="Bubble Sort", complexity="O(n²)")

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

        for pass_idx in range(n - 1):
            swapped = False
            inner_limit = n - pass_idx - 1  # LimitLine boundary

            for j in range(inner_limit):
                self.comparisons += 1
                yield SortResult(
                    success=True,
                    message=f"Comparing index {j} (value {arr[j]}) and index {j + 1} (value {arr[j + 1]})",
                    operation_type=OpType.COMPARE,
                    array_state=list(arr),
                    highlight_indices=(j, j + 1),
                )

                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    self.writes += 2
                    yield SortResult(
                        success=True,
                        message=f"Swap {arr[j + 1]} and {arr[j]}",
                        operation_type=OpType.SWAP,
                        array_state=list(arr),
                        highlight_indices=(j, j + 1),
                    )
                    swapped = True

            if not swapped:
                break

        yield SortResult(
            success=True,
            message="Sort complete",
            operation_type=OpType.TERMINAL,
            is_complete=True,
            array_state=list(arr),
            highlight_indices=tuple(range(n)),
        )
