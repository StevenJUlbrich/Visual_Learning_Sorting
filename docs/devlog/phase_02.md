# DEVLOG Archive — Phase 2 (Algorithm Generators)

**Archived from:** `DEVLOG.md` on 2026-04-20 during the DEVLOG restructure.
**Covers:** All four algorithm generator implementations — Bubble Sort (2a), Selection Sort (2b), Insertion Sort (2c), Heap Sort (2d). Includes pre-action plans and post-action closeouts.
**Entries:** Newest first, preserving original format.

---

## 2026-04-20 11:06 EDT — Phase 2d closed: heap.py authored and smoke-tested (post-action)

### Worked on

Implemented `src/visualizer/models/heap.py` per the pre-action plan below. `HeapSort` extends `BaseSortAlgorithm` with `name="Heap Sort"` and `complexity="O(n log n)"`. `_sift_down` is a private generator method invoked via `yield from` from both Phase 1 (build) and Phase 2 (extraction).

### Results

**Exit criteria — all met:**

1. `comparisons == 20` on `[4, 7, 2, 6, 1, 5, 3]` ✓
2. `writes == 30` on `[4, 7, 2, 6, 1, 5, 3]` ✓
3. Final tick `is_complete == True`; final array `[1, 2, 3, 4, 5, 6, 7]` ✓
4. Empty input yields exactly one `FAILURE` tick ✓

**Bonus checks — all met:**

- D-058 verified across all 11 Logical Tree T3 ticks: parent is always first; the non-parent indices are a subset of `{2p+1, 2p+2}` in every case.
- Boundary T3 count = 6 (one per extraction); each is contiguous `range(0, heap_size)`.
- Logical Tree T3 count = 11 (4 in Phase 1 + 7 in Phase 2 across the six extraction sift-downs).
- T3 ticks never advance `comparisons` or `writes` — monotonicity check on RANGE ticks reports zero violations.
- Step count (T1 + T2) = **35** — matches CLAUDE.md Counter Accuracy table exactly.

Ruff + format: clean on first run (production file). Pyright: still blocked by missing `libatomic1` on WSL2 (Phase 2a/2b/2c open question carries forward); manual type review found no issues — `_sift_down` return type `Generator[SortResult]` matches `sort_generator`, no `Any` escapes, every `SortResult` field explicitly typed.

### Decisions made during authoring

- **`_sift_down` as a private method, not a module-level function.** The pseudocode sketches `sift_down(arr, start, end)` as a free function, but it mutates counters on the sorting instance. Making it a method gives natural access to `self.comparisons`, `self.writes`, and `self.data` without threading them through parameters. Leading underscore marks it private — not part of the `BaseSortAlgorithm` contract.
- **`largest = right` decision is NOT a yielded T1.** Pseudocode §4 is explicit: after the two per-child T1 compares, an internal `if arr[right] > arr[left]: largest = right` fires as a pure decision (not a data comparison in the pedagogical sense). Yielding it as T1 would bump `comparisons` from 20 to 22+. Encoded as a plain `if` with no yield or counter touch.
- **Swap condition uses strict `>` not `>=`.** Pseudocode has `if arr[largest] > arr[parent]`. For duplicate values no swap fires, which is correct behaviour for Heap Sort and matches the pseudocode literally.
- **Boundary T3 uses `tuple(range(heap_size))`, not `tuple(range(0, heap_size))`.** Single-argument `range` is idiomatic Python; semantically identical. No spec impact.
- **T1 message uses doc 03 format `"Comparing index {x} (value {arr[x]}) and index {y} (value {arr[y]})"`; T2 swap and both T3 variants follow pseudocode format.** Doc 03 §Tick Taxonomy line 125 prescribes only the T1 compare text for Heap Sort; pseudocode §4 supplies the rest. Consistent with the Phase 2a/2b/2c authority split.

### Surprises and corrections

