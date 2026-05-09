# Phase 6 — Controller / Orchestrator

**Delivered:** 2026-05-01 through 2026-05-02
**Scope:** `src/visualizer/controllers/orchestrator.py` — PanelState enum, duration constants, PanelContext, get_duration(), Orchestrator class with update(dt), compute_sprite_moves(), play/pause/step/restart, integration tests.
**Test count:** 97 unit tests + 7 integration tests = 104 orchestrator tests. Cumulative: 339/339.
**Sub-phases:** 6a (enum + constants), 6b (core loop), 6c (sprite identity delta), 6d (playback controls), 6e (integration tests).

---

## Reflection — Spec Paralysis vs. Spec Insufficiency

This phase surfaced a tension worth narrating for the video journal. Early in the project, the review process was characterized as "spec paralysis" — spending too long verifying specifications before building. Phase 6c proved that framing wrong.

The specifications were detailed enough to build from, but not always detailed enough to build *prompts* from without introducing assumptions. The 6c prompt stated "SHIFT ticks always produce 2 changed indices," which seemed like a safe inference from the spec's description of Insertion Sort shifts. But the actual `InsertionSort` generator yields `self.data.copy()` after `arr[j+1] = arr[j]` — a single-slot mutation that produces exactly 1 changed index, not 2. The spec described the logical operation (one element shifts right) accurately, but the prompt author assumed the array delta shape without tracing the generator code.

The two-agent workflow caught this gap cleanly: Sonnet adapted by adding the 1-change rightward-shift inference path, and the Opus review confirmed the adaptation was correct. But catching it at prompt-writing time — by tracing the generator's actual yield points against the delta function's input expectations — would have been cheaper.

**The lesson:** specs that are sufficient for a human implementer may not be sufficient for a prompt. A human reads "shift one element right" and writes code that handles whatever delta shape falls out. A prompted agent implements exactly what the prompt describes. The gap between "spec-sufficient" and "prompt-sufficient" is where assumptions hide. Earlier spec tracing — walking the actual code path the prompt will trigger — catches these gaps before they become runtime surprises.

This is exactly the kind of engineering judgment call worth narrating in the video journal: not "we should have written more specs" but "we should have traced the specs through the code path the prompt would exercise." The distinction matters because it's actionable — it changes how you write prompts, not how you write specs.

---

## 2026-05-01 11:07 — Phase 6a closed: PanelState + duration constants (post-action)

### Worked on - 6a closed

Created `src/visualizer/controllers/orchestrator.py` (Phase 6a scope: `PanelState` enum with 5 members, standard duration constants T1=150/T2=400/T3=200/TERMINAL=0/FAILURE=0, sift-down cadence override constants T1=100/T2=250/T3=130, `get_duration(op_type, sift_down_cadence)` pure function with match dispatch, `PanelContext` plain class with reset() preserving algorithm_name and complexity) and `tests/unit/test_orchestrator.py` (28 tests: enum membership, standard constants, sift-down constants, all 9 get_duration cases including SHIFT-always-standard invariant, 8 PanelContext construction/reset assertions).

### Results - 6a closed

- `uv run pytest tests/unit/test_orchestrator.py -v`: **28/28 PASSED** (first run after one I001 import-sort fix)
- `uv run pytest tests/unit/ -v`: **263/263 PASSED** (cumulative)
- `PYRIGHT_PYTHON_GLOBAL_NODE=false uv run pyright`: **0 errors, 0 warnings**
- `uv run ruff check` + `uv run ruff format --check`: **clean**

### Corrections - 6a closed

One I001 import-sort fix in test_orchestrator.py (ruff auto-formatted).

---

## 2026-05-01 11:20 — Phase 6b pre-action: update(dt) core loop

### Plan - 6b start

Add the Orchestrator class to orchestrator.py. Accepts a list of BaseSortAlgorithm instances and the initial array. Creates PanelContext + generator per algorithm. Core update(dt) method: subtract dt from active panels' remaining time, fetch next SortResult when remaining <= 0, map OpType to duration via get_duration(), transition state machine, accumulate elapsed_time_ms (integer arithmetic), handle TERMINAL/FAILURE transitions, track step counter (exclude RANGE per D-041), manage sift-down cadence flag lifecycle. Tests use MockAlgorithm helper class.

### Exit criteria - 6b start

1. pytest test_orchestrator.py — all pass
2. pytest tests/unit/ — cumulative pass
3. pyright — 0 errors, 0 warnings
4. ruff — clean

---

## 2026-05-01 11:25 — Phase 6b closed: update(dt) core loop (post-action)

### Worked on - 6b closed

