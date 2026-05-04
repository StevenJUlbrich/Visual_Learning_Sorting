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