**Surprise 1 — Contiguity alone cannot distinguish Boundary T3 from Logical Tree T3.** The pseudocode §4 note claims "Boundary T3 ticks are contiguous `tuple(range(0, k))` — distinguishable from Logical Tree T3." This is only true for `heap_size >= 4`. When `heap_size = 3`, the boundary tuple `(0, 1, 2)` collides exactly with the Logical Tree T3 emitted at parent=0 with both children (`left=1, right=2`). When `heap_size = 2`, boundary `(0, 1)` collides with a parent=0 single-child logical tree T3. My first smoke-test classifier used contiguity alone and misclassified 5 logical-tree ticks as boundary. Resolution: classify by message-text prefix (`"Active heap:"` vs `"Evaluating tree level"`), which the generator emits unambiguously. Spec implication: if TC-A19 (the test-plan helper) relies on contiguity alone, it will mis-segment the Phase 2 tail end. Worth a follow-up in Phase 3 when TC-A19 is authored. Captured as an open question below.

**Surprise 2 — Pre-flight trace miscounted Phase 1 logical-tree T3 count.** Pre-action table said 10 total logical T3 ticks; actual is 11 (Phase 1 = 4, not 3). Root cause: I counted the three Phase 1 sift-downs but only summed their T2 swaps, not their T3 level-entry emissions. The counter-relevant totals (`comparisons=20`, `writes=30`, `steps=35`) were all correct — only the book-keeping bonus count was off. Smoke-test expected value corrected to 11; no production-code change needed.

Neither surprise impacted the counter targets. The production implementation matched the pseudocode on the first code-write pass.

### Open questions

- **libatomic1 still missing.** Blocker carries forward from Phase 2a → 2b → 2c → 2d. Fix: `sudo apt-get install libatomic1`.
- **TC-A19 contiguity-based segmentation may need revision.** The pseudocode's claim that "Boundary T3 ticks are contiguous — distinguishable from Logical Tree T3" breaks for `heap_size ∈ {2, 3}` when the logical-tree T3 at parent=0 is also contiguous. If Phase 3's TC-A19 helper relies on contiguity alone, it must either (a) add a message-prefix check or (b) use sequencing context (boundary T3 always precedes an extraction T2; logical-tree T3 always precedes one or two T1 compares). Flag for Phase 3 test authoring.

### Next

**Phase 2 complete.** All four generators delivered: `bubble.py` (20/26), `selection.py` (21/10), `insertion.py` (17/19), `heap.py` (20/30/35). Next up: Phase 3 — algorithm unit tests. Could run in parallel with Phase 4 (easing module) per the original implementation order. Bring `heap.py` to the Cowork (Opus) session for spec-level review before moving to Phase 3.

---

## 2026-04-20 11:03 EDT — Phase 2d start: heap.py plan (pre-action)

### Model / session

Opus 4.6 (1M context, xhigh effort) per the 2026-04-19 model-strategy entry. Heap Sort is the most complex generator in Phase 2: two algorithmic phases, a recursive sift-down helper called via `yield from`, two distinct T3 variants, counter reconciliation across 15 swaps and 10 logical-tree levels, and the D-058 parent-first highlight rule. This is exactly the constraint-intersection density that justifies Opus.

### Plan

Implement `src/visualizer/models/heap.py` against `00_PSEUDOCODE.md §4`. Structure:

- **`HeapSort.sort_generator`** — top-level generator that drives Phase 1 (build) and Phase 2 (extract).
- **`HeapSort._sift_down(start, end)`** — private generator method. `end` is the exclusive upper bound. Called via `yield from` from both phases. Emits the sift-down grammar per TC-A19: T3 Logical Tree → T1 compare(s) (1 or 2) → T2 swap (0 or 1), repeated per level until heap property holds or left child falls out of range.

**Phase 1 — Build Max-Heap:**

```text
for start in range(n // 2 - 1, -1, -1):
    yield from self._sift_down(start, n)
```

Three sift-downs for n=7: start = 2, 1, 0.

**Phase 2 — Extraction:**

```text
heap_size = n
while heap_size > 1:
    end = heap_size - 1
    yield boundary-T3 (contiguous tuple(range(0, heap_size)))
    swap arr[0] with arr[end]; writes += 2; yield T2
    heap_size -= 1
    yield from self._sift_down(0, heap_size)
```

Six extractions for n=7.

### Traps to watch for

