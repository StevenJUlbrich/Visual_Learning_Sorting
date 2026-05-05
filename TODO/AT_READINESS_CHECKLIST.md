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
- [ ] 4 panels visible in 2×2 grid
- [ ] Each shows `4 7 2 6 1 5 3` as circular ring sprites
- [ ] All timers read `00.00s`
- [ ] All counters read `Steps: 0 | Cmp: 0 | Wr: 0`
- [ ] App is paused (no animation)

---

## AT-02 Independent Queue Progression
**Status: ✅ IMPL + 👁️ VISUAL**

`orchestrator.step()` advances each panel's independent queue by one tick. `get_duration()` returns per-OpType durations. T3 RANGE ticks do not increment step counters (Critical Rule #3, enforced in orchestrator).

**What to check visually:**
- [ ] Press Step (Right Arrow) once — each panel animates one operation
- [ ] Step again — deterministic, no forced sync between panels
- [ ] Step counter only increments on T1/T2, not on T3 range highlights

---

## AT-03 Completion Race (All Algorithms)
**Status: ✅ IMPL + 👁️ VISUAL**

Different operation costs (T1=150ms, T2=400ms, T3=200ms, with Heap sift-down overrides) create genuine timing differences. Completed panels freeze their elapsed timer via PanelState.COMPLETED in orchestrator.

**What to check visually:**
- [ ] Press Space to play — all four panels animate independently
- [ ] Faster algorithms finish first (elapsed timers differ)
- [ ] Completed panels stop animating, timers frozen
- [ ] Final arrays all show `1 2 3 4 5 6 7`

---

## AT-03a Completion Green Panel
**Status: ✅ IMPL + 👁️ VISUAL**

`PanelRenderer.draw_background()` switches to `COMPLETED_BG = (35, 55, 42)` when `ViewPanelState.COMPLETED` is passed. `_map_panel_state()` in main.py translates orchestrator state to view state. Sprites transition to `ColorState.COMPLETE` (green `(80, 220, 120)`) on terminal tick.

**What to check visually:**
- [ ] Each panel background turns muted green `(35, 55, 42)` on completion
- [ ] HUD stats (Big-O, elapsed, steps, comparisons, writes) remain visible and frozen
- [ ] Green panel is distinct from app background `(30, 30, 35)` and standard panel `(45, 45, 53)`

---

## AT-04 Generator Completion Contract
**Status: ✅ IMPL + 🤖 AUTO + 👁️ VISUAL**

Automated tests (TC-A4 in Phase 6e) verify exactly one terminal tick per algorithm. Orchestrator transitions to PanelState.COMPLETED and stops pulling from generator.

**What to check visually:**
- [ ] Clear terminal state per algorithm (green sprites, frozen timer)
- [ ] No further progress ticks after completion

---

## AT-05 Selection Sort Regression Guard
**Status: ✅ IMPL + 🤖 AUTO + 👁️ VISUAL**

TC-A6 (Phase 6e integration test) verifies Selection Sort produces fully sorted output. Generator contract ensures no residual inversions.

**What to check visually:**
- [ ] Selection Sort final array is `1 2 3 4 5 6 7` — no trailing inversions

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
- [ ] Selection Sort swaps: visible y-axis arc separating the two sprites
- [ ] Heap Sort swaps: visible arc motion in tree layout
- [ ] Bubble Sort swaps: lift to compare lane, horizontal slide, no arc
- [ ] No teleporting or abrupt snaps during play (pausing mid-animation is acceptable)

---

## AT-08 Duplicate Value Stability
**Status: ⚠️ GAP — Needs code change to test**

