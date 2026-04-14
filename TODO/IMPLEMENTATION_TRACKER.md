# Implementation Tracker

Status key: `[ ]` not started | `[~]` in progress | `[x]` done | `[!]` blocked

---

## Phase 0 — Pre-Coding Gaps (Spec Completions)

These items were identified during agentic readiness review (2026-04-05). They fill gaps in the existing design docs that would cause agent drift or implementation ambiguity.

### 0.1 Algorithm Pseudocode

> **Risk:** An agent can write a valid sort that produces a different tick sequence than the tests expect. The expected counter values (doc 03) and tick sequence contracts (TC-A9, TC-A19) imply a specific implementation, but it's not written down.

- [ ] **Bubble Sort pseudocode** — Document the exact early-exit condition. The spec says "8 swaps with early exit" for `[4, 7, 2, 6, 1, 5, 3]` (doc 03 writes table). Show the outer/inner loop structure and the `swapped` flag.
- [ ] **Insertion Sort pseudocode** — Document the while-loop structure including when the terminating T1 compare fires (loop exits by `arr[j] > key` failing vs `j < 0`). Must match TC-A9 and TC-A14 expectations (passes i=1, i=3 emit terminating comparisons; passes i=2, i=4 do not).
- [ ] **Selection Sort pseudocode** — Document the scan loop and min_idx update logic. Must match comparisons=21, writes=10.
- [ ] **Heap Sort pseudocode** — Document sift-down direction (top-down), child comparison order (left then right), Phase 1 node processing order (floor(n/2)-1 down to 0), and Phase 2 extraction loop. Must match TC-A19 sift-down tick contract (T3 -> T1{1,2} -> T2{0,1} per level).

### 0.2 Missing Project Files

- [x] **Path reconciliation (D-080)** — Resolved `src/visualizer/` vs `visual_sort/src/` conflict in favor of `src/visualizer/` (matches all 4,000 lines of specs and CLAUDE.md). Empty scaffold at `visual_sort/` removed; new package skeleton created with `__init__.py` in `models/`, `views/`, `controllers/`, plus `tests/`.
- [x] **`pyproject.toml`** — Lock dependencies: `pygame >=2.5`, dev deps `ruff`, `pyright`, `pytest`. Include `[tool.pytest.ini_options]` markers from doc 08 Section 4.3. Include `[tool.ruff]` and `[tool.pyright]` sections. *(closed 2026-04-14; hatchling src-layout per D-080, pytest markers exactly as specced, ruff py313 + strict pyright.)*
- [ ] **`config.toml`** — Create the app config file referenced by docs 04, 08, 09. Content: `[window]` section with `preset = "desktop"`.
- [ ] **`assets/fonts/`** — Acquire and place `Inter-Bold.ttf`, `Inter-Regular.ttf`, `FiraCode-Regular.ttf` per doc 04 Section 3.2.

### 0.3 Implementation Order Document

- [ ] **`docs/design_docs/13_IMPLEMENTATION_ORDER.md`** — Codify the phased build sequence below so agents have a defined starting point and dependency chain.

---

## Phase 1 — Data Contracts and Base Classes

**Depends on:** Phase 0.2 (`pyproject.toml`)
**Output:** `src/visualizer/models/contracts.py`
**Testable without Pygame:** Yes

- [ ] `OpType` enum (COMPARE, SWAP, SHIFT, RANGE, TERMINAL, FAILURE)
- [ ] `SortResult` dataclass with all fields per doc 03
- [ ] `BaseSortAlgorithm` ABC with `data`, `size`, `comparisons`, `writes`, `name`, `complexity`
- [ ] `sort_generator` abstract method signature returning `Generator[SortResult, None, None]`

**Verification:** Import succeeds, pyright clean, ruff clean.

---

## Phase 2 — Algorithm Generators (Model Layer)

**Depends on:** Phase 1
**Output:** `src/visualizer/models/{bubble,selection,insertion,heap}.py`
**Testable without Pygame:** Yes

### 2.1 Bubble Sort