- **D-058 — parent first in Logical Tree T3.** `highlight_indices` must be `(parent, left, right)` or `(parent, left)` — never `(left, right, parent)` or similar. The TC-A19 segmentation helper relies on this.
- **T3 contiguity distinction.** Boundary T3 is `tuple(range(0, heap_size))` — contiguous. Logical Tree T3 is non-contiguous (parent, left, right or parent, left). The View differentiates by checking `tuple(sorted(indices)) == tuple(range(min, max+1))`. Confusing the two breaks TC-A19.
- **T3 does NOT increment any counters.** No `self.comparisons += 1`, no `self.writes += 1`, no step counter touch. Pure visual aid per D-041. Bug potential: pattern-matching "every yield ↔ counter++" would over-count.
- **`largest` update uses arr[right] > arr[left] comparison — NOT yielded as a T1.** Pseudocode §4 sets `largest = left`, emits T1(parent, left), conditionally emits T1(parent, right), then internally decides `largest = right if arr[right] > arr[left]`. That last inequality is a decision, not a tick. Yielding it as T1 would inflate `comparisons` to 22+.
- **Swap condition uses arr[largest] > arr[parent].** Not `>=`. If equal values exist, no swap is emitted. Matters for duplicate-value arrays (not default_7, but worth encoding correctly).
- **Extraction swap happens BEFORE heap_size decrement; sift-down uses the decremented heap_size.** The sift-down repair must operate on the shrunken heap — the just-extracted root value (now at `end`) must not be touched again.
- **Message authority: doc 03 for T1, pseudocode for T2 and T3.** Doc 03 line 125 prescribes the T1 compare format (`"Comparing index {x} (value {arr[x]}) and index {y} (value {arr[y]})"`). Doc 03 is silent on T2 swap text and both T3 variants; pseudocode §4 supplies those.
- **`sift_down(0, 1)` after the last extraction must return immediately** (left=1 >= end=1). Otherwise a stray tick is emitted for a one-element heap. The gate `if left >= end: return` handles this.

### Manual trace (pre-flight) for `[4, 7, 2, 6, 1, 5, 3]`

Phase 1 (build max-heap from `n//2-1 = 2` down to 0):

| Sift-down | Parent | Children | T1 compares | T2 swaps | Compares Δ | Writes Δ |
|-----------|--------|----------|-------------|----------|------------|----------|
| `sd(2,7)` | 2      | 5,6      | 2           | 1        | 2          | 2        |
| `sd(1,7)` | 1      | 3,4      | 2           | 0        | 2          | 0        |
| `sd(0,7)` | 0 → 1  | 1,2 then 3,4 | 4       | 2        | 4          | 4        |

Phase 1 subtotals: compares=8, writes=6. Max-heap = `[7, 6, 5, 4, 1, 2, 3]`.

Phase 2 (6 extractions):

| Ext | Pre-swap heap_size | Boundary T3 tuple length | Sift-down T1 | Sift-down T2 | Compares Δ | Writes Δ |
|-----|--------------------|--------------------------|--------------|--------------|------------|----------|
| 1   | 7                  | 7                        | 4            | 2            | 4          | 2+4 = 6  |
| 2   | 6                  | 6                        | 2            | 1            | 2          | 2+2 = 4  |
| 3   | 5                  | 5                        | 3            | 2            | 3          | 2+4 = 6  |
| 4   | 4                  | 4                        | 2            | 1            | 2          | 2+2 = 4  |
| 5   | 3                  | 3                        | 1            | 0            | 1          | 2+0 = 2  |
| 6   | 2                  | 2                        | 0            | 0            | 0          | 2+0 = 2  |

Phase 2 subtotals: compares=12, writes=24. Final array = `[1, 2, 3, 4, 5, 6, 7]`.

**Grand totals:** comparisons = 8+12 = **20** ✓; writes = 6+24 = **30** ✓.

Step count cross-check: T1 + T2 ticks = 20 + 15 = **35** ✓ (6 boundary T3 and 10 logical-tree T3 excluded per D-041; terminal tick not a step).

### Exit criteria

- `ruff check` + `ruff format --check` clean
- `pyright` clean (still blocked by missing `libatomic1`; manual type review substitutes — same status as Phase 2a/2b/2c)
- Smoke script: comparisons=20, writes=30, final tick `is_complete=True`, empty input yields single FAILURE tick
- Bonus checks: final array `[1,2,3,4,5,6,7]`; D-058 parent-first verified across all Logical Tree T3 ticks; boundary T3 count == 6 and each is contiguous; Logical Tree T3 count == 10 across Phase 1+2 and each is non-contiguous; T3 ticks produce no counter change (comparisons and writes advance only on T1/T2); step count (T1+T2) == 35

