# Product Requirements Document (PRD)
## Bucket Sort Visualizer — Lightning Labs Style (PRD v1)

**Status:** Draft  
**Last updated:** 2026-02-08  
**Source inputs:** Design Approach v3 + reference animation video

---

## 0. Document Control

| Field | Value |
|---|---|
| Product | Bucket Sort Visualizer (Lightning Labs) |
| Primary goal | Teach Bucket Sort visually via a polished animation |
| Target OS | Windows 10/11 |
| Runtime | Python 3.13 (UV-managed) |
| Rendering | Pygame |
| Export | mp4 via ffmpeg (stdin piping) |

---

## 1. Executive Summary

Bucket Sort Visualizer is a desktop Python application that renders a dark‑neon “Lightning Labs” style animation of the Bucket Sort algorithm. The visualization progresses through three phases — **Scatter**, **Sort**, **Gather** — and includes a synchronized “Algorithm Logic” pseudocode panel that highlights the currently executing step.

This product is designed for **visual learners**, instructors, and content creators who want a crisp, reproducible demo (seeded randomness) with optional mp4 export.

---

## 2. Problem Statement

Many learners struggle to understand non-comparison / distribution-style sorting techniques because most explanations are static or purely textual. Bucket sort is especially intuitive when shown as **distribution into buckets**, **local sorting**, then **recombination** — but that requires a clear, well-paced, visually consistent animation.

---

## 3. Goals and Success Metrics

### 3.1 Goals (P0)
- G1: Provide a clear, step-by-step visualization of bucket sort: READY → SCATTER → SORT → GATHER → SORTED.
- G2: Ensure the visualization is reproducible for teaching and recording (seed support).
- G3: Match the Lightning Labs dark-neon aesthetic closely enough to feel “like the reference.”

### 3.2 Success Metrics (pragmatic / measurable)
- S1: Deterministic runs reproduce the same input and animation order for a given preset+count+seed.
- S2: Export mode produces a playable mp4 with no temporary frame files.
- S3: Algorithm output is correct for all presets and element counts (unit tests).
- S4: Viewer comprehension (qualitative): users can explain “scatter/sort/gather” after watching once.

---

## 4. Users and Use Cases

### 4.1 Primary Personas
- P1: Visual learner (beginner CS student)
- P2: Instructor / tutor (wants repeatable in-class demos)
- P3: Content creator (wants quick export to mp4)

### 4.2 Core Use Cases
- UC1: Run interactive demo from a menu, show phases.
- UC2: Run scripted demo from CLI with a seed for consistent results.
- UC3: Export mp4 for sharing/embedding.

---

## 5. In Scope / Out of Scope

### 5.1 In Scope
- Dark-neon “Lightning Labs” UI with two panels: animation + algorithm logic panel.
- 3 presets (small/medium/large), element count 10–15, random seed.
- Animation phases: READY, SCATTER, SORT BUCKETS, GATHER, SORTED celebration.
- Optional mp4 export using ffmpeg.
- Tests for algorithm correctness and step sequencing.

### 5.2 Out of Scope (initially)
- Additional algorithms (quick sort, merge sort, radix, etc.)
- Web version
- Full accessibility localization / translations
- Fully headless render pipeline on Windows (can revisit later)

---

## 6. Assumptions & Dependencies

- A1: Users can install Python 3.13 and UV (or use prebuilt env).
- A2: ffmpeg is installed when export is desired.
- A3: Rendering runs at a stable target FPS (30 FPS target; actual may vary by machine).
- A4: Primary OS is Windows 10/11.

---

# 7. Functional Requirements (PRD IDs)

**Priority legend:**  
- P0 = must have for MVP  
- P1 = should have (next)  
- P2 = nice to have

---

## 7.1 App Configuration & Presets

### PRD-1.0 Presets (P0)
**Requirement:** The app MUST include three presets: Small (0–99), Medium (0–199), Large (0–999) with predefined bucket counts and bucket widths.

**Acceptance Criteria**
- Small: 4 buckets sized 25 each
- Medium: 8 buckets sized 25 each
- Large: 10 buckets sized 100 each
- Preset validation confirms full range coverage with no gaps.

### PRD-1.1 Element count limits (P0)
**Requirement:** The app MUST support selecting an element count between 10 and 15 inclusive.

**Acceptance Criteria**
- Interactive and CLI paths enforce the bounds.

### PRD-1.2 Random seed (P0)
**Requirement:** The app MUST accept an optional seed to produce deterministic runs.

**Acceptance Criteria**
- Same preset+count+seed yields same input list and same visual sequence ordering.

---

## 7.2 User Interfaces (Menu + CLI)

### PRD-2.0 Dual interface (P0)
**Requirement:** The app MUST support both:
1) an interactive menu (Pygame), and  
2) direct CLI execution that bypasses the menu when preset and count are provided.

