# Phase 7c-4 — Heap Sort Choreography

## Copy everything below this line into Claude Code

---

You are implementing Phase 7c-4 of the Sorting Algorithm Visualizer. This is the final and most complex choreography sub-phase. Heap Sort uses a **dual-zone layout**: active heap elements are positioned in a binary tree (top zone) and extracted elements land in a sorted row (bottom zone). This phase integrates the pre-built `TreeLayout` geometry module, adds tree-aware arc swaps, extraction arcs (1.75× height), staggered boundary sweep coloring, steel-blue extracted state, parent-child edge rendering, and a `HeapOverlay` class for visual assets (edges, phase label, boundary marker, placeholder outlines).

After this phase, the Heap Sort panel (panel index 3) will display a binary tree that sifts down with crossing arcs, extracts roots with dramatic elevated arcs into a growing sorted row below, and shows edges, labels, and visual markers that communicate the heap's structure.

## Rules

- Do NOT run any git commands.
- Do NOT create new spec or documentation files.
- Do NOT modify `orchestrator.py`, `sprite.py`, `easing.py`, `panel.py`, `window.py`, `pointer.py`, `limitline.py`, `hud.py`, `tree_layout.py`, or any model file.
- Only modify `src/visualizer/views/sprite_manager.py` and `src/visualizer/main.py`.
- All four lint/typecheck/test gates must pass before you stop.

## Scope — what is IN Phase 7c-4

1. **SpriteManager: `tree_layout` constructor parameter** — `TreeLayout | None`, default `None`. Only the Heap Sort panel passes a TreeLayout instance.
2. **SpriteManager: Heap Sort __init__ state** — `_heap_size`, `_heap_node_positions`, `_extraction_arc_height`, `_is_extraction_swap`, `_heap_sweep_indices`. Initial position override for sprites → tree node positions.
3. **SpriteManager: `_dispatch_heap` method** — handles all Heap Sort tick types: T3 Boundary (sweep setup), T3 Logical Tree (no motion), T1 Compare (no motion), T2 Swap (sift-down arc or extraction arc).
4. **SpriteManager: `_compute_heap_positions` method** — 2D arc interpolation between tree/sorted-row positions. Standard arc for sift-down, elevated arc for extraction.
5. **SpriteManager: `_apply_heap_sweep` method** — staggered coloring during Boundary T3 (120ms sweep window + 80ms hold).
6. **SpriteManager: steel-blue persistence** — extracted sprites set to `ColorState.SETTLED` and re-forced after shared highlight resets.
7. **SpriteManager: `_draw_heap` method** — tree-specific z-ordering (sorted row → tree by depth → arcing sprites on top).
8. **SpriteManager: `heap_size` property** — exposes current heap size for HeapOverlay.
9. **HeapOverlay class** in `sprite_manager.py` — draws parent-child edges, phase label, boundary marker, sorted-row placeholder outlines.
10. **main.py wiring** — TreeLayout construction, HeapOverlay creation, render loop integration for panel 3 with split draw (draw_under before sprites, draw_over after).
11. **Restart handling** — `heap_overlay.reset()` called on K_r.

## Scope — what is DEFERRED (do NOT implement)

- Unit tests for HeapOverlay or Heap Sort choreography (visual verification only)
- Tree node resize animation when heap shrinks (snap repositioning is acceptable)
- Any changes to model files, orchestrator, or pre-built view modules

## STEP 1 — DEVLOG PRE-ACTION

Append the following entry to `DEVLOG.md`:

```markdown
## 2026-05-05 — Phase 7c-4 pre-action: Heap Sort choreography

### Plan

Integrate TreeLayout into SpriteManager for the Heap Sort panel (index 3). Override sprite home positions from flat baseline to binary tree layout + sorted row. Add `_dispatch_heap` for tree-aware tick handling: Boundary T3 with staggered sweep, Logical Tree T3 simultaneous flash, sift-down standard arcs, extraction elevated arcs (1.75×), steel-blue extracted coloring. Create HeapOverlay class for parent-child edges (with active orange highlighting during Logical Tree T3), phase label (BUILD MAX-HEAP / EXTRACTION), sorted-row placeholder outlines, and heap boundary marker. Wire into main.py with split draw order (edges before sprites, labels after).

### Exit criteria

1. pyright — 0 errors, 0 warnings
2. ruff check + ruff format — clean
3. Existing test suite — 339/339 still passing (no regressions)
4. Visual: Heap Sort panel shows binary tree with sifting arcs, extraction arcs to sorted row, edges, phase label, boundary marker
```

