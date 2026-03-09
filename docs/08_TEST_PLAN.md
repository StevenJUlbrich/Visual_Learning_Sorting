# 08 TEST PLAN - QA Strategy and Execution Matrix

Scope: Implementation-facing QA plan for Sorting Algorithm Visualizer v1 (Pygame Sprite Engine).
Primary objective: Prevent correctness drift, ensure operation-weighted timers are accurate, and validate smooth Pygame interpolation physics.

## 1) Quality Risks and Priorities

### P0 (Highest)

- Algorithm outputs incorrect final order.
- Selection Sort terminal near-sorted bug reappears.
- **Heap Sort phase violation:** Build Max-Heap phase completes incorrectly, causing extraction phase to produce invalid sort order.
- **Independent Timer Desync:** A panel's elapsed time calculates incorrectly based on its operation costs.
- **Physics Derailment:** Sprites calculate incorrect `(x, y)` target coordinates or fail to reach their exact destinations due to float-to-integer rounding drift.
- **Counter inaccuracy:** Comparisons or writes counters do not match expected values for deterministic input, misleading learners about algorithm behavior.
- **Insertion Sort tick sequence violation:** Compare and shift ticks emitted in wrong order, or missing terminating comparison, causing incorrect animation sequence.

### P1

- Controller processes queues unevenly, causing unintended blocking across active algorithms.
- Failure in one algorithm halts the entire application.
- Heap Sort T3 range emphasis ticks emitted during wrong phase (build instead of extraction).
- T3 range emphasis ticks incorrectly incrementing the step counter.
- Insertion Sort key-selection tick incorrectly incrementing the comparisons counter.

## 2) Test Levels

- **Unit tests:** Model algorithms, data contract invariants, counter accuracy, and `NumberSprite` math helpers.
- **Integration tests:** Controller queue processing, independent timer accumulation, step counter logic (T3 exclusion), and algorithm lifecycle.
- **Manual exploratory:** Fluidity of Pygame motion, arc pathing clarity, heap boundary highlight visibility, insertion sort lift/shift/drop sequence, and runtime interaction (Pause/Step behavior).

## 3) Test Data Strategy

- Required fixtures:
  - `default_7`: `[4, 7, 2, 6, 1, 5, 3]` — the application default array. Used for counter accuracy tests and primary correctness checks.
  - `reverse_7`: `[7, 6, 5, 4, 3, 2, 1]` — worst-case for Bubble/Insertion Sort. Used for edge-case testing (note: this is a valid max-heap, so Heap Sort Phase 1 has no swaps).
  - `sorted_7`: `[1, 2, 3, 4, 5, 6, 7]` — best-case for Bubble/Insertion Sort. Used for terminating comparison tests.
  - `duplicates_7`: `[3, 1, 3, 2, 1, 2, 3]` — duplicate stability tests.
  - `single_1`: `[1]` — minimal non-empty input.
  - `empty_0`: `[]` — failure tick contract.
- Deterministic seeded random arrays for repeatability.

## 4) Core Test Cases (Automated)

### TC-A1 Final Sortedness (All Algorithms)

- Arrange: instantiate algorithm with non-empty fixture.
- Act: consume generator until terminal tick.
- Assert: final `array_state` sorted ascending.

### TC-A2 Final Completion Tick Contract

- Assert exactly one terminal completion tick.
- Assert completion tick has `success=True`, `is_complete=True`, and full-array highlight.

### TC-A3 Empty Input Contract (`empty_0` fixture)

- Arrange: instantiate algorithm with `empty_0`.
- Act: consume generator to exhaustion.
- Assert: exactly one failure tick yielded (`success=False`, `is_complete=False`).

### TC-A4 Controller Independent Queues & Timers

- Mock the algorithm generators to yield known operation types (e.g., 2 compares, 1 swap).
- Assert the Controller accurately calculates the total simulated elapsed time based on the absolute defined operation costs (`(2 * 150ms) + (1 * 400ms)`).

### TC-A5 Sprite Physics and Math

- Unit test the `NumberSprite` easing functions (e.g., `ease_in_out_quad`).
- Assert that given a start of `x=0`, a target of `x=100`, and a time ratio `t=0.5`, the internal `x` reflects the mathematical midpoint of the curve (50.0).
- Assert that acceleration/deceleration at `t=0.2` and `t=0.8` are non-linear compared to standard progression.
- Assert that upon `t >= 1.0`, the exact `x` snaps precisely to the target to eliminate drift.

### TC-A6 Controller Fairness

- Ensure all active generators receive execution opportunities.
- No algorithm may stall while others continue progressing.

