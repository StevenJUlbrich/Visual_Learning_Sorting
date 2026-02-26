# 01 PRD - Sorting Algorithm Visualizer

## Product Summary
An educational desktop visualizer that shows four sorting algorithms running side-by-side on the same numbers, one global tick at a time, so learners can see operational differences directly.

## What It Is
- A Python + Pygame portfolio project focused on algorithm mechanics.
- A fixed 4-panel comparison for Bubble Sort, Selection Sort, Insertion Sort, and Merge Sort.
- A number-based visualization (not bars) with per-panel step counting.
- A deterministic demo: same starting array for all algorithms on each restart.

## What It Is Not
- Not a general sorting playground (no custom arrays in v1).
- Not a benchmarking tool.
- Not an audio visualizer.
- Not a video exporter.

## Target User Experience
- User opens app and sees a clean 2x2 grid with all algorithms ready.
- App starts paused so user can inspect initial state.
- User can run/pause globally, step one global tick at a time, change speed, and restart.
- Faster algorithms finish early, display completion state, and remain idle while others continue.

## Core User Stories
- As a learner, I want to see all four algorithms process the same data so I can compare them fairly.
- As a learner, I want to pause and step through operations to understand each move.
- As a learner, I want completion and error states to be explicit and readable.
- As a maintainer, I want strict contracts so adding a new algorithm does not break UI/runtime behavior.

## Scope
### In Scope (v1)
- 4 fixed algorithms: Bubble, Selection, Insertion, Merge.
- Global tick model via generator outputs.
- On-screen controls + keyboard shortcuts.
- Two supported resolutions via config flag: 1280x720 and 720x996.

### Out of Scope (v1)
- Custom arrays.
- Algorithm picker UI.
- >4 simultaneous panels.
- Sound effects.
- Replay/history timeline.

## Success Criteria
- Every algorithm reaches a correct sorted final array.
- Global controls are deterministic and consistent across all panels.
- Contract-driven architecture is strong enough for agentic implementation without ambiguity.
- Acceptance tests in `docs/06_ACCEPTANCE_TESTS.md` pass.

## References
- Decision authority: `docs/DECISIONS.md`
- Architecture: `docs/02_ARCHITECTURE.md`
- Contracts: `docs/03_DATA_CONTRACTS.md`
