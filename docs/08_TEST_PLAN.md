# 08 TEST PLAN - QA Strategy and Execution Matrix

Scope: Implementation-facing QA plan for Sorting Algorithm Visualizer v1 (Pygame Sprite Engine).
Primary objective: Prevent correctness drift, ensure operation-weighted timers are accurate, and validate smooth Pygame interpolation physics.

## 1) Quality Risks and Priorities

### P0 (Highest)

- Algorithm outputs incorrect final order.
- Selection Sort terminal near-sorted bug reappears.
- **Heap Sort phase violation:** Build Max-Heap phase completes incorrectly, causing extraction phase to produce invalid sort order.
- **Independent Timer Desync:** A panel's elapsed time calculates incorrectly based on its operation costs.
- **Physics Derailment:** Sprites calculate incorrect `(x, y)` target coordinates or fail to reach their exact destinations due to float-to-integer rounding drift.
- **Counter inaccuracy:** Comparisons or writes counters do not match expected values for deterministic input, misleading learners about algorithm behavior.
- **Insertion Sort tick sequence violation:** Compare and shift ticks emitted in wrong order, or missing terminating comparison, causing incorrect animation sequence.
- **Headless init failure:** Pygame subsystem initialization crashes in CI or in a WSL shell without WSLg due to missing `SDL_VIDEODRIVER=dummy`.

### P1

- Controller processes queues unevenly, causing unintended blocking across active algorithms.
- Failure in one algorithm halts the entire application.
- Heap Sort T3 range emphasis ticks emitted during wrong phase (build instead of extraction).
- T3 range emphasis ticks incorrectly incrementing the step counter.
- Insertion Sort key-selection tick incorrectly incrementing the comparisons counter.
- Panel state machine enters an invalid or unreachable state during pause/resume/restart transitions.

## 2) Test Levels

- **Unit tests (`tests/unit/`):** Model algorithms, data contract invariants, counter accuracy, easing math, and pure helper functions. No Pygame subsystem dependency required for model tests. Easing tests import `views/easing.py` which must be a pure-math module with no Pygame imports.
- **Integration tests (`tests/integration/`):** Controller queue processing, independent timer accumulation, step counter logic (T3 exclusion), panel state machine transitions, pause/resume interpolation, and algorithm lifecycle. These require the headless Pygame session fixture.
- **Manual exploratory:** Fluidity of Pygame motion, arc pathing clarity, heap boundary highlight visibility, insertion sort lift/shift/drop sequence, and runtime interaction (Pause/Step behavior).

## 3) Test Data Strategy

- Required fixtures (defined in `tests/conftest.py`):
  - `default_7`: `[4, 7, 2, 6, 1, 5, 3]` — the application default array. Used for counter accuracy tests and primary correctness checks.
  - `reverse_7`: `[7, 6, 5, 4, 3, 2, 1]` — worst-case for Bubble/Insertion Sort. Used for edge-case testing (note: this is a valid max-heap, so Heap Sort Phase 1 has no swaps).
  - `sorted_7`: `[1, 2, 3, 4, 5, 6, 7]` — best-case for Bubble/Insertion Sort. Used for terminating comparison tests.
  - `duplicates_7`: `[3, 1, 3, 2, 1, 2, 3]` — duplicate stability tests.
  - `single_1`: `[1]` — minimal non-empty input.
  - `empty_0`: `[]` — failure tick contract.
- Deterministic seeded random arrays for repeatability.

## 4) Test Infrastructure

### 4.1 Directory Layout

```text
tests/
├── conftest.py           # Shared fixtures and headless Pygame session
├── unit/
│   ├── conftest.py       # Unit-specific fixtures (if needed)
│   ├── test_bubble.py
│   ├── test_selection.py
│   ├── test_insertion.py
│   ├── test_heap.py
│   ├── test_contracts.py
│   └── test_easing.py
└── integration/
    ├── conftest.py       # Integration-specific fixtures (if needed)
    ├── test_controller.py
    ├── test_panel_state.py
    └── test_timer.py
```

### 4.2 conftest.py Specification (Headless Pygame Session)

The root `tests/conftest.py` must enforce headless mode and manage Pygame lifecycle:

