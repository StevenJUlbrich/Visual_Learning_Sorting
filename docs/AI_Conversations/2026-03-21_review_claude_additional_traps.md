# Additional Agent Traps — Claude Code Review (2026-03-21)

Context: Supplementary review following `2026-03-21_review_gemini.md`. The Gemini review correctly identified four high-risk agent traps (Sprite Identity, Independent Timing, Heap Tree Geometry, T3→T1→T2 Sequence). This document identifies **five additional traps** of comparable severity that were not covered.

---

### Trap E — Bubble Sort Sub-State Timing Within a Single T1 Tick

**The Trap:** An AI agent will treat a T1 compare tick as a simple 150ms highlight. The spec actually requires a **3-phase internal choreography** within that single 150ms window — ascent, hold, and descent — with locked timing boundaries. An agent that emits a flat orange highlight for 150ms produces a visually broken Bubble Sort that looks identical to Selection Sort's highlight-only T1.

**What the spec requires** (`10_ANIMATION_SPEC.md` Section 5.1.1, `05_ALGORITHMS_VIS_SPEC.md` Section 4.1):

| Phase | Time Window | Motion |
| --- | --- | --- |
| Ascent | 0–60ms (40%) | Both sprites at `j` and `j+1` ease from `home_y` to `home_y - 50px` |
| Hold | 60–100ms (27%) | Pair holds at lifted position in orange |
| Descent | 100–150ms (33%) | Pair eases back to `home_y` |

Additionally, the T2 swap (400ms) has its own sub-state: the pair **stays at the compare lane** while exchanging `x` positions (0–300ms), then settles vertically back to baseline (300–400ms). This is a **linear horizontal slide while lifted**, not an arc — fundamentally different from Selection Sort and Heap Sort swaps.

**Why it matters:** The compare-lift is the visual signature that distinguishes Bubble Sort from the other algorithms. Without it, there is no visible motion on non-swap comparisons, and the learner cannot perceive the "heartbeat" scan rhythm described in the pedagogical notes (`05_ALGORITHMS_VIS_SPEC.md` Section 9).

**Relevant tests:** AT-14 (Bubble Sort Swap-Lift Counter Sync), TC-A19 is Heap-specific but Bubble Sort's choreography has no equivalent automated trace test — it relies on manual verification (08_TEST_PLAN Section 6).

---

### Trap F — Selection Sort Triple-Pointer State Machine

**The Trap:** An AI agent will implement Selection Sort with highlight-only rendering (two orange indices), which satisfies the model layer contract. But the View layer requires **three independently tracked labeled pointer arrow assets** (`i`, `j`, `min`) with specific positioning rules and coalescing behavior. This is a rendering-layer state machine that has no model-layer equivalent — the model emits standard T1/T2 ticks and the View must infer pointer positions from them.

**What the spec requires** (D-068, `05_ALGORITHMS_VIS_SPEC.md` Section 4.2, `views/pointer.py`):

1. **`i` pointer** — downward arrow **above** the baseline row, marks the sorted boundary. Advances one slot right after each swap. **Hides during swap arc motion**, reappears after settle.
2. **`j` pointer** — upward arrow **below** the baseline row, scan cursor. Advances left-to-right during each scan phase.
3. **`min` pointer** — upward arrow **below** the baseline row, minimum tracker. Jumps when a smaller element is found.
4. **Coalescing rule:** When `j == min_idx`, only the `min` label is shown. When `j` advances past that index, both labels separate again.

**Why it matters:** An agent that skips the pointer assets produces a Selection Sort panel with no structural position cues — the learner sees two orange circles but cannot distinguish the scan cursor from the minimum tracker. AT-24 explicitly tests for all three pointers and the coalescing behavior.

**Relevant tests:** AT-24 (Selection Sort Pointer Assets), TC-A23 (Pointer Tracking).

---

### Trap G — Sift-Down Cadence Flag (Duration Switching)

**The Trap:** An AI agent will use a single duration lookup table for all Heap Sort ticks. The spec requires the Controller to maintain a **per-panel boolean flag** (`sift_down_cadence`) that dynamically switches between two duration tables depending on whether the current ticks are part of a post-extraction sift-down repair.

**What the spec requires** (`10_ANIMATION_SPEC.md` Section 5.4.2, D-056):

| Tick Type | Standard Duration | Sift-Down Cadence Duration |
| --- | --- | --- |
| T1 Compare | 150ms | **100ms** |
| T2 Swap | 400ms | **250ms** |
| T3 Logical Tree Highlight | 200ms | **130ms** |

**Flag lifecycle:**
- Set to `True` after the Controller dispatches an extraction T2 swap (`(0, end)`).
- Reset to `False` when the next boundary T3 tick fires (start of next extraction step) or when the algorithm completes.
- **Never active** during Phase 1 (Build Max-Heap) — Phase 1 sift-downs always use standard durations.

**Why it matters:** Without the cadence flag, Heap Sort's post-extraction sift-down plays at the same speed as the extraction itself, losing the "rapid cascade" visual rhythm described in the reference video. The flag also has a **race timing impact** — reduced durations decrease Heap Sort's total elapsed time, affecting the competitive outcome.

**Relevant tests:** No dedicated automated test exists for cadence timing in the current test plan. The race outcome (AT-03) would indirectly catch gross timing errors, but a subtle bug (e.g., cadence active during Phase 1) would only manifest as a slightly wrong elapsed time.

