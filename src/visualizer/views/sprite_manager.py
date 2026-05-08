"""SpriteManager — per-panel sprite lifecycle, animation dispatch, and rendering.

Owns NumberSprite instances for one algorithm panel. Receives tick updates
from PanelContext, interpolates positions with easing, and draws with z-ordering.

Phase 7b scope: flat baseline row for all algorithms, standard swap arcs,
highlight coloring. Per-algorithm choreography deferred to later phases.

See doc 12 (animation foundation), doc 10 §2 (interpolation rules).
"""

from __future__ import annotations

import pygame

from visualizer.controllers.orchestrator import PanelContext, PanelState, get_duration
from visualizer.models.contracts import OpType, SortResult
from visualizer.views.easing import ease_in_out_quad, sine_arc
from visualizer.views.hud import BubbleHUD, HeapBoundaryLabel, HeapPhaseLabel
from visualizer.views.limitline import LimitLine
from visualizer.views.pointer import PointerSet
from visualizer.views.sprite import ColorState, NumberSprite
from visualizer.views.tree_layout import (
    ACTIVE_EDGE_COLOR,
    DEFAULT_EDGE_COLOR,
    EDGE_WIDTH,
    PLACEHOLDER_COLOR,
    TreeLayout,
)


class SpriteManager:
    """Owns and animates NumberSprite instances for one algorithm panel.

    Detects new ticks by identity comparison on ctx.current_tick, dispatches
    sprite_moves to update home positions, and interpolates exact_x/exact_y
    each frame using ease_in_out_quad (horizontal) and sine_arc (swap vertical).
    """

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
        self._algorithm_name = algorithm_name
        self._panel_rect = panel_rect
        self._array_x_padding = array_x_padding
        self._slot_width = slot_width
        self._font = font
        self._initial_array = list(initial_array)
        self._arc_height: float = panel_rect.height * 0.08
        self._compare_lane_y: float = (panel_rect.y + panel_rect.height // 2) - 50

        self._sprites: list[NumberSprite] = [
            NumberSprite(i, initial_array[i], i, panel_rect, array_x_padding, slot_width, font)
            for i in range(len(initial_array))
        ]

        self._last_tick: SortResult | None = None
        self._animation_elapsed_ms: int = 0
        self._animation_duration_ms: int = 0
        self._animating_sprites: dict[int, tuple[float, float]] = {}
        self._swap_left_id: int | None = None
        self._swap_right_id: int | None = None
        self._current_op_type: OpType | None = None

        # Insertion Sort cross-tick state
        self._insertion_lift_offset: float = panel_rect.height * 0.06
        self._insertion_key_id: int | None = None
        self._insertion_key_elevated: bool = False
        self._insertion_is_placement: bool = False

        # Heap Sort state
        self._tree_layout: TreeLayout | None = tree_layout
        self._heap_size: int = len(initial_array)
        self._heap_node_positions: list[tuple[float, float]] = []
        self._extraction_arc_height: float = panel_rect.height * 0.14
        self._is_extraction_swap: bool = False
        self._heap_sweep_indices: tuple[int, ...] | None = None

        # Selection Sort settled-region state
        self._selection_sorted_count: int = 0
        self._selection_last_j: int = -1

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

    # ---------------------------------------------------------------------------
    # Internal dispatch
    # ---------------------------------------------------------------------------

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

        # Force key sprite to ACTIVE (orange) while elevated — Insertion Sort cross-tick state.
        # This overrides the default highlight reset so the key stays orange during
        # compare/shift ticks where it's not in highlight_indices.
        if self._insertion_key_elevated and self._insertion_key_id is not None:
            self._sprites[self._insertion_key_id].set_color_state(ColorState.ACTIVE)

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
        elif self._algorithm_name == "Selection Sort":
            self._dispatch_selection(tick, ctx, op)
        elif self._algorithm_name == "Insertion Sort":
            self._dispatch_insertion(tick, ctx, op)
        elif self._algorithm_name == "Heap Sort":
            self._dispatch_heap(tick, ctx, op)
        else:
            self._dispatch_default(tick, ctx, op)

        self._animation_elapsed_ms = 0
        self._animation_duration_ms = get_duration(op, ctx.sift_down_cadence)
        self._last_tick = tick

    def _dispatch_default(self, tick: SortResult, ctx: PanelContext, op: OpType) -> None:
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

            # Swap places the pass minimum at index self._selection_sorted_count.
            self._selection_sorted_count += 1

        elif op == OpType.COMPARE:
            # No-swap pass detection: when a new outer-loop pass starts without
            # a preceding swap, the element at the old i was already in position.
            # Detect new pass by j resetting (j decreased or first tick).
            # Only then check min_idx — at pass start, min_idx == i.
            if tick.highlight_indices is not None and len(tick.highlight_indices) == 2:
                min_idx = tick.highlight_indices[0]
                j = tick.highlight_indices[1]
                if j <= self._selection_last_j or self._selection_last_j == -1:
                    # New pass started — catch up for any skipped no-swap passes
                    while self._selection_sorted_count < min_idx:
                        self._selection_sorted_count += 1
                self._selection_last_j = j

        # Re-apply settled color to the sorted prefix
        self._apply_selection_settled(ctx)

    def _apply_selection_settled(self, ctx: PanelContext) -> None:
        """Force ColorState.SETTLED for all sprites in the sorted prefix (slot < sorted_count)."""
        for slot in range(self._selection_sorted_count):
            sprite_id = ctx.slot_to_sprite_id[slot]
            self._sprites[sprite_id].set_color_state(ColorState.SETTLED)

    def _dispatch_bubble(self, tick: SortResult, ctx: PanelContext, op: OpType) -> None:
        """Bubble Sort motion setup: T1 = compare-lift, T2 = snap-up + horizontal exchange."""
        self._animating_sprites = {}
        self._swap_left_id = None
        self._swap_right_id = None

        if op == OpType.COMPARE:
            if tick.highlight_indices is not None:
                for slot_idx in tick.highlight_indices:
                    sprite_id = ctx.slot_to_sprite_id[slot_idx]
                    sprite = self._sprites[sprite_id]
                    self._animating_sprites[sprite_id] = (sprite.exact_x, sprite.exact_y)

        elif op == OpType.SWAP:
            for sprite_id, new_slot in ctx.sprite_moves.items():
                sprite = self._sprites[sprite_id]
                sprite.exact_y = self._compare_lane_y
                self._animating_sprites[sprite_id] = (sprite.exact_x, self._compare_lane_y)
                sprite.update_home(new_slot)

    def _dispatch_insertion(self, tick: SortResult, ctx: PanelContext, op: OpType) -> None:
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

    def _dispatch_heap(self, tick: SortResult, ctx: PanelContext, op: OpType) -> None:
        """Heap Sort motion setup: tree swaps, extraction arcs, boundary sweep."""
        self._animating_sprites = {}
        self._swap_left_id = None
        self._swap_right_id = None
        self._is_extraction_swap = False
        self._heap_sweep_indices = None

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

        elif op == OpType.SWAP:
            hi = tick.highlight_indices
            # Record start positions FIRST
            for sprite_id, _new_slot in ctx.sprite_moves.items():
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
                            self._swap_left_id = sprite_id  # arcs up (root → sorted row)
                        else:
                            self._swap_right_id = sprite_id  # arcs down (end → root)
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

    def _recompute_heap_positions(self) -> None:
        """Recompute cached tree node positions for current heap_size."""
        if self._tree_layout is not None:
            self._heap_node_positions = self._tree_layout.node_positions(self._heap_size)

    def _apply_sorted_settled(self, ctx: PanelContext) -> None:
        """Force ColorState.SETTLED for all sprites in the sorted row (slot >= heap_size)."""
        for slot in range(self._heap_size, len(self._sprites)):
            sprite_id = ctx.slot_to_sprite_id[slot]
            self._sprites[sprite_id].set_color_state(ColorState.SETTLED)

    # ---------------------------------------------------------------------------
    # Per-frame update and draw
    # ---------------------------------------------------------------------------

    def update(self, dt: int, ctx: PanelContext) -> None:
        """Detect new ticks, advance elapsed time, and recompute sprite positions."""
        if ctx.current_tick is not None and ctx.current_tick is not self._last_tick:
            self._dispatch_tick(ctx)

        if ctx.state == PanelState.ANIMATING_OPERATION and self._animation_duration_ms > 0:
            self._animation_elapsed_ms += dt

        if self._animation_duration_ms > 0 and self._animating_sprites:
            if self._algorithm_name == "Bubble Sort":
                self._compute_bubble_positions()
            elif self._algorithm_name == "Insertion Sort":
                self._compute_insertion_positions()
            elif self._algorithm_name == "Heap Sort":
                self._compute_heap_positions()
            else:
                self._compute_default_positions()

        # Heap Sort boundary sweep coloring
        if (
            self._algorithm_name == "Heap Sort"
            and self._heap_sweep_indices is not None
            and self._animation_duration_ms > 0
        ):
            self._apply_heap_sweep(ctx)

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

    def _compute_bubble_positions(self) -> None:
        """Bubble Sort motion: 3-phase compare-lift (T1), horizontal exchange + settle (T2)."""
        elapsed = self._animation_elapsed_ms
        duration = self._animation_duration_ms
        t = min(elapsed / duration, 1.0)

        if self._current_op_type == OpType.COMPARE:
            for sprite_id, (start_x, start_y) in self._animating_sprites.items():
                sprite = self._sprites[sprite_id]
                sprite.exact_x = start_x

                if elapsed <= 67:
                    sub_t = min(elapsed / 67, 1.0)
                    eased = ease_in_out_quad(sub_t)
                    sprite.exact_y = start_y + (self._compare_lane_y - start_y) * eased
                elif elapsed <= 100:
                    sprite.exact_y = self._compare_lane_y
                else:
                    sub_t = min((elapsed - 100) / 50, 1.0)
                    eased = ease_in_out_quad(sub_t)
                    sprite.exact_y = (
                        self._compare_lane_y + (sprite.home_y - self._compare_lane_y) * eased
                    )

        elif self._current_op_type == OpType.SWAP:
            for sprite_id, (start_x, _start_y) in self._animating_sprites.items():
                sprite = self._sprites[sprite_id]

                if elapsed <= 300:
                    sub_t = min(elapsed / 300, 1.0)
                    eased = ease_in_out_quad(sub_t)
                    sprite.exact_x = start_x + (sprite.home_x - start_x) * eased
                    sprite.exact_y = self._compare_lane_y
                else:
                    sprite.exact_x = sprite.home_x
                    sub_t = min((elapsed - 300) / 100, 1.0)
                    eased = ease_in_out_quad(sub_t)
                    sprite.exact_y = (
                        self._compare_lane_y + (sprite.home_y - self._compare_lane_y) * eased
                    )

        if t >= 1.0:
            for sprite_id in self._animating_sprites:
                s = self._sprites[sprite_id]
                s.exact_x = s.home_x
                s.exact_y = s.home_y
            self._animating_sprites = {}

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

    def _compute_heap_positions(self) -> None:
        """Heap Sort motion: 2D ease with vertical arc offset for swaps."""
        t = min(self._animation_elapsed_ms / self._animation_duration_ms, 1.0)
        eased_t = ease_in_out_quad(t)

        arc_height = self._extraction_arc_height if self._is_extraction_swap else self._arc_height

        for sprite_id, (start_x, start_y) in self._animating_sprites.items():
            sprite = self._sprites[sprite_id]
            # Base interpolation: ease both axes from start to home
            base_x = start_x + (sprite.home_x - start_x) * eased_t
            base_y = start_y + (sprite.home_y - start_y) * eased_t
            # Vertical arc offset
            arc_offset = arc_height * sine_arc(t)
            if sprite_id == self._swap_left_id:
                sprite.exact_x = base_x
                sprite.exact_y = base_y - arc_offset  # arcs up
            elif sprite_id == self._swap_right_id:
                sprite.exact_x = base_x
                sprite.exact_y = base_y + arc_offset  # arcs down
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

    def draw(self, surface: pygame.Surface) -> None:
        """Draw sprites with algorithm-appropriate z-ordering."""
        if self._algorithm_name == "Heap Sort":
            self._draw_heap(surface)
            return

        baseline: list[NumberSprite] = []
        lifted: list[NumberSprite] = []

        for sprite in self._sprites:
            if sprite.exact_y < sprite.home_y:
                lifted.append(sprite)
            else:
                baseline.append(sprite)

        baseline.sort(key=lambda s: s.home_x)
        lifted.sort(key=lambda s: s.exact_y, reverse=True)

        for sprite in baseline:
            sprite.draw(surface)
        for sprite in lifted:
            sprite.draw(surface)

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

    @property
    def insertion_key_info(self) -> tuple[float, float, int] | None:
        """Return (exact_x, exact_y, ring_radius) of the elevated key sprite, or None."""
        if self._insertion_key_elevated and self._insertion_key_id is not None:
            sprite = self._sprites[self._insertion_key_id]
            return (sprite.exact_x, sprite.exact_y, sprite.ring_radius)
        return None

    @property
    def heap_size(self) -> int:
        """Current active heap size (for HeapOverlay)."""
        return self._heap_size

    def reset(self, initial_array: list[int]) -> None:
        """Snap all sprites to initial positions and clear all animation state."""
        self._initial_array = list(initial_array)
        self._sprites = [
            NumberSprite(
                i,
                initial_array[i],
                i,
                self._panel_rect,
                self._array_x_padding,
                self._slot_width,
                self._font,
            )
            for i in range(len(initial_array))
        ]
        self._last_tick = None
        self._animation_elapsed_ms = 0
        self._animation_duration_ms = 0
        self._animating_sprites = {}
        self._swap_left_id = None
        self._swap_right_id = None
        self._current_op_type = None
        self._insertion_key_id = None
        self._insertion_key_elevated = False
        self._insertion_is_placement = False
        # Heap Sort state
        self._is_extraction_swap = False
        self._heap_sweep_indices = None
        self._heap_size = len(initial_array)
        # Selection Sort state
        self._selection_sorted_count = 0
        self._selection_last_j = -1
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


class SelectionOverlay:
    """Tracks i/j/min pointer indices for the Selection Sort panel."""

    def __init__(self, pointer_set: PointerSet) -> None:
        self._pointer_set = pointer_set
        self._last_tick: SortResult | None = None
        self._awaiting_new_pass: bool = True
        self._i: int = 0
        self._j: int = 0
        self._min: int = 0
        self._draw_i: int | None = None
        self._draw_j: int | None = None
        self._draw_min: int | None = None

    def update(self, ctx: PanelContext) -> None:
        if ctx.current_tick is not None and ctx.current_tick is not self._last_tick:
            self._process_tick(ctx.current_tick)
            self._last_tick = ctx.current_tick

    def _process_tick(self, tick: SortResult) -> None:
        op = tick.operation_type

        if op == OpType.COMPARE:
            if tick.highlight_indices is None or len(tick.highlight_indices) != 2:
                return
            min_idx = tick.highlight_indices[0]
            j = tick.highlight_indices[1]
            if self._awaiting_new_pass or j < self._j:
                self._i = min_idx
                self._awaiting_new_pass = False
            self._min = min_idx
            self._j = j
            self._draw_i = self._i
            self._draw_j = j
            self._draw_min = min_idx

        elif op == OpType.SWAP:
            if tick.highlight_indices is None or len(tick.highlight_indices) != 2:
                return
            self._draw_i = None
            self._draw_j = None
            self._draw_min = tick.highlight_indices[1]
            self._awaiting_new_pass = True

        elif op in (OpType.TERMINAL, OpType.FAILURE):
            self._draw_i = None
            self._draw_j = None
            self._draw_min = None

    def draw(self, surface: pygame.Surface) -> None:
        self._pointer_set.draw(surface, self._draw_i, self._draw_j, self._draw_min)

    def reset(self) -> None:
        self._last_tick = None
        self._awaiting_new_pass = True
        self._i = 0
        self._j = 0
        self._min = 0
        self._draw_i = None
        self._draw_j = None
        self._draw_min = None


class BubbleOverlay:
    """Manages LimitLine, BubbleHUD, and ComparisonPointer for the Bubble Sort panel."""

    def __init__(
        self,
        limit_line: LimitLine,
        bubble_hud: BubbleHUD,
        panel_rect: pygame.Rect,
        array_x_padding: int,
        slot_width: float,
        ring_radius: int,
    ) -> None:
        self._limit_line = limit_line
        self._bubble_hud = bubble_hud
        self._panel_rect = panel_rect
        self._array_x_padding = array_x_padding
        self._slot_width = slot_width
        self._ring_radius = ring_radius
        self._last_tick: SortResult | None = None
        self._j: int = -1
        self._pointer_visible: bool = False
        self._home_y: float = panel_rect.y + panel_rect.height // 2
        self._arrow_gap: int = 5
        self._arrow_height: int = 12
        self._arrow_half_width: int = 5
        self._pointer_color: tuple[int, int, int] = (80, 220, 120)

    def update(self, ctx: PanelContext) -> None:
        if ctx.current_tick is not None and ctx.current_tick is not self._last_tick:
            self._process_tick(ctx.current_tick)
            self._last_tick = ctx.current_tick

    def _process_tick(self, tick: SortResult) -> None:
        op = tick.operation_type

        if op == OpType.COMPARE:
            if tick.highlight_indices is None or len(tick.highlight_indices) != 2:
                return
            j = tick.highlight_indices[0]
            if self._j >= 0 and j < self._j:
                self._limit_line.advance()
            self._j = j
            self._pointer_visible = True

        elif op in (OpType.TERMINAL, OpType.FAILURE):
            self._pointer_visible = False

    def draw(self, surface: pygame.Surface, comparisons: int, writes: int) -> None:
        self._limit_line.draw(surface)
        self._bubble_hud.draw(surface, comparisons, writes // 2)
        if self._pointer_visible and self._j >= 0:
            self._draw_comparison_pointer(surface)

    def _draw_comparison_pointer(self, surface: pygame.Surface) -> None:
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

    def reset(self) -> None:
        self._last_tick = None
        self._j = -1
        self._pointer_visible = False
        self._limit_line.reset()


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


# ---------------------------------------------------------------------------
# HeapOverlay constants
# ---------------------------------------------------------------------------

_BOUNDARY_DASH: int = 6
_BOUNDARY_GAP: int = 4
_BOUNDARY_LINE_COLOR: tuple[int, int, int] = (150, 150, 160)
_BOUNDARY_LINE_WIDTH: int = 2
_BOUNDARY_LABEL_OFFSET: int = 15  # px below sorted_row_y + node_radius


class HeapOverlay:
    """Draws edges, phase label, boundary marker, and placeholder outlines for Heap Sort."""

    def __init__(
        self,
        tree_layout: TreeLayout,
        phase_label: HeapPhaseLabel,
        boundary_label: HeapBoundaryLabel,
        array_size: int,
        panel_rect: pygame.Rect,
    ) -> None:
        self._tree_layout = tree_layout
        self._phase_label = phase_label
        self._boundary_label = boundary_label
        self._array_size = array_size
        self._panel_rect = panel_rect
        self._heap_size: int = array_size
        self._phase: str | None = "BUILD MAX-HEAP"
        self._active_edge_parent: int | None = None
        self._active_edge_children: tuple[int, ...] = ()
        self._last_tick: SortResult | None = None

    def update(self, ctx: PanelContext, heap_size: int) -> None:
        self._heap_size = heap_size
        if ctx.current_tick is not None and ctx.current_tick is not self._last_tick:
            self._process_tick(ctx.current_tick)
            self._last_tick = ctx.current_tick

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
            self._phase = None
            self._active_edge_parent = None
            self._active_edge_children = ()

    def draw_under(self, surface: pygame.Surface) -> None:
        """Draw edges, placeholders, and boundary line (behind sprites)."""
        self._draw_edges(surface)
        if self._phase == "EXTRACTION":
            self._draw_placeholders(surface)
            if self._heap_size < self._array_size:
                self._draw_boundary_line(surface)

    def _draw_edges(self, surface: pygame.Surface) -> None:
        """Draw parent-child edges for the active heap tree."""
        if self._heap_size <= 1:
            return
        positions = self._tree_layout.node_positions(self._heap_size)
        for i in range(1, self._heap_size):
            parent_idx = (i - 1) // 2
            is_active = parent_idx == self._active_edge_parent and i in self._active_edge_children
            color = ACTIVE_EDGE_COLOR if is_active else DEFAULT_EDGE_COLOR
            start = (round(positions[parent_idx][0]), round(positions[parent_idx][1]))
            end = (round(positions[i][0]), round(positions[i][1]))
            pygame.draw.line(surface, color, start, end, EDGE_WIDTH)

    def _draw_placeholders(self, surface: pygame.Surface) -> None:
        """Draw dim circle outlines in the sorted row for active heap slots."""
        radius = self._tree_layout.tree_node_radius
        row_y = round(self._tree_layout.sorted_row_y)
        for slot in range(self._heap_size):
            cx = round(self._tree_layout.sorted_row_x(slot))
            pygame.draw.circle(surface, PLACEHOLDER_COLOR, (cx, row_y), radius, 1)

    def _draw_boundary_line(self, surface: pygame.Surface) -> None:
        """Draw vertical dashed line between last active slot and first sorted slot."""
        boundary_x = (
            self._tree_layout.sorted_row_x(self._heap_size - 1)
            + self._tree_layout.sorted_row_x(self._heap_size)
        ) / 2
        # Clamp to panel bounds — don't draw outside the Heap Sort panel
        panel_left = self._panel_rect.x + 10
        panel_right = self._panel_rect.right - 10
        if boundary_x < panel_left or boundary_x > panel_right:
            return
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
                surface,
                _BOUNDARY_LINE_COLOR,
                (bx, round(y)),
                (bx, round(end_y)),
                _BOUNDARY_LINE_WIDTH,
            )
            y += _BOUNDARY_DASH + _BOUNDARY_GAP

    def draw_over(self, surface: pygame.Surface) -> None:
        """Draw phase label and boundary label (on top of sprites)."""
        if self._phase is not None:
            label_y = self._tree_layout.tree_top
            self._phase_label.draw(surface, self._phase, label_y)
        if self._heap_size < self._array_size:
            boundary_x = (
                self._tree_layout.sorted_row_x(self._heap_size - 1)
                + self._tree_layout.sorted_row_x(self._heap_size)
            ) / 2
            panel_left = self._panel_rect.x + 10
            panel_right = self._panel_rect.right - 10
            if panel_left <= boundary_x <= panel_right:
                label_y_boundary = (
                    self._tree_layout.sorted_row_y
                    + self._tree_layout.tree_node_radius
                    + _BOUNDARY_LABEL_OFFSET
                )
                self._boundary_label.draw(surface, boundary_x, label_y_boundary)

    def reset(self) -> None:
        self._last_tick = None
        self._heap_size = self._array_size
        self._phase = "BUILD MAX-HEAP"
        self._active_edge_parent = None
        self._active_edge_children = ()
