# Phase 10h — Selection Sort `i` Pointer Visibility (Issue #4 continued)

**Model:** Sonnet 4.6
**Context:** Phase 10e increased the `i` pointer gap from 5px to 12px, but the pointer is still nearly invisible. Two problems remain: (a) the arrow is too small (12px height, 5px half-width) — it's a tiny triangle that gets lost, and (b) the color is `PRIMARY_TEXT` `(240, 240, 245)` — light gray that blends into the dark background. The `j` and `min` pointers are clearly visible because they're orange `(255, 140, 0)`.

**Fix:** Make the `i` pointer larger (16px height, 7px half-width) and change its color to cyan `(80, 200, 220)` — a cool tone that contrasts with both the dark background and the warm orange of `j`/`min`, reinforcing the semantic difference (sorted boundary vs. scan cursor).

**Out of scope:**
- Algorithm generators, contracts, orchestrator (unchanged)
- All overlays in sprite_manager.py (unchanged)
- main.py, hud.py, tree_layout.py, limitline.py (unchanged)
- `j` and `min` pointer appearance (unchanged — keep 12px height, 5px half-width, orange)

---

## STEP 1 — DEVLOG PRE-ACTION

Append the following entry to `DEVLOG.md` (at the end of the file):

```markdown
---

### 2026-05-08 — 10h pre-action: `i` pointer visibility — bigger arrow + cyan color (Issue #4 continued)

**Problem:** 10e increased gap but `i` pointer still nearly invisible. Arrow too small (12×5) and color too faint (light gray blends into background).

**Plan:** Two files changed:
1. `pointer.py` — Add `I_ARROW_HEIGHT = 16`, `I_ARROW_HALF_WIDTH = 7`. Change `POINTER_I_COLOR` from `PRIMARY_TEXT` to `(80, 200, 220)` (cyan). Rename shared `ARROW_HEIGHT`/`ARROW_HALF_WIDTH` to `JMIN_ARROW_HEIGHT`/`JMIN_ARROW_HALF_WIDTH`. Update `_draw_i_pointer` to use `I_` constants. Update `_draw_jmin_pointer` to use `JMIN_` constants.
2. `test_pointer.py` — Update color assertion from `(240, 240, 245)` to `(80, 200, 220)`.

**Exit criteria:**
1. `uv run ruff check src/ tests/` — clean
2. `uv run ruff format --check src/ tests/` — clean
3. `uv run pytest -x` — 345/345 (one test assertion updated, no regressions)
4. Import check — OK
```

---

## STEP 2 — IMPLEMENTATION

### §1 Split arrow geometry constants and change `i` color

**File:** `src/visualizer/views/pointer.py`

Replace the arrow geometry constants block AND the pointer colors block:

```python
# ---------------------------------------------------------------------------
# Arrow geometry constants
# ---------------------------------------------------------------------------

ARROW_HEIGHT: int = 12
ARROW_HALF_WIDTH: int = 5
I_ARROW_GAP: int = 12  # clearance between ring edge and i-pointer tip (above)
JMIN_ARROW_GAP: int = 5  # clearance between ring edge and j/min-pointer tip (below)
LABEL_GAP: int = 2  # gap between arrow base and label text

# ---------------------------------------------------------------------------
# Pointer colors
# ---------------------------------------------------------------------------

POINTER_I_COLOR: tuple[int, int, int] = PRIMARY_TEXT  # (240, 240, 245)
POINTER_J_COLOR: tuple[int, int, int] = COLOR_MAP[ColorState.ACTIVE]  # (255, 140, 0)
POINTER_MIN_COLOR: tuple[int, int, int] = COLOR_MAP[ColorState.ACTIVE]  # (255, 140, 0)
```

With:

```python
# ---------------------------------------------------------------------------
# Arrow geometry constants
# ---------------------------------------------------------------------------

I_ARROW_HEIGHT: int = 16
I_ARROW_HALF_WIDTH: int = 7
JMIN_ARROW_HEIGHT: int = 12
JMIN_ARROW_HALF_WIDTH: int = 5
I_ARROW_GAP: int = 12  # clearance between ring edge and i-pointer tip (above)
JMIN_ARROW_GAP: int = 5  # clearance between ring edge and j/min-pointer tip (below)
LABEL_GAP: int = 2  # gap between arrow base and label text

# ---------------------------------------------------------------------------
# Pointer colors
# ---------------------------------------------------------------------------

POINTER_I_COLOR: tuple[int, int, int] = (80, 200, 220)  # cyan — sorted boundary
POINTER_J_COLOR: tuple[int, int, int] = COLOR_MAP[ColorState.ACTIVE]  # (255, 140, 0)
POINTER_MIN_COLOR: tuple[int, int, int] = COLOR_MAP[ColorState.ACTIVE]  # (255, 140, 0)
```

After this change, the `PRIMARY_TEXT` import on line 17 is unused. Remove it:

Replace:

```python
from visualizer.views.panel import PRIMARY_TEXT
```

With:

```python
```

(Delete the line entirely.)

### §2 Update `_draw_i_pointer` to use `I_` constants

**File:** `src/visualizer/views/pointer.py`

Replace:

