This is the exact piece where your Go/Rust-inspired data contract meets the visual layer. We are going to build the `AlgorithmPanel` class.

The core architectural rule for this class is **Single Responsibility**: The Panel has zero idea *how* an array gets sorted. It only knows how to look at the `SortResult` dataclass and paint those exact instructions onto its designated rectangle on the screen.

Here is the implementation of the `AlgorithmPanel`.

### 1. The Panel Implementation

Create a new file in your views directory.

```python
# src/visualizer/views/panel.py
import pygame

from ..models.state import SortResult
from .theme import Colors, Typography

class AlgorithmPanel:
    """
    Renders a single algorithm's state within a specific bounded rectangle.
    Completely decoupled from the sorting logic.
    """
    def __init__(self, surface: pygame.Surface, rect: pygame.Rect, 
                 title: str, complexity: str, typography: Typography):
        self.surface = surface
        self.rect = rect
        self.title = title
        self.complexity = complexity
        self.typography = typography
        self.step_counter = 0

    def draw(self, result: SortResult | None) -> None:
        """
        The main render pass for the panel. 
        Reads the Result object and determines whether to draw the happy or failure path.
        """
        # 1. Base Geometry: Draw the panel background with rounded corners
        pygame.draw.rect(
            self.surface, 
            Colors.PANEL_BACKGROUND, 
            self.rect, 
            border_radius=12
        )

        # If we haven't received a state yet, just draw the empty container
        if result is None:
            self._draw_header()
            return

        # 2. Branching: Handle the explicit Failure Path
        if not result.success:
            self._draw_header()
            self._draw_error_state(result.message)
            return

        # 3. Branching: Handle the Happy Path (Iterating or Complete)
        # Increment steps only if we aren't finished
        if not result.is_complete:
            self.step_counter += 1

        self._draw_header()
        
        # Draw the array, ensuring it exists before rendering
        if result.array_state:
            self._draw_array(
                array=result.array_state,
                highlights=result.highlight_indices or (),
                is_complete=result.is_complete
            )

    def _draw_header(self) -> None:
        """Draws the title, Big-O complexity, and step counter at the top of the panel."""
        if not self.typography.title_font or not self.typography.body_font:
            return

        # Title (Top Left)
        title_surf = self.typography.title_font.render(self.title, True, Colors.TEXT_PRIMARY)
        self.surface.blit(title_surf, (self.rect.x + 20, self.rect.y + 15))

        # Metrics: Complexity and Steps (Top Right)
        metrics_text = f"{self.complexity}  |  Steps: {self.step_counter}"
        metrics_surf = self.typography.body_font.render(metrics_text, True, Colors.TEXT_SECONDARY)
        
        # Right-align the metrics
        metrics_x = self.rect.right - metrics_surf.get_width() - 20
        self.surface.blit(metrics_surf, (metrics_x, self.rect.y + 20))

    def _draw_array(self, array: list[int], highlights: tuple[int, ...], is_complete: bool) -> None:
        """Draws the numbers evenly spaced across the panel."""
        if not self.typography.number_font or not array:
            return

        # Calculate horizontal spacing
        padding = 40
        available_width = self.rect.width - (padding * 2)
        slot_width = available_width / len(array)
        
        # Center the numbers vertically in the panel
        y_center = self.rect.y + (self.rect.height // 2)

        for idx, value in enumerate(array):
            # Determine the color based on the strict state rules
            if is_complete:
                color = Colors.ARRAY_COMPLETE
            elif idx in highlights:
                color = Colors.ARRAY_HIGHLIGHT
            else:
                color = Colors.ARRAY_DEFAULT

            # Render the number with anti-aliasing (True)
            text_surf = self.typography.number_font.render(str(value), True, color)
            
            # Calculate exact center for this specific number's slot
            x_center = self.rect.x + padding + (idx * slot_width) + (slot_width / 2)
            text_rect = text_surf.get_rect(center=(x_center, y_center))
            
            self.surface.blit(text_surf, text_rect)

    def _draw_error_state(self, error_message: str) -> None:
        """Draws the explicit failure state if the algorithm errors out."""
        if not self.typography.body_font:
            return
            
        # Tint the panel border red
        pygame.draw.rect(self.surface, Colors.ERROR_STATE, self.rect, width=3, border_radius=12)
        
        error_surf = self.typography.body_font.render(f"Failed: {error_message}", True, Colors.ERROR_STATE)
        error_rect = error_surf.get_rect(center=(self.rect.centerx, self.rect.centery))
        self.surface.blit(error_surf, error_rect)

```

### 2. Architectural Takeaways

This file perfectly realizes the vision we laid out in the planning phase:

* **Handling the Contract:** Look at `def draw(self, result: SortResult | None)`. This is the power of the Go/Rust pattern. We check `if not result.success` right away. The View doesn't have a massive `try/except` block catching Pygame rendering errors. It reads the explicit failure state bubbled up from your recursive Merge Sort and cleanly pivots to `_draw_error_state`.
* **Numbers vs. Bars:** Inside `_draw_array`, we mathematically divide the panel width by `len(array)` to create invisible "slots." By using `get_rect(center=...)`, the numbers map directly into the center of these slots regardless of array size. It keeps the UI looking clean and incredibly readable, which satisfies your educational goal.
* **Modern UI Enforcement:** Pygame's `border_radius=12` on the background rectangle, combined with the anti-aliased font rendering (`True` in `font.render`), completely strips away the 1990s aesthetic.

---

### Next Step

With the Panel built, we now have the brush to paint our algorithms. The final piece of the View layer is the **Grid/Window Manager**, which will initialize the main Pygame screen and arrange four of these `AlgorithmPanel` instances into a perfectly spaced 2x2 layout.

Shall we wire up that layout class to close out Brick 4?