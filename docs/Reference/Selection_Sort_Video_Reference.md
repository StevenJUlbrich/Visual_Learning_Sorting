# Selection Sort Video Reference

## Pygame Developer Observation Write-Up

Purpose: capture what the video demonstrates so the animation behavior can later be translated into the application's visual system.

This document intentionally focuses on **behavior and motion**, not styling.

---

# 1. High-Level Behavior

The video demonstrates **Selection Sort as a scanning algorithm**.

The animation clearly emphasizes three conceptual elements:

1. **Current scan position**
2. **Current minimum candidate**
3. **Final placement swap**

The visual language is designed to make the viewer understand:

* the algorithm scans the remaining unsorted region
* the minimum element is tracked during the scan
* once the scan completes, the minimum swaps into the next sorted position

The animation is therefore **state driven**, not just swap driven.

---

# 2. Layout Observed

The animation uses a **single horizontal row of values**.

Each value appears as a circular node or visual token.

The layout has three visual zones:

### Baseline row

This is the primary array representation.

All values sit on a horizontal baseline except when temporarily animated.

### Active scan indicator

A moving pointer or visual highlight marks the current index being examined.

This pointer moves **left → right** during the scan phase.

### Sorted region

The left side of the row gradually becomes the sorted region.

Elements placed there appear visually stable and are not revisited by the algorithm.

---

# 3. Selection Sort Teaching Model in the Video

The animation visually breaks the algorithm into two phases per outer loop.

### Phase A: scanning for minimum

During the scan phase the animation shows:

* the scan cursor moving across the array
* the currently known minimum element
* comparisons between the scan element and the current minimum

This phase is visually distinct from swapping.

### Phase B: final swap

After scanning the entire unsorted region:

* the discovered minimum swaps with the element at the current sorted boundary
* the sorted boundary moves forward one position

This separation is important.

The swap does **not** happen during scanning.

It happens **once per outer loop**.

---

# 4. Visual States Observed

The video appears to represent several logical states visually.

## State: resting element

Default appearance when the element is neither being scanned nor selected as minimum.

### State: scan candidate

The element currently being inspected by the scan cursor.

This element is visually highlighted so the viewer can follow the scanning process.

### State: current minimum

The smallest element found so far during the scan.

This element remains visually marked while scanning continues.

### State: sorted element

Once an element has been swapped into the sorted region it becomes visually stable.

The algorithm does not revisit it.

---

# 5. Motion Choreography

The animation separates **scan motion** from **swap motion**.

---

# 5.1 Scan progression

The scan cursor moves one element to the right at a time.

For each step:

* the current scan element is highlighted
* the algorithm compares it against the current minimum

Visually the animation suggests:

* scan candidate is emphasized
* the current minimum remains marked
* the comparison moment is visually readable

This comparison phase may include a slight pause or emphasis so the viewer understands the decision.

---

# 5.2 Minimum update behavior

When the scan finds a new smaller value:

* the minimum marker moves from the old minimum element to the new one

This is visually important because it demonstrates the algorithm's logic.

The previous minimum returns to normal appearance.

---

# 5.3 End of scan

Once the scan reaches the end of the unsorted region:

* the minimum element is known
* the algorithm prepares to swap it into position

At this moment the scan cursor stops moving.

The viewer sees clearly:

* where the minimum is
* where it will be moved

---

# 5.4 Swap animation

The swap happens between:

* the first element in the unsorted region
* the discovered minimum

The animation likely shows:

* the two elements exchanging horizontal positions
* possibly via arc motion or direct slide

This swap is visually emphasized as the conclusion of the scan phase.

---

# 5.5 Sorted boundary advance

After the swap:

* the sorted region grows by one element
* the algorithm begins the next scan from the next index

The boundary shift is visible.

---

# 6. Motion Types Implied by the Video

From a Pygame perspective, the animation implies several reusable motion types.

### Highlight motion

Change visual appearance without changing position.

Used for:

* scan candidate
* current minimum

---

### Cursor movement

A separate visual marker moves horizontally along the array.

This marker represents the scan index.

---

### Minimum indicator movement

A visual marker shifts to the newly discovered minimum element.

This marker persists across scan steps.

---

### Swap motion

Two elements exchange positions horizontally.

This is the only large positional motion in the animation.

---

### Region boundary movement

A conceptual boundary separating sorted and unsorted regions moves one step right after each outer loop.

This may be represented visually with a line or shading.

---

# 7. Pygame Implementation Interpretation

A Pygame developer implementing this would likely think in terms of these objects.

---

## Value sprites

Each array value should be represented as a persistent sprite-like object.

Each sprite would track:

* logical index
* value
* baseline position
* current animated position
* highlight state
* minimum state
* sorted state

---

## Cursor indicator

A separate renderable element representing the current scan index.

Likely positioned relative to the baseline row.

---

## Minimum indicator

A persistent marker attached to the current minimum element.

This marker changes owner when a new minimum is found.

---

## Sorted boundary marker

A visual marker separating sorted and unsorted sections.

Moves one index right after each outer loop.

---

# 8. State Transitions Observed

The algorithm progresses through a repeating pattern.

### Start of outer loop

First unsorted element is the tentative minimum.

### Scan step

Cursor moves to next element.

### Compare step

Current element compared to current minimum.

### Minimum update (optional)

If smaller element found, update minimum marker.

### Scan continues

Cursor advances.

### End of scan

Minimum element identified.

### Swap

Minimum swaps with the first unsorted element.

### Boundary advance

Sorted region expands.

---

# 9. Teaching Goals of the Animation

The animation focuses on communicating three things clearly:

1. **Selection Sort scans the array to find the smallest value**
2. **The smallest value is tracked during scanning**
3. **Only one swap occurs per pass**

The animation therefore spends most of its time showing:

* scanning
* minimum updates

Not swapping.

---

# 10. What This Video Does NOT Define

Even though the animation is useful as reference, it does not specify several implementation details.

Examples include:

* exact vertical offset values
* exact motion durations
* easing curves
* exact highlight colors
* exact pointer geometry
* exact node shapes
* exact sprite layering rules

These details would need to be standardized later in the real documentation.

---

# 11. Key Technical Takeaway

From a Pygame implementation perspective, this animation shows that **Selection Sort should not reuse the Bubble Sort choreography**.

Bubble Sort animation emphasizes:

* adjacent comparisons
* repeated swaps

Selection Sort animation emphasizes:

* scanning
* tracking a minimum
* a single swap per pass

This means Selection Sort requires its **own motion grammar**.

---

# 12. Developer Summary

If I were summarizing this video for another Pygame engineer implementing the visualizer:

Selection Sort should be animated as a scanning process where a cursor traverses the unsorted portion of the array while tracking the smallest value encountered. The current scan element and current minimum are visually distinct. Once the scan completes, the minimum element swaps with the first unsorted element, expanding the sorted region. The animation emphasizes scanning and minimum discovery rather than frequent swaps.

---

If you want, the next step should be:

**turning this reference write-up into the exact changes needed in your existing docs**, without introducing new document types or unnecessary spec sprawl.
