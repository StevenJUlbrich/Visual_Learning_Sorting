# 02 ARCHITECTURE - MVC, Pygame Sprites, Independent Queues

## Directory Tree

`src/visualizer/`
├── `main.py`                 # App entry point, config loading, and root Controller instantiation
├── `models/`
│   ├── `contracts.py`        # SortResult, OpType, BaseSortAlgorithm
│   ├── `bubble.py`           # BubbleSort implementation
│   ├── `insertion.py`        # InsertionSort implementation
│   ├── `heap.py`             # HeapSort implementation
│   └── `selection.py`        # SelectionSort implementation
├── `views/`
│   ├── `window.py`           # Pygame display init and master proportional layout
│   ├── `panel.py`            # Individual algorithm rendering frame, header, and UI counters
│   ├── `sprite.py`           # NumberSprite class — circular outlined ring with easing math
│   ├── `easing.py`           # Mathematical curves for fluid animation (pure math, no Pygame imports)
│   ├── `tree_layout.py`      # Heap Sort binary tree positioning, edge rendering, and node-to-slot mapping
│   ├── `pointer.py`          # Labeled pointer arrow assets (Selection Sort: i/j/min; Bubble Sort: ComparisonPointer)
│   ├── `limitline.py`        # Bubble Sort vertical dashed boundary line
│   └── `hud.py`              # Overlay components: Bubble Sort counters, Heap Sort phase label
└── `controllers/`
    └── `orchestrator.py`     # Independent queue management, operation timing, and event loop

## Architecture Style

Strict MVC under `src/visualizer/`.

- `models/`: algorithms + shared data contracts. Logic is strictly isolated here.
- `views/`: Pygame rendering, UI layouts, and the `NumberSprite` entity system. All algorithms use a universal active highlight color `(255, 140, 0)` orange (D-067). Sprites are circular outlined rings (D-069). Algorithm identity is communicated through panel title text and 2x2 grid position, not highlight color (D-070).
- `controllers/`: app lifecycle, input handling, and independent queue orchestration.
- main.py owns the pygame event loop.
- Controller exposes update(dt).
- View exposes render().

## Runtime Model: The Decoupled Race

The execution operates on two parallel, decoupled tracks:

1. **Render Track (The View):** A high-frequency Pygame `while True:` loop runs continuously. On every frame, it calculates the delta-time (`dt`) and calls `update(dt)` on all active Sprite entities, ensuring smooth visual easing regardless of algorithm state.
2. **Logical Track (The Controller):** The Controller manages four independent algorithm queues. It pulls `SortResult` yields from each algorithm and assigns a simulated time cost (in milliseconds) to each operation. It dispatches target `(x, y)` commands to the Sprites and waits for the operation cost duration to elapse before pulling the next yield.

### Each panel maintains

- current_operation_remaining_ms
- pending_generator

Controller subtracts dt each frame.
When <=0, next SortResult is requested.

## Independent Queue Semantics

- Each active algorithm generator is advanced based on its own elapsed simulated time, not a global clock.
- Fast algorithms will exhaust their queues and reach terminal states before slower algorithms.
- Completed/failed algorithms stop their individual timers but remain visually static on screen.
- This enables a true side-by-side race where the speed of completion directly reflects the algorithm's operational efficiency.

## Component Boundaries

### Model Responsibilities

- Maintain an algorithm-local mutable array copy.
- Yield `SortResult` for every atomic operation and terminal state.
- Never execute rendering logic or mutate View state.

### View Responsibilities

The controller/view computes sprite movement by comparing prior logical index ownership to the new logical index ownership after each tick. Sprite-to-slot mapping must never rely on raw value matching.

- Maintain `NumberSprite` objects — circular outlined rings (D-069) tracking value, exact floating-point `(x, y)` coords, and target coords. Ring outline and number text share the same color, changing together based on state (blue default, orange active, green completion, steel-blue settled).
- Execute time-normalized easing functions (e.g., quadratic ease-in-out) to move sprites smoothly and naturally, decoupling physical destination mapping from strict frame-rate integration.
- Dynamically calculate resting layout coordinates based on the active resolution proportions.
- Render algorithm-specific instructional assets per panel (see Per-Panel View Components below).

#### Per-Panel View Components

Each algorithm panel renders its own set of instructional assets in addition to the shared NumberSprite system:

| Algorithm | Layout | Instructional Assets |
| --- | --- | --- |
| **Bubble Sort** | Flat single row | `ComparisonPointer` (green arrow below baseline), `LimitLine` (vertical dashed boundary), HUD counters (Comparisons, Exchanges) |
| **Selection Sort** | Flat single row | Three labeled pointer arrows: `i` (above, sorted boundary), `j` (below, scan cursor), `min` (below, minimum tracker). Coalescing behavior when `j == min`. (D-068) |
| **Insertion Sort** | Flat single row | `KEY` label on lifted sprite (D-071), empty gap at extracted slot (D-072), color-only sorted/unsorted boundary (D-073) |
| **Heap Sort** | **Binary tree + sorted row** | Tree layout with parent-child edges (D-074), phase label "BUILD MAX-HEAP" / "EXTRACTION" (D-075), heap boundary dashed line (D-076) |

