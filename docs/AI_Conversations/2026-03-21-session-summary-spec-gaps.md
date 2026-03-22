# Session Summary — Spec Gap Analysis (2026-03-21)

## What Happened Today

Three-stage review chain examining whether the specifications are truly agent-ready:

1. **Gemini system design review** (`2026-03-21_review_gemini.md`) — Praised the spec architecture but identified four high-risk "agent traps" (A–D): Sprite Identity, Independent Timing, Heap Tree Geometry, and the T3→T1→T2 tick sequence.

2. **Claude supplementary trap review** (`2026-03-21_review_claude_additional_traps.md`) — Found five additional traps (E–I) of comparable severity: Bubble Sort 3-phase lift, Selection Sort triple pointer, Sift-down cadence flag, T3 variant rendering split, and Insertion Sort cross-tick key elevation.

3. **Gemini agent prompt recommendations** (`2026-03-21-gemini-recommendations.md`) — Proposed system prompts and a phased workflow to guard against traps A–D plus the Result Pattern rule. Claude review found it missed traps E–I entirely and that Phase 4 was under-specified.

4. **Claude supplementary prompts** (`2026-03-21-claude-supplementary-prompts.md`) — Drafted the missing CRITICAL RULE prompts for traps E–I, a Phase 3 addendum for the cadence flag, and split Phase 4 into five per-algorithm sub-phases with validation gates.

---

## The Core Problem

**If the specs require nine supplementary "trap" documents and special system prompts to produce a correct implementation, the specs themselves are insufficient.**

The trap documents are a symptom, not a solution. Each trap exists because the relevant spec either:

- **Buries critical behavior** inside prose that an agent (or human) can easily skim past,
- **Splits a single contract across multiple documents** without cross-references, forcing the implementer to mentally stitch them together, or
- **Omits the rendering contract entirely**, assuming the implementer will infer View behavior from Model-layer tick descriptions.

An agent that reads the specs cover-to-cover and follows them literally should produce a correct implementation. If it can't, the specs need to change — not the agent's prompt.

---

## Specific Spec Gaps by Trap

### Trap E — Bubble Sort Compare-Lift

**Gap:** The 3-phase timing split (ascent/hold/descent within 150ms) is described in `10_ANIMATION_SPEC.md` Section 5.1.1 and `05_ALGORITHMS_VIS_SPEC.md` Section 4.1, but neither document flags this as the distinguishing visual signature of Bubble Sort. The information reads as optional choreography detail, not as a mandatory rendering contract with locked phase boundaries.

**Spec fix needed:** Elevate the 3-phase split to a named contract (e.g., "Bubble Sort Compare-Lift Contract") with a summary table, explicit phase boundaries, and a note that flat-highlight rendering is a spec violation. Add a cross-reference from the algorithm spec to the animation spec and vice versa.

### Trap F — Selection Sort Triple Pointer

**Gap:** D-068 locks the decision for three pointer assets, and `05_ALGORITHMS_VIS_SPEC.md` Section 4.2 describes them. But the coalescing rule (`j == min_idx` → show only `min`) and the `i`-hides-during-swap behavior are buried in paragraph text. There is no consolidated pointer state machine or lifecycle table.

**Spec fix needed:** Add a "Selection Sort Pointer Lifecycle" table to the algorithm vis spec showing pointer visibility and position for each tick type (scan T1, swap T2, inter-pass reset). Include the coalescing rule as a row, not inline prose.

### Trap G — Sift-Down Cadence Flag

**Gap:** D-056 and `10_ANIMATION_SPEC.md` Section 5.4.2 define the reduced durations and flag lifecycle. But the Controller spec (`06_CONTROLLER_SPEC.md` or equivalent) does not mention the cadence flag at all. The flag is a Controller-layer mechanism described only in the Animation spec, creating a cross-document blind spot.

**Spec fix needed:** Add the cadence flag to the Controller spec as a named state variable with explicit set/reset triggers. Cross-reference the Animation spec for duration values. Add a note that Phase 1 sift-downs are excluded.

### Trap H — T3 Variant Rendering

**Gap:** `03_DATA_CONTRACTS.md` documents both T3 variants under OpType.RANGE but uses the same enum value for both. The View must branch on contiguity — but the detection heuristic and the two rendering behaviors (sweep vs. snap-on) are split between the data contracts doc and the animation spec. Neither document contains a consolidated branching table.

