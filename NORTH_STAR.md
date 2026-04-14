# NORTH STAR — Visual Learning Sorting

**Purpose:** Executive reference for the project blueprint. One page. The authoritative *what* and *why*; the authoritative *how* lives in `docs/design_docs/`.

**Status:** Pre-code blueprint phase. Specification is being completed and simulated before implementation begins.

---

## What Is Being Built

A **pedagogical sorting algorithm visualizer** in Python/Pygame. Four classical algorithms — Bubble, Selection, Insertion, Heap — execute simultaneously in a 2×2 panel grid, driven by per-algorithm operation queues with weighted timing so the race reflects algorithmic cost rather than frame parity. Each algorithm yields a typed sequence of `SortResult` ticks; the view layer renders each tick class with a distinct, contract-bound animation (compare-lift for Bubble, triple-pointer scan for Selection, key-lift-and-shift for Insertion, binary-tree sift-down for Heap).

## Why It Is Being Built

Two objectives, both first-class:

1. **Pedagogical artifact.** Learners see *why* Heap Sort dominates O(n²) algorithms by watching the tree collapse in real time next to Bubble Sort's patient pairwise comparisons. Identity-stable sprites make the mechanism — not just the outcome — legible.

2. **Engineering journal.** The blueprint-first methodology itself is the subject. Every decision, its rationale, and its simulation trace is recorded so the project can be taught — including in video form — as a worked example of disciplined spec-first development in an era that rewards shortcuts.

## Definition of Done (v1)

- All four algorithms sort `[4, 7, 2, 6, 1, 5, 3]` correctly, with counter accuracy matching the table in `CLAUDE.md` exactly (Bubble 20/26, Selection 21/10, Insertion 17/19, Heap 20/30/35).
- Tick sequences pass TC-A6 through TC-A19 in `docs/design_docs/08_TEST_PLAN.md`.
- Acceptance tests AT-01 through AT-27 in `docs/design_docs/07_ACCEPTANCE_TESTS.md` pass on real hardware at the Desktop preset (1280×720).
- Headless CI (`SDL_VIDEODRIVER=dummy`) runs the full pytest suite green on GitHub Actions.
- Animation contracts in `docs/contracts/*.md` are observably honored by the running app at the Tablet preset as well.
- `DEVLOG.md` is continuous — every work session recorded.

## Hard Constraints (non-negotiable for v1)

- Python 3.13+, UV, Pygame ≥ 2.5, Ubuntu WSL host.
- Strict MVC under `src/visualizer/` per D-002 and D-080.
- No exceptions from algorithm generators — domain errors yield a T0 failure tick and return (D-020).
- Sprite identity by unique ID, never by value (duplicate values prohibit value-matching).
- All specs in `docs/design_docs/DECISIONS.md` are locked unless explicitly renegotiated and re-entered as a new D-NNN.

## Explicit Non-Goals (v1)

User-provided arrays (F-001), algorithm picker (F-002), more than four simultaneous algorithms (F-003), audio cues (F-004), dynamic playback speed (F-005). These are deferred by decision, not by oversight.

## Authoritative References

- Canonical decisions: `docs/design_docs/DECISIONS.md` (D-001 through D-080)
- Architecture: `docs/design_docs/02_ARCHITECTURE.md`
- Type surface: `docs/design_docs/03_DATA_CONTRACTS.md`
- Algorithm generator pseudocode: `docs/design_docs/00_PSEUDOCODE.md`
- Build sequence: `docs/design_docs/13_IMPLEMENTATION_ORDER.md`
- Decision trail and session narrative: `DEVLOG.md`

## Current Phase

Phase 0 closes when the three TTF fonts are placed in `assets/fonts/` (run `scripts/fetch_fonts.sh` on the host). All other Phase 0 gaps are closed. Phase 1 (`contracts.py`) is unblocked pending that single action.
