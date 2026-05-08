# CLAUDE.md — Session Context for Visual Learning Sorting

## Project Identity

Sorting Algorithm Visualizer built with Python/Pygame. Four algorithms (Bubble, Selection, Insertion, Heap Sort) race side-by-side in a 2x2 panel grid. Each algorithm is a generator yielding `SortResult` ticks. The View animates sprites based on tick type and operation timing. The Controller manages independent queues per algorithm, creating a genuine race driven by simulated operation costs.

Package manager: **UV**. Python: **3.13+**. Platform: **Ubuntu (WSL on Dell 7770)**.

## Architecture

Strict MVC under `src/visualizer/`:

```
src/visualizer/
├── main.py                  # Pygame event loop, config loading
├── models/
│   ├── contracts.py         # SortResult, OpType, BaseSortAlgorithm
│   ├── bubble.py            # BubbleSort generator
│   ├── insertion.py         # InsertionSort generator
│   ├── heap.py              # HeapSort generator
│   └── selection.py         # SelectionSort generator
├── views/
│   ├── window.py            # Display init, 2x2 grid layout
│   ├── panel.py             # Per-algorithm rendering frame + header
│   ├── sprite.py            # NumberSprite — circular ring, float coords, easing
│   ├── easing.py            # Pure math, no Pygame imports
│   ├── tree_layout.py       # Heap Sort binary tree positioning
│   ├── pointer.py           # Selection Sort i/j/min arrows
│   ├── limitline.py         # Bubble Sort boundary line
│   └── hud.py               # Overlay counters, Heap phase label
└── controllers/
    └── orchestrator.py      # Independent queues, operation timing, event dispatch
```

## Critical Rules — Never Violate

1. **Sprite identity by unique ID, never by value.** Duplicate values in the array (e.g., `[3,1,3,2]`) make value-matching ambiguous. Track sprites via a permanent ID→slot mapping. Compute index deltas between array states to determine which sprite moved where.

2. **No exceptions from algorithms.** Domain errors (empty input, invalid data) yield a T0 failure tick and return. An unhandled exception crashes the Pygame event loop and kills all four panels.

3. **T3 (RANGE) ticks do not increment the step counter.** They are visual teaching aids, not algorithmic operations (D-041).

4. **Insertion Sort shifts one element at a time.** Each shift is an individual T1 compare + T2 shift tick pair. Never batch (D-060, D-064).

5. **Universal orange highlight `(255, 140, 0)` for all algorithms.** No per-algorithm accent colors. Identity comes from panel title + grid position (D-067).

6. **Operation timing is integer milliseconds.** T1 Compare=150ms, T2 Swap/Shift=400ms, T3 Range=200ms. Heap Sort sift-down cadence override after extraction: T1=100ms, T2=250ms, T3=130ms (D-056).

7. **dt clamp:** `dt = min(clock.tick(60), 33)` — prevents sprite overshoot on frame drops.

8. **Array state snapshots must be copies.** Every successful tick includes a copied `array_state`, never a reference to the mutable working array (D-011).

## SortResult Contract

```python
class OpType(Enum):
    COMPARE = auto()   # T1 — 150ms
    SWAP = auto()      # T2 — 400ms
    SHIFT = auto()     # T2 — 400ms
    RANGE = auto()     # T3 — 200ms (visual only, no mutation)
    TERMINAL = auto()  # Completion
    FAILURE = auto()   # T0 failure

@dataclass(slots=True)
class SortResult:
    success: bool
    message: str
    operation_type: OpType
    is_complete: bool = False
    array_state: list[int] | None = None
    highlight_indices: tuple[int, ...] | None = None
```

## Counter Accuracy (default array `[4, 7, 2, 6, 1, 5, 3]`)

| Algorithm | Comparisons | Writes | Steps |
|-----------|------------|--------|-------|
| Bubble Sort | 20 | 26 | — |
| Selection Sort | 21 | 10 | — |
| Insertion Sort | 17 | 19 | — |
| Heap Sort | 20 | 30 | 35 |

