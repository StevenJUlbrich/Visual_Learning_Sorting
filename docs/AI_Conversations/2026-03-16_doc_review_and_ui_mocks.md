# Conversation: Doc Review & UI Mock Generation

**Date:** 2026-03-16
**Tool:** Claude Code (Opus 4.6)
**Status:** Complete

## Request

1. Review all markdown spec files in `docs/` (base level)
2. Create 3–4 mock UI PNG files in `docs/screen_Ideas/`
3. Cross-reference `docs/Reference/` images and behavior markdowns
4. Goal: visual representation before code generation begins

## Documents Reviewed

All 11 spec files (01_PRD through 11_CI), DECISIONS.md, and all 4 reference write-ups (Bubble, Selection, Insertion, Heap Sort video references) with their associated image sets.

## Doc Review Findings

### Discrepancies Between Archived Mocks and Current Specs

The 3 existing mocks in `docs/Archive/` are outdated and do not reflect the current spec state:

| Issue | Archived Mock | Current Spec |
|-------|--------------|--------------|
| Algorithm set | Merge Sort (bottom-right) | **Heap Sort** (D-003) |
| Initial array | `[7, 6, 5, 4, 3, 2, 1]` | **`[4, 7, 2, 6, 1, 5, 3]`** (D-006) |
| Speed controls | "Speed 1x" button + "S Speed" shortcut | **Removed** from v1 scope |
| Metrics layout | Beside title (same line) | **Below title** (D-047, D-062) |
| Bubble Sort assets | None shown | **ComparisonPointer** (green arrow), **LimitLine** (dashed), **HUD counters** required |
| Heap Sort visuals | N/A (was Merge) | Orange accent, settled/extracted steel-blue, boundary sweep |
| Insertion Sort visuals | Generic | Key-lift to compare lane, sequential shift, diagonal drop |
| Window title | Not shown | **"Learn Visual - Expand Knowledge"** (D-027) |

### Spec Consistency Notes

- All 11 docs are internally consistent. The DECISIONS.md (D-001 through D-066) accurately tracks every locked decision across the spec set.
- Cross-references between docs (e.g., 05_ALGORITHMS_VIS_SPEC referencing 10_ANIMATION_SPEC sections) are valid and accurate.
- Counter values in 03_DATA_CONTRACTS, 07_ACCEPTANCE_TESTS, and 08_TEST_PLAN are aligned (Bubble: Comps=20/Writes=26, Selection: 21/10, Insertion: 17/19, Heap: 20/30).
- The 4 reference video write-ups correctly describe behaviors that have been formalized into the spec docs. No contradictions found.

### Spec Strengths

- Extremely thorough tick-level behavior specification for all 4 algorithms
- WCAG AAA contrast compliance documented with exact ratios
- Clear separation of concerns (MVC architecture, model/view/controller boundaries)
- Worked examples for Insertion Sort passes provide unambiguous implementation guidance
- Heap Sort T3 tick variants (boundary vs logical tree) clearly distinguished by contiguity rule

### Areas for Awareness (Not Issues)

- The spec set is dense (~40 pages total). An implementer should use DECISIONS.md as their primary navigation index.
- Bubble Sort has the most complex choreography (compare-lift + swap-lift + arrow + limit line + HUD) despite being the simplest algorithm.
- AT-20 (Selection Sort sorted region stability) extends settled color to Selection Sort, which was previously Heap-only per D-063. The acceptance test effectively amends D-063's scope.

## Mock UI Files Created

### `docs/screen_Ideas/01_startup_paused.png`
**State:** Initial startup, paused
- 2x2 grid: Bubble (cyan), Selection (red), Insertion (magenta), Heap (orange)
- Array `[4, 7, 2, 6, 1, 5, 3]` in default blue across all panels
- All counters at zero, "Ready" messages
- Control bar: Play/Step/Restart, PAUSED indicator, keyboard shortcuts
- Window title: "Learn Visual - Expand Knowledge"

