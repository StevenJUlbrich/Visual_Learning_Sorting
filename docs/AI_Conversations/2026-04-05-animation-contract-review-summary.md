# Animation Contract Review Summary (2026-04-05)

## Scope

This document summarizes review work performed against the animation contract documents and the design-document set in `docs/design_docs`.

Reviewed contracts:

- `docs/contracts/HEAP_SORT_ANIMATION.md`
- `docs/contracts/BUBBLE_SORT_ANIMATION.md`
- `docs/contracts/INSERTION_SORT_ANIMATION.md`

Review goal:

- Determine whether each contract's knowledge **supports**, **clarifies**, or **contradicts** the design docs.
- Identify design-doc inconsistencies exposed by the contract reviews.
- Confirm whether follow-up fixes removed the contradictions without creating new problems.

---

## Executive Summary

The reviewed animation contracts are now broadly aligned with the design docs after a series of targeted corrections.

### Final status by contract

- **Heap Sort:** Aligned after fixing the sift-down grammar, T3 payload constraints, and inaccurate references.
- **Bubble Sort:** Aligned after correcting stale arc-swap language and normalizing compare-lift timing references.
- **Insertion Sort:** Aligned after adding the terminating-comparison phase, fixing post-placement color wording, and disambiguating the insertion boundary language in the UI spec.

### Main pattern observed

Most issues were not root-level animation-contract problems. The contracts often captured the intended choreography correctly, while some design docs lagged behind or used broader wording that conflicted with the more specific animation specs.

### Outcome

At the end of the review sequence, the reviewed contracts and the related design docs are consistent on the issues examined here.

---

## Review Outcomes by Contract

## 1. Heap Sort Animation Contract

### Initial findings

The Heap Sort contract was mostly strong, but two substantive issues were identified:

1. **Sift-down grammar was too narrow.**
   The contract described the build-phase sequence as `T3 -> T1 -> T2`, while the design docs required a level to be:

   `T3 -> T1 [1 or 2] -> T2 [0 or 1]`

2. **T3 Logical Tree Highlight payload was overconstrained.**
   The contract implied a strict three-index payload `(parent, left_child, right_child)`, while the data contract explicitly allows `(parent, left_child)` when only one child exists.

### Additional gaps found during review

The contract initially omitted or underemphasized several required UI details that were already locked in the design docs:

- active orange edge rendering during logical-tree highlights
- sorted-row placeholder outlines for active heap slots
- heap boundary marker behavior

These were classified as missing details rather than deep conceptual contradictions because the contract already declared dependency on the UI and data specs.

### Fixes confirmed

The following corrections were later confirmed:

- sift-down grammar updated to the correct `T3 -> T1 [1 or 2] -> T2 [0 or 1]` form
- payload wording updated to allow the single-child case and to preserve the parent-first invariant
- missing Heap UI assets added to the contract
- bad cross-references corrected to point at the proper sections in the design docs

### Final assessment

**Status:** Aligned.

The Heap Sort contract now supports and clarifies the design docs without introducing new contradictions.

---

## 2. Bubble Sort Animation Contract

### Initial findings

The Bubble Sort contract was already close to the intended choreography and correctly emphasized Bubble Sort's defining motion grammar:

- compare-lift
- lifted horizontal exchange
- lifted settle

The main contradictions uncovered were actually in the design docs around it.

### Contradictions exposed by review

1. **Swap path conflict.**
   The Bubble contract correctly defined Bubble swaps as a **linear horizontal slide while lifted**, but some design docs still described Bubble swaps as arc-based.

2. **Timing mismatch.**
   The contract used the frame-level timing split aligned to the animation spec:

   - `0-67ms`
   - `67-100ms`
   - `100-150ms`

   Some supporting design docs still used an older rounded split:

   - `0-60ms`
   - `60-100ms`
   - `100-150ms`

### Fixes confirmed

The following updates were later confirmed across the design docs:

- arc-swap wording replaced with the correct lifted horizontal slide wording
- the generic acceptance test was updated so Bubble was no longer grouped with arc-swap algorithms
- the compare-lift timing references were normalized to the `0-67 / 67-100 / 100-150` split
- the remaining `compare_lift_offset` inconsistency in `DECISIONS.md` was fixed to `50px`

### Final assessment

**Status:** Aligned.