Heap Sort has 6 boundary T3 ticks (excluded from step count).

## Read-Order Guide for Spec Files

### Tier 1 — Read first for any task

| File | What it locks |
|------|--------------|
| `docs/design_docs/DECISIONS.md` | 81 locked decisions (D-001 through D-081). Canonical authority. |
| `docs/design_docs/02_ARCHITECTURE.md` | MVC structure, module boundaries, independent queue semantics |
| `docs/design_docs/03_DATA_CONTRACTS.md` | SortResult, OpType, tick taxonomy, highlight rules |
| `TODO/IMPLEMENTATION_TRACKER.md` | Current build status, phase dependencies, what's done/blocked |

### Tier 2 — Read for the specific layer you're building

**Model layer (algorithms):**
- `docs/design_docs/05_ALGORITHMS_VIS_SPEC.md` — Tick taxonomy and highlight semantics for all four sorts
- `docs/contracts/BUBBLE_SORT_ANIMATION.md` — Bubble Sort tick-by-tick contract
- `docs/contracts/SELECTION_SORT_ANIMATION.md` — Selection Sort tick-by-tick contract
- `docs/contracts/INSERTION_SORT_ANIMATION.md` — Insertion Sort tick-by-tick contract
- `docs/contracts/HEAP_SORT_ANIMATION.md` — Heap Sort tick-by-tick contract

**View layer (rendering):**
- `docs/design_docs/10_ANIMATION_SPEC.md` — Sprite motion, easing, frame timing, per-algorithm motion signatures
- `docs/design_docs/12_ANIMATION_FOUNDATION.md` — Shared rendering contracts (sprite identity, z-order, highlights)
- `docs/design_docs/04_UI_SPEC.md` — Panel layout, header rhythm, colors, fonts, resolution presets

**Controller layer:**
- `docs/design_docs/06_BEHAVIOR_SPEC.md` — Play/pause/step/restart, operation timing, panel state machine

**Testing:**
- `docs/design_docs/07_ACCEPTANCE_TESTS.md` — AT-01 through AT-27, human-checkable criteria
- `docs/design_docs/08_TEST_PLAN.md` — QA strategy, test levels, fixtures, TC-A test case matrix

### Tier 3 — Reference as needed

- `docs/design_docs/01_PRD.md` — Product requirements overview
- `docs/design_docs/09_DEV_ENV.md` — Dev environment setup
- `docs/design_docs/11_CI.md` — GitHub Actions CI pipeline
- `docs/AI_Conversations/` — Review sessions, gap analysis, agent trap identification

## Build Status

**Active phase: Post-10 (all implementation and visual testing complete).** Phases 0–10 are complete. 345/345 tests passing. See `TODO/IMPLEMENTATION_TRACKER.md` for the full breakdown.

