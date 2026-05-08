# Phase 10f — Fix False Extraction Detection During BUILD MAX-HEAP (Issue #10)

**Model:** Sonnet 4.6
**Context:** During BUILD MAX-HEAP, sift-down at the root produces a SWAP tick with `highlight_indices` containing index 0. The extraction detection in `_dispatch_heap()` uses `is_extraction = hi is not None and 0 in hi`, which falsely triggers on this root sift-down swap. This prematurely decrements `_heap_size`, places a sprite in the sorted row, and recomputes tree geometry for the wrong node count. The cascade causes: (a) "heap boundary" label appearing during BUILD MAX-HEAP, (b) tree edges disappearing as nodes migrate to the sorted row, (c) the tree collapsing into a flat row during extraction.

**Root cause trace (default array `[4, 7, 2, 6, 1, 5, 3]`):**
1. BUILD MAX-HEAP sifts down at parent 0 (value 4), swaps with child at index 1 (value 7).
2. `highlight_indices = (0, 1)` → `0 in hi` = True → `is_extraction` = True (WRONG).
3. `_heap_size` drops from 7 → 6. Tree recomputed for 6 nodes. Sprite at slot 6 placed in sorted row.
4. All subsequent tree geometry is wrong. Further root swaps during extraction compound the error.

**Fix:** Add `_heap_in_extraction: bool` flag to SpriteManager. Set it True when the first boundary T3 fires (message starts with "Active heap"), which marks the BUILD→EXTRACTION transition. Gate extraction detection on this flag.

**Defensive addition:** Gate the boundary LABEL drawing in `HeapOverlay.draw_over()` on `self._phase == "EXTRACTION"`, matching the existing gate in `draw_under()`. With the SpriteManager fix, `_heap_size` will correctly stay at `_array_size` during BUILD MAX-HEAP, so this is belt-and-suspenders — but it closes the inconsistency.

**Out of scope:**
- Algorithm generators, contracts, orchestrator (unchanged)
- Other overlays (BubbleOverlay, SelectionOverlay, InsertionOverlay)
- HeapPhaseLabel, HeapBoundaryLabel in hud.py (unchanged)
- tree_layout.py, main.py (no changes needed)
- No new tests — this is a visual-only fix; existing 345 tests must pass unchanged

---

## STEP 1 — DEVLOG PRE-ACTION

Append the following entry to `DEVLOG.md` (at the end of the file):

```markdown
---

### 2026-05-08 — 10f pre-action: Fix false extraction detection during BUILD MAX-HEAP (Issue #10)

**Root cause:** `_dispatch_heap()` in SpriteManager detects extraction swaps via `is_extraction = hi is not None and 0 in hi`. During BUILD MAX-HEAP, sift-down at the root produces a SWAP with index 0 in highlight_indices, falsely triggering extraction. This prematurely decrements `_heap_size`, corrupts tree geometry, and places sprites in the sorted row. All three visual symptoms (boundary label during build, disappearing edges, flat-row tree) trace to this single bug.

**Plan:** Three changes, all in `sprite_manager.py`:
1. Add `_heap_in_extraction: bool = False` to SpriteManager `__init__` and `reset()`.
2. Set `_heap_in_extraction = True` on boundary T3 ("Active heap" message) in `_dispatch_heap()`.
3. Gate extraction detection: `is_extraction = self._heap_in_extraction and hi is not None and 0 in hi`.
4. (Defensive) Gate boundary label drawing in `HeapOverlay.draw_over()` on `self._phase == "EXTRACTION"`.

**Exit criteria:**
1. `uv run ruff check src/ tests/` — clean
2. `uv run ruff format --check src/ tests/` — clean
3. `uv run pytest -x` — 345/345 (no test changes, no regressions)
4. Import check — OK
```

---

## STEP 2 — IMPLEMENTATION

### §1 Add `_heap_in_extraction` flag to `__init__`

**File:** `src/visualizer/views/sprite_manager.py`

In `SpriteManager.__init__`, in the "Heap Sort state" block (around line 78), add the new flag after `_heap_sweep_indices`:

Replace:

```python
        # Heap Sort state
        self._tree_layout: TreeLayout | None = tree_layout
        self._heap_size: int = len(initial_array)
        self._heap_node_positions: list[tuple[float, float]] = []
        self._extraction_arc_height: float = panel_rect.height * 0.14
        self._is_extraction_swap: bool = False
        self._heap_sweep_indices: tuple[int, ...] | None = None
```

With:

```python
        # Heap Sort state
        self._tree_layout: TreeLayout | None = tree_layout
        self._heap_size: int = len(initial_array)
        self._heap_node_positions: list[tuple[float, float]] = []
        self._extraction_arc_height: float = panel_rect.height * 0.14
        self._is_extraction_swap: bool = False
        self._heap_sweep_indices: tuple[int, ...] | None = None
        self._heap_in_extraction: bool = False
```

### §2 Set `_heap_in_extraction = True` on boundary T3

**File:** `src/visualizer/views/sprite_manager.py`

In `_dispatch_heap()`, inside the boundary T3 handler (around line 302), add the flag set after the "Active heap" check:

Replace:

```python
        if op == OpType.RANGE:
            hi = tick.highlight_indices
            if tick.message.startswith("Active heap"):
                # Boundary T3 — staggered sweep: reset highlights, sweep applies progressively
                self._heap_sweep_indices = hi
                for sprite in self._sprites:
                    sprite.set_color_state(ColorState.DEFAULT)
                # Re-apply steel-blue for sorted-row sprites
                self._apply_sorted_settled(ctx)
```

With:

```python
        if op == OpType.RANGE:
            hi = tick.highlight_indices
            if tick.message.startswith("Active heap"):
                # Boundary T3 — marks BUILD→EXTRACTION transition
                self._heap_in_extraction = True
                # Staggered sweep: reset highlights, sweep applies progressively
                self._heap_sweep_indices = hi
                for sprite in self._sprites:
                    sprite.set_color_state(ColorState.DEFAULT)
                # Re-apply steel-blue for sorted-row sprites
                self._apply_sorted_settled(ctx)
```

### §3 Gate extraction detection on `_heap_in_extraction`

**File:** `src/visualizer/views/sprite_manager.py`

In `_dispatch_heap()`, the SWAP handler (around line 320), change the extraction detection:

Replace:

```python
            # Detect extraction swap: one of the highlighted indices is 0
            is_extraction = hi is not None and 0 in hi
```

With:

```python
            # Detect extraction swap: must be in extraction phase AND involve the root
            is_extraction = (
                self._heap_in_extraction and hi is not None and 0 in hi
            )
```

### §4 Reset flag in `reset()`

**File:** `src/visualizer/views/sprite_manager.py`

In `SpriteManager.reset()`, in the "Heap Sort state" block (around line 694), add the flag reset:

Replace:

```python
        # Heap Sort state
        self._is_extraction_swap = False
        self._heap_sweep_indices = None
        self._heap_size = len(initial_array)
```

With:

```python
        # Heap Sort state
        self._is_extraction_swap = False
        self._heap_sweep_indices = None
        self._heap_size = len(initial_array)
        self._heap_in_extraction = False
```

### §5 (Defensive) Gate boundary label on EXTRACTION phase in HeapOverlay

**File:** `src/visualizer/views/sprite_manager.py`

In `HeapOverlay.draw_over()`, add a phase check to the boundary label block so it matches the existing phase gate in `draw_under()`:

Replace:

```python
        if self._heap_size < self._array_size:
            boundary_x = (
                self._tree_layout.sorted_row_x(self._heap_size - 1)
                + self._tree_layout.sorted_row_x(self._heap_size)
            ) / 2
            panel_left = self._panel_rect.x + 10
            panel_right = self._panel_rect.right - 10
            if panel_left <= boundary_x <= panel_right:
                label_y_boundary = (
                    self._tree_layout.sorted_row_y
                    + self._tree_layout.tree_node_radius
                    + _BOUNDARY_LABEL_OFFSET
                )
                self._boundary_label.draw(surface, boundary_x, label_y_boundary)
```

