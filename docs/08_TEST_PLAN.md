# 08 TEST PLAN - QA Strategy and Execution Matrix

Scope: Implementation-facing QA plan for Sorting Algorithm Visualizer v1 (Tkinter Independent Queue Architecture).
Primary objective: prevent correctness drift, ensure operation-weighted timers are accurate, and validate smooth visual interpolation.

## 1) Quality Risks and Priorities

### P0 (Highest)

* Algorithm outputs incorrect final order.
* Shared mutable state between algorithms corrupts fairness/comparison.
* Selection Sort terminal near-sorted bug reappears.
* **Independent Timer Desync:** A panel's elapsed time calculates incorrectly based on its operation costs, invalidating the "race" concept.

### P1

* **Tweening Failures:** Visual nodes calculate incorrect `(x, y)` target coordinates or fail to reach their destinations.
* Post-completion ticks continue accidentally.
* Failure in one algorithm halts the entire application (breaking queue isolation).

### P2

* Minor UI state inconsistencies (labels/colors) not affecting correctness or timer accuracy.
* Slight frame drops during Tkinter `after()` loop rendering.

## 2) Test Levels

* **Unit tests:** Model algorithms, data contract invariants, and math helpers (interpolation formulas).
* **Integration tests:** Tkinter controller queue processing, independent timer accumulation, algorithm lifecycle, restart/deactivation.
* **Manual exploratory:** Fluidity of motion, pacing, visual readability of the race, and runtime interaction (Pause/Step behavior).

## 3) Test Data Strategy

### Required fixtures

* `reverse_7`: `[7, 6, 5, 4, 3, 2, 1]` (default worst-case visual fixture).
* `sorted_7`: `[1, 2, 3, 4, 5, 6, 7]`.
* `mixed_7`: representative shuffled arrays.
* `duplicates_7`: includes repeated values to verify permutation + stable handling assumptions.
* `single_1`: single element.
* `empty_0`: empty array (failure-path expectation).

### Randomized coverage

* Deterministic seeded random arrays for repeatability.
* At least one property-style sweep asserting sorted output + permutation preservation.

## 4) Core Test Cases (Automated)

### TC-A1 Final Sortedness (All Algorithms, non-empty fixtures)

* Arrange: instantiate algorithm with non-empty fixture (`reverse_7`, `sorted_7`, `mixed_7`, `duplicates_7`, `single_1`).
* Act: consume generator until terminal tick.
* Assert: final `array_state` sorted ascending.

### TC-A2 Final Completion Tick Contract (non-empty fixtures)

* Assert exactly one terminal completion tick.
* Assert completion tick has `success=True`, `is_complete=True`, and full-array highlight.

### TC-A3 Tick Stream Contract Validity (non-empty fixtures)

* For each yielded tick, assert required fields and valid state combinations.
* Ensure no non-terminal success tick appears after completion.

### TC-A3b Empty Input Contract (`empty_0` fixture)

* Arrange: instantiate algorithm with `empty_0` (`[]`).
* Act: consume generator to exhaustion.
* Assert: exactly one failure tick yielded (`success=False`, `is_complete=False`).
* Assert: no completion tick and no progress ticks are emitted.

### TC-A4 Snapshot Isolation (`array_state`)

* Mutate returned `array_state` from a yielded tick.
* Assert algorithm internal state is unchanged (copy semantics).

### TC-A5 No Shared Mutable Model State

* Create multiple models from same source list object.
* Advance one model and assert others unchanged.
* Mutate original source list after initialization and assert model states unaffected.

### TC-A6 Selection Regression

* Run Selection Sort across fixture set.
* Assert zero inversions in terminal output.
* Explicitly fail if pattern similar to `[..., 12, 11]` occurs.

### TC-A7 Controller Independent Queues & Timers (NEW)

* Mock the algorithm generators to yield known operation types (e.g., 2 compares, 1 swap).
* Assert the Controller accurately calculates the total simulated elapsed time based on the defined operation costs (e.g., `(2 * 150ms) + (1 * 400ms)`).
* Verify deactivation and timer halting only occurs for the algorithm that completed or failed.

### TC-A8 Visual Interpolation Math (NEW)

* Unit test the View layer's linear interpolation function.
* Assert that at `progress_ratio = 0.5`, an object moving from `x=0` to `x=100` returns `x=50`.

## 5) Manual Test Pass (Release Gate)

* Verify startup paused state and identical initial arrays.
* Verify play/pause/step/restart/speed controls.
* **Observe the Race:** Ensure faster algorithms visually finish earlier, freeze their panels, and halt their UI timers, while slower algorithms continue animating.
* **Observe Interpolation:** Verify elements slide smoothly between slots without instantly "teleporting."
* Trigger one algorithm failure and verify isolation.

## 6) Traceability Matrix

* Correctness: TC-A1, AT-03.
* Final tick contract: TC-A2, TC-A3, AT-04.
* Empty input contract: TC-A3b.
* No shared mutability: TC-A4, TC-A5, AT-05.
* Selection bug regression: TC-A6, AT-06.
* **Racing / Timers:** TC-A7, AT-08.
* **Tweening:** TC-A8, AT-08.

## 7) Tooling and Execution

* Unit/integration automation: `pytest`. Tkinter Controller logic can be tested statelessly without invoking `mainloop()`.
* Optional property-style checks: deterministic seed loops.
* Report format: failing case includes fixture name, algorithm, last 5 ticks, and terminal state payload.

## 8) Exit / Sign-off Criteria

* 100% pass on P0/P1 automated suite.
* Manual release-gate checklist completed with no open critical defects.
* Any deferred issues documented with severity, impact, and mitigation.
