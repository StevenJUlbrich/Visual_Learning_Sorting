# 05 ALGORITHMS VIS SPEC - Tick Taxonomy and Highlight Semantics

Scope: This spec locks algorithm visualization behavior for Bubble, Selection, Insertion, and Merge Sort.
Grounding sources: `docs/reference/Brick_3_bubble_sort.md`, `docs/reference/Brick_3_merge_sort.md`, and `docs/Sorting_Algorithm_Visualizer_Planning.md`.

## 1) Global Visualization Contract

- Every algorithm is a generator that yields `SortResult` ticks.
- A tick is an atomic visual event mapped to one algorithm operation/state update.
- Each successful non-terminal tick must provide:
  - `success=True`
  - `is_complete=False`
  - `array_state` snapshot copy
  - appropriate `highlight_indices`
- Each algorithm must end with exactly one completion tick:
  - `success=True`
  - `is_complete=True`
  - full-array highlight (`tuple(range(size))`)
- Empty input boundary must yield failure tick (`success=False`) and stop.

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

### T3 - Range Emphasis Tick (Merge-Specific)

- Purpose: show active subarray segment being merged.
- Fields: `success=True`, `is_complete=False`, copied `array_state`.
- Highlight: contiguous index range `left..right`.

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

1. Emit key-selection tick (classified as `T2 Write/Mutation Context`) highlighting `(i,)`.
2. For each right-shift while condition holds, emit `T1 Compare Tick` on `(j, j+1)` before/with shift intent.
3. After insertion, emit `T2 Write/Mutation Tick` on placed index `(j+1,)`.

Additional rules:

- Shift operations must be visually represented as writes.
- Must emit final `T4 Completion Tick`.

### 3.4 Merge Sort

Required recursive sequence:

1. Recursively process left and right halves.
2. At start of each merge operation, emit `T3 Range Emphasis Tick` on full range `left..right`.
3. During merge loop:
   - emit `T1 Compare Tick` for current merge decision.
   - perform write into main array, then emit `T2 Write/Mutation Tick` on destination index.
4. For remaining elements in either side, each write emits `T2 Write/Mutation Tick`.

Additional rules:

- Recursive bubbling must remain explicit and contract-driven.
- Must emit final `T4 Completion Tick`.

## 4) Highlight Semantics (Locked)

### Compare Highlights

- Compare operations highlight exactly the indices being compared.
- Bubble: `(j, j+1)`.
- Selection: `(min_idx, j)`.
- Insertion shift-compare: `(j, j+1)`.
- Merge compare: destination-focused index allowed (per Brick 3 implementation), but must remain consistent within algorithm.

### Swap/Write Highlights

- Swap ticks highlight both swapped indices.
- Shift ticks highlight source/destination pair or destination index (consistent per algorithm implementation).
- Placement ticks highlight the insertion/placement index.

### Merge-Range Highlights

- Merge range emphasis highlights a contiguous tuple `tuple(range(left, right + 1))`.
- This serves as subarray emphasis equivalent to bracket semantics in v1.

## 5) Merge Bracket/Subarray Emphasis Decision

Decision: **Literal bracket graphics are not required in v1.**

Required behavior in v1:

- Merge Sort must emit explicit range emphasis ticks (`T3`) for each merge segment.
- View layer must render this via contiguous highlighted indices.

Rationale:

- Planning notes value bracket-like subarray emphasis.
- Brick 3 merge implementation already encodes this cleanly through `highlight_indices` range ticks.
- Range highlighting preserves clarity without introducing additional drawing complexity.

## 6) Consistency and QA Hooks

- Every yield message must describe the operation in learner-friendly text.
- No tick may expose mutable `self.data` directly; snapshots must be copied.
- Completion tick must represent a fully sorted array (selection-sort regression guard).
- Tick density may vary by algorithm; this variance is intentional and instructional.
