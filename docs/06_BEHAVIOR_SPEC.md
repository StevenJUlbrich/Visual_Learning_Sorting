# 06 BEHAVIOR SPEC - Runtime Controls and Panel Behavior

## Startup Behavior

- App initializes all four algorithms with identical initial array `[4, 7, 2, 6, 1, 5, 3]`.
- App starts in the paused state.
- Initial frame renders panels, base sprites, and metadata (0 steps, 0.00s elapsed).

## Control Behavior (Path 2 Controls)

### Play/Pause

- **Play:** Begins the independent time accumulators for all active queues, starting the race. Sprites begin interpolating.
- **Pause:** Freezes all time accumulators immediately. Active sprites pause their time-normalized movement and hold their exact mid-air `(x, y)` positions. All visual state is frozen: sprite positions, highlight colors, and the panel message line. No tick is re-fetched or restarted on resume — animation continues from the exact interrupted point with remaining duration.

### Step

- Enabled only while paused.
- Step input is **ignored** while a step animation is still in progress. The user must wait for the current step animation to complete before stepping again.
- "Step" forces every active algorithm to advance its queue to the conclusion of its *current* pending logical operation, smoothly animating the sprites to their final target positions for that specific move before pausing again.
- A single Step action processes exactly one newly fetched SortResult per active algorithm panel. If that tick produces motion, the app animates that motion to completion using the **same operation duration and easing as play mode** (e.g., 400ms for a swap), then immediately returns to paused state.

### Restart

- Re-initializes all models, queues, panel counters, and elapsed timers.
- Uses original initial array values.
- If sprites are mid-animation, all positions **snap instantly** to the initial array layout. There is no animated return. All animation state (elapsed time, interpolation progress, highlights) is discarded.
- Returns app to paused state with a clean initial frame.

## Racing and Operation Timing

Time is driven by absolute simulated operation costs:

- **Compare Operation (`T1`):** `150ms` simulated cost.
- **Write/Swap Operation (`T2`):** `400ms` simulated cost (allows time for physical sprite interpolation).
- **Range Emphasis (`T3`):** `200ms` simulated cost — used by Heap Sort to display the active heap boundary before each extraction swap.

**Heap Sort Sift-Down Cadence Override:** After a Heap Sort extraction swap completes, the Controller applies reduced simulated costs to the subsequent sift-down repair ticks: T1 → `100ms`, T2 → `250ms`, T3 (Logical Tree) → `130ms`. This creates a rapid cascading visual rhythm. The override resets at the start of the next extraction step. Phase 1 (Build Max-Heap) sift-down uses standard durations. Full specification in `10_ANIMATION_SPEC.md` Section 5.3.2.

The View tracks and displays an `Elapsed Time` metric formatted to two decimal places (e.g., `03.45s`) for each panel.

## Tick and Counting Behavior

- A panel "step" increments strictly upon receiving a `SortResult` where `success=True`, `is_complete=False`, and `operation_type` is **not** `OpType.RANGE`.
- T3 Range Emphasis ticks (used by Heap Sort for boundary display) do **not** increment the step count. They are a visual teaching aid, not an algorithmic operation.
- Completion ticks (`is_complete=True`) and failure ticks do not increment the step count.
- Upon completion, the panel's elapsed timer permanently halts, proving its final "race" time.

## Completion Behavior

- On `SortResult(success=True, is_complete=True)`, the algorithm queue is emptied and marked inactive.
- The elapsed timer for that specific panel stops permanently.
- Completed panel keeps final sorted array visible, applies completion color treatment, and ceases step incrementation.

## Failure Behavior

- On `SortResult(success=False, ...)`, algorithm is marked inactive and its timer stops.
- Failure panel shows explicit error state border and latest message.
- Other algorithms continue racing unaffected.

## Input Modality

- Clickable UI controls and keyboard shortcuts mirror each other.

### Keyboard Bindings (Locked)

| Key | Action |
| --- | --- |
| `Space` | Play / Pause |
| `Right Arrow` | Step (resolve current operation, only while paused) |
| `R` | Restart |
| `Escape` | Quit app cleanly |
