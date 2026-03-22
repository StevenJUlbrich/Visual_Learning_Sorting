# Session — Animation Agent Strategy (2026-03-22)

## How We Got Here

### The Review Chain (2026-03-21)

A three-stage review chain identified **nine agent traps** (A–I) in the specifications — places where an implementer following the specs literally would produce incorrect visual behavior. The session summary (`2026-03-21-session-summary-spec-gaps.md`) proposed three options:

- **Option A:** Patch the specs directly (recommended by the summary)
- **Option B:** Create a consolidated `11_VIEW_CONTRACTS.md`
- **Option C:** Fold trap prompts into agent prompt docs

### The Root Cause Analysis (2026-03-22)

Before choosing an option, we investigated **why** the gaps exist despite the concept being straightforward (4 algorithms, same array, visual side-by-side comparison).

**Finding:** The specs were designed inside-out — algorithms and data contracts first (Bricks 1–3), basic rendering second (Brick 4), controller last (Brick 5). The View layer — the actual product for a visual learning tool — was never given a dedicated deep-design session. Result:

- 65% of DECISIONS.md entries are Model/Data concerns
- View-layer decisions are scattered, reactive, and late (March 11–17 review passes)
- 7 of 9 traps are pure View-layer concerns
- Animation choreography (what makes each algorithm *look* distinct) was treated as an implementation detail, not a specification

**Conclusion:** The specs thoroughly describe *what data the algorithms emit*. They are fragmented about *how the View renders that data into motion*. Patching the specs (Option A) would treat the symptom. The actual need is a **dedicated animation layer** with its own contracts and specialized agents.

---

## Decision: Animation Agent Architecture

**Rejected:** Options A, B, and C from the 2026-03-21 session summary.

**Chosen approach:** Per-algorithm animation contracts + specialized animation agents, built brick-by-brick with review gates.

### Principles

1. **Model/Controller specs stay as-is.** They are solid. No churn on proven work.
2. **Per-algorithm animation contracts** become the single source of truth for View-layer rendering. Each contract is a self-contained document covering one algorithm's complete visual behavior.
3. **Four specialized animation agents**, one per algorithm. Each agent reads its contract and produces correct rendering code. The contracts replace the need to stitch together information scattered across docs 03, 05, 06, and 10.
4. **Existing spec documents are updated to cross-reference** the new contracts — not gutted. Docs 03, 05, 06, and 10 still own their respective layers. Animation-specific rendering details are extracted into contracts; the original docs gain cross-references pointing to the authoritative contract.
5. **GitHub checkpoints** at each brick boundary.
6. **Brick-by-brick delivery** — each phase produces reviewable, understandable output before the next begins.
7. **Trap traceability** — every existing trap (A–I) maps to a specific contract section. No trap is lost or unaddressed.
8. **Skills assessment** — identify what Claude Code skills are needed for validation, review, and generation. Build only what's necessary.

---

## Trap Traceability Matrix

Every contract must resolve its mapped traps. This table is the accountability ledger.

| Trap | Name | Source | Severity | Target Contract | Status |
|------|------|--------|----------|-----------------|--------|
| A | Sprite Identity | Gemini review | High | All (shared concern) | Open |
| B | Independent Timing | Gemini review | High | All (shared concern) | Open |
| C | Heap Tree Geometry | Gemini review | High | Heap Sort Contract | Open |
| D | T3→T1→T2 Tick Sequence | Gemini review | High | Heap Sort Contract | Open |
| E | Bubble Sort 3-Phase Lift | Claude review | High | Bubble Sort Contract | Open |
| F | Selection Sort Triple Pointer | Claude review | High | Selection Sort Contract | Open |
| G | Sift-Down Cadence Flag | Claude review | High | Heap Sort Contract | Open |
| H | T3 Variant Rendering | Claude review | High | Heap Sort Contract | Open |
| I | Insertion Sort Cross-Tick Key Elevation | Claude review | High | Insertion Sort Contract | Open |

**Shared concerns (Traps A & B):** Sprite identity and independent timing affect all four algorithms. These will be addressed in a shared **Animation Foundation** document that each per-algorithm contract imports. This prevents duplication while keeping the shared rules explicit.

---

## Proposed Brick Plan

### Brick 6 — Animation Foundation

**Scope:** The shared rendering framework that all four algorithm contracts depend on.

**Delivers:**
- Sprite identity contract (resolves Trap A)
- Timing model and frame independence contract (resolves Trap B)
- Easing curve library (extract from `10_ANIMATION_SPEC.md`)
- Z-ordering rules
- Cross-tick state model (defines when and how View state persists across tick boundaries)
- Contract format template (the table/state-machine structure all per-algorithm contracts will use)

**Validates against:** Traps A, B

**Output:** `docs/12_ANIMATION_FOUNDATION.md` + contract format template

---

### Brick 7 — Bubble Sort Animation Contract

**Scope:** Complete visual behavior contract for Bubble Sort.

**Delivers:**
- Compare-Lift Contract: 3-phase timing table with exact boundaries (resolves Trap E)
- Swap choreography state machine
- Pass boundary visual behavior
- Arrow/pointer lifecycle
- Worked example with the canonical `[7, 6, 5, 4, 3, 2, 1]` array

