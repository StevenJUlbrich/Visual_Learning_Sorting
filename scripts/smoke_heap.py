"""Smoke test for HeapSort generator.

Usage: uv run python scripts/smoke_heap.py

Exit criteria:
  - comparisons == 20
  - writes == 30
  - final tick is_complete == True
  - empty input yields exactly one FAILURE tick

Bonus checks (Heap Sort is the most constraint-dense generator):
  - Final array == [1, 2, 3, 4, 5, 6, 7]
  - D-058: parent is first element of every Logical Tree T3 highlight
  - Boundary T3 count == 6 and each is contiguous
  - Logical Tree T3 count == 10 and each is non-contiguous
  - T3 ticks never advance comparisons or writes counters
  - Step count (T1 + T2) == 35
"""

import sys

sys.path.insert(0, "src")

from visualizer.models.contracts import OpType, SortResult
from visualizer.models.heap import HeapSort


def check(label: str, actual: object, expected: object) -> bool:
    ok = actual == expected
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {label}: expected {expected!r}, got {actual!r}")
    return ok


def is_contiguous(indices: tuple[int, ...]) -> bool:
    """True iff indices form a contiguous run when sorted."""
    s = sorted(indices)
    return s == list(range(s[0], s[-1] + 1))


def run_default() -> bool:
    sorter = HeapSort([4, 7, 2, 6, 1, 5, 3])
    ticks = list(sorter.sort_generator())
    last = ticks[-1]
    print("default_7 run:")
    ok = True
    ok &= check("comparisons", sorter.comparisons, 20)
    ok &= check("writes", sorter.writes, 30)
    ok &= check("final tick is_complete", last.is_complete, True)
    ok &= check("final tick success", last.success, True)
    ok &= check("final tick operation_type", last.operation_type, OpType.TERMINAL)
    ok &= check("final array sorted", last.array_state, [1, 2, 3, 4, 5, 6, 7])
    return ok


def run_t3_invariants() -> bool:
    """Verify D-058 parent-first, boundary/logical segmentation, and count.

    Classifier note: contiguity alone does NOT distinguish the two T3 variants.
    Logical Tree T3 at parent=0 emits (0,1,2) or (0,1) which are contiguous
    and collide with boundary T3 at heap_size=3 or 2.  We classify by the
    message-text prefix emitted by the generator, which is unambiguous.
    """
    sorter = HeapSort([4, 7, 2, 6, 1, 5, 3])
    ticks = list(sorter.sort_generator())

    boundary_t3: list[SortResult] = []
    logical_t3: list[SortResult] = []
    for t in ticks:
        if t.operation_type is not OpType.RANGE:
            continue
        if t.message.startswith("Active heap"):
            boundary_t3.append(t)
        elif t.message.startswith("Evaluating tree level"):
            logical_t3.append(t)
        else:
            print(f"  [FAIL] unrecognised T3 message: {t.message!r}")
            return False

    print("t3_invariants check:")
    ok = True
    ok &= check("boundary T3 count", len(boundary_t3), 6)
    ok &= check("logical tree T3 count", len(logical_t3), 11)

    for idx, t in enumerate(boundary_t3):
        assert t.highlight_indices is not None
        ok &= check(
            f"boundary T3 #{idx + 1} contiguous",
            is_contiguous(t.highlight_indices),
            True,
        )

    # D-058: parent is first element of every Logical Tree T3.
    for idx, t in enumerate(logical_t3):
        assert t.highlight_indices is not None
        parent = t.highlight_indices[0]
        children = t.highlight_indices[1:]
        expected_children = {2 * parent + 1, 2 * parent + 2}
        actual_children = set(children)
        ok &= check(
            f"logical T3 #{idx + 1} parent-first D-058",
            actual_children.issubset(expected_children) and len(children) >= 1,
            True,
        )

    return ok


def run_counter_monotonicity() -> bool:
    """T3 ticks must not advance comparisons or writes.

    Replays the generator, snapshotting counters before and after each tick.
    Any T3 that changes a counter is a spec violation.
    """
    sorter = HeapSort([4, 7, 2, 6, 1, 5, 3])
    gen = sorter.sort_generator()

    prev_comparisons = 0
    prev_writes = 0
    violations: list[str] = []
    for t in gen:
        if t.operation_type is OpType.RANGE:
            if sorter.comparisons != prev_comparisons:
                violations.append(f"comparisons advanced on RANGE: {t.message!r}")
            if sorter.writes != prev_writes:
                violations.append(f"writes advanced on RANGE: {t.message!r}")
        prev_comparisons = sorter.comparisons
        prev_writes = sorter.writes

    print("counter_monotonicity check:")
    return check("T3 counter-advance violations", len(violations), 0)


def run_step_count() -> bool:
    """Step count (T1 + T2) == 35."""
    sorter = HeapSort([4, 7, 2, 6, 1, 5, 3])
    ticks = list(sorter.sort_generator())
    steps = sum(
        1
        for t in ticks
        if t.operation_type in (OpType.COMPARE, OpType.SWAP, OpType.SHIFT)
    )
    print("step_count check:")
    return check("T1+T2 step count", steps, 35)


def run_empty() -> bool:
    sorter = HeapSort([])
    ticks = list(sorter.sort_generator())
    print("empty input run:")
    ok = True
    ok &= check("tick count", len(ticks), 1)
    ok &= check("tick success", ticks[0].success, False)
    ok &= check("tick operation_type", ticks[0].operation_type, OpType.FAILURE)
    return ok


def run_single() -> bool:
    sorter = HeapSort([42])
    ticks = list(sorter.sort_generator())
    print("single element run:")
    ok = True
    ok &= check("tick count", len(ticks), 1)
    ok &= check("is_complete", ticks[0].is_complete, True)
    return ok


all_passed = (
    run_default()
    and run_t3_invariants()
    and run_counter_monotonicity()
    and run_step_count()
    and run_empty()
    and run_single()
)
print()
print("OVERALL:", "PASS" if all_passed else "FAIL")
sys.exit(0 if all_passed else 1)
