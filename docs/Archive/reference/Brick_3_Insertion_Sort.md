Let's complete the iterative trio with **Insertion Sort**.

Insertion Sort is mechanically fascinating to watch because it behaves exactly how most humans sort a hand of playing cards. It builds a "sorted" section on the left side of the array and shifts elements to the right to make room for the new card.

Here is the concrete implementation of `InsertionSort`.

### 1. The Insertion Sort Implementation

Create a new file in your models directory.

```python
# src/visualizer/models/insertion_sort.py
from collections.abc import Generator

from .base import BaseSortAlgorithm
from .state import SortResult

class InsertionSort(BaseSortAlgorithm):
    """
    Implements the Insertion Sort algorithm.
    Time Complexity: $O(n^2)$ worst-case, but $O(n)$ best-case (nearly sorted).
    """
    
    def __init__(self, data: list[int]):
        super().__init__(data, name="Insertion Sort")

    def sort_generator(self) -> Generator[SortResult, None, None]:
        # Fail-Fast Boundary Check
        if self.size == 0:
            yield SortResult(
                success=False,
                message="Error: Cannot sort an empty array."
            )
            return

        # The Iterative Sort
        for i in range(1, self.size):
            key = self.data[i]
            j = i - 1
            
            # TICK 1: Yield the selection of the 'key' (the card we are holding)
            yield SortResult(
                success=True,
                message=f"Selected key {key} to insert into the sorted left section",
                array_state=self.data.copy(),
                highlight_indices=(i,)
            )

            # Phase 1: Shift elements greater than key to the right
            while j >= 0 and self.data[j] > key:
                
                # TICK 2: Yield the comparison and impending shift
                yield SortResult(
                    success=True,
                    message=f"Element {self.data[j]} is larger than {key}, shifting right",
                    array_state=self.data.copy(),
                    highlight_indices=(j, j + 1)
                )
                
                self.data[j + 1] = self.data[j]
                j -= 1
            
            # Phase 2: Insert the key into its correct sorted position
            self.data[j + 1] = key
            
            # TICK 3: Yield the final placement of the key
            yield SortResult(
                success=True,
                message=f"Inserted key {key} into position {j + 1}",
                array_state=self.data.copy(),
                highlight_indices=(j + 1,)
            )
        
        # FINAL TICK: The Completion State
        yield SortResult(
            success=True,
            message="Insertion Sort Complete",
            is_complete=True,
            array_state=self.data.copy(),
            highlight_indices=tuple(range(self.size))
        )

```

### 2. Architectural Takeaways

Watching this alongside Bubble and Selection sort will be highly educational for a few reasons:

* **The Best-Case Scenario:** While you decided to use a reverse-sorted worst-case array for your initial load (which is great), if a user were to restart the animation on an already-sorted array, Insertion Sort would fly through in exactly $n-1$ ticks, while Selection Sort would still churn through its full $O(n^2)$ loop. This algorithm is adaptive.
* **The "Ghost" Element:** Notice how `key = self.data[i]` temporarily removes a value from the logical flow, and we use a `while` loop to shift items `self.data[j + 1] = self.data[j]`. Visually, this will look like a "hole" or duplicate number sliding down the array until the `key` is finally dropped into place at `self.data[j + 1] = key`.
* **State Accuracy:** Just like the others, we are strictly passing `self.data.copy()` back to the Pygame view. If we didn't, the View would try to render the array while the `while` loop was still shifting elements in memory, causing visual tearing.

---

### Next Step

We have successfully built the three iterative algorithms (Bubble, Selection, Insertion). They all map cleanly to our `BaseSortAlgorithm` interface and properly yield our Go/Rust-inspired `SortResult` dataclass.

We only have one algorithm left for Brick 3: **Merge Sort**.

Because Merge Sort is a divide-and-conquer recursive algorithm, it requires a specialized approach. We will have to explicitly bubble up the `SortResult` through the recursive call stack to maintain our Pure Result Pattern contract.

Are you ready to tackle the complexity of Merge Sort to close out Brick 3?