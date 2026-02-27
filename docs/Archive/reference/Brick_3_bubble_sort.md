Welcome to **Brick 3**. Now we get to see the architecture we designed in action.

Bubble Sort is the perfect starting point. It is strictly iterative, making it an ideal testbed for our `SortResult` contract and the generator "tick" system.

Here is the concrete implementation of your `BubbleSort` class.

### 1. The Bubble Sort Implementation

Create a new file in your models directory.

```python
# src/visualizer/models/bubble_sort.py
from collections.abc import Generator

from .base import BaseSortAlgorithm
from .state import SortResult

class BubbleSort(BaseSortAlgorithm):
    """
    Implements the Bubble Sort algorithm.
    Time Complexity: $O(n^2)$ worst-case.
    """
    
    def __init__(self, data: list[int]):
        # Pass the data and the explicit name up to the ABC
        super().__init__(data, name="Bubble Sort")

    def sort_generator(self) -> Generator[SortResult, None, None]:
        # Fail-Fast Boundary Check (The Failure Path)
        if self.size == 0:
            yield SortResult(
                success=False,
                message="Error: Cannot sort an empty array."
            )
            return

        # The Iterative Sort (The Happy Path)
        for i in range(self.size):
            swapped = False
            for j in range(0, self.size - i - 1):
                
                # TICK 1: Yield the comparison intent BEFORE swapping
                yield SortResult(
                    success=True,
                    message=f"Comparing elements {self.data[j]} and {self.data[j+1]}",
                    array_state=self.data.copy(),
                    highlight_indices=(j, j + 1)
                )

                # The Logic
                if self.data[j] > self.data[j + 1]:
                    self.data[j], self.data[j + 1] = self.data[j + 1], self.data[j]
                    swapped = True
                    
                    # TICK 2: Yield the result AFTER swapping
                    yield SortResult(
                        success=True,
                        message=f"Swapped to {self.data[j]} and {self.data[j+1]}",
                        array_state=self.data.copy(),
                        highlight_indices=(j, j + 1)
                    )
            
            # Optimization: If the inner loop did not swap, the array is fully sorted early
            if not swapped:
                break
        
        # FINAL TICK: The Completion State
        # Highlighting the entire array to signal completion
        yield SortResult(
            success=True,
            message="Bubble Sort Complete",
            is_complete=True,
            array_state=self.data.copy(),
            highlight_indices=tuple(range(self.size))
        )

```

### 2. Architectural Takeaways

Notice how exactly this fulfills your requirements for an educational portfolio piece:

* **The Atomic Tick:** A single iteration of the inner loop can take either *one* tick (if it just compares and moves on) or *two* ticks (if it compares, then swaps). This ensures the user physically sees the heavy cost of the swapping operations, perfectly illustrating the $O(n^2)$ complexity.
* **State Freezing:** Notice the constant use of `self.data.copy()`. In Python, lists are passed by reference. If we yielded `self.data` directly, the algorithm would continue sorting in the background, and by the time Pygame drew the frame, the array might look completely different. Yielding a `.copy()` takes a strict, frozen snapshot of memory at that exact microsecond.
* **The Error Boundary:** We start with an explicit check for an empty array, yielding our Go/Rust-style failure state. The Controller will see `success=False` on tick one and cleanly halt the panel without crashing the application.

---

### Next Steps

We have three algorithms left: **Selection Sort**, **Insertion Sort**, and **Merge Sort**.

Insertion and Selection are also iterative and will follow a very similar structure to Bubble Sort. Merge Sort is recursive and will require us to implement the manual error-bubbling we discussed when finalizing the Pure Result pattern.

Would you like me to tackle Selection/Insertion next, or jump straight into the deeper recursive complexity of Merge Sort?