```python
import os
import pytest

# CRITICAL: Set before any Pygame import anywhere in the test suite.
# This must be at module level, not inside a fixture, because Pygame
# may be imported at collection time by test modules.
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame  # noqa: E402 — must follow env var setup


@pytest.fixture(scope="session", autouse=True)
def _pygame_session():
    """Initialize Pygame once for the entire test session, then quit."""
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def default_7():
    return [4, 7, 2, 6, 1, 5, 3]


@pytest.fixture
def reverse_7():
    return [7, 6, 5, 4, 3, 2, 1]


@pytest.fixture
def sorted_7():
    return [1, 2, 3, 4, 5, 6, 7]


@pytest.fixture
def duplicates_7():
    return [3, 1, 3, 2, 1, 2, 3]


@pytest.fixture
def single_1():
    return [1]


@pytest.fixture
def empty_0():
    return []
```

Key rules:

- `SDL_VIDEODRIVER=dummy` and `SDL_AUDIODRIVER=dummy` are set at **module level** before any `import pygame`. This guarantees headless mode even if Pygame is imported during test collection.
- `pygame.init()` is called once per session. This initializes the font subsystem, which `NumberSprite` tests require for surface creation.
- `pygame.quit()` runs at session teardown.
- Individual test functions must not call `pygame.init()` or `pygame.quit()`.
- Data fixtures return fresh list copies (Python default for list literals) to prevent cross-test mutation.

### 4.3 Pytest Markers

