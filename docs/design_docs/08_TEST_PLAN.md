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
- **Tree layout geometry error:** Heap Sort tree nodes positioned incorrectly, overlapping, or edges pointing to wrong children. (Mitigated by D-079: minimum panel width is now 489px.)
- **Pointer asset desync:** Selection Sort `i`/`j`/`min` arrows not tracking the correct indices during scan or after swap.
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
- Assert T3 ticks are emitted in both phases:
  - **Phase 1 (Build Max-Heap):** Assert Logical Tree Highlight T3 ticks (non-contiguous `highlight_indices`) are emitted during sift-down. Assert Phase 1 produces at least one T2 swap tick (verifying the input has heap violations).
  - **Phase 2 (Extraction):** Assert Boundary Emphasis T3 ticks (contiguous `highlight_indices` matching `tuple(range(0, k))`) are emitted at the start of each extraction step, with strictly decreasing `k` values. Assert Logical Tree Highlight T3 ticks are emitted during post-extraction sift-down repairs.
- Assert sorted region grows by exactly one element between each pair of consecutive boundary T3 ticks.
- Marker: `@pytest.mark.unit`

### TC-A8 Heap Sort Sift-Down Correctness

- Unit-test the sift-down function in isolation with known max-heap violations.
- Assert that after sift-down, the subtree rooted at the target index satisfies the max-heap property.
- Assert that sift-down emits T3 (Logical Tree Highlight), T1 (Compare), and T2 (Swap) ticks in the mandatory sequence defined by the sift-down tick contract (see TC-A19).
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

### TC-A19 Heap Sort Sift-Down Tick Sequence Contract (Visual Trace)

**Motivation:** An implementation can pass sortedness and counter tests while silently violating the visual learning contract — e.g., omitting the T3 Logical Tree Highlight before comparisons, or emitting T1 before T3 at a sift-down level. Because the tick sequence *is* the visual experience, a log-based trace of `OpType` values is the most effective self-verification mechanism.

**Procedure:**

- Instantiate HeapSort with `default_7` fixture (`[4, 7, 2, 6, 1, 5, 3]`).
- Consume the full generator, collecting every tick's `op_type` into an ordered trace list.
- Identify sift-down regions in the trace: contiguous subsequences bounded by `RANGE` (T3 Logical Tree Highlight) ticks that are **not** boundary emphasis ticks. Boundary T3 ticks are distinguished by having contiguous `highlight_indices` (`tuple(range(0, k))`); Logical Tree T3 ticks have non-contiguous `highlight_indices`.
- For **each** sift-down level (each Logical Tree T3 tick), assert the following sequence contract:

```text
RANGE (T3)  →  COMPARE (T1) [1 or 2]  →  WRITE (T2) [0 or 1]
```

Specifically:

1. The sift-down level **must** begin with exactly one `OpType.RANGE` tick whose `highlight_indices` is non-contiguous (the parent-child triangle).
2. The `RANGE` tick **must** be immediately followed by 1 or 2 `OpType.COMPARE` ticks (left child comparison, optionally right child comparison).
3. No `COMPARE` tick may appear at a sift-down level without a preceding `RANGE` tick at that same level.
4. If a swap occurs, exactly one `OpType.WRITE` tick follows the comparisons. If no swap occurs (heap property satisfied), no `WRITE` tick is emitted and the sift-down terminates.
5. If a `WRITE` tick is emitted, the next tick must be either another `RANGE` tick (sift-down continues at the next tree level) or a non-sift-down tick (sift-down complete).

**Assertion examples for `default_7`:**

- Phase 1 (Build Max-Heap): Assert that every sift-down invocation begins each level with a Logical Tree T3 tick. For the input `[4, 7, 2, 6, 1, 5, 3]`, Phase 1 processes nodes at indices 2, 1, 0 and produces 3 swap events — each preceded by the T3 → T1 sequence.
- Phase 2 (Extraction): Assert that after each boundary T3 tick and extraction T2 swap, the subsequent sift-down repair follows the same T3 → T1 → T2 contract at every level, with no T1 tick appearing before its level's T3 tick.

**Anti-patterns this test catches:**

- T3 tick omitted entirely (comparisons happen without tree context).
- T3 tick emitted after T1 (learner sees comparison before understanding which branch is active).
- Multiple T3 ticks emitted at the same sift-down level (visual stutter).
- T1 compare tick emitted for the right child without a preceding T3 tick at that level.

**Implementation guidance:** The test should build a structured trace, not just a flat `OpType` list. A helper function can segment the trace into sift-down levels by detecting Logical Tree T3 ticks (non-contiguous `highlight_indices`) and validating each segment independently. Example:

```python
def extract_sift_down_levels(ticks):
    """Group ticks into sift-down levels, each starting with a Logical Tree T3."""
    levels = []
    current_level = []
    for tick in ticks:
        if tick.op_type == OpType.RANGE and not _is_contiguous(tick.highlight_indices):
            if current_level:
                levels.append(current_level)
            current_level = [tick]
        elif current_level:  # Only collect if inside a sift-down level
            current_level.append(tick)
            if tick.op_type == OpType.WRITE:
                levels.append(current_level)
                current_level = []
    if current_level:
        levels.append(current_level)
    return levels


def assert_sift_down_level_contract(level_ticks):
    """Assert T3 -> T1{1,2} -> T2{0,1} ordering for a single sift-down level."""
    assert level_ticks[0].op_type == OpType.RANGE, "Level must start with T3"
    assert not _is_contiguous(level_ticks[0].highlight_indices), "Must be tree highlight, not boundary"

    compare_count = 0
    write_count = 0
    for tick in level_ticks[1:]:
        if tick.op_type == OpType.COMPARE:
            assert write_count == 0, "T1 compare must not follow T2 write within same level"
            compare_count += 1
        elif tick.op_type == OpType.WRITE:
            assert compare_count >= 1, "T2 write must follow at least one T1 compare"
            write_count += 1

    assert 1 <= compare_count <= 2, f"Expected 1-2 compares, got {compare_count}"
    assert write_count <= 1, f"Expected 0-1 writes, got {write_count}"
```

- Marker: `@pytest.mark.unit`

### TC-A20 Tree Layout Node Positioning

- Instantiate the tree layout geometry calculator with Desktop panel dimensions (611×296).
- For heap_size = 7, assert all 7 node positions are within panel bounds.
- Assert root (index 0) is horizontally centered.
- Assert level 1 nodes are horizontally symmetric around center.
- Assert level 2 nodes are horizontally symmetric and do not overlap with level 1 nodes.
- Assert no two nodes at the same level overlap (minimum gap = node diameter).
- Repeat with Tablet panel dimensions (489×327) to verify both presets.
- Marker: `@pytest.mark.unit`

### TC-A21 Tree Layout Edge Connectivity

- For heap_size = 7, compute all parent-child edges.
- Assert edge from index 0 connects to index 1 and index 2.
- Assert edge from index 1 connects to index 3 and index 4.
- Assert edge from index 2 connects to index 5 and index 6.
- Assert no edge exists for leaf nodes (3, 4, 5, 6 as children).
- Marker: `@pytest.mark.unit`

### TC-A22 Tree Layout Shrinking

- For decreasing heap_size values (7, 6, 5, 4, 3, 2, 1), compute tree positions.
- Assert the number of rendered tree nodes equals heap_size.
- Assert edges only connect to nodes within the current heap_size.
- Assert nodes at indices >= heap_size are not positioned in the tree.
- Marker: `@pytest.mark.unit`

### TC-A23 Selection Sort Pointer Tracking

- Consume the Selection Sort generator for `default_7` fixture.
- For each T1 tick, assert:
  - The `j` pointer index matches the scan cursor position in `highlight_indices`.
  - The `min` pointer index matches the running minimum.
  - When `min_idx` updates, the `min` pointer moves to the new index on the next tick.
- Marker: `@pytest.mark.unit`

### TC-A24 Insertion Sort KEY Label Lifecycle

- Consume the Insertion Sort generator for `default_7` fixture.
- For each outer pass, assert:
  - The KEY label activates on the key-selection T1 tick (single-index highlight).
  - The KEY label remains active during all subsequent T1 compare and T2 shift ticks.
  - The KEY label deactivates on the T2 placement tick.
- Marker: `@pytest.mark.unit`

## 6) Manual Test Pass (Release Gate)

- Verify startup paused state and identical initial arrays `[4, 7, 2, 6, 1, 5, 3]`.
- Verify play/pause/step/restart controls.
- **Observe the Race:** Ensure faster algorithms visually finish earlier, freeze their panels, and halt their UI timers.
- **Observe the Physics:** Verify elements slide smoothly, use vertical arcs when swapping, and respect the universal orange active highlight (D-067) and circular ring sprite shapes (D-069).
- **Observe Heap Sort Phases:** Verify Phase 1 shows actual swaps (heap being built). Verify the orange heap boundary highlight pulses during extraction and visibly shrinks one slot each step.
- **Observe Insertion Sort Lift/Drop:** Verify the key element lifts above the array, stays elevated during comparisons and shifts, and drops smoothly into position.
- **Observe Selection Sort Pointers:** Verify `i` arrow stays above the sorted boundary, `j` scans left-to-right below the row, and `min` jumps when a new minimum is found. Verify coalescing when `j == min`.
- **Observe Insertion Sort KEY Label:** Verify "KEY" label appears on lift, stays visible during all shifts, and disappears on placement drop. Verify the gap is visible at the extracted slot.
- **Observe Heap Sort Tree:** Verify binary tree renders with correct parent-child edges. Verify tree shrinks during extraction. Verify phase label changes from "BUILD MAX-HEAP" to "EXTRACTION". Verify sorted row grows below the tree.
- **Observe Circular Ring Sprites:** Verify all number sprites are circular outlined rings, not squares or bare text. Verify ring color matches number text color.
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
