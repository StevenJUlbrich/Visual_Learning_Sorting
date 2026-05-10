# Development Timeline

Phase-by-phase build history showing what was built, which AI model executed it, how many corrections were needed, and the cumulative test count. Full details are in the devlog archives under `docs/devlog/`.

## Phase Summary

| Phase | What | Model | Corrections | Tests | Cumulative |
|-------|------|-------|-------------|-------|------------|
| 0 | Spec gaps (pyproject, config, pseudocode, fonts helper, implementation order) | Human + Opus | — | — | — |
| 1 | `contracts.py` — SortResult, OpType, BaseSortAlgorithm | Opus 4.6 | 0 | — | — |
| 2a | `bubble.py` — Bubble Sort generator (20/26) | Sonnet 4.6 | 0 | — | — |
| 2b | `selection.py` — Selection Sort generator (21/10) | Sonnet 4.6 | 0 | — | — |
| 2c | `insertion.py` — Insertion Sort generator (17/19) | Opus 4.6 | 0 | — | — |
| 2d | `heap.py` — Heap Sort generator (20/30/35) | Opus 4.6 | 0 | — | — |
| 3 | Algorithm unit tests (TC-A1/A2/A3/A7-A14/A19) | Sonnet 4.6 | 0 | 29 | 29 |
| 4 | `easing.py` — ease_in_out_quad, ease_out_cubic, sine_arc (TC-A5) | Sonnet 4.6 | 0 | 21 | 50 |
| 5a | `window.py` — GridLayout, load_preset, init_display | Sonnet 4.6 | 0 | 25 | 75 |
| 5b | `sprite.py` — NumberSprite, ColorState, COLOR_MAP | Opus 4.6 | 0 | 19 | 94 |
| 5c | `panel.py` — PanelRenderer, header rhythm, state overlays | Opus 4.6 | 0 | 31 | 125 |
| 5d | `tree_layout.py` — binary tree node positions, edges, sorted row (TC-A20/A21/A22) | Sonnet 4.6 | 0 | 38 | 163 |
| 5e | `pointer.py` — Selection Sort i/j/min arrows, coalescing (TC-A23) | Sonnet 4.6 | 0 | 25 | 188 |
| 5f | `limitline.py` — Bubble Sort dashed boundary, advance/reset | Sonnet 4.6 | 0 | 21 | 209 |
| 5g | `hud.py` — BubbleHUD + HeapPhaseLabel + HeapBoundaryLabel | Sonnet 4.6 | 0 | 26 | 235 |
| 6a | `orchestrator.py` (partial) — PanelState, duration constants, PanelContext, get_duration | Sonnet 4.6 | 0 | 28 | 263 |
| 6b | `orchestrator.py` — Orchestrator update(dt) core loop, state machine | Opus 4.6 | 0 | 27 | 290 |
| 6c | `orchestrator.py` — compute_sprite_moves(), slot mapping | Sonnet 4.6 | 0 | 16 | 306 |
| 6d | `orchestrator.py` — play/pause/step/restart controls | Sonnet 4.6 | 0 | 26 | 332 |
| 6e | Integration tests — TC-A4/A6/A15-A18 + counter accuracy | Sonnet 4.6 | 0 | 7 | 339 |
| 7 | `main.py` — Pygame event loop, config, keyboard bindings | Sonnet 4.6 | 1 ruff | 0 | 339 |
| 7b | `sprite_manager.py` — SpriteManager, animation dispatch | Sonnet 4.6 | 0 | 0 | 339 |
| 7c-1 | Selection Sort pointer overlay | Sonnet 4.6 | 0 | 0 | 339 |
| 7c-2 | Bubble Sort choreography (compare-lift, BubbleOverlay) | Sonnet 4.6 | 2 ruff | 0 | 339 |
| 7c-3 | Insertion Sort choreography (key elevation, InsertionOverlay) | Sonnet 4.6 | 0 | 0 | 339 |
| 7c-4 | Heap Sort choreography (tree layout, HeapOverlay, 2D arcs) | **Opus 4.6** | 0 | 0 | 339 |
| 7c-5 | Selection Sort settled color + configurable array | Sonnet 4.6 | 0 | 0 | 339 |
| 10a | Build verification, WSLg limitation documented | Human | — | 0 | 339 |
| 10b | Visual acceptance test walkthrough (AT-01 through AT-27) | Human | — | 0 | 339 |
| 10c | compute_sprite_moves() duplicate-value fix | Opus 4.6 | 0 | 6 | 345 |
| 10d | Heap visual fixes batch (boundary clamping, placeholder gating) | Sonnet 4.6 | 0 | 0 | 345 |
| 10d-fix | HeapPhaseLabel repositioned to upper-right | Sonnet 4.6 | 1 ruff | 0 | 345 |
| 10e | Selection Sort `i` pointer spacing | Sonnet 4.6 | 1 ruff | 0 | 345 |
| 10f | False extraction detection fix | Sonnet 4.6 | 0 | 0 | 345 |
| 10g | Bubble Sort boundary line hide on completion | Sonnet 4.6 | 0 | 0 | 345 |
| 10h | Selection Sort `i` pointer visibility (larger arrows, cyan color) | Sonnet 4.6 | 1 ruff | 0 | 345 |
| 10i | Selection Sort `i` pointer relocated below j/min tier | Sonnet 4.6 | 1 ruff | 0 | 345 |

