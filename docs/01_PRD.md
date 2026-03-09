# 01 PRD - Sorting Algorithm Visualizer

## Product Summary

An educational desktop visualizer that shows four sorting algorithms running concurrently. It features smooth, frame-by-frame sprite animations and independent operation timers, allowing learners to watch the algorithms physically "race" to sort the same data set.

## What It Is

- A Python + Pygame portfolio project focused on algorithm mechanics and animation physics.
- A fixed 4-panel comparison for Bubble Sort, Selection Sort, Insertion Sort, and Heap Sort.
- A sprite-based visualization where numbers move fluidly across the screen.
- A true race: algorithms operate on independent timers based on the simulated cost of their operations.

## Target User Experience

- User opens app and sees a clean 2x2 grid with all algorithms ready.
- App starts paused so the user can inspect the initial identical array states with the array being [7,6,5,4,3,2,1]
- User presses Play, and all four algorithms begin animating simultaneously. Faster algorithms physically complete their operations and halt their timers earlier than slower ones.
- User can pause mid-animation and step through logical operations. (Speed controls have been removed to ensure animation stability).

### Rendering Target

The application prioritizes seamless, fluid motion decoupled from strict frame rates.
Animations operate on a time-normalized progression ($t$) to ensure sprites reach their targets accurately even if hardware frame rates fluctuate.

## Scope

### In Scope (v1)

- 4 fixed algorithms: Bubble, Selection, Insertion, Heap.
- The array will be [7,6,5,4,3,2,1] for all algorithms.
- Pygame `Sprite` entity system for continuous `(x, y)` coordinate interpolation.
- Independent operation queues and visual timers.
- On-screen controls + keyboard shortcuts.
- Dynamic proportional resolution scaling. The UI geometry calculates dynamically at startup to support arbitrary window sizes cleanly (e.g., standard 1080p).
- Animations follow the motion contracts defined in 10_ANIMATION_SPEC.md.

### Default Dataset

The visualizer always initializes with the fixed array:

[7, 6, 5, 4, 3, 2, 1]

Array size for v1 is always 7 elements.
No runtime array editing exists in v1.

### Out of Scope (v1)

- Custom arrays or user input.
- Algorithm picker UI.
- Bar-chart visualizations.
- Sound effects.
