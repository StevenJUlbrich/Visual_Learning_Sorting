Starting with the Theme is the exact right move. In UI development, hardcoding `(255, 0, 0)` or `pygame.font.SysFont` deep inside your rendering loops is a massive source of technical debt. By isolating our colors and typography into a single configuration file, we guarantee consistency across the entire application and make future tweaks trivial.

Here is the concrete implementation of our modern, dark-mode theme.

### 1. The Theme Implementation

Create a new file in your views directory.

```python
# src/visualizer/views/theme.py
import logging
from dataclasses import dataclass
import pygame

@dataclass(frozen=True)
class Colors:
    """
    A modern, dark-mode color palette.
    Using muted RGB values to avoid the harshness of legacy pure colors.
    """
    # Backgrounds
    APP_BACKGROUND: tuple[int, int, int] = (30, 30, 36)      # Deep slate gray
    PANEL_BACKGROUND: tuple[int, int, int] = (45, 45, 53)    # Slightly lighter for elevation
    
    # Typography
    TEXT_PRIMARY: tuple[int, int, int] = (240, 240, 245)     # Off-white for readability
    TEXT_SECONDARY: tuple[int, int, int] = (170, 170, 180)   # Muted gray for step counters
    
    # Algorithm States
    ARRAY_DEFAULT: tuple[int, int, int] = (100, 150, 255)    # Soft blue for resting numbers
    ARRAY_HIGHLIGHT: tuple[int, int, int] = (255, 180, 50)   # Warm amber for active comparisons/swaps
    ARRAY_COMPLETE: tuple[int, int, int] = (80, 220, 120)    # Mint green for finished state
    ERROR_STATE: tuple[int, int, int] = (235, 80, 80)        # Soft red for explicit failures

class Typography:
    """
    Manages font loading with graceful degradation.
    Implements the fail-safe pattern discussed in our architecture.
    """
    def __init__(self):
        self.title_font: pygame.font.Font | None = None
        self.body_font: pygame.font.Font | None = None
        self.number_font: pygame.font.Font | None = None

    def initialize_fonts(self) -> None:
        """
        Attempts to load modern TTF fonts from the assets folder.
        Falls back to safe system fonts if assets are missing.
        """
        # Ensure pygame font module is initialized
        if not pygame.font.get_init():
            pygame.font.init()

        try:
            # Assuming you will place 'Inter-Bold.ttf' and 'FiraCode-Regular.ttf' in /assets/
            self.title_font = pygame.font.Font("assets/Inter-Bold.ttf", 24)
            self.body_font = pygame.font.Font("assets/Inter-Regular.ttf", 16)
            self.number_font = pygame.font.Font("assets/FiraCode-Regular.ttf", 28)
            logging.info("Successfully loaded custom TTF assets.")
            
        except FileNotFoundError:
            # The Graceful Degradation Path
            logging.warning("AssetLoadError: Custom fonts not found. Falling back to system fonts.")
            
            # Using freetype/sysfont fallbacks that look reasonably modern
            self.title_font = pygame.font.SysFont("segoeui, arial", 24, bold=True)
            self.body_font = pygame.font.SysFont("segoeui, arial", 16)
            self.number_font = pygame.font.SysFont("consolas, courier", 28)

```

### 2. Architectural Takeaways

This file perfectly encapsulates the design principles we agreed upon in Brick 1:

* **Immutability:** The `Colors` dataclass uses `frozen=True`. This acts just like a `const` struct in Rust or Go. It physically prevents any other part of your application from accidentally overwriting a theme color at runtime.
* **Graceful Degradation:** The `initialize_fonts` method is a textbook example of safe UI engineering. It tries to load your slick, branded fonts (like *Inter* for the UI and *Fira Code* for the array numbers), but if a user clones your repo and forgets to download the assets, the app doesn't crash. It catches the error, logs a warning, and falls back to safe Windows/Linux system fonts.
* **Semantic Naming:** Notice we didn't name our colors `LIGHT_BLUE` or `YELLOW`. We named them `ARRAY_DEFAULT` and `ARRAY_HIGHLIGHT`. This decouples the *intent* of the color from its *value*. If you later decide your highlight color should be pink, you only change the RGB tuple here; the Pygame logic doesn't need to be updated.

---

### Next Step

With our colors and fonts safely locked in, we can start painting shapes on the screen.

Are you ready to build the **`AlgorithmPanel`** view, which will take our `SortResult` dataclass and use these theme colors to render the actual array numbers, highlighting, and Big-O step counters?