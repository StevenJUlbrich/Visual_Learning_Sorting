# 12 ANIMATION FOUNDATION — Shared Rendering Contracts

**Scope:** This document defines the shared rendering framework that all four per-algorithm animation contracts depend on. It is the single source of truth for sprite identity, timing, easing, z-ordering, highlight behavior, and cross-tick state persistence. Per-algorithm contracts import these rules — they do not redefine them.

**Resolves:** Trap A (Sprite Identity), Trap B (Independent Timing)

**Cross-references:**
- `10_ANIMATION_SPEC.md` — frame timing, interpolation math, algorithm-specific motion signatures
- `02_ARCHITECTURE.md` — MVC boundaries, panel state machine, sprite identity
- `03_DATA_CONTRACTS.md` — SortResult, OpType, tick taxonomy
- `06_BEHAVIOR_SPEC.md` — controller timing, pause/resume, step mode

---

## 1) Sprite Identity Contract

> **Trap A resolved here.** An agent implementing sprite tracking by value matching will produce visual corruption (teleporting sprites, wrong sprite arcing) that is difficult to diagnose from model-layer tests.

### 1.1 Identity Rules

| # | Rule | Violation Consequence |
|---|------|-----------------------|
| 1 | Each `NumberSprite` receives a **permanent unique ID** at initialization. This ID never changes. | Sprites cannot be tracked across ticks |
| 2 | The Controller maintains a `sprite_id -> current_slot_index` mapping. | Slot assignments lost on tick transition |
| 3 | On receiving a new `SortResult`, the Controller computes the **index delta** between previous and new `array_state`. It must **never** scan the new array for value matches. | Duplicate values (e.g., `[3, 1, 3, 2]`) cause wrong sprite selection |
| 4 | For T2 swap ticks (two indices): the values at the two indices have exchanged. Identify sprites by their current slot, not their displayed value. | Wrong sprite receives arc motion |
| 5 | For T2 shift ticks (Insertion Sort): one value slides from index `j` to `j+1`. Identify the sprite at slot `j` and reassign to slot `j+1`. | Shift animates wrong element |
| 6 | After updating the mapping, recalculate each affected sprite's `home_x` for its new slot. The sprite interpolates from current `(exact_x, exact_y)` to new `(home_x, home_y)`. | Sprite teleports instead of animating |

### 1.2 Anti-Pattern: Value Matching

```python
# WRONG — fails with duplicate values
def find_sprite(self, value, new_array):
    for sprite in self.sprites:
        if sprite.value == value:  # Which "3"?
            return sprite

# CORRECT — identity-based delta
def compute_delta(self, old_state, new_state):
    moved = {}
    for idx in range(len(old_state)):
        if old_state[idx] != new_state[idx]:
            moved[idx] = new_state[idx]
    # Resolve sprite_id from slot mapping, not value
```

### 1.3 Sprite Coordinate System

| Property | Definition |
|----------|------------|
| `exact_x`, `exact_y` | Float-precision position (center of rendered text surface) |
| `home_x` | Horizontal center of assigned slot: `panel_rect.x + ARRAY_X_PADDING + (slot_index * slot_width) + (slot_width / 2)` |
| `home_y` | Vertical baseline: `panel_rect.y + panel_rect.height // 2` |
| At rest | `exact_x == home_x` and `exact_y == home_y` |
| Render | Blit with center aligned to `(round(exact_x), round(exact_y))` |

---

## 2) Timing Contract

> **Trap B resolved here.** An agent that ties animation to frame count instead of elapsed time will produce inconsistent motion across different hardware. An agent that doesn't clamp dt will allow sprites to overshoot after hitches.

### 2.1 Frame Clock

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Target FPS | 60 | `pygame.time.Clock.tick(60)` |
| dt clamp | `dt = min(clock.tick(60), 33)` | Prevents overshoot on hitches (window drag, OS sleep) |
| Max dt | 33ms (2 frames at 60 FPS) | Single large dt cannot skip animation phases |

### 2.2 Operation Durations (Standard)

