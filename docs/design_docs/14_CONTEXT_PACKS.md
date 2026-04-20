# 14 CONTEXT PACKS — Phase-Bound Reading Lists

**Status:** Locked. Authoritative index for what to load per phase.
**Scope:** One pack per implementation phase (Phase 0 through Phase 10), aligned with `13_IMPLEMENTATION_ORDER.md`. Each pack names the exact files and decision IDs required to work on that phase — either in **forward mode** (implementation) or **backward mode** (audit/review).

## How to Use This Document

Every pack entry is **deterministic**: file paths are explicit, decision IDs are named. There is no classifier, no keyword matching, no inference. Load what the pack says, nothing more.

**Forward mode.** You are writing this phase's code. Load every file in the `Inputs` section. The `Expected outputs` section is your checklist of files to produce. The `Notes` section flags phase-specific traps and constraints.

**Backward mode (audit).** This phase is complete. Load the `Inputs` plus every file in `Expected outputs`. Verify the outputs comply with the inputs. The `Notes` section names the specific failure modes to look for.

**Decision ID handling.** Packs reference only current binding decisions. If you encounter a superseded ID (D-007, D-017, D-019, D-054, D-065, D-066), consult the Supersession Index at the top of `DECISIONS.md` and apply the current binding rule instead.

**Platform neutrality.** `CLAUDE.md` is listed explicitly in every pack that needs it rather than treated as implicitly loaded. Different agent platforms handle `CLAUDE.md` differently; explicit listing is deterministic.

---

## Pack — Phase 0 · Pre-Coding Gaps (Audit)

**Intent:** Verify that all spec-completion gaps identified in the 2026-04-05 readiness review are closed. This pack is primarily useful in backward mode — Phase 0 is mostly done, but audit is still valuable when returning to the project.

**Inputs:**
- Spec files:
  - `NORTH_STAR.md`
  - `CLAUDE.md`
  - `docs/design_docs/DECISIONS.md` (Supersession Index + D-078, D-079, D-080)
  - `docs/design_docs/13_IMPLEMENTATION_ORDER.md`
  - `docs/design_docs/00_PSEUDOCODE.md`
  - `TODO/IMPLEMENTATION_TRACKER.md` (Phase 0 section)
- Decision IDs: **D-018**, **D-077**, **D-079**, **D-080**
- Upstream code files: none
- Test references: none

**Expected outputs (all already produced except fonts):**
- `pyproject.toml` — hatchling build, pygame ≥ 2.5, pytest markers, ruff, pyright configs
- `config.toml` — `[window] preset = "desktop"`
- `src/visualizer/{__init__,models/__init__,views/__init__,controllers/__init__}.py`
- `tests/__init__.py`
- `docs/design_docs/00_PSEUDOCODE.md`
- `docs/design_docs/13_IMPLEMENTATION_ORDER.md`
- `docs/design_docs/14_CONTEXT_PACKS.md` (this file)
- `scripts/fetch_fonts.sh`
- `assets/fonts/{Inter-Bold,Inter-Regular,FiraCode-Regular}.ttf` (pending host-side run of `scripts/fetch_fonts.sh`)

**Approximate token budget:** ~18K tokens (NORTH_STAR + CLAUDE + pseudocode + implementation order + Phase 0 tracker section).

**Notes:**
- Only open item is fonts acquisition. SysFont fallback per doc 04 §3.3 keeps the app functional in the interim.
- Path layout is `src/visualizer/` per D-080; the earlier `visual_sort/src/` scaffold was removed.

---

## Pack — Phase 1 · Data Contracts and Base Classes

**Intent:** Produce `contracts.py` — the type surface every downstream phase imports. This is the smallest phase and serves as the dogfood test for this context-pack design.

**Inputs:**
- Spec files:
  - `docs/design_docs/03_DATA_CONTRACTS.md` (entire file)
  - `docs/design_docs/00_PSEUDOCODE.md` (Conventions section only)
  - `CLAUDE.md` (Critical Rules + SortResult Contract sections)
  - `pyproject.toml` (ruff + pyright config for local compliance)
- Decision IDs: **D-002** (MVC structure), **D-011** (array state copies), **D-020** (no exceptions), **D-041** (T3 excluded from step count)
- Upstream code files: none (this is the first coding phase)
- Test references: none (Phase 3 is where tests land)

