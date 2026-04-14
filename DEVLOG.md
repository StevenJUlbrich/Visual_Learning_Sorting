# DEVLOG — Visual Learning Sorting

**Purpose:** Chronological engineering journal. Each entry records the work performed, the decisions made (and their rationale), and the open questions remaining. This is the project's decision trail and the source material for the video journal.

**Format:** Newest entries at the top. Each session gets a dated heading. Within an entry: *Worked on*, *Decisions*, *Open questions*, *Next*. Entries are terse but complete — they should stand on their own when read six months from now or when scripted into narration.

---

## 2026-04-14 — Phase 0 closeout: pyproject, config, pseudocode, implementation order, fonts helper

### Worked on
Closed the bulk of Phase 0 gaps in a single session following the tracker audit. The day's output was five concrete artifacts: a path-reconciliation decision (D-080), a full `pyproject.toml` rewrite, a `config.toml` rewrite to the preset-based shape, a comprehensive algorithm pseudocode reference (`00_PSEUDOCODE.md`), an implementation-order blueprint (`13_IMPLEMENTATION_ORDER.md`), and a version-pinned fonts acquisition helper (`scripts/fetch_fonts.sh`).

### Decisions
- **D-080 (locked):** Source package lives at `src/visualizer/`, not `visual_sort/src/`. Every spec file already referenced `src/visualizer/`; the prior empty scaffold at `visual_sort/` was the outlier. Renaming empty directories is cheaper than rewriting 4,000 lines of spec. Distribution name remains `visual-learning-sorting`, import name is `visualizer`.
- `pyproject.toml` uses hatchling as the build backend with `[tool.hatch.build.targets.wheel].packages = ["src/visualizer"]`. Pytest markers copied verbatim from doc 08 §4.3. Ruff targets py313 with isort + pyupgrade + bugbear + simplify rule groups. Pyright is strict, with the three "unknown" categories downgraded to warning so partial pygame stubs don't block CI.
- `config.toml` dropped the obsolete `orientation = "landscape"` / `"portrait"` shape. Replaced with `preset = "desktop"` per D-018 (preset-based resolution selection) and D-079 (no portrait orientation in v1). The two valid values are `"desktop"` (1280×720) and `"tablet"` (1024×768).
- `00_PSEUDOCODE.md` is numbered `00_` deliberately so it precedes all other design docs in the read order. It is now the single source of truth for generator control flow. Animation contracts define *what ticks look like*; pseudocode defines *when ticks are emitted*.
- Insertion Sort's terminating-compare rule (`if j >= 0` at loop exit) is written out with a pass-by-pass truth table for `default_7`, because this is the specific rule TC-A14 tests and the most likely source of cmp=13 or cmp=21 drift if an implementer gets it wrong.
- Heap Sort sift-down is written as a reusable helper rather than inlined, because Phase 1 (build-heap) and Phase 2 (extraction repair) both call it. The contiguous-vs-non-contiguous `highlight_indices` distinction for boundary T3 vs. Logical Tree T3 is stated explicitly because TC-A19's trace segmentation depends on it.

### Open questions
- **Fonts acquisition on the sandbox.** The dev sandbox proxy rejected GitHub release binary downloads (curl exit 56 post-TLS-handshake). Not a project-level issue — on the WSL host, `scripts/fetch_fonts.sh` will close it. Worth noting in case a CI job ever needs to install fonts from behind a similar allowlist; the workflow may need to vendor the TTFs into the repo or proxy them through a permitted CDN.
- **`main.py` at repo root vs. inside the package.** Currently a six-line stub at the root. Phase 7 will need to move it to `src/visualizer/main.py` so `[project.scripts] visual-sort = "visualizer.main:main"` resolves. Decision deferred to that phase.
- **Rapid-cadence timing in the controller.** The orchestrator needs to distinguish between "sift-down during Phase 1 build" (standard cadence) and "sift-down after extraction swap" (rapid cadence: T1=100, T2=250, T3=130). The pseudocode notes this is a controller concern, but the exact signal — phase flag on the generator vs. inferred from tick history — is a Phase 6 decision.

### Next
Single remaining Phase 0 action: run `bash scripts/fetch_fonts.sh` on the WSL host to place the three TTFs. After that, Phase 1 (`contracts.py`) is unblocked.

---

## 2026-04-14 — Project state review and methodology realignment

### Worked on
Full state audit of the project. Finding: 142 tracked items across 10 phases, all open; 4,000 lines of design documentation and 79 locked decisions; zero lines of implementation code. Source scaffold at `visual_sort/src/` was empty and in conflict with `src/visualizer/` references throughout the specs. Fonts directory contained only a README.

### Decisions
- The project is operating in a **blueprint-first** methodology: complete the specification, simulate it, and only then write code. This is an intentional engineering choice — the cost of rewriting tick-sequence-bound animation contracts or counter-accuracy-bound generators is high, and the cost of up-front simulation is cheap by comparison. The project is not in "paralysis" — it is in disciplined pre-implementation.
- A secondary objective of the project is a **video journal** documenting the engineering methodology itself. This DEVLOG is the raw material for that journal. It is written for a future reader — potentially the author, potentially an audience — who needs to understand not just what was done but why.
- Two reference artifacts are added alongside the existing docs set: `NORTH_STAR.md` (executive project blueprint, one page) and `DEVLOG.md` (this file — dated engineering journal). Neither replaces anything; both compress the existing spec set into retrieval-optimized forms.

### Open questions
- Should the video journal's audience be stated explicitly in `NORTH_STAR.md` — peer engineers, career-change learners, the general dev-curious public? The framing of the journal entries may change depending on the answer.
- Where should the project's origin story live? The context (20 years at JPM Chase, motivation to teach disciplined spec-first development in contrast to prevailing "vibe coding" practice) is material for the video journal but not for the design docs. Likely belongs in a separate `docs/AI_Conversations/` entry or in a dedicated `docs/VIDEO_JOURNAL/` directory.

### Next
Proceed with Phase 0 closeout (see next entry, which is the same date).

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
