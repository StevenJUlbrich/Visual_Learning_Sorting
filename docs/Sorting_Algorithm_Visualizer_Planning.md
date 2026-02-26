# Sorting Algorithm Visualizer — Project Planning Notes

**Date:** February 22, 2026
**Status:** Planning / Pre-Development
**Purpose:** Portfolio piece — educational tool to help others learn sorting algorithm mechanics

---

## Reference Material

Reviewed video: `Sorting_Algorithm___Dark_Code.mp4` — a 17-second, 720×996 portrait animation showing four sorting algorithms (Bubble, Insertion, Merge, Selection) running simultaneously on a dark background with number-based arrays and color-coded highlights per algorithm.

### Video Observations
- Simultaneous side-by-side comparison is intuitive
- Color-coding per algorithm (cyan=Bubble, magenta=Insertion, purple=Merge, red=Selection)
- Merge Sort shows sub-array brackets during divide-and-conquer — nice touch
- **Bug noted:** Selection Sort ends with `[1, 3, 7, 9, 12, 11]` — not fully sorted
- No step/comparison counters
- Arrays differ in size and values across algorithms (not a fair comparison)
- At 17 seconds, individual steps are hard to follow without pausing

---

## Decided — Architecture

- **Pattern:** MVC
- **Sort algorithms:** Each sorting algorithm is its own class with a common interface
- **Generator/yield pattern:** Each sort class yields at every atomic operation (one comparison, one swap, one shift, one placement) with metadata describing what just happened
- **Yield metadata drives:** color highlighting and step counter
- **Extensible:** Design allows adding new sort methods, but max 4 displayed simultaneously
- **Rendering engine:** Pygame
- **Output:** Application-based (use Camtasia for video capture if needed)

## Decided — Visual Style

- **Numbers, not bars** — bars show progress but numbers show mechanics (the educational point)
- **Step counter** per algorithm panel
- **Speed selection:** 1x, 1.5x, 2x
- **Distinctive colors** as each part/phase completes
- **No history** of changes — user can restart to re-watch
- **Layout:** 2×2 grid for four algorithm panels

## Decided — Pacing & Control

- **Step-by-step** with option for auto-play
- **Each algorithm advances one atomic operation per tick simultaneously** — all four yield their next operation on the same tick. This means Merge Sort finishes in fewer ticks than Bubble Sort, and the user watches that happen. That *is* the lesson.
- **Global pause/resume** (not per-panel)

## Decided — Data & State

- **Same array** across all four algorithms
- **7 elements**
- **Preset worst-case array** as default
- **No user input for custom arrays** (dropped for simplicity)

---

## Open Questions

### Algorithm Selection
- Are the initial four fixed (Bubble, Insertion, Merge, Selection), or is there a menu/UI to swap in others from a library?
- This affects whether a selector UI is needed now or just planned architecturally.

### Worst-Case Array Definition
- Worst case differs per algorithm. Reverse-sorted is worst for Bubble and Insertion, but Merge Sort is always O(n log n).
- Do we show "worst case for Bubble Sort" and let others run on that same array?
- Or a dropdown: "worst case for: [algorithm name]"?
- Or just one sensible default (reverse-sorted) since it demonstrates the most dramatic contrast?

### Current Action Label
- Should each panel show a small text label for the current action (e.g., "Comparing 7 and 3", "Swapping")?
- Or just let the colors tell the story?

### Big-O Labels
- Show algorithm complexity (O(n²), O(n log n)) alongside the step counter?
- Would reinforce theory connection.

### Completed Panel Behavior
- When an algorithm finishes before others, does its panel show a "Complete" state and sit idle?
- That idle time is a teaching moment — the user sees faster algorithms waiting.

### Sound
- Pitch-mapped tones for operations (common in sorting visualizations)?
- Or overkill for this project?

### Visual Identity
- Lightning Labs branding (matching Bucket Sort project)?
- Or separate identity for this project?

### UI Elements Summary (Confirmed So Far)
- Start / Step button
- Speed selector (1x, 1.5x, 2x)
- Restart button
- Pause/Resume (global)
- Step counter per panel

---

## Not In Scope (Current Phase)
- User input for custom arrays
- Bar-based visualization
- More than 4 simultaneous algorithms
- Video export (handled externally via Camtasia)
- History/replay of changes
