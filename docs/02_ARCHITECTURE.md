# 02 ARCHITECTURE - MVC, Tick Model, Runtime

## Architecture Style
Strict MVC under `src/visualizer/`.

- `models/`: algorithms + shared data contracts.
- `views/`: rendering/theme/layout/UI widgets.
- `controllers/`: app lifecycle, input handling, global tick orchestration.

No import bleeding across layers beyond required contracts.

## Runtime Model
- Pygame loop runs continuously.
- Controller owns global app state (`paused`, speed multiplier, active generators, current panel states).
- On each render frame:
1. Process events.
2. If not paused and time accumulator >= `tick_interval_ms`, advance exactly one global tick (one `next()` per active algorithm) and reset accumulator (see `06_BEHAVIOR_SPEC.md` Tick Timing).
3. Render full frame from current states.

## Global Tick Semantics
- A global tick is one controller advance cycle.
- During one global tick, each active algorithm generator is advanced once (`next(gen)` exactly once).
- Completed/failed algorithms are skipped in later ticks.
- This enables direct visual cadence comparison without time skew.

## Component Boundaries
### Model Responsibilities
- Maintain algorithm-local mutable array copy.
- Yield `SortResult` for every atomic operation and terminal state.
- Never mutate View or Controller state.

### View Responsibilities
- Purely render from latest `SortResult` values.
- Keep panel-local counters and visual states.
- Never execute algorithm logic.

### Controller Responsibilities
- Instantiate models with shared initial data copied per model.
- Own generator lifecycle and halt policy (`success=False` or `is_complete=True`).
- Translate UI events into control state changes.

## Error Model
- Domain and algorithm-flow failures must be represented by `SortResult(success=False, ...)`.
- Controller must not crash app for one algorithm failure; it deactivates that algorithm and continues others.
- Unexpected runtime exceptions may be logged and converted to failure state where practical.

## Config + Runtime Targets
- Default target: landscape 1280x720.
- Alternate supported target: portrait 720x996.
- Same layout logic (2x2) for both targets.

## Extensibility Rules
- New algorithms must implement `BaseSortAlgorithm` and `sort_generator` contract.
- UI must remain contract-driven; no algorithm-specific logic in panel rendering.
- Max simultaneous displayed algorithms remains 4 in v1.
