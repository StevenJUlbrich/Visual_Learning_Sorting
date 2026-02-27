# Sorting Algorithm Visualizer — Project Planning Notes

> **SUPERSEDED**: This file is historical. All open questions below have been resolved.
> The authoritative sources are `docs/DECISIONS.md` and `docs/01_PRD.md` through `docs/10_CI.md`.
> Do not use this file to derive implementation decisions.

**Date:** February 22, 2026
**Status:** Historical — superseded by locked specification docs
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

## Open Questions (All Resolved)

> Every question below has been resolved. Resolution references are inline.

### Algorithm Selection — *Resolved: D-003, F-002*
- ~~Are the initial four fixed?~~ Yes, fixed set of four (D-003). Picker deferred (F-002).

### Worst-Case Array Definition — *Resolved: D-006*
- ~~Which array?~~ Identical `[7, 6, 5, 4, 3, 2, 1]` for all algorithms (D-006).

### Current Action Label — *Resolved: D-010, D-021*
- ~~Show action text or just colors?~~ Message line always visible with current action text (D-010, D-021).

### Big-O Labels — *Resolved: D-023*
- ~~Show complexity?~~ Yes, as `complexity` property on each algorithm class (D-023).

### Completed Panel Behavior — *Resolved: D-015*
- ~~Panel behavior on completion?~~ Completed panels remain visible and idle (D-015).

### Sound — *Resolved: F-004*
- ~~Add audio cues?~~ Deferred beyond v1 (F-004).

### Visual Identity — *Resolved: D-027*
- ~~Branding?~~ Standalone identity "Learn Visual - Expand Knowledge" (D-027).

### UI Elements Summary — *Resolved: D-012, D-013, D-022*
- Controls: Play/Pause, Step, Restart, Speed cycle (D-012, D-013).
- Keyboard bindings locked (D-022).

---

## Not In Scope (Current Phase)
- User input for custom arrays
- Bar-based visualization
- More than 4 simultaneous algorithms
- Video export (handled externally via Camtasia)
- History/replay of changes