**Spec fix needed:** Add an explicit "T3 Rendering Branch" section to the animation spec (or the View spec) with: (a) the detection heuristic code, (b) a side-by-side table of the two rendering behaviors, (c) a note that a single-path implementation is a spec violation.

### Trap I — Insertion Sort Cross-Tick Key Elevation

**Gap:** D-039 and the animation spec describe the key staying elevated, but neither document explicitly states that the View must maintain **persistent state across tick boundaries**. The per-tick rendering model implied by the rest of the spec (receive tick → render → wait → next tick) naturally leads an implementer to reset state between ticks. The cross-tick persistence requirement is the exception, and exceptions must be called out loudly.

**Spec fix needed:** Add a "Cross-Tick View State" section that explicitly names which algorithms require persistent View state between ticks and what that state contains. For Insertion Sort: active key sprite_id, elevated y-position, KEY label visibility, gap slot index. Make clear this is a deviation from the default per-tick rendering model.

### Traps A–D (Gemini's findings)

These are better covered by the existing specs but still benefit from consolidation:

- **Trap A (Sprite Identity):** Spec is adequate but could add a "sprite tracking" anti-pattern callout.
- **Trap B (Timing):** Spec is adequate. The `dt` clamping and integer math rules are present.
- **Trap C (Heap Geometry):** Spec provides formulas. Could benefit from a worked example with actual pixel coordinates for the default `[7,6,5,4,3,2,1]` array.
- **Trap D (Tick Sequence):** Spec is adequate. The T3→T1→T2 sequence is explicit.

---

## What Needs to Happen Next

### Option A: Patch the Specs Directly

Go through each spec document and embed the missing contracts, lifecycle tables, and cross-references so that the trap documents become redundant. The goal: an agent reading only the numbered spec docs (01–10) produces a correct implementation without needing supplementary prompts.

**Scope:** Moderate. Mostly restructuring existing information, not writing new requirements. Estimated touchpoints:

| Spec Document | Changes Needed |
|---------------|----------------|
| `03_DATA_CONTRACTS.md` | Add T3 rendering branch table |
| `05_ALGORITHMS_VIS_SPEC.md` | Add Bubble Compare-Lift Contract, Selection Pointer Lifecycle table, Insertion Cross-Tick State section |
| `06_CONTROLLER_SPEC.md` (or equivalent) | Add cadence flag as named state variable |
| `10_ANIMATION_SPEC.md` | Add cross-references back to algorithm spec, elevate sub-phase tables to named contracts |

### Option B: Create a Consolidated "View Contracts" Spec

Instead of patching multiple docs, create a new `11_VIEW_CONTRACTS.md` that consolidates all algorithm-specific rendering behaviors, cross-tick state requirements, and branching logic in one place. The existing specs remain as-is; the new doc serves as the single source of truth for View-layer implementation.

**Trade-off:** Avoids churn on existing specs but adds another document to the stack and creates potential for specs to drift out of sync.

### Option C: Fold Trap Prompts into Agent Prompt Docs

Accept that the specs describe *what* the system does and the agent prompts describe *how to avoid mistakes building it*. Keep both. Update `docs/AGENT_PROMPTS/IMPLEMENTER.md` to include all nine trap prompts and the revised phased workflow.

**Trade-off:** Fastest to execute, but doesn't fix the root cause. Future spec readers (human or AI) who don't use the agent prompts will hit the same traps.

---

## Recommendation

**Option A is the right call.** The specs are the single source of truth. If they can't stand alone, they're incomplete. The trap documents and supplementary prompts should be treated as a gap analysis that feeds back into spec revisions — not as permanent companions to the specs.

The agent prompt docs (`AGENT_PROMPTS/`) should contain workflow guidance (phased build order, validation gates) but should not need to duplicate or clarify spec content. If the IMPLEMENTER prompt needs to say "don't forget X," that's a signal that X isn't clear enough in the spec.

Once the specs are patched, the trap documents become historical artifacts — useful as a record of the review process but not required for implementation.

---

## Files Produced Today

| File | Purpose |
|------|---------|
| `2026-03-21_review_gemini.md` | Gemini system design review (traps A–D) |
| `2026-03-21_review_claude_additional_traps.md` | Claude supplementary review (traps E–I) |
| `2026-03-21-gemini-recommendations.md` | Gemini agent prompts and phased workflow |
| `2026-03-21-claude-supplementary-prompts.md` | Claude supplementary prompts (E–I) and revised Phase 4 |
| `2026-03-21-session-summary-spec-gaps.md` | **This document** — session summary and spec gap analysis |
