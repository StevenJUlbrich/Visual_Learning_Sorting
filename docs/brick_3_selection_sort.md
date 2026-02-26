Moving right along to **Selection Sort**.

In your original planning document, you noted a bug in your reference video where the Selection Sort algorithm finished without fully sorting the array. As your mentor, I love that you caught that. That happens when visualizations don't properly bind their animation frames to the actual state of the algorithm. Our `SortResult` contract makes that bug mathematically impossible here.

Here is the concrete implementation of `SelectionSort`.

### 1. The Selection Sort Implementation

Create a new file in your models directory.

```python
# src/visualizer/models/selection_sort.py
from collections.abc import Generator

from .base import BaseSortAlgorithm
from .state import SortResult

class SelectionSort(BaseSortAlgorithm):
    """
    Implements the Selection Sort algorithm.
    Time Complexity: $O(n^2)$ for all cases.
    """
    
    def __init__(self, data: list[int]):
        super().__init__(data, name="Selection Sort")

    def sort_generator(self) -> Generator[SortResult, None, None]:
        # Fail-Fast Boundary Check
        if self.size == 0:
            yield SortResult(
                success=False,
                message="Error: Cannot sort an empty array."
            )
            return

        # The Iterative Sort
        for i in range(self.size):
            min_idx = i
            
            # Phase 1: Search for the minimum element in the remaining unsorted array
            for j in range(i + 1, self.size):
                
                # TICK 1: Yield the search comparison
                # This highlights the current suspected minimum and the element being checked
                yield SortResult(
                    success=True,
                    message=f"Checking if {self.data[j]} is less than current min {self.data[min_idx]}",
                    array_state=self.data.copy(),
                    highlight_indices=(min_idx, j)
                )
                
                if self.data[j] < self.data[min_idx]:
                    min_idx = j
            
            # Phase 2: Swap the found minimum into its correct sorted position
            if min_idx != i:
                self.data[i], self.data[min_idx] = self.data[min_idx], self.data[i]
                
                # TICK 2: Yield the swap operation
                yield SortResult(
                    success=True,
                    message=f"Swapped new minimum {self.data[i]} into position {i}",
                    array_state=self.data.copy(),
                    highlight_indices=(i, min_idx)
                )
        
        # FINAL TICK: The Completion State
        yield SortResult(
            success=True,
            message="Selection Sort Complete",
            is_complete=True,
            array_state=self.data.copy(),
            highlight_indices=tuple(range(self.size))
        )

```

### 2. Architectural Takeaways

Notice how Selection Sort tells a completely different visual story than Bubble Sort, even though both are $O(n^2)$ algorithms:

* **The Visual Cadence:** In Bubble Sort, you yielded a swap almost constantly. In Selection Sort, the algorithm spends most of its ticks just *searching* (Phase 1). It only yields a swap *once* per outer loop (Phase 2). When the user watches this run side-by-side with Bubble Sort, they will physically see Selection Sort making far fewer writes/swaps to memory. That is a massive educational win.
* **Highlighting Logic:** The `highlight_indices` tuple during the search phase `(min_idx, j)` is crucial. It keeps the "current minimum" visually anchored in one color, while the `j` index sweeps across the rest of the array. It makes the mechanics instantly readable without needing text.

---

### Next Steps

We have successfully knocked out the two easiest iterative algorithms. We have **Insertion Sort** and **Merge Sort** remaining for Brick 3.

Would you like to implement Insertion Sort next, or are you ready to tackle the recursive complexity and manual error-bubbling of Merge Sort?