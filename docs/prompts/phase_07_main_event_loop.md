# Phase 7 — Main Event Loop (`src/visualizer/main.py`)

## Copy everything below this line into Claude Code

---

You are implementing Phase 7 of the Sorting Algorithm Visualizer. This phase creates `src/visualizer/main.py` — the entry point that wires the Pygame event loop to the existing Orchestrator (Phase 6) and View layer (Phase 5), making the app runnable for the first time.

## Rules

- Do NOT run any git commands.
- Do NOT create new spec or documentation files.
- Do NOT modify any existing algorithm, view, or controller files — only create `src/visualizer/main.py`.
- All four lint/typecheck/test gates must pass before you stop.
- Follow existing code style: `from __future__ import annotations`, docstrings on all public functions/classes, ruff + pyright strict clean.

## STEP 1 — DEVLOG PRE-ACTION

Append the following entry to the **top** of the current-phase section in `DEVLOG.md` (immediately below the `## Current Phase: 7` heading and the placeholder text). Remove the `*No entries yet.*` placeholder if present.

```markdown
## 2026-05-04 — Phase 7 pre-action: Main event loop

### Plan

Create `src/visualizer/main.py` exposing a `main()` function (referenced by `pyproject.toml` entry `visual-sort = "visualizer.main:main"`). Responsibilities: load `config.toml` to select resolution preset (fallback to desktop if missing or invalid), initialize Pygame and display via `init_display()`, load fonts with fallback (doc 04 §3.3), instantiate the four algorithm models with `[4, 7, 2, 6, 1, 5, 3]`, create the Orchestrator, build PanelRenderers for the 2×2 grid, and run the Pygame event loop. Event loop: `clock.tick(60)` with `dt = min(raw_dt, 33)` clamp (CLAUDE.md Critical Rule #7), keyboard bindings (Space → play/pause, Right Arrow → step, R → restart, Escape → quit per D-022), `orchestrator.update(dt)` each frame, then render: clear screen, draw each panel's background + header (title, metrics line, message from current_tick), and `pygame.display.flip()`. On-screen control buttons are deferred — keyboard-only for Phase 7. Sprite animation rendering is deferred to Phase 7b — this phase gets the skeleton loop running with panel frames and header text updating live.

### Exit criteria

1. `uv run python -m visualizer.main` launches a 1280×720 window titled "Learn Visual - Expand Knowledge" with 4 panel rectangles visible (headless/dummy driver: no crash, clean exit on Escape).
2. pyright — 0 errors, 0 warnings.
3. ruff check + ruff format — clean.
4. Existing test suite — 339/339 still passing (no regressions).
```

## STEP 2 — IMPLEMENTATION

Create `src/visualizer/main.py` with the following structure.

### 2.1 Config loading

```python
def _load_config() -> tuple[int, int]:
    """Load config.toml and return (width, height); default to desktop on any error."""
```

- Use `tomllib` (stdlib Python 3.11+).
- Config path: `Path(__file__).resolve().parents[2] / "config.toml"` (two levels up from `src/visualizer/main.py` reaches the repo root).
- If the file is missing, log a warning to stdout and return `(1280, 720)`.
- If the preset value is unknown, log a warning and return `(1280, 720)`.
- Use `load_preset()` from `visualizer.views.window` for the actual lookup.

### 2.2 Font loading

```python
def _load_fonts() -> tuple[pygame.font.Font, pygame.font.Font, pygame.font.Font]:
    """Load (title_font, body_font, number_font) with SysFont fallback per doc 04 §3.3."""
```

- Font asset directory: `Path(__file__).resolve().parents[2] / "assets" / "fonts"`.
- Try bundled files first: `Inter-Bold.ttf` size 24, `Inter-Regular.ttf` size 16, `FiraCode-Regular.ttf` size 28.
- Fallback: `pygame.font.SysFont("segoeui, arial", size)` for title/body, `pygame.font.SysFont("consolas, courier", 28)` for number.
- Never crash on missing fonts.

### 2.3 Algorithm + Orchestrator setup

```python
INITIAL_ARRAY: list[int] = [4, 7, 2, 6, 1, 5, 3]
```

- Import all four algorithm classes: `BubbleSort`, `SelectionSort`, `InsertionSort`, `HeapSort`.
- Instantiate each with `INITIAL_ARRAY`.
- Pass the four instances + `INITIAL_ARRAY` to `Orchestrator(algorithms, initial_array)`.

### 2.4 Render helpers

Create a helper that maps `PanelContext` state to rendering data for each frame:

- **Panel state mapping:** `PanelState.COMPLETED` → `panel.PanelState.COMPLETED`, `PanelState.FAILED` → `panel.PanelState.FAILED`, else → `panel.PanelState.RUNNING`.
- **Metrics string:** `f"{ctx.complexity} | {elapsed_str} | Steps: {ctx.step_count} | Cmp: {ctx.comparisons} | Wr: {ctx.writes}"` where `elapsed_str` is `ctx.elapsed_time_ms` formatted as `"SS.DDs"` (e.g., `8200` → `"08.20s"`).
- **Message string:** `ctx.current_tick.message if ctx.current_tick else ""`.

