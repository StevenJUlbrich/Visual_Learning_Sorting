# Phase 7c-3 — Insertion Sort Choreography

## Copy everything below this line into Claude Code

---

You are implementing Phase 7c-3 of the Sorting Algorithm Visualizer. This phase adds Insertion Sort's unique visual signature: the **Key-Lift, Sequential Shift, Diagonal Drop** sequence. The key sprite lifts above baseline and stays elevated across multiple ticks (persistent cross-tick state), baseline elements shift horizontally beneath it, and the key swoops diagonally to its insertion point. A "KEY" label floats above the elevated sprite.

After this phase, the Insertion Sort panel (panel index 2) will show the key extracting upward, elements sliding right beneath it one-by-one, and the key dropping diagonally into the gap — the defining visual signature of Insertion Sort.

## Rules

- Do NOT run any git commands.
- Do NOT create new spec or documentation files.
- Do NOT modify `orchestrator.py`, `sprite.py`, `easing.py`, `panel.py`, `window.py`, `pointer.py`, `limitline.py`, `hud.py`, `tree_layout.py`, or any model file.
- Only modify `src/visualizer/views/sprite_manager.py` and `src/visualizer/main.py`.
- All four lint/typecheck/test gates must pass before you stop.

## Scope — what is IN Phase 7c-3

1. **Insertion Sort persistent cross-tick state** — the key sprite stays elevated across multiple ticks until placement.
2. **Key Selection (T1 COMPARE, single-index highlight)** — sprite at `(i,)` lifts to `home_y - lift_offset` over 150ms. KEY label appears. Sprite stays elevated.
3. **Compare during shift loop (T1 COMPARE, two-index highlight)** — highlight only, no motion. Key stays elevated.
4. **Shift (T2 SHIFT, two-index highlight)** — only the baseline sprite animates (horizontal slide right). Key sprite does NOT move. Gap migrates implicitly.
5. **Placement (T2 SHIFT, single-index highlight)** — key sprite eases both axes simultaneously (diagonal drop) to destination slot over 400ms. KEY label disappears.
6. **KEY label** — orange "KEY" text rendered above the elevated key sprite.
7. **Force-ACTIVE color on key** — key sprite stays orange while elevated, even when not in the current tick's `highlight_indices`.
8. **InsertionOverlay class** — draws the KEY label above the key sprite. Receives position via SpriteManager property.
9. **Wire into `main.py`** — create InsertionOverlay for panel 2, read key position each frame, draw label, reset on K_r.

## Scope — what is DEFERRED (do NOT implement)

- Heap Sort tree layout, extraction arc, boundary sweep, phase/boundary labels
- Sorted-boundary color transition (green-to-blue) — the contract says this is communicated through color, but the model doesn't emit per-sprite color ticks for this. Deferred to a polish pass.
- Unit tests for InsertionOverlay or the Insertion choreography methods (visual verification only)

## STEP 1 — DEVLOG PRE-ACTION

Append the following entry to `DEVLOG.md`:

```markdown
## 2026-05-05 — Phase 7c-3 pre-action: Insertion Sort choreography

### Plan

Add Insertion Sort's cross-tick key elevation to SpriteManager. Key selection T1 (single-index highlight) lifts the key sprite to home_y - lift_offset (panel_height * 0.06) and holds it there across subsequent compare and shift ticks. Shift T2 (two-index) animates only the baseline sprite horizontally; the key stays elevated and is excluded from _animating_sprites. Placement T2 (single-index) triggers a diagonal drop — both axes eased simultaneously. Force key to ACTIVE (orange) on every tick while elevated. Create InsertionOverlay for the KEY label. Wire into main.py for panel 2.

### Exit criteria

1. pyright — 0 errors, 0 warnings
2. ruff check + ruff format — clean
3. Existing test suite — 339/339 still passing (no regressions)
4. Visual: Insertion Sort key lifts, stays elevated during shifts, drops diagonally, KEY label visible
```

## STEP 2 — IMPLEMENTATION

### 2.1 Understanding the tick data shapes