**Completed (2026-04-23 / 2026-04-24 / 2026-04-30 / 2026-05-01):**
- Phase 0: Spec gaps (pyproject.toml, config.toml, pseudocode, fonts helper, implementation order)
- Phase 1: `contracts.py` — SortResult, OpType, BaseSortAlgorithm
- Phase 2: All four generators — Bubble (20/26), Selection (21/10), Insertion (17/19), Heap (20/30/35)
- Phase 3: Model unit tests — 29 tests, TC-A1/A2/A3/A7/A8/A9/A10/A11/A12/A13/A14/A19
- Phase 4: `easing.py` — ease_in_out_quad, ease_out_cubic, sine_arc (21 tests, TC-A5)
- Phase 5a: `window.py` — GridLayout, load_preset, init_display (25 tests); cumulative 75/75
- Phase 5b: `sprite.py` — NumberSprite, ColorState, COLOR_MAP (19 tests); cumulative 94/94
- Phase 5c: `panel.py` — PanelRenderer, header rhythm, state overlays (31 tests); cumulative 125/125
- Phase 5d: `tree_layout.py` — binary tree node positions, edges, sorted row (38 tests, TC-A20/A21/A22); cumulative 163/163
- Phase 5e: `pointer.py` — Selection Sort i/j/min arrows, coalescing (25 tests, TC-A23); cumulative 188/188
- Phase 5f: `limitline.py` — Bubble Sort dashed boundary, advance/reset (21 tests); cumulative 209/209
- Phase 5g: `hud.py` — BubbleHUD counters + HeapPhaseLabel + HeapBoundaryLabel (26 tests); cumulative 235/235
- Phase 6a: `orchestrator.py` (partial) — PanelState enum, duration constants, PanelContext, get_duration (28 tests); cumulative 263/263
- Phase 6b: `orchestrator.py` — Orchestrator class, update(dt) core loop, state machine, cadence lifecycle (27 tests); cumulative 290/290
- Phase 6c: `orchestrator.py` — compute_sprite_moves() pure function, slot_to_sprite_id mapping, sprite_moves dict, PanelContext.array_size (16 tests); cumulative 306/306
- Phase 6d: `orchestrator.py` — play(), pause(), step(), restart(), is_running/is_stepping properties, _running/_stepping guards, _algorithm_classes for restart re-instantiation (26 tests); cumulative 332/332
- Phase 6e: `tests/integration/test_orchestrator_integration.py` — TC-A4/A6/A15/A16/A17/A18 + counter accuracy, FailingAlgorithm helper (7 tests); cumulative 339/339

- Phase 7: `main.py` — Pygame event loop, config loading, font loading with fallback, keyboard bindings (Space/Right/R/Escape), orchestrator.update(dt) + panel rendering per frame (211 lines); cumulative 339/339 (no new tests)

- Phase 7b: `sprite_manager.py` — SpriteManager class (per-panel sprite lifecycle, animation dispatch via sprite_moves, ease_in_out_quad horizontal + sine_arc swap vertical, highlight colors, z-ordering, restart/pause handling); main.py wired with 4 SpriteManagers (200+207 lines); cumulative 339/339 (no new tests)

- Phase 7c-1: `SelectionOverlay` class in sprite_manager.py — tracks i/j/min pointer indices from Selection Sort ticks, wires PointerSet into panel 1. `algorithm_name` parameter added to SpriteManager.__init__. (2026-05-05, Sonnet 4.6, zero corrections)

- Phase 7c-2: Bubble Sort choreography — SpriteManager refactored: `_dispatch_tick` split into shared + algorithm-specific dispatch (`_dispatch_default`, `_dispatch_bubble`). `_compute_bubble_positions` implements 3-phase compare-lift (ascent 67ms, hold 33ms, descent 50ms) + horizontal swap slide at compare_lane_y. `BubbleOverlay` class manages LimitLine, BubbleHUD, and ComparisonPointer. (2026-05-05, Sonnet 4.6, 2 ruff corrections)

- Phase 7c-3: Insertion Sort choreography — cross-tick key elevation via `_insertion_key_id`/`_insertion_key_elevated` state. `_dispatch_insertion` handles key-lift (single-index T1), shift exclusion (key excluded from `_animating_sprites`), diagonal drop (single-index T2 placement). Key-color force in `_dispatch_tick` keeps elevated key orange across ticks. `InsertionOverlay` class renders stateless KEY label. (2026-05-05, Sonnet 4.6, zero corrections)

