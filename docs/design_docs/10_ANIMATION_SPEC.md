# 10 ANIMATION SPEC - Sprite Motion Contracts

Scope: Defines how the Pygame View layer translates discrete logical operations into smooth, physical sprite motion.

## 1) Frame Timing and Clock Contract

- The render loop uses `pygame.time.Clock` with a target of **60 FPS** via `clock.tick(60)`.
- Delta-time (`dt`) returned by the clock is **clamped to a maximum of 33ms** (equivalent to two frames at 60 FPS). This prevents a single large `dt` from overshooting sprite positions after hitches (window drag, OS sleep, debugger pause).
- Clamping formula applied each frame: `dt = min(clock.tick(60), 33)`.

## 2) Interpolation (Tweening) Rules

- Motion must occur smoothly over the duration commanded by the Controller (e.g., 400ms for a swap).
- Standard spatial movement utilizes time-normalized easing functions (e.g., Quadratic or Cubic Ease-In-Out) based on elapsed operation time. The interpolation ratio (`t`) is calculated and clamped as:

  `t = min(elapsed_time / total_duration, 1.0)`

- The clamp to `1.0` guarantees that regardless of Pygame's frame delta-time (`dt`), the sprite will never overshoot. The sprite maps exactly to the mathematical easing curve and lands perfectly on target at `t=1.0`, eliminating physics derailment from frame drops or accumulated float error.
- The internal sprite state must track `exact_x` and `exact_y` as floats, syncing to the integer `rect` only at the final render step.

## 3) Sprite Coordinate System

### 3.1 Anchor Point

- A sprite's `(exact_x, exact_y)` represents the **center** of the rendered text surface.
- At render time, the text surface is blitted with its center aligned to `(round(exact_x), round(exact_y))`.

### 3.2 Home Position

- `home_x`: the horizontal center of the sprite's assigned array slot, calculated as:
  `home_x = panel_rect.x + ARRAY_X_PADDING + (slot_index * slot_width) + (slot_width / 2)`
- `home_y`: the vertical baseline for the array row, calculated as:
  `home_y = panel_rect.y + panel_rect.height // 2`
- When a sprite is at rest (no active animation), `exact_x == home_x` and `exact_y == home_y`.

### 3.3 Sprite Identity Enforcement

The Controller must track sprites by their **unique ID** assigned at initialization — never by the numeric value they display. This is a hard constraint that prevents visual corruption when duplicate values exist in the array.

**Why value matching fails:** Consider the `duplicates_7` fixture `[3, 1, 3, 2, 1, 2, 3]`. If the Controller identifies sprites by value, a swap involving one of the three `3`s cannot be resolved — the wrong sprite may receive the movement command, causing it to "teleport" to a new position instead of arcing smoothly. This is especially destructive during Heap Sort extraction swaps, where the root-to-end arc is a high-stakes visual event (elevated arc height, 400ms duration). A teleporting sprite destroys the phase-transition signal entirely.

**Identity rules:**

1. Each `NumberSprite` receives a **permanent unique ID** at initialization (e.g., sequential integer or UUID). This ID never changes for the lifetime of the sprite.
2. The Controller maintains a mapping of `sprite_id → current_slot_index` that represents the current logical position of each sprite.
3. When a new `SortResult` arrives with an updated `array_state`, the Controller must compute the **index delta** between the previous `array_state` and the new `array_state` to determine which sprite moved where. It must not scan the new `array_state` for value matches.
4. For swap operations (T2 with two indices), the delta is deterministic: the values at the two indices have exchanged. The Controller identifies the two sprites currently occupying those slots (by the `sprite_id → slot` mapping) and assigns each to the other's slot.
5. For shift operations (Insertion Sort T2), the delta shows one value sliding from index `j` to `j+1`. The Controller identifies the sprite at slot `j` and reassigns it to slot `j+1`.
6. After computing the delta and updating the `sprite_id → slot` mapping, each affected sprite's `home_x` is recalculated for its new slot. The sprite then interpolates from its current `(exact_x, exact_y)` to the new `(home_x, home_y)`.