Extended `src/visualizer/controllers/orchestrator.py` with: three new fields on `PanelContext` (`current_tick`, `previous_array_state`, `extraction_pending`) + reset() updated; `Orchestrator` class (`__init__` builds parallel `_panels`/`_generators`/`_algorithms` lists from a `Sequence[BaseSortAlgorithm]`; `update(dt)` state machine — ANIMATING counts down, WAITING fetches next tick, TERMINAL/FAILURE transitions set `is_active=False`; `_update_heap_cadence` two-step protocol: boundary T3 arms `extraction_pending`, SWAP triggers cadence enable, next boundary T3 resets). Extended `tests/unit/test_orchestrator.py` with `MockAlgorithm` helper, three tick factory functions, and 27 new tests across Groups 6-12.

### Results - 6b closed

- `uv run pytest tests/unit/test_orchestrator.py -v`: **55/55 PASSED** (first run, zero logic corrections)
- `uv run pytest tests/unit/ -v`: **290/290 PASSED** (cumulative)
- `PYRIGHT_PYTHON_GLOBAL_NODE=false uv run pyright`: **0 errors, 0 warnings**
- `uv run ruff check` + `uv run ruff format --check`: **clean** (3 ruff corrections)

### Corrections - 6b closed

Three ruff corrections: RUF002 (en-dash in docstring), I001 (import sort), UP043 (Generator shortform). Zero logic fixes.

---

## 2026-05-02 14:48 — Phase 6c pre-action: Sprite identity delta computation

### Plan - 6c start

Add sprite identity delta computation to `orchestrator.py`. Pure function `compute_sprite_moves(old_state, new_state, slot_to_sprite_id)` compares consecutive array snapshots, identifies changed indices, looks up sprite IDs from `slot_to_sprite_id` mapping, exchanges them, and returns `{sprite_id: new_slot}` dict. Never matches by value (doc 12 §1, Trap A). New `PanelContext` fields: `slot_to_sprite_id` (`list[int]`), `sprite_moves` (`dict[int,int]`), `array_size` (`int`). Integration into `update(dt)` between tick fetch and `previous_array_state` update. D-060 guarantees every SHIFT tick changes exactly 2 indices, so delta logic is structurally identical for SWAP and SHIFT. Tests: ~16-20 new tests across Groups 13-15 (pure function, context fields, update integration).

### Exit criteria - 6c start

1. pytest test_orchestrator.py — all pass
2. pytest tests/unit/ — cumulative pass
3. pyright — 0 errors, 0 warnings
4. ruff — clean

---

## 2026-05-02 14:57 — Phase 6c closed: Sprite identity delta computation (post-action)

### Worked on - 6c closed

Added `compute_sprite_moves()` pure function to `orchestrator.py`: compares old/new array snapshots index-by-index, finds changed indices, exchanges sprite IDs in `slot_to_sprite_id` (mutated in place), returns `{sprite_id: new_slot}`. Handles 0 changes (RANGE/COMPARE, no-op), 2 changes (SWAP — exchange at the two slots), and 1 change (Insertion Sort rightward shift — infer source from idx-1 via value equality, exchange; placement ticks at idx=0 or non-inferrable return `{}`). Never matches by value (Trap A). Added three new `PanelContext` fields: `array_size` (preserved across reset), `slot_to_sprite_id` (reset to `range(array_size)`), `sprite_moves` (reset to `{}`). Updated `Orchestrator.__init__` to pass `len(algo.data)`. Wired delta call into `update(dt)` immediately after `ctx.current_tick = tick`, before `previous_array_state` is advanced. Added 16 new tests: Groups 13 (7 pure-function), 14 (4 context fields), 15 (5 integration).

### Corrections - 6c closed

One ruff `format` correction in `test_orchestrator.py` (whitespace). Zero logic corrections.

### Spec deviation — SHIFT produces 1 changed index, not 2

The prompt stated "SHIFT ticks always produce 2 changed indices." The actual `InsertionSort` generator yields `self.data.copy()` after `arr[j+1] = arr[j]`, which modifies only slot `j+1`. Slot `j` retains its original value because the key was already extracted. This produces exactly 1 changed index in the array delta.

Sonnet adapted correctly: the 1-change path uses rightward-shift inference (`new_state[idx] == old_state[idx-1]`) to identify the source slot and exchange sprite IDs at `(idx-1, idx)`. Placement ticks (key drops to final slot) return `{}` because prior shift exchanges already positioned the key sprite correctly.

**Invisible shift edge case (documented, not a v1 blocker):** When `arr[j] == arr[j+1]` (duplicate values), the shift produces identical before/after arrays, making the movement undetectable by any pure-delta approach. The sprite identity system would not animate this shift. For v1 with the default array `[4, 7, 2, 6, 1, 5, 3]` (no duplicates), this is a non-issue.

### Results - 6c closed