## STEP 2 — IMPLEMENTATION

### 2.1 New imports in `sprite_manager.py`

Add these to the existing import block:

```python
from visualizer.views.hud import BubbleHUD, HeapBoundaryLabel, HeapPhaseLabel
from visualizer.views.tree_layout import (
    ACTIVE_EDGE_COLOR,
    DEFAULT_EDGE_COLOR,
    EDGE_WIDTH,
    PLACEHOLDER_COLOR,
    TreeLayout,
)
```

Update the `BubbleHUD` import line to also import `HeapBoundaryLabel` and `HeapPhaseLabel`. Import `TreeLayout` and the four color/width constants from `tree_layout.py`.

### 2.2 `SpriteManager.__init__` — add `tree_layout` parameter + Heap Sort fields

Add `tree_layout: TreeLayout | None = None` as the **last** parameter (after `initial_array`):

```python
def __init__(
    self,
    algorithm_name: str,
    panel_rect: pygame.Rect,
    array_x_padding: int,
    slot_width: float,
    font: pygame.font.Font,
    initial_array: list[int],
    tree_layout: TreeLayout | None = None,
) -> None:
```

Add these fields after the existing Insertion Sort cross-tick state fields:

```python
# Heap Sort state
self._tree_layout: TreeLayout | None = tree_layout
self._heap_size: int = len(initial_array)
self._heap_node_positions: list[tuple[float, float]] = []
self._extraction_arc_height: float = panel_rect.height * 0.14
self._is_extraction_swap: bool = False
self._heap_sweep_indices: tuple[int, ...] | None = None
```

Then, at the **end** of `__init__`, add the initial position override for Heap Sort:

```python
# Override sprite positions for Heap Sort — tree layout instead of flat baseline
if algorithm_name == "Heap Sort" and tree_layout is not None:
    self._heap_node_positions = tree_layout.node_positions(len(initial_array))
    tree_radius = tree_layout.tree_node_radius
    for i, sprite in enumerate(self._sprites):
        pos = self._heap_node_positions[i]
        sprite.home_x = pos[0]
        sprite.home_y = pos[1]
        sprite.exact_x = pos[0]
        sprite.exact_y = pos[1]
        sprite.ring_radius = tree_radius
```

**Why:** All 7 sprites start at tree node positions on the first frame. `ring_radius` is overridden to `tree_node_radius` (which uses `TREE_NODE_DIAMETER_RATIO = 0.55`, smaller than the flat `RING_DIAMETER_RATIO = 0.65`) to prevent overlap in the tree.

### 2.3 `_dispatch_tick` — add Heap Sort branch + sorted-row color force

In the algorithm-specific dispatch section, add a `"Heap Sort"` branch:

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

### 2.4 `_dispatch_heap` method

Add this method after `_dispatch_insertion`. This is the core Heap Sort tick handler.

```python
def _dispatch_heap(self, tick: SortResult, ctx: PanelContext, op: OpType) -> None:
    """Heap Sort motion setup: tree swaps, extraction arcs, boundary sweep."""
```

**Structure:**

1. Clear animation state at the top (same pattern as other dispatch methods):
   ```python
   self._animating_sprites = {}
   self._swap_left_id = None
   self._swap_right_id = None
   self._is_extraction_swap = False
   self._heap_sweep_indices = None
   ```

2. **Handle `OpType.RANGE` — discriminate Boundary T3 vs Logical Tree T3:**

   Use the tick message prefix per D-081:
   - Boundary T3: `tick.message.startswith("Active heap")`
   - Logical Tree T3: all other RANGE ticks (message starts with `"Evaluating tree level"`)

   **Boundary T3 (sweep setup):**
   ```python
   if op == OpType.RANGE:
       hi = tick.highlight_indices
       if tick.message.startswith("Active heap"):
           # Boundary T3 — staggered sweep: reset highlights, sweep applies progressively
           self._heap_sweep_indices = hi
           for sprite in self._sprites:
               sprite.set_color_state(ColorState.DEFAULT)
           # Re-apply steel-blue for sorted-row sprites
           self._apply_sorted_settled(ctx)
       # Logical Tree T3: shared highlight code already set parent+children to ACTIVE.
       # No motion for any RANGE tick.
   ```

   **Why reset highlights for sweep:** The shared highlight code in `_dispatch_tick` already set all boundary indices to ACTIVE. The sweep overrides this — reset to DEFAULT and let `_apply_heap_sweep` progressively re-apply ACTIVE based on elapsed time.

   **Why no explicit Logical Tree T3 handling:** The shared highlight code correctly sets all highlighted indices (parent + children) to ACTIVE simultaneously. No motion occurs. The edge highlighting is handled by HeapOverlay.