**Cross-reference:** This constraint is also stated in `02_ARCHITECTURE.md` Section "Sprite Identity" — the animation spec reiterates it here because incorrect identity resolution manifests as visual bugs (teleporting, wrong sprite arcing) that are difficult to diagnose from model-layer tests alone.

### 3.4 Slot Assignment

- When a `SortResult` provides a new `array_state`, the Controller computes the index delta between the previous and new array states using the sprite identity mapping (see Section 3.3).
- Each affected sprite updates its `home_x` to the center of its newly assigned slot.
- Sprites interpolate from their current `(exact_x, exact_y)` toward the new `(home_x, home_y)` over the operation duration.

### 3.5 Compare Lane (Vertical Offset Coordinate)

The **compare lane** is a vertical position above the baseline row where sprites temporarily reside during comparison or key-selection events. All algorithms use the universal active highlight color `(255, 140, 0)` orange when sprites are in the compare lane or highlighted during operations — there are no per-algorithm accent colors for active node highlighting.

| Algorithm | Offset Token | Value | Trigger | Duration |
| --- | --- | --- | --- | --- |
| Bubble Sort | `compare_lift_offset` | `50px` | T1 compare tick on `(j, j+1)` and Bubble swap-lift state | Transient in T1; held during lifted horizontal exchange in T2 |
| Insertion Sort | `lift_offset` | `panel_height * 0.06` | T1 key-selection tick on `(i,)` | Sustained — sprite remains at `home_y - lift_offset` across all subsequent ticks until the T2 placement drop |
| Selection Sort | — | — | — | No compare-lane motion (highlight-only) |
| Heap Sort | — | — | — | No compare-lane motion (highlight-only; tree structure communicated via T3 pulsed highlights) |

**Coordinate formula:** When a sprite is in the compare lane, its `exact_y` target is `home_y - offset` where `offset` is the algorithm-specific token above. The sprite eases to and from this position using the standard ease-in-out curve.

For Bubble Sort, the compare lane is locked to `compare_lane_y = home_y - 50` pixels. This exact pixel offset is the reference choreography value and is used for both the non-swap hold state and the pre-exchange swap-lift state.

**Design rationale:** The compare lane provides **visual isolation** — lifting sprites above the resting baseline makes the current algorithmic focus unmistakable, even at a glance. The two algorithms that use it (Bubble Sort, Insertion Sort) have different offset magnitudes and durations, creating distinct visual signatures:

- Bubble Sort's compare lane is **fixed and instructional** (50px above baseline, both sprites) — the pair is lifted into a dedicated teaching lane before either holding or exchanging.
- Insertion Sort's compare lane is **taller and sustained** (key hovers for the entire insertion cycle) — the key is prominently separated while multiple shifts occur beneath it.

Selection Sort and Heap Sort do not use compare-lane motion because their pedagogical emphasis is elsewhere (scan/minimum tracking and tree-relationship highlighting, respectively).

## 4) Render Order (Z-Ordering)

### 4.1 Unified Principle

**Any sprite that is vertically displaced above the baseline (`exact_y < home_y`) must render on top of all sprites at the baseline.** This is the single governing rule — all algorithm-specific z-order behaviors derive from it.

Rationale: Sprites in the compare lane (Section 3.5) or on an upward arc represent the current algorithmic focus. Drawing them on top prevents visual occlusion and keeps the learner's attention on the active operation.

### 4.2 Default Order

- When no animation is active, draw order follows array index (index 0 drawn first, index 6 drawn last).

### 4.3 Lifted Sprite Rules

The following situations produce lifted sprites that must draw on top of baseline sprites:

| Situation | Lifted Sprite(s) | Z-Order Among Lifted |
| --- | --- | --- |
| **Bubble Sort compare-lift** (T1) | Both sprites at `j` and `j+1` | Default index order between the two (no z-swap) |
| **Bubble Sort swap-lift exchange** (T2) | Both sprites at `j` and `j+1` in the compare lane | Default index order between the two while lifted horizontal exchange is in progress |
| **Selection/Heap swap arc** (T2) | Left sprite (arcs upward) | Left sprite draws on top of right sprite (which arcs downward, below baseline) |
| **Heap Sort extraction arc** (T2) | Left sprite at index 0 (arcs upward) | Same as swap arc — left on top |
| **Insertion Sort key lift** (sustained) | Key sprite at `(i,)` | Key draws on top of all other sprites, including shifted elements |

### 4.4 Conflict Resolution

If multiple lifted sprites exist simultaneously (e.g., theoretically possible during rapid frame rendering), the sprite with the **smallest `exact_y`** (highest on screen) draws last (on top). If tied, default index order breaks the tie.

### 4.5 Restoration

When a sprite returns to `home_y` (compare-lift descent completes, Bubble swap-lift settles, swap arc lands, key drops into place), it immediately reverts to default index-order rendering. There is no lingering z-order elevation after the animation concludes.

## 5) Algorithm-Specific Motion Signatures

### 5.1 Bubble Sort

- **Action:** The `ComparisonPointer` moves to `j`, the adjacent pair activates, and the pair either holds visibly without swapping or exchanges positions while lifted in the compare lane.

#### 5.1.1 Bubble Sort Frame-Level Sequence

The Bubble Sort choreography is defined against the 60 FPS render contract.

- **Arrow move to `j`:** `2` frames (`~33ms`). The green `ComparisonPointer` translates horizontally to index `j`.
- **Pair lift + color change:** `4` frames (`~67ms`). The nodes at `j` and `j+1` turn orange `(255, 140, 0)` immediately on arrow arrival and rise from `home_y` to `compare_lane_y = home_y - 50`.
- **Non-swap hold:** `2` frames (`~33ms`). If no swap follows, the orange pair remains stationary in the compare lane so the comparison is visible.
- **Return to baseline without swap:** `3` frames (`~50ms`). The pair descends back to `home_y` before the next comparison begins.
- **Optional position swap:** `18` frames (`300ms`) inside the 400ms T2 duration. While both sprites remain at `compare_lane_y`, they exchange `x` positions using a linear horizontal slide with standard ease-in-out interpolation applied to `x` only.
- **Return to baseline after swap:** `6` frames (`100ms`). After the horizontal exchange completes, both sprites descend together from `compare_lane_y` back to `home_y` in their new slots.

#### 5.1.2 Bubble Sort Pathing

- **ComparisonPointer path:** horizontal translation only; no vertical travel.
- **Compare-lift path:** vertical translation only from `home_y` to `compare_lane_y`.
- **Swap path:** **linear horizontal slide while lifted**, not an arc. During the exchange phase, both sprites keep a constant `y` value of `compare_lane_y` and interpolate only their `x` coordinates.
- **Settle path:** vertical translation only from `compare_lane_y` back to `home_y`.

#### 5.1.3 Bubble Sort Timing Contract

- **T1 Compare tick (150ms total):**
  - Frames `1–2` (`0–33ms`): arrow move to `j` completes.
  - Frames `1–4` (`0–67ms`): pair turns orange `(255, 140, 0)` and lifts to the compare lane.
  - Frames `5–6` (`67–100ms`): non-swap hold in the compare lane.
  - Frames `7–9` (`100–150ms`): if no swap follows, pair returns to baseline and releases orange active state at tick end.
- **T2 Swap tick (400ms total):**
  - Frames `1–18` (`0–300ms`): pair exchanges `x` positions while staying fixed at `compare_lane_y`.
  - Frames `19–24` (`300–400ms`): pair settles vertically from `compare_lane_y` back to `home_y` in the new slot order.

#### 5.1.4 Bubble Sort Compare-Lift and Swap-Lift Details