**Acceptance Criteria**
- If user provides `--preset` AND `--count`, menu is skipped.
- Otherwise, menu is shown.

### PRD-2.1 CLI flags (P0)
**Requirement:** The CLI MUST support:
- `--preset {small,medium,large}`
- `--count 10-15`
- `--seed int`
- `--export` boolean
- `--no-code-panel` boolean

**Acceptance Criteria**
- Invalid combinations are handled with clear error output.
- `--export` triggers ffmpeg availability check.

### PRD-2.2 Menu controls (P0)
**Requirement:** The menu MUST allow selecting preset, element count, export option, code panel visibility, and optional seed.

**Acceptance Criteria**
- Keyboard: arrows adjust selection; Tab cycles; Enter starts; ESC exits.
- Mouse interaction supported for selection and Start button.

---

## 7.3 Rendering & Layout

### PRD-3.0 Resolution and FPS target (P0)
**Requirement:** The default window MUST be 1694×924 with a target render loop of 30 FPS.

**Acceptance Criteria**
- App opens with the specified resolution and title.
- Animation timing is frame-derived from second-based constants.

### PRD-3.1 Lightning Labs visual style (P0)
**Requirement:** The UI MUST match the “Lightning Labs” dark-neon aesthetic (dark background, neon phase colors, glowing active elements, grid-like backdrop).

**Acceptance Criteria**
- Phase colors: cyan (scatter), yellow (sort), magenta (gather), green (sorted).
- Default element state is muted grey; active is bright with glow.

### PRD-3.2 Two-panel structure (P0)
**Requirement:** The app MUST show:
- Top panel: animation stage (input row, buckets, output row)
- Middle branding strip: “LIGHTNING LABS”
- Bottom panel: “ALGORITHM LOGIC” pseudocode with active-line highlight

**Acceptance Criteria**
- Pseudocode panel highlight changes during animation steps.
- Branding strip is visible between panels.

---

## 7.4 Algorithm Visualization Flow (Phases & Sub-Phases)

### PRD-4.0 Global flow (P0)
**Requirement:** The visualization MUST progress through:
READY → SCATTER → SORT BUCKETS → GATHER → SORTED.

**Acceptance Criteria**
- Each phase has an on-screen label.
- Phase transitions include a brief pause.

---

### PRD-4.1 READY phase (P0)

#### PRD-4.1.1 Input row (P0)
**Requirement:** Display N unsorted values as circles in a horizontal row in the top panel.

**Acceptance Criteria**
- Values are visible and readable.
- Circle styling matches default (muted grey).

#### PRD-4.1.2 Buckets (P0)
**Requirement:** Display empty bucket outlines beneath the input row with range labels.

**Acceptance Criteria**
- Bucket count and labels match preset ranges.
- Buckets are empty at READY.

#### PRD-4.1.3 Hold (P0)
**Requirement:** Hold READY state for a configurable duration before starting scatter.

**Acceptance Criteria**
- Uses a `ready_hold` timing constant.

---

### PRD-4.2 PHASE 1 — SCATTER (P0)

#### PRD-4.2.1 Active element selection and glow warmup (P0)
**Requirement:** Before moving each element, briefly highlight it (glow warmup).

**Acceptance Criteria**
- Glow appears for `scatter_glow_warmup` duration.

#### PRD-4.2.2 Arc motion (P0)
**Requirement:** Each element MUST move along a smooth arc from the input row into its target bucket.

**Acceptance Criteria**
- Arc motion uses an ease-in-out sine feel.
- Each element’s travel duration uses `scatter_per_element`.
- Scatter begins with stagger delay `scatter_stagger` between elements.

#### PRD-4.2.3 Correct bucket targeting (P0)
**Requirement:** Each element MUST land in the mathematically correct bucket per preset range rules.

**Acceptance Criteria**
- Bucket index computed matches bucket ranges.
- Visual placement matches the computed bucket.

#### PRD-4.2.4 Bucket stacking and overflow handling (P0)
**Requirement:** Elements MUST stack bottom-up within a bucket. If the stack exceeds bucket height, spacing compresses to keep all visible.

**Acceptance Criteria**
- All elements remain visible within bucket bounds.
- Stack order remains consistent and readable.

#### PRD-4.2.5 Code panel sync (P0)
**Requirement:** During scatter, the code panel MUST highlight the “push into bucket” line.

**Acceptance Criteria**
- Highlight updates exactly when each element is pushed.

---

### PRD-4.3 PHASE 2 — SORT BUCKETS (P0)

#### PRD-4.3.1 Bucket-by-bucket processing (P0)
**Requirement:** The animation MUST process buckets in index order.

**Acceptance Criteria**
- Clear transition between buckets with `sort_bucket_pause`.

#### PRD-4.3.2 Local sort visualization (P0)
**Requirement:** Within each bucket, show insertion-sort-style comparisons and swaps (or shifts), with visual emphasis on involved elements.

