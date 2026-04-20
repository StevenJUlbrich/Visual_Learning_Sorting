# DEVLOG — Visual Learning Sorting

**Purpose:** Chronological engineering journal. Each entry records the work performed, the decisions made (and their rationale), and the open questions remaining. This is the project's decision trail and the source material for the video journal.

**Format:** Newest entries at the top. Each session gets a dated heading. Within an entry: *Worked on*, *Decisions*, *Open questions*, *Next*. Entries are terse but complete — they should stand on their own when read six months from now or when scripted into narration.

---

## 2026-04-19 — Model strategy for agentic implementation: Opus / Sonnet / Haiku assignment per phase

### Worked on
Evaluated each remaining project phase against the three available Claude models (Opus 4.6, Sonnet 4.6, Haiku 4.5) to optimize token cost without sacrificing output quality. The evaluation considered constraint density per phase, reasoning depth required, risk of subtle spec violations, and the mechanical vs. architectural nature of each task.

Additionally established a two-session workflow: Claude Code (VSCode/Ubuntu) handles implementation with the assigned model; this Cowork session (Opus) serves as the oversight/review layer with full spec context loaded. One algorithm at a time for Phase 2.

### Model assignments

**Opus 4.6 — high-constraint, multi-spec-intersection work (~30% of implementation):**

