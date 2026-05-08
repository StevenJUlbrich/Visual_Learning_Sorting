# Phase 10i — Move Selection Sort `i` Pointer Below j/min Tier (Issue #4 continued)

**Model:** Sonnet 4.6
**Context:** Phases 10e and 10h improved the `i` pointer (larger cyan arrow, 12px gap from ring), but the pointer is ABOVE the baseline and collides with the panel header counters (Comparisons/Swaps). The `i` label top (~y=92) touches the header bottom (~y=92). Moving `i` below the sprites, underneath the `j`/`min` tier, eliminates the collision entirely and keeps all three pointers clearly visible with vertical separation.

**Pre-execution note:** `pointer.py` and `test_pointer.py` were both found truncated again (same pattern as before 10e). **Both have been manually restored from git.** The current files are complete and parse correctly.

**Fix:** Reposition `i` pointer from ABOVE baseline to BELOW `j`/`min` tier. Change `i_arrow_y()` to compute position below the `j`/`min` label bottom. Flip `_draw_i_pointer` from downward-pointing to upward-pointing triangle with label below. Update docstrings, constants, and tests.

**Layout after fix (top to bottom):**
- Panel header (title, counters, message)
- (clear space)
- Sprite rings on baseline
- 5px gap (JMIN_ARROW_GAP)
- j/min upward arrows + labels (~34px)
- 8px gap (I_ARROW_GAP, reduced from 12)
- i upward arrow + label (~38px)
- ~39px clearance to panel bottom

**Out of scope:**
- Algorithm generators, contracts, orchestrator (unchanged)
- All overlays in sprite_manager.py (unchanged)
- main.py, hud.py, tree_layout.py, limitline.py (unchanged)
- `j` and `min` pointer appearance (unchanged)
- `POINTER_I_COLOR` — stays cyan `(80, 200, 220)` from 10h
- `I_ARROW_HEIGHT`/`I_ARROW_HALF_WIDTH` — stay 16/7 from 10h

---

## STEP 1 — DEVLOG PRE-ACTION

Append the following entry to `DEVLOG.md` (at the end of the file):

```markdown
---

### 2026-05-08 — 10i pre-action: Move `i` pointer below j/min tier (Issue #4 continued)

**Problem:** `i` pointer above baseline collides with panel header counters. Label top (~y=92) touches header bottom (~y=92). Despite 10e gap increase and 10h size/color improvements, the above-baseline position has no room.

**Plan:** Two files changed:
1. `pointer.py` — Update module + class docstrings. Change `I_ARROW_GAP` from 12 to 8 (now means spacing below j/min labels, not above ring). Rewrite `i_arrow_y()` to position below j/min tier using font height. Flip `_draw_i_pointer` to upward triangle with label below (same orientation as j/min).
2. `test_pointer.py` — Update imports (add `JMIN_ARROW_HEIGHT`, `LABEL_GAP`). Rename `test_i_arrow_y_above_baseline` → `test_i_arrow_y_below_jmin`. Update `test_i_arrow_y_formula` to match new formula (add `body_font` parameter).

**Exit criteria:**
1. `uv run ruff check src/ tests/` — clean
2. `uv run ruff format --check src/ tests/` — clean
3. `uv run pytest -x` — 345/345 (tests updated, no regressions)
4. Import check — OK
```

---

## STEP 2 — IMPLEMENTATION

### §1 Update module docstring

**File:** `src/visualizer/views/pointer.py`

Replace:

```python
"""Selection Sort pointer arrow geometry and rendering.

Three labeled pointer arrows for Selection Sort:
  i   — downward triangle ABOVE baseline, marks sorted boundary
  j   — upward triangle BELOW baseline, marks scan cursor
  min — upward triangle BELOW baseline, marks minimum tracker

Coalescing (D-068): when j and min occupy the same slot, only min is shown.

See doc 05 §4.2, D-068.
"""
```

With:

```python
"""Selection Sort pointer arrow geometry and rendering.

Three labeled pointer arrows for Selection Sort:
  i   — upward triangle BELOW j/min tier, marks sorted boundary (cyan)
  j   — upward triangle BELOW baseline, marks scan cursor (orange)
  min — upward triangle BELOW baseline, marks minimum tracker (orange)

All three pointers are below the baseline. j and min sit close to the sprite
rings; i sits further below with vertical spacing to keep labels readable.

Coalescing (D-068): when j and min occupy the same slot, only min is shown.

See doc 05 §4.2, D-068.
"""
```

