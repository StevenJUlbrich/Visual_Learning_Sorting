# 13 IMPLEMENTATION ORDER

**Status:** Locked (closes Phase 0.3).
**Purpose:** Single-page map of the build sequence. Any contributor — human or agent — should read this **before** starting any implementation task, and consult it whenever asking "what depends on what?"

This document does not duplicate work items (that is `TODO/IMPLEMENTATION_TRACKER.md`). It defines the **dependency graph** and **entry/exit criteria** per phase, so an agent can pick up where the prior one left off without accidentally skipping a prerequisite.

---

## Top-Level Dependency Graph

```text
Phase 0  ──▶  Phase 1  ──▶  Phase 2  ──┐
                 │                     ├──▶  Phase 5  ──▶  Phase 6  ──▶  Phase 7  ──▶  Phase 8  ──▶  Phase 9  ──▶  Phase 10
                 ▼                     │
              Phase 3                  │
              Phase 4  ────────────────┘
```

- **Phase 0** (Spec gaps) must close before any code.
- **Phase 1** (Contracts) must close before any algorithm or view code imports `SortResult`.
- **Phase 2** (Algorithm generators) and **Phase 4** (Easing math) can run in parallel — they share no code.
- **Phase 3** (Unit tests for algorithms) depends on Phase 2 but runs in parallel with Phase 4.
- **Phase 5** (View layer) depends on Phase 1 + Phase 4.
- **Phase 6** (Controller) depends on Phase 1, 2, 4, and 5.
- **Phase 7** (Main entry point) depends on Phase 6.
- **Phases 8–10** are integration / CI / manual acceptance, strictly serial at the tail.

---

## Phase-by-Phase Entry & Exit Criteria

### Phase 0 — Pre-Coding Gaps

**Goal:** Close every spec ambiguity identified in the 2026-04-05 agentic readiness review.

**Entry:** Repo cloned, design docs reviewed.

**Exit (all must be true):**

- `pyproject.toml` locks `pygame>=2.5`, `ruff`, `pyright`, `pytest`, and the three pytest markers.
- `config.toml` has `[window] preset = "desktop"` (no `orientation` key).
- `src/visualizer/` exists with empty `__init__.py` files in `models/`, `views/`, `controllers/`, and a `tests/` directory.
- `docs/design_docs/00_PSEUDOCODE.md` exists (this completes 0.1).
- `docs/design_docs/13_IMPLEMENTATION_ORDER.md` exists (this file; completes 0.3).
- `assets/fonts/{Inter-Bold,Inter-Regular,FiraCode-Regular}.ttf` are present, OR `scripts/fetch_fonts.sh` has been run and the SysFont fallback (doc 04 §3.3) has been verified as the interim path.

**Blockers:** None — this is the first phase.

---

### Phase 1 — Data Contracts and Base Classes

**Goal:** Freeze the type surface that every downstream layer imports.

**Depends on:** Phase 0.2 (pyproject.toml so `pyright` can run).

**Output:** `src/visualizer/models/contracts.py` containing `OpType`, `SortResult`, and `BaseSortAlgorithm`.

**Exit:**

- `from visualizer.models.contracts import OpType, SortResult, BaseSortAlgorithm` succeeds.
- `pyright src/visualizer/models/contracts.py` returns 0 errors.
- `ruff check src/visualizer/models/contracts.py` returns clean.
- `SortResult` uses `@dataclass(slots=True)` with the field order from doc 03.

**Testable without Pygame:** Yes.

---

### Phase 2 — Algorithm Generators (Model Layer)

**Goal:** Implement the four generators so their tick sequences match `00_PSEUDOCODE.md` exactly.

**Depends on:** Phase 1.

**Runs in parallel with:** Phase 4 (easing — no shared code).

**Output:**

- `src/visualizer/models/bubble.py`
- `src/visualizer/models/selection.py`
- `src/visualizer/models/insertion.py`
- `src/visualizer/models/heap.py`

**Exit:** For each algorithm, a quick smoke script shows:
- Consuming the generator sorts `default_7` correctly.
- The final tick has `is_complete=True`.
- Empty-input guard yields a single T0 failure tick.
- No exceptions escape the generator (D-020).

Formal verification is Phase 3.

**Testable without Pygame:** Yes.

---

### Phase 3 — Algorithm Unit Tests

**Goal:** Verify counter accuracy, tick sequencing, and edge cases (TC-A6 through TC-A19).

**Depends on:** Phase 2 (all four algorithms implemented).

**Runs in parallel with:** Phase 4 (easing tests — no shared code).

**Output:** `tests/models/test_bubble.py`, `test_selection.py`, `test_insertion.py`, `test_heap.py`.

