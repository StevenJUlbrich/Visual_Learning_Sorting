# Phase 10 — Manual Acceptance Testing and Visual Bug Fixes

**Dates:** 2026-05-08
**Test count at entry:** 345/345 (339 original + 6 duplicate-value tests from 10c)
**Test count at exit:** 345/345 (no new tests; two pointer tests updated in-place)

---

### 2026-05-08 14:00 — 10a: Build Verification and Platform Testing

**Worked on:** Application launch and full-run verification on Windows 11 native (Dell 7770).

All four panels animate independently. Play/pause/step/restart all functional via keyboard (Space/Right/R/Escape). Counter accuracy confirmed against expected values:

| Algorithm | Cmp | Wr | Steps | Expected | Match |
|-----------|-----|-----|-------|----------|-------|
| Bubble Sort | 20 | 26 | — | 20/26 | ✓ |
| Selection Sort | 21 | 10 | — | 21/10 | ✓ |
| Insertion Sort | 17 | 19 | — | 17/19 | ✓ |
| Heap Sort | 20 | 30 | 35 | 20/30/35 | ✓ |

All four panels reach completion with green backgrounds and green sprites. Elapsed timers freeze correctly on completion.

**WSLg / Pygame limitation:** Pygame window displays under WSLg but keyboard input does not register. The event loop receives no KEYDOWN events — likely a WSLg compositor focus delivery issue. `clock.tick(60)` runs normally, sprites render correctly, but no interaction is possible. Workaround: run natively on Windows 11. Ubuntu 24 laptop testing deferred. No code changes needed.

---

### 2026-05-08 15:00 — 10b: Visual Acceptance Test Results

**Worked on:** Walked through AT-01 through AT-27 using `TODO/AT_READINESS_CHECKLIST.md`. Results marked with `[x]` (pass), `[p]` (partial), `[f]` (fail).

**Passing (no issues):** AT-01 (partial — Heap tree layout noted), AT-02, AT-03, AT-04, AT-05, AT-07, AT-09, AT-10, AT-11, AT-12, AT-13, AT-14, AT-15, AT-16, AT-17 (untested — requires config change), AT-18, AT-19, AT-20, AT-25, AT-26, AT-27.

**Issues found:** 7 active issues from visual testing across AT-08, AT-21, AT-22, AT-23, AT-24.

