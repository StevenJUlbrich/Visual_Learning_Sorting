# DEVLOG — Visual Learning Sorting

**Purpose:** Chronological engineering journal. Each entry records the work performed, the decisions made (and their rationale), and the open questions remaining. This is the project's decision trail and the source material for the video journal.

**Format:** Newest entries at the top. Each session gets a dated heading. Within an entry: *Worked on*, *Decisions*, *Open questions*, *Next*. Entries are terse but complete — they should stand on their own when read six months from now or when scripted into narration.

**Archive structure:** Completed phases are archived into `docs/devlog/` to keep this file lean. Pre-action plans are preserved in the archives — they are valuable video journal material. The archive files are the authoritative record; this file carries only current-phase work and one-line summaries of archived phases.

---

## Archived Phases

| Phase | Archive file | Summary |
|-------|-------------|---------|
| 0 + 1 | [`docs/devlog/phase_00_01.md`](docs/devlog/phase_00_01.md) | Project state review, Phase 0 closeout (pyproject, config, pseudocode, implementation order, fonts helper), agentic risk assessment, mempalace post-mortem, context-pack adoption, Phase 1 contracts.py, Correction C verification, model strategy. |
| 2 | [`docs/devlog/phase_02.md`](docs/devlog/phase_02.md) | All four algorithm generators: Bubble Sort (2a, 20/26), Selection Sort (2b, 21/10), Insertion Sort (2c, 17/19), Heap Sort (2d, 20/30/35). Includes pre-action plans, post-action closeouts, corrections (bubble message format, selection yield timing), and the T3 contiguity spec bug discovery. |

---

## 2026-04-20 — D-081: T3 contiguity spec bug resolved — message-prefix classification locked

### Worked on

Resolved the T3 contiguity spec bug discovered during Phase 2d (heap.py). The bug was more severe than initially framed: it affects every sift-down rooted at index 0, not just the edge cases at heap_size ∈ {2, 3}. For `default_7`, 6 of 11 Logical Tree T3 ticks produce contiguous tuples that a contiguity-based classifier would misidentify as Boundary T3 ticks.

Resolution: classify by **message prefix** (`"Active heap"` = Boundary, `"Evaluating tree level"` = Logical Tree), locked as D-081. No production code changes — `heap.py` already emits the correct distinct prefixes. Six spec documents amended to replace all contiguity-based classification language with message-prefix references.

### Amended documents

1. `03_DATA_CONTRACTS.md` §Distinguishing the two variants — replaced contiguity rule with message-prefix rule, added rationale paragraph.
2. `00_PSEUDOCODE.md` §4 — updated TC-A19 invariants and boundary T3 inline comment.
3. `08_TEST_PLAN.md` TC-A19 — replaced `_is_contiguous` helper with `_is_logical_tree_t3` using message prefix; updated procedure prose and assertion rule #1.
4. `05_ALGORITHMS_VIS_SPEC.md` §6.1 — updated "Distinction from boundary T3 ticks" paragraph.
5. `heap.py` module docstring — replaced "distinguished by index contiguity" with "distinguished by message prefix" and added explicit warning against contiguity classification.
6. `DECISIONS.md` — added D-081 with full rationale and list of amended docs.

### Decisions

- **D-081 (locked).** Message-prefix classification chosen over sequencing-context (which would require lookahead/buffering in the View and a state machine in TC-A19). Message prefix is self-contained — each tick classifiable in isolation.
- **No SortResult schema change.** Adding a `range_variant` field was considered and rejected; the existing `message` field already carries the discriminator, and changing the Phase 1 data contract would ripple across the project.

### Open questions

- None from this resolution. The bug is fully closed. TC-A19 can now be authored correctly in Phase 3.

### Next

Phase 3 (algorithm unit tests) is unblocked. Phase 4 (easing module) can run in parallel.

---

## 2026-04-20 — Phase 3b closed: test_selection.py (post-action)

### Worked on

Created `tests/unit/test_selection.py` (6 tests: TC-A1, TC-A2, TC-A3, TC-A10, single-element guard, swap-skip test on `sorted_7`). Full unit suite now at 12 tests (bubble + selection).

### Results

- `uv run pytest tests/unit/test_selection.py -v`: **6/6 PASSED**
- `uv run pytest tests/unit/ -v`: **12/12 PASSED**
- `uv run pyright tests/`: **0 errors, 0 warnings**
- `uv run ruff check tests/` + `uv run ruff format --check tests/`: **clean**

No corrections needed — first write was clean.

### Decisions

- **`sorted_7` swap-skip test asserts both `len(swap_ticks) == 0` and `writes == 0`** — double-checking the same invariant via two independent views (tick list and counter) catches a hypothetical bug where a swap happened but didn't yield a tick, or vice versa.

### Open questions

None.

### Next

Phase 3c: test_insertion.py (TC-A1, TC-A2, TC-A3, TC-A9, TC-A10, TC-A11, TC-A14).

---

