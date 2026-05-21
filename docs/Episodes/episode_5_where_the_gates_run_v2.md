# Episode 5 — Where the Gates Run (v2)

**Series:** Visual Learning Sorting — AI-Assisted Development Case Study
**Episode title card:** *Episode 5 — Where the Gates Run*
**YouTube public title:** *35 Phases. Not One Big PR.*
**Target runtime:** 3:15–3:25 (hard ceiling 3:35)
**Central lesson:** **A phase isn't a unit of scheduling. It's a unit of containment — and it's the only place a gate has to fire.**
**Shareable line:** *"Gates catch what AI didn't do. Phases give the gates somewhere to fire."*

---

## What changed from v1 → v2

Editorial pass after v1 review. The structural shape, lesson, trichotomy, runtime, and shareable line are unchanged. Seven localized edits address the gaps the critique found: the recovery beat needed evidence, the technical readout was clunky, the CTA was generic, the containment visual undersold the metaphor, and the devlog claim could be made more specific now that verification passed.

| Field | v1 | v2 |
|---|---|---|
| 2:15 recovery beat | "rollback is one file, not one branch" (claim only) | Same claim, now grounded as a cross-reference to Ep 4's Phase 10 truncations, with a "didn't ship" pre-emption |
| 2:15 visual | Three static cards | Three cards + 2-second B-roll cut to Ep 4's recovery clip during the recovery beat |
| 1:30–2:15 VO | Read TC-A20/A21/A22 and `src/visualizer/views/tree_layout.py` aloud | Drop the test-case IDs and the file-path prefix from VO; visual carries the metadata, VO carries meaning |
| 3:00 outro CTA | Generic "subscribe if you've been watching" | Engagement question: "what does your team currently treat as one unit of AI work?" |
| Image Prompt 5 (containment column) | "Self-contained box holding a damaged file" | Sealed-bulkhead / quarantine boundary holding contained damage — the blast-radius metaphor reads on screen |
| 1:00 devlog bullet | "What was delivered, and what the next phase can rely on" | The five real sections: worked on, results, corrections, decisions, next |
| Verification item 5 | Open ("verify devlog continuity") | **VERIFIED** — Phase 5d devlog at `docs/devlog/phase_05.md` lines 213–245 has a structured handover format including an explicit `Next` section naming Phase 5e |

---

## Episode Purpose

Episode 4 introduced gates as the thing that catches silent AI failures — parse checks, full test runs, diff stats, raw diff review. The implicit question that episode left unanswered: *where do those gates run?* You can't drop a gate on a thousand-line PR halfway through and expect it to mean anything. Gates need a boundary to fire at.

Episode 5 is about that boundary. The phase.

The project ran on thirty-five phases across seven days. Each phase had four parts — an entry context, a scoped output, exit gates, and a devlog entry. The same four parts, thirty-five times. That repetition isn't a slog. It's the discipline that made AI-assisted development auditable.

The episode's job is to take the abstract idea "split the work into phases" and make it concrete: what does one phase actually look like, what's inside it, and what makes the phase boundary load-bearing instead of cosmetic.

---

## Core Claim

Most conversations about AI productivity ask the wrong question: *"How do I get the AI to write more code, faster?"*

The better question: *"Where does each unit of work stop and prove itself?"*

In this project, the answer was the phase. A phase is the smallest unit of AI work that can be reviewed independently and recovered from independently if something goes wrong. Without it, there's no place for a gate to fire, no audit trail to read six months later, and no recovery surface when the AI silently breaks something.

The phase isn't a project-management artifact. It's an engineering primitive. The thirty-five-phase plan wasn't about pacing the work — it was about giving every AI edit somewhere to stop, test, and prove itself before the next one started.

---

## Shareable Lines

**Primary:**

> **"Gates catch what AI didn't do. Phases give the gates somewhere to fire."**

**Secondary:**

> **"A phase isn't a unit of scheduling. It's a unit of containment."**

> **"The phase is the smallest unit of AI work that can be reviewed independently."**

> **"Thirty-five phases. Not one big PR."**

> **"AI didn't make the discipline necessary. It made the discipline visible."**

---

## Tone

Same investigative documentary voice as Episode 4. Slightly more conceptual — the case study is supporting evidence, not the spine. Walk the viewer through a structural insight, then prove it with one real phase.

