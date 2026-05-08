# Phase 7c-2 — Bubble Sort Choreography

## Copy everything below this line into Claude Code

---

You are implementing Phase 7c-2 of the Sorting Algorithm Visualizer. This phase adds Bubble Sort's unique visual signature: the **3-Phase Compare-Lift** (T1 ticks physically lift sprite pairs into a compare lane), the **Horizontal Swap Slide** (T2 swaps slide sprites at compare-lane height then settle down — NO arc), and three overlay assets (ComparisonPointer, LimitLine, BubbleHUD). It also refactors `SpriteManager` to support algorithm-specific motion dispatch.

After this phase, the Bubble Sort panel (panel index 0) will show pairs lifting 50px above baseline for comparisons, sliding horizontally past each other for swaps, a green arrow tracking `j`, a dashed boundary line shrinking each pass, and live comparison/exchange counters.

## Rules

- Do NOT run any git commands.
- Do NOT create new spec or documentation files.
- Do NOT modify `orchestrator.py`, `sprite.py`, `easing.py`, `panel.py`, `window.py`, `pointer.py`, `limitline.py`, `hud.py`, `tree_layout.py`, or any model file.
- Only modify `src/visualizer/views/sprite_manager.py` and `src/visualizer/main.py`.
- All four lint/typecheck/test gates must pass before you stop.

## Scope — what is IN Phase 7c-2

1. **SpriteManager refactor** — split `_dispatch_tick` into shared highlight/terminal/failure handling + algorithm-specific dispatch (`_dispatch_default` for Selection/Insertion/Heap, `_dispatch_bubble` for Bubble). Split position computation in `update()` into `_compute_default_positions` and `_compute_bubble_positions`.
2. **Bubble T1 — 3-Phase Compare-Lift (150ms):** Both sprites at `(j, j+1)` execute a vertical choreography within the 150ms tick:
   - Phase 1 (Ascent): 0–67ms → ease from `home_y` up to `compare_lane_y`
   - Phase 2 (Hold): 67–100ms → hold at `compare_lane_y`
   - Phase 3 (Descent): 100–150ms → ease from `compare_lane_y` back down to `home_y`
3. **Bubble T2 — Horizontal Swap Slide (400ms):** NOT an arc swap. Two phases:
   - Phase 1 (Exchange): 0–300ms → sprites at `compare_lane_y`, x-coordinates interpolate to exchange slots
   - Phase 2 (Settle): 300–400ms → sprites descend from `compare_lane_y` to `home_y`
4. **`BubbleOverlay` class** — manages LimitLine, BubbleHUD, and ComparisonPointer for the Bubble Sort panel. Tracks `j` index and pass boundaries from tick data.
5. **ComparisonPointer** — a green `(80, 220, 120)` upward-pointing triangle anchored below the baseline, positioned at the current `j` slot. Drawn by BubbleOverlay.
6. **Wire into `main.py`** — create BubbleOverlay for panel 0, call update/draw in the render loop, reset on K_r.

## Scope — what is DEFERRED (do NOT implement)

- Insertion Sort key elevation, diagonal drop, KEY label
- Heap Sort tree layout, extraction arc, boundary sweep, phase/boundary labels
- Unit tests for BubbleOverlay or the Bubble choreography methods (visual verification only)

## STEP 1 — DEVLOG PRE-ACTION

Append the following entry to `DEVLOG.md`:

```markdown
## 2026-05-05 — Phase 7c-2 pre-action: Bubble Sort choreography

### Plan

Refactor SpriteManager to support algorithm-specific motion dispatch. For Bubble Sort (panel 0): override T1 compare to a 3-phase vertical choreography (ascent 0–67ms, hold 67–100ms, descent 100–150ms at compare_lane_y = home_y - 50px), override T2 swap from arc to horizontal slide at compare_lane_y (0–300ms) then settle to baseline (300–400ms). Create BubbleOverlay class managing LimitLine (advance per pass via j-decrease detection), BubbleHUD (comparisons + exchanges counters), and ComparisonPointer (green arrow below j). Wire into main.py for panel 0. No changes to Selection/Insertion/Heap Sort behavior — they continue using the default motion model.

### Exit criteria

1. pyright — 0 errors, 0 warnings
2. ruff check + ruff format — clean
3. Existing test suite — 339/339 still passing (no regressions)
4. Visual: Bubble Sort sprites lift during compares, slide horizontally during swaps, green arrow tracks j, dashed line shrinks per pass, counters visible
```

