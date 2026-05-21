# Episode 4 — When AI Fails Quietly (v4 — numbers synced to recording sandbox)

**Series:** Visual Learning Sorting — AI-Assisted Development Case Study
**Episode title card:** *Episode 4 — When AI Fails Quietly*
**YouTube public title:** *The AI Said Done. The File Was Half Gone.*
**Target runtime:** 3:15–3:25 (hard ceiling 3:35)
**Central lesson:** **Silent AI failures look like success until an independent check proves otherwise.**
**Shareable line:** *"The dangerous AI failure isn't the wrong answer. It's the missing one."*

---

## What changed from v3 → v4

v3 carried over the investigation agent's overstated numbers (73 lines lost, "two whole methods gone"). The recording sandbox produced the honest figures. v4 swaps every quoted number to what will actually appear on screen during the terminal recording.

| Field | v3 | v4 (verified against `recording/sandbox.py`) |
|---|---|---|
| Truncated file size | 144 lines | **118 lines** |
| Expected size | 217 lines | **145 lines** (post-edit intent) |
| Lines lost | 73 | **26** (wc -l delta), 27 by git diff stat |
| Cut at line | 144 | **119** |
| What disappeared | "tail of `_draw_jmin_pointer`, full `draw()` method, full `reset()` method" | **tail of `_draw_jmin_pointer`** (the file has no separate `draw()` or `reset()` methods — that claim in v3 was wrong) |
| Last visible line | `label_rect = lab` | **`label_rect =`** (no value — produces a real `SyntaxError`; the `lab` text from the case study isn't a parse failure) |
| Parse error | `SyntaxError: unexpected EOF while parsing` | **`SyntaxError: invalid syntax (line 119)`** (real, reproduced) |

Structural shape, lesson, trichotomy, and shareable line are unchanged. The edits are localized to the 0:00, 0:18, 1:00, and 2:10 segments where numbers are quoted, plus the verification checklist and image-prompt overlay text.

---

## Episode Purpose

Episode 3 ended on a specific hook: four file truncation incidents the AI didn't notice. Episode 4 pays that off — but it pays it off as a *category* of failure, not as a war story.

The category: AI failures aren't always wrong answers. Sometimes the AI produces *less than it claimed* and reports success. The file is shorter. A function is gone. The diff has deletions in places nothing should have been deleted. The AI's self-report says complete.

The reason this matters is that the AI's self-report is the bug. You can't catch it by asking the AI to double-check — the AI has already checked, in its own view, and reported success. The only thing that catches a silent failure is something independent of the AI's claim.

In this project, the realization came incident-by-incident. The first truncation taught me which gate was missing. By the fourth, the checks had tightened to where damage could no longer ship.

---

## Core Claim

Two categories of AI failure in software work:

1. **Loud failures** — the AI produced something wrong. Visible in the diff. Review catches them.
2. **Quiet failures** — the AI produced *less than it claimed*. The success message is wrong. Only an independent check catches them.

Handling quiet failures isn't a matter of better prompting or smarter models. It's a matter of having checks that run **outside the AI's self-report**:

- Does the file still parse?
- Does the full test suite still pass?
- Did the file shrink without a stated reason?
- Does the raw diff show deletions outside the stated scope?

None of those depend on the AI noticing anything. That's the entire point.

---

## Shareable Lines

**Primary:**

> **"The dangerous AI failure isn't the wrong answer. It's the missing one."**

**Secondary:**

> **"Sometimes the AI didn't misunderstand. It just stopped writing."**

> **"A self-check is not an independent check. It's the same system grading itself."**

> **"Not the AI's summary of the diff. The diff."**

> **"Review catches bad logic. Gates catch broken structure. The raw diff catches missing work."**

---

## Tone

Investigative documentary. Postmortem voice, not panic voice. Process discipline, not "AI is broken."

---

## Episode Structure

Total runtime: **~3:15–3:25**.

| Segment | Time | Purpose |
|---|---:|---|
| Cold open | 0:00–0:18 | Real terminal: `wc -l` shows 118, AST parse fails at line 119. |
| Bridge from Ep 3 | 0:18–0:35 | Variant C: gates evolved during the build. |
| Loud vs. quiet failures | 0:35–1:00 | Establish the category distinction. |
| The Phase 10e incident | 1:00–1:45 | One real case, walked through end-to-end. |
| Why self-check isn't a gate | 1:45–2:10 | The AI's self-report is the bug. |
| The checks that caught them | 2:10–2:42 | Parse, full suite, diff stat, raw diff. |
| The lesson | 2:42–3:05 | Trichotomy + shareable line. |
| Episode 5 hook + outro | 3:05–3:20 | Phase boundaries as the answer. |

---

# Full Script Draft

## 0:00–0:18 — Cold open

**Visual:** Dark terminal window. Two commands run in sequence (recorded against `recording/sandbox/`):

```
$ wc -l src/visualizer/views/pointer.py
118 src/visualizer/views/pointer.py

$ python3 -c "import ast; ast.parse(open('src/visualizer/views/pointer.py').read())"
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/usr/lib/python3.10/ast.py", line 50, in parse
    return compile(source, filename, mode, flags,
  File "<unknown>", line 119
    label_rect =
                ^
SyntaxError: invalid syntax
```

Hold on the `SyntaxError` line for ~2 seconds.

**Voiceover:**

> "This is the AI failure mode that doesn't look like a failure."
>
> *[Beat]*
>
> "The AI didn't get the answer wrong. It just stopped writing — somewhere around line one nineteen — and reported the edit complete."

**On-screen text (overlay, not the terminal — terminal stays raw):**

```
The edit reported success.
The file was 26 lines short.
```

> **Production note:** Generated by `python recording/sandbox.py truncate`. The case study text in `wiki/Misalignment-Case-Studies.md` describes the cut as `label_rect = lab`, but that exact partial line parses cleanly in Python. The sandbox uses `label_rect =` (no right-hand side) which produces a real `SyntaxError`. If you want the on-screen text to read `label_rect = lab` for case-study continuity, stylize in post — but the parse-failure recording must be the version without `lab`.

---

## 0:18–0:35 — Bridge from Episode 3

**Visual:** Cut to the Episode 3 outro card ("4 truncation incidents. 0 caught by the AI."). Hold a beat, then transition forward.

**Voiceover (Variant C — gates evolved during the build):**

> "Last episode I closed on a category: file truncations the AI didn't catch."
>
> "There were four of them. The first one taught me which check was missing. By the fourth, the gates were tight enough that the damage couldn't ship."

**On-screen text:**

```
4 truncation incidents.
0 caught by the AI.
The gates got tighter incident by incident.
```

> **Sources:** Count verified in three records — `docs/devlog/phase_10.md` line 269; `wiki/Development-Timeline.md` lines 79–90; `wiki/Misalignment-Case-Studies.md` line 98. "Gates evolved" framing supported by `wiki/Misalignment-Case-Studies.md` line 112 ("AST parse was added as a standard gate for all subsequent phases").

---

## 0:35–1:03 — Loud vs. quiet failures

**Visual:** Split card.

Left side, dimmer:

```
LOUD FAILURES
The AI produced something wrong.
Review catches them.
```

Right side, brighter, orange accent:

```
QUIET FAILURES
The AI produced less than it claimed.
Only independent checks catch them.
```

**Voiceover:**

> "There are two categories of AI failure."
>
> "Loud failures are wrong answers. You can usually see them in review — they're in the diff."
>
> "Quiet failures are missing answers. A function disappears. A test file ends halfway through. The success message says done. The file says otherwise."

**On-screen text (final card):**

```
A wrong answer shows up in review.
A missing answer shows up in the diff —
if you actually check it.
```

---

## 1:03–1:45 — The Phase 10e incident

**Visual:** Walk through Phase 10e end-to-end. On-screen sequence (all captured against `recording/sandbox/`):

1. **The prompt summary** (overlay card):
   ```
   Phase 10e — Selection Sort i-pointer spacing.
   Split ARROW_GAP into I_ARROW_GAP (12px) and JMIN_ARROW_GAP (5px).
   Update i_arrow_y() to use the larger gap.
   ~3 constants, 2 functions, ~5 test assertions.
   ```
2. **The AI's success indicator** (stylized — actual transcript not captured): a small "Edit applied" badge.
3. **The first independent check** (real): the terminal from the cold open — `wc -l` showing 118, AST parse failing at line 119.
4. **What was lost** (overlay): the tail of `_draw_jmin_pointer`, ending where the writing stopped mid-statement.
5. **The recovery** (terminal): `git show HEAD~1:src/visualizer/views/pointer.py > src/visualizer/views/pointer.py`, then `wc -l` reading 144 and a clean `ast.parse` returning successfully.

**Voiceover:**

> "Here's the cleanest example."
>
> "Phase ten-e. A small refactor on the Selection Sort pointer code. Three constants. Two functions. Five test assertions. Bounded scope. Locked spec."
>
> "The AI returned a success message."
>
> "The next independent check disagreed. The file had been a hundred and forty-four lines. It was now a hundred and eighteen. Twenty-six lines short — the tail of one method, plus the line where the writing stopped."
>
> "Abstract syntax tree (AST) parse caught it. That gate had been added one phase earlier, after the first truncation. This was the first incident it caught."
>
> *[Beat]*
>
> "The AI reported success on an edit that left the file unable to compile."

**On-screen text:**

```
"Edit applied."
        ↓
26 lines missing.
File no longer parsed.
```

> **Sources:** `docs/devlog/phase_10.md` lines 167–180; `wiki/Misalignment-Case-Studies.md` lines 96–118; `wiki/Development-Timeline.md` line 86. **Sandbox-verified numbers:** baseline 144 → truncated 118 (wc -l), 27 deletions by `git diff --stat`. The "tail of one method" framing is honest — the file has no separate `draw()` or `reset()` methods; `_draw_jmin_pointer` is the last method in the class and its last several lines were lost.

---

## 1:45–2:10 — Why self-check isn't a gate

**Visual:** A flowchart of the AI loop: prompt → edit → self-check → success message. Highlight the **self-check** node and mark it broken.

**Voiceover:**

> "Here's why this matters."
>
> "When the AI's self-report is wrong, asking the AI to double-check is not a gate. It's the same system grading itself."
>
> "Code review can catch a wrong answer. It does not reliably catch a missing one — not unless the reviewer reads the raw diff, line by line, every time."
>
> *[Beat]*
>
> "One of the four truncations reached into the test file itself. The safety net was being damaged during the edit."

**On-screen text:**

```
A self-check is not an independent check.
It's the same system grading itself.
```

> **Source for test-file truncation:** `docs/devlog/phase_10.md` line 207 ("Also restored truncated `pointer.py` and `test_pointer.py` (same truncation pattern as before 10e)"). The truncated test code held pointer formula tests, not tests that would have detected the truncation specifically — so the framing is "safety net being damaged" rather than "tests that would have caught it."

---

## 2:10–2:42 — The checks that caught them

**Visual:** Four check icons appear in sequence. As the voiceover names each, that check lights up.

```
CHECK 1: Parse (does the file still compile?)
CHECK 2: Full test suite (every test, not just touched files)
CHECK 3: Diff stat (line-count delta — sudden drops flagged)
CHECK 4: Raw git diff (read the patch yourself)
```

**Voiceover:**

> "These are the checks that caught or prevented the truncations."
>
> "One — does the file still parse. A truncated Python file is a syntax error. The interpreter notices before any test runs."
>
> "Two — the full test suite, not just the touched files. AI 'success' messages often scope tests to the file the AI edited. That's not enough. Run the whole suite."
>
> "Three — the diff stat. A refactor that removes twenty-seven lines without saying so is suspicious."
>
> "Four — read the raw diff. Not the AI's summary of the diff. The diff."

**On-screen text:**

```
None of these depend on the AI noticing anything.
That's the whole point.
```

> **Sandbox-verified:** the diff-stat line "twenty-seven lines" matches `git diff --stat` output from the truncated sandbox ("1 insertion(+), 27 deletions(-)"). It also pairs with the "twenty-six lines short" wc -l framing at 1:00 — the discrepancy is because git counts the partial rewritten last line as both an insertion and a deletion. If you want a single consistent number across the episode, use "twenty-six" everywhere and rewrite this line to: *"A refactor that removes twenty-six lines without saying so is suspicious."*

---

## 2:42–3:05 — The lesson

**Visual:** Lesson card. Three short rows.

```
REVIEW             →  catches bad logic
GATES              →  catch broken structure
THE RAW DIFF       →  catches missing work
```

Below, large:

```
You need all three.
```

**Voiceover:**

> "That's the lesson."
>
> "Review catches bad logic. Gates catch broken structure. The raw diff catches missing work."
>
> "If your AI workflow only has the first, the quiet failures get through. And by the time you notice, you may not remember what was supposed to be there."
>
> *[Beat — slowest delivery in the episode]*
>
> "The dangerous AI failure isn't the wrong answer. It's the missing one."

**On-screen text (hold 4–5 seconds):**

```
The dangerous AI failure
isn't the wrong answer.
It's the missing one.
```

---

## 3:05–3:20 — Episode 5 hook + outro

**Visual:** Quick cut to the implementation tracker — phases listed with model assignments and exit gates. Highlight a phase boundary.

**Voiceover:**

> "Gates only work if there's somewhere to put them."
>
> "Episode 5 is about phase boundaries — how I sliced the work so every AI edit had a place to stop, test, and prove itself."
>
> *[Beat]*
>
> "If you're tired of AI tools that claim success without earning it, subscribe."

**On-screen text:**

```
Next: How the work was sliced.
Every AI edit had a place to stop and prove itself.
```

---

## Total Runtime

~3:15–3:25 target. Hard ceiling 3:35.

---

## Voiceover Delivery Notes

### Overall tone

Investigative documentary. Slightly slower pace than Episode 3 — you're walking the viewer through evidence, not arguing methodology.

### Key delivery moments

**0:00 cold open:** "This is the AI failure mode that doesn't look like a failure." — flat, declarative. Let it land matter-of-factly.

**0:18 bridge:** Drop pace on "four." "There were four of them." — period. Then: "The first one taught me which check was missing. By the fourth, the gates were tight enough that the damage couldn't ship." That second sentence is what makes the framing honest — it shows learning, not perfection.

**1:00 case study:** Procedural tone. "Here's the cleanest example. Phase ten-e." Each fact gets its own beat. The "one forty-four → one eighteen → twenty-six gone" sequence should land like reading off evidence in a postmortem.

**1:30 the AST parse beat:** "AST parse caught it. That gate had been added one phase earlier, after the first truncation. This was the first incident it caught." — this is the *story* of the episode. The gate that didn't exist before 10d caught its first truncation in 10e. Slow down. Let it land.

**1:45 the structural insight:** "A self-check is not an independent check. It's the same system grading itself." — two beats between sentences. The technical thesis.

**2:10 the checks list:** Steady cadence. Each check is a beat.

**2:42 the lesson:** Slowest delivery in the episode. Three clauses, each a separate breath: *"Review catches bad logic."* — beat — *"Gates catch broken structure."* — beat — *"The raw diff catches missing work."*

**3:05 Episode 5 hook:** Slight forward energy.

---

## Verification Checklist — Status

| # | Item | Status |
|---|---|---|
| 1 | Truncation incident count | **VERIFIED — exactly four source-code truncations during Phase 10.** Sources: `docs/devlog/phase_10.md` line 269; `wiki/Development-Timeline.md` lines 79–90; `wiki/Misalignment-Case-Studies.md` line 98. |
| 2 | Cold open terminal | **VERIFIED and recordable.** `recording/sandbox.py truncate` produces the real `wc -l = 118` and `SyntaxError: invalid syntax (line 119)`. Original raw terminal wasn't captured to git; the sandbox is the reproducible substitute. |
| 3 | Case study specifics | **VERIFIED. Phase 10e, pointer.py.** Task: `ARROW_GAP` split into `I_ARROW_GAP`/`JMIN_ARROW_GAP`. Baseline: 144 lines. Truncated: 118 lines (`wc -l`). Delta: 26 lines by wc -l / 27 deletions by `git diff --stat`. Lost: tail of `_draw_jmin_pointer`. Caught by: AST parse (gate added after 10d). Recovery: `git show HEAD~1:src/visualizer/views/pointer.py > pointer.py`. |
| 4 | "Safety net was damaged" line | **VERIFIED in softer form.** `test_pointer.py` was truncated in 10h, cut mid-call `pointer_set.draw(surf`. The locked-in v4 phrasing is *"One of the truncations reached into the test file itself. The safety net was being damaged during the edit."* The stronger "removed the tests that would have caught the truncation" remains dropped. |
| 5 | The four checks | **VERIFIED.** Across the four incidents: 10d caught by test failure, 10e by AST parse, 10h-pointer by manual diff inspection, 10h-test_pointer by AST parse. All four checks have at least one real receipt. |
| 6 | AI success message wording | **NOT CAPTURED.** Raw AI replies weren't preserved. The visual uses a stylized "Edit applied" badge; the voiceover doesn't quote a literal AI message. No further action required. |
| 7 | Episode 5 direction | Still your call. Outro currently teases phase boundaries; rewrite if you want Ep 5 to go elsewhere. |

---

# Visual Asset Plan

## Required Screen Recordings (against `recording/sandbox/`)

| Clip | What to record | Source |
|---|---|---|
| 01 | Terminal: `wc -l` → 118, then `python3 -c "import ast; ast.parse(...)"` failing with `SyntaxError: invalid syntax (line 119)` on `label_rect =` | Sandbox after `truncate` |
| 02 | `git diff --stat` showing `1 insertion(+), 27 deletions(-)` | Sandbox after `truncate` |
| 03 | Episode 3 outro card ("4 truncation incidents. 0 caught by the AI.") | Already exists |
| 04 | Stylized "Edit applied" badge paired with the broken file | Build in editor |
| 05 | AST parse failure (alternate take of clip 01) | Sandbox after `truncate` |
| 06 | `git show HEAD~1:src/visualizer/views/pointer.py > src/visualizer/views/pointer.py` recovery, then `wc -l` → 144 and `ast.parse` returning cleanly | Sandbox, in-recording |
| 07 | Implementation tracker showing Phase 10 entries with exit gates | `TODO/IMPLEMENTATION_TRACKER.md` |

See `recording/RECORDING_GUIDE.md` for verbatim recording commands.

---

# Image Prompt Pack

Identical to v3 except Image Prompt 3 overlay text is updated to match the recording.

## Image Prompt 1 — Episode 4 Main Title Card

```text
Create a polished technical documentary title card for a software engineering YouTube series. Theme: a quiet, invisible AI failure inside a codebase. The composition should suggest a file that has been silently cut short — a code panel where the bottom half fades or dissolves into the background. Include subtle motifs of a green "success" indicator next to a broken parse warning, suggesting that the AI reported success while the file was damaged. Use a premium documentary style with charcoal background, blueprint grid texture, neon blue interface lines, and an orange warning accent on the truncation boundary. Leave a large clean text-safe area in the center or lower third for overlaying the episode title later. No company logos. No people. Style: serious, investigative, credible — not horror, not sci-fi.
```

Overlay text:

```
EPISODE 4 — WHEN AI FAILS QUIETLY
```

## Image Prompt 2 — Loud vs. Quiet Failure Split Card

```text
Create a clean 16:9 technical explainer graphic split into two sides. Left side: dimmer, labeled "Loud Failures" — show a code panel with a visible red bug marker, an obviously wrong line, and a "review catches it" arrow. Right side: brighter with orange accent, labeled "Quiet Failures" — show a code panel where the bottom half is missing or faded, with a green "success" indicator next to a parse warning, and a "only independent checks catch it" arrow. Dark documentary style, blueprint grid, neon blue lines, orange accent on the right side. No logos. No people.
```

Overlay text:

```
Loud: wrong answer.
Quiet: missing answer.
```

## Image Prompt 3 — The Truncation Visual *(overlay text updated for v4)*

```text
Create a clean technical visualization of a Python source file that has been silently truncated by an AI edit. Show the top portion of the file rendered normally with realistic-looking Python code, then a clear cutoff line around the middle where the code abruptly ends mid-statement on a line that reads "label_rect =" (assignment with no right-hand side). Below the cutoff, fade to dark or show a "file ends here" indicator. To one side, show a small floating "Edit applied" success badge. To the other side, show a red parse warning. The composition should make the contradiction between the success badge and the truncated reality immediately obvious. Dark blueprint software engineering style, neon blue line numbers, orange warning accent on the truncation boundary, charcoal background. No logos.
```

Overlay text:

```
144 lines expected.
118 lines saved.
"Edit applied."
```

## Image Prompt 4 — The Self-Check Trap

```text
Create a clean technical diagram showing an AI feedback loop with a hidden flaw. The loop has four nodes: Prompt → Edit → Self-Check → Success Report. The Self-Check node should be visibly highlighted as broken — a subtle crack, warning indicator, or marker showing that this is where the failure is invisible. Dark blueprint engineering style, neon blue arrows, orange warning on the Self-Check node, charcoal background. No logos, no humans.
```

Overlay text:

```
A self-check is not an independent check.
It's the same system grading itself.
```

## Image Prompt 5 — The Four Independent Checks

```text
Create a clean technical workflow graphic showing four engineering checks arranged in sequence. Each is a labeled rectangular checkpoint. Check 1: "Parse" with a code/syntax icon. Check 2: "Full Test Suite" with a checklist icon. Check 3: "Diff Stat" with a file-size delta indicator. Check 4: "Raw Diff" with a magnifying glass over a diff. Each checkpoint should clearly look independent of the AI — emphasize that these run outside the AI's loop. Dark documentary engineering style, neon blue frames, orange accent on the connecting flow line, charcoal background. No logos. No people.
```

Overlay text:

```
None of these depend on the AI noticing anything.
That's the whole point.
```

## Image Prompt 6 — The Trichotomy Lesson Card

```text
Create a clean final lesson card for a software engineering documentary. Three short labeled rows arranged vertically, each with a small distinct visual motif on the left side. Row 1: "REVIEW" with a code review pane motif, paired with the phrase "catches bad logic." Row 2: "GATES" with an automated checkpoint motif, paired with the phrase "catch broken structure." Row 3: "THE RAW DIFF" with a magnifying glass over a patch, paired with the phrase "catches missing work." Below the three rows, leave a large text-safe area for the conclusion: "You need all three." Premium documentary style, charcoal background, blueprint grid, white typography space, neon blue lines, orange accents on the verbs. No logos. No realistic people. Authoritative and uncluttered.
```

Overlay text:

```
Review catches bad logic.
Gates catch broken structure.
The raw diff catches missing work.
You need all three.
```

## Image Prompt 7 — Shareable Line Card

```text
Create a clean, high-contrast quote card for a technical YouTube series. Background: dark charcoal with subtle blueprint grid texture. Center: a large text-safe area for a single short quote. To one side, a small motif of a truncated code panel with a "success" indicator visible. Premium technical documentary style, neon blue thin lines, orange accent on the motif. No logos. No humans.
```

Overlay text:

```
The dangerous AI failure
isn't the wrong answer.
It's the missing one.
```

## Image Prompt 8 — Episode 5 Teaser

```text
Create a clean technical teaser image representing how a software project is sliced into bounded phases. Show a vertical stack of phase cards, each with a small "exit gate" indicator on the right side. Dark documentary engineering style, blueprint grid, neon blue dividers, orange accents on the gate indicators, charcoal background. No logos. No humans.
```

Overlay text:

```
Next: How the work was sliced.
```

## Image Prompt 9 — YouTube Thumbnail (primary)

```text
Create a high-impact YouTube thumbnail for a technical software engineering video. Theme: an AI silently failing inside a code file. Show a large code panel on one side with its lower half clearly truncated or missing, paired with a bright green "success" indicator that is visibly contradicting the reality. Dark documentary style, blueprint blue and orange accents, bold empty area for large thumbnail text. No logos. No realistic people. Professional, not cartoonish.
```

Thumbnail text:

```
THE AI SAID DONE.
THE FILE WAS HALF GONE.
```

## Image Prompt 10 — YouTube Thumbnail (alternate)

```text
Create a professional YouTube thumbnail for an AI-assisted software engineering case study. Center: a large bold question — "Quiet Failure" — with a visual motif of a truncated file behind it. To one side, a stack of "check" checkpoint icons clearly marked as catching the failure. Dark technical documentary style, neon blue lines, orange highlights, large clean text area. No logos, no humans.
```

Thumbnail text:

```
4 TRUNCATIONS.
0 CAUGHT BY THE AI.
```

## Image Prompts 11 & 12 — 9:16 Shorts Backgrounds

```
The AI said done.
The file was half gone.
```

```
Review. Gates. The raw diff.
You need all three.
```

---

# Editing Notes

Same as v3.

- Claim → receipt → claim → receipt rhythm.
- No title card until after the cold open beat.
- Each check at 2:10–2:42 gets ~5 seconds.
- Shareable line card holds for at least 4 seconds.
- Episode 5 hook lands on the implementation tracker visual.

What to avoid: AI doom imagery, music swelling on the count, naming a specific model on screen, showing your face during the structural insight, calling the AI "lying," a neat one-to-one "four incidents = four gates" claim.

---

# YouTube Description Draft

```text
The dangerous AI failure isn't the wrong answer. It's the missing one.

This is Episode 4 of a six-part series on AI-assisted development.

Episode 3 ended on a specific claim: four times during this build,
the AI silently truncated the files it was editing. Zero of those
incidents were caught by the AI. The first one taught me which
check was missing. By the fourth, the gates were tight enough
that the damage couldn't ship.

Episode 4 walks through the cleanest case — Phase 10e, a small
refactor where the AI's success message claimed completion while
the file had silently shrunk by twenty-six lines. AST parse caught
it one phase after that gate had been added.

In this episode:
- The two categories of AI failure: loud vs. quiet
- Why a self-check is not a gate (it's the same system grading itself)
- One real incident, walked through end-to-end
- The four independent checks: parse, full suite, diff stat, raw diff
- Why review, gates, and the raw diff are three different jobs

📂 Project repository: https://github.com/StevenJUlbrich/Visual_Learning_Sorting
📖 Project wiki: https://github.com/StevenJUlbrich/Visual_Learning_Sorting/wiki

⏱️ Chapters:
0:00 The failure that doesn't look like one
0:18 What Episode 3 left open
0:37 Loud vs. quiet failures
1:02 One real incident — Phase 10e
1:51 Why self-check isn't a gate
2:21 The four independent checks
3:04 The lesson
3:29 What's next

🎯 Coming up:
Episode 5 — How the work was sliced. Phase boundaries: how every
AI edit had a place to stop, test, and prove itself.

Shareable line:
The dangerous AI failure isn't the wrong answer. It's the missing one.

Subscribe if you're tired of AI tools that claim success without
earning it.

#AIAssistedDevelopment #AIWorkflow #SoftwareEngineering #DeveloperTools #SpecDrivenDevelopment
```
```tags
AI-assisted development, spec-driven development, Claude Code,  software engineering methodology, prompt engineering, Python sorting  visualizer, Pygame, sorting algorithms, technical documentation, AI code review, vibe coding alternative, engineering with AI
```

---

# LinkedIn Post Draft

```text
The dangerous AI failure isn't the wrong answer. It's the missing one.

That's the central lesson from Episode 4 of my Visual Learning
Sorting case study.

There are two categories of AI failure in software work.

Loud failures: the AI produced something wrong. A bug. A misread
spec. A hallucinated API. Review catches them, because they're
in the diff.

Quiet failures: the AI produced LESS than it claimed. The file is
shorter. A function is gone. A test was deleted while a refactor
was happening. The success message says done. The file says otherwise.

Quiet failures are dangerous specifically because the AI's self-report
is wrong. Asking the AI to double-check doesn't help — that's the
same system grading itself.

During Phase 10 of this build, the AI silently truncated four
source files. None caught by the AI. The first one taught me
which check was missing.

The cleanest example: Phase 10e. A small refactor on the Selection
Sort pointer code — three constants, two functions, five test
assertions. The AI returned a success message. The next
independent check found the file had shrunk from 144 lines to 118.
Twenty-six lines gone — the tail of one method, plus the partial
line where the writing stopped.

AST parse caught it. That gate had been added one phase earlier,
after the first truncation. This was the first incident it caught.

The checks that caught or prevented the rest:

1. Parse — does the file still compile?
2. Full test suite — every test, not just the touched files.
3. Diff stat — sudden line-count drops flagged for review.
4. Raw git diff — read the patch, not the AI's summary of the patch.

The lesson is a trichotomy, not a binary:

Review catches bad logic.
Gates catch broken structure.
The raw diff catches missing work.

You need all three.

Episode 4 is up: https://youtu.be/2WGUS4qxUdM

If your team uses AI for code edits, I'd be curious which of these
three layers you've found hardest to keep disciplined.

#AIAssistedDevelopment #AIWorkflow #SoftwareEngineering #DeveloperTools
```

---

# Final Episode 4 Summary

Episode 4 should leave the viewer with one idea:

> **Silent AI failures look like success until an independent check proves otherwise.**

The practical lesson:

> **Review catches bad logic. Gates catch broken structure. The raw diff catches missing work. A workflow that relies on the AI noticing its own failures will miss the quiet ones.**

The professional credibility message:

> **Process discipline matters more than model choice. The check that catches a silent failure is the one that doesn't depend on the AI's self-report.**
