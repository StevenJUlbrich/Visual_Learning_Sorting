# Phase 7c-5 — Selection Sort Settled Color + Configurable Initial Array

## Copy everything below this line into Claude Code

---

You are implementing Phase 7c-5 of the Sorting Algorithm Visualizer. This phase addresses two acceptance-test gaps:

**Gap 1 (AT-20):** Selection Sort needs a steel-blue settled region. After each pass places the minimum at index `i`, that element must transition to `ColorState.SETTLED` (steel-blue `(130, 150, 190)`) and remain steel-blue for the rest of the sort. On completion, settled elements transition to green like everything else. This extends D-063 (previously Heap Sort only) to Selection Sort, as AT-20 explicitly requires.

**Gap 2 (AT-08):** The initial array is hardcoded to `[4, 7, 2, 6, 1, 5, 3]`. AT-08 requires testing with `[3, 1, 3, 2, 1, 2, 3]` (duplicates). Add an optional `array` key to `config.toml` so the user can switch arrays without editing Python code.

After this phase, the Selection Sort panel will visually distinguish its sorted prefix from the unsorted region using the same steel-blue color contract as Heap Sort, and the initial array will be configurable via `config.toml`.

## Rules

- Do NOT run any git commands.
- Do NOT create new spec or documentation files.
- Do NOT modify `orchestrator.py`, `sprite.py`, `easing.py`, `panel.py`, `window.py`, `pointer.py`, `limitline.py`, `hud.py`, `tree_layout.py`, or any model file.
- Only modify these files: `src/visualizer/views/sprite_manager.py`, `src/visualizer/main.py`, `config.toml`.
- All four lint/typecheck/test gates must pass before you stop.

## Scope — what is IN Phase 7c-5

1. `_dispatch_selection` method in SpriteManager — replaces `_dispatch_default` for Selection Sort
2. `_selection_sorted_count: int` tracking state in SpriteManager
3. `_apply_selection_settled` method — forces `ColorState.SETTLED` for sprites in positions `0..(sorted_count-1)`
4. Settled-color persistence across ticks — override the shared highlight-reset in `_dispatch_tick`
5. `reset()` clears `_selection_sorted_count` to 0
6. `config.toml` optional `[sort]` section with `array` key
7. `_load_array()` function in `main.py` that reads the config or falls back to `[4, 7, 2, 6, 1, 5, 3]`

## Scope — what is DEFERRED (do NOT implement)

- Extending settled color to Bubble Sort or Insertion Sort
- Any changes to the Selection Sort model/generator
- Any changes to SelectionOverlay (pointer tracking works correctly as-is)
- Unit tests for the new behavior (visual verification via AT-20)

## STEP 1 — DEVLOG PRE-ACTION

Append the following entry to `DEVLOG.md`:

```markdown
## 2026-05-05 — Phase 7c-5 pre-action: Selection Sort settled color + array config

### Plan

Address two acceptance-test gaps:

1. **AT-20 (Selection Sort settled region):** Add `_dispatch_selection` to SpriteManager that tracks the growing sorted prefix. After each T2 swap places the minimum, increment `_selection_sorted_count` and apply `ColorState.SETTLED` to sprites at indices `0..sorted_count-1`. Add `_apply_selection_settled` (same pattern as Heap Sort's `_apply_sorted_settled`) to persist steel-blue across the shared highlight reset in `_dispatch_tick`. Extends D-063 to Selection Sort as required by AT-20.

2. **AT-08 (configurable array):** Add optional `[sort]` section to `config.toml` with `array` key. Add `_load_array()` to `main.py` that parses the config or falls back to the default `[4, 7, 2, 6, 1, 5, 3]`. This allows testing with duplicate values `[3, 1, 3, 2, 1, 2, 3]` by editing config.toml instead of Python code.

### Exit criteria

1. pyright — 0 errors, 0 warnings
2. ruff check + ruff format — clean
3. Existing test suite — 339/339 still passing (no regressions)
4. Visual: Selection Sort settled prefix grows steel-blue after each swap
5. Config: changing `config.toml` array changes the visualized dataset
```

## STEP 2 — IMPLEMENTATION

### 2.1 Add Selection Sort state to `SpriteManager.__init__`

In the `__init__` method, after the existing Heap Sort state block (around line 84), add:

```python
        # Selection Sort settled-region state
        self._selection_sorted_count: int = 0
```

This tracks how many elements from the left side of the array are in their final sorted position. It starts at 0 and increments by 1 after each pass's T2 swap.

### 2.2 Create `_dispatch_selection` method

Add this method in `SpriteManager`, immediately after `_dispatch_default` (which currently handles Selection Sort via the `else` branch). The method follows the same structure as `_dispatch_default` but adds settled-region tracking.

