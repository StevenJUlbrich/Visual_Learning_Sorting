# Phase 5 Archive — View Layer (Sprites, Panels, Layout)

**Archived from DEVLOG.md.** Seven sub-phases (5a–5g), 185 view-layer tests (235 cumulative). Delivered 2026-04-23 through 2026-05-01.

**Sub-phases:**

- 5a: window.py — GridLayout, load_preset, init_display (25 tests)
- 5b: sprite.py — NumberSprite, ColorState, COLOR_MAP (19 tests)
- 5c: panel.py — PanelRenderer, header rhythm, state overlays (31 tests)
- 5d: tree_layout.py — binary tree node positions, edges, sorted row (38 tests, TC-A20/A21/A22)
- 5e: pointer.py — Selection Sort i/j/min arrows, coalescing (25 tests, TC-A23)
- 5f: limitline.py — Bubble Sort dashed boundary, advance/reset (21 tests)
- 5g: hud.py — BubbleHUD counters + HeapPhaseLabel + HeapBoundaryLabel (26 tests)

---

## 2026-05-01 09:35 — Phase 5g closed: hud.py (post-action)

### Worked on

Created `src/visualizer/views/hud.py` (BubbleHUD: comparisons/exchanges counters at panel bottom-left, exchanges_y = panel.bottom − 22, comparisons_y one font-height + 4px above; HeapPhaseLabel: orange phase label centered on panel.centerx, caller passes label_y; HeapBoundaryLabel: "heap boundary" text centered on boundary_x, LINE_COLOR imported from limitline.py as single source of truth) and `tests/unit/test_hud.py` (26 tests: color constant values, position formulas, bounds checks, draw no-crash for all three classes).

### Results

- `uv run pytest tests/unit/test_hud.py -v`: **26/26 PASSED** (first run, zero corrections)
- `uv run pytest tests/unit/ -v`: **235/235 PASSED** (cumulative)
- `PYRIGHT_PYTHON_GLOBAL_NODE=false uv run pyright src/visualizer/views/hud.py tests/unit/test_hud.py`: **0 errors, 0 warnings**
- `uv run ruff check` + `uv run ruff format --check`: **clean** (test_hud.py reformatted once — multiline argument list in two draw no-crash tests collapsed by ruff)

### Corrections

1. **Ruff format** — two draw-test function calls reformatted from multiline to single-line. Tests still passed throughout.

### Decisions

- **`BOTTOM_MARGIN = 22`, `LINE_SPACING = 4`** — keeps both counter lines well within panel bounds on the Desktop preset (comparisons_y ≈ 270, exchanges_y ≈ 294, panel.bottom = 316). Exported as constants so tests can verify the formula without hardcoding magic numbers.
- **`PHASE_LABEL_COLOR = COLOR_MAP[ColorState.ACTIVE]`** — expression, not a literal, evaluated at import time. Guarantees that phase label color stays in sync with the universal active highlight (D-067) if the color ever changes.
- **`BOUNDARY_LABEL_COLOR = LINE_COLOR`** — alias, not a copy. Single source of truth: limitline.py owns the value; hud.py just references it. Consistent with the decision recorded in Phase 5f closeout.
- **Three classes, zero cross-dependencies** — BubbleHUD, HeapPhaseLabel, HeapBoundaryLabel share no state. Each can be instantiated and tested independently. The Controller will own all three and call draw() each frame.

### Open questions

- None.

### Phase 5 (View Layer) status

Phase 5 is complete as a standalone unit (all seven sub-phases 5a–5g pass). The remaining view behaviors (Z-ordering, highlight state transitions, compare lane, sorted-sweep animation) are Controller-driven and will be integrated in Phase 6 (orchestrator.py). No view module requires changes before Phase 6 begins.

### Next

Phase 6: `orchestrator.py` — Controller / Orchestrator (independent queues, operation timing, event dispatch, sprite state management).

---

## 2026-05-01 09:25 — Phase 5g start: hud.py plan (pre-action)

### Model / session

Sonnet 4.6. View layer — HUD overlays: BubbleHUD counters + HeapPhaseLabel + HeapBoundaryLabel.

### Plan

