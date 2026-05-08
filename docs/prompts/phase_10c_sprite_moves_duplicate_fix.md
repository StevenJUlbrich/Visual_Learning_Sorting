# Phase 10c — Fix `compute_sprite_moves()` for Duplicate Values

**Model:** Opus 4.7
**Context:** Phase 10 acceptance testing revealed that `compute_sprite_moves()` silently fails when the array contains duplicate values. Sprites end up in wrong positions because the function can't detect movement when equal values shift or swap.

---

## STEP 1 — DEVLOG PRE-ACTION

Append the following entry to `DEVLOG.md` (at the end of the current Phase 10 section):

```markdown
### 10c pre-action: Fix compute_sprite_moves() for duplicate values (2026-05-08)

**Plan:** Augment `compute_sprite_moves()` with `operation_type` and `highlight_indices` parameters (both optional, default `None`). When the existing value-delta detection finds zero changes but the tick is a SHIFT or SWAP with a 2-element `highlight_indices`, use the highlight data to determine which slots exchanged sprites. Existing logic unchanged for non-empty `changed` lists (backward compatible). Update call site in `Orchestrator.update()` to pass tick data. Add 6 new unit tests for duplicate-value cases. Existing 8 Group 13 tests and 7 integration tests must pass unchanged.

**Root cause:** `changed = [i for i in range(len(old_state)) if old_state[i] != new_state[i]]` produces an empty list when equal values shift or swap. The function returns `{}` — no sprite movement. Over a full sort with duplicates, sprites diverge from actual positions.

**Exit criteria:**
1. `uv run ruff check src/ tests/` — clean
2. `uv run ruff format --check src/ tests/` — clean
3. `uv run pytest -x` — all passing (339 existing + 6 new = 345)
4. Import check — OK
5. All existing tests pass WITHOUT modification to their call signatures
```

---

## STEP 2 — IMPLEMENTATION

### §1 Problem Statement

`compute_sprite_moves()` in `src/visualizer/controllers/orchestrator.py` (lines 87–122) detects which sprites moved by comparing old and new array states:

```python
changed = [i for i in range(len(old_state)) if old_state[i] != new_state[i]]
```

With unique values, every SHIFT or SWAP changes at least one slot's value, so `changed` is non-empty and the function works.

With duplicate values, a SHIFT or SWAP between equal-valued slots produces identical old/new states. `changed` is empty. The function returns `{}` — no sprite movement detected. Over a full sort, sprites accumulate in wrong positions.

**Concrete example (Insertion Sort, array `[3, 1, 3, 2, 1, 2, 3]`):**

Pass 3, key=2. Array before pass: `[1, 3, 3, 2, 1, 2, 3]`.

1. Shift slot 2→3: `arr[3] = arr[2]` (value 3 replaces value 2). State: `[1, 3, 3, 3, 1, 2, 3]`. Slot 3 changed 2→3. `changed = [3]` → **detected correctly.**
2. Shift slot 1→2: `arr[2] = arr[1]` (value 3 replaces value 3). State: `[1, 3, 3, 3, 1, 2, 3]` — unchanged. `changed = []` → **movement invisible.** Sprite at slot 1 should move to slot 2 but doesn't.

The same problem affects SWAP operations. Heap Sort extraction swaps `arr[0]` with `arr[end]` unconditionally. If both hold the same value, `changed` is empty and the extraction is invisible.

**Visual result:** Insertion Sort shows `1, 2, 3, 1, 2, 3, 3` instead of `1, 1, 2, 2, 3, 3, 3`. Heap Sort has sprites vertically misaligned in the sorted row.

---

## §2 Fix Strategy

Augment `compute_sprite_moves()` with the tick's `operation_type` and `highlight_indices`. When the value-delta detection (`changed`) works (non-empty), use it — no behavior change for unique-value arrays. When `changed` is empty but the tick indicates a SHIFT or SWAP occurred, use `highlight_indices` to determine which slots are involved and move sprites accordingly.

This is approach (A) from the devlog — minimal contract change, uses data already in every tick.

---

## §3 Changes to `compute_sprite_moves()`

### §3.1 New Signature

```python
def compute_sprite_moves(
    old_state: list[int],
    new_state: list[int],
    slot_to_sprite_id: list[int],
    operation_type: OpType | None = None,
    highlight_indices: tuple[int, ...] | None = None,
) -> dict[int, int]:
```