- **Lift offset:** `compare_lift_offset = 50px`.
- **Activation event:** the nodes at `j` and `j+1` change to orange `(255, 140, 0)` on the same frame that the arrow arrives at `j`.
- **Both sprites lift as a unit** — they share the same vertical offset at all times. This emphasizes that Bubble Sort evaluates *pairs*, unlike Insertion Sort which isolates a single key.
- **Z-ordering:** During the lift or lifted exchange, both lifted sprites draw on top of all non-lifted sprites. Between the two lifted sprites, default index order is maintained.
- **Scope:** This motion grammar applies **only to Bubble Sort**. Selection Sort remains highlight-only during T1 and uses arc motion only for T2 swaps.

### 5.2 Selection Sort (Swaps)

- **Action:** Two elements exchange indices.
- **Motion:** Both sprites ease their `x` coordinates to the other's home position using the standard easing curve. To prevent visual collision, a vertical arc offset is applied using a sine curve mapped to the same time parameter `t`:
  - Arc offset formula: `arc_offset = arc_height * sin(pi * t)`
  - `arc_height = panel_height * 0.08`
  - Left sprite (lower index): `exact_y = home_y - arc_offset` (arcs upward).
  - Right sprite (higher index): `exact_y = home_y + arc_offset` (arcs downward).
- The arc peaks at `t=0.5` and returns to `home_y` at `t=1.0`.

Selection Sort retains the standard arc swap because its teaching focus is scan/minimum tracking rather than a lifted exchange state.

- **Selection Sort:** T2 swap on `(i, min_idx)`. The sprite at index `i` (left, the sorted-region destination) arcs upward; the sprite at index `min_idx` (right, the discovered minimum) arcs downward. Because `i < min_idx` is always true during Selection Sort swaps (the sorted region grows from the left), the left/right arc assignment is deterministic. The upward arc on `i` and downward arc on `min_idx` produce the clean crossing exchange seen in the reference video, with no visual collision at the midpoint.

### 5.3 Insertion Sort (Lift, Shift, and Drop)

- **Action:** A key is selected, elements shift right, and the key is placed at its sorted position.

#### 5.3.1 Lift Offset Geometry

- **Lift height:** `lift_offset = panel_height * 0.06` — a **proportional** value, not a fixed pixel count.
- **Rationale:** Tying the offset to `panel_height` guarantees visual consistency across both resolution presets. In Desktop mode (panel height ≈ 296px), the lift is ≈ 18px; in Tablet mode (panel height ≈ 327px), it is ≈ 20px. Both produce a clearly visible separation from the baseline without colliding with the header region (capped at 35% of panel height per D-062).
- **Relationship to other offsets:** Insertion Sort keeps a proportional sustained lift because the key remains elevated for the duration of the entire pass, whereas Bubble Sort uses a fixed 50px pair-lift for a short compare-and-exchange choreography. The sustained Insertion lift remains visually distinct because it isolates a single key across multiple ticks rather than a brief adjacent pair event.
- **Simplification from D-077:** Because the window size is locked at startup (no mid-animation resizing), the lift offset is computed once and remains constant for the entire session. No dynamic recalculation is needed.

#### 5.3.2 Motion Sequence