The Bubble contract supported the intended design from the start. The later work mostly repaired stale or less precise design-doc language around it.

---

## 3. Insertion Sort Animation Contract

### Initial findings

The Insertion Sort contract strongly matched the intended motion model in several important areas:

- sustained key lift
- persistent KEY label
- empty-gap visualization
- one-at-a-time shift cadence
- diagonal placement drop
- key-on-top z-order rule

Two substantive issues were identified.

### Initial issues found

1. **Missing terminating-comparison phase.**
   The contract initially described compare-and-shift followed by placement, but did not document the required final T1 compare when the loop exits by condition `arr[j] <= key`.

2. **Unsupported post-placement color wording.**
   The contract said the placed key remained orange briefly and turned green at the next pass. That wording did not match the shared highlight replacement rules or the completion-color rules.

### Broader design-doc inconsistency exposed

The review also exposed a design-doc ambiguity about Insertion Sort's color boundary:

- insertion-specific docs and locked decisions said the sorted/unsorted boundary is communicated by a **green-to-blue** color transition
- a later UI-spec passage could be read as saying Insertion Sort does **not** use a color distinction at all

This turned out to be a wording problem, not a design intent change.

### Fixes confirmed

The following corrections were later confirmed:

- a new terminating-comparison subsection was added
- the worked example now covers both exit paths:
  - `j < 0`
  - exit-by-condition
- the unsupported post-placement color language was replaced with wording that defers to the standard highlight replacement rule and D-073
- the ambiguous UI-spec passage was rewritten so it clearly says Insertion Sort does not use the **settled steel-blue** color, while still acknowledging the **green-to-blue** boundary

### Final assessment

**Status:** Aligned.

The Insertion Sort contract now supports and clarifies the design docs, and the surrounding docs no longer conflict on the reviewed issues.

---

## Design-Doc Corrections Confirmed During Review

The review process led to a number of important doc-level repairs outside the contracts themselves.

### Confirmed design-doc fixes

- Heap Sort tick grammar corrected to reflect optional compare and swap counts per sift-down level.
- Heap Sort T3 payload wording corrected to allow the single-child case.
- Heap Sort contract references corrected to point to actual design-doc headings.
- Bubble Sort swap-path language corrected from arc motion to lifted horizontal exchange where needed.
- Bubble Sort compare-lift timing references normalized to the animation spec.
- Bubble Sort `compare_lift_offset` references normalized to `50px` where stale proportional wording remained.
- Insertion Sort terminating-comparison requirement made explicit in the contract.
- Insertion Sort post-placement color wording aligned with shared highlight rules.
- UI-spec insertion boundary wording disambiguated to preserve D-073.

---

## Recommendations

## 1. Treat the animation spec as the choreography source of truth

The reviews repeatedly showed that the most precise motion definitions lived in `10_ANIMATION_SPEC.md`, while broader docs sometimes retained stale summaries. Future doc changes should be checked against the animation spec first.

## 2. Keep contract docs synchronized with supporting design docs

When a contract is updated, the following supporting docs should be checked in the same pass when relevant:

- `05_ALGORITHMS_VIS_SPEC.md`
- `06_BEHAVIOR_SPEC.md`
- `07_ACCEPTANCE_TESTS.md`
- `12_ANIMATION_FOUNDATION.md`
- `DECISIONS.md`

This is especially important for:

- timing tables
- color-state rules
- tick grammar
- asset lifecycle behavior
- motion path wording

## 3. Prefer explicit lifecycle subsections for algorithm-specific exceptions

The clearest fixes were the ones that elevated special cases into named subsections rather than leaving them implied in prose. This pattern worked well for:

- Heap Sort T3 variants and sift-down grammar
- Bubble Sort compare-lift timing and swap path
- Insertion Sort terminating comparison and persistent key state

## 4. When a rule depends on another doc, cite the exact heading

Several review passes were spent correcting vague or inaccurate cross-references. Future contract updates should point to exact heading names rather than approximate section labels whenever possible.

---

## Current Conclusion

Based on the review and follow-up verification work completed on 2026-04-05:

- the reviewed animation contracts are now consistent with the design docs on the issues examined
- the main contradictions that surfaced during review have been corrected
- the remaining work, if any, is routine maintenance rather than structural repair

This summary should be treated as the high-level record of the review sequence and its recommendations.