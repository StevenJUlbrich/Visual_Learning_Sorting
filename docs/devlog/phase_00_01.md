# DEVLOG Archive — Phases 0 and 1

**Archived from:** `DEVLOG.md` on 2026-04-20 during the DEVLOG restructure.
**Covers:** Project state review, Phase 0 closeout, agentic risk assessment, mempalace post-mortem, context-pack adoption, Phase 1 (contracts.py), doc-03 corrections, model strategy.
**Entries:** Newest first, preserving original format.

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

**Human only:**

- Phase 10: Manual acceptance — real-monitor visual inspection of AT-01 through AT-27. Cowork (Opus) assists with check-off sheet organization and result recording.

### Decisions
- **Session boundaries over mid-session model switching.** Rather than switching models within a Claude Code session (which forces the new model to pay for all prior context tokens), group by model across sessions: Sonnet session for Bubble+Selection, Opus session for Insertion+Heap. Avoids Opus token rates on Bubble/Selection context and avoids Sonnet rates on context it won't use well for the harder algorithms.
- **Oversight stays on Opus.** The review role (this Cowork session) needs full spec context and the ability to catch violations the implementation model missed. Catching a bug in review is cheaper than discovering it three phases later.
- **Escalation rule:** If Sonnet produces a deliverable that fails exit criteria after one correction attempt, escalate to Opus for that specific file rather than iterating further on Sonnet.
- **DEVLOG updates by the active model.** Initially considered Haiku for all DEVLOG appends, but refined away — the model that just wrote the code already has the context for what it did and what it noticed. Switching to Haiku to save ~200 tokens of structured append isn't worth the friction. The real Haiku savings come from Phase 9 (CI YAML) and standalone tracker checkbox updates.
- **TC-A19 escalation trigger (concrete).** If Sonnet's TC-A19 sift-down segmentation helper fails to correctly distinguish boundary T3 (contiguous) from logical-tree T3 (non-contiguous) on the first attempt, switch to Opus for that test file. Don't iterate on Sonnet — the contiguity-check logic is exactly the kind of multi-constraint reasoning where Opus pays for itself immediately.

### Open questions
- None. The three refinements (session boundaries, DEVLOG by active model, TC-A19 escalation trigger) resolved the open questions from the initial draft.

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

- **Granularity:** Per-phase, not per-task. Eleven packs total.
- **Scope:** Each pack serves both forward (implementation) and backward (audit) modes.
- **Format:** Structured blocks (Option B) over bullet lists.
- **Coverage test:** Informal. A bottom-of-document table of queries and expected packs.
- **Adoption mechanics:** Reference document only. Platform-neutral.
- **Authoring order:** Before Phase 1 begins. Phase 1 is the dogfood test.
- **Supersession ID handling in packs:** Current binding IDs only. The Supersession Index in `DECISIONS.md` carries the full chain.

### Open questions
- **Pack token-budget estimates are rough.** Eyeballed from line counts, not measured against a tokenizer.
- **Phase 5 may want sub-loading.** Advisory not prescriptive.
- **Phase 6 orchestrator rapid-cadence signal.** Still unresolved.

### Next
Phase 1 begins. Use the Phase 1 pack as the dogfood test.

---

## 2026-04-14 — Mempalace post-mortem and archive

### Worked on
Reviewed three legacy files at the repo root — `mempalace.yaml`, `mempalace.yaml.bak`, and `entities.json`. Archived into `docs/AI_Conversations/mempalace-experiment/` with a companion `README.md` documenting the attempt, the specific failure modes identified, and the lessons inherited by the active context-pack design.

### Decisions
- **Archive rather than delete.** High-value video journal content (failure modes are more instructive than success stories).
- **Do not revive.** The underlying mismatch — keyword taxonomy cannot express task-shaped queries — is not solved by tuning.

### Failure modes documented
1. Keyword ambiguity at scale.
2. Taxonomy dimension orthogonal to query dimension.
3. Keywords cannot traverse cross-references.
4. Room coverage incomplete; load-bearing files landed in catch-all.
5. Iteration toward mechanization *reduced* accuracy.
6. No measurement loop.

### Lessons carried forward into the context-pack design
- Group by implementation phase, not document type.
- Enumerate file paths explicitly.
- Name cross-references by ID.
- Define a coverage test.

### Next
Resume discussion of the context-pack proposal.

---

## 2026-04-14 — Agentic-coder context and hallucination risk assessment (UNDER REVIEW)

### Worked on
Evaluated whether the existing spec corpus (4,521 lines / ~306K characters / ~75-80K tokens across 18 markdown files) is appropriately sized and structured for agentic coding tools.

### Identified risk vectors
1. Context dilution — 75-80K tokens leaves ~25% of a 200K window for working code.
2. Supersession blindness — agents find superseded rules first by keyword.
3. Cross-reference hallucination — agents fabricate plausible content for unloaded D-NNN references.
4. Worked-example drift — partial-context agents verify against the wrong doc's trace.
5. Vocabulary fragility — partial-context agents infer T0-T4 meaning from usage, not definition.

### Proposed mitigations
- High leverage: Supersession index, per-phase context packs, inline active/superseded markers.
- Medium leverage: Root-level glossary, counter table consolidation.
- Structural: Project-specific skill file.

### Decisions
No binding decisions this session. Assessment complete, mitigations on the table for author review.

### Next
Author review in progress. No immediate action.

---

## 2026-04-14 — Phase 0 closeout: pyproject, config, pseudocode, implementation order, fonts helper

### Worked on
Closed the bulk of Phase 0 gaps: D-080 (path reconciliation), `pyproject.toml` rewrite, `config.toml` rewrite, `00_PSEUDOCODE.md`, `13_IMPLEMENTATION_ORDER.md`, and `scripts/fetch_fonts.sh`.

### Decisions
- **D-080 (locked):** Source package at `src/visualizer/`, not `visual_sort/src/`.
- `pyproject.toml`: hatchling build, pytest markers from doc 08, ruff py313, pyright strict.
- `config.toml`: `preset = "desktop"` per D-018/D-079.
- `00_PSEUDOCODE.md`: single source of truth for generator control flow.
- Insertion Sort terminating-compare written with pass-by-pass truth table.
- Heap Sort sift-down as reusable helper with contiguous-vs-non-contiguous T3 distinction.

### Open questions
- Fonts acquisition blocked on sandbox proxy.
- `main.py` location deferred to Phase 7.
- Rapid-cadence timing signal deferred to Phase 6.

### Next
Run `bash scripts/fetch_fonts.sh` on WSL host, then Phase 1 is unblocked.

---

## 2026-04-14 — Project state review and methodology realignment

### Worked on
Full state audit: 142 tracked items across 10 phases, all open; 4,000 lines of design documentation and 79 locked decisions; zero implementation code. Source scaffold conflict identified and resolved.

### Decisions
- Project operates in **blueprint-first** methodology. Not paralysis — disciplined pre-implementation.
- Secondary objective: **video journal** documenting the engineering methodology. DEVLOG is the raw material.
- Added `NORTH_STAR.md` and `DEVLOG.md` as retrieval-optimized reference artifacts.

### Open questions
- Video journal audience framing.
- Project origin story location.

### Next
Phase 0 closeout.
