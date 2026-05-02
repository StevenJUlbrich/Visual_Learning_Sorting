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

---

## 2026-05-01 11:25 — Phase 6b closed: update(dt) core loop (post-action)

### Worked on

Extended `src/visualizer/controllers/orchestrator.py` with: three new fields on `PanelContext` (`current_tick`, `previous_array_state`, `extraction_pending`) + reset() updated; `Orchestrator` class (`__init__` builds parallel `_panels`/`_generators`/`_algorithms` lists from a `Sequence[BaseSortAlgorithm]`; `update(dt)` state machine — ANIMATING counts down, WAITING fetches next tick, TERMINAL/FAILURE transitions set `is_active=False`; `_update_heap_cadence` two-step protocol: boundary T3 arms `extraction_pending`, SWAP triggers cadence enable, next boundary T3 resets). Extended `tests/unit/test_orchestrator.py` with `MockAlgorithm` helper, three tick factory functions, and 27 new tests across Groups 6-12.

### Results

- `uv run pytest tests/unit/test_orchestrator.py -v`: **55/55 PASSED** (first run, zero logic corrections)
- `uv run pytest tests/unit/ -v`: **290/290 PASSED** (cumulative)
- `PYRIGHT_PYTHON_GLOBAL_NODE=false uv run pyright`: **0 errors, 0 warnings**
- `uv run ruff check` + `uv run ruff format --check`: **clean** (3 ruff corrections)

### Corrections

Three ruff corrections: RUF002 (en-dash in docstring), I001 (import sort), UP043 (Generator shortform). Zero logic fixes.

### Next

Phase 6c: Sprite identity delta computation.

---

## 2026-05-02 14:57 — Phase 6c closed: Sprite identity delta computation (post-action)

### Worked on

Added `compute_sprite_moves()` pure function to `orchestrator.py`: compares old/new array snapshots index-by-index, finds changed indices, exchanges sprite IDs in `slot_to_sprite_id` (mutated in place), returns `{sprite_id: new_slot}`. Handles 0 changes (RANGE/COMPARE, no-op), 2 changes (SWAP — exchange at the two slots), and 1 change (Insertion Sort rightward shift — infer source from idx-1 via value equality, exchange; placement ticks at idx=0 or non-inferrable return `{}`). Never matches by value (Trap A). Added three new `PanelContext` fields: `array_size` (preserved across reset), `slot_to_sprite_id` (reset to `range(array_size)`), `sprite_moves` (reset to `{}`). Updated `Orchestrator.__init__` to pass `len(algo.data)`. Wired delta call into `update(dt)` immediately after `ctx.current_tick = tick`, before `previous_array_state` is advanced. Added 16 new tests: Groups 13 (7 pure-function), 14 (4 context fields), 15 (5 integration).

### Corrections

One ruff `format` correction in `test_orchestrator.py` (whitespace). Zero logic corrections.

### Note on spec deviation

The spec plan stated "SHIFT tick always changes exactly 2 adjacent indices." Actual `InsertionSort` generator yields `list(arr)` *after* `arr[j+1] = arr[j]`, producing exactly 1 changed index (only `j+1` mutates; `j` retains its old value). The 1-change path uses a rightward-shift inference (`new_state[idx] == old_state[idx-1]`) to correctly exchange sprite IDs at `(idx-1, idx)`. Placement ticks (key drop to final slot) return `{}` because the key sprite was already tracked at the target slot via prior shift exchanges.

### Results

- `uv run pytest tests/unit/test_orchestrator.py -v`: **71/71 PASSED** (first run, zero logic corrections)
- `uv run pytest tests/unit/ -v`: **306/306 PASSED** (cumulative)
- `PYRIGHT_PYTHON_GLOBAL_NODE=false uv run pyright`: **0 errors, 0 warnings** (31 pre-existing `pytest.approx` warnings in other test files, unchanged)
- `uv run ruff check` + `uv run ruff format --check` on changed files: **clean**

### Next

Phase 6d — Play/Pause/Step/Restart.

---

## 2026-05-02 16:45 — Phase 6d closed: Play/Pause/Step/Restart (post-action)

### Worked on

Added playback controls to `src/visualizer/controllers/orchestrator.py`: three new `Orchestrator.__init__` fields (`_running`, `_stepping`, `_algorithm_classes`); guard at top of `update(dt)` (`if not _running and not _stepping: return`); modified ANIMATING drain to go `IDLE_PAUSED` instead of `WAITING_FOR_NEXT_TICK` when `_stepping`; step completion check after the panel loop (clears `_stepping` once all active panels are `IDLE_PAUSED`); four new public methods: `play()` (sets `_running=True`, transitions `IDLE_PAUSED→WAITING`; ignored while stepping), `pause()` (clears `_running`), `step()` (sets `_stepping=True`, transitions `IDLE_PAUSED→WAITING`; ignored while running or mid-step), `restart()` (re-instantiates algorithms from stored classes + `_initial_array`, resets all `PanelContext`s, re-seeds generators); `is_running` and `is_stepping` read-only properties.

Updated `tests/unit/test_orchestrator.py`: added `SimpleAlgorithm` concrete helper (takes only `data`; used for restart tests since `MockAlgorithm.__init__` takes extra params); added 26 new tests across Groups 16-20 (play, pause, step, restart, initial-state/guard); retrofitted all pre-6d tests that called `update()` to use `orch.play()` instead of `orch._running = True` (eliminates `reportPrivateUsage` errors).

