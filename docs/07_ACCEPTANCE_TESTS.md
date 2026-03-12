# 07 ACCEPTANCE TESTS - Human Checks and Automated Intent

Scope: Acceptance criteria for Sorting Algorithm Visualizer v1 (Pygame Sprite Engine & Independent Queues).

## Definition of Done

All items below must pass:

- Every algorithm reaches a fully sorted final array in ascending order.
- Every algorithm emits exactly one final completion tick.
- No shared mutable array behavior exists between algorithm instances.
- Selection Sort cannot terminate in a near-sorted state.
- Global controls map strictly to Path 2 UI expectations.
- Panels support Option B theme accents and Option C resolution flags without rendering artifacts.
- Sprites animate smoothly via `dt` without teleporting, and independent elapsed timers halt precisely upon algorithm completion.
- Comparisons and writes counters accurately reflect the algorithmic operations performed.

## Acceptance Tests (Human-Checkable)

### AT-01 Startup Baseline

- Launch app.
- Expect paused state and 4 visible algorithm panels.
- Expect each panel shows the initial array `[4, 7, 2, 6, 1, 5, 3]`.
- Expect all elapsed timers in the panel headers to read `0.00s`.
- Expect all counters to read Steps: 0, Comps: 0, Writes: 0.

### AT-02 Independent Queue Progression

- While paused, press Step once.
- Expect each active algorithm to advance its independent animation queue to the conclusion of its currently pending logical operation, smoothly animating the sprites to their targets.
- Repeat multiple times; expect deterministic progression across all panels without forced synchronization.
- Verify the step counter only increments on successful, non-terminal, non-RANGE yields.

### AT-03 Completion Race (All Algorithms)

- Press Play and run to completion.
- Verify faster algorithms finish animating earlier, enter their completion state, and permanently halt their individual elapsed timers.
- For each panel, verify final numbers are ascending `[1, 2, 3, 4, 5, 6, 7]` and unchanged after completion.

### AT-04 Generator Completion Contract

- Observe full run for each algorithm.
- Verify there is a clear terminal completion state.
- Verify no additional progress ticks occur after completion.

### AT-05 Selection Sort Regression Guard

- Run Selection Sort panel to completion.
- Specifically verify final sequence is fully sorted; no residual inversion is allowed.
- Failure example (must never occur): trailing inversion like `[..., 12, 11]`.

### AT-06 Failure Isolation

- Simulate one algorithm failure tick (`success=False`).
- Expect only that panel to deactivate, show error state, and freeze its elapsed timer.
- Other panels continue animating to completion.

### AT-07 Sprite Motion and Tweening Smoothness

- During Play, observe the physical movement of the sprites.
- Verify that swaps (Bubble, Selection, Heap) utilize a `y`-axis arc to prevent visual collisions.
- Verify that elements do not "teleport" or snap abruptly unless the user pauses or steps mid-animation.

### AT-08 Duplicate Value Stability

Use dataset: [3,1,3,2,1,2,3]

Verify:

- Duplicate values remain visually distinct sprites.
- No sprite disappears or duplicates visually.
- Final sorted array preserves multiset equality.
- All sprites maintain stable animation behavior.

### AT-09 Heap Sort Two-Phase Visual Distinction

- Run Heap Sort panel to completion.
- Verify that during Phase 1 (Build Max-Heap), actual swaps occur — the heap is being actively constructed with visible element movements (3 heap violations are repaired for the default array).
- Verify that T3 Range Emphasis ticks are visible at the start of each extraction step, showing the shrinking active heap boundary highlighted in the panel accent color (orange).
- Verify that after the final extraction, all sprites are in ascending order and the completion color is applied to the full array.
- Verify that all Heap Sort motion remains in-place on the main array row (no auxiliary row animation).

### AT-10 Heap Sort Phase Correctness

- Run Heap Sort panel to completion.
- Verify the Build Max-Heap phase completes before any extraction swap occurs (no element is swapped to its sorted position before the full heap is constructed).
- For `[4, 7, 2, 6, 1, 5, 3]`, verify that after Phase 1 the array becomes a valid max-heap (`[7, 6, 5, 4, 1, 2, 3]`).
- Verify the sorted region (right side of array) grows by one element per extraction step.

### AT-11 Insertion Sort Lift-and-Settle Sequence