| # | Severity | AT | Description | Fix Phase |
|---|----------|-----|-------------|-----------|
| **7** | **CRITICAL** | AT-08 | `compute_sprite_moves()` fails with duplicate values — sprites in wrong positions | 10c |
| 8 | HIGH | AT-08/21 | Heap sorted-row vertical misalignment (likely downstream of #7) | verify after 10c |
| 3 | HIGH | AT-23 | Boundary marker crosses into Insertion Sort panel | 10d |
| 1 | MEDIUM | AT-22 | Phase label overlaps root node (both phases) | 10d |
| 9 | MEDIUM | AT-22 | EXTRACTION label persists after completion | 10d |
| 4 | MEDIUM | AT-24 | Selection Sort `i` pointer too close to sprites | 10e |
| 6 | LOW | AT-21/23 | Sorted-row placeholders visible during BUILD MAX-HEAP | 10d |

**Closed items:** Issue #5 (AT-27 colored dot) — confirmed not an issue. AT-21 completion green — confirmed not an issue.

**Decisions:**
- Fix #7 first, alone — foundational, affects all algorithms with duplicates. Issue #8 may auto-resolve.
- Opus for 10c, Sonnet for 10d/10e — match model to decision density, not code volume (same lesson as Phase 7c-4).
- Batch Heap visual fixes (#1, #3, #6, #9) into 10d — all touch HeapOverlay; separate prompts risk merge conflicts.
- Don't change SortResult contract — approach (A) uses existing `operation_type` + `highlight_indices`, minimal change surface.
- Verify #8 after #7 before writing a fix — avoid fixing a symptom when the cause is about to change.

**Next:** Execute 10c prompt (Opus — compute_sprite_moves duplicate fix).

---

### 2026-05-08 — 10c pre-action: Fix compute_sprite_moves() for duplicate values

**Plan:** Augment `compute_sprite_moves()` with `operation_type` and `highlight_indices` parameters (both optional, default `None`). When the existing value-delta detection finds zero changes but the tick is a SHIFT or SWAP with a 2-element `highlight_indices`, use the highlight data to determine which slots exchanged sprites. Existing logic unchanged for non-empty `changed` lists (backward compatible). Update call site in `Orchestrator.update()` to pass tick data. Add 6 new unit tests for duplicate-value cases. Existing 8 Group 13 tests and 7 integration tests must pass unchanged.

**Root cause:** `changed = [i for i in range(len(old_state)) if old_state[i] != new_state[i]]` produces an empty list when equal values shift or swap. The function returns `{}` — no sprite movement. Over a full sort with duplicates, sprites diverge from actual positions.

**Exit criteria:**
1. `uv run ruff check src/ tests/` — clean
2. `uv run ruff format --check src/ tests/` — clean
3. `uv run pytest -x` — all passing (339 existing + 6 new = 345)
4. Import check — OK
5. All existing tests pass WITHOUT modification to their call signatures

---

### 2026-05-08 — 10c closed: Fix compute_sprite_moves() for duplicate values

**Worked on:** Added `operation_type: OpType | None = None` and `highlight_indices: tuple[int, ...] | None = None` parameters to `compute_sprite_moves()` (orchestrator.py:87). When `changed` is empty AND `operation_type in (SWAP, SHIFT)` AND `highlight_indices` has exactly 2 elements, swaps the two slots in `slot_to_sprite_id` and returns `{sprite_a: j, sprite_b: i}`. Existing 1-change and 2-change paths untouched. Call site at `Orchestrator.update()` (line 274) forwards `tick.operation_type` and `tick.highlight_indices`. 6 new Group 13 tests added: duplicate SHIFT, duplicate SWAP, placement single-element guard, plus full-sort identity preservation for Insertion/Bubble/Heap on `[3, 1, 3, 2, 1, 2, 3]`.

**Corrections:** Zero corrections.

**Results:**
- `uv run ruff check src/ tests/`: **clean**
- `uv run ruff format --check src/ tests/`: **clean** (38 files)
- `uv run pytest -x`: **345/345 PASSED** (339 existing + 6 new)
- Import check: **OK**

**Visual verification (Steven, 2026-05-08):** Confirmed with duplicate array `[3, 1, 3, 2, 1, 2, 3]`. All four panels show `[1, 1, 2, 2, 3, 3, 3]` at completion. Insertion Sort correct (was `1, 2, 3, 1, 2, 3, 3`). Heap Sort sorted-row sprites all on same baseline — **Issue #8 resolved** by this fix (downstream effect confirmed). Both Issues #7 and #8 closed.

**Next:** Draft and execute 10d (Heap visual batch — Issues #1, #3, #6, #9) and 10e (pointer spacing — Issue #4).

---

### 2026-05-08 — 10d closed: Heap Sort visual fixes (Issues #3, #6, #9 fixed; Issue #1 partial)

**Worked on:** Four changes in HeapOverlay class (`sprite_manager.py`):
- §1: `panel_rect` parameter added to HeapOverlay constructor.
- §2: Phase label offset changed from static `_PHASE_LABEL_OFFSET = 20` to dynamic `tree_node_radius + 8`. Wrapped in `if self._phase is not None` guard.
- §3: Boundary marker and label clamped to panel rect bounds (skip drawing when outside).
- §4: Placeholders and boundary line gated on `self._phase == "EXTRACTION"`.
- §5: `self._phase = None` on TERMINAL/FAILURE.
- §6: Type annotation widened to `str | None`.
- §7: `main.py` call site passes `panel_rect=layout.panel_rects[3]`.
- §8: Removed unused `_PHASE_LABEL_OFFSET` constant.

**Corrections:** Zero corrections (ruff/format clean on first run).

**Results:**
- `uv run ruff check src/ tests/`: **clean**
- `uv run ruff format --check src/ tests/`: **clean**
- `uv run pytest -x`: **345/345 PASSED** (no regressions)
- Import check: **OK**

**Post-execution issue: File truncation.** The 10d execution truncated `sprite_manager.py` at line 1017 — the boundary label section of `draw_over()` and the entire `reset()` method were lost. Manually restored from `git show HEAD~1` reference. AST parse verified: all 9 HeapOverlay methods present.

**Visual verification (Steven, 2026-05-08):** Issues #3, #6, #9 confirmed fixed. **Issue #1 still present** — phase label ("BUILD MAX-HEAP" / "EXTRACTION") still overlaps root node. Root cause: `label_y` is the text TOP edge, but the text renders downward by ~18px (font_height), so the bottom of the label sits inside the root ring even with the `tree_node_radius + 8` offset.

**Decision:** Reposition the phase label to the upper-right of the tree area (Option B) rather than continuing to fight for vertical space above the root. This is a design improvement, not just a bug fix. Prompt drafted as `10d-fix`.

**Next:** Execute 10d-fix (label reposition), then 10e (pointer spacing — Issue #4).

---

### 2026-05-08 — 10d-fix closed: Phase label repositioned to upper-right (Issue #1)

**Worked on:** HeapPhaseLabel right-aligned (`hud.py`): `_center_x` → `_right_x = panel.right - 15`, `center_x` property → `right_x`, draw x = `_right_x - text_width`. HeapOverlay.draw_over() (`sprite_manager.py`): label_y simplified to `tree_top` — no vertical clearance math needed since the label is horizontally separated from the root node. Test updated (`test_hud.py`): property test renamed and assertion updated to `DESKTOP_RECT.right - 15`.

**Corrections:** 1 ruff correction (W292 missing trailing newline — residue from the manual file restore after 10d truncation).

**Results:**
- `uv run ruff check src/ tests/`: **clean** (after 1 correction)
- `uv run ruff format --check src/ tests/`: **clean**
- `uv run pytest -x`: **345/345 PASSED** (no regressions)
- Import check: **OK**

**Visual verification (Steven, 2026-05-08):** Phase label ("BUILD MAX-HEAP" / "EXTRACTION") now positioned in upper-right of tree area. No overlap with root node. Issue #1 closed.

**Next:** Execute 10f (extraction detection fix — Issue #10), then 10e (pointer spacing — Issue #4).

---

### 2026-05-08 — 10f closed: False extraction detection fixed (Issue #10)

**Worked on:** Added `_heap_in_extraction: bool` flag to SpriteManager — set True on boundary T3 ("Active heap" message), gates extraction detection in SWAP handler. Prevents `_heap_size` from decrementing during BUILD MAX-HEAP root sift-down. Defensive phase gate added to HeapOverlay.draw_over() boundary label drawing.

**Root cause:** `is_extraction = hi is not None and 0 in hi` fired during BUILD MAX-HEAP when sift-down at the root produced a SWAP with index 0 in `highlight_indices`. This prematurely decremented `_heap_size`, corrupted tree geometry, placed sprites in the sorted row, and caused: (a) boundary label during BUILD, (b) disappearing edges, (c) flat-row tree collapse.

**Corrections:** Zero corrections.

**Results:**
- `uv run ruff check src/ tests/`: **clean**
- `uv run ruff format --check src/ tests/`: **clean**
- `uv run pytest -x`: **345/345 PASSED** (no regressions)
- Import check: **OK**

**Visual verification (Steven, 2026-05-08):** All three symptoms resolved. BUILD MAX-HEAP maintains full 7-node tree with edges intact. Root sift-down swap (4↔7) no longer triggers extraction. Tree shrinks correctly during EXTRACTION. Issue #10 closed.

**Next:** Draft and execute 10e (Selection Sort pointer spacing — Issue #4).

---

### 2026-05-08 — 10e closed: Selection Sort `i` pointer spacing (Issue #4)

**Worked on:** Split `ARROW_GAP` (5px) into `I_ARROW_GAP` (12px) and `JMIN_ARROW_GAP` (5px) in `pointer.py`. `i_arrow_y()` uses the larger gap, giving the `i` pointer visible clearance above sprite rings. `jmin_arrow_y()` uses the original gap — `j`/`min` pointers unchanged. Test formulas in `test_pointer.py` updated to match new constant names. Also restored truncated `pointer.py` (last 3 lines of `_draw_jmin_pointer` were missing).

**Corrections:** 1 ruff correction (W292 trailing newline in pointer.py — residue from manual file restore).

**Results:**
- `uv run ruff check src/ tests/`: **clean** (after 1 correction)
- `uv run ruff format --check src/ tests/`: **clean**
- `uv run pytest -x`: **345/345 PASSED** (no regressions)
- Import check: **OK**

**Next:** Visual verification pending. Proceed to 10g (Bubble boundary line) and 10h (pointer visibility).

---

### 2026-05-08 — 10g closed: Bubble Sort boundary line hidden on completion (Issue #11)

**Worked on:** Added `_sort_complete: bool` flag to BubbleOverlay. Set True on TERMINAL/FAILURE. Gates `self._limit_line.draw(surface)` on `not self._sort_complete`. Reset to False in `reset()`.

**Corrections:** Zero corrections.

**Results:**
- `uv run ruff check src/ tests/`: **clean**
- `uv run ruff format --check src/ tests/`: **clean**
- `uv run pytest -x`: **345/345 PASSED** (no regressions)
- Import check: **OK**

**Visual verification (Steven, 2026-05-08):** Boundary line disappears on completion (green state). Reappears correctly after restart (R). Issue #11 closed.

**Next:** Execute 10h (i pointer size + cyan color).

---

### 2026-05-08 — 10h closed: `i` pointer visibility — bigger arrow + cyan color (Issue #4 continued)

**Worked on:** Split shared `ARROW_HEIGHT`/`ARROW_HALF_WIDTH` into `I_ARROW_HEIGHT = 16`/`I_ARROW_HALF_WIDTH = 7` (bigger) and `JMIN_ARROW_HEIGHT = 12`/`JMIN_ARROW_HALF_WIDTH = 5` (unchanged). Changed `POINTER_I_COLOR` from `PRIMARY_TEXT (240, 240, 245)` to cyan `(80, 200, 220)`. Removed unused `PRIMARY_TEXT` import. Updated `_draw_i_pointer` and `_draw_jmin_pointer` to use respective constants. Color test renamed `test_pointer_i_color_is_cyan`, assertion updated.

Also restored truncated `pointer.py` and `test_pointer.py` (same truncation pattern as before 10e).

**Corrections:** 1 ruff format correction.

**Results:**
- `uv run ruff check src/ tests/`: **clean** (after 1 correction)
- `uv run ruff format --check src/ tests/`: **clean**
- `uv run pytest -x`: **345/345 PASSED** (no regressions)
- Import check: **OK**

**Visual verification (Steven, 2026-05-08):** Cyan arrow visible but still too close to panel header counters — the above-baseline position has no room. Prompted 10i to relocate below.

**Next:** Execute 10i (move i pointer below j/min tier).

---

### 2026-05-08 — 10i closed: `i` pointer moved below j/min tier (Issue #4 final)

**Worked on:** Rewrote `i_arrow_y()` to position below j/min label bottom using `body_font.get_height()`. Flipped `_draw_i_pointer` from downward to upward triangle with label below arrow (matching j/min orientation). Changed `I_ARROW_GAP` from 12 to 8 (now means spacing between j/min label bottom and i tip, not spacing above ring). Updated module + class docstrings. Two tests updated: position test asserts `i_arrow_y > jmin_arrow_y`, formula test uses new computation with `body_font` fixture parameter.

Also restored truncated `pointer.py` and `test_pointer.py` before execution.

**Corrections:** 1 ruff format correction.

**Results:**
- `uv run ruff check src/ tests/`: **clean** (after 1 correction)
- `uv run ruff format --check src/ tests/`: **clean**
- `uv run pytest -x`: **345/345 PASSED** (no regressions)
- Import check: **OK**

**Visual verification (Steven, 2026-05-08):** All three pointers clearly visible below sprites. `i` (cyan) sits beneath `j`/`min` (orange) with clean separation. No header collision. Issue #4 fully resolved.

---

### Phase 10 Issue Register — Final State

| # | Issue | Fix Phase | Status |
|---|-------|-----------|--------|
| 1 | Phase label overlaps root node | 10d-fix | CLOSED |
| 3 | Boundary marker crosses into Insertion panel | 10d | CLOSED |
| 4 | `i` pointer visibility | 10e + 10h + 10i | CLOSED |
| 5 | Colored dot preceding title | — | NOT AN ISSUE |
| 6 | Sorted-row placeholders during BUILD | 10d | CLOSED |
| 7 | compute_sprite_moves duplicate values | 10c | CLOSED |
| 8 | Heap sorted-row misalignment | 10c (downstream) | CLOSED |
| 9 | EXTRACTION label persists after completion | 10d | CLOSED |
| 10 | False extraction during BUILD MAX-HEAP | 10f | CLOSED |
| 11 | Bubble boundary line persists on completion | 10g | CLOSED |

**Files changed during Phase 10:**
- `src/visualizer/controllers/orchestrator.py` — compute_sprite_moves() duplicate-value augmentation (10c)
- `src/visualizer/views/sprite_manager.py` — HeapOverlay panel_rect, phase gating, boundary clamping, BubbleOverlay sort_complete, SpriteManager _heap_in_extraction (10d, 10f, 10g)
- `src/visualizer/views/hud.py` — HeapPhaseLabel right-alignment (10d-fix)
- `src/visualizer/views/pointer.py` — Arrow geometry split (I_ vs JMIN_), i pointer repositioned below j/min, cyan color (10e, 10h, 10i)
- `src/visualizer/main.py` — HeapOverlay panel_rect argument (10d)
- `tests/unit/test_orchestrator_sprite_moves.py` — 6 new duplicate-value tests (10c)
- `tests/unit/test_hud.py` — HeapPhaseLabel right_x test (10d-fix)
- `tests/unit/test_pointer.py` — Pointer formula + color tests updated (10e, 10h, 10i)

**Recurring issue: File truncation.** Claude Code agent truncated files on 4 separate occasions during Phase 10 (sprite_manager.py in 10d, pointer.py in 10e and 10h, test_pointer.py in 10h). Each was manually restored from git. Pattern: last 3–5 lines of a method lost. Mitigation: always verify file integrity with `wc -l` and AST parse after agent execution.

**Recurring issue: DEVLOG entries not written.** Claude Code agent consistently failed to write DEVLOG pre/post entries despite explicit prompt instructions. All entries manually appended after each execution.
