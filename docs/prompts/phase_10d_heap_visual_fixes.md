# Phase 10d — Heap Sort Visual Fixes (Issues #1, #3, #6, #9)

**Model:** Sonnet 4.6
**Context:** Phase 10 acceptance testing found four visual issues in the Heap Sort panel, all in `HeapOverlay` or closely related constants in `sprite_manager.py`. These are prescriptive mechanical fixes — exact changes specified below.

**Out of scope:**
- Algorithm generators, contracts, orchestrator (unchanged)
- Other overlays (BubbleOverlay, SelectionOverlay, InsertionOverlay)
- main.py rendering loop (one call-site update for new constructor param)

---

## STEP 1 — DEVLOG PRE-ACTION

Append the following entry to `DEVLOG.md` (at the end of the current Phase 10 section):

```markdown
---

### 2026-05-08 — 10d pre-action: Heap Sort visual fixes (Issues #1, #3, #6, #9)

**Plan:** Four fixes in HeapOverlay class, all in `src/visualizer/views/sprite_manager.py`:
1. Issue #1 — Increase phase label offset so "BUILD MAX-HEAP" / "EXTRACTION" clears the root node.
2. Issue #3 — Clamp boundary marker drawing to panel rect; skip when boundary_x falls outside panel.
3. Issue #6 — Gate sorted-row placeholder drawing on extraction phase.
4. Issue #9 — Hide phase label on TERMINAL (set `_phase = None`, guard draw).

One call-site update in `main.py` to pass `panel_rect` to HeapOverlay constructor.

**Exit criteria:**
1. `uv run ruff check src/ tests/` — clean
2. `uv run ruff format --check src/ tests/` — clean
3. `uv run pytest -x` — 345/345 (no test changes, no regressions)
4. Import check — OK
```

---

## STEP 2 — IMPLEMENTATION

### §1 HeapOverlay constructor — add `panel_rect` parameter

**File:** `src/visualizer/views/sprite_manager.py`