3. **Handle `OpType.COMPARE` — no action needed:**

   T1 compares are highlight-only. The shared code handles highlights. No motion for Heap Sort compares.

4. **Handle `OpType.SWAP` — sift-down or extraction:**

   ```python
   elif op == OpType.SWAP:
       hi = tick.highlight_indices
       # Record start positions FIRST
       for sprite_id, new_slot in ctx.sprite_moves.items():
           sprite = self._sprites[sprite_id]
           self._animating_sprites[sprite_id] = (sprite.exact_x, sprite.exact_y)

       # Detect extraction swap: one of the highlighted indices is 0
       is_extraction = hi is not None and 0 in hi
       self._is_extraction_swap = is_extraction

       if is_extraction:
           # Decrement heap size BEFORE computing target positions
           self._heap_size -= 1
           self._recompute_heap_positions()
           # Snap non-swapping tree sprites to new positions (tree geometry changed)
           for slot in range(self._heap_size):
               sid = ctx.slot_to_sprite_id[slot]
               if sid not in self._animating_sprites:
                   pos = self._heap_node_positions[slot]
                   self._sprites[sid].home_x = pos[0]
                   self._sprites[sid].home_y = pos[1]
                   self._sprites[sid].exact_x = pos[0]
                   self._sprites[sid].exact_y = pos[1]

       # Set target homes for swapping sprites
       for sprite_id, new_slot in ctx.sprite_moves.items():
           self._set_heap_home(self._sprites[sprite_id], new_slot)

       # Arc direction assignment
       if len(self._animating_sprites) == 2:
           if is_extraction:
               # Extraction: root sprite arcs UP, end sprite arcs DOWN
               for sprite_id, new_slot in ctx.sprite_moves.items():
                   if new_slot != 0:
                       self._swap_left_id = sprite_id   # arcs up (root → sorted row)
                   else:
                       self._swap_right_id = sprite_id   # arcs down (end → root)
           else:
               # Sift-down: lower target slot arcs up (child→parent), higher arcs down
               ids = list(ctx.sprite_moves.keys())
               if ctx.sprite_moves[ids[0]] < ctx.sprite_moves[ids[1]]:
                   self._swap_left_id = ids[0]
                   self._swap_right_id = ids[1]
               else:
                   self._swap_left_id = ids[1]
                   self._swap_right_id = ids[0]

       # Re-apply steel-blue for sorted-row sprites
       self._apply_sorted_settled(ctx)
   ```

   **Why snap non-swapping sprites during extraction:** When `heap_size` decrements, `TreeLayout.node_positions(new_size)` may return different positions for the same indices (particularly when the tree depth decreases, e.g., 4→3 crosses a depth boundary). Snapping during the extraction arc's start frame prevents stale positions during the subsequent sift-down.

   **Extraction arc direction:** The spec (§5 and doc 10 §5.4) requires "Left sprite (index 0) arcs upward." The root sprite goes to the sorted row (higher slot index), but must arc UP. The assignment is based on SOURCE position (root), not target slot. `swap_left` = root (arcs up), `swap_right` = end (arcs down).

### 2.5 `_set_heap_home` helper

```python
def _set_heap_home(self, sprite: NumberSprite, slot: int) -> None:
    """Set sprite's home position based on tree (slot < heap_size) or sorted row."""
    if self._tree_layout is None:
        return
    if slot < self._heap_size:
        pos = self._heap_node_positions[slot]
        sprite.home_x = pos[0]
        sprite.home_y = pos[1]
    else:
        sprite.home_x = self._tree_layout.sorted_row_x(slot)
        sprite.home_y = self._tree_layout.sorted_row_y
```

### 2.6 `_recompute_heap_positions` helper

```python
def _recompute_heap_positions(self) -> None:
    """Recompute cached tree node positions for current heap_size."""
    if self._tree_layout is not None:
        self._heap_node_positions = self._tree_layout.node_positions(self._heap_size)
```

### 2.7 `_apply_sorted_settled` helper

```python
def _apply_sorted_settled(self, ctx: PanelContext) -> None:
    """Force ColorState.SETTLED for all sprites in the sorted row (slot >= heap_size)."""
    for slot in range(self._heap_size, len(self._sprites)):
        sprite_id = ctx.slot_to_sprite_id[slot]
        self._sprites[sprite_id].set_color_state(ColorState.SETTLED)
```