The Heap Sort panel is the only panel that does not use the standard flat single-row layout. It renders a binary tree of active heap elements above a compact sorted-region row. See `05_ALGORITHMS_VIS_SPEC.md` Section 4.4 and `views/tree_layout.py`.

### Controller Responsibilities

- Instantiate models with shared initial data.
- Map `SortResult` actions to specific physical destinations and simulated time costs.
- Track independent elapsed time for each panel to simulate the "race".
- Manage the `sift_down_cadence` flag for Heap Sort post-extraction duration reduction.

## Error Model

- Domain and algorithm-flow failures must be represented by `SortResult(success=False, ...)`.
- Controller must not crash app for one algorithm failure; it deactivates that algorithm and continues others.

## Config + Runtime Targets

- Proportional geometry target. The View calculates `x` and `y` baselines, padding, and sprite dimensions dynamically as percentages of the active window resolution defined in `config.toml` (e.g., standard 1080p support).
- Extensibility Rules: New algorithms must implement `BaseSortAlgorithm` and `sort_generator` contract. Max simultaneous displayed algorithms remains 4 in v1.

## Sprite Identity

- Sprite instances represent logical array positions, not values.
- Each sprite has a permanent ID created at initialization.
- When a SortResult provides a new array_state, the controller/view computes which logical index each sprite must move to based on index transitions between the previous and new array states.
- Sprite movement must never rely on value matching because duplicate values may exist.

### Heap Sort Tree ↔ Array Index Mapping

In the Heap Sort panel, each sprite exists in both the tree layout and the underlying array. The sprite's permanent ID and logical array index remain the canonical identity — the tree layout is a **view-layer position mapping** that translates array indices to `(x, y)` tree coordinates:

- **Active heap sprites** (indices `0..heap_size-1`): positioned by `tree_layout.py` using the binary tree formula — root at top center, children spread at each level.
- **Sorted/extracted sprites** (indices `>= heap_size`): positioned in the compact sorted row below the tree.
- When an extraction swap moves a sprite from tree position (index 0) to the sorted row (index `end`), the sprite's target coordinates transition from the tree root position to the sorted row slot. The elevated extraction arc (D-052) animates this transition.
- When a sift-down swap exchanges two sprites within the tree, both sprites swap their tree positions along the parent-child edge path.

The Controller dispatches the same `SortResult` ticks as all other algorithms. The View layer decides *where* to render each sprite based on the panel's algorithm type (tree layout for Heap Sort, flat row for others).

## Panel Runtime State Machine

Each panel maintains one of the following states:

- idle_paused
- animating_operation (includes both motion animations and static highlight durations)
- waiting_for_next_tick
- completed
- failed

State transitions:

idle_paused → waiting_for_next_tick when Play begins
waiting_for_next_tick → animating_operation when a SortResult is fetched
animating_operation → waiting_for_next_tick when animation finishes
waiting_for_next_tick → completed when completion tick received
waiting_for_next_tick → failed when failure tick received

### Multi-Tick Logical Operations (Heap Sort Sift-Down)

The `animating_operation` state processes **one tick at a time** — it does not batch or group ticks. A single "logical" sift-down step in Heap Sort spans multiple ticks (T3 → T1 → T1 → T2), but the state machine treats each tick as an independent `animating_operation → waiting_for_next_tick` cycle. The Controller does not need to know that these ticks are part of the same logical sift-down level.

This preserves MVC decoupling: the Model decides tick ordering and content (the strict T3 → T1 → T2 sequence defined in 05_ALGORITHMS_VIS_SPEC Section 4.4), while the Controller simply maps each tick's `OpType` to a duration and dispatches sprite commands. The Controller's only Heap Sort-specific behavior is the `sift_down_cadence` flag (see 10_ANIMATION_SPEC Section 5.4.2), which adjusts duration selection — it does not alter the state machine topology.

**Static highlight durations within `animating_operation`:** Not all ticks in `animating_operation` produce sprite movement. T3 Range Emphasis ticks (Heap Sort boundary highlights and Logical Tree Highlights) consume `dt` against `current_operation_remaining_ms` like any other tick, but they dispatch **no `(x, y)` target changes** to sprites. The Controller must not attempt to compute or force movement logic for these ticks — they are purely chromatic (highlight color applied, duration elapses, state transitions to `waiting_for_next_tick`). This is a key distinction: `animating_operation` means "a tick is active and consuming time," not "sprites are in motion." The same applies to T1 compare ticks for Selection Sort and Heap Sort, which apply highlights without positional displacement (unlike Bubble Sort's compare-lift or Insertion Sort's key-lift, which do move sprites during T1).

**Invariant:** The state machine transition graph is identical for all four algorithms. Algorithm-specific behavior is expressed through tick content (`OpType`, `highlight_indices`) and duration selection, never through additional states or transitions.

## Operation Timing

Each panel maintains:

- current_operation_remaining_ms
- pending_generator
- elapsed_time_ms

During each frame:

1. Controller subtracts dt from current_operation_remaining_ms.
2. When remaining time ≤ 0, the next SortResult is requested.
3. The SortResult.operation_type determines the duration of the next animation.
