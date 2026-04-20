"""Unit tests for InsertionSort generator — TC-A1, TC-A2, TC-A3, TC-A9, TC-A10, TC-A11, TC-A14."""

import pytest

from visualizer.models.contracts import OpType, SortResult
from visualizer.models.insertion import InsertionSort


def _segment_passes(ticks: list[SortResult]) -> list[list[SortResult]]:
    """Split tick stream into per-pass buckets, each starting with a key-selection tick."""
    passes: list[list[SortResult]] = []
    current: list[SortResult] = []
    for t in ticks:
        if (
            t.operation_type is OpType.COMPARE
            and t.highlight_indices is not None
            and len(t.highlight_indices) == 1
            and t.message.startswith("Selecting key")
        ):
            if current:
                passes.append(current)
            current = [t]
        elif t.operation_type is OpType.TERMINAL:
            if current:
                passes.append(current)
        else:
            current.append(t)
    return passes


@pytest.mark.unit
def test_tc_a1_final_sortedness(default_7: list[int]) -> None:
    sorter = InsertionSort(default_7)
    ticks = list(sorter.sort_generator())
    terminal = next(t for t in ticks if t.operation_type is OpType.TERMINAL)
    assert terminal.array_state == [1, 2, 3, 4, 5, 6, 7]


@pytest.mark.unit
def test_tc_a2_completion_tick(default_7: list[int]) -> None:
    sorter = InsertionSort(default_7)
    ticks = list(sorter.sort_generator())
    terminals = [t for t in ticks if t.operation_type is OpType.TERMINAL]
    assert len(terminals) == 1
    t = terminals[0]
    assert t.success is True
    assert t.is_complete is True
    assert t.highlight_indices == tuple(range(7))


@pytest.mark.unit
def test_tc_a3_empty_input(empty_0: list[int]) -> None:
    sorter = InsertionSort(empty_0)
    ticks = list(sorter.sort_generator())
    assert len(ticks) == 1
    assert ticks[0].success is False
    assert ticks[0].operation_type is OpType.FAILURE


@pytest.mark.unit
def test_tc_a10_counter_accuracy(default_7: list[int]) -> None:
    sorter = InsertionSort(default_7)
    list(sorter.sort_generator())
    assert sorter.comparisons == 17
    assert sorter.writes == 19


@pytest.mark.unit
def test_single_element_terminal_only(single_1: list[int]) -> None:
    sorter = InsertionSort(single_1)
    ticks = list(sorter.sort_generator())
    assert len(ticks) == 1
    assert ticks[0].operation_type is OpType.TERMINAL
    assert ticks[0].is_complete is True
    assert not any(t.operation_type in (OpType.COMPARE, OpType.SHIFT) for t in ticks)


@pytest.mark.unit
def test_tc_a9_per_pass_tick_sequence(default_7: list[int]) -> None:
    # Truth table from pseudocode §3: (shift_compares, terminating, shifts, placements)
    expected = [
        (0, True, 0, 1),  # i=1 key=7: no shifts, loop never enters, j=0 at exit
        (2, False, 2, 1),  # i=2 key=2: 2 shifts, j falls to -1
        (1, True, 1, 1),  # i=3 key=6: 1 shift, exits by arr[j]<=key
        (4, False, 4, 1),  # i=4 key=1: 4 shifts, j falls to -1
        (2, True, 2, 1),  # i=5 key=5: 2 shifts, exits by arr[j]<=key
        (4, True, 4, 1),  # i=6 key=3: 4 shifts, exits by arr[j]<=key
    ]

    sorter = InsertionSort(default_7)
    ticks = list(sorter.sort_generator())
    passes = _segment_passes(ticks)
    assert len(passes) == 6

    for idx, (pass_ticks, (exp_sc, exp_term, exp_sh, exp_pl)) in enumerate(
        zip(passes, expected, strict=True)
    ):
        label = f"pass {idx + 1}"

        # First tick: key-selection T1 with single-index highlight.
        first = pass_ticks[0]
        assert first.operation_type is OpType.COMPARE, (
            f"{label}: first tick must be T1 key-selection"
        )
        assert first.highlight_indices is not None
        assert len(first.highlight_indices) == 1, (
            f"{label}: key-selection must have single-index highlight"
        )

        body = pass_ticks[1:]
        shift_ticks = [
            t
            for t in body
            if t.operation_type is OpType.SHIFT
            and t.highlight_indices is not None
            and len(t.highlight_indices) == 2
        ]
        placement_ticks = [
            t
            for t in body
            if t.operation_type is OpType.SHIFT
            and t.highlight_indices is not None
            and len(t.highlight_indices) == 1
        ]
        compare_ticks = [t for t in body if t.operation_type is OpType.COMPARE]
        has_terminating = len(compare_ticks) > len(shift_ticks)
        shift_compare_count = len(compare_ticks) - (1 if has_terminating else 0)

        assert shift_compare_count == exp_sc, f"{label}: shift compare count"
        assert len(shift_ticks) == exp_sh, f"{label}: shift count"
        assert len(placement_ticks) == exp_pl, f"{label}: placement count"
        assert has_terminating == exp_term, f"{label}: terminating compare"

        # Last tick of each pass is T2 SHIFT placement on a single index.
        last = pass_ticks[-1]
        assert last.operation_type is OpType.SHIFT, f"{label}: last tick must be T2 placement"
        assert last.highlight_indices is not None
        assert len(last.highlight_indices) == 1, (
            f"{label}: placement must have single-index highlight"
        )


@pytest.mark.unit
def test_tc_a11_key_selection_no_comparisons(default_7: list[int]) -> None:
    sorter = InsertionSort(default_7)
    ticks = list(sorter.sort_generator())
    all_compare_ticks = [t for t in ticks if t.operation_type is OpType.COMPARE]
    key_selection_ticks = [
        t
        for t in all_compare_ticks
        if t.highlight_indices is not None and len(t.highlight_indices) == 1
    ]
    assert sorter.comparisons == len(all_compare_ticks) - len(key_selection_ticks)


@pytest.mark.unit
def test_tc_a14_terminating_compare_sorted(sorted_7: list[int]) -> None:
    sorter = InsertionSort(sorted_7)
    ticks = list(sorter.sort_generator())

    # No element needs to move on a sorted input — no shift ticks.
    shift_ticks = [
        t
        for t in ticks
        if t.operation_type is OpType.SHIFT
        and t.highlight_indices is not None
        and len(t.highlight_indices) == 2
    ]
    assert len(shift_ticks) == 0

    # One placement write per pass (6 passes for n=7), zero shift writes.
    assert sorter.writes == 6
    # One terminating compare per pass (key-selection not counted).
    assert sorter.comparisons == 6

    # Per-pass: key-selection T1, terminating T1, placement T2 — nothing else.
    passes = _segment_passes(ticks)
    assert len(passes) == 6
    for i, pass_ticks in enumerate(passes):
        body = pass_ticks[1:]
        body_shifts = [
            t
            for t in body
            if t.operation_type is OpType.SHIFT
            and t.highlight_indices is not None
            and len(t.highlight_indices) == 2
        ]
        body_placements = [
            t
            for t in body
            if t.operation_type is OpType.SHIFT
            and t.highlight_indices is not None
            and len(t.highlight_indices) == 1
        ]
        body_compares = [t for t in body if t.operation_type is OpType.COMPARE]
        assert len(body_shifts) == 0, f"pass {i + 1}: no shifts on sorted input"
        assert len(body_placements) == 1, f"pass {i + 1}: exactly one placement"
        assert len(body_compares) == 1, f"pass {i + 1}: exactly one terminating compare"