Create `src/visualizer/views/hud.py` (three classes: BubbleHUD counter overlay at panel bottom-left, HeapPhaseLabel centered-horizontal phase label, HeapBoundaryLabel "heap boundary" marker below sorted row) and `tests/unit/test_hud.py` (~20+ tests: position formulas, color constants, draw no-crash, bounds checks).

### Critical context

- `LINE_COLOR = (150, 150, 160)` imported from `limitline.py` — single source of truth for boundary marker color.
- `COLOR_MAP[ColorState.ACTIVE] = (255, 140, 0)` imported from `sprite.py` — phase label orange.
- `compute_header_inset_x(panel_width)` from `panel.py` → `max(int(w * 0.03), 12)` = 18 for Desktop.
- BubbleHUD anchors: `counter_x = panel_rect.x + inset_x`, `exchanges_y = panel_rect.bottom - BOTTOM_MARGIN`, `comparisons_y = exchanges_y - font_height - LINE_SPACING`.
- HeapPhaseLabel: center_x = panel_rect.centerx; caller passes label_y.
- HeapBoundaryLabel: caller passes boundary_x and label_y; text centered on boundary_x.
- BOTTOM_MARGIN = 22px, LINE_SPACING = 4px.
- This is the last Phase 5 sub-phase.

---

## 2026-04-30 10:12 — Phase 5f closed: limitline.py (post-action)

### Worked on

Created `src/visualizer/views/limitline.py` (LimitLine class: `boundary_index`, `x_position`, `is_visible` properties; `advance()`, `reset()`, `draw()`; `LINE_COLOR` exported for reuse in hud.py) and `tests/unit/test_limitline.py` (21 tests: initial state, advance/reset behavior, visibility transitions, x formula, slot-center bounds check, line-span invariant, color constant, draw no-crash for all states).

### Results

- `uv run pytest tests/unit/test_limitline.py -v`: **21/21 PASSED** (first run, zero corrections)
- `uv run pytest tests/unit/ -v`: **209/209 PASSED** (cumulative)
- `PYRIGHT_PYTHON_GLOBAL_NODE=false uv run pyright src/visualizer/views/limitline.py tests/unit/test_limitline.py`: **0 errors** (3 pre-existing pytest.approx warnings)
- `uv run ruff check` + `uv run ruff format --check`: **clean** (limitline.py reformatted once — multiline x_position expression collapsed to one line by ruff)

### Corrections

1. **Ruff format** — `x_position` return expression reformatted from multiline to single line (fits within 88 chars). Tests still passed throughout.

### Decisions

- **`LINE_COLOR` exported at module level** — doc 04 §4.3.2 confirms the same color `(150, 150, 160)` is used for Heap Sort boundary marker. Exporting from `limitline.py` establishes it as the single source of truth; `hud.py` will import from here.
- **`is_visible = 0 < boundary_index < array_size`** — the line has no meaning when at the far right (array_size, before any pass) or at 0 (everything sorted). Strictly interior visibility prevents rendering a line at a nonsensical position.
- **`advance()` guard at 0** — prevents `boundary_index` going negative if the Controller somehow calls advance() more times than there are passes. Safe and silent.

### Open questions

- None.

### Next

Phase 5g: `hud.py` (Bubble Sort HUD overlay counters + Heap Sort phase label).

---

## 2026-04-30 10:12 — Phase 5f start: limitline.py plan (pre-action)

### Model / session

Sonnet 4.6. View layer — LimitLine: Bubble Sort vertical dashed boundary line.

### Plan

Create `src/visualizer/views/limitline.py` (LimitLine class — boundary_index, x_position, is_visible, advance, reset, draw) and `tests/unit/test_limitline.py` (~20 tests: position formula, visibility states, advance/reset, draw no-crash, slot-center bounds check, line span invariant).

### Critical context

- Line sits at `x = panel_rect.x + array_x_padding + (boundary_index * slot_width)` — left edge of the boundary slot, i.e. midpoint between slot [boundary_index-1] and slot [boundary_index].
- Initial: `boundary_index = array_size` → is_visible=False (no boundary before first pass).
- Visible when `0 < boundary_index < array_size`.
- advance() decrements by 1, guarded at 0.
- Dash pattern: 6px draw, 4px gap; draw with pygame.draw.line per segment.
- `LINE_COLOR = (150, 150, 160)` — shared with Heap Sort boundary marker (doc 04 §4.3.2); exported so hud.py can reuse.
- Line vertical extent: `home_y ± ring_radius ± LINE_MARGIN` (keeps line contained to array region).