```python
    def _dispatch_selection(self, tick: SortResult, ctx: PanelContext, op: OpType) -> None:
        """Selection Sort motion setup: standard arc swap + settled-region tracking."""
        self._animating_sprites = {}
        self._swap_left_id = None
        self._swap_right_id = None

        for sprite_id, new_slot in ctx.sprite_moves.items():
            sprite = self._sprites[sprite_id]
            self._animating_sprites[sprite_id] = (sprite.exact_x, sprite.exact_y)
            sprite.update_home(new_slot)

        if op == OpType.SWAP and len(self._animating_sprites) == 2:
            ids = list(ctx.sprite_moves.keys())
            if ctx.sprite_moves[ids[0]] < ctx.sprite_moves[ids[1]]:
                self._swap_left_id = ids[0]
                self._swap_right_id = ids[1]
            else:
                self._swap_left_id = ids[1]
                self._swap_right_id = ids[0]

            # After swap completes its animation dispatch, increment sorted count.
            # The swap places the pass minimum at index self._selection_sorted_count.
            self._selection_sorted_count += 1

        elif op == OpType.COMPARE:
            # Detect no-swap passes: Selection Sort's outer loop increments i every pass.
            # When min_idx == i, no swap is emitted — the element is already in place.
            # The next T1 compare has highlight_indices[0] = min_idx (the new i),
            # which is > our tracked sorted_count. The while loop catches up.
            if tick.highlight_indices is not None and len(tick.highlight_indices) == 2:
                min_idx = tick.highlight_indices[0]
                while self._selection_sorted_count < min_idx:
                    self._selection_sorted_count += 1

        # Apply settled color to the sorted prefix
        self._apply_selection_settled(ctx)
```

**Important edge case — last pass without swap:** If the last outer-loop pass (`i = n-2`) ends without a swap (element already in place), no subsequent T1 compare fires to trigger the catch-up — the next tick is TERMINAL. However, TERMINAL is handled by the shared block in `_dispatch_tick` (line ~126-131), which sets ALL sprites to `ColorState.COMPLETE` and returns early before `_dispatch_selection` runs. So the user sees green, never a missing steel-blue frame. The visual behavior is correct: for the brief duration of the last pass's T1 compares, `sorted_count` may be one behind the ideal, but the scan operates only in the unsorted suffix (right of the settled prefix), so the settled region is visually consistent.

**Key insight — no-swap pass detection:** Selection Sort's outer loop increments `i` every pass. When `min_idx == i`, no swap is emitted — the element is already in place. The next T1 compare will have `min_idx` (which equals the new `i`) greater than our tracked `_selection_sorted_count`. The `while` loop catches up by incrementing for each skipped pass.

### 2.3 Create `_apply_selection_settled` method

Add this immediately after `_dispatch_selection`:

```python
    def _apply_selection_settled(self, ctx: PanelContext) -> None:
        """Force ColorState.SETTLED for all sprites in the sorted prefix (slot < sorted_count)."""
        for slot in range(self._selection_sorted_count):
            sprite_id = ctx.slot_to_sprite_id[slot]
            self._sprites[sprite_id].set_color_state(ColorState.SETTLED)
```

This is the exact same pattern as Heap Sort's `_apply_sorted_settled`, but operating on the LEFT prefix instead of the RIGHT suffix.

### 2.4 Wire `_dispatch_selection` into the dispatch routing

In `_dispatch_tick`, change the `else` branch (line ~146-147) to route Selection Sort to the new method:

**Current code (lines 139-147):**
```python
        # --- Algorithm-specific motion setup ---
        if self._algorithm_name == "Bubble Sort":
            self._dispatch_bubble(tick, ctx, op)
        elif self._algorithm_name == "Insertion Sort":
            self._dispatch_insertion(tick, ctx, op)
        elif self._algorithm_name == "Heap Sort":
            self._dispatch_heap(tick, ctx, op)
        else:
            self._dispatch_default(tick, ctx, op)
```

**New code:**
```python
        # --- Algorithm-specific motion setup ---
        if self._algorithm_name == "Bubble Sort":
            self._dispatch_bubble(tick, ctx, op)
        elif self._algorithm_name == "Selection Sort":
            self._dispatch_selection(tick, ctx, op)
        elif self._algorithm_name == "Insertion Sort":
            self._dispatch_insertion(tick, ctx, op)
        elif self._algorithm_name == "Heap Sort":
            self._dispatch_heap(tick, ctx, op)
        else:
            self._dispatch_default(tick, ctx, op)
```

### 2.5 Add settled-color persistence to `_dispatch_tick`

The shared highlight-reset at the top of `_dispatch_tick` (lines 112-113) resets ALL sprites to `ColorState.DEFAULT` on every new tick:

```python
        for sprite in self._sprites:
            sprite.set_color_state(ColorState.DEFAULT)
```

