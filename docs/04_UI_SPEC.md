# 04 UI SPEC - Layout, Typography, Colors, States

Scope: This spec locks the visual and compositional behavior for v1 UI, grounded in Brick 4 (`Theme`, `Panel`) and planning notes.

## 1) UI Design Goals

- Maximize readability of algorithm mechanics (numbers + highlights).
- Keep visuals modern and consistent (dark palette, anti-aliased text, rounded geometry).
- Preserve algorithm identity at a glance using panel title and grid position.
- Meet WCAG 2.1 AAA contrast for large text (≥ 4.5:1) on all number sprites and AAA for normal text (≥ 7:1) on all informational text rendered at body size.

## 2) Window, Grid, and Spacing Rules

### 2.1 Window Title

- `"Learn Visual - Expand Knowledge"`

### 2.2 Supported Window Sizes

- Two fixed presets selected via `config.toml`:
  - **Desktop:** 1280×720
  - **Tablet:** 1024×768
- Window size is locked at startup. The `pygame.display.set_mode()` call does not include the `RESIZABLE` flag. No `VIDEORESIZE` event handling is needed (D-077).
- Portrait orientation (720×996) is removed (D-079).

### 2.3 Grid Layout

- Main visualization area is always a `2x2` panel grid.
- The grid manager eliminates hardcoded magic numbers and uses these proportional spacing tokens calculated dynamically from window dimensions:
  - `PADDING = window_width * 0.015`
  - `CONTROL_BAR_HEIGHT = window_height * 0.07` (reserved at bottom of window for on-screen controls)
- The grid occupies the space above the control bar:
  - `grid_height = window_height - CONTROL_BAR_HEIGHT - PADDING`
- Panel dimensions are computed dynamically:
  - `panel_width = (window_width - (PADDING * 3)) // 2`
  - `panel_height = (grid_height - (PADDING * 3)) // 2`
- Panel positions:
  - Top-left: `(PADDING, PADDING)`
  - Top-right: `(PADDING * 2 + panel_width, PADDING)`
  - Bottom-left: `(PADDING, PADDING * 2 + panel_height)`
  - Bottom-right: `(PADDING * 2 + panel_width, PADDING * 2 + panel_height)`
- Control bar position:
  - Anchored at `y = window_height - CONTROL_BAR_HEIGHT`, full window width, centered content.

### 2.4 Panel Geometry

- Panel container background uses `pygame.draw.rect(..., border_radius=PANEL_RADIUS)` for rounded corners. No surface clipping mask is required; child elements (text, sprites) are positioned within the panel rect insets and do not need to be clipped to the rounded edge.
- Corner radius token: `PANEL_RADIUS = 12`.
- Error state keeps the same radius and adds a border overlay.

### 2.5 Control Button Layout

- The control bar contains three buttons:
  - Play/Pause
  - Step
  - Restart

Buttons scale proportionally or center horizontally inside the control bar with equal padding.

### 2.6 Resolution Geometry Reference

Derived values for the two supported presets:

| Token | Desktop (1280×720) | Tablet (1024×768) |
| --- | --- | --- |
| `PADDING` | 19px | 15px |
| `CONTROL_BAR_HEIGHT` | 50px | 54px |
| `panel_width` | 611px | 489px |
| `panel_height` | 296px | 327px |
| `slot_width` (7 items) | 78px | 63px |
| `arc_height` | 24px | 26px |
| `lift_offset` | 18px | 20px |

These are computed values for reference; the implementation calculates them once at startup from the configured window dimensions. Both presets guarantee panel widths ≥ 489px, ensuring the Heap Sort tree renders with ample horizontal spacing.

## 3) Typography Rules (Locked)

### 3.1 Font Families and Sizes

- Title font: `Inter-Bold.ttf`, size `24`.
- Body/metrics/message font: `Inter-Regular.ttf`, size `16`.
- Number font: `FiraCode-Regular.ttf`, size `28`.

