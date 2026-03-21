# Supplementary Agent Prompts & Revised Phase 4 — Claude Code Review (2026-03-21)

Context: This document complements `2026-03-21-gemini-recommendations.md`. The Gemini recommendations provided system prompts for traps A–D and a phased workflow, but did not address traps E–I identified in `2026-03-21_review_claude_additional_traps.md`. Additionally, the Gemini "Trap E" prompt (Result Pattern / no-exceptions) is relabeled here as a **general rule** since it overlaps with the base spec's error-handling contract rather than a rendering trap.

---

## 1. Missing Trap-Specific System Prompts (E–I)

Inject these alongside the Gemini prompts A–D as **CRITICAL RULES** in the agent's system context.

---

### Prompt for Trap E: Bubble Sort 3-Phase Compare-Lift

> **CRITICAL RULE — BUBBLE SORT COMPARE CHOREOGRAPHY:** A Bubble Sort T1 compare tick (150ms) is NOT a flat orange highlight. It requires a **3-phase internal choreography** with locked timing boundaries:
>
> | Phase | Time Window | Motion |
> |-------|-------------|--------|
> | Ascent | 0–60ms (40%) | Both sprites at `j` and `j+1` ease from `home_y` to `home_y - 50px` and turn orange `(255, 140, 0)` |
> | Hold | 60–100ms (27%) | Pair holds at lifted position in orange |
> | Descent | 100–150ms (33%) | Pair eases back to `home_y` |
>
> The `compare_lift_offset` is a **fixed 50px** (not proportional to panel height).
>
> If the T1 results in a swap, the subsequent T2 swap tick (400ms) has its own sub-state:
> - **0–300ms:** Pair **stays at `compare_lane_y`** (lifted) while exchanging `x` positions via linear horizontal slide.
> - **300–400ms:** Pair settles vertically back to `home_y`.
>
> This is a **horizontal slide while lifted**, NOT an arc — fundamentally different from Selection Sort and Heap Sort swap arcs. The compare-lift is the visual signature that distinguishes Bubble Sort. Without it, non-swap comparisons produce no visible motion and the learner cannot perceive the "heartbeat" scan rhythm.

---

### Prompt for Trap F: Selection Sort Triple-Pointer State Machine

> **CRITICAL RULE — SELECTION SORT POINTER ASSETS (D-068):** Selection Sort requires **three independently tracked labeled pointer arrow assets** rendered by the View layer. The model emits standard T1/T2 ticks — the View must infer pointer positions from them.
>
> | Pointer | Direction | Position | Behavior |
> |---------|-----------|----------|----------|
> | `i` | Downward arrow | **Above** baseline row | Marks sorted boundary. Advances one slot right after each swap. **Hides during swap arc motion**, reappears after settle. |
> | `j` | Upward arrow | **Below** baseline row | Scan cursor. Advances left-to-right during each scan phase. |
> | `min` | Upward arrow | **Below** baseline row | Minimum tracker. Jumps to new position when a smaller element is found during scan. |
>
> **Coalescing rule:** When `j == min_idx`, render **only** the `min` label at that position. When `j` advances past that index, both labels separate and render independently again.
>
> **Swap arc geometry** (for T2 swaps between `i` and `min_idx`):
> - `arc_height = panel_height * 0.08`
> - Lower-index sprite arcs **upward**: `exact_y = home_y - arc_height * sin(π * t)`
> - Higher-index sprite arcs **downward**: `exact_y = home_y + arc_height * sin(π * t)`
>
> An agent that skips pointer assets produces a panel with no structural position cues — the learner sees two orange circles but cannot distinguish scan cursor from minimum tracker. AT-24 and TC-A23 explicitly test for all three pointers and coalescing behavior.

---

### Prompt for Trap G: Heap Sort Sift-Down Cadence Flag (D-056)