**Why this is needed:** The shared highlight code in `_dispatch_tick` resets ALL sprites to DEFAULT before applying new highlights. Extracted sprites must stay steel-blue across ticks. This re-applies SETTLED after each shared reset. Called at the end of `_dispatch_heap` for RANGE and SWAP ticks.

### 2.8 `_compute_heap_positions` method

Add in the position computation section. This uses **2D arc interpolation** — both x and y ease from start to target, with a vertical arc offset applied on top.

```python
def _compute_heap_positions(self) -> None:
    """Heap Sort motion: 2D ease with vertical arc offset for swaps."""
    t = min(self._animation_elapsed_ms / self._animation_duration_ms, 1.0)
    eased_t = ease_in_out_quad(t)

    arc_height = (
        self._extraction_arc_height if self._is_extraction_swap else self._arc_height
    )

    for sprite_id, (start_x, start_y) in self._animating_sprites.items():
        sprite = self._sprites[sprite_id]
        # Base interpolation: ease both axes from start to home
        base_x = start_x + (sprite.home_x - start_x) * eased_t
        base_y = start_y + (sprite.home_y - start_y) * eased_t
        # Vertical arc offset
        arc_offset = arc_height * sine_arc(t)
        if sprite_id == self._swap_left_id:
            sprite.exact_x = base_x
            sprite.exact_y = base_y - arc_offset    # arcs up
        elif sprite_id == self._swap_right_id:
            sprite.exact_x = base_x
            sprite.exact_y = base_y + arc_offset    # arcs down
        else:
            sprite.exact_x = base_x
            sprite.exact_y = base_y

    if t >= 1.0:
        for sprite_id in self._animating_sprites:
            s = self._sprites[sprite_id]
            s.exact_x = s.home_x
            s.exact_y = s.home_y
        # Steel-blue for extracted sprite landing in sorted row
        if self._is_extraction_swap and self._swap_left_id is not None:
            self._sprites[self._swap_left_id].set_color_state(ColorState.SETTLED)
        self._animating_sprites = {}
        self._swap_left_id = None
        self._swap_right_id = None
        self._is_extraction_swap = False
```

**Why 2D arc differs from flat-baseline default:** In `_compute_default_positions`, the y arc uses `sprite.home_y ± arc_offset` directly because all sprites share the same baseline `home_y`. In the tree, start_y ≠ home_y (parent and child are at different depths), so we interpolate both axes and add the arc on top of the interpolated base path. At t=0.5 the arc peaks; at t=1.0 it returns to zero and sprites land at their targets.

**Extraction arc height:** `panel_height * 0.14` (1.75× standard `panel_height * 0.08`) per doc 10 §5.4 and HEAP_SORT_ANIMATION.md §5.2. This creates the dramatic upward lift before the root descends into the sorted row.

### 2.9 `_apply_heap_sweep` method

Add after the position computation block in `update()`:

```python
# Heap Sort boundary sweep coloring
if (
    self._algorithm_name == "Heap Sort"
    and self._heap_sweep_indices is not None
    and self._animation_duration_ms > 0
):
    self._apply_heap_sweep(ctx)
```

The method itself:

```python
def _apply_heap_sweep(self, ctx: PanelContext) -> None:
    """Staggered sweep: progressively highlight active heap indices during Boundary T3."""
    if self._heap_sweep_indices is None:
        return
    elapsed = self._animation_elapsed_ms
    end = len(self._heap_sweep_indices) - 1
    if end <= 0:
        # Single element — highlight immediately
        for slot_idx in self._heap_sweep_indices:
            sid = ctx.slot_to_sprite_id[slot_idx]
            self._sprites[sid].set_color_state(ColorState.ACTIVE)
    else:
        sweep_window = 120.0
        for i, slot_idx in enumerate(self._heap_sweep_indices):
            delay = (i / end) * sweep_window
            if elapsed >= delay:
                sid = ctx.slot_to_sprite_id[slot_idx]
                self._sprites[sid].set_color_state(ColorState.ACTIVE)
    # Clear sweep state when animation completes
    t = min(elapsed / self._animation_duration_ms, 1.0)
    if t >= 1.0:
        self._heap_sweep_indices = None
```

