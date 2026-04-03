# Brick 7: Bubble Sort Animation Contract

**File:** `docs/contracts/BUBBLE_SORT_ANIMATION.md`

## 1. Overview

This contract defines the strict visual choreography for the Bubble Sort panel. The defining visual signature of Bubble Sort is the **3-Phase Compare-Lift**—where adjacent pairs are physically elevated into a dedicated compare lane to isolate the comparison from the rest of the array.

## 2. Dedicated UI Assets

The Bubble Sort panel requires the following specific View assets:

* **`ComparisonPointer`**: A green upward-pointing arrow anchored below the baseline row. It translates horizontally to follow the active inner-loop index `j`.
* **`LimitLine`**: A vertical dashed boundary line situated *between* array slots. It marks the right-side sorted boundary and shrinks leftward after each outer loop pass.
* **HUD Counters**: A persistent overlay anchored in the bottom-left of the panel displaying live `Comparison Count` and `Exchange Count`.

## 3. The 3-Phase Compare-Lift Contract (Resolves Trap E)

When the model yields a `T1 Compare Tick` on `(j, j+1)`, the View must execute a strict 3-phase vertical animation within the 150ms tick duration. Implementing this as a static color highlight is a spec violation.

* **Lift Offset:** `compare_lane_y = home_y - 50px`. Both sprites lift together.
* **Color:** Both sprites transition to the universal active highlight color `(255, 140, 0)` orange exactly as the lift begins.

| Phase | Duration | Visual Action |
| :--- | :--- | :--- |
| **1. Ascent** | `0 - 67ms` | Sprites at `j` and `j+1` ease upward from `home_y` to `compare_lane_y`. |
| **2. Hold** | `67 - 100ms` | Sprites hold stationary at `compare_lane_y`. This guarantees the comparison is readable even if no swap occurs. |
| **3. Descent** | `100 - 150ms` | If no swap is commanded next, the sprites ease back down to `home_y` and lose their orange highlight. |

## 4. The Swap Contract (T2 Tick)

If the model determines a swap is necessary, it yields a `T2 Write/Mutation Tick` (400ms duration) on `(j, j+1)`.

**Crucial Choreography Note:** Unlike Selection or Heap Sort which use arc swaps, Bubble Sort executes a **linear horizontal slide while lifted**.

| Phase | Duration | Visual Action |
| :--- | :--- | :--- |
| **1. Pre-Lift (Optional)** | `0ms` | If the sprites are resting at `home_y` (because the T1 descent completed), they instantly snap or rapidly ease to `compare_lane_y`. |
| **2. Horizontal Exchange** | `0 - 300ms` | Both sprites maintain a fixed `y` of `compare_lane_y` while their `x` coordinates interpolate to exchange slots. |
| **3. Settle** | `300 - 400ms` | Both sprites descend vertically from `compare_lane_y` back to `home_y` in their new slot order. |

## 5. Pass Boundary Behavior

* The `ComparisonPointer` must never cross to the right of the `LimitLine`.
* At the end of every outer-loop pass, the `LimitLine` shifts exactly one slot to the left, visually walling off the newly sorted element at the end of the array.
* Elements to the right of the `LimitLine` are visually excluded from further scans but remain in the default array color until the final `T4 Completion Tick`.

## 6. Z-Ordering Guarantee

During any lift or lifted exchange, the sprites at `j` and `j+1` must be drawn on top of all other sprites on the baseline. Between the two lifted sprites, standard array index drawing order is maintained.

## 7. Worked Example (`[4, 7, 2, 6, 1, 5, 3]`)

**Pass 1, Initial Steps:**

1. **Start:** `LimitLine` is positioned to the right of index 6.
2. **T1 Compare `(0, 1)`:** The arrow moves to index 0. `4` and `7` turn orange and lift 50px into the compare lane. They hold.
3. **No Swap:** `4` is not greater than `7`. The pair descends to `home_y` and returns to the default blue.
4. **T1 Compare `(1, 2)`:** The arrow moves to index 1. `7` and `2` turn orange and lift 50px. They hold.
5. **T2 Swap `(1, 2)`:** `7` and `2` slide past each other horizontally while suspended in the compare lane. Once the horizontal exchange is complete, they descend to the baseline in the order `[..., 2, 7, ...]`. HUD Exchange Count increments.