> **CRITICAL RULE — SIFT-DOWN CADENCE FLAG:** The Controller must maintain a **per-panel boolean flag** (`sift_down_cadence`) that dynamically switches between two duration tables. Do NOT use a single static duration lookup for all Heap Sort ticks.
>
> | Tick Type | Standard Duration | Sift-Down Cadence Duration |
> |-----------|-------------------|---------------------------|
> | T1 Compare | 150ms | **100ms** |
> | T2 Swap | 400ms | **250ms** |
> | T3 Logical Tree Highlight | 200ms | **130ms** |
>
> **Flag lifecycle:**
> 1. **Set `True`** immediately after the Controller dispatches an extraction T2 swap (indices `(0, end)`).
> 2. **Reset `False`** when the next boundary T3 tick fires (start of next extraction step) OR when the algorithm completes.
> 3. **Never active during Phase 1** (Build Max-Heap) — Phase 1 sift-downs always use standard durations.
>
> **Named constants (required in code):**
> ```python
> SIFT_DOWN_COMPARE_DURATION = 100   # ms
> SIFT_DOWN_SWAP_DURATION    = 250   # ms
> SIFT_DOWN_TREE_HIGHLIGHT   = 130   # ms
> ```
>
> **Scope exclusions:** The cadence reduction does NOT apply to:
> - Extraction swap itself — always 400ms with elevated arc (`panel_height * 0.14`)
> - Boundary T3 tick — always 200ms with sweep rendering
>
> Without this flag, Heap Sort's post-extraction sift-down plays at extraction speed, losing the "rapid cascade" visual rhythm. The flag also affects total elapsed time, impacting the competitive race outcome (AT-03).

---

### Prompt for Trap H: T3 Variant Rendering — Sweep vs. Simultaneous Flash

> **CRITICAL RULE — T3 RENDERING MUST BRANCH ON CONTIGUITY:** Both Heap Sort T3 variants use the same `OpType.RANGE` enum value and the same orange accent color. You MUST inspect `highlight_indices` at render time and branch into **two completely different rendering behaviors**.
>
> **Detection heuristic:**
> ```python
> indices = tick.highlight_indices
> is_contiguous = indices == tuple(range(min(indices), max(indices) + 1))
> ```
>
> | Property | Boundary T3 (Contiguous) | Logical Tree T3 (Non-contiguous) |
> |----------|--------------------------|----------------------------------|
> | `highlight_indices` | `tuple(range(0, heap_size))` | e.g., `(1, 3, 4)` — parent + children |
> | Rendering | **Staggered left-to-right sweep** | **Simultaneous snap-on** |
> | Duration | Always 200ms | 200ms (Phase 1) or 130ms (Phase 2 cadence) |
> | Pedagogical signal | "This is the active heap region" | "This parent owns these children" |
>
> **Sweep implementation (Boundary T3):**
> - Total 200ms = 120ms sweep + 80ms hold.
> - Per-index staggered delay: `highlight_delay(i) = (i / end) * 120ms`
> - Each index snaps from default color to orange at its delay threshold (no per-index easing).
> - Requires **per-index elapsed time tracking** in the View.
> - During the final 80ms hold, all indices are highlighted together.
>
> **Snap-on implementation (Logical Tree T3):**
> - All indices in `highlight_indices` turn orange simultaneously at tick start.
> - Hold for full tick duration. No stagger.
>
> If both variants render as a uniform flash, the boundary emphasis becomes visually indistinguishable from the tree highlight, collapsing two distinct pedagogical signals into one.

---

### Prompt for Trap I: Insertion Sort Sustained Key Elevation (D-039)

