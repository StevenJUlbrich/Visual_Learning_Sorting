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
│       │   ├── ui.py               # Custom Button class
│       │   └── grid.py             # VisualizerWindow (responsive layout)
│       ├── controllers/      
│       │   ├── __init__.py
│       │   └── main_controller.py  # Main execution loop
│       └── main.py                 # Application entry point with config flags
├── assets/                         # Contains TTF fonts (e.g., Inter, FiraCode)
└── tests/                    

```

## 3. Core Architectural Directives

### A. State Management (The Pure Result Pattern)

**CRITICAL:** Do NOT use standard Python `Exception` raising for algorithm logic flow or domain errors. We are using a Go/Rust-inspired Pure Result Pattern.

* Every algorithm is a Generator.
* Every single "tick" (atomic operation) MUST yield a `SortResult` dataclass.
* **Recursive Bubbling:** For recursive algorithms like Merge Sort, do NOT use `yield from`. You must explicitly unpack and check the success state to bubble failures up the call stack.

### B. Array State Immutability

**CRITICAL:** Python passes lists by reference. When yielding the `array_state` to the View layer, you MUST yield a frozen copy of the list (`self.data.copy()`).

### C. UI/UX Principles (Modern Pygame)

* **No legacy colors:** Use the muted dark-mode hex/RGB tuples defined in `views/theme.py`.
* **No system fonts by default:** Attempt to load custom `.ttf` files from `assets/`. Implement a `try/except FileNotFoundError` block to gracefully degrade to `pygame.font.SysFont`.
* **Anti-aliasing:** All `font.render()` calls MUST have `antialias=True`.
* **Geometry:** Use `border_radius` on Pygame rectangles.

### D. UI Control Scope (Custom Clickable UI)

**CRITICAL:** Do NOT import any third-party UI libraries (e.g., `pygame_gui`). The application must feature a custom, minimal clickable UI built entirely with Pygame primitives.

* **The Component:** Create a `Button` class in `src/visualizer/views/ui.py`. It must use `pygame.draw.rect` with `border_radius` for styling and center rendered text within its bounding box.
* **The Controls:** The UI must include buttons for: Play/Pause, Step Forward (only active when paused), Restart, and Speed Toggle (1x, 1.5x, 2x).
* **Collision Logic:** The Controller layer MUST handle button interactions by checking `button.rect.collidepoint(event.pos)`.

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

* **The "Step" Definition:** A "step" is strictly defined as any yielded `SortResult` where `success=True` and `is_complete=False`. The View layer must simply increment its counter upon receiving this state.

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
* **Merge Sort Specifics:** In-place modification is required for UI stability. Create a temp copy of the sub-array during the `merge` phase and overwrite `self.data` using a pointer to maintain array length for the Pygame renderer.

### Views (The Rendering Engine)

* **Color Semantics (Per-Algorithm Accents):** The visualizer uses specific accent colors per algorithm defined in `theme.py` (Bubble = Cyan `(0, 255, 255)`, Insertion = Magenta `(255, 0, 255)`, Merge = Purple `(170, 0, 255)`, Selection = Red `(255, 80, 80)`). The `AlgorithmPanel` must accept an `accent_color` and apply it to indices in `highlight_indices`. Resting numbers use `Colors.ARRAY_DEFAULT`.
* **Responsive Layout:** The `VisualizerWindow` must dynamically calculate the 2x2 grid and UI button placement based on the provided width and height.

### Controllers (The Main Loop)

* **Configurable Resolution:** `main.py` must support initializing the `MainController` with either Landscape (1280x720) or Portrait (720x996) resolutions.
* **Tick Execution:** Iterates through generators calling `next(gen)` once per frame per active algorithm.
* **Event Handling:** Explicitly handles `pygame.MOUSEBUTTONDOWN` for UI interaction:
* **Play/Pause:** Toggles the global pause state.
* **Step:** Advances the tick logic exactly once manually.
* **Restart:** Re-instantiates the model classes with a fresh copy of the initial array.
* **Speed Toggle:** Adjusts `pygame.time.Clock().tick()` multipliers.