- [ ] Generator yields T1 compare on `(j, j+1)` before swap decision
- [ ] Early-exit optimization (swapped flag per pass)
- [ ] LimitLine boundary: inner loop stops at `n - pass - 1`
- [ ] Completion tick with full-array highlight
- [ ] Empty-input T0 failure tick guard
- [ ] Counter accuracy: comparisons=20, writes=26 for default array

### 2.2 Selection Sort

- [ ] Scan phase: T1 on `(min_idx, j)` with min tracking
- [ ] Message includes current minimum on every scan tick
- [ ] T2 swap on `(i, min_idx)` — skip when `i == min_idx`
- [ ] Completion tick with full-array highlight
- [ ] Empty-input T0 failure tick guard
- [ ] Counter accuracy: comparisons=21, writes=10 for default array

### 2.3 Insertion Sort

- [ ] T1 key-selection on `(i,)` — single-index highlight, does NOT increment comparisons
- [ ] T1 compare on `(j, j+1)` during shift loop — increments comparisons
- [ ] T2 shift on `(j, j+1)` — one element at a time, never batch (D-060, D-064)
- [ ] Terminating T1 compare when loop exits by condition (not by `j < 0`)
- [ ] T2 placement tick as final tick of each pass
- [ ] Completion tick with full-array highlight
- [ ] Empty-input T0 failure tick guard
- [ ] Counter accuracy: comparisons=17, writes=19 for default array

### 2.4 Heap Sort

- [ ] Phase 1 (Build Max-Heap): process nodes floor(n/2)-1 down to 0
- [ ] Sift-down tick sequence per level: T3 Logical Tree -> T1 compare(s) -> T2 swap (if needed)
- [ ] T3 Logical Tree Highlight: non-contiguous `(parent, left_child, right_child)`, parent always first
- [ ] Phase 2 (Extraction): T3 Boundary Emphasis (contiguous range, strictly decreasing k) before each extraction
- [ ] Extraction T2 swap on `(0, end)`
- [ ] Post-extraction sift-down repair with same tick sequence contract
- [ ] Settled elements: indices >= heap_size after extraction
- [ ] Completion tick with full-array highlight
- [ ] Empty-input T0 failure tick guard
- [ ] Counter accuracy: comparisons=20, writes=30 for default array
- [ ] Step count = 35 (T3 ticks excluded)
- [ ] T3 tick count = 6 boundary emphasis ticks for n=7

---

## Phase 3 — Unit Tests (Model Layer)

**Depends on:** Phase 1, Phase 2
**Output:** `tests/conftest.py`, `tests/unit/test_*.py`
**Testable without Pygame:** Yes (model tests only)

- [ ] Root `conftest.py` — verbatim from doc 08 Section 4.2 (SDL_VIDEODRIVER=dummy at module level, fixtures)
- [ ] `pyproject.toml` markers registered (unit, integration, slow)
- [ ] **TC-A1** Final sortedness (all algorithms, all fixtures)
- [ ] **TC-A2** Completion tick contract (exactly one, success=True, is_complete=True, full highlight)
- [ ] **TC-A3** Empty input contract (exactly one failure tick)
- [ ] **TC-A5** Easing function math (ease_in_out_quad boundary values)
- [ ] **TC-A7** Heap Sort phase contract (T3 variants, boundary decreasing k)
- [ ] **TC-A8** Sift-down correctness (subtree satisfies max-heap after sift-down)
- [ ] **TC-A9** Insertion Sort tick sequence (per-pass first/last tick, T1/T2 alternation)
- [ ] **TC-A10** Counter accuracy (all 4 algorithms, exact values)
- [ ] **TC-A11** Key-selection does not increment comparisons
- [ ] **TC-A12** Swap writes count (Bubble Sort: writes == swap_count * 2)
- [ ] **TC-A13** T3 step counter exclusion (steps=35, T3 count=6)
- [ ] **TC-A14** Insertion Sort terminating comparison (sorted_7 fixture)
- [ ] **TC-A19** Heap Sort sift-down tick sequence contract (T3->T1->T2 per level)
- [ ] **TC-A20** Tree layout node positioning (both presets, no overlap)
- [ ] **TC-A21** Tree layout edge connectivity
- [ ] **TC-A22** Tree layout shrinking (heap_size 7 down to 1)
- [ ] **TC-A23** Selection Sort pointer tracking
- [ ] **TC-A24** Insertion Sort KEY label lifecycle