- **Motion sequence within the Insertion Sort tick group:**
  1. **Lift (key-selection T1 tick):** The selected key sprite eases from `home_y` to `home_y - lift_offset` over the T1 duration (150ms). This is the **first visual event** of the pass. The sprite remains elevated across all subsequent compare and shift ticks until the placement drop.
  2. **Compare and Shift (T1 compare + T2 shift ticks):** Shifted elements ease horizontally from their current slot to the adjacent slot using the standard easing curve. The lifted key sprite holds its elevated `y` position and does not move horizontally during compare or shift ticks.
  3. **Drop / Settle (T2 placement tick):** The **final visual event** of the pass. The lifted key sprite interpolates **both axes simultaneously** over the T2 duration (400ms), creating a diagonal drop trajectory:
     - **Horizontal:** `exact_x` eases from current `home_x` (the key's original slot, or wherever it visually resides) to the destination slot's `home_x`.
     - **Vertical:** `exact_y` eases from `home_y - lift_offset` back down to `home_y`.
     - Both axes share the **same time parameter `t`** and the **same ease-in-out curve**, so horizontal and vertical progress are perfectly synchronized. At `t=0` the key is elevated at its pre-drop position; at `t=1` it rests precisely in its sorted slot at baseline.
     - **Visual effect:** The combined motion produces a smooth diagonal arc from the compare lane to the target slot — the key visibly "settles" into position rather than dropping straight down and then sliding sideways (or vice versa). This diagonal trajectory matches professional sorting animations where the key glides into its final home in a single fluid gesture.
- Easing for all three sub-motions uses the same ease-in-out curve as swaps.

### 5.4 Heap Sort (In-Place Swaps with Tree Highlight and Extraction Arc)

- **Action:** Two elements exchange indices during sift-down or root extraction.
- **Sift-down swap motion:** Identical arc swap motion to Selection Sort — both sprites interpolate their `x` coordinates to each other's home position. Left sprite arcs upward, right sprite arcs downward. Standard `arc_height = panel_height * 0.08` and sine formula.
- **Extraction swap motion:** When the root (index 0) swaps with the end of the heap region, a **higher arc** is used to visually distinguish this **phase-transition move** from internal sift-down repairs. This elevated arc is mandatory for root-to-end swaps and must not be used for any other swap type:
  - `extraction_arc_height = panel_height * 0.14` (1.75× the standard `arc_height` of `panel_height * 0.08`).
  - Same sine formula: `arc_offset = extraction_arc_height * sin(pi * t)`.
  - Left sprite (index 0) arcs upward, right sprite (index `end`) arcs downward.
  - Duration: always **400ms** (standard T2 duration — the sift-down cadence reduction does not apply to the extraction swap itself).
  - The dramatic height signals to the learner that this is the major structural event — extracting the maximum from the heap — not a routine repair.
  - **Implementation constant:** `EXTRACTION_ARC_MULTIPLIER = 1.75` or `EXTRACTION_ARC_HEIGHT = panel_height * 0.14`. The Controller must detect extraction swaps (T2 tick on `(0, end)` during Phase 2) and apply this arc height instead of the standard.
- **Logical Tree Highlight (T3):** Before each sift-down level's comparisons (in both Phase 1 and Phase 2), a T3 tick highlights the **parent-child triangle** — the parent index and its existing children within the heap boundary. The accent color (orange) renders simultaneously on the triangle members for 200ms with no positional change. The non-contiguous highlight pattern (e.g., indices 1, 3, 4) implies the binary tree structure within the flat row.
- **Heap Boundary Emphasis (T3) with Sweep:** At the start of each extraction step, a T3 tick highlights the contiguous range `0..heap_size-1` in accent color. Rather than appearing instantly on all indices, the highlight **sweeps** from index 0 to `end` over the T3 duration (200ms), creating a left-to-right "refresh" effect that visually re-establishes the heap boundary before each extraction (see Section 5.4.1).
- **Sift-Down Cadence:** After an extraction swap completes, the subsequent sift-down repair sequence uses **reduced simulated costs** to create a rapid-fire "ripple" effect, visually conveying that sift-down is a fast internal repair rather than a major structural event (see Section 5.4.2).
- **Binary tree layout:** Heap Sort renders active heap elements in a **binary tree layout** in the upper portion of the panel's array region, with parent-child edges drawn between nodes. Swap arcs during sift-down operate within the tree layout — parent and child nodes exchange positions along their edge path. Extraction swaps move the root node from the tree to the sorted row below using the elevated arc (`extraction_arc_height`). A compact **sorted row** below the tree serves as the extraction destination and grows from right to left as elements are extracted from the heap.

#### 5.4.1 Heap Boundary Sweep

When a Boundary Emphasis T3 tick fires for Heap Sort extraction, the View renders the highlight as a **staggered sweep** rather than an instant flash:

- The total T3 duration remains **200ms**.
- Each index in the range `0..end` receives its orange accent highlight at a staggered offset: `highlight_delay(i) = (i / end) * sweep_window`, where `sweep_window = 120ms`.
- The remaining time (`200ms - sweep_window = 80ms`) is the **hold phase** — all indices are highlighted simultaneously before the tick completes.
- The per-index delay is purely visual (View-layer rendering). The Controller still treats the T3 tick as a single 200ms operation. The algorithm model is not affected.
- The sweep direction is always left-to-right (index 0 highlights first), reinforcing the array's index ordering.

**Implementation note:** The sweep can be achieved by tracking per-index elapsed time in the View. Each index transitions from default color to accent color when `elapsed >= highlight_delay(i)`. No easing is applied to individual index transitions — each index snaps to accent color at its delay threshold.

#### 5.4.2 Sift-Down Cadence (Post-Extraction)

After an extraction swap (T2 on `(0, end)`), the sift-down repair sequence that follows uses **reduced operation durations** to create a rapid, cascading visual rhythm:

| Tick Type | Standard Duration | Sift-Down Cadence Duration |
| --- | --- | --- |
| T1 Compare | 150ms | **100ms** |
| T2 Swap | 400ms | **250ms** |
| T3 Logical Tree Highlight | 200ms | **130ms** |

**Implementation constants:** These durations should be defined as named constants (or configuration parameters) in the Controller, not inlined as magic numbers. Recommended constant names:

```python
SIFT_DOWN_COMPARE_DURATION = 100   # ms (reduced from standard 150ms)
SIFT_DOWN_SWAP_DURATION    = 250   # ms (reduced from standard 400ms)
SIFT_DOWN_TREE_HIGHLIGHT   = 130   # ms (reduced from standard 200ms)
```

The Controller selects between standard and reduced durations based on the `sift_down_cadence` flag (see below). An agentic coder may hardcode these values or expose them as tunable parameters — either approach satisfies the spec provided the durations match the table above.

**Scope:** The reduced cadence applies **only** to sift-down ticks that immediately follow an extraction swap within the same extraction step. It does not apply to:

- Phase 1 (Build Max-Heap) sift-down ticks — these use standard durations because the learner needs time to absorb the heap construction process.
- The extraction swap itself — always 400ms with elevated arc.
- The boundary T3 tick — always 200ms with sweep.

**Controller mechanism:** The Controller tracks a `sift_down_cadence` flag per Heap Sort panel. The flag is set to `True` after dispatching an extraction T2 swap, and reset to `False` when the next boundary T3 tick fires (start of the next extraction step) or when the algorithm completes. While the flag is active, the Controller applies the reduced duration table when mapping `OpType` to simulated cost for that panel.

**Rationale:** The reference video (see `docs/Reference/Heap_Sort_Video_Reference.md`) shows sift-down repairs as a rapid-fire cascade after each extraction. The reduced durations create this visual rhythm while remaining slow enough for the learner to follow the parent-child comparisons. The 250ms swap duration still allows readable arc motion — the easing curve compresses but does not lose legibility. Phase 1 retains standard timing because building the heap is the conceptually dense phase where the learner first encounters tree relationships.

**Race impact:** The reduced sift-down durations decrease Heap Sort's total elapsed time, making it more competitive in the race. This is intentional — it reflects the algorithmic reality that sift-down is an O(log n) repair, and the visual pacing should convey that these repairs are efficient relative to the extraction event that triggers them.

#### 5.4.3 Branching Visualization (T3 Logical Tree Highlight)

The T3 tick for sift-down tree logic communicates the binary heap's parent-child relationship within the flat array row. This subsection defines the exact visual behavior.

**Color:** The **accent color (orange)** is applied to all indices provided in the tick's `highlight_indices` tuple — typically `(parent, left_child, right_child)`, or `(parent, left_child)` when only one child exists within the heap boundary. This orange matches the universal active highlight color `(255, 140, 0)` used by all algorithms for active-node highlighting.

**Rendering:** All provided indices highlight **simultaneously** — there is no stagger or sweep. The orange accent snaps on at tick start across all members of the parent-child triangle at the same instant. This simultaneous appearance is the visual mechanism that implies a tree relationship: the learner perceives that these non-contiguous indices (e.g., 1, 3, 4) are grouped because they light up together, even though they are separated by unrelated elements in the flat row.

**Duration:**

- **Phase 1 (Build Max-Heap):** 200ms (standard T3 duration). The learner needs time to absorb the tree relationships during initial heap construction.
- **Phase 2 (Post-Extraction Sift-Down):** 130ms (reduced sift-down cadence, per Section 5.4.2). The faster timing creates the cascading ripple rhythm appropriate for internal repairs.

**No positional change:** No sprite displacement occurs on this tick. The highlight is purely chromatic — sprites remain at their current `(exact_x, exact_y)` positions.

**Distinction from Boundary T3 ticks:** Both tick types use the T3 tick type and the orange accent color, but they are visually distinguishable:

| Property | Boundary T3 | Branching T3 |
| --- | --- | --- |
| Highlight pattern | Contiguous range `0..heap_size-1` | Non-contiguous parent-child group (e.g., `1, 3, 4`) |
| Rendering | Staggered left-to-right sweep (Section 5.4.1) | Simultaneous snap-on |
| Timing context | Once per extraction step, before extraction swap | Before each sift-down level's comparisons |
| Pedagogical signal | "This is the active heap region" | "This parent owns these children" |

#### Heap Sort Extraction Visual Sequence (per extraction step)

1. **Boundary T3** tick fires: indices `0..end` highlight via left-to-right sweep over 200ms (no movement).
2. **Extraction T2** swap tick fires: root (index 0) and end (index `end`) exchange positions via **elevated arc motion** (`extraction_arc_height`) over 400ms. Controller sets `sift_down_cadence = True`.
3. **Sift-down sequence** (reduced cadence): For each level of sift-down repair:
   a. **Logical Tree T3** tick fires: parent-child triangle renders in accent color for **130ms** (no movement).
   b. **T1** compare ticks fire: highlight compared indices for **100ms**.
   c. **T2** swap tick fires (if needed): sprites arc with standard arc height over **250ms**.
4. The element now at index `end` renders in the settled/extracted color to show it has left the active heap.

## 6) Highlight Behavior

- Highlights apply **instantly** at tick start. There is no fade-in or fade-out transition. **Exception:** Heap Sort boundary T3 ticks use a staggered left-to-right sweep (see Section 5.4.1); per-index highlights still snap on (no fade), but their start times are offset across the sweep window.
- When the next tick begins, the previous tick's highlights are **replaced** by the new tick's `highlight_indices`. Indices not in the new set revert to their default color immediately.
- During pause, the current tick's highlights remain visible and frozen.
- During step mode, the stepped tick's highlights are visible for the duration of the step animation and persist until the next step or play action.

## 7) Pause and Resume Interpolation

- On pause, all sprite state is frozen: `exact_x`, `exact_y`, elapsed operation time, highlight colors, and the panel message line.
- On resume, each sprite's animation continues from the exact interrupted point. The remaining operation duration (`total_duration - elapsed_time`) is used to calculate the remaining `t` progression. No tick is re-fetched or restarted.

## 8) Step Mode Animation

- Step mode uses the **same operation duration and easing** as play mode (e.g., 400ms for a swap, 150ms for a compare).
- Step input is **ignored** while a step animation is still in progress. The user must wait for the current step animation to complete before stepping again.
- After the step animation completes, the app returns to paused state with all sprites at their final positions for that tick.

## 9) Restart During Animation

- If Restart is triggered while sprites are mid-animation, all sprites **snap instantly** to the initial array positions. There is no animated return.
- All animation state (elapsed time, interpolation progress, highlights) is discarded.
- The app enters paused state with a clean initial frame.
