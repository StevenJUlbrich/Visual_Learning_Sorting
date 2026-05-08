# Phase 10 — Manual Acceptance Testing and Visual Bug Fixes

**Started:** 2026-05-08
**Scope:** AT-01 through AT-27 visual verification, bug triage, and targeted fixes.
**Test platform:** Windows 11 native (Dell 7770). WSLg tested but unusable for keyboard input.

---

## 10a — Build Verification and Platform Testing (2026-05-08)

### Successful Build

Application launches and runs correctly on Windows 11 native. All four panels animate independently. Play/pause/step/restart all functional via keyboard (Space/Right/R/Escape).

**Counter accuracy verified (default array `[4, 7, 2, 6, 1, 5, 3]`):**

| Algorithm | Cmp | Wr | Steps | Expected | Match |
|-----------|-----|-----|-------|----------|-------|
| Bubble Sort | 20 | 26 | — | 20/26 | ✓ |
| Selection Sort | 21 | 10 | — | 21/10 | ✓ |
| Insertion Sort | 17 | 19 | — | 17/19 | ✓ |
| Heap Sort | 20 | 30 | 35 | 20/30/35 | ✓ |

All four panels reach completion with green backgrounds and green sprites. Elapsed timers freeze correctly on completion. Independent queue timing creates visible race behavior.

### WSLg / Pygame Limitation

Pygame window displays under WSLg (Ubuntu on Dell 7770 WSL) but keyboard input does not register. The event loop receives no KEYDOWN events — likely a WSLg compositor focus delivery issue. `clock.tick(60)` runs normally, sprites render correctly, but no interaction is possible.

**Workaround:** Run natively on Windows 11. Ubuntu 24 laptop testing deferred.
**Impact:** Development workflow only. No code changes needed.

---

## 10b — Visual Acceptance Test Results (2026-05-08)

### AT Results Summary

Walked through AT-01 through AT-27 using `TODO/AT_READINESS_CHECKLIST.md`. Results marked with `[x]` (pass), `[p]` (partial), `[f]` (fail).

**Passing (no issues):** AT-01 (partial — Heap tree layout noted), AT-02, AT-03, AT-04, AT-05, AT-07, AT-09, AT-10, AT-11, AT-12, AT-13, AT-14, AT-15, AT-16, AT-17 (untested — requires config change), AT-18, AT-19, AT-20, AT-25, AT-26, AT-27.

**Issues found:** 7 active issues from visual testing across AT-08, AT-21, AT-22, AT-23, AT-24.

### Issue Register