---

## 2026-04-20 10:46 EDT — Phase 2c closed: insertion.py authored and smoke-tested (post-action)

### Worked on

Implemented `src/visualizer/models/insertion.py` per the pre-action plan below. All four pseudocode phases (key selection, compare-and-shift, terminating compare, placement) emit ticks in the prescribed order with the prescribed counters.

### Results

**Exit criteria — all met:**

1. `comparisons == 17` on `[4, 7, 2, 6, 1, 5, 3]` ✓
2. `writes == 19` on `[4, 7, 2, 6, 1, 5, 3]` ✓
3. Final tick `is_complete == True`; final array `[1, 2, 3, 4, 5, 6, 7]` ✓
4. Empty input yields exactly one `FAILURE` tick ✓

**Bonus checks — all met:**

- Pass-by-pass counter segmentation matches the `00_PSEUDOCODE.md §3` truth table exactly across all 6 passes (shift-compares, shifts, placements, terminating-present).
- No duplicate indices in any 2-element `highlight_indices`.
- Key-selection and placement emit single-index highlights as specified.

Ruff: clean on first run. Format: clean on first run. Pyright: still blocked by missing `libatomic1` on WSL2 host (Phase 2a DEVLOG open question still pending); manual type review found no issues — all annotations explicit, no `Any` escapes, all `SortResult` fields typed correctly.

### Decisions made during authoring

- **Terminating compare uses the same doc 03 compare message as shift-loop compares.** Doc 03 §Tick Taxonomy line 124 prescribes one compare format for Insertion Sort; it does not specify a distinct "terminating" variant. Pseudocode uses a suffix ("— stop") but doc 03 is the message authority per the Phase 2b lesson. Using one format keeps the message line pedagogically consistent. If a future spec update adds a terminating-specific message, it's a one-line change.
- **Shift and placement messages follow pseudocode format verbatim.** Doc 03 is silent on T2 text for Insertion Sort. Pseudocode §3 supplies `"Shift arr[{j}]={arr[j]} right to slot {j + 1}"` and `"Place key={key} at slot {j + 1}"`. Used these literally.
- **Key-selection tick is `OpType.COMPARE` with no counter increment.** Doc 03 line 153 is explicit: key-selection uses `COMPARE` for timing alignment but is not a data comparison. Implemented by emitting the tick without touching `self.comparisons`.
- **Smoke script includes pass-segmentation bonus check.** The pseudocode pass-by-pass truth table is the single highest-risk spec in the project. A smoke test that re-verifies it per-pass (not just in aggregate) catches off-by-one errors that the counter totals would mask (e.g., an extra compare in one pass balanced by a missing compare in another). Cheap insurance for a cheap test.

### Surprises / non-obvious findings

- **None.** The pre-flight manual trace against the truth table caught every potential off-by-one before the first yield was written. Writing against a fully-traced target array is strictly better than writing-then-fixing.
- **`arr[j]` in the shift message is the post-copy value.** After `arr[j+1] = arr[j]`, both slots hold the same value and `arr[j]` in the f-string still resolves to the shifted value (the original was never overwritten on the source slot — it gets overwritten on the *next* iteration when a new `arr[j+1] = arr[j]` executes with the decremented j). Pseudocode convention confirmed consistent.

### Open questions (status)

- **libatomic1 still missing.** Pyright blocker carries forward to Phase 2d. `sudo apt-get install libatomic1` resolves it.

### DEVLOG housekeeping (2026-04-20 10:54 EDT)

Two post-review fixes to the DEVLOG itself, flagged during Phase 2c sign-off:

- **Entry ordering restored to newest-first.** The Phase 2a (bubble) entry had drifted to the very top of the file, above the Phase 2c entries that followed it chronologically. Root cause: the pre-action/post-action entries were prepended via `Edit` with the same anchor used for the first DEVLOG update, which pushed Phase 2a up instead of Phase 2c. Moved Phase 2a to its correct position between Phase 2b and the 2026-04-19 model-strategy entry. Final top-to-bottom order: Phase 2c post → Phase 2c pre → Phase 2b → Phase 2a → model strategy → Correction C → Phase 1 → earlier.
- **Model version corrected.** The pre-action entry's "Model / session" section said "Opus 4.7"; the session is actually on Opus 4.6. Fixed inline.

