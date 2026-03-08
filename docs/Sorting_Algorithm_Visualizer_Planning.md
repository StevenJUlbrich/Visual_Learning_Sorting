# Sorting_Algorithm_Visualizer_Planning.md (Rewritten)

**Status:** Historical — superseded by locked specification docs
**Purpose:** Portfolio piece — educational tool to help others learn sorting algorithm mechanics

---

## Reference Material

Reviewed video: `Sorting_Algorithm___Dark_Code.mp4` — a 17-second, 720×996 portrait animation showing four sorting algorithms (Bubble, Insertion, Merge, Selection) running simultaneously on a dark background with number-based arrays and color-coded highlights per algorithm.

### Video Observations

* Simultaneous side-by-side comparison is intuitive.
* Color-coding per algorithm (cyan=Bubble, magenta=Insertion, purple=Merge, red=Selection).
* Merge Sort shows sub-array brackets during divide-and-conquer — nice touch.
* **Bug noted:** Selection Sort ends with `[1, 3, 7, 9, 12, 11]` — not fully sorted.

---

## Decided — Architecture & Animation Engine

* **Pattern:** MVC.
* **Front End:** Pygame using `pygame.sprite.Sprite` and `pygame.sprite.Group`. Each number is an independent sprite object with its own `update(dt)` delta-time logic to handle physical movement and coordinate math.
* **Independent Queues:** Algorithms run concurrently but independently.
* **Sort algorithms:** Each sorting algorithm is its own class with a common interface.
* **Generator/yield pattern:** Each sort class yields at every atomic operation with metadata describing what just happened.

* **Independent Queues:** Algorithms run concurrently but independently. * **Sort algorithms:** Each sorting algorithm is its own class with a common interface.
* **Generator/yield pattern:** Each sort class yields at every atomic operation with metadata describing what just happened.

## Decided — Visual Style

* **Sprite Entities:** Numbers acting as physical sprites, not static bars.
* **Theme (Option B):** Each panel has an accent color tinted per algorithm to strongly establish identity.
* **Layout (Option C):** 2×2 grid supporting both landscape and portrait window orientations via a config flag.
* **Speed selection:** 1x, 1.5x, 2x
* **Distinctive colors** as each part/phase completes
* **No history** of changes — user can restart to re-watch

## Decided — Pacing & Control

* **Operation-Weighted Timing:** Different algorithmic operations (compares, swaps) take different amounts of simulated time. Fast algorithms finish their visual race sooner than slow algorithms.
* **UI Controls (Path 2):** Dedicated UI control scoping for playback.
* **Global pause/resume**.

## Decided — Data & State

* **Same array** across all four algorithms.
* **7 elements**.
* **Preset worst-case array** as default.

## Not In Scope (Current Phase)

* User input for custom arrays
* Bar-based visualization
* More than 4 simultaneous algorithms
* Video export (handled externally via Camtasia)
* History/replay of changes
  