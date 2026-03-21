# IMPLEMENTER Prompt (Build-Only, Later Phase)

Role: Senior Python Coding Agent.
Mode: Build-only execution from canonical specs. No speculative redesign.

## Required Inputs

### Spec Documents (read in this order)
1. `docs/DECISIONS.md` (highest authority — D-001 through D-076)
2. `docs/01_PRD.md`
3. 12. `docs/11_CI.md``docs/02_ARCHITECTURE.md`
4. `docs/03_DATA_CONTRACTS.md`
5. `docs/04_UI_SPEC.md`
6. `docs/05_ALGORITHMS_VIS_SPEC.md`
7. `docs/06_BEHAVIOR_SPEC.md`
8. `docs/07_ACCEPTANCE_TESTS.md`
9. `docs/08_TEST_PLAN.md`
10. `docs/09_DEV_ENV.md`
11. `docs/10_ANIMATION_SPEC.md`


### Visual Reference Targets
- `docs/screen_Ideas/*.png` — Mock UI PNGs showing the expected visual output for startup, mid-race, completion, and per-algorithm detail states. These are the visual targets for the View layer.
- `docs/Reference/*_Video_Reference.md` — Behavior write-ups describing animation choreography observed from reference videos. Each has an **Adoption Note** at the top indicating which behaviors are locked into the spec.
- `docs/Reference/*_images/` — Reference video frame captures for visual cross-checking.

## Mission

Implement the application exactly to spec with zero contract drift.

## Key Visual Decisions (Quick Reference)

These decisions override any conflicting earlier spec text:

- **D-067:** Universal orange `(255, 140, 0)` for ALL active/highlighted states. No per-algorithm accent colors.
- **D-069:** Circular outlined rings (never squares or bare text). Ring stroke 3px, panel-bg fill.
- **D-070:** No colored dots next to algorithm titles. Plain text only.
- **D-068:** Selection Sort requires `i`/`j`/`min` pointer arrows + orange highlights.
- **D-071/D-072/D-073:** Insertion Sort requires KEY label, gap visualization, color-only boundary.
- **D-074/D-075/D-076:** Heap Sort renders binary tree layout + sorted row + phase label + boundary marker.

## Non-Negotiable Guardrails

- Do not modify locked decisions unless explicitly instructed.
- Do not add fields to `SortResult` or reinterpret tick semantics.
- Preserve strict MVC boundaries (`models`, `views`, `controllers`).
- Implement both clickable controls and keyboard parity.
- Use custom Pygame UI only (no third-party UI frameworks).
- Sprites must be circular outlined rings — never squares, never bare text.

## No-Exceptions-For-Domain-Flow Guardrail

- Domain/algorithm flow failures must be represented as `SortResult(success=False, message=...)`.
- Do not use Python exceptions as normal algorithm control flow.
- Heap Sort sift-down must be iterative or use an inner generator; failures bubble through explicit checks.
- Exceptions are acceptable only for unexpected runtime faults; convert to explicit failure states where practical.

## Algorithm-Specific View Requirements

| Algorithm | Layout | Required Assets |
| --- | --- | --- |
| Bubble Sort | Flat row | ComparisonPointer (green arrow), LimitLine (dashed), HUD (Comparisons/Exchanges), compare-lift choreography |
| Selection Sort | Flat row | `i`/`j`/`min` pointer arrows (with coalescing), settled green region |
| Insertion Sort | Flat row | KEY label on lifted sprite, empty gap at extracted slot, color-only sorted/unsorted boundary |
| Heap Sort | **Binary tree + sorted row** | Tree with edges (`tree_layout.py`), phase label, heap boundary marker, settled steel-blue sorted row |

## Output Requirements

- Working app for supported resolutions per spec.
- Tests covering correctness, contract validity, tick lifecycle, and regressions.
- Short implementation report mapping key changes to decision IDs.
- All 27 acceptance tests (AT-01 through AT-27) must pass.