**Expected outputs:**
- Code: `src/visualizer/models/contracts.py` containing:
  - `OpType` enum: `COMPARE`, `SWAP`, `SHIFT`, `RANGE`, `TERMINAL`, `FAILURE`
  - `SortResult` dataclass with `slots=True` and fields per doc 03
  - `BaseSortAlgorithm` ABC with `data`, `size`, `comparisons`, `writes`, `name`, `complexity`, and abstract `sort_generator` method returning `Generator[SortResult, None, None]`
- Tests: none this phase
- Artifacts: none

**Approximate token budget:** ~14K tokens.

**Notes:**
- Must typecheck clean under pyright's strict mode.
- Must not import `pygame`.
- `SortResult` must use `@dataclass(slots=True)` for memory efficiency.
- Phase 1 is deliberately small enough to fit in any agent's context without the pack strictly being necessary — it is the **dogfood test** for the pack design itself. If authoring Phase 1 against this pack reveals missing inputs, note them in DEVLOG and adjust the pack before Phase 2.

---

## Pack — Phase 2 · Algorithm Generators (Model Layer)

**Intent:** Implement the four generators (`bubble.py`, `selection.py`, `insertion.py`, `heap.py`) with tick sequences matching `00_PSEUDOCODE.md` exactly.

**Inputs:**
- Spec files:
  - `docs/design_docs/00_PSEUDOCODE.md` (entire file — this is the canonical control-flow spec)
  - `docs/design_docs/03_DATA_CONTRACTS.md`
  - `docs/design_docs/05_ALGORITHMS_VIS_SPEC.md`
  - `docs/contracts/BUBBLE_SORT_ANIMATION.md`
  - `docs/contracts/SELECTION_SORT_ANIMATION.md`
  - `docs/contracts/INSERTION_SORT_ANIMATION.md`
  - `docs/contracts/HEAP_SORT_ANIMATION.md`
  - `CLAUDE.md` (Counter Accuracy table)
- Decision IDs (model-relevant only — view-layer decisions are in the Phase 5 pack):
  - **D-003** (four algorithms in v1)
  - **D-006** (initial array `[4, 7, 2, 6, 1, 5, 3]`)
  - **D-011** (array copies in every tick)
  - **D-020** (no exceptions — use T0 failure tick)
  - **D-041** (T3 does not increment step counter)
  - **D-056** (independent queues, operation-weighted timing)
  - **D-058** (Heap T3 must include parent as first element of `highlight_indices`)
  - **D-060**, **D-064** (Insertion Sort sequential shift — never batch)
  - **D-065**, **D-066** → see Supersession Index; current binding is **D-068** for Selection pointer semantics, but the T1 tuple order `(min_idx, j)` is the model-relevant rule
- Upstream code files: `src/visualizer/models/contracts.py`
- Test references: TC-A6 through TC-A19 (Phase 3 will implement)

**Expected outputs:**
- Code:
  - `src/visualizer/models/bubble.py`
  - `src/visualizer/models/selection.py`
  - `src/visualizer/models/insertion.py`
  - `src/visualizer/models/heap.py`
- Tests: none this phase (Phase 3 produces them)
- Artifacts: none

**Approximate token budget:** ~35K tokens. This is one of the larger packs.

**Notes:**
- **Counter accuracy table is the exit gate.** Bubble 20/26, Selection 21/10, Insertion 17/19, Heap 20/30/35. If a generator produces different counters for `default_7`, it does not pass.
- **Insertion Sort's terminating-compare rule** (`if j >= 0` at loop exit) is the single highest-risk control-flow decision. The pseudocode §3 includes a pass-by-pass truth table; refer to it when TC-A14 is eventually authored.
- **Heap Sort's T3 contiguity distinction** (boundary T3 is contiguous `range(0, k)`; Logical Tree T3 is non-contiguous triangle) is what TC-A19 uses to segment the trace. Do not conflate the two variants.
- **No exceptions.** Empty-input handling yields a single T0 failure tick and returns. Any `raise` in a generator is a spec violation.
- **Array copies, not references.** Every tick with `array_state` must `list(arr)`, not `arr`.

---

## Pack — Phase 3 · Algorithm Unit Tests

**Intent:** Verify Phase 2 generators via automated tick-sequence and counter-accuracy tests (TC-A6 through TC-A19).

