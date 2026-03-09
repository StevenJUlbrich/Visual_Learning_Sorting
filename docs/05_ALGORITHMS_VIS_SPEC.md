# 05 ALGORITHMS VIS SPEC - Tick Taxonomy and Highlight Semantics

Scope: This spec locks algorithm visualization behavior for Bubble, Selection, Insertion, and Heap Sort.
Grounding sources: Data Contracts (03), Animation Spec (10), and planning notes.

## 1) Global Visualization Contract

- Every algorithm is a generator that yields `SortResult` ticks.
- A tick is an atomic visual event mapped to one algorithm operation/state update.
- Each successful non-terminal tick must provide:
  - `success=True`
  - `is_complete=False`
  - `array_state` snapshot copy
  - appropriate `highlight_indices`
- For non-empty input, each algorithm must end with exactly one completion tick:
  - `success=True`
  - `is_complete=True`
  - full-array highlight (`tuple(range(size))`)
- For empty input (`len(data) == 0`), the algorithm must yield exactly one failure tick (`success=False`) and stop. No completion tick is emitted.

## 2) Tick Taxonomy (Locked)

### T0 - Failure Tick

- Purpose: explicit domain failure signaling.
- Fields: `success=False`, `message` required, `is_complete=False`.
- Highlight: optional; default none.

### T1 - Compare Tick

- Purpose: show comparison intent before mutation.
- Fields: `success=True`, `is_complete=False`, copied `array_state`.
- Highlight: compared indices.

### T2 - Write/Mutation Tick

- Purpose: show array mutation after compare/decision.
- Includes swap, shift, placement operations.
- Fields: `success=True`, `is_complete=False`, copied `array_state`.
- Highlight: indices affected by mutation.

### T3 - Range Emphasis Tick (Heap Sort active boundary)

- Purpose: show the active unsorted heap region at the start of each extraction step.
- Fields: `success=True`, `is_complete=False`, copied `array_state`.
- Highlight: contiguous index range `0..heap_size-1` representing the live heap.
- No sprite displacement occurs on this tick.

### T4 - Completion Tick

- Purpose: terminal sorted state.
- Fields: `success=True`, `is_complete=True`, copied final `array_state`.
- Highlight: all indices.

## 3) Per-Algorithm Yield Requirements

### 3.1 Bubble Sort

Required sequence per inner iteration `j`:

1. `T1 Compare Tick` on `(j, j+1)` before any swap decision.
2. If swap needed, perform swap then emit `T2 Write/Mutation Tick` on `(j, j+1)`.

Additional rules:

- Early-exit optimization allowed (`swapped=False` pass).
- Must still emit one final `T4 Completion Tick`.

### 3.2 Selection Sort

Required sequence per outer index `i`:

1. During scan (`j = i+1..end`), emit `T1 Compare Tick` on `(min_idx, j)`.
2. If `min_idx != i`, perform swap then emit `T2 Write/Mutation Tick` on `(i, min_idx)`.

Additional rules:

- Search phase is comparison-heavy; swap phase is sparse and explicit.
- Must emit final `T4 Completion Tick`.

### 3.3 Insertion Sort

Required sequence per outer index `i`:

1. Emit key-selection tick (classified as `T1 compare context`) highlighting `(i,)`.
2. For each right-shift while condition holds, emit `T1 Compare Tick` on `(j, j+1)` before/with shift intent.
3. After insertion, emit `T2 Write/Mutation Tick` on placed index `(j+1,)`.

Additional rules:

- Shift operations must be visually represented as writes.
- Must emit final `T4 Completion Tick`.

### 3.4 Heap Sort

Heap Sort operates in two phases: **Build Max-Heap** and **Extraction**.

#### Phase 1 — Build Max-Heap

- Iterate `i` from `n // 2 - 1` down to `0`, calling sift-down for each node.
- Sift-down sequence for a node at index `i` with heap boundary `heap_size`:
  1. Identify the largest among `i`, left child `(2*i + 1)`, and right child `(2*i + 2)` if within bounds.
  2. For each child comparison, emit `T1 Compare Tick` on `(i, child_index)` (or `(largest, child_index)` as the running largest changes).
  3. If `largest != i`, perform swap then emit `T2 Write/Mutation Tick` on `(i, largest)`, then recurse sift-down from `largest`.

#### Phase 2 — Extraction

- Iterate `end` from `n - 1` down to `1`:
  1. Emit `T3 Range Emphasis Tick` on `tuple(range(0, end + 1))` to highlight the active heap boundary before the extraction swap.
  2. Swap root (`index 0`) with `end`, then emit `T2 Write/Mutation Tick` on `(0, end)`.
  3. Call sift-down from `index 0` with `heap_size = end`, yielding T1/T2 ticks per comparison and swap as in Phase 1.

Additional rules:

- Sift-down must be implemented iteratively or as an inner generator; `yield from` may be used for a sift-down sub-generator provided failure bubbling remains explicit.
- Must emit final `T4 Completion Tick`.

## 4) Highlight Semantics (Locked)

### Compare Highlights

- Compare operations highlight exactly the indices being compared.
- Bubble: `(j, j+1)`.
- Selection: `(min_idx, j)`.
- Insertion shift-compare: `(j, j+1)`.
- Heap sift-down compare: `(parent_idx, child_idx)` or `(largest, child_idx)` as the running largest updates.

### Swap/Write Highlights

- Swap ticks highlight both swapped indices.
- Shift ticks highlight source/destination pair or destination index (consistent per algorithm implementation).
- Placement ticks highlight the insertion/placement index.

### Heap Boundary Range Highlights

- Heap extraction range emphasis highlights `tuple(range(0, heap_size))`.
- This shows the learner exactly which portion of the array is still an active max-heap before each root extraction.

## 5) Heap Sort Visual Phasing Decision

Decision: **Two-phase visual distinction is required in v1.**

Required behavior in v1:

- Heap Sort must emit T3 range emphasis ticks at the start of every extraction step to make the shrinking heap boundary visible.
- T1/T2 ticks during sift-down communicate individual comparisons and swaps within the heap.
- No separate auxiliary row animation is used; all Heap Sort motion is in-place on the main array row.

Rationale:

- The shrinking boundary communicates the core O(n log n) behavior of heap extraction.
- Range highlighting preserves clarity without introducing additional drawing complexity.
- In-place motion is visually consistent with Bubble and Selection Sort panels.

## 6) Consistency and QA Hooks

- Every yield message must describe the operation in learner-friendly text.
  - Examples: `"Comparing index 0 (7) and index 2 (5)"`, `"Swapping root 7 with end 1 — extracting max"`, `"Active heap: indices 0–4"`.
- No tick may expose mutable `self.data` directly; snapshots must be copied.
- Completion tick must represent a fully sorted array.
- Tick density varies between phases; the dense sift-down phase and sparse extraction phase are intentional and instructional.

## 7) Operation → Animation Mapping

- COMPARE
  - Highlight compared indices.
  - No sprite movement.

- SWAP
  - Two sprites exchange horizontal positions.
  - Swap animation uses arc motion defined in Animation Spec.

- SHIFT
  - Sprite moves horizontally into a new index position.

- RANGE
  - Highlight contiguous range only (active heap boundary).
  - No sprite displacement.

- TERMINAL
  - No motion.
  - Entire array receives completion color.
