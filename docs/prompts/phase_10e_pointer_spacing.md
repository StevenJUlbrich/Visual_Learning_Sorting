# Phase 10e — Selection Sort `i` Pointer Spacing (Issue #4)

**Model:** Sonnet 4.6
**Context:** The Selection Sort `i` pointer (downward triangle above the baseline) sits only 5px above the sprite ring (`ARROW_GAP = 5`). At desktop resolution the ring radius is ~25px, so the arrow tip is right at the ring edge — it gets visually lost against the sprite. The `j` and `min` pointers below the baseline are fine at 5px gap.

**Fix:** Introduce a separate `I_ARROW_GAP` constant (12px) for the `i` pointer, giving it comfortable clearance above the sprite ring. Keep `ARROW_GAP` at 5px for `j`/`min` pointers (rename to `JMIN_ARROW_GAP` for clarity). Update `i_arrow_y()` to use the new constant. Update the formula test to match.

**Pre-execution note:** `pointer.py` was found truncated at line 141 (last 3 lines of `_draw_jmin_pointer` missing). **This has already been manually restored.** The current file is complete and parses correctly.

**Out of scope:**
- Algorithm generators, contracts, orchestrator (unchanged)
- All overlays in sprite_manager.py (unchanged)
- main.py, hud.py, tree_layout.py (unchanged)
- No new tests — one existing test updated for the renamed constant

---

## STEP 1 — DEVLOG PRE-ACTION

Append the following entry to `DEVLOG.md` (at the end of the file):

```markdown
---

### 2026-05-08 — 10e pre-action: Selection Sort `i` pointer spacing (Issue #4)

**Plan:** Increase `i` pointer clearance from sprite ring. Three files changed:
1. `pointer.py` — Rename `ARROW_GAP` to `JMIN_ARROW_GAP` (stays 5px). Add `I_ARROW_GAP = 12`. Update `i_arrow_y()` to use `I_ARROW_GAP`. Update `jmin_arrow_y()` to use `JMIN_ARROW_GAP` (no behavioral change).
2. `test_pointer.py` — Update import: `ARROW_GAP` → `I_ARROW_GAP`, `JMIN_ARROW_GAP`. Update `test_i_arrow_y_formula` to use `I_ARROW_GAP`. Update `test_jmin_arrow_y_formula` to use `JMIN_ARROW_GAP`.

**Exit criteria:**
1. `uv run ruff check src/ tests/` — clean
2. `uv run ruff format --check src/ tests/` — clean
3. `uv run pytest -x` — 345/345 (test formula updated, no regressions)
4. Import check — OK
```

---

## STEP 2 — IMPLEMENTATION

### §1 Rename `ARROW_GAP` and add `I_ARROW_GAP`

**File:** `src/visualizer/views/pointer.py`

Replace the arrow geometry constants block:

```python
ARROW_HEIGHT: int = 12
ARROW_HALF_WIDTH: int = 5
ARROW_GAP: int = 5  # clearance between ring edge and arrow tip
LABEL_GAP: int = 2  # gap between arrow base and label text
```

With:

```python
ARROW_HEIGHT: int = 12
ARROW_HALF_WIDTH: int = 5
I_ARROW_GAP: int = 12  # clearance between ring edge and i-pointer tip (above)
JMIN_ARROW_GAP: int = 5  # clearance between ring edge and j/min-pointer tip (below)
LABEL_GAP: int = 2  # gap between arrow base and label text
```

### §2 Update `i_arrow_y()` and `jmin_arrow_y()`

**File:** `src/visualizer/views/pointer.py`

Replace:

```python
    def i_arrow_y(self) -> float:
        """Tip y for the i pointer arrow (above baseline, tip points toward ring)."""
        return self._home_y - self._ring_radius - ARROW_GAP

    def jmin_arrow_y(self) -> float:
        """Tip y for j and min pointer arrows (below baseline, tip points toward ring)."""
        return self._home_y + self._ring_radius + ARROW_GAP
```

With:

```python
    def i_arrow_y(self) -> float:
        """Tip y for the i pointer arrow (above baseline, tip points toward ring)."""
        return self._home_y - self._ring_radius - I_ARROW_GAP

    def jmin_arrow_y(self) -> float:
        """Tip y for j and min pointer arrows (below baseline, tip points toward ring)."""
        return self._home_y + self._ring_radius + JMIN_ARROW_GAP
```