**Timing per doc 10 §5.4.1:** Total T3 = 200ms. Sweep window = 120ms (indices stagger left-to-right). Hold = remaining 80ms (all indices ACTIVE together). Per-index delay = `(i / end) * 120ms`. Each index snaps to ACTIVE at its delay threshold — no per-index easing.

### 2.10 `update()` — add Heap Sort branch

In the position computation `if` chain, add Heap Sort:

```python
if self._animation_duration_ms > 0 and self._animating_sprites:
    if self._algorithm_name == "Bubble Sort":
        self._compute_bubble_positions()
    elif self._algorithm_name == "Insertion Sort":
        self._compute_insertion_positions()
    elif self._algorithm_name == "Heap Sort":
        self._compute_heap_positions()
    else:
        self._compute_default_positions()
```

### 2.11 `draw()` — Heap Sort z-ordering override

Modify the existing `draw` method to branch on Heap Sort:

```python
def draw(self, surface: pygame.Surface) -> None:
    """Draw sprites with algorithm-appropriate z-ordering."""
    if self._algorithm_name == "Heap Sort":
        self._draw_heap(surface)
        return

    # --- Existing draw logic for non-Heap algorithms ---
    baseline: list[NumberSprite] = []
    lifted: list[NumberSprite] = []
    # ... rest of existing code unchanged ...
```

The `_draw_heap` method:

```python
def _draw_heap(self, surface: pygame.Surface) -> None:
    """Heap Sort z-ordering: sorted row → tree (deep first) → arcing sprites."""
    sorted_sprites: list[NumberSprite] = []
    tree_sprites: list[NumberSprite] = []
    arcing_sprites: list[NumberSprite] = []

    sorted_row_y = self._tree_layout.sorted_row_y if self._tree_layout else 0.0

    for sprite in self._sprites:
        if sprite.sprite_id in self._animating_sprites:
            arcing_sprites.append(sprite)
        elif sprite.home_y >= sorted_row_y - 1:
            sorted_sprites.append(sprite)
        else:
            tree_sprites.append(sprite)

    # Sorted row: left to right
    sorted_sprites.sort(key=lambda s: s.home_x)
    # Tree: deeper nodes first (higher y draws first, shallower nodes on top)
    tree_sprites.sort(key=lambda s: s.home_y, reverse=True)
    # Arcing: downward-arcing first, upward-arcing last (on top)
    arcing_sprites.sort(key=lambda s: s.exact_y, reverse=True)

    for s in sorted_sprites:
        s.draw(surface)
    for s in tree_sprites:
        s.draw(surface)
    for s in arcing_sprites:
        s.draw(surface)
```

**Z-ordering per HEAP_SORT_ANIMATION.md §6:**
- Sorted row sprites render first (behind the tree).
- Tree sprites render deeper nodes first so parent draws on top of children.
- Arcing sprites render last. The sprite with the lowest `exact_y` (highest on screen, arcing upward) draws last = on top.

### 2.12 `heap_size` property

Add after the existing `insertion_key_info` property:

```python
@property
def heap_size(self) -> int:
    """Current active heap size (for HeapOverlay)."""
    return self._heap_size
```

### 2.13 `reset()` additions

At the end of the existing `reset` method (after clearing Insertion Sort state), add:

```python
# Heap Sort state
self._is_extraction_swap = False
self._heap_sweep_indices = None
self._heap_size = len(initial_array)
if self._algorithm_name == "Heap Sort" and self._tree_layout is not None:
    self._heap_node_positions = self._tree_layout.node_positions(len(initial_array))
    tree_radius = self._tree_layout.tree_node_radius
    for i, sprite in enumerate(self._sprites):
        pos = self._heap_node_positions[i]
        sprite.home_x = pos[0]
        sprite.home_y = pos[1]
        sprite.exact_x = pos[0]
        sprite.exact_y = pos[1]
        sprite.ring_radius = tree_radius
```

### 2.14 `HeapOverlay` class in `sprite_manager.py`

Add this class **after** the `InsertionOverlay` class, at the end of the file.

#### Constants (module-level or class-level)

```python
_BOUNDARY_DASH: int = 6
_BOUNDARY_GAP: int = 4
_BOUNDARY_LINE_COLOR: tuple[int, int, int] = (150, 150, 160)
_BOUNDARY_LINE_WIDTH: int = 2
_PHASE_LABEL_OFFSET: int = 20  # px above tree_top for the phase label
_BOUNDARY_LABEL_OFFSET: int = 15  # px below sorted_row_y + node_radius
```

#### Constructor