The Insertion Sort model (`src/visualizer/models/insertion.py`) yields these tick patterns per pass:

| Tick | OpType | highlight_indices | sprite_moves | Meaning |
|------|--------|-------------------|-------------|---------|
| Key Selection | COMPARE | `(i,)` — 1 element | `{}` empty | Key extracted |
| Shift-loop Compare | COMPARE | `(j, j+1)` — 2 elements | `{}` empty | Comparing against key |
| Shift | SHIFT | `(j, j+1)` — 2 elements | `{sprite_a: idx, sprite_b: idx-1}` — 2 entries | Element slides right |
| Terminating Compare | COMPARE | `(j, j+1)` — 2 elements | `{}` empty | Why key stops here |
| Placement | SHIFT | `(j+1,)` — 1 element | `{}` empty | Key drops to gap |

**Critical distinction:** Both shift and placement are `OpType.SHIFT`. Differentiate by `len(highlight_indices)`: 2 = shift-loop, 1 = placement.

**Critical note on sprite_moves during shifts:** `compute_sprite_moves` swaps BOTH the shifted sprite AND the key sprite in the slot mapping. For shifts: `{shifted_sprite: new_slot, key_sprite: shifted_sprite_old_slot}`. The key sprite's slot index decreases by 1 each shift. You MUST call `update_home` for both sprites (so the slot mapping stays correct), but only animate the shifted sprite. The key sprite's `home_x` updates but its `exact_x`/`exact_y` stay at the elevated position.

### 2.2 SpriteManager — new fields in `__init__`

Add these fields after `self._current_op_type`:

```python
# Insertion Sort cross-tick state
self._insertion_lift_offset: float = panel_rect.height * 0.06
self._insertion_key_id: int | None = None
self._insertion_key_elevated: bool = False
self._insertion_is_placement: bool = False
```

### 2.3 SpriteManager — update `_dispatch_tick` with Insertion branch and key color force

Two changes to `_dispatch_tick`:

**A) Add key-color force after highlight application:**

After the highlight application block (the `for slot_idx in tick.highlight_indices` loop) and BEFORE the terminal/failure check, add:

```python
# Force key sprite to ACTIVE (orange) while elevated — Insertion Sort cross-tick state.
# This overrides the default highlight reset so the key stays orange during
# compare/shift ticks where it's not in highlight_indices.
if self._insertion_key_elevated and self._insertion_key_id is not None:
    self._sprites[self._insertion_key_id].set_color_state(ColorState.ACTIVE)
```

**B) Add Insertion Sort branch in the algorithm dispatch:**

Change the dispatch block from:

```python
if self._algorithm_name == "Bubble Sort":
    self._dispatch_bubble(tick, ctx, op)
else:
    self._dispatch_default(tick, ctx, op)
```

To:

```python
if self._algorithm_name == "Bubble Sort":
    self._dispatch_bubble(tick, ctx, op)
elif self._algorithm_name == "Insertion Sort":
    self._dispatch_insertion(tick, ctx, op)
else:
    self._dispatch_default(tick, ctx, op)
```

### 2.4 SpriteManager — `_dispatch_insertion` method

