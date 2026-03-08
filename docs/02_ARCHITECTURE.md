# 02 ARCHITECTURE - MVC, Pygame Sprites, Independent Queues

## Directory Tree

```text
src/visualizer/
├── main.py                 # App entry point, config loading, and root Controller instantiation
├── models/
│   ├── contracts.py        # SortResult, OpType, BaseSortAlgorithm
│   ├── bubble.py           # BubbleSort implementation
│   ├── insertion.py        # InsertionSort implementation
│   ├── merge.py            # MergeSort implementation
│   └── selection.py        # SelectionSort implementation
├── views/
│   ├── window.py           # Pygame display init and master 2x2 grid layout
│   ├── panel.py            # Individual algorithm rendering frame and UI counters
│   └── sprite.py           # NumberSprite class containing dt interpolation math
└── controllers/
    └── orchestrator.py     # Independent queue management, operation timing, and event loop
```

## Architecture Style

Strict MVC under `src/visualizer/`.

- `models/`: algorithms + shared data contracts. Logic is strictly isolated here.
- `views/`: Pygame rendering, UI layouts, and the `NumberSprite` entity system. Theme utilizes Option B (each panel has an accent color tinted per algorithm).
- `controllers/`: app lifecycle, input handling, and independent queue orchestration.'
- main.py owns the pygame event loop.
- Controller exposes update(dt).
- View exposes render().

## Runtime Model: The Decoupled Race

The execution operates on two parallel, decoupled tracks:

1. **Render Track (The View):** A high-frequency Pygame `while True:` loop runs continuously (e.g., 60 FPS). On every frame, it calculates the delta-time (`dt`) and calls `update(dt)` on all active Sprite entities, ensuring smooth visual interpolation regardless of algorithm state.
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

The View layer MUST maintain a persistent list of NumberSprite objects initialized at startup. When receiving a new SortResult.array_state, the View MUST NOT destroy and recreate sprites. Instead, it must map the values in the new array_state to the existing NumberSprite instances and invoke their set_target(new_x, new_y) methods to initiate the tweening.

- Maintain `NumberSprite` objects (tracking value, exact floating-point `(x, y)` coords, and target coords).
- Execute linear interpolation formulas to move sprites smoothly over the `dt` window.
- Dynamically calculate resting layout coordinates based on the active Option C orientation flag.

### Controller Responsibilities

- Instantiate models with shared initial data.
- Map `SortResult` actions to specific physical destinations and simulated time costs.
- Track independent elapsed time for each panel to simulate the "race".

## Error Model

- Domain and algorithm-flow failures must be represented by `SortResult(success=False, ...)`.
- Controller must not crash app for one algorithm failure; it deactivates that algorithm and continues others.

## Config + Runtime Targets (Option C)

- Landscape target: `1280x720`.
- Portrait target: `720x996`.
- Target is determined via a config flag. The View dynamically calculates origin `(x, y)` baseline slots for the arrays based on the active resolution.
- Extensibility Rules: New algorithms must implement `BaseSortAlgorithm` and `sort_generator` contract. Max simultaneous displayed algorithms remains 4 in v1.

## Sprite Identity

- Sprites represent array positions, not values.
- Each sprite has a stable ID created at initialization.
  