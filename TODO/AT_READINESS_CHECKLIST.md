# AT-01 through AT-27 — Readiness Assessment

Generated: 2026-05-05 | Based on: Phase 7c-4 completion (all choreography wired)

## Legend

| Symbol | Meaning |
|--------|---------|
| ✅ IMPL | Implementation covers this — verify visually |
| ⚠️ GAP | Feature partially or not implemented — action needed before testing |
| 👁️ VISUAL | Requires human observation while running the app |
| 🤖 AUTO | Covered by existing automated tests (Phase 3 / Phase 6e) |

---

## AT-01 Startup Baseline
**Status: ✅ IMPL + 👁️ VISUAL**

The orchestrator starts in paused state (`_running = False`). All four panels render with `INITIAL_ARRAY = [4, 7, 2, 6, 1, 5, 3]`. Counters initialize to zero, elapsed timers to `00.00s`. Panel renderers draw headers with these values from PanelContext defaults.

**What to check visually:**
- [x] 4 panels visible in 2×2 grid
- [p] Each shows `4 7 2 6 1 5 3` as circular ring sprites: The heap sort is showing a populated branch layout tree and shadow of circles below the tree
- [x] All timers read `00.00s`
- [x] All counters read `Steps: 0 | Cmp: 0 | Wr: 0`
- [x] App is paused (no animation)

---

## AT-02 Independent Queue Progression
**Status: ✅ IMPL + 👁️ VISUAL**

`orchestrator.step()` advances each panel's independent queue by one tick. `get_duration()` returns per-OpType durations. T3 RANGE ticks do not increment step counters (Critical Rule #3, enforced in orchestrator).

**What to check visually:**
- [x] Press Step (Right Arrow) once — each panel animates one operation
- [x] Step again — deterministic, no forced sync between panels
- [x] Step counter only increments on T1/T2, not on T3 range highlights

---

## AT-03 Completion Race (All Algorithms)
**Status: ✅ IMPL + 👁️ VISUAL**

Different operation costs (T1=150ms, T2=400ms, T3=200ms, with Heap sift-down overrides) create genuine timing differences. Completed panels freeze their elapsed timer via PanelState.COMPLETED in orchestrator.

**What to check visually:**
- [x] Press Space to play — all four panels animate independently
- [x] Faster algorithms finish first (elapsed timers differ)
- [x] Completed panels stop animating, timers frozen
- [x] Final arrays all show `1 2 3 4 5 6 7`

---

## AT-03a Completion Green Panel
**Status: ✅ IMPL + 👁️ VISUAL**

`PanelRenderer.draw_background()` switches to `COMPLETED_BG = (35, 55, 42)` when `ViewPanelState.COMPLETED` is passed. `_map_panel_state()` in main.py translates orchestrator state to view state. Sprites transition to `ColorState.COMPLETE` (green `(80, 220, 120)`) on terminal tick.

**What to check visually:**
- [x] Each panel background turns muted green `(35, 55, 42)` on completion
- [x] HUD stats (Big-O, elapsed, steps, comparisons, writes) remain visible and frozen
- [x] Green panel is distinct from app background `(30, 30, 35)` and standard panel `(45, 45, 53)`

---

## AT-04 Generator Completion Contract
**Status: ✅ IMPL + 🤖 AUTO + 👁️ VISUAL**

Automated tests (TC-A4 in Phase 6e) verify exactly one terminal tick per algorithm. Orchestrator transitions to PanelState.COMPLETED and stops pulling from generator.

**What to check visually:**
- [x] Clear terminal state per algorithm (green sprites, frozen timer)
- [x] No further progress ticks after completion

---

## AT-05 Selection Sort Regression Guard
**Status: ✅ IMPL + 🤖 AUTO + 👁️ VISUAL**

TC-A6 (Phase 6e integration test) verifies Selection Sort produces fully sorted output. Generator contract ensures no residual inversions.