## Correction Analysis

Across 35 AI-executed phases: **7 total corrections, all ruff formatting** (import sort order, trailing newlines, list comprehension style). Zero logic corrections. Zero test failures caused by incorrect AI-generated logic.

This doesn't mean the AI always produced correct code on the first try — it means the prompt engineering was precise enough that logic errors didn't make it through. When logic issues did exist (duplicate-value blindspot, false extraction detection, T3 contiguity collision), they were caught by spec-level reasoning during prompt design or by acceptance testing, not by iterating on broken output.

## Model Usage Breakdown

| Model | Phases | Percentage | Used for |
|-------|--------|-----------|----------|
| Sonnet 4.6 | 25 phases | ~71% | Well-specified mechanical execution: simple algorithms, view components, tests, bug fixes with clear scope |
| Opus 4.6 | 8 phases | ~23% | Multi-constraint judgment: complex algorithms (Insertion, Heap), orchestrator core, Heap choreography, duplicate-value fix |
| Human | 2 phases | ~6% | Visual acceptance testing (AT walkthrough), build verification |

The model assignment was deliberate — see [Spec-First Methodology](Spec-First-Methodology) for the rationale. The key insight: match the model to the decision density, not the code volume.

## Timeline

| Date | Work |
|------|------|
| 2026-04-14 | Phase 0 — Spec gap closure, project scaffolding |
| 2026-04-19 | Phase 1 — contracts.py, model strategy established |
| 2026-04-20 | Phase 2 — All four algorithm generators |
| 2026-04-23 | Phases 3-4 — Algorithm unit tests + easing module (50 tests) |
| 2026-04-24 | Phase 5 — View layer (window, sprite, panel, tree, pointer, limitline, hud — 185 tests) |
| 2026-04-30 | Phase 6 — Controller/Orchestrator (104 tests) |
| 2026-05-01 | Phase 6e — Integration tests (339 cumulative) |
| 2026-05-04 | Phase 7 — Main event loop + sprite rendering |
| 2026-05-05 | Phase 7c — Per-algorithm choreography (5 sub-phases in one day) |
| 2026-05-08 | Phase 10 — Acceptance testing + 10 visual bug fixes (345 cumulative) |
| 2026-05-10 | Post-10 — Repo cleanup, README rewrite, wiki drafting |

## File Truncation Incidents

4 incidents during Phase 10, all involving the Claude Code agent silently truncating files mid-write:

| Phase | File | Truncation point | Detection |
|-------|------|------------------|-----------|
| 10d | `sprite_manager.py` | Line 1017 — lost `reset()` method | Test failure |
| 10e | `pointer.py` | Line 144 — mid-assignment `label_rect = lab` | AST parse error |
| 10h | `pointer.py` | Same region — last 3 lines of `_draw_jmin_pointer` | Manual inspection |
| 10i | `test_pointer.py` | Line 216 — mid-call `pointer_set.draw(surf` | AST parse error |

All were recovered from git (`git show HEAD~1:path/to/file`). AST parse verification was added as a standard gate after the first incident. Larger files (~1000 lines) were more susceptible.

## Where to Find Everything

| Resource | Location |
|----------|----------|
| Full devlog archives | [`docs/devlog/`](../docs/devlog/) |
| Prompt documents | [`docs/prompts/`](../docs/prompts/) |
| Design specifications | [`docs/design_docs/`](../docs/design_docs/) |
| Acceptance test checklist | [`TODO/AT_READINESS_CHECKLIST.md`](../TODO/AT_READINESS_CHECKLIST.md) |
| Implementation tracker | [`TODO/IMPLEMENTATION_TRACKER.md`](../TODO/IMPLEMENTATION_TRACKER.md) |
| AI conversation reviews | [`docs/AI_Conversations/`](../docs/AI_Conversations/) |