- Run Insertion Sort panel, stepping through operations one tick at a time.
- For each outer loop pass (i = 1 through 6), verify the following visual sequence:

  **First event — Key Lift:**
  1. The very first tick of the pass lifts the key element above the array row into the compare lane. No other tick (compare, shift, or placement) precedes it. The key is highlighted on a single index `(i,)`.

  **Mid-pass — Sustained Elevation:**
  2. After the key lifts, step through all subsequent compare and shift ticks for the pass. **At every tick**, verify the key sprite remains visually elevated above the baseline — it must never drop back to the array row or flicker to baseline between ticks.
  3. Compare highlights appear on the element being checked and the adjacent position. The key stays lifted.
  4. If the comparison triggers a shift, the element slides right one slot before the next comparison. The key stays lifted.
  5. When the insertion point is found, a final comparison highlight shows the element that is not greater than the key (if the key does not go to position 0). The key stays lifted.

  **Final event — Settle / Drop:**
  6. The last tick of the pass is a T2 placement tick. The key sprite eases diagonally — simultaneously moving horizontally to the destination slot and vertically from the compare lane back down to the baseline — in a single smooth motion. After this tick completes, the key is at rest in its sorted position at `home_y`.

- **Regression guard:** If the key visually drops to baseline at any point before the placement tick, or if any tick other than the key-selection T1 appears first in a pass, the test fails.

### AT-12 Counter Accuracy

Run all algorithms to completion with `[4, 7, 2, 6, 1, 5, 3]` and verify:

- **Bubble Sort:** Comparisons = 20, Writes = 26 (13 swaps x 2 array writes each).
- **Selection Sort:** Comparisons = 21, Writes = 10 (5 swaps x 2 array writes each).
- **Insertion Sort:** Comparisons = 17, Writes = 19 (13 shifts + 6 placements, each 1 array write).
- **Heap Sort:** Comparisons = 20, Writes = 30 (15 swaps x 2 array writes each).

### AT-13 T3 Step Counter Exclusion

- Run Heap Sort to completion.
- Count the visible T3 range emphasis highlights (should be 6 for n=7).
- Verify the panel step count does **not** include these T3 ticks. Heap Sort's step count should be 35 (20 T1 + 15 T2), not 41.

### AT-14 Accent Color Readability (AAA Contrast)

- Launch app and begin sorting.
- For each panel, when a highlight activates (compare or swap tick), verify the accent-colored number is clearly legible against the panel background:
  - **Bubble (cyan):** bright and vivid, highest contrast.
  - **Selection (red):** warm red, clearly distinguishable from the dark panel.
  - **Insertion (magenta):** vibrant magenta, not muddy or dim.
  - **Heap (orange):** warm orange, easily readable.
- Verify that **settled/extracted** elements in the Heap Sort panel (after leaving the active heap) are clearly readable — they should appear as a muted steel-blue, visually distinct from both the vivid default blue and the orange accent, without blending into the dark panel background.
- Verify the **completion color** (green) is bright and legible when all elements turn green at algorithm finish.

### AT-15 Portrait Mode Layout Integrity

- Set `config.toml` to `orientation = "portrait"` (720x996) and launch app.
- Verify all four panels are visible in the 2x2 grid without overlapping or clipping.
- Verify the metrics line (Big-O, elapsed time, counters) is fully visible and not truncated or overlapping with the algorithm title.
- Verify the message line is visible and does not collide with the metrics line above or the array numbers below.
- Verify number sprites fit within their slots without overlapping adjacent numbers.
- Verify arc motion during swaps does not cause sprites to overlap with header text or escape the panel boundary.

### AT-16 Landscape Mode Layout Integrity

- Set `config.toml` to `orientation = "landscape"` (1280x720) and launch app.
- Verify all four panels are visible in the 2x2 grid with proportional spacing.
- Verify header, metrics, message, and array regions are vertically stacked without overlap.
- Verify all text is anti-aliased (smooth edges, no jagged stairstepping on curves of letters like "S", "O", "C").

### AT-17 Selection Sort Min Tracking

- Run Selection Sort panel, stepping through operations one tick at a time.
- For each outer pass `i`, observe the scan phase (`j = i+1` through `n-1`):
  1. On each T1 compare tick, verify that **two** indices are highlighted in the panel accent color (red): the current scan cursor `j` and the running minimum `min_idx`.
  2. When a new, smaller element is found at index `j`, verify the minimum highlight **moves** to `j` on the next tick — the previous `min_idx` loses its accent and `j` becomes the new `min_idx`.
  3. When the element at `j` is not smaller than the current minimum, verify the minimum highlight **stays** on `min_idx` — it does not flicker or disappear between ticks.
