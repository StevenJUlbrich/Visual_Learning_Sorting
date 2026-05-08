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
| 10 | [`docs/devlog/phase_10.md`](docs/devlog/phase_10.md) | Manual AT testing (Windows 11), WSLg limitation documented, 7 active visual bugs found (critical: compute_sprite_moves duplicate-value failure). Fix plan: 10c (Opus — sprite identity), 10d (Sonnet — Heap visual batch), 10e (Sonnet — pointer spacing). |

---

## Current Phase: 10 — Manual Acceptance Testing and Visual Bug Fixes

*Detailed entries in [`docs/devlog/phase_10.md`](docs/devlog/phase_10.md).*

**Status:** 10a (build verification) and 10b (AT visual testing) complete. 7 active issues found. Fix plan drafted: 10c (compute_sprite_moves duplicate fix, Opus), 10d (Heap visual batch, Sonnet), 10e (pointer spacing, Sonnet).

**Next:** Execute 10c prompt.