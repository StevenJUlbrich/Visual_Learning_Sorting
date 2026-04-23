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
| `docs/design_docs/DECISIONS.md` | 79 locked decisions (D-001 through D-079). Canonical authority. |
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

**Active phase: Phase 5 (View Layer).** Phases 0–4 and Phase 5a are complete. See `TODO/IMPLEMENTATION_TRACKER.md` for the full breakdown.

**Completed (2026-04-23):**
- Phase 0: Spec gaps (pyproject.toml, config.toml, pseudocode, fonts helper, implementation order)
- Phase 1: `contracts.py` — SortResult, OpType, BaseSortAlgorithm
- Phase 2: All four generators — Bubble (20/26), Selection (21/10), Insertion (17/19), Heap (20/30/35)
- Phase 3: Model unit tests — 50 tests, TC-A1/A2/A3/A5/A7/A8/A9/A10/A11/A12/A13/A14/A19
- Phase 4: `easing.py` — ease_in_out_quad, ease_out_cubic, sine_arc (21 tests, TC-A5)
- Phase 5a: `window.py` — GridLayout, load_preset, init_display (25 tests); cumulative 75/75

**Next:** Phase 5b — `sprite.py` (NumberSprite: circular ring, float coords, easing integration).

Build order: Phase 0 → Phase 1 → Phase 2 + Phase 4 (parallel) → Phase 3 → Phase 5 → Phase 6 → Phase 7 → Phase 8 → Phase 9 → Phase 10.

## Initial Array

`[4, 7, 2, 6, 1, 5, 3]` — chosen because it is not a valid max-heap (3 violations), has 13 inversions, and produces meaningful visual activity across all four algorithms (D-006).