Register custom markers in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = [
    "unit: Pure model/math tests — no Pygame subsystem needed beyond session init",
    "integration: Controller/View interaction tests — require headless Pygame session",
    "slow: Tests with large fixtures or exhaustive generator consumption",
]
```

Usage: `uv run pytest -m unit` for fast feedback; `uv run pytest -m integration` for controller tests; `uv run pytest` for the full suite.

### 4.4 Controller Testability Contract

The Controller (`controllers/orchestrator.py`) must be testable without a live Pygame display window. To achieve this:

- **Model layer (algorithms):** Fully testable in isolation. Algorithm classes accept `list[int]` and yield `SortResult`. No Pygame dependency.
- **Easing module (`views/easing.py`):** Must be a **pure-math module** with no Pygame imports. This allows TC-A5 easing tests to run without display initialization.
- **Controller queue logic:** The Controller's timing logic (subtracting `dt`, requesting next `SortResult`, accumulating `elapsed_time_ms`) must be extractable into methods that accept `dt` and mock generators — no dependency on `pygame.display` or `pygame.Surface`.
- **Sprite coordinate math:** `NumberSprite` requires `pygame.font` (initialized by the session fixture). With `SDL_VIDEODRIVER=dummy`, font rendering produces valid surfaces with correct dimensions. Coordinate and easing math can be tested against these surfaces.
- **View rendering:** Not tested automatically. The `render()` path that blits to a `pygame.display` surface is excluded from automated tests and covered by manual exploratory testing only.

If the Controller implementation couples queue logic with rendering, integration tests must inject a **mock View** that implements the render interface as a no-op. The Controller must not call `pygame.display.set_mode()` or `pygame.display.flip()` internally — those belong to `main.py` and the View layer.

### 4.5 Timer Arithmetic Precision

All simulated elapsed time accumulation must use **integer milliseconds** internally (not floats). This eliminates floating-point drift in timer assertions.

- Operation costs are defined as integer constants: `T1 = 150`, `T2 = 400`, `T3 = 200` (milliseconds).
- `elapsed_time_ms` is an `int` accumulator, incremented by the exact operation cost upon tick completion.
- Timer assertions use **exact integer equality** (e.g., `assert elapsed == 700`), not approximate float comparisons.
- The View layer converts to display format (`elapsed_time_ms / 1000` → `f"{seconds:.2f}s"`) only at render time.

## 5) Core Test Cases (Automated)

### TC-A1 Final Sortedness (All Algorithms)

- Arrange: instantiate algorithm with non-empty fixture.
- Act: consume generator until terminal tick.
- Assert: final `array_state` sorted ascending.
- Marker: `@pytest.mark.unit`

### TC-A2 Final Completion Tick Contract

- Assert exactly one terminal completion tick.
- Assert completion tick has `success=True`, `is_complete=True`, and full-array highlight.
- Marker: `@pytest.mark.unit`

### TC-A3 Empty Input Contract (`empty_0` fixture)

- Arrange: instantiate algorithm with `empty_0`.
- Act: consume generator to exhaustion.
- Assert: exactly one failure tick yielded (`success=False`, `is_complete=False`).
- Marker: `@pytest.mark.unit`

### TC-A4 Controller Independent Queues & Timers

- Mock the algorithm generators to yield known operation types (e.g., 2 compares, 1 swap).
- Simulate the Controller's `update(dt)` loop by feeding deterministic `dt` values.
- Assert the Controller accurately calculates the total simulated elapsed time using integer millisecond arithmetic: `(2 * 150) + (1 * 400) = 700`.
- Assert each panel's `elapsed_time_ms` is exact (integer equality, no tolerance).
- Marker: `@pytest.mark.integration`

### TC-A5 Sprite Physics and Math

- Unit test the easing functions (e.g., `ease_in_out_quad`) from `views/easing.py`.
- Assert that given a start of `x=0`, a target of `x=100`, and a time ratio `t=0.5`, the internal `x` reflects the mathematical midpoint of the curve (50.0).
- Assert that acceleration/deceleration at `t=0.2` and `t=0.8` are non-linear compared to standard progression.
- Assert that upon `t >= 1.0`, the exact `x` snaps precisely to the target to eliminate drift.
- Marker: `@pytest.mark.unit`

### TC-A6 Controller Fairness

- Ensure all active generators receive execution opportunities.
- No algorithm may stall while others continue progressing.
- Simulate 4 concurrent generators with differing tick counts and operation mixes.
- Feed uniform `dt` increments and assert all generators reach completion (no starvation).
- Marker: `@pytest.mark.integration`

### TC-A7 Heap Sort Phase Contract

- Consume Heap Sort generator for `default_7` fixture.
- Assert at least one T3 Range Emphasis Tick is emitted.
- Assert T3 ticks only appear after the build-max-heap phase concludes.
- Assert Phase 1 produces at least one T2 swap tick (verifying the input has heap violations).
- Assert each T3 tick's `highlight_indices` is `tuple(range(0, k))` for strictly decreasing `k` values across successive T3 ticks.
- Assert sorted region grows by exactly one element between each pair of consecutive T3 ticks.
- Marker: `@pytest.mark.unit`

### TC-A8 Heap Sort Sift-Down Correctness

- Unit-test the sift-down function in isolation with known max-heap violations.
- Assert that after sift-down, the subtree rooted at the target index satisfies the max-heap property.
- Assert that only T1/T2 ticks are emitted by sift-down (no T3 ticks inside sift-down).
- Marker: `@pytest.mark.unit`

### TC-A9 Insertion Sort Tick Sequence

- Consume Insertion Sort generator for `default_7` fixture.
- For each outer pass `i` (from 1 to 6):
  - Assert the first tick is a T1 (COMPARE) key-selection tick with `highlight_indices == (i,)`.
  - Assert subsequent ticks follow the pattern: T1 compare on `(j, j+1)`, then T2 shift on `(j, j+1)`, for each shifted element.
  - For passes where `j >= 0` at loop exit (key does not go to position 0), assert a terminating T1 compare tick is emitted.
  - Assert the final tick of the pass is a T2 (SHIFT) placement tick on a single index.
- For `default_7`, passes i=1 (key=7) and i=3 (key=6) should emit terminating comparison ticks (loop exits by condition). Passes i=2 (key=2) and i=4 (key=1) should not (loop exits by `j < 0`).
- Marker: `@pytest.mark.unit`

### TC-A10 Counter Accuracy (All Algorithms)

- Consume each algorithm's generator for `default_7` fixture.
- Assert exact counter values:
  - **Bubble Sort:** `comparisons == 20`, `writes == 26`.
  - **Selection Sort:** `comparisons == 21`, `writes == 10`.
  - **Insertion Sort:** `comparisons == 17`, `writes == 19`.
  - **Heap Sort:** `comparisons == 20`, `writes == 30`.
- Marker: `@pytest.mark.unit`

### TC-A11 Key-Selection Does Not Increment Comparisons

- Consume Insertion Sort generator for any non-empty fixture.
- Count the number of T1 ticks where `highlight_indices` has exactly one index (key-selection ticks).
- Assert `algorithm.comparisons` equals total T1 tick count minus the key-selection tick count.
- Marker: `@pytest.mark.unit`

### TC-A12 Swap Writes Count

- Consume Bubble Sort generator for `default_7` fixture.
- Count the number of T2 (SWAP) ticks emitted.
- Assert `algorithm.writes == swap_tick_count * 2`.
- Marker: `@pytest.mark.unit`

### TC-A13 T3 Step Counter Exclusion

- Consume Heap Sort generator for `default_7` fixture.
- Count all ticks where `success=True`, `is_complete=False`, `operation_type != RANGE`.
- Assert this count equals 35 (the expected step count).
- Count all T3 (RANGE) ticks separately and assert count equals 6.
- Marker: `@pytest.mark.unit`

### TC-A14 Insertion Sort Terminating Comparison

- Consume Insertion Sort generator for `sorted_7` fixture (already sorted: `[1, 2, 3, 4, 5, 6, 7]`).
- For each pass `i`, the while-loop condition `arr[j] > key` fails immediately on the first check.
- Assert that each pass emits: T1 key-selection, T1 terminating comparison (showing `arr[i-1] <= key`), T2 placement on `(i,)`.
- Assert no shift ticks are emitted (no elements need to move).
- Marker: `@pytest.mark.unit`

### TC-A15 Panel State Machine Transitions (Happy Path)

- Instantiate a Controller with one mock algorithm generator that yields 2 ticks then completes.
- Assert panel starts in `idle_paused`.
- Simulate Play → assert transition to `waiting_for_next_tick`.
- Feed `dt` until first tick consumed → assert `animating_operation`.
- Feed `dt` until animation completes → assert `waiting_for_next_tick`.
- Continue until completion tick → assert `completed`.
- Assert `elapsed_time_ms` is frozen at the exact accumulated value.
- Marker: `@pytest.mark.integration`

### TC-A16 Panel State Machine Failure Isolation

- Instantiate a Controller with two mock generators: one yields a failure tick immediately, the other yields normal ticks.
- Feed `dt` until the failure tick is consumed.
- Assert the failed panel enters `failed` state and its timer stops.
- Assert the other panel continues progressing through `animating_operation` / `waiting_for_next_tick` states.
- Marker: `@pytest.mark.integration`

### TC-A17 Pause Freezes Interpolation State

- Instantiate a Controller with a mock generator yielding one swap tick.
- Start Play, feed `dt = 200` (halfway through 400ms swap).
- Trigger Pause.
- Assert `current_operation_remaining_ms` is preserved (approximately 200ms remaining).
- Feed additional `dt` values while paused → assert `elapsed_time_ms` and sprite positions do not change.
- Resume Play and feed remaining `dt` → assert operation completes and next tick is fetched.
- Marker: `@pytest.mark.integration`

### TC-A18 Restart Resets All State

- Instantiate a Controller, start Play, feed `dt` to advance through several ticks.
- Trigger Restart.
- Assert all panels return to `idle_paused`.
- Assert all `elapsed_time_ms` values are `0`.
- Assert all counters (steps, comparisons, writes) are `0`.
- Assert generators are re-created from the original initial array.
- Marker: `@pytest.mark.integration`

## 6) Manual Test Pass (Release Gate)

- Verify startup paused state and identical initial arrays `[4, 7, 2, 6, 1, 5, 3]`.
- Verify play/pause/step/restart controls.
- **Observe the Race:** Ensure faster algorithms visually finish earlier, freeze their panels, and halt their UI timers.
- **Observe the Physics:** Verify elements slide smoothly, use vertical arcs when swapping, and respect the Option B accent color tinting.
- **Observe Heap Sort Phases:** Verify Phase 1 shows actual swaps (heap being built). Verify the orange heap boundary highlight pulses during extraction and visibly shrinks one slot each step.
- **Observe Insertion Sort Lift/Drop:** Verify the key element lifts above the array, stays elevated during comparisons and shifts, and drops smoothly into position.
- **Verify Counters:** After completion, cross-check displayed comparisons and writes values against expected values for `[4, 7, 2, 6, 1, 5, 3]`.

## 7) Tooling and Execution

- Unit/integration automation: `pytest` with headless Pygame session fixture.
- Selective execution: `uv run pytest -m unit` (fast, no Controller), `uv run pytest -m integration` (Controller/View layer).
- Full suite: `SDL_VIDEODRIVER=dummy uv run pytest -q` (environment variable is also set in `conftest.py` as a safety net).
- CI pipeline: see `docs/11_CI.md` for the GitHub Actions configuration with `SDL_VIDEODRIVER=dummy`.

## 8) Testability Constraints

### What CAN be tested headlessly

- All algorithm generators (model layer) — fully deterministic, no Pygame dependency.
- Easing math (`views/easing.py`) — pure functions, no Pygame imports.
- Controller queue timing — integer `dt` simulation with mock generators.
- Panel state machine transitions — state tracking with mock tick sequences.
- `NumberSprite` coordinate math — requires `pygame.font` (provided by session fixture with dummy driver).
- Counter accuracy — direct attribute reads on algorithm instances after generator consumption.

### What CANNOT be tested headlessly

- Pixel-accurate rendering output (blit positions, color values on screen).
- Visual arc motion smoothness and z-ordering correctness.
- Highlight color application on actual surfaces.
- Control bar click target areas.
- Frame rate stability under load.

These are covered by the manual test pass (Section 6).
