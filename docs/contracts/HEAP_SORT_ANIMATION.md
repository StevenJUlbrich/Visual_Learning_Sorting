# Brick 10: Heap Sort Animation Contract

## 1. Dependencies & Cross-References
>
> **CRITICAL ARCHITECTURE NOTE:** This document defines choreography only. To prevent Agent Traps, it MUST be implemented in conjunction with:
>
> * `12_ANIMATION_FOUNDATION.md`: Governs sprite identity, global frame timing, `dt` clamping, and standard easing functions.
> * `04_UI_SPEC.md`: Governs layout math, font sizing, and panel container geometry.
> * `03_DATA_CONTRACTS.md`: Governs the exact `SortResult` payload shape yielded by the Model.

## 2. Overview & Layout Override (Crucial)

This contract defines the strict visual choreography for the Heap Sort panel.
**Layout Override:** Unlike all other algorithms, Heap Sort does **not** use a single flat baseline row. The View must divide the panel into two distinct vertical zones:

1. **The Tree Zone (Top):** Active elements (`index < heap_size`) are positioned dynamically to form a visual binary tree.
2. **The Sorted Row (Bottom):** Extracted elements (`index >= heap_size`) are positioned in a flat, compact horizontal row at the bottom of the panel, growing right-to-left.

## 3. Dedicated UI Assets & Visual Tokens

* **Parent-Child Edges:** Straight lines drawn in `(120, 120, 130)` connecting the center of a parent node to its children. These lines must only be drawn for indices `< heap_size`. During a T3 Logical Tree Highlight tick, edges between the highlighted parent and its highlighted children render in active Orange `(255, 140, 0)` (see 04_UI_SPEC §4.5).
* **Phase Label:** A text element positioned centrally. It reads `"BUILD MAX-HEAP"` (Orange) during Phase 1, and `"EXTRACTION"` (Orange) during Phase 2.
* **Active Highlight Color:** Universal Orange `(255, 140, 0)` for all T1/T3 highlights.
* **Extracted State Color:** Elements in the Sorted Row transition to a Steel-Blue color `(130, 150, 190)`.
* **Sorted-Row Placeholder Outlines:** Active heap slots (indices `< heap_size`) render in the Sorted Row as dim placeholder outlines `(60, 60, 68)` with no number, indicating the element is currently in the tree above (see 04_UI_SPEC §4.5).
* **Heap Boundary Marker:** A vertical dashed line (6px dash, 4px gap) in `(150, 150, 160)` drawn between the last active heap slot and the first sorted slot in the Sorted Row. It shifts one position leftward after each extraction (see 04_UI_SPEC §4.5, 07_ACCEPTANCE_TESTS AT-23).

## 4. Phase 1: Build Max-Heap (The Sift-Down Grammar)

Each sift-down level follows the grammar defined in 05_ALGORITHMS_VIS_SPEC §4.4 and 08_TEST_PLAN §8.3:

```text
T3 (Logical Tree Highlight)  →  T1 (Compare) [1 or 2]  →  T2 (Swap) [0 or 1]
```

One T1 fires for the left child; a second T1 fires only if a right child exists within the heap boundary. The T2 swap fires only if the largest child is greater than the parent; otherwise the sift-down terminates at this level with no swap.

### 1. The Logical Tree Highlight (T3 Tick - 200ms)

* **Trigger:** Emitted before any comparison at a specific sift-down level.
* **Payload:** `highlight_indices` is a tuple of `(parent, left_child, right_child)` when both children exist, or `(parent, left_child)` when only the left child is within the heap boundary. The parent index is always the first element (contract invariant from 03_DATA_CONTRACTS §3.2 Variant B).
* **Visual Action (Simultaneous Snap):** All nodes in the provided tuple flash Orange instantly. No sweep, no stagger, and no positional movement. This explicitly highlights the tree triangle (or pair) being evaluated.

### 2. The Compare (T1 Tick(s) - 150ms each)

* **Visual Action:** The specific indices being compared flash Orange. No positional movement.
* One or two T1 ticks fire per sift-down level, depending on how many children exist.

### 3. The Intra-Tree Swap (T2 Tick - 400ms, conditional)

* **Motion Model (Standard Arc):** The parent and child exchange positions using a standard arc swap.
* **Arc Height:** `arc_height = panel_height * 0.08`.
* **Pathing:** Because nodes are positioned in a tree, the arc interpolates between their specific 2D tree coordinates, visually crossing along the edge path. The node moving upward draws on top.

## 5. Phase 2: Extraction (The Phase-Transition Grammar)

Phase 2 visually moves elements from the Tree Zone to the Sorted Row.

### 1. The Heap Boundary Sweep (T3 Tick - 200ms)

* **Trigger:** Start of each extraction step. Payload highlights the entire active heap `range(0, heap_size)`.
* **Visual Action (Staggered Sweep):** The nodes flash Orange in a left-to-right sweep across a `120ms` window, holding for the final `80ms`. This visually confirms the current bounds of the tree.

### 2. The Extraction Swap (T2 Tick - 400ms)

* **Trigger:** Swapping index `0` (the Root) with `end` (the last active heap index).
* **Motion Model (Elevated Arc):** The Root node arcs dramatically out of the Tree Zone and down into the Sorted Row.
* **Arc Height:** **CRITICAL:** Must use `extraction_arc_height = panel_height * 0.14` (1.75x standard height) to distinguish this structural phase-transition from a normal repair.
* **Resolution:** The element landing in the Sorted Row turns Steel-Blue. The parent-child edge to that slot disappears.

### 3. Rapid Sift-Down Cadence

After an Extraction Swap, the ensuing sift-down repairs use a **reduced timeline** to simulate a rapid ripple effect:

* **T3 Tree Highlight:** Reduces from 200ms to **130ms**.
* **T1 Compare:** Reduces from 150ms to **100ms**.
* **T2 Swap:** Reduces from 400ms to **250ms**.

## 6. Z-Ordering Guarantee

* Any node arcing upward (towards the Root) is drawn on top of the node arcing downward.
* The lifted Extraction Arc (Root moving to Sorted Row) must draw on top of all other Tree nodes and edges.

## 7. Worked Example Summary (`[4, 7, 2, 6, 1, 5, 3]`)

* **Build Phase:** Array is drawn as a tree. The system highlights `(index 2, index 5, index 6)` which are `(2, 5, 3)`. They flash orange. It compares 5 and 3, then compares 2 and 5. It performs a Standard Arc Swap between 2 and 5.
* **Extraction Phase:** Once built, the Root (`7`) swaps with the end (`3`). The `7` node launches off the top of the tree using the elevated `0.14` arc height and lands in the bottom Sorted Row, turning Steel-Blue. Rapid sift-down commences to fix the tree.
