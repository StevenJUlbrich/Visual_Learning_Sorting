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

### Failure Tick Contract (T0) — All Algorithms

Domain-level errors (empty input, invalid data) must **never** raise Python exceptions. An unhandled exception propagates through the Controller and crashes the Pygame event loop, killing all four panels — including the three healthy algorithms mid-race. Instead, the algorithm must yield a `T0 Failure Tick` and return, allowing the Controller to deactivate that single panel while the remaining algorithms continue.

**Anti-pattern — exception instead of T0:**

```python
# WRONG: Crashes the entire application
def sort_generator(self):
    if len(self.data) == 0:
        raise ValueError("Cannot sort empty array")  # Kills Pygame event loop
```

**Correct pattern — T0 yield:**

```python
# CORRECT: Signals failure through the tick contract
def sort_generator(self):
    if len(self.data) == 0:
        yield SortResult(
            success=False,
            array_state=[],
            highlight_indices=(),
            op_type=OpType.COMPARE,  # OpType is irrelevant for failure ticks
            message="Cannot sort: empty array",
            comparisons=0,
            writes=0,
            is_complete=False,
        )
        return  # Generator exits cleanly — no completion tick
```

**Key rules:**
- `success=False` is the signal. The Controller checks this field and transitions the panel to `failed` state (see 02_ARCHITECTURE.md Panel Runtime State Machine).
- `is_complete=False` — a failure is not a successful completion.
- `message` is required — it appears in the panel's message line so the learner sees a human-readable explanation.
- The generator must `return` after yielding the failure tick. No further ticks (including T4 completion) may be emitted.
- This contract applies identically to all four algorithms. Each algorithm's `sort_generator` must begin with an empty-input guard that yields T0 and returns.

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

1. The `ComparisonPointer` moves to index `j` while remaining to the left of the `LimitLine`, which marks the current right-side boundary of the unsorted region.
2. `T1 Compare Tick` on `(j, j+1)` before any swap decision. The View applies a **compare-lift** to the adjacent pair: both sprites at indices `j` and `j+1` ease upward from `home_y` to `home_y - compare_lift_offset` over the first half of the T1 duration, hold briefly, then ease back to `home_y` by tick end (see Animation Spec Section 5.1.1). This temporary vertical isolation makes every comparison visually readable — even comparisons that do not result in a swap.
3. If swap needed, perform swap then emit `T2 Write/Mutation Tick` on `(j, j+1)`. The swap uses a **linear horizontal slide while both sprites remain lifted** at `compare_lane_y` — not an arc. After the horizontal exchange completes, both sprites descend together to `home_y` (see 10_ANIMATION_SPEC Section 5.1.2).
4. If no swap needed, the algorithm advances to the next `j`. The compare-lift's return to baseline serves as the visual "release" signal that the pair was inspected but left in place.

Pass boundary rules:

- A Bubble Sort pass ends when the `ComparisonPointer` reaches the active `LimitLine` boundary. No further compare tick may target an index pair that crosses or lies to the right of that boundary within the same outer-loop pass.
- At the conclusion of every outer-loop pass, the `LimitLine` must decrement by one slot (move one slot left), shrinking the active comparison window for the next pass.
- Elements to the right of the `LimitLine` are treated as visually settled and are excluded from the comparison scan. The `ComparisonPointer` must never enter that settled suffix.

Additional rules:

- Early-exit optimization allowed (`swapped=False` pass).
- Must still emit one final `T4 Completion Tick`.
- The compare-lift is a **View-layer animation only**. The algorithm model does not track lift state — it emits standard T1 ticks. The View recognizes Bubble Sort T1 ticks by the panel's algorithm identity and applies the lift choreography automatically.
- The shrinking window is a required teaching signal, not an optional decoration. Even when early-exit occurs, the last completed pass still defines the current `LimitLine` position and the visually excluded suffix.

#### Compare-Lift Motion Contract