| Tick Type | OpType | Standard Duration | Usage |
|-----------|--------|-------------------|-------|
| T1 Compare | `COMPARE` | **150ms** | All algorithm comparisons |
| T2 Write | `SWAP` / `SHIFT` | **400ms** | All swaps and shifts |
| T3 Range | `RANGE` | **200ms** | Heap Sort boundary/tree highlights |
| T4 Terminal | `TERMINAL` | 0ms | No animation — apply completion styling |
| T0 Failure | `FAILURE` | 0ms | No animation — apply error styling |

### 2.3 Sift-Down Cadence Override (Heap Sort Only)

After a Heap Sort extraction swap, the subsequent sift-down uses reduced durations:

| Tick Type | Standard | Cadence | Reduction |
|-----------|----------|---------|-----------|
| T1 Compare | 150ms | **100ms** | 33% faster |
| T2 Swap | 400ms | **250ms** | 37% faster |
| T3 Tree Highlight | 200ms | **130ms** | 35% faster |

**Controller state:** `sift_down_cadence` flag per Heap Sort panel.
- **Set:** After dispatching an extraction T2 swap (`(0, end)` in Phase 2)
- **Reset:** When the next boundary T3 tick fires, or when the algorithm completes
- **Excluded:** Phase 1 (Build Max-Heap) sift-downs always use standard durations
- **Excluded:** The extraction swap itself — always 400ms with elevated arc

> **Cross-reference:** This flag is a **Controller-layer** state variable. It is defined here and in the Heap Sort Animation Contract. The Controller spec (`06_BEHAVIOR_SPEC.md`) references it but defers to this document for lifecycle rules.

### 2.4 Independent Panel Timing

Each panel maintains its own timing state:

```
current_operation_remaining_ms  — countdown for active tick
elapsed_time_ms                 — total race time for this panel
pending_generator               — algorithm's tick generator
```

- Controller subtracts `dt` each frame from `current_operation_remaining_ms`
- When `<= 0`, the next `SortResult` is requested from the generator
- `operation_type` determines duration of next animation
- Completed/failed panels stop their timer but remain visible

**Race semantics:** Panels are independent. A fast algorithm completes and freezes while slower ones continue. The elapsed time display proves the race result.

### 2.5 Interpolation (Tweening)

All sprite motion uses time-normalized easing:

```python
t = min(elapsed_time / total_duration, 1.0)
position = start + (end - start) * ease_in_out(t)
```

| Rule | Detail |
|------|--------|
| Clamp to 1.0 | Sprite never overshoots — lands exactly on target |
| Float precision | `exact_x` and `exact_y` are floats; sync to integer `rect` only at render |
| Easing function | Quadratic or Cubic Ease-In-Out (same curve for all motions) |
| Frame independence | Motion is smooth regardless of actual frame rate |

---

## 3) Z-Ordering Contract

### 3.1 Governing Rule

**Any sprite with `exact_y < home_y` (above baseline) renders on top of all sprites at baseline.** This is the single z-order principle. All algorithm-specific behaviors derive from it.

### 3.2 Specific Situations

| Situation | Lifted Sprite(s) | Z-Order Among Lifted |
|-----------|-------------------|----------------------|
| Bubble Sort compare-lift (T1) | Both at `j` and `j+1` | Default index order |
| Bubble Sort swap-lift exchange (T2) | Both at `j` and `j+1` | Default index order |
| Selection/Heap swap arc (T2) | Left sprite arcs up | Left on top of right |
| Heap extraction arc (T2) | Root sprite at index 0 arcs up | Root on top |
| Insertion Sort key lift (sustained) | Key sprite at `(i,)` | Key on top of all |

### 3.3 Conflict Resolution

If multiple lifted sprites exist: sprite with smallest `exact_y` (highest on screen) draws last (on top). Ties broken by default index order.

### 3.4 Restoration

When a sprite returns to `home_y`, it immediately reverts to default index-order rendering. No lingering z-order elevation after animation ends.

### 3.5 Default Order

When no animation is active: draw order follows array index (0 first, 6 last).

---

## 4) Highlight Behavior Contract

### 4.1 Application Rules

| Rule | Detail |
|------|--------|
| Timing | Highlights apply **instantly** at tick start (no fade-in/out) |
| Replacement | When a new tick begins, previous highlights are replaced. Indices not in the new set revert to default color immediately |
| Pause | Current tick's highlights remain visible and frozen |
| Step mode | Stepped tick's highlights persist until next step or play |
| Universal color | All active highlights use orange `(255, 140, 0)` — no per-algorithm accent colors |