**Inputs:**
- Spec files:
  - `docs/design_docs/08_TEST_PLAN.md` (TC-A6 through TC-A19 sections)
  - `docs/design_docs/00_PSEUDOCODE.md` (Invariants sections per algorithm)
  - `docs/design_docs/03_DATA_CONTRACTS.md`
  - `docs/design_docs/07_ACCEPTANCE_TESTS.md` (AT-09 through AT-23 for cross-reference)
  - `pyproject.toml` (pytest markers: `unit`, `integration`, `slow`)
  - `CLAUDE.md` (Counter Accuracy table — reproduce exactly)
- Decision IDs: same as Phase 2 (the tests verify those decisions)
- Upstream code files:
  - `src/visualizer/models/contracts.py`
  - `src/visualizer/models/bubble.py`
  - `src/visualizer/models/selection.py`
  - `src/visualizer/models/insertion.py`
  - `src/visualizer/models/heap.py`
- Test references: TC-A6 through TC-A19 (this phase implements them)

**Expected outputs:**
- Tests:
  - `tests/models/test_bubble.py`
  - `tests/models/test_selection.py`
  - `tests/models/test_insertion.py`
  - `tests/models/test_heap.py`
- All tests marked `@pytest.mark.unit`.
- `tests/conftest.py` with `SDL_VIDEODRIVER=dummy` / `SDL_AUDIODRIVER=dummy` os.environ setup (safety net even for unit tests per doc 09 §3).

**Approximate token budget:** ~22K tokens.

**Notes:**
- **The tests must reproduce the CLAUDE.md counter table exactly.** Any deviation is a Phase 2 bug, not a test bug.
- **TC-A14** is the Insertion Sort terminating-compare truth-table test. Uses the per-pass expectations from `00_PSEUDOCODE.md §3`.
- **TC-A19** requires a helper that segments the Heap trace into sift-down levels by T3 **message prefix** (D-081). Do not use contiguity — it fails for parent=0 sift-downs. The helper skeleton is given in the test plan; do not reinvent it.
- Runs headlessly — no `pygame.display` required for model tests.

---

## Pack — Phase 4 · Easing Module

**Intent:** Pure-math easing primitives (no Pygame dependency) usable by the View layer.

**Inputs:**
- Spec files:
  - `docs/design_docs/10_ANIMATION_SPEC.md` (easing function definitions)
  - `docs/design_docs/08_TEST_PLAN.md` §4.4 (no-pygame-import constraint)
- Decision IDs: none specific to easing math
- Upstream code files: none
- Test references: TC-A5 (easing unit test)

**Expected outputs:**
- Code: `src/visualizer/views/easing.py` — functions `ease_in_out_quad`, `ease_out_cubic`, `sine_arc` (and any others specified in doc 10)
- Tests: `tests/views/test_easing.py`

**Approximate token budget:** ~8K tokens. Smallest pack in the project.

**Notes:**
- **`grep -l "import pygame" src/visualizer/views/easing.py` must return empty.** This is the test-plan invariant that makes TC-A5 runnable without display init.
- Runs in parallel with Phases 2 and 3 — no shared code with the algorithm layer.
- Pure Python stdlib only. No numpy, no external math libraries.

---

## Pack — Phase 5 · View Layer

**Intent:** Rendering primitives — panels, sprites, pointers, tree layout, HUD, limit line, phase labels.

**Inputs:**
- Spec files:
  - `docs/design_docs/04_UI_SPEC.md` (entire file — layout, colors, fonts, header rhythm)
  - `docs/design_docs/10_ANIMATION_SPEC.md` (sprite motion, easing, per-algorithm motion signatures)
  - `docs/design_docs/12_ANIMATION_FOUNDATION.md` (shared rendering contracts — sprite identity, z-order, highlight state machine)
  - `docs/contracts/BUBBLE_SORT_ANIMATION.md`
  - `docs/contracts/SELECTION_SORT_ANIMATION.md`
  - `docs/contracts/INSERTION_SORT_ANIMATION.md`
  - `docs/contracts/HEAP_SORT_ANIMATION.md`
  - `docs/design_docs/03_DATA_CONTRACTS.md` (OpType and SortResult consumed by renderer)
  - `CLAUDE.md` (universal orange, panel background, z-order rules)
  - `config.toml` (preset loading)