- **Lift offset:** `compare_lift_offset = 50px` (fixed). This locks Bubble Sort to the observed reference choreography, where the pair rises into a dedicated compare lane before either holding or exchanging.
- **Timing within the 150ms T1 duration:**
  - `0–67ms` (45%): both sprites ease upward from `home_y` to `home_y - compare_lift_offset`.
  - `67–100ms` (22%): hold at lifted position (comparison is visually prominent).
  - `100–150ms` (33%): both sprites ease back down to `home_y`.
- **Easing:** Standard ease-in-out curve for both ascent and descent.
- **Both sprites lift equally** — unlike Insertion Sort where only the key lifts, Bubble Sort lifts the entire adjacent pair as a unit, emphasizing that the algorithm evaluates *pairs*, not individual elements.
- **Z-ordering during lift:** Both lifted sprites draw on top of non-lifted sprites. Between the two lifted sprites, default index order is maintained (no z-order swap until the T2 arc begins).

Counter behavior:

- `self.comparisons += 1` before every T1 compare tick.
- `self.writes += 2` before every T2 swap tick (a swap modifies two array positions).

### 4.2 Selection Sort

Selection Sort follows a strict two-phase "scan-then-swap" pattern per outer index `i`, mirroring the instructional pacing observed in the reference video (`docs/Reference/Selection_Sort_Video_Reference.md`).

#### Phase 1 — Scan (Find Minimum)

For each `j` from `i+1` to `n-1`:

1. Compare `arr[j]` against `arr[min_idx]`. If `arr[j] < arr[min_idx]`, update `min_idx = j`.
2. Emit `T1 Compare Tick` with `highlight_indices = (min_idx, j)`.

**Highlight contract:** Every T1 tick during the scan **must** include both `min_idx` and `j` in `highlight_indices`. This two-index highlight serves a dual purpose:
- `min_idx` represents the **running minimum pointer** — the best candidate found so far. By including it on every tick, the learner can visually track the minimum as it "jumps" to a new position whenever a smaller element is found.
- `j` represents the **scan cursor** — the element currently being evaluated.

When `min_idx` updates (a new minimum is found), the next T1 tick's highlight reflects the updated `min_idx`, so the learner sees the minimum pointer relocate. When `min_idx` does not change, both highlights persist on the same pair, reinforcing that the current scan element was not smaller.

**Message format:** `"Comparing index {min_idx} (value {arr[min_idx]}) and index {j} (value {arr[j]})"`. If `min_idx` updates, an additional message variant may note: `"New minimum found: {arr[j]} at index {j}"`.

#### Phase 2 — Swap (Place Minimum)

After the scan completes:

- If `min_idx != i`: the minimum is not already in its sorted position. Perform `arr[i], arr[min_idx] = arr[min_idx], arr[i]` and emit `T2 Write/Mutation Tick` on `(i, min_idx)`. The View triggers a standard swap arc animation — both sprites exchange horizontal positions with the left sprite arcing upward and the right sprite arcing downward (see Animation Spec Section 5.1). This single swap places the minimum into its final sorted position.
- If `min_idx == i`: the minimum is already in position. No T2 tick is emitted — the algorithm advances to the next outer index silently. The learner observes many comparisons followed by no swap, which reinforces that Selection Sort only writes when necessary.

#### Pointer Assets (Required)

Selection Sort requires three labeled pointer arrow assets that track algorithm state in real time, providing structural position information alongside the color highlights:

1. **`i` pointer (Sorted Boundary):** A downward-pointing arrow positioned **above** the baseline row, centered over the current outer loop index `i`. It marks the next position in the sorted region to be filled. Advances one slot rightward after each completed swap. Color: primary text `(240, 240, 245)`.

2. **`j` pointer (Scan Cursor):** An upward-pointing arrow positioned **below** the baseline row, centered under the current inner loop scan index `j`. It advances left-to-right during each scan phase. Color: active highlight `(255, 140, 0)` orange.