The two new parameters default to `None` for backward compatibility with tests. Import `OpType` at the top of the module (it's already available — `from visualizer.models.contracts import OpType` exists via PanelContext usage; verify and add if needed).

### §3.2 Logic Changes

The existing logic handles three cases based on `len(changed)`: 0, 1, and 2. The fix adds a **fallback path** when `changed` is empty but a mutation tick is present.

After the existing `if len(changed) == 0: return {}` block, replace it with:

```python
if len(changed) == 0:
    # Value-delta detection found nothing. For unique arrays, this means
    # no movement occurred. For duplicate arrays, equal-value shifts/swaps
    # produce identical states. Fall through to highlight-based detection.
    if operation_type in (OpType.SWAP, OpType.SHIFT) and highlight_indices is not None:
        if len(highlight_indices) == 2:
            i, j = highlight_indices[0], highlight_indices[1]
            sprite_a = slot_to_sprite_id[i]
            sprite_b = slot_to_sprite_id[j]
            slot_to_sprite_id[i] = sprite_b
            slot_to_sprite_id[j] = sprite_a
            return {sprite_a: j, sprite_b: i}
    return {}
```

**Why this works:**

- **SWAP with equal values:** `highlight_indices = (slot_a, slot_b)`. Both slots hold the same value. The swap is a no-op on the array but the sprites at those slots must exchange positions. The 2-element highlight gives us both slots.
- **SHIFT with equal values:** `highlight_indices = (j, j+1)`. The element at slot `j` copied to slot `j+1`, but both already held the same value. The sprite at `j` should move to `j+1` and the sprite at `j+1` should move to `j` (same swap-the-IDs pattern as the existing 1-change handler).
- **Placement SHIFT (1-element highlight):** `highlight_indices = (j+1,)`. This is the "key drops to slot" tick. With `len(highlight_indices) != 2`, the guard rejects it and returns `{}` — same as the existing placement handler. Correct behavior.

### §3.3 Important: Do NOT change the existing 1-change and 2-change paths

The existing handlers for `len(changed) == 1` and `len(changed) == 2` are correct and must remain unchanged. They handle the common case (unique values) efficiently. The new code only activates when `changed` is empty AND a mutation tick is present.

---

## §4 Call Site Update

In `Orchestrator.update()` (around line 256), pass the tick's operation_type and highlight_indices:

```python
# Sprite identity delta (6c)
if tick.array_state is not None and ctx.previous_array_state is not None:
    ctx.sprite_moves = compute_sprite_moves(
        ctx.previous_array_state,
        tick.array_state,
        ctx.slot_to_sprite_id,
        operation_type=tick.operation_type,
        highlight_indices=tick.highlight_indices,
    )
else:
    ctx.sprite_moves = {}
```

---

## §5 Test Updates

### §5.1 Existing Tests — Signature Compatibility

The new parameters default to `None`, so **all existing Group 13 tests pass without modification.** When `operation_type` is `None`, the `if operation_type in (OpType.SWAP, OpType.SHIFT)` guard is `False`, and the function falls through to `return {}` — same as before.

Verify this claim by running the existing test suite unchanged after the code modification. If any test fails, investigate — it means the logic change has an unintended side effect.

### §5.2 New Tests — Duplicate Value Cases

Add the following tests to Group 13 in `tests/unit/test_orchestrator.py`. Place them after the existing `test_slot_to_sprite_id_mutated_in_place` test.

**Test 1: SHIFT with equal values detected via highlight_indices.**

```python
@pytest.mark.unit
def test_shift_duplicate_values_detected() -> None:
    """When a shift copies value X to a slot already holding X, changed is empty.
    The function must use highlight_indices to detect the movement."""
    # Simulates: arr[2] = arr[1] where both hold value 3.
    # old_state and new_state are identical — value delta is empty.
    old_state = [1, 3, 3, 3, 1, 2, 3]
    new_state = [1, 3, 3, 3, 1, 2, 3]  # identical
    slot_mapping = [0, 1, 2, 3, 4, 5, 6]
    result = compute_sprite_moves(
        old_state, new_state, slot_mapping,
        operation_type=OpType.SHIFT,
        highlight_indices=(1, 2),
    )
    # Sprite at slot 1 moves to slot 2, sprite at slot 2 moves to slot 1.
    assert result == {1: 2, 2: 1}
    assert slot_mapping == [0, 2, 1, 3, 4, 5, 6]
```

**Test 2: SWAP with equal values detected via highlight_indices.**

```python
@pytest.mark.unit
def test_swap_duplicate_values_detected() -> None:
    """When a swap exchanges two equal values, changed is empty.
    The function must use highlight_indices to detect the movement."""
    # Simulates: heap extraction swap of arr[0] and arr[2] where both hold 3.
    old_state = [3, 1, 3]
    new_state = [3, 1, 3]  # identical
    slot_mapping = [0, 1, 2]
    result = compute_sprite_moves(
        old_state, new_state, slot_mapping,
        operation_type=OpType.SWAP,
        highlight_indices=(0, 2),
    )
    assert result == {0: 2, 2: 0}
    assert slot_mapping == [2, 1, 0]
```

**Test 3: Placement SHIFT with duplicate values — key drops into slot holding same value.**

```python
@pytest.mark.unit
def test_placement_duplicate_value_no_spurious_move() -> None:
    """Placement tick where key value equals the value already in the target slot.
    old_state and new_state are identical (key=3 placed into slot already holding 3).
    highlight_indices has 1 element (placement slot). The fallback must NOT fire
    because len(highlight_indices) != 2."""
    old_state = [1, 3, 3, 3, 1, 2, 3]
    new_state = [1, 3, 3, 3, 1, 2, 3]  # identical — placement of same value
    slot_mapping = [0, 1, 2, 3, 4, 5, 6]
    result = compute_sprite_moves(
        old_state, new_state, slot_mapping,
        operation_type=OpType.SHIFT,
        highlight_indices=(1,),  # single-element: placement
    )
    # changed is empty, highlight has 1 element → guard rejects → returns {}
    assert result == {}
    assert slot_mapping == [0, 1, 2, 3, 4, 5, 6]  # unchanged
```

**Test 4: Full Insertion Sort with duplicates preserves sprite identity.**

```python
@pytest.mark.unit
def test_full_sort_duplicates_identity_preserved() -> None:
    """Run Insertion Sort on a duplicate-heavy array. Every sprite ID must appear
    exactly once in the final slot_mapping."""
    from visualizer.models.insertion import InsertionSort

    arr = [3, 1, 3, 2, 1, 2, 3]
    algo = InsertionSort(list(arr))
    slot_mapping = list(range(len(arr)))
    prev = list(arr)
    for tick in algo.sort_generator():
        if tick.array_state is not None:
            compute_sprite_moves(
                prev, tick.array_state, slot_mapping,
                operation_type=tick.operation_type,
                highlight_indices=tick.highlight_indices,
            )
            prev = tick.array_state
    # All 7 sprite IDs present exactly once
    assert sorted(slot_mapping) == list(range(len(arr)))
    assert len(set(slot_mapping)) == len(arr)
```

**Test 5: Full Bubble Sort with duplicates preserves sprite identity.**

```python
@pytest.mark.unit
def test_full_sort_bubble_duplicates_identity_preserved() -> None:
    """Run Bubble Sort on a duplicate-heavy array. Every sprite ID must appear
    exactly once in the final slot_mapping."""
    from visualizer.models.bubble import BubbleSort

    arr = [3, 1, 3, 2, 1, 2, 3]
    algo = BubbleSort(list(arr))
    slot_mapping = list(range(len(arr)))
    prev = list(arr)
    for tick in algo.sort_generator():
        if tick.array_state is not None:
            compute_sprite_moves(
                prev, tick.array_state, slot_mapping,
                operation_type=tick.operation_type,
                highlight_indices=tick.highlight_indices,
            )
            prev = tick.array_state
    assert sorted(slot_mapping) == list(range(len(arr)))
    assert len(set(slot_mapping)) == len(arr)
```

**Test 6: Full Heap Sort with duplicates preserves sprite identity.**

```python
@pytest.mark.unit
def test_full_sort_heap_duplicates_identity_preserved() -> None:
    """Run Heap Sort on a duplicate-heavy array. Every sprite ID must appear
    exactly once in the final slot_mapping."""
    from visualizer.models.heap import HeapSort

    arr = [3, 1, 3, 2, 1, 2, 3]
    algo = HeapSort(list(arr))
    slot_mapping = list(range(len(arr)))
    prev = list(arr)
    for tick in algo.sort_generator():
        if tick.array_state is not None:
            compute_sprite_moves(
                prev, tick.array_state, slot_mapping,
                operation_type=tick.operation_type,
                highlight_indices=tick.highlight_indices,
            )
            prev = tick.array_state
    assert sorted(slot_mapping) == list(range(len(arr)))
    assert len(set(slot_mapping)) == len(arr)
```

### §5.3 Existing Full-Sort Test

The existing `test_full_sort_identity_preserved` (line 706) runs Bubble Sort with the default unique array and does NOT pass `operation_type` / `highlight_indices`. This must continue to pass unchanged — it validates that the `None` defaults preserve backward compatibility.

### §5.4 Integration Tests

The 7 integration tests in `tests/integration/test_orchestrator_integration.py` exercise the orchestrator's `update(dt)` loop, which calls `compute_sprite_moves` at line 256. These tests use the default array (unique values) and should pass without modification. Run them to verify no regressions.

---

## §6 Import Verification

Ensure `OpType` is imported in `orchestrator.py`. Check the existing imports at the top of the file. `OpType` is already used indirectly via `PanelContext` and `get_duration()` which reference `SortResult.operation_type`. If `OpType` is not directly imported, add:

```python
from visualizer.models.contracts import OpType
```

to the imports section (it may already be present via `SortResult` — verify).

---

## §7 What NOT to Change

1. **Do NOT modify any algorithm generator** (bubble.py, selection.py, insertion.py, heap.py). The algorithms are correct. The bug is in sprite tracking, not sorting logic.
2. **Do NOT modify `SortResult` or `OpType`** in contracts.py. No contract changes.
3. **Do NOT modify sprite_manager.py or main.py.** This fix is controller-layer only.
4. **Do NOT remove or modify the existing `len(changed) == 1` or `len(changed) == 2` handlers.** They handle the common case correctly. The new code is a fallback when `changed` is empty.

---

---

## STEP 3 — GATES

Run all four in sequence. All must pass. Fix any issues before proceeding.

```bash
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run pytest -x
python -c "from visualizer.controllers.orchestrator import compute_sprite_moves, Orchestrator; print('OK')"
```

---

## STEP 4 — DEVLOG POST-ACTION

Append a post-action entry to `DEVLOG.md` immediately after the 10c pre-action entry:

```markdown
### 10c closed: Fix compute_sprite_moves() for duplicate values (2026-05-08)

**Worked on**

[Describe what was actually changed — new parameters added, fallback logic, call site update, tests added. Note any deviations from the plan.]

**Corrections**

[List any ruff/format corrections, or "Zero corrections" if clean on first run.]

**Results**

- `uv run ruff check src/ tests/`: **[clean/N issues]**
- `uv run ruff format --check src/ tests/`: **[clean/N issues]**
- `uv run pytest -x`: **[N]/[N] PASSED** (expected 345 = 339 existing + 6 new)
- Import check: **[PASS/FAIL]**

**Verification note**

Manual visual verification deferred to Steven — run with `config.toml` array `[3, 1, 3, 2, 1, 2, 3]` and confirm:
- All four panels show `[1, 1, 2, 2, 3, 3, 3]` at completion
- Insertion Sort sprites in correct order (was `1, 2, 3, 1, 2, 3, 3`)
- Heap Sort sorted-row sprites all on same baseline y-coordinate
- Then restore default array `[4, 7, 2, 6, 1, 5, 3]` and verify no regressions

**Next**

If Issue #8 (Heap vertical misalignment) resolves with this fix, close it. Proceed to 10d (Heap visual batch) and 10e (pointer spacing).
```

---

## Files Changed (Summary)

| File | Change |
|------|--------|
| `src/visualizer/controllers/orchestrator.py` | `compute_sprite_moves()` signature + fallback logic + call site |
| `tests/unit/test_orchestrator.py` | 6 new tests (duplicate-value cases) |
| `DEVLOG.md` | Pre-action and post-action entries for 10c |

---

## Context Files to Read

Read these files before writing any code:

1. `CLAUDE.md` — Critical Rules (especially #1 sprite identity by unique ID)
2. `src/visualizer/controllers/orchestrator.py` — `compute_sprite_moves()` (lines 87–122), call site (lines 254–260), existing imports
3. `tests/unit/test_orchestrator.py` — Group 13 tests (lines 649–725), imports (lines 9–24)
4. `src/visualizer/models/contracts.py` — `OpType` enum, `SortResult` dataclass
5. `DEVLOG.md` — Active working journal (append pre/post entries at end of current Phase 10 section)