### `docs/screen_Ideas/02_mid_race_running.png`
**State:** Mid-race, all algorithms running with characteristic behaviors
- **Bubble:** Compare-lift on indices 2-3 (cyan), green arrow below, dashed LimitLine, HUD counters
- **Selection:** Scan phase with red highlights on min_idx and j, settled steel-blue on sorted left region
- **Insertion:** Key "6" lifted above array in magenta, gap at shifted position, value 7 highlighted
- **Heap:** Orange boundary emphasis on indices 0-4 (active heap), steel-blue on indices 5-6 (sorted)
- Control bar: RUNNING indicator, Pause button active, Step grayed out

### `docs/screen_Ideas/03_bubble_sort_detail.png`
**State:** Close-up (800x500) of Bubble Sort panel showing all unique assets
- Compare-lift: indices 3-4 elevated above baseline in cyan
- ComparisonPointer: green triangle below baseline at index 3 with "j" label
- LimitLine: vertical dashed line between indices 5-6 with "limit" label
- Annotated: "Compare Lane" and "Baseline" reference lines, "Active comparison position" callout
- HUD: Comparisons and Exchanges counters in bottom-left

### `docs/screen_Ideas/04_completion_state.png`
**State:** Race complete, all algorithms finished
- All arrays show `[1, 2, 3, 4, 5, 6, 7]` in completion green (80, 220, 120)
- Race results visible via elapsed times: Selection (3.95s) < Heap (4.80s) < Bubble (5.35s) < Insertion (5.60s)
- Counter values match spec expectations
- Control bar: COMPLETE indicator, Play/Step grayed, Restart active

## Mock Review Feedback (Round 1)

Initial mocks rejected — numbers were rendered as bare text, not as game sprites. The following visual design decisions were clarified:

### Sprite Node Style (Confirmed)

| Question | Answer | Spec Cross-Check |
|----------|--------|-----------------|
| **Circle style** | Outlined ring with number inside. Never a square. | Aligns with all 4 reference videos (circular nodes). Selection ref specifically shows "circular node with a green border on a gray fill." |
| **Circle size** | Game piece, but subtle (~50-60px diameter within 78px slots) | Fits within spec's `slot_width` at landscape resolution. |
| **Circle fill** | Matches panel background (45, 45, 53) — ring outline carries the color signal | Consistent with Selection ref "gray fill" inside ring. The outline/ring is the primary color indicator. |
| **Color states** | Follows Insertion Sort reference: accent-colored ring for active, green for sorted, blue (default) for unsorted | Maps to spec's per-algorithm accent colors (cyan/red/magenta/orange) rather than a universal orange. |

### Resolved: Universal Orange Active Color

**Decision:** Override per-algorithm accent colors (D-017, D-043) with a **universal orange `(255, 140, 0)`** for all active/highlighted sprite states across all 4 algorithms. This matches the reference video style where orange = "this element is currently active."

**Impact on existing spec decisions:**
- D-017 (per-panel accent colors): **Overridden** — active highlights are now orange for all panels
- D-043 (insertion magenta, selection red corrections): **Superseded** — no longer needed for sprite highlights
- D-054 (orange reserved for Heap Sort): **Superseded** — orange is now universal

**Resolved:** Per-algorithm colored title dots are **removed**. They are a distraction and possible confusion point. Algorithm identity comes from the panel title text and grid position alone.

## Decisions Made

- Archived mocks should remain in `docs/Archive/` as historical record; new mocks in `docs/screen_Ideas/` are the current visual reference.
- AI conversation tracking folder created at `docs/AI_Conversations/` with dated markdown files.
- **Sprite nodes must be circles (outlined ring), never squares or bare text.** Fill matches panel background; the ring outline carries the color state.
- Mocks to be regenerated with corrected sprite style.
- Mocks regenerated (Round 2) with circular outlined rings, universal orange, no title dots.

## Selection Sort Detail Mock (Round 3)

### Request
Create a detailed Selection Sort mock (like the Bubble Sort detail `03_bubble_sort_detail.png`) showing all unique Selection Sort visual elements.

### Reference Image Analysis (docs/Reference/selection_sort_images/)
Key behaviors observed from reference frames (ignoring square shapes and code sections):