3. **`min` pointer (Minimum Tracker):** An upward-pointing arrow positioned **below** the baseline row, centered under the current minimum candidate index `min_idx`. It jumps to a new index whenever a smaller element is discovered. Color: active highlight `(255, 140, 0)` orange.

**Coalescing behavior:** When `j` and `min` occupy the same index (immediately after a new minimum is discovered), only the `min` label is shown — `j` visually merges into `min`. When `j` advances past that index, both labels separate again.

**Pointer behavior during swap:** The `i` pointer is hidden during the swap arc motion and reappears after the elements settle at the baseline. The `min` pointer remains visible below the swapping element during the arc.

These pointer assets work in conjunction with the orange ring highlights on the active comparison pair (`min_idx` and `j`), providing both structural (position) and state (color) cues simultaneously.

Additional rules:

- The scan phase is comparison-heavy; the swap phase is sparse and explicit. For `[4, 7, 2, 6, 1, 5, 3]`, there are 21 comparisons but only 5 swaps.
- No vertical offset or compare-lane motion applies to Selection Sort T1 ticks — the visual emphasis is on the scan cursor and minimum tracking via highlight color, not spatial displacement. This distinguishes Selection Sort's visual signature from Bubble Sort (pair-lift) and Insertion Sort (key-lift).
- Must emit final `T4 Completion Tick`.

Counter behavior:

- `self.comparisons += 1` before every T1 compare tick.
- `self.writes += 2` before every T2 swap tick (a swap modifies two array positions).

### 4.3 Insertion Sort

Insertion Sort requires a precise tick sequence to correctly visualize the key-selection, comparison, shifting, and placement phases.

Required sequence per outer index `i` (from `1` to `n-1`):

#### Key Label Asset (Required)

When the key sprite is lifted into the compare lane, the View must render a **"KEY" label** in the active highlight color `(255, 140, 0)` orange, positioned adjacent to the lifted circle (to its right or above). The label remains visible for the entire duration the key is elevated — from the key-selection T1 tick through all compare and shift ticks until the T2 placement drop. The label disappears when the key settles back to the baseline. This label serves the same identification purpose as Selection Sort's "min" pointer label: the learner immediately knows which element is the active insertion target.

#### Gap Visualization

When the key lifts from its baseline slot, that slot renders as **empty space** (no circle, no outline — just the panel background). As elements shift right during the compare-and-shift loop, the gap migrates leftward through the sorted region. The gap is not a rendered object — it is the absence of a sprite at a baseline slot. The empty space is a critical visual cue: it shows the learner where the key was extracted from and where space is being created for its insertion.

#### Sorted/Unsorted Boundary

Insertion Sort communicates the sorted/unsorted boundary **entirely through color transition** — green rings (sorted) transition to blue rings (unsorted) with no separate boundary marker, pointer, or line. The color distinction is self-evident and does not require additional visual assets.

#### Step 1 — Key Selection (First Visual Event)

- Emit `T1 Compare Tick` on `(i,)` highlighting the selected key.
- This tick is the **first visual event** of every outer loop pass — no other tick (compare, shift, or placement) may precede it within the pass. The lift establishes the key's identity before any comparisons or shifts occur, giving the learner a clear "this is the element being inserted" moment.
- This tick does **not** increment `self.comparisons` — it is a key-selection signal, not a data comparison.
- The key sprite begins its visual lift to the compare lane (`home_y - lift_offset`) on this tick and **remains elevated** across all subsequent ticks in the pass until the T2 Placement tick drops it (see Step 4). The "KEY" label appears immediately on lift. See Animation Spec Section 5.2.

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

#### Step 4 — Placement / Settle (Final Visual Event)

- Place the key: `arr[j+1] = key`. Emit `T2 Write/Mutation Tick` (OpType.SHIFT) on `(j+1,)` — shows the key dropping into its sorted position. Increment `self.writes += 1` before yielding.
- This T2 Placement tick is the **final action of the pass** — no other tick may follow it within the same outer loop iteration. It closes the pass that was opened by the key-selection T1 tick in Step 1.
- **Settle motion:** The key sprite eases simultaneously in both axes — horizontally to the destination slot's `home_x` and vertically from the compare lane (`home_y - lift_offset`) back down to `home_y` — over the T2 duration (400ms) using the standard ease-in-out curve. This smooth "settle" into position gives the learner a clear visual signal that the insertion is complete before the next pass begins. See Animation Spec Section 5.2.

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