---

### Trap H — T3 Variant Rendering (Sweep vs. Simultaneous Flash)

**The Trap:** Both Heap Sort T3 variants use the same `OpType.RANGE` enum value and the same orange accent color. An AI agent will implement a single T3 rendering path. The spec requires the View to **inspect `highlight_indices` contiguity** at render time and branch into two completely different rendering behaviors.

**What the spec requires** (`03_DATA_CONTRACTS.md` "OpType.RANGE — Heap Sort Highlight Variants", `10_ANIMATION_SPEC.md` Section 5.4.1 and 5.4.3):

| Property | Boundary T3 (Variant A) | Logical Tree T3 (Variant B) |
| --- | --- | --- |
| `highlight_indices` | Contiguous: `tuple(range(0, heap_size))` | Non-contiguous: e.g., `(1, 3, 4)` |
| Rendering | **Staggered left-to-right sweep** over 120ms + 80ms hold | **Simultaneous snap-on** across all indices |
| Detection heuristic | `indices == tuple(range(min(indices), max(indices) + 1))` | Anything else |

**The sweep implementation** is non-trivial: each index transitions from default to orange at a staggered offset `highlight_delay(i) = (i / end) * 120ms`, requiring per-index elapsed time tracking in the View. The remaining 80ms is a hold phase where all indices are highlighted together.

**Why it matters:** If an agent applies a uniform flash to both variants, the boundary emphasis (pedagogically signaling "this is the active heap region") becomes visually indistinguishable from the tree highlight (signaling "this parent owns these children"). The two signals collapse into one, defeating the spec's pedagogical intent.

**Relevant tests:** AT-09 (Heap Sort Two-Phase Visual Distinction) tests for visible boundary highlights but relies on manual observation of the sweep vs. flash distinction. No automated test validates the sweep rendering.

---

### Trap I — Insertion Sort Sustained Key Elevation Across Tick Boundaries

**The Trap:** An AI agent will implement per-tick rendering: apply highlight and motion at tick start, clear at tick end. For Insertion Sort, the key sprite must remain **elevated above the baseline across multiple tick boundaries** — from the key-selection T1 through all compare and shift ticks until the final T2 placement drop. If the View resets sprite `y` position between ticks, the key will flicker to baseline and back on every tick transition.

**What the spec requires** (D-039, `05_ALGORITHMS_VIS_SPEC.md` Section 4.3, `10_ANIMATION_SPEC.md` Section 5.3):

- The key sprite lifts to `home_y - lift_offset` (where `lift_offset = panel_height * 0.06`) on the key-selection T1 tick.
- The key **stays at that `y` position** across all subsequent T1 compare and T2 shift ticks within the same outer pass. The key does not move horizontally during compare/shift ticks — only shifted elements move.
- The key drops back to `home_y` **only** on the T2 placement tick, via a simultaneous diagonal motion (horizontal to destination slot + vertical to baseline) using the same `t` parameter for both axes.

**Implementation implication:** The View must maintain a **per-panel "active key" state** that persists across tick boundaries. This state tracks: (a) which sprite is the key, (b) that it should render at `home_y - lift_offset`, and (c) that the "KEY" label (D-071) should be visible. The state is set on key-selection T1 and cleared on placement T2. An agent that treats each tick as an isolated rendering event will break this.

**Why it matters:** AT-11 is an explicit regression guard: "If the key visually drops to baseline at any point before the placement tick... the test fails." AT-25 tests the KEY label lifecycle. Both require cross-tick state persistence.

**Relevant tests:** AT-11 (Insertion Sort Lift-and-Settle Sequence), AT-25 (Insertion Sort KEY Label and Gap), TC-A24 (KEY Label Lifecycle).

---

## Summary Table

| Trap | Risk | Spec Source | Automated Test Coverage |
| --- | --- | --- | --- |
| **E** — Bubble Sort sub-state timing | View produces flat highlight instead of 3-phase lift | 10_ANIMATION Section 5.1.1 | Manual only (AT-14 partial) |
| **F** — Selection Sort triple pointer | No structural cues, scan/min indistinguishable | D-068, 05_ALGS Section 4.2 | AT-24, TC-A23 |
| **G** — Sift-down cadence flag | Wrong race timing, no cascade rhythm | D-056, 10_ANIMATION Section 5.4.2 | No dedicated test |
| **H** — T3 variant rendering split | Boundary and tree highlights visually collapse | 03_DATA Section RANGE variants | Manual only (AT-09 partial) |
| **I** — Insertion key cross-tick elevation | Key flickers to baseline between ticks | D-039, 10_ANIMATION Section 5.3 | AT-11, AT-25, TC-A24 |

## Recommended Agent Prompting Strategy

When instructing an AI agent to implement the View layer, explicitly call out these cross-cutting concerns:

1. **Bubble Sort T1 is not a simple highlight** — it has internal sub-phases with locked timing splits.
2. **Selection Sort needs a pointer renderer** — three assets with independent tracking and coalescing logic.
3. **Heap Sort Controller needs a cadence flag** — duration selection is stateful, not a static lookup.
4. **T3 rendering must branch on contiguity** — one OpType, two rendering paths.
5. **Insertion Sort key elevation is cross-tick state** — the View must persist key identity across tick boundaries, not reset per-tick.

These traps complement the Gemini review's traps A–D. Together, A–I represent the nine highest-risk areas for an AI agent implementing this spec.
