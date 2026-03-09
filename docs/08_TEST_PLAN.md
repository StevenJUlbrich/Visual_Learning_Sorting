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

### P1

- Controller processes queues unevenly, causing unintended blocking across active algorithms.
- Failure in one algorithm halts the entire application.
- Heap Sort T3 range emphasis ticks emitted during wrong phase (build instead of extraction).

## 2) Test Levels

- **Unit tests:** Model algorithms, data contract invariants, and `NumberSprite` math helpers (linear interpolation formulas).
- **Integration tests:** Controller queue processing, independent timer accumulation, and algorithm lifecycle.
- **Manual exploratory:** Fluidity of Pygame motion, arc pathing clarity, heap boundary highlight visibility, and runtime interaction (Pause/Step behavior).

## 3) Test Data Strategy

- Required fixtures: `reverse_7`, `sorted_7`, `mixed_7`, `duplicates_7`, `single_1`, `empty_0`.
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
- Assert the Controller accurately calculates the total simulated elapsed time based on the defined operation costs (e.g., `(2 * 150ms) + (1 * 400ms)`).

### TC-A5 Sprite Physics and Math

- Unit test the `NumberSprite` float interpolation function.
- Assert that given a start of `x=0`, a target of `x=100`, and an accumulated `dt` mapping to a `0.5` progress ratio, the exact internal `x` equals `50.0`.
- Assert that upon `progress >= 1.0`, the exact `x` snaps to the target to eliminate drift.

### TC-A6 Controller Fairness

- Ensure all active generators receive execution opportunities.
- No algorithm may stall while others continue progressing.

### TC-A7 Heap Sort Phase Contract

- Consume Heap Sort generator for `reverse_7` fixture.
- Assert at least one T3 Range Emphasis Tick is emitted.
- Assert T3 ticks only appear after the build-max-heap phase concludes (i.e., no T3 ticks while `i` is descending from `n//2 - 1` to `0` during phase 1).
- Assert each T3 tick's `highlight_indices` is `tuple(range(0, k))` for strictly decreasing `k` values across successive T3 ticks.
- Assert sorted region grows by exactly one element between each pair of consecutive T3 ticks.

### TC-A8 Heap Sort Sift-Down Correctness

- Unit-test the sift-down function in isolation with known max-heap violations.
- Assert that after sift-down, the subtree rooted at the target index satisfies the max-heap property.
- Assert that only T1/T2 ticks are emitted by sift-down (no T3 ticks inside sift-down).

## 5) Manual Test Pass (Release Gate)

- Verify startup paused state and identical initial arrays.
- Verify play/pause/step/restart/speed controls.
- **Observe the Race:** Ensure faster algorithms visually finish earlier, freeze their panels, and halt their UI timers.
- **Observe the Physics:** Verify elements slide smoothly, use vertical arcs when swapping, and respect the Option B accent color tinting.
- **Observe Heap Sort Phases:** Verify the orange heap boundary highlight pulses during extraction and visibly shrinks one slot each step.

## 6) Tooling and Execution

- Unit/integration automation: `pytest`. Pygame Controller/Sprite math logic can be tested statelessly without invoking the display `while True:` loop.

## 7) Controller fairness test

    - all active generators receive execution opportunities.