Font size `28` at screen resolution (96 DPI) equals approximately 21pt, which qualifies as **WCAG large text** (≥ 18pt). This is relevant for contrast ratio thresholds on number sprites.

Font size `16` at 96 DPI equals approximately 12pt, which is **WCAG normal text**. All informational text at this size must meet the stricter 7:1 AAA contrast ratio.

### 3.2 Font Asset Directory

Font files are bundled in the `assets/fonts/` directory at the repository root:

```text
assets/
└── fonts/
    ├── Inter-Bold.ttf
    ├── Inter-Regular.ttf
    └── FiraCode-Regular.ttf
```

### 3.3 Fallback Behavior

- Font loading must attempt bundled assets from `assets/fonts/` first.
- If a font asset is missing, app must not crash.
- Fallbacks:
  - Title/body → `pygame.font.SysFont("segoeui, arial", size)`
  - Number → `pygame.font.SysFont("consolas, courier", 28)`

### 3.4 Text Rendering Quality

- All text rendering must use anti-aliasing (`antialias=True`).

### 3.5 Font Surface Caching

- Each `NumberSprite` must pre-render and cache its text surfaces for each color state it can display: default array color, panel accent (highlight) color, completion color, and settled/extracted color.
- Cached surfaces are created once at sprite initialization (and again on restart).
- During rendering, the sprite selects the appropriate pre-cached surface based on its current visual state rather than calling `font.render()` every frame.
- This eliminates redundant anti-aliased text rendering across 28 sprites at 60 FPS.

## 4) Per-Panel Composition (Locked)

Each algorithm panel contains the following UI regions and elements, laid out vertically from top to bottom using proportional insets.

### 4.1 Header Region

The header is a **strictly vertical stack**: Title → Metrics → Message, rendered top-to-bottom with no horizontal adjacency between elements. This vertical stacking is a layout invariant that provides a consistent visual rhythm across both resolution presets.

#### 4.1.1 Header Vertical Rhythm

The three header elements flow downward from the panel's top-left inset corner, separated by fixed pixel gaps:

```
┌─ Panel ─────────────────────────────────────────┐
│  ↕ HEADER_INSET_Y                               │
│  ← HEADER_INSET_X →                             │
│  ┌─ Title ────────────────────────────────────┐  │
│  │ "Heap Sort"  (Inter-Bold 24, primary text) │  │
│  └────────────────────────────────────────────┘  │
│  ↕ METRICS_GAP (4px)                             │
│  ┌─ Metrics ──────────────────────────────────┐  │
│  │ "O(n log n) | 03.45s | Steps: 35 | ..."   │  │
│  └────────────────────────────────────────────┘  │
│  ↕ MESSAGE_GAP (6px)                             │
│  ┌─ Message ──────────────────────────────────┐  │
│  │ "Swapping index 0 (value 7) with index 6…" │  │
│  └────────────────────────────────────────────┘  │
│                                                   │
│  ═══════ Array Rendering Region ═══════           │
│         4   7   2   6   1   5   3                 │
│                                                   │
└───────────────────────────────────────────────────┘
```

**Spacing tokens:**

- `HEADER_INSET_X = panel_width * 0.03` (minimum 12px) — left margin from panel edge.
- `HEADER_INSET_Y = panel_height * 0.04` (minimum 10px) — top margin from panel edge.
- `METRICS_GAP = 4px` — fixed gap between title bottom and metrics top.
- `MESSAGE_GAP = 6px` — fixed gap between metrics bottom and message top.

**Total header height budget:**

`header_total = HEADER_INSET_Y + title_height + METRICS_GAP + metrics_height + MESSAGE_GAP + message_height`

At fixed font sizes (24px title, 16px body × 2 lines), the approximate header height is:

- Desktop (296px panel): ~24 + 4 + 16 + 6 + 16 = 66px rendered content + ~12px top inset = **~78px** (26% of panel height).
- Tablet (327px panel): same pixel height = **~78px** (24% of panel height).

