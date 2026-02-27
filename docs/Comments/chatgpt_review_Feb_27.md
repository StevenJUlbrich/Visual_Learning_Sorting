**Findings (High → Low)**

**High**
- Conflicting UI behavior in reference Brick docs vs locked specs. `docs/reference/Brick_4_The_Panel.md` shows a single `ARRAY_HIGHLIGHT` color, increments steps on every draw call, omits the message line, and does not render comparisons/writes. This conflicts with per‑algorithm accents, message line visibility, and step counter semantics in `docs/04_UI_SPEC.md` and `docs/03_DATA_CONTRACTS.md`.  
  Files: `docs/reference/Brick_4_The_Panel.md`, `docs/04_UI_SPEC.md`, `docs/03_DATA_CONTRACTS.md`
- Grid/window layout conflicts with locked UI spec. `docs/reference/Brick_4_The_Grid_Manager.md` sets window title to “Sorting Algorithm Visualizer” and has no control‑bar reservation; the spec requires `"Learn Visual - Expand Knowledge"` and a fixed 48px control bar with grid height computed above it.  
  Files: `docs/reference/Brick_4_The_Grid_Manager.md`, `docs/04_UI_SPEC.md`
- Controller behavior and controls differ from locked behavior. `docs/reference/Brick_5_The_Controller.md` omits Step/Restart controls, uses 1/2/3 keys for speed (no cycle), and has no on‑screen controls. This conflicts with global Step/Restart, speed cycle, keyboard bindings, and clickable controls in `docs/06_BEHAVIOR_SPEC.md` and `docs/DECISIONS.md`.  
  Files: `docs/reference/Brick_5_The_Controller.md`, `docs/06_BEHAVIOR_SPEC.md`, `docs/DECISIONS.md`
- Algorithm/base contracts in reference Bricks omit required fields. `docs/reference/brick_2.md` lacks `complexity`, `comparisons`, and `writes` on `BaseSortAlgorithm`, and the algorithm implementations in `docs/reference/Brick_3_*.md` do not maintain comparisons/writes counters. This conflicts with `docs/03_DATA_CONTRACTS.md` and decision D‑023/D‑028 in `docs/DECISIONS.md`.  
  Files: `docs/reference/brick_2.md`, `docs/reference/Brick_3_bubble_sort.md`, `docs/03_DATA_CONTRACTS.md`, `docs/DECISIONS.md`

**Medium**
- Non‑project legacy doc lives in the main docs set. `docs/reference/bucket_sort_visualizer_design_v3.md` is for a different product (Bucket Sort Visualizer) and contains setup, structure, and feature details that directly conflict with this project’s locked scope.  
  File: `docs/reference/bucket_sort_visualizer_design_v3.md`
- Stale review document includes outdated conclusions. `docs/Comments/review_1_claude.md` claims undecided items and missing keyboard bindings that are already locked in `docs/DECISIONS.md` and `docs/06_BEHAVIOR_SPEC.md`, which can mislead downstream agents.  
  Files: `docs/Comments/review_1_claude.md`, `docs/DECISIONS.md`, `docs/06_BEHAVIOR_SPEC.md`

**Low**
- Planning doc still lists open questions that are now resolved, but it isn’t clearly marked as historical. This can confuse implementers about what is still undecided.  
  Files: `docs/Sorting_Algorithm_Visualizer_Planning.md`, `docs/DECISIONS.md`

**Assessment**
The core spec set (`docs/01_PRD.md` through `docs/10_CI.md` plus `docs/DECISIONS.md`) is strong and sufficiently detailed to generate a coding solution. The biggest risk is ambiguity from non‑canonical reference docs that include conflicting code and behavior. Without an explicit “authority map,” a builder could easily drift.

**Residual Risks / Gaps**
- No explicit “canonical vs reference” index to prevent drift when consuming docs.
- UI control bar layout details (button positions/text) are not fully specified, which can lead to inconsistent UI implementations.

**Suggested Next Steps**
1. Create a `docs/SPEC_INDEX.md` that explicitly lists canonical docs (01‑10 + DECISIONS) and marks all Brick/reference/planning files as non‑canonical.  
2. Move non‑project docs (`docs/reference/bucket_sort_visualizer_design_v3.md`) into `docs/Archive/` or annotate as legacy.  
3. Add a short “Status: historical” banner to `docs/Sorting_Algorithm_Visualizer_Planning.md` and `docs/Comments/review_1_claude.md` to prevent confusion.