The boundary clamp (Issue #3) needs the panel's left x-coordinate. Rather than reaching into `tree_layout._panel_rect` (private), add `panel_rect` as a constructor parameter.

Change the `__init__` signature from:

```python
def __init__(
    self,
    tree_layout: TreeLayout,
    phase_label: HeapPhaseLabel,
    boundary_label: HeapBoundaryLabel,
    array_size: int,
) -> None:
```

To:

```python
def __init__(
    self,
    tree_layout: TreeLayout,
    phase_label: HeapPhaseLabel,
    boundary_label: HeapBoundaryLabel,
    array_size: int,
    panel_rect: pygame.Rect,
) -> None:
```

Add to the body after `self._array_size = array_size`:

```python
self._panel_rect = panel_rect
```

### §2 Issue #1 — Phase label offset (AT-22)

**Problem:** `_PHASE_LABEL_OFFSET = 20` places the label 20px above `tree_top`, but the root node center IS at `tree_top` (depth 0). The root ring extends `tree_node_radius` above that (~22-26px at desktop resolution), so the label sits inside the root sprite.

**Fix:** Replace the static constant with a dynamic offset computed in `draw_over()` that clears the root ring.

In `draw_over()`, replace:

```python
label_y = self._tree_layout.tree_top - _PHASE_LABEL_OFFSET
self._phase_label.draw(surface, self._phase, label_y)
```

With:

```python
if self._phase is not None:
    root_clearance = self._tree_layout.tree_node_radius + 8
    label_y = self._tree_layout.tree_top - root_clearance
    self._phase_label.draw(surface, self._phase, label_y)
```

This positions the label `tree_node_radius + 8` pixels above `tree_top`, guaranteeing clearance above the root ring. The `8` provides comfortable visual breathing room.

The `if self._phase is not None` guard also handles Issue #9 (see §5 below).

After this change, the `_PHASE_LABEL_OFFSET` constant at line 889 is unused. Remove it.

### §3 Issue #3 — Boundary marker clamp (AT-23)

**Problem:** As `heap_size` shrinks during extraction, `boundary_x` (midpoint between `sorted_row_x(heap_size - 1)` and `sorted_row_x(heap_size)`) moves leftward. The Heap Sort panel is bottom-right (panel index 3). When `heap_size` reaches 1 or 0, `boundary_x` is near or past the panel's left edge, rendering the dashed line and "heap boundary" label in the adjacent Insertion Sort panel.

**Fix:** In `_draw_boundary_line()`, clamp `boundary_x` to the panel's left edge and skip drawing if out of bounds. In `draw_over()`, apply the same clamp to the boundary label.

Replace `_draw_boundary_line()` entirely:

```python
def _draw_boundary_line(self, surface: pygame.Surface) -> None:
    """Draw vertical dashed line between last active slot and first sorted slot."""
    boundary_x = (
        self._tree_layout.sorted_row_x(self._heap_size - 1)
        + self._tree_layout.sorted_row_x(self._heap_size)
    ) / 2
    # Clamp to panel bounds — don't draw outside the Heap Sort panel
    panel_left = self._panel_rect.x + 10  # small inset from edge
    panel_right = self._panel_rect.right - 10
    if boundary_x < panel_left or boundary_x > panel_right:
        return
    radius = self._tree_layout.tree_node_radius
    row_y = self._tree_layout.sorted_row_y
    y_start = row_y - radius - 10
    y_end = row_y + radius + 10
    # Dashed line: 6px dash, 4px gap
    y = y_start
    bx = round(boundary_x)
    while y < y_end:
        end_y = min(y + _BOUNDARY_DASH, y_end)
        pygame.draw.line(
            surface,
            _BOUNDARY_LINE_COLOR,
            (bx, round(y)),
            (bx, round(end_y)),
            _BOUNDARY_LINE_WIDTH,
        )
        y += _BOUNDARY_DASH + _BOUNDARY_GAP
```

In `draw_over()`, apply the same clamp to the boundary label section. Replace the existing boundary label block:

```python
if self._heap_size < self._array_size:
    boundary_x = (
        self._tree_layout.sorted_row_x(self._heap_size - 1)
        + self._tree_layout.sorted_row_x(self._heap_size)
    ) / 2
    label_y_boundary = (
        self._tree_layout.sorted_row_y
        + self._tree_layout.tree_node_radius
        + _BOUNDARY_LABEL_OFFSET
    )
    self._boundary_label.draw(surface, boundary_x, label_y_boundary)
```

With:

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

### §4 Issue #6 — Placeholder phase gate (AT-21/AT-23)

**Problem:** `_draw_placeholders()` draws dim circle outlines in the sorted row unconditionally. During BUILD MAX-HEAP, these appear as meaningless ghost circles below the tree.

**Fix:** In `draw_under()`, gate the placeholder call on extraction phase.

Replace:

```python
def draw_under(self, surface: pygame.Surface) -> None:
    """Draw edges, placeholders, and boundary line (behind sprites)."""
    self._draw_edges(surface)
    self._draw_placeholders(surface)
    if self._heap_size < self._array_size:
        self._draw_boundary_line(surface)
```

With:

```python
def draw_under(self, surface: pygame.Surface) -> None:
    """Draw edges, placeholders, and boundary line (behind sprites)."""
    self._draw_edges(surface)
    if self._phase == "EXTRACTION":
        self._draw_placeholders(surface)
        if self._heap_size < self._array_size:
            self._draw_boundary_line(surface)
```

Note: this also gates the boundary line on extraction phase, which is correct — the boundary line only has meaning during extraction when the sorted row is being populated.

### §5 Issue #9 — Hide phase label on completion (AT-22)

**Problem:** On TERMINAL tick, `_phase` stays as `"EXTRACTION"` and `draw_over()` continues drawing it. Other overlays (SelectionOverlay, BubbleOverlay) hide their decorations on TERMINAL.

**Fix:** In `_process_tick()`, set `self._phase = None` on TERMINAL/FAILURE.

Replace:

```python
elif op in (OpType.TERMINAL, OpType.FAILURE):
    self._active_edge_parent = None
    self._active_edge_children = ()
```

With:

```python
elif op in (OpType.TERMINAL, OpType.FAILURE):
    self._phase = None
    self._active_edge_parent = None
    self._active_edge_children = ()
```

The `if self._phase is not None` guard in `draw_over()` (added in §2) handles the rendering side. No additional changes needed.

Also update `reset()` — the current code sets `self._phase = "BUILD MAX-HEAP"` which is correct for restart. No change needed there.

### §6 Update `_phase` type annotation

In `__init__`, change:

```python
self._phase: str = "BUILD MAX-HEAP"
```

To:

```python
self._phase: str | None = "BUILD MAX-HEAP"
```

### §7 Call site update in main.py

**File:** `src/visualizer/main.py`

Update the HeapOverlay construction (around line 279) to pass `panel_rect`:

Replace:

```python
heap_overlay = HeapOverlay(
    tree_layout=_heap_tree_layout,
    phase_label=_heap_phase_label,
    boundary_label=_heap_boundary_label,
    array_size=len(initial_array),
)
```

With:

```python
heap_overlay = HeapOverlay(
    tree_layout=_heap_tree_layout,
    phase_label=_heap_phase_label,
    boundary_label=_heap_boundary_label,
    array_size=len(initial_array),
    panel_rect=layout.panel_rects[3],
)
```

### §8 Clean up unused constant

Remove the `_PHASE_LABEL_OFFSET` constant (line 889 in sprite_manager.py):

```python
_PHASE_LABEL_OFFSET: int = 20  # px above tree_top for the phase label
```

This line should be deleted entirely. It is no longer referenced after the §2 change.

### §9 What NOT to change

1. **Do NOT modify HeapPhaseLabel or HeapBoundaryLabel** in `hud.py`. The draw methods are correct — the issue is in HeapOverlay's coordinate calculations, not the label renderers.
2. **Do NOT modify tree_layout.py.** All geometry calculations are correct.
3. **Do NOT modify any other overlay class** (BubbleOverlay, SelectionOverlay, InsertionOverlay).
4. **Do NOT modify orchestrator.py or any model file.**
5. **Do NOT modify any test file.** HeapOverlay is visual-only with no unit tests. The 345 existing tests must pass unchanged.

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

Append a post-action entry to `DEVLOG.md` immediately after the 10d pre-action entry:

```markdown
---

### 2026-05-08 — 10d closed: Heap Sort visual fixes (Issues #1, #3, #6, #9)

**Worked on**

[Describe what was actually changed — phase label offset, boundary clamp, placeholder gate, phase label hide, panel_rect constructor param, constant removal. Note any deviations from the plan.]

**Corrections**

[List any ruff/format corrections, or "Zero corrections" if clean on first run.]

**Results**

- `uv run ruff check src/ tests/`: **[clean/N issues]**
- `uv run ruff format --check src/ tests/`: **[clean/N issues]**
- `uv run pytest -x`: **345/345 PASSED** (no regressions)
- Import check: **[PASS/FAIL]**

**Verification note**

Manual visual verification deferred to Steven — check with both default and duplicate arrays:
- Phase label ("BUILD MAX-HEAP" / "EXTRACTION") clears the root node at all times
- No boundary marker or label visible in Insertion Sort panel
- No placeholder circles during BUILD MAX-HEAP phase
- Phase label disappears on sort completion (green state)
- Restart (R) restores "BUILD MAX-HEAP" label correctly

**Next**

Proceed to 10e (Selection Sort pointer spacing — Issue #4).
```

---

## Context Files to Read

Read these files before writing any code:

1. `CLAUDE.md` — Critical Rules
2. `src/visualizer/views/sprite_manager.py` — HeapOverlay class (lines 893–1021), module-level constants (lines 885–890)
3. `src/visualizer/main.py` — HeapOverlay construction site (lines 273–284)
4. `src/visualizer/views/tree_layout.py` — TreeLayout public API (`tree_top`, `tree_node_radius`, `sorted_row_x()`, `sorted_row_y`)
5. `DEVLOG.md` — Active working journal (append pre/post entries at end of current Phase 10 section)