For Heap Sort, this is fixed by calling `_apply_sorted_settled` inside `_dispatch_heap`. For Selection Sort, we need to re-apply settled color AFTER the shared reset and AFTER the highlight application. The natural place is inside `_dispatch_selection` — the call to `self._apply_selection_settled(ctx)` at the end of the method already handles this, because `_dispatch_selection` runs AFTER the shared highlight block.

**However**, there is a subtlety: on a TERMINAL tick, `_dispatch_tick` returns early (line 131) BEFORE reaching the algorithm-specific dispatch. The terminal handler sets all sprites to `ColorState.COMPLETE` (green), which is correct — settled elements SHOULD transition to green on completion. So no special handling is needed for TERMINAL.

**Verify this logic is correct by tracing the execution for a T1 compare tick:**
1. Shared block resets all sprites to DEFAULT (line 112-113)
2. Shared block applies ACTIVE to highlighted indices (lines 114-117)
3. `_dispatch_selection` is called (line ~141)
4. Inside `_dispatch_selection`, motion setup occurs
5. `_apply_selection_settled` re-forces SETTLED on the sorted prefix, overriding any DEFAULT that was set in step 1
6. Result: sorted prefix = steel-blue, highlighted = orange, others = default blue ✓

### 2.6 Update `_compute_default_positions` routing

In the `update()` method (around line 346-354), Selection Sort currently falls through to `_compute_default_positions` via the `else` branch:

```python
            if self._algorithm_name == "Bubble Sort":
                self._compute_bubble_positions()
            elif self._algorithm_name == "Insertion Sort":
                self._compute_insertion_positions()
            elif self._algorithm_name == "Heap Sort":
                self._compute_heap_positions()
            else:
                self._compute_default_positions()
```

This is **correct and does not need changing**. Selection Sort uses the standard arc-swap motion model — the only change is settled coloring, not motion. Leave the `else` → `_compute_default_positions()` path intact. Selection Sort intentionally shares the default motion computation.

### 2.7 Update `reset()` — clear Selection Sort state

In the `reset()` method (around line 617), add after the existing state clears (around line 644 after `self._heap_size = len(initial_array)`):

```python
        # Selection Sort state
        self._selection_sorted_count = 0
```

### 2.8 Modify `config.toml` — add optional `[sort]` section

Add to the end of `config.toml`:

```toml

[sort]
# Override the initial array. Must be a list of integers with 2-20 elements.
# Default (comment out or remove to use): [4, 7, 2, 6, 1, 5, 3]
# Duplicate-value test (AT-08): [3, 1, 3, 2, 1, 2, 3]
# array = [4, 7, 2, 6, 1, 5, 3]
```

The key is commented out by default, so the app uses the hardcoded fallback. Users uncomment and change it to test different arrays.

### 2.9 Add `_load_array()` function to `main.py`

Add this function after `_load_config()` (after line 71):

```python
def _load_array() -> list[int]:
    """Load initial array from config.toml [sort] section; fall back to default."""
    default = [4, 7, 2, 6, 1, 5, 3]
    try:
        with _CONFIG_PATH.open("rb") as f:
            config = tomllib.load(f)
        raw = config["sort"]["array"]
        if not isinstance(raw, list) or len(raw) < 2 or len(raw) > 20:
            print(
                "WARNING: config.toml [sort].array must be a list of 2-20 integers — using default.",
                file=sys.stderr,
            )
            return default
        arr = [int(v) for v in raw]
        return arr
    except (FileNotFoundError, KeyError, tomllib.TOMLDecodeError):
        return default
    except (TypeError, ValueError) as exc:
        print(
            f"WARNING: config.toml [sort].array error ({exc}) — using default.",
            file=sys.stderr,
        )
        return default
```