### Pre-computed Desktop values (array_size=7, ring_radius=25, home_y=167)

- Initial x = 19 + 30 + 7*(551/7) = 600.0 (past last slot)
- After advance: x = 49 + 6*(551/7) ≈ 521.29; between slot 5 center (481.93) and slot 6 center (560.64) ✓
- Line top = 167 - 25 - 12 = 130; line bottom = 167 + 25 + 12 = 204

### Exit criteria

- `uv run pytest tests/unit/test_limitline.py -v` all green
- `uv run pytest tests/unit/ -v` cumulative (188 + new tests)
- `PYRIGHT_PYTHON_GLOBAL_NODE=false uv run pyright src/visualizer/views/limitline.py tests/unit/test_limitline.py` 0 errors
- `uv run ruff check` + `uv run ruff format --check` clean

---

## 2026-04-30 09:51 — Phase 5e closed: pointer.py (post-action)

### Worked on

Created `src/visualizer/views/pointer.py` (`PointerSet` class: `slot_center_x`, `i_arrow_y`, `jmin_arrow_y`, `coalesced_pointers`, `draw`; private `_draw_i_pointer` and `_draw_jmin_pointer` helpers) and `tests/unit/test_pointer.py` (25 tests: arrow position invariants, slot center formula, D-068 coalescing all cases, color constants, draw no-crash for all states including edge slots 0 and 6).

### Results

- `uv run pytest tests/unit/test_pointer.py -v`: **25/25 PASSED** (first run, zero corrections)
- `uv run pytest tests/unit/ -v`: **188/188 PASSED** (cumulative)
- `PYRIGHT_PYTHON_GLOBAL_NODE=false uv run pyright src/visualizer/views/pointer.py tests/unit/test_pointer.py`: **0 errors** (6 pre-existing pytest.approx warnings)
- `uv run ruff check` + `uv run ruff format --check`: **clean** (both files already formatted)

### Corrections

None — first-run clean on all four exit criteria.

### Decisions

- **`coalesced_pointers` exposed as public method** — allows tests to verify the D-068 coalescing rule (j==min → j hidden) directly without pixel inspection. `draw()` calls it internally, guaranteeing tests and production code share the same coalescing path.
- **Colors imported from existing constants** — `POINTER_I_COLOR = PRIMARY_TEXT` (panel.py), `POINTER_J_COLOR = POINTER_MIN_COLOR = COLOR_MAP[ColorState.ACTIVE]` (sprite.py). No new color definitions.
- **`round()` for polygon vertices** — `slot_center_x()` returns float; converting to int via `round()` before polygon construction avoids pygame type ambiguity and produces crisp pixel-aligned arrows.

### Open questions

- None.

### Next

Phase 5f: `limitline.py` (Bubble Sort vertical dashed boundary line).

---

## 2026-04-30 09:51 — Phase 5e start: pointer.py plan (pre-action)

### Model / session

Sonnet 4.6. View layer — PointerSet: Selection Sort i/j/min labeled arrow geometry and rendering.

### Plan

Create `src/visualizer/views/pointer.py` (PointerSet class — slot_center_x, i_arrow_y, jmin_arrow_y, coalesced_pointers, draw) and `tests/unit/test_pointer.py` (~25 tests: arrow positions, slot center formula, coalescing D-068, color constants, draw no-crash).

### Critical context

- Three arrows: `i` (downward, above baseline), `j` and `min` (upward, below baseline).
- Coalescing rule (D-068): when `j_index == min_index` both not None, only `min` is shown. `j` is hidden.
- `i_arrow_y() = home_y - ring_radius - ARROW_GAP` (above ring, tip points toward ring).
- `jmin_arrow_y() = home_y + ring_radius + ARROW_GAP` (below ring, tip points toward ring).
- Colors: i uses PRIMARY_TEXT (240,240,245) from panel.py; j and min use COLOR_MAP[ColorState.ACTIVE] (255,140,0) from sprite.py.
- Use `pygame.draw.polygon` for triangle arrows, font.render for labels.
- Expose `coalesced_pointers(i,j,min)` method so tests can verify coalescing logic directly.

### Pre-computed Desktop values (panel_rect=Rect(19,19,611,297))

