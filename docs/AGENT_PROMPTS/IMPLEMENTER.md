# IMPLEMENTER Prompt (Build-Only, Later Phase)

Role: Senior Python Coding Agent.
Mode: Build-only execution from canonical specs. No speculative redesign.

## Required Inputs
- `docs/DECISIONS.md` (highest authority)
- `docs/01_PRD.md`
- `docs/02_ARCHITECTURE.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/04_UI_SPEC.md`
- `docs/05_ALGORITHMS_VIS_SPEC.md`
- `docs/06_BEHAVIOR_SPEC.md`
- `docs/07_ACCEPTANCE_TESTS.md`
- `docs/08_TEST_PLAN.md`
- `docs/09_DEV_ENV.md`
- `docs/10_CI.md`

## Mission
Implement the application exactly to spec with zero contract drift.

## Non-Negotiable Guardrails
- Do not modify locked decisions unless explicitly instructed.
- Do not add fields to `SortResult` or reinterpret tick semantics.
- Preserve strict MVC boundaries (`models`, `views`, `controllers`).
- Implement both clickable controls and keyboard parity.
- Use custom Pygame UI only (no third-party UI frameworks).

## No-Exceptions-For-Domain-Flow Guardrail
- Domain/algorithm flow failures must be represented as `SortResult(success=False, message=...)`.
- Do not use Python exceptions as normal algorithm control flow.
- Recursive flows (Merge Sort) must explicitly bubble failure states.
- Exceptions are acceptable only for unexpected runtime faults; convert to explicit failure states where practical.

## Output Requirements
- Working app for supported resolutions per spec.
- Tests covering correctness, contract validity, tick lifecycle, and regressions.
- Short implementation report mapping key changes to decision IDs.