Avoid:
- "Agile methodology" framing — this is not about sprints.
- "Microservices for prompts" — clever but wrong analogy.
- Suggesting the phase count is the point. Thirty-five is what *this* project needed. The right count for a different project is different.

---

## Episode Structure

Total runtime: **~3:15–3:25**.

| Segment | Time | Purpose |
|---|---:|---|
| Cold open | 0:00–0:20 | One phase boundary visualized. Visual hook. |
| Bridge from Ep 4 | 0:20–0:40 | "Gates only work if there's somewhere to put them." |
| Wrong question / better question | 0:40–1:00 | Reframe productivity into containment. |
| The phase shape | 1:00–1:30 | Anatomy: entry context, scoped output, exit gates, devlog. |
| One real phase | 1:30–2:15 | Phase 5d — Heap tree layout. Tighter VO; visuals carry metadata. |
| Why the boundary matters | 2:15–2:40 | Containment, audit, recovery — with Phase 10 callback on recovery. |
| The lesson | 2:40–3:00 | Phase as engineering primitive + shareable line. |
| Episode 6 hook + outro | 3:00–3:20 | What goes *inside* a phase, plus engagement question. |

---

# Full Script Draft

## 0:00–0:20 — Cold open

**Visual:** Dark technical background. A single vertical slice of the implementation tracker animates in: one phase card above ("done" badge, gates row showing parse ✓ tests ✓ ruff ✓), a horizontal "exit gate" divider below it, and the next phase card entering from below. Hold on the divider — that's the visual hook.

**Voiceover:**

> "This is how the work moved."
>
> *[Beat]*
>
> "Not one big push. Thirty-five phases, each with a place to stop, test, and prove itself."
>
> "Without those boundaries, there's nowhere for a gate to run."

**On-screen text:**

```
35 phases.
Each one had to clear its gates
before the next one started.
```

---

## 0:20–0:40 — Bridge from Episode 4

**Visual:** Cut to Episode 4's lesson card briefly (the trichotomy: review / gates / raw diff). Hold for ~1 second, then dissolve.

**Voiceover:**

> "Last episode closed on a list of checks: parse, full suite, diff stat, raw diff. None of them depend on the AI noticing anything."
>
> "Gates only work if there's somewhere to put them."
>
> "Episode 5 is about that somewhere."

**On-screen text:**

```
Gates need a boundary to fire at.
The boundary is the phase.
```

---

## 0:40–1:00 — Wrong question / better question

**Visual:** Split card.

Left side, dimmer:

```
COMMON QUESTION
How do I get AI
to write more code, faster?
```

Right side, brighter, orange accent:

```
BETTER QUESTION
Where does each unit of work
stop and prove itself?
```

**Voiceover:**

> "When people talk about AI productivity, they usually ask: how do I get it to write more code, faster?"
>
> "That question has a place. But it skips something."
>
> "The better question: where does each unit of work stop and prove itself?"

**On-screen text:**

```
Productivity is downstream of containment.
```

---

## 1:00–1:30 — The phase shape

**Visual:** A clean four-part diagram of a single phase, animating each part in as the voiceover names it.

```
ENTRY CONTEXT  →  SCOPED OUTPUT  →  EXIT GATES  →  DEVLOG ENTRY
    specs           one file          parse · tests       worked on
   decisions        sometimes two     ruff · pyright      results
    priors          always bounded                        corrections
                                                          decisions
                                                          next
```

**Voiceover:**

> "Every phase in this project had four parts."
>
> "An entry context — the specs, decisions, and prior phases the work depends on."
>
> "A scoped output — usually one file, sometimes two. Always bounded."
>
> "A set of exit gates — parse, tests, ruff, pyright."
>
> "And a devlog entry — what was worked on, what the gates returned, what got corrected, what was decided, and what the next phase can rely on."
>
> *[Beat]*
>
> "Four parts. Thirty-five times."

**On-screen text:**

```
Same shape, thirty-five times.
That's the discipline.
```

> **v2 note:** The devlog bullet now names the five sections the real entries actually contain (`worked on` / `results` / `corrections` / `decisions` / `next`). This is what Phase 5d's devlog literally looks like — see `docs/devlog/phase_05.md` lines 213–245. The longer VO clause earns its time because it shows the devlog is a structured artifact, not a status note.

---

