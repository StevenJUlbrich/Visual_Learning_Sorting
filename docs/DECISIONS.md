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
- D-013 Playback controls: play/pause, step, restart, speed cycle (1x→1.5x→2x→1x wrapping); default speed is 1x at startup and after restart.
- D-014 Startup behavior: app starts paused.
- D-015 Completion behavior: completed panels remain visible and idle while others continue.
- D-016 Failure behavior: failure deactivates only failing algorithm; app keeps running.
- D-017 Theme strategy: shared dark theme + per-algorithm accent colors.
- D-018 Resolution targets: support both 1280x720 (default) and 720x996 via `config.toml` at repo root.
- D-019 Merge visualization in v1: range highlighting required; literal brackets deferred.
- D-020 Domain flow: avoid exception-driven algorithm control flow; use explicit failure states.
- D-021 Message line visibility: `message` line is always visible in the panel UI.
- D-022 Keyboard bindings: Space=play/pause, Right Arrow=step, R=restart, S=speed cycle, Escape=quit.
- D-023 Big-O labels: each algorithm class exposes a `complexity` property; values are Bubble=`O(n²)`, Selection=`O(n²)`, Insertion=`O(n²)`, Merge=`O(n log n)`.
- D-024 Empty array behavior: generators yield exactly one failure tick and stop; no completion tick emitted.
- D-025 Completion tick highlight: completion tick must include `highlight_indices=tuple(range(size))` (full-array highlight).
- D-026 Control bar layout: fixed 48px control bar at bottom of window; panel grid computed from remaining height above it.
- D-027 Branding: standalone identity "Learn Visual - Expand Knowledge"; used as window title.
- D-028 Secondary counters: panels display comparisons and writes counters alongside the step counter; tracked as `comparisons` and `writes` properties on `BaseSortAlgorithm`.

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
- C-005 Message line visibility ambiguity (N-002 said undecided, `04_UI_SPEC.md` assumed always-visible): resolved to always visible, locked as D-021.