### 4.2 Exception: Heap Boundary Sweep

Heap Sort boundary T3 ticks use a staggered left-to-right sweep (see Heap Sort Animation Contract). Per-index highlights still snap on (no fade), but start times are offset across the sweep window.

### 4.3 Color State Machine

| State | Color | When |
|-------|-------|------|
| Default (at rest) | Blue `(100, 149, 237)` | No active highlight on this sprite |
| Active (highlighted) | Orange `(255, 140, 0)` | Sprite's index is in current tick's `highlight_indices` |
| Settled/Sorted | Steel-blue `(130, 150, 190)` | Heap Sort extracted elements |
| Completion | Green `(80, 220, 120)` | After T4 completion tick — full array |
| Failure | Error styling | After T0 failure tick |

Ring outline and number text share the same color, changing together based on state.

---

## 5) Compare Lane Contract

The **compare lane** is a vertical position above the baseline where sprites temporarily reside during comparison or key-selection events.

| Algorithm | Offset Token | Value | Trigger | Duration |
|-----------|-------------|-------|---------|----------|
| Bubble Sort | `compare_lift_offset` | `50px` (fixed) | T1 compare on `(j, j+1)` | Transient — returns to baseline within T1 or held through T2 |
| Insertion Sort | `lift_offset` | `panel_height * 0.06` (proportional) | T1 key-selection on `(i,)` | **Sustained** — key stays elevated across all ticks until T2 placement drop |
| Selection Sort | — | — | — | No compare-lane motion (highlight-only) |
| Heap Sort | — | — | — | No compare-lane motion (highlight-only) |

**Formula:** `exact_y_target = home_y - offset`

**Design rationale:** Lifting sprites above baseline makes the current algorithmic focus unmistakable. Bubble Sort's lift is fixed and brief (pair comparison). Insertion Sort's lift is proportional and sustained (key isolation across an entire pass).

---

## 6) Cross-Tick View State Model

> This section defines when the View must maintain state across tick boundaries — a deviation from the default per-tick rendering model.

### 6.1 Default Model: Stateless Per-Tick Rendering

For most ticks, the rendering cycle is:
1. Receive tick from Controller
2. Apply highlights and start motion
3. Complete motion
4. Wait for next tick

No View state carries over between ticks. Each tick is self-contained.

### 6.2 Exception: Persistent View State

The following algorithms require View state that persists across tick boundaries:

| Algorithm | Persistent State | Set When | Cleared When | What It Contains |
|-----------|-----------------|----------|--------------|-----------------|
| **Insertion Sort** | Key elevation | T1 key-selection tick on `(i,)` | T2 placement tick (diagonal drop) | Active key `sprite_id`, elevated `exact_y`, KEY label visibility, gap slot index |
| **Heap Sort** | Sift-down cadence flag | Extraction T2 swap dispatched | Next boundary T3 tick fires, or algorithm completes | Boolean flag on Controller per panel |
| **Heap Sort** | Phase identity | Phase 1 start / Phase 2 start | Algorithm completes | Current phase for label display ("BUILD MAX-HEAP" / "EXTRACTION") |
| **Heap Sort** | Sorted region set | Each extraction swap | Algorithm completes | Set of extracted sprite indices (for steel-blue coloring and sorted-row positioning) |

**Insertion Sort key elevation is the critical case.** The key sprite lifts on a T1 tick and does not descend until a T2 placement tick — potentially many ticks later. An implementer who resets sprite positions between ticks will drop the key back to baseline after every tick, destroying the sustained hover that is Insertion Sort's visual signature.

### 6.3 Implementation Guidance

Persistent state should be modeled as explicit named variables on the panel or View component, not as implicit side effects of animation state. When persistent state is active:

- The View checks for persistent state **before** applying per-tick rendering
- Persistent state overrides default "return to home" behavior for affected sprites
- Persistent state is cleared by a specific tick type (documented in table above), not by timeout or frame count

---

## 7) Pause, Resume, and Step Contract

### 7.1 Pause

