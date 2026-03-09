# Selection Sort Video Reference

## Pygame Developer Observation Write-Up

Purpose: Capture what the video demonstrates so the animation behavior can later be translated into the application's visual system.

This document intentionally focuses on **behavior and motion**, not styling.

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

Each value appears as a circular node or visual token.

The layout has three visual zones:

### Baseline Row

This is the primary array representation.

All values sit on a horizontal baseline except when temporarily animated.

### Active Scan Indicator

A moving pointer or visual highlight marks the current index being examined.

This pointer moves **left → right** during the scan phase.

### Sorted Region

The left side of the row gradually becomes the sorted region.

Elements placed there appear visually stable and are not revisited by the algorithm.

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

The video appears to represent several logical states visually.

### State: Resting Element

Default appearance when the element is neither being scanned nor selected as minimum.

### State: Scan Candidate

The element currently being inspected by the scan cursor.

This element is visually highlighted so the viewer can follow the scanning process.

### State: Current Minimum

The smallest element found so far during the scan.

This element remains visually marked while scanning continues.

### State: Sorted Element

Once an element has been swapped into the sorted region it becomes visually stable.

The algorithm does not revisit it.

---

## 5. Motion Choreography

The animation separates **scan motion** from **swap motion**.

### 5.1 Scan Progression

The scan cursor moves one element to the right at a time.

For each step:

- The current scan element is highlighted.
- The algorithm compares it against the current minimum.

Visually the animation suggests:

- Scan candidate is emphasized.
- The current minimum remains marked.
- The comparison moment is visually readable.

This comparison phase may include a slight pause or emphasis so the viewer understands the decision.

### 5.2 Minimum Update Behavior

When the scan finds a new smaller value:

- The minimum marker moves from the old minimum element to the new one.

This is visually important because it demonstrates the algorithm's logic.

The previous minimum returns to normal appearance.

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

- The first element in the unsorted region.
- The discovered minimum.

The animation likely shows:

- The two elements exchanging horizontal positions.
- Possibly via arc motion or direct slide.

This swap is visually emphasized as the conclusion of the scan phase.

### 5.5 Sorted Boundary Advance

After the swap:

- The sorted region grows by one element.
- The algorithm begins the next scan from the next index.

The boundary shift is visible.

---

## 6. Motion Types Implied by the Video

From a Pygame perspective, the animation implies several reusable motion types.

### Highlight Motion

Change visual appearance without changing position.

Used for:

- Scan candidate.
- Current minimum.

---

### Cursor Movement

A separate visual marker moves horizontally along the array.

This marker represents the scan index.

---

### Minimum Indicator Movement

A visual marker shifts to the newly discovered minimum element.

This marker persists across scan steps.

---

### Swap Motion

Two elements exchange positions horizontally.

This is the only large positional motion in the animation.

---

### Region Boundary Movement

A conceptual boundary separating sorted and unsorted regions moves one step right after each outer loop.

This may be represented visually with a line or shading.

---

## 7. Pygame Implementation Interpretation

A Pygame developer implementing this would likely think in terms of these objects.

### Value Sprites

Each array value should be represented as a persistent sprite-like object.

Each sprite would track:

- `logical_index`
- `value`
- `baseline_position`
- `current_animated_position`
- `highlight_state`
- `minimum_state`
- `sorted_state`

### Cursor Indicator

A separate renderable element representing the current scan index.

Likely positioned relative to the baseline row.

### Minimum Indicator

A persistent marker attached to the current minimum element.

This marker changes owner when a new minimum is found.

### Sorted Boundary Marker

A visual marker separating sorted and unsorted sections.

Moves one index right after each outer loop.

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

Even though the animation is useful as reference, it does not specify several implementation details.

Examples include:

- Exact vertical offset values.
- Exact motion durations.
- Easing curves.
- Exact highlight colors.
- Exact pointer geometry.
- Exact node shapes.
- Exact sprite layering rules.

These details would need to be standardized later in the real documentation.

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

> Selection Sort should be animated as a scanning process where a cursor traverses the unsorted portion of the array while tracking the smallest value encountered. The current scan element and current minimum are visually distinct. Once the scan completes, the minimum element swaps with the first unsorted element, expanding the sorted region. The animation emphasizes scanning and minimum discovery rather than frequent swaps.
