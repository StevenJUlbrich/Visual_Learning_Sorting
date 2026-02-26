Welcome back. It is great to see the handoff document fully populated. With our pure MVC structure and strict Go/Rust-style data contract locked in, we are ready to build the final major component of your application.

### Kicking off Brick 5: The Controller

The Controller acts as the orchestrator. Its responsibility is to initialize the shared state, start the Pygame event loop, listen for user inputs, and advance the algorithm generators exactly one "tick" per frame. Crucially, it must respect the strict `SortResult` contract we built in Brick 2: if an algorithm yields a failure state, the Controller must immediately halt that specific generator while allowing the others to continue.

Here is the implementation of the main controller and the application entry point.

### 1. The Main Controller Implementation

Create a new file in your controllers directory.

```python
# src/visualizer/controllers/main_controller.py
import pygame
import sys

from ..models.bubble_sort import BubbleSort
from ..models.selection_sort import SelectionSort
from ..models.insertion_sort import InsertionSort
from ..models.merge_sort import MergeSort
from ..models.state import SortResult
from ..views.grid import VisualizerWindow

class MainController:
    """
    The orchestrator of the application.
    Wires the Models to the View and manages the global tick system and event loop.
    """
    def __init__(self):
        pygame.init()
        
        # 1. Initialize the View
        self.window = VisualizerWindow(width=1280, height=720)
        
        # 2. Initialize Shared Data (The Worst-Case Array)
        # A reverse-sorted 7-element array provides maximum visual contrast
        self.initial_data = [7, 6, 5, 4, 3, 2, 1]
        
        # 3. Initialize the Models
        self.models = [
            BubbleSort(self.initial_data),
            SelectionSort(self.initial_data),
            InsertionSort(self.initial_data),
            MergeSort(self.initial_data)
        ]
        
        # 4. Wire the View Panels
        # Explicitly passing the complexities to avoid brittle docstring parsing
        algo_info = [
            ("Bubble Sort", "O(n²)"),
            ("Selection Sort", "O(n²)"),
            ("Insertion Sort", "O(n²)"),
            ("Merge Sort", "O(n log n)")
        ]
        self.window.setup_panels(algo_info)
        
        # 5. Setup Generator Tracking
        self.generators = {m.name: m.sort_generator() for m in self.models}
        self.current_states: dict[str, SortResult | None] = {m.name: None for m in self.models}
        self.active_algorithms = {m.name: True for m in self.models}
        
        # 6. Global State Controls
        self.clock = pygame.time.Clock()
        self.base_fps = 2  # 2 frames per second makes the atomic steps readable
        self.speed_multiplier = 1.0
        self.paused = True # Start paused so the user can inspect the initial array

    def run(self) -> None:
        """The main application loop."""
        running = True
        
        # Do an initial draw to show the empty panels and starting titles
        self.window.draw_frame(self.current_states)
        
        while running:
            running = self._handle_events()
            
            if not self.paused:
                self._advance_ticks()
            
            self.window.draw_frame(self.current_states)
            
            # Control the execution speed
            self.clock.tick(int(self.base_fps * self.speed_multiplier))
            
        pygame.quit()
        sys.exit()

    def _handle_events(self) -> bool:
        """Processes Pygame events like quitting, pausing, and speed adjustments."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_1:
                    self.speed_multiplier = 1.0
                elif event.key == pygame.K_2:
                    self.speed_multiplier = 1.5
                elif event.key == pygame.K_3:
                    self.speed_multiplier = 2.0
                    
        return True

    def _advance_ticks(self) -> None:
        """
        Advances every active algorithm generator by exactly one step.
        Enforces the Pure Result Pattern contract.
        """
        for name, gen in self.generators.items():
            if not self.active_algorithms[name]:
                continue
                
            try:
                # Ask the algorithm for its next state
                result = next(gen)
                self.current_states[name] = result
                
                # Enforce the contract: halt if failed or completed
                if not result.success or result.is_complete:
                    self.active_algorithms[name] = False
                    
            except StopIteration:
                # Failsafe in case a generator exhausts without yielding a complete state
                self.active_algorithms[name] = False

```

### 2. The Application Entry Point

To keep things perfectly standard, create your entry point at the root of the `src` directory.

```python
# src/visualizer/main.py
from visualizer.controllers.main_controller import MainController

def main():
    """Application entry point."""
    app = MainController()
    app.run()

if __name__ == "__main__":
    main()

```

### 3. Architectural Takeaways

This controller effectively realizes all the advanced concepts we planned:

* **The Global Tick:** In `_advance_ticks`, the Controller loops through the dictionary of generators, calling `next(gen)` exactly once per active model. This means that if you hit the spacebar, Bubble Sort does one comparison, Merge Sort does one divide/merge step, and Pygame draws them both to the screen simultaneously. It forces a perfect 1:1 visual comparison of operational efficiency.
* **Honoring the Contract:** Look at `if not result.success or result.is_complete: self.active_algorithms[name] = False`. The Controller never inspects the arrays to see if they are sorted. It trusts the `SortResult` dataclass completely. If Merge Sort bubbles up a failure, the Controller just flips that algorithm's active flag to `False`. The panel will cleanly stop ticking while the other three algorithms keep running.
* **Input Decoupling:** The UI speed controls (1x, 1.5x, 2x using the number keys) do not alter the algorithm logic at all. They simply change the multiplier passed into `self.clock.tick()`.

---

With these two files, the application is functionally complete. The MVC triad is closed.

Would you like to run the `uv run python src/visualizer/main.py` command to test the application in your WSL environment, or do you want to add an on-screen visual indicator for the current playback speed first?