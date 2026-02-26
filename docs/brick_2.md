Welcome back. I have full context on our architecture, our strict MVC layout, and the Go/Rust-inspired Pure Result Pattern we locked in. As your mentor, I love starting here because defining the core data contract and interfaces is what separates scalable software engineering from just writing scripts.

Let's start building **Brick 2: The Data Model & Interface**.

We are going to create two foundational pieces inside your `src/visualizer/models/` directory. First, the `SortResult` dataclass (our strict communication contract), and second, the `BaseSortAlgorithm` abstract class (our blueprint).

### 1. The Pure Result Contract (`SortResult`)

This object is the only way our algorithms will communicate with the Pygame controller. Because we are avoiding Python Exceptions for logic flow, this object must cleanly handle both the "happy path" (a successful tick) and the "failure path" (an error).

Here is the implementation:

```python
# src/visualizer/models/state.py
from dataclasses import dataclass

@dataclass(slots=True)
class SortResult:
    """
    The strict communication contract between the Model and the Controller.
    Enforces explicit success/failure states without relying on hidden Exception bubbling.
    """
    success: bool
    message: str
    is_complete: bool = False
    array_state: list[int] | None = None
    highlight_indices: tuple[int, ...] | None = None

```

**The Architectural "Why":**

* **`slots=True`:** In Python 3.13, adding `slots=True` to a dataclass prevents the dynamic creation of attributes at runtime and significantly reduces memory overhead. It makes the class rigid and strict, which perfectly mimics the safety of structs in Go or Rust.
* **Optional Fields:** By defaulting `array_state` and `highlight_indices` to `None`, we allow the algorithm to yield a lightweight failure state (e.g., `SortResult(success=False, message="Index out of bounds")`) without needing to mock up fake array data.

---

### 2. The Abstract Interface (`BaseSortAlgorithm`)

Now we need a blueprint that guarantees every sorting algorithm we write behaves exactly the same way. By using Python's `abc` (Abstract Base Classes) module, we force structural typing. If a future developer tries to add "Quick Sort" but forgets to implement the generator, the application will fail fast upon instantiation, rather than crashing halfway through a run.

```python
# src/visualizer/models/base.py
from abc import ABC, abstractmethod
from collections.abc import Generator
from .state import SortResult

class BaseSortAlgorithm(ABC):
    """
    The foundational interface for all sorting algorithms.
    Guarantees a unified API for the Controller to interact with.
    """
    
    def __init__(self, data: list[int], name: str):
        self.name = name
        # Create an independent copy to prevent mutating the shared initial worst-case array
        self.data = data.copy()
        self.size = len(self.data)

    @abstractmethod
    def sort_generator(self) -> Generator[SortResult, None, None]:
        """
        The core execution loop. 
        Must yield a SortResult for every atomic operation.
        Must explicitly bubble up failure states (success=False) if an error occurs.
        """
        pass

```

**The Architectural "Why":**

* **Data Copying:** Notice `self.data = data.copy()`. Because your project requires all four algorithms to sort the exact same worst-case array simultaneously, passing the raw list into four classes would cause them to mutate the same block of memory. Creating an internal copy upon initialization safely isolates the state for each algorithm panel.
* **The Generator Signature:** `Generator[SortResult, None, None]` tells the `pyright` type checker exactly what to expect: it yields a `SortResult`, accepts `None` as a send value, and returns `None` when exhausted. This strict typing ensures your agentic coding tools will auto-complete perfectly when we write the Controller.

---

With these two files, **Brick 2** is essentially complete. Your data model is strictly defined, and your polymorphic interface is locked in.

Would you like to move directly into **Brick 3** and implement the first concrete algorithm (like Bubble Sort) to test how we yield these `SortResult` states?