- Verify the message line references the current minimum on every scan tick (e.g., `"Comparing index 3 (value 6) with current min 2 at index 2"`).
- **Regression guard:** If the minimum highlight disappears or jumps to an index that is not the actual running minimum, the test fails.

### AT-18 Selection Sort Sorted Region Stability

- Run Selection Sort panel to completion, stepping through operations.
- After each swap (T2 tick placing the minimum at index `i`), verify:
  1. The element now at index `i` transitions to the **settled/extracted color** `(130, 150, 190)` (desaturated steel-blue) — it is visually distinct from both the default array blue and the active accent red.
  2. On all subsequent passes, the settled elements at indices `0..i` are **never** highlighted by the scan cursor. The scan only operates on the unsorted region (`i+1..n-1`); settled elements remain steel-blue and visually inert.
  3. The sorted region grows from left to right — after pass `i`, exactly `i+1` elements on the left side of the array display the settled color.
- On the completion tick, all settled elements transition from steel-blue to the global completion color (green), matching the behavior defined for Heap Sort extracted elements.
- **Note:** This extends the settled/extracted color to Selection Sort (previously v1 scope was Heap Sort only per D-063). The visual contract is identical: settled = "this element is in its final position, but the algorithm is still working."

## Automated Acceptance Intent (for `tests/`)

### A) Minimum Correctness Checks (non-empty fixtures only)

- For each algorithm class with non-empty input, consume generator to terminal tick.
- Assert final `array_state` is sorted ascending.
- Assert final output is a permutation of input multiset.
- Assert completion tick count is exactly 1.

### B) Generator Contract Checks (non-empty fixtures only)

- Assert every yielded item is `SortResult`.
- Assert `message` is present on every yield.
- Assert there is exactly one terminal tick where `success=True and is_complete=True`.

### C) Controller Queue and Timer Semantics

- Assert the Controller accurately calculates total simulated elapsed time based on predefined operation costs (`T1`, `T2`, `T3`).
- On a completion tick, assert only that algorithm deactivates and its timer halts.

### D) Heap Sort Phase Contract

- Consume the Heap Sort generator for the default fixture `[4, 7, 2, 6, 1, 5, 3]`.
- Assert at least one `T3 Range Emphasis Tick` is emitted (active heap boundary display).
- Assert T3 ticks only appear during Phase 2 (extraction), never during Phase 1 (build max-heap).
- Assert that each T3 tick's `highlight_indices` forms the contiguous range `tuple(range(0, k))` for a strictly decreasing `k`.
- Assert Phase 1 produces at least one T2 swap tick (heap violations exist in this input).

### E) Insertion Sort Tick Sequence Contract

- Consume the Insertion Sort generator for `[4, 7, 2, 6, 1, 5, 3]`.
- For each outer pass `i` (from 1 to 6):

  **Pass boundary checks:**
  - Assert the **first tick** of the pass is a T1 key-selection (`OpType.COMPARE`) with `highlight_indices == (i,)` — a single-element tuple. Any other tick type, or a multi-element highlight, is a contract violation.
  - Assert the **last tick** of the pass is a T2 placement (`OpType.SHIFT`) with `highlight_indices` containing exactly one index — the destination slot.

  **Mid-pass sequence checks:**
  - Assert subsequent T1/T2 ticks alternate correctly: T1 compare on `(j, j+1)`, then T2 shift on `(j, j+1)` for each element that moves. No two consecutive T1s or two consecutive T2s within the shift loop.
  - If the loop exits by condition (`j >= 0`), assert a terminating T1 compare tick is emitted on `(j, j+1)`.

  **Counter checks:**
  - Assert the key-selection T1 tick does **not** increment `comparisons` (it is a selection signal, not a data comparison).
  - Assert every other T1 tick in the pass **does** increment `comparisons` by 1.
  - Assert every T2 shift tick increments `writes` by 1, and the T2 placement tick increments `writes` by 1.

### F) Counter Accuracy Contract

- For each algorithm with `[4, 7, 2, 6, 1, 5, 3]`:
  - Consume generator to completion.
  - Assert `comparisons` matches expected value (Bubble: 20, Selection: 21, Insertion: 17, Heap: 20).
  - Assert `writes` matches expected value (Bubble: 26, Selection: 10, Insertion: 19, Heap: 30).

### G) T3 Step Counter Exclusion

- Consume the Heap Sort generator for `[4, 7, 2, 6, 1, 5, 3]`.
- Count all ticks where `success=True`, `is_complete=False`, and `operation_type != RANGE`.
- Assert this count equals 35 (the panel step count, with T3 ticks excluded).
