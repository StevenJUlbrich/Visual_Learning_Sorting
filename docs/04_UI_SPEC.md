# 04 UI SPEC - Layout, Typography, Colors, States

Scope: This spec locks the visual and compositional behavior for v1 UI, grounded in Brick 4 (`Theme`, `Panel`) and planning notes.

## 1) UI Design Goals

- Maximize readability of algorithm mechanics (numbers + highlights).
- Keep visuals modern and consistent (dark palette, anti-aliased text, rounded geometry).
- Preserve algorithm identity at a glance using stable per-panel accents.
- Meet WCAG 2.1 AAA contrast for large text (≥ 4.5:1) on all number sprites and AAA for normal text (≥ 7:1) on all informational text rendered at body size.

## 2) Window, Grid, and Spacing Rules

### 2.1 Window Title

- `"Learn Visual - Expand Knowledge"`

### 2.2 Supported Window Sizes

- Dynamic target based on `config.toml` window resolution.

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

Derived values for the two supported configurations:

| Token | Landscape (1280x720) | Portrait (720x996) |
| --- | --- | --- |
| `PADDING` | 19px | 11px |
| `CONTROL_BAR_HEIGHT` | 50px | 70px |
| `panel_width` | 611px | 343px |
| `panel_height` | 296px | 441px |
| `slot_width` (7 items) | 78px | 44px |
| `arc_height` | 24px | 35px |
| `lift_offset` | 18px | 26px |

These are computed values for reference; the implementation always calculates dynamically from the window dimensions.

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

The header is a **strictly vertical stack**: Title → Metrics → Message, rendered top-to-bottom with no horizontal adjacency between elements. This vertical stacking is a layout invariant that prevents text overflow in narrow panels (portrait mode at 343px width) and provides a consistent visual rhythm across all resolutions.

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

- Landscape (296px panel): ~24 + 4 + 16 + 6 + 16 = 66px rendered content + ~12px top inset = **~78px** (26% of panel height).
- Portrait (441px panel): same pixel height = **~78px** (18% of panel height).

The header must never exceed **35% of panel height**. If a future font or resolution change would exceed this budget, the message line is the first element to be omitted (metrics and title are mandatory).

#### Title Line

- Algorithm name in title font, left-aligned.
- Anchor: `x = rect.x + HEADER_INSET_X`, `y = rect.y + HEADER_INSET_Y`.
- Color: primary text `(240, 240, 245)`.

#### Metrics Line

- Displayed **below** the title line, never beside it. This vertical separation is the primary overflow prevention mechanism for portrait panels (343px width), where a side-by-side layout would exceed available horizontal space.
- Anchor: `x = rect.x + HEADER_INSET_X`, `y = title_y + title_height + METRICS_GAP`.
- Format: `"<Big-O> | <elapsed> | Steps: <n> | Comps: <n> | Writes: <n>"`.
- Example: `"O(n²) | 03.45s | Steps: 35 | Comps: 21 | Writes: 30"`.
- Color: secondary text `(190, 190, 200)`.
- Font: body font (Inter-Regular 16).
- **Portrait overflow rule:** If the metrics string exceeds `panel_width - (HEADER_INSET_X * 2)`, the view truncates with an ellipsis (`…`) from the right. Counter labels are never abbreviated — the string truncates from the `Writes:` field leftward, preserving Big-O and elapsed time as highest priority.

#### Message Line

- Shows latest `SortResult.message`.
- Purpose: expose current action/error semantics for learning clarity.
- Anchor: `x = rect.x + HEADER_INSET_X`, `y = metrics_y + metrics_height + MESSAGE_GAP`.
- Styling: body font + secondary text color in normal state, error text color `(255, 120, 120)` in failure state.
- If the message text exceeds panel width minus insets, it is truncated with an ellipsis (`…`) rather than wrapping.

### 4.3 Array Rendering Region

- Numbers only (no bars).
- Horizontal spacing uses internal array padding proportional token: `ARRAY_X_PADDING = panel_width * 0.05`.
- Number slots are evenly distributed across available width.
- Numbers are centered in their slot. (`slot_width = (panel_width - ARRAY_X_PADDING*2) / array_size`)
- Vertical anchor defaults to panel center (`rect.y + rect.height // 2`).

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

This rule is a **layout integrity invariant**: a lifted key must never disappear behind a shifting baseline element, regardless of panel dimensions or orientation. The full motion-level specification is in `10_ANIMATION_SPEC.md` Section 4. See also D-033.

### 4.6 State Overlays

- Completion state: all numbers in completion color.
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

### 4.7 Bubble Sort Specific Assets (Locked)

Based on instructional reference sequences, the Bubble Sort panel requires specific persistent UI markers that reside in the background rendering layer (drawn *before* base sprites to prevent text occlusion).

