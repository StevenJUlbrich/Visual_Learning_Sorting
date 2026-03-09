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
- Duration: 150ms simulated cost.
- No sprite position change.

### T2 - Write/Mutation Tick

- Purpose: show array mutation after compare/decision.
- Includes swap, shift, placement operations.
- Fields: `success=True`, `is_complete=False`, copied `array_state`.
- Highlight: indices affected by mutation.
- Duration: 400ms simulated cost.

### T3 - Range Emphasis Tick (Heap Sort active boundary)

- Purpose: show the active unsorted heap region at the start of each extraction step.
- Fields: `success=True`, `is_complete=False`, copied `array_state`.
- Highlight: contiguous index range `0..heap_size-1` representing the live heap.
- Duration: 200ms simulated cost.
- No sprite displacement occurs on this tick.
- Does **not** increment the panel step counter (it is a visual teaching aid, not an algorithmic operation).

### T4 - Completion Tick

- Purpose: terminal sorted state.
- Fields: `success=True`, `is_complete=True`, copied final `array_state`.
- Highlight: all indices.

## 3) Complexity Labels (Locked)

Each algorithm exposes a `complexity` string representing its **worst-case** time complexity. These are worst-case because the fixed input `[7, 6, 5, 4, 3, 2, 1]` triggers worst-case behavior for the O(n²) algorithms.

- Bubble Sort: `"O(n²)"`
- Selection Sort: `"O(n²)"`
- Insertion Sort: `"O(n²)"`
- Heap Sort: `"O(n log n)"`

## 4) Per-Algorithm Yield Requirements

### 4.1 Bubble Sort

Required sequence per inner iteration `j`:

1. `T1 Compare Tick` on `(j, j+1)` before any swap decision.
2. If swap needed, perform swap then emit `T2 Write/Mutation Tick` on `(j, j+1)`.

Additional rules:

- Early-exit optimization allowed (`swapped=False` pass).
- Must still emit one final `T4 Completion Tick`.

Counter behavior:

- `self.comparisons += 1` before every T1 compare tick.
- `self.writes += 2` before every T2 swap tick (a swap modifies two array positions).

### 4.2 Selection Sort

Required sequence per outer index `i`:

1. During scan (`j = i+1..end`), emit `T1 Compare Tick` on `(min_idx, j)`.
2. If `min_idx != i`, perform swap then emit `T2 Write/Mutation Tick` on `(i, min_idx)`.

Additional rules:

- Search phase is comparison-heavy; swap phase is sparse and explicit.
- Must emit final `T4 Completion Tick`.

Counter behavior:

- `self.comparisons += 1` before every T1 compare tick.
- `self.writes += 2` before every T2 swap tick.

### 4.3 Insertion Sort

Insertion Sort requires a precise tick sequence to correctly visualize the key-selection, comparison, shifting, and placement phases.

Required sequence per outer index `i` (from `1` to `n-1`):

#### Step 1 — Key Selection

- Emit `T1 Compare Tick` on `(i,)` highlighting the selected key.
- This tick does **not** increment `self.comparisons` — it is a key-selection signal, not a data comparison.
- The key sprite begins its visual lift (see Animation Spec Section 5.2).

#### Step 2 — Compare-and-Shift Loop

Starting from `j = i - 1`, while `j >= 0` and `arr[j] > key`:

1. Emit `T1 Compare Tick` on `(j, j+1)` — shows the comparison between `arr[j]` and the key. Increment `self.comparisons += 1` before yielding.
2. Perform the shift: `arr[j+1] = arr[j]`. Emit `T2 Write/Mutation Tick` (OpType.SHIFT) on `(j, j+1)` — shows the element at `j` sliding right to `j+1`. Increment `self.writes += 1` before yielding.
3. Decrement `j`.

The lifted key sprite remains elevated and stationary during all compare and shift ticks.

#### Step 3 — Terminating Comparison (when loop exits by condition)

If the loop exits because `arr[j] <= key` (not because `j < 0`), emit one final `T1 Compare Tick` on `(j, j+1)` — shows the comparison that determined the insertion point. Increment `self.comparisons += 1`. This tells the learner *why* the key is placed here: the element at `j` is not greater than the key.