## 1:30–2:15 — One real phase: Phase 5d

**Visual:** Walk through Phase 5d on screen. Sequence:

1. **The phase card** (overlay): `Phase 5d — Heap Sort tree layout. Sonnet 4.6. 38 tests. Zero corrections.`
2. **Entry context** (file references on screen): `docs/design_docs/10_ANIMATION_SPEC.md` plus the three test case IDs `TC-A20`, `TC-A21`, `TC-A22` displayed visually.
3. **Scoped output** (file path on screen): `src/visualizer/views/tree_layout.py` — full path visible so the viewer registers it as a real artifact.
4. **Exit gates** (terminal): `uv run pytest tests/unit/test_tree_layout.py` → 38 passed. `ruff check` → clean. `ruff format` → clean. `pyright` → clean.
5. **Devlog entry** (overlay card showing the real sections): the `Next` section reading `Phase 5e: pointer.py (Selection Sort i/j/min arrows with coalescing, D-068, TC-A23)` highlighted.

**Voiceover (tightened in v2 — metadata moved to visuals):**

> "Phase five-d. Heap Sort tree layout."
>
> "Entry context: the animation spec, plus three strict test cases. The geometry the sprite layer would later render against."
>
> "Scoped output: one file — `tree_layout.py`. Binary tree node positions, edges, sorted-row mapping."
>
> "Exit gates: thirty-eight unit tests. Ruff clean. Pyright clean."
>
> *[Beat]*
>
> "Devlog: one-sixty-three of one-sixty-three tests passing. Phase closed. Five-e ready to start."
>
> "That's the shape. One file. One scoped change. Gates that fire before the phase closes."

**On-screen text:**

```
Phase 5d — closed
1 file · 38 tests · 0 corrections
```

> **v2 note on pacing:** Critique flagged "A-twenty, twenty-one, twenty-two" and `src/visualizer/views/tree_layout.py` as a mouthful in audio. v2 drops the test-case IDs from VO ("three strict test cases" instead) and drops the path prefix from VO (just "`tree_layout.py`"). The visuals still show the full IDs and full path — receipts stay, audio drag goes away. About 20% shorter than v1, scans naturally, no information lost.
>
> **Sources for every on-screen claim:** `TODO/IMPLEMENTATION_TRACKER.md` Phase 5d entry; `docs/devlog/phase_05.md` lines 213–245 (verified to contain handover format); the cumulative count "163/163" matches the CLAUDE.md status line.

---

## 2:15–2:40 — Why the boundary matters

**Visual:** Three short cards stack in sequence as the voiceover names each. **During the third card (recovery), cut briefly to Episode 4's recovery footage** — the `git show HEAD~1:src/visualizer/views/pointer.py > src/visualizer/views/pointer.py` command from the recording sandbox, followed by `wc -l` reading 144. ~2 seconds. Then back to the three-things card.

```
CONTAINMENT      Damage stays inside one phase.
AUDIT            Every phase has a devlog entry.
RECOVERY         Rollback is one file, not one branch.
```

**Voiceover (revised in v2 — recovery beat now cross-references Episode 4):**