Neither fix touched the technical content of any entry — only ordering and the single model-version string. Spec-review feedback confirmed Issue 2 (the Selection Sort `prev_min` narrative) was intentionally preserved as a correction story valuable for the video journal.

### Next

Phase 2d: `heap.py` — the last Phase 2 algorithm. Two phases (build + extract), recursive sift-down with `yield from`, two T3 variants (boundary contiguous vs logical-tree non-contiguous), D-058 parent-first highlight, counter reconciliation 20/30/35 with 6 excluded boundary ticks. Staying on Opus for this one per the model strategy.

---

## 2026-04-20 10:45 EDT — Phase 2c start: insertion.py plan (pre-action)

### Model / session

Opus 4.6 (1M context, xhigh effort) per the 2026-04-19 model-strategy entry — Insertion Sort's terminating-compare rule is the highest-risk control-flow decision in the project, which is exactly the constraint-density the Opus assignment anticipates.

### Plan

Implement `src/visualizer/models/insertion.py` strictly against `00_PSEUDOCODE.md §3`. Phase structure per pass:

1. **Key Selection (Phase 1).** Single T1 tick with `highlight_indices=(i,)`, `OpType.COMPARE`. Does **NOT** increment `self.comparisons` — visual/pedagogical tick only per D-071 / doc 03 line 153. Message: doc 03 format `"Selecting key: {arr[i]} at index {i}"`.

2. **Compare-and-shift loop (Phase 2).** Each iteration emits T1 compare + T2 shift individually. Never batch (D-060, D-064). Each shift is `OpType.SHIFT`, `writes += 1`, `highlight_indices=(j, j+1)`. Compare message: doc 03 format `"Comparing index {j} (value {arr[j]}) with key {key}"`. Shift message: pseudocode format (doc 03 silent on T2 text).

3. **Terminating Compare (Phase 2b).** Fires **only** when while-loop exits by `arr[j] <= key`, NOT by `j < 0`. Control-flow gate: `if j >= 0`. Uses same doc 03 compare message format. This is the rule TC-A14 pins down.

4. **Placement (Phase 3).** `arr[j+1] = key`, `writes += 1`, `OpType.SHIFT`, `highlight_indices=(j+1,)` single-index. Pseudocode message.

### Traps to watch for

- **Key-selection counter rule.** The key-selection T1 uses `OpType.COMPARE` for timing alignment but does NOT increment the counter. Easy to over-count if the comparisons++ is pattern-matched to every COMPARE yield.
- **Terminating-compare gate.** Yielding the terminating T1 unconditionally would over-count comparisons by roughly 1 per pass where `j < 0` at exit. For `default_7` that's 2 extra comparisons → 19 instead of 17. Counter table catches this.
- **Sequential shift emission.** Batching shifts into a single T2 would break D-060 / D-064 and TC-A9. Each shift must be its own T2 tick preceded by its own T1 compare.
- **Single-index highlight on placement.** Placement uses `(j+1,)`, not `(j, j+1)`. The view layer differentiates these.
- **Message format source of truth.** Lesson from Phase 2a/2b: doc 03 §Tick Taxonomy is the message authority; pseudocode is the control-flow authority. Where doc 03 prescribes a message format, use doc 03 (compare, key-selection). Where doc 03 is silent (shift, placement), follow pseudocode.

### Manual trace (pre-flight)

Traced `[4, 7, 2, 6, 1, 5, 3]` against the pseudocode pass-by-pass truth table to verify my mental model before coding:

| Pass | key | Shift compares | Terminating? | Shifts | Placement |
|------|-----|----------------|--------------|--------|-----------|
| i=1  | 7   | 0              | Yes (j=0)    | 0      | 1         |
| i=2  | 2   | 2              | No (j=-1)    | 2      | 1         |
| i=3  | 6   | 1              | Yes (j=1)    | 1      | 1         |
| i=4  | 1   | 4              | No (j=-1)    | 4      | 1         |
| i=5  | 5   | 2              | Yes (j=2)    | 2      | 1         |
| i=6  | 3   | 4              | Yes (j=1)    | 4      | 1         |