**What to check visually:**
- [x] Selection Sort final array is `1 2 3 4 5 6 7` — no trailing inversions

---

## AT-06 Failure Isolation
**Status: ✅ IMPL + 🤖 AUTO**

TC-A17/A18 (Phase 6e) test failure isolation with FailingAlgorithm helper. Panel enters FAILED state, other panels continue. `ColorState.ERROR` (red) applied to failed panel sprites.

**What to check visually (optional — requires code modification to inject failure):**
- [ ] Only the failed panel deactivates with error state
- [ ] Other panels continue to completion

---

## AT-07 Sprite Motion and Tweening Smoothness
**Status: ✅ IMPL + 👁️ VISUAL**

Selection Sort uses `_dispatch_default` with sine_arc vertical offset on swaps. Heap Sort uses 2D arc interpolation (`_compute_heap_positions`). Bubble Sort uses compare-lane lift with horizontal slide (no arc at compare lane). All use `ease_in_out_quad` for horizontal motion. dt clamp `min(raw_dt, 33)` prevents overshoot.

**What to check visually:**
- [x] Selection Sort swaps: visible y-axis arc separating the two sprites
- [x] Heap Sort swaps: visible arc motion in tree layout
- [x] Bubble Sort swaps: lift to compare lane, horizontal slide, no arc
- [x] No teleporting or abrupt snaps during play (pausing mid-animation is acceptable)

---

## AT-08 Duplicate Value Stability
**Status: ✅ IMPL + 👁️ VISUAL (Phase 7c-5 added config support)**