### Corrections

One ruff format correction in both files. Zero logic fixes. Pre-6d tests retrofitted to use `play()` to eliminate 27 pyright `reportPrivateUsage` errors — no semantic change to those tests.

### Results

- `uv run pytest tests/unit/test_orchestrator.py -v`: **97/97 PASSED** (first run after ruff format; zero logic corrections)
- `uv run pytest tests/unit/ -v`: **332/332 PASSED** (cumulative)
- `PYRIGHT_PYTHON_GLOBAL_NODE=false uv run pyright`: **0 errors, 0 warnings** (31 pre-existing `pytest.approx` warnings in other test files, unchanged)
- `uv run ruff check` + `uv run ruff format --check` on changed files: **clean**

### Next

Phase 6e — Integration tests (TC-A4, A6, A15, A16, A17, A18).

---

## 2026-05-02 15:30 — Phase 6d pre-action: Play/Pause/Step/Restart

### Plan

Add play/pause/step/restart controls to Orchestrator. Global `_running` bool gates update(dt) processing — pause simply sets it False, preserving panel states (ANIMATING timers, WAITING) exactly as-is. Play sets True and transitions IDLE_PAUSED → WAITING. Step uses a `_stepping` flag: transitions active IDLE_PAUSED → WAITING, lets update(dt) process normally, but ANIMATING drain goes to IDLE_PAUSED instead of WAITING. When no active panel is still mid-step (all IDLE_PAUSED, COMPLETED, or FAILED), _stepping clears. Step input rejected while _running or _stepping. Restart re-instantiates algorithms from stored classes + initial_array, resets PanelContexts (including slot_to_sprite_id and sprite_moves from 6c), re-seeds generators and previous_array_state. Tests: ~15-20 new tests across Groups 16-19 (play, pause, step, restart).

### Exit criteria

1. pytest test_orchestrator.py — all pass
2. pytest tests/unit/ — cumulative pass
3. pyright — 0 errors, 0 warnings
4. ruff — clean

---

## 2026-05-02 14:48 — Phase 6c pre-action: Sprite identity delta computation

### Plan

Add sprite identity delta computation to orchestrator.py. Pure function compute_sprite_moves(old_state, new_state, slot_to_sprite_id) compares consecutive array snapshots, identifies changed indices, looks up sprite IDs from slot_to_sprite_id mapping, exchanges them, and returns {sprite_id: new_slot} dict. Never matches by value (doc 12 §1, Trap A). New PanelContext fields: slot_to_sprite_id (list[int]), sprite_moves (dict[int,int]), array_size (int). Integration into update(dt) between tick fetch and previous_array_state update. D-060 guarantees every SHIFT tick changes exactly 2 indices, so delta logic is structurally identical for SWAP and SHIFT. Tests: ~16-20 new tests across Groups 13-15 (pure function, context fields, update integration).

### Exit criteria

1. pytest test_orchestrator.py — all pass
2. pytest tests/unit/ — cumulative pass
3. pyright — 0 errors, 0 warnings
4. ruff — clean

---

## 2026-05-01 11:20 — Phase 6b pre-action: update(dt) core loop

### Plan

Add the Orchestrator class to orchestrator.py. Accepts a list of BaseSortAlgorithm instances and the initial array. Creates PanelContext + generator per algorithm. Core update(dt) method: subtract dt from active panels' remaining time, fetch next SortResult when remaining ≤ 0, map OpType to duration via get_duration(), transition state machine, accumulate elapsed_time_ms (integer arithmetic), handle TERMINAL/FAILURE transitions, track step counter (exclude RANGE per D-041), manage sift-down cadence flag lifecycle. Tests use MockAlgorithm helper class.

### Exit criteria

1. pytest test_orchestrator.py — all pass
2. pytest tests/unit/ — cumulative pass
3. pyright — 0 errors, 0 warnings
4. ruff — clean

---

## 2026-05-01 11:07 — Phase 6a closed: PanelState + duration constants (post-action)

### Worked on

Created `src/visualizer/controllers/orchestrator.py` (Phase 6a scope: `PanelState` enum with 5 members, standard duration constants T1=150/T2=400/T3=200/TERMINAL=0/FAILURE=0, sift-down cadence override constants T1=100/T2=250/T3=130, `get_duration(op_type, sift_down_cadence)` pure function with match dispatch, `PanelContext` plain class with reset() preserving algorithm_name and complexity) and `tests/unit/test_orchestrator.py` (28 tests: enum membership, standard constants, sift-down constants, all 9 get_duration cases including SHIFT-always-standard invariant, 8 PanelContext construction/reset assertions).

### Results

- `uv run pytest tests/unit/test_orchestrator.py -v`: **28/28 PASSED** (first run after one I001 import-sort fix)
- `uv run pytest tests/unit/ -v`: **263/263 PASSED** (cumulative)
- `PYRIGHT_PYTHON_GLOBAL_NODE=false uv run pyright`: **0 errors, 0 warnings**
- `uv run ruff check` + `uv run ruff format --check`: **clean**

### Corrections

One I001 import-sort fix in test_orchestrator.py (ruff auto-formatted).

### Next

Phase 6b: Core loop — update(dt) + tick dispatch.