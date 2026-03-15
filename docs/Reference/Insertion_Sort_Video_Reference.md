# Insertion Sort Video Reference

## Pygame Developer Observation Write-Up

Purpose: Document the animation behavior from the reference video so motion patterns can later be translated into the visualizer's animation system.

The focus is **how the algorithm is visually communicated**, not styling.

---

## 1. High-Level Behavior

The animation presents **Insertion Sort as a build-up process**, where a sorted region grows from **left to right**.

At any moment, the animation communicates three conceptual elements:

1. **Sorted region** (left side)
2. **Key element being inserted**
3. **Shifting elements to make space**

The key teaching idea is:

> The algorithm takes one element from the unsorted region and inserts it into the correct position in the sorted region.

Unlike Bubble Sort or Selection Sort, this animation centers around **one moving element (the key)** and **multiple shifting elements**.

---

## 2. Layout Observed

The animation uses a **single horizontal row of values** on a black background, with the title "Insertion Sort" displayed at the top center.

Each value is represented as a **circular node** with a solid color fill. The input array shown is `[3, 7, 2, 6, 4, 5, 1]`.

The row is divided into two visually distinct zones by **color**:

### Sorted Region (Green)

Left portion of the array that is already ordered.

These elements display a **light green fill** and remain visually stable during most of the animation. The green region grows left-to-right as each key is successfully inserted.

### Unsorted Region (Blue)

Right portion of the array containing elements not yet processed.

These elements display a **blue fill**, visually distinct from the green sorted region. The next element from this region becomes the **key** for insertion.

### Color-Based Boundary

Unlike Bubble Sort (which uses a `LimitLine` marker) or Selection Sort (which uses an `i` pointer), Insertion Sort communicates the sorted/unsorted boundary **entirely through the green-to-blue color transition**. No separate pointer or line asset marks the boundary.

---

## 3. Core Teaching Model

The animation emphasizes a repeating sequence:

1. Select the next element from the unsorted region.
2. Lift that element as the **key**.
3. Scan left through the sorted region.
4. Shift larger elements right.
5. Insert the key into its correct location.
6. Expand the sorted region.

The viewer is meant to follow the movement of the key and the shifts that create space for it.

---

## 4. Visual States Observed (Confirmed from Reference Frames)

The reference frames confirm four distinct visual states, each communicated through **node fill color**:

### State: Sorted Element (Green Fill)

Elements in the sorted region that are confirmed to be in correct order. Light green fill. These remain visually stable unless they need to shift right to make room for a key.

### State: Unsorted Element (Blue Fill)

Elements in the unsorted region that have not yet been processed. Blue fill. The leftmost blue element becomes the next key.

### State: Active Key (Orange/Tan Fill)

The element currently being inserted. **Orange/tan fill**, visually distinct from both green and blue (see frames `004_2.00.png`, `010_4.25.png`, `025_9.88.png`).

The key is **physically lifted above the baseline row** into a compare lane, leaving a visible gap in the array. The orange color persists while the key is elevated and briefly after placement — the key transitions to green on the next pass.

### State: Recently Placed Key (Orange at Baseline)

After the key drops into its sorted position, it briefly retains its orange fill at the baseline (see frames `009_3.88.png`, `020_8.00.png`). It transitions to green when the next outer loop pass begins and the sorted region visually expands to include it.

---

## 5. Motion Choreography

The animation separates **key motion** from **array motion**.

This distinction is central to understanding insertion sort visually.

### 5.1 Key Selection and Lift

At the start of each outer iteration:

- The next element from the unsorted region (leftmost blue element) becomes the **key**.
- The key's fill color changes from **blue to orange/tan** immediately.
- The key **lifts vertically above the baseline row** into a compare lane, leaving a **visible empty gap** at its original position in the baseline (see frame `004_2.00.png`: key `2` is elevated above the row with a gap below it).

The lift height is significant — the key hovers well above the baseline, creating clear spatial separation. The empty gap at the baseline is a critical visual cue: it shows the viewer exactly where the key was extracted from and where space needs to be created for its insertion.

### 5.2 Scan Through Sorted Region

The animation compares the key against sorted elements moving **right to left**.

The key remains **elevated and stationary** during comparisons. The comparison is implied by the key's horizontal position relative to the element being examined — there is no separate scan cursor or pointer asset.

The key remains elevated throughout the entire scan-and-shift sequence until insertion.

### 5.3 Shift Behavior

When a sorted element is larger than the key:

- That element shifts **one position to the right**, filling the gap.
- A **new gap opens at the element's previous position**.
- The gap effectively **migrates leftward** through the sorted region as each larger element shifts right.

The shift is a **horizontal slide of a single element to the adjacent slot** (see frames `006_2.75.png` through `008_3.50.png`: elements `7` and `3` shift right sequentially as key `2` hovers above).

**Critical observation — sequential, not simultaneous:** Shifts happen **one element at a time**. Each element completes its rightward slide before the next element begins shifting. This one-at-a-time cadence is a core pedagogical requirement — the learner can trace the "ripple" of shifts moving leftward.

**Key tracks the gap:** While the key remains elevated, it **translates horizontally** to stay above the migrating gap (see frame `008_3.50.png`: key `2` has moved leftward to hover above the new gap position). This tracking motion reinforces the visual connection between the key and its eventual insertion point.

### 5.4 End of Scan Condition

The scan stops when either:

- The correct insertion position is found.
- The beginning of the sorted region is reached.

At this point, there is a gap in the sorted region where the key belongs.

### 5.5 Key Insertion (Diagonal Drop)

Once the insertion point is identified, the key executes a **diagonal drop** — it moves simultaneously downward (from the compare lane to the baseline) and horizontally (to the target slot) in a single smooth motion (see frame `005_2.38.png`: key `2` mid-drop, and frame `025_9.88.png`: key `5` settling into position).