The header must never exceed **35% of panel height**. If a future font or resolution change would exceed this budget, the message line is the first element to be omitted (metrics and title are mandatory).

#### Title Line

- Plain algorithm name text in title font, left-aligned (e.g., "Bubble Sort"). No colored dot prefix or decorative symbol — algorithm identity comes from the panel title text and grid position.
- Anchor: `x = rect.x + HEADER_INSET_X`, `y = rect.y + HEADER_INSET_Y`.
- Color: primary text `(240, 240, 245)`.

#### Metrics Line

- Displayed **below** the title line, never beside it. This vertical separation provides a consistent layout across both resolution presets.
- Anchor: `x = rect.x + HEADER_INSET_X`, `y = title_y + title_height + METRICS_GAP`.
- Format: `"<Big-O> | <elapsed> | Steps: <n> | Comps: <n> | Writes: <n>"`.
- Example: `"O(n²) | 03.45s | Steps: 35 | Comps: 21 | Writes: 30"`.
- Color: secondary text `(190, 190, 200)`.
- Font: body font (Inter-Regular 16).
- **Overflow rule:** If the metrics string exceeds `panel_width - (HEADER_INSET_X * 2)`, the view truncates with an ellipsis (`…`) from the right. Counter labels are never abbreviated — the string truncates from the `Writes:` field leftward, preserving Big-O and elapsed time as highest priority. With the minimum panel width now 489px (Tablet preset), overflow is not expected under normal conditions.

#### Message Line

- Shows latest `SortResult.message`.
- Purpose: expose current action/error semantics for learning clarity.
- Anchor: `x = rect.x + HEADER_INSET_X`, `y = metrics_y + metrics_height + MESSAGE_GAP`.
- Styling: body font + secondary text color in normal state, error text color `(255, 120, 120)` in failure state.
- If the message text exceeds panel width minus insets, it is truncated with an ellipsis (`…`) rather than wrapping.

### 4.3 Array Rendering Region

- Numbers only (no bars).
- Each number is rendered inside a **circular outlined ring** (never a square or bare text).
  - Circle diameter is proportional to slot width (~65% of `slot_width`).
  - Ring stroke width: 3px.
  - Circle interior fill matches the panel background `(45, 45, 53)` — the ring outline is the primary color signal.
  - The ring outline color and the number text color always match, changing together based on state.
- Horizontal spacing uses internal array padding proportional token: `ARRAY_X_PADDING = panel_width * 0.05`.
- Number slots are evenly distributed across available width.
- Numbers are centered in their slot. (`slot_width = (panel_width - ARRAY_X_PADDING*2) / array_size`)
- Vertical anchor defaults to panel center (`rect.y + rect.height // 2`).

**Heap Sort Exception:** The Heap Sort panel uses a different layout than the other three algorithms. Instead of a single horizontal row, it renders a **binary tree visualization** of the active heap in the upper portion of the array region, with a compact sorted-element row below. The other three algorithm panels (Bubble, Selection, Insertion) retain the standard single horizontal row layout.

#### 4.3.2 Heap Sort Tree Layout Geometry

The tree occupies the vertical space between the header bottom and the sorted row. The sorted row is anchored near the panel bottom.

**Available area:**

- `tree_top = header_total + 10` (below header with small gap)
- `sorted_row_y = rect.y + panel_height - SORTED_ROW_MARGIN` where `SORTED_ROW_MARGIN = panel_height * 0.18`
- `tree_area_height = sorted_row_y - tree_top - 20` (gap between tree and sorted row)

**Tree node sizing:**

- `tree_node_diameter = min(slot_width * 0.55, tree_area_height / 4)` — scales with panel but never exceeds 1/4 of tree area height (ensures 3 levels fit)
- Ring stroke: 3px (same as flat-row sprites)

**Level positioning (vertical):**

For a 7-element array (3 tree levels: 0, 1, 2):