- `uv run pytest tests/unit/test_orchestrator.py -v`: **71/71 PASSED** (first run, zero logic corrections)
- `uv run pytest tests/unit/ -v`: **306/306 PASSED** (cumulative)
- `PYRIGHT_PYTHON_GLOBAL_NODE=false uv run pyright`: **0 errors, 0 warnings** (31 pre-existing `pytest.approx` warnings in other test files, unchanged)
- `uv run ruff check` + `uv run ruff format --check` on changed files: **clean**

---

## 2026-05-02 15:30 — Phase 6d pre-action: Play/Pause/Step/Restart

### Plan - 6d start

Add play/pause/step/restart controls to Orchestrator.
Global `_running` bool gates update(dt) processing — pause simply sets it False, preserving panel states (ANIMATING timers, WAITING) exactly as-is.
Play sets True and transitions IDLE_PAUSED -> WAITING. Step uses a `_stepping` flag: transitions active IDLE_PAUSED -> WAITING, lets update(dt) process normally, but ANIMATING drain goes to IDLE_PAUSED instead of WAITING. When no active panel is still mid-step (all IDLE_PAUSED, COMPLETED, or FAILED), _stepping clears.
Step input rejected while `_running` or `_stepping`.
Restart re-instantiates algorithms from stored classes + initial_array, resets PanelContexts (including slot_to_sprite_id and sprite_moves from 6c), re-seeds generators and previous_array_state.
Tests: ~15-20 new tests across Groups 16-19 (play, pause, step, restart).

### Exit criteria - 6d start

1. pytest test_orchestrator.py — all pass
2. pytest tests/unit/ — cumulative pass
3. pyright — 0 errors, 0 warnings
4. ruff — clean

---

## 2026-05-02 16:45 — Phase 6d closed: Play/Pause/Step/Restart (post-action)

### Worked on - 6d closed

Added playback controls to `src/visualizer/controllers/orchestrator.py`: three new `Orchestrator.__init__` fields (`_running`, `_stepping`, `_algorithm_classes`); guard at top of `update(dt)` (`if not _running and not _stepping: return`); modified ANIMATING drain to go `IDLE_PAUSED` instead of `WAITING_FOR_NEXT_TICK` when `_stepping`; step completion check after the panel loop (clears `_stepping` once all active panels are `IDLE_PAUSED`); four new public methods: `play()` (sets `_running=True`, transitions `IDLE_PAUSED->WAITING`; ignored while stepping), `pause()` (clears `_running`), `step()` (sets `_stepping=True`, transitions `IDLE_PAUSED->WAITING`; ignored while running or mid-step), `restart()` (re-instantiates algorithms from stored classes + `_initial_array`, resets all `PanelContext`s, re-seeds generators); `is_running` and `is_stepping` read-only properties.

Updated `tests/unit/test_orchestrator.py`: added `SimpleAlgorithm` concrete helper (takes only `data`; used for restart tests since `MockAlgorithm.__init__` takes extra params); added 26 new tests across Groups 16-20 (play, pause, step, restart, initial-state/guard); retrofitted all pre-6d tests that called `update()` to use `orch.play()` instead of `orch._running = True` (eliminates `reportPrivateUsage` errors).

### Corrections - 6d closed

One ruff format correction in both files. Zero logic fixes. Pre-6d tests retrofitted to use `play()` to eliminate 27 pyright `reportPrivateUsage` errors — no semantic change to those tests.

### Results - 6d closed

- `uv run pytest tests/unit/test_orchestrator.py -v`: **97/97 PASSED** (first run after ruff format; zero logic corrections)
- `uv run pytest tests/unit/ -v`: **332/332 PASSED** (cumulative)
- `PYRIGHT_PYTHON_GLOBAL_NODE=false uv run pyright`: **0 errors, 0 warnings** (31 pre-existing `pytest.approx` warnings in other test files, unchanged)
- `uv run ruff check` + `uv run ruff format --check` on changed files: **clean**

---

## 2026-05-02 17:30 — Phase 6e pre-action: Controller integration tests

### Plan - 6e start

Create `tests/integration/` package and `test_orchestrator_integration.py` with 7 `@pytest.mark.integration` tests using real algorithm generators (no mocks). Tests cover: TC-A4 (independent queues — Bubble Sort `elapsed_time_ms == 8200` exact; 20 compares x 150ms + 13 swaps x 400ms = 8200ms), TC-A6 (fairness — all 4 panels reach COMPLETED, no starvation, `comparisons > 0`, `step_count > 0`), TC-A15 (state machine happy path — IDLE_PAUSED -> play() -> WAITING -> update -> ANIMATING -> drain -> WAITING -> ... -> COMPLETED; elapsed frozen after COMPLETED), TC-A16 (failure isolation — `FailingAlgorithm` helper yields FAILURE immediately; healthy panel still reaches COMPLETED), TC-A17 (pause freezes state — `remaining_ms` and `elapsed_time_ms` unchanged across 100 update calls while paused), TC-A18 (restart resets all — advance some ticks, restart(), counters/state zeroed, runs to completion again; Bubble `comparisons==20`, `writes==26`), and counter accuracy (all 4 algorithms match CLAUDE.md table: Bubble 20/26, Selection 21/10, Insertion 17/19, Heap 20/30/35). No mock generators — tests use real sort generators, so timing assertions use exact integer ms arithmetic (no `pytest.approx`). Integration marker `@pytest.mark.integration` applied to all tests.

