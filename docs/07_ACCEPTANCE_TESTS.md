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

### AT-11 Insertion Sort Tick Sequence

- Run Insertion Sort panel, stepping through operations.
- For each pass, verify the visible sequence:
  1. Key element lifts above the array row.
  2. Compare highlights appear on the element being checked and the adjacent position.
  3. If the comparison triggers a shift, the element slides right before the next comparison.
  4. When the insertion point is found, a final comparison highlight shows the element that is not greater than the key (if the key does not go to position 0).
  5. The key drops into the correct position.
- Verify the key sprite remains elevated throughout all compare and shift ticks until placement.

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
- For each outer pass `i`:
  - Assert the first tick is a T1 key-selection on `(i,)`.
  - Assert subsequent T1/T2 ticks alternate correctly: T1 compare, then T2 shift for each element that moves.
  - If the loop exits by condition (`j >= 0`), assert a terminating T1 compare tick is emitted.
  - Assert the final tick of the pass is a T2 placement tick on a single index.

### F) Counter Accuracy Contract

- For each algorithm with `[4, 7, 2, 6, 1, 5, 3]`:
  - Consume generator to completion.
  - Assert `comparisons` matches expected value (Bubble: 20, Selection: 21, Insertion: 17, Heap: 20).
  - Assert `writes` matches expected value (Bubble: 26, Selection: 10, Insertion: 19, Heap: 30).

### G) T3 Step Counter Exclusion

- Consume the Heap Sort generator for `[4, 7, 2, 6, 1, 5, 3]`.
- Count all ticks where `success=True`, `is_complete=False`, and `operation_type != RANGE`.
- Assert this count equals 35 (the panel step count, with T3 ticks excluded).