### §3 Update test imports and formulas

**File:** `tests/unit/test_pointer.py`

Replace the import:

```python
from visualizer.views.pointer import (
    ARROW_GAP,
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
    POINTER_I_COLOR,
    POINTER_J_COLOR,
    POINTER_MIN_COLOR,
    PointerSet,
)
```

Replace the `i` arrow formula test:

```python
@pytest.mark.unit
def test_i_arrow_y_formula(pointer_set: PointerSet) -> None:
    expected = HOME_Y - RING_RADIUS - ARROW_GAP
    assert pointer_set.i_arrow_y() == pytest.approx(expected)
```

With:

```python
@pytest.mark.unit
def test_i_arrow_y_formula(pointer_set: PointerSet) -> None:
    expected = HOME_Y - RING_RADIUS - I_ARROW_GAP
    assert pointer_set.i_arrow_y() == pytest.approx(expected)
```

Replace the `jmin` arrow formula test:

```python
@pytest.mark.unit
def test_jmin_arrow_y_formula(pointer_set: PointerSet) -> None:
    expected = HOME_Y + RING_RADIUS + ARROW_GAP
    assert pointer_set.jmin_arrow_y() == pytest.approx(expected)
```

With:

```python
@pytest.mark.unit
def test_jmin_arrow_y_formula(pointer_set: PointerSet) -> None:
    expected = HOME_Y + RING_RADIUS + JMIN_ARROW_GAP
    assert pointer_set.jmin_arrow_y() == pytest.approx(expected)
```

### §4 What NOT to change

1. **Do NOT modify any algorithm generator, orchestrator, or model file.**
2. **Do NOT modify sprite_manager.py** — SelectionOverlay calls `pointer_set.draw()` which is unchanged.
3. **Do NOT modify main.py** — PointerSet constructor call is unchanged.
4. **Do NOT modify any other test file.** Only `test_pointer.py` changes.
5. **Do NOT change `ARROW_HEIGHT`, `ARROW_HALF_WIDTH`, or `LABEL_GAP`** — these are fine.
6. **Do NOT change `_draw_i_pointer` or `_draw_jmin_pointer`** — they use `i_arrow_y()` and `jmin_arrow_y()` which handle the gap internally.

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

Append a post-action entry to `DEVLOG.md` immediately after the 10e pre-action entry:

```markdown
---

### 2026-05-08 — 10e closed: Selection Sort `i` pointer spacing (Issue #4)

**Worked on**

[Describe: ARROW_GAP split into I_ARROW_GAP (12px) and JMIN_ARROW_GAP (5px). i_arrow_y() uses I_ARROW_GAP. Test formulas updated. pointer.py truncation was already restored before this prompt.]

**Corrections**

[List any ruff/format corrections, or "Zero corrections" if clean on first run.]

**Results**

- `uv run ruff check src/ tests/`: **[clean/N issues]**
- `uv run ruff format --check src/ tests/`: **[clean/N issues]**
- `uv run pytest -x`: **345/345 PASSED** (no regressions)
- Import check: **[PASS/FAIL]**

**Verification note**

Manual visual verification deferred to Steven:
- `i` pointer arrow has visible clearance above sprite rings (was 5px, now 12px)
- `j` and `min` pointers below sprites unchanged (still 5px gap)
- Pointer labels ("i", "j", "min") positioned correctly relative to their arrows
- Coalescing (D-068) still works: when j == min, only min shown

**Next**

All Phase 10 issues resolved. Update AT_READINESS_CHECKLIST.md and proceed to phase closeout.
```

---

## Context Files to Read

Read these files before writing any code:

1. `CLAUDE.md` — Critical Rules
2. `src/visualizer/views/pointer.py` — PointerSet class, arrow constants (lines 23–27), i_arrow_y/jmin_arrow_y (lines 72–78)
3. `tests/unit/test_pointer.py` — Import block (lines 12–18), formula tests (lines 57–66)
4. `DEVLOG.md` — Active working journal (append pre/post entries at end)
