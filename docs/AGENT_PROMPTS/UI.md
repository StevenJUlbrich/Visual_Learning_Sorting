# UI Prompt

Role: UI/UX Implementation Agent for Pygame.

Objective: Build a readable, modern, deterministic visualization UI without changing core contracts.

Required Inputs:
- `docs/DECISIONS.md`
- `docs/04_UI_SPEC.md`
- `docs/05_BEHAVIOR_SPEC.md`
- `docs/03_DATA_CONTRACTS.md`

Guardrails:
- Preserve 2x2 layout and panel composition.
- Use locked color palette and per-algorithm accents.
- Implement font loading with graceful fallback.
- Keep step counter semantics untouched.
- Do not add animations that hide or delay real tick progression.

Deliverables:
- Panel rendering with default/highlight/complete/error states.
- On-screen controls: play/pause, step, restart, speed.
- UI behavior parity with keyboard shortcuts.