### 2.5 Main event loop

```python
def main() -> None:
```

Sequence:
1. `pygame.init()`
2. `width, height = _load_config()`
3. `surface, layout = init_display(width, height)`
4. Load fonts.
5. Build 4 `PanelRenderer` instances, one per `layout.panel_rects[i]`.
6. Instantiate algorithms + Orchestrator.
7. `clock = pygame.time.Clock()`
8. Enter `while True:` loop:
   a. Event handling:
      - `pygame.QUIT` → break
      - `pygame.KEYDOWN`:
        - `K_SPACE` → toggle play/pause (`orchestrator.is_running` check → `pause()` or `play()`)
        - `K_RIGHT` → `orchestrator.step()`
        - `K_r` → `orchestrator.restart()`
        - `K_ESCAPE` → break
   b. `raw_dt = clock.tick(60)` 
   c. `dt = min(raw_dt, 33)`
   d. `orchestrator.update(dt)`
   e. `surface.fill((30, 30, 35))` — dark background behind panels
   f. For each panel `i` in `0..3`:
      - Map `orchestrator.panels[i]` to `PanelState` for the renderer.
      - Call `panel_renderers[i].draw_background(surface, state)`.
      - Build the metrics string and message string from `PanelContext`.
      - Call `panel_renderers[i].draw_header(surface, algorithm_name, metrics, message, state)`.
   g. `pygame.display.flip()`
9. `pygame.quit()`

### 2.6 Entry guard

```python
if __name__ == "__main__":
    main()
```

### 2.7 Delete legacy stub

The file `/main.py` at the repo root is a legacy placeholder (`print("Hello from visual-learning-sorting!")`). Delete it — the entry point is now `src/visualizer/main.py` via `pyproject.toml`'s `[project.scripts]`.

## STEP 3 — VERIFICATION

Run all four gates:

```bash
# Gate 1: App launches without crash under dummy driver
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy uv run python -c "
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import pygame
pygame.init()
from visualizer.main import main
# Can't run the full loop headlessly (no quit event), but import + setup should succeed
print('Import OK')
pygame.quit()
"

# Gate 2: Pyright
PYRIGHT_PYTHON_GLOBAL_NODE=false uv run pyright src/visualizer/main.py

# Gate 3: Ruff
uv run ruff check src/visualizer/main.py && uv run ruff format --check src/visualizer/main.py

# Gate 4: Existing tests — no regressions
uv run pytest tests/ -q
```

All four must pass. Fix any issues before proceeding.

## STEP 4 — DEVLOG POST-ACTION

Append a post-action entry to `DEVLOG.md` immediately after the pre-action entry:

```markdown
## 2026-05-04 — Phase 7 closed: Main event loop (post-action)

### Worked on

[Describe what was actually created — file structure, key design choices, any deviations from the plan.]

### Corrections

[List any ruff/pyright corrections, or "Zero corrections" if clean on first run.]

### Results

- App launch (dummy driver): [PASS/FAIL]
- `uv run pyright src/visualizer/main.py`: **[N] errors, [N] warnings**
- `uv run ruff check` + `uv run ruff format --check`: **[clean/N issues]**
- `uv run pytest tests/ -q`: **339/339 PASSED** (no regressions)

### Next

[What comes next — likely Phase 7b: sprite animation rendering, or on-screen control buttons.]
```

## Context files to read

Read these files before writing any code:

1. `CLAUDE.md` — Critical Rules (especially #6 timing, #7 dt clamp), architecture, counter table
2. `docs/design_docs/06_BEHAVIOR_SPEC.md` — Keyboard bindings, startup behavior, control semantics
3. `docs/design_docs/04_UI_SPEC.md` §2 (grid layout) + §3 (typography/fonts) + §4 (header rhythm)
4. `docs/design_docs/02_ARCHITECTURE.md` — MVC boundaries, runtime model (render track + logical track)
5. `docs/design_docs/09_DEV_ENV.md` §5 (run commands) + §8 (config.toml)
6. `src/visualizer/views/window.py` — `load_preset()`, `init_display()`, `GridLayout`
7. `src/visualizer/views/panel.py` — `PanelRenderer`, `PanelState`, `draw_background()`, `draw_header()`
8. `src/visualizer/controllers/orchestrator.py` — `Orchestrator`, `PanelContext`, `PanelState` (controller enum)
9. `src/visualizer/models/contracts.py` — `BaseSortAlgorithm`
10. `pyproject.toml` — entry point `visual-sort = "visualizer.main:main"`
11. `config.toml` — current preset value

---