```python
    def _draw_i_pointer(self, surface: pygame.Surface, slot_index: int) -> None:
        cx = self.slot_center_x(slot_index)
        tip_y = self.i_arrow_y()
        base_y = tip_y - ARROW_HEIGHT
        points: list[tuple[int, int]] = [
            (round(cx), round(tip_y)),
            (round(cx - ARROW_HALF_WIDTH), round(base_y)),
            (round(cx + ARROW_HALF_WIDTH), round(base_y)),
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

### §3 Update `_draw_jmin_pointer` to use `JMIN_` constants

**File:** `src/visualizer/views/pointer.py`

Replace:

```python
    def _draw_jmin_pointer(
        self,
        surface: pygame.Surface,
        slot_index: int,
        label: str,
        color: tuple[int, int, int],
    ) -> None:
        cx = self.slot_center_x(slot_index)
        tip_y = self.jmin_arrow_y()
        base_y = tip_y + ARROW_HEIGHT
        points: list[tuple[int, int]] = [
            (round(cx), round(tip_y)),
            (round(cx - ARROW_HALF_WIDTH), round(base_y)),
            (round(cx + ARROW_HALF_WIDTH), round(base_y)),
        ]
        pygame.draw.polygon(surface, color, points)
        label_surf = self._body_font.render(label, True, color)
        label_rect = label_surf.get_rect()
        label_rect.centerx = round(cx)
        label_rect.top = round(base_y) + LABEL_GAP
        surface.blit(label_surf, label_rect)
```

With:

```python
    def _draw_jmin_pointer(
        self,
        surface: pygame.Surface,
        slot_index: int,
        label: str,
        color: tuple[int, int, int],
    ) -> None:
        cx = self.slot_center_x(slot_index)
        tip_y = self.jmin_arrow_y()
        base_y = tip_y + JMIN_ARROW_HEIGHT
        points: list[tuple[int, int]] = [
            (round(cx), round(tip_y)),
            (round(cx - JMIN_ARROW_HALF_WIDTH), round(base_y)),
            (round(cx + JMIN_ARROW_HALF_WIDTH), round(base_y)),
        ]
        pygame.draw.polygon(surface, color, points)
        label_surf = self._body_font.render(label, True, color)
        label_rect = label_surf.get_rect()
        label_rect.centerx = round(cx)
        label_rect.top = round(base_y) + LABEL_GAP
        surface.blit(label_surf, label_rect)
```

### §4 Update color test

**File:** `tests/unit/test_pointer.py`

Replace:

```python
@pytest.mark.unit
def test_pointer_i_color_is_primary_text() -> None:
    assert POINTER_I_COLOR == (240, 240, 245)
```

With:

```python
@pytest.mark.unit
def test_pointer_i_color_is_cyan() -> None:
    assert POINTER_I_COLOR == (80, 200, 220)
```

### §5 What NOT to change

1. **Do NOT modify any algorithm generator, orchestrator, or model file.**
2. **Do NOT modify sprite_manager.py** — SelectionOverlay calls `pointer_set.draw()` unchanged.
3. **Do NOT modify main.py** — PointerSet constructor call unchanged.
4. **Do NOT change `POINTER_J_COLOR` or `POINTER_MIN_COLOR`** — orange is correct for scan pointers.
5. **Do NOT change `I_ARROW_GAP`, `JMIN_ARROW_GAP`, or `LABEL_GAP`** — these are correct from 10e.
6. **Do NOT change `i_arrow_y()` or `jmin_arrow_y()`** — gap calculations are correct from 10e.
7. **Do NOT change any test other than the color assertion.**

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

Append a post-action entry to `DEVLOG.md` immediately after the 10h pre-action entry:

```markdown
---

### 2026-05-08 — 10h closed: `i` pointer visibility — bigger arrow + cyan color (Issue #4)

**Worked on**

[Describe: ARROW_HEIGHT/ARROW_HALF_WIDTH split into I_ (16/7) and JMIN_ (12/5) variants. POINTER_I_COLOR changed from PRIMARY_TEXT (240,240,245) to cyan (80,200,220). Unused PRIMARY_TEXT import removed. _draw_i_pointer and _draw_jmin_pointer updated to use respective constants. Color test updated.]

**Corrections**

[List any ruff/format corrections, or "Zero corrections" if clean on first run.]

**Results**

- `uv run ruff check src/ tests/`: **[clean/N issues]**
- `uv run ruff format --check src/ tests/`: **[clean/N issues]**
- `uv run pytest -x`: **345/345 PASSED** (no regressions)
- Import check: **[PASS/FAIL]**

**Verification note**

Manual visual verification deferred to Steven:
- `i` pointer is now a larger cyan triangle, clearly visible above sprite rings
- `i` label text is cyan, readable against dark background
- `j` and `min` pointers unchanged (orange, same size as before)
- Coalescing (D-068) still works: when j == min, only min shown
- Sorted boundary semantic is visually distinct from scan cursor

**Next**

All Phase 10 issues resolved. Proceed to Phase 10 closeout.
```

---

## Context Files to Read

Read these files before writing any code:

1. `CLAUDE.md` — Critical Rules
2. `src/visualizer/views/pointer.py` — Constants (lines 23–36), `_draw_i_pointer` (lines 110–124), `_draw_jmin_pointer` (lines 126–144)
3. `tests/unit/test_pointer.py` — Color test (line 165–166)
4. `DEVLOG.md` — Active working journal (append pre/post entries at end)
