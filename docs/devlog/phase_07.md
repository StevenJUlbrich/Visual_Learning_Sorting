# Phase 7 — Main Event Loop, Sprite Animation, and Per-Algorithm Choreography

**Delivered:** 2026-05-04 through 2026-05-05
**Scope:** `src/visualizer/main.py` (Pygame event loop, config loading, keyboard bindings, overlay wiring) and `src/visualizer/views/sprite_manager.py` (SpriteManager class, per-algorithm dispatch/motion/draw, four overlay classes). Also `config.toml` (array config in 7c-5).
**Test count:** No new tests — all view integration is visual-only. Cumulative: 339/339 (no regressions across all sub-phases).
**Sub-phases:** 7 (event loop), 7b (sprite rendering), 7c-1 (Selection Sort pointers), 7c-2 (Bubble Sort choreography), 7c-3 (Insertion Sort choreography), 7c-4 (Heap Sort choreography), 7c-5 (Selection Sort settled color + configurable array).

---

## Phase 7 — Main Event Loop (2026-05-04)

Created `src/visualizer/main.py` (211 lines). Pygame event loop with `clock.tick(60)` and `dt = min(raw_dt, 33)` clamp (Critical Rule #7). Keyboard bindings: Space (play/pause), Right Arrow (step), R (restart), Escape (quit). Config loading via `load_preset()` with fallback. Font loading with SysFont fallback chain. Panel renderers draw backgrounds and headers with live metrics from PanelContext.

- `_load_config()` → width/height from `config.toml` or desktop default
- `_load_fonts()` → Inter-Bold (title), Inter-Regular (body), FiraCode-Regular (numbers) with SysFont fallback
- `_map_panel_state()` → translates orchestrator PanelState to view PanelState (name collision resolved with alias)
- `_elapsed_str()`, `_build_metrics()`, `_build_message()` → header string formatters

**Model:** Sonnet 4.6. One ruff correction (list comprehension collapse). Gates: 339/339.

## Phase 7b — Sprite Animation Rendering (2026-05-04)

Created `src/visualizer/views/sprite_manager.py` (158 lines). SpriteManager class owns 7 NumberSprite instances per panel. New-tick detection by identity comparison (`ctx.current_tick is not self._last_tick`). Sprite motion: `ease_in_out_quad` horizontal + `sine_arc` vertical for swaps. Z-ordering: baseline sprites (by home_x) drawn first, lifted sprites (by descending exact_y) on top. Color states: DEFAULT (blue), ACTIVE (orange) from highlight_indices, COMPLETE (green), ERROR (red).

All four algorithms share the same flat baseline + arc-swap motion model at this stage. Per-algorithm choreography deferred to 7c.

**Model:** Sonnet 4.6. Zero corrections. Gates: 339/339.

## Phase 7c — Per-Algorithm Choreography (2026-05-05)

Five sub-phases, each adding algorithm-specific visual behavior to SpriteManager. The 7c series progressively refactored the dispatch and rendering architecture: `_dispatch_tick` was split into shared highlight/terminal/failure handling plus algorithm-specific branches, and `update()` was split into algorithm-specific position computation methods.

### 7c-1: Selection Sort Pointer Overlay

Added `algorithm_name: str` parameter to `SpriteManager.__init__`. Created `SelectionOverlay` class: tracks `i` (sorted boundary), `j` (scan cursor), `min` (minimum tracker) pointer indices from `highlight_indices`. New-pass detection via `_awaiting_new_pass` flag. T2 SWAP hides i/j, keeps min visible. Wired pre-built `PointerSet` from `pointer.py` to panel 1 in `main.py`.

**Model:** Sonnet 4.6. Zero corrections. Gates: 339/339.

### 7c-2: Bubble Sort Choreography

Major SpriteManager refactoring: `_dispatch_tick` split into shared + `_dispatch_bubble` / `_dispatch_default`. Position computation split into `_compute_bubble_positions` / `_compute_default_positions`.

Bubble Sort motion: T1 compare uses 3-phase vertical choreography (ascent 0–67ms to `compare_lane_y`, hold 67–100ms, descent 100–150ms). T2 swap snaps to compare lane then does horizontal exchange (0–300ms) and settle (300–400ms). No arc during swap — sprites slide horizontally while lifted.

Created `BubbleOverlay` class: manages LimitLine (advance per pass via j-decrease detection), BubbleHUD (comparisons + exchanges counters at bottom-left), ComparisonPointer (green upward triangle below active j slot).

**Model:** Sonnet 4.6. Two ruff corrections (import sort order, unused loop variable). Gates: 339/339.

### 7c-3: Insertion Sort Choreography

Cross-tick key elevation: `_insertion_key_id` / `_insertion_key_elevated` persist the lifted key sprite across multiple ticks within a pass. `_dispatch_insertion` handles three cases: key-lift (single-index T1 → sprite moves to `home_y - insertion_lift_offset`), shift exclusion (key sprite excluded from `_animating_sprites` during shift ticks, stays elevated), diagonal drop (single-index T2 placement → ease from elevated position diagonally to destination slot at baseline).

Key-color force in `_dispatch_tick`: after shared highlight reset, if key is elevated, force `ColorState.ACTIVE` on key sprite — keeps it orange across compare/shift ticks where it's not in `highlight_indices`.

Created `InsertionOverlay` class: stateless "KEY" label rendered adjacent to elevated key sprite via `insertion_key_info` property.

**Model:** Sonnet 4.6. Zero corrections. Gates: 339/339.

### 7c-4: Heap Sort Choreography

The most complex sub-phase — fundamentally different from the flat-baseline algorithms.

**TreeLayout integration:** Heap Sort sprites override `home_x`/`home_y` from flat baseline to `TreeLayout.node_positions()` during `__init__`. Active heap elements positioned in binary tree, extracted elements in `TreeLayout.sorted_row_x/y`. `tree_node_radius` applied to sprite ring_radius.

**`_dispatch_heap`:** Discriminates three tick types:

- Boundary T3 (`message.startswith("Active heap")`) → staggered sweep: 120ms sweep window with per-index delay, then 80ms hold. `_apply_heap_sweep` progressively sets `ColorState.ACTIVE`.
- Logical Tree T3 (`message.startswith("Evaluating tree level")`) → simultaneous flash, handled by shared highlight.
- T2 SWAP → record start positions, then distinguish sift-down (lower-slot arcs up) from extraction (root arcs UP despite going to higher slot index — direction based on source position, not target).

**Extraction mechanics:** `_heap_size` decrements before computing target positions so tree geometry is correct for the post-swap state. Non-swapping sprites snap to new tree positions when geometry changes.

**2D arc interpolation (`_compute_heap_positions`):** Both x AND y eased from start to target, with `sine_arc` vertical offset on top. Different from flat-baseline where y arc uses `home_y` directly. Extraction arcs use 1.75× height (`panel_height * 0.14`).

**Steel-blue persistence:** `_apply_sorted_settled` re-forces `ColorState.SETTLED` for sorted-row sprites after each shared highlight reset.

**Z-ordering (`_draw_heap`):** sorted row (left-to-right) → tree sprites (deep-first, higher y draws first) → arcing sprites (downward-first, upward-on-top).

Created `HeapOverlay` class with split draw:

- `draw_under` (before sprites): parent-child edges with active orange highlighting, sorted-row placeholder outlines, dashed boundary marker
- `draw_over` (after sprites): phase label ("BUILD MAX-HEAP" / "EXTRACTION"), boundary label

main.py wired with split render: `heap_overlay.draw_under(surface)` → `sprite_managers[3].draw(surface)` → `heap_overlay.draw_over(surface)`.

**Model: Opus 4.6.** This was the only sub-phase that used Opus instead of Sonnet. The decision was deliberate — 7c-4 has more interacting systems and genuine judgment calls than any prior phase: dual-zone layout, 2D arc physics, extraction direction reversal, sweep timing, split draw ordering, snap-on-geometry-change for non-swapping sprites. Sonnet excels at prescriptive mechanical execution; Opus was needed for the architectural judgment. The bet paid off: zero corrections, plus Opus added a headless smoke test unprompted.

sprite_manager.py: 965 lines. main.py: 337 lines. Zero corrections + headless smoke test. Gates: 339/339.

### 7c-5: Selection Sort Settled Color + Configurable Array

Addressed two acceptance-test gaps identified during AT readiness assessment:

**AT-20 (Selection Sort settled region):** Created `_dispatch_selection` replacing `_dispatch_default` for Selection Sort. Same arc-swap motion model (still uses `_compute_default_positions`), but adds `_selection_sorted_count` tracking. Increments on T2 SWAP. No-swap pass detection: when a T1 COMPARE has `highlight_indices[0]` (min_idx) greater than `_selection_sorted_count`, the gap represents passes where `min_idx == i` (element already in place, no swap emitted). A `while` loop catches up. `_apply_selection_settled` forces `ColorState.SETTLED` on the sorted prefix `0..sorted_count-1`, same pattern as Heap Sort's `_apply_sorted_settled`.

**AT-08 (configurable initial array):** `config.toml` gains optional `[sort]` section with `array` key (commented out by default). `_load_array()` in `main.py` reads config, validates 2–20 integers, falls back to `[4, 7, 2, 6, 1, 5, 3]`. `_build_orchestrator()` parameterized with `initial_array`. All `INITIAL_ARRAY` references in `main()` replaced with config-loaded value.

**Model:** Sonnet 4.6. Zero corrections. Gates: 339/339.

---

## Reflection — Model Selection as an Engineering Decision

Phase 7c surfaced a pattern worth documenting: model selection is not about capability but about task shape.

Five of the six sub-phases (7c-1 through 7c-3, 7c-5) used Sonnet 4.6. Their prompts were highly prescriptive — exact method bodies, exact insertion points, exact routing changes. The agent's job was mechanical execution: follow the blueprint, fix any lint issues, pass the gates. Sonnet is faster, cheaper, and equally reliable for this class of work.

Phase 7c-4 (Heap Sort) was different. The prompt was detailed but contained genuine judgment calls: how to interpolate positions when both x and y change simultaneously, when to decrement heap_size relative to computing target positions, which sprite arcs up vs. down during extraction, how to snap non-swapping sprites when tree geometry changes mid-animation. These aren't ambiguities in the prompt — they're architectural decisions that emerge from the interaction of multiple specified systems. Opus 4.6 handled them cleanly with zero corrections and added value beyond the prompt (headless smoke test).

The lesson: match the model to the decision density, not the code volume. A 200-line change with no judgment calls is Sonnet territory. A 200-line change where 5 lines require understanding why the arc direction reverses for extraction swaps is Opus territory. The cost difference is marginal; the reliability difference on judgment-heavy tasks is not.

---

## Summary

| Sub-phase | Files | Lines at HEAD | Model | Corrections |
| ----------- | ------- | --------------- | ------- | ------------- |
| 7 (event loop) | main.py | 211 | Sonnet 4.6 | 1 ruff |
| 7b (sprite render) | sprite_manager.py, main.py | 158+211 | Sonnet 4.6 | 0 |
| 7c-1 (Selection pointers) | sprite_manager.py, main.py | ~230+270 | Sonnet 4.6 | 0 |
| 7c-2 (Bubble choreography) | sprite_manager.py, main.py | ~400+280 | Sonnet 4.6 | 2 ruff |
| 7c-3 (Insertion choreography) | sprite_manager.py, main.py | ~576+293 | Sonnet 4.6 | 0 |
| 7c-4 (Heap choreography) | sprite_manager.py, main.py | 965+337 | **Opus 4.6** | 0 |
| 7c-5 (Selection settled + config) | sprite_manager.py, main.py, config.toml | ~1000+350 | Sonnet 4.6 | 0 |

Total corrections across Phase 7: 3 (all ruff formatting, no logic errors).
