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
- No **logical** position change — the `array_state` snapshot is unchanged from the prior tick. However, algorithm-specific **temporary visual offsets** (e.g., Bubble Sort compare-lift) may apply during the T1 duration. These offsets are View-layer animations that return to baseline by tick end; they do not alter slot assignments or home positions.

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

Each algorithm exposes a `complexity` string representing its **worst-case** time complexity.

- Bubble Sort: `"O(n²)"`
- Selection Sort: `"O(n²)"`
- Insertion Sort: `"O(n²)"`
- Heap Sort: `"O(n log n)"`

## 4) Per-Algorithm Yield Requirements

### 4.1 Bubble Sort

Required sequence per inner iteration `j`:

1. `T1 Compare Tick` on `(j, j+1)` before any swap decision. The View applies a **compare-lift** to the adjacent pair: both sprites at indices `j` and `j+1` ease upward from `home_y` to `home_y - compare_lift_offset` over the first half of the T1 duration, hold briefly, then ease back to `home_y` by tick end (see Animation Spec Section 5.1.1). This temporary vertical isolation makes every comparison visually readable — even comparisons that do not result in a swap.
2. If swap needed, perform swap then emit `T2 Write/Mutation Tick` on `(j, j+1)`. The swap arc motion begins from the baseline (`home_y`), not from the lifted position — the compare-lift has already returned to baseline before the T2 tick starts.
3. If no swap needed, the algorithm advances to the next `j`. The compare-lift's return to baseline serves as the visual "release" signal that the pair was inspected but left in place.

Additional rules:

- Early-exit optimization allowed (`swapped=False` pass).
- Must still emit one final `T4 Completion Tick`.
- The compare-lift is a **View-layer animation only**. The algorithm model does not track lift state — it emits standard T1 ticks. The View recognizes Bubble Sort T1 ticks by the panel's algorithm identity and applies the lift choreography automatically.

#### Compare-Lift Motion Contract

- **Lift offset:** `compare_lift_offset = panel_height * 0.05` (proportional). This is intentionally smaller than Insertion Sort's `lift_offset` (`0.06`) to maintain visual hierarchy — the Insertion Sort lift is a sustained, prominent displacement across multiple ticks, while the Bubble Sort compare-lift is a brief pulse within a single T1 tick.
- **Timing within the 150ms T1 duration:**
  - `0–60ms` (40%): both sprites ease upward from `home_y` to `home_y - compare_lift_offset`.
  - `60–100ms` (27%): hold at lifted position (comparison is visually prominent).
  - `100–150ms` (33%): both sprites ease back down to `home_y`.
- **Easing:** Standard ease-in-out curve for both ascent and descent.
- **Both sprites lift equally** — unlike Insertion Sort where only the key lifts, Bubble Sort lifts the entire adjacent pair as a unit, emphasizing that the algorithm evaluates *pairs*, not individual elements.
- **Z-ordering during lift:** Both lifted sprites draw on top of non-lifted sprites. Between the two lifted sprites, default index order is maintained (no z-order swap until the T2 arc begins).

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

#### Step 2 — Compare-and-Shift Loop (Sequential Shift Guarantee)

Starting from `j = i - 1`, while `j >= 0` and `arr[j] > key`:

1. Emit `T1 Compare Tick` on `(j, j+1)` — shows the comparison between `arr[j]` and the key. Increment `self.comparisons += 1` before yielding.
2. Perform the shift: `arr[j+1] = arr[j]`. Emit `T2 Write/Mutation Tick` (OpType.SHIFT) on `(j, j+1)` — shows the element at `j` sliding right to `j+1`. Increment `self.writes += 1` before yielding.
3. Decrement `j`.

The lifted key sprite remains elevated and stationary during all compare and shift ticks.

**Sequential Shift Guarantee:** Each element that needs to shift right is processed as its own **individual compare-then-shift tick pair** (T1 + T2). Elements must never shift simultaneously as a batch or block. This one-at-a-time pacing is a core pedagogical requirement — the learner must observe each shift as a discrete, identifiable event:

- The compare tick (T1) shows *which* element is being evaluated against the key.
- The shift tick (T2) shows *that specific element* sliding one slot to the right.
- Only after the shift animation completes does the algorithm proceed to compare the next element leftward.

This sequential cadence ensures the learner can trace the "ripple" of shifts moving leftward through the sorted region. If multiple elements need to shift (e.g., key `1` in `[2, 4, 6, 7, 1, 5, 3]` requires 4 shifts), each shift is fully visible as a separate motion event with its own 150ms compare + 400ms shift cycle. The total animation time scales linearly with shift count, which directly communicates the O(n) cost of deep insertions.

**Anti-pattern: block shift.** An implementation that batches multiple shifts into a single T2 tick (moving several elements simultaneously) violates this guarantee. The worked examples below demonstrate the correct one-at-a-time sequence.

#### Step 3 — Terminating Comparison (when loop exits by condition)

If the loop exits because `arr[j] <= key` (not because `j < 0`), emit one final `T1 Compare Tick` on `(j, j+1)` — shows the comparison that determined the insertion point. Increment `self.comparisons += 1`. This tells the learner *why* the key is placed here: the element at `j` is not greater than the key.

If the loop exits because `j < 0` (key is the smallest element), no terminating comparison tick is emitted — there is no element to compare against.

#### Step 4 — Placement

- Place the key: `arr[j+1] = key`. Emit `T2 Write/Mutation Tick` (OpType.SHIFT) on `(j+1,)` — shows the key dropping into its sorted position. Increment `self.writes += 1` before yielding.
- The key sprite eases back down from its elevated position to the target slot.

#### Worked Example: `[4, 7, 2, 6, 1, 5, 3]`, pass `i=2`

Array before: `[4, 7, 2, 6, 1, 5, 3]` (after i=1 completed — key 7 was already in position, no shifts needed).

1. **Key-selection T1** on `(2,)`: `"Selecting key: 2 at index 2"`. Key 2 lifts. (No comparisons increment.)
2. **Compare T1** on `(1, 2)`: `"Comparing index 1 (value 7) with key 2"`. comparisons → 1.
3. **Shift T2** on `(1, 2)`: `"Shifting 7 from index 1 to index 2"`. Array → `[4, _, 7, 6, 1, 5, 3]` (logically; 7 moves right). writes → 1.
4. **Compare T1** on `(0, 1)`: `"Comparing index 0 (value 4) with key 2"`. comparisons → 2.
5. **Shift T2** on `(0, 1)`: `"Shifting 4 from index 0 to index 1"`. Array → `[_, 4, 7, 6, 1, 5, 3]`. writes → 2.
6. Loop exits: `j < 0`. No terminating comparison.
7. **Placement T2** on `(0,)`: `"Placing key 2 at index 0"`. Array → `[2, 4, 7, 6, 1, 5, 3]`. writes → 3. Key drops.

#### Worked Example: `[4, 7, 2, 6, 1, 5, 3]`, pass `i=3` (terminating comparison case)

Array before: `[2, 4, 7, 6, 1, 5, 3]` (after i=2 completed).

1. **Key-selection T1** on `(3,)`: `"Selecting key: 6 at index 3"`. Key 6 lifts.
2. **Compare T1** on `(2, 3)`: `"Comparing index 2 (value 7) with key 6"`. comparisons → 1.
3. **Shift T2** on `(2, 3)`: `"Shifting 7 from index 2 to index 3"`. Array → `[2, 4, _, 7, 1, 5, 3]`. writes → 1.
4. **Compare T1** on `(1, 2)`: `"Comparing index 1 (value 4) with key 6"`. 4 is not > 6 — loop exits by condition. comparisons → 2. *(This is the terminating comparison.)*
5. **Placement T2** on `(2,)`: `"Placing key 6 at index 2"`. Array → `[2, 4, 6, 7, 1, 5, 3]`. writes → 2. Key drops.

Additional rules:

- Must emit final `T4 Completion Tick`.

### 4.4 Heap Sort

Heap Sort operates in two phases: **Build Max-Heap** and **Extraction**.

Phase 1 is not merely a sequence of array swaps — it is a **structural transformation** that converts an arbitrary array into a valid max-heap. The sift-down procedure must visually communicate the **parent-child triangle** relationship (indices `i`, `2i+1`, `2i+2`) at each level of repair, so the learner understands the tree structure being enforced even though elements are displayed in a flat row.

#### Phase 1 — Build Max-Heap

- Iterate `i` from `n // 2 - 1` down to `0`, calling sift-down for each node.
- Sift-down sequence for a node at index `i` with heap boundary `heap_size`:

**Sift-down tick-by-tick procedure:**

1. Set `largest = i`.
2. Compute `left = 2*i + 1` and `right = 2*i + 2`.
3. **Logical Tree Highlight (T3):** Before any comparison at this sift-down level, emit a `T3 Range Emphasis Tick` highlighting the **parent-child triangle** — the tuple of existing indices from `(i, left, right)` where `left` and `right` are included only if they fall within `heap_size`. This tick communicates which tree relationship is about to be evaluated. Duration: 200ms. The accent color (orange) renders simultaneously on the parent and its children, implying the binary tree structure within the flat array layout.
   - Message format: `"Heapify: examining node {i} (value {arr[i]}) with children [{left_desc}, {right_desc}]"` where each child description includes its index and value, or is omitted if the child does not exist.
   - This T3 tick does **not** increment the step counter (consistent with all T3 ticks).
4. If `left < heap_size`:
   - Emit `T1 Compare Tick` on `(largest, left)` — compares current largest with left child. Increment `self.comparisons += 1`.
   - If `arr[left] > arr[largest]`, update `largest = left`.
5. If `right < heap_size`:
   - Emit `T1 Compare Tick` on `(largest, right)` — compares current largest with right child. **Note:** if `largest` was updated to `left` in step 4, this comparison is now between the left child and the right child, which is correct (finding the larger of the two children to potentially swap with the parent). Increment `self.comparisons += 1`.
   - If `arr[right] > arr[largest]`, update `largest = right`.
6. If `largest != i`:
   - Perform swap `arr[i], arr[largest] = arr[largest], arr[i]`.
   - Emit `T2 Write/Mutation Tick` on `(i, largest)`. Increment `self.writes += 2`.
   - Continue sift-down from `largest` (repeat from step 1 with `i = largest`).

**Note on `[4, 7, 2, 6, 1, 5, 3]`:** This input is **not** a valid max-heap (it has 3 heap violations), so Phase 1 performs actual sift-down swaps — the learner sees the heap being constructed with visible repairs at multiple tree levels. The build phase produces the max-heap `[7, 6, 5, 4, 1, 2, 3]`. The Logical Tree Highlight ticks make each repair's tree context visible: the learner can identify the parent and its children before each comparison-and-swap decision.

#### Phase 2 — Extraction

- Iterate `end` from `n - 1` down to `1`:
  1. Emit `T3 Range Emphasis Tick` on `tuple(range(0, end + 1))` to highlight the active heap boundary before the extraction swap. The View renders this as a left-to-right sweep (see Animation Spec Section 5.3.1).
  2. **Extraction Swap:** Swap root (`index 0`) with `end`, then emit `T2 Write/Mutation Tick` on `(0, end)`. Increment `self.writes += 2`. This swap uses the **elevated extraction arc** (`panel_height * 0.14`) rather than the standard arc height, visually distinguishing it as a phase-transition move (see Section 6.2 and Animation Spec Section 5.3).
  3. Call sift-down from `index 0` with `heap_size = end`. Sift-down emits Logical Tree Highlight T3 ticks before each level's comparisons, plus T1/T2 ticks per comparison and swap as described in Phase 1. The Controller applies **reduced sift-down cadence** durations (T1: 100ms, T2: 250ms, T3: 130ms) to create a rapid cascading rhythm (see Animation Spec Section 5.3.2).