```python
class HeapOverlay:
    """Draws edges, phase label, boundary marker, and placeholder outlines for Heap Sort."""

    def __init__(
        self,
        tree_layout: TreeLayout,
        phase_label: HeapPhaseLabel,
        boundary_label: HeapBoundaryLabel,
        array_size: int,
    ) -> None:
        self._tree_layout = tree_layout
        self._phase_label = phase_label
        self._boundary_label = boundary_label
        self._array_size = array_size
        self._heap_size: int = array_size
        self._phase: str = "BUILD MAX-HEAP"
        self._active_edge_parent: int | None = None
        self._active_edge_children: tuple[int, ...] = ()
        self._last_tick: SortResult | None = None
```

#### Method: `update(self, ctx: PanelContext, heap_size: int) -> None`

```python
def update(self, ctx: PanelContext, heap_size: int) -> None:
    self._heap_size = heap_size
    if ctx.current_tick is not None and ctx.current_tick is not self._last_tick:
        self._process_tick(ctx.current_tick)
        self._last_tick = ctx.current_tick
```

#### Method: `_process_tick(self, tick: SortResult) -> None`

```python
def _process_tick(self, tick: SortResult) -> None:
    op = tick.operation_type
    hi = tick.highlight_indices

    if op == OpType.RANGE:
        if tick.message.startswith("Active heap"):
            # Boundary T3 — switch phase, clear edge highlighting
            self._phase = "EXTRACTION"
            self._active_edge_parent = None
            self._active_edge_children = ()
        else:
            # Logical Tree T3 — set edge highlighting
            if hi is not None and len(hi) >= 2:
                self._active_edge_parent = hi[0]
                self._active_edge_children = hi[1:]
            else:
                self._active_edge_parent = None
                self._active_edge_children = ()

    elif op in (OpType.COMPARE, OpType.SWAP):
        # Clear edge highlighting during compares and swaps
        self._active_edge_parent = None
        self._active_edge_children = ()

    elif op in (OpType.TERMINAL, OpType.FAILURE):
        self._active_edge_parent = None
        self._active_edge_children = ()
```

#### Method: `draw_under(self, surface: pygame.Surface) -> None`

Draws elements that go BEHIND sprites: edges, placeholder outlines, boundary dashed line.

```python
def draw_under(self, surface: pygame.Surface) -> None:
    """Draw edges, placeholders, and boundary line (behind sprites)."""
    self._draw_edges(surface)
    self._draw_placeholders(surface)
    if self._heap_size < self._array_size:
        self._draw_boundary_line(surface)
```

**`_draw_edges`:**

```python
def _draw_edges(self, surface: pygame.Surface) -> None:
    """Draw parent-child edges for the active heap tree."""
    if self._heap_size <= 1:
        return
    positions = self._tree_layout.node_positions(self._heap_size)
    for i in range(1, self._heap_size):
        parent_idx = (i - 1) // 2
        is_active = (
            parent_idx == self._active_edge_parent
            and i in self._active_edge_children
        )
        color = ACTIVE_EDGE_COLOR if is_active else DEFAULT_EDGE_COLOR
        start = (round(positions[parent_idx][0]), round(positions[parent_idx][1]))
        end = (round(positions[i][0]), round(positions[i][1]))
        pygame.draw.line(surface, color, start, end, EDGE_WIDTH)
```

**Why we don't call `tree_layout.edges()`:** We need the INDEX of each edge's parent and child to check against `_active_edge_parent`/`_active_edge_children`. The `edges()` method returns position tuples without indices. Computing inline avoids needing to modify `tree_layout.py`.

**`_draw_placeholders`:**

```python
def _draw_placeholders(self, surface: pygame.Surface) -> None:
    """Draw dim circle outlines in the sorted row for active heap slots."""
    radius = self._tree_layout.tree_node_radius
    row_y = round(self._tree_layout.sorted_row_y)
    for slot in range(self._heap_size):
        cx = round(self._tree_layout.sorted_row_x(slot))
        pygame.draw.circle(surface, PLACEHOLDER_COLOR, (cx, row_y), radius, 1)
```

**Why:** Per HEAP_SORT_ANIMATION.md §3 — "Active heap slots render in the Sorted Row as dim placeholder outlines `(60, 60, 68)` with no number." These show where extracted elements will eventually land.

**`_draw_boundary_line`:**

