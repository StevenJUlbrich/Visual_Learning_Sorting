# 10 ANIMATION SPEC - Sprite Motion Contracts

Scope: Defines how the Pygame View layer translates discrete logical operations into smooth, physical sprite motion.

## 1) Interpolation (Tweening) Rules

- Motion must occur smoothly over the duration commanded by the Controller (e.g., 400ms for a swap).
- Standard spatial movement utilizes time-normalized easing functions (e.g., Quadratic or Cubic Ease-In-Out) based on elapsed operation time. The interpolation ratio (`t`) is calculated as:
  `t = elapsed_time / total_duration`

 $$t = \frac{\text{elapsed\_time}}{\text{total\_duration}}$$

- This guarantees that regardless of Pygame's frame delta-time (`dt`), the sprite will map exactly to the mathematical easing curve and land perfectly on target at `t=1.0`, eliminating physics derailment from frame drops.
- The internal sprite state must track `exact_x` and `exact_y` as floats, syncing to the integer `rect` only at the final render step.

## 2) Algorithm-Specific Motion Signatures

### 2.1 Bubble & Selection Sort (Swaps)

- **Action:** Two elements exchange indices.
- **Motion:** Both sprites ease their `x` coordinates to the other's home position. To prevent visual collision, one sprite applies a temporary negative `y` offset (arcs up) while the other applies a positive `y` offset (arcs down) mapped against the time curve.
  - Left sprite arcs upward, right sprite arcs downward.

### 2.2 Insertion Sort (Lift and Drop)

- **Action:** A key is selected, elements shift, and the key is placed.
- **Motion (Lift):** The selected key visually "lifts" by subtracting 30 pixels from its `y` coordinate, holding that elevation.
- **Motion (Shift):** Shifted elements slide horizontally.
- **Motion (Drop):** The held key smoothly returns to the base `y` line at its newly sorted index.

### 2.3 Heap Sort (In-Place Swaps with Boundary Highlight)

- **Action:** Two elements exchange indices during sift-down or root extraction.
- **Motion:** Identical arc swap motion to Bubble and Selection Sort — both sprites interpolate their `x` coordinates to each other's home position. Left sprite arcs upward, right sprite arcs downward.
- **Heap Boundary Emphasis (T3):** On a Range Emphasis tick, the sprites at indices `0..heap_size-1` briefly render in the panel accent color (orange) for the T3 duration (200ms) with no positional change. This visually communicates the active heap region to the learner.
- **No auxiliary row:** All Heap Sort motion occurs on the main array `y` row. There is no secondary animation row for Heap Sort.

#### Heap Sort Extraction Visual Sequence (per extraction step)

1. T3 tick fires: indices `0..end` flash accent color for 200ms (no movement).
2. T2 swap tick fires: root (index 0) and end (index `end`) exchange positions via arc motion over 400ms.
3. Sift-down T1/T2 ticks fire: comparisons highlight and swaps arc within the shrinking heap boundary.
4. The element now at index `end` renders in a "settled" dimmed color to show it has left the active heap.
