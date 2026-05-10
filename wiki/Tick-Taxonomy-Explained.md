# Tick Taxonomy Explained

Every algorithm in this project is a Python generator that yields `SortResult` objects — typed operation records called "ticks." The tick taxonomy is the classification system that tells the Controller how long to wait and tells the View how to animate. Understanding ticks is the key to understanding how the entire pipeline works.

## The SortResult Contract

```python
@dataclass(slots=True)
class SortResult:
    success: bool                              # True for normal operations, False for errors
    message: str                               # Human-readable description, always required
    operation_type: OpType                     # Which tick type (see below)
    is_complete: bool = False                  # True only on the final completion tick
    array_state: list[int] | None = None       # Snapshot of the array AFTER this operation
    highlight_indices: tuple[int, ...] | None = None  # Which elements to highlight
```

Every tick carries a complete `array_state` snapshot — a copy of the array at that point in time. This is how the Controller detects what changed: it compares the previous state to the new state and computes which sprites need to move. The snapshot must be a copy, never a reference to the mutable working array, because the generator continues modifying the array after yielding.

## The Six Operation Types

### T0 — FAILURE

Signals an unrecoverable domain error, such as an empty input array. The generator yields one failure tick and terminates. The Controller deactivates only the failing panel — the other three algorithms continue. No counter increments.

### T1 — COMPARE (150ms)

Signals an evaluation step. The Controller displays the tick for 150ms (or 100ms under Heap Sort sift-down cadence). The `highlight_indices` tuple identifies which elements are being compared, and the View renders them in orange.

T1 ticks have algorithm-specific visual behavior:

- **Bubble Sort**: Both sprites in the compared pair lift vertically (50px), creating a brief "examination" moment before a potential swap.
- **Selection Sort**: Highlight-only — no sprite movement. The message identifies both the scan cursor and the current minimum.
- **Insertion Sort (key selection)**: Single-index highlight `(i,)`. The key sprite lifts to the compare lane and stays elevated across all subsequent ticks until placement. This tick does NOT increment `self.comparisons` — it's a conceptual step, not a data comparison.
- **Insertion Sort (compare-during-shift)**: Two-index highlight `(j, j+1)`. The baseline element flashes orange while the key remains elevated above.
- **Heap Sort**: Two-index highlight comparing parent with child during sift-down.

The comparisons counter increments on every T1 tick except Insertion Sort key-selection. This exception is specified by D-038 and is mechanically verified by the counter target: Insertion Sort on `[4, 7, 2, 6, 1, 5, 3]` must produce exactly 17 comparisons. If key-selection ticks were counted, the total would be 23.

### T2 — SWAP (400ms) and SHIFT (400ms)

Both signal a mutation — the array has changed. The `array_state` snapshot reflects the new arrangement. The Controller displays the tick for 400ms (or 250ms under Heap sift-down cadence), and the View animates sprites moving to their new positions.

**SWAP** involves two elements exchanging positions. The View uses arc motion — one sprite arcs up, the other arcs down — so the learner can visually track which element went where. Each swap increments `self.writes` by 2 (two array positions modified).

**SHIFT** is used by Insertion Sort for single-element movements: shifting an element one position right (1 write) or placing the key into its sorted position (1 write).

The distinction matters for counter accuracy: a Bubble Sort swap costs 2 writes, while an Insertion Sort shift costs 1 write. This is why Selection Sort (5 swaps = 10 writes) is dramatically lower than Bubble Sort (13 swaps = 26 writes) despite having more comparisons.

### T3 — RANGE (200ms)

A non-mutating visual aid. No sprite movement, no array mutation, no counter increments, no step counter increment. The `array_state` is identical to the previous tick's. Used exclusively by Heap Sort for two purposes:

**Boundary Emphasis** — A contiguous range `(0, 1, ..., heap_size-1)` highlighting the active heap region before each extraction. The View renders this as a staggered left-to-right sweep (120ms sweep window + 80ms hold). Message starts with `"Active heap"`.

**Logical Tree Highlight** — A non-contiguous tuple `(parent, left_child, right_child)` showing the tree relationship being evaluated during sift-down. The View renders this as a simultaneous flash on all highlighted nodes. Message starts with `"Evaluating tree level"`.

The two variants are distinguished by message prefix (D-081), not by highlight-set contiguity. This is because at parent index 0, the Logical Tree tuple `(0, 1, 2)` is structurally identical to a 3-element Boundary tuple.

T3 ticks are excluded from the step counter (D-041). This ensures Heap Sort's step count (35) reflects only its actual comparisons and mutations, enabling fair cross-algorithm comparison. The 6 boundary T3 ticks and 11 logical-tree T3 ticks are visual teaching aids.

### TERMINAL — Completion

The final tick, yielded once when the sort is complete. Carries the fully sorted `array_state` and `highlight_indices=tuple(range(size))` (full-array highlight). The View transitions all sprites to completion green and the panel background to muted green. Stats freeze. No counter increments.

### FAILURE — Error

Yielded on domain errors (empty input). Carries a descriptive message. The generator terminates immediately after. No array state is required.

## How Ticks Drive the Race

The timing assignments are what create the racing behavior. Consider two algorithms on the same input:

- Selection Sort does 21 comparisons (21 × 150ms = 3,150ms) and 5 swaps (5 × 400ms = 2,000ms) = 5,150ms total
- Bubble Sort does 20 comparisons (20 × 150ms = 3,000ms) and 13 swaps (13 × 400ms = 5,200ms) = 8,200ms total

Bubble Sort takes ~60% longer despite doing fewer comparisons, because it does far more swaps. The visualizer makes this concrete: learners see Bubble Sort still swapping while Selection Sort has already finished.

## Counter Semantics Summary

| Counter | Incremented by | NOT incremented by |
|---------|---------------|-------------------|
| `comparisons` | T1 data comparisons | T1 key-selection (Insertion Sort), T2, T3, TERMINAL, FAILURE |
| `writes` | T2 SWAP (+2), T2 SHIFT (+1) | T1, T3, TERMINAL, FAILURE |
| `steps` | T1, T2 | T3 (excluded), TERMINAL, FAILURE |

The `writes` counter counts individual array positions modified, not operations. A swap modifies two positions (both elements move), so it counts as 2 writes. This matches standard algorithm analysis (Knuth, Sedgewick) and enables learners to make accurate cross-algorithm comparisons.