```python
def _dispatch_insertion(
    self, tick: SortResult, ctx: PanelContext, op: OpType
) -> None:
    """Insertion Sort motion setup: key-lift, shift exclusion, diagonal drop."""
    self._animating_sprites = {}
    self._swap_left_id = None
    self._swap_right_id = None
    self._insertion_is_placement = False

    hi = tick.highlight_indices

    if op == OpType.COMPARE:
        if hi is not None and len(hi) == 1:
            # --- Key Selection: lift the key sprite ---
            slot_idx = hi[0]
            sprite_id = ctx.slot_to_sprite_id[slot_idx]
            sprite = self._sprites[sprite_id]
            self._insertion_key_id = sprite_id
            self._insertion_key_elevated = True
            self._animating_sprites[sprite_id] = (sprite.exact_x, sprite.exact_y)
            # Target y is home_y - lift_offset (computed in _compute_insertion_positions)
        # Two-index COMPARE (shift-loop or terminating): highlight only, no motion.
        # Key stays elevated via cross-tick state. No _animating_sprites needed.

    elif op == OpType.SHIFT:
        if hi is not None and len(hi) == 2:
            # --- Shift: animate shifted sprite right, key stays elevated ---
            for sprite_id, new_slot in ctx.sprite_moves.items():
                sprite = self._sprites[sprite_id]
                sprite.update_home(new_slot)  # Update home_x for BOTH sprites
                # Only animate the NON-key sprite
                if sprite_id != self._insertion_key_id:
                    self._animating_sprites[sprite_id] = (sprite.exact_x, sprite.exact_y)
            # The key sprite's home_x updated (for eventual drop target)
            # but its exact_x/exact_y stay at elevated position — not in _animating_sprites.

        elif hi is not None and len(hi) == 1:
            # --- Placement: diagonal drop for key sprite ---
            self._insertion_is_placement = True
            if self._insertion_key_id is not None:
                sprite = self._sprites[self._insertion_key_id]
                self._animating_sprites[self._insertion_key_id] = (
                    sprite.exact_x,
                    sprite.exact_y,
                )
                # home_x is already at the destination slot (updated during shifts).
                # home_y is baseline — the y target for the drop.
            self._insertion_key_elevated = False
```

