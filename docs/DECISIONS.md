# Status values

* Locked: must be followed by all implementation agents.
* Not decided: unresolved; requires explicit decision before affected scope expands.
* Deferred: intentionally postponed beyond v1.

## Locked

* **D-001 Product:** Build Sorting Algorithm Visualizer.
* **D-002 Architecture:** Strict MVC under `src/visualizer/` using a **Pygame front end**.
* **D-003 Algorithms in v1:** Bubble, Selection, Insertion, Heap (fixed set of four).
* **D-004 Visualization primitive:** Pygame Sprite entities with independent `(x, y)` coordinate tracking, target coordinate interpolation, and delta-time (`dt`) updates.
* **D-005 Layout:** 2x2 grid, max 4 simultaneous panels.
* **D-006 Initial data:** identical `[4, 7, 2, 6, 1, 5, 3]` per algorithm instance. Chosen because it is not a valid max-heap (3 violations), has 13 inversions, and produces meaningful visual activity across all four algorithms.
* **D-007 Tick model (REPLACED):** Independent operation queues per algorithm. Time is driven by operation-weighted simulated costs, creating a genuine race.
* **D-008 `SortResult` contract:** Canonical contract is defined in `docs/03_DATA_CONTRACTS.md`.
* **D-009 Step counting:** Increments on successful non-terminal ticks where `operation_type` is not `RANGE`. T3 range emphasis ticks are excluded from the step counter.
* **D-010 Message policy:** `message` is required on every yielded `SortResult`. Messages must include both index and value for clarity.
* **D-011 Array snapshot policy:** successful ticks must include copied `array_state` snapshots.
* **D-012 Controls scope:** Path 2 UI controls.
* **D-013 Playback controls:** play/pause, step, restart.
* **D-014 Startup behavior:** app starts paused.
* **D-015 Completion behavior:** completed panels remain visible and idle, halting their independent elapsed timer.
* **D-016 Failure behavior:** failure deactivates only failing algorithm; app keeps running.
* **D-017 Theme strategy (Option B):** Each panel has a distinct accent color tinted per algorithm.
* **D-018 Resolution targets (Option C):** Support both landscape and portrait window orientations via a config flag.
* **D-019 Heap Sort visualization in v1:** T3 Range Emphasis ticks required during Phase 2 (extraction) to display the active heap boundary; in-place motion only (no auxiliary row).
* **D-020 Domain flow:** avoid exception-driven algorithm control flow; use explicit failure states.
* **D-021 Message line visibility:** `message` line is always visible in the panel UI.
* **D-022 Keyboard bindings:** Space=play/pause, Right Arrow=step, R=restart, Escape=quit.
* **D-023 Big-O labels:** each algorithm class exposes a `complexity` property. Values are worst-case: Bubble `"O(n²)"`, Selection `"O(n²)"`, Insertion `"O(n²)"`, Heap `"O(n log n)"`.
* **D-024 Empty array behavior:** generators yield exactly one failure tick and stop.
* **D-025 Completion tick highlight:** completion tick must include `highlight_indices=tuple(range(size))`.
* **D-026 Control bar layout:** proportional control bar at bottom of window (`window_height * 0.07`).
* **D-027 Branding:** standalone identity "Learn Visual - Expand Knowledge".
* **D-028 Secondary counters:** panels display comparisons and writes counters.
* **D-029 Render loop:** Application uses `pygame.time.Clock` at 60 FPS target. Each frame computes delta-time (`dt`), clamped to 33ms maximum, used for sprite interpolation.
* **D-030 Heap Sort accent color:** `(255, 140, 0)` (orange) — replaces the purple previously assigned to Merge Sort.
* **D-031 Sprite anchor:** Sprite `(exact_x, exact_y)` represents the center of the rendered text surface. Integer `rect` is synced at render time only.
* **D-032 Arc motion:** Swap arcs use `arc_height = panel_height * 0.08` with `sin(pi * t)` offset. Left sprite arcs up, right sprite arcs down.
* **D-033 Z-ordering:** During swap animations, the upward-arcing sprite draws on top. During Insertion Sort lift, the lifted sprite draws on top. Default order is array index.
* **D-034 Font surface caching:** NumberSprites pre-render text surfaces per color state at initialization; no per-frame `font.render()` calls.
* **D-035 Settled color (REVISED by D-044):** Heap Sort extracted elements use `(130, 150, 190)` — desaturated steel-blue variant of the default array value color. See D-044 for rationale.
* **D-036 Highlight transitions:** Highlights apply instantly at tick start and are replaced instantly by the next tick. No fade transitions.
* **D-037 Write counter semantics:** `writes` counts individual array positions modified. Swap = 2 writes, shift = 1 write, placement = 1 write. Matches standard algorithm analysis.
* **D-038 Comparisons counter semantics:** `comparisons` counts data comparisons only. Insertion Sort key-selection ticks use `OpType.COMPARE` for timing but do not increment the comparisons counter.
* **D-039 Insertion Sort tick sequence:** Each shift requires both a T1 compare tick and a T2 shift tick. A terminating T1 compare is emitted when the loop exits by condition (not by `j < 0`). The key sprite remains elevated across all ticks until the T2 placement tick.
* **D-040 Complexity string format:** Use Unicode superscript: `"O(n²)"` and `"O(n log n)"`. These represent worst-case time complexity.
* **D-041 T3 step counter exclusion:** RANGE ticks (T3) do not increment the panel step counter. They are a visual teaching aid, not an algorithmic operation.
* **D-042 AAA contrast compliance:** All foreground colors on panel background `(45, 45, 53)` must meet WCAG 2.1 AAA for their text-size category. Number sprites (FiraCode 28px = large text) require ≥ 4.5:1. Body text (Inter 16px = normal text) requires ≥ 7:1. Contrast ratios are documented in `04_UI_SPEC.md` Section 5.
* **D-043 Accent color corrections:** Insertion accent changed from `(255, 0, 255)` to `(255, 50, 255)` (4.35:1 → 4.7:1). Selection accent changed from `(255, 80, 80)` to `(255, 95, 95)` (4.24:1 → 4.6:1). Both now meet AAA for large text.
* **D-044 Settled color redesign:** Settled/extracted color changed from `(60, 90, 155)` to `(130, 150, 190)` (2.03:1 → 4.6:1). Visual distinction from default array blue `(100, 150, 255)` is now achieved through desaturation rather than dimming, because a dimmed variant cannot be darker than the default (4.8:1) while still meeting the 4.5:1 AAA floor.
* **D-045 Secondary text uplift:** Secondary text changed from `(170, 170, 180)` to `(190, 190, 200)` (5.93:1 → 7.4:1) to meet AAA for normal text at body font size.
* **D-046 Error text split:** Error border remains `(235, 80, 80)` (border does not require text contrast). Error message text uses `(255, 120, 120)` (5.5:1), meeting AA for normal text. True AAA (7:1) for red-hued text on dark backgrounds is not achievable without shifting to pink; AA is accepted as a practical compromise for error messages.
* **D-047 Metrics line layout:** Metrics are rendered below the title line (not beside it on the same baseline) to prevent text overflow in portrait panels (343px width). Format: `"<Big-O> | <elapsed> | Steps: <n> | Comps: <n> | Writes: <n>"`.
* **D-048 Header vertical rhythm:** Panel header uses proportional insets (`HEADER_INSET_X = panel_width * 0.03`, `HEADER_INSET_Y = panel_height * 0.04`) with minimum pixel floors. Title → metrics → message flow vertically with fixed gaps (4px, 6px).
* **D-049 Font asset path:** Font files bundled in `assets/fonts/` directory. Loading attempts bundled path first, falls back to system fonts.
* **D-050 Fixed font sizes:** Font sizes (24/16/28) are absolute pixel values, not proportional to panel dimensions. Proportional font scaling is deferred to post-v1.

## Deferred

* **F-001** User-provided custom arrays.
* **F-002** Algorithm picker / dynamic algorithm set.
* **F-003** More than four simultaneous algorithms.
* **F-004** Audio cues.
* **F-005** Dynamic playback speed modification.
