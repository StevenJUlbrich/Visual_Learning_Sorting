Here is a comprehensive **Agentic Context & Implementation Guide**. You can save this as `AGENT_PROMPT.md` and feed it directly into Cursor, Copilot, or any other agentic coding tool. It is written specifically for an AI to parse, understand, and strictly adhere to the architectural rules we established.

---

# Agentic Context & Implementation Guide

**Project:** Sorting Algorithm Visualizer
**Role:** AI Software Engineer / Coding Agent
**Objective:** Implement a production-ready, highly decoupled MVC Pygame application based on the following strict architectural constraints.

## 1. Environment & Tech Stack

* **Language:** Python 3.13
* **Environment:** Ubuntu WSL executing on a Windows 11 host.
* **Dependency Manager:** `uv`
* **Core Libraries:** `pygame` (Rendering engine)
* **Dev Tools:** `ruff` (Linting/Formatting), `pyright` (Strict type checking)

## 2. Directory Structure

You must strictly adhere to this MVC layout within the `src/` directory. No import bleeding.

```text
sorting-visualizer/
├── src/                      
│   └── visualizer/           
│       ├── __init__.py
│       ├── models/           
│       │   ├── __init__.py
│       │   ├── state.py            # Holds SortResult dataclass
│       │   ├── base.py             # Holds BaseSortAlgorithm ABC
│       │   ├── bubble_sort.py
│       │   ├── selection_sort.py
│       │   ├── insertion_sort.py
│       │   └── merge_sort.py
│       ├── views/            
│       │   ├── __init__.py
│       │   ├── theme.py            # Colors & Typography
│       │   ├── panel.py            # AlgorithmPanel class
│       │   └── grid.py             # VisualizerWindow (2x2 layout)
│       ├── controllers/      
│       │   ├── __init__.py
│       │   └── main_controller.py  # Main execution loop
│       └── main.py                 # Application entry point
├── assets/                         # Contains TTF fonts (e.g., Inter, FiraCode)
└── tests/                    

```

## 3. Core Architectural Directives

### A. State Management (The Pure Result Pattern)

**CRITICAL:** Do NOT use standard Python `Exception` raising for algorithm logic flow or domain errors. We are using a Go/Rust-inspired Pure Result Pattern.

* Every algorithm is a Generator.
* Every single "tick" (atomic operation) MUST yield a `SortResult` dataclass.
* **Recursive Bubbling:** For recursive algorithms like Merge Sort, do NOT use `yield from`. You must explicitly unpack and check the success state to bubble failures up the call stack:
```python
for result in self._merge_sort(left, mid):
    yield result
    if not result.success: return

```



### B. Array State Immutability

**CRITICAL:** Python passes lists by reference. When yielding the `array_state` to the View layer, you MUST yield a frozen copy of the list (`self.data.copy()`). If you yield the raw list, the background Pygame loop will render torn states.

### C. UI/UX Principles (Modern Pygame)

* **No legacy colors:** Do not use `(255, 0, 0)` or pure RGBs. Use the muted dark-mode hex/RGB tuples defined in `views/theme.py`.
* **No system fonts by default:** Attempt to load custom `.ttf` files from `assets/`. Implement a `try/except FileNotFoundError` block to gracefully degrade to `pygame.font.SysFont` if assets are missing.
* **Anti-aliasing:** All `font.render()` calls MUST have `antialias=True`.
* **Geometry:** Use `border_radius` on Pygame rectangles to ensure modern, rounded UI panels.

### D. UI Control Scope (Custom Clickable UI)

**CRITICAL:** Do NOT import any third-party UI libraries (e.g., `pygame_gui`). The application must feature a custom, minimal clickable UI built entirely with Pygame primitives.
* **The Component:** Create a `Button` class in `src/visualizer/views/ui.py`. It must use `pygame.draw.rect` with `border_radius` for styling and center rendered text within its bounding box.
* **The Controls:** The UI must include buttons for: 
  1. Play/Pause
  2. Step Forward (only active when paused)
  3. Restart (resets arrays to the initial worst-case state)
  4. Speed Toggle (cycles through 1x, 1.5x, 2x)
* **Collision Logic:** The Controller layer MUST handle button interactions by listening for `pygame.MOUSEBUTTONDOWN` events and checking `button.rect.collidepoint(event.pos)`.

## 4. Data Contracts

### The `SortResult` Contract

```python
from dataclasses import dataclass

@dataclass(slots=True)
class SortResult:
    success: bool
    message: str
    is_complete: bool = False
    array_state: list[int] | None = None
    highlight_indices: tuple[int, ...] | None = None
```

### The `BaseSortAlgorithm` Interface

```python
from abc import ABC, abstractmethod
from collections.abc import Generator
from .state import SortResult

class BaseSortAlgorithm(ABC):
    def __init__(self, data: list[int], name: str):
        self.name = name
        self.data = data.copy() # Isolate state
        self.size = len(self.data)

    @abstractmethod
    def sort_generator(self) -> Generator[SortResult, None, None]:
        pass

```

## 5. Component Implementation Details

### Models (The Algorithms)

* **Initial State:** All 4 algorithms receive the exact same worst-case array upon initialization: `[7, 6, 5, 4, 3, 2, 1]`.
* **Tick Cadence:** Yield a state *before* a swap (comparison highlight) and *after* a swap (placement highlight) to accurately visualize time complexity cost.
* **Merge Sort Specifics:** In-place modification is required for UI stability. Create a temp copy of the sub-array during the `merge` phase and overwrite `self.data` using a pointer to maintain array length for the Pygame renderer.

### Views (The Rendering Engine)

* **Color Semantics (Per-Algorithm Accents):** The visualizer does NOT use a global highlight color. The `AlgorithmPanel` `__init__` method MUST accept an `accent_color: tuple[int, int, int]` parameter. 
* **Highlighting Logic:** Inside `_draw_array`, if an index is in `highlight_indices`, it must be rendered using that specific panel's `accent_color`. Resting numbers use `Colors.ARRAY_DEFAULT`, and completed algorithms use `Colors.ARRAY_COMPLETE`.
* **Routing:** The `VisualizerWindow` must map the correct accent color from `theme.Colors` to the corresponding algorithm when instantiating the panels in `setup_panels`.
* **AlgorithmPanel:** Responsible for a single algorithm. Receives a `SortResult`. If `success=False`, it must draw an explicit Error UI border/message. Maps the array values into evenly spaced horizontal slots using `rect.center`.
* **VisualizerWindow:** Calculates dynamic width/height for a 2x2 grid based on window size. Routes `SortResult` dict to the 4 respective `AlgorithmPanel` instances.

### Controllers (The Main Loop)
* **MainController:** Holds the 4 generator instances and manages the global UI state.
* **Tick Execution:** Iterates through generators calling `next(gen)` once per frame per active algorithm.
* **Failure Handling:** If a generator yields `success=False`, set that algorithm's active flag to `False` but continue running the others.
* **Event Handling:** Explicitly handles `pygame.MOUSEBUTTONDOWN` for UI interaction.
  * **Play/Pause:** Toggles the global pause state.
  * **Step:** Advances the tick logic exactly once manually.
  * **Restart:** Re-instantiates the model classes with a fresh copy of the initial array and resets active flags.
  * **Speed Toggle:** Adjusts `pygame.time.Clock().tick()` multipliers.