## 2026-04-20 — Phase 3b start: test_selection.py plan (pre-action)

### Model / session
Sonnet 4.6 per model strategy. Selection Sort tests are well-specified with straightforward counter targets.

### Plan
Create `tests/unit/test_selection.py` with TC-A1, TC-A2, TC-A3, TC-A10 for Selection Sort, plus Selection-specific checks.

### Exit criteria
- `uv run pytest tests/unit/test_selection.py -v` all green
- `uv run pyright tests/` clean
- `uv run ruff check tests/` + `uv run ruff format --check tests/` clean

---

## 2026-04-20 — Phase 3a closed: conftest + test_bubble.py (post-action)

### Worked on

Created `tests/conftest.py` (session-scoped headless Pygame init, 6 data fixtures), `tests/unit/__init__.py` (empty), and `tests/unit/test_bubble.py` (6 tests covering TC-A1, TC-A2, TC-A3, TC-A10, TC-A12, plus single-element guard).

### Results

- `uv run pytest tests/unit/test_bubble.py -v`: **6/6 PASSED**
- `uv run pyright tests/`: **0 errors, 0 warnings**
- `uv run ruff check tests/` + `uv run ruff format --check tests/`: **clean**

Two corrections before clean pass:
1. **`_pygame_session` return type** — first draft used `pytest.FixtureRequest` (wrong). Fixed to `Generator[None]` (the correct type for a generator fixture).
2. **`noqa: E402` unnecessary** — ruff does not flag `import pygame` after module-level `os.environ` assignments as E402; the noqa was spurious (`RUF100`). Removed.
3. **Pyright `reportUnusedFunction`** — `_pygame_session` is called by pytest's fixture system, invisible to static analysis. Suppressed with `# pyright: ignore[reportUnusedFunction]` on the `def` line.

### Decisions

- **`Generator[None]` not `Generator[None, None, None]`** — Python 3.13 PEP 696 makes the send/return type arguments default to `None`. Ruff UP043 flags the explicit form. Using the short form is consistent with the project's `py313` target.
- **Removed doc 08's `# noqa: E402` comment** — it was specified verbatim in the spec but ruff 0.5+ no longer flags the import as E402 in this context. Removing it keeps ruff clean without changing semantics.

### Open questions

None from this sub-phase. conftest is complete and reusable for all remaining Phase 3 files.

### Next

Phase 3b: test_selection.py (TC-A1, TC-A2, TC-A3, TC-A10).

---

## 2026-04-20 — Phase 3a start: conftest + test_bubble.py plan (pre-action)

### Model / session
Sonnet 4.6 per model strategy. Bubble Sort tests are well-specified with explicit counter targets and straightforward tick structure.

### Plan
- Create `tests/conftest.py` verbatim from doc 08 §4.2
- Create `tests/unit/__init__.py` (empty)
- Create `tests/unit/test_bubble.py` with TC-A1, TC-A2, TC-A3, TC-A10, TC-A12

### Exit criteria
- `uv run pytest tests/unit/test_bubble.py -v` all green
- `uv run pyright tests/` clean
- `uv run ruff check tests/` + `uv run ruff format --check tests/` clean

---

## 2026-04-20 — DEVLOG restructure: archive-by-phase + tracker separation

### Worked on

Split the monolithic DEVLOG into an archive-by-phase structure to prevent context bloat as the project grows. Two archive files created under `docs/devlog/`:

- `phase_00_01.md` — all pre-Phase-2 entries (project state review through model strategy).
- `phase_02.md` — all Phase 2 entries (bubble 2a through heap 2d, including pre-action plans).

Main DEVLOG slimmed to: format guidance, archive summary table, current-phase entries, and the entry template. Pre-action plans preserved in archives for video journal use.

### Decisions

- **Archive by phase, not by date or size.** Phase boundaries are the natural unit of work in this project. Each archive file is self-contained and can be loaded independently.
- **Pre-action plans stay in the archive.** They are primary video journal material — showing the planning-before-coding methodology. Removing them would undercut the secondary project objective.
- **One-line summary per archived phase in main DEVLOG.** Gives orientation without forcing a full archive read. Links to archive files for drill-down.

### Open questions

- **IMPLEMENTATION_TRACKER needs Phase 2 completion evidence.** All four generators delivered but the tracker hasn't been updated yet.
- **T3 contiguity spec bug.** Needs resolution before Phase 3 TC-A19 authoring. Two resolution paths: message-prefix classification or sequencing-context classification.
- **libatomic1 resolved.** `sudo apt-get install libatomic1` was executed successfully. Pyright is now functional.
- **Fonts acquisition.** `scripts/fetch_fonts.sh` still needs to run on WSL host.

### Next

Update IMPLEMENTATION_TRACKER with Phase 2 completion. Then Phase 3 (algorithm unit tests) and Phase 4 (easing module) can begin — they are independent and can run in parallel per the implementation order.

---

## Entry Template (for future use)

```markdown
## YYYY-MM-DD — One-line session summary

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