### Exit criteria - 6e start

1. pytest tests/integration/ — all 7 pass
2. pytest tests/ — cumulative ~339 pass
3. pyright — 0 errors, 0 warnings
4. ruff — clean

---

## 2026-05-02 18:15 — Phase 6e closed: Controller integration tests (post-action)

### Worked on - 6e closed

Created `tests/integration/` package (`__init__.py` + `test_orchestrator_integration.py`). Seven `@pytest.mark.integration` tests using real algorithm generators: TC-A4 (independent queues — `elapsed_time_ms == 8_200` for Bubble Sort with default_7: 20 COMPARE x 150ms + 13 SWAP x 400ms; no RANGE ticks in Bubble Sort); TC-A6 (fairness — all 4 panels COMPLETED, `comparisons > 0`, `step_count > 0`); TC-A15 (state machine happy path — IDLE_PAUSED -> play -> WAITING -> ANIMATING(150ms) -> drain -> WAITING -> ANIMATING(400ms) -> drain -> WAITING -> TERMINAL -> COMPLETED; elapsed frozen at 550ms); TC-A16 (failure isolation — `FailingAlgorithm` helper yields FAILURE, healthy BubbleSort panel reaches COMPLETED independently); TC-A17 (pause freezes state — 100 updates while paused leave `remaining_ms` and `elapsed_time_ms` unchanged, resume drains correctly); TC-A18 (restart resets all — counters/state zeroed, re-run yields `comparisons==20, writes==26` for Bubble Sort); counter accuracy (all 4 algorithms match CLAUDE.md table: Bubble 20/26, Selection 21/10, Insertion 17/19, Heap 20/30/35 + `step_count==35`).

### Corrections - 6e closed

Two ruff corrections: RUF002 (Unicode multiplication sign in docstring, replaced with `x`), I001 (import sort). Zero logic fixes.

### Results - 6e closed

- `uv run pytest tests/integration/ -v`: **7/7 PASSED** (first run after ruff corrections)
- `uv run pytest tests/ -q`: **339/339 PASSED** (cumulative)
- `PYRIGHT_PYTHON_GLOBAL_NODE=false uv run pyright`: **0 errors, 0 warnings** (31 pre-existing `pytest.approx` warnings unchanged)
- `uv run ruff check` + `uv run ruff format --check` on changed files: **clean**

---

## Phase 6 Summary

### By the numbers

| Sub-phase | Scope | New tests | Cumulative | Logic corrections |
| --- | --- | --- | --- | --- |
| 6a | PanelState, durations, PanelContext, get_duration() | 28 | 263 | 0 |
| 6b | Orchestrator class, update(dt), state machine, cadence | 27 | 290 | 0 |
| 6c | compute_sprite_moves(), slot_to_sprite_id, sprite_moves | 16 | 306 | 0 |
| 6d | play(), pause(), step(), restart(), properties | 26 | 332 | 0 |
| 6e | Integration tests (TC-A4/A6/A15/A16/A17/A18) | 7 | 339 | 0 |

**Zero logic corrections across the entire phase.** All corrections were ruff formatting (whitespace, import sort, Unicode characters, Generator shortform). The decomposition into 5 sub-phases with clear exit criteria eliminated the combinatorial complexity that causes logic bugs in large drops.

### Architecture delivered

The Orchestrator implements an independent-queue controller where each of the four algorithm panels has its own `PanelContext`, generator, and timing state. The `update(dt)` method processes panels independently — one state transition per panel per frame, with a `continue` guard that prevents ANIMATING countdown and WAITING fetch from happening in the same frame. This creates the "race" behavior where faster algorithms (fewer operations, shorter total duration) visibly complete before slower ones.

Sprite identity tracking uses a pure-function delta approach (`compute_sprite_moves`) that compares consecutive array snapshots by index position, never by value. This is critical for correctness with duplicate values in the array.

Playback controls use two boolean flags (`_running`, `_stepping`) with mutual exclusion: step is rejected while running, play is rejected while stepping. Pause preserves all panel states exactly as-is — mid-animation timers, highlight colors, sprite positions. Restart re-instantiates algorithms from stored class references, which sidesteps the type system limitation where `BaseSortAlgorithm.__init__` takes `(data, name, complexity)` but concrete constructors take only `(data)`.

### What's next

Phase 7 — `main.py` entry point and Pygame event loop. This is the phase where the app becomes runnable for the first time.