---

## Phase 4 — Easing and Pure Math

**Depends on:** None (can parallel with Phase 2)
**Output:** `src/visualizer/views/easing.py`
**Testable without Pygame:** Yes (pure math, no Pygame imports)

- [ ] `ease_in_out_quad(t)` — quadratic ease-in-out
- [ ] Boundary guarantees: `f(0.0) == 0.0`, `f(1.0) == 1.0`
- [ ] Non-linear at `t=0.2` and `t=0.8`
- [ ] Clamp: `t >= 1.0` returns exactly `1.0`

---

## Phase 5 — View Layer (Sprites, Panels, Layout)

**Depends on:** Phase 1, Phase 4
**Output:** `src/visualizer/views/{window,panel,sprite,tree_layout,pointer,limitline,hud}.py`
**Requires Pygame:** Yes (headless OK for coordinate math)

- [ ] `NumberSprite` — circular outlined ring, float `(exact_x, exact_y)`, font surface caching per color state (D-034, D-069)
- [ ] `window.py` — display init, 2x2 grid layout with proportional tokens (doc 04 Section 2)
- [ ] `panel.py` — header vertical rhythm (title -> metrics -> message), array region, state overlays
- [ ] `tree_layout.py` — binary tree positioning for Heap Sort, edge rendering, sorted row (doc 04 Section 4.3.2)
- [ ] `pointer.py` — Selection Sort `i`/`j`/`min` arrows with coalescing (D-068)
- [ ] `limitline.py` — Bubble Sort vertical dashed boundary
- [ ] `hud.py` — Bubble Sort comparison/exchange counters overlay
- [ ] Z-ordering: lifted sprites on top of baseline (doc 12 Section 3)
- [ ] Highlight behavior: instant apply/replace, no fade (doc 12 Section 4)
- [ ] Compare lane: Bubble 50px transient, Insertion proportional sustained (doc 12 Section 5)
- [ ] Heap boundary sweep: staggered left-to-right over 120ms + 80ms hold (doc 10 Section 5.4.1)
- [ ] Insertion Sort KEY label + gap visualization (D-071, D-072)
- [ ] Heap Sort phase label "BUILD MAX-HEAP" / "EXTRACTION" (D-075)
- [ ] Heap Sort heap boundary marker dashed line (D-076)
- [ ] Completion panel green background `(35, 55, 42)` (D-078)
- [ ] Error state border + message styling

---

## Phase 6 — Controller (Orchestrator)

**Depends on:** Phase 1, Phase 2, Phase 5
**Output:** `src/visualizer/controllers/orchestrator.py`

- [ ] Independent queue per algorithm panel
- [ ] Panel state machine: idle_paused -> waiting_for_next_tick -> animating_operation -> completed/failed
- [ ] Operation timing: T1=150ms, T2=400ms, T3=200ms (integer milliseconds)
- [ ] Sift-down cadence override: T1=100ms, T2=250ms, T3=130ms (set after extraction swap, reset on boundary T3)
- [ ] Sprite identity delta computation (ID-based, never value-matching)
- [ ] `update(dt)` — subtract dt from remaining, fetch next SortResult when <= 0
- [ ] `elapsed_time_ms` — integer accumulator per panel, freezes on completion/failure
- [ ] Step counter: increment on success=True, is_complete=False, op_type != RANGE
- [ ] Failure isolation: one panel fails, others continue
- [ ] Play/Pause: freeze/resume all time accumulators and sprite positions
- [ ] Step: advance one tick per active panel, animate to completion, re-pause
- [ ] Restart: snap all sprites to initial, reset all state, re-pause

---

## Phase 7 — Integration (main.py + Event Loop)

