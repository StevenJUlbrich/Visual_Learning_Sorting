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

---

## 2026-04-23 10:03 — Phase 5a closed: window.py (post-action)

### Worked on

Created `src/visualizer/views/window.py` (`load_preset`, `GridLayout`, `init_display`) and `tests/unit/test_window.py` (25 tests: desktop/tablet dimension assertions, all four panel rect coordinates, non-overlap and bounds invariants for both presets, min panel-width guard, unknown-preset ValueError).

### Results

- `uv run pytest tests/unit/test_window.py -v`: **25/25 PASSED** (first run)
- `uv run pytest tests/unit/ -v`: **75/75 PASSED** (cumulative)
- `PYRIGHT_PYTHON_GLOBAL_NODE=false uv run pyright src/visualizer/views/window.py tests/unit/test_window.py`: **0 errors** (1 pre-existing `pytest.approx` warning)
- `uv run ruff check` + `uv run ruff format --check`: **clean**

### Corrections

1. **`reportConstantRedefinition` on `@dataclass` with `field(init=False)`** — pyright strict treats the dataclass field declarations (e.g., `PADDING: int = field(init=False)`) as class-level constant definitions, then flags the `__post_init__` assignments as redefinitions. Switched from `@dataclass` to a plain class; `__init__` makes the first assignment (definition, not redefinition). Task allowed "dataclass or class" — plain class is the correct call here.
2. **RUF002/RUF003: ambiguous `×` character** — module docstring and test comments used `×` (U+00D7 MULTIPLICATION SIGN). Ruff flags it as visually ambiguous with `x`. Replaced with `x` throughout.
3. **`ruff format` reformatted `test_window.py`** — one long assertion line wrapped. No logic change.

### Decisions

- **Plain class over `@dataclass`** — avoids `reportConstantRedefinition` without suppression comments and is more readable for this pattern (computed layout is not a typical dataclass).
- **`panel_height == 297`, not 296** — doc 04 §2.6 reference table shows 296 but the formula `(651 - 57) // 2 = 297` is authoritative. Test asserts the computed value; comment documents the discrepancy.

### Open questions

- None.

### Next

Phase 5b: `sprite.py` (NumberSprite — circular ring, float coords, easing integration).

---

## 2026-04-23 09:58 — Phase 5a start: window.py plan (pre-action)

### Model / session
Sonnet 4.6. First View layer brick — pure layout math, no rendering logic.

### Plan
Create `src/visualizer/views/window.py` (display init, 2×2 grid math, config.toml preset loading) and `tests/unit/test_window.py` (coordinate-math verification against doc 04 §2.6 reference table).

### Exit criteria
- `uv run pytest tests/unit/test_window.py -v` all green
- `uv run pytest tests/unit/ -v` all green (cumulative, should be 51+ tests)
- `PYRIGHT_PYTHON_GLOBAL_NODE=false uv run pyright src/visualizer/views/window.py tests/unit/test_window.py` clean
- `uv run ruff check src/visualizer/views/window.py tests/unit/test_window.py` + format check clean

---

(no entries yet beyond the pre-action above — Phase 5 post-action entries will follow)

---

## Entry Template (for future use)

```markdown
## YYYY-MM-DD HH:MM — One-line session summary

### Worked on
Prose. What was touched, what was produced.

### Decisions
- What was decided.
- Why this path rather than alternatives.
- Decision-ID link if it was locked into DECISIONS.md.

### Open questions
- Unresolved items. Where they will be answered.

### Next
The single most concrete next action.
```