**Design decisions:**
- Minimum 2 elements (single-element arrays short-circuit with TERMINAL, no interesting visualization).
- Maximum 20 elements (beyond this, sprites become too small in the panel). You can raise this if needed.
- `int(v)` coercion handles TOML's native integer type.
- Falls back silently on missing key (most users won't have it).
- Uses the same `_CONFIG_PATH` already defined for window preset loading.

### 2.10 Wire `_load_array()` into `main()`

In the `main()` function, replace the use of the module-level `INITIAL_ARRAY` constant with a call to `_load_array()`. The module-level constant stays as the fallback default but the running array comes from config.

**Current code (inside `main()`, around line 174-175):**
```python
    width, height = _load_config()
    surface, layout = init_display(width, height)
```

**Add after that line:**
```python
    initial_array = _load_array()
```

Then **replace every reference to `INITIAL_ARRAY` inside `main()`** with `initial_array`:

There are exactly 5 references to `INITIAL_ARRAY` inside `main()`:

1. **Line ~204** in the SpriteManager list comprehension:
   ```python
   initial_array=INITIAL_ARRAY,
   ```
   → Change to:
   ```python
   initial_array=initial_array,
   ```

2. **Line ~229** `array_size=len(INITIAL_ARRAY)`:
   → Change to `array_size=len(initial_array)`

3. **Line ~258** `array_size=len(INITIAL_ARRAY)`:
   → Change to `array_size=len(initial_array)`

4. **Line ~261** `Orchestrator(algorithms, INITIAL_ARRAY)`:
   First, the algorithm constructors also need the array. Look at `_build_orchestrator()` — it currently uses `INITIAL_ARRAY`. We need to parameterize it.

5. **Line ~280** `sm.reset(INITIAL_ARRAY)`:
   → Change to `sm.reset(initial_array)`

### 2.11 Parameterize `_build_orchestrator()`

**Current:**
```python
def _build_orchestrator() -> Orchestrator:
    """Instantiate the four algorithms and return a configured Orchestrator."""
    algorithms = [
        BubbleSort(INITIAL_ARRAY),
        SelectionSort(INITIAL_ARRAY),
        InsertionSort(INITIAL_ARRAY),
        HeapSort(INITIAL_ARRAY),
    ]
    return Orchestrator(algorithms, INITIAL_ARRAY)
```

**New:**
```python
def _build_orchestrator(initial_array: list[int]) -> Orchestrator:
    """Instantiate the four algorithms and return a configured Orchestrator."""
    algorithms = [
        BubbleSort(initial_array),
        SelectionSort(initial_array),
        InsertionSort(initial_array),
        HeapSort(initial_array),
    ]
    return Orchestrator(algorithms, initial_array)
```

Update the call site in `main()`:
```python
    orchestrator = _build_orchestrator(initial_array)
```

### 2.12 Keep `INITIAL_ARRAY` as module-level constant

Do NOT remove `INITIAL_ARRAY` from the module level. It serves as the documented default and is the fallback inside `_load_array()`. The `_load_array()` function returns `[4, 7, 2, 6, 1, 5, 3]` as its default, matching `INITIAL_ARRAY`. The module constant remains for readability and for any test code that imports it.

However, `main()` now uses `initial_array` (from `_load_array()`) everywhere instead of `INITIAL_ARRAY` directly.

## STEP 3 — VERIFICATION GATES

Run all four gates in sequence. Every gate must pass cleanly.

### Gate 1: pyright

```bash
cd /home/steven/Projects/Visual_Learning_Sorting && uv run pyright src/
```

Expected: 0 errors, 0 warnings.

### Gate 2: ruff

```bash
cd /home/steven/Projects/Visual_Learning_Sorting && uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/
```

Expected: clean.

### Gate 3: pytest

```bash
cd /home/steven/Projects/Visual_Learning_Sorting && uv run pytest tests/ -q
```

Expected: 339 passed (no regressions). No new tests in this phase.

### Gate 4: import check

```bash
cd /home/steven/Projects/Visual_Learning_Sorting && uv run python -c "from visualizer.views.sprite_manager import SpriteManager, SelectionOverlay; print('OK')"
```

Expected: `OK`.

If any gate fails, fix the issue and re-run all gates.

## STEP 4 — DEVLOG POST-ACTION

Append the following entry to `DEVLOG.md`:

```markdown
## 2026-05-05 — Phase 7c-5 post-action: Selection Sort settled color + array config

### What was built

1. **Selection Sort settled region (AT-20):**
   - `_dispatch_selection` method in SpriteManager — replaces `_dispatch_default` for Selection Sort
   - `_selection_sorted_count` tracks the growing sorted prefix
   - `_apply_selection_settled` forces `ColorState.SETTLED` (steel-blue) on indices `0..sorted_count-1`
   - No-swap pass detection: when min_idx > sorted_count on a T1 compare, catches up for skipped passes
   - Settled color persists across shared highlight reset (same pattern as Heap Sort)
   - On TERMINAL tick, settled sprites transition to green via shared completion handler

2. **Configurable initial array (AT-08):**
   - `config.toml` gains optional `[sort]` section with `array` key
   - `_load_array()` in main.py reads config or falls back to `[4, 7, 2, 6, 1, 5, 3]`
   - `_build_orchestrator()` parameterized with `initial_array`
   - All `INITIAL_ARRAY` references in `main()` replaced with config-loaded `initial_array`

### Verification

- pyright: 0 errors
- ruff: clean
- pytest: 339/339 passed
- Import check: OK
```

## STEP 5 — FINAL SUMMARY

Report:
1. Files modified and line counts
2. All four gate results
3. Confirmation that Selection Sort panels now show steel-blue sorted prefix
4. Confirmation that config.toml array override is functional