Totals: compares = 13 + 4 = **17** ✓; writes = 13 shifts + 6 placements = **19** ✓. Matches CLAUDE.md Counter Accuracy table.

### Exit criteria

- `pyright` clean (blocked by missing `libatomic1` same as Phase 2a/2b; manual type review will substitute)
- `ruff check` + `ruff format --check` clean
- Smoke script: comparisons=17, writes=19, final tick `is_complete=True`, empty input yields single FAILURE tick
- Optional bonus checks: pass-by-pass counter segmentation matches the truth table above; no duplicate indices in any 2-element `highlight_indices`

---

## 2026-04-20 — Phase 2b closed: selection.py authored and smoke-tested

### Worked on

Implemented `src/visualizer/models/selection.py` against the Phase 2 pack in `14_CONTEXT_PACKS.md`. Pseudocode source: `00_PSEUDOCODE.md §2`. `SelectionSort` extends `BaseSortAlgorithm` with `name="Selection Sort"` and `complexity="O(n²)"`. Outer loop selects sorted boundary `i`; inner scan tracks `min_idx`. Swap skipped when `min_idx == i` (no T2 emitted in that pass).

Smoke script `scripts/smoke_selection.py` verified all exit criteria plus a highlight-uniqueness guard:

1. `comparisons == 21` on `[4, 7, 2, 6, 1, 5, 3]` ✓
2. `writes == 10` on `[4, 7, 2, 6, 1, 5, 3]` ✓
3. Final tick `is_complete == True` ✓
4. Empty input yields exactly one `FAILURE` tick ✓
5. No duplicate indices in any T1 `highlight_indices` (new-minimum case) ✓

Ruff: clean after one fix (RUF002 — Unicode multiplication sign `×` in docstring, replaced with ASCII `x`). Format check: clean.

Pyright still blocked by missing `libatomic1`; same environment constraint as Phase 2a.

### Decisions

- **Two-variant T1 message, determined after comparison.** Doc 03 §Tick Taxonomy line 122 specifies two message forms: the standard compare form and a "New minimum" form when `arr[j] < arr[min_idx]`. Comparison is evaluated before the yield; the message branch is chosen from the result. One T1 per `j` iteration preserved — comparisons counter unaffected.

- **`prev_min` saves old `min_idx` before update; highlight uses `(prev_min, j)`.** After `min_idx = j`, using `(min_idx, j)` in the highlight would produce `(j, j)` — duplicate indices, a contract violation. Saving the old position as `prev_min` and using `(prev_min, j)` keeps `highlight_indices` unique while matching the D-068 semantic: the tuple shows the two indices whose values were just compared. The pseudocode comment "the next T1 will show it" confirms the old min_idx is correct for the current tick's highlight.

- **Swap message follows pseudocode literal: `f"Swap arr[{i}] and arr[{min_idx}]"`.** Doc 03 prescribes no specific Selection Sort swap message format; pseudocode §2 is the reference.

### Spec review findings (Opus oversight session)

Two issues identified before sign-off:

**Issue 1 — Yield timing diverges from pseudocode.** The implementation checked `arr[j] < arr[min_idx]` first, updated `min_idx`, saved `prev_min`, then yielded using `prev_min`. The pseudocode (§2 lines 91-98) is explicit: yield T1 with current `min_idx`, *then* update silently. The `if/else` branch with two separate yields and `prev_min` is unnecessary complexity — yielding before the update avoids the duplicate-index problem entirely and matches the pseudocode structure.

**Issue 2 — "New minimum" message.** Doc 03 §Tick Taxonomy line 122 describes a two-message variant for Selection Sort T1 (standard compare vs "New minimum: …"). The pseudocode has one message format for all T1 ticks and a silent post-yield update. These two specs are in tension; the pseudocode is the control-flow authority. Adopting Issue 1's fix collapses both issues: with one yield path there is only one message, and the "new minimum" variant from doc 03 is superseded by pseudocode intent.

**Root cause of both issues:** Attempting to differentiate the "new minimum" message before verifying whether the pseudocode supported a second yield. Should have checked pseudocode control flow first, then doc 03 message table, not the reverse.

### Corrections

