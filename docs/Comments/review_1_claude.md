# Project Review: Visual Learning Sorting

## What This Is
A pre-implementation specification package for an educational desktop app (Python 3.13 + Pygame) that visualizes Bubble, Selection, Insertion, and Merge Sort running side-by-side in a 2x2 grid, sharing one global tick clock so learners can directly compare algorithmic behavior.

Document Inventory (35 files across docs/)

| Category | Files | Purpose |
|---|---|---|
|Core Specs (01-09) | 10 files |Canonical, locked requirements|
|Brick Transcripts (1-5)| 10 files |Design conversation history with code sketches|
|Agent Prompts|	4 files| Role-scoped prompts for agentic implementation |
|Context Handoffs |	3 files |	Session-to-session AI continuity docs |
|Planning & Reviews | 4 files |	Original planning notes, ChatGPT review, agentic guide |
|Legacy (Bucket Sort)|	3 files |	Superseded prior project PRDs |


## Strengths

1. Exceptionally thorough contract-first design. The 03_DATA_CONTRACTS.md is genuinely excellent - it defines SortResult as the single source of truth with valid state combinations, step counter semantics, and generator contract requirements. This alone eliminates entire classes of implementation bugs.

2. Decisions are tracked and locked. DECISIONS.md has 20 locked decisions, 3 undecided items, 6 deferred items, and 4 resolved conflicts. This is the kind of decision log that prevents agentic drift.

3. The review feedback loop worked. The project_review_1_chatgpt.md identified 5 spec gaps (contract mismatch, UI control scope, color identity, step counter definition, window orientation). All 5 were subsequently resolved in the core specs - a clean audit trail.

4. Multi-layered QA design. The 06_ACCEPTANCE_TESTS.md and 07_TEST_PLAN.md together cover human-checkable acceptance tests, automated contract checks, the Selection Sort regression guard, and snapshot isolation tests. The traceability matrix in 07 maps test cases to acceptance criteria.

5. Pure Result Pattern is well-motivated. The decision to avoid exception-driven control flow for domain failures is consistently enforced across all agent prompts and spec documents. The Merge Sort explicit failure bubbling pattern is clearly documented.

## Issues and Gaps

### Critical (would cause implementation confusion)

1. AGENTS.md references the wrong project.
AGENTS.md is titled "Bucket Sort Visualizer (Lightning Labs)" and references PRD.md, DESIGN.md, bucket_sort_viz, PowerShell commands, and Windows-first conventions. This directly contradicts DECISIONS.md D-001 which locks the project as "Sorting Algorithm Visualizer (not Bucket Sort)." An agentic builder loading this file would receive conflicting project identity and commands.

2. Brick docs contain raw code but are not canonical specs.
The Brick files (Brick_1.md through Brick_5_The_Controller.md) are design conversation transcripts that include full Python implementations. However, the core specs (01-09) are supposed to be the canonical source. If an implementer reads both, they'll face ambiguity about whether to follow the Brick code verbatim or the spec documents. Key differences:

    - Brick 4 Panel uses a single Colors.ARRAY_HIGHLIGHT color; the spec (04_UI_SPEC.md:94-100) requires per-algorithm accent colors
    - Brick 5 Controller has no Step button, no Restart, and no on-screen clickable controls; the spec (05_BEHAVIOR_SPEC.md) requires all of these
    - Brick 5 uses number keys (1/2/3) for speed; the spec requires a speed cycle toggle

 3. Three undecided items (N-001 through N-003) in DECISIONS.md need resolution before implementation.

    - N-002 (message line visibility) directly affects panel composition and UI layout
    - N-003 (secondary counters) affects panel header rendering
### High
4. No pyproject.toml or project scaffolding exists.

    The repo is purely documentation. 08_DEV_ENV.md references uv sync and specific run commands, but there's no pyproject.toml, no src/ directory, no assets/ folder, and no .gitignore. An implementer agent would need to bootstrap from scratch, and there's a mismatch between Brick 1's path (/mnt/d/Visual_Learning_Sorting) and the spec's src/visualizer/ structure.

5. Agentic prompt draft (agentic_prompt_draft.md) contains implementation details that conflict with specs.
    It specifies a ui.py Button class and accent_color parameter for panels, which aren't mentioned in the formal specs. It also references configurable resolution via main.py flags, which isn't formalized in 05_BEHAVIOR_SPEC.md or 08_DEV_ENV.md.

6. Keyboard shortcut mappings are not specified.

05_BEHAVIOR_SPEC.md says "Keyboard shortcuts are also required as parity controls" but never defines the actual key bindings. The Brick 5 Controller uses Space for pause and 1/2/3 for speed, but this isn't locked anywhere in the canonical specs.

### Medium
7. File naming inconsistency.
    
    The Brick docs use mixed casing: Brick_1.md vs brick_2.md vs brick_3_selection_sort.md vs Brick_3_Insertion_Sort.md. Minor, but signals lack of a naming convention.

8. Legacy Bucket Sort documents should be archived or removed.
    
    Three files (PRD_bucket_sort_visualizer_v1.md, PRD_bucket_sort_visualizer_v1_1_codex_ready.md, bucket_sort_visualizer_design_v3.md) total ~1,800 lines of content for a different project. They could mislead an agent scanning the docs directory.

9. The 05 prefix is used twice. Both 05_ALGORITHMS_VIS_SPEC.md and 
    
    05_BEHAVIOR_SPEC.md share the 05_ prefix. Should be 05 and 06 (with subsequent files renumbered).

10. Colors dataclass uses class-level defaults but frozen=True.

    The Brick 4 theme code defines Colors as @dataclass(frozen=True) with mutable default values. This works but means you'd need to instantiate Colors() to use the values. The spec (04_UI_SPEC.md) defines them as raw tuples. The implementer needs clarity on whether these are class constants or instance attributes.

## Recommendations (Priority Order)

1. Fix or remove AGENTS.md - it actively contradicts the project. Either rewrite it for this project or delete it.

2. Resolve N-001, N-002, N-003 in DECISIONS.md before handing to an implementer.

3. Add a SPEC_INDEX.md that explicitly marks which documents are canonical (01-09 + DECISIONS) vs reference-only (Bricks, handoffs, legacy). Alternatively, move non-canonical docs into a docs/reference/ subdirectory.

4. Define keyboard bindings in the behavior spec (Space=pause, S=step, R=restart, Up/Down=speed, etc.).

5. Create the project scaffold (pyproject.toml, directory structure, .gitignore) or document that the implementer agent should create it as step 1.

6. Archive legacy Bucket Sort docs to docs/archive/ or remove them from the repo.

7. Renumber the 05_ collision to sequential numbering.

### Overall Assessment

This is a remarkably well-prepared pre-coding specification package. The core specs (01-09), DECISIONS.md, and agent prompts form a coherent, internally consistent system that an agentic implementer could execute from with high fidelity. The main risks are the stale/conflicting peripheral documents (AGENTS.md, Brick transcripts, legacy PRDs) that could introduce drift if an agent ingests them without understanding their status. Cleaning up the document hierarchy and resolving the three open decisions would make this implementation-ready.