**Acceptance Criteria**
- Comparison highlight appears for `sort_compare_hold`.
- Movement animation for reorder uses `sort_swap` duration and a smooth quad easing feel.

#### PRD-4.3.3 Code panel sync (P0)
**Requirement:** During bucket sorting, highlight the insertionSort line.

**Acceptance Criteria**
- Highlight stays on the sort line during bucket sort steps.

---

### PRD-4.4 PHASE 3 — GATHER (P0)

#### PRD-4.4.1 Gather order (P0)
**Requirement:** Gather elements from buckets in ascending bucket order, producing a final sorted output row.

**Acceptance Criteria**
- Output row order is globally sorted.

#### PRD-4.4.2 Arc motion to output row (P0)
**Requirement:** Each element MUST fly from its bucket to the output row in an arc motion distinct from scatter.

**Acceptance Criteria**
- Uses ease-in-back feel.
- Each element’s gather duration uses `gather_per_element`.
- Consecutive gathers stagger by `gather_stagger`.

#### PRD-4.4.3 Code panel sync (P0)
**Requirement:** During gather, highlight the “output.concat(b)” line.

**Acceptance Criteria**
- Highlight updates during each gather action.

---

### PRD-4.5 SORTED + CELEBRATION (P0)

#### PRD-4.5.1 Final row celebration pulse (P0)
**Requirement:** When sorted, the output row MUST glow/pulse green for a celebration hold duration.

**Acceptance Criteria**
- Celebration lasts `celebration_hold`.
- Pulse rate uses `celebration_pulse_rate`.

#### PRD-4.5.2 End state label (P0)
**Requirement:** Display a “SORTED” label in green in the top panel.

**Acceptance Criteria**
- Visible and consistent with reference styling.

---

## 7.5 Algorithm Logic Panel

### PRD-5.0 Pseudocode lines (P0)
**Requirement:** The code panel MUST display the pseudocode for Scatter / Sort / Gather and visually highlight the currently active line.

**Acceptance Criteria**
- Lines include: scatter loop, bucket push, sort call, gather concat.
- Highlight bar is clearly visible behind the active line.

### PRD-5.1 Step-to-line mapping (P0)
**Requirement:** The animation system MUST map each step type to a code line index for highlighting.

**Acceptance Criteria**
- Scatter → push line
- Compare/swap/no-swap → insertionSort line
- Gather → concat line
- Phase transitions / celebration → no highlight

---

## 7.6 Video Export (mp4)

### PRD-6.0 Export mode (P0)
**Requirement:** When `--export` is enabled, the app MUST write an mp4 by piping raw frames to ffmpeg stdin (no temporary frame images).

**Acceptance Criteria**
- Exported video plays correctly in standard players.
- No temp PNG frame directory is created.

### PRD-6.1 ffmpeg detection (P0)
**Requirement:** If export is requested and ffmpeg is missing, the app MUST exit with an actionable message.

**Acceptance Criteria**
- Message includes Windows install guidance.

---

## 7.7 Testing, Documentation, and CI

### PRD-7.0 Unit tests (P0)
**Requirement:** Provide automated tests for algorithm correctness and step sequencing across presets.

**Acceptance Criteria**
- Tests pass for small/medium/large presets and count 10–15.

### PRD-7.1 CI pipeline (P1)
**Requirement:** Add GitHub Actions CI to run lint (ruff) and pytest on push/PR.

**Acceptance Criteria**
- CI runs on Windows and Ubuntu.
- Failures are visible on PRs.

### PRD-7.2 Docs (P1)
**Requirement:** Include algorithm theory docs and design decisions docs.

**Acceptance Criteria**
- Documentation explains bucket sort intuition, complexity, and when it works best.

---

# 8. Non-Functional Requirements (NFR)

### PRD-NFR-1 Performance (P0)
- Maintain a smooth animation experience at target FPS on a typical Windows 10/11 laptop.

### PRD-NFR-2 Reliability (P0)
- Application should not crash on invalid CLI args; must show helpful usage messages.

### PRD-NFR-3 Determinism (P0)
- Seeded runs must be fully deterministic (input + animation order).

### PRD-NFR-4 Maintainability (P0)
- Algorithm and visualization concerns must remain separable enough for unit testing.

---

# 9. Open Questions (for you)

1) Should inputs allow duplicate values?  
2) For “insertion sort” visualization: do you want **true shifting** or “swap-based” animation?  
3) Should the input row close gaps as elements scatter (reflow), or remain with gaps?  
4) Should the app include playback controls (pause / step / restart), or run straight through like the reference?  
5) Should export include audio cues if enabled, and do we need audio in the mp4?  
6) How strict is “match the reference video” (pixel-perfect vs same vibe)?  
7) Do you want this shipped as a Python project only, or also a Windows executable (PyInstaller) later?

---
