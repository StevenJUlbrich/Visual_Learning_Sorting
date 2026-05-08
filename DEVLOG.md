# DEVLOG — Visual Learning Sorting

**Purpose:** Chronological engineering journal. Each entry records the work performed, the decisions made (and their rationale), and the open questions remaining. This is the project's decision trail and the source material for the video journal.

**Format:** Newest entries at the top. Each entry gets a timestamped heading (YYYY-MM-DD HH:MM). Within an entry: *Worked on*, *Decisions*, *Open questions*, *Next*. Entries are terse but complete — they should stand on their own when read six months from now or when scripted into narration.

**Timestamp convention (adopted 2026-04-23):** All entries use `YYYY-MM-DD HH:MM` format in headings to support multiple entries per day. Entries prior to this date used date-only granularity and are preserved as-is in the phase archives.

**Archive structure:** Completed phases are archived into `docs/devlog/` to keep this file lean. Pre-action plans are preserved in the archives — they are valuable video journal material. The archive files are the authoritative record; this file carries only current-phase work and one-line summaries of archived phases. Archives are grouped by layer boundary, not individual phase.

---

## Archived Phases

| Phase | Archive file | Summary |
| ----- | ----------- | ------- |
| 0 + 1 | [`docs/devlog/phase_00_01.md`](docs/devlog/phase_00_01.md) | Project state review, Phase 0 closeout (pyproject, config, pseudocode, implementation order, fonts helper), agentic risk assessment, mempalace post-mortem, context-pack adoption, Phase 1 contracts.py, Correction C verification, model strategy. |
| 2 | [`docs/devlog/phase_02.md`](docs/devlog/phase_02.md) | All four algorithm generators: Bubble Sort (2a, 20/26), Selection Sort (2b, 21/10), Insertion Sort (2c, 17/19), Heap Sort (2d, 20/30/35). Includes pre-action plans, post-action closeouts, corrections, and T3 contiguity spec bug discovery. |
| 3 + 4 | [`docs/devlog/phase_03_04.md`](docs/devlog/phase_03_04.md) | D-081 resolution (message-prefix T3 classification). Phase 3: algorithm unit tests (conftest, bubble, selection, insertion, heap — 29 tests, TC-A1/A2/A3/A7/A8/A9/A10/A11/A12/A13/A14/A19). Phase 4: easing module (ease_in_out_quad, ease_out_cubic, sine_arc — 21 tests, TC-A5). Cumulative: 50/50. |
| 5 | [`docs/devlog/phase_05.md`](docs/devlog/phase_05.md) | View Layer: window.py (GridLayout), sprite.py (NumberSprite, ColorState), panel.py (PanelRenderer, header rhythm, state overlays), tree_layout.py (binary tree geometry, TC-A20/A21/A22), pointer.py (Selection Sort arrows, D-068 coalescing, TC-A23), limitline.py (Bubble Sort boundary), hud.py (BubbleHUD counters, HeapPhaseLabel, HeapBoundaryLabel). 185 view-layer tests, 235 cumulative. Doc 12 color fix. |
| 6 | [`docs/devlog/phase_06.md`](docs/devlog/phase_06.md) | Controller/Orchestrator: PanelState, duration constants, PanelContext, get_duration(), Orchestrator update(dt) core loop, compute_sprite_moves() sprite identity delta, play/pause/step/restart controls, integration tests (TC-A4/A6/A15/A16/A17/A18). 104 orchestrator tests (97 unit + 7 integration), 339 cumulative. Zero logic corrections. Spec paralysis vs. spec insufficiency reflection. |
| 7 | [`docs/devlog/phase_07.md`](docs/devlog/phase_07.md) | Main event loop, sprite animation, per-algorithm choreography: event loop (7), sprite rendering (7b), Selection Sort pointers (7c-1), Bubble Sort compare-lift + BubbleOverlay (7c-2), Insertion Sort key elevation + InsertionOverlay (7c-3), Heap Sort tree layout + HeapOverlay (7c-4, **Opus 4.6**), Selection Sort settled color + configurable array (7c-5). sprite_manager.py ~1000 lines, main.py ~350 lines. 339 cumulative (no new tests). 3 total corrections (all ruff). Model selection reflection. |
| 10 | [`docs/devlog/phase_10.md`](docs/devlog/phase_10.md) | Manual acceptance testing (AT-01 through AT-27) and visual bug fixes. 10 issues found, all resolved: compute_sprite_moves duplicate-value fix (10c, Opus), Heap visual batch -- boundary clamping, placeholder gating, EXTRACTION label hide, phase label right-align (10d/10d-fix), false extraction detection (10f), Bubble boundary line hide on completion (10g), Selection Sort i pointer -- spacing increase, cyan color, relocated below j/min tier (10e/10h/10i). 6 new tests (10c), 345 cumulative. 4 file truncation incidents (all restored from git). |

---

## Current Phase: Post-10 -- Next steps

Phase 10 manual acceptance testing complete. All 27 ATs pass. All 10 visual issues resolved. 345/345 tests passing.

**Remaining work:**

- Phase 9 (CI pipeline) -- deferred during Phase 10, ready to implement
- On-screen control buttons (Play/Pause, Step, Restart) -- deferred from Phase 7
- Ubuntu 24 native testing -- deferred from 10a (WSLg keyboard issue)
- Font assets (`assets/fonts/`) -- still using SysFont fallback
