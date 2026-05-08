# Phase 10d-fix — Reposition Heap Phase Label to Upper-Right (Issue #1 revisit)

**Model:** Sonnet 4.6
**Context:** Phase 10d fixed Issues #3, #6, #9 correctly but Issue #1 (phase label overlapping root node) persists. The 10d fix replaced the static `_PHASE_LABEL_OFFSET = 20` with `tree_node_radius + 8`, but this still overlaps because `label_y` is the TEXT TOP — the text extends downward by `font_height` (~18px), so the bottom of the label still sits inside the root ring.

Additionally, the 10d execution truncated `sprite_manager.py` — the boundary label section of `draw_over()` and the `reset()` method were lost. **This has already been manually restored.** Do not re-create these sections; they are present and correct in the current file.

**Design decision:** Instead of fighting for vertical space between the header and root node, move the phase label to the upper-right corner of the tree area. This eliminates the overlap entirely and reads as a clean status indicator.

**Out of scope:**
- Algorithm generators, contracts, orchestrator (unchanged)
- Other overlays (BubbleOverlay, SelectionOverlay, InsertionOverlay)
- tree_layout.py, main.py (no changes needed)
- HeapBoundaryLabel (unchanged)

---

## STEP 1 — DEVLOG PRE-ACTION

Append the following entry to `DEVLOG.md` (at the end of the file):

```markdown
---

### 2026-05-08 — 10d-fix pre-action: Reposition phase label to upper-right (Issue #1 revisit)

**Problem:** 10d's vertical offset fix (`tree_node_radius + 8`) still overlaps the root node because `label_y` is the text top edge — the text renders downward by ~18px (font_height), so the bottom of the label sits inside the root ring.

**Plan:** Reposition the phase label from centered-above-root to right-aligned in the upper-right of the tree area. Two files changed:
1. `hud.py` — HeapPhaseLabel: right-align instead of center. Store `_right_x` (panel right edge minus 15px margin). `draw()` positions text right-aligned at `_right_x`.
2. `sprite_manager.py` — HeapOverlay.draw_over(): set `label_y = tree_top` (vertically aligned with root node center, but horizontally separated — no overlap possible).
3. `test_hud.py` — Update `center_x` property test to `right_x`.

Also notes: 10d execution truncated sprite_manager.py (boundary label section of draw_over + reset method lost). Already restored manually before this prompt.

**Exit criteria:**
1. `uv run ruff check src/ tests/` — clean
2. `uv run ruff format --check src/ tests/` — clean
3. `uv run pytest -x` — 345/345 (no test changes except property rename)
4. Import check — OK
```

---

## STEP 2 — IMPLEMENTATION

### §1 HeapPhaseLabel — right-align instead of center

**File:** `src/visualizer/views/hud.py`

Replace the entire `HeapPhaseLabel` class (lines 80–109):

```python
class HeapPhaseLabel:
    """Heap Sort phase label (BUILD MAX-HEAP / EXTRACTION) centered horizontally.

    The caller passes label_y so the Controller can position it relative to
    the tree root node (doc 04 §4.3.2, D-075).
    """

    def __init__(
        self,
        panel_rect: pygame.Rect,
        body_font: pygame.font.Font,
    ) -> None:
        self._font = body_font
        self._center_x: int = panel_rect.centerx

    @property
    def center_x(self) -> int:
        """Horizontal center used for text centering (panel.centerx)."""
        return self._center_x

    def draw(
        self,
        surface: pygame.Surface,
        phase: str,
        label_y: float,
    ) -> None:
        """Draw phase label centered horizontally in panel at label_y."""
        text_surf = self._font.render(phase, True, PHASE_LABEL_COLOR)
        x = self._center_x - text_surf.get_width() // 2
        surface.blit(text_surf, (x, round(label_y)))
```

With:

```python
class HeapPhaseLabel:
    """Heap Sort phase label (BUILD MAX-HEAP / EXTRACTION) right-aligned in panel.

    The caller passes label_y so the Controller can position it relative to
    the tree root node (doc 04 §4.3.2, D-075).
    """

    _RIGHT_MARGIN: int = 15  # px inset from panel right edge

    def __init__(
        self,
        panel_rect: pygame.Rect,
        body_font: pygame.font.Font,
    ) -> None:
        self._font = body_font
        self._right_x: int = panel_rect.right - self._RIGHT_MARGIN

    @property
    def right_x(self) -> int:
        """Right edge x used for text alignment (panel.right - margin)."""
        return self._right_x

    def draw(
        self,
        surface: pygame.Surface,
        phase: str,
        label_y: float,
    ) -> None:
        """Draw phase label right-aligned in panel at label_y."""
        text_surf = self._font.render(phase, True, PHASE_LABEL_COLOR)
        x = self._right_x - text_surf.get_width()
        surface.blit(text_surf, (x, round(label_y)))
```

