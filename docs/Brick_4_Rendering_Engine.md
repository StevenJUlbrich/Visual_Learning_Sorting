### Kicking off Brick 4: The Rendering Engine

In Brick 3, we built the "brains" of the operation. Now, we need to build the "face." The View layer's entire job is to take the `SortResult` dataclass yielded by our algorithms and translate it into pixels on the screen. Because we committed to a modern UI (avoiding the 1990s legacy Pygame look), we need to be very intentional about our colors, typography, and geometry.

Here is how we should break down Brick 4:

1. **The Theme (`theme.py`):** Before we draw any shapes, we need a centralized source of truth for our color palette and typography. Hardcoding `(255, 0, 0)` into drawing functions is a massive anti-pattern. We will define a sleek dark-mode palette and our font configurations here.
2. **The Panel (`panel.py`):** This is the core view component. An `AlgorithmPanel` class will represent one quadrant of our 2x2 grid. It will take a Pygame surface, the algorithm's name, its Big-O complexity, and the current `SortResult`, and handle all the rendering (the numbers, the active highlight colors, and the step counter).
3. **The Grid Manager (`grid.py`):** A lightweight view class to orchestrate the four panels and handle the global spacing/padding so the layout looks like a professional application.

### The Architectural "Why"

By keeping the View layer completely ignorant of *how* the algorithms work, we preserve our MVC boundaries. The `AlgorithmPanel` won't know if it's drawing Merge Sort or Bubble Sort; it only knows how to draw the array state and highlight the indices passed to it via the `SortResult`. If you decide to add Quick Sort later, you won't have to touch a single line of Pygame rendering code.

Would you like me to draft the `theme.py` file with our modern dark-mode palette first, or should we jump straight into outlining the Pygame rendering logic for the `AlgorithmPanel`?