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
from visualizer.views.pointer import PointerSet
from visualizer.views.sprite import ColorState, NumberSprite


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
    ) -> None:
        self._algorithm_name = algorithm_name
        self._panel_rect = panel_rect
        self._array_x_padding = array_x_padding
        self._slot_width = slot_width
        self._font = font
        self._initial_array = list(initial_array)
        self._arc_height: float = panel_rect.height * 0.08

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

    # ---------------------------------------------------------------------------
    # Internal dispatch
    # ---------------------------------------------------------------------------

    def _dispatch_tick(self, ctx: PanelContext) -> None:
        """Apply a newly detected tick: set colors, record start positions, set up arc."""
        tick = ctx.current_tick
        if tick is None:
            return

        op = tick.operation_type
        self._current_op_type = op

        # Reset all sprites to default, then apply highlights.
        for sprite in self._sprites:
            sprite.set_color_state(ColorState.DEFAULT)

        if tick.highlight_indices is not None:
            for slot_idx in tick.highlight_indices:
                sprite_id = ctx.slot_to_sprite_id[slot_idx]
                self._sprites[sprite_id].set_color_state(ColorState.ACTIVE)

        # Terminal: completion color, no motion.
        if op == OpType.TERMINAL:
            for sprite in self._sprites:
                sprite.set_color_state(ColorState.COMPLETE)
            self._animation_duration_ms = 0
            self._last_tick = tick
            return

        # Failure: error color, no motion.
        if op == OpType.FAILURE:
            for sprite in self._sprites:
                sprite.set_color_state(ColorState.ERROR)
            self._animation_duration_ms = 0
            self._last_tick = tick
            return

        # Record start positions and update home slots.
        self._animating_sprites = {}
        self._swap_left_id = None
        self._swap_right_id = None

        for sprite_id, new_slot in ctx.sprite_moves.items():
            sprite = self._sprites[sprite_id]
            self._animating_sprites[sprite_id] = (sprite.exact_x, sprite.exact_y)
            sprite.update_home(new_slot)

        # Swap arc: lower target slot → arcs UP (left), higher → arcs DOWN (right).
        if op == OpType.SWAP and len(self._animating_sprites) == 2:
            ids = list(ctx.sprite_moves.keys())
            if ctx.sprite_moves[ids[0]] < ctx.sprite_moves[ids[1]]:
                self._swap_left_id = ids[0]
                self._swap_right_id = ids[1]
            else:
                self._swap_left_id = ids[1]
                self._swap_right_id = ids[0]

        self._animation_elapsed_ms = 0
        self._animation_duration_ms = get_duration(op, ctx.sift_down_cadence)
        self._last_tick = tick

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

    def draw(self, surface: pygame.Surface) -> None:
        """Draw sprites: baseline group first (by slot), lifted group on top (highest last)."""
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