#### Tree Visualization (Required)

The Heap Sort panel renders a **binary tree layout** of the active heap elements, positioned in the upper portion of the panel's array rendering region. This tree visualization is unique to Heap Sort — the other three algorithms use a flat single-row layout.

**Tree layout rules:**
- Tree nodes are circular outlined rings (D-069) connected by parent-child edge lines drawn in `(120, 120, 130)`.
- The root node is centered horizontally at the top of the tree area.
- Each level of the tree is positioned progressively lower, with children spread horizontally beneath their parent.
- Parent-child edges are straight lines connecting the center of the parent circle to the center of each child circle.
- The tree dynamically shrinks as elements are extracted — nodes removed from the heap disappear from the tree and appear in the sorted row below.
- Node highlight colors follow the universal active highlight (D-067): orange `(255, 140, 0)` during T1 compare and T3 tree highlights, default blue when at rest within the heap.

**Sorted region row:**
- Below the tree, a compact horizontal row displays elements that have been extracted from the heap.
- Sorted elements use the settled/extracted color `(130, 150, 190)` steel-blue rings.
- The sorted row grows from right to left as extractions proceed.
- On the completion tick, all elements (tree collapses, sorted row becomes full) transition to green `(80, 220, 120)`.

**Heap boundary marker:**
- A subtle vertical dashed line separates the active heap slots from the sorted slots in the row below the tree, labeled "heap boundary".

**Phase label:**
- During Phase 1, the text "BUILD MAX-HEAP" is rendered in orange `(255, 140, 0)` within the tree visualization area.
- During Phase 2, the text changes to "EXTRACTION".
- The label is positioned inside the panel content area (between tree nodes or below the tree root), matching the reference video's "Heapify" text placement.

#### Phase 1 — Build Max-Heap

- Iterate `i` from `n // 2 - 1` down to `0`, calling sift-down for each node.
- Sift-down sequence for a node at index `i` with heap boundary `heap_size`:

**Strict Sift-Down Tick Sequence (Mandatory):**

The sift-down procedure is defined as a strict, invariant sequence at each tree level: **T3 (Logical Tree Highlight) → T1 (Compare) → T2 (Swap/Mutation)**. This ordering is not advisory — it is a hard contract. The T3 tick is a mandatory precursor that establishes the parent-child context before any comparison or mutation occurs at that level. Violating this ordering (e.g., emitting a T1 before the T3, or omitting the T3 entirely) breaks the visual learning contract because the learner would see comparisons without first understanding which tree relationship is being evaluated.

**Sift-down tick-by-tick procedure:**

At each sift-down level, set `largest = i`, compute `left = 2*i + 1` and `right = 2*i + 2`, then execute the following tick sequence:

1. **Logical Tree Highlight (T3) — FIRST TICK OF EVERY LEVEL:** Before any comparison or mutation at this sift-down level, emit a `T3 Range Emphasis Tick` that visually "draws" the tree branch being evaluated. The `highlight_indices` field must contain the **parent and both existing children** — the tuple `(i, left, right)` where `left` and `right` are included only if they fall within `heap_size`. This is the first yielded tick at every sift-down level, without exception. The accent color (orange) renders simultaneously on all members of the triangle, visually drawing the parent-child branch within the flat array layout. Duration: 200ms.
   - **Branching contract:** `highlight_indices` must always include the parent index `i`. It must include `left` (`2*i+1`) if `left < heap_size`, and `right` (`2*i+2`) if `right < heap_size`. The resulting tuple of 1–3 indices is the model's declaration of the tree branch — the View uses this non-contiguous grouping to imply the binary tree structure. A T3 tick that omits the parent or includes indices outside the parent-child relationship violates the branching contract.
   - Message format: `"Heapify: examining node {i} (value {arr[i]}) with children [{left_desc}, {right_desc}]"` where each child description includes its index and value, or is omitted if the child does not exist.
   - This T3 tick does **not** increment the step counter (consistent with all T3 ticks).