On pause, **all** state freezes:
- `exact_x`, `exact_y` (mid-motion positions)
- `elapsed_time` within current operation
- Highlight colors
- Panel message line
- Cross-tick persistent state (key elevation, cadence flag, etc.)

### 7.2 Resume

Resume continues from the exact interrupted point:
- Remaining duration: `total_duration - elapsed_time`
- No tick is re-fetched or restarted
- Sprite continues its easing curve from the current `t` value

### 7.3 Step Mode

- Uses **same duration and easing** as play mode
- Step input **ignored** while a step animation is in progress
- After step animation completes, app returns to paused state
- One step = one `SortResult` tick fully animated

### 7.4 Restart

- All sprites **snap instantly** to initial positions (no animated return)
- All animation state discarded: elapsed time, interpolation, highlights, persistent state
- App enters paused state with clean initial frame

---

## 8) Swap Arc Contract

The default arc motion used by Selection Sort, Heap Sort sift-down, and Heap Sort extraction:

### 8.1 Standard Arc

```python
arc_offset = arc_height * sin(pi * t)
arc_height = panel_height * 0.08
```

- Left sprite (lower index): `exact_y = home_y - arc_offset` (arcs **upward**)
- Right sprite (higher index): `exact_y = home_y + arc_offset` (arcs **downward**)
- Both sprites interpolate `exact_x` toward each other's home position using ease-in-out
- Arc peaks at `t = 0.5`, returns to `home_y` at `t = 1.0`

### 8.2 Extraction Arc (Heap Sort Only)

```python
extraction_arc_height = panel_height * 0.14  # 1.75x standard
```

- Same sine formula, elevated height
- Applied **only** to root-to-end swaps (`(0, end)` during Phase 2)
- Duration: always 400ms (cadence reduction does not apply)
- Root arcs upward, end element arcs downward

### 8.3 Bubble Sort Does NOT Use Arc

Bubble Sort uses a different motion: linear horizontal slide while lifted at `compare_lane_y`. See Bubble Sort Animation Contract.

---

## 9) Contract Format Template

All per-algorithm animation contracts follow this structure:

```markdown
# [Algorithm] Animation Contract

## Overview
- Algorithm name, trap(s) resolved, cross-references

## Visual Signature
- What makes this algorithm look distinct to a learner

## Tick-to-Motion Mapping
- Table: each tick type -> exact motion, timing, highlight behavior

## State Machine
- Named states, transitions, triggers
- What persistent View state is required (if any)

## Pointer/Label Assets
- What instructional overlays this algorithm requires

## Worked Example
- Full tick sequence for canonical array [4, 7, 2, 6, 1, 5, 3]
- Frame-by-frame for at least one representative operation

## Validation Checklist
- Trap-specific checks
- Foundation contract compliance checks
```

---

## 10) Foundation Compliance Checklist

Every per-algorithm contract must satisfy these foundation rules. This checklist is used during contract review.

| # | Check | Foundation Section |
|---|-------|--------------------|
| 1 | Sprites tracked by ID, never by value | Section 1 |
| 2 | All motion uses time-normalized `t = elapsed / duration` with clamp to 1.0 | Section 2.5 |
| 3 | dt clamped to 33ms maximum | Section 2.1 |
| 4 | Lifted sprites render on top of baseline sprites | Section 3 |
| 5 | Highlights apply instantly, replace on new tick | Section 4 |
| 6 | Universal orange `(255, 140, 0)` for all active highlights | Section 4.3 |
| 7 | Cross-tick state explicitly named and lifecycle-documented | Section 6 |
| 8 | Pause freezes all state; resume continues from exact point | Section 7 |
| 9 | Step mode uses same duration/easing as play mode | Section 7.3 |
| 10 | Restart snaps to initial — no animated return | Section 7.4 |

---

## Appendix A — Trap Resolution Mapping

| Trap | Name | How This Document Resolves It |
|------|------|-------------------------------|
| **A** | Sprite Identity | Section 1: Identity rules table, anti-pattern example, coordinate system |
| **B** | Independent Timing | Section 2: Frame clock, dt clamping, panel independence, interpolation rules |

Traps C–I are resolved by their respective per-algorithm contracts, which import this foundation.
