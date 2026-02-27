# 07 ACCEPTANCE TESTS - Human Checks and Automated Intent

Scope: Acceptance criteria for Sorting Algorithm Visualizer v1.
Grounding: `docs/Sorting_Algorithm_Visualizer_Planning.md` and locked visualization/runtime contracts.

## Definition of Done
All items below must pass:
- Every algorithm reaches a fully sorted final array in ascending order.
- Every algorithm emits exactly one final completion tick (`success=True`, `is_complete=True`).
- No shared mutable array behavior exists between algorithm instances.
- Selection Sort cannot terminate in a near-sorted state (reference bug regression blocked).
- Global controls and tick behavior meet `docs/06_BEHAVIOR_SPEC.md`.

## Acceptance Tests (Human-Checkable)

### AT-01 Startup Baseline
- Launch app.
- Expect paused state and 4 visible algorithm panels.
- Expect each panel starts from the same initial values.

### AT-02 Global Tick Consistency
- While paused, press Step once.
- Expect each active algorithm to advance exactly one tick.
- Repeat multiple times; expect deterministic progression with no skipped/extra panel advancement.

### AT-03 Completion Correctness (All Algorithms)
- Run to completion.
- For each panel, verify final numbers are ascending and unchanged after completion.
- Verify each panel enters completion state and stops advancing.

### AT-04 Generator Completion Contract
- Observe full run for each algorithm.
- Verify there is a clear terminal completion state.
- Verify no additional progress ticks occur after completion.

### AT-05 No Shared Mutable Array Isolation
- Start run and pause mid-way.
- Confirm each panel diverges only according to its own algorithm path.
- Restart and compare: each algorithm always starts from same original array, unaffected by other panels' prior mutations.

### AT-06 Selection Sort Regression Guard
- Run Selection Sort panel to completion.
- Specifically verify final sequence is fully sorted; no residual inversion is allowed.
- Failure example (must never occur): trailing inversion like `[..., 12, 11]`.

### AT-07 Failure Isolation
- Simulate one algorithm failure tick (`success=False`).
- Expect only that panel deactivates and shows error state.
- Other panels continue to completion.

## Automated Acceptance Intent (for `tests/`)

### A) Minimum Correctness Checks
- For each algorithm class, consume generator to terminal tick.
- Assert final `array_state` is sorted ascending.
- Assert final output is a permutation of input multiset.
- Assert completion tick count is exactly 1.

### B) Generator Contract Checks
- Assert every yielded item is `SortResult`.
- Assert `message` is present on every yield.
- Assert there is exactly one terminal tick where `success=True and is_complete=True`.
- Assert no `success=True and is_complete=False` ticks are emitted after terminal tick.

### C) No Shared Mutable Array Checks
- Instantiate all algorithms with same source list object.
- Advance one algorithm; assert other algorithm internal `data` remains unchanged.
- Mutate original source list after instantiation; assert model internal states remain unchanged.
- For every successful tick, mutate returned `array_state`; assert model internal `data` is unaffected (snapshot-copy guarantee).

### D) Selection Bug Regression Tests
- Input fixture includes reverse-sorted array and mixed random arrays.
- For Selection Sort, assert terminal array is strictly non-decreasing at every adjacent pair.
- Add explicit guard assertion: no terminal state may contain any inversion index `i` where `a[i] > a[i+1]`.

### E) Controller Tick/Deactivation Semantics
- Per global tick, controller calls `next()` once per active generator.
- On completion tick, only that algorithm deactivates.
- On failure tick, only that algorithm deactivates.

## Exit Criteria
- All acceptance tests pass manually.
- All automated acceptance checks pass in CI/local.
- No open severity-1 or severity-2 defects related to correctness, terminal contract, array isolation, or selection regression.