### §2 Update class docstring

**File:** `src/visualizer/views/pointer.py`

Replace:

```python
    """Manages the three Selection Sort pointer arrows (i, j, min).

    Arrow rendering:
    - i: downward triangle ABOVE baseline; label above arrow
    - j, min: upward triangles BELOW baseline; labels below arrows

    Coalescing (D-068): j is hidden when j_index == min_index.
    """
```

With:

```python
    """Manages the three Selection Sort pointer arrows (i, j, min).

    Arrow rendering (all below baseline):
    - j, min: upward triangles close to rings; labels below arrows (orange)
    - i: upward triangle below j/min tier; label below arrow (cyan)

    Coalescing (D-068): j is hidden when j_index == min_index.
    """
```

### §3 Change `I_ARROW_GAP` value and comment

**File:** `src/visualizer/views/pointer.py`

Replace:

```python
I_ARROW_GAP: int = 12  # clearance between ring edge and i-pointer tip (above)
```

With:

```python
I_ARROW_GAP: int = 8  # clearance between j/min label bottom and i-pointer tip
```

### §4 Rewrite `i_arrow_y()` to position below j/min tier

**File:** `src/visualizer/views/pointer.py`

Replace:

```python
    def i_arrow_y(self) -> float:
        """Tip y for the i pointer arrow (above baseline, tip points toward ring)."""
        return self._home_y - self._ring_radius - I_ARROW_GAP
```

With:

```python
    def i_arrow_y(self) -> float:
        """Tip y for the i pointer arrow (below j/min tier, tip points upward)."""
        jmin_label_bottom = (
            self.jmin_arrow_y()
            + JMIN_ARROW_HEIGHT
            + LABEL_GAP
            + self._body_font.get_height()
        )
        return jmin_label_bottom + I_ARROW_GAP
```

### §5 Flip `_draw_i_pointer` to upward triangle with label below

**File:** `src/visualizer/views/pointer.py`

Replace:

```python
    def _draw_i_pointer(self, surface: pygame.Surface, slot_index: int) -> None:
        cx = self.slot_center_x(slot_index)
        tip_y = self.i_arrow_y()
        base_y = tip_y - I_ARROW_HEIGHT
        points: list[tuple[int, int]] = [
            (round(cx), round(tip_y)),
            (round(cx - I_ARROW_HALF_WIDTH), round(base_y)),
            (round(cx + I_ARROW_HALF_WIDTH), round(base_y)),
        ]
        pygame.draw.polygon(surface, POINTER_I_COLOR, points)
        label_surf = self._body_font.render("i", True, POINTER_I_COLOR)
        label_rect = label_surf.get_rect()
        label_rect.centerx = round(cx)
        label_rect.bottom = round(base_y) - LABEL_GAP
        surface.blit(label_surf, label_rect)
```

With:

```python
    def _draw_i_pointer(self, surface: pygame.Surface, slot_index: int) -> None:
        cx = self.slot_center_x(slot_index)
        tip_y = self.i_arrow_y()
        base_y = tip_y + I_ARROW_HEIGHT
        points: list[tuple[int, int]] = [
            (round(cx), round(tip_y)),
            (round(cx - I_ARROW_HALF_WIDTH), round(base_y)),
            (round(cx + I_ARROW_HALF_WIDTH), round(base_y)),
        ]
        pygame.draw.polygon(surface, POINTER_I_COLOR, points)
        label_surf = self._body_font.render("i", True, POINTER_I_COLOR)
        label_rect = label_surf.get_rect()
        label_rect.centerx = round(cx)
        label_rect.top = round(base_y) + LABEL_GAP
        surface.blit(label_surf, label_rect)
```

### §6 Update test imports

**File:** `tests/unit/test_pointer.py`

Replace:

```python
from visualizer.views.pointer import (
    I_ARROW_GAP,
    JMIN_ARROW_GAP,
    POINTER_I_COLOR,
    POINTER_J_COLOR,
    POINTER_MIN_COLOR,
    PointerSet,
)
```

With:

```python
from visualizer.views.pointer import (
    I_ARROW_GAP,
    JMIN_ARROW_GAP,
    JMIN_ARROW_HEIGHT,
    LABEL_GAP,
    POINTER_I_COLOR,
    POINTER_J_COLOR,
    POINTER_MIN_COLOR,
    PointerSet,
)
```

### §7 Update `test_i_arrow_y_above_baseline` → position test

**File:** `tests/unit/test_pointer.py`

Replace:

```python
@pytest.mark.unit
def test_i_arrow_y_above_baseline(pointer_set: PointerSet) -> None:
    assert pointer_set.i_arrow_y() < HOME_Y
```

With:

```python
@pytest.mark.unit
def test_i_arrow_y_below_jmin(pointer_set: PointerSet) -> None:
    assert pointer_set.i_arrow_y() > pointer_set.jmin_arrow_y()
```

### §8 Update `test_i_arrow_y_formula`

**File:** `tests/unit/test_pointer.py`

Replace:

```python
@pytest.mark.unit
def test_i_arrow_y_formula(pointer_set: PointerSet) -> None:
    expected = HOME_Y - RING_RADIUS - I_ARROW_GAP
    assert pointer_set.i_arrow_y() == pytest.approx(expected)
```

With:

```python
@pytest.mark.unit
def test_i_arrow_y_formula(
    pointer_set: PointerSet, body_font: pygame.font.Font
) -> None:
    jmin_tip = HOME_Y + RING_RADIUS + JMIN_ARROW_GAP
    jmin_label_bottom = jmin_tip + JMIN_ARROW_HEIGHT + LABEL_GAP + body_font.get_height()
    expected = jmin_label_bottom + I_ARROW_GAP
    assert pointer_set.i_arrow_y() == pytest.approx(expected)
```

### §9 What NOT to change

1. **Do NOT modify any algorithm generator, orchestrator, or model file.**
2. **Do NOT modify sprite_manager.py** — SelectionOverlay calls `pointer_set.draw()` unchanged.
3. **Do NOT modify main.py** — PointerSet constructor call unchanged.
4. **Do NOT change `POINTER_I_COLOR`** — stays cyan `(80, 200, 220)` from 10h.
5. **Do NOT change `I_ARROW_HEIGHT` or `I_ARROW_HALF_WIDTH`** — stay 16/7 from 10h.
6. **Do NOT change `JMIN_ARROW_GAP`, `JMIN_ARROW_HEIGHT`, `JMIN_ARROW_HALF_WIDTH`, or `LABEL_GAP`** — these are correct.
7. **Do NOT change `_draw_jmin_pointer`** — j/min rendering is unchanged.
8. **Do NOT change `jmin_arrow_y()`** — j/min position is unchanged.
9. **Do NOT change any test other than the two position tests and the import block.**

---

## STEP 3 — GATES

Run all four in sequence. All must pass. Fix any issues before proceeding.

```bash
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run pytest -x
python -c "from visualizer.views.pointer import PointerSet; print('OK')"
```

---

## STEP 4 — DEVLOG POST-ACTION

Append a post-action entry to `DEVLOG.md` immediately after the 10i pre-action entry:

```markdown
---

### 2026-05-08 — 10i closed: `i` pointer moved below j/min tier (Issue #4)

**Worked on**

[Describe: i_arrow_y() rewritten to position below j/min label bottom using font height. _draw_i_pointer flipped from downward to upward triangle, label below arrow. I_ARROW_GAP reduced from 12 to 8 (now means spacing between j/min labels and i tip). Module + class docstrings updated. Two tests updated: position test asserts i_arrow_y > jmin_arrow_y, formula test uses new computation with body_font.get_height().]

**Corrections**

[List any ruff/format corrections, or "Zero corrections" if clean on first run.]

**Results**

- `uv run ruff check src/ tests/`: **[clean/N issues]**
- `uv run ruff format --check src/ tests/`: **[clean/N issues]**
- `uv run pytest -x`: **345/345 PASSED** (no regressions)
- Import check: **[PASS/FAIL]**

**Verification note**

Manual visual verification deferred to Steven:
- `i` pointer is now a cyan upward triangle BELOW the j/min pointers
- `i` label ("i") visible in cyan below the arrow
- `j` and `min` labels fully readable (no overlap from i)
- Panel header counters have clear space above sprites (no collision)
- Coalescing (D-068) still works: when j == min, only min shown
- All three pointers point upward toward the sprite rings

**Next**

Visual verification of all Phase 10 pointer/boundary fixes (10e, 10g, 10h, 10i). Phase 10 closeout if no further issues.
```

---

## Context Files to Read

Read these files before writing any code:

1. `CLAUDE.md` — Critical Rules
2. `src/visualizer/views/pointer.py` — Full file (module docstring, constants, PointerSet class)
3. `tests/unit/test_pointer.py` — Import block, position tests, formula tests
4. `DEVLOG.md` — Active working journal (append pre/post entries at end)