The architecture supports duplicates by design (Critical Rule #1: sprite identity by unique ID, never by value). Phase 7c-5 added `[sort].array` to `config.toml` — uncomment and set to `[3, 1, 3, 2, 1, 2, 3]` to test.

**What to check visually:**
- [x] Edit `config.toml`: uncomment `array = [3, 1, 3, 2, 1, 2, 3]`
- [x] Launch app — verify 7 sprites with duplicate values displayed
- [x] Run to completion — verify no sprite disappears or duplicates visually
- [f] Verify final sorted array is `[1, 1, 2, 2, 3, 3, 3]`
- [f] Verify all sprites animate stably across all 4 panels:Answser - the heap sort array is not aligned properly.
- [x] Re-comment the array line in config.toml after testing

---

## AT-09 Heap Sort Two-Phase Visual Distinction
**Status: ✅ IMPL + 👁️ VISUAL**

HeapOverlay renders phase label ("BUILD MAX-HEAP" / "EXTRACTION"). Boundary T3 ticks show staggered orange sweep of active heap. TreeLayout renders binary tree with parent-child edges. Extracted sprites move to sorted row with steel-blue color.

**What to check visually:**
- [x] Phase 1: visible swaps during heap construction (3 violations repaired)
- [x] T3 range emphasis: shrinking active heap highlighted in orange
- [x] Binary tree layout with parent-child edges visible
- [x] Sorted row below tree grows as extractions proceed
- [x] Final: all sprites ascending, green completion color

---

## AT-10 Heap Sort Phase Correctness
**Status: ✅ IMPL + 🤖 AUTO + 👁️ VISUAL**

Heap Sort generator (Phase 2) guarantees build phase completes before extraction. Automated tests (TC-A19) verify phase ordering. Integration test (TC-A15) confirms T3 ticks only during extraction.

**What to check visually:**
- [ ] Build Max-Heap completes fully before any extraction
- [x] After Phase 1, tree represents valid max-heap `[7, 6, 5, 4, 1, 2, 3]`
- [x] Sorted region grows by one per extraction step

---

## AT-11 Insertion Sort Lift-and-Settle Sequence
**Status: ✅ IMPL + 👁️ VISUAL**

`_dispatch_insertion` handles key-lift (single-index T1 with `highlight_indices` length 1), sustained elevation via `_insertion_key_elevated` cross-tick state, and diagonal drop (T2 placement). Key stays at `compare_lane_y - insertion_lift_offset` throughout compare/shift ticks. Placement eases diagonally to home position.

**What to check visually (step through each pass i=1..6):**
- [x] First tick of each pass: key lifts above baseline, single index highlighted
- [x] All subsequent compare/shift ticks: key remains elevated (never drops mid-pass)
- [x] Compare highlights on checked elements; shifts slide right one slot
- [x] Final T2 placement: key eases diagonally to destination slot
- [x] After placement, key is at rest at home_y

---

## AT-12 Counter Accuracy
**Status: ✅ IMPL + 🤖 AUTO + 👁️ VISUAL**

Phase 6e integration tests verify exact counter values: Bubble (20/26), Selection (21/10), Insertion (17/19), Heap (20/30). These are locked in CLAUDE.md.

**What to check visually:**
- [x] Bubble Sort: Cmp=20, Wr=26
- [x] Selection Sort: Cmp=21, Wr=10
- [x] Insertion Sort: Cmp=17, Wr=19
- [x] Heap Sort: Cmp=20, Wr=30

---

## AT-13 Bubble Sort LimitLine Migration
**Status: ✅ IMPL + 👁️ VISUAL**

`BubbleOverlay` manages `LimitLine` which tracks boundary position. `limitline.py` has `advance()` (moves one slot left) and provides the dashed vertical line. ComparisonPointer renders below the active comparison pair.

**What to check visually:**
- [x] Step through Bubble Sort — see vertical dashed line marking sorted boundary
- [x] After each pass: limit line moves exactly one slot left
- [x] Comparison pointer never enters the settled region right of the limit line
- [x] Region right of limit line is visually excluded from scan

---

## AT-14 Bubble Sort Swap-Lift Counter Sync
**Status: ✅ IMPL + 👁️ VISUAL**

BubbleHUD renders Comparisons and Exchanges counters in bottom-left. Counter values come from `ctx.comparisons` and `ctx.writes` which update on tick dispatch (before animation begins). The 3-phase compare-lift choreography (ascent/hold/descent) begins after counter update.

**What to check visually:**
- [x] On comparison: pair turns orange and lifts to compare lane
- [x] Comparisons counter already incremented when lift begins
- [x] On swap: horizontal exchange at compare lane, Exchanges counter increments
- [x] Counters visible throughout swap-lift choreography
- [x] Counter order: comparison first, then exchange (never reversed)

---

## AT-15 T3 Step Counter Exclusion
**Status: ✅ IMPL + 🤖 AUTO + 👁️ VISUAL**

Critical Rule #3: T3 RANGE ticks do not increment step counter. Enforced in orchestrator. TC-A15 (Phase 6e) verifies Heap Sort step count = 35 (20 T1 + 15 T2), excluding 6 T3 ticks.

**What to check visually:**
- [x] Count 6 visible boundary sweep highlights during Heap Sort extraction
- [x] Final Heap Sort step count = 35 (not 41)

---

## AT-16 Accent Color Readability (AAA Contrast)
**Status: ✅ IMPL + 👁️ VISUAL**

Universal orange `(255, 140, 0)` per D-067. Steel-blue `(130, 150, 190)` for settled/extracted. Completion green `(80, 220, 120)`. All defined in `COLOR_MAP` in sprite.py.

**What to check visually:**
- [x] Orange highlights clearly legible against dark panel background
- [x] Heap Sort extracted sprites: steel-blue distinct from default blue and orange
- [x] Completion green is bright and legible

---

## AT-17 Tablet Preset Layout Integrity
**Status: ✅ IMPL + 👁️ VISUAL**

`window.py` supports `load_preset("tablet")` → 1024×768. GridLayout computes panel_rects with proportional spacing. `init_display` sets `NOFRAME` (no resize per D-077). TreeLayout handles panel widths ≥ 489px.

**What to check visually:**
- [x] Set `config.toml` → `preset = "tablet"`
- [x] 4 panels visible, no overlap or clipping
- [x] Metrics line fully visible, not truncated
- [x] Message line doesn't collide with metrics or array
- [x] Number sprites fit within slots
- [x] Arc motion stays within panel boundaries
- [x] Heap Sort tree has clear horizontal separation
- [x] Window cannot be resized

---

## AT-18 Desktop Preset Layout Integrity
**Status: ✅ IMPL + 👁️ VISUAL**

Default config: `preset = "desktop"` → 1280×720. Same layout engine as tablet with larger panels.

**What to check visually:**
- [x] 4 panels visible with proportional spacing
- [x] Header, metrics, message, array regions stacked without overlap
- [x] Text is anti-aliased (smooth edges on curved letters)
- [x] Window cannot be resized

---

## AT-19 Selection Sort Min Tracking
**Status: ✅ IMPL + 👁️ VISUAL**

`SelectionOverlay` tracks `i`, `j`, and `min_idx` from Selection Sort tick messages. Highlight indices in ticks mark `j` and `min_idx` with orange. Message line shows comparison details.

**What to check visually:**
- [x] Two indices highlighted during each T1 compare: scan cursor `j` and `min_idx`
- [x] When new minimum found: min highlight moves to `j`
- [x] When `j` is not smaller: min highlight stays on `min_idx`
- [x] Message line references current minimum on every scan tick

---

## AT-20 Selection Sort Sorted Region Stability
**Status: ✅ IMPL + 👁️ VISUAL (Phase 7c-5)**

`_dispatch_selection` replaces `_dispatch_default` for Selection Sort. `_selection_sorted_count` tracks the growing sorted prefix — increments on T2 SWAP, with `while` catch-up on T1 COMPARE for no-swap passes. `_apply_selection_settled` forces `ColorState.SETTLED` (steel-blue) on sprites at indices `0..sorted_count-1`, surviving the shared highlight reset. On TERMINAL, all sprites transition to green via the shared completion handler.

**What to check visually:**
- [x] Step through Selection Sort — after each swap, the element placed at index `i` turns steel-blue
- [x] Settled elements (indices `0..i`) remain steel-blue on all subsequent passes
- [x] Scan cursor (orange) never highlights settled elements
- [x] Sorted region grows from left to right
- [x] On completion, all elements (including settled) transition to green

---

## AT-21 Heap Sort Tree Visualization
**Status: ✅ IMPL + 👁️ VISUAL**

TreeLayout positions nodes in binary tree. `_draw_heap` renders tree sprites with z-ordering. HeapOverlay draws parent-child edges. Extracted sprites move to sorted row. Tree shrinks by one node per extraction. Sorted row grows right-to-left with steel-blue.

**What to check visually:**
- [x] Phase 1: all 7 elements in binary tree with visible edges
- [x] Root centered at top, children spread horizontally below
- [x] Each extraction: root removed from tree → sorted row below
- [x] Tree visibly shrinks by one node per extraction
- [x] Edges connect correct parent-child nodes, update during sift-down
- [x] Sorted row grows right-to-left with steel-blue rings
- [x] Completion: all elements transition to green (confirmed not an issue)

---

## AT-22 Heap Sort Phase Label
**Status: ✅ IMPL + 👁️ VISUAL**

`HeapPhaseLabel` renders "BUILD MAX-HEAP" or "EXTRACTION" inside the tree area. HeapOverlay tracks phase and calls label.draw(). Label persists throughout each phase.

**What to check visually:**
- [x] During Phase 1: "BUILD MAX-HEAP" visible in orange text in tree area
- [x] When Phase 2 begins: label changes to "EXTRACTION"
- [x] Label visible throughout each phase, not just on individual ticks
- [f] Label is inside the visualization area, not in the message line: Answer heap boundary marker is not aligned properly and leaves the area of the tree and overlaps with the sorted row.

---

## AT-23 Heap Sort Heap Boundary Marker
**Status: ✅ IMPL + 👁️ VISUAL**

`HeapBoundaryLabel` renders boundary marker. HeapOverlay draws dashed line in sorted row separating active heap from sorted slots. Boundary moves left after each extraction.

**What to check visually:**
- [x] Vertical dashed line visible in sorted row below tree
- [x] Boundary moves one position left after each extraction
- [f] Boundary doesn't overlap with sorted elements

---

## AT-24 Selection Sort Pointer Assets
**Status: ✅ IMPL + 👁️ VISUAL**

`PointerSet` (Phase 5e, 25 tests, TC-A23) renders `i`, `j`, `min` labeled arrows. `SelectionOverlay` tracks indices from tick data and updates PointerSet. Coalescing when `j == min` shows only `min`.

**What to check visually:**
- [f] Three labeled pointer arrows visible: `i` (above), `j` (below), `min` (below): `i` pointer is too close to sprites and gets lost in the visual design — needs more vertical offset.
- [x] `i` centered over current outer loop index
- [x] `j` advances left-to-right during scan
- [x] `min` marks current minimum candidate
- [x] When new minimum found: `min` jumps to `j`'s index
- [x] When `j == min`: only `min` shown (coalescing)
- [x] After swap: `i` advances right, `min` resets, `j` starts from `i+1`

---

## AT-25 Insertion Sort KEY Label and Gap
**Status: ✅ IMPL + 👁️ VISUAL**

`InsertionOverlay` renders "KEY" label via `body_font.render()`. `insertion_key_info` property exposes (sprite_id, is_elevated) state. KEY label appears when key is elevated, disappears on placement. Gap at original slot: key sprite moves to compare lane, original position is empty.

**What to check visually:**
- [x] On key-selection T1: "KEY" label appears adjacent to lifted orange circle
- [x] KEY label remains visible throughout compare and shift ticks
- [x] On T2 placement: KEY label disappears as circle settles
- [x] Original baseline slot shows empty space while key is lifted

---

## AT-26 Circular Ring Sprite Shape
**Status: ✅ IMPL + 👁️ VISUAL**

`NumberSprite.draw()` renders `pygame.draw.circle` with `RING_STROKE_WIDTH = 3`, fill with `PANEL_BG_COLOR = (45, 45, 53)`, number text centered. Ring outline and text share same color from `COLOR_MAP`.

**What to check visually:**
- [x] All 28 sprites (7 × 4 panels) are circular outlined rings
- [x] Ring outline color matches number text color (blue `(100, 150, 255)` default)
- [x] Circle interior matches panel background (outlined, not solid-filled)
- [x] No squares, solid fills, or bare text

---

## AT-27 No Algorithm Title Dots
**Status: ✅ IMPL + 👁️ VISUAL**

`PanelRenderer.draw_header()` renders plain text titles. No colored dots or decorative symbols. `_ALGORITHM_NAMES` in main.py: `["Bubble Sort", "Selection Sort", "Insertion Sort", "Heap Sort"]`.

**What to check visually:**
- [x] Four panel titles: plain text only
- [X] No colored dot, circle, or symbol precedes any title

---

## Summary

| Category | Count | Tests |
|----------|-------|-------|
| ✅ Should pass (verify visually) | 26 | AT-01–05, AT-07–27 |
| ✅ Needs code injection to test | 1 | AT-06 (failure isolation) |
| 🤖 Automated coverage exists | 8 | AT-04, AT-05, AT-06, AT-10, AT-12, AT-15 (+ visual) |

All 27 acceptance tests are now implementable. Phase 7c-5 closed both gaps (AT-20 settled color, AT-08 configurable array).

### Recommended Test Order

1. **AT-01, AT-26, AT-27** — Static startup checks (paused state)
2. **AT-18** — Desktop layout integrity
3. **AT-02** — Step-through progression
4. **AT-11, AT-25** — Insertion Sort tick-by-tick (most detailed visual check)
5. **AT-19, AT-24** — Selection Sort pointers and min tracking
6. **AT-13, AT-14** — Bubble Sort limit line and counter sync
7. **AT-09, AT-10, AT-21, AT-22, AT-23** — Heap Sort tree, phases, boundary
8. **AT-15** — T3 step counter exclusion (count boundary sweeps)
9. **AT-07, AT-16** — Motion smoothness and color readability
10. **AT-03, AT-03a, AT-04, AT-05** — Full run to completion
11. **AT-12** — Counter accuracy (verify exact numbers)
12. **AT-17** — Tablet preset (requires config change)
13. **AT-08** — Duplicate values (requires array change)
14. **AT-20** — Selection Sort settled region (step through to verify steel-blue)
15. **AT-06** — Failure isolation (requires code injection — optional)

---

## Issues Found During Visual Testing

### Issue #1 — Heap Sort phase label overlaps root node (AT-22) — ACTIVE
**Severity:** Visual — readability (affects both phases)
**Screenshots:** (1) Startup state — "BUILD MAX-HEAP" collides with root sprite. (2) Extraction state — "EXTRACTION" renders directly on top of root sprite, splitting the word around the orange circle. Label is unreadable throughout the entire extraction phase because every extraction step has an active root node at the same y-coordinate.
**Root cause:** `_PHASE_LABEL_OFFSET` in HeapOverlay is too small. `label_y = self._tree_layout.tree_top - _PHASE_LABEL_OFFSET` places the label at approximately the same y as the root node. Needs a larger offset that accounts for the root node's radius plus clearance.
**Fix target:** `src/visualizer/views/sprite_manager.py` → `_PHASE_LABEL_OFFSET` constant increase, or compute dynamically as `tree_node_radius + font_height + margin`.

### Issue #9 — EXTRACTION label persists after sort completion (AT-22) — ACTIVE
**Severity:** Visual — cosmetic
**Observed:** "EXTRACTION" label remains visible on the completed Heap Sort panel (green background, all sprites green). Other overlays (SelectionOverlay pointers, BubbleOverlay comparison pointer) hide on TERMINAL. HeapOverlay should follow the same pattern.
**Root cause:** `HeapOverlay._process_tick()` TERMINAL handler clears edge highlighting but doesn't clear `self._phase`. `draw_over()` unconditionally draws the phase label regardless of completion state. Needs a `_completed` flag or phase set to `None` on TERMINAL, with a guard in `draw_over()`.
**Fix target:** `src/visualizer/views/sprite_manager.py` → HeapOverlay._process_tick() TERMINAL branch + draw_over() guard.

### Issue #2 — Sorted-row placeholders visible during BUILD MAX-HEAP (AT-21/AT-23) — SUPERSEDED by Issue #6
**Severity:** Visual — cosmetic (lower priority per Steven)
**Screenshot:** Same startup state — gray ghost circles below tree have no meaning until extraction begins.
**Root cause:** `HeapOverlay.draw_under()` draws placeholders unconditionally. Could gate on phase (only draw during EXTRACTION).
**Fix target:** `src/visualizer/views/sprite_manager.py` → HeapOverlay.draw_under() conditional on extraction phase.

### Issue #3 — Heap boundary marker renders outside Heap Sort panel (AT-23) — ACTIVE
**Severity:** Visual — functional (boundary marker crosses panel boundaries)
**Screenshot:** Mid-sort and completion states — dashed boundary line and "heap boundary" label render in the Insertion Sort panel (panel index 2) instead of staying within Heap Sort panel (panel index 3).
**Observed:** The boundary marker starts at the right edge of the Heap Sort area, then as extraction proceeds, it travels leftward and eventually crosses the panel boundary into the Insertion Sort panel area. At completion, the label and dashed line are fully inside the Insertion Sort panel.
**Root cause:** `HeapBoundaryLabel` x-coordinate calculation likely uses absolute coordinates that go negative or cross the panel left edge. The draw routine doesn't clip to the Heap Sort panel rect. Additionally, the dashed line in `HeapOverlay.draw_under()` may extend beyond the panel's left boundary.
**Fix target:** `src/visualizer/views/hud.py` → `HeapBoundaryLabel` coordinate clamping, and/or `src/visualizer/views/sprite_manager.py` → HeapOverlay boundary drawing with panel rect clipping.

### Issue #4 — Selection Sort `i` pointer too close to sprites (AT-24) — ACTIVE
**Severity:** Visual — readability
**Observed:** The `i` pointer arrow (above-array) renders too close to the sprite rings and gets lost in the visual design. The pointer needs more vertical clearance above the sprites to be clearly distinguishable.
**Root cause:** `PointerSet` above-array offset is too small. The gap between the sprite ring top and the `i` arrow tip needs to increase.
**Fix target:** `src/visualizer/views/pointer.py` → above-arrow y-offset calculation (increase vertical gap).

### Issue #5 — Colored dot preceding title (AT-27) — CLOSED
**Resolution:** Confirmed by Steven as not an issue. AT-27 passes.

### Issue #7 — Sprite tracking fails with duplicate values — CLOSED (AT-08)
**Severity:** Functional — **correctness bug**
**Screenshot:** Duplicate array `[3, 1, 3, 2, 1, 2, 3]` completion state. Insertion Sort shows `1, 2, 3, 1, 2, 3, 3` (wrong). Heap Sort sorted row has two sprites vertically misaligned.
**Root cause:** `compute_sprite_moves()` in `orchestrator.py` detects movement by comparing `old_state[i] != new_state[i]`. When a SHIFT copies a value to an adjacent slot that already holds the same value (duplicate), `changed` is empty and the sprite movement goes undetected. Example: shifting value 3 from slot 1 to slot 2 when slot 2 already holds 3 produces identical old/new states. The same bug affects SWAP operations between equal-value slots (Heap Sort extraction of root when root == end value).
**Impact:** Sprites accumulate in wrong positions over the sort. Every algorithm is affected when duplicates are present.
**Fix:** `compute_sprite_moves()` needs augmentation. Two approaches:
  - (A) Pass `operation_type` and `highlight_indices` from the tick. For SHIFT/SWAP ticks, use `highlight_indices` to determine which slots are involved, regardless of whether values changed.
  - (B) Add explicit `(from_slot, to_slot)` fields to SortResult (larger contract change).
  - Approach (A) is preferred — minimal contract change, uses data already available.
**Fix target:** `src/visualizer/controllers/orchestrator.py` → `compute_sprite_moves()` signature and logic, plus all call sites.

### Issue #8 — Heap Sort sorted-row sprites vertically misaligned — CLOSED (AT-08/AT-21)
**Severity:** Visual — functional
**Screenshot:** Same duplicate array completion. Two sprites in sorted row (second `1`, last `3`) float above the baseline while others sit correctly.
**Root cause:** Likely downstream effect of Issue #7 — when extraction swaps between equal values go undetected, the sprite-to-slot mapping diverges from actual positions. The tree-to-sorted-row animation targets wrong sprite IDs, causing some sprites to not fully settle to the sorted row y-position.
**Fix:** Will likely resolve when Issue #7 is fixed. Verify after Issue #7 fix.

### Issue #6 — Sorted-row placeholders visible during BUILD MAX-HEAP (AT-21/AT-23) — ACTIVE
**Severity:** Visual — cosmetic (lower priority)
**Reclassified from Issue #2.** Placeholder circles below the tree are visible from startup even though extraction hasn't begun. Gate drawing on extraction phase.
**Fix target:** `src/visualizer/views/sprite_manager.py` → HeapOverlay.draw_under() conditional on `self._phase == "EXTRACTION"`.
