# Episode 2 — Why I Over-Specified a Tiny Sorting App

**Series:** Small App. Serious Engineering.
**Episode thesis:** Misalignment between intent and implementation is the silent killer of software projects. Over-specification is not the disease — it is the vaccine.
**Role perspective:** Graphics/Engine Programmer review of the proposed solution.
**Date:** 2026-05-14

---

## Series Recap — Where Episode 2 Fits

Episode 1 introduced the project and the claim: this sorting visualizer was built using AI-assisted engineering, not AI-abdicated engineering. The app is deliberately small — four sorting algorithms racing side-by-side in a 2×2 grid — but the process around it is production-grade. Episode 1 established the thesis that spec-driven development with AI is fundamentally different from "vibe coding," and that the distinction matters for anyone building software they intend to maintain.

Episode 2 answers the obvious follow-up question: **why would anyone write 81 locked design decisions, 14 specification documents, and 4 animation contracts for a sorting visualizer?**

The answer is not "because documentation is virtuous." The answer is that every one of those specs exists because its absence would have introduced a concrete, traceable failure.

---

## The Central Argument

Most software failures are not coding failures. They are alignment failures.

A developer understands one thing. The spec implies another. The AI prompt assumes a third. The rendered output satisfies none of them. The bug report says "it doesn't work," but the root cause is that nobody agreed on what "working" meant before the first line of code was written.

This project was designed as a controlled experiment to test whether pre-coding specification — taken to an unusual level of detail for a small application — could eliminate that class of failure when working with AI coding agents.

The results were mixed in an instructive way. The specs prevented most categories of drift. But Phase 6 proved that specifications sufficient for a human implementer are not always sufficient for an AI prompt. That gap — between "spec-sufficient" and "prompt-sufficient" — is the central lesson of the entire series.

---

## What Was Actually Specified

The project locked 81 design decisions (D-001 through D-081) before implementation began. These are not aspirational guidelines. Each one is a numbered, dated, immutable constraint with a rationale. Changing one requires a formal supersession entry.

The specification surface includes:

- **Product requirements** (01_PRD) — scope, audience, explicit non-goals, default dataset
- **Architecture** (02_ARCHITECTURE) — strict MVC, module boundaries, independent queue semantics, panel state machine
- **Data contracts** (03_DATA_CONTRACTS) — SortResult dataclass, OpType enum, tick taxonomy, highlight rules, counter semantics
- **UI specification** (04_UI_SPEC) — panel layout, header vertical rhythm, color palette with WCAG AAA contrast ratios, font stack, resolution presets
- **Algorithm visualization spec** (05_ALGORITHMS_VIS_SPEC) — per-algorithm tick sequences, motion signatures, pointer assets, boundary markers
- **Behavior spec** (06_BEHAVIOR_SPEC) — play/pause/step/restart, operation timing, keyboard bindings
- **Acceptance tests** (07_ACCEPTANCE_TESTS) — 27 human-checkable criteria (AT-01 through AT-27)
- **Test plan** (08_TEST_PLAN) — QA strategy, 24 automated test cases, headless infrastructure
- **Animation spec** (10_ANIMATION_SPEC) — frame timing, interpolation rules, sprite coordinate system, z-ordering, per-algorithm motion signatures
- **Animation foundation** (12_ANIMATION_FOUNDATION) — shared rendering contracts, sprite identity, cross-tick state model
- **Implementation order** (13_IMPLEMENTATION_ORDER) — 10-phase dependency graph with entry/exit criteria per phase
- **4 animation contracts** — tick-by-tick choreography documents for Bubble, Selection, Insertion, and Heap Sort

This is not typical for a project of this size. That is the point. The project is small enough that every spec can be traced to its effect in the running application.

---

## The Proof: Where Specs Prevented Failures

### Sprite identity by unique ID (D-012, doc 12 §1)

The array `[4, 7, 2, 6, 1, 5, 3]` has no duplicates. But the spec required sprite tracking by unique ID, never by value, because a future array like `[3, 1, 3, 2]` would make value-matching ambiguous. Without this spec, the initial implementation would have matched sprites by value — it is the obvious approach — and the system would have broken silently the moment duplicate values appeared.

Phase 10c confirmed this: `compute_sprite_moves()` needed a highlight-indices augmentation specifically for SWAP and SHIFT operations involving equal values. The fix was straightforward because the spec had already established the correct identity model. Without the spec, the bug would have surfaced as "animations look wrong sometimes" with no clear diagnostic path.

