# INSERTION SORT ANIMATION CONTRACT

## 1. Dependencies & Cross-References
>
> **CRITICAL ARCHITECTURE NOTE:** This document defines choreography only. To prevent Agent Traps, it MUST be implemented in conjunction with:
>
> * `12_ANIMATION_FOUNDATION.md`: Governs sprite identity, global frame timing, `dt` clamping, and standard easing functions.
> * `04_UI_SPEC.md`: Governs layout math, font sizing, and panel container geometry.
> * `03_DATA_CONTRACTS.md`: Governs the exact `SortResult` payload shape yielded by the Model.

## 2. Overview

This contract defines the strict visual choreography for the Insertion Sort panel. Unlike Bubble or Selection Sort, Insertion Sort relies on a single suspended element (the Key) and a migrating empty slot. Its defining visual signature is the **"Key-Lift, Sequential Shift, Diagonal Drop"** sequence.

## 3. Dedicated UI Assets & Visual Tokens

Insertion Sort relies on distinct color states and a dynamic label rather than pointer arrows or boundary lines.

* **Sorted Boundary (Color-Based):** There is NO pointer or line asset for the sorted boundary. It is communicated entirely through the color transition from Sorted Green `(80, 220, 120)` on the left to Unsorted Blue `(100, 150, 255)` on the right.
* **Active Key Color:** Active Highlight Orange `(255, 140, 0)`.
* **The "KEY" Label:** When the key is lifted, a text label reading "KEY" (colored Orange) must render adjacent to or just above the lifted sprite. It disappears when the key returns to the baseline.
* **The Gap:** The baseline slot vacated by the lifted key renders as pure empty space (no ring, no outline). This gap migrates leftward as elements shift.

## 4. Phase 1: The Key Selection Contract (T1 Tick)

The first visual event of every outer loop pass is the key extraction.

* **Tick:** Model yields a `T1 Compare Tick` highlighting a single index `(i,)`.
* **Lift Offset:** `lift_offset = panel_height * 0.06`.
* **Motion:** The sprite at index `i` changes to Active Orange, the "KEY" label appears, and the sprite eases vertically from `home_y` to `home_y - lift_offset` over the 150ms duration.
* **Sustained State:** The key **remains elevated and stationary** in the compare lane across all subsequent compare and shift ticks until Phase 3.

## 5. Phase 2: The Compare-and-Shift Contract

While the key is suspended, the algorithm scans leftwards. **Strict Sequential Shift Guarantee:** Elements must shift one at a time. Block-shifting multiple elements in a single tick is a spec violation.

### The Compare (T1 Tick)

* **Tick:** Model yields a `T1 Compare Tick` on `(j, j+1)`.
* **Action:** The baseline sprite at `j` flashes Active Orange to indicate it is being compared against the hovering key. **No motion occurs.**

### The Shift (T2 Tick)

* **Tick:** Model yields a `T2 Write/Mutation Tick` on `(j, j+1)`.
* **Motion (Linear Slide):** The baseline sprite at index `j` interpolates its `x` coordinate to slide one slot to the right into `j+1`. It stays strictly at `home_y`.
* **Gap Migration:** Visually, the empty gap shifts one slot to the left as the sprite slides right.

## 6. Phase 2b: The Terminating Comparison (T1 Tick, conditional)

If the compare-and-shift loop exits because `arr[j] <= key` (not because `j < 0`), the Model emits one final `T1 Compare Tick` on `(j, j+1)` before placement. This tick shows the learner *why* the key stops here: the element at `j` is not greater than the key. It increments `self.comparisons` (see 05_ALGORITHMS_VIS_SPEC §4.3 Step 3, 07_ACCEPTANCE_TESTS AT-11 step 5).

If the loop exits because `j < 0` (key is the smallest element seen so far), no terminating comparison is emitted — there is no element to compare against.

## 7. Phase 3: The Placement Contract (T2 Tick)

Once the insertion point is found, the pass concludes by dropping the key into the migrating gap.

* **Tick:** Model yields a `T2 Write/Mutation Tick` highlighting a single index (the destination slot).
* **Motion (Diagonal Drop):** The key sprite eases **both axes simultaneously** over the 400ms duration.
  * `exact_x` interpolates horizontally to the destination slot.
  * `exact_y` interpolates vertically from `home_y - lift_offset` down to `home_y`.
* **Resolution:** The key lands perfectly in the empty gap at the baseline. The "KEY" label vanishes. Standard highlight rules apply: when the next tick begins, the placed sprite's orange highlight reverts to its default color (see 12_ANIMATION_FOUNDATION §4.1). The sorted/unsorted boundary is communicated through the green-to-blue color transition on ring sprites, not through a post-placement color event (see D-073, 05_ALGORITHMS_VIS_SPEC §4.3).

## 8. Z-Ordering Guarantee

The lifted Key sprite MUST be drawn on top of all other baseline sprites at all times during the pass. If the Key travels horizontally over a shifting baseline sprite, the Key must not be visually occluded.

## 9. Worked Example (`[4, 7, 2, 6, 1, 5, 3]`)

### Pass `i=2` (loop exits by `j < 0` — no terminating comparison)

*Array before: `[4, 7, 2, ...]` (4 and 7 are already sorted)*

1. **Phase 1 (Key Selection):** T1 on `(2,)`. Sprite `2` turns orange, gets the "KEY" label, and lifts `panel_height * 0.06` into the air. A gap appears at index 2.
2. **Phase 2 (Compare):** T1 on `(1, 2)`. Sprite `7` flashes orange.
3. **Phase 2 (Shift):** T2 on `(1, 2)`. Sprite `7` slides right into the gap at index 2. The gap is now at index 1.
4. **Phase 2 (Compare):** T1 on `(0, 1)`. Sprite `4` flashes orange.
5. **Phase 2 (Shift):** T2 on `(0, 1)`. Sprite `4` slides right into the gap at index 1. The gap is now at index 0.
6. Loop exits: `j < 0`. No terminating comparison.
7. **Phase 3 (Placement):** T2 on `(0,)`. The floating key `2` swoops diagonally down into the gap at index 0. Array is logically now `[2, 4, 7, ...]`.

### Pass `i=3` (loop exits by condition — terminating comparison fires)

*Array before: `[2, 4, 7, 6, ...]`*

1. **Phase 1 (Key Selection):** T1 on `(3,)`. Sprite `6` turns orange, gets the "KEY" label, and lifts. A gap appears at index 3.
2. **Phase 2 (Compare):** T1 on `(2, 3)`. Sprite `7` flashes orange. 7 > 6, so shift follows.
3. **Phase 2 (Shift):** T2 on `(2, 3)`. Sprite `7` slides right into the gap at index 3. The gap is now at index 2.
4. **Phase 2b (Terminating Comparison):** T1 on `(1, 2)`. Sprite `4` flashes orange. 4 is not > 6 — loop exits by condition. This tick shows the learner why the key stops here.
5. **Phase 3 (Placement):** T2 on `(2,)`. The floating key `6` swoops diagonally down into the gap at index 2. Array is logically now `[2, 4, 6, 7, ...]`.