**Key design notes:**
- For shifts, `update_home` is called for BOTH sprites in `sprite_moves` (so slot tracking stays correct), but only the non-key sprite is added to `_animating_sprites`.
- For placement, `sprite_moves` is empty (the orchestrator's `compute_sprite_moves` returns `{}` for placement). The key sprite's `home_x` was already set to the correct destination during the preceding shifts. The animation eases from the current (elevated) position to `(home_x, home_y)`.
- `_insertion_key_elevated` is set to False at placement dispatch time, so the key-color force stops on the NEXT tick. During the placement animation itself, the key still renders as ACTIVE (orange) because the tick's `highlight_indices = (destination,)` includes it.

### 2.5 SpriteManager — update `update()` position branch

Change the position computation block from:

```python
if self._algorithm_name == "Bubble Sort":
    self._compute_bubble_positions()
else:
    self._compute_default_positions()
```

To:

```python
if self._algorithm_name == "Bubble Sort":
    self._compute_bubble_positions()
elif self._algorithm_name == "Insertion Sort":
    self._compute_insertion_positions()
else:
    self._compute_default_positions()
```

### 2.6 SpriteManager — `_compute_insertion_positions` method

```python
def _compute_insertion_positions(self) -> None:
    """Insertion Sort motion: key lift (T1), horizontal shift (T2), diagonal drop (T2)."""
    elapsed = self._animation_elapsed_ms
    duration = self._animation_duration_ms
    t = min(elapsed / duration, 1.0)
    eased_t = ease_in_out_quad(t)

    if self._current_op_type == OpType.COMPARE:
        # Key selection lift: ease y from home_y to home_y - lift_offset
        for sprite_id, (start_x, start_y) in self._animating_sprites.items():
            sprite = self._sprites[sprite_id]
            sprite.exact_x = start_x  # No horizontal motion
            target_y = sprite.home_y - self._insertion_lift_offset
            sprite.exact_y = start_y + (target_y - start_y) * eased_t

    elif self._current_op_type == OpType.SHIFT:
        if self._insertion_is_placement:
            # Diagonal drop: ease BOTH x and y simultaneously
            for sprite_id, (start_x, start_y) in self._animating_sprites.items():
                sprite = self._sprites[sprite_id]
                sprite.exact_x = start_x + (sprite.home_x - start_x) * eased_t
                sprite.exact_y = start_y + (sprite.home_y - start_y) * eased_t
        else:
            # Horizontal shift: baseline sprite slides right at home_y
            for sprite_id, (start_x, start_y) in self._animating_sprites.items():
                sprite = self._sprites[sprite_id]
                sprite.exact_x = start_x + (sprite.home_x - start_x) * eased_t
                sprite.exact_y = start_y  # Stay at home_y

    # --- Snap on completion ---
    if t >= 1.0:
        if self._current_op_type == OpType.COMPARE and self._insertion_key_elevated:
            # Key selection complete: snap to ELEVATED position, NOT home_y.
            # The key must stay above baseline until placement.
            for sprite_id in self._animating_sprites:
                sprite = self._sprites[sprite_id]
                sprite.exact_x = sprite.home_x
                sprite.exact_y = sprite.home_y - self._insertion_lift_offset
            self._animating_sprites = {}
        else:
            # Shift or placement complete: snap to home
            for sprite_id in self._animating_sprites:
                sprite = self._sprites[sprite_id]
                sprite.exact_x = sprite.home_x
                sprite.exact_y = sprite.home_y
            self._animating_sprites = {}
            # Clear key state after placement
            if self._insertion_is_placement:
                self._insertion_key_id = None
```

**Critical: the key selection snap.** When the key lift animation completes (t >= 1.0), the sprite must snap to `home_y - lift_offset`, NOT to `home_y`. If it snapped to `home_y`, the key would drop back down immediately. The elevated position must persist until placement.

### 2.7 SpriteManager — `insertion_key_info` property

Add this property to SpriteManager (after the `draw` method, before `reset`):

```python
@property
def insertion_key_info(self) -> tuple[float, float, int] | None:
    """Return (exact_x, exact_y, ring_radius) of the elevated key sprite, or None."""
    if self._insertion_key_elevated and self._insertion_key_id is not None:
        sprite = self._sprites[self._insertion_key_id]
        return (sprite.exact_x, sprite.exact_y, sprite.ring_radius)
    return None
```

This exposes the key sprite's position for external rendering (KEY label) without exposing SpriteManager internals.

### 2.8 SpriteManager — update `reset()`

Add insertion state clearing at the end of the `reset` method:

```python
self._insertion_key_id = None
self._insertion_key_elevated = False
self._insertion_is_placement = False
```

### 2.9 Create `InsertionOverlay` class in `sprite_manager.py`

Add this class after `BubbleOverlay`, at the bottom of the file:

```python
class InsertionOverlay:
    """Draws the 'KEY' label above the elevated key sprite for Insertion Sort."""

    _LABEL_COLOR: tuple[int, int, int] = (255, 140, 0)  # Active orange
    _LABEL_GAP: int = 6  # pixels between ring top and label bottom

    def __init__(self, body_font: pygame.font.Font) -> None:
        self._font = body_font
        self._label_surface: pygame.Surface = body_font.render("KEY", True, self._LABEL_COLOR)

    def draw(
        self,
        surface: pygame.Surface,
        key_info: tuple[float, float, int] | None,
    ) -> None:
        """Draw the KEY label above the key sprite if it is elevated.

        key_info: (exact_x, exact_y, ring_radius) from SpriteManager.insertion_key_info.
        """
        if key_info is None:
            return
        key_x, key_y, ring_radius = key_info
        label_rect = self._label_surface.get_rect(
            centerx=round(key_x),
            bottom=round(key_y) - ring_radius - self._LABEL_GAP,
        )
        surface.blit(self._label_surface, label_rect)
```

The label surface is pre-rendered once in `__init__` (body_font, orange color). `draw()` just positions and blits it. No state tracking needed — the label is purely driven by `key_info` being non-None.

### 2.10 Modify `src/visualizer/main.py`

**Update imports:**

```python
from visualizer.views.sprite_manager import (
    BubbleOverlay,
    InsertionOverlay,
    SelectionOverlay,
    SpriteManager,
)
```

**Create InsertionOverlay** — after the BubbleOverlay creation block, before `orchestrator`:

```python
# Insertion Sort KEY label overlay (panel index 2)
insertion_overlay = InsertionOverlay(body_font)
```

**Wire into the render loop** — add overlay call for panel 2, alongside existing overlays:

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

    # Insertion Sort KEY label (panel index 2)
    if i == 2:
        insertion_overlay.draw(surface, sprite_managers[i].insertion_key_info)
```

Note: `InsertionOverlay` has no `update()` or `reset()` methods — it's stateless, purely driven by `insertion_key_info`. No restart wiring needed.

## STEP 3 — VERIFICATION

Run all gates:

```bash
# Gate 1: Pyright
PYRIGHT_PYTHON_GLOBAL_NODE=false uv run pyright src/visualizer/views/sprite_manager.py src/visualizer/main.py

# Gate 2: Ruff
uv run ruff check src/visualizer/views/sprite_manager.py src/visualizer/main.py && uv run ruff format --check src/visualizer/views/sprite_manager.py src/visualizer/main.py

# Gate 3: Existing tests — no regressions
uv run pytest tests/ -q

# Gate 4: Import check — InsertionOverlay loads without error
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy uv run python -c "
from visualizer.views.sprite_manager import SpriteManager, SelectionOverlay, BubbleOverlay, InsertionOverlay
print('All imports OK')
print('insertion_key_info is property:', hasattr(SpriteManager, 'insertion_key_info'))
"
```

All four must pass. Fix any issues before proceeding.

## STEP 4 — DEVLOG POST-ACTION

Append a post-action entry to `DEVLOG.md` immediately after the pre-action entry:

```markdown
## 2026-05-05 — Phase 7c-3 closed: Insertion Sort choreography (post-action)

### Worked on

[Describe what was actually created — _dispatch_insertion, _compute_insertion_positions, insertion_key_info property, InsertionOverlay class, main.py wiring. Note the cross-tick key elevation, shift exclusion pattern, diagonal drop, key-color force. Any deviations from the plan.]

### Corrections

[List any ruff/pyright corrections, or "Zero corrections" if clean on first run.]

### Results

- `uv run pyright src/visualizer/views/sprite_manager.py src/visualizer/main.py`: **[N] errors, [N] warnings**
- `uv run ruff check` + `uv run ruff format --check`: **[clean/N issues]**
- `uv run pytest tests/ -q`: **339/339 PASSED** (no regressions)
- Import check: **[PASS/FAIL]**

### Next

Phase 7c-4: Heap Sort choreography (TreeLayout integration, parent-child edges, extraction arc, boundary sweep, sorted row, phase/boundary labels).
```

## Context files to read

Read these files before writing any code:

1. `CLAUDE.md` — Critical Rules (especially #1 sprite identity, #4 Insertion Sort shifts one-at-a-time, #5 universal orange, #6 timing)
2. `src/visualizer/views/sprite_manager.py` — **Read the ENTIRE file (423 lines).** Current SpriteManager with `_dispatch_tick`, `_dispatch_default`, `_dispatch_bubble`, `_compute_default_positions`, `_compute_bubble_positions`, `update`, `draw`, `reset`, plus `SelectionOverlay` and `BubbleOverlay`. Your changes add Insertion-specific methods alongside the existing Bubble-specific ones.
3. `src/visualizer/main.py` — **Read the ENTIRE file (281 lines).** Current render loop with SelectionOverlay (panel 1) and BubbleOverlay (panel 0). Your changes add InsertionOverlay for panel 2.
4. `src/visualizer/models/insertion.py` — The tick sequence: key-selection T1 `(i,)`, compare T1 `(j, j+1)`, shift T2 `(j, j+1)`, terminating compare T1 `(j, j+1)`, placement T2 `(j+1,)`. Placement uses OpType.SHIFT with single-index highlight.
5. `src/visualizer/controllers/orchestrator.py` — `compute_sprite_moves()`: for 1-change shifts, returns `{sprite_a: idx, sprite_b: idx-1}` (both shifted sprite AND key sprite swap in the mapping). For placement, returns `{}` (empty).
6. `docs/contracts/INSERTION_SORT_ANIMATION.md` — §4 (Key Selection — lift offset, sustained state), §5 (Compare-and-Shift — sequential, horizontal-only), §7 (Placement — diagonal drop, both axes), §8 (z-ordering — key on top always)
7. `docs/design_docs/12_ANIMATION_FOUNDATION.md` — §5 (compare lane: Insertion lift_offset = panel_height * 0.06), §6 (cross-tick persistent state — key elevation lifecycle)

---