- `level_y(d) = tree_top + (d * level_spacing)` where `level_spacing = tree_area_height / max_depth` and `max_depth = floor(log2(heap_size))`
- Level 0 (root): 1 node at `level_y(0)`
- Level 1: 2 nodes at `level_y(1)`
- Level 2: up to 4 nodes at `level_y(2)`

**Node positioning (horizontal):**

Each node's horizontal position is computed from the panel center using binary subdivision:

- `node_x(index) = panel_center_x + horizontal_offset(index)`
- The horizontal spread at each level uses: `spread = panel_width * 0.35 / (2 ** depth)` — tighter at deeper levels
- Root (index 0): `x = panel_center_x`
- Left child (index 1): `x = panel_center_x - spread_level_1`
- Right child (index 2): `x = panel_center_x + spread_level_1`
- Index 3: `x = panel_center_x - spread_level_1 - spread_level_2`
- Index 4: `x = panel_center_x - spread_level_1 + spread_level_2`
- Index 5: `x = panel_center_x + spread_level_1 - spread_level_2`
- Index 6: `x = panel_center_x + spread_level_1 + spread_level_2`

General formula for any index `i`:

```
depth = floor(log2(i + 1))
position_in_level = i - (2**depth - 1)
total_at_level = 2**depth
x = panel_rect.x + ARRAY_X_PADDING + (position_in_level + 0.5) * (panel_width - 2*ARRAY_X_PADDING) / total_at_level
y = level_y(depth)
```

**Parent-child edges:**

- Straight lines from parent node center `(px, py)` to child node center `(cx, cy)`
- Default edge color: `(120, 120, 130)` — subtle, does not compete with node highlights
- Active edge color (during T3 Logical Tree Highlight): `(255, 140, 0)` orange — matches the highlighted nodes
- Line width: 2px

**Sorted row below tree:**

- Positioned at `sorted_row_y`, full panel width with `ARRAY_X_PADDING`
- Uses the same `slot_width` as the flat-row panels: `slot_width = (panel_width - ARRAY_X_PADDING*2) / array_size`
- Sorted elements render as steel-blue `(130, 150, 190)` rings at their final array index positions
- Active heap slots in the sorted row render as dim placeholder outlines `(60, 60, 68)` with no number — they represent "this element is in the tree above"
- Circle diameter matches the flat-row sprite size (~65% of `slot_width`), not the tree node size

**Heap boundary marker:**

- Vertical dashed line between the last active heap slot and the first sorted slot in the sorted row
- Dash pattern: 6px dash, 4px gap
- Color: `(150, 150, 160)`
- Label "heap boundary" in `(150, 150, 160)` at ~12px below the sorted row

**Phase label:**

- Text "BUILD MAX-HEAP" (Phase 1) or "EXTRACTION" (Phase 2) rendered in orange `(255, 140, 0)`
- Font: body font (Inter-Regular 16)
- Positioned to the right of the root node or centered below the root, within the tree area
- The label updates when the algorithm transitions from Phase 1 to Phase 2

#### 4.3.1 Bubble Sort Instructional Assets

- The Bubble Sort panel must render a `ComparisonPointer` asset as a **green upward-pointing arrow**.
- The `ComparisonPointer` is anchored **below the baseline row**, centered under the active comparison slot, and moves horizontally as the active index changes.
- The Bubble Sort panel must render a `LimitLine` asset as a **vertical dashed line**.
- The `LimitLine` resides **between array slots**, not on top of a number sprite, and marks the current right-side unsorted boundary.
- At the end of each Bubble Sort pass, the `LimitLine` shifts one slot to the left.

### 4.4 Panel Surface Strategy

- Each panel draws directly to the main display surface. Panels do not use independent `pygame.Surface` objects or `subsurface`.
- Rounded corners are achieved via `pygame.draw.rect` with `border_radius`. Child elements are positioned within insets and do not require clipping.

### 4.5 Sprite Z-Ordering Rule (Locked)

Within each panel, sprites are drawn in a defined order to prevent visual occlusion of the active algorithmic focus:

1. **Baseline sprites** (sprites at rest, `exact_y == home_y`) are drawn in array-index order (index 0 first, index 6 last).
2. **Lifted sprites** — any sprite whose `exact_y < home_y` — **must always render on top of all baseline sprites.** This includes:
   - Insertion Sort keys elevated in the compare lane during a pass.
   - Bubble Sort adjacent pairs during a compare-lift pulse.
   - The upward-arcing sprite in a swap animation.
3. **Among multiple lifted sprites**, the sprite with the **smallest `exact_y`** (highest on screen) draws last (topmost). If tied, array-index order breaks the tie.
4. **Restoration:** When a lifted sprite returns to `home_y` (lift descent completes, swap arc lands, key settles into place), it immediately reverts to default index-order rendering. No z-elevation persists after the animation concludes.

This rule is a **layout integrity invariant**: a lifted key must never disappear behind a shifting baseline element, regardless of panel dimensions. The full motion-level specification is in `10_ANIMATION_SPEC.md` Section 4. See also D-033.

### 4.6 State Overlays

- Completion state: panel background transitions to muted completion green `(35, 55, 42)` (D-078). All numbers display in completion color `(80, 220, 120)`. The HUD stats (Big-O, elapsed time, steps, comparisons, writes) freeze at their final values and remain displayed on the green panel. The green background provides a definitive "finish line" signal visible at a glance.
- Error state: error border + readable failure message.
  - Error border color: `(235, 80, 80)`.
  - Error border thickness = 3px.
  - Error message text color: `(255, 120, 120)` (lighter red for contrast compliance at body font size).

#### 4.6.1 Bubble Sort HUD Overlay

- The Bubble Sort panel must include a **persistent instructional HUD** anchored to the **bottom-left corner** of the panel content area.
- The HUD displays two live text counters: `Comparison Count` and `Exchange Count`.
- Both counters remain visible throughout idle, running, paused, and completed states.
- `Comparison Count` increments as each comparison begins.
- `Exchange Count` increments when a swap is executed.

## 5) Color Identity Decision (Locked)

Decision: **Universal active highlight color** — all algorithms share a single accent color for compare, swap, and range emphasis ticks.

Rationale: Algorithm identity is communicated through panel title text and grid position, not highlight color. A universal accent simplifies the palette, reduces cognitive load, and avoids per-algorithm color memorization.

### 5.1 Core Palette

All colors are verified against panel background `(45, 45, 53)` for WCAG 2.1 contrast compliance.

| Role | Color (RGB) | Contrast vs Panel BG | WCAG Rating |
| --- | --- | --- | --- |
| App background | `(30, 30, 36)` | — | N/A (no text) |
| Panel background | `(45, 45, 53)` | — | Base surface |
| Panel background (completed) | `(35, 55, 42)` | — | Completion finish line (D-078) |
| Primary text | `(240, 240, 245)` | 12.0:1 | AAA normal |
| Secondary text | `(190, 190, 200)` | 7.4:1 | AAA normal |
| Default array value | `(100, 150, 255)` | 4.8:1 | AAA large |
| Complete state | `(80, 220, 120)` | 7.7:1 | AAA normal |
| Error border | `(235, 80, 80)` | 3.8:1 | AA large (border only) |
| Error text | `(255, 120, 120)` | 5.5:1 | AA normal, AAA large |
| Settled/extracted | `(130, 150, 190)` | 4.6:1 | AAA large |

### 5.2 Universal Active Highlight

**Universal active highlight: `(255, 140, 0)` orange** — applied to all algorithms during compare, swap, and range emphasis ticks.

This color is applied to number sprites rendered at FiraCode 28px (large text, AAA threshold = 4.5:1). Orange `(255, 140, 0)` achieves **5.9:1** contrast against panel background `(45, 45, 53)`, exceeding AAA for large text.

Algorithm identity is communicated through panel title and grid position, not highlight color.

#### Heap Sort Active Highlight Scope