### TC-A7 Heap Sort Phase Contract

- Consume Heap Sort generator for `default_7` fixture.
- Assert at least one T3 Range Emphasis Tick is emitted.
- Assert T3 ticks only appear after the build-max-heap phase concludes.
- Assert Phase 1 produces at least one T2 swap tick (verifying the input has heap violations).
- Assert each T3 tick's `highlight_indices` is `tuple(range(0, k))` for strictly decreasing `k` values across successive T3 ticks.
- Assert sorted region grows by exactly one element between each pair of consecutive T3 ticks.

### TC-A8 Heap Sort Sift-Down Correctness

- Unit-test the sift-down function in isolation with known max-heap violations.
- Assert that after sift-down, the subtree rooted at the target index satisfies the max-heap property.
- Assert that only T1/T2 ticks are emitted by sift-down (no T3 ticks inside sift-down).

### TC-A9 Insertion Sort Tick Sequence

- Consume Insertion Sort generator for `default_7` fixture.
- For each outer pass `i` (from 1 to 6):
  - Assert the first tick is a T1 (COMPARE) key-selection tick with `highlight_indices == (i,)`.
  - Assert subsequent ticks follow the pattern: T1 compare on `(j, j+1)`, then T2 shift on `(j, j+1)`, for each shifted element.
  - For passes where `j >= 0` at loop exit (key does not go to position 0), assert a terminating T1 compare tick is emitted.
  - Assert the final tick of the pass is a T2 (SHIFT) placement tick on a single index.
- For `default_7`, passes i=1 (key=7) and i=3 (key=6) should emit terminating comparison ticks (loop exits by condition). Passes i=2 (key=2) and i=4 (key=1) should not (loop exits by `j < 0`).

### TC-A10 Counter Accuracy (All Algorithms)

- Consume each algorithm's generator for `default_7` fixture.
- Assert exact counter values:
  - **Bubble Sort:** `comparisons == 20`, `writes == 26`.
  - **Selection Sort:** `comparisons == 21`, `writes == 10`.
  - **Insertion Sort:** `comparisons == 17`, `writes == 19`.
  - **Heap Sort:** `comparisons == 20`, `writes == 30`.

### TC-A11 Key-Selection Does Not Increment Comparisons

- Consume Insertion Sort generator for any non-empty fixture.
- Count the number of T1 ticks where `highlight_indices` has exactly one index (key-selection ticks).
- Assert `algorithm.comparisons` equals total T1 tick count minus the key-selection tick count.

### TC-A12 Swap Writes Count

- Consume Bubble Sort generator for `default_7` fixture.
- Count the number of T2 (SWAP) ticks emitted.
- Assert `algorithm.writes == swap_tick_count * 2`.

### TC-A13 T3 Step Counter Exclusion

- Consume Heap Sort generator for `default_7` fixture.
- Count all ticks where `success=True`, `is_complete=False`, `operation_type != RANGE`.
- Assert this count equals 35 (the expected step count).
- Count all T3 (RANGE) ticks separately and assert count equals 6.

### TC-A14 Insertion Sort Terminating Comparison

- Consume Insertion Sort generator for `sorted_7` fixture (already sorted: `[1, 2, 3, 4, 5, 6, 7]`).
- For each pass `i`, the while-loop condition `arr[j] > key` fails immediately on the first check.
- Assert that each pass emits: T1 key-selection, T1 terminating comparison (showing `arr[i-1] <= key`), T2 placement on `(i,)`.
- Assert no shift ticks are emitted (no elements need to move).

## 5) Manual Test Pass (Release Gate)

- Verify startup paused state and identical initial arrays `[4, 7, 2, 6, 1, 5, 3]`.
- Verify play/pause/step/restart controls.
- **Observe the Race:** Ensure faster algorithms visually finish earlier, freeze their panels, and halt their UI timers.
- **Observe the Physics:** Verify elements slide smoothly, use vertical arcs when swapping, and respect the Option B accent color tinting.
- **Observe Heap Sort Phases:** Verify Phase 1 shows actual swaps (heap being built). Verify the orange heap boundary highlight pulses during extraction and visibly shrinks one slot each step.
- **Observe Insertion Sort Lift/Drop:** Verify the key element lifts above the array, stays elevated during comparisons and shifts, and drops smoothly into position.
- **Verify Counters:** After completion, cross-check displayed comparisons and writes values against expected values for `[4, 7, 2, 6, 1, 5, 3]`.

## 6) Tooling and Execution

- Unit/integration automation: `pytest`. Pygame Controller/Sprite math logic can be tested statelessly without invoking the display `while True:` loop.