- Phase 7c-4: Heap Sort choreography — TreeLayout integration: sprites positioned at binary tree nodes (active heap) + sorted row (extracted). `_dispatch_heap` discriminates Boundary T3 (staggered 120ms sweep + 80ms hold) vs Logical Tree T3 (simultaneous flash) via D-081 message prefix. 2D arc interpolation for sift-down swaps; extraction arc at 1.75× height with reversed direction (root arcs UP). Steel-blue persistence via `_apply_sorted_settled`. `_draw_heap` z-ordering: sorted row → tree (deep-first) → arcing (upward-on-top). `HeapOverlay` class: parent-child edges with active orange highlighting, phase label (BUILD MAX-HEAP/EXTRACTION), sorted-row placeholder outlines, dashed boundary marker. Split draw (draw_under/draw_over) in main.py. sprite_manager.py: 965 lines; main.py: 337 lines. (2026-05-05, Opus 4.6, zero corrections + headless smoke test)

- Phase 7c-5: Selection Sort settled color + configurable array — `_dispatch_selection` replaces `_dispatch_default` for Selection Sort: standard arc-swap motion + `_selection_sorted_count` tracking (increment on T2 SWAP, `while` catch-up on T1 COMPARE for no-swap passes). `_apply_selection_settled` forces `ColorState.SETTLED` (steel-blue) on sorted prefix `0..sorted_count-1`. Dispatch routing updated: `elif "Selection Sort"` before Insertion Sort branch. `config.toml` gains optional `[sort].array` key; `_load_array()` in main.py reads config or falls back to default; `_build_orchestrator()` parameterized with `initial_array`. Addresses AT-20 + AT-08. (2026-05-05, Sonnet 4.6, zero corrections)

- Phase 10a: Build verification — counter accuracy confirmed, WSLg keyboard limitation documented (Windows native workaround). (2026-05-08)

- Phase 10b: Visual acceptance test walkthrough — AT-01 through AT-27. 7 issues found across AT-08, AT-21, AT-22, AT-23, AT-24. Issue triage and fix ordering established. (2026-05-08)

- Phase 10c: `compute_sprite_moves()` duplicate-value fix — highlight_indices augmentation for SWAP/SHIFT with equal values. 6 new tests. Issues #7 and #8 closed. (2026-05-08, Opus 4.6, zero corrections)

- Phase 10d: Heap Sort visual fixes batch — HeapOverlay panel_rect clamping, placeholder/boundary gating on EXTRACTION, phase label None on TERMINAL. Issues #3, #6, #9 closed. Issue #1 partial. (2026-05-08, Sonnet 4.6, zero corrections)

- Phase 10d-fix: HeapPhaseLabel repositioned to upper-right — `hud.py` right-aligned, `sprite_manager.py` simplified label_y. Issue #1 closed. (2026-05-08, Sonnet 4.6, 1 ruff correction)

- Phase 10f: False extraction detection fix — `_heap_in_extraction` flag gates extraction check in `_dispatch_heap` SWAP handler. Issue #10 closed. (2026-05-08, Sonnet 4.6, zero corrections)

- Phase 10e: Selection Sort `i` pointer spacing — `ARROW_GAP` split into `I_ARROW_GAP` (12px) and `JMIN_ARROW_GAP` (5px). (2026-05-08, Sonnet 4.6, 1 ruff correction)

- Phase 10g: Bubble Sort boundary line hide on completion — `_sort_complete` flag in BubbleOverlay. Issue #11 closed. (2026-05-08, Sonnet 4.6, zero corrections)

- Phase 10h: Selection Sort `i` pointer visibility — arrow geometry split (I_ 16/7 vs JMIN_ 12/5), cyan color `(80, 200, 220)`. (2026-05-08, Sonnet 4.6, 1 ruff correction)

- Phase 10i: Selection Sort `i` pointer relocated below j/min tier — `i_arrow_y()` rewritten with font-height-aware positioning, `_draw_i_pointer` flipped to upward triangle. Issue #4 fully closed. (2026-05-08, Sonnet 4.6, 1 ruff correction)

**Next:** Phase 9 (CI pipeline) deferred until needed. On-screen control buttons deferred. Ubuntu 24 native testing deferred. Font assets still using SysFont fallback.