Additional rules:

- Sift-down must be implemented iteratively or as an inner generator; `yield from` may be used for a sift-down sub-generator provided failure bubbling remains explicit.
- Must emit final `T4 Completion Tick`.

## 5) Highlight Semantics (Locked)

### Compare Highlights

- Compare operations highlight exactly the indices being compared.
- Bubble: `(j, j+1)`. Additionally, the View applies a temporary **compare-lift** (vertical offset) to both sprites during the T1 duration, isolating the pair from the baseline row (see Section 4.1).
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

### Heap Logical Tree Highlights

- Sift-down parent-child triangle highlights the tuple of `(parent, left_child, right_child)` where children exist within the heap boundary.
- This shows the learner which tree relationship is being evaluated, even though elements are displayed in a flat row.
- The highlight pattern is **non-contiguous** (e.g., indices `(1, 3, 4)`), distinguishing it from the contiguous boundary highlights.

## 6) Heap Sort Visual Phasing Decision

Decision: **Two-phase visual distinction is required in v1, enhanced with Logical Tree Highlights.**

Required behavior in v1:

- Heap Sort must emit T3 range emphasis ticks at the start of every extraction step to make the shrinking heap boundary visible.
- T1/T2 ticks during sift-down communicate individual comparisons and swaps within the heap.
- No separate auxiliary row animation is used; all Heap Sort motion is in-place on the main array row.

### 6.1 Logical Tree Highlight (v1 Required)

While v1 does not render a tree layout, it must **imply** tree structure through targeted highlighting during sift-down operations. This bridges the gap between the flat array display and the binary heap relationships the algorithm operates on.

**Mechanism:** Before each sift-down level's comparisons (in both Phase 1 and Phase 2), the algorithm emits a T3 tick that highlights the **parent-child triangle** — the parent index and its existing children. The accent color (orange) renders simultaneously on all members of the triangle for 200ms.

**Visual effect:** The learner sees 2–3 numbers flash orange together in a pattern that is *not* contiguous (e.g., indices 1, 3, 4). This non-contiguous grouping is the visual cue that a tree relationship exists — the learner intuitively perceives that index 1 "owns" indices 3 and 4, even without drawn edges.

**Distinction from boundary T3 ticks:** Boundary T3 ticks highlight a contiguous range (`0..heap_size-1`) and appear once per extraction step. Logical Tree Highlight T3 ticks highlight a non-contiguous parent-child group and appear before each sift-down level's comparisons. Both use the same T3 tick type and accent color; the viewer distinguishes them by the highlight pattern (contiguous = boundary, scattered = tree relationship).

### 6.2 Extraction Swap Visual Distinction (v1 Required)

The extraction swap (root element to end of heap) is a **phase-transition move** that fundamentally differs from intra-heap sift-down swaps. To communicate this visually, extraction swaps use an elevated arc height:

- **Extraction arc height:** `extraction_arc_height = panel_height * 0.14` (1.75× the standard `arc_height` of `panel_height * 0.08`).
- **Standard sift-down arc height:** unchanged at `panel_height * 0.08`.

The taller arc on extraction swaps gives the root-to-end move a visually dramatic quality, signaling to the learner that this is the major structural event (removing the max from the heap) rather than an internal repair. This is defined in the Animation Spec (10_ANIMATION_SPEC.md Section 5.3).

Rationale:

- The shrinking boundary communicates the core O(n log n) behavior of heap extraction.
- The Logical Tree Highlight communicates parent-child relationships without requiring a tree layout, drawing on the reference video's emphasis on tree structure (see `docs/Reference/Heap_Sort_Video_Reference.md`).
- The elevated extraction arc visually separates the "extract max" event from routine sift-down swaps, reinforcing the two-phase teaching model.
- Range highlighting preserves clarity without introducing additional drawing complexity.
- In-place motion is visually consistent with Bubble and Selection Sort panels.

## 7) Consistency and QA Hooks