- ARRAY_X_PADDING=30, slot_width=551/7≈78.714, ring_radius=25, home_y=167
- i_arrow_y=137 (above baseline), jmin_arrow_y=197 (below baseline)

### Exit criteria

- `uv run pytest tests/unit/test_pointer.py -v` all green
- `uv run pytest tests/unit/ -v` cumulative (163 + new tests)
- `PYRIGHT_PYTHON_GLOBAL_NODE=false uv run pyright src/visualizer/views/pointer.py tests/unit/test_pointer.py` 0 errors
- `uv run ruff check` + `uv run ruff format --check` clean

---

## 2026-04-30 09:23 — Phase 5d closed: tree_layout.py (post-action)

### Worked on

Created `src/visualizer/views/tree_layout.py` (pure-geometry `TreeLayout` class: `node_positions`, `edges`, `sorted_row_x`, `tree_node_radius` property; public attributes `tree_top`, `sorted_row_y`, `tree_area_height`, `tree_node_diameter`) and `tests/unit/test_tree_layout.py` (38 tests covering TC-A20/A21/A22, geometry invariants, sorted row formula).

### Results

- `uv run pytest tests/unit/test_tree_layout.py -v`: **38/38 PASSED** (first run after 1 test fix)
- `uv run pytest tests/unit/ -v`: **163/163 PASSED** (cumulative)
- `PYRIGHT_PYTHON_GLOBAL_NODE=false uv run pyright src/visualizer/views/tree_layout.py tests/unit/test_tree_layout.py`: **0 errors** (6 pre-existing pytest.approx warnings, same as other test files)
- `uv run ruff check` + `uv run ruff format --check`: **clean** (both files reformatted once, then clean)

### Corrections