**Depends on:** Phase 5, Phase 6
**Output:** `src/visualizer/main.py`

- [ ] Pygame init, clock, display.set_mode (no RESIZABLE flag — D-077)
- [ ] `config.toml` loading (preset selection)
- [ ] Window title "Learn Visual - Expand Knowledge"
- [ ] Event loop: keyboard bindings (Space, Right Arrow, R, Escape — D-022)
- [ ] On-screen control buttons (Play/Pause, Step, Restart)
- [ ] dt clamping: `dt = min(clock.tick(60), 33)` (doc 10 Section 1)
- [ ] Controller.update(dt) -> View.render() per frame
- [ ] Font loading with fallback (doc 04 Section 3.3)

---

## Phase 8 — Integration Tests

**Depends on:** Phase 6, Phase 7
**Output:** `tests/integration/test_{controller,panel_state,timer}.py`

- [ ] **TC-A4** Controller independent queues and timers (integer ms arithmetic)
- [ ] **TC-A6** Controller fairness (no starvation across 4 generators)
- [ ] **TC-A15** Panel state machine transitions (happy path)
- [ ] **TC-A16** Panel state machine failure isolation
- [ ] **TC-A17** Pause freezes interpolation state
- [ ] **TC-A18** Restart resets all state

---

## Phase 9 — CI Pipeline

**Depends on:** Phase 3, Phase 8
**Output:** `.github/workflows/ci.yml`

- [ ] GitHub Actions config per doc 11 Section 4
- [ ] SDL_VIDEODRIVER=dummy + SDL_AUDIODRIVER=dummy at job level
- [ ] Steps: checkout, uv install, sync, lint, typecheck, unit tests, full suite
- [ ] Trigger: PR to main + push to main

---

## Phase 10 — Manual Acceptance Testing

**Depends on:** All prior phases
**Spec:** doc 07 (all AT-01 through AT-27)

- [ ] AT-01 Startup baseline
- [ ] AT-02 Independent queue progression (step mode)
- [ ] AT-03 Completion race
- [ ] AT-03a Completion green panel
- [ ] AT-04 Generator completion contract
- [ ] AT-05 Selection Sort regression guard
- [ ] AT-06 Failure isolation
- [ ] AT-07 Sprite motion and tweening smoothness
- [ ] AT-08 Duplicate value stability
- [ ] AT-09 Heap Sort two-phase visual distinction
- [ ] AT-10 Heap Sort phase correctness
- [ ] AT-11 Insertion Sort lift-and-settle sequence
- [ ] AT-12 Counter accuracy
- [ ] AT-13 Bubble Sort LimitLine migration
- [ ] AT-14 Bubble Sort swap-lift counter sync
- [ ] AT-15 T3 step counter exclusion
- [ ] AT-16 Accent color readability
- [ ] AT-17 Tablet preset layout integrity
- [ ] AT-18 Desktop preset layout integrity
- [ ] AT-19 Selection Sort min tracking
- [ ] AT-20 Selection Sort sorted region stability
- [ ] AT-21 Heap Sort tree visualization
- [ ] AT-22 Heap Sort phase label
- [ ] AT-23 Heap Sort heap boundary marker
- [ ] AT-24 Selection Sort pointer assets
- [ ] AT-25 Insertion Sort KEY label and gap
- [ ] AT-26 Circular ring sprite shape
- [ ] AT-27 No algorithm title dots

---

## Dependency Graph (Quick Reference)

```plaintext
Phase 0 (spec gaps)
  |
Phase 1 (contracts)
  |
  +---> Phase 2 (algorithms) ---> Phase 3 (unit tests)
  |         |
  +---> Phase 4 (easing) --------+
  |                               |
  +---> Phase 5 (view layer) -----+---> Phase 6 (controller)
                                          |
                                    Phase 7 (main.py)
                                          |
                                    Phase 8 (integration tests)
                                          |
                                    Phase 9 (CI)
                                          |
                                    Phase 10 (manual acceptance)
```

Phases 2 and 4 can run in parallel. Phases 3 can begin as soon as each algorithm in Phase 2 is complete.
