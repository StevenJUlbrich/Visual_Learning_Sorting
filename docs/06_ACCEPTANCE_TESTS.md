# 06 ACCEPTANCE TESTS - Human Checks and Automation Intent

## Definition of Done
All conditions below must be satisfied:
- Canonical docs are internally consistent and match `docs/DECISIONS.md`.
- All four algorithms complete with correctly sorted final arrays.
- Global controls (play/pause/step/speed/restart) behave per `docs/05_BEHAVIOR_SPEC.md`.
- Contract integrity checks pass for generator outputs.
- No regressions on known risks (selection-sort incomplete-final-state issue).

## Human-Checkable Acceptance Tests
### AT-01 Startup State
- Launch app.
- Expect paused state.
- Expect 4 panels visible with algorithm names and step counters at zero.

### AT-02 Global Play/Pause
- Press Play, observe all active panels advance.
- Press Pause, observe all motion stops immediately.

### AT-03 Single Step
- While paused, press Step once.
- Expect each active algorithm to advance exactly one tick.
- Repeat and verify deterministic progression.

### AT-04 Speed Cycle
- Toggle speed through 1x, 1.5x, 2x.
- Expect perceptible pacing change with no logic/state corruption.

### AT-05 Restart
- Run several ticks.
- Press Restart.
- Expect all panels reset to initial data and paused state.

### AT-06 Completion Behavior
- Let run to finish.
- Expect each panel to stop independently on completion, preserve final sorted state, and show completion treatment.

### AT-07 Failure Isolation
- Inject or simulate one algorithm failure state.
- Expect only that panel to stop and show error state; others continue.

### AT-08 Selection Sort Regression Guard
- Verify Selection Sort final array is fully sorted (no near-sorted terminal bug).

## Automated Test Intent (for `tests/`)
### Contract Tests
- Validate all yielded objects conform to `SortResult` schema.
- Assert valid field combinations only.
- Assert `message` present on every yield.
- Assert snapshot immutability pattern (`array_state` is a copy, not live mutable reference).

### Algorithm Correctness Tests
- For each algorithm, consume generator to terminal state and assert final array sorted ascending.
- Assert exactly one completion tick on success path.

### Tick Semantics Tests
- Simulate controller advance cycle and assert one `next()` per active generator per global tick.
- Assert step counter increments only for successful non-terminal ticks.

### Controller Lifecycle Tests
- Restart recreates generators and resets state.
- Failure result deactivates only failing algorithm.
- Completion result deactivates only completed algorithm.

## Non-Functional Checks
- Fonts fallback path works when TTF assets are absent.
- UI remains readable at both supported resolutions.
