# Spec-First Methodology

This page explains how 15 design documents and 81 locked decisions governed AI code generation throughout the project, and why this approach was necessary.

## The Problem with "Vibe Coding"

The default way people use AI for code generation is conversational: describe what you want, let the model write it, iterate on the output. This works for small, self-contained tasks. It breaks down on anything with cross-cutting constraints.

A sorting visualizer sounds simple, but the constraints interact in non-obvious ways. The Insertion Sort generator must emit individual compare-then-shift tick pairs (never batched), the key-selection tick must use `OpType.COMPARE` for timing purposes but must NOT increment the comparisons counter, and the terminating compare must fire only when the loop exits by condition (not by `j < 0`). An AI agent that "writes a working Insertion Sort" will sort correctly but violate two or three of these constraints — and you won't know unless you have something to check against.

The specifications exist to make misalignment detectable.

## What Was Written Before Any Code

Before the first line of implementation, the project produced:

**15 design documents** covering product requirements, architecture, data contracts, UI layout, algorithm visualization specifications, behavior specification, acceptance tests, test plan, dev environment, animation specification, CI pipeline, and animation foundation. These aren't aspirational outlines — they're binding contracts that lock specific behaviors.

**81 locked decisions** in `DECISIONS.md` (D-001 through D-081), each resolving a specific ambiguity. For example:

- **D-060**: "Each element shift in Insertion Sort is an individual compare-then-shift tick pair. Elements must never shift simultaneously as a batch."
- **D-058**: "All Heap Sort RANGE ticks must include the sift-down parent index in `highlight_indices` whenever a sift-down is active. For Logical Tree Highlights, the parent is always the first tuple member."
- **D-081**: "The View layer distinguishes Boundary T3 from Logical Tree T3 ticks by message prefix, not by highlight-set contiguity."

These decisions exist because they're the exact points where AI agents make wrong assumptions. Without D-060, every model tested would batch shifts for "efficiency." Without D-081, the view layer misclassifies 6 of 11 Logical Tree T3 ticks.

**Counter targets** — precise expected values for each algorithm on the reference array `[4, 7, 2, 6, 1, 5, 3]`:

| Algorithm | Comparisons | Writes | Steps |
|-----------|------------|--------|-------|
| Bubble Sort | 20 | 26 | — |
| Selection Sort | 21 | 10 | — |
| Insertion Sort | 17 | 19 | — |
| Heap Sort | 20 | 30 | 35 |

These aren't documentation — they're mechanical pass/fail gates. If Insertion Sort produces 15 comparisons instead of 17, the terminating-compare rule is broken. If Heap Sort produces 22 comparisons instead of 20, the internal `largest = right` decision is being yielded as a T1 tick. The numbers diagnose the specific failure.

**Tick-level animation contracts** for each algorithm, prescribing the exact sequence of operations. "Working code that sorts correctly" isn't sufficient — it must sort correctly in the right sequence of steps, with the right highlight indices, the right counter increments, and the right message format.

## The Two-Agent Workflow

The spec-first approach led to splitting two concerns between different agents:

### Agent 1: Cowork (Opus) — The Architect

This agent has the full specification context loaded. Its job is to read the specs, design prompts with exact code paths and exit gates, and make judgment calls about architectural trade-offs. It produces a prompt document for each implementation phase.

A typical prompt includes: the exact file to create or modify, the methods to implement with their signatures, the spec references that constrain the implementation, the counter targets that serve as exit gates, and the lint/test commands that must pass.

### Agent 2: Claude Code (Sonnet or Opus) — The Builder

This agent receives the prompt and executes it mechanically. It writes code, runs lint and format checks, runs the test suite, and reports pass/fail against the exit criteria. It doesn't interpret the specs — it follows the prompt.

This separation exists because judgment and execution are different failure modes. When the same model does both, it rationalizes its own mistakes: "I batched the shifts for efficiency" or "I incremented the counter here because it seemed logical." When execution is mechanical and gates are objective, misalignment becomes visible rather than rationalized.

### Model Selection as Engineering

Not all implementation tasks need the same model. The project used a deliberate model assignment strategy:

- **Opus** for high-constraint, multi-spec-intersection work: Insertion Sort (terminating-compare rule), Heap Sort (two T3 variants, recursive sift-down, phase transitions), the Orchestrator (independent queues, timing, state machine), and Heap Sort choreography (2D arc physics, extraction direction reversal, tree geometry changes).
- **Sonnet** for well-specified, single-constraint-domain work: Bubble Sort, Selection Sort, easing math, view components, tests.
- **Haiku** for mechanical bookkeeping: CI pipeline YAML.

The lesson: match the model to the decision density, not the code volume. A 200-line change with no judgment calls is Sonnet territory. A 200-line change where 5 lines require understanding why the arc direction reverses for extraction swaps is Opus territory.

## The Four-Step Prompt Pattern

Every implementation phase followed the same structure:

1. **DEVLOG PRE-ACTION** — Record the plan before execution. What will be built, which specs constrain it, what the exit criteria are. This creates an audit trail: if the output drifts from the plan, you can identify exactly where.

2. **IMPLEMENTATION** — The prescriptive prompt with code paths, insertion points, and gate commands.

3. **GATES** — Mechanical pass/fail checks: `ruff check` (lint), `ruff format --check` (formatting), `pytest -x` (tests), AST parse verification, counter target comparison. If any gate fails, the prompt is corrected and re-run — not iterated on conversationally.

4. **DEVLOG POST-ACTION** — Record what actually happened. Corrections made, surprises encountered, decisions that emerged during implementation. This is where misalignment incidents get documented.

The pre-action and post-action entries are preserved in the devlog archives. They serve double duty: engineering documentation during development, and source material for the video walkthrough.

## What This Produces

The outcome isn't just working code. It's working code with a verifiable audit trail:

- Every decision has a rationale (DECISIONS.md)
- Every phase has a plan and a result (devlog archives)
- Every prompt is preserved (docs/prompts/)
- Every misalignment incident is documented (devlog + case studies)
- Every counter target is checked mechanically (test suite)

This is the difference between "AI wrote my code" and "I engineered a system where AI executed my specifications under mechanical verification." The specifications are the engineering artifact. The code is the output.