1. **`pytest.approx` as right operand of `>=`** — `assert abs(...) >= pytest.approx(...)` raises `TypeError`. Fixed by using `>= desktop.tree_node_diameter` directly (the gap is 137.75px vs 34.0px; no floating-point ambiguity).
2. **3 unused imports** — `SORTED_ROW_MARGIN_RATIO`, `TREE_HEADER_GAP`, `TREE_SORTED_GAP` imported but not directly referenced in tests (they're implicit in fixture construction). Removed from test imports; pyright `reportUnusedImport` resolved.
3. **RUF007** — ruff flags `zip(level2, level2[1:])` as preferring `itertools.pairwise()`. Switched to `itertools.pairwise(level2)`.
4. **Ruff format** — `tree_layout.py` reformatted once (long `edges` return type annotation). Tests passed throughout.

### Decisions

- **Public attributes for `tree_top`, `sorted_row_y`, `tree_area_height`, `tree_node_diameter`** — tests need to verify geometry constraints; exposing as attributes is simpler than properties and consistent with `window.py`'s approach.
- **`tree_node_radius` as `@property`** — always derived from `tree_node_diameter`, so a property enforces the `int(diameter) // 2` invariant.
- **Level spacing division-by-zero guard** — `max_depth=0` when `heap_size=1`; `level_spacing=0.0` prevents the div by zero, and `level_y(0) = tree_top + 0*0 = tree_top` correctly positions the single root node.

### Open questions

- None.

### Next

Phase 5e: `pointer.py` (Selection Sort i/j/min arrows with coalescing, D-068, TC-A23).

---

## 2026-04-30 09:23 — Phase 5d start: tree_layout.py plan (pre-action)

### Model / session

Sonnet 4.6. Pure geometry module — Heap Sort binary tree node positions, edges, sorted row.

### Plan

Create `src/visualizer/views/tree_layout.py` (TreeLayout class, pure coordinates, no rendering) and `tests/unit/test_tree_layout.py` (~24 tests covering TC-A20 node positioning, TC-A21 edge connectivity, TC-A22 tree shrinking, plus additional geometry invariants).

### Critical context

- PURE GEOMETRY — no `pygame.draw` calls anywhere in `tree_layout.py`. Coordinates only.
- Authoritative horizontal formula (doc 04 §4.3.2 code block):
  `x = panel_rect.x + ARRAY_X_PADDING + (position_in_level + 0.5) * (panel_width - 2*ARRAY_X_PADDING) / total_at_level`
  Produces root exactly at `panel_rect.x + panel_width/2` (float center).
- `sorted_row_y = panel_rect.y + panel_height - int(panel_height * 0.18)`
- `tree_area_height = sorted_row_y - tree_top - 20`
- `tree_node_diameter = min(slot_width * 0.55, tree_area_height / 4)` — limits to 1/4 height (3 levels fit)
- Edge case: `heap_size=1` → `max_depth=0`, avoid div-by-zero in level_spacing; `level_spacing=0.0`.
- Edge case: `heap_size=0` → empty lists.
- `tree_node_radius = int(tree_node_diameter) // 2` — must be int.
- Public attributes for `tree_top`, `sorted_row_y`, `tree_area_height`, `tree_node_diameter` so tests can verify geometry without exposing private state.

### Pre-computed Desktop values (header_total=78)

- tree_top=107, sorted_row_y=263, tree_area_height=136, tree_node_diameter=34.0, radius=17
- Root x=324.5 (panel centerx=324, diff=0.5 ≤ 1px ✓)
- Level 1 dist from center: 137.75px each side
- Level 2 min adjacent gap: 137.75px >> 34.0px (no overlap)

### Exit criteria

- `uv run pytest tests/unit/test_tree_layout.py -v` all green
- `uv run pytest tests/unit/ -v` cumulative green (125 + new tests)
- `PYRIGHT_PYTHON_GLOBAL_NODE=false uv run pyright src/visualizer/views/tree_layout.py tests/unit/test_tree_layout.py` 0 errors
- `uv run ruff check` + `uv run ruff format --check` clean on both files

---

## 2026-04-30 09:08 — Phase 5c closed: panel.py (post-action)

### Worked on

Created `src/visualizer/views/panel.py` (`PanelState` enum, `PanelRenderer` class, module-level helpers `compute_header_inset_x`, `compute_header_inset_y`, `compute_header_total`, `truncate_text`) and `tests/unit/test_panel.py` (31 tests covering header spacing tokens, anchor positions, header height budget, color constants, pixel-check background variants, draw no-crash, and metrics truncation).

### Results

- `uv run pytest tests/unit/test_panel.py -v`: **31/31 PASSED** (first run)
- `uv run pytest tests/unit/ -v`: **125/125 PASSED** (cumulative)
- `PYRIGHT_PYTHON_GLOBAL_NODE=false uv run pyright src/visualizer/views/panel.py tests/unit/test_panel.py`: **0 errors, 0 warnings, 0 informations**
- `uv run ruff check` + `uv run ruff format --check`: **clean** (both files reformatted once, then clean)

### Corrections

1. **Ruff format** — reformatted both files on first pass (long lines in fixture signatures, blank-line after function signatures). Tests still passed during the unformatted state. Applied `uv run ruff format` and re-confirmed 125/125.

### Decisions

- **Module-level helpers (`compute_header_inset_x`, `compute_header_inset_y`, `compute_header_total`)** — exposed as public module-level functions so tests can verify spacing-token math directly without constructing a `PanelRenderer`. Same pattern as `GridLayout` in `window.py`.
- **`truncate_text` public** — tests need to assert truncation behavior directly. Naming mirrors `truncate_text` (not `_truncate`) to avoid pyright `reportPrivateUsage` and give tests clean import access.
- **`PANEL_BG` imported from `sprite.py` as `PANEL_BG_COLOR`** — single source of truth for panel background color (45, 45, 53); panel.py aliases it as `PANEL_BG`.
- **Pixel-check tests use center of DESKTOP_RECT** — the rounded-rect interior is guaranteed solid color at the center, so `surface.get_at((cx, cy))` reliably reflects the fill color for both RUNNING and COMPLETED states.

### Open questions

- None.

### Next

Phase 5d: `tree_layout.py` (Heap Sort binary tree positioning, edge rendering, sorted row).

---

## 2026-04-30 09:08 — Phase 5c start: panel.py plan (pre-action)

### Model / session

Sonnet 4.6. View layer — PanelRenderer: background, header vertical rhythm, state overlays.

### Plan

Create `src/visualizer/views/panel.py` (PanelRenderer class + spacing-token helpers) and `tests/unit/test_panel.py` (coordinate math + color constant + pixel-check tests). ~26 tests targeting header spacing tokens, anchor positions, header budget, color constants, background state variants, and metrics truncation.

### Critical context

- Header spacing tokens computed from panel dimensions: `HEADER_INSET_X = max(int(w * 0.03), 12)`, `HEADER_INSET_Y = max(int(h * 0.04), 10)`. Fixed gaps: `METRICS_GAP=4`, `MESSAGE_GAP=6`.
- Three-line header stack: Title (Inter-Bold 24, primary text `(240,240,245)`) → Metrics (Inter-Regular 16, secondary `(190,190,200)`) → Message (same font; error color `(255,120,120)` in failed state).
- Header height must not exceed 35% of panel height. Message is the first element dropped if over budget.
- Panel BG `(45,45,53)` imported from sprite.py as `PANEL_BG_COLOR`. Completion BG `(35,55,42)` (D-078). Error adds `(235,80,80)` border, 3px, same border_radius.
- Draw directly to main display surface — no subsurface (doc 04 §4.4).
- Panel does NOT own sprites, tree layout, pointers, limitline, or HUD.
- Truncate with `…` (U+2026) when metrics or message exceeds `panel_width - inset_x*2`.

### Exit criteria

- `uv run pytest tests/unit/test_panel.py -v` all green
- `uv run pytest tests/unit/ -v` cumulative green (94 + new tests)
- `PYRIGHT_PYTHON_GLOBAL_NODE=false uv run pyright src/visualizer/views/panel.py tests/unit/test_panel.py` 0 errors
- `uv run ruff check` + `uv run ruff format --check` clean on both files

---

## 2026-04-24 16:52 — Phase 5b closed: sprite.py (post-action)

### Worked on

Created `src/visualizer/views/sprite.py` (`ColorState`, `COLOR_MAP`, `NumberSprite`) and `tests/unit/test_sprite.py` (19 tests: home_x/home_y math for slots 0/3/6, ring_radius, initial color state, is_lifted, surface_cache completeness, update_home preserves exact coords, draw no-error, sprite identity, distinct-slot home_x). Fixed doc 12 §4.3: `(100, 149, 237)` → `(100, 150, 255)` to align with doc 04 §5.1 authoritative palette.

### Results

- `uv run pytest tests/unit/test_sprite.py -v`: **19/19 PASSED** (first run)
- `uv run pytest tests/unit/ -v`: **94/94 PASSED** (cumulative)
- `PYRIGHT_PYTHON_GLOBAL_NODE=false uv run pyright src/visualizer/views/sprite.py tests/unit/test_sprite.py`: **0 errors** (12 pre-existing `pytest.approx` warnings)
- `uv run ruff check` + `uv run ruff format --check`: **clean**
- `grep "(100, 150, 255)" docs/design_docs/12_ANIMATION_FOUNDATION.md`: **1 match** — doc 12 fix confirmed

### Corrections

1. **`reportPrivateUsage` on `_surface_cache`** — pyright strict flags single-underscore attributes accessed outside the class. Tests legitimately inspect the cache to verify init behavior. Renamed `_surface_cache` → `surface_cache` (public). `_build_surface_cache` remains private (internal helper).
2. **`replace_all` collateral** — using `replace_all` to rename `_surface_cache` also mangled `_build_surface_cache` → `_buildsurface_cache` and two test function names (`test_surface_cache_*` → `testsurface_cache_*`). Fixed with targeted edits. Tests still passed during the mangled state because pytest runs whatever names it finds; the names themselves were wrong. Lesson: use targeted edits for partial-token renames, not `replace_all`.
3. **Import order** — ruff I001: `pygame` must precede `pytest` in test imports (alphabetical within third-party group). Swapped.
4. **Ruff format** — reformatted `home_x` multi-line expression in sprite.py from 4-line to 1-line form (within 88 char limit).
5. **Doc 12 color fix** — `(100, 149, 237)` → `(100, 150, 255)` to align with doc 04 §5.1 authoritative palette (WCAG contrast ratios calculated against `(100, 150, 255)`).

### Decisions

- **`surface_cache` public, `_build_surface_cache` private** — the cache itself is inspectable state; the builder is an internal initialization detail. Public cache allows tests and future Controller code to inspect state without hacks.
- **Five color states as `Enum`** — `ColorState.DEFAULT` etc. gives pyright-checkable exhaustiveness over the `COLOR_MAP` dict; string literals would not.

### Open questions

- None.

### Next

Phase 5c: `panel.py` (per-algorithm panel rendering — header vertical rhythm, array region, state overlays).

---

## 2026-04-24 16:47 — Phase 5b start: sprite.py plan (pre-action)

### Model / session

Sonnet 4.6. Core View layer class — NumberSprite with ring rendering, font caching, color states.

### Plan

Create `src/visualizer/views/sprite.py` (NumberSprite class) and `tests/unit/test_sprite.py` (coordinate math + color state tests). Fix doc 12 §4.3 color discrepancy.

### Critical context

- Doc 04 §5.1 says default array blue is `(100, 150, 255)` — this is authoritative (WCAG contrast calculated against it).
- Doc 12 §4.3 says `(100, 149, 237)` — this is wrong. Fix doc 12 to match doc 04.
- Ring: 3px stroke, diameter = int(slot_width * 0.65), interior fill = panel background (45, 45, 53).
- Ring outline color and number text color always match (doc 04 §4.3).
- Five color states: DEFAULT (100, 150, 255), ACTIVE (255, 140, 0), SETTLED (130, 150, 190), COMPLETE (80, 220, 120), ERROR (255, 120, 120).
- Font surface caching: pre-render text for all 5 states at init, select cached surface at draw time (doc 04 §3.5).
- Sprite identity: permanent unique ID, never changes (doc 12 §1.1 rule #1).
- The sprite does NOT own animation, color-state decisions, or slot mapping — those are Controller responsibilities.

### Exit criteria

- `uv run pytest tests/unit/test_sprite.py -v` all green
- `uv run pytest tests/unit/ -v` all green (cumulative, 76+ tests)
- `PYRIGHT_PYTHON_GLOBAL_NODE=false uv run pyright src/visualizer/views/sprite.py tests/unit/test_sprite.py` clean
- `uv run ruff check src/visualizer/views/sprite.py tests/unit/test_sprite.py` + format check clean
- Doc 12 §4.3 color fixed

---

## 2026-04-23 10:03 — Phase 5a closed: window.py (post-action)

### Worked on

Created `src/visualizer/views/window.py` (`load_preset`, `GridLayout`, `init_display`) and `tests/unit/test_window.py` (25 tests: desktop/tablet dimension assertions, all four panel rect coordinates, non-overlap and bounds invariants for both presets, min panel-width guard, unknown-preset ValueError).

### Results

- `uv run pytest tests/unit/test_window.py -v`: **25/25 PASSED** (first run)
- `uv run pytest tests/unit/ -v`: **75/75 PASSED** (cumulative)
- `PYRIGHT_PYTHON_GLOBAL_NODE=false uv run pyright src/visualizer/views/window.py tests/unit/test_window.py`: **0 errors** (1 pre-existing `pytest.approx` warning)
- `uv run ruff check` + `uv run ruff format --check`: **clean**

### Corrections

1. **`reportConstantRedefinition` on `@dataclass` with `field(init=False)`** — pyright strict treats the dataclass field declarations (e.g., `PADDING: int = field(init=False)`) as class-level constant definitions, then flags the `__post_init__` assignments as redefinitions. Switched from `@dataclass` to a plain class; `__init__` makes the first assignment (definition, not redefinition). Task allowed "dataclass or class" — plain class is the correct call here.
2. **RUF002/RUF003: ambiguous `×` character** — module docstring and test comments used `×` (U+00D7 MULTIPLICATION SIGN). Ruff flags it as visually ambiguous with `x`. Replaced with `x` throughout.
3. **`ruff format` reformatted `test_window.py`** — one long assertion line wrapped. No logic change.

### Decisions

- **Plain class over `@dataclass`** — avoids `reportConstantRedefinition` without suppression comments and is more readable for this pattern (computed layout is not a typical dataclass).
- **`panel_height == 297`, not 296** — doc 04 §2.6 reference table shows 296 but the formula `(651 - 57) // 2 = 297` is authoritative. Test asserts the computed value; comment documents the discrepancy.

### Open questions

- None.

### Next

Phase 5b: `sprite.py` (NumberSprite — circular ring, float coords, easing integration).

---

## 2026-04-23 09:58 — Phase 5a start: window.py plan (pre-action)

### Model / session

Sonnet 4.6. First View layer brick — pure layout math, no rendering logic.

### Plan

Create `src/visualizer/views/window.py` (display init, 2x2 grid math, config.