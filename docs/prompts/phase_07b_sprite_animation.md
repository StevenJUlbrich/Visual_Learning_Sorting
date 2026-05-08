# Phase 7b — Sprite Animation Rendering

## Copy everything below this line into Claude Code

---

You are implementing Phase 7b of the Sorting Algorithm Visualizer. This phase creates `src/visualizer/views/sprite_manager.py` — a per-panel sprite manager that owns `NumberSprite` instances, dispatches motion from the orchestrator's `sprite_moves`, interpolates positions with easing each frame, and renders sprites with z-ordering. It also modifies `src/visualizer/main.py` to wire the sprite managers into the render loop.

After this phase, all four algorithm panels will show circular number sprites that physically move when swaps and shifts occur, with smooth easing and sine-arc vertical separation during swaps.

## Rules

- Do NOT run any git commands.
- Do NOT create new spec or documentation files.
- Do NOT modify `orchestrator.py`, `sprite.py`, `easing.py`, `panel.py`, `window.py`, or any model file.
- Only create `src/visualizer/views/sprite_manager.py` and modify `src/visualizer/main.py`.
- All four lint/typecheck/test gates must pass before you stop.

## Scope — what is IN Phase 7b

1. `SpriteManager` class — owns 7 `NumberSprite` instances for one panel
2. New-tick detection — compare `ctx.current_tick` identity each frame to detect tick changes
3. Sprite motion dispatch — read `ctx.sprite_moves` dict, call `update_home(new_slot)` on affected sprites, record animation start positions
4. Per-frame easing interpolation — advance `_animation_elapsed_ms` by `dt`, compute `t`, interpolate `exact_x` via `ease_in_out_quad`
5. Swap arc motion — for `OpType.SWAP` ticks, apply `sine_arc(t) * arc_height` vertical offset (standard `arc_height = panel_height * 0.08`). Left sprite (lower index) arcs UP (`home_y - offset`), right sprite (higher index) arcs DOWN (`home_y + offset`). SHIFT ticks are horizontal only — no arc.
6. Highlight color — at tick start, set `ColorState.ACTIVE` on sprites at `highlight_indices`, revert all others to `ColorState.DEFAULT`
7. Completion color — on `TERMINAL` tick, set all sprites to `ColorState.COMPLETE`
8. Failure color — on `FAILURE` tick, set all sprites to `ColorState.ERROR`
9. Z-ordering — draw baseline sprites first (by slot index), then lifted sprites sorted by `exact_y` ascending (highest on screen = drawn last = on top)
10. Restart handling — `main.py` calls `sprite_manager.reset(initial_array)` to recreate all sprites at initial positions
11. Pause handling — only advance `_animation_elapsed_ms` when `ctx.state == PanelState.ANIMATING_OPERATION`
12. Wire into `main.py` render loop — create 4 `SpriteManager` instances, call `update(dt, ctx)` then `draw(surface)` per panel each frame

## Scope — what is DEFERRED (do NOT implement)

- Bubble Sort 3-phase compare-lift (vertical choreography within T1 ticks)
- Insertion Sort sustained key elevation + KEY label + gap visualization
- Heap Sort binary tree layout (tree_layout.py wiring — all algorithms use flat baseline row for now)
- Heap Sort extraction arc (elevated `panel_height * 0.14` height)
- Heap Sort boundary sweep (staggered left-to-right)
- Selection Sort pointer arrows (i/j/min from pointer.py)
- Bubble Sort ComparisonPointer + LimitLine
- HUD overlays (BubbleHUD counters, HeapPhaseLabel, HeapBoundaryLabel)
- On-screen control buttons

For Phase 7b, ALL four algorithms render in a flat horizontal row with the same motion model: horizontal easing for all position changes, standard sine arc for SWAP operations, highlight-only for COMPARE and RANGE ticks. This creates a visible, working race. The per-algorithm visual signatures come in subsequent phases.

## STEP 1 — DEVLOG PRE-ACTION

Append the following entry to `DEVLOG.md` immediately after the Phase 7 post-action entry (or at the top of the current-phase section if no post-action exists yet):