### Operation timing as integer milliseconds (D-056)

The spec locked T1 Compare at 150ms, T2 Swap/Shift at 400ms, T3 Range at 200ms, with Heap Sort sift-down cadence overrides at 100/250/130ms. These are not suggestions — they are the exact values the controller uses to schedule operations.

This matters because the "race" between algorithms is the core pedagogical feature. If timing drifted or was implemented as approximate floats, the race outcome would vary between runs. Integer millisecond arithmetic makes the race deterministic and reproducible, which means acceptance tests can assert on exact elapsed times (e.g., Bubble Sort completes in exactly 8,200ms with the default array: 20 compares at 150ms + 13 swaps at 400ms).

### Counter accuracy table (CLAUDE.md)

The spec published the exact expected counter values for the default array:

| Algorithm | Comparisons | Writes | Steps |
|-----------|------------|--------|-------|
| Bubble Sort | 20 | 26 | — |
| Selection Sort | 21 | 10 | — |
| Insertion Sort | 17 | 19 | — |
| Heap Sort | 20 | 30 | 35 |

Integration tests (Phase 6e) verified these values against the real algorithm generators. Any generator bug that changes counter output breaks the test immediately. This is not possible without the spec — you cannot test counter accuracy if you have not defined what "accurate" means before writing the code.

### T3 RANGE ticks excluded from step counter (D-041)

Heap Sort emits 6 boundary T3 ticks that are visual teaching aids, not algorithmic operations. Without the spec, these ticks would have been counted as steps, inflating Heap Sort's step count from 35 to 41. The error would have been invisible — the app would look correct, but the pedagogical claim ("Heap Sort completes in 35 steps") would have been wrong.

### Animation contract review (2026-04-05)

Before any view code was written, an animation contract review identified and corrected:

- Heap Sort sift-down grammar that was too narrow (rigid `T3 → T1 → T2` vs. correct `T3 → T1{1,2} → T2{0,1}`)
- Bubble Sort swap-path language that still described arc motion instead of lifted horizontal exchange
- Insertion Sort missing terminating-comparison phase
- 6 stale cross-references pointing to wrong section numbers

Every one of these would have produced a prompt that built the wrong animation. The review caught them before they became runtime defects.

---

## The Proof: Where Specs Were Not Enough

### Phase 6c — The SHIFT tick assumption

The Phase 6c prompt stated: "SHIFT ticks always produce 2 changed indices." This seemed like a safe inference from the spec's description of Insertion Sort shifts — one element moves right, so two array positions change.

The actual generator yields `self.data.copy()` after `arr[j+1] = arr[j]`, which modifies only slot `j+1`. Slot `j` retains its original value because the key was already extracted. The array delta shows exactly 1 changed index, not 2.

The spec described the logical operation accurately. A human reading "shift one element right" would write code that handles whatever delta shape falls out. The AI prompt author assumed the delta shape from the spec's prose without tracing the generator's actual yield point. The spec was correct. The prompt was wrong.

This is the gap between "spec-sufficient" and "prompt-sufficient." The spec tells you *what* happens. The prompt needs to know *what the code emits when it happens*. Those are different things.

The two-agent workflow (Sonnet built, Opus reviewed) caught the gap at runtime. But catching it at prompt-writing time — by tracing the generator's yield against the delta function's input expectations — would have been cheaper.

### Phase 10 — 345 tests passed, 10 visual bugs remained

All 345 automated tests were green. Then manual acceptance testing (AT-01 through AT-27) found 10 visual issues:

- `compute_sprite_moves()` failed silently with duplicate values (#7, #8)
- Heap Sort overlay elements rendered outside panel boundaries (#3)
- Heap Sort placeholder outlines appeared during the wrong phase (#6)
- Heap Sort phase label obscured by sprites (#1)
- False extraction detection in Heap Sort SWAP handler (#10)
- Bubble Sort boundary line persisted after completion (#11)
- Selection Sort `i` pointer was visually indistinguishable from `j` and `min` (#4)

These are not test failures — the unit and integration tests correctly verified the model and controller layers. These are rendering issues that only surface when a human watches the animation run. The spec covered what should happen. The tests verified the data flow. But visual correctness requires visual inspection.

The lesson: automated tests verify contracts. Acceptance tests verify experience. Both are necessary. Neither is sufficient alone.

---

## Graphics/Engine Review — Key Findings

As the Graphics/Engine Programmer reviewing this codebase, six architectural strengths stand out:

1. **Time-normalized interpolation** — every sprite motion uses `t = min(elapsed / duration, 1.0)` with easing, preventing overshoot regardless of frame rate. The `dt = min(clock.tick(60), 33)` clamp (Critical Rule #7) prevents large frame drops from teleporting sprites.

2. **Generator-based algorithm model** — each algorithm is a Python generator yielding typed `SortResult` ticks. The view layer never reaches into algorithm internals. This separation means you can test all four algorithms without Pygame installed.

3. **Independent per-algorithm queues** — the orchestrator processes each panel's timing independently. Bubble Sort's T2 swap (400ms) blocks only Bubble Sort's panel, not the other three. This creates the authentic race behavior that is the core pedagogical feature.

4. **Sprite identity delta** — `compute_sprite_moves()` compares consecutive array snapshots by index, never by value. The pure function returns `{sprite_id: new_slot}`, which the view translates into animation targets. This is the correct approach for handling duplicate values.

5. **Per-algorithm choreography contracts** — each algorithm has a distinct visual language: Bubble Sort uses compare-lift pairs with horizontal exchange at a compare lane. Selection Sort uses triple-pointer scan (i/j/min). Insertion Sort uses sustained key elevation with sequential one-at-a-time shifts. Heap Sort uses binary tree layout with 2D arc interpolation for sift-down swaps and extraction arcs.

6. **Phase-gated implementation** — the 10-phase build sequence with entry/exit criteria per phase meant that no rendering code was written before contracts were frozen, no controller code was written before generators were tested, and no integration happened before unit tests were green. This is disciplined and it shows in the zero-logic-correction record across Phases 6a through 6e.

The primary concern is the `sprite_manager.py` god object (1,040 lines housing dispatch, interpolation, overlay, and draw logic for all four algorithms). This is a known consequence of the Phase 7 delivery timeline and a natural candidate for refactoring into per-algorithm strategy classes in a future phase.

---

## The Numbers

| Metric | Value |
|--------|-------|
| Design decisions locked | 81 (D-001 through D-081) |
| Specification documents | 14 |
| Animation contracts | 4 |
| Acceptance test criteria | 27 (AT-01 through AT-27) |
| Automated test cases | 24 (TC-A1 through TC-A24) |
| Tests passing | 345 / 345 |
| Source lines (production) | ~2,650 |
| Implementation phases | 10 |
| Logic corrections (Phase 6) | 0 |
| Visual bugs found in acceptance | 10 (all resolved) |
| File truncation incidents (Phase 10) | 4 (all restored from git) |
| Models used | Sonnet 4.6 (primary), Opus 4.6 (Heap choreography + duplicate-value fix) |

---

## Episode 2 Key Takeaways

1. **Over-specification is not about documentation volume.** It is about reducing ambiguity before it becomes runtime drift. Every spec in this project traces to a concrete failure it prevented or a concrete gap it exposed.

2. **"Spec-sufficient" and "prompt-sufficient" are different standards.** A human reads a spec and infers implementation details. An AI prompt implements exactly what the prompt describes. The gap between them is where assumptions hide.

3. **Automated tests verify contracts. Acceptance tests verify experience.** 345 green tests did not prevent 10 visual bugs. Both layers are necessary.

4. **The process caught the bugs that mattered.** The sprite identity spec prevented silent corruption. The animation contract review prevented wrong choreography. The acceptance tests caught rendering issues that unit tests cannot see. The spec-driven process did not eliminate all bugs — it made them findable and fixable.

5. **Small app, serious engineering.** The application is deliberately small so that every engineering decision is traceable from spec to implementation to test to visual output. The size is the feature, not the limitation.

---

## Connection to Episode 3

Episode 2 ends with the SHIFT tick gap — the moment the spec was right but the prompt was wrong. Episode 3 picks up that thread: "The Moment the Spec Wasn't Enough." That episode dives into Phase 6's spec-paralysis-vs-spec-insufficiency reflection and the two-agent workflow that caught the gap. The question shifts from "why specify?" to "how do you specify for AI?"

---

*This document is a reference companion to Episode 2 of the "Small App. Serious Engineering." video series. It is intended for review, sharing, and script development. The authoritative project record lives in the repository's design docs, devlog archives, and CLAUDE.md.*