2. If `left < heap_size`:
   - Emit `T1 Compare Tick` on `(largest, left)` — compares current largest with left child. Increment `self.comparisons += 1`.
   - If `arr[left] > arr[largest]`, update `largest = left`.
3. If `right < heap_size`:
   - Emit `T1 Compare Tick` on `(largest, right)` — compares current largest with right child. **Note:** if `largest` was updated to `left` in step 2, this comparison is now between the left child and the right child, which is correct (finding the larger of the two children to potentially swap with the parent). Increment `self.comparisons += 1`.
   - If `arr[right] > arr[largest]`, update `largest = right`.
4. If `largest != i`:
   - Perform swap `arr[i], arr[largest] = arr[largest], arr[i]`.
   - Emit `T2 Write/Mutation Tick` on `(i, largest)`. Increment `self.writes += 2`.
   - Continue sift-down from `largest` (repeat from step 1 with `i = largest`).

**Logical Tree Highlight Integration (Mandatory):** Before comparing a parent to its children at any sift-down level (in both Phase 1 and Phase 2), a T3 tick **must** be yielded containing the indices of the parent and any valid children. This T3 tick is a precursor to every comparison level — no T1 compare tick may be emitted at a given sift-down level without a preceding T3 tick for that level's parent-child triangle.

**Yield Sequence Example (per sift-down level):**

```python
# Phase 1 or 2 Sift-Down Level
# 1. T3: Logical Tree Highlight (Parent + Children)
yield SortResult(..., highlight_indices=(i, left, right), op_type=OpType.RANGE, ...)

# 2. T1: Compare Parent/Largest with Left
yield SortResult(..., highlight_indices=(largest, left), op_type=OpType.COMPARE, ...)

# 3. T1: Compare Largest with Right
yield SortResult(..., highlight_indices=(largest, right), op_type=OpType.COMPARE, ...)

# 4. T2: Swap if necessary
yield SortResult(..., highlight_indices=(i, largest), op_type=OpType.WRITE, ...)
```

**Reference Implementation Logic (`sift_down` generator):**

The `sift_down` generator in `heap.py` should follow this structure to ensure the correct tick sequence is sent to the Controller:

```python
def sift_down(arr, i, heap_size):
    while True:
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2

        # --- T3: Logical Tree Highlight (Branching Visual) ---
        # Yield the 'branch' (parent + existing children)
        triangle = [i]
        if left < heap_size: triangle.append(left)
        if right < heap_size: triangle.append(right)

        yield SortResult(
            success=True,
            array_state=list(arr),
            highlight_indices=tuple(triangle),
            op_type=OpType.RANGE,  # Triggers T3 duration/color
            message=f"Examining tree branch at index {i}"
        )

        # --- T1: Standard Comparisons ---
        if left < heap_size:
            yield SortResult(..., highlight_indices=(largest, left), op_type=OpType.COMPARE, ...)
            if arr[left] > arr[largest]:
                largest = left

        if right < heap_size:
            yield SortResult(..., highlight_indices=(largest, right), op_type=OpType.COMPARE, ...)
            if arr[right] > arr[largest]:
                largest = right

        # --- T2: Mutation ---
        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            yield SortResult(..., highlight_indices=(i, largest), op_type=OpType.WRITE, ...)
            i = largest
        else:
            break
```

