# 08 TEST PLAN - QA Strategy and Execution Matrix

Scope: Implementation-facing QA plan for Sorting Algorithm Visualizer v1.
Primary objective: prevent correctness drift and contract drift while preserving educational visualization behavior.

## 1) Quality Risks and Priorities

### P0 (Highest)
- Algorithm outputs incorrect final order.
- Missing or malformed completion tick.
- Shared mutable state between algorithms corrupts fairness/comparison.
- Selection Sort terminal near-sorted bug reappears.

### P1
- Controller advances unevenly across active algorithms.
- Post-completion ticks continue accidentally.
- Failure in one algorithm halts whole app.

### P2
- Minor UI state inconsistencies (labels/colors) not affecting correctness.

## 2) Test Levels
- Unit tests: model algorithms and data contract invariants.
- Integration tests: controller tick loop, algorithm lifecycle, restart/deactivation.
- Manual exploratory: UI behavior, pacing, readability, and runtime interaction.

## 3) Test Data Strategy

### Required fixtures
- `reverse_7`: `[7, 6, 5, 4, 3, 2, 1]` (default worst-case visual fixture).
- `sorted_7`: `[1, 2, 3, 4, 5, 6, 7]`.
- `mixed_7`: representative shuffled arrays.
- `duplicates_7`: includes repeated values to verify permutation + stable handling assumptions.
- `single_1`: single element.
- `empty_0`: empty array (failure-path expectation).

### Randomized coverage
- Deterministic seeded random arrays for repeatability.
- At least one property-style sweep asserting sorted output + permutation preservation.

## 4) Core Test Cases (Automated)

### TC-A1 Final Sortedness (All Algorithms, non-empty fixtures)
- Arrange: instantiate algorithm with non-empty fixture (`reverse_7`, `sorted_7`, `mixed_7`, `duplicates_7`, `single_1`).
- Act: consume generator until terminal tick.
- Assert: final `array_state` sorted ascending.

### TC-A2 Final Completion Tick Contract (non-empty fixtures)
- Assert exactly one terminal completion tick.
- Assert completion tick has `success=True`, `is_complete=True`, and full-array highlight.

### TC-A3 Tick Stream Contract Validity (non-empty fixtures)
- For each yielded tick, assert required fields and valid state combinations.
- Ensure no non-terminal success tick appears after completion.

### TC-A3b Empty Input Contract (`empty_0` fixture)
- Arrange: instantiate algorithm with `empty_0` (`[]`).
- Act: consume generator to exhaustion.
- Assert: exactly one failure tick yielded (`success=False`, `is_complete=False`).
- Assert: `message` is present and describes empty input.
- Assert: no completion tick and no progress ticks are emitted.

### TC-A4 Snapshot Isolation (`array_state`)
- Mutate returned `array_state` from a yielded tick.
- Assert algorithm internal state is unchanged (copy semantics).

### TC-A5 No Shared Mutable Model State
- Create multiple models from same source list object.
- Advance one model and assert others unchanged.
- Mutate original source list after initialization and assert model states unaffected.

### TC-A6 Selection Regression
- Run Selection Sort across fixture set.
- Assert zero inversions in terminal output.
- Explicitly fail if pattern similar to `[..., 12, 11]` occurs.

### TC-A7 Controller Global Tick Semantics
- With multiple active generators, verify one `next()` per active generator per tick.
- Verify deactivation only for algorithm that completed or failed.

## 5) Manual Test Pass (Release Gate)
- Verify startup paused state and identical initial arrays.
- Verify play/pause/step/restart/speed controls.
- Observe independent completion timing while preserving final static states.
- Trigger one algorithm failure and verify isolation.

## 6) Traceability Matrix
- Correctness: TC-A1, AT-03.
- Final tick contract: TC-A2, TC-A3, AT-04.
- Empty input contract: TC-A3b, D-024.
- No shared mutability: TC-A4, TC-A5, AT-05.
- Selection bug regression: TC-A6, AT-06.

## 7) Tooling and Execution
- Unit/integration automation: `pytest`.
- Optional property-style checks: deterministic seed loops.
- Report format: failing case includes fixture name, algorithm, last 5 ticks, and terminal state payload.

## 8) Exit / Sign-off Criteria
- 100% pass on P0/P1 automated suite.
- Manual release-gate checklist completed with no open critical defects.
- Any deferred issues documented with severity, impact, and mitigation.
