# Selection Sort Video Reference

## Pygame Developer Observation Write-Up

Purpose: Capture what the video demonstrates so the animation behavior can later be translated into the application's visual system.

This document intentionally focuses on **behavior and motion**, not styling.

> **Adoption Note (2026-03-16):** The `i`/`j`/`min` pointer arrow system described in this reference has been adopted for the application (D-068). Selection Sort now uses all three labeled pointer assets alongside the universal orange active highlight color (D-067). The coalescing behavior (j merges into min at same index) is also adopted. Node shapes are circular outlined rings (D-069), not the squares shown in the reference video. See `04_UI_SPEC.md` and `05_ALGORITHMS_VIS_SPEC.md` for locked spec details.

---

## 1. High-Level Behavior

The video demonstrates **Selection Sort as a scanning algorithm**.

The animation clearly emphasizes three conceptual elements:

1. **Current scan position**
2. **Current minimum candidate**
3. **Final placement swap**

The visual language is designed to make the viewer understand:

- The algorithm scans the remaining unsorted region.
- The minimum element is tracked during the scan.
- Once the scan completes, the minimum swaps into the next sorted position.

The animation is therefore **state driven**, not just swap driven.

---

## 2. Layout Observed

The animation uses a **single horizontal row of values**.

Each value appears as a circular node with a green border on a gray fill.

The layout has three visual zones:

### Baseline Row

This is the primary array representation.

All values sit on a horizontal baseline except when temporarily animated during a swap.

### Confirmed Pointer Assets

The reference frames show **three labeled arrow assets** with fixed placement relative to the baseline row:

1. **`i` pointer (Sorted Boundary):** A **downward-pointing arrow** labeled `i`, positioned **above** the baseline row. It marks the current outer loop index — the next position in the sorted region to be filled. It advances one slot rightward after each completed swap.
2. **`j` pointer (Scan Cursor):** An **upward-pointing arrow** labeled `j`, positioned **below** the baseline row. It marks the current inner loop scan index and advances left-to-right during each scan phase.
3. **`min` pointer (Minimum Tracker):** An **upward-pointing arrow** labeled `min`, positioned **below** the baseline row. It marks the index of the smallest element found so far during the current scan. It **jumps** to a new index whenever a smaller element is discovered.

**Coalescing behavior:** When the scan cursor `j` discovers a new minimum, the `min` label transfers to `j`'s current index. When `j` and `min` occupy the same index, only the `min` label is shown — the `j` label visually merges into `min` rather than overlapping (see frames `009_5.00.png` and `010_5.38.png`). When `j` advances past that index, the two labels separate again.

### Sorted Region

The left side of the row progressively becomes the sorted region.

After each swap, the element placed at index `i` transitions to a **bright green fill**, visually distinct from the gray unsorted nodes. This green color persists for all subsequent frames, creating a left-to-right growing green region that tracks algorithm progress (see frames `019_10.50.png` onward).

Elements in the sorted region are not revisited by the scan cursor.

---

## 3. Selection Sort Teaching Model in the Video

The animation visually breaks the algorithm into two phases per outer loop.

### Phase A: Scanning for Minimum

During the scan phase the animation shows:

- The scan cursor moving across the array.
- The currently known minimum element.
- Comparisons between the scan element and the current minimum.

This phase is visually distinct from swapping.

### Phase B: Final Swap

After scanning the entire unsorted region:

- The discovered minimum swaps with the element at the current sorted boundary.
- The sorted boundary moves forward one position.

This separation is important.

The swap does **not** happen during scanning.

It happens **once per outer loop**.

---

## 4. Visual States Observed

The reference frames confirm the following distinct visual states.

### State: Resting Element

Gray fill with green border. Default appearance when the element is neither being scanned nor selected as minimum.

### State: Scan Candidate

Indicated by the `j` arrow positioned below the element. The element itself retains the same gray fill — the distinction from resting elements is provided **entirely by the labeled arrow**, not by a node color change.

### State: Current Minimum

Indicated by the `min` arrow positioned below the element. Like the scan candidate, the node retains gray fill — the `min` label is the sole visual marker.

