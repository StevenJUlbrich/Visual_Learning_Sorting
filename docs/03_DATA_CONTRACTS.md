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
    RANGE = auto()    # Maps to T3 (200ms) — non-mutating visual aid; accent color only, no sprite movement
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
RANGE → **non-mutating visual aid**; refreshes accent color on highlighted indices only.
        Invariants:
        - No sprite displacement (no `exact_x`/`exact_y` target changes).
        - No `array_state` mutation — the snapshot is identical to the prior tick's.
        - No `writes` or `comparisons` counter increments.
        - Does not increment the panel step counter (see Step Counter Definition).
        Used by Heap Sort for two purposes:
        (a) Boundary emphasis: contiguous range 0..heap_size-1, rendered as a left-to-right sweep
            (see Animation Spec Section 5.3.1). Refreshes the orange accent on the active heap region.
        (b) Logical Tree Highlight: non-contiguous parent-child triangle during sift-down,
            rendered as a simultaneous accent flash on the parent and its children.
        See "OpType.RANGE — Heap Sort Highlight Variants" below for full rules
TERMINAL → no motion; apply completion styling

### highlight_indices rules

- Indices must be unique.
- Order does not affect rendering.
- Indices must exist within array_state bounds.

### OpType.RANGE — Heap Sort Highlight Variants

Heap Sort emits two distinct variants of `OpType.RANGE` ticks. Both use the same `OpType` enum value and the same accent color (orange), but differ in highlight pattern and purpose.

**Non-mutation guarantee (applies to both variants):** A RANGE tick is a pure visual aid. It must not modify `self.data`, must not change any sprite's target position, must not increment `self.comparisons` or `self.writes`, and must not increment the panel step counter. The `array_state` snapshot in a RANGE tick must be **identical** to the snapshot from the immediately preceding tick — if the View or a test harness detects a difference, it is a contract violation. The Controller consumes the tick's simulated cost (200ms standard, or 130ms under sift-down cadence) for race timing, but the cost represents **display time**, not computational work.

#### Variant A — Boundary Emphasis

- **Purpose:** Show the active heap region before each extraction swap.
- **highlight_indices:** `tuple(range(0, heap_size))` — a contiguous range.
- **When emitted:** Once per extraction step, before the extraction swap.
- **Active sift-down parent rule:** If a boundary T3 tick fires while a sift-down is conceptually in progress (e.g., during Phase 1 build or between extraction steps), the parent node currently being sifted must be **included** in the highlight set even if boundary semantics alone would not require it. In practice, boundary ticks fire *before* sift-down begins within each extraction step, so this rule serves as a safety contract: **the highlight set must always contain the sift-down parent if one is active**. This ensures the "active node" is never visually lost during the boundary-to-sift-down transition.

#### Variant B — Logical Tree Highlight

- **Purpose:** Show the parent-child triangle being evaluated during sift-down.
- **highlight_indices:** Non-contiguous tuple of `(parent, left_child, right_child)` where children exist within the heap boundary. Example: `(1, 3, 4)`.
- **When emitted:** Before each sift-down level's comparisons, in both Phase 1 (Build Max-Heap) and Phase 2 (Extraction sift-down).
- **Active sift-down parent rule:** The sift-down parent index (`i`) must **always** be the first member of the highlight tuple. This is a contract invariant — the parent is the anchor of the tree relationship being communicated. If only one child exists (e.g., a left child with no right sibling), the tuple is `(parent, left_child)`. The parent is never omitted.

#### Distinguishing the two variants

The View layer distinguishes Boundary from Logical Tree T3 ticks by the **contiguity** of the highlight set:

- If `highlight_indices == tuple(range(min_idx, max_idx + 1))` (contiguous from 0), it is a Boundary Emphasis tick → render with sweep (Section 5.3.1 of Animation Spec).
- Otherwise (non-contiguous, or not starting at 0), it is a Logical Tree Highlight tick → render as simultaneous accent flash.

This distinction is deterministic and requires no additional metadata on `SortResult`.

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