Key changes:
- `_center_x` → `_right_x` (computed as `panel_rect.right - 15`)
- `center_x` property → `right_x` property
- `draw()` x-calculation: `self._right_x - text_surf.get_width()` (right-aligned instead of centered)
- Docstrings updated to say "right-aligned"

### §2 HeapOverlay.draw_over() — update label_y calculation

**File:** `src/visualizer/views/sprite_manager.py`

In `draw_over()`, replace the phase label block:

```python
        if self._phase is not None:
            root_clearance = self._tree_layout.tree_node_radius + 8
            label_y = self._tree_layout.tree_top - root_clearance
            self._phase_label.draw(surface, self._phase, label_y)
```

With:

```python
        if self._phase is not None:
            label_y = self._tree_layout.tree_top
            self._phase_label.draw(surface, self._phase, label_y)
```

The label is now right-aligned (handled by HeapPhaseLabel), so the `root_clearance` calculation is no longer needed. `label_y = tree_top` positions the text top at the root node center height — since the label is horizontally separated from the root node, this vertical alignment looks natural without any overlap risk.

### §3 Update test — property rename

**File:** `tests/unit/test_hud.py`

Replace:

```python
@pytest.mark.unit
def test_heap_phase_label_center_x_uses_panel_center(heap_phase_label: HeapPhaseLabel) -> None:
    assert heap_phase_label.center_x == DESKTOP_RECT.centerx
```

With:

```python
@pytest.mark.unit
def test_heap_phase_label_right_x_uses_panel_right(heap_phase_label: HeapPhaseLabel) -> None:
    assert heap_phase_label.right_x == DESKTOP_RECT.right - 15
```

### §4 What NOT to change

1. **Do NOT modify HeapBoundaryLabel** in `hud.py` — unchanged.
2. **Do NOT modify tree_layout.py** — all geometry correct.
3. **Do NOT modify main.py** — no call-site changes needed (HeapPhaseLabel constructor signature is unchanged).
4. **Do NOT modify any other overlay class** (BubbleOverlay, SelectionOverlay, InsertionOverlay).
5. **Do NOT modify orchestrator.py or any model file.**
6. **Do NOT touch the boundary label section or `reset()` method in HeapOverlay** — these were already restored after the 10d truncation.

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

Append a post-action entry to `DEVLOG.md` immediately after the 10d-fix pre-action entry:

```markdown
---

### 2026-05-08 — 10d-fix closed: Phase label repositioned to upper-right (Issue #1)

**Worked on**

[Describe: HeapPhaseLabel right-aligned (hud.py), draw_over label_y simplified (sprite_manager.py), test updated. Note the file truncation was already restored before this prompt.]

**Corrections**

[List any ruff/format corrections, or "Zero corrections" if clean on first run.]

**Results**

- `uv run ruff check src/ tests/`: **[clean/N issues]**
- `uv run ruff format --check src/ tests/`: **[clean/N issues]**
- `uv run pytest -x`: **345/345 PASSED** (no regressions)
- Import check: **[PASS/FAIL]**

**Verification note**

Manual visual verification deferred to Steven — check with default array:
- Phase label ("BUILD MAX-HEAP" / "EXTRACTION") positioned in upper-right of tree area
- Label does NOT overlap root node or any tree nodes
- Label disappears on sort completion (green state) — confirmed by 10d fix
- Restart (R) restores "BUILD MAX-HEAP" label correctly in upper-right position

**Next**

Proceed to 10e (Selection Sort pointer spacing — Issue #4).
```

---

## Context Files to Read

Read these files before writing any code:

1. `CLAUDE.md` — Critical Rules
2. `src/visualizer/views/hud.py` — HeapPhaseLabel class (lines 80–109)
3. `src/visualizer/views/sprite_manager.py` — HeapOverlay.draw_over() method (lines 1007–1012)
4. `tests/unit/test_hud.py` — HeapPhaseLabel tests (lines 159–198)
5. `DEVLOG.md` — Active working journal (append pre/post entries at end)
