# 06 BEHAVIOR SPEC.md (Rewritten)

## Startup Behavior

* App initializes all four algorithms with identical initial array `[7, 6, 5, 4, 3, 2, 1]`.
* App starts in paused state.
* Initial frame renders panels, base nodes, and metadata (0 steps, 0.00s elapsed) before any algorithm ticks.

## Control Behavior (Path 2 Controls)

### Play/Pause

* Scope: global.
* Play: Begins the independent time accumulators for all active queues, starting the race.
* Pause: Freezes all time accumulators immediately. Active tweens hold their exact mid-air `(x, y)` positions.

### Step

* Enabled only while paused.
* Because algorithms are decoupled, "Step" forces every active algorithm to advance its queue to the conclusion of its *current* pending logical operation, bypassing the timer constraint for that single move.

### Speed Toggle

* Cycles deterministic multipliers: `1.0x` → `1.5x` → `2.0x` → `1.0x` (wrapping).
* Default speed is `1.0x` at startup and after restart.
* Mathematically divides the operation time costs (e.g., a 400ms swap takes 200ms at 2.0x speed).

### Restart

* Re-initializes all models, queues, panel counters, and elapsed timers.
* Uses original initial array values.
* Returns app to paused state.

## Racing and Operation Timing

Instead of a fixed global tick, time is driven by operation cost. Base costs at `1.0x` speed:

* **Compare Operation (`T1`):** `150ms` simulated cost.
* **Write/Swap Operation (`T2`):** `400ms` simulated cost (allows time for physical interpolation).
* **Range Emphasis (`T3`):** `200ms` simulated cost.

The View tracks and displays an `Elapsed Time` metric formatted to two decimal places (e.g., `03.45s`) for each panel.

## Completion Behavior

* On `SortResult(success=True, is_complete=True)`, the algorithm queue is emptied and marked inactive.
* The elapsed timer for that specific panel stops permanently.
* Completed panel keeps final sorted array visible, applies completion color treatment, and ceases step incrementation.

## Failure Behavior

* On `SortResult(success=False, ...)`, algorithm is marked inactive and its timer stops.
* Failure panel shows explicit error state border and latest message.
* Other algorithms continue racing unaffected.

## Input Modality

* Clickable UI controls and keyboard shortcuts mirror each other.

### Keyboard Bindings (Locked)

| Key | Action |
| --- | --- |
| `Space` | Play / Pause |
| `Right Arrow` | Step (resolve current operation, only while paused) |
| `R` | Restart |
| `S` | Speed cycle (1x → 1.5x → 2x → 1x) |
| `Escape` | Quit app cleanly |
