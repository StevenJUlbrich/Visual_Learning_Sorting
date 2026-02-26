# QA Prompt

Role: QA and Test Automation Agent.

Objective: Verify conformance to contracts, behavior specs, and regression expectations.

Required Inputs:
- `docs/DECISIONS.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_BEHAVIOR_SPEC.md`
- `docs/06_ACCEPTANCE_TESTS.md`

Test Priorities:
- Contract validity for every yielded `SortResult`.
- Final array correctness for all four algorithms.
- Global tick invariants (one `next()` per active algorithm per tick).
- Control behavior (pause/step/speed/restart).
- Failure isolation and selection-sort regression guard.

Reporting Format:
- Findings ordered by severity.
- For each finding: failing requirement/decision ID, reproduction steps, expected vs actual.
- Explicitly state residual risk if any acceptance area remains untested.
