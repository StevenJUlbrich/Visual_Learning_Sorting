"""Smoke test for InsertionSort generator.

Usage: uv run python scripts/smoke_insertion.py

Exit criteria:
  - comparisons == 17
  - writes == 19
  - final tick is_complete == True
  - empty input yields exactly one FAILURE tick

Bonus checks:
  - Pass-by-pass counter segmentation matches pseudocode §3 truth table
  - No duplicate indices in any 2-element highlight_indices
  - Single-element highlights on key-selection and placement
"""

import sys

sys.path.insert(0, "src")

from visualizer.models.contracts import OpType, SortResult
from visualizer.models.insertion import InsertionSort


def check(label: str, actual: object, expected: object) -> bool:
    ok = actual == expected
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {label}: expected {expected!r}, got {actual!r}")
    return ok


def run_default() -> bool:
    sorter = InsertionSort([4, 7, 2, 6, 1, 5, 3])
    ticks = list(sorter.sort_generator())
    last = ticks[-1]
    print("default_7 run:")
    ok = True
    ok &= check("comparisons", sorter.comparisons, 17)
    ok &= check("writes", sorter.writes, 19)
    ok &= check("final tick is_complete", last.is_complete, True)
    ok &= check("final tick success", last.success, True)
    ok &= check("final tick operation_type", last.operation_type, OpType.TERMINAL)
    ok &= check(
        "final array sorted",
        last.array_state,
        [1, 2, 3, 4, 5, 6, 7],
    )
    return ok


def run_pass_segmentation() -> bool:
    """Verify per-pass counter breakdown matches pseudocode §3 truth table.

    Expected per-pass: (shift_compares, terminating?, shifts, placement)
        i=1 (key=7): 0, True,  0, 1
        i=2 (key=2): 2, False, 2, 1
        i=3 (key=6): 1, True,  1, 1
        i=4 (key=1): 4, False, 4, 1
        i=5 (key=5): 2, True,  2, 1
        i=6 (key=3): 4, True,  4, 1
    """
    sorter = InsertionSort([4, 7, 2, 6, 1, 5, 3])
    ticks = list(sorter.sort_generator())

    # Segment by key-selection: single-index highlight at (i,) for i >= 1
    # marks the start of a new pass.
    passes: list[list[SortResult]] = []
    current: list[SortResult] = []
    for t in ticks:
        if (
            t.operation_type == OpType.COMPARE
            and t.highlight_indices is not None
            and len(t.highlight_indices) == 1
            and t.highlight_indices[0] >= 1
            and t.message.startswith("Selecting key")
        ):
            if current:
                passes.append(current)
            current = [t]
        elif t.operation_type == OpType.TERMINAL:
            if current:
                passes.append(current)
        else:
            current.append(t)

    expected_passes = [
        # (shift_compares, shifts, placements, terminating)
        (0, 0, 1, True),
        (2, 2, 1, False),
        (1, 1, 1, True),
        (4, 4, 1, False),
        (2, 2, 1, True),
        (4, 4, 1, True),
    ]

    print("pass_segmentation check:")
    ok = check("pass count", len(passes), 6)
    if not ok:
        return False

    for idx, (pass_ticks, (exp_scmp, exp_sh, exp_pl, exp_term)) in enumerate(
        zip(passes, expected_passes, strict=True)
    ):
        # First tick is key-selection, skip it for counter math
        body = pass_ticks[1:]
        shift_ticks = [
            t
            for t in body
            if t.operation_type == OpType.SHIFT
            and t.highlight_indices is not None
            and len(t.highlight_indices) == 2
        ]
        placement_ticks = [
            t
            for t in body
            if t.operation_type == OpType.SHIFT
            and t.highlight_indices is not None
            and len(t.highlight_indices) == 1
        ]
        compare_ticks = [t for t in body if t.operation_type == OpType.COMPARE]

        has_terminating = len(compare_ticks) > len(shift_ticks)
        ok &= check(f"pass {idx + 1} shift_compares", len(shift_ticks), exp_scmp)
        ok &= check(f"pass {idx + 1} placements", len(placement_ticks), exp_pl)
        ok &= check(f"pass {idx + 1} terminating", has_terminating, exp_term)
    return ok


def run_highlight_invariants() -> bool:
    sorter = InsertionSort([4, 7, 2, 6, 1, 5, 3])
    ticks = list(sorter.sort_generator())
    dup_violations = [
        t
        for t in ticks
        if t.highlight_indices is not None
        and len(t.highlight_indices) == 2
        and t.highlight_indices[0] == t.highlight_indices[1]
    ]
    print("highlight_invariants check:")
    return check("no duplicate indices in 2-element highlights", len(dup_violations), 0)


def run_empty() -> bool:
    sorter = InsertionSort([])
    ticks = list(sorter.sort_generator())
    print("empty input run:")
    ok = True
    ok &= check("tick count", len(ticks), 1)
    ok &= check("tick success", ticks[0].success, False)
    ok &= check("tick operation_type", ticks[0].operation_type, OpType.FAILURE)
    return ok


def run_single() -> bool:
    sorter = InsertionSort([42])
    ticks = list(sorter.sort_generator())
    print("single element run:")
    ok = True
    ok &= check("tick count", len(ticks), 1)
    ok &= check("is_complete", ticks[0].is_complete, True)
    return ok


all_passed = (
    run_default()
    and run_pass_segmentation()
    and run_highlight_invariants()
    and run_empty()
    and run_single()
)
print()
print("OVERALL:", "PASS" if all_passed else "FAIL")
sys.exit(0 if all_passed else 1)
