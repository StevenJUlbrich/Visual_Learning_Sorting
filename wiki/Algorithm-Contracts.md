# Algorithm Contracts

Each algorithm has a tick-level contract that specifies exactly what operations it must emit, in what order, with what counter increments. These contracts are the mechanical gates that catch AI misalignment — if the counter targets don't match, the implementation is wrong regardless of whether it sorts correctly.

All examples use the reference array `[4, 7, 2, 6, 1, 5, 3]`.

## Counter Targets (Reference Array)

| Algorithm | Comparisons | Writes | Steps | T3 Ticks |
|-----------|------------|--------|-------|----------|
| Bubble Sort | 20 | 26 | — | 0 |
| Selection Sort | 21 | 10 | — | 0 |
| Insertion Sort | 17 | 19 | — | 0 |
| Heap Sort | 20 | 30 | 35 | 17 (6 boundary + 11 logical tree) |

## Bubble Sort

**File:** `src/visualizer/models/bubble.py`

**Control flow:** Classic two-loop with `swapped` early-exit flag. The inner limit shrinks by one per pass (`n - pass_idx - 1`), which is the boundary the LimitLine visualizes.

**Tick sequence per inner iteration:**

1. T1 COMPARE on `(j, j+1)` — always fires. Increments `comparisons`.
2. T2 SWAP on `(j, j+1)` — fires only if `arr[j] > arr[j+1]`. Increments `writes += 2`.

**Early exit:** If a complete pass produces no swaps (`swapped = False`), the outer loop breaks. For the reference array, Pass 5 (j=0..1) produces zero swaps and triggers early exit, saving Pass 6.

**Trace for reference array:**

- Pass 1 (j=0..5): 6 comparisons, 5 swaps → `[4, 2, 6, 1, 5, 3, 7]`
- Pass 2 (j=0..4): 5 comparisons, 4 swaps → `[2, 4, 1, 5, 3, 6, 7]`
- Pass 3 (j=0..3): 4 comparisons, 2 swaps → `[2, 1, 4, 3, 5, 6, 7]`
- Pass 4 (j=0..2): 3 comparisons, 2 swaps → `[1, 2, 3, 4, 5, 6, 7]`
- Pass 5 (j=0..1): 2 comparisons, 0 swaps → early exit
- **Total:** 20 comparisons, 13 swaps × 2 = 26 writes

**Visual choreography:** Compare-lift (both sprites rise 50px), horizontal swap while lifted, descent. LimitLine marks the shrinking boundary. BubbleHUD shows live counters.

## Selection Sort

**File:** `src/visualizer/models/selection.py`

**Control flow:** Outer loop selects sorted boundary `i`. Inner loop scans `i+1..n-1` tracking running minimum. Single conditional swap per pass.

**Tick sequence per inner iteration:**

1. T1 COMPARE on `(min_idx, j)` — `min_idx` always first (D-068). Increments `comparisons`. The `min_idx` update happens silently after the yield, so `highlight_indices` always shows the pre-update minimum.

**Tick at end of each outer pass:**

2. T2 SWAP on `(i, min_idx)` — fires only if `min_idx != i`. Increments `writes += 2`. Skipped entirely when the minimum is already in the correct position.

**Counter math:**

- Inner loop iterations: 6 + 5 + 4 + 3 + 2 + 1 = 21 comparisons
- Swap passes: 5 of 6 passes require swaps = 10 writes (pass where `min_idx == i` produces no T2 tick and no writes)

**Highlight rule:** The `highlight_indices` tuple is always `(min_idx, j)` with `min_idx` first. This isn't just convention — the pointer overlay uses the first index to position the `min` arrow and the second for `j`.

**Visual choreography:** Three labeled pointer arrows (i/j/min). Sorted prefix turns steel-blue. No-swap passes are detected by the `while` catch-up in `_dispatch_selection`.

## Insertion Sort

**File:** `src/visualizer/models/insertion.py`

**Control flow:** Four-phase pass structure — the most complex tick contract of the four algorithms.

**Phase 1 — Key Selection:**

