# Status values

* Locked: must be followed by all implementation agents.
* Not decided: unresolved; requires explicit decision before affected scope expands.
* Deferred: intentionally postponed beyond v1.

## Locked

* **D-001 Product:** Build Sorting Algorithm Visualizer.
* **D-002 Architecture:** Strict MVC under `src/visualizer/` using a **Pygame front end**.
* **D-003 Algorithms in v1:** Bubble, Selection, Insertion, Merge (fixed set of four).
* **D-004 Visualization primitive:** Pygame Sprite entities with independent `(x, y)` coordinate tracking, target coordinate interpolation, and delta-time (`dt`) updates.
* **D-005 Layout:** 2x2 grid, max 4 simultaneous panels.
* **D-006 Initial data:** identical `[7, 6, 5, 4, 3, 2, 1]` per algorithm instance.
* **D-007 Tick model (REPLACED):** Independent operation queues per algorithm. Time is driven by operation-weighted simulated costs, creating a genuine race.
* **D-008 `SortResult` contract:** Canonical contract is defined in `docs/03_DATA_CONTRACTS.md`.
* **D-009 Step counting:** Increments strictly according to the defined "step" conditions.
* **D-010 Message policy:** `message` is required on every yielded `SortResult`.
* **D-011 Array snapshot policy:** successful ticks must include copied `array_state` snapshots.
* **D-012 Controls scope:** Path 2 UI controls.
* **D-013 Playback controls:** play/pause, step, restart, speed cycle; default speed is 1x.
* **D-014 Startup behavior:** app starts paused.
* **D-015 Completion behavior:** completed panels remain visible and idle, halting their independent elapsed timer.
* **D-016 Failure behavior:** failure deactivates only failing algorithm; app keeps running.
* **D-017 Theme strategy (Option B):** Each panel has a distinct accent color tinted per algorithm.
* **D-018 Resolution targets (Option C):** Support both landscape and portrait window orientations via a config flag.
* **D-019 Merge visualization in v1:** range highlighting required; literal brackets deferred.
* **D-020 Domain flow:** avoid exception-driven algorithm control flow; use explicit failure states.
* **D-021 Message line visibility:** `message` line is always visible in the panel UI.
* **D-022 Keyboard bindings:** Space=play/pause, Right Arrow=step, R=restart, S=speed cycle, Escape=quit.
* **D-023 Big-O labels:** each algorithm class exposes a `complexity` property.
* **D-024 Empty array behavior:** generators yield exactly one failure tick and stop.
* **D-025 Completion tick highlight:** completion tick must include `highlight_indices=tuple(range(size))`.
* **D-026 Control bar layout:** fixed 48px control bar at bottom of window.
* **D-027 Branding:** standalone identity "Learn Visual - Expand Knowledge".
* **D-028 Secondary counters:** panels display comparisons and writes counters.
* **D-029 Render loop:** Application uses a pygame.time.Clock based render loop. Each frame computes delta-time (dt) used for sprite interpolation.

## Deferred

* **F-001** User-provided custom arrays.
* **F-002** Algorithm picker / dynamic algorithm set.
* **F-003** More than four simultaneous algorithms.
* **F-004** Audio cues.
