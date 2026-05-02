# 2026-04-23 Project Gap Review

Scope: review the current repository against `DEVLOG.md`, `TODO/IMPLEMENTATION_TRACKER.md`, and the design docs under `docs/design_docs/`.

Assumption: the requested output location "`memplace-exiperment`" refers to the existing folder `docs/AI_Conversations/mempalace-experiment/`.

## Executive Summary

The project is **well-specified and partially implemented**, but it is still in an **early-to-mid build state**, not yet a runnable application. The strongest completed area is the **model layer** plus pure math/view-layout foundations:

- Phase 1 is present: `src/visualizer/models/contracts.py`
- Phase 2 is present: all four algorithm generators exist
- Phase 3 is substantially present: algorithm unit tests exist
- Phase 4 is present: `src/visualizer/views/easing.py`
- Phase 5a is present: `src/visualizer/views/window.py`

The main gap is that the repository does **not yet contain the runtime spine** needed to realize the design goals:

- no `src/visualizer/main.py`
- no `src/visualizer/controllers/orchestrator.py`
- no view modules for sprites/panels/pointers/tree/HUD
- no integration test suite
- no CI workflow
- no acceptance-test execution evidence

In short: the project has a solid specification corpus and correct foundational bricks, but it is **not yet capable of delivering the agentic visualizer experience described by the docs**.

Note on project history: the first four phases are **documented in the archived devlog files** under `docs/devlog/`, not lost. This review treats those archives as the historical record and compares them against the code currently present in the repository.

## Verified Alignment

### Implemented and consistent with the tracker/devlog

1. **Phase 1 contracts are present**
   - `src/visualizer/models/contracts.py` exists and defines `OpType`, `SortResult`, and `BaseSortAlgorithm`.

2. **Phase 2 algorithms are present**
   - `src/visualizer/models/bubble.py`
   - `src/visualizer/models/selection.py`
   - `src/visualizer/models/insertion.py`
   - `src/visualizer/models/heap.py`

3. **Phase 3 unit-test coverage is present for the implemented model/math work**
   - `tests/unit/test_bubble.py`
   - `tests/unit/test_selection.py`
   - `tests/unit/test_insertion.py`
   - `tests/unit/test_heap.py`
   - `tests/unit/test_easing.py`
   - `tests/unit/test_window.py`

4. **Phase 4 easing is present**
   - `src/visualizer/views/easing.py`

5. **Phase 5a window layout work is present and matches the latest devlog/tracker**
   - `DEVLOG.md` records Phase 5a closeout and names `window.py` / `test_window.py`.
   - `TODO/IMPLEMENTATION_TRACKER.md` marks `window.py` complete.
   - `src/visualizer/views/window.py` and `tests/unit/test_window.py` both exist.

6. **Core setup files are aligned with the plan**
   - `pyproject.toml` exists with the declared script entry `visual-sort = "visualizer.main:main"`.
   - `config.toml` exists with `[window] preset = "desktop"`.

7. **The first four phases are preserved in archived devlogs**
   - `docs/devlog/phase_00_01.md`
   - `docs/devlog/phase_02.md`
   - `docs/devlog/phase_03_04.md`
   - The top-level `DEVLOG.md` correctly points to those archives and carries the active Phase 5 work.

## Gaps Found

### P0: Declared application entry point is not implemented

This is the largest concrete mismatch between project wiring and current code.

- `pyproject.toml:15` declares `visual-sort = "visualizer.main:main"`.
- `docs/design_docs/13_IMPLEMENTATION_ORDER.md` says Phase 7 output is `src/visualizer/main.py`.
- That file does **not** exist.
- The only `main.py` in the repo is the root-level stub:
  - `main.py:1` defines `main()`
  - `main.py:2` only prints `"Hello from visual-learning-sorting!"`

Impact:

- the packaged launch path described by the project metadata is currently broken/incomplete
- the app cannot satisfy startup acceptance tests or Phase 7 exit criteria

### P0: Controller/orchestrator layer is entirely absent

The design depends on independent queues, per-panel timers, play/pause/step/restart, and tick-duration orchestration.

Missing:

- `src/visualizer/controllers/orchestrator.py`

Tracker/design references:

- `TODO/IMPLEMENTATION_TRACKER.md` Phase 6 is fully unchecked
- `docs/design_docs/13_IMPLEMENTATION_ORDER.md` names `src/visualizer/controllers/orchestrator.py` as the Phase 6 output
- `docs/design_docs/02_ARCHITECTURE.md` defines this controller as the owner of queue timing and state