> **CRITICAL RULE — INSERTION SORT CROSS-TICK KEY STATE:** The View must maintain a **per-panel "active key" state** that persists across tick boundaries. Do NOT reset sprite positions between ticks.
>
> **Key elevation lifecycle:**
> 1. **Key-selection T1 tick:** The key sprite lifts from `home_y` to `home_y - lift_offset` where `lift_offset = panel_height * 0.06`. Set the active key state: store (a) which `sprite_id` is the key, (b) that it renders at `home_y - lift_offset`, (c) that the "KEY" label (D-071) in orange `(255, 140, 0)` is visible adjacent to the lifted circle.
> 2. **All subsequent T1 compare and T2 shift ticks within the same outer pass:** The key sprite **stays elevated**. It does not move horizontally — only shifted elements move. The KEY label remains visible. The gap at the key's original baseline slot migrates leftward as elements shift right (D-072).
> 3. **T2 placement tick:** The key drops via **simultaneous diagonal motion** — horizontal to destination slot `home_x` + vertical to `home_y` — using the **same time parameter `t`** and **same ease-in-out curve** for both axes, producing a synchronized diagonal arc over 400ms. Clear the active key state. Hide the KEY label.
>
> **What breaks without this:** If the View resets sprite `y` position between ticks, the key flickers to baseline and back on every tick transition. AT-11 is an explicit regression guard: "If the key visually drops to baseline at any point before the placement tick, the test fails." AT-25 tests the KEY label lifecycle.
>
> **Sequential shift guarantee (D-060, D-064):** Each shifted element requires its own T1 compare + T2 shift pair. Never batch multiple shifts into a single T2 tick. The key remains elevated throughout all of these individual shift pairs.

---

## 2. Revised Phase 3 Addendum: Controller Cadence Logic

The Gemini Phase 3 task ("implement the headless Controller") must include explicit instruction for Trap G. Append to Phase 3:

> **Phase 3 Addendum — Cadence Flag:**
> * **Agent Task:** "Within `orchestrator.py`, implement the `sift_down_cadence` boolean flag per panel. When selecting tick duration for Heap Sort, check this flag and use the reduced duration table when `True`. Write a unit test that verifies: (a) flag is `False` during Phase 1, (b) flag is `True` after extraction swap, (c) flag resets to `False` at next boundary T3, (d) extraction swap itself always uses 400ms regardless of flag state."
> * **Validation Gate:** Dedicated cadence flag unit test passes before proceeding to Phase 4.

---

## 3. Revised Phase 4: Per-Algorithm View Sub-Phases

The original Gemini Phase 4 ("Pygame View Binding") is too coarse. The View-layer traps (E, F, H, I) are algorithm-specific and should be implemented and validated independently.

### Phase 4A: Core View Infrastructure

* **Agent Task:** "Implement `NumberSprite`, the base rendering loop, the `sprite_id → slot_index` tracking, and universal orange `(255, 140, 0)` highlight application. Wire sprites to the Controller's index delta mapping. Implement the easing-driven sprite interpolation (`exact_x`, `exact_y`) with `t` parameter progression."
* **Validation Gate:** Sprites render at correct positions and smoothly interpolate between slots using a trivial test generator. No teleportation on the `[3, 1, 3, 2, 1, 2, 3]` duplicate-value test case (Trap A).

### Phase 4B: Bubble Sort View — Compare-Lift Choreography

* **Agent Task:** "Implement the Bubble Sort 3-phase compare-lift within T1 (ascent 0–60ms, hold 60–100ms, descent 100–150ms) using `compare_lift_offset = 50px`. Implement the T2 swap as a horizontal slide at `compare_lane_y` (0–300ms) followed by vertical settle (300–400ms). Ensure both sprites lift together and settle together."
* **Validation Gate:** Manual frame-by-frame verification that (a) non-swap comparisons produce visible upward motion, (b) swap motion is horizontal-while-lifted not arc-shaped. AT-14 partial.

### Phase 4C: Selection Sort View — Pointer Assets

