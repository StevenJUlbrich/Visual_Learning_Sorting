# 03 DATA CONTRACTS - Canonical Source

This file is the single source of truth for algorithm/controller/view runtime contracts.
Indices must be unique.
Order has no semantic meaning.

## SortResult (Definitive)

```python
from enum import Enum, auto

class OpType(Enum):
    COMPARE = auto()  # Maps to T1 (150ms)
    SWAP = auto()     # Maps to T2 (400ms)
    SHIFT = auto()    # Maps to T2 (400ms)
    RANGE = auto()    # Maps to T3 (200ms) — active heap boundary or region emphasis
    TERMINAL = auto()  # Used for completion ticks
    FAILURE = auto()   # Used for explicit failure ticks

@dataclass(slots=True)
class SortResult:
    success: bool
    message: str
    operation_type: OpType  # Agent uses this for queue timing
    is_complete: bool = False
    array_state: list[int] | None = None
    highlight_indices: tuple[int, ...] | None = None
```

COMPARE → highlight only, no sprite position change
SWAP → exchange two sprite home slots with arc path, duration = T2
SHIFT → source/destination horizontal slide, duration = T2
RANGE → highlight contiguous range only, no sprite displacement; used by Heap Sort to
        show the active heap boundary (indices 0..heap_size-1) at the start of each extraction step
TERMINAL → no motion; apply completion styling

### highlight_indices rules

- Indices must be unique.
- Order does not affect rendering.
- Indices must exist within array_state bounds.

## Field Semantics

- `success`
  - `True`: normal algorithm progression or normal completion.
  - `False`: explicit algorithm/domain failure.
- `message`
  - Required for every yielded result.
  - Human-readable action/error text displayed in the panel message line (always visible per D-021).
  - Must include both index and value for clarity (e.g., `"Comparing index 0 (value 7) and index 2 (value 5)"`).
- `is_complete`
  - `True` only on normal terminal state.
  - Must not be used with `success=False`.
- `array_state`
  - Required on successful non-terminal and terminal ticks.
  - Optional (`None`) on failure ticks.
  - Failure ticks must include the most recent array_state if available.
  - Must be an immutable snapshot copy at yield time (`self.data.copy()`).
- `highlight_indices`
  - Optional tuple of indices to accent for current tick.
  - Empty/`None` means no accent.
  - If provided, all indices must be valid for `array_state` length.

## Valid State Combinations

- Progress tick: `success=True`, `is_complete=False`, `array_state!=None`.
- Completion tick: `success=True`, `is_complete=True`, `array_state!=None`.
- Failure tick: `success=False`, `is_complete=False`, `array_state` optional.

Invalid combinations are contract violations.

### Generator Completion Behavior

- After emitting a completion or failure tick, the generator must terminate naturally.
- No additional SortResult objects may be yielded after the terminal event.

## Tick Taxonomy

- Compare tick: highlights compared indices.
- Swap tick: highlights swapped indices and new snapshot.
- Shift/placement tick: highlights moved/placed indices and new snapshot.
- Range emphasis tick: highlights a contiguous range of indices; used by Heap Sort for active
  heap boundary display (range tuple expanded to indices 0..heap_size-1).
- Terminal completion tick: final sorted array snapshot with full-array highlight (`highlight_indices=tuple(range(size))`).
- Failure tick: explicit error state with message.

## Step Counter Definition

A panel step increments on every received `SortResult` where:

- `success=True`
- `is_complete=False`
- `operation_type` is **not** `OpType.RANGE`

RANGE ticks (T3) do not increment the step counter. They are a visual teaching aid that communicates the active heap boundary, not an algorithmic operation. Excluding them ensures Heap Sort's step count reflects only its actual comparisons and mutations, allowing fair cross-algorithm comparison.

Completion and failure ticks do not increment step count.

## Secondary Counters (Comparisons and Writes)

Each algorithm tracks its own `comparisons` and `writes` counters as instance attributes on `BaseSortAlgorithm`:

### Comparisons Counter

- `comparisons`: incremented by the algorithm each time a **data comparison** occurs (before yielding a compare tick).
- Not all COMPARE-typed ticks are data comparisons. Specifically, Insertion Sort's key-selection tick uses `OpType.COMPARE` for timing purposes but does **not** increment `comparisons` — selecting a key is a conceptual step, not a comparison between two data elements.
- Initialized to `0` in `__init__` and reset on re-instantiation (restart).

### Writes Counter

- `writes`: incremented by the algorithm to reflect the number of **individual array positions modified** by each mutation.
- Increment rules per operation type:
  - **Swap** (`OpType.SWAP`): `writes += 2` — a swap modifies two array positions.
  - **Shift** (`OpType.SHIFT`): `writes += 1` — a shift writes one element to an adjacent position.
  - **Placement** (`OpType.SHIFT` for insertion): `writes += 1` — placing a key writes one element.
- This matches standard algorithm analysis where array writes are counted individually, enabling accurate cross-algorithm comparison.
- Initialized to `0` in `__init__` and reset on re-instantiation (restart).

### Counter Display

The view layer reads `comparisons` and `writes` properties directly from the algorithm instance for display in the panel header metrics line.

## Generator Contract

Each algorithm generator must:

- Yield at every atomic operation.
- Yield exactly one terminal completion tick on success.
- Yield failure tick and stop on unrecoverable domain failure.
- Generators must terminate naturally after emitting the final tick.
- Avoid `yield from` for recursive failure bubbling where explicit checking is required by design.
- On empty input (`len(data) == 0`), yield exactly one failure tick (`success=False`, `message` explaining empty input) and stop. No completion tick is emitted.

## BaseSortAlgorithm Interface

```python
from abc import ABC, abstractmethod
from collections.abc import Generator

class BaseSortAlgorithm(ABC):
    def __init__(self, data: list[int], name: str, complexity: str):
        self.name = name
        self.complexity = complexity
        self.data = data.copy()
        self.size = len(self.data)
        self.comparisons: int = 0
        self.writes: int = 0

    @abstractmethod
    def sort_generator(self) -> Generator[SortResult, None, None]:
        ...
```
