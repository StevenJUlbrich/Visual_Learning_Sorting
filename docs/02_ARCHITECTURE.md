# 02 ARCHITECTURE.md (Rewritten)

## Architecture Style

Strict MVC under `src/visualizer/`.

* `models/`: algorithms + shared data contracts. Data processing logic is strictly isolated here.
* `views/`: Tkinter front-end (`Canvas` and `Frame` widgets), theme (Option B accents), layout, and coordinate interpolation (tweening).
* `controllers/`: app lifecycle, Tkinter event binding, independent animation queue orchestration.

No import bleeding across layers beyond required contracts.

## Runtime Model: The Decoupled Race

* The application uses a Tkinter `mainloop()` driven by `root.after()` scheduled callbacks.
* The Controller owns global app state (`paused`, speed multiplier) and manages four **independent algorithm queues**.
* The execution operates on two parallel tracks:
  
1. **Logical Track (The Generators):** The Controller pulls `SortResult` yields from each algorithm independently. Instead of executing uniformly, the Controller assigns a simulated time cost (in milliseconds) to each operation type (e.g., Compare, Swap).
2. **Render Track (The View):** The View runs a high-frequency render loop (e.g., 60fps). It consumes operations from each panel's queue and interpolates the `(x, y)` coordinates of visual nodes smoothly over the duration of the assigned time cost.

## Independent Queue Semantics

* Each active algorithm generator is advanced based on its own elapsed simulated time, not a global clock.
* Fast algorithms will exhaust their queues and reach terminal states before slower algorithms.
* Completed/failed algorithms stop their individual timers but remain visually static on screen.
* This enables a true side-by-side race where the speed of completion directly reflects the algorithm's operational efficiency.

## Component Boundaries

### Model Responsibilities

* Maintain algorithm-local mutable array copy.
* Yield `SortResult` for every atomic operation and terminal state.
* Never mutate View or Controller state.

### View Responsibilities

* Maintain distinct `VisualNode` objects (tracking value, current `(x, y)`, and target `(x, y)`).
* Execute smooth tweening formulas to animate nodes between states over a specified time duration.
* Keep panel-local UI counters (Steps, Time, Comparisons, Writes) updated.
* Never execute algorithm logic.

### Controller Responsibilities

* Instantiate models with shared initial data copied per model.
* Map `SortResult` actions to specific duration costs.
* Own generator lifecycle and halt policy (`success=False` or `is_complete=True`).
* Translate UI events into control state changes.

## Error Model

* Domain and algorithm-flow failures must be represented by `SortResult(success=False, ...)`.
* Controller must not crash app for one algorithm failure; it deactivates that algorithm and continues others.

## Config + Runtime Targets (Option C)

* Landscape target: `1280x720`.
* Portrait target: `720x996`.
* Target is determined via a config flag. The View dynamically calculates origin `(x, y)` baseline slots for the arrays based on the active resolution.
* Extensibility Rules: New algorithms must implement `BaseSortAlgorithm` and `sort_generator` contract. Max simultaneous displayed algorithms remains 4 in v1.
