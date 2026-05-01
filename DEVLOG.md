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

---

## 2026-05-01 11:07 — Phase 6a closed: PanelState + duration constants (post-action)

### Worked on

Created `src/visualizer/controllers/orchestrator.py` (Phase 6a scope: `PanelState` enum with 5 members, standard duration constants T1=150/T2=400/T3=200/TERMINAL=0/FAILURE=0, sift-down cadence override constants T1=100/T2=250/T3=130, `get_duration(op_type, sift_down_cadence)` pure function with match dispatch, `PanelContext` plain class with reset() preserving algorithm_name and complexity) and `tests/unit/test_orchestrator.py` (28 tests: enum membership, standard constants, sift-down constants, all 9 get_duration cases including SHIFT-always-standard invariant, 8 PanelContext construction/reset assertions).

### Results

- `uv run pytest tests/unit/test_orchestrator.py -v`: **28/28 PASSED** (first run after one I001 import-sort fix)
- `uv run pytest tests/unit/ -v`: **263/263 PASSED** (cumulative)
- `PYRIGHT_PYTHON_GLOBAL_NODE=false uv run pyright`: **0 errors, 0 warnings**
- `uv run ruff check` + `uv run ruff format --check`: **clean**

### Corrections

One I001 import-sort fix in test_orchestrator.py (ruff auto-formatted).

### Next

Phase 6b: Core loop — update(dt) + tick dispatch.