The architecture supports duplicates by design (Critical Rule #1: sprite identity by unique ID, never by value). However, the app is hardcoded to `INITIAL_ARRAY = [4, 7, 2, 6, 1, 5, 3]` — no duplicates. Testing with `[3, 1, 3, 2, 1, 2, 3]` requires either a config option or a code change to `INITIAL_ARRAY` in main.py.

**Action needed:**
- [ ] Temporarily change `INITIAL_ARRAY` to `[3, 1, 3, 2, 1, 2, 3]` in main.py
- [ ] Verify no sprite disappears or duplicates visually
- [ ] Verify final sorted array is `[1, 1, 2, 2, 3, 3, 3]`
- [ ] Verify all sprites animate stably
- [ ] Revert `INITIAL_ARRAY` after testing

---

## AT-09 Heap Sort Two-Phase Visual Distinction
**Status: ✅ IMPL + 👁️ VISUAL**

HeapOverlay renders phase label ("BUILD MAX-HEAP" / "EXTRACTION"). Boundary T3 ticks show staggered orange sweep of active heap. TreeLayout renders binary tree with parent-child edges. Extracted sprites move to sorted row with steel-blue color.

**What to check visually:**
- [ ] Phase 1: visible swaps during heap construction (3 violations repaired)
- [ ] T3 range emphasis: shrinking active heap highlighted in orange
- [ ] Binary tree layout with parent-child edges visible
- [ ] Sorted row below tree grows as extractions proceed
- [ ] Final: all sprites ascending, green completion color

---

## AT-10 Heap Sort Phase Correctness
**Status: ✅ IMPL + 🤖 AUTO + 👁️ VISUAL**

Heap Sort generator (Phase 2) guarantees build phase completes before extraction. Automated tests (TC-A19) verify phase ordering. Integration test (TC-A15) confirms T3 ticks only during extraction.

**What to check visually:**
- [ ] Build Max-Heap completes fully before any extraction
- [ ] After Phase 1, tree represents valid max-heap `[7, 6, 5, 4, 1, 2, 3]`
- [ ] Sorted region grows by one per extraction step

---

## AT-11 Insertion Sort Lift-and-Settle Sequence
**Status: ✅ IMPL + 👁️ VISUAL**

`_dispatch_insertion` handles key-lift (single-index T1 with `highlight_indices` length 1), sustained elevation via `_insertion_key_elevated` cross-tick state, and diagonal drop (T2 placement). Key stays at `compare_lane_y - insertion_lift_offset` throughout compare/shift ticks. Placement eases diagonally to home position.

**What to check visually (step through each pass i=1..6):**
- [ ] First tick of each pass: key lifts above baseline, single index highlighted
- [ ] All subsequent compare/shift ticks: key remains elevated (never drops mid-pass)
- [ ] Compare highlights on checked elements; shifts slide right one slot
- [ ] Final T2 placement: key eases diagonally to destination slot
- [ ] After placement, key is at rest at home_y

---

## AT-12 Counter Accuracy
**Status: ✅ IMPL + 🤖 AUTO + 👁️ VISUAL**

Phase 6e integration tests verify exact counter values: Bubble (20/26), Selection (21/10), Insertion (17/19), Heap (20/30). These are locked in CLAUDE.md.

**What to check visually:**
- [ ] Bubble Sort: Cmp=20, Wr=26
- [ ] Selection Sort: Cmp=21, Wr=10
- [ ] Insertion Sort: Cmp=17, Wr=19
- [ ] Heap Sort: Cmp=20, Wr=30

---

## AT-13 Bubble Sort LimitLine Migration
**Status: ✅ IMPL + 👁️ VISUAL**

`BubbleOverlay` manages `LimitLine` which tracks boundary position. `limitline.py` has `advance()` (moves one slot left) and provides the dashed vertical line. ComparisonPointer renders below the active comparison pair.

**What to check visually:**
- [ ] Step through Bubble Sort — see vertical dashed line marking sorted boundary
- [ ] After each pass: limit line moves exactly one slot left
- [ ] Comparison pointer never enters the settled region right of the limit line
- [ ] Region right of limit line is visually excluded from scan

---

## AT-14 Bubble Sort Swap-Lift Counter Sync
**Status: ✅ IMPL + 👁️ VISUAL**

BubbleHUD renders Comparisons and Exchanges counters in bottom-left. Counter values come from `ctx.comparisons` and `ctx.writes` which update on tick dispatch (before animation begins). The 3-phase compare-lift choreography (ascent/hold/descent) begins after counter update.

**What to check visually:**
- [ ] On comparison: pair turns orange and lifts to compare lane
- [ ] Comparisons counter already incremented when lift begins
- [ ] On swap: horizontal exchange at compare lane, Exchanges counter increments
- [ ] Counters visible throughout swap-lift choreography
- [ ] Counter order: comparison first, then exchange (never reversed)

---

## AT-15 T3 Step Counter Exclusion
**Status: ✅ IMPL + 🤖 AUTO + 👁️ VISUAL**

Critical Rule #3: T3 RANGE ticks do not increment step counter. Enforced in orchestrator. TC-A15 (Phase 6e) verifies Heap Sort step count = 35 (20 T1 + 15 T2), excluding 6 T3 ticks.

**What to check visually:**
- [ ] Count 6 visible boundary sweep highlights during Heap Sort extraction
- [ ] Final Heap Sort step count = 35 (not 41)

---

## AT-16 Accent Color Readability (AAA Contrast)
**Status: ✅ IMPL + 👁️ VISUAL**

Universal orange `(255, 140, 0)` per D-067. Steel-blue `(130, 150, 190)` for settled/extracted. Completion green `(80, 220, 120)`. All defined in `COLOR_MAP` in sprite.py.

**What to check visually:**
- [ ] Orange highlights clearly legible against dark panel background
- [ ] Heap Sort extracted sprites: steel-blue distinct from default blue and orange
- [ ] Completion green is bright and legible

---

## AT-17 Tablet Preset Layout Integrity
**Status: ✅ IMPL + 👁️ VISUAL**

`window.py` supports `load_preset("tablet")` → 1024×768. GridLayout computes panel_rects with proportional spacing. `init_display` sets `NOFRAME` (no resize per D-077). TreeLayout handles panel widths ≥ 489px.

**What to check visually:**
- [ ] Set `config.toml` → `preset = "tablet"`
- [ ] 4 panels visible, no overlap or clipping
- [ ] Metrics line fully visible, not truncated
- [ ] Message line doesn't collide with metrics or array
- [ ] Number sprites fit within slots
- [ ] Arc motion stays within panel boundaries
- [ ] Heap Sort tree has clear horizontal separation
- [ ] Window cannot be resized

---

## AT-18 Desktop Preset Layout Integrity
**Status: ✅ IMPL + 👁️ VISUAL**

Default config: `preset = "desktop"` → 1280×720. Same layout engine as tablet with larger panels.

**What to check visually:**
- [ ] 4 panels visible with proportional spacing
- [ ] Header, metrics, message, array regions stacked without overlap
- [ ] Text is anti-aliased (smooth edges on curved letters)
- [ ] Window cannot be resized

---

## AT-19 Selection Sort Min Tracking
**Status: ✅ IMPL + 👁️ VISUAL**

`SelectionOverlay` tracks `i`, `j`, and `min_idx` from Selection Sort tick messages. Highlight indices in ticks mark `j` and `min_idx` with orange. Message line shows comparison details.

**What to check visually:**
- [ ] Two indices highlighted during each T1 compare: scan cursor `j` and `min_idx`
- [ ] When new minimum found: min highlight moves to `j`
- [ ] When `j` is not smaller: min highlight stays on `min_idx`
- [ ] Message line references current minimum on every scan tick

---

## AT-20 Selection Sort Sorted Region Stability
**Status: ⚠️ GAP — Steel-blue for Selection Sort NOT implemented**

Selection Sort uses `_dispatch_default`, which does standard highlight-on/highlight-off. There is no logic to transition placed elements to `ColorState.SETTLED` (steel-blue) after each swap. The settled color behavior was implemented for Heap Sort (`_apply_sorted_settled`) but NOT extended to Selection Sort.

**AT-20 requires:**
1. After each Selection Sort swap places the minimum at index `i`, that sprite should transition to `ColorState.SETTLED` (steel-blue `(130, 150, 190)`)
2. Settled elements should never be re-highlighted by the scan cursor
3. Sorted region grows left-to-right with steel-blue color
4. On completion tick, settled elements transition to green

**Action needed:**
- [ ] Implement `_dispatch_selection` method in SpriteManager (analogous to `_dispatch_heap` etc.)
- [ ] Track sorted-region indices, apply `ColorState.SETTLED` after swaps
- [ ] Ensure highlight reset in `_dispatch_tick` does NOT re-highlight settled Selection Sort sprites
- [ ] This is a Phase 7c follow-up — may warrant a 7c-5 prompt

---

## AT-21 Heap Sort Tree Visualization
**Status: ✅ IMPL + 👁️ VISUAL**

TreeLayout positions nodes in binary tree. `_draw_heap` renders tree sprites with z-ordering. HeapOverlay draws parent-child edges. Extracted sprites move to sorted row. Tree shrinks by one node per extraction. Sorted row grows right-to-left with steel-blue.

**What to check visually:**
- [ ] Phase 1: all 7 elements in binary tree with visible edges
- [ ] Root centered at top, children spread horizontally below
- [ ] Each extraction: root removed from tree → sorted row below
- [ ] Tree visibly shrinks by one node per extraction
- [ ] Edges connect correct parent-child nodes, update during sift-down
- [ ] Sorted row grows right-to-left with steel-blue rings
- [ ] Completion: all elements transition to green

---

## AT-22 Heap Sort Phase Label
**Status: ✅ IMPL + 👁️ VISUAL**

`HeapPhaseLabel` renders "BUILD MAX-HEAP" or "EXTRACTION" inside the tree area. HeapOverlay tracks phase and calls label.draw(). Label persists throughout each phase.

**What to check visually:**
- [ ] During Phase 1: "BUILD MAX-HEAP" visible in orange text in tree area
- [ ] When Phase 2 begins: label changes to "EXTRACTION"
- [ ] Label visible throughout each phase, not just on individual ticks
- [ ] Label is inside the visualization area, not in the message line

---

## AT-23 Heap Sort Heap Boundary Marker
**Status: ✅ IMPL + 👁️ VISUAL**

`HeapBoundaryLabel` renders boundary marker. HeapOverlay draws dashed line in sorted row separating active heap from sorted slots. Boundary moves left after each extraction.

**What to check visually:**
- [ ] Vertical dashed line visible in sorted row below tree
- [ ] Boundary moves one position left after each extraction
- [ ] Boundary doesn't overlap with sorted elements

---

## AT-24 Selection Sort Pointer Assets
**Status: ✅ IMPL + 👁️ VISUAL**

`PointerSet` (Phase 5e, 25 tests, TC-A23) renders `i`, `j`, `min` labeled arrows. `SelectionOverlay` tracks indices from tick data and updates PointerSet. Coalescing when `j == min` shows only `min`.

**What to check visually:**
- [ ] Three labeled pointer arrows visible: `i` (above), `j` (below), `min` (below)
- [ ] `i` centered over current outer loop index
- [ ] `j` advances left-to-right during scan
- [ ] `min` marks current minimum candidate
- [ ] When new minimum found: `min` jumps to `j`'s index
- [ ] When `j == min`: only `min` shown (coalescing)
- [ ] After swap: `i` advances right, `min` resets, `j` starts from `i+1`

---

## AT-25 Insertion Sort KEY Label and Gap
**Status: ✅ IMPL + 👁️ VISUAL**

`InsertionOverlay` renders "KEY" label via `body_font.render()`. `insertion_key_info` property exposes (sprite_id, is_elevated) state. KEY label appears when key is elevated, disappears on placement. Gap at original slot: key sprite moves to compare lane, original position is empty.

**What to check visually:**
- [ ] On key-selection T1: "KEY" label appears adjacent to lifted orange circle
- [ ] KEY label remains visible throughout compare and shift ticks
- [ ] On T2 placement: KEY label disappears as circle settles
- [ ] Original baseline slot shows empty space while key is lifted

---

## AT-26 Circular Ring Sprite Shape
**Status: ✅ IMPL + 👁️ VISUAL**

`NumberSprite.draw()` renders `pygame.draw.circle` with `RING_STROKE_WIDTH = 3`, fill with `PANEL_BG_COLOR = (45, 45, 53)`, number text centered. Ring outline and text share same color from `COLOR_MAP`.

**What to check visually:**
- [ ] All 28 sprites (7 × 4 panels) are circular outlined rings
- [ ] Ring outline color matches number text color (blue `(100, 150, 255)` default)
- [ ] Circle interior matches panel background (outlined, not solid-filled)
- [ ] No squares, solid fills, or bare text

---

## AT-27 No Algorithm Title Dots
**Status: ✅ IMPL + 👁️ VISUAL**

`PanelRenderer.draw_header()` renders plain text titles. No colored dots or decorative symbols. `_ALGORITHM_NAMES` in main.py: `["Bubble Sort", "Selection Sort", "Insertion Sort", "Heap Sort"]`.

**What to check visually:**
- [ ] Four panel titles: plain text only
- [ ] No colored dot, circle, or symbol precedes any title

---

## Summary

| Category | Count | Tests |
|----------|-------|-------|
| ✅ Should pass (verify visually) | 24 | AT-01–07, AT-09–19, AT-21–27 |
| ⚠️ Gap — needs implementation | 1 | AT-20 (Selection Sort settled color) |
| ⚠️ Gap — needs config change | 1 | AT-08 (duplicate value array) |
| 🤖 Automated coverage exists | 8 | AT-04, AT-05, AT-06, AT-10, AT-12, AT-15 (+ visual) |

### Known Gaps Requiring Action

**1. AT-20 — Selection Sort Sorted Region Stability (implementation gap)**

Selection Sort currently uses `_dispatch_default` — it has no mechanism to mark placed elements as `ColorState.SETTLED` (steel-blue). This is the only acceptance test that describes a feature not present in the current code. A Phase 7c-5 sub-task is needed to:
- Add `_dispatch_selection` to SpriteManager
- Track the sorted prefix (indices `0..i` after pass `i`)
- Apply `ColorState.SETTLED` to those sprites
- Prevent highlight reset from overriding settled state (same pattern as Heap Sort's `_apply_sorted_settled`)

**2. AT-08 — Duplicate Value Stability (test data gap)**

The implementation architecturally supports duplicates (sprite identity by ID, not value). But the app is hardcoded to `[4, 7, 2, 6, 1, 5, 3]`. Testing requires temporarily changing `INITIAL_ARRAY` in main.py to `[3, 1, 3, 2, 1, 2, 3]`. No code changes needed — just a data swap for one test run.

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
14. **AT-06** — Failure isolation (requires code injection)
15. **AT-20** — ❌ BLOCKED until Selection Sort settled-color is implemented