1. **Three pointer assets:** `i` (downward arrow ABOVE baseline), `j` (upward arrow BELOW baseline), `min` (upward arrow BELOW baseline)
2. **Coalescing behavior:** When `j` discovers new minimum, `j` and `min` merge at same index — only `min` label shown (frames 009, 010)
3. **Sorted region grows left-to-right:** After each swap, the placed element transitions to bright green fill (frames 019, 040, 050)
4. **Arc swap motion:** Left element (at `i`) arcs UPWARD, right element (at `min_idx`) arcs DOWNWARD (frame 017, 035)
5. **`i` pointer hides during swap** and reappears after landing
6. **Scan is the dominant visual phase** — many comparisons, sparse swaps

### Resolved: Pointer Arrows + Color Highlights
**Decision:** Use BOTH `i`/`j`/`min` labeled pointer arrows (from reference video) AND orange/green/steel-blue color highlights. This provides maximum teaching signal — the arrows show structural positions while the colors show state. This overrides D-065/D-066 which specified highlight-only approach.

**Impact on spec:** Selection Sort now requires three pointer assets (like Bubble Sort's ComparisonPointer) in addition to ring color changes. This is a visual enhancement, not a simplification.

### Mock Generated

`docs/screen_Ideas/05_selection_sort_detail.png` (800x500) — Selection Sort detail close-up showing:
- 6 circular ring sprites: [1, 2, 5, 3, 6, 4] mid-scan during pass i=2
- Green rings (indices 0-1): sorted region with "Sorted region" bracket
- Orange rings (indices 3-4): active comparison — min candidate and scan cursor
- Blue rings (indices 2, 5): unsorted elements
- `i` pointer (white, above row): marks sorted boundary at index 2
- `min` pointer (orange, below row): tracks current minimum at index 3
- `j` pointer (orange, below row): scan cursor at index 4
- Dotted boundary line between sorted/unsorted regions
- Annotation: "min tracks smallest found so far"
- HUD: Comparisons: 9, Swaps: 2

## Files Created / Modified

- `docs/AI_Conversations/` — new folder for tracking AI conversation requests and outcomes
- `docs/AI_Conversations/2026-03-16_doc_review_and_ui_mocks.md` — this file
- `docs/screen_Ideas/01_startup_paused.png` — startup/paused state mock
- `docs/screen_Ideas/02_mid_race_running.png` — mid-race running state mock
- `docs/screen_Ideas/03_bubble_sort_detail.png` — Bubble Sort detail mock with annotations
- `docs/screen_Ideas/04_completion_state.png` — completion/race-finished state mock
- `docs/screen_Ideas/05_selection_sort_detail.png` — Selection Sort detail mock with pointer arrows

## Spec Documents Updated

All changes propagated from conversation decisions to spec files on 2026-03-16:

| File | Changes Applied |
|------|----------------|
| `docs/04_UI_SPEC.md` | Circular ring sprites (Section 4.3), universal orange (Section 5.2), removed title dots (Section 4.1), updated Heap accent scope |
| `docs/05_ALGORITHMS_VIS_SPEC.md` | Selection Sort pointer assets (Section 4.2), universal orange highlights (Section 5, 8) |
| `docs/06_BEHAVIOR_SPEC.md` | Bubble Sort active color green → orange throughout timing contract |
| `docs/10_ANIMATION_SPEC.md` | Universal orange in compare lane (Section 3.5), Bubble Sort active color (Section 5.1) |
| `docs/DECISIONS.md` | D-017/D-043/D-054/D-065/D-066 marked revised; added D-067 (universal orange), D-068 (Selection pointers), D-069 (circular rings), D-070 (no title dots) |
| `docs/Reference/Selection_Sort_Video_Reference.md` | Adoption note: pointer arrows adopted (D-068) |
| `docs/Reference/Bubble_Sort_Video_Reference_Write-Up.md` | Adoption note: choreography adopted, active color is orange not green |
| `docs/Reference/Insertion_Sort_Video_Reference.md` | Adoption note: key-lift adopted, orange matches reference |
| `docs/Reference/Heap_Sort_Video_Reference.md` | Adoption note: two-phase distinction adopted, universal orange |
