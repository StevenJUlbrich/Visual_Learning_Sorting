# SELECTION SORT ANIMATION CONTRACT

## 1\. Dependencies & Cross-References

> **CRITICAL ARCHITECTURE NOTE:** This document defines choreography only. To prevent Agent Traps, it MUST be implemented in conjunction with:
>
> * `12_ANIMATION_FOUNDATION.md`: Governs sprite identity, global frame timing, `dt` clamping, and standard easing functions.
> * `04_UI_SPEC.md`: Governs layout math, font sizing, and panel container geometry.
> * `03_DATA_CONTRACTS.md`: Governs the exact `SortResult` payload shape yielded by the Model.

## 2\. Overview

This contract defines the strict visual choreography for the Selection Sort panel. The defining visual signature of Selection Sort is the **Scan-then-Swap** mechanic, communicated through a highly specific **Triple Pointer System** that tracks the sorted boundary, the current scan cursor, and the discovered minimum.

## 3\. Dedicated UI Assets & Visual Tokens

The Selection Sort panel requires three labeled pointer arrows.

* **`i` Pointer (Sorted Boundary):** A downward-pointing arrow positioned **above** the baseline row. Color: Primary Text `(240, 240, 245)`.
* **`j` Pointer (Scan Cursor):** An upward-pointing arrow positioned **below** the baseline row. Color: Active Highlight Orange `(255, 140, 0)`.
* **`min` Pointer (Minimum Tracker):** An upward-pointing arrow positioned **below** the baseline row. Color: Active Highlight Orange `(255, 140, 0)`.

## 4\. The Triple Pointer Lifecycle (Resolves Trap F)

The View must manage the visibility and positioning of the three pointers according to this strict state machine:

| Event / State | `i` Pointer | `j` Pointer | `min` Pointer |
| :--- | :--- | :--- | :--- |
| **Start of Pass** | Visible above index `i`. | Visible below index `i+1`. | Visible below index `i` (initial minimum). |
| **Scan (New Min Not Found)** | Visible above `i`. | Moves to new index `j`. | Remains at current `min_idx`. |
| **Scan (New Min Found)** | Visible above `i`. | **Coalesces:** Hides instantly because it shares a slot with `min`. | Jumps to the new `min_idx`. |
| **T2 Swap Animation** | **Hides instantly** to prevent visual collision with the arcing sprite. | Hides (pass is over). | Remains visible below the arcing `min_idx` sprite. |
| **End of Swap / Settle** | Reappears above the newly incremented `i` index. | Hides until next scan begins. | Hides until next pass begins. |

## 5\. The Scan Contract (T1 Tick)

When the model yields a `T1 Compare Tick` on `(min_idx, j)`, the View executes a strict 150ms visual highlight to indicate the scan.

* **Motion:** **None.** The sprites remain securely anchored at `home_y`. Selection Sort does *not* use a compare-lift.
* **Action:** The `j` pointer translates to the new index `j`. Both the sprite at `min_idx` and the sprite at `j` instantly transition to Active Highlight Orange `(255, 140, 0)`.
* **Resolution:** If the minimum updates, the `min` pointer jumps to the new slot. The previous minimum sprite instantly reverts to Default Blue.

## 6\. The Swap Contract (T2 Tick)

If the model determines `min_idx != i` at the end of a pass, it yields a `T2 Write/Mutation Tick` on `(i, min_idx)`.

* **Motion Model:** Standard Arc Swap.
* **Arc Height:** `arc_height = panel_height * 0.08`.

| Phase | Duration | Visual Action |
| :--- | :--- | :--- |
| **1. Preparation** | `0ms` | The `i` pointer hides. |
| **2. Arc Exchange** | `0 - 400ms` | Both sprites interpolate `x` to exchange slots. Simultaneously, a vertical offset is applied using a sine curve over the duration `t`.  • **Left Sprite (Index `i`):** Arcs **upward** (`exact_y = home_y - arc_offset`).  • **Right Sprite (Index `min_idx`):** Arcs **downward** (`exact_y = home_y + arc_offset`). |
| **3. Settle** | `400ms` | Sprites land at `home_y` in their new slots. The `i` pointer reappears at the new sorted boundary. |

*Note on Z-Ordering:* The Left Sprite (arcing upward) must always be drawn on top of the Right Sprite (arcing downward).

## 7\. Worked Example (`[4, 7, 2, 6, 1, 5, 3]`)

**Pass 1 (`i = 0`):**

1. **Start:** `i` pointer is above `4` (index 0). `min` pointer is below `4`.
2. **T1 Compare `(0, 1)`:** `j` pointer appears below `7`. Sprites `4` and `7` turn orange. `4` is still the minimum.
3. **T1 Compare `(0, 2)`:** `j` pointer moves below `2`. Sprites `4` and `2` turn orange.
4. **New Minimum:** `2 < 4`. The `min` pointer jumps to index 2. The `j` pointer hides (coalescing rule) because it is also at index 2. Sprite `4` returns to blue.
5. **...Scan Continues...** Minimum eventually updates to `1` at index 4.
6. **T2 Swap `(0, 4)`:** The pass ends. The `i` pointer hides. Sprite `4` (left) arcs upward. Sprite `1` (right) arcs downward. They land at `home_y`.
7. **Reset:** The `i` pointer reappears above index 1. The array is now `[1, 7, 2, 6, 4, 5, 3]`.