| # | Severity | AT | Description | Fix Phase |
|---|----------|-----|-------------|-----------|
| **7** | **CRITICAL** | AT-08 | `compute_sprite_moves()` fails with duplicate values — sprites in wrong positions | 10c |
| 8 | HIGH | AT-08/21 | Heap sorted-row vertical misalignment (likely downstream of #7) | verify after 10c |
| 3 | HIGH | AT-23 | Boundary marker crosses into Insertion Sort panel | 10d |
| 1 | MEDIUM | AT-22 | Phase label overlaps root node (both phases) | 10d |
| 9 | MEDIUM | AT-22 | EXTRACTION label persists after completion | 10d |
| 4 | MEDIUM | AT-24 | Selection Sort `i` pointer too close to sprites | 10e |
| 6 | LOW | AT-21/23 | Sorted-row placeholders visible during BUILD MAX-HEAP | 10d |

### Closed Items

| # | AT | Resolution |
|---|-----|-----------|
| 5 | AT-27 | Colored dot — confirmed not an issue |
| — | AT-21 | Completion green — confirmed not an issue |

---

## Fix Plan — Brick by Brick

Three fix sub-phases, ordered by dependency and risk. Each sub-phase gets its own Claude Code prompt with model selection matched to decision density.

### 10c — Fix `compute_sprite_moves()` duplicate-value handling (Issue #7)

**Model: Opus 4.6** — judgment-heavy. Changes a core controller function's interface, must handle all four algorithm tick patterns, and requires updating 8+ unit tests plus integration test verification.

**Root cause:** `compute_sprite_moves()` detects movement by comparing `old_state[i] != new_state[i]`. When duplicate values shift or swap, the old and new values at a slot are identical, so `changed` is empty and the sprite movement goes undetected. Over a full sort with duplicates, sprites accumulate in wrong positions.

**Fix approach:** Augment `compute_sprite_moves()` with `operation_type` and `highlight_indices` parameters from the current tick. When `changed` is empty but the tick is SHIFT or SWAP, use `highlight_indices` to determine which slots are involved and move sprites accordingly. Fallback to existing logic when `changed` is non-empty (performance optimization — no behavior change for unique arrays).

**Files:**
- `src/visualizer/controllers/orchestrator.py` — function signature + logic + call site
- `tests/unit/test_orchestrator.py` — update Group 13 tests for new signature, add duplicate-value test cases

**Verification:** Run with `config.toml` array `[3, 1, 3, 2, 1, 2, 3]`. All four panels should show `[1, 1, 2, 2, 3, 3, 3]` at completion. Check Issue #8 (Heap alignment) resolves.

**Gates:** `uv run ruff check src/ tests/`, `uv run ruff format --check src/ tests/`, `uv run pytest -x`, import verification.

### 10d — Heap Sort visual fixes (Issues #1, #3, #6, #9)

**Model: Sonnet 4.6** — prescriptive mechanical execution. Four independent fixes in HeapOverlay and related constants. No architectural judgment needed.

**Fixes:**
1. **Issue #1 — Phase label offset.** Increase `_PHASE_LABEL_OFFSET` in `sprite_manager.py` from 20 to `tree_node_radius + font_height + margin` (dynamically computed in HeapOverlay.__init__). Label must clear the root sprite ring at all times.
2. **Issue #3 — Boundary clamp.** In `HeapOverlay._draw_boundary_line()` and `draw_over()`, clamp `boundary_x` to `max(boundary_x, panel_rect.x + margin)`. Skip drawing entirely if boundary would fall outside the panel rect.
3. **Issue #6 — Placeholder phase gate.** In `HeapOverlay._draw_placeholders()` (called from `draw_under()`), only draw when `self._phase == "EXTRACTION"`.
4. **Issue #9 — Hide label on completion.** In `HeapOverlay._process_tick()` TERMINAL branch, set `self._phase = None`. In `draw_over()`, guard phase label draw with `if self._phase is not None`.

**Files:**
- `src/visualizer/views/sprite_manager.py` — HeapOverlay class (all four fixes)

**Gates:** Same four-gate check. No test changes expected (HeapOverlay is visual-only, no unit tests).

### 10e — Selection Sort pointer spacing (Issue #4)

**Model: Sonnet 4.6** — single constant adjustment.

**Fix:** Increase the vertical offset for above-array `i` pointer in `pointer.py`. The gap between sprite ring top and arrow tip needs to grow so `i` is clearly distinguishable from the sprite row.

**Files:**
- `src/visualizer/views/pointer.py` — above-arrow y-offset constant

**Gates:** Same four-gate check. Existing pointer tests (25, Phase 5e) should still pass — they test positioning logic, not pixel-exact coordinates (verify).

---

## Decision Log

| Decision | Rationale |
|----------|-----------|
| Fix #7 first, alone | Foundational — affects all algorithms with duplicates. Issue #8 may auto-resolve. |
| Opus for 10c, Sonnet for 10d/10e | Match model to decision density, not code volume (same lesson as Phase 7c-4). |
| Batch Heap visual fixes into 10d | All four touch HeapOverlay; separate prompts risk merge conflicts. |
| Don't change SortResult contract | Approach (A) uses existing `operation_type` + `highlight_indices` — minimal change surface. |
| Verify #8 after #7 before writing a fix | Avoid fixing a symptom when the cause is about to change. |

---
