# Phase 7c-1 — Selection Sort Pointer Overlay

## Copy everything below this line into Claude Code

---

You are implementing Phase 7c-1 of the Sorting Algorithm Visualizer. This phase creates a `SelectionOverlay` class that tracks the `i` / `j` / `min` pointer indices from Selection Sort tick data and wires the pre-built `PointerSet` (from `pointer.py`) into the Selection Sort panel. It also adds an `algorithm_name` parameter to `SpriteManager.__init__` as a forward-looking hook for later choreography sub-phases.

After this phase, the Selection Sort panel (panel index 1) will display three labeled pointer arrows — `i` above the baseline, `j` and `min` below — that move in sync with the algorithm's scan-and-swap pattern.

## Rules

- Do NOT run any git commands.
- Do NOT create new spec or documentation files.
- Do NOT modify `orchestrator.py`, `sprite.py`, `easing.py`, `panel.py`, `window.py`, `pointer.py`, `limitline.py`, `hud.py`, `tree_layout.py`, or any model file.
- Only modify `src/visualizer/views/sprite_manager.py` and `src/visualizer/main.py`.
- All four lint/typecheck/test gates must pass before you stop.

## Scope — what is IN Phase 7c-1

1. Add `algorithm_name: str` parameter to `SpriteManager.__init__` — store as `self._algorithm_name`, no behavioral change yet
2. `SelectionOverlay` class in `sprite_manager.py` — owns a `PointerSet` instance, tracks pointer indices from ticks, draws pointers
3. Wire `SelectionOverlay` into `main.py` for panel index 1 (Selection Sort)
4. Pointer index tracking from tick `highlight_indices`:
   - T1 Compare: `highlight_indices = (min_idx, j)` — extract both values
   - T2 Swap: `highlight_indices = (i, min_idx)` — extract both, prepare for next pass
   - TERMINAL/FAILURE: hide all pointers
5. New-pass detection: identify when a new outer-loop pass begins (j decreases or first tick after a swap)
6. Pointer visibility rules per the Selection Sort Animation Contract §4:
   - During T1 scan: all three pointers visible (coalescing handled by PointerSet)
   - During T2 swap: `i` hides, `j` hides, `min` stays visible
   - After completion: all hidden
7. Restart handling: `selection_overlay.reset()` called alongside `sm.reset()` on K_r

## Scope — what is DEFERRED (do NOT implement)

- Bubble Sort 3-phase compare-lift, horizontal swap slide, LimitLine, BubbleHUD, ComparisonPointer
- Insertion Sort key elevation, diagonal drop, KEY label
- Heap Sort tree layout, extraction arc, boundary sweep, phase/boundary labels
- Any motion model changes in SpriteManager — Selection Sort uses the existing Phase 7b baseline (standard arc swaps, highlight-only compares)
- Unit tests for SelectionOverlay (visual verification only for this phase)

## STEP 1 — DEVLOG PRE-ACTION

Append the following entry to `DEVLOG.md`:

```markdown
## 2026-05-05 — Phase 7c-1 pre-action: Selection Sort pointer overlay

### Plan

Create `SelectionOverlay` class in `sprite_manager.py` that tracks the `i` (sorted boundary), `j` (scan cursor), and `min` (minimum tracker) pointer indices by reading `highlight_indices` from Selection Sort ticks. Wire the pre-built `PointerSet` from `pointer.py` to draw labeled arrows in the Selection Sort panel (index 1). Add `algorithm_name` parameter to `SpriteManager.__init__` as a hook for later choreography sub-phases. No changes to sprite motion — Selection Sort uses the existing baseline arc swap model.

### Exit criteria

1. pyright — 0 errors, 0 warnings
2. ruff check + ruff format — clean
3. Existing test suite — 339/339 still passing (no regressions)
4. Visual: Selection Sort panel shows i/j/min arrows that track the algorithm's scan pattern
```

## STEP 2 — IMPLEMENTATION

### 2.1 Modify `SpriteManager.__init__` — add `algorithm_name` parameter

Add `algorithm_name: str` as the **first** parameter after `self` (before `panel_rect`):

```python
def __init__(
    self,
    algorithm_name: str,
    panel_rect: pygame.Rect,
    array_x_padding: int,
    slot_width: float,
    font: pygame.font.Font,
    initial_array: list[int],
) -> None:
    self._algorithm_name = algorithm_name
    # ... rest of existing __init__ unchanged ...
```

Store it as `self._algorithm_name`. No other behavioral changes to SpriteManager.

### 2.2 Create `SelectionOverlay` class in `sprite_manager.py`

Add this class **after** the `SpriteManager` class in the same file.

```python
"""SelectionOverlay — tracks i/j/min pointer indices for the Selection Sort panel."""
```

#### Imports needed (add at top of sprite_manager.py)

```python
from visualizer.views.pointer import PointerSet
```

#### Class: `SelectionOverlay`

**Constructor** `__init__(self, pointer_set: PointerSet)`:

- `pointer_set: PointerSet` — the pre-built pointer arrow renderer (created in main.py)
- Internal state:
  - `_pointer_set: PointerSet` — stored reference
  - `_last_tick: SortResult | None = None` — for identity-based new-tick detection
  - `_awaiting_new_pass: bool = True` — True at start and after each T2 swap
  - `_i: int = 0` — current sorted boundary index
  - `_j: int = 0` — current scan cursor index (initialized to 0; first T1 will trigger new-pass detection)
  - `_min: int = 0` — current minimum tracker index
  - `_draw_i: int | None = None` — i pointer slot to draw (None = hidden)
  - `_draw_j: int | None = None` — j pointer slot to draw (None = hidden)
  - `_draw_min: int | None = None` — min pointer slot to draw (None = hidden)

**Method: `update(self, ctx: PanelContext) -> None`**:

1. New-tick detection (same identity-check pattern as SpriteManager):
   - If `ctx.current_tick is not None and ctx.current_tick is not self._last_tick`:
     - Call `self._process_tick(ctx.current_tick)`
     - Set `self._last_tick = ctx.current_tick`

**Method: `_process_tick(self, tick: SortResult) -> None`**:

Handle each operation type:

**Case `OpType.COMPARE` (T1 — scan tick):**

1. Guard: if `tick.highlight_indices is None or len(tick.highlight_indices) != 2`, return.
2. Extract: `min_idx = tick.highlight_indices[0]`, `j = tick.highlight_indices[1]`.
3. **New-pass detection:** If `self._awaiting_new_pass` is True **OR** `j < self._j`:
   - `self._i = min_idx` — at pass start, `min_idx` equals `i` (the sorted boundary).
   - `self._awaiting_new_pass = False`
4. Update tracking: `self._min = min_idx`, `self._j = j`.
5. Set draw state: `self._draw_i = self._i`, `self._draw_j = j`, `self._draw_min = min_idx`.

**Why new-pass detection works:**
- Within a pass, `j` strictly increases from `i+1` to `n-1`. A decrease in `j` means a new pass started.
- After a T2 swap, `_awaiting_new_pass` is True, catching the next T1 as a new pass start.
- At pass start, `min_idx == i` (the generator initializes `min_idx = i` before scanning), so reading `min_idx` from the first T1 gives us the correct `i`.
- For passes where `min_idx == i` (no swap needed), there is no T2. The next pass's first T1 has `j = new_i + 1`, which is less than the previous pass's last `j` (which was `n-1`). So `j < self._j` triggers correctly.

**Case `OpType.SWAP` (T2 — swap tick):**

1. Guard: if `tick.highlight_indices is None or len(tick.highlight_indices) != 2`, return.
2. Per Selection Sort Animation Contract §4 — during T2 swap:
   - `self._draw_i = None` — i pointer hides (prevents collision with arcing sprite)
   - `self._draw_j = None` — j pointer hides (pass is over)
   - `self._draw_min = tick.highlight_indices[1]` — min pointer stays visible below arcing min sprite
3. Set `self._awaiting_new_pass = True` — next T1 starts a new pass.

**Case `OpType.TERMINAL` or `OpType.FAILURE`:**

1. Hide all pointers: `self._draw_i = None`, `self._draw_j = None`, `self._draw_min = None`.

**All other OpTypes (SHIFT, RANGE):** No action — Selection Sort does not emit these.

**Method: `draw(self, surface: pygame.Surface) -> None`**:

```python
self._pointer_set.draw(surface, self._draw_i, self._draw_j, self._draw_min)
```

PointerSet.draw() already handles:
- None values → pointer not drawn
- D-068 coalescing → j hidden when j == min

**Method: `reset(self) -> None`**:

Clear all state to initial:
```python
self._last_tick = None
self._awaiting_new_pass = True
self._i = 0
self._j = 0
self._min = 0
self._draw_i = None
self._draw_j = None
self._draw_min = None
```

### 2.3 Modify `src/visualizer/main.py`

**New imports to add:**

```python
from visualizer.views.pointer import PointerSet
from visualizer.views.sprite import RING_DIAMETER_RATIO
from visualizer.views.sprite_manager import SelectionOverlay, SpriteManager
```

Update the existing `SpriteManager` import line to also import `SelectionOverlay`.

**Update SpriteManager construction** — pass `algorithm_name` as the first argument:

The algorithm order is: index 0 = Bubble Sort, 1 = Selection Sort, 2 = Insertion Sort, 3 = Heap Sort. Use `orchestrator.panels[i].algorithm_name` to get names, but the orchestrator isn't created yet at that point. Instead, define a name list:

```python
_ALGORITHM_NAMES: list[str] = ["Bubble Sort", "Selection Sort", "Insertion Sort", "Heap Sort"]
```

Add this as a module-level constant near `INITIAL_ARRAY`. Then update the sprite_managers list comprehension:

