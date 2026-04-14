# DEVLOG — Visual Learning Sorting

**Purpose:** Chronological engineering journal. Each entry records the work performed, the decisions made (and their rationale), and the open questions remaining. This is the project's decision trail and the source material for the video journal.

**Format:** Newest entries at the top. Each session gets a dated heading. Within an entry: *Worked on*, *Decisions*, *Open questions*, *Next*. Entries are terse but complete — they should stand on their own when read six months from now or when scripted into narration.

---

## 2026-04-14 — Agentic-coder context and hallucination risk assessment (UNDER REVIEW)

### Worked on
Stepped back from coding momentum to evaluate whether the existing spec corpus — 4,521 lines / ~306K characters / ~75-80K tokens across 18 markdown files — is appropriately sized and structured for use with agentic coding tools (Claude Code, Cursor, Cline, and similar). The question was not whether the specs are *good* (they are deliberately thorough by methodology) but whether they are *machine-readable in the way agents actually read*.

Measured three density metrics against the corpus to ground the conversation in evidence rather than opinion:

- **Supersession events:** 14 decisions in `DECISIONS.md` are marked REVISED / REPLACED / superseded. D-017 → D-067 (universal orange highlight replaced per-algorithm accents), D-065/D-066 → D-068 (selection sort pointer assets), D-019 → D-074 (heap tree visualization), D-007 → D-056 (tick model), among others.
- **Cross-reference density:** 270 inter-document citations — 183 D-NNN decision references, 39 AT-NN acceptance test references, 48 TC-A test case references. Averages out to one cross-reference every 17 lines.
- **Distributed facts:** Counter accuracy table (Bubble 20/26, Selection 21/10, Insertion 17/19, Heap 20/30/35) appears in `CLAUDE.md` and is implicitly referenced elsewhere. Initial array `[4, 7, 2, 6, 1, 5, 3]` appears dozens of times across docs. Tick taxonomy (T0-T4) defined once in `03_DATA_CONTRACTS.md` but used everywhere.

### Identified risk vectors (for the record)
1. **Context dilution** — Loading 75-80K tokens of spec into a 200K-window agent leaves roughly one-quarter of the window for tool output, reasoning, and working code. On smaller-window agents (128K or less) this is already past comfort.
2. **Supersession blindness** — Agents grep by concept, not by decision chronology. A search for "accent color" finds the superseded D-017 rule first because it appears earlier in `DECISIONS.md`. The predictable failure mode: agent implements the superseded rule faithfully.
3. **Cross-reference hallucination** — When an agent sees "see D-058" but D-058 is not loaded in its working context, the common failure is not an error — it's a plausible-sounding fabrication of what D-058 says. Silent, hard to catch in code review.
4. **Worked-example drift** — `default_7` sorted traces appear in multiple docs. A partial-context agent can "verify" an implementation against the doc it has while violating another doc's more authoritative version.
5. **Vocabulary fragility** — T0-T4, OpType enum values, tick taxonomy terms are defined in one file. Partial-context agents infer meaning from usage rather than definition, producing occasional confident misuse.

### Proposed mitigations (pending decision)
Six mitigations were discussed, ordered by leverage:

- **High leverage, small effort:**
  - Supersession index at top of `DECISIONS.md` — flat table mapping superseded IDs → current binding IDs. ~30 lines. Eliminates supersession-blindness class entirely.
  - Per-phase context pack doc (`14_CONTEXT_PACKS.md`) naming exactly which files to load for each implementation phase. Cuts working context by 60-70% per task.
  - Inline `[STILL ACTIVE]` / `[SUPERSEDED BY D-NNN]` marker on each decision for machine-readable status.

- **Medium leverage:**
  - Root-level glossary in `03_DATA_CONTRACTS.md` defining T0-T4, OpType, SortResult, "tick," "sift-down," "pass," `default_7`, initial array, counter table. Eliminates vocabulary-fragility.
  - Counter table consolidation into exactly one location (proposed: `03_DATA_CONTRACTS.md`) with other docs linking rather than duplicating.

- **Structural:**
  - Project-specific skill file (`.claude/skills/vls-context/SKILL.md`) that forces context-loading order for any agent entering the repo.

### Explicitly rejected approaches
- **Do not** break large design docs into many small files — this worsens cross-reference chasing rather than improving it. Current doc sizes (none exceed ~600 lines) are well-scoped.
- **Do not** compress decision text for its own sake — D-064's length exists because the shortened version caused agent drift in the first place.

### Decisions
No binding decisions made this session. The assessment is complete and the proposed mitigations are on the table, but the author is reviewing whether to adopt them, and which subset, before committing.

This is deliberate: the context-pack approach implies a particular way of bounding agent tasks (explicit file-load lists per phase), and adopting it changes how subsequent phases will be executed. Worth making deliberately rather than reactively.

### Open questions
- **Which mitigations to adopt.** The high-leverage three (supersession index, context packs, active/superseded markers) address the two largest risk classes and are inexpensive; the medium-leverage two (glossary, counter consolidation) depend on the first three. The skill file is structural and only worth doing if the project will routinely be opened by agents rather than the author alone.
- **Whether to author the mitigations before or after Phase 1.** Argument for before: Phase 1 is the first real code and benefits most from bounded context. Argument for after: Phase 1 is small enough (`contracts.py` only) to fit easily in any agent's context regardless; delaying the mitigations until Phase 2 (algorithm generators, which have the highest risk of tick-sequence drift) is the minimum-regret path.
- **Whether the author intends to run this project primarily through agents, primarily by hand, or mixed.** The answer shapes how much mitigation effort is warranted. A solo hand-coded project with occasional agent assistance needs less infrastructure than a project where agents own entire phases.

### Next
Author review in progress. No immediate action. When the review concludes, proceed either with (a) authoring the chosen mitigations before Phase 1, or (b) starting Phase 1 with mitigations deferred.

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