Key structural points:
- The `while True` loop with `i = largest` at the bottom implements iterative sift-down (no recursion), satisfying the "iteratively or as an inner generator" requirement.
- The T3 tick is emitted at the **top** of the loop, guaranteeing it precedes every comparison level — including levels reached after a swap cascades downward.
- The `triangle` list dynamically includes only children within `heap_size`, handling leaf nodes and single-child parents correctly.
- The `largest` variable tracks the running winner across comparisons, so the T1 highlight on `(largest, right)` correctly reflects the left-vs-right comparison when the left child won the first comparison.
- The `break` when `largest == i` terminates the sift-down when the heap property is satisfied — no T2 tick is emitted for that level.

**Note on `[4, 7, 2, 6, 1, 5, 3]`:** This input is **not** a valid max-heap (it has 3 heap violations), so Phase 1 performs actual sift-down swaps — the learner sees the heap being constructed with visible repairs at multiple tree levels. The build phase produces the max-heap `[7, 6, 5, 4, 1, 2, 3]`. The Logical Tree Highlight ticks make each repair's tree context visible: the learner can identify the parent and its children before each comparison-and-swap decision.

#### Phase 2 — Extraction

- Iterate `end` from `n - 1` down to `1`:
  1. Emit `T3 Range Emphasis Tick` on `tuple(range(0, end + 1))` to highlight the active heap boundary before the extraction swap. The View renders this as a left-to-right sweep (see Animation Spec Section 5.4.1).
  2. **Extraction Swap:** Swap root (`index 0`) with `end`, then emit `T2 Write/Mutation Tick` on `(0, end)`. Increment `self.writes += 2`. This swap uses the **elevated extraction arc** (`panel_height * 0.14`) rather than the standard arc height, visually distinguishing it as a phase-transition move (see Section 6.2 and Animation Spec Section 5.4).
  3. Call sift-down from `index 0` with `heap_size = end`. Sift-down emits Logical Tree Highlight T3 ticks before each level's comparisons, plus T1/T2 ticks per comparison and swap as described in Phase 1. The Controller applies **reduced sift-down cadence** durations (T1: 100ms, T2: 250ms, T3: 130ms) to create a rapid cascading rhythm (see Animation Spec Section 5.4.2).

Additional rules:

- Sift-down must be implemented iteratively or as an inner generator; `yield from` may be used for a sift-down sub-generator provided failure bubbling remains explicit.
- Must emit final `T4 Completion Tick`.

#### Heap Sort Negative Case (Empty Input)

Heap Sort is particularly susceptible to exception-based failures because `n // 2 - 1` evaluates to `-1` for an empty array, and iterating `range(-1, -1, -1)` produces no sift-down calls — but the subsequent extraction phase may attempt to access `arr[0]` on an empty list, raising an `IndexError`.

**Required behavior:** The generator must guard against empty input at the top of `sort_generator`, before any phase logic executes:

```python
def sort_generator(self):
    if len(self.data) == 0:
        yield SortResult(
            success=False,
            array_state=[],
            highlight_indices=(),
            op_type=OpType.COMPARE,
            message="Cannot sort: empty array",
            comparisons=0,
            writes=0,
            is_complete=False,
        )
        return  # No Phase 1, no Phase 2, no completion tick

    # Phase 1 — Build Max-Heap
    # Phase 2 — Extraction
    # ... (normal algorithm logic)
```

The same guard pattern applies to single-element input (`len(data) == 1`), which should skip both phases and immediately emit a T4 completion tick — a single-element array is trivially sorted.

## 5) Highlight Semantics (Locked)

### Compare Highlights

All compare highlights use the universal active highlight color `(255, 140, 0)` orange, regardless of algorithm.

- Compare operations highlight exactly the indices being compared.
- Bubble: `(j, j+1)` — highlighted in active highlight color `(255, 140, 0)` orange. Additionally, the View applies a temporary **compare-lift** (vertical offset) to both sprites during the T1 duration, isolating the pair from the baseline row (see Section 4.1).
- Selection: `(min_idx, j)` — highlighted in active highlight color `(255, 140, 0)` orange.
- Insertion compare-during-shift: `(j, j+1)` — highlighted in active highlight color `(255, 140, 0)` orange. The element at `j` is compared against the lifted key (visually above the array).
- Insertion key-selection: `(i,)` — single-index highlight on the key being extracted.
- Heap sift-down compare: `(largest, child_idx)` — highlighted in active highlight color `(255, 140, 0)` orange. This reflects the running `largest` value, so when comparing the right child, the highlight may show `(left_child, right_child)` if the left child was already found to be larger than the parent.

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