#### 4.7.1 The Limit Line
- **Visual Role:** Marks the boundary between the active unsorted region and the right-side settled suffix.
- **Asset Rendering:** A vertical dashed line spanning the height of the `Array Rendering Region`.
- **Color:** `(190, 190, 200)` (Secondary Text color for WCAG AAA compliance).
- **Label:** The word "limit" rendered in `Inter-Regular 16` at the top of the dashed line.

#### 4.7.2 The Comparison Cursor
- **Visual Role:** Tracks the current $j$ index of the inner loop scan.
- **Asset Rendering:** An upward-pointing geometric arrow or caret.
- **Color:** `(80, 220, 120)` (Complete state green) to draw the eye to the active index.
- **Placement:** Anchored horizontally to the center of the active slot, vertically positioned directly below the array baseline (`home_y`).

#### 4.7.3 HUD Updates
- The Metrics Line (Section 4.1.1) must actively display real-time increments for `Comps: <n>` (Comparisons) and `Writes: <n>` (Exchanges/Swaps) as they occur in the animation loop.

## 5) Color Identity Decision (Locked)

Decision: **Per-panel algorithm accent colors** (not a single global highlight color).

Rationale from planning + Brick 4:

- Planning explicitly calls out algorithm color coding as a teaching aid.
- Brick 4 theme defines dedicated accent constants per algorithm.

### 5.1 Core Palette

All colors are verified against panel background `(45, 45, 53)` for WCAG 2.1 contrast compliance.

| Role | Color (RGB) | Contrast vs Panel BG | WCAG Rating |
| --- | --- | --- | --- |
| App background | `(30, 30, 36)` | — | N/A (no text) |
| Panel background | `(45, 45, 53)` | — | Base surface |
| Primary text | `(240, 240, 245)` | 12.0:1 | AAA normal |
| Secondary text | `(190, 190, 200)` | 7.4:1 | AAA normal |
| Default array value | `(100, 150, 255)` | 4.8:1 | AAA large |
| Complete state | `(80, 220, 120)` | 7.7:1 | AAA normal |
| Error border | `(235, 80, 80)` | 3.8:1 | AA large (border only) |
| Error text | `(255, 120, 120)` | 5.5:1 | AA normal, AAA large |
| Settled/extracted | `(130, 150, 190)` | 4.6:1 | AAA large |

### 5.2 Algorithm Accent Mapping

All accent colors are applied to number sprites rendered at FiraCode 28px (large text, AAA threshold = 4.5:1).

| Algorithm | Color (RGB) | Contrast vs Panel BG | WCAG Rating |
| --- | --- | --- | --- |
| Bubble | `(0, 255, 255)` cyan | 10.9:1 | AAA large |
| Insertion | `(255, 50, 255)` magenta | 4.7:1 | AAA large |
| Heap | `(255, 140, 0)` orange | 5.9:1 | AAA large |
| Selection | `(255, 95, 95)` red | 4.6:1 | AAA large |

Mapping is fixed by algorithm name and does not rotate at runtime.

#### Heap Sort Accent Scope

The Heap accent color (orange) is **reserved exclusively for active heap members** — elements at indices `0..heap_size-1` that are still participating in the heap data structure. Once an element is extracted from the heap (swapped to the sorted region beyond the heap boundary), it permanently loses its orange accent eligibility and transitions to the settled/extracted color (see Section 5.3). This ensures a clear visual contract: **orange = still in the heap; steel-blue = sorted and done**.

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
- **Insertion accent (magenta):** `(255, 0, 255)` → `(255, 50, 255)`. The original had 4.35:1, failing AAA even for large text (4.5:1 required). Adding a small green channel raises luminance to 4.7:1 while preserving the magenta identity.
- **Selection accent (red):** `(255, 80, 80)` → `(255, 95, 95)`. The original had 4.24:1, failing AAA for large text. The brighter variant reaches 4.6:1 while remaining clearly red.
- **Settled/extracted:** `(60, 90, 155)` → `(130, 150, 190)`. The original had 2.03:1, failing even AA for any text size. The new value is a desaturated steel-blue that achieves 4.6:1 (AAA large text) while remaining visually distinct from the vivid default array blue `(100, 150, 255)`. The distinction is now achieved through **desaturation** rather than dimming, because a dimmed variant cannot simultaneously be darker than the default (4.8:1) and meet the 4.5:1 AAA floor.
- **Error text:** `(235, 80, 80)` → `(255, 120, 120)` (for message text only; error border remains `(235, 80, 80)`). The original had 3.77:1 at body font size (normal text, needs 7:1 for AAA). The new value achieves 5.5:1, meeting AA for normal text and AAA for large text. True AAA normal-text red on this dark background is not achievable without shifting to pink, so AA is accepted for error message text as a practical compromise.

## 6) State-to-Visual Rules

- Idle/pre-first-tick: panel shell + header + zero steps visible.
- Running tick:
  - Non-highlighted indices → default array color.
  - `highlight_indices` → panel accent color.
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
  - Entire array row uses completion color.
  - Panel remains visible and static.
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
- No proportional font scaling (font sizes are fixed at 24/16/28 across resolutions).
