# 03 DATA CONTRACTS - Canonical Source

This file is the single source of truth for algorithm/controller/view runtime contracts.

## SortResult (Definitive)

```python
from dataclasses import dataclass

@dataclass(slots=True)
class SortResult:
    success: bool
    message: str
    is_complete: bool = False
    array_state: list[int] | None = None
    highlight_indices: tuple[int, ...] | None = None
```

## Field Semantics
- `success`
  - `True`: normal algorithm progression or normal completion.
  - `False`: explicit algorithm/domain failure.
- `message`
  - Required for every yielded result.
  - Human-readable action/error text for debugging and optional UI line.
- `is_complete`
  - `True` only on normal terminal state.
  - Must not be used with `success=False`.
- `array_state`
  - Required on successful non-terminal and terminal ticks.
  - Optional (`None`) on failure ticks.
  - Must be an immutable snapshot copy at yield time (`self.data.copy()`).
- `highlight_indices`
  - Optional tuple of indices to accent for current tick.
  - Empty/`None` means no accent.
  - If provided, all indices must be valid for `array_state` length.

## Valid State Combinations
- Progress tick: `success=True`, `is_complete=False`, `array_state!=None`.
- Completion tick: `success=True`, `is_complete=True`, `array_state!=None`.
- Failure tick: `success=False`, `is_complete=False`, `array_state` optional.

Invalid combinations are contract violations.

## Tick Taxonomy
- Compare tick: highlights compared indices.
- Swap tick: highlights swapped indices and new snapshot.
- Shift/placement tick: highlights moved/placed indices and new snapshot.
- Merge range tick: highlights active merge range (range tuple expanded to indices).
- Terminal completion tick: final sorted array snapshot.
- Failure tick: explicit error state with message.

## Step Counter Definition
A panel step increments on every received `SortResult` where:
- `success=True`
- `is_complete=False`

Completion and failure ticks do not increment step count.

## Generator Contract
Each algorithm generator must:
- Yield at every atomic operation.
- Yield exactly one terminal completion tick on success.
- Yield failure tick and stop on unrecoverable domain failure.
- Avoid `yield from` for recursive failure bubbling where explicit checking is required by design.

## BaseSortAlgorithm Interface

```python
from abc import ABC, abstractmethod
from collections.abc import Generator

class BaseSortAlgorithm(ABC):
    def __init__(self, data: list[int], name: str):
        self.name = name
        self.data = data.copy()
        self.size = len(self.data)

    @abstractmethod
    def sort_generator(self) -> Generator[SortResult, None, None]:
        ...
```
