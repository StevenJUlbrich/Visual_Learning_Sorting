# AGENTS.md — Bucket Sort Visualizer (Lightning Labs)

Codex: use this file as the **persistent source of project instructions**.

## Source of truth

- **Product requirements:** `PRD.md` (requirement IDs are binding).
- **Visual/design reference:** `DESIGN.md` (animation look & feel).

If `PRD.md` and `DESIGN.md` conflict, follow `PRD.md` and add a short note to the PR describing the conflict.

## Working agreements

- Work in **small, reviewable commits**. Prefer one PRD requirement cluster per PR.
- Reference the relevant **PRD IDs** in commit messages and PR descriptions (e.g., `PRD-4.2.1`, `PRD-5.1.3`).
- Do not add new runtime dependencies without explicit approval.
- Windows-first (PowerShell). Avoid Unix-only assumptions.
- Keep algorithm logic testable and decoupled from rendering (model/steps separate from view/pygame).

## Project commands (Windows / PowerShell)

- Install/sync deps:
  - `uv sync`
- Run (menu/app):
  - `uv run python -m bucket_sort_viz`
- Run a deterministic CLI demo:
  - `uv run python -m bucket_sort_viz --preset small --count 10 --seed 42`
- Tests:
  - `uv run pytest -q`
- Lint:
  - `uv run ruff check src tests`

## Definition of done (for any PR)

- [ ] All affected PRD requirements implemented.
- [ ] `uv run ruff check src tests` passes.
- [ ] `uv run pytest -q` passes.
- [ ] Manual verification steps written in the PR description (what to run + what you should see).

## Large work (ExecPlans)

If a task is complex (multi-hour, multi-area refactor, or involves several PRD sections):
1. Create or update an **ExecPlan** in `PLANS.md`.
2. Keep the plan “living”: update progress checkboxes and decision log as you go.
3. Implement milestone-by-milestone, validating each milestone with tests and a runnable demo.

