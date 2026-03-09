# 10 ANIMATION SPEC - Sprite Motion Contracts

Scope: Defines how the Pygame View layer translates discrete logical operations into smooth, physical sprite motion.

## 1) Frame Timing and Clock Contract

- The render loop uses `pygame.time.Clock` with a target of **60 FPS** via `clock.tick(60)`.
- Delta-time (`dt`) returned by the clock is **clamped to a maximum of 33ms** (equivalent to two frames at 60 FPS). This prevents a single large `dt` from overshooting sprite positions after hitches (window drag, OS sleep, debugger pause).
- Clamping formula applied each frame: `dt = min(clock.tick(60), 33)`.

## 2) Interpolation (Tweening) Rules

- Motion must occur smoothly over the duration commanded by the Controller (e.g., 400ms for a swap).
- Standard spatial movement utilizes time-normalized easing functions (e.g., Quadratic or Cubic Ease-In-Out) based on elapsed operation time. The interpolation ratio (`t`) is calculated and clamped as:

  `t = min(elapsed_time / total_duration, 1.0)`

- The clamp to `1.0` guarantees that regardless of Pygame's frame delta-time (`dt`), the sprite will never overshoot. The sprite maps exactly to the mathematical easing curve and lands perfectly on target at `t=1.0`, eliminating physics derailment from frame drops or accumulated float error.
- The internal sprite state must track `exact_x` and `exact_y` as floats, syncing to the integer `rect` only at the final render step.

## 3) Sprite Coordinate System

### 3.1 Anchor Point

- A sprite's `(exact_x, exact_y)` represents the **center** of the rendered text surface.
- At render time, the text surface is blitted with its center aligned to `(round(exact_x), round(exact_y))`.

### 3.2 Home Position

- `home_x`: the horizontal center of the sprite's assigned array slot, calculated as:
  `home_x = panel_rect.x + ARRAY_X_PADDING + (slot_index * slot_width) + (slot_width / 2)`
- `home_y`: the vertical baseline for the array row, calculated as:
  `home_y = panel_rect.y + panel_rect.height // 2`
- When a sprite is at rest (no active animation), `exact_x == home_x` and `exact_y == home_y`.

### 3.3 Slot Assignment

- When a `SortResult` provides a new `array_state`, the controller computes index transitions between the previous and new array states.
- Each sprite updates its `home_x` to the center of its newly assigned slot.
- Sprites interpolate from their current `(exact_x, exact_y)` toward the new `(home_x, home_y)` over the operation duration.

## 4) Render Order (Z-Ordering)

- Default draw order follows array index (index 0 drawn first, index 6 drawn last).
- During a swap animation, the **upward-arcing sprite** (left sprite) is drawn **last** (on top) so it visually passes over the downward-arcing sprite.
- During an Insertion Sort lift, the **lifted sprite** is drawn last (on top of shifted sprites).
- Outside of active animations, default index order is restored.

## 5) Algorithm-Specific Motion Signatures

### 5.1 Bubble & Selection Sort (Swaps)

- **Action:** Two elements exchange indices.
- **Motion:** Both sprites ease their `x` coordinates to the other's home position using the standard easing curve. To prevent visual collision, a vertical arc offset is applied using a sine curve mapped to the same time parameter `t`:
  - Arc offset formula: `arc_offset = arc_height * sin(pi * t)`
  - `arc_height = panel_height * 0.08`
  - Left sprite (lower index): `exact_y = home_y - arc_offset` (arcs upward).
  - Right sprite (higher index): `exact_y = home_y + arc_offset` (arcs downward).
- The arc peaks at `t=0.5` and returns to `home_y` at `t=1.0`.

### 5.2 Insertion Sort (Lift, Shift, and Drop)

- **Action:** A key is selected, elements shift right, and the key is placed at its sorted position.
- **Lift height:** `lift_offset = panel_height * 0.06` (proportional, not a fixed pixel value).
- **Motion sequence within the Insertion Sort tick group:**
  1. **Lift (key-selection T1 tick):** The selected key sprite eases from `home_y` to `home_y - lift_offset` over the T1 duration. The sprite remains elevated across all subsequent compare and shift ticks until the placement drop.
  2. **Compare and Shift (T1 compare + T2 shift ticks):** Shifted elements ease horizontally from their current slot to the adjacent slot using the standard easing curve. The lifted key sprite holds its elevated `y` position and does not move horizontally during compare or shift ticks.
  3. **Drop (T2 placement tick):** The lifted key sprite eases horizontally to its destination slot `home_x` and simultaneously eases vertically from `home_y - lift_offset` back to `home_y`, using the standard easing curve over the T2 duration.
- Easing for all three sub-motions uses the same ease-in-out curve as swaps.

### 5.3 Heap Sort (In-Place Swaps with Boundary Highlight)

- **Action:** Two elements exchange indices during sift-down or root extraction.
- **Motion:** Identical arc swap motion to Bubble and Selection Sort — both sprites interpolate their `x` coordinates to each other's home position. Left sprite arcs upward, right sprite arcs downward. Same `arc_height` and sine formula.
- **Heap Boundary Emphasis (T3):** On a Range Emphasis tick, the sprites at indices `0..heap_size-1` render in the panel accent color (orange) for the T3 duration (200ms) with no positional change. This visually communicates the active heap region to the learner.
- **No auxiliary row:** All Heap Sort motion occurs on the main array `y` row. There is no secondary animation row for Heap Sort.

#### Heap Sort Extraction Visual Sequence (per extraction step)

1. T3 tick fires: indices `0..end` render in accent color for 200ms (no movement).
2. T2 swap tick fires: root (index 0) and end (index `end`) exchange positions via arc motion over 400ms.
3. Sift-down T1/T2 ticks fire: comparisons highlight and swaps arc within the shrinking heap boundary.
4. The element now at index `end` renders in the settled/extracted color to show it has left the active heap.

## 6) Highlight Behavior

- Highlights apply **instantly** at tick start. There is no fade-in or fade-out transition.
- When the next tick begins, the previous tick's highlights are **replaced** by the new tick's `highlight_indices`. Indices not in the new set revert to their default color immediately.
- During pause, the current tick's highlights remain visible and frozen.
- During step mode, the stepped tick's highlights are visible for the duration of the step animation and persist until the next step or play action.

## 7) Pause and Resume Interpolation

- On pause, all sprite state is frozen: `exact_x`, `exact_y`, elapsed operation time, highlight colors, and the panel message line.
- On resume, each sprite's animation continues from the exact interrupted point. The remaining operation duration (`total_duration - elapsed_time`) is used to calculate the remaining `t` progression. No tick is re-fetched or restarted.

## 8) Step Mode Animation

- Step mode uses the **same operation duration and easing** as play mode (e.g., 400ms for a swap, 150ms for a compare).
- Step input is **ignored** while a step animation is still in progress. The user must wait for the current step animation to complete before stepping again.
- After the step animation completes, the app returns to paused state with all sprites at their final positions for that tick.

## 9) Restart During Animation

- If Restart is triggered while sprites are mid-animation, all sprites **snap instantly** to the initial array positions. There is no animated return.
- All animation state (elapsed time, interpolation progress, highlights) is discarded.
- The app enters paused state with a clean initial frame.
