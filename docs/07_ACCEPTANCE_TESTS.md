# 07 ACCEPTANCE TESTS.md (Rewritten)

## Definition of Done

All items below must pass to consider the implementation complete:

* Every algorithm reaches a fully sorted final array in ascending order.
* Every algorithm emits exactly one final completion tick.
* No shared mutable array behavior exists between algorithm instances.
* Selection Sort cannot terminate in a near-sorted state.
* Global controls map to Path 2 UI expectations, and independent timers halt correctly on terminal states.

## Acceptance Tests (Human-Checkable)

### AT-01 Startup Baseline

* Launch the application.
* Expect a paused state and 4 visible algorithm panels.
* Expect each panel to start from the same initial values.
* Expect all elapsed timers in the panel headers to read `0.00s`.

### AT-02 Independent Queue Progression

* While paused, press the Step button or keyboard shortcut once.
* Expect each active algorithm to advance its independent animation queue to the conclusion of its currently pending logical operation.
* Repeat multiple times to observe deterministic progression across all panels without forced synchronization.
* Verify the step counter only increments on successful, non-terminal yields.

### AT-03 Completion Correctness (All Algorithms)

* Run the visualizer to completion.
* For each panel, verify final numbers are ascending and unchanged after completion.
* Verify each panel enters its completion state, stops advancing, and its individual elapsed timer permanently halts.

### AT-04 Generator Completion Contract

* Observe a full run for each algorithm.
* Verify there is a clear terminal completion state.
* Verify no additional progress ticks occur after completion.

### AT-05 No Shared Mutable Array Isolation

* Start a run and pause mid-way.
* Confirm each panel diverges only according to its own algorithm path.
* Restart and compare: each algorithm always starts from the same original array, unaffected by other panels' prior mutations.

### AT-06 Selection Sort Regression Guard

* Run the Selection Sort panel to completion.
* Specifically verify the final sequence is fully sorted; no residual inversion is allowed.
* The sequence must explicitly not fail with a trailing inversion like `[..., 12, 11]`.

### AT-07 Failure Isolation

* Simulate one algorithm failure tick (`success=False`).
* Expect only that specific panel to deactivate and show an error state.
* Expect the elapsed timer for that specific panel to freeze.
* Expect all other panels to continue racing to completion.

### AT-08 The Race and Timer Independence

* Press Play to begin the global race.
* Observe that the Tkinter Canvas nodes interpolate at different overall speeds based on operation costs.
* Verify that faster algorithms finish earlier and freeze their timers, while slower algorithms continue updating their elapsed time until they complete.

## Automated Acceptance Intent (for `tests/`)

### A) Minimum Correctness Checks (non-empty fixtures only)

* For each algorithm class with non-empty input, consume the generator to the terminal tick.
* Assert the final `array_state` is sorted ascending.
* Assert the final output is a permutation of the input multiset.
* Assert the completion tick count is exactly 1.

### B) Generator Contract Checks (non-empty fixtures only)

* Assert every yielded item is a `SortResult`.
* Assert a `message` is present on every yield.
* Assert there is exactly one terminal tick where `success=True` and `is_complete=True`.
* Assert no `success=True` and `is_complete=False` ticks are emitted after the terminal tick.

### B2) Empty Input Contract Checks (`empty_0` fixture)

* For each algorithm class with empty input, consume the generator to the terminal tick.
* Assert exactly one failure tick is yielded (`success=False`, `is_complete=False`).
* Assert a `message` is present and describes the empty input condition.
* Assert no completion tick is emitted.
* Assert no progress ticks are emitted.

### C) No Shared Mutable Array Checks

* Instantiate all algorithms with the same source list object.
* Advance one algorithm; assert the other algorithms' internal `data` remains unchanged.
* Mutate the original source list after instantiation; assert model internal states remain unchanged.
* For every successful tick, mutate the returned `array_state`; assert the model internal `data` is unaffected (snapshot-copy guarantee).

### D) Selection Bug Regression Tests

* Ensure the input fixture includes a reverse-sorted array and mixed random arrays.
* For Selection Sort, assert the terminal array is strictly non-decreasing at every adjacent pair.
* Add an explicit guard assertion: no terminal state may contain any inversion index `i` where `a[i] > a[i+1]`.

### E) Controller Queue and Timer Semantics

* Assert the Tkinter controller maintains independent elapsed timers for each active generator based on operation time costs.
* On a completion tick, assert that only that algorithm deactivates and its timer halts.
* On a failure tick, assert that only that algorithm deactivates and its timer halts.
