"""Smoke test for BubbleSort generator.

Usage: uv run python scripts/smoke_bubble.py

Exit criteria:
  - comparisons == 20
  - writes == 26
  - final tick is_complete == True
  - empty input yields exactly one FAILURE tick
"""

import sys

sys.path.insert(0, "src")

from visualizer.models.bubble import BubbleSort
from visualizer.models.contracts import OpType


def check(label: str, actual: object, expected: object) -> bool:
    ok = actual == expected
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {label}: expected {expected!r}, got {actual!r}")
    return ok


def run_default() -> bool:
    default = [4, 7, 2, 6, 1, 5, 3]
    sorter = BubbleSort(default)
    ticks = list(sorter.sort_generator())
    last = ticks[-1]
    print("default_7 run:")
    ok = True
    ok &= check("comparisons", sorter.comparisons, 20)
    ok &= check("writes", sorter.writes, 26)
    ok &= check("final tick is_complete", last.is_complete, True)
    ok &= check("final tick success", last.success, True)
    ok &= check("final tick operation_type", last.operation_type, OpType.TERMINAL)
    return ok


def run_empty() -> bool:
    sorter = BubbleSort([])
    ticks = list(sorter.sort_generator())
    print("empty input run:")
    ok = True
    ok &= check("tick count", len(ticks), 1)
    ok &= check("tick success", ticks[0].success, False)
    ok &= check("tick operation_type", ticks[0].operation_type, OpType.FAILURE)
    return ok


def run_single() -> bool:
    sorter = BubbleSort([42])
    ticks = list(sorter.sort_generator())
    print("single element run:")
    ok = True
    ok &= check("tick count", len(ticks), 1)
    ok &= check("is_complete", ticks[0].is_complete, True)
    return ok


all_passed = run_default() and run_empty() and run_single()
print()
print("OVERALL:", "PASS" if all_passed else "FAIL")
sys.exit(0 if all_passed else 1)