- Every yield message must describe the operation in learner-friendly text.
  - Include both index and value for clarity: `"Comparing index 0 (value 4) and index 2 (value 2)"`.
  - Heap extraction: `"Swapping index 0 (value 7) with index 6 (value 3) — extracting max"`.
  - Range emphasis: `"Active heap: indices 0–4"`.
  - Key selection: `"Selecting key: 2 at index 2"`.
  - Shift: `"Shifting 7 from index 1 to index 2"`.
  - Placement: `"Placing key 2 at index 0"`.
- No tick may expose mutable `self.data` directly; snapshots must be copied.
- Completion tick must represent a fully sorted array.
- Tick density varies between phases; the dense sift-down phase and sparse extraction phase are intentional and instructional.

## 8) Operation → Animation Mapping

- COMPARE
  - Highlight compared indices.
  - No logical position change. Algorithm-specific temporary visual offsets may apply:
    - **Bubble Sort:** Compare-lift — both sprites in the adjacent pair temporarily ease upward and return to baseline within the T1 duration (see Section 4.1, Animation Spec Section 5.1.1).
    - **Insertion Sort key-selection:** Key sprite begins sustained lift (see Section 4.3, Animation Spec Section 5.2).
    - **All others:** No sprite movement.

- SWAP
  - Two sprites exchange horizontal positions.
  - Swap animation uses arc motion defined in Animation Spec.
  - Heap Sort extraction swaps (root ↔ end) use the elevated arc height (`panel_height * 0.14`); all other swaps use the standard arc height (`panel_height * 0.08`).

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

**Bubble Sort:** The largest unsorted element "bubbles" to the right on each pass. Each adjacent pair **lifts briefly above the baseline** during comparison, making every comparison visually prominent — including comparisons that do *not* result in a swap. The learner should notice that the lift-and-release rhythm provides a consistent visual "heartbeat" for the scan, while swaps add the dramatic arc motion on top. Later passes get shorter as the right side of the array becomes sorted. With `[4, 7, 2, 6, 1, 5, 3]`, some comparisons trigger swaps and some do not — the learner sees both outcomes clearly because even non-swap comparisons have visible motion.

**Selection Sort:** The algorithm scans the entire unsorted portion to find the minimum, then places it with a single swap. The learner should observe many comparisons followed by one swap (or no swap if the minimum is already in position). Despite being O(n²), Selection Sort has very few writes — for `[4, 7, 2, 6, 1, 5, 3]`, only 5 swaps (10 array writes).

**Insertion Sort:** Elements are "picked up" from the unsorted portion and inserted into the correct position within the growing sorted portion. The learner should observe the key lifting, elements sliding right to make room, and the key dropping into place. Some keys travel far (like 1, which shifts to position 0), while others stay close (like 7, which is already in position) — the learner sees varying insertion depths.

**Heap Sort:** Two distinct phases with tree-aware visual cues. Phase 1 (Build Max-Heap) repairs 3 heap violations, showing actual swaps as the tree structure is established — before each sift-down level, a Logical Tree Highlight flashes the parent-child triangle (e.g., indices 1, 3, 4) in orange, letting the learner perceive the binary tree relationships within the flat row. Phase 2 (Extraction) repeatedly moves the root (maximum) to the sorted region via a dramatically tall arc swap (1.75× standard height), visually distinguishing this phase-transition event from routine sift-down repairs. The learner should observe the orange heap boundary shrinking by one element per extraction, directly illustrating why the sorted region grows from the right.

### About the Race Outcome

The race outcome reflects operation costs for the specific input `[4, 7, 2, 6, 1, 5, 3]` at n=7. At this small size, constant factors and per-operation costs dominate over asymptotic complexity differences (log₂ 7 ≈ 2.8, so n log n ≈ 19.6 vs n² = 49 — less than a 3x gap). Selection Sort wins the race because it performs very few swaps (the most expensive operation at 400ms each), despite being O(n²). Heap Sort's O(n log n) advantage becomes decisive at larger array sizes, which are out of scope for v1.
