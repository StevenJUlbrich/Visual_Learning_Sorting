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
* **D-019 Heap Sort visualization in v1 (REVISED — locked):** T3 Range Emphasis ticks required during both Phase 1 (build) and Phase 2 (extraction). In-place motion only (no auxiliary row or tree layout), but Heap Sort must use **multi-index pulsed highlights to simulate tree-node relationships** (parent/children) within the linear array row. Sift-down emits Logical Tree Highlight T3 ticks that flash the parent-child triangle (indices `i`, `2i+1`, `2i+2`) in orange before each level's comparisons, implying binary tree structure without a drawn tree. Boundary T3 ticks display the active heap region with a left-to-right sweep. Two T3 variants are distinguished by highlight contiguity (see `03_DATA_CONTRACTS.md`). See D-051, D-052, D-053, D-054, D-056, D-057, D-058 for detailed mechanics.
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
* **D-033 Z-ordering (REVISED):** Unified principle: any sprite vertically displaced above the baseline (`exact_y < home_y`) renders on top of all baseline sprites. Applies to Bubble Sort compare-lift pairs, Insertion Sort lifted keys, and upward-arcing swap sprites. Among multiple lifted sprites, the highest (`smallest exact_y`) draws last. Default index order when at rest. See `10_ANIMATION_SPEC.md` Section 4.
* **D-034 Font surface caching:** NumberSprites pre-render text surfaces per color state at initialization; no per-frame `font.render()` calls.
* **D-035 Settled color (REVISED by D-044, confirmed by D-055):** Heap Sort extracted elements use `(130, 150, 190)` — desaturated steel-blue that provides the "sorted region" contrast seen in the Heap Sort reference video (`docs/Reference/Heap_Sort_Video_Reference.md` Section 3.2). Elements extracted from the heap permanently transition to this color, visually separating the growing sorted region (right side, steel-blue) from the shrinking active heap (left side, default blue / orange highlights). See D-044 for contrast rationale, D-054 for accent scope, D-055 for lifecycle rules.
* **D-036 Highlight transitions:** Highlights apply instantly at tick start and are replaced instantly by the next tick. No fade transitions.
* **D-037 Write counter semantics:** `writes` counts individual array positions modified. Swap = 2 writes, shift = 1 write, placement = 1 write. Matches standard algorithm analysis.
* **D-038 Comparisons counter semantics:** `comparisons` counts data comparisons only. Insertion Sort key-selection ticks use `OpType.COMPARE` for timing but do not increment the comparisons counter.
* **D-039 Insertion Sort tick sequence (REVISED — locked):** Lift-and-Shift motion choreography. The key-selection T1 tick lifts the key sprite to the compare lane (`home_y - lift_offset`); the key remains elevated across all subsequent compare and shift ticks until the T2 placement tick drops it into its sorted position. Each shift requires both a T1 compare tick and a T2 shift tick — elements shift one at a time, never as a batch (see D-060). A terminating T1 compare is emitted when the loop exits by condition (not by `j < 0`). See `10_ANIMATION_SPEC.md` Section 5.2, `05_ALGORITHMS_VIS_SPEC.md` Section 4.3.
* **D-040 Complexity string format:** Use Unicode superscript: `"O(n²)"` and `"O(n log n)"`. These represent worst-case time complexity.
* **D-041 T3 step counter exclusion:** RANGE ticks (T3) do not increment the panel step counter. They are a visual teaching aid, not an algorithmic operation.
* **D-042 AAA contrast compliance (REVISED — locked):** All foreground colors on panel background `(45, 45, 53)` must meet WCAG 2.1 AAA for their text-size category. Number sprites (FiraCode 28px = large text) require ≥ 4.5:1. Body text (Inter 16px = normal text) requires ≥ 7:1. This requirement applies to all color variants introduced during the visual refinement cycle, including corrected accent colors (D-043), settled/extracted color (D-044), secondary text (D-045), and error text (D-046, AA accepted for red-hued text). Contrast ratios are documented in `04_UI_SPEC.md` Section 5.
* **D-043 Accent color corrections:** Insertion accent changed from `(255, 0, 255)` to `(255, 50, 255)` (4.35:1 → 4.7:1). Selection accent changed from `(255, 80, 80)` to `(255, 95, 95)` (4.24:1 → 4.6:1). Both now meet AAA for large text.
* **D-044 Settled color redesign:** Settled/extracted color changed from `(60, 90, 155)` to `(130, 150, 190)` (2.03:1 → 4.6:1). Visual distinction from default array blue `(100, 150, 255)` is now achieved through desaturation rather than dimming, because a dimmed variant cannot be darker than the default (4.8:1) while still meeting the 4.5:1 AAA floor.
* **D-045 Secondary text uplift:** Secondary text changed from `(170, 170, 180)` to `(190, 190, 200)` (5.93:1 → 7.4:1) to meet AAA for normal text at body font size.
* **D-046 Error text split:** Error border remains `(235, 80, 80)` (border does not require text contrast). Error message text uses `(255, 120, 120)` (5.5:1), meeting AA for normal text. True AAA (7:1) for red-hued text on dark backgrounds is not achievable without shifting to pink; AA is accepted as a practical compromise for error messages.
* **D-047 Metrics line layout:** Metrics are rendered below the title line (not beside it on the same baseline) to prevent text overflow in portrait panels (343px width). Format: `"<Big-O> | <elapsed> | Steps: <n> | Comps: <n> | Writes: <n>"`.
* **D-048 Header vertical rhythm:** Panel header uses proportional insets (`HEADER_INSET_X = panel_width * 0.03`, `HEADER_INSET_Y = panel_height * 0.04`) with minimum pixel floors. Title → metrics → message flow vertically with fixed gaps (4px, 6px).
* **D-049 Font asset path:** Font files bundled in `assets/fonts/` directory. Loading attempts bundled path first, falls back to system fonts.
* **D-050 Fixed font sizes:** Font sizes (24/16/28) are absolute pixel values, not proportional to panel dimensions. Proportional font scaling is deferred to post-v1.
* **D-051 Heap Sort Logical Tree Highlight:** Sift-down emits a T3 tick before each level's comparisons highlighting the parent-child triangle (indices `i`, `2i+1`, `2i+2` where children exist). Non-contiguous orange highlight implies binary tree structure within the flat array row. Applies to both Phase 1 (Build) and Phase 2 (Extraction sift-down). Grounded in `docs/Reference/Heap_Sort_Video_Reference.md` tree-relationship emphasis.
* **D-052 Heap Sort extraction arc elevation:** Extraction swaps (root ↔ end) use `extraction_arc_height = panel_height * 0.14` (1.75× standard `0.08`). Visually distinguishes the phase-transition move from routine sift-down swaps.
* **D-053 Heap Sort Build Max-Heap as structural transformation:** Phase 1 is specified as a structural transformation that enforces binary heap invariants, not merely a sequence of array swaps. Sift-down procedure highlights tree relationships before comparisons to communicate the conceptual model.
* **D-054 Heap accent scope restriction:** Orange accent `(255, 140, 0)` is reserved exclusively for active heap members (indices `0..heap_size-1`). Extracted elements outside the heap boundary never render in orange.
* **D-055 Settled/extracted state lifecycle:** After a Heap Sort extraction swap, the element placed beyond the heap boundary permanently transitions to settled/extracted color `(130, 150, 190)`. This is a one-way transition — settled elements do not revert to default array color. On completion tick, settled color is replaced by the global completion color `(80, 220, 120)`.
* **D-056 Sift-down cadence override:** Post-extraction sift-down ticks use reduced durations (T1: 100ms, T2: 250ms, T3: 130ms) to create a rapid cascading rhythm. Phase 1 (Build Max-Heap) sift-down retains standard durations. The cadence flag is set after each extraction swap and reset at the next boundary T3 tick. See `10_ANIMATION_SPEC.md` Section 5.3.2.
* **D-057 Heap boundary sweep:** Boundary T3 ticks render as a left-to-right staggered sweep (120ms sweep window + 80ms hold) rather than an instant flash. View-layer only; Controller still treats the tick as a single 200ms operation. See `10_ANIMATION_SPEC.md` Section 5.3.1.
* **D-059 Bubble Sort compare-lift:** T1 compare ticks in Bubble Sort trigger a temporary vertical offset (`compare_lift_offset = panel_height * 0.05`) on the adjacent pair `(j, j+1)`. Ascent 0–60ms, hold 60–100ms, descent 100–150ms within the 150ms T1 duration. Both sprites lift as a unit. Selection Sort T1 ticks are unaffected (highlight-only). See `10_ANIMATION_SPEC.md` Section 5.1.1, `05_ALGORITHMS_VIS_SPEC.md` Section 4.1.
* **D-062 Header vertical rhythm as layout invariant:** Header elements stack strictly vertically (Title → Metrics → Message) with no horizontal adjacency. METRICS_GAP = 4px, MESSAGE_GAP = 6px. Total header must not exceed 35% of panel height. Portrait overflow: metrics string truncates from the Writes field leftward, preserving Big-O and elapsed time. See `04_UI_SPEC.md` Section 4.1.1.
* **D-063 Settled color as general concept:** Settled/extracted color `(130, 150, 190)` represents elements that have permanently left the active unsorted region. Provides a "sorted history" visual layer distinct from completion green (which signals the entire sort is finished). v1 scope: Heap Sort only. Designed for post-v1 extensibility to other algorithms. See `04_UI_SPEC.md` Section 5.3.
* **D-061 Compare Lane coordinate:** A conceptual vertical position above the baseline (`home_y - offset`) where sprites reside during comparison or key-selection. Bubble Sort: `compare_lift_offset = panel_height * 0.05` (transient, both sprites). Insertion Sort: `lift_offset = panel_height * 0.06` (sustained, key only). Selection Sort and Heap Sort do not use compare-lane motion. See `10_ANIMATION_SPEC.md` Section 3.4.
* **D-060 Insertion Sort sequential shift guarantee:** Each element shift in Insertion Sort is an individual compare-then-shift tick pair (T1 + T2). Elements must never shift simultaneously as a batch. One-at-a-time pacing is a pedagogical requirement so the learner can trace the leftward ripple of shifts. See `05_ALGORITHMS_VIS_SPEC.md` Section 4.3 Step 2.
* **D-058 RANGE tick active-parent guarantee:** All Heap Sort `OpType.RANGE` ticks must include the sift-down parent index in `highlight_indices` whenever a sift-down is active. For Logical Tree Highlights, the parent is always the first tuple member. For Boundary Emphasis ticks, the parent is included by virtue of the contiguous range — but the contract explicitly requires it even if future refactoring changes the range construction. View distinguishes boundary vs. tree T3 ticks by highlight contiguity (no extra metadata needed). See `03_DATA_CONTRACTS.md` "OpType.RANGE — Heap Sort Highlight Variants".
* **D-064 Insertion Sort sequential shift requirement (locked):** During the compare-and-shift loop, each element must shift individually as a discrete T1 compare + T2 shift tick pair. Elements must **never** shift simultaneously as a batch or block. This one-at-a-time pacing is a pedagogical requirement grounded in the Insertion Sort reference video (`docs/Reference/Insertion_Sort_Video_Reference.md`), which shows elements sliding rightward one by one so the learner can trace the leftward ripple of shifts. The animation time for a pass scales linearly with the number of shifts — this is intentional and must not be optimized away. Strengthens D-060 with explicit video-grounded rationale. See `05_ALGORITHMS_VIS_SPEC.md` Section 4.3 Step 2, `07_ACCEPTANCE_TESTS.md` AT-11.

## Deferred

* **F-001** User-provided custom arrays.
* **F-002** Algorithm picker / dynamic algorithm set.
* **F-003** More than four simultaneous algorithms.
* **F-004** Audio cues.
* **F-005** Dynamic playback speed modification.