- Decision IDs (view-relevant):
  - **D-004** (sprite entities with float coordinate tracking)
  - **D-005** (2×2 grid, max four panels)
  - **D-067** (universal active highlight `(255, 140, 0)` — note: supersedes D-017 and D-054)
  - **D-068** (Selection Sort pointer assets i/j/min — note: supersedes D-065, D-066)
  - **D-069** (sprite circular ring shape, 3px stroke)
  - **D-070** (no algorithm title dots)
  - **D-071** (Insertion Sort KEY label)
  - **D-072** (Insertion Sort gap as empty space)
  - **D-073** (Insertion Sort color-only boundary)
  - **D-074** (Heap Sort binary tree visualization — note: supersedes D-019 flat-row constraint)
  - **D-075** (Heap Sort phase label — BUILD MAX-HEAP / EXTRACTION)
  - **D-076** (Heap Sort heap boundary dashed line)
  - **D-077** (fixed window size, no RESIZABLE)
  - **D-078** (completion green panel background)
  - **D-079** (no portrait — two landscape presets only)
- Upstream code files:
  - `src/visualizer/models/contracts.py`
  - `src/visualizer/views/easing.py`
- Test references: AT-01 through AT-08, AT-17, AT-18 (visual acceptance, backstopped by Phase 10 manual walkthrough)

**Expected outputs:**
- Code:
  - `src/visualizer/views/window.py` — display init, 2×2 grid math
  - `src/visualizer/views/panel.py` — per-algorithm frame + header
  - `src/visualizer/views/sprite.py` — `NumberSprite` class
  - `src/visualizer/views/tree_layout.py` — Heap binary tree node positioning
  - `src/visualizer/views/pointer.py` — Selection Sort i/j/min arrow assets
  - `src/visualizer/views/limitline.py` — Bubble Sort boundary line
  - `src/visualizer/views/hud.py` — counter overlays, Heap phase label
- Tests: view-layer smoke tests are optional at this phase; formal acceptance is Phase 10.

**Approximate token budget:** ~45K tokens. Largest pack in the project. Consider loading on a per-module basis if working on a single view file.

**Notes:**
- **Universal orange is non-negotiable.** Anyone reading an older doc or contract fragment may encounter "per-algorithm accent colors" — that rule was superseded by D-067. Never implement per-algorithm colors.
- **Selection Sort requires both pointers AND color highlights** (D-068 refines D-065/D-066 to use both, not highlight-only). The three labeled arrows are required assets.
- **Heap Sort is a binary tree, not a flat row.** The D-019 flat-row-only constraint was superseded by D-074. Implement tree layout from the start.
- **Fonts may be missing.** SysFont fallback per doc 04 §3.3 keeps rendering functional; accept the metric differences.
- **No RESIZABLE flag.** D-077 locks window size at startup. Do not add resize handlers.
- Given the token budget, consider sub-loading: to implement `sprite.py`, load only `12_ANIMATION_FOUNDATION.md`, `04_UI_SPEC.md §3` (fonts/colors), `03_DATA_CONTRACTS.md`, plus D-067, D-069. Skip the four per-algorithm contracts until implementing `panel.py`.

---

## Pack — Phase 6 · Controller (Orchestrator)

**Intent:** Event loop with independent per-algorithm queues, operation-weighted timing, and the play/pause/step/restart state machine.

**Inputs:**
- Spec files:
  - `docs/design_docs/06_BEHAVIOR_SPEC.md` (entire file — controls, operation timing, panel state machine)
  - `docs/design_docs/02_ARCHITECTURE.md` (independent queue semantics)
  - `docs/design_docs/08_TEST_PLAN.md` §4.4 (Controller testability contract — no pygame.display dependency)
  - `docs/design_docs/03_DATA_CONTRACTS.md` (SortResult consumed by controller)
  - `CLAUDE.md` (operation timing constants: T1=150, T2=400, T3=200, Heap rapid-cadence T1=100/T2=250/T3=130; dt clamp rule)
- Decision IDs:
  - **D-056** (independent operation queues — current binding, supersedes D-007)
  - **D-016** (failure deactivates only the failing algorithm)
  - **D-041** (T3 excluded from step count)
  - **D-078** (completion panel freezes stats)