#### Branching Visualization (Branching Contract)

The Logical Tree Highlight serves as a **dynamic focus mechanism** that works in conjunction with the rendered binary tree layout (see Section 4.4, Tree Visualization). The T3 tick's highlight pattern identifies the specific parent-child branch being evaluated at each sift-down level, adding operational emphasis on top of the persistent tree edges.

**Branching contract for `highlight_indices`:** The T3 tick's `highlight_indices` field must satisfy all of the following:
- **Must include** the parent index `i` — always present.
- **Must include** `left` (`2*i+1`) if `left < heap_size` — draws the left branch.
- **Must include** `right` (`2*i+2`) if `right < heap_size` — draws the right branch.
- **Must not include** any index outside the parent-child triple — extraneous indices would corrupt the branch visual by implying tree relationships that do not exist.
- The resulting tuple contains 1–3 indices depending on the node's position in the tree (leaf nodes have no children, last internal node may have only a left child).

This contract is the model's explicit declaration of which tree branch is being evaluated. The View consumes `highlight_indices` directly to render the branching visual — there is no secondary branch-detection logic. If the model emits incorrect indices, the View will draw incorrect branches.

**Pedagogical invariant:** The learner must be able to perceive which tree branch is under evaluation at each sift-down step. When indices `(1, 3, 4)` flash orange simultaneously — with the corresponding tree nodes and connecting edges highlighted — the learner sees both the structural relationship (drawn edges) and the operational focus (orange highlight) reinforcing each other. This pattern repeats at every sift-down level (as the mandatory first tick — see Section 4.4 step 1), reinforcing the tree mental model throughout both phases of the algorithm.

## 6) Heap Sort Visual Phasing Decision

Decision: **Two-phase visual distinction is required in v1, enhanced with Logical Tree Highlights.**

Required behavior in v1:

- Heap Sort must emit T3 range emphasis ticks at the start of every extraction step to make the shrinking heap boundary visible.
- T1/T2 ticks during sift-down communicate individual comparisons and swaps within the heap.
- Heap Sort renders a binary tree layout for active heap elements in the upper portion of the panel, with a sorted row below the tree that grows as elements are extracted (see Section 4.4, Tree Visualization). This tree layout is unique to Heap Sort — the other three algorithms use a flat single-row layout.

### 6.1 Logical Tree Highlight (v1 Required)

v1 renders a binary tree layout for Heap Sort (see Section 4.4, Tree Visualization), and the Logical Tree Highlight T3 ticks work in conjunction with the visible tree edges to **reinforce** parent-child relationships during sift-down operations. The T3 highlights complement the drawn tree structure by adding dynamic color emphasis to the specific branch being evaluated.

**Mechanism:** Before each sift-down level's comparisons (in both Phase 1 and Phase 2), the algorithm emits a T3 tick that highlights the **parent-child triangle** — the parent index and its existing children. The accent color (orange) renders simultaneously on all members of the triangle for 200ms. Because the tree layout already draws parent-child edges, the T3 highlight serves as a **focus cue** — it tells the learner "this is the branch being evaluated right now" within the full tree structure.

**Visual effect:** The learner sees 2–3 tree nodes and their connecting edges flash orange together, drawing attention to the specific parent-child relationship being evaluated. The combination of persistent tree edges (structural context) and transient T3 highlights (operational focus) gives the learner both the global tree shape and the local sift-down action simultaneously.

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
- In-place motion remains visually consistent with the shared sprite system while preserving Heap Sort's own arc-based extraction and sift-down identity.

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
  - Highlight compared indices. All algorithms use the universal active highlight color `(255, 140, 0)` orange.
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
