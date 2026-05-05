# DEVLOG — Visual Learning Sorting

**Purpose:** Chronological engineering journal. Each entry records the work performed, the decisions made (and their rationale), and the open questions remaining. This is the project's decision trail and the source material for the video journal.

**Format:** Newest entries at the top. Each entry gets a timestamped heading (YYYY-MM-DD HH:MM). Within an entry: *Worked on*, *Decisions*, *Open questions*, *Next*. Entries are terse but complete — they should stand on their own when read six months from now or when scripted into narration.

**Timestamp convention (adopted 2026-04-23):** All entries use `YYYY-MM-DD HH:MM` format in headings to support multiple entries per day. Entries prior to this date used date-only granularity and are preserved as-is in the phase archives.

**Archive structure:** Completed phases are archived into `docs/devlog/` to keep this file lean. Pre-action plans are preserved in the archives — they are valuable video journal material. The archive files are the authoritative record; this file carries only current-phase work and one-line summaries of archived phases. Archives are grouped by layer boundary, not individual phase.

---

## Archived Phases

| Phase | Archive file | Summary |
|-------|-------------|---------|
| 0 + 1 | [`docs/devlog/phase_00_01.md`](docs/devlog/phase_00_01.md) | Project state review, Phase 0 closeout (pyproject, config, pseudocode, implementation order, fonts helper), agentic risk assessment, mempalace post-mortem, context-pack adoption, Phase 1 contracts.py, Correction C verification, model strategy. |
| 2 | [`docs/devlog/phase_02.md`](docs/devlog/phase_02.md) | All four algorithm generators: Bubble Sort (2a, 20/26), Selection Sort (2b, 21/10), Insertion Sort (2c, 17/19), Heap Sort (2d, 20/30/35). Includes pre-action plans, post-action closeouts, corrections, and T3 contiguity spec bug discovery. |
| 3 + 4 | [`docs/devlog/phase_03_04.md`](docs/devlog/phase_03_04.md) | D-081 resolution (message-prefix T3 classification). Phase 3: algorithm unit tests (conftest, bubble, selection, insertion, heap — 29 tests, TC-A1/A2/A3/A7/A8/A9/A10/A11/A12/A13/A14/A19). Phase 4: easing module (ease_in_out_quad, ease_out_cubic, sine_arc — 21 tests, TC-A5). Cumulative: 50/50. |
| 5 | [`docs/devlog/phase_05.md`](docs/devlog/phase_05.md) | View Layer: window.py (GridLayout), sprite.py (NumberSprite, ColorState), panel.py (PanelRenderer, header rhythm, state overlays), tree_layout.py (binary tree geometry, TC-A20/A21/A22), pointer.py (Selection Sort arrows, D-068 coalescing, TC-A23), limitline.py (Bubble Sort boundary), hud.py (BubbleHUD counters, HeapPhaseLabel, HeapBoundaryLabel). 185 view-layer tests, 235 cumulative. Doc 12 color fix. |
| 6 | [`docs/devlog/phase_06.md`](docs/devlog/phase_06.md) | Controller/Orchestrator: PanelState, duration constants, PanelContext, get_duration(), Orchestrator update(dt) core loop, compute_sprite_moves() sprite identity delta, play/pause/step/restart controls, integration tests (TC-A4/A6/A15/A16/A17/A18). 104 orchestrator tests (97 unit + 7 integration), 339 cumulative. Zero logic corrections. Spec paralysis vs. spec insufficiency reflection. |

---

## Current Phase: 7 — Main Event Loop and Pygame Rendering Integration

## 2026-05-04 — Phase 7 pre-action: Main event loop

### Plan