* **Agent Task:** "Implement the three pointer arrow assets in `views/pointer.py`: `i` (downward, above baseline), `j` (upward, below baseline), `min` (upward, below baseline). Implement coalescing: when `j == min_idx`, show only `min`. Implement `i` hiding during swap arc motion. Implement the arc swap with `arc_height = panel_height * 0.08` using `sin(π * t)` — lower-index sprite arcs up, higher-index sprite arcs down."
* **Validation Gate:** AT-24 (pointer assets present and correctly labeled), TC-A23 (pointer tracking and coalescing). Visual verification of arc direction.

### Phase 4D: Insertion Sort View — Cross-Tick Key Elevation

* **Agent Task:** "Implement the per-panel `active_key` state that persists across tick boundaries. On key-selection T1: lift sprite to `home_y - panel_height * 0.06`, show KEY label (D-071), mark gap at origin slot (D-072). Across all subsequent compare/shift ticks: maintain elevation, do not reset `y`. On placement T2: diagonal drop using shared `t` parameter for both axes, clear key state, hide label."
* **Validation Gate:** AT-11 (key never drops to baseline before placement), AT-25 (KEY label lifecycle), TC-A24. Explicit regression check: pause at mid-pass and verify key sprite `y < home_y`.

### Phase 4E: Heap Sort View — T3 Variant Split & Tree Layout

* **Agent Task:** "Implement the T3 rendering branch. Detect contiguity of `highlight_indices`. For contiguous (Boundary T3): implement staggered left-to-right sweep with per-index delay `highlight_delay(i) = (i / end) * 120ms` plus 80ms hold. For non-contiguous (Logical Tree T3): implement simultaneous snap-on. Implement the binary tree layout using `depth = floor(log2(i + 1))` and `spread = panel_width * 0.35 / (2 ** depth)`. Implement the extraction arc at `panel_height * 0.14`."
* **Validation Gate:** AT-09 (two-phase visual distinction). Manual verification: boundary sweep visibly progresses left-to-right; tree highlight appears all-at-once. Tree node positions match logarithmic formula.

---

## 4. Complete Trap Coverage Matrix

| Trap | Source | Prompt | Phase | Validation Gate |
|------|--------|--------|-------|-----------------|
| **A** — Sprite identity | Gemini | Gemini Prompt A | 4A | Duplicate-value test |
| **B** — Blocking timing | Gemini | Gemini Prompt B | 3 | TC-A4, TC-A15 |
| **C** — Heap geometry | Gemini | Gemini Prompt C | 4E | Manual tree layout |
| **D** — T3→T1→T2 sequence | Gemini | Gemini Prompt D | 1 | TC-A19 |
| **E** — Bubble 3-phase lift | Claude | **Trap E prompt** | **4B** | AT-14, manual |
| **F** — Selection pointers | Claude | **Trap F prompt** | **4C** | AT-24, TC-A23 |
| **G** — Cadence flag | Claude | **Trap G prompt** | **3 addendum** | Dedicated unit test |
| **H** — T3 variant split | Claude | **Trap H prompt** | **4E** | AT-09, manual |
| **I** — Key cross-tick state | Claude | **Trap I prompt** | **4D** | AT-11, AT-25, TC-A24 |

---

## 5. Recommended Prompt Injection Order

When constructing the agent's system context, inject prompts in this order to match the phased workflow:

1. **Phase 1 prompts:** Gemini Prompt D (tick sequences), Gemini Prompt E (Result Pattern)
2. **Phase 3 prompts:** Gemini Prompt B (timing), **Trap G prompt** (cadence flag)
3. **Phase 4A prompts:** Gemini Prompt A (sprite identity)
4. **Phase 4B prompts:** **Trap E prompt** (Bubble compare-lift)
5. **Phase 4C prompts:** **Trap F prompt** (Selection pointers)
6. **Phase 4D prompts:** **Trap I prompt** (Insertion key elevation)
7. **Phase 4E prompts:** Gemini Prompt C (Heap geometry), **Trap H prompt** (T3 variant split)

This ensures each prompt is active precisely when the agent enters its relevant phase, minimizing context window noise during earlier phases.
