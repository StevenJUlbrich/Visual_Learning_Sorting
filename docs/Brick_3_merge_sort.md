This is where the architecture we chose really shows its strength.

Because Merge Sort is a divide-and-conquer recursive algorithm, we cannot just use a simple `while` or `for` loop. We have to traverse down a call stack and back up. This is exactly why we implemented the **Pure Result Pattern** (Option B). Instead of letting Python magically bubble up exceptions if something goes wrong, we are going to explicitly check the success state of every recursive yield and bubble it up manually, just like you would in Rust or Go.

Here is the concrete implementation of `MergeSort`.

### 1. The Merge Sort Implementation

Create the final model file.

```python
# src/visualizer/models/merge_sort.py
from collections.abc import Generator

from .base import BaseSortAlgorithm
from .state import SortResult

class MergeSort(BaseSortAlgorithm):
    """
    Implements the Merge Sort algorithm.
    Time Complexity: $O(n \log n)$ for all cases.
    """

    def __init__(self, data: list[int]):
        super().__init__(data, name="Merge Sort")

    def sort_generator(self) -> Generator[SortResult, None, None]:
        # Fail-Fast Boundary Check
        if self.size == 0:
            yield SortResult(
                success=False,
                message="Error: Cannot sort an empty array."
            )
            return

        # Start the recursive sorting process
        # We iterate over the generator to catch and bubble up states/errors explicitly
        for result in self._merge_sort(0, self.size - 1):
            yield result
            if not result.success:
                return  # Bubble up the failure and halt execution

        # FINAL TICK: The Completion State
        yield SortResult(
            success=True,
            message="Merge Sort Complete",
            is_complete=True,
            array_state=self.data.copy(),
            highlight_indices=tuple(range(self.size))
        )

    def _merge_sort(self, left: int, right: int) -> Generator[SortResult, None, None]:
        """Recursive division of the array."""
        if left >= right:
            return

        mid = left + (right - left) // 2

        # 1. Traverse Left Half
        for result in self._merge_sort(left, mid):
            yield result
            if not result.success: return

        # 2. Traverse Right Half
        for result in self._merge_sort(mid + 1, right):
            yield result
            if not result.success: return

        # 3. Merge the Halves
        for result in self._merge(left, mid, right):
            yield result
            if not result.success: return

    def _merge(self, left: int, mid: int, right: int) -> Generator[SortResult, None, None]:
        """Merges two sorted sub-arrays back into the main array."""
        
        # TICK: Highlight the sub-array brackets during divide-and-conquer
        yield SortResult(
            success=True,
            message=f"Merging sub-arrays from index {left} to {right}",
            array_state=self.data.copy(),
            highlight_indices=tuple(range(left, right + 1))
        )

        # Create temporary arrays for the two halves
        left_copy = self.data[left:mid + 1]
        right_copy = self.data[mid + 1:right + 1]

        i = 0  # Index for left_copy
        j = 0  # Index for right_copy
        k = left  # Index for self.data (the main array)

        # Compare and place elements back into the main array
        while i < len(left_copy) and j < len(right_copy):
            # TICK: Show the comparison
            yield SortResult(
                success=True,
                message=f"Comparing {left_copy[i]} and {right_copy[j]}",
                array_state=self.data.copy(),
                highlight_indices=(k,)
            )

            if left_copy[i] <= right_copy[j]:
                self.data[k] = left_copy[i]
                i += 1
            else:
                self.data[k] = right_copy[j]
                j += 1

            # TICK: Show the placement
            yield SortResult(
                success=True,
                message=f"Placed {self.data[k]} at index {k}",
                array_state=self.data.copy(),
                highlight_indices=(k,)
            )
            k += 1

        # Exhaust any remaining elements in the left copy
        while i < len(left_copy):
            self.data[k] = left_copy[i]
            yield SortResult(
                success=True,
                message=f"Placed remaining left element {self.data[k]} at index {k}",
                array_state=self.data.copy(),
                highlight_indices=(k,)
            )
            i += 1
            k += 1

        # Exhaust any remaining elements in the right copy
        while j < len(right_copy):
            self.data[k] = right_copy[j]
            yield SortResult(
                success=True,
                message=f"Placed remaining right element {self.data[k]} at index {k}",
                array_state=self.data.copy(),
                highlight_indices=(k,)
            )
            j += 1
            k += 1

```

### 2. Architectural Takeaways

This is the exact file you want to point to during an interview. It highlights several advanced concepts:

* **Explicit Control Flow:** Look at `for result in self._merge_sort(...)`. Instead of using Python's syntactic sugar (`yield from self._merge_sort(...)`), we unpack the generator and check `if not result.success: return`. This enforces our strict contract. We know exactly how and when a failure will exit the recursion tree without hidden magic.
* **In-Place Mutation for UI State:** Standard theoretical Merge Sort often returns new arrays. However, because our UI (Pygame) needs to read from a single, consistent array length to draw the grid smoothly, we overwrite `self.data` directly using `k` as the pointer.
* **The "Bracket" Highlight:** You mentioned in your original notes that the video reference showed sub-array brackets during the divide-and-conquer phase. The very first tick in `_merge` yields a `highlight_indices` spanning from `left` to `right + 1`. This will allow your View layer to light up the entire sub-section of the array being merged, visually communicating the $O(n \log n)$ chunking behavior perfectly.

---

### Brick 3 Complete

We now have our Data Model (`SortResult`), our Interface (`BaseSortAlgorithm`), and all four concrete sorting classes built, strictly typed, and completely decoupled from any UI logic.

Would you like to move on to **Brick 4: The Rendering Engine**, where we start building the Pygame views, defining the custom colors, and rendering the 2x2 grid to actually display these states?