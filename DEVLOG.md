# DEVLOG — Visual Learning Sorting

**Purpose:** Chronological engineering journal. Each entry records the work performed, the decisions made (and their rationale), and the open questions remaining. This is the project's decision trail and the source material for the video journal.

**Format:** Newest entries at the top. Each entry gets a timestamped heading (YYYY-MM-DD HH:MM). Within an entry: *Worked on*, *Decisions*, *Open questions*, *Next*. Entries are terse but complete — they should stand on their own when read six months from now or when scripted into narration.

**Timestamp convention (adopted 2026-04-23):** All entries use `YYYY-MM-DD HH:MM` format in headings to support multiple entries per day. Entries prior to this date used date-only granularity and are preserved as-is in the phase archives.

**Archive structure:** Completed phases are archived into `docs/devlog/` to keep this file lean. Pre-action plans are preserved in the archives — they are valuable video journal material. The archive files are the authoritative record; this file carries only current-phase work and one-line summaries of archived phases. Archives are grouped by layer boundary, not individual phase.

---

## Archived Phases

| Phase | Archive file | Summary |
|-------|-------------|---------|
| 0 + 1 | [`docs/devlog/phase_00_01.md`](docs/devlog/phase_00_01.md) | Project state review, Phase 0 closeout (pyproject, config, pseudocode, implementation order, fonts helper), agentic risk assessment, mempalace post-mortem, context-pack adoption, Phase 1 contracts.py, Correction C verification, model strategy. |
| 2 | [`docs/devlog/phase_02.md`](docs/devlog/phase_02.md) | All four algorithm generators: Bubble Sort (2a, 20/26), Selection Sort (2b, 21/10), Insertion Sort (2c, 17/19), Heap Sort (2d, 20/30/35). Includes pre-action plans, post-action closeouts, corrections, and T3 contiguity spec bug discovery. |
| 3 + 4 | [`docs/devlog/phase_03_04.md`](docs/devlog/phase_03_04.md) | D-081 resolution (message-prefix T3 classification). Phase 3: algorithm unit tests (conftest, bubble, selection, insertion, heap — 29 tests, TC-A1/A2/A3/A7/A8/A9/A10/A11/A12/A13/A14/A19). Phase 4: easing module (ease_in_out_quad, ease_out_cubic, sine_arc — 21 tests, TC-A5). Cumulative: 50/50. |
| 5 | [`docs/devlog/phase_05.md`](docs/devlog/phase_05.md) | View Layer: window.py (GridLayout), sprite.py (NumberSprite, ColorState), panel.py (PanelRenderer, header rhythm, state overlays), tree_layout.py (binary tree geometry, TC-A20/A21/A22), pointer.py (Selection Sort arrows, D-068 coalescing, TC-A23), limitline.py (Bubble Sort boundary), hud.py (BubbleHUD counters, HeapPhaseLabel, HeapBoundaryLabel). 185 view-layer tests, 235 cumulative. Doc 12 color fix. |
| 6 | [`docs/devlog/phase_06.md`](docs/devlog/phase_06.md) | Controller/Orchestrator: PanelState, duration constants, PanelContext, get_duration(), Orchestrator update(dt) core loop, compute_sprite_moves() sprite identity delta, play/pause/step/restart controls, integration tests (TC-A4/A6/A15/A16/A17/A18). 104 orchestrator tests (97 unit + 7 integration), 339 cumulative. Zero logic corrections. Spec paralysis vs. spec insufficiency reflection. |
| 7 | [`docs/devlog/phase_07.md`](docs/devlog/phase_07.md) | Main event loop, sprite animation, per-algorithm choreography: event loop (7), sprite rendering (7b), Selection Sort pointers (7c-1), Bubble Sort compare-lift + BubbleOverlay (7c-2), Insertion Sort key elevation + InsertionOverlay (7c-3), Heap Sort tree layout + HeapOverlay (7c-4, **Opus 4.6**), Selection Sort settled color + configurable array (7c-5). sprite_manager.py ~1000 lines, main.py ~350 lines. 339 cumulative (no new tests). 3 total corrections (all ruff). Model selection reflection. |

---

## Current Phase: 10 — Manual Acceptance Testing and Visual Bug Fixes

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