> "Three things the phase boundary gave me that one big PR wouldn't have."
>
> "One — containment. If the AI broke something, it broke it inside one phase. Diagnosable scope."
>
> "Two — audit. Every phase had a devlog entry. Six months from now, you can read why a decision was made and what was tested when."
>
> "Three — recovery. If a phase failed, the rollback was one file. Not one branch."
>
> *[Beat — B-roll cuts in here: Episode 4's recovery footage, ~2 seconds]*
>
> "That's what reversed each of the Phase 10 truncations from the last episode. And it's why those incidents didn't ship."
>
> *[Beat]*
>
> "None of these are AI features. They're discipline features. AI just made them more visible."

**On-screen text (after the B-roll, back on the three-things card):**

```
AI didn't make the discipline necessary.
It made the discipline visible.
```

> **v2 note:** Critique flagged that the v1 recovery beat sat without evidence. The Phase 10 cross-reference fixes that — viewers saw the truncation incidents in Episode 4, and the recovery footage already exists. The "didn't ship" line pre-empts the obvious counter-question ("but did the bug make it to production?"). Two seconds of B-roll, no new shoot, plural truncations heavier than one. The boundary metaphor now has receipts.

---

## 2:40–3:00 — The lesson

**Visual:** Lesson card.

```
A PHASE ISN'T A UNIT OF SCHEDULING.
IT'S A UNIT OF CONTAINMENT.
```

Below, smaller:

```
The smallest unit of AI work
that can be reviewed independently
and recovered from independently.
```

**Voiceover:**

> "That's the lesson."
>
> "A phase isn't a unit of scheduling. It's a unit of containment."
>
> "The smallest unit of AI work that can be reviewed independently — and recovered from independently if something goes wrong."
>
> *[Beat — slowest delivery]*
>
> "Gates catch what AI didn't do. Phases give the gates somewhere to fire."

**On-screen text (hold 4–5 seconds):**

```
Gates catch what AI didn't do.
Phases give the gates somewhere to fire.
```

---

## 3:00–3:20 — Episode 6 hook + outro

**Visual:** Cut to a prompt file on screen — `docs/prompts/phase_10e_pointer_spacing.md` or similar. Highlight the scoped instructions and the locked constraints at the top.

**Voiceover (revised in v2 — engagement question replaces generic CTA):**

> "But the phase boundary only does its job if the work inside it is bounded the right way."
>
> "Episode 6 is about what goes inside a phase. The prompt the AI reads. The contracts it has to bind to. And why locking those before the code is written is what made this methodology scale."
>
> *[Beat]*
>
> "Subscribe to see the back-half synthesis — and let me know in the comments: what does your team currently treat as one unit of AI work?"

**On-screen text:**

```
Next: What goes inside a phase.
The prompt. The locked contracts.
The work the AI doesn't get to redefine.
```

> **v2 note:** Critique flagged the v1 outro as a missed engagement opportunity — the LinkedIn and YouTube descriptions had a thoughtful "what does your team treat as one unit" question, but the script just said "subscribe." Moving the question into the video drives comments (algorithm signal) and converts passive viewers into reflective ones. Direct adoption from the description copy keeps the channel voice consistent.

---

## Total Runtime

~3:15–3:20 target. Hard ceiling 3:35. The 2-second Phase 10 B-roll at 2:15 is included in the segment budget — no new total runtime added.

---

## Voiceover Delivery Notes

### Overall tone

Same investigative documentary voice as Ep 4. Slightly more conceptual cadence — you're walking the viewer through structure, not evidence. The case study (1:30–2:15) is the proof, not the spine.

### Key delivery moments

**0:00 cold open:** "This is how the work moved." — flat, declarative. Don't oversell. "Thirty-five phases" is the receipt; let it land matter-of-factly.

**0:20 bridge:** "Episode 5 is about that somewhere." — slight pause before "somewhere." That one word is what bridges Ep 4 to Ep 5.

**1:00 phase shape:** Procedural cadence. Each of the four parts is a beat. The devlog clause is the longest (five sections named) — don't rush it. The list structure rewards a slight breath between each section name: "what was worked on" — *beat* — "what the gates returned" — *beat* — and so on. Viewers should hear it as a real template.

**1:30 case study:** Shift to specifics. "Phase five-d. Heap Sort tree layout." — flat, like reading a tracker entry. The receipts land harder when the delivery doesn't try to dramatize them. Use the breath between each line — entry, output, gates, devlog — to let the visual catch up with the audio.

**2:15 three things:** Three short clauses, each its own beat. The third — "rollback is one file, not one branch" — is the line working developers will remember. **Pause before the Phase 10 callback line** so the editor can land the B-roll cut without rushing it. "That's what reversed each of the Phase 10 truncations from the last episode" should feel like a pointer back to the prior episode, not a new claim.

**2:30 the punchline:** "AI didn't make the discipline necessary. It made the discipline visible." — slow down. This is the credibility line of the episode.

**2:40 the lesson:** Slowest delivery in the episode. *"A phase isn't a unit of scheduling. It's a unit of containment."* — two beats between the sentences.

**3:00 Ep 6 hook + question:** Forward energy through "the prompt the AI reads, the contracts it has to bind to." Then a deliberate slowdown for the comments question — that's the line you want the viewer to actually act on, not the line you want them to hear.

---

## Verification Checklist (do before recording)

| # | Item | Status |
|---|---|---|
| 1 | Phase count | Script says "thirty-five phases." Confirm against `TODO/IMPLEMENTATION_TRACKER.md` final count. If different, change every reference (cold open, on-screen text, YouTube title, LinkedIn post). |
| 2 | Phase 5d specifics | Tests: 38. Corrections: 0. Cumulative after 5d: 163/163. **VERIFIED** against `docs/devlog/phase_05.md` lines 213–225 and CLAUDE.md status line. |
| 3 | "Three strict test cases" | TC-A20, TC-A21, TC-A22 are the right cases for tree layout. **VERIFIED** against `docs/devlog/phase_05.md` lines 217 (devlog header) and 257 (start-of-phase plan). On-screen visual carries the IDs; VO says "three strict test cases." |
| 4 | "One file, sometimes two. Always bounded." | Confirm this describes the project's actual phase shape. If many phases touched 3+ files, soften to "usually one to three files, always scoped to a stated output." |
| 5 | Devlog continuity claim ("what the next phase can rely on") | **VERIFIED.** `docs/devlog/phase_05.md` Phase 5d entry has structured `Worked on` / `Results` / `Corrections` / `Decisions` / `Open questions` / `Next` sections. The `Next` section explicitly names Phase 5e and its specifics (line 245). v2 expanded the VO bullet to name those sections directly. |
| 6 | Phase 10 recovery footage availability | Required for the 2-second B-roll cut at 2:15. Confirm the recovery clip from Episode 4 (`git show HEAD~1:...` plus `wc -l 144`) is in your project archive or re-runnable from `recording/sandbox.py`. If not, the cross-reference VO line still works without the cut. |
| 7 | Episode 6 direction | Outro commits to "prompt + contracts." If you'd rather Ep 6 cover the human decision loop or a retrospective, rewrite the outro before recording. |

---

# Visual Asset Plan

## Required Screen Recordings

| Clip | What to record | Source |
|---|---|---|
| 01 | Implementation tracker scroll/highlight — phases stacked with gate rows visible | `TODO/IMPLEMENTATION_TRACKER.md` |
| 02 | A single phase card animating in with its four parts labeled | Editor graphic |
| 03 | Terminal: `uv run pytest tests/unit/test_tree_layout.py` showing 38 passed | Live run against the project |
| 04 | Devlog entry for Phase 5d, with the `Next` section highlighted | `docs/devlog/phase_05.md` |
| 05 | A prompt file from `docs/prompts/` — scoped instructions visible at the top | Existing file |
| 06 | **(v2 addition)** Re-use Episode 4's recovery footage — `git show HEAD~1:...` and `wc -l` reading 144 — for the 2-second callback at 2:15 | Existing Ep 4 footage or re-runnable via `recording/sandbox.py` |

Same visual rhythm as Ep 4: claim → receipt → claim → receipt. The phase-shape diagram (1:00–1:30) is the only static moment.

---

# Image Prompt Pack

Same dark blueprint conventions as Ep 4: charcoal background, neon blue lines, orange accents, no logos, no people.

## Image Prompt 1 — Episode 5 Main Title Card

```text
Create a polished technical documentary title card for a software engineering YouTube series. Theme: the phase boundary as the unit of containment in AI-assisted development. The composition should suggest a stack of bounded work units arranged vertically, each with subtle gate-check indicators on its right edge. Between two phases, a horizontal divider should be visually highlighted in orange to mark the phase boundary as the focal point. Use a premium documentary style with charcoal background, blueprint grid texture, neon blue interface lines, and orange accents on the boundary marker. Leave a large clean text-safe area in the center or lower third for overlaying the episode title later. No company logos. No people. Style: serious, structural, engineering-credible.
```

Overlay text:

```
EPISODE 5 — WHERE THE GATES RUN
```

## Image Prompt 2 — Wrong / Better Question Split Card

```text
Create a clean 16:9 technical explainer graphic split into two sides. Left side: dimmer, labeled "Common question" — show a question about productivity ("write more code, faster") with a small productivity-arrow motif. Right side: brighter with orange accent, labeled "Better question" — show a question about containment ("where does each unit of work stop and prove itself") with a small phase-boundary motif. The contrast between the two sides should make clear that the right question is about structure, not speed. Dark documentary style, blueprint grid, neon blue lines, orange accent on the right side. No logos. No people.
```

Overlay text:

```
Productivity is downstream of containment.
```

## Image Prompt 3 — The Phase Shape Diagram

```text
Create a clean horizontal flow diagram showing the four parts of an engineering phase: entry context, scoped output, exit gates, devlog entry. Each part should be a labeled rectangular node connected by directional arrows. Inside each node, include small visual motifs: entry context shows stacked spec/decision documents; scoped output shows a single file icon; exit gates shows a row of small check marks; devlog entry shows a notebook with five visible section labels reading "worked on", "results", "corrections", "decisions", "next". Dark blueprint engineering style, neon blue connectors, orange accent on the exit-gates node, charcoal background. Leave space below for an annotation line.
```

Overlay text:

```
Same shape, thirty-five times.
That's the discipline.
```

## Image Prompt 4 — Phase 5d Case Card

```text
Create a polished case-study card for a software engineering documentary. The card represents one engineering phase in detail. Header bar shows "Phase 5d — Heap Sort tree layout" with a small "closed" badge. Body shows four labeled sections: Entry context (lists a spec document and three test case IDs), Scoped output (shows a single Python file icon labeled tree_layout.py), Exit gates (a row of small check marks for pytest, ruff, pyright), Devlog entry (a small notebook icon with "163/163" visible and a "next: Phase 5e" line). Dark blueprint engineering style, neon blue interior lines, orange accent on the exit-gates row, charcoal background. No logos. No people. Make it look like a real engineering tracker entry, not a marketing slide.
```

Overlay text:

```
Phase 5d — closed
1 file · 38 tests · 0 corrections
```

## Image Prompt 5 — Three Things The Boundary Buys *(revised in v2 — containment column now uses sealed-bulkhead metaphor)*

```text
Create a clean three-column technical explainer graphic. Each column shows one benefit of a phase boundary. Column 1 — "Containment": show a self-contained section of a code panel surrounded by a sealed quarantine boundary, with red damage indicators visibly contained INSIDE the seal — the surrounding code area outside the seal is clean and unaffected. The visual should communicate blast-radius containment, like a sealed bulkhead in a ship hull or a network quarantine zone. Column 2 — "Audit": a stacked devlog timeline showing multiple chronological entries, each with visible section headers, conveying a readable historical record. Column 3 — "Recovery": a single Python file icon being restored via a small git-arrow indicator, with the rest of the codebase intact. Each column has a one-line label below the visual. Dark blueprint engineering style, charcoal background, neon blue dividers between columns, orange accents on the small visuals inside each column. No logos. No people.
```

Overlay text:

```
Containment.    Audit.    Recovery.
Three things one big PR can't give you.
```

## Image Prompt 6 — Lesson Card

```text
Create a clean final lesson card for a software engineering documentary. Center: two short stacked lines reading "A phase isn't a unit of scheduling. / It's a unit of containment." Below, smaller, in three short lines: "The smallest unit of AI work / that can be reviewed independently / and recovered from independently." Premium documentary style, charcoal background, blueprint grid, white typography space, neon blue thin lines, orange accent on the word "containment." No logos. No realistic people. Authoritative and uncluttered.
```

Overlay text:

```
A phase isn't a unit of scheduling.
It's a unit of containment.
```

## Image Prompt 7 — Shareable Line Card

```text
Create a clean, high-contrast quote card for a technical YouTube series. Background: dark charcoal with subtle blueprint grid texture. Center: a large text-safe area for a single short quote in two short lines. To one side, a small motif showing a check-gate firing at a phase boundary. Premium technical documentary style, neon blue thin lines, orange accent on the gate motif. No logos. No humans.
```

Overlay text:

```
Gates catch what AI didn't do.
Phases give the gates somewhere to fire.
```

## Image Prompt 8 — Episode 6 Teaser

```text
Create a clean technical teaser image representing a prompt file. Show a document panel with a header reading "Phase prompt" and the visible body showing scoped instructions (sample text like "Output file: ...", "Locked decisions: ...", "Exit gates: ..."). The composition should emphasize that the prompt is a bounded artifact, not a free-form request. Dark documentary engineering style, blueprint grid, neon blue interface lines, orange accents on the locked-constraints lines, charcoal background. Leave a text-safe area below for the next-episode teaser. No logos. No humans.
```

Overlay text:

```
Next: What goes inside a phase.
```

## Image Prompt 9 — YouTube Thumbnail (primary)

```text
Create a high-impact YouTube thumbnail for a technical software engineering video. Theme: the methodology of slicing a project into bounded phases rather than building it as one large unit. Show a large code panel on one side cleanly sliced into multiple small bounded sections, contrasted with a single large unsliced code panel that looks tangled. Dark documentary style, blueprint blue and orange accents, bold empty area for large thumbnail text. No logos. No realistic people. Professional, not cartoonish.
```

Thumbnail text:

```
35 PHASES.
NOT ONE BIG PR.
```

## Image Prompt 10 — YouTube Thumbnail (alternate)

```text
Create a professional YouTube thumbnail for an AI-assisted software engineering case study. Show a stack of phase cards on one side, each with a small "gate" checkpoint on its boundary; on the other side, large bold text about phases as containment. Dark technical documentary style, neon blue lines, orange highlights on the gate markers, large clean text area. No logos, no humans.
```

Thumbnail text:

```
THE PHASE IS THE
UNIT OF CONTAINMENT.
```

## Image Prompts 11 & 12 — 9:16 Shorts Backgrounds

```
35 phases.
Not one big PR.
```

```
Gates catch what AI didn't do.
Phases give them somewhere to fire.
```

---

# Editing Notes

## Visual rhythm

Same claim → receipt → claim → receipt rhythm as Ep 4. The phase-shape diagram (1:00–1:30) is the only segment where the visual is conceptual rather than evidential. Everything else points at real files, real tracker entries, or real terminal output.

Recommended pattern:

- Start on the implementation tracker — phase boundary visible before any text.
- Show the title card *after* the cold open beat.
- The four-part phase-shape diagram gets ~30 seconds — give viewers time to read each label.
- The Phase 5d walkthrough should feel like a tracker entry, not a marketing tour.
- The "three things" cards at 2:15–2:40 each get ~7 seconds — short enough to feel like a checklist, long enough to read. **The recovery card holds an extra ~2 seconds while the Phase 10 B-roll cuts in.**
- The lesson card holds for at least 4 seconds.

## The Phase 10 callback (new in v2)

When the voiceover at 2:15 hits *"rollback was one file, not one branch,"* the visual cuts away from the three-things card for ~2 seconds to Ep 4's recovery footage. The cut should land on the moment `wc -l` reads `144 src/visualizer/views/pointer.py` — a frame the viewer recognizes from Ep 4 as the recovery confirmation. Then back to the three-things card for the "AI didn't make the discipline necessary" line.

This callback does three things at once: grounds an abstract claim in concrete evidence, builds series-spanning continuity, and confirms that the recovery wasn't theoretical. No new shoot required.

## What to avoid

- "Agile sprint" framing. The phase is not a sprint. It has stricter exit gates and a smaller scope.
- Implying the thirty-five-phase count is universal. It's what this project needed.
- Showing your face during the phase-shape diagram. The structure is the visual.
- Music swelling on "thirty-five phases." Let the receipts carry it.
- Holding the Phase 10 B-roll too long. Two seconds. Not four.

---

# YouTube Description Draft

```text
Gates catch what AI didn't do. Phases give the gates somewhere to fire.

That's the central lesson from Episode 5 of my Visual Learning 
Sorting case study.

When people talk about AI productivity, they usually ask: how do I 
get it to write more code, faster? That question has a place. But 
it skips something.

The better question: where does each unit of work stop and prove 
itself?

For this project, the answer was the phase. Thirty-five of them, 
across seven days. Each one had the same four parts:

→ An entry context — the specs, decisions, and prior phases the 
   work depends on.
→ A scoped output — usually one file, sometimes two. Always 
   bounded.
→ A set of exit gates — parse, tests, ruff, pyright.
→ A devlog entry — what was worked on, what the gates returned, 
   what got corrected, what was decided, and what the next phase 
   can rely on.

Episode 4 explained why those gates matter. Episode 5 explains why 
the phase boundary is the only place they can fire.

Phase 5d is the clean example. Heap Sort tree layout. One file. 
Thirty-eight unit tests. Zero corrections. The phase opened with 
its entry context locked, the AI wrote one bounded change, the 
gates fired before the phase closed, and the devlog recorded what 
the next phase could rely on.

That shape, thirty-five times.

The phase boundary did three things one big PR couldn't have:

Containment — if the AI broke something, it broke it inside one 
phase.
Audit — every phase had a devlog entry that explains the why, 
not just the what.
Recovery — when a phase failed, the rollback was one file, not 
one branch. That's how the Phase 10 truncations from Episode 4 
got reversed in seconds.

None of these are AI features. They're discipline features. AI 
just made them more visible.

A phase isn't a unit of scheduling. It's a unit of containment.

📂 Project repository: https://github.com/StevenJUlbrich/Visual_Learning_Sorting
📖 Project wiki: https://github.com/StevenJUlbrich/Visual_Learning_Sorting/wiki

⏱️ Chapters:
0:00 The failure that doesn't look like one
0:18 Bridge from Episode 4
0:38 Wrong question / better question
0:57 The phase shape
1:35 One real phase: Phase 5d
2:30  Why the boundary matters
3:22 The lesson
3:48 What's next

If you've been thinking about how to scope work for AI tools, 
I'd be curious what your team treats as "one unit" — a feature, 
a file, a PR, a phase.

#AIAssistedDevelopment #AIWorkflow #SoftwareEngineering
```

---

# LinkedIn Post Draft

```text
Gates catch what AI didn't do. Phases give the gates somewhere to fire.

That's the central lesson from Episode 5 of my Visual Learning 
Sorting case study.

When people talk about AI productivity, they usually ask: how 
do I get it to write more code, faster?

That question has a place. But it skips something.

The better question: where does each unit of work stop and prove 
itself?

For this project, the answer was the phase. Thirty-five of them, 
across seven days. Each phase had the same four parts:

1. An entry context — specs, decisions, prior phases.
2. A scoped output — usually one file.
3. A set of exit gates — parse, tests, ruff, pyright.
4. A devlog entry with what was worked on, what the gates 
   returned, what got corrected, what was decided, and what 
   the next phase can rely on.

Same shape, thirty-five times.

Phase 5d is the clean example. Heap Sort tree layout. One file. 
Thirty-eight unit tests. Zero corrections. Entry context locked, 
one bounded change, gates fired, devlog recorded.

What the phase boundary bought, that one big PR wouldn't have:

→ Containment. If the AI broke something, it broke it inside 
   one phase. Diagnosable scope.
→ Audit. Every phase had a devlog entry. The reasoning was 
   captured at the time, not reconstructed later.
→ Recovery. Rollback was one file, not one branch. That's how 
   the Phase 10 truncations from Episode 4 got reversed in 
   seconds.

None of these are AI features. They're discipline features. AI 
just made them more visible.

A phase isn't a unit of scheduling. It's a unit of containment.

Episode 5 is up: https://youtu.be/Od_z8fPdSz8

If you've been scoping work for AI tools, what does your team 
treat as "one unit" — a feature, a file, a PR, or something else?

A phase isn't a unit of scheduling. It's a unit of containment.

📂 Project repository: https://github.com/StevenJUlbrich/Visual_Learning_Sorting
📖 Project wiki: https://github.com/StevenJUlbrich/Visual_Learning_Sorting/wiki


#AIAssistedDevelopment #AIWorkflow #SoftwareEngineering
```

---

# Final Episode 5 Summary

Episode 5 should leave the viewer with one idea:

> **The phase boundary is where AI work proves itself. Without it, there's nowhere for a gate to fire.**

The practical lesson:

> **Slice the work into bounded units, each with an entry context, a scoped output, exit gates, and a devlog entry that names what the next phase can rely on. That structure is what makes AI-assisted development auditable.**

The professional credibility message:

> **AI didn't make the discipline necessary. It made the discipline visible. The phase is the engineering primitive that holds the discipline together.**

---

# Open decisions for v3 (if needed)

v2 addresses every item from the v1 critique. Likely v3 changes — if any — would come from a second editorial pass and would target:

1. **Title lock-in.** *Where the Gates Run* and *35 Phases. Not One Big PR.* are both candidates. v3 picks one and updates everywhere it appears.
2. **Phase count verification.** If the project's real phase count differs from "thirty-five," update every reference.
3. **B-roll timing.** The 2-second Phase 10 callback may want to be 1.5 or 2.5 seconds depending on the cut. Adjust after editing-pass timings are real.
4. **Ep 6 direction confirmation.** Currently committed to prompt + contracts. v3 only revisits if the back-half direction changes.