Create `src/visualizer/main.py` exposing a `main()` function (referenced by `pyproject.toml` entry `visual-sort = "visualizer.main:main"`). Responsibilities: load `config.toml` to select resolution preset (fallback to desktop if missing or invalid), initialize Pygame and display via `init_display()`, load fonts with fallback (doc 04 §3.3), instantiate the four algorithm models with `[4, 7, 2, 6, 1, 5, 3]`, create the Orchestrator, build PanelRenderers for the 2×2 grid, and run the Pygame event loop. Event loop: `clock.tick(60)` with `dt = min(raw_dt, 33)` clamp (CLAUDE.md Critical Rule #7), keyboard bindings (Space → play/pause, Right Arrow → step, R → restart, Escape → quit per D-022), `orchestrator.update(dt)` each frame, then render: clear screen, draw each panel's background + header (title, metrics line, message from current_tick), and `pygame.display.flip()`. On-screen control buttons are deferred — keyboard-only for Phase 7. Sprite animation rendering is deferred to Phase 7b — this phase gets the skeleton loop running with panel frames and header text updating live.

### Exit criteria

1. `uv run python -m visualizer.main` launches a 1280×720 window titled "Learn Visual - Expand Knowledge" with 4 panel rectangles visible (headless/dummy driver: no crash, clean exit on Escape).
2. pyright — 0 errors, 0 warnings.
3. ruff check + ruff format — clean.
4. Existing test suite — 339/339 still passing (no regressions).

## 2026-05-04 — Phase 7 closed: Main event loop (post-action)

### Worked on

Created `src/visualizer/main.py` (211 lines). Key structure:

- `_load_config()` — reads `config.toml` via `load_preset()`; catches `FileNotFoundError`, `KeyError`, `ValueError`, and `TOMLDecodeError` with stderr warnings, falls back to desktop 1280×720.
- `_load_fonts()` — tries bundled `assets/fonts/{Inter-Bold,Inter-Regular,FiraCode-Regular}.ttf`; falls back to `SysFont` on `OSError`; never crashes.
- `_elapsed_str()` — integer milliseconds → `"SS.DDs"` format (e.g. 8200 → `"08.20s"`).
- `_map_panel_state()` — translates orchestrator `PanelState` to view `PanelState` (name collision resolved with `PanelState as ViewPanelState`).
- `_build_metrics()` / `_build_message()` — construct header strings from `PanelContext`.
- `main()` — full Pygame event loop: `clock.tick(60)`, `dt = min(raw_dt, 33)` clamp, Space/Right/R/Escape bindings, `orchestrator.update(dt)`, background fill, panel background + header draw, `display.flip()`.

Deleted legacy `main.py` stub at repo root (contained only `print("Hello from visual-learning-sorting!")`).

No sprite animation rendering in this phase — panel frames and live header text are functional. Sprite layer deferred to Phase 7b.

### Corrections

One correction: ruff reformatted `_build_panel_renderers` — collapsed a multi-line list comprehension into a single line. No logic changes.

### Results

- App launch (dummy driver): **PASS**
- `uv run pyright src/visualizer/main.py`: **0 errors, 0 warnings**
- `uv run ruff check` + `uv run ruff format --check`: **clean**
- `uv run pytest tests/ -q`: **339/339 PASSED** (no regressions)

### Next

Phase 7b: sprite animation rendering — wire `NumberSprite` instances into the panel loop, dispatch `sprite_moves` from `PanelContext`, and render sprites each frame with easing.

## 2026-05-04 — Phase 7b pre-action: Sprite animation rendering

### Plan

Create `src/visualizer/views/sprite_manager.py` with a `SpriteManager` class that owns 7 `NumberSprite` instances per panel. Each frame: detect new ticks by comparing `ctx.current_tick` identity, dispatch `sprite_moves` to update sprite home positions, advance interpolation elapsed time by `dt` (only when `ctx.state == ANIMATING_OPERATION`), compute eased positions (`ease_in_out_quad` for horizontal, `sine_arc` for swap vertical offset), apply highlight colors from `highlight_indices`, handle completion/failure color states, and draw sprites with z-ordering (lifted sprites on top). Modify `main.py` to create 4 SpriteManagers and wire them into the render loop after panel headers. All four algorithms use a flat baseline row with standard arc swaps — per-algorithm choreography (compare-lift, key elevation, tree layout) is deferred.

### Exit criteria

1. pyright — 0 errors, 0 warnings
2. ruff check + ruff format — clean
3. Existing test suite — 339/339 still passing (no regressions)
4. Visual: sprites appear at correct home positions in all 4 panels and move on play/step

## 2026-05-04 — Phase 7b closed: Sprite animation rendering (post-action)

### Worked on

Created `src/visualizer/views/sprite_manager.py` (158 lines). Key structure:

- `__init__`: stores panel geometry params for reset; creates 7 `NumberSprite` instances; computes `_arc_height = panel_rect.height * 0.08`; initializes animation state (`_last_tick`, `_animation_elapsed_ms`, `_animation_duration_ms`, `_animating_sprites`, `_swap_left_id`, `_swap_right_id`, `_current_op_type`).
- `_dispatch_tick`: resets all sprites to DEFAULT, applies `highlight_indices` via `slot_to_sprite_id`, handles TERMINAL (all COMPLETE) and FAILURE (all ERROR) with no motion, records start positions before calling `update_home` for each `sprite_moves` entry, sets `_swap_left_id`/`_swap_right_id` by comparing target slots (lower target → arcs UP), computes duration via `get_duration`.
- `update`: identity comparison `ctx.current_tick is not self._last_tick` for new-tick detection; advances `_animation_elapsed_ms` only when `ctx.state == ANIMATING_OPERATION`; computes `t = min(elapsed/duration, 1.0)` and `eased_t = ease_in_out_quad(t)`; for SWAP ops applies `sine_arc(t) * arc_height` vertically (left arcs UP, right arcs DOWN); snaps to home when `t >= 1.0`.
- `draw`: partitions sprites into baseline (`exact_y >= home_y`) and lifted (`exact_y < home_y`); baseline sorted by `home_x`, lifted sorted descending by `exact_y` (smallest draws last = on top).
- `reset`: recreates all sprites from scratch, clears all animation state.

Modified `main.py`: added `SpriteManager` import; renamed `_number_font` → `number_font`; created 4 `SpriteManager` instances from `layout.panel_rects`; added `sm.reset(INITIAL_ARRAY)` to K_r handler; added `sprite_managers[i].update(dt, ctx)` + `sprite_managers[i].draw(surface)` inside panel render loop after `draw_header`.

### Corrections

Zero corrections — clean on first run.

### Results

- `uv run pyright src/visualizer/views/sprite_manager.py src/visualizer/main.py`: **0 errors, 0 warnings**
- `uv run ruff check` + `uv run ruff format --check`: **clean**
- `uv run pytest tests/ -q`: **339/339 PASSED** (no regressions)
- Import check: **PASS**

### Next

Phase 7c: per-algorithm choreography — Bubble Sort compare-lift (3-phase T1 vertical), Insertion Sort sustained key elevation + KEY label + gap visualization, Heap Sort binary tree layout (tree_layout.py wiring), Selection Sort pointer arrows (pointer.py wiring).

## 2026-05-05 — Phase 7c-1 pre-action: Selection Sort pointer overlay

### Plan

Create `SelectionOverlay` class in `sprite_manager.py` that tracks the `i` (sorted boundary), `j` (scan cursor), and `min` (minimum tracker) pointer indices by reading `highlight_indices` from Selection Sort ticks. Wire the pre-built `PointerSet` from `pointer.py` to draw labeled arrows in the Selection Sort panel (index 1). Add `algorithm_name` parameter to `SpriteManager.__init__` as a hook for later choreography sub-phases. No changes to sprite motion — Selection Sort uses the existing baseline arc swap model.

### Exit criteria

1. pyright — 0 errors, 0 warnings
2. ruff check + ruff format — clean
3. Existing test suite — 339/339 still passing (no regressions)
4. Visual: Selection Sort panel shows i/j/min arrows that track the algorithm's scan pattern

## 2026-05-05 — Phase 7c-1 closed: Selection Sort pointer overlay (post-action)

### Worked on

Added `algorithm_name: str` as the first parameter to `SpriteManager.__init__` (stored as `self._algorithm_name`; no behavioral change). Added `from visualizer.views.pointer import PointerSet` import to `sprite_manager.py`. Created `SelectionOverlay` class in `sprite_manager.py` after `SpriteManager`: constructor stores a `PointerSet` reference and initializes all tracking state; `update()` uses identity-check new-tick detection; `_process_tick()` handles T1 COMPARE (new-pass detection via `_awaiting_new_pass` or `j < self._j`, extracts `min_idx`/`j` from `highlight_indices`), T2 SWAP (hides i/j, keeps min visible at `highlight_indices[1]`, sets `_awaiting_new_pass = True`), and TERMINAL/FAILURE (hides all); `draw()` delegates to `PointerSet.draw()`; `reset()` clears all state.

Modified `main.py`: added `PointerSet`, `RING_DIAMETER_RATIO`, and `SelectionOverlay` imports; added `_ALGORITHM_NAMES` module-level constant; updated `SpriteManager` list comprehension to pass `algorithm_name=_ALGORITHM_NAMES[i]`; created `_ring_radius`, `_pointer_set`, and `selection_overlay` after `sprite_managers` in `main()`; wired `selection_overlay.update(ctx)` + `.draw(surface)` inside panel render loop for `i == 1`; added `selection_overlay.reset()` to K_r restart handler.

### Corrections

Zero corrections — clean on first run.

### Results

- `uv run pyright src/visualizer/views/sprite_manager.py src/visualizer/main.py`: **0 errors, 0 warnings**
- `uv run ruff check` + `uv run ruff format --check`: **clean**
- `uv run pytest tests/ -q`: **339/339 PASSED** (no regressions)
- Import check: **PASS**

### Next

Phase 7c-2: Bubble Sort choreography (3-phase compare-lift, horizontal swap slide, LimitLine, BubbleHUD, ComparisonPointer).

## 2026-05-05 — Phase 7c-2 pre-action: Bubble Sort choreography

### Plan

Refactor SpriteManager to support algorithm-specific motion dispatch. For Bubble Sort (panel 0): override T1 compare to a 3-phase vertical choreography (ascent 0–67ms, hold 67–100ms, descent 100–150ms at compare_lane_y = home_y - 50px), override T2 swap from arc to horizontal slide at compare_lane_y (0–300ms) then settle to baseline (300–400ms). Create BubbleOverlay class managing LimitLine (advance per pass via j-decrease detection), BubbleHUD (comparisons + exchanges counters), and ComparisonPointer (green arrow below j). Wire into main.py for panel 0. No changes to Selection/Insertion/Heap Sort behavior — they continue using the default motion model.

### Exit criteria

1. pyright — 0 errors, 0 warnings
2. ruff check + ruff format — clean
3. Existing test suite — 339/339 still passing (no regressions)
4. Visual: Bubble Sort sprites lift during compares, slide horizontally during swaps, green arrow tracks j, dashed line shrinks per pass, counters visible

## 2026-05-05 — Phase 7c-2 closed: Bubble Sort choreography (post-action)

### Worked on

Refactored `SpriteManager` dispatch and position computation: split `_dispatch_tick` into shared highlight/terminal/failure handling + algorithm branch (`_dispatch_bubble` for Bubble Sort, `_dispatch_default` for all others). Split inline position computation in `update()` into `_compute_default_positions` (exact extraction of prior logic — horizontal ease_in_out_quad, sine_arc vertical for swaps) and `_compute_bubble_positions` (3-phase compare-lift: ascent 0–67ms, hold 67–100ms, descent 100–150ms; 2-phase swap slide: horizontal exchange 0–300ms at compare_lane_y, settle 300–400ms). Added `_compare_lane_y = (panel_rect.y + panel_rect.height // 2) - 50` to `SpriteManager.__init__`. Added `BubbleHUD` and `LimitLine` imports to `sprite_manager.py`.

Created `BubbleOverlay` class in `sprite_manager.py`: constructor stores LimitLine/BubbleHUD references and arrow geometry constants; `_process_tick` handles T1 COMPARE (pass-boundary detection via `j < self._j`, calls `limit_line.advance()`, sets pointer visible) and TERMINAL/FAILURE (hides pointer); `draw` calls `limit_line.draw()`, `bubble_hud.draw(comparisons, writes // 2)`, and `_draw_comparison_pointer` for the green upward triangle below slot `_j`; `reset` clears state and calls `limit_line.reset()`.

Modified `main.py`: added `BubbleHUD`, `LimitLine`, and `BubbleOverlay` imports (fixed import sort order on first ruff run); created `_home_y_bubble`, `_limit_line`, `_bubble_hud`, and `bubble_overlay` after `selection_overlay`; wired `bubble_overlay.update(ctx)` + `.draw(surface, ctx.comparisons, ctx.writes)` for `i == 0` in render loop; added `bubble_overlay.reset()` to K_r handler.

### Corrections

Two corrections on first run: (1) ruff I001 — import sort order in `main.py` (`BubbleHUD`/`LimitLine` added after `PointerSet`/`RING_DIAMETER_RATIO`, needed to precede them alphabetically); (2) ruff B007 — unused loop variable `start_y` in `_compute_bubble_positions` SWAP branch renamed to `_start_y`.

### Results

- `uv run pyright src/visualizer/views/sprite_manager.py src/visualizer/main.py`: **0 errors, 0 warnings**
- `uv run ruff check` + `uv run ruff format --check`: **clean**
- `uv run pytest tests/ -q`: **339/339 PASSED** (no regressions)
- Import check: **PASS**

### Next

Phase 7c-3: Insertion Sort choreography (cross-tick key elevation, diagonal drop placement, KEY label, gap visualization).

## 2026-05-05 — Phase 7c-3 pre-action: Insertion Sort choreography

### Plan

Add Insertion Sort's cross-tick key elevation to SpriteManager. Key selection T1 (single-index highlight) lifts the key sprite to home_y - lift_offset (panel_height * 0.06) and holds it there across subsequent compare and shift ticks. Shift T2 (two-index) animates only the baseline sprite horizontally; the key stays elevated and is excluded from _animating_sprites. Placement T2 (single-index) triggers a diagonal drop — both axes eased simultaneously. Force key to ACTIVE (orange) on every tick while elevated. Create InsertionOverlay for the KEY label. Wire into main.py for panel 2.

### Exit criteria

1. pyright — 0 errors, 0 warnings
2. ruff check + ruff format — clean
3. Existing test suite — 339/339 still passing (no regressions)
4. Visual: Insertion Sort key lifts, stays elevated during shifts, drops diagonally, KEY label visible

## 2026-05-05 — Phase 7c-3 closed: Insertion Sort choreography (post-action)

### Worked on

Added Insertion Sort cross-tick key elevation to `SpriteManager`. New `__init__` fields: `_insertion_lift_offset` (panel_height * 0.06), `_insertion_key_id`, `_insertion_key_elevated`, `_insertion_is_placement`.

Added key-color force in `_dispatch_tick`: after highlight application, if key is elevated, forces key sprite to ACTIVE (orange) regardless of whether it appears in `highlight_indices`. Added `_dispatch_insertion` branch in the algorithm dispatch.

Created `_dispatch_insertion`: single-index T1 COMPARE triggers key-lift (records sprite start position, sets `_insertion_key_elevated = True`); two-index T2 SHIFT calls `update_home` for both sprites in `sprite_moves` but only adds the non-key sprite to `_animating_sprites`; single-index T2 SHIFT (placement) sets `_insertion_is_placement = True`, adds key sprite to `_animating_sprites`, clears `_insertion_key_elevated`.

Created `_compute_insertion_positions`: T1 COMPARE eases y from start to `home_y - lift_offset`; T2 SHIFT (horizontal) eases shifted sprite x at fixed y; T2 SHIFT (placement) eases both x and y simultaneously (diagonal drop). Snap-on-completion for key selection snaps to `home_y - lift_offset` (NOT `home_y`) so the elevated position persists until placement.

Added `insertion_key_info` property: returns `(exact_x, exact_y, ring_radius)` when key is elevated, else `None`.

Updated `reset()` to clear all three insertion state fields.

Created `InsertionOverlay` class: pre-renders "KEY" label surface in orange `(255, 140, 0)` in `__init__`; `draw()` positions label above key sprite top (ring_radius + 6px gap) and blits; stateless — purely driven by `key_info` being non-None.

Modified `main.py`: updated import to include `InsertionOverlay`; created `insertion_overlay = InsertionOverlay(body_font)` after BubbleOverlay block; added `insertion_overlay.draw(surface, sprite_managers[i].insertion_key_info)` for `i == 2` in render loop. No `update()` or `reset()` wiring needed (stateless overlay).

### Corrections

One correction: ruff reformatted `sprite_manager.py` (whitespace/line-length adjustments). No logic changes.

### Results

- `uv run pyright src/visualizer/views/sprite_manager.py src/visualizer/main.py`: **0 errors, 0 warnings**
- `uv run ruff check` + `uv run ruff format --check`: **clean**
- `uv run pytest tests/ -q`: **339/339 PASSED** (no regressions)
- Import check: **PASS**

### Next

Phase 7c-4: Heap Sort choreography (TreeLayout integration, parent-child edges, extraction arc, boundary sweep, sorted row, phase/boundary labels).

## 2026-05-05 — Phase 7c-4 pre-action: Heap Sort choreography

### Plan

Integrate TreeLayout into SpriteManager for the Heap Sort panel (index 3). Override sprite home positions from flat baseline to binary tree layout + sorted row. Add `_dispatch_heap` for tree-aware tick handling: Boundary T3 with staggered sweep, Logical Tree T3 simultaneous flash, sift-down standard arcs, extraction elevated arcs (1.75×), steel-blue extracted coloring. Create HeapOverlay class for parent-child edges (with active orange highlighting during Logical Tree T3), phase label (BUILD MAX-HEAP / EXTRACTION), sorted-row placeholder outlines, and heap boundary marker. Wire into main.py with split draw order (edges before sprites, labels after).

### Exit criteria

1. pyright — 0 errors, 0 warnings
2. ruff check + ruff format — clean
3. Existing test suite — 339/339 still passing (no regressions)
4. Visual: Heap Sort panel shows binary tree with sifting arcs, extraction arcs to sorted row, edges, phase label, boundary marker

## 2026-05-05 — Phase 7c-4 closed: Heap Sort choreography (post-action)

### Worked on

`SpriteManager` extended with Heap Sort tree-aware choreography:

- New `tree_layout: TreeLayout | None = None` constructor parameter (last). Heap Sort fields: `_tree_layout`, `_heap_size`, `_heap_node_positions`, `_extraction_arc_height` (panel_height * 0.14, 1.75× standard), `_is_extraction_swap`, `_heap_sweep_indices`. Initial position override applies tree node positions and `tree_node_radius` to all sprites for the Heap Sort panel (panel index 3 only).
- `_dispatch_heap` — branches on op type. RANGE: discriminates Boundary T3 (`message.startswith("Active heap")`) vs Logical Tree T3 by D-081 message prefix. Boundary T3 resets all sprites to DEFAULT, sets `_heap_sweep_indices`, and re-applies SETTLED for sorted-row sprites. Logical Tree T3 leaves shared highlight code's parent+children orange flash intact. SWAP: detects extraction (highlight contains 0), decrements `_heap_size` and recomputes positions BEFORE setting target homes, snaps non-swapping tree sprites to new geometry (handles depth-boundary changes like 4→3), assigns `_swap_left_id`/`_swap_right_id` based on source position for extractions (root → up, end → down) or target slot for sift-down (lower target → up).
- `_set_heap_home`, `_recompute_heap_positions`, `_apply_sorted_settled` helpers.
- `_compute_heap_positions` — 2D arc interpolation: eases both x and y from start to home (start_y ≠ home_y in tree), adds `arc_height * sine_arc(t)` vertical offset on top. Selects `_extraction_arc_height` vs `_arc_height` based on `_is_extraction_swap`. On completion, snaps to home, sets SETTLED on extracted sprite, clears swap state.
- `_apply_heap_sweep` — staggered coloring during Boundary T3. Per-index delay = `(i / end) * 120ms` over the 200ms tick (120ms sweep window + 80ms hold). Each index snaps to ACTIVE at its delay threshold. Single-element fallback: highlight immediately. Cleared on `t >= 1.0`.
- Sweep call wired in `update()` after position computation, gated on `_heap_sweep_indices is not None and _animation_duration_ms > 0` (fires for Boundary T3 even when `_animating_sprites` is empty).
- `_draw_heap` — overrides `draw()` for Heap Sort: partitions sprites into sorted-row (home_y >= sorted_row_y - 1), tree (home_y < sorted_row_y), and arcing (id in `_animating_sprites`). Draws sorted row first (left→right by home_x), tree next (deeper-first by home_y desc), arcing last (downward-arcing first, upward-arcing on top by exact_y desc).
- `heap_size` property exposed for HeapOverlay. `reset()` re-initializes Heap state and re-applies tree positions.

`HeapOverlay` class added to `sprite_manager.py`:
- Module-level constants: `_BOUNDARY_DASH=6`, `_BOUNDARY_GAP=4`, `_BOUNDARY_LINE_COLOR=(150,150,160)`, `_BOUNDARY_LINE_WIDTH=2`, `_PHASE_LABEL_OFFSET=20`, `_BOUNDARY_LABEL_OFFSET=15`.
- `update(ctx, heap_size)` — reads heap_size each frame, processes new ticks via identity check.
- `_process_tick` — Boundary T3 switches `_phase` to "EXTRACTION", clears edge highlight; Logical Tree T3 sets `_active_edge_parent` (hi[0]) and `_active_edge_children` (hi[1:]); COMPARE/SWAP/TERMINAL/FAILURE clear edge highlight.
- `draw_under` — calls `_draw_edges` (per-edge active check via parent/children indices, since `tree_layout.edges()` returns positions only), `_draw_placeholders` (dim circle outlines in sorted row for active heap slots), `_draw_boundary_line` (vertical dashed line, gated on `_heap_size < _array_size`).
- `draw_over` — phase label centered above tree top; boundary label below sorted row when active heap < array size.

`main.py` wiring:
- Added imports: `HeapBoundaryLabel`, `HeapPhaseLabel`, `compute_header_total`, `TreeLayout`, `HeapOverlay`.
- TreeLayout built before sprite_managers using `compute_header_total(panel_rects[3].height, title_h, body_h, body_h)`.
- `tree_layout=_heap_tree_layout if i == 3 else None` passed to each SpriteManager.
- HeapOverlay constructed with HeapPhaseLabel and HeapBoundaryLabel.
- Render loop split-draw for panel 3: `heap_overlay.update(ctx, sprite_managers[3].heap_size)` + `draw_under(surface)` BEFORE `sprite_managers[i].draw(surface)`; `heap_overlay.draw_over(surface)` AFTER.
- `heap_overlay.reset()` added to K_r restart handler.

### Corrections

One correction: ruff reformatted `sprite_manager.py` (whitespace/line-length adjustments — same as 7c-3). No logic changes.

### Results

- `uv run pyright src/visualizer/views/sprite_manager.py src/visualizer/main.py`: **0 errors, 0 warnings**
- `uv run ruff check` + `uv run ruff format --check`: **clean**
- `uv run pytest tests/ -q`: **339/339 PASSED** (no regressions)
- Import check: **PASS**
- Bonus smoke test (headless construct/draw/reset of SpriteManager + HeapOverlay): **PASS**

### Next

Phase 7c complete — all four algorithms have per-panel choreography. Next: visual verification (AT acceptance tests), then CLAUDE.md / IMPLEMENTATION_TRACKER updates.