- Upstream code files:
  - `src/visualizer/models/contracts.py`
  - `src/visualizer/models/{bubble,selection,insertion,heap}.py`
  - `src/visualizer/views/*.py`
- Test references: TC-A15, TC-A16, TC-A17, TC-A18 (Phase 8 will implement)

**Expected outputs:**
- Code: `src/visualizer/controllers/orchestrator.py`
- Tests: none this phase (Phase 8 produces them)

**Approximate token budget:** ~20K tokens.

**Notes:**
- **`dt = min(clock.tick(60), 33)`** — the dt clamp is CLAUDE.md's Critical Rule #7. Without it, a single slow frame causes sprite overshoot.
- **Operation timings are integer milliseconds.** Float timings invite rounding drift across many ticks.
- **Heap rapid-cadence trigger.** The reduced timeline (T3=130, T1=100, T2=250) applies to sift-downs that occur *after* an extraction swap in Phase 2. The model emits ticks identically in both phases; the orchestrator consults tick context and phase to pick the timing. How to signal phase — via a flag on the generator, via tick-history inference, or via a separate method — is an open Phase 6 design decision. See DEVLOG 2026-04-14 open questions.
- **Controller must be testable without `pygame.display`.** Extract queue-timing logic into methods that accept `dt` and mock generators per doc 08 §4.4.

---

## Pack — Phase 7 · Main Entry and Config Loading

**Intent:** Wire the four panels, orchestrator, and Pygame event loop into a runnable app. Load `config.toml` to select resolution preset.

**Inputs:**
- Spec files:
  - `docs/design_docs/02_ARCHITECTURE.md` (config + runtime targets section)
  - `docs/design_docs/09_DEV_ENV.md` §8 (config.toml loader shape)
  - `docs/design_docs/06_BEHAVIOR_SPEC.md` (app lifecycle, quit handling)
  - `config.toml` (the file being loaded)
  - `pyproject.toml` (`[project.scripts]` entry)
- Decision IDs:
  - **D-018** (two resolution presets: desktop 1280×720, tablet 1024×768)
  - **D-077** (fixed window size, no RESIZABLE)
  - **D-079** (landscape only, no portrait)
- Upstream code files:
  - `src/visualizer/controllers/orchestrator.py`
  - `src/visualizer/models/*.py`
  - `src/visualizer/views/*.py`
- Test references: none formal; manual smoke via `uv run visual-sort`.

**Expected outputs:**
- Code: `src/visualizer/main.py` exposing `main()` (referenced by `[project.scripts] visual-sort`)
- Tests: none this phase

**Approximate token budget:** ~12K tokens.

**Notes:**
- **`main.py` migrates from repo root into the package.** The current stub at `/main.py` is legacy; delete it once `src/visualizer/main.py` is working.
- **Missing config.toml defaults to desktop** per doc 09 §8.
- **Invalid `preset` value should not crash** — log a warning and fall back to desktop.
- The `tomllib` module is stdlib in Python 3.11+; no external TOML dependency needed.

---

## Pack — Phase 8 · Integration Tests

**Intent:** Controller/View interaction tests — pause freezes interpolation, restart resets state, steps respect queue independence.

**Inputs:**
- Spec files:
  - `docs/design_docs/08_TEST_PLAN.md` (TC-A15 through TC-A18 sections)
  - `docs/design_docs/06_BEHAVIOR_SPEC.md` (state machine for pause/play/step/restart)
  - `docs/design_docs/09_DEV_ENV.md` §3 (headless testing setup)
  - `CLAUDE.md` (operation timing)
- Decision IDs: same as Phase 6 (tests verify those)
- Upstream code files:
  - `src/visualizer/controllers/orchestrator.py`
  - `src/visualizer/views/*.py`
- Test references: TC-A15, TC-A16, TC-A17, TC-A18 (this phase implements)

**Expected outputs:**
- Tests:
  - `tests/integration/test_controller_play_step.py`
  - `tests/integration/test_pause_resume.py`
  - `tests/integration/test_restart.py`
- All tests marked `@pytest.mark.integration`.

**Approximate token budget:** ~14K tokens.

**Notes:**
- Runs under `SDL_VIDEODRIVER=dummy` per doc 09 §3.
- `conftest.py` at `tests/` already sets the env vars as a safety net; the primary path is shell-level.
- These tests may instantiate a real `Orchestrator` against mock generators to isolate timing logic from the algorithm layer.

