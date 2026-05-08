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

## Current Phase: 10 — Manual Acceptance Testing (AT-01 through AT-27)

*Phase 7 entries archived to `docs/devlog/phase_07.md`.*

### 2026-05-08 14:00 — AT Visual Testing Session (Windows 11)

**Worked on:** Steven ran the app natively on Windows 11 (WSLg keyboard focus unreliable) and walked through AT-01 through AT-27 using the AT_READINESS_CHECKLIST.md. Marked results with `[x]` (pass), `[p]` (partial), and `[f]` (fail) with inline observations.

**WSLg note:** App displays under WSLg but keyboard input (Space, Right Arrow, R, Escape) doesn't register — likely a focus/event delivery issue in WSLg. Windows 11 native execution works correctly. Ubuntu 24 laptop testing deferred.

**Pass summary:** Majority of AT tests pass. Counter accuracy confirmed: Bubble (20/26), Selection (21/10), Insertion (17/19), Heap (20/30/35) all match expected values. All four panels complete with green backgrounds and green sprites. Play/pause/step/restart all functional.

**Issues found (5 total):**

| # | AT | Description | Severity |
|---|-----|-------------|----------|
| 1 | AT-22 | Heap phase label ("BUILD MAX-HEAP") overlaps tree root node | Visual — readability |
| 2 | AT-21/23 | Sorted-row placeholder circles visible during BUILD MAX-HEAP phase | Visual — cosmetic |
| 3 | AT-23 | Heap boundary marker (dashed line + label) renders outside Heap Sort panel into Insertion Sort panel | Visual — functional |
| 4 | AT-21 | Completion: Heap Sort elements don't all transition to green | Visual — functional |
| 5 | AT-27 | Colored dot preceding algorithm title text | Visual — cosmetic |

**AT-24 partial fail:** Steven noted `i` pointer is "above the array" — needs clarification whether this is a positioning error or just unexpected placement vs. spec expectation. The `[f]` mark has inline note but most sub-items pass.

**Decisions:**
- Issue #3 (cross-panel boundary) is highest priority — functional rendering bug
- Issue #1 (label overlap) is high priority — affects readability
- Issues #2 and #5 are lower priority cosmetic items
- Issue #4 (AT-21 completion green) needs investigation — may be the same green-vs-steel-blue question

**Open questions:**
- AT-21 completion fail: Is the issue that steel-blue sprites don't transition to green, or that the TERMINAL tick handler doesn't reach Heap Sort's sorted-row sprites?
- AT-27 colored dot: Need screenshot to determine source — could be a font rendering artifact or an unintended draw call
- AT-24 `i` pointer: Is the issue that `i` appears above the array (by design — doc 04 §4.4) or that its vertical position is wrong?

**Next:** Compile fix list, draft Phase 10-fix prompt for Claude Code execution.