# 06 BEHAVIOR SPEC - Runtime Controls and Panel Behavior

## Startup Behavior

- App initializes all four algorithms with identical initial array `[7, 6, 5, 4, 3, 2, 1]`.
- App starts in paused state.
- Initial frame renders panels and metadata before any algorithm ticks.

## Control Behavior

### Play/Pause

- Scope: global.
- Play: enables automatic global tick advancement.
- Pause: freezes tick advancement while keeping rendering responsive.

### Step

- Enabled only while paused.
- Executes exactly one global tick.
- During that tick, each active algorithm advances once.

### Speed Toggle

- Cycles deterministic multipliers: `1.0` → `1.5` → `2.0` → `1.0` (wrapping).
- Default speed is `1.0` at startup and after restart.
- Applies only to controller clock pacing, never algorithm logic.

### Tick Timing (Locked)

- Base tick interval: `500ms` (2 algorithm ticks per second at 1.0x).
- Formula: `tick_interval_ms = 500 / speed_multiplier`.
- Concrete values:
  | Speed | Interval | Ticks/sec |
  |---|---|---|
  | 1.0x | 500ms | 2.0 |
  | 1.5x | 333ms | 3.0 |
  | 2.0x | 250ms | 4.0 |
- The render loop runs at display refresh rate (uncapped or vsync). Tick advancement is gated by an accumulator against `tick_interval_ms`, not by frame rate.
- Step mode ignores tick timing and advances immediately on input.

### Restart

- Re-initializes all models, generators, panel counters, and active flags.
- Uses original initial array values.
- Returns app to paused state.

## Completion Behavior

- On `SortResult(success=True, is_complete=True)`, algorithm is marked inactive.
- Completed panel keeps final sorted array visible.
- Completed panel uses completion color treatment and completion label.
- Completed panel no longer increments step count.

## Failure Behavior

- On `SortResult(success=False, ...)`, algorithm is marked inactive.
- Failure panel shows explicit error state and latest message.
- Other algorithms continue unaffected.

## Tick and Counting Behavior

- One global tick calls `next(gen)` once per active algorithm.
- Step count increments only on non-terminal successful ticks.
- Completion and failure ticks do not increment step count.

## Merge Sort Visual Rule

- Merge operations must highlight active merge range via `highlight_indices`.
- Literal bracket drawing is deferred; range highlighting is required in v1.

## Input Modality

- Clickable controls are required in v1.
- Keyboard shortcuts are also required as parity controls.

### Keyboard Bindings (Locked)

| Key | Action |
|---|---|
| `Space` | Play / Pause |
| `Right Arrow` | Step (one tick, only while paused) |
| `R` | Restart |
| `S` | Speed cycle (1x → 1.5x → 2x → 1x) |
| `Escape` | Quit |

## Shutdown Behavior

- Quit event exits app loop cleanly.
- Pygame resources are closed on shutdown.
