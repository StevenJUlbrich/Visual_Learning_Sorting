# Phase 10g — Hide Bubble Sort Boundary Line on Completion (Issue #11)

**Model:** Sonnet 4.6
**Context:** The Bubble Sort boundary line (vertical dashed line marking sorted/unsorted boundary) persists after sort completion. `LimitLine.draw()` has a visibility check (`is_visible` = `0 < boundary_index < array_size`), but the boundary doesn't reach 0 on completion — Bubble Sort terminates when a pass completes with no swaps, at which point the boundary may still be mid-array. The line should disappear on TERMINAL, matching how Heap Sort hides its phase label on completion.

**Fix:** Add `_sort_complete: bool` flag to `BubbleOverlay`. Set it True on TERMINAL. Gate the limit line draw call on `not self._sort_complete`. Reset the flag in `reset()`.

**Out of scope:**
- Algorithm generators, contracts, orchestrator (unchanged)
- LimitLine class in limitline.py (unchanged — its own visibility logic is correct)
- Other overlays (SelectionOverlay, InsertionOverlay, HeapOverlay)
- main.py, hud.py, pointer.py, tree_layout.py (unchanged)
- No test changes — BubbleOverlay is visual-only with no unit tests

---

## STEP 1 — DEVLOG PRE-ACTION

Append the following entry to `DEVLOG.md` (at the end of the file):

```markdown
---

### 2026-05-08 — 10g pre-action: Hide Bubble Sort boundary line on completion (Issue #11)

**Problem:** Bubble Sort boundary line (LimitLine) persists after sort completion. The line's `is_visible` check relies on `boundary_index` reaching 0, but Bubble Sort terminates when a pass has no swaps — the boundary may still be mid-array.

**Plan:** One file changed (`sprite_manager.py`):
1. Add `_sort_complete: bool = False` to BubbleOverlay.__init__.
2. Set `self._sort_complete = True` on TERMINAL in `_process_tick()`.
3. Gate limit line draw: `if not self._sort_complete:` before `self._limit_line.draw(surface)` in `draw()`.
4. Reset flag in `reset()`.

**Exit criteria:**
1. `uv run ruff check src/ tests/` — clean
2. `uv run ruff format --check src/ tests/` — clean
3. `uv run pytest -x` — 345/345 (no test changes, no regressions)
4. Import check — OK
```

---

## STEP 2 — IMPLEMENTATION

### §1 Add `_sort_complete` flag to BubbleOverlay

**File:** `src/visualizer/views/sprite_manager.py`

In `BubbleOverlay.__init__`, after `self._pointer_color` (around line 805), add the flag:

Replace:

```python
        self._pointer_color: tuple[int, int, int] = (80, 220, 120)
```

With:

```python
        self._pointer_color: tuple[int, int, int] = (80, 220, 120)
        self._sort_complete: bool = False
```

### §2 Set flag on TERMINAL

**File:** `src/visualizer/views/sprite_manager.py`

In `BubbleOverlay._process_tick()`, update the TERMINAL handler:

Replace:

```python
        elif op in (OpType.TERMINAL, OpType.FAILURE):
            self._pointer_visible = False
```

With:

```python
        elif op in (OpType.TERMINAL, OpType.FAILURE):
            self._pointer_visible = False
            self._sort_complete = True
```

### §3 Gate limit line draw

**File:** `src/visualizer/views/sprite_manager.py`

In `BubbleOverlay.draw()`, gate the limit line:

Replace:

```python
    def draw(self, surface: pygame.Surface, comparisons: int, writes: int) -> None:
        self._limit_line.draw(surface)
        self._bubble_hud.draw(surface, comparisons, writes // 2)
```

With:

```python
    def draw(self, surface: pygame.Surface, comparisons: int, writes: int) -> None:
        if not self._sort_complete:
            self._limit_line.draw(surface)
        self._bubble_hud.draw(surface, comparisons, writes // 2)
```

### §4 Reset flag in `reset()`

**File:** `src/visualizer/views/sprite_manager.py`

In `BubbleOverlay.reset()`:

Replace:

```python
    def reset(self) -> None:
        self._last_tick = None
        self._j = -1
        self._pointer_visible = False
        self._limit_line.reset()
```

With:

```python
    def reset(self) -> None:
        self._last_tick = None
        self._j = -1
        self._pointer_visible = False
        self._sort_complete = False
        self._limit_line.reset()
```

### §5 What NOT to change

1. **Do NOT modify LimitLine** in `limitline.py` — its visibility logic is correct.
2. **Do NOT modify any algorithm generator, orchestrator, or model file.**
3. **Do NOT modify any other overlay class.**
4. **Do NOT modify any test file.**

---

## STEP 3 — GATES

Run all four in sequence. All must pass. Fix any issues before proceeding.

```bash
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run pytest -x
python -c "from visualizer.views.sprite_manager import BubbleOverlay; print('OK')"
```

---

## STEP 4 — DEVLOG POST-ACTION

Append a post-action entry to `DEVLOG.md` immediately after the 10g pre-action entry:

```markdown
---

### 2026-05-08 — 10g closed: Bubble Sort boundary line hidden on completion (Issue #11)

**Worked on**

[Describe: Added `_sort_complete` flag to BubbleOverlay, set True on TERMINAL, gates limit line draw. Reset in reset().]

**Corrections**

[List any ruff/format corrections, or "Zero corrections" if clean on first run.]

**Results**

- `uv run ruff check src/ tests/`: **[clean/N issues]**
- `uv run ruff format --check src/ tests/`: **[clean/N issues]**
- `uv run pytest -x`: **345/345 PASSED** (no regressions)
- Import check: **[PASS/FAIL]**

**Verification note**

Manual visual verification deferred to Steven:
- Boundary line visible during sorting, advances leftward each pass
- Boundary line disappears when sort completes (green state)
- Comparison pointer (green triangle) still disappears on completion
- Counters (Comparisons/Exchanges) still visible on completion
- Restart (R) restores boundary line correctly

**Next**

Update issue register. Proceed to Phase 10 closeout if no further issues found.
```

---

## Context Files to Read

Read these files before writing any code:

1. `CLAUDE.md` — Critical Rules
2. `src/visualizer/views/sprite_manager.py` — BubbleOverlay class (lines 780–853)
3. `DEVLOG.md` — Active working journal (append pre/post entries at end)