**C1 — Rewrite inner loop to yield before update (resolves Issue 1 and Issue 2).** Single yield per `j`, no `prev_min`, no branch. `highlight_indices=(min_idx, j)` is always unique because `min_idx` hasn't been updated at yield time. Message uses the standard compare format for all T1 ticks. Smoke tests re-run and counters still match.

### Open questions

- **libatomic1 still missing.** Pyright cannot run until `sudo apt-get install libatomic1` is executed on the WSL2 host. Both Phase 2a and 2b deliverables are pending that one-time fix.

### Next

Phase 2c: `insertion.py` (Opus — terminating-compare rule is high-risk). Escalation path if Sonnet is used: switch on first counter failure.

---

## 2026-04-20 — Phase 2a closed: bubble.py authored and smoke-tested

### Worked on

Implemented `src/visualizer/models/bubble.py` against the Phase 2 pack in `14_CONTEXT_PACKS.md`. Pseudocode source: `00_PSEUDOCODE.md §1`. `BubbleSort` extends `BaseSortAlgorithm`, constructing with `name="Bubble Sort"` and `complexity="O(n²)"`. Generator control flow is classic two-loop with `swapped` early-exit; inner limit is `n - pass_idx - 1` (the LimitLine boundary).

Smoke script `scripts/smoke_bubble.py` verified all four exit criteria:

1. `comparisons == 20` on `[4, 7, 2, 6, 1, 5, 3]` ✓
2. `writes == 26` on `[4, 7, 2, 6, 1, 5, 3]` ✓
3. Final tick `is_complete == True` ✓
4. Empty input yields exactly one `FAILURE` tick ✓

Ruff check + format check: clean.

**Pyright blocked by environment:** WSL2 system is missing `libatomic1`, which the pyright-python Node.js runtime requires. Manual type review performed instead (see Decisions). To enable pyright: `sudo apt-get install libatomic1`.

### Decisions

- **Manual pyright review findings:** All annotations are explicit. `sort_generator` return type matches the base class `Generator[SortResult]` exactly. `arr = self.data` is `list[int]`; `list(arr)` copies produce `list[int]`. Tuple literals `(j, j+1)` satisfy `tuple[int, ...]`. No `Any` escapes. No issues found that would fail strict mode.
- **Single-element guard yields TERMINAL with `highlight_indices=(0,)`.** Pseudocode says `yield T4_done()` for `n==1`; `T4_done` is `highlight_indices=tuple(range(n))`, which is `(0,)` for n=1. Consistent with the final tick convention.
- **Swap message uses post-mutation values.** Pseudocode says `f"Swap {arr[j+1]} and {arr[j]}"` after the swap; both `arr[j]` and `arr[j+1]` already hold the exchanged values at that point. Matches the pseudocode literally.
- **No T3 ticks emitted.** Confirmed — Bubble Sort emits only T1 and T2 ticks plus the terminal. Per 00_PSEUDOCODE.md §1 invariants.

### Corrections

**C1 — Bubble Sort compare message format.** Line 51 used `f"Compare {arr[j]} and {arr[j + 1]}"`. Doc 03 §Tick Taxonomy specifies `f"Comparing index {j} (value {arr[j]}) and index {j + 1} (value {arr[j + 1]})"`. Fixed in place; smoke tests still pass.

**Why it was missed:** The Phase 2 pack names `00_PSEUDOCODE.md` as the canonical control-flow spec and the pseudocode §1 shows the terse `f"Compare {arr[j]} and {arr[j+1]}"` form. Doc 03 §Tick Taxonomy carries the fuller pedagogical format, but the pack lists doc 03 as a secondary input and the implementation session followed the pseudocode wording literally without cross-checking doc 03's message schema. The fix is a one-line message string change with no counter or tick-structure impact.

**Lesson for remaining generators:** When authoring the T1 message string, verify the exact format against doc 03 §Tick Taxonomy, not just `00_PSEUDOCODE.md`. The pseudocode is authoritative for *when* a tick fires; doc 03 is authoritative for *what each field contains*.

### Open questions

- **libatomic1 missing on dev WSL2.** `sudo apt-get install libatomic1` resolves it. Until then, pyright cannot be invoked and CI will need to be run on a machine with the library available.

### Next

Phase 2b: `selection.py`. Bring `bubble.py` to the Cowork (Opus) session for spec-level review before proceeding.