```markdown
## 2026-05-04 — Phase 7b pre-action: Sprite animation rendering

### Plan

Create `src/visualizer/views/sprite_manager.py` with a `SpriteManager` class that owns 7 `NumberSprite` instances per panel. Each frame: detect new ticks by comparing `ctx.current_tick` identity, dispatch `sprite_moves` to update sprite home positions, advance interpolation elapsed time by `dt` (only when `ctx.state == ANIMATING_OPERATION`), compute eased positions (`ease_in_out_quad` for horizontal, `sine_arc` for swap vertical offset), apply highlight colors from `highlight_indices`, handle completion/failure color states, and draw sprites with z-ordering (lifted sprites on top). Modify `main.py` to create 4 SpriteManagers and wire them into the render loop after panel headers. All four algorithms use a flat baseline row with standard arc swaps — per-algorithm choreography (compare-lift, key elevation, tree layout) is deferred.

### Exit criteria

1. pyright — 0 errors, 0 warnings
2. ruff check + ruff format — clean
3. Existing test suite — 339/339 still passing (no regressions)
4. Visual: sprites appear at correct home positions in all 4 panels and move on play/step
```

## STEP 2 — IMPLEMENTATION

### 2.1 Create `src/visualizer/views/sprite_manager.py`

```python
"""SpriteManager — per-panel sprite lifecycle, animation dispatch, and rendering.

Owns NumberSprite instances for one algorithm panel. Receives tick updates
from PanelContext, interpolates positions with easing, and draws with z-ordering.

Phase 7b scope: flat baseline row for all algorithms, standard swap arcs,
highlight coloring. Per-algorithm choreography deferred to later phases.

See doc 12 (animation foundation), doc 10 §2 (interpolation rules).
"""
```

#### Class: `SpriteManager`

**Constructor** `__init__(self, panel_rect, array_x_padding, slot_width, font, initial_array)`:

- `panel_rect: pygame.Rect` — the panel's bounding rectangle
- `array_x_padding: int` — horizontal padding from `GridLayout.ARRAY_X_PADDING`
- `slot_width: float` — from `GridLayout.slot_width`
- `font: pygame.font.Font` — the number font for sprite text rendering
- `initial_array: list[int]` — e.g. `[4, 7, 2, 6, 1, 5, 3]`, used for sprite values
- Store these for restart use.
- Create 7 `NumberSprite` instances: `sprite_id=i`, `value=initial_array[i]`, `slot_index=i`.
- Store sprites in a `list[NumberSprite]` indexed by `sprite_id`.
- Compute `arc_height: float = panel_rect.height * 0.08` (doc 12 §8.1).

Internal animation state:
- `_last_tick: SortResult | None = None` — reference to last dispatched tick (identity comparison)
- `_animation_elapsed_ms: int = 0`
- `_animation_duration_ms: int = 0`
- `_animating_sprites: dict[int, tuple[float, float]]` — `{sprite_id: (start_x, start_y)}` for sprites with active motion
- `_swap_left_id: int | None = None` — sprite_id of the left (lower-index) sprite during a swap (for arc direction)
- `_swap_right_id: int | None = None` — sprite_id of the right (higher-index) sprite during a swap
- `_current_op_type: OpType | None = None` — operation type of current animation

**Method: `_dispatch_tick(self, ctx: PanelContext) -> None`** (called when a new tick is detected):

1. Read `ctx.current_tick`. If `None`, return.
2. Get operation type from the tick.
3. **Highlight application:** Reset ALL sprites to `ColorState.DEFAULT`. If `tick.highlight_indices` is not None, set those sprites to `ColorState.ACTIVE`. Use `ctx.slot_to_sprite_id` to map slot indices to sprite IDs: `sprite_id = ctx.slot_to_sprite_id[slot_idx]`.
4. **Terminal handling:** If `OpType.TERMINAL`, set all sprites to `ColorState.COMPLETE`. No motion.
5. **Failure handling:** If `OpType.FAILURE`, set all sprites to `ColorState.ERROR`. No motion.
6. **Motion setup from sprite_moves:** For each `{sprite_id: new_slot}` in `ctx.sprite_moves`:
   - Record `start_x = sprite.exact_x` and `start_y = sprite.exact_y` in `_animating_sprites`.
   - Call `sprite.update_home(new_slot)` to set the new `home_x`.