**Validates against:** Trap E + Traps A, B (via foundation)

**Output:** `docs/contracts/BUBBLE_SORT_ANIMATION.md`

---

### Brick 8 — Selection Sort Animation Contract

**Scope:** Complete visual behavior contract for Selection Sort.

**Delivers:**
- Pointer Lifecycle table: i_ptr, j_ptr, min_ptr visibility/position per tick type (resolves Trap F)
- Coalescing rule as explicit table row
- Scan-phase highlight behavior
- Arc swap choreography
- Worked example

**Validates against:** Trap F + Traps A, B (via foundation)

**Output:** `docs/contracts/SELECTION_SORT_ANIMATION.md`

---

### Brick 9 — Insertion Sort Animation Contract

**Scope:** Complete visual behavior contract for Insertion Sort.

**Delivers:**
- Cross-Tick State Persistence table: what state survives tick boundaries, what resets (resolves Trap I)
- Key elevation lifecycle (lift, hold across shifts, diagonal drop)
- Gap slot tracking
- KEY label visibility rules
- Worked example

**Validates against:** Trap I + Traps A, B (via foundation)

**Output:** `docs/contracts/INSERTION_SORT_ANIMATION.md`

---

### Brick 10 — Heap Sort Animation Contract

**Scope:** Complete visual behavior contract for Heap Sort. Highest complexity — three traps.

**Delivers:**
- Tree geometry contract with worked pixel coordinates for default array (resolves Trap C)
- T3→T1→T2 tick sequence table (resolves Trap D)
- T3 Rendering Branch: detection heuristic + side-by-side sweep vs. snap-on table (resolves Trap H)
- Cadence flag lifecycle: set/reset triggers, duration table, Phase 1 exclusion (resolves Trap G)
- Phase 1 (Build) and Phase 2 (Extraction) state machines
- Worked example

**Validates against:** Traps C, D, G, H + Traps A, B (via foundation)

**Output:** `docs/contracts/HEAP_SORT_ANIMATION.md`

---

### Brick 11 — Spec Cross-References & Agent Definitions

**Scope:** Wire the new contracts back into the existing spec ecosystem and define the four animation agents.

**Delivers:**
- Cross-reference updates to docs 03, 05, 06, 10 (pointers to contracts, not content deletion)
- Four agent prompt definitions (one per algorithm) in `docs/AGENT_PROMPTS/`
- Phased agent workflow document
- Skills assessment: which Claude Code skills are needed for contract validation, implementation review, and scaffolding
- Trap traceability matrix — all statuses updated to Resolved
- DECISIONS.md updates for new locked decisions

**Output:** Updated spec docs + `docs/AGENT_PROMPTS/ANIMATION_*.md` + skills recommendations

---

### Brick 12 — GitHub Checkpoint & Transition Summary

**Scope:** Package everything for the repository and future sessions.

**Delivers:**
- PR with all new documents and cross-reference updates
- Updated AI_CONTEXT_HANDOFF for the next implementation session
- Session summary document
- Memory updates

---

## Skills Assessment (Preliminary)

| Skill Need | Purpose | Priority | Notes |
|------------|---------|----------|-------|
| Contract Validator | Check that a contract covers all mapped traps | High | Could be a review checklist or automated |
| Implementation Reviewer | Compare rendered output against contract tables | Medium | Useful during coding phase |
| Contract Scaffolder | Generate animation code skeleton from contract tables | Medium | Speeds up Brick 13+ (actual coding) |
| Test Generator | Produce acceptance tests from contract state machines | Medium | Feeds into `07_ACCEPTANCE_TESTS.md` |

Skills will be assessed fully in Brick 11 once the contracts exist and the actual requirements are concrete.

---

## What This Session Decided

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | Rejected spec patching (Option A) | Treats symptom, not cause |
| 2 | Animation agents, not general-purpose | The complexity is domain-specific |
| 3 | Per-algorithm contracts, not one monolith | Testable in isolation, focused prompts |
| 4 | Shared Animation Foundation | Traps A & B are cross-cutting; avoid duplication |
| 5 | Brick-by-brick with review gates | Matches project's proven pattern |
| 6 | Trap traceability is mandatory | No trap gets lost or silently ignored |
| 7 | Existing specs get cross-references, not surgery | Preserve proven work, add pointers |
| 8 | 4 algorithms: Bubble, Selection, Insertion, Heap | Merge Sort removed. Heap Sort's tree view animation adds visual complexity worth the investment. Archived Brick 3 Merge Sort is historical only. |

---

## Files Referenced

| File | Role |
|------|------|
| `2026-03-21-session-summary-spec-gaps.md` | Prior session: gap analysis and 3 options |
| `2026-03-21_review_gemini.md` | Gemini review: traps A–D |
| `2026-03-21_review_claude_additional_traps.md` | Claude review: traps E–I |
| `2026-03-21-gemini-recommendations.md` | Gemini agent prompts (partial) |
| `2026-03-21-claude-supplementary-prompts.md` | Claude supplementary prompts E–I |
| **This document** | Animation agent strategy and brick plan |

---

## Next Step

**Brick 6 — Animation Foundation.** User reviews this document first, then we begin.