```python
def _draw_boundary_line(self, surface: pygame.Surface) -> None:
    """Draw vertical dashed line between last active slot and first sorted slot."""
    boundary_x = (
        self._tree_layout.sorted_row_x(self._heap_size - 1)
        + self._tree_layout.sorted_row_x(self._heap_size)
    ) / 2
    radius = self._tree_layout.tree_node_radius
    row_y = self._tree_layout.sorted_row_y
    y_start = row_y - radius - 10
    y_end = row_y + radius + 10
    # Dashed line: 6px dash, 4px gap
    y = y_start
    bx = round(boundary_x)
    while y < y_end:
        end_y = min(y + _BOUNDARY_DASH, y_end)
        pygame.draw.line(
            surface, _BOUNDARY_LINE_COLOR,
            (bx, round(y)), (bx, round(end_y)),
            _BOUNDARY_LINE_WIDTH,
        )
        y += _BOUNDARY_DASH + _BOUNDARY_GAP
```

#### Method: `draw_over(self, surface: pygame.Surface) -> None`

Draws elements that go ON TOP of sprites: phase label text, boundary label text.

```python
def draw_over(self, surface: pygame.Surface) -> None:
    """Draw phase label and boundary label (on top of sprites)."""
    label_y = self._tree_layout.tree_top - _PHASE_LABEL_OFFSET
    self._phase_label.draw(surface, self._phase, label_y)
    if self._heap_size < self._array_size:
        boundary_x = (
            self._tree_layout.sorted_row_x(self._heap_size - 1)
            + self._tree_layout.sorted_row_x(self._heap_size)
        ) / 2
        label_y_boundary = (
            self._tree_layout.sorted_row_y
            + self._tree_layout.tree_node_radius
            + _BOUNDARY_LABEL_OFFSET
        )
        self._boundary_label.draw(surface, boundary_x, label_y_boundary)
```

#### Method: `reset(self) -> None`

```python
def reset(self) -> None:
    self._last_tick = None
    self._heap_size = self._array_size
    self._phase = "BUILD MAX-HEAP"
    self._active_edge_parent = None
    self._active_edge_children = ()
```

### 2.15 Modify `src/visualizer/main.py`

#### New imports

```python
from visualizer.views.hud import BubbleHUD, HeapBoundaryLabel, HeapPhaseLabel
from visualizer.views.panel import PanelRenderer, compute_header_total
from visualizer.views.panel import PanelState as ViewPanelState
from visualizer.views.tree_layout import TreeLayout
from visualizer.views.sprite_manager import (
    BubbleOverlay,
    HeapOverlay,
    InsertionOverlay,
    SelectionOverlay,
    SpriteManager,
)
```

Update existing import lines:
- Add `HeapBoundaryLabel, HeapPhaseLabel` to the `hud` import line.
- Add `compute_header_total` to the `panel` import line.
- Add `TreeLayout` import from `tree_layout`.
- Add `HeapOverlay` to the `sprite_manager` import line.

#### Create TreeLayout and pass to SpriteManager

After building `panel_renderers` and before building `sprite_managers`, create the TreeLayout for panel 3:

```python
# Heap Sort tree layout (panel index 3)
_title_h = title_font.get_height()
_body_h = body_font.get_height()
_heap_header_total = compute_header_total(
    layout.panel_rects[3].height, _title_h, _body_h, _body_h,
)
_heap_tree_layout = TreeLayout(
    panel_rect=layout.panel_rects[3],
    header_total=_heap_header_total,
    array_x_padding=layout.ARRAY_X_PADDING,
    slot_width=layout.slot_width,
)
```

Then update the `sprite_managers` list comprehension to pass `tree_layout` for panel 3:

```python
sprite_managers = [
    SpriteManager(
        algorithm_name=_ALGORITHM_NAMES[i],
        panel_rect=layout.panel_rects[i],
        array_x_padding=layout.ARRAY_X_PADDING,
        slot_width=layout.slot_width,
        font=number_font,
        initial_array=INITIAL_ARRAY,
        tree_layout=_heap_tree_layout if i == 3 else None,
    )
    for i in range(4)
]
```

#### Create HeapOverlay

After the Insertion Sort overlay creation, add:

```python
# Heap Sort overlay (panel index 3)
_heap_phase_label = HeapPhaseLabel(
    panel_rect=layout.panel_rects[3],
    body_font=body_font,
)
_heap_boundary_label = HeapBoundaryLabel(body_font)
heap_overlay = HeapOverlay(
    tree_layout=_heap_tree_layout,
    phase_label=_heap_phase_label,
    boundary_label=_heap_boundary_label,
    array_size=len(INITIAL_ARRAY),
)
```