7. **Swap arc setup:** If operation is `OpType.SWAP` and exactly 2 sprites are moving:
   - Determine which sprite has the lower target slot index → that's the "left" sprite (arcs UP).
   - The other is the "right" sprite (arcs DOWN).
   - Store their IDs in `_swap_left_id` and `_swap_right_id`.
8. **Duration:** Compute via `get_duration(tick.operation_type, ctx.sift_down_cadence)`. For TERMINAL/FAILURE, duration is 0.
9. Reset `_animation_elapsed_ms = 0`, set `_animation_duration_ms` and `_current_op_type`.
10. Store `_last_tick = ctx.current_tick`.

**Method: `update(self, dt: int, ctx: PanelContext) -> None`** (called every frame):

1. **New tick detection:** If `ctx.current_tick is not None and ctx.current_tick is not self._last_tick`, call `_dispatch_tick(ctx)`.
2. **Advance animation:** Only if `ctx.state == PanelState.ANIMATING_OPERATION` and `_animation_duration_ms > 0`:
   - `_animation_elapsed_ms += dt`
3. **Compute positions:** If `_animation_duration_ms > 0` and there are animating sprites:
   - `t = min(self._animation_elapsed_ms / self._animation_duration_ms, 1.0)`
   - `eased_t = ease_in_out_quad(t)`
   - For each `sprite_id, (start_x, start_y)` in `_animating_sprites`:
     - `sprite.exact_x = start_x + (sprite.home_x - start_x) * eased_t`
     - If this is a SWAP and sprite is `_swap_left_id`:
       - `arc_offset = self._arc_height * sine_arc(t)`
       - `sprite.exact_y = sprite.home_y - arc_offset` (arcs UP, above baseline)
     - If this is a SWAP and sprite is `_swap_right_id`:
       - `arc_offset = self._arc_height * sine_arc(t)`
       - `sprite.exact_y = sprite.home_y + arc_offset` (arcs DOWN, below baseline)
     - Else (SHIFT or other): `sprite.exact_y = start_y + (sprite.home_y - start_y) * eased_t`
   - If `t >= 1.0`: snap all animating sprites to their home positions, clear `_animating_sprites`, clear `_swap_left_id`/`_swap_right_id`.

**Method: `draw(self, surface: pygame.Surface) -> None`**:

1. Partition sprites into two lists: `baseline` (where `exact_y >= home_y` or equal) and `lifted` (where `exact_y < home_y`).
   - Include sprites arcing downward (`exact_y > home_y`) in the baseline group — they're below the row, not above.
2. Sort `baseline` by current slot position (use `home_x` as proxy for slot order).
3. Sort `lifted` by `exact_y` descending (so the highest sprite — smallest `exact_y` — draws LAST, on top).
4. Draw all `baseline` sprites first, then all `lifted` sprites.

**Method: `reset(self, initial_array: list[int]) -> None`**:

- Recreate all 7 `NumberSprite` instances from scratch with initial positions.
- Clear all animation state (`_last_tick`, `_animating_sprites`, `_swap_left_id`, etc.).

### 2.2 Modify `src/visualizer/main.py`

**Imports to add:**
```python
from visualizer.views.sprite_manager import SpriteManager
```

**After building panel renderers (around line 165), create sprite managers:**

```python
sprite_managers = [
    SpriteManager(
        panel_rect=layout.panel_rects[i],
        array_x_padding=layout.ARRAY_X_PADDING,
        slot_width=layout.slot_width,
        font=number_font,
        initial_array=INITIAL_ARRAY,
    )
    for i in range(4)
]
```