## STEP 2 — IMPLEMENTATION

### 2.1 SpriteManager — new instance variable

Add one new field in `__init__`, after `self._arc_height`:

```python
self._compare_lane_y: float = (panel_rect.y + panel_rect.height // 2) - 50
```

This is the fixed vertical position 50px above the baseline, used only by Bubble Sort. Harmless to compute for all algorithms.

### 2.2 SpriteManager — refactor `_dispatch_tick`

Replace the existing `_dispatch_tick` method with this structure. The highlight application and terminal/failure handling remain shared. The motion-setup logic (lines 99–121 in the current file) moves into `_dispatch_default`. A new `_dispatch_bubble` handles Bubble-specific setup.

```python
def _dispatch_tick(self, ctx: PanelContext) -> None:
    """Apply a newly detected tick: colors, then algorithm-specific motion setup."""
    tick = ctx.current_tick
    if tick is None:
        return

    op = tick.operation_type
    self._current_op_type = op

    # --- Shared: highlight application (all algorithms) ---
    for sprite in self._sprites:
        sprite.set_color_state(ColorState.DEFAULT)
    if tick.highlight_indices is not None:
        for slot_idx in tick.highlight_indices:
            sprite_id = ctx.slot_to_sprite_id[slot_idx]
            self._sprites[sprite_id].set_color_state(ColorState.ACTIVE)

    # --- Shared: terminal / failure (all algorithms) ---
    if op == OpType.TERMINAL:
        for sprite in self._sprites:
            sprite.set_color_state(ColorState.COMPLETE)
        self._animation_duration_ms = 0
        self._last_tick = tick
        return
    if op == OpType.FAILURE:
        for sprite in self._sprites:
            sprite.set_color_state(ColorState.ERROR)
        self._animation_duration_ms = 0
        self._last_tick = tick
        return

    # --- Algorithm-specific motion setup ---
    if self._algorithm_name == "Bubble Sort":
        self._dispatch_bubble(tick, ctx, op)
    else:
        self._dispatch_default(tick, ctx, op)

    self._animation_elapsed_ms = 0
    self._animation_duration_ms = get_duration(op, ctx.sift_down_cadence)
    self._last_tick = tick
```

### 2.3 SpriteManager — `_dispatch_default` method

This is the existing motion-setup logic (lines 99–117 of current file), extracted verbatim into its own method:

```python
def _dispatch_default(
    self, tick: SortResult, ctx: PanelContext, op: OpType
) -> None:
    """Default motion setup: sprite_moves → record start, update home, arc for swaps."""
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
```

### 2.4 SpriteManager — `_dispatch_bubble` method

Handles Bubble Sort T1 and T2 differently from the default:

```python
def _dispatch_bubble(
    self, tick: SortResult, ctx: PanelContext, op: OpType
) -> None:
    """Bubble Sort motion setup: T1 = compare-lift, T2 = snap-up + horizontal exchange."""
    self._animating_sprites = {}
    self._swap_left_id = None
    self._swap_right_id = None

    if op == OpType.COMPARE:
        # T1: both sprites at j, j+1 will lift to compare_lane_y.
        # No slot change (no sprite_moves), just vertical motion.
        if tick.highlight_indices is not None:
            for slot_idx in tick.highlight_indices:
                sprite_id = ctx.slot_to_sprite_id[slot_idx]
                sprite = self._sprites[sprite_id]
                self._animating_sprites[sprite_id] = (sprite.exact_x, sprite.exact_y)

    elif op == OpType.SWAP:
        # T2: snap sprites to compare_lane_y, then horizontal exchange + settle.
        # The snap handles the case where T1 descent completed (sprites at home_y).
        for sprite_id, new_slot in ctx.sprite_moves.items():
            sprite = self._sprites[sprite_id]
            sprite.exact_y = self._compare_lane_y  # Instant snap to compare lane
            self._animating_sprites[sprite_id] = (sprite.exact_x, self._compare_lane_y)
            sprite.update_home(new_slot)  # Set new home_x for horizontal target
```