With:

```python
        if self._phase == "EXTRACTION" and self._heap_size < self._array_size:
            boundary_x = (
                self._tree_layout.sorted_row_x(self._heap_size - 1)
                + self._tree_layout.sorted_row_x(self._heap_size)
            ) / 2
            panel_left = self._panel_rect.x + 10
            panel_right = self._panel_rect.right - 10
            if panel_left <= boundary_x <= panel_right:
                label_y_boundary = (
                    self._tree_layout.sorted_row_y
                    + self._tree_layout.tree_node_radius
                    + _BOUNDARY_LABEL_OFFSET
                )
                self._boundary_label.draw(surface, boundary_x, label_y_boundary)
```

### §6 What NOT to change

1. **Do NOT modify any algorithm generator** (bubble.py, selection.py, insertion.py, heap.py).
2. **Do NOT modify orchestrator.py** — the tick data is correct; the bug is in the view layer's interpretation.
3. **Do NOT modify tree_layout.py** — geometry calculations are correct.
4. **Do NOT modify hud.py** — HeapPhaseLabel and HeapBoundaryLabel are correct.
5. **Do NOT modify main.py** — no call-site changes needed.
6. **Do NOT modify any test file.** Existing 345 tests must pass unchanged.
7. **Do NOT modify HeapOverlay.__init__, update(), _process_tick(), draw_under(), _draw_edges(), _draw_placeholders(), _draw_boundary_line(), or reset().** Only draw_over() gets the §5 defensive gate.

---

## STEP 3 — GATES

Run all four in sequence. All must pass. Fix any issues before proceeding.

```bash
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run pytest -x
python -c "from visualizer.views.sprite_manager import HeapOverlay; print('OK')"
```

---

## STEP 4 — DEVLOG POST-ACTION

Append a post-action entry to `DEVLOG.md` immediately after the 10f pre-action entry:

```markdown
---

### 2026-05-08 — 10f closed: False extraction detection fixed (Issue #10)

**Worked on**

[Describe: Added `_heap_in_extraction` boolean flag to SpriteManager — set True on boundary T3 ("Active heap" message), gates extraction detection in SWAP handler. Prevents `_heap_size` from decrementing during BUILD MAX-HEAP root sift-down. Defensive phase gate added to HeapOverlay.draw_over() boundary label drawing.]

**Corrections**

[List any ruff/format corrections, or "Zero corrections" if clean on first run.]

**Results**

- `uv run ruff check src/ tests/`: **[clean/N issues]**
- `uv run ruff format --check src/ tests/`: **[clean/N issues]**
- `uv run pytest -x`: **345/345 PASSED** (no regressions)
- Import check: **[PASS/FAIL]**

**Verification note**

Manual visual verification deferred to Steven — check with default array `[4, 7, 2, 6, 1, 5, 3]`:
- During BUILD MAX-HEAP: all 7 nodes remain in tree positions, no boundary label visible, edges intact throughout
- Root sift-down swap (4↔7) does NOT trigger extraction behavior
- Transition to EXTRACTION: boundary T3 fires, then first extraction swap correctly decrements heap_size
- Tree shrinks correctly as extractions proceed — edges and node positions update properly at each step
- Sorted row populates from right to left with steel-blue sprites
- No sprites appear at sorted-row positions during BUILD MAX-HEAP
- Restart (R) correctly resets to BUILD MAX-HEAP with full 7-node tree

**Next**

Proceed to 10e (Selection Sort pointer spacing — Issue #4).
```

---

## Context Files to Read

Read these files before writing any code:

1. `CLAUDE.md` — Critical Rules
2. `src/visualizer/views/sprite_manager.py` — SpriteManager.__init__ (lines 78–84), _dispatch_heap() (lines 292–361), reset() (lines 694–697), HeapOverlay.draw_over() (lines 1007–1025)
3. `DEVLOG.md` — Active working journal (append pre/post entries at end)
