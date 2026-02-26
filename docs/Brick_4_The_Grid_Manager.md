This is the final piece of our View layer. We need a manager to orchestrate the main Pygame window and mathematically slice it up into a perfectly spaced 2x2 grid for our four `AlgorithmPanel` instances.

By building a dedicated `VisualizerWindow` class, we keep the Controller's logic incredibly clean later on. The Controller will simply hand this window a dictionary of states, and the window will route those states to the correct panels.

Here is the implementation of our Grid Manager.

### 1. The Grid Manager Implementation

Create a new file in your views directory.

```python
# src/visualizer/views/grid.py
import pygame

from ..models.state import SortResult
from .theme import Colors, Typography
from .panel import AlgorithmPanel

class VisualizerWindow:
    """
    Manages the main Pygame display and the 2x2 grid layout.
    Routes state updates to the appropriate individual algorithm panels.
    """
    def __init__(self, width: int = 1280, height: int = 720):
        self.width = width
        self.height = height
        self.padding = 20
        
        # Initialize the main display surface
        pygame.display.set_caption("Sorting Algorithm Visualizer")
        self.screen = pygame.display.set_mode((self.width, self.height))
        
        # Load our typography system and trigger the asset loading
        self.typography = Typography()
        self.typography.initialize_fonts()
        
        # Dictionary to hold our 4 panel instances
        self.panels: dict[str, AlgorithmPanel] = {}

    def setup_panels(self, algorithms_info: list[tuple[str, str]]) -> None:
        """
        Calculates the 2x2 grid math and instantiates the panels.
        Accepts a list of tuples: (Algorithm Name, Big-O Complexity)
        """
        if len(algorithms_info) > 4:
            raise ValueError("The grid manager only supports a maximum of 4 panels.")

        # Calculate dynamic width and height for a 2x2 grid
        # 3 paddings horizontally (left, middle, right) and vertically
        panel_width = (self.width - (self.padding * 3)) // 2
        panel_height = (self.height - (self.padding * 3)) // 2

        # Define the (x, y) starting coordinates for the 4 quadrants
        quadrants = [
            (self.padding, self.padding),                                              # Top-Left
            (self.padding * 2 + panel_width, self.padding),                            # Top-Right
            (self.padding, self.padding * 2 + panel_height),                           # Bottom-Left
            (self.padding * 2 + panel_width, self.padding * 2 + panel_height)          # Bottom-Right
        ]

        for i, (name, complexity) in enumerate(algorithms_info):
            x, y = quadrants[i]
            rect = pygame.Rect(x, y, panel_width, panel_height)
            
            # Instantiate the Panel and store it by algorithm name for easy routing
            self.panels[name] = AlgorithmPanel(
                surface=self.screen,
                rect=rect,
                title=name,
                complexity=complexity,
                typography=self.typography
            )

    def draw_frame(self, states: dict[str, SortResult | None]) -> None:
        """
        The main render pass for the entire window.
        Clears the screen, routes states to panels, and swaps the display buffer.
        """
        # 1. Clear the screen with our deep slate gray background
        self.screen.fill(Colors.APP_BACKGROUND)

        # 2. Command each panel to draw its current state
        for name, panel in self.panels.items():
            # If a state exists for this panel, pass it down. Otherwise, pass None.
            current_state = states.get(name)
            panel.draw(current_state)

        # 3. Swap the Pygame display buffers to render the frame to the user
        pygame.display.flip()

```

### 2. Architectural Takeaways

This file perfectly bridges the gap between your Pygame logic and your strict MVC requirements:

* **Dynamic Math vs. Hardcoding:** Look at `setup_panels`. Instead of manually typing `pygame.Rect(20, 20, 600, 300)`, we calculate `panel_width` and `panel_height` dynamically based on the window size and padding. If you later decide to change the resolution from 720p to 1080p, the grid will automatically scale perfectly without touching a single line of panel math.
* **State Routing:** The `draw_frame` method expects a dictionary mapping the algorithm's name to its current `SortResult` (e.g., `{"Bubble Sort": SortResult(...)}`). The window doesn't inspect the array or check if it's sorted; it acts purely as a router, handing the data to the correct `AlgorithmPanel` and telling it to paint.
* **Double Buffering:** Pygame uses a double-buffer system. We clear the screen (`self.screen.fill`), draw all four panels in memory, and then call `pygame.display.flip()` exactly once per frame. This eliminates screen tearing and flickering, which is crucial for a smooth animation.

---

### Brick 4 Complete

We have officially finished the View layer. We have our `Theme` defining our modern aesthetic, our `AlgorithmPanel` handling the granular array rendering, and our `VisualizerWindow` orchestrating the 2x2 layout.

The only piece left is **Brick 5: The Controller**.

This is where we will write the main game loop, initialize the shared worst-case array, start the four algorithm generators, and manage the global "tick" system that advances them all simultaneously.

Are you ready to move to Brick 5 and wire the Models and Views together to bring this application to life?