When `j` and `min` point to the same index (immediately after a new minimum is discovered), only the `min` label is shown.

### State: Sorted Element

Once an element has been swapped into the sorted region, it transitions to a **bright green fill** that persists for the remainder of the animation.

This progressive green region grows from left to right, providing a clear visual history of algorithm progress. The algorithm does not revisit sorted elements — the `j` scan cursor never enters the green region.

---

## 5. Motion Choreography

The animation separates **scan motion** from **swap motion**.

### 5.1 Scan Progression

The `j` arrow moves one element to the right at a time below the baseline row.

For each step:

- The `j` arrow advances to the next unsorted index.
- The `min` arrow remains at the current minimum's index.
- Both arrows are simultaneously visible, giving the viewer two reference points.

The comparison moment is readable because the viewer can see the spatial relationship between `j` (the element being tested) and `min` (the current best candidate).

### 5.2 Minimum Update Behavior

When the scan finds a new smaller value:

- The `min` arrow jumps from the old minimum's index to `j`'s current index.
- At that moment, `j` and `min` occupy the same position — the `j` label merges into `min` (only `min` is shown).
- When `j` advances to the next index, the two arrows separate again — `min` stays at the discovered minimum while `j` continues rightward.

This jump-and-coalesce pattern is visually important because it demonstrates the algorithm's decision logic: the viewer sees `min` relocate to a new position, immediately understanding that a better candidate was found.

### 5.3 End of Scan

Once the scan reaches the end of the unsorted region:

- The minimum element is known.
- The algorithm prepares to swap it into position.

At this moment the scan cursor stops moving.

The viewer sees clearly:

- Where the minimum is.
- Where it will be moved.

### 5.4 Swap Animation

The swap happens between:

- The element at index `i` (the first unsorted position).
- The element at `min_idx` (the discovered minimum).

The reference frames confirm **arc motion**, not a direct slide:

- The **left element** (at index `i`) arcs **upward** above the baseline (see frame `017_9.75.png`: value `3` rises above the row).
- The **right element** (at `min_idx`) arcs **downward** below the baseline (see frame `017_9.75.png`: value `1` drops below the row).
- The two elements cross paths at the midpoint and land in each other's former positions.

This upward/downward crossing arc is the same motion pattern used in the application's standard swap animation, preventing visual collision at the midpoint.

**Pointer behavior during swap:** The `i` pointer above the row is not visible during the swap motion (see frame `017_9.75.png`). It reappears after the swap lands and the elements settle at the baseline. The `min` pointer remains visible below the swapping element during the arc.

This swap is visually emphasized as the conclusion of the scan phase.

### 5.5 Sorted Boundary Advance

After the swap:

- The newly placed element at index `i` transitions to **bright green fill**, joining the sorted region.
- The `i` pointer advances one position to the right, marking the next unsorted boundary.
- The `min` pointer resets to the new `i` position for the next scan.
- The `j` pointer resets to `i + 1` and begins the next left-to-right scan.

The growing green region on the left side of the array provides a clear, progressive visual record of the sort's progress.

---

## 6. Confirmed Motion Types

From a Pygame perspective, the reference frames confirm the following discrete motion types.

### Pointer Translation

The `j` and `min` arrows translate horizontally below the baseline row. The `i` arrow translates horizontally above the baseline row. These are the primary visual signals during the scan phase — no node color changes occur during scanning.

---

### Pointer Coalescing

When `j` discovers a new minimum and both pointers occupy the same index, the `j` label is suppressed and only `min` is displayed. When `j` advances, both labels reappear separately.

---

### Arc Swap Motion

Two elements exchange positions via **crossing arcs** (confirmed in frames `017_9.75.png`, `035_20.38.png`):

- Left element (index `i`) arcs **upward**.
- Right element (`min_idx`) arcs **downward**.

This is the only large positional motion in the animation.

---

### Sorted Color Transition

After each swap lands, the element at index `i` transitions from gray fill to **bright green fill**. This is a one-way, permanent color change that creates the progressive sorted-region visual.

---

### Boundary Advance

