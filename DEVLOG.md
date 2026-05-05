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