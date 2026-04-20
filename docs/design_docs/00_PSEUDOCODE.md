# 00 PSEUDOCODE — Algorithm Generator Reference

**Status:** Locked (closes Phase 0.1).
**Scope:** Exact generator shape for each of the four algorithms. Any implementation that diverges from this pseudocode will produce a tick sequence that fails TC-A9, TC-A14, TC-A19, and/or the counter accuracy table in `CLAUDE.md`.

This document is the **single source of truth for control flow**. The animation contracts (`docs/contracts/*.md`) define what each tick *looks like* on screen; this document defines *when* each tick is emitted relative to loop structure. Implementations must match both.

---

## Conventions

- `arr` — the working list, mutated in place. Never yielded by reference; every tick with `array_state` yields `list(arr)` (D-011).
- `yield T1(indices, msg)` — yield a `SortResult(success=True, operation_type=OpType.COMPARE, array_state=list(arr), highlight_indices=indices, message=msg)`.
- `yield T2(indices, msg)` — same shape with `operation_type=OpType.SWAP` or `OpType.SHIFT` as noted.
- `yield T3(indices, msg)` — `OpType.RANGE`. Does NOT increment step counter (D-041).
- `yield T4_done()` — final tick: `is_complete=True`, `highlight_indices=tuple(range(n))`, full-array highlight.
- `yield T0_fail(msg)` — `success=False`, `operation_type=OpType.FAILURE`. Used only for empty-input guard. No exceptions (D-020).
- Counters `self.comparisons` and `self.writes` are incremented **inside the generator** before the corresponding yield, except where noted (Insertion Sort key-selection T1 does NOT increment comparisons — it's a visual tick).

---

## 1. Bubble Sort

**Target counters for `[4, 7, 2, 6, 1, 5, 3]`:** comparisons = 20, writes = 26.

**Loop shape:** Classic two-loop with `swapped` early-exit flag. Inner loop shrinks by one slot per pass (`n - pass - 1`) — this is what the LimitLine visualizes.

```text
function bubble_sort_generator(arr):
    n = len(arr)
    if n == 0:
        yield T0_fail("Empty input")
        return
    if n == 1:
        yield T4_done()
        return

    for pass_idx in 0 .. n-2:                       # outer loop
        swapped = False
        inner_limit = n - pass_idx - 1              # LimitLine position

        for j in 0 .. inner_limit - 1:
            # T1: Compare (j, j+1) — always fires before the swap decision
            self.comparisons += 1
            yield T1((j, j+1), f"Compare {arr[j]} and {arr[j+1]}")

            if arr[j] > arr[j+1]:
                # Mutate
                arr[j], arr[j+1] = arr[j+1], arr[j]
                self.writes += 2                    # two slots written per swap

                # T2: Swap (j, j+1)
                yield T2_swap((j, j+1), f"Swap {arr[j+1]} and {arr[j]}")
                swapped = True

        if not swapped:                             # early exit — array is sorted
            break

    yield T4_done()
```

### Invariants verified by TC-A9-style trace

- For every T2, the immediately preceding tick is a T1 on the same `(j, j+1)`.
- No T3 ticks are emitted. Bubble Sort does not use RANGE ticks.
- `writes` is always `2 * swap_count` (each swap writes two slots). Given 13 swaps for `default_7`, `writes = 26`. ✓
- `comparisons` equals the sum of inner-loop iterations actually executed before the early-exit break. For `default_7` this is 20. ✓

---

## 2. Selection Sort

**Target counters for `[4, 7, 2, 6, 1, 5, 3]`:** comparisons = 21, writes = 10.

**Loop shape:** Outer loop selects position `i` (sorted boundary). Inner loop scans `i+1 .. n-1` finding `min_idx`. Single swap per pass, skipped when `min_idx == i`.

```text
function selection_sort_generator(arr):
    n = len(arr)
    if n == 0:
        yield T0_fail("Empty input")
        return
    if n == 1:
        yield T4_done()
        return

    for i in 0 .. n-2:                              # outer loop — selects sorted boundary
        min_idx = i                                 # running minimum initialized to i

        for j in i+1 .. n-1:                        # scan phase
            # T1: Compare (min_idx, j) — order matters for highlight rule D-065
            self.comparisons += 1
            yield T1((min_idx, j),
                     f"Scanning: current min is arr[{min_idx}]={arr[min_idx]}, checking arr[{j}]={arr[j]}")

            if arr[j] < arr[min_idx]:
                min_idx = j                         # update running minimum
                # NOTE: no separate tick for min update — the next T1 will show it

        # End of scan: swap if min_idx moved
        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            self.writes += 2
            yield T2_swap((i, min_idx), f"Swap arr[{i}] and arr[{min_idx}]")
        # If min_idx == i, no T2 is emitted (skipped swap per D-065 / TC-A8)

    yield T4_done()
```

### Invariants verified by trace tests

- Every T1 tuple is `(min_idx, j)` — `min_idx` is always first for the "persistent minimum highlight" rule (D-065).
- T2 is emitted only when `min_idx != i`. For `default_7`, exactly 5 passes produce a swap → `writes = 10`. ✓
- Total T1 count = `sum(n-1-i for i in 0..n-2)` = `6+5+4+3+2+1 = 21`. ✓

---

## 3. Insertion Sort

**Target counters for `[4, 7, 2, 6, 1, 5, 3]`:** comparisons = 17, writes = 19.

**Loop shape:** Outer loop selects key at index `i`. Inner while-loop shifts elements right one at a time (D-060, D-064 — never batch). The **terminating compare** fires only when the loop exits by condition (`arr[j] <= key`), not when it exits by `j < 0`. This is the decision that TC-A14 pins down.

```text
function insertion_sort_generator(arr):
    n = len(arr)
    if n == 0:
        yield T0_fail("Empty input")
        return
    if n == 1:
        yield T4_done()
        return

    for i in 1 .. n-1:                              # outer loop
        key = arr[i]

        # Phase 1: Key Selection T1 — single-index highlight (i,)
        # IMPORTANT: does NOT increment self.comparisons (D-071 visual tick)
        yield T1((i,), f"Selecting key arr[{i}]={key}")

        j = i - 1

        # Phase 2: Compare-and-shift loop — one element per iteration
        while j >= 0 and arr[j] > key:
            # T1 Compare (j, j+1) — increments comparisons
            self.comparisons += 1
            yield T1((j, j+1), f"Compare arr[{j}]={arr[j]} > key={key}")

            # T2 Shift (j, j+1) — one slot at a time, never batch
            arr[j+1] = arr[j]
            self.writes += 1
            yield T2_shift((j, j+1), f"Shift arr[{j}]={arr[j]} right to slot {j+1}")

            j -= 1

        # Phase 2b: Terminating Compare (conditional) — fires only if loop
        # exited by `arr[j] <= key`, NOT if it exited by `j < 0`.
        # TC-A14: passes i=1 (key=7) and i=3 (key=6) emit this; i=2, i=4 do not.
        if j >= 0:
            self.comparisons += 1
            yield T1((j, j+1), f"Compare arr[{j}]={arr[j]} <= key={key} — stop")

        # Phase 3: Placement T2 — single-index highlight (j+1,)
        arr[j+1] = key
        self.writes += 1
        yield T2_shift((j+1,), f"Place key={key} at slot {j+1}")

    yield T4_done()
```

### Invariants verified by TC-A9 and TC-A14

- Key-selection T1 is the first tick of every pass and has a single-index tuple `(i,)`.
- Each compare-shift pair is emitted individually; the `while` body always yields `compare → shift → decrement j` (never batched).
- Terminating T1 fires iff `j >= 0` at loop exit. For `default_7`:
  - `i=1` (key=7): while-loop never enters (`arr[0]=4 <= 7`) → 1 terminating compare.
  - `i=2` (key=2): shifts until `j<0` → 0 terminating compares.
  - `i=3` (key=6): shifts once, exits by `arr[1]=4 <= 6` → 1 terminating compare.
  - `i=4` (key=1): shifts until `j<0` → 0 terminating compares.
  - `i=5` (key=5): shifts twice, exits by `arr[2]=4 <= 5` → 1 terminating compare.
  - `i=6` (key=3): shifts three times, exits by `arr[2]=4 <= 3`? wait, 4 > 3 so continues; eventually exits by `arr[1]=2 <= 3` → 1 terminating compare.
- Writes = (total shifts) + (placements per pass) = 13 shifts + 6 placements = 19. ✓
- Comparisons = (shift compares) + (terminating compares) = 13 + 4 = 17. ✓

---

## 4. Heap Sort

**Target counters for `[4, 7, 2, 6, 1, 5, 3]`:** comparisons = 20, writes = 30, steps = 35 (6 boundary T3 ticks excluded from step count per D-041).

**Loop shape:** Two phases. Phase 1 builds a max-heap by sifting down from the last parent (`n//2 - 1`) to the root. Phase 2 extracts the root repeatedly, swapping with the current end, shrinking `heap_size`, and sifting the new root down.

**Sift-down grammar (TC-A19):** Every sift-down level must emit `T3 Logical Tree → T1 compares (1 or 2) → T2 swap (0 or 1)`. The T3 is emitted **before** any compare, highlighting the parent-child triangle.

```text
function sift_down(arr, start, end):
    # end is exclusive upper bound; sift arr[start] down within arr[start..end-1]
    parent = start
    while true:
        left  = 2*parent + 1
        right = 2*parent + 2

        # Gate: at least the left child must be in range
        if left >= end:
            return

        # --- T3 Logical Tree Highlight (NON-contiguous indices) ---
        # highlight_indices MUST include parent as the first element (D-058)
        if right < end:
            yield T3((parent, left, right), f"Evaluating tree level at parent {parent}")
        else:
            yield T3((parent, left), f"Evaluating tree level at parent {parent}")

        # --- T1 Compare(s) — left child, and right child if present ---
        largest = left
        self.comparisons += 1
        yield T1((parent, left), f"Compare parent={arr[parent]} with left={arr[left]}")

        if right < end:
            self.comparisons += 1
            yield T1((parent, right), f"Compare parent={arr[parent]} with right={arr[right]}")
            if arr[right] > arr[left]:
                largest = right

        # --- T2 Swap (conditional) ---
        if arr[largest] > arr[parent]:
            arr[parent], arr[largest] = arr[largest], arr[parent]
            self.writes += 2
            yield T2_swap((parent, largest), f"Swap arr[{parent}] and arr[{largest}]")
            parent = largest                       # descend; loop continues
        else:
            return                                 # heap property holds; stop


function heap_sort_generator(arr):
    n = len(arr)
    if n == 0:
        yield T0_fail("Empty input")
        return
    if n == 1:
        yield T4_done()
        return

    # --- Phase 1: Build Max-Heap ---
    # Process nodes floor(n/2)-1 down to 0 (top-down within each sift-down).
    for start in (n // 2 - 1) .. 0 step -1:
        yield from sift_down(arr, start, n)

    # --- Phase 2: Extraction ---
    heap_size = n
    while heap_size > 1:
        end = heap_size - 1

        # Boundary T3 — CONTIGUOUS range(0, heap_size). TC-A19 uses message prefix
        # ("Active heap" vs "Evaluating tree level") to distinguish from Logical Tree T3
        # (D-081). Does NOT increment steps.
        yield T3(tuple(range(0, heap_size)), f"Active heap: indices 0..{end}")

        # Extraction swap: root with end
        arr[0], arr[end] = arr[end], arr[0]
        self.writes += 2
        yield T2_swap((0, end), f"Extract root={arr[end]} to slot {end}")

        heap_size -= 1                             # shrink active heap
        yield from sift_down(arr, 0, heap_size)    # repair (uses reduced cadence timing, view-layer concern)

    yield T4_done()
```

### Invariants verified by TC-A19

- Every non-terminal sift-down level begins with exactly one T3 whose message starts with `"Evaluating tree level"` (the Logical Tree variant). TC-A19's `extract_sift_down_levels` uses this message-prefix check (D-081). **Note:** contiguity alone is insufficient — Logical Tree T3 at parent=0 produces contiguous tuples `(0, 1, 2)` or `(0, 1)` that collide with Boundary T3 shape.
- Boundary T3 ticks (Phase 2 pre-swap) have messages starting with `"Active heap"` — distinguishable from Logical Tree T3 by prefix, not by tuple contiguity.
- Each sift-down level emits 1 or 2 T1s (left always, right conditionally).
- T2 within a sift-down level is emitted at most once, and only when a child exceeds the parent.
- Phase 1 for `default_7` processes indices 2, 1, 0 → 3 sift-downs. Phase 2 executes 6 extractions. The 6 boundary T3s are the ones excluded from `step_count` (35 steps vs. 41 total ticks).
- Rapid-cadence timing (T3=130ms, T1=100ms, T2=250ms) is a **view-layer** concern applied to sift-downs that occur *after* an extraction swap. The model emits ticks identically in both phases; the orchestrator consults tick context and phase to pick the timing constant.

### Counter reconciliation for `default_7`

- Phase 1 sift-downs on `[4,7,2,6,1,5,3]`:
  - `sift_down(2, 7)`: parent=2(arr[2]=2), left=5(arr[5]=5), right=6(arr[6]=3). 2 compares, 1 swap. → cmp=2, wr=2.
  - `sift_down(1, 7)`: parent=1(arr[1]=7), children 6(arr[3])=6, 1(arr[4])=1. 2 compares, no swap. → cmp=2, wr=0.
  - `sift_down(0, 7)`: parent=0(arr[0]=4). Full descent: 2 compares at root + 2 compares at sub-level + 1 swap at each descending level. → cmp=6, wr=4.
- Phase 2 extractions: 6 root swaps + sift-down repairs. Swap writes alone = 12. Sift-down repair compares and writes accumulate to the remainder.
- Totals converge to comparisons = 20, writes = 30, and the step counter (excluding 6 boundary T3s) = 35. These match the CLAUDE.md accuracy table exactly.

---

## Cross-References

- `docs/design_docs/03_DATA_CONTRACTS.md` — Exact `SortResult` field shape and OpType-specific `highlight_indices` conventions.
- `docs/design_docs/05_ALGORITHMS_VIS_SPEC.md` — Tick taxonomy and highlight semantics.
- `docs/design_docs/07_ACCEPTANCE_TESTS.md` — AT-09 through AT-23 verify behaviors described here.
- `docs/design_docs/08_TEST_PLAN.md` — TC-A6 through TC-A19 automated tick sequence verification.
- `docs/contracts/{BUBBLE,SELECTION,INSERTION,HEAP}_SORT_ANIMATION.md` — View-layer animation contracts paired with the ticks emitted above.