```python
sprite_managers = [
    SpriteManager(
        algorithm_name=_ALGORITHM_NAMES[i],
        panel_rect=layout.panel_rects[i],
        array_x_padding=layout.ARRAY_X_PADDING,
        slot_width=layout.slot_width,
        font=number_font,
        initial_array=INITIAL_ARRAY,
    )
    for i in range(4)
]
```

**Create the SelectionOverlay** — after creating sprite_managers, before `orchestrator`:

```python
# Selection Sort pointer overlay (panel index 1)
_ring_radius = int(layout.slot_width * RING_DIAMETER_RATIO) // 2
_pointer_set = PointerSet(
    panel_rect=layout.panel_rects[1],
    array_x_padding=layout.ARRAY_X_PADDING,
    slot_width=layout.slot_width,
    ring_radius=_ring_radius,
    body_font=body_font,
)
selection_overlay = SelectionOverlay(_pointer_set)
```

**Wire into the render loop** — after `sprite_managers[i].draw(surface)`, add the overlay calls for panel 1:

```python
for i, renderer in enumerate(panel_renderers):
    ctx = orchestrator.panels[i]
    view_state = _map_panel_state(ctx)
    renderer.draw_background(surface, view_state)
    renderer.draw_header(
        surface,
        ctx.algorithm_name,
        _build_metrics(ctx),
        _build_message(ctx),
        view_state,
    )
    sprite_managers[i].update(dt, ctx)
    sprite_managers[i].draw(surface)

    # Selection Sort pointer overlay (panel index 1)
    if i == 1:
        selection_overlay.update(ctx)
        selection_overlay.draw(surface)
```

**Wire restart** — in the K_r handler, after resetting sprite managers:

```python
elif event.key == pygame.K_r:
    orchestrator.restart()
    for sm in sprite_managers:
        sm.reset(INITIAL_ARRAY)
    selection_overlay.reset()
```

## STEP 3 — VERIFICATION

Run all gates:

```bash
# Gate 1: Pyright
PYRIGHT_PYTHON_GLOBAL_NODE=false uv run pyright src/visualizer/views/sprite_manager.py src/visualizer/main.py

# Gate 2: Ruff
uv run ruff check src/visualizer/views/sprite_manager.py src/visualizer/main.py && uv run ruff format --check src/visualizer/views/sprite_manager.py src/visualizer/main.py

# Gate 3: Existing tests — no regressions
uv run pytest tests/ -q

# Gate 4: Import check — SelectionOverlay loads without error
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy uv run python -c "
from visualizer.views.sprite_manager import SpriteManager, SelectionOverlay
print('SpriteManager imported OK')
print('SelectionOverlay imported OK')
"
```

All four must pass. Fix any issues before proceeding.

## STEP 4 — DEVLOG POST-ACTION

Append a post-action entry to `DEVLOG.md` immediately after the pre-action entry:

```markdown
## 2026-05-05 — Phase 7c-1 closed: Selection Sort pointer overlay (post-action)

### Worked on

[Describe what was actually created — SelectionOverlay class, pointer tracking logic, main.py wiring, any deviations from the plan.]

### Corrections

[List any ruff/pyright corrections, or "Zero corrections" if clean on first run.]

### Results

- `uv run pyright src/visualizer/views/sprite_manager.py src/visualizer/main.py`: **[N] errors, [N] warnings**
- `uv run ruff check` + `uv run ruff format --check`: **[clean/N issues]**
- `uv run pytest tests/ -q`: **339/339 PASSED** (no regressions)
- Import check: **[PASS/FAIL]**

### Next

Phase 7c-2: Bubble Sort choreography (3-phase compare-lift, horizontal swap slide, LimitLine, BubbleHUD, ComparisonPointer).
```

## Context files to read

Read these files before writing any code:

1. `CLAUDE.md` — Critical Rules (especially #1 sprite identity, #5 universal orange, #6 timing)
2. `src/visualizer/views/pointer.py` — PointerSet constructor (`panel_rect`, `array_x_padding`, `slot_width`, `ring_radius`, `body_font`), `draw(surface, i_index, j_index, min_index)` — all nullable ints, `coalesced_pointers()` for D-068
3. `src/visualizer/views/sprite.py` — `RING_DIAMETER_RATIO = 0.65`, `ring_radius = int(slot_width * RING_DIAMETER_RATIO) // 2`
4. `src/visualizer/views/sprite_manager.py` — current SpriteManager (do not change motion/draw/reset logic, only add `algorithm_name` param)
5. `src/visualizer/main.py` — current render loop structure, panel order (0=Bubble, 1=Selection, 2=Insertion, 3=Heap)
6. `src/visualizer/models/selection.py` — T1 yields `highlight_indices=(min_idx, j)`, T2 yields `highlight_indices=(i, min_idx)`
7. `docs/contracts/SELECTION_SORT_ANIMATION.md` — §4 Triple Pointer Lifecycle (visibility rules), §5 Scan Contract, §6 Swap Contract

---