1. T1 COMPARE on `(i,)` — single-index highlight. Does NOT increment `comparisons` (D-038). This is a visual tick that triggers the key-lift animation.

**Phase 2 — Compare-and-Shift Loop:**

Each iteration emits exactly two ticks (never batched — D-060, D-064):

2. T1 COMPARE on `(j, j+1)` — increments `comparisons`. The compare fires before the shift.
3. T2 SHIFT on `(j, j+1)` — `arr[j+1] = arr[j]`, increments `writes += 1`. One element moves one position right.

**Phase 2b — Terminating Compare (conditional):**

4. T1 COMPARE on `(j, j+1)` — fires ONLY if the while-loop exited by condition `arr[j] <= key` (meaning `j >= 0` at loop exit). Does NOT fire if `j` fell below 0. This is the control-flow rule that TC-A14 tests. Increments `comparisons`.

**Phase 3 — Placement:**

5. T2 SHIFT on `(j+1,)` — single-index highlight. `arr[j+1] = key`, increments `writes += 1`. Triggers the diagonal-drop animation.

**Counter breakdown for reference array:**

- 6 passes (i=1..6), each with a key-selection T1 (0 comparisons)
- 13 compare-during-shift iterations (13 comparisons, 13 shifts = 13 writes)
- 4 terminating compares (j >= 0 at loop exit for 4 of 6 passes)
- 6 placements (6 writes)
- **Total:** 13 + 4 = 17 comparisons, 13 + 6 = 19 writes

**Why the sequential shift guarantee matters (D-060, D-064):** AI agents consistently try to batch shifts for "efficiency." The one-at-a-time pacing is a pedagogical requirement — the learner needs to see each element slide rightward individually to understand how the sorted region absorbs the key. The animation time scales linearly with shift count, and this is intentional.

## Heap Sort

**File:** `src/visualizer/models/heap.py`

**Control flow:** Two phases driven by `sort_generator`. Private `_sift_down` generator method called via `yield from` from both phases.

**Phase 1 — Build Max-Heap:**

Sift down from `floor(n/2) - 1` to `0`. For 7 elements, this processes nodes 2, 1, 0.

**Phase 2 — Extraction:**

Swap root with current end, shrink `heap_size`, sift the new root down within the reduced heap. Repeat until `heap_size == 1`.

**Sift-down tick sequence (per level):**

1. T3 RANGE — Logical Tree Highlight on `(parent, left, right)` or `(parent, left)`. Parent always first (D-058). No counter increments.
2. T1 COMPARE — parent vs left child. Increments `comparisons`.
3. T1 COMPARE — parent vs right child (if right child exists). Increments `comparisons`.
4. T2 SWAP — conditional, fires only if `arr[largest] > arr[parent]`. Increments `writes += 2`.

If no swap occurs, sift-down terminates at this level. If a swap occurs, `parent = largest` and the loop continues to the next tree level.

**Extraction tick sequence (per extraction step):**

1. T3 RANGE — Boundary Emphasis on `tuple(range(heap_size))`. No counter increments.
2. T2 SWAP — root with `heap_size - 1`. Increments `writes += 2`.
3. Sift-down on new root (emits its own T3/T1/T2 sequence).

**Internal decision rule:** After comparing parent vs both children, an internal `if arr[right] > arr[left]: largest = right` fires as a pure decision. This is NOT yielded as a T1 tick and does NOT increment comparisons. If it were yielded, `comparisons` would jump from 20 to 22+, which would fail the counter target.

**Counter breakdown for reference array:**

- 20 T1 comparisons, 15 T2 swaps (15 × 2 = 30 writes)
- 35 steps (T1 + T2 only)
- 6 boundary T3 + 11 logical-tree T3 = 17 T3 ticks (excluded from step count)

**T3 variant classification (D-081):** Message prefix, not contiguity. `"Active heap"` → boundary sweep. `"Evaluating tree level"` → simultaneous flash. This is because at parent=0, the Logical Tree tuple `(0, 1, 2)` is indistinguishable from a 3-element Boundary tuple by shape alone.