Note: rename `_number_font` to `number_font` (remove the leading underscore since it's now used).

**In the event loop — keyboard handling for Restart (K_r):**

After `orchestrator.restart()`, also reset all sprite managers:
```python
elif event.key == pygame.K_r:
    orchestrator.restart()
    for sm in sprite_managers:
        sm.reset(INITIAL_ARRAY)
```

**In the render loop — after draw_header, before display.flip:**

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
```

The `update` + `draw` calls go inside the per-panel loop, after the header is drawn, so sprites render on top of the panel background but within the panel bounds.

### 2.3 Imports in `sprite_manager.py`

The module needs:
```python
from visualizer.controllers.orchestrator import PanelContext, PanelState, get_duration
from visualizer.models.contracts import OpType, SortResult
from visualizer.views.easing import ease_in_out_quad, sine_arc
from visualizer.views.sprite import ColorState, NumberSprite
```

Note the cross-layer import: `sprite_manager.py` (view) imports `PanelContext` and `PanelState` from the controller. This is acceptable — the view reads controller state but does not mutate it. The MVC boundary is: controller provides state, view reads and renders.

## STEP 3 — VERIFICATION

Run all gates:

```bash
# Gate 1: Pyright
PYRIGHT_PYTHON_GLOBAL_NODE=false uv run pyright src/visualizer/views/sprite_manager.py src/visualizer/main.py

# Gate 2: Ruff
uv run ruff check src/visualizer/views/sprite_manager.py src/visualizer/main.py && uv run ruff format --check src/visualizer/views/sprite_manager.py src/visualizer/main.py

# Gate 3: Existing tests — no regressions
uv run pytest tests/ -q

# Gate 4: Import check — sprite_manager loads without error
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy uv run python -c "
from visualizer.views.sprite_manager import SpriteManager
print('SpriteManager imported OK')
"
```

All four must pass. Fix any issues before proceeding.

## STEP 4 — DEVLOG POST-ACTION

Append a post-action entry to `DEVLOG.md` immediately after the pre-action entry:

```markdown
## 2026-05-04 — Phase 7b closed: Sprite animation rendering (post-action)

### Worked on

[Describe what was actually created — file structure, key design choices, any deviations from the plan.]

### Corrections

[List any ruff/pyright corrections, or "Zero corrections" if clean on first run.]

### Results

- `uv run pyright src/visualizer/views/sprite_manager.py src/visualizer/main.py`: **[N] errors, [N] warnings**
- `uv run ruff check` + `uv run ruff format --check`: **[clean/N issues]**
- `uv run pytest tests/ -q`: **339/339 PASSED** (no regressions)
- Import check: **[PASS/FAIL]**

### Next

[What comes next — likely Phase 7c: per-algorithm choreography (Bubble compare-lift, Insertion key elevation, Heap tree layout).]
```

## Context files to read

Read these files before writing any code:

1. `CLAUDE.md` — Critical Rules (especially #1 sprite identity, #6 timing, #7 dt clamp)
2. `src/visualizer/views/sprite.py` — NumberSprite constructor, update_home(), set_color_state(), draw(), exact_x/exact_y, home_x/home_y, ColorState enum, COLOR_MAP
3. `src/visualizer/views/easing.py` — ease_in_out_quad(t), sine_arc(t)
4. `src/visualizer/controllers/orchestrator.py` — PanelContext fields (current_tick, sprite_moves, slot_to_sprite_id, state, sift_down_cadence, is_active), PanelState enum, get_duration()
5. `src/visualizer/models/contracts.py` — OpType enum, SortResult dataclass
6. `src/visualizer/main.py` — current render loop structure (modify, don't rewrite)
7. `docs/design_docs/12_ANIMATION_FOUNDATION.md` — §1 (sprite identity), §2.5 (interpolation/tweening), §3 (z-ordering), §4 (highlight behavior), §8 (swap arc contract)
8. `docs/design_docs/10_ANIMATION_SPEC.md` — §2 (interpolation rules), §3 (coordinate system), §4 (render order), §5.2 (Selection Sort arc swap — same model used by all swaps in Phase 7b)

---
