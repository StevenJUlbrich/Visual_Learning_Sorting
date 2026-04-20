"""Unit tests for BubbleSort generator — TC-A1, TC-A2, TC-A3, TC-A10, TC-A12."""

import pytest

from visualizer.models.bubble import BubbleSort
from visualizer.models.contracts import OpType


@pytest.mark.unit
def test_tc_a1_final_sortedness(default_7: list[int]) -> None:
    sorter = BubbleSort(default_7)
    ticks = list(sorter.sort_generator())
    terminal = next(t for t in ticks if t.operation_type is OpType.TERMINAL)
    assert terminal.array_state == [1, 2, 3, 4, 5, 6, 7]


@pytest.mark.unit
def test_tc_a2_completion_tick(default_7: list[int]) -> None:
    sorter = BubbleSort(default_7)
    ticks = list(sorter.sort_generator())
    terminals = [t for t in ticks if t.operation_type is OpType.TERMINAL]
    assert len(terminals) == 1
    t = terminals[0]
    assert t.success is True
    assert t.is_complete is True
    assert t.highlight_indices == tuple(range(7))


@pytest.mark.unit
def test_tc_a3_empty_input(empty_0: list[int]) -> None:
    sorter = BubbleSort(empty_0)
    ticks = list(sorter.sort_generator())
    assert len(ticks) == 1
    assert ticks[0].success is False
    assert ticks[0].operation_type is OpType.FAILURE


@pytest.mark.unit
def test_tc_a10_counter_accuracy(default_7: list[int]) -> None:
    sorter = BubbleSort(default_7)
    list(sorter.sort_generator())
    assert sorter.comparisons == 20
    assert sorter.writes == 26


@pytest.mark.unit
def test_tc_a12_swap_writes(default_7: list[int]) -> None:
    sorter = BubbleSort(default_7)
    ticks = list(sorter.sort_generator())
    swap_count = sum(1 for t in ticks if t.operation_type is OpType.SWAP)
    assert sorter.writes == swap_count * 2


@pytest.mark.unit
def test_single_element_terminal_only(single_1: list[int]) -> None:
    sorter = BubbleSort(single_1)
    ticks = list(sorter.sort_generator())
    assert len(ticks) == 1
    assert ticks[0].operation_type is OpType.TERMINAL
    assert ticks[0].is_complete is True
    assert not any(t.operation_type in (OpType.COMPARE, OpType.SWAP) for t in ticks)