Orange is the universal active color shared by all algorithms. For Heap Sort specifically, during boundary emphasis T3 ticks, orange highlights the active heap region — elements at indices `0..heap_size-1` that are still participating in the heap data structure. Once an element is extracted from the heap (swapped to the sorted region beyond the heap boundary), it permanently loses its orange highlight eligibility and transitions to the settled/extracted color (see Section 5.3). The settled/extracted color `(130, 150, 190)` still applies to elements that have left the heap. This ensures a clear visual contract: **orange = active; steel-blue = sorted and done**.

### 5.3 Settled/Extracted State Color (Formalized)

The **settled/extracted color** `(130, 150, 190)` (desaturated steel-blue) represents elements that have **permanently left the active unsorted region** and entered their final sorted position. This color serves a specific pedagogical purpose: it provides a visible "sorted history" layer that tracks algorithm progress *without* using the vibrant completion green `(80, 220, 120)`, which is reserved exclusively for the final completion tick when the entire array is confirmed sorted.

#### Visual Contract

- **Settled ≠ Complete.** Settled steel-blue communicates "this element is done, but the algorithm is still working." Completion green communicates "the entire sort has finished." This distinction prevents the learner from mistaking a partially sorted region for a fully sorted array.
- **Desaturated, not dimmed.** The steel-blue is visually distinct from the vivid default array blue `(100, 150, 255)` through **desaturation** rather than dimming. The learner perceives settled elements as "quieter" — still readable, but no longer demanding attention.
- **One-way transition.** Once an element enters the settled state, it does not revert to the default array color. It remains steel-blue until the completion tick, at which point it transitions to green with all other elements.

#### v1 Scope — Heap Sort

In v1, the settled/extracted color applies **exclusively to Heap Sort** extracted elements — elements at indices `>= heap_size` that have been swapped out of the active heap via root-to-end extraction. This creates the progressive visual narrative described in Section 6: steel-blue accumulates from the right (sorted region) while orange/blue remains on the left (active heap).

Other algorithms in v1 do not use the settled color because:

- **Bubble Sort:** The right-side settled suffix is tracked by the `LimitLine` boundary and cursor exclusion rules rather than by a separate settled-color treatment.
- **Selection Sort:** Elements swapped into the sorted left region could semantically qualify, but Selection Sort's visual emphasis is on the scan/minimum pattern, and adding a third color state would clutter a panel that already has accent + default + highlight transitions.
- **Insertion Sort:** The growing sorted region on the left is conceptually similar, but the key-lift/shift/drop choreography already provides strong visual separation between "sorted" and "unsorted" without needing a color distinction.

#### Post-v1 Extensibility

The settled color is designed to be algorithm-agnostic. If future versions add sorted-region visualization to Bubble, Selection, or Insertion Sort (e.g., via boundary markers or progressive color transitions), the same `(130, 150, 190)` can be applied without palette changes. The WCAG AAA contrast (4.6:1 for large text) ensures readability across all panels.

### 5.4 Color Changes from Prior Spec (Rationale)

The following colors were adjusted to meet AAA accessibility requirements:

- **Secondary text:** `(170, 170, 180)` → `(190, 190, 200)`. The original had 5.93:1 contrast, failing AAA for normal text (7:1 required). The new value achieves 7.4:1.
- **~~Insertion accent (magenta)~~:** Superseded — per-algorithm accents replaced by universal orange `(255, 140, 0)` highlight (see Section 5.2).
- **~~Selection accent (red)~~:** Superseded — per-algorithm accents replaced by universal orange `(255, 140, 0)` highlight (see Section 5.2).
- **Settled/extracted:** `(60, 90, 155)` → `(130, 150, 190)`. The original had 2.03:1, failing even AA for any text size. The new value is a desaturated steel-blue that achieves 4.6:1 (AAA large text) while remaining visually distinct from the vivid default array blue `(100, 150, 255)`. The distinction is now achieved through **desaturation** rather than dimming, because a dimmed variant cannot simultaneously be darker than the default (4.8:1) and meet the 4.5:1 AAA floor.
- **Error text:** `(235, 80, 80)` → `(255, 120, 120)` (for message text only; error border remains `(235, 80, 80)`). The original had 3.77:1 at body font size (normal text, needs 7:1 for AAA). The new value achieves 5.5:1, meeting AA for normal text and AAA for large text. True AAA normal-text red on this dark background is not achievable without shifting to pink, so AA is accepted for error message text as a practical compromise.

