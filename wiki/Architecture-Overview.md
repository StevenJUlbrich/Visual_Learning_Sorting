# Architecture Overview

The application follows strict MVC under `src/visualizer/`, with clear boundaries between algorithm logic, rendering, and orchestration.

## Directory Structure

```
src/visualizer/
├── main.py                  # Pygame event loop, config loading, font fallback
├── models/
│   ├── contracts.py         # SortResult dataclass, OpType enum, BaseSortAlgorithm base class
│   ├── bubble.py            # BubbleSort generator (20 comparisons, 26 writes)
│   ├── selection.py         # SelectionSort generator (21 comparisons, 10 writes)
│   ├── insertion.py         # InsertionSort generator (17 comparisons, 19 writes)
│   └── heap.py              # HeapSort generator (20 comparisons, 30 writes, 35 steps)
├── views/
│   ├── sprite_manager.py    # Per-algorithm choreography dispatch + 4 overlay classes (~1000 lines)
│   ├── sprite.py            # NumberSprite — circular ring, float coords, color state machine
│   ├── panel.py             # Panel frame rendering, header rhythm (title → metrics → message)
│   ├── tree_layout.py       # Heap Sort binary tree node positioning and edge rendering
│   ├── pointer.py           # Selection Sort i/j/min labeled arrows with coalescing
│   ├── limitline.py         # Bubble Sort vertical dashed boundary line
│   ├── hud.py               # Overlay counters (BubbleHUD) and phase labels (HeapPhaseLabel)
│   └── easing.py            # Pure math — ease_in_out_quad, ease_out_cubic, sine_arc
├── controllers/
│   └── orchestrator.py      # Independent queues, operation timing, state machine, sprite moves
└── config.toml              # Resolution preset + optional custom array
```

## Data Flow: Generator to Animation

The runtime operates on two decoupled tracks that together create the racing behavior.

### The Logical Track (Model → Controller)

Each algorithm is a Python generator that yields `SortResult` ticks — typed operation records describing what just happened (a comparison, a swap, a shift, a visual range highlight). The generator owns a mutable copy of the array and advances one atomic operation per `yield`. It never knows about rendering.

The Controller (`orchestrator.py`) manages four independent queues, one per algorithm. When a queue is ready for its next operation, the Controller pulls the next `SortResult` from that algorithm's generator and assigns a simulated time cost in milliseconds based on the operation type. This is how the race works: a compare costs 150ms, a swap costs 400ms. An algorithm that does fewer expensive operations finishes sooner — visibly.

### The Render Track (Controller → View)

A Pygame `while True` loop runs at 60 FPS. Each frame computes delta-time (`dt`), clamped to 33ms maximum to prevent sprite overshoot on frame drops. The Controller subtracts `dt` from each panel's remaining operation time. When a panel's timer reaches zero, the next tick is dispatched: the View receives target coordinates and highlight colors, and sprites ease toward their destinations using quadratic or cubic curves.

The two tracks never block each other. A panel can be mid-animation (sprites still interpolating toward targets) while another panel has already finished its current operation and is waiting for the next tick.

### The Sprite Identity Problem

This is Critical Rule #1 in the project, and it exists because of duplicate values.

When the Controller receives a new `array_state` from a tick, it needs to figure out which sprites moved where. The naive approach — match by value — breaks immediately with duplicates: if the array is `[3, 1, 3, 2]` and a swap produces `[3, 3, 1, 2]`, value-matching can't tell which `3` moved.

The solution: every sprite has a permanent unique ID assigned at initialization. The Controller maintains a `slot_to_sprite_id` mapping (which sprite is currently at which array index). When a new `array_state` arrives, it computes index deltas between the old and new states to determine which slots changed, then updates the mapping. Sprites are tracked by ID, never by value.

This was the source of one of the most significant bugs found during acceptance testing — see [Misalignment Case Studies](Misalignment-Case-Studies) for the `compute_sprite_moves()` duplicate-value incident.

## Independent Queue Semantics

Each panel maintains its own state machine with five states:

```
idle_paused → waiting_for_next_tick → animating_operation → waiting_for_next_tick → ...
                                                                                  ↘ completed
                                                                                  ↘ failed
```

The state machine topology is identical for all four algorithms. Algorithm-specific behavior is expressed through tick content (what `OpType`, which `highlight_indices`) and duration selection — never through additional states or transitions.

Each panel tracks its own elapsed simulated time. Fast algorithms exhaust their generators and reach completion while slower algorithms are still mid-sort. Completed panels freeze their stats and remain visible with a green background while the race continues.

## Operation Timing

Operation costs are integer milliseconds, assigned by the Controller based on `OpType`:

| Operation | Type | Standard Duration | Heap Sift-Down Cadence |
|-----------|------|------------------|----------------------|
| Compare | T1 | 150ms | 100ms |
| Swap | T2 | 400ms | 250ms |
| Shift | T2 | 400ms | — |
| Range Emphasis | T3 | 200ms | 130ms |

Heap Sort has a special "sift-down cadence" that activates after each extraction swap — the reduced durations create a rapid cascading rhythm during the repair phase, then reset at the next boundary highlight.

## Per-Algorithm Visual Choreography

Each algorithm has custom animation behavior beyond the shared arc-swap motion:

**Bubble Sort** — compare-lift choreography. Both sprites in a comparison pair lift vertically (50px ascent over 67ms, hold 33ms, descent 50ms), then swap horizontally while lifted. A dashed LimitLine marks the shrinking unsorted boundary. HUD counters show comparisons and exchanges.

**Selection Sort** — three labeled pointer arrows (`i` above the sorted boundary, `j` and `min` below the scan region). When `j == min`, only `min` renders (coalescing). Sorted elements turn steel-blue. The `i` pointer uses cyan coloring and sits below the `j`/`min` tier for visual separation.

**Insertion Sort** — key elevation. The selected key lifts to a compare lane and stays elevated across all compare/shift ticks until placement. Shifts happen one at a time (never batched — this is a locked pedagogical requirement). A "KEY" label follows the elevated sprite. The gap left by the key migrates as elements shift.

**Heap Sort** — binary tree layout. Active heap elements render as tree nodes with parent-child edges. Extracted elements move to a sorted row below the tree. Sift-down swaps follow 2D arc paths along tree edges. Extraction arcs use 1.75× standard height. Boundary T3 ticks render as staggered left-to-right sweeps. A phase label shows "BUILD MAX-HEAP" or "EXTRACTION."

## Error Model

Domain failures (empty input, invalid data) produce a `SortResult` with `success=False` and a descriptive message. The Controller deactivates only the failing panel — the other three algorithms continue. An unhandled exception in a generator would crash the Pygame event loop, which is why the algorithms are required to handle all errors through the tick protocol rather than raising exceptions.