**Key differences from `_dispatch_default`:**
- **T1 COMPARE:** Populates `_animating_sprites` from `highlight_indices` (not `sprite_moves`, which is empty for compares). Records current positions as start. Does NOT call `update_home` — sprites return to the same slot after the lift.
- **T2 SWAP:** Snaps `exact_y` to `compare_lane_y` before recording start position. This ensures the horizontal exchange begins at the compare lane. Records `start_y = compare_lane_y`. Calls `update_home` for new x target. Does NOT set `_swap_left_id`/`_swap_right_id` — Bubble Sort T2 uses horizontal slide, not arc.

### 2.5 SpriteManager — refactor `update()` position computation

Replace the inline position computation block (lines 135–161 in current file) with a branch:

```python
def update(self, dt: int, ctx: PanelContext) -> None:
    """Detect new ticks, advance elapsed time, and recompute sprite positions."""
    if ctx.current_tick is not None and ctx.current_tick is not self._last_tick:
        self._dispatch_tick(ctx)

    if ctx.state == PanelState.ANIMATING_OPERATION and self._animation_duration_ms > 0:
        self._animation_elapsed_ms += dt

    if self._animation_duration_ms > 0 and self._animating_sprites:
        if self._algorithm_name == "Bubble Sort":
            self._compute_bubble_positions()
        else:
            self._compute_default_positions()
```

### 2.6 SpriteManager — `_compute_default_positions` method

Extract the existing position computation verbatim:

```python
def _compute_default_positions(self) -> None:
    """Standard motion: ease_in_out_quad horizontal, sine_arc for swaps."""
    t = min(self._animation_elapsed_ms / self._animation_duration_ms, 1.0)
    eased_t = ease_in_out_quad(t)

    for sprite_id, (start_x, start_y) in self._animating_sprites.items():
        sprite = self._sprites[sprite_id]
        sprite.exact_x = start_x + (sprite.home_x - start_x) * eased_t

        if self._current_op_type == OpType.SWAP:
            arc_offset = self._arc_height * sine_arc(t)
            if sprite_id == self._swap_left_id:
                sprite.exact_y = sprite.home_y - arc_offset
            elif sprite_id == self._swap_right_id:
                sprite.exact_y = sprite.home_y + arc_offset
            else:
                sprite.exact_y = start_y + (sprite.home_y - start_y) * eased_t
        else:
            sprite.exact_y = start_y + (sprite.home_y - start_y) * eased_t

    if t >= 1.0:
        for sprite_id in self._animating_sprites:
            s = self._sprites[sprite_id]
            s.exact_x = s.home_x
            s.exact_y = s.home_y
        self._animating_sprites = {}
        self._swap_left_id = None
        self._swap_right_id = None
```

### 2.7 SpriteManager — `_compute_bubble_positions` method

The heart of the Bubble choreography. Multi-phase timing within a single tick:

```python
def _compute_bubble_positions(self) -> None:
    """Bubble Sort motion: 3-phase compare-lift (T1), horizontal exchange + settle (T2)."""
    elapsed = self._animation_elapsed_ms
    duration = self._animation_duration_ms
    t = min(elapsed / duration, 1.0)

    if self._current_op_type == OpType.COMPARE:
        # 3-Phase Compare-Lift within 150ms:
        #   Phase 1 (Ascent):  0–67ms  → ease from home_y to compare_lane_y
        #   Phase 2 (Hold):    67–100ms → hold at compare_lane_y
        #   Phase 3 (Descent): 100–150ms → ease from compare_lane_y to home_y
        for sprite_id, (start_x, start_y) in self._animating_sprites.items():
            sprite = self._sprites[sprite_id]
            sprite.exact_x = start_x  # No horizontal motion in T1

            if elapsed <= 67:
                # Ascent
                sub_t = min(elapsed / 67, 1.0)
                eased = ease_in_out_quad(sub_t)
                sprite.exact_y = start_y + (self._compare_lane_y - start_y) * eased
            elif elapsed <= 100:
                # Hold
                sprite.exact_y = self._compare_lane_y
            else:
                # Descent
                sub_t = min((elapsed - 100) / 50, 1.0)
                eased = ease_in_out_quad(sub_t)
                sprite.exact_y = self._compare_lane_y + (sprite.home_y - self._compare_lane_y) * eased

    elif self._current_op_type == OpType.SWAP:
        # 2-Phase Horizontal Swap Slide within 400ms:
        #   Phase 1 (Exchange): 0–300ms → x interpolates at fixed compare_lane_y
        #   Phase 2 (Settle):   300–400ms → descend from compare_lane_y to home_y
        for sprite_id, (start_x, start_y) in self._animating_sprites.items():
            sprite = self._sprites[sprite_id]

            if elapsed <= 300:
                # Horizontal exchange at compare lane
                sub_t = min(elapsed / 300, 1.0)
                eased = ease_in_out_quad(sub_t)
                sprite.exact_x = start_x + (sprite.home_x - start_x) * eased
                sprite.exact_y = self._compare_lane_y  # Fixed y
            else:
                # Settle: descend to baseline
                sprite.exact_x = sprite.home_x  # Already at target x
                sub_t = min((elapsed - 300) / 100, 1.0)
                eased = ease_in_out_quad(sub_t)
                sprite.exact_y = self._compare_lane_y + (sprite.home_y - self._compare_lane_y) * eased

    # Snap to home on completion (same as default)
    if t >= 1.0:
        for sprite_id in self._animating_sprites:
            s = self._sprites[sprite_id]
            s.exact_x = s.home_x
            s.exact_y = s.home_y
        self._animating_sprites = {}
```

**Important implementation notes:**
- `elapsed` is `self._animation_elapsed_ms` (integer milliseconds). Phase boundaries at 67ms, 100ms, 300ms.
- Each phase computes its own `sub_t` from the phase-local elapsed time and phase duration.
- `sub_t` is always clamped to `[0.0, 1.0]` with `min(..., 1.0)`.
- The descent phase duration is `150 - 100 = 50ms`. The settle phase duration is `400 - 300 = 100ms`.
- At `t >= 1.0`, all sprites snap to home (identical to default behavior). This guarantees no floating-point drift.
- The swap left/right IDs (`_swap_left_id`, `_swap_right_id`) are NOT used by Bubble Sort — both sprites slide horizontally at the same y. No arc.

### 2.8 Create `BubbleOverlay` class in `sprite_manager.py`

Add this class **after** `SelectionOverlay` at the bottom of `sprite_manager.py`.

#### Additional imports needed (add at top of sprite_manager.py)

```python
from visualizer.views.hud import BubbleHUD
from visualizer.views.limitline import LimitLine
```

#### Class: `BubbleOverlay`

**Constructor** `__init__(self, limit_line: LimitLine, bubble_hud: BubbleHUD, panel_rect: pygame.Rect, array_x_padding: int, slot_width: float, ring_radius: int)`:

- Store all parameters.
- Internal state:
  - `_last_tick: SortResult | None = None`
  - `_j: int = -1` — current j index for ComparisonPointer (sentinel -1 = not started)
  - `_pointer_visible: bool = False`
  - `_home_y: float = panel_rect.y + panel_rect.height // 2`
- Compute arrow geometry constants (reuse values from `pointer.py`):
  - `_arrow_gap: int = 5`
  - `_arrow_height: int = 12`
  - `_arrow_half_width: int = 5`
  - `_pointer_color: tuple[int, int, int] = (80, 220, 120)` — green (matches completion green palette)

**Method: `update(self, ctx: PanelContext) -> None`**:

Identity-based new-tick detection (same pattern as SelectionOverlay):
```python
if ctx.current_tick is not None and ctx.current_tick is not self._last_tick:
    self._process_tick(ctx.current_tick)
    self._last_tick = ctx.current_tick
```

**Method: `_process_tick(self, tick: SortResult) -> None`**:

**Case `OpType.COMPARE`:**
1. Guard: `tick.highlight_indices is None or len(tick.highlight_indices) != 2` → return.
2. Extract `j = tick.highlight_indices[0]` — for Bubble Sort T1, `highlight_indices = (j, j+1)`, so `j` is the first element.
3. **Pass boundary detection:** If `self._j >= 0 and j < self._j` → a new pass started (j decreased from the previous pass's last value). Call `self._limit_line.advance()`.
4. Update `self._j = j`.
5. Set `self._pointer_visible = True`.

**Case `OpType.SWAP`:**
1. No pointer update needed — the swap occurs at the same `(j, j+1)` pair, pointer stays at `j`.

**Case `OpType.TERMINAL` or `OpType.FAILURE`:**
1. `self._pointer_visible = False`.

**Method: `draw(self, surface: pygame.Surface, comparisons: int, writes: int) -> None`**:

```python
self._limit_line.draw(surface)
self._bubble_hud.draw(surface, comparisons, writes // 2)
if self._pointer_visible and self._j >= 0:
    self._draw_comparison_pointer(surface)
```

Note: `writes // 2` converts write count to exchange count (each swap writes 2 positions).

**Method: `_draw_comparison_pointer(self, surface: pygame.Surface) -> None`**:

Draw a green upward-pointing triangle below the baseline at slot `self._j`:

```python
cx = (
    self._panel_rect.x
    + self._array_x_padding
    + self._j * self._slot_width
    + self._slot_width / 2
)
tip_y = self._home_y + self._ring_radius + self._arrow_gap
base_y = tip_y + self._arrow_height
points: list[tuple[int, int]] = [
    (round(cx), round(tip_y)),
    (round(cx - self._arrow_half_width), round(base_y)),
    (round(cx + self._arrow_half_width), round(base_y)),
]
pygame.draw.polygon(surface, self._pointer_color, points)
```

This draws an upward-pointing triangle (tip toward the sprite, base below), matching the j/min arrows in `pointer.py`.

**Method: `reset(self) -> None`**:

```python
self._last_tick = None
self._j = -1
self._pointer_visible = False
self._limit_line.reset()
```

### 2.9 Modify `src/visualizer/main.py`

**New imports to add:**

```python
from visualizer.views.hud import BubbleHUD
from visualizer.views.limitline import LimitLine
from visualizer.views.sprite_manager import BubbleOverlay, SelectionOverlay, SpriteManager
```

Update the existing `sprite_manager` import line to also import `BubbleOverlay`.

**Create the BubbleOverlay** — after creating the SelectionOverlay, before `orchestrator`:

```python
# Bubble Sort overlay (panel index 0)
_home_y_bubble = layout.panel_rects[0].y + layout.panel_rects[0].height // 2
_limit_line = LimitLine(
    panel_rect=layout.panel_rects[0],
    array_x_padding=layout.ARRAY_X_PADDING,
    slot_width=layout.slot_width,
    home_y=_home_y_bubble,
    ring_radius=_ring_radius,
    array_size=len(INITIAL_ARRAY),
)
_bubble_hud = BubbleHUD(
    panel_rect=layout.panel_rects[0],
    body_font=body_font,
    inset_x=layout.ARRAY_X_PADDING,
)
bubble_overlay = BubbleOverlay(
    limit_line=_limit_line,
    bubble_hud=_bubble_hud,
    panel_rect=layout.panel_rects[0],
    array_x_padding=layout.ARRAY_X_PADDING,
    slot_width=layout.slot_width,
    ring_radius=_ring_radius,
)
```

Note: `_ring_radius` is already computed from Phase 7c-1 (`int(layout.slot_width * RING_DIAMETER_RATIO) // 2`). Reuse it.

**Wire into the render loop** — add overlay calls for panel 0 (alongside the existing panel 1 selection overlay):

```python
for i, renderer in enumerate(panel_renderers):
    ctx = orchestrator.panels[i]
    view_state = _map_panel_state(ctx)
    renderer.draw_background(surface, view_state)
    renderer.draw_header(
        surface,
        ctx.algorithm_name,
        _build_metrics(ctx),
        _build_message(ctx),
        view_state,
    )
    sprite_managers[i].update(dt, ctx)
    sprite_managers[i].draw(surface)

    # Bubble Sort overlay (panel index 0)
    if i == 0:
        bubble_overlay.update(ctx)
        bubble_overlay.draw(surface, ctx.comparisons, ctx.writes)

    # Selection Sort pointer overlay (panel index 1)
    if i == 1:
        selection_overlay.update(ctx)
        selection_overlay.draw(surface)
```

**Wire restart** — in the K_r handler, after resetting sprite managers and selection overlay:

```python
elif event.key == pygame.K_r:
    orchestrator.restart()
    for sm in sprite_managers:
        sm.reset(INITIAL_ARRAY)
    selection_overlay.reset()
    bubble_overlay.reset()
```

## STEP 3 — VERIFICATION

Run all gates:

```bash
# Gate 1: Pyright
PYRIGHT_PYTHON_GLOBAL_NODE=false uv run pyright src/visualizer/views/sprite_manager.py src/visualizer/main.py

# Gate 2: Ruff
uv run ruff check src/visualizer/views/sprite_manager.py src/visualizer/main.py && uv run ruff format --check src/visualizer/views/sprite_manager.py src/visualizer/main.py

# Gate 3: Existing tests — no regressions
uv run pytest tests/ -q

# Gate 4: Import check — BubbleOverlay loads without error
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy uv run python -c "
from visualizer.views.sprite_manager import SpriteManager, SelectionOverlay, BubbleOverlay
print('SpriteManager imported OK')
print('SelectionOverlay imported OK')
print('BubbleOverlay imported OK')
"
```

All four must pass. Fix any issues before proceeding.

## STEP 4 — DEVLOG POST-ACTION

Append a post-action entry to `DEVLOG.md` immediately after the pre-action entry:

```markdown
## 2026-05-05 — Phase 7c-2 closed: Bubble Sort choreography (post-action)

### Worked on

[Describe what was actually created — SpriteManager refactoring (dispatch split, position computation split), _dispatch_bubble, _compute_bubble_positions (3-phase T1, 2-phase T2), BubbleOverlay class, main.py wiring. Any deviations from the plan.]

### Corrections

[List any ruff/pyright corrections, or "Zero corrections" if clean on first run.]

### Results

- `uv run pyright src/visualizer/views/sprite_manager.py src/visualizer/main.py`: **[N] errors, [N] warnings**
- `uv run ruff check` + `uv run ruff format --check`: **[clean/N issues]**
- `uv run pytest tests/ -q`: **339/339 PASSED** (no regressions)
- Import check: **[PASS/FAIL]**

### Next

Phase 7c-3: Insertion Sort choreography (cross-tick key elevation, diagonal drop placement, KEY label, gap visualization).
```

## Context files to read

Read these files before writing any code:

1. `CLAUDE.md` — Critical Rules (especially #5 universal orange, #6 timing, #7 dt clamp)
2. `src/visualizer/views/sprite_manager.py` — **Read the ENTIRE file.** Current SpriteManager with `_dispatch_tick`, `update`, `draw`, `reset`, plus `SelectionOverlay`. Your refactoring must preserve SelectionOverlay unchanged and maintain all existing behavior for Selection/Insertion/Heap Sort.
3. `src/visualizer/main.py` — **Read the ENTIRE file.** Current render loop with SelectionOverlay wiring. Your changes add to this without breaking existing structure.
4. `src/visualizer/views/limitline.py` — `LimitLine(panel_rect, array_x_padding, slot_width, home_y, ring_radius, array_size)`, `.advance()`, `.reset()`, `.draw(surface)`
5. `src/visualizer/views/hud.py` — `BubbleHUD(panel_rect, body_font, inset_x)`, `.draw(surface, comparisons, exchanges)`
6. `src/visualizer/views/easing.py` — `ease_in_out_quad(t)` used for all sub-phase easing
7. `src/visualizer/models/bubble.py` — T1 yields `highlight_indices=(j, j+1)`, T2 yields `highlight_indices=(j, j+1)`. Inner limit shrinks per pass.
8. `docs/contracts/BUBBLE_SORT_ANIMATION.md` — §3 (3-Phase Compare-Lift timing), §4 (Swap Contract — horizontal slide NOT arc), §5 (pass boundary + LimitLine behavior)

---