## 6) State-to-Visual Rules

- Idle/pre-first-tick: panel shell + header + zero steps visible.
- Running tick:
  - Non-highlighted indices → default array color.
  - `highlight_indices` → universal active highlight color (orange).
  - Step counter increments only on successful non-terminal ticks (defined in data contracts).
  - Bubble Sort additionally renders the `ComparisonPointer` as a green upward-pointing arrow below the baseline row and the `LimitLine` as a dashed boundary between slots.
  - Bubble Sort keeps the bottom-left HUD visible with live `Comparison Count` and `Exchange Count` values.
- Settled/extracted state (Heap Sort only):
  - Applies to elements in the **sorted region** of the Heap Sort panel — indices beyond the current heap boundary (`index >= heap_size`) that have been extracted via root-to-end swaps.
  - These elements render in the settled/extracted color `(130, 150, 190)` (desaturated steel-blue) **permanently** for the remainder of the sort, even when not highlighted.
  - Settled elements are **never** rendered in the orange accent color. If a T3 boundary highlight or a Logical Tree Highlight tick fires, settled indices outside the heap boundary are excluded from the highlight set.
  - The transition is one-way: once an element enters the sorted region after an extraction swap, it does not revert to the default array color.
  - **Progressive sorted-boundary transition:** The settled region grows from right to left as extractions proceed. After each extraction swap, the sorted boundary advances one position leftward (from index `n-1` toward index `1`), and the newly placed element immediately adopts the settled color. The View determines settled status by comparing each element's current array index against `heap_size`: any element at index `≥ heap_size` renders in settled color. This produces a progressive visual history — the learner watches the right side of the array gradually fill with steel-blue numbers, one element per extraction, while the active heap on the left (default blue / orange highlights) visibly shrinks. The growing steel-blue region directly illustrates that the sorted output is being built incrementally from the maximum downward.
  - **Extraction sequence for `[4, 7, 2, 6, 1, 5, 3]`:** After the max-heap `[7, 6, 5, 4, 1, 2, 3]` is built, the first extraction places `7` at index 6 (settled). The next places `6` at index 5 (settled). The boundary continues leftward: indices 6, 5, 4, 3, 2, 1 transition in sequence. After the final extraction, only index 0 remains in the active heap — it is the last element and needs no swap, so it transitions on the completion tick when all elements turn green.
- Complete tick:
  - Panel background transitions to muted completion green `(35, 55, 42)` (D-078).
  - Entire array row uses completion color `(80, 220, 120)`.
  - HUD stats (Big-O, elapsed time, steps, comparisons, writes) freeze at their final values on the green panel.
  - Panel remains visible and static — a definitive "finish line" for the race.
  - For Heap Sort, the settled/extracted color is **replaced** by the completion color — all seven numbers turn green uniformly.
- Failure tick:
  - Panel gets error border and failure text.
  - Message line switches to error text color.
  - No further step increments.

## 7) Control Surface (UI Scope)

- On-screen controls are required for v1:
  - Play/Pause
  - Step
  - Restart
- Keyboard shortcuts must mirror these controls.

## 8) Explicit Non-Goals for UI v1

- No bar chart rendering.
- No per-panel independent playback controls.
- No historical trail/replay layers.
- No audio UI elements.
- No proportional font scaling (font sizes are fixed at 24/16/28 across presets).
- No runtime window resizing (window is locked at startup — D-077).
- No portrait orientation (D-079).