**Exit:**
- `uv run pytest -m unit -k "bubble or selection or insertion or heap"` is all green.
- Counter table in `CLAUDE.md` is reproduced exactly by collected metrics (20/26, 21/10, 17/19, 20/30/35).
- TC-A14 confirms Insertion Sort terminating-compare logic for `i=1, i=3` (emit) vs. `i=2, i=4` (skip).
- TC-A19 confirms Heap Sort sift-down grammar `T3 → T1{1,2} → T2{0,1}` at every level.

---

### Phase 4 — Easing Module

**Goal:** Pure-math easing primitives usable by the View without Pygame.

**Depends on:** Phase 1 (only for the `pyproject.toml`-enforced toolchain).

**Runs in parallel with:** Phases 2 and 3.

**Output:** `src/visualizer/views/easing.py` (no `import pygame`), plus `tests/views/test_easing.py`.

**Exit:**
- `ease_in_out_quad`, `ease_out_cubic`, `sine_arc` functions implemented per doc 10.
- `grep -l "import pygame" src/visualizer/views/easing.py` returns empty (required by doc 08 §4.4).
- Easing unit tests green.

**Testable without Pygame:** Yes — this is the whole point of isolating this module.

---

### Phase 5 — View Layer

**Goal:** Rendering primitives — panels, sprites, pointers, tree layout, HUD.

**Depends on:** Phase 1 (contracts), Phase 4 (easing). Fonts (Phase 0.2) are strongly recommended but not strictly required thanks to the SysFont fallback.

**Output:**
- `src/visualizer/views/window.py` — display init, 2×2 grid.
- `src/visualizer/views/panel.py` — per-algorithm frame + header.
- `src/visualizer/views/sprite.py` — NumberSprite (circular ring, float coords, easing).
- `src/visualizer/views/tree_layout.py` — Heap Sort binary tree positioning.
- `src/visualizer/views/pointer.py` — Selection Sort i/j/min arrows.
- `src/visualizer/views/limitline.py` — Bubble Sort boundary line.
- `src/visualizer/views/hud.py` — counter overlays + Heap phase label.

**Exit:**
- `pygame.init()` with `SDL_VIDEODRIVER=dummy` succeeds and all modules import.
- A manual "fire one tick, render one frame, exit" smoke runs without error for each algorithm's panel.

---

### Phase 6 — Controller (Orchestrator)

**Goal:** Independent-queue event loop, operation timing, play/pause/step/restart state machine.

**Depends on:** Phases 1, 2, 4, 5.

**Output:** `src/visualizer/controllers/orchestrator.py`.

**Exit:**
- `dt = min(clock.tick(60), 33)` clamp is in place.
- Operation timings are the exact integer ms values (T1=150, T2=400, T3=200, plus Heap rapid-cadence overrides 100/250/130).
- Controller runs against mock generators without any `pygame.display` dependency (per doc 08 §4.4).

---

### Phase 7 — Main Entry & `config.toml` Loading

**Goal:** Wire everything together at the Pygame event loop level.

**Depends on:** Phase 6.

**Output:** `src/visualizer/main.py` exposing `main()` (referenced by `[project.scripts]` in `pyproject.toml`).

**Exit:**
- `uv run visual-sort` launches a window at the configured preset resolution.
- `config.toml` with `preset = "tablet"` switches resolution; with the file absent, the app defaults to desktop (1280×720).
- Quit event cleanly shuts down all four panels.

---

### Phase 8 — Integration Tests

**Goal:** Confirm Controller/View interaction, play/pause/step/restart state machine (TC-A15 through TC-A18).

**Depends on:** Phase 7.

**Output:** `tests/integration/test_controller.py`, `test_pause_resume.py`, `test_restart.py`.

**Exit:** `uv run pytest -m integration` green under `SDL_VIDEODRIVER=dummy`.

---

### Phase 9 — CI Pipeline

**Goal:** GitHub Actions workflow per doc 11.

**Depends on:** Phase 8 green locally.

**Output:** `.github/workflows/ci.yml`.

**Exit:** `SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy uv run pytest -q` runs in CI. Ruff and Pyright gate merges.

---

### Phase 10 — Manual Acceptance

**Goal:** Walk through AT-01 through AT-27 on a real monitor.

**Depends on:** Phase 9 passing.

**Output:** Check-off sheet in `TODO/` or equivalent.

**Exit:** Every AT item recorded as PASS; any FAIL cycles back to the responsible phase.

---

## How an Agent Should Use This Document

1. **Find your task** in `TODO/IMPLEMENTATION_TRACKER.md`.
2. **Identify its phase.**
3. **Verify every prior-phase exit criterion is met** — if not, close the earlier gap first rather than proceeding speculatively.
4. **Consult the phase's "Testable without Pygame" note** — if yes, write tests before or alongside the implementation.
5. **After finishing,** check the relevant boxes in the tracker AND confirm this phase's exit criteria are all satisfied before marking it done.

A failure to honor phase dependencies is the single most common source of agent drift in a project of this size.