---

## Pack — Phase 9 · CI Pipeline

**Intent:** GitHub Actions workflow that runs ruff, pyright, and the full test suite on every push and pull request.

**Inputs:**
- Spec files:
  - `docs/design_docs/11_CI.md` (workflow shape, matrix, gates)
  - `docs/design_docs/09_DEV_ENV.md` §3 (headless env vars at job level)
  - `pyproject.toml` (tool configs CI must honor)
- Decision IDs: none
- Upstream code files: all prior phase outputs
- Test references: all TC-A and AT tests runnable under headless

**Expected outputs:**
- `.github/workflows/ci.yml`
- Optional: a `Makefile` or `justfile` for local-CI parity

**Approximate token budget:** ~6K tokens.

**Notes:**
- `SDL_VIDEODRIVER=dummy` and `SDL_AUDIODRIVER=dummy` must be set at the job `env:` block, not just per-step — ensures Pygame imports during test collection don't crash.
- Ruff, pyright, and pytest are the three gates. All must pass to merge.
- Pin Python to 3.13 in the CI matrix to match `requires-python`.

---

## Pack — Phase 10 · Manual Acceptance

**Intent:** Human verification on real hardware that AT-01 through AT-27 pass at both the Desktop and Tablet presets.

**Inputs:**
- Spec files:
  - `docs/design_docs/07_ACCEPTANCE_TESTS.md` (AT-01 through AT-27)
  - `docs/design_docs/04_UI_SPEC.md` (preset layout expectations)
  - `docs/contracts/{BUBBLE,SELECTION,INSERTION,HEAP}_SORT_ANIMATION.md` (visual correctness criteria)
- Decision IDs: all visual and behavioral decisions (effectively every D-NNN referenced in Phases 5 and 6)
- Upstream code files: the full running app
- Test references: AT-01 through AT-27

**Expected outputs:**
- A manual check-off sheet (format author's choice — could be a fresh markdown file in `TODO/`, a spreadsheet, or annotations on `07_ACCEPTANCE_TESTS.md`).

**Approximate token budget:** ~12K tokens for the acceptance doc itself; visual inspection is the actual load.

**Notes:**
- Run on real hardware, not in WSL, if possible — `SDL_VIDEODRIVER=dummy` is for automation, not for human acceptance.
- AT-17 requires `preset = "tablet"` in config.toml; AT-18 requires `preset = "desktop"`. Switch config and re-launch between the two.
- Any AT failure cycles back to the responsible phase rather than being patched at this layer.

---

## Coverage Test — Archetypal Queries

This section exists because the mempalace experiment failed partly from the absence of a feedback loop. Each query below names the pack(s) that should answer it. If a real query arrives that cannot be answered from any single pack, the pack design is broken and must be amended before proceeding.

| Query | Answering Pack(s) |
| :--- | :--- |
| "Implement Insertion Sort's generator." | Phase 2 |
| "Verify the Heap Sort counter accuracy table." | Phase 3 |
| "Write the `ease_out_cubic` function." | Phase 4 |
| "Render a Selection Sort `min` pointer." | Phase 5 |
| "Where does the dt clamp go?" | Phase 6 |
| "Load config.toml and pick a resolution." | Phase 7 |
| "Pause during a T2 swap — what should happen?" | Phase 6 + Phase 8 |
| "Which decisions govern Heap Sort's tree layout?" | Phase 5 (D-074, D-075, D-076) |
| "Is there a color accent for Bubble Sort?" | Phase 5 (D-067 — universal orange, superseded any per-algorithm color) |
| "What files does the CI need to gate on?" | Phase 9 |
| "Which acceptance tests cover the Tablet preset?" | Phase 10 (AT-17) |
| "Did Phase 0 close properly?" | Phase 0 (audit mode) |

**Rule:** If a query requires pulling files from more than two packs, that query is either cross-phase (expected — e.g., pause-during-swap spans controller and integration) or it represents a missing pack. Record any mismatch in DEVLOG and adjust this document before continuing the affected work.

---

## Amendment Protocol

This document is living. When to amend:

1. **New phase added to `13_IMPLEMENTATION_ORDER.md`** → new pack here