Impact:

- no independent algorithm race exists yet
- no runtime state machine exists
- no elapsed-time or step-count runtime behavior can be validated

### P0: View layer is mostly unbuilt

Only `window.py` and `easing.py` exist under `src/visualizer/views/`.

Missing major Phase 5 files:

- `src/visualizer/views/panel.py`
- `src/visualizer/views/sprite.py`
- `src/visualizer/views/tree_layout.py`
- `src/visualizer/views/pointer.py`
- `src/visualizer/views/limitline.py`
- `src/visualizer/views/hud.py`

Impact against the design docs:

- no `NumberSprite` circular ring implementation
- no font-surface caching
- no Selection Sort pointers
- no Bubble Sort `ComparisonPointer` / `LimitLine`
- no Heap Sort tree visualization
- no Heap phase label
- no Bubble HUD counters
- no completion/error state rendering

This means many design-doc “teaching signals” are still specification-only rather than implemented behavior.

### P1: Test plan coverage stops at unit tests for completed bricks

Observed test layout:

- only `tests/unit/` exists
- no `tests/integration/` directory is present

Tracker/test-plan gaps still open:

- TC-A20 tree layout node positioning
- TC-A21 tree layout edge connectivity
- TC-A22 tree layout shrinking
- TC-A23 Selection Sort pointer tracking
- TC-A24 Insertion Sort KEY label lifecycle
- all Phase 8 integration tests (TC-A4, A6, A15, A16, A17, A18)

Impact:

- the repository currently verifies generator correctness well
- it does **not** verify controller fairness, pause/resume, restart, or panel state-machine behavior

### P1: Font assets are still not installed

The tracker intentionally leaves this partially open, and the filesystem confirms it remains open.

Observed:

- `assets/fonts/` contains only `README.md`
- missing:
  - `Inter-Bold.ttf`
  - `Inter-Regular.ttf`
  - `FiraCode-Regular.ttf`

Impact:

- if/when the view layer is built, it must rely on fallback fonts
- header and number metrics may diverge from the locked UI spec until the TTF assets are added

### P1: No CI workflow exists yet

Missing:

- `.github/workflows/ci.yml`

Impact:

- no automated repository gate for ruff/pyright/pytest
- no enforcement of headless Pygame setup in CI

### P2: Manual acceptance phase has not started

The tracker leaves all manual acceptance items unchecked:

- AT-01 through AT-27 remain open

This is expected given the missing runtime/view/controller layers, but it is still a project gap relative to the stated goal.

## Important “Claim vs Current Reality” Notes

1. **The devlog/tracker are internally consistent**
   - I did not find evidence that they falsely claim completed work beyond what is on disk for Phases 1-5a.

2. **The project is not yet runnable as a visualizer**
   - The docs describe a fairly rich Pygame application.
   - The current repo implements the algorithms and some layout math, but not the executable UI/controller system.

3. **The packaging story is ahead of the code**
   - `pyproject.toml` already advertises a console script.
   - The corresponding packaged module entry point does not yet exist.

4. **The repository is strong on specification, weaker on integration**
   - This is good for agentic implementation readiness.
   - It also means the remaining risk is now concentrated in runtime glue: animation state, controller timing, sprite identity, and panel rendering.

## Verification Limits

I was able to inspect the repository contents directly, but environment-local `uv` verification was blocked by host-specific permissions/cache issues:

- `uv` cache path creation failed under the user profile
- `uv` Python discovery also hit access issues under the user roaming profile

Because of that, this review is based on:

- source inspection
- file-presence verification
- direct comparison to the tracker/devlog/design docs

It is **not** a fresh green/red execution verdict for pytest, pyright, or ruff on this machine.

## Recommended Next Sequence

1. Implement Phase 5b next: `src/visualizer/views/sprite.py`
2. Finish the rest of Phase 5 view primitives: `panel.py`, `tree_layout.py`, `pointer.py`, `limitline.py`, `hud.py`
3. Implement Phase 6 `controllers/orchestrator.py`
4. Replace the root stub workflow with a real packaged app entry at `src/visualizer/main.py`
5. Add Phase 8 integration tests before attempting manual acceptance
6. Add CI once the runtime path is stable

## Bottom Line

The project is **not blocked by missing design clarity**. It is blocked by **missing runtime implementation**.

The biggest actionable gaps are:

- missing packaged app entry module
- missing controller/orchestrator
- missing most of the view layer
- missing integration/CI coverage

Those are the gaps preventing the repository from becoming the “agentic developer and agent” visual teaching app described by the specs.
