# 10 ANIMATION SPEC - Sprite Motion Contracts

Scope: Defines how the Pygame View layer translates discrete logical operations into smooth, physical sprite motion.

## 1) Interpolation (Tweening) Rules

- Motion must occur smoothly over the duration commanded by the Controller (e.g., 400ms for a swap).
- Standard spatial movement utilizes float-based linear interpolation factoring in Pygame's frame delta-time (`dt`).
- The internal sprite state must track `exact_x` and `exact_y` as floats to prevent rounding drift, syncing to the integer `rect` only at the final render step.

## 2) Algorithm-Specific Motion Signatures

### 2.1 Bubble & Selection Sort (Swaps)

- **Action:** Two elements exchange indices.
- **Motion:** Both sprites interpolate their `x` coordinates to the other's home position. To prevent visual collision, one sprite applies a temporary negative `y` offset (arcs up) while the other applies a positive `y` offset (arcs down) during the transit.
  - Left sprite arcs upward, right sprite arcs downward.

### 2.2 Insertion Sort (Lift and Drop)

- **Action:** A key is selected, elements shift, and the key is placed.
- **Motion (Lift):** The selected key visually "lifts" by subtracting 30 pixels from its `y` coordinate, holding that elevation.
- **Motion (Shift):** Shifted elements slide horizontally.
- **Motion (Drop):** The held key smoothly returns to the base `y` line at its newly sorted index.

### 2.3 Merge Sort (Auxiliary Array)

- **Action:** Elements are sorted into a temporary array segment.
- **Motion:** The View defines an auxiliary `y` row below the main array. Sprites involved in the active merge segment drop to this row, sort horizontally, and then the entire group slides back up to the primary `y` line upon completion.