#### Wire into the render loop

Modify the render loop to call HeapOverlay with **split draw** — `draw_under` before sprites, `draw_over` after:

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

    # Heap Sort overlay: edges and placeholders BEFORE sprites
    if i == 3:
        heap_overlay.update(ctx, sprite_managers[3].heap_size)
        heap_overlay.draw_under(surface)

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

    # Heap Sort overlay: phase label and boundary label AFTER sprites
    if i == 3:
        heap_overlay.draw_over(surface)
```

#### Wire restart

In the K_r handler, after existing overlay resets:

```python
elif event.key == pygame.K_r:
    orchestrator.restart()
    for sm in sprite_managers:
        sm.reset(INITIAL_ARRAY)
    selection_overlay.reset()
    bubble_overlay.reset()
    heap_overlay.reset()
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

# Gate 4: Import check — HeapOverlay loads without error
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy uv run python -c "
from visualizer.views.sprite_manager import SpriteManager, HeapOverlay
print('SpriteManager imported OK')
print('HeapOverlay imported OK')
"
```

All four must pass. Fix any issues before proceeding.

## STEP 4 — DEVLOG POST-ACTION

Append a post-action entry to `DEVLOG.md` immediately after the pre-action entry:

```markdown
## 2026-05-05 — Phase 7c-4 closed: Heap Sort choreography (post-action)

### Worked on

[Describe what was actually created — tree position override, _dispatch_heap, 2D arc interpolation, extraction arc, staggered sweep, steel-blue persistence, _draw_heap z-ordering, HeapOverlay class, main.py wiring, any deviations from the plan.]

### Corrections

[List any ruff/pyright corrections, or "Zero corrections" if clean on first run.]

### Results

- `uv run pyright src/visualizer/views/sprite_manager.py src/visualizer/main.py`: **[N] errors, [N] warnings**
- `uv run ruff check` + `uv run ruff format --check`: **[clean/N issues]**
- `uv run pytest tests/ -q`: **339/339 PASSED** (no regressions)
- Import check: **[PASS/FAIL]**

### Next

Phase 7c complete — all four algorithms have per-panel choreography. Next: visual verification (AT acceptance tests), then CLAUDE.md / IMPLEMENTATION_TRACKER updates.
```

## Context files to read

Read these files before writing any code:

1. `CLAUDE.md` — Critical Rules (especially #1 sprite identity, #5 universal orange, #6 timing, #7 dt clamp)
2. `src/visualizer/views/tree_layout.py` — TreeLayout constructor (`panel_rect`, `header_total`, `array_x_padding`, `slot_width`), `node_positions(heap_size)`, `edges(heap_size)`, `sorted_row_x(slot_index)`, `sorted_row_y`, `tree_top`, `tree_node_radius`, color constants (`DEFAULT_EDGE_COLOR`, `ACTIVE_EDGE_COLOR`, `PLACEHOLDER_COLOR`, `EDGE_WIDTH`)
3. `src/visualizer/views/hud.py` — HeapPhaseLabel constructor (`panel_rect`, `body_font`), `draw(surface, phase, label_y)`; HeapBoundaryLabel constructor (`body_font`), `draw(surface, boundary_x, label_y)`
4. `src/visualizer/views/sprite.py` — NumberSprite fields (`home_x`, `home_y`, `exact_x`, `exact_y`, `ring_radius`, `sprite_id`), `update_home()`, `set_color_state()`, `ColorState` enum (especially `SETTLED` for steel-blue)
5. `src/visualizer/views/sprite_manager.py` — current SpriteManager structure (dispatch pattern, position computation, draw z-ordering, reset), existing overlay classes
6. `src/visualizer/main.py` — current render loop, overlay wiring pattern, panel order (3=Heap Sort)
7. `src/visualizer/models/heap.py` — tick patterns: Boundary T3 message prefix `"Active heap"`, Logical Tree T3 message prefix `"Evaluating tree level"`, extraction swap `highlight_indices=(0, end)`, sift-down grammar
8. `src/visualizer/controllers/orchestrator.py` — `compute_sprite_moves()`, `PanelContext` fields, `sift_down_cadence` flag
9. `docs/contracts/HEAP_SORT_ANIMATION.md` — §2 Layout Override, §3 Visual Tokens, §4 Sift-Down Grammar, §5 Extraction Grammar, §6 Z-Ordering
10. `src/visualizer/views/panel.py` — `compute_header_total()` function signature

---