The key lands in the gap at the baseline. Upon landing, the key **retains its orange fill** briefly (see frame `009_3.88.png`: key `2` rests at baseline in orange, frame `029_11.38.png`: key `1` at baseline still orange). The orange-to-green transition occurs at the start of the next outer loop pass.

### 5.6 Sorted Boundary Expansion

After the key is inserted:

- The sorted boundary expands one element to the right.
- The recently placed key transitions from **orange to green**, joining the sorted region visually.
- The next unsorted (blue) element becomes the new key.

The boundary is communicated entirely through the **green-to-blue color transition** in the baseline row — no separate boundary marker is used.

---

## 6. Confirmed Motion Types

From a Pygame animation perspective, the reference frames confirm the following discrete motion types.

### Vertical Lift Motion

The key element lifts **upward** from the baseline row into a compare lane. The lift creates a visible gap at the baseline. The key changes from blue to **orange/tan** fill on lift.

### Horizontal Key Tracking

While elevated, the key **translates horizontally** to track the migrating gap below it. This is not a separate motion event — it accompanies shifts as the gap moves leftward.

### Sequential Horizontal Shift

Elements larger than the key slide **one slot to the right**, one at a time. Each shift fills the gap at one position and opens a new gap at the adjacent position. Shifts are strictly sequential — never simultaneous.

### Diagonal Drop (Insertion)

The key drops from the compare lane into the gap, moving **simultaneously downward and horizontally** in a single diagonal trajectory. This is the only combined-axis motion in the Insertion Sort choreography.

### Color-Based Boundary Advance

The sorted/unsorted boundary is communicated through the **green-to-blue color transition**. After each insertion, the recently placed key transitions from orange to green, expanding the green region by one element. No pointer, line, or shading asset is used.

---

## 7. Pygame Implementation Interpretation

A Pygame engineer implementing this animation needs the following objects.

### Value Sprites

Each value is represented by a persistent sprite-like object.

Each sprite maintains:

- `value`
- `logical_index`
- `exact_x`, `exact_y` (current animated position)
- `home_x`, `home_y` (baseline slot position)
- `is_key` (currently elevated in the compare lane)
- `is_sorted` (controls green vs. blue fill)

### Key Color State

The key element uses a **third fill color** (orange/tan) distinct from both the sorted green and unsorted blue. This color is applied immediately when the key is selected and persists until the start of the next outer loop pass, when it transitions to green.

### Gap Rendering

When the key lifts, the baseline slot it vacated should render as an **empty gap** (no sprite). As elements shift right, the gap migrates leftward. The gap is not a rendered object — it is the absence of a sprite at a baseline slot.

### Sorted Region (Color-Based, No Marker)

The sorted boundary is communicated entirely through color:
- **Green fill** = sorted region
- **Blue fill** = unsorted region
- **Orange fill** = active key

No separate boundary marker, pointer, or shading asset is required for Insertion Sort.

---

## 8. State Transitions Observed

The animation follows a consistent state cycle:

### Start Iteration

Next unsorted element becomes the key.

### Lift Key

Key moves upward from the array.

### Scan Left

Algorithm compares key against sorted elements moving leftward.

### Shift Elements

Elements larger than the key slide right.

### Find Insertion Point

The scan stops when the correct slot is identified.

### Insert Key

Key drops into the open slot.

### Expand Sorted Region

Sorted boundary advances.

---

## 9. Teaching Goals of the Animation

The animation focuses on clearly conveying these algorithm concepts:

1. Insertion sort maintains a growing sorted region.
2. Each new element is temporarily removed and inserted into place.
3. Larger elements shift right to make space.
4. Only one element (the key) is actively inserted at a time.

The animation therefore spends most of its time showing:

- The movement of the key.
- The shifting of elements.

Rather than complex swaps.

---

## 10. What the Video Does Not Define

Although the reference frames confirm key behaviors, the following implementation details remain unspecified by the video alone:

- Exact vertical offset of the key lift (pixel height above baseline).
- Exact animation durations for lift, shift, and drop motions.
- Easing curves for each motion phase.
- Exact RGB color values (the green, blue, and orange fills are approximate; production colors are defined in the application's UI spec).
- Exact node geometry (corner radius, border width).
- Sprite layering rules during the lift and drop.
- Whether the key's horizontal tracking during shifts is continuous or discrete per shift.

These details are standardized in the application's spec documents (`04_UI_SPEC.md`, `10_ANIMATION_SPEC.md`).

---

## 11. Key Technical Insight

Insertion sort animation requires a **different motion grammar** than Bubble Sort or Selection Sort.

Bubble Sort emphasizes **adjacent swaps**.

Selection Sort emphasizes **scan and single swap per pass**.

Insertion Sort emphasizes **lifting a key and shifting elements**.

The visual choreography therefore centers around **a single lifted element and sequential horizontal shifts**.

---

## 12. Developer Summary

> The insertion sort animation uses three color states — green (sorted), blue (unsorted), and orange (active key) — to communicate algorithm progress without any pointer or boundary marker assets. The key is extracted from the unsorted region, changes to orange, and lifts vertically into a compare lane above the baseline, leaving a visible gap. Elements larger than the key shift right one at a time (sequentially, never simultaneously), migrating the gap leftward while the elevated key tracks horizontally above it. Once the insertion point is found, the key executes a diagonal drop — moving simultaneously downward and horizontally into the gap. The key retains its orange fill at the baseline briefly, then transitions to green at the start of the next pass, expanding the sorted region by one element. The animation emphasizes the key's sustained elevation, the sequential shift ripple, and the diagonal settle as its distinctive motion grammar.