- Phase 2c: Insertion Sort generator — terminating-compare rule (`if j >= 0` at loop exit) is the highest-risk control-flow decision in the project; key-selection T1 does NOT increment comparisons. Pass-by-pass truth table exists specifically because agents get this wrong.
- Phase 2d: Heap Sort generator — two phases, recursive sift-down with `yield from`, two T3 variants distinguished by contiguity, D-058 parent-first highlight, counter reconciliation 20/30/35 with 6 excluded boundary ticks.
- Phase 5 (partial): `sprite.py` and `panel.py` — sprite identity-by-ID (Critical Rule #1), z-order, highlight state machine, per-algorithm motion signatures, header rhythm, completion styling all converge.
- Phase 6: Orchestrator — independent-queue model, operation-weighted timing, Heap rapid-cadence trigger, pause-during-interpolation, dt clamp. Open design question on Heap phase signaling.
- Oversight/review: This Cowork session remains on Opus for spec-level review of all deliverables.

**Sonnet 4.6 — well-specified, single-constraint-domain work (~55% of implementation):**

- Phase 2a: Bubble Sort generator — explicit pseudocode, straightforward loop shape, simple counter math.
- Phase 2b: Selection Sort generator — `(min_idx, j)` ordering and skip-swap rules are clearly specified.
- Phase 3: Algorithm unit tests — TC-A identifiers are prescriptive, counter table is the exit gate. Escalate TC-A19 sift-down segmentation helper to Opus only if Sonnet struggles.
- Phase 4: Easing module — pure math, smallest pack (~8K tokens), no cross-cutting constraints.
- Phase 5 (partial): `tree_layout.py`, `pointer.py`, `limitline.py`, `hud.py`, `window.py` — self-contained modules with clear specs.
- Phase 7: Main entry — config loading, Pygame init, event loop wiring. Low ambiguity.
- Phase 8: Integration tests — named test cases (TC-A15 through TC-A18), documented state machine.

**Haiku 4.5 — mechanical bookkeeping (~15% of implementation):**

- Phase 9: CI pipeline — GitHub Actions YAML from doc 11 spec. Boilerplate.
- All DEVLOG and tracker updates across every phase — structured append to established format.

**Human only:**

- Phase 10: Manual acceptance — real-monitor visual inspection of AT-01 through AT-27. Cowork (Opus) assists with check-off sheet organization and result recording.

### Decisions
- **Model-per-task, not model-per-session.** Claude Code supports model switching (`--model` flag or `/model` command). The implementation agent should switch models between algorithms rather than running everything on one model.
- **Oversight stays on Opus.** The review role needs full spec context and the ability to catch violations the implementation model missed. Catching a bug in review is cheaper than discovering it three phases later.
- **Escalation rule:** If Sonnet produces a deliverable that fails exit criteria after one correction attempt, escalate to Opus for that specific file rather than iterating further on Sonnet.
- **DEVLOG updates via Haiku.** The format is established, the content is known, no reasoning required. This is the single easiest token savings in the project.

### Open questions
- **Claude Code model switching friction.** Need to confirm the `/model` command or `--model` flag works smoothly mid-session in VSCode. If switching models requires restarting the session, the per-algorithm model switching may not be practical — in that case, run Bubble+Selection in one Sonnet session, then start a new Opus session for Insertion+Heap.
- **Haiku for DEVLOG in practice.** Haiku needs the existing DEVLOG format and the content to append handed to it explicitly. If the implementation agent is already Sonnet or Opus, it may be simpler to let that model write the DEVLOG entry inline rather than switching to Haiku for a 200-token append. Evaluate after the first algorithm.

### Next
Begin Phase 2a (Bubble Sort) in Claude Code with Sonnet. Bring the completed `bubble.py` back to this Cowork session for spec-level review before moving to Selection Sort.

---

## 2026-04-16 — Correction C verified: Heap Sort writes = 30 confirmed by independent trace

### Worked on
Independently verified Correction C (doc-03 Heap Sort writes ~22 → 30) by writing a step-by-step Python trace of `heap_sort_generator` on the default array `[4, 7, 2, 6, 1, 5, 3]`. The trace mirrors the pseudocode in `00_PSEUDOCODE.md` §4 exactly — every sift-down level, every swap, every T3 highlight — and logs the running writes counter at each mutation.

**Phase 1 — Build Max-Heap: 6 writes (3 swaps)**

- `sift_down(2, 7)`: arr[2]=2 swapped with arr[5]=5 → +2 (running: 2)
- `sift_down(1, 7)`: arr[1]=7 already largest → 0 (running: 2)
- `sift_down(0, 7)`: two-level descent — arr[0]=4↔arr[1]=7, then arr[1]=4↔arr[3]=6 → +4 (running: 6)

Max-heap: `[7, 6, 5, 4, 1, 2, 3]`

**Phase 2 — Extraction: 24 writes (6 root swaps + 6 sift-down repair swaps)**

| Extraction | Root swap | Sift-down repair swaps | Writes | Running |
|---|---|---|---|---|
| 1 | arr[0]↔arr[6] | 2 levels (root→1, 1→3) | 6 | 12 |
| 2 | arr[0]↔arr[5] | 1 level (root→2) | 4 | 16 |
| 3 | arr[0]↔arr[4] | 2 levels (root→1, 1→3) | 6 | 22 |
| 4 | arr[0]↔arr[3] | 1 level (root→1) | 4 | 26 |
| 5 | arr[0]↔arr[2] | 0 (heap holds) | 2 | 28 |
| 6 | arr[0]↔arr[1] | 0 (heap_size=1) | 2 | **30** |

**All three counters match CLAUDE.md binding table:** comparisons = 20, writes = 30, steps = 35 (with 6 boundary T3 ticks excluded per D-041).

The old doc-03 value of "~22" was counting swap *operations* (15 total swaps) rather than *array positions written* (15 × 2 = 30). The distinction is defined in doc 03 §Per-Operation Increment Rules: "A single swap operation modifies two array positions, so it counts as 2 writes."

### Decisions
- **Correction C signed off.** The ~22 → 30 change in doc-03 §Per-Algorithm Expected Write Totals is confirmed correct. The value now matches CLAUDE.md, 00_PSEUDOCODE.md §Counter reconciliation, and this independent trace.
- The trace script is disposable (not committed). The verification value lives in this DEVLOG entry and in the doc-03 table itself.

### Open questions
- None from this verification. All three doc-03 corrections (A: Bubble 8→13 swaps, B: highlight_indices order nuance, C: Heap ~22→30 writes) are now closed.

### Next
Phase 2 (algorithm generators) is fully unblocked. Four files to produce: `bubble.py`, `selection.py`, `insertion.py`, `heap.py` under `src/visualizer/models/`.

---

## 2026-04-14 — Phase 1 closed: contracts.py authored and verified; dogfood observations

### Worked on
Authored `src/visualizer/models/contracts.py` against the Phase 1 pack in `14_CONTEXT_PACKS.md`. The pack served as the dogfood test for the context-pack design. The file is 116 lines including docstrings: `OpType` enum with the six tick classes, `SortResult` dataclass with `slots=True` and fields in doc-03 order, and `BaseSortAlgorithm` ABC with `__init__(data, name, complexity)` and an abstract `sort_generator` method.

All four Phase 1 exit criteria verified:

1. `from visualizer.models.contracts import OpType, SortResult, BaseSortAlgorithm` succeeds with `PYTHONPATH=src`.
2. `pyright src/visualizer/models/contracts.py` → 0 errors, 0 warnings, 0 informations.
3. `ruff check` → clean after one fix (see judgment calls below).
4. `SortResult.__slots__` populated with exactly the six fields in the doc-03 order.

### Decisions made during authoring (the seven judgment calls identified in the earlier walkthrough)

- **`message` default** — required, no default. Every tick must carry human-readable text per doc 03 §Field Semantics. Implemented as a positional field.
- **`array_state` copy enforcement** — left to the generator. The dataclass does not add a `__post_init__` copy; enforcement is a contract at the generator boundary. Inline docstring calls this out explicitly.
- **`BaseSortAlgorithm.__init__` copy semantics** — `self.data = data.copy()` at construction, matching doc 03 §BaseSortAlgorithm Interface line 215 exactly. External callers cannot mutate the algorithm's view.
- **`name` and `complexity` as constructor parameters vs. ClassVar** — doc 03 explicitly defines them as `__init__` parameters. My earlier walkthrough suggested `ClassVar` as "reasonable"; the loaded spec overruled that. This is a good example of why the walkthrough is not the implementation — the walkthrough anticipated a decision the spec had already made.
- **`size` attribute** — computed once in `__init__` (`self.size = len(self.data)`). Matches doc 03 line 216.
- **Return type of `sort_generator`** — `Generator[SortResult]`, the PEP 696 default-elided form. See "Ruff UP043 fix" below.
- **`OpType` values via `auto()`** — matches doc 03 exactly. Integer values are fine for v1; serialization (if ever needed) is not a v1 concern.

### Ruff UP043 fix (divergence from doc 03 spec text)

Doc 03 §BaseSortAlgorithm Interface specifies the abstract method return type as `Generator[SortResult, None, None]`. Ruff in py313 mode flagged this as UP043 ("unnecessary default type arguments") because Python 3.13's `collections.abc.Generator` uses PEP 696 defaults, making `Generator[SortResult]` equivalent. Applied the ruff-suggested fix. The runtime behavior and type-checking semantics are identical; only the literal annotation string differs.

**Consequence for spec:** Doc 03 should be updated to reflect the 3.13-idiomatic form, or the ruff rule should be disabled project-wide. Low-priority cleanup — not blocking Phase 2. Recorded as an open question below.

### Dogfood observations on the Phase 1 pack

The pack was sufficient but revealed four observations worth recording:

1. **Spec inconsistency between doc 03 and CLAUDE.md / 00_PSEUDOCODE.md on Bubble Sort swap count.** Doc 03 §Per-Algorithm Expected Write Totals states "8 swaps (with early exit) = 16 writes" for `default_7`. CLAUDE.md's Counter Accuracy table states `Bubble Sort | 20 | 26`. My own trace of `[4, 7, 2, 6, 1, 5, 3]` through bubble with early exit produces 13 swaps (5+4+2+2), which is 26 writes — matching CLAUDE.md and 00_PSEUDOCODE.md, NOT matching doc 03. **Doc 03's table is wrong.** This does not affect contracts.py, but it will bite Phase 2 if the agent reads doc 03 before the counter sanity-check. Needs a correction to doc 03's table (8 → 13, 16 → 26) and a separate DEVLOG entry recording the correction. The Phase 2 pack already notes "CLAUDE.md Counter Accuracy table is the exit gate" — that framing was already correct; this observation just surfaces why the framing matters.

2. **Internal contradiction in doc 03 on `highlight_indices` order.** Line 5: "Order has no semantic meaning." But §Tick Taxonomy for Selection Sort says the tuple is `(min_idx, j)` with order implied, and D-058 plus §OpType.RANGE rules for Heap Sort mandate the parent as first element. The contract invariant exists for Heap Sort and Selection Sort (per-algorithm, tuple-order-sensitive); the blanket "order has no semantic meaning" is wrong. Suggest amending doc 03 to say "Order has no rendering semantics, but per-algorithm contracts may require a specific position for the lead index (see per-algorithm sections and D-058)."

3. **Pack input list was complete.** No additional files needed during authoring beyond the four named inputs (`03_DATA_CONTRACTS.md`, `00_PSEUDOCODE.md §Conventions`, `CLAUDE.md`, `pyproject.toml`) plus the four decision IDs. No additions proposed to the Phase 1 pack's Inputs section.

4. **Token budget estimate (~14K) held up.** The actual load was in that neighborhood; no surprises.

### Environment observations

- The dev sandbox does not allow UV to download the Python toolchain from GitHub releases (same proxy block that prevented font downloads). Installing tooling via `pip install --break-system-packages` against the system Python worked. This is a sandbox/CI-path issue, not a project issue; on the WSL host, `uv sync --dev` should work normally.
- Ruff 0.15.10 and Pyright were installed from PyPI without issue.
- Pyright required no additional configuration beyond the `[tool.pyright]` block in `pyproject.toml` (strict mode, include src + tests, py313 target).

### Open questions
- **Doc 03 swap count correction for Bubble Sort.** Update `8 swaps` → `13 swaps` and `16` → `26` in §Per-Algorithm Expected Write Totals. Small surgical edit; low risk. Consider bundling with the other doc-03 corrections (the `highlight_indices` ordering clarification). Timing: before Phase 2 starts.
- **Doc 03 update for `Generator[SortResult]` idiom.** Matches contracts.py, more modern, ruff-compatible. Alternatively disable UP043 project-wide if you prefer the explicit form for pedagogical clarity. Either is defensible.
- **No other surprises from Phase 1.** The pack-design proved sound on its first real test.

### Next
**Phase 2 (algorithm generators) is unblocked.** Before starting, consider closing the two doc-03 corrections identified above — both are small and both improve agent accuracy on the higher-stakes Phase 2 work. Alternatively, proceed to Phase 2 and record the corrections as known-good deviations.

---

## 2026-04-14 — Context-pack adoption: Supersession Index + 14_CONTEXT_PACKS.md authored

### Worked on
Closed the agent-context / hallucination mitigation item identified in the earlier 2026-04-14 assessment. Two concrete artifacts landed, plus a tracker update and this entry.

**Supersession Index** added to the top of `DECISIONS.md`. Six clean supersessions catalogued in a flat table: D-007→D-056 (tick model), D-017→D-067 (theme strategy), D-019→D-074 (Heap Sort flat-row constraint), D-054→D-067 (Heap accent color), D-065→D-068 (Selection minimum tracking), D-066→D-068 (Selection cursor distinction). The index explicitly distinguishes *superseded* decisions (old rule no longer binding) from *refined* decisions marked `(REVISED)` without a `REPLACED` or `SUPERSEDED by D-NNN` clause — the latter remain current binding and are intentionally excluded from the index to prevent over-correction.

**`14_CONTEXT_PACKS.md`** authored. Eleven packs, one per implementation phase (Phase 0 through Phase 10), structured-block format, deterministic file-path and decision-ID enumeration, no classifier or keyword inference. Each pack has sections for Intent, Inputs (spec files + decision IDs + upstream code files + test references), Expected Outputs, Approximate Token Budget, and Notes. An informal coverage test at the bottom lists twelve archetypal queries and names the pack(s) that answer each. An amendment protocol codifies when and how the document should change over time.

### Decisions
The six-question discussion from the earlier assessment entry resolved as follows:

- **Granularity:** Per-phase, not per-task. Eleven packs total. Tighter per-task packs were an option but were explicitly rejected — the phase boundary in `13_IMPLEMENTATION_ORDER.md` is already the unit of work.
- **Scope:** Each pack serves both forward (implementation) and backward (audit) modes. One pack per phase; audit mode adds the code outputs to the loaded set but does not require a separate pack entry.
- **Format:** Structured blocks (Option B) over bullet lists. Better machine-parseability, better for growth, clearer when presenting a pack to an audience.
- **Coverage test:** Informal. A bottom-of-document table of queries and expected packs. No pytest enforcement. Justified by the project's bounded scope — the pack set is not expected to grow.
- **Adoption mechanics:** Reference document only. No `.claude/skills/vls-context/SKILL.md`. Platform-neutral. `CLAUDE.md` is listed explicitly in every pack that needs it rather than assumed to be implicitly loaded, because different agent platforms handle `CLAUDE.md` differently.
- **Authoring order:** Before Phase 1 begins. Phase 1 is deliberately the dogfood test — it is small enough to work without a pack, so any pack-design flaw revealed during Phase 1 can be fixed before Phase 2 (the higher-stakes algorithm implementation) begins.
- **Supersession ID handling in packs:** Current binding IDs only. The Supersession Index in `DECISIONS.md` carries the full chain for audit reach-back.

### Open questions
- **Pack token-budget estimates are rough.** The notes include approximate token counts (14K for Phase 1, ~35K for Phase 2, ~45K for Phase 5). These are eyeballed from line counts, not measured against a tokenizer. If an agent run reveals a pack that actually overflows a working window, the budget figures need recalibration. Low-priority until a real overflow is observed.
- **Phase 5 may want sub-loading.** The view-layer pack is the largest (~45K tokens). The Notes section suggests sub-loading by view module (sprite alone vs. full view set), but this is advisory not prescriptive. If Phase 5 work in practice needs formal sub-packs, amend.
- **Phase 6 orchestrator rapid-cadence signal.** Still unresolved — whether the model carries a phase flag, whether the orchestrator infers from tick history, or whether a dedicated method is added. Flagged in Phase 6 Notes and carried forward from the earlier entry.

### Next
Phase 1 begins. Use the Phase 1 pack as the dogfood test. If any input proves missing or any expected output is wrong, fix the pack in place and note it here before proceeding.

---

## 2026-04-14 — Mempalace post-mortem and archive

### Worked on
Reviewed three legacy files at the repo root — `mempalace.yaml` (117 lines, keyword-driven configuration), `mempalace.yaml.bak` (24 lines, prose-description earlier version), and `entities.json` (6 lines, nearly empty). These were the surviving artifacts of an earlier attempt to solve the same retrieval-routing problem that is currently under consideration via the context-pack proposal. The `mempalace` package was a dev dependency in the original `pyproject.toml` (removed during the 2026-04-14 rewrite).

Archived all three files into `docs/AI_Conversations/mempalace-experiment/` with a companion `README.md` documenting the attempt, the specific failure modes identified, and the lessons inherited by the active context-pack design.

### Decisions
- **Archive rather than delete.** The artifacts earn their keep as teaching material — a worked example of a retrieval-routing attempt that failed, with diagnosis. This is high-value video journal content (failure modes are more instructive than success stories) and a concrete reminder of design pitfalls when the context-pack design begins.
- **Do not revive.** The underlying mismatch — keyword taxonomy cannot express task-shaped queries over a cross-referenced corpus — is not solved by tuning keywords. A revival would repeat the failure.
- **Root cleanliness.** Archiving removes three files from repo root that had no active role, reducing noise for anyone (human or agent) doing initial orientation via `ls`.

### Failure modes documented (for posterity and for the context-pack design)
1. Keyword ambiguity at scale — a single realistic query matched four rooms simultaneously with no tie-breaker.
2. Taxonomy dimension (by document type) orthogonal to query dimension (by task).
3. Keywords cannot traverse cross-references; the spec is a graph, not a set.
4. Room coverage was incomplete; load-bearing files (`CLAUDE.md`, pseudocode) landed in the `general` catch-all.
5. Iteration moved from prose descriptions to keywords — a move toward mechanization that *reduced* accuracy, signaling the mechanism itself was wrong.
6. No measurement loop — no log of queries tried, classifications returned, or accuracy. The YAML broke silently and got shelved without diagnosis.

### Lessons carried forward into the context-pack design (pending adoption)
- Group by **implementation phase**, not document type.
- **Enumerate file paths explicitly**; no classifier, no keyword matching.
- **Name cross-references by ID** (D-NNN, TC-A-NN, AT-NN) so they can be fetched deterministically.
- Define a **coverage test** — a list of archetypal queries that each named pack must answer. Break is detected immediately, not months in.

### Open questions
None from this session. The mempalace chapter is closed; the lessons are captured.

### Next
Resume discussion of the context-pack proposal (currently marked UNDER REVIEW in the 2026-04-14 assessment entry below), now informed by the mempalace lessons.

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
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           