If the loop exits because `j < 0` (key is the smallest element), no terminating comparison tick is emitted — there is no element to compare against.

#### Step 4 — Placement

- Place the key: `arr[j+1] = key`. Emit `T2 Write/Mutation Tick` (OpType.SHIFT) on `(j+1,)` — shows the key dropping into its sorted position. Increment `self.writes += 1` before yielding.
- The key sprite eases back down from its elevated position to the target slot.

#### Worked Example: `[7, 6, 5, 4, 3, 2, 1]`, pass `i=2`

Array before: `[6, 7, 5, 4, 3, 2, 1]` (after i=1 completed).

1. **Key-selection T1** on `(2,)`: `"Selecting key: 5 at index 2"`. Key 5 lifts. (No comparisons increment.)
2. **Compare T1** on `(1, 2)`: `"Comparing index 1 (value 7) with key 5"`. comparisons → 1.
3. **Shift T2** on `(1, 2)`: `"Shifting 7 from index 1 to index 2"`. Array → `[6, 7, 7, 4, 3, 2, 1]` (logically; 7 moves right). writes → 1.
4. **Compare T1** on `(0, 1)`: `"Comparing index 0 (value 6) with key 5"`. comparisons → 2.
5. **Shift T2** on `(0, 1)`: `"Shifting 6 from index 0 to index 1"`. Array → `[6, 6, 7, 4, 3, 2, 1]`. writes → 2.
6. Loop exits: `j < 0`. No terminating comparison.
7. **Placement T2** on `(0,)`: `"Placing key 5 at index 0"`. Array → `[5, 6, 7, 4, 3, 2, 1]`. writes → 3. Key drops.

Additional rules:

- Must emit final `T4 Completion Tick`.

### 4.4 Heap Sort

Heap Sort operates in two phases: **Build Max-Heap** and **Extraction**.

#### Phase 1 — Build Max-Heap

- Iterate `i` from `n // 2 - 1` down to `0`, calling sift-down for each node.
- Sift-down sequence for a node at index `i` with heap boundary `heap_size`:

**Sift-down tick-by-tick procedure:**

1. Set `largest = i`.
2. Compute `left = 2*i + 1` and `right = 2*i + 2`.
3. If `left < heap_size`:
   - Emit `T1 Compare Tick` on `(largest, left)` — compares current largest with left child. Increment `self.comparisons += 1`.
   - If `arr[left] > arr[largest]`, update `largest = left`.
4. If `right < heap_size`:
   - Emit `T1 Compare Tick` on `(largest, right)` — compares current largest with right child. **Note:** if `largest` was updated to `left` in step 3, this comparison is now between the left child and the right child, which is correct (finding the larger of the two children to potentially swap with the parent). Increment `self.comparisons += 1`.
   - If `arr[right] > arr[largest]`, update `largest = right`.
5. If `largest != i`:
   - Perform swap `arr[i], arr[largest] = arr[largest], arr[i]`.
   - Emit `T2 Write/Mutation Tick` on `(i, largest)`. Increment `self.writes += 2`.
   - Continue sift-down from `largest` (repeat from step 1 with `i = largest`).

**Note on `[7, 6, 5, 4, 3, 2, 1]`:** This input is already a valid max-heap (each parent is greater than both children). Phase 1 will emit only comparison ticks with no swaps. This is expected behavior — it demonstrates that the build phase verifies the heap property, even when no repairs are needed.

#### Phase 2 — Extraction

- Iterate `end` from `n - 1` down to `1`:
  1. Emit `T3 Range Emphasis Tick` on `tuple(range(0, end + 1))` to highlight the active heap boundary before the extraction swap.
  2. Swap root (`index 0`) with `end`, then emit `T2 Write/Mutation Tick` on `(0, end)`. Increment `self.writes += 2`.
  3. Call sift-down from `index 0` with `heap_size = end`, yielding T1/T2 ticks per comparison and swap as described above.

Additional rules:

- Sift-down must be implemented iteratively or as an inner generator; `yield from` may be used for a sift-down sub-generator provided failure bubbling remains explicit.
- Must emit final `T4 Completion Tick`.

## 5) Highlight Semantics (Locked)

### Compare Highlights

- Compare operations highlight exactly the indices being compared.
- Bubble: `(j, j+1)`.
- Selection: `(min_idx, j)`.
- Insertion compare-during-shift: `(j, j+1)` — the element at `j` is compared against the lifted key (visually above the array).
- Insertion key-selection: `(i,)` — single-index highlight on the key being extracted.
- Heap sift-down compare: `(largest, child_idx)` — this reflects the running `largest` value, so when comparing the right child, the highlight may show `(left_child, right_child)` if the left child was already found to be larger than the parent.

### Swap/Write Highlights

- Swap ticks highlight both swapped indices.
- Shift ticks highlight the source and destination pair `(j, j+1)`.
- Placement ticks highlight the single destination index `(j+1,)`.

### Heap Boundary Range Highlights

- Heap extraction range emphasis highlights `tuple(range(0, heap_size))`.
- This shows the learner exactly which portion of the array is still an active max-heap before each root extraction.

## 6) Heap Sort Visual Phasing Decision

Decision: **Two-phase visual distinction is required in v1.**

Required behavior in v1:

- Heap Sort must emit T3 range emphasis ticks at the start of every extraction step to make the shrinking heap boundary visible.
- T1/T2 ticks during sift-down communicate individual comparisons and swaps within the heap.
- No separate auxiliary row animation is used; all Heap Sort motion is in-place on the main array row.

Rationale:

- The shrinking boundary communicates the core O(n log n) behavior of heap extraction.
- Range highlighting preserves clarity without introducing additional drawing complexity.
- In-place motion is visually consistent with Bubble and Selection Sort panels.

## 7) Consistency and QA Hooks

- Every yield message must describe the operation in learner-friendly text.
  - Include both index and value for clarity: `"Comparing index 0 (value 7) and index 2 (value 5)"`.
  - Heap extraction: `"Swapping index 0 (value 7) with index 6 (value 1) — extracting max"`.
  - Range emphasis: `"Active heap: indices 0–4"`.
  - Key selection: `"Selecting key: 5 at index 2"`.
  - Shift: `"Shifting 7 from index 1 to index 2"`.
  - Placement: `"Placing key 5 at index 0"`.
- No tick may expose mutable `self.data` directly; snapshots must be copied.
- Completion tick must represent a fully sorted array.
- Tick density varies between phases; the dense sift-down phase and sparse extraction phase are intentional and instructional.

## 8) Operation → Animation Mapping

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

## 9) Pedagogical Notes

### What the Learner Should Observe

**Bubble Sort:** The largest unsorted element "bubbles" to the right on each pass. The learner should notice that later passes get shorter as the right side of the array becomes sorted. With reverse-sorted input, every comparison triggers a swap — this is worst-case behavior.

**Selection Sort:** The algorithm scans the entire unsorted portion to find the minimum, then places it with a single swap. The learner should observe many comparisons followed by one swap (or no swap if the minimum is already in position). Despite being O(n²), Selection Sort has very few writes — for `[7, 6, 5, 4, 3, 2, 1]`, only 3 swaps.

**Insertion Sort:** Elements are "picked up" from the unsorted portion and inserted into the correct position within the growing sorted portion. The learner should observe the key lifting, elements sliding right to make room, and the key dropping into place. With reverse-sorted input, every key must travel to position 0 — worst-case behavior.

**Heap Sort:** Two distinct phases. Phase 1 (Build Max-Heap) verifies and repairs the heap property — for this input, the array is already a valid max-heap so only comparisons occur. Phase 2 (Extraction) repeatedly moves the root (maximum) to the sorted region and repairs the heap. The learner should observe the orange heap boundary shrinking by one element per extraction, directly illustrating why the sorted region grows from the right.

### About the Race Outcome

The race outcome reflects operation costs for the specific input `[7, 6, 5, 4, 3, 2, 1]` at n=7. At this small size, constant factors and per-operation costs dominate over asymptotic complexity differences (log₂ 7 ≈ 2.8, so n log n ≈ 19.6 vs n² = 49 — less than a 3x gap). Selection Sort may win the race because it performs very few swaps for this input, despite being O(n²). Heap Sort's O(n log n) advantage becomes decisive at larger array sizes, which are out of scope for v1.
