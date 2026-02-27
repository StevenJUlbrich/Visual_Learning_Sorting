# 04 UI SPEC - Layout, Typography, Colors, States

Scope: This spec locks the visual and compositional behavior for v1 UI, grounded in Brick 4 (`Theme`, `Panel`) and planning notes.

## 1) UI Design Goals
- Maximize readability of algorithm mechanics (numbers + highlights).
- Keep visuals modern and consistent (dark palette, anti-aliased text, rounded geometry).
- Preserve algorithm identity at a glance using stable per-panel accents.

## 2) Window, Grid, and Spacing Rules

### 2.1 Window Title
- `"Learn Visual - Expand Knowledge"`

### 2.2 Supported Window Sizes
- Default: `1280x720` (landscape).
- Alternate: `720x996` (portrait).

### 2.3 Grid Layout
- Main visualization area is always a `2x2` panel grid.
- The grid manager uses these spacing/sizing tokens:
  - `PADDING = 20`
  - `CONTROL_BAR_HEIGHT = 48` (reserved at bottom of window for on-screen controls)
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
- Panel container background uses rounded corners.
- Corner radius token: `PANEL_RADIUS = 12`.
- Error state keeps the same radius and adds a border overlay.

## 3) Typography Rules (Locked)

### 3.1 Font Families and Sizes
- Title font: `Inter-Bold.ttf`, size `24`.
- Body/metrics/message font: `Inter-Regular.ttf`, size `16`.
- Number font: `FiraCode-Regular.ttf`, size `28`.

### 3.2 Fallback Behavior
- Font loading must attempt bundled assets from `assets/` first.
- If a font asset is missing, app must not crash.
- Fallbacks:
  - Title/body -> `pygame.font.SysFont("segoeui, arial", size)`
  - Number -> `pygame.font.SysFont("consolas, courier", 28)`

### 3.3 Text Rendering Quality
- All text rendering must use anti-aliasing (`antialias=True`).

## 4) Per-Panel Composition (Locked)

Each algorithm panel contains the following UI regions and elements:

### 4.1 Header Region
- Left side: algorithm title (e.g., `Bubble Sort`).
- Right side: metrics line `"<Big-O> | Steps: <n> | Comps: <n> | Writes: <n>"`.
- Default placement tokens from Brick 4:
  - Title anchor: `x = rect.x + 20`, `y = rect.y + 15`.
  - Metrics right aligned with right inset `20`, baseline around `y = rect.y + 20`.

### 4.2 Message Line (Required)
- A message line is included and shows latest `SortResult.message`.
- Purpose: expose current action/error semantics for learning clarity.
- Styling: body font + secondary text color in normal state, error color in failure state.

### 4.3 Array Rendering Region
- Numbers only (no bars).
- Horizontal spacing uses internal array padding token: `ARRAY_X_PADDING = 40`.
- Number slots are evenly distributed across available width.
- Numbers are centered in their slot.
- Vertical anchor defaults to panel center (`rect.y + rect.height // 2`).

### 4.4 State Overlays
- Completion state: all numbers in completion color.
- Error state: red border + readable failure message (`"Failed: ..."`).

## 5) Color Identity Decision (Locked)

Decision: **Per-panel algorithm accent colors** (not a single global highlight color).

Rationale from planning + Brick 4:
- Planning explicitly calls out algorithm color coding as a teaching aid.
- Brick 4 theme defines dedicated accent constants per algorithm.

### 5.1 Core Palette
- App background: `(30, 30, 36)`
- Panel background: `(45, 45, 53)`
- Primary text: `(240, 240, 245)`
- Secondary text: `(170, 170, 180)`
- Default array value: `(100, 150, 255)`
- Complete state: `(80, 220, 120)`
- Error state: `(235, 80, 80)`

### 5.2 Algorithm Accent Mapping
- Bubble: `(0, 255, 255)` (cyan)
- Insertion: `(255, 0, 255)` (magenta)
- Merge: `(170, 0, 255)` (purple)
- Selection: `(255, 80, 80)` (red)

Mapping is fixed by algorithm name and does not rotate at runtime.

## 6) State-to-Visual Rules
- Idle/pre-first-tick: panel shell + header + zero steps visible.
- Running tick:
  - Non-highlighted indices -> default array color.
  - `highlight_indices` -> panel accent color.
  - Step counter increments only on successful non-terminal ticks (defined in data contracts).
- Complete tick:
  - Entire array row uses completion color.
  - Panel remains visible and static.
- Failure tick:
  - Panel gets error border and failure text.
  - No further step increments.

## 7) Control Surface (UI Scope)
- On-screen controls are required for v1:
  - Play/Pause
  - Step
  - Restart
  - Speed toggle (`1x -> 1.5x -> 2x`)
- Keyboard shortcuts must mirror these controls.

## 8) Explicit Non-Goals for UI v1
- No bar chart rendering.
- No per-panel independent playback controls.
- No historical trail/replay layers.
- No audio UI elements.
