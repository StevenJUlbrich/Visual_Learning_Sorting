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

## Acceptance Tests (Human-Checkable)

### AT-01 Startup Baseline

- Launch app.
- Expect paused state and 4 visible algorithm panels.
- Expect each panel starts from the same initial values.
- Expect all elapsed timers in the panel headers to read `0.00s`.

### AT-02 Independent Queue Progression

- While paused, press Step once.
- Expect each active algorithm to advance its independent animation queue to the conclusion of its currently pending logical operation, smoothly animating the sprites to their targets.
- Repeat multiple times; expect deterministic progression across all panels without forced synchronization.
- Verify the step counter only increments on successful, non-terminal yields.

### AT-03 Completion Race (All Algorithms)

- Press Play and run to completion.
- Verify faster algorithms finish animating earlier, enter their completion state, and permanently halt their individual elapsed timers.
- For each panel, verify final numbers are ascending and unchanged after completion.

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
- Verify that swaps (Bubble, Selection) utilize a `y`-axis arc to prevent visual collisions.
- Verify that elements do not "teleport" or snap abruptly unless the user pauses or steps mid-animation.

### AT-08 Duplicate value arrays

- animate without sprite identity confusion.

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