The `i` pointer advances one index rightward after each swap, visually separating the green sorted region from the gray unsorted region. No separate boundary line or shading is used — the `i` pointer and the green color transition together communicate the boundary.

---

## 7. Pygame Implementation Interpretation

A Pygame developer implementing this would need the following objects.

### Value Sprites

Each array value is represented as a persistent sprite-like object.

Each sprite tracks:

- `logical_index`
- `value`
- `baseline_position`
- `current_animated_position`
- `is_sorted` (controls gray vs. green fill)

### `i` Pointer Asset

A downward-pointing arrow labeled `i`, rendered **above** the baseline row.

Anchored horizontally to the center of the active slot at outer loop index `i`. Advances one slot rightward after each completed swap. Hidden during swap arc motion.

### `j` Pointer Asset

An upward-pointing arrow labeled `j`, rendered **below** the baseline row.

Anchored horizontally to the center of the current scan index. Advances left-to-right during each scan phase. Suppressed (visually merged) when occupying the same index as `min`.

### `min` Pointer Asset

An upward-pointing arrow labeled `min`, rendered **below** the baseline row.

Anchored horizontally to the center of the current minimum candidate's index. Jumps to a new position when a smaller element is discovered. When `j` and `min` share an index, only `min` is displayed.

### Sorted Region (Color-Based)

The sorted boundary is communicated through the **progressive green fill** on sorted elements, combined with the `i` pointer position. No separate boundary line or shading is required.

---

## 8. State Transitions Observed

The algorithm progresses through a repeating pattern.

### Start of Outer Loop

First unsorted element is the tentative minimum.

### Scan Step

Cursor moves to next element.

### Compare Step

Current element compared to current minimum.

### Minimum Update (Optional)

If smaller element found, update minimum marker.

### Scan Continues

Cursor advances.

### End of Scan

Minimum element identified.

### Swap

Minimum swaps with the first unsorted element.

### Boundary Advance

Sorted region expands.

---

## 9. Teaching Goals of the Animation

The animation focuses on communicating three things clearly:

1. **Selection Sort scans the array to find the smallest value**
2. **The smallest value is tracked during scanning**
3. **Only one swap occurs per pass**

The animation therefore spends most of its time showing:

- Scanning.
- Minimum updates.

Not swapping.

---

## 10. What This Video Does Not Define

Even though the reference frames confirm key behaviors, the following implementation details remain unspecified by the video alone:

- Exact vertical arc offset values (pixel heights for upward/downward arcs).
- Exact motion durations and easing curves.
- Exact colors (the green sorted fill and gray unsorted fill are approximate; production colors are defined in the application's UI spec).
- Exact pointer geometry (arrow shape, size, label font).
- Exact sprite layering rules during arc motion.
- Whether the `i` pointer hiding during swaps is mandatory or incidental to the reference video's rendering.

These details are standardized in the application's spec documents (`04_UI_SPEC.md`, `10_ANIMATION_SPEC.md`).

---

## 11. Key Technical Takeaway

From a Pygame implementation perspective, this animation shows that **Selection Sort should not reuse the Bubble Sort choreography**.

Bubble Sort animation emphasizes:

- Adjacent comparisons.
- Repeated swaps.

Selection Sort animation emphasizes:

- Scanning.
- Tracking a minimum.
- A single swap per pass.

This means Selection Sort requires its **own motion grammar**.

---

## 12. Developer Summary

> Selection Sort is animated as a scanning process driven by three labeled pointer assets: `i` (above the row, marking the sorted boundary), `j` (below the row, scan cursor), and `min` (below the row, running minimum tracker). The `j` pointer advances left-to-right during each scan; when it discovers a new minimum, `min` jumps to that index and the two labels coalesce. Once the scan completes, the minimum swaps with the element at `i` via a crossing arc (left element arcs up, right arcs down). After the swap lands, the element at `i` transitions to a bright green fill, permanently marking it as sorted. The sorted green region grows left-to-right across passes. The animation emphasizes scanning and minimum discovery — node color changes occur only for the sorted transition, while scan-phase distinctions rely entirely on the labeled arrow assets.
