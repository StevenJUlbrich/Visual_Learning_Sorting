# DECISIONS - Single Source of Truth

Status values:
- Locked: must be followed by all implementation agents.
- Not decided: unresolved; requires explicit decision before affected scope expands.
- Deferred: intentionally postponed beyond v1.

## Locked
- D-001 Product: Build Sorting Algorithm Visualizer.
- D-002 Architecture: Strict MVC under `src/visualizer/`.
- D-003 Algorithms in v1: Bubble, Selection, Insertion, Merge (fixed set of four).
- D-004 Visualization primitive: numbers, not bars.
- D-005 Layout: 2x2 grid, max 4 simultaneous panels.
- D-006 Initial data: identical `[7, 6, 5, 4, 3, 2, 1]` per algorithm instance.
- D-007 Tick model: one global tick advances each active generator exactly once.
- D-008 `SortResult` canonical contract is defined in `docs/03_DATA_CONTRACTS.md`.
- D-009 Step counting: increment only on successful non-terminal ticks.
- D-010 Message policy: `message` is required on every yielded `SortResult`.
- D-011 Array snapshot policy: successful ticks must include copied `array_state` snapshots.
- D-012 Controls scope: v1 includes on-screen clickable controls plus keyboard parity.
- D-013 Playback controls: play/pause, step, restart, speed cycle (1x/1.5x/2x).
- D-014 Startup behavior: app starts paused.
- D-015 Completion behavior: completed panels remain visible and idle while others continue.
- D-016 Failure behavior: failure deactivates only failing algorithm; app keeps running.
- D-017 Theme strategy: shared dark theme + per-algorithm accent colors.
- D-018 Resolution targets: support both 1280x720 (default) and 720x996 via config.
- D-019 Merge visualization in v1: range highlighting required; literal brackets deferred.
- D-020 Domain flow: avoid exception-driven algorithm control flow; use explicit failure states.

## Not Decided
- N-001 Branding identity for this project (Lightning Labs aligned vs standalone visual identity).
- N-002 Whether to display `message` line always visible or optional toggle in final UI.
- N-003 Whether to add secondary counters (comparisons/writes) beyond single step counter.

## Deferred
- F-001 User-provided custom arrays.
- F-002 Algorithm picker / dynamic algorithm set.
- F-003 More than four simultaneous algorithms.
- F-004 Audio cues.
- F-005 Replay/history timeline.
- F-006 Built-in video export.

## Conflict Resolutions Applied
- C-001 Contract mismatch (`array_state` omitted in some docs): resolved to required-on-success in `03_DATA_CONTRACTS.md`.
- C-002 Control ambiguity (keyboard-only vs clickable): resolved to clickable + keyboard parity for v1.
- C-003 Orientation ambiguity: resolved to dual support, landscape default.
- C-004 Merge bracket ambiguity: resolved to range highlights required, literal bracket drawing deferred.