- Compare tick: highlights compared indices. Algorithm-specific semantics:
  - **Bubble Sort:** T1 on `(j, j+1)` — compares adjacent pair. Message: `"Comparing index {j} (value {arr[j]}) and index {j+1} (value {arr[j+1]})"`.
  - **Selection Sort (Scan phase):** T1 on `(min_idx, j)` — compares scan cursor `j` against the running minimum `min_idx`. The `highlight_indices` always includes both the current minimum and the element under evaluation, so the learner can track the minimum pointer as it moves through the unsorted region. Message must reference the current minimum: `"Comparing index {j} (value {arr[j]}) with current min {arr[min_idx]} at index {min_idx}"`. When a new minimum is found, the message should note: `"New minimum: {arr[j]} at index {j}"`.
  - **Insertion Sort (key-selection):** T1 on `(i,)` — single-index highlight, no data comparison. Message: `"Selecting key: {arr[i]} at index {i}"`.
  - **Insertion Sort (compare-during-shift):** T1 on `(j, j+1)` — compares element against lifted key. Message: `"Comparing index {j} (value {arr[j]}) with key {key}"`.
  - **Heap Sort (sift-down):** T1 on `(largest, child_idx)` — compares parent/largest with child. Message: `"Comparing index {largest} (value {arr[largest]}) and index {child_idx} (value {arr[child_idx]})"`.
- Swap tick: highlights swapped indices and new snapshot.
- Shift/placement tick: highlights moved/placed indices and new snapshot.
- Range emphasis tick: **non-mutating visual aid** — no sprite movement, no array mutation, no counter increments. Used by Heap Sort for two highlight variants:
  - Boundary emphasis: contiguous range `0..heap_size-1` — refreshes orange accent on the active heap region via left-to-right sweep.
  - Logical Tree Highlight: non-contiguous parent-child triangle `(parent, left, right)` — refreshes orange accent on the tree relationship under evaluation. The sift-down parent is always included.
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
- **Counting unit: array positions, not operations.** A single swap *operation* modifies two array positions, so it counts as 2 writes. A single shift *operation* modifies one array position, so it counts as 1 write. This per-position granularity matches standard algorithm analysis (e.g., Knuth, Sedgewick) and enables the learner to make accurate cross-algorithm comparisons from the metrics line.

#### Per-Operation Increment Rules

| Operation | OpType | `writes` Increment | Rationale |
| --- | --- | --- | --- |
| **Swap** | `SWAP` | `+= 2` | Both `arr[i]` and `arr[j]` are overwritten |
| **Shift** | `SHIFT` | `+= 1` | `arr[j+1] = arr[j]` — one position written |
| **Placement** | `SHIFT` | `+= 1` | `arr[j+1] = key` — one position written |
| **Compare** | `COMPARE` | `+= 0` | Read-only operation — no array mutation |
| **Range** | `RANGE` | `+= 0` | Non-mutating visual aid — no array mutation |
| **Terminal** | `TERMINAL` | `+= 0` | No mutation on completion or failure |

#### Per-Algorithm Expected Write Totals for `[4, 7, 2, 6, 1, 5, 3]`

These expected values serve as QA verification anchors for the default dataset:

| Algorithm | Write Operations | Calculation | Expected `writes` |
| --- | --- | --- | --- |
| **Bubble Sort** | 8 swaps (with early exit) | 8 × 2 = 16 | **16** |
| **Selection Sort** | 5 swaps | 5 × 2 = 10 | **10** |
| **Insertion Sort** | 13 shifts + 6 placements | 13 × 1 + 6 × 1 = 19 | **19** |
| **Heap Sort** | 3 build swaps + 6 extraction swaps + sift-down swaps | varies by sift-down depth | **~22** (exact count depends on sift-down paths) |

**Note:** These totals are derived from the specific input `[4, 7, 2, 6, 1, 5, 3]`. Different inputs produce different write counts. The values above are for QA regression testing, not general algorithm properties.

#### Invariants

- `writes` is incremented by the algorithm model **before** yielding the corresponding `SortResult`. The counter value visible to the View at render time already includes the current tick's writes.
- `writes` must never be incremented on COMPARE, RANGE, TERMINAL, or FAILURE ticks.
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
