Here's the integrated final script for Episode 3, with the three edits applied to the revised structure.

---

# Episode 3 — Why I Did Not Let One AI Model Own the Project

**Working title:** *Why I Did Not Let One AI Model Own the Project*
**Alternate title:** *One AI Model Should Not Own Every Role*
**Target runtime:** 4:00–4:30 (realistic for the content density)
**Central lesson:** Do not ask one AI model to own every role in the software process.
**Shareable line:** *"The memory was not in the AI. The memory was in the process."*

---

## Script

### 0:00–0:15 — Cold open

**Visual:** Dark technical background. Four role cards appear one at a time over ~5 seconds: **Spec Reviewer**, **Architect**, **Builder**, **Reviewer**. Smaller secondary labels appear below each: model names or descriptions. No logos.

After the fourth card appears, they arrange into a horizontal flow shape. Hold briefly.

**Voiceover:**

> "I used four different AI models on this project."
>
> *[Beat — full second of silence]*
>
> "Not as a gimmick. Because specification, implementation, and review are different jobs — and one model shouldn't own all of them."

**On-screen text:**

```
One project.
Multiple AI roles.
Human-owned decisions.
```

---

### 0:15–0:35 — Bridge from Episode 2

**Visual:** Cut to Image 2 (the broken green completion screenshot from Episode 2). Hold briefly, then quick cut to a single overlay card showing the Episode 2 stats.

**Voiceover:**

> "Episode 2 showed the acceptance campaign. Twenty-seven acceptance tests. Ten visual issues reviewed. Nine confirmed visual defects. Zero algorithm bugs."
>
> "The tests said the arrays were sorted. The screen was still misleading the viewer."
>
> "Episode 3 is about the workflow that made those bugs findable instead of mysterious."

**On-screen text:**

```
27 acceptance tests
10 visual issues reviewed
9 confirmed defects
0 algorithm bugs
```

---

### 0:35–1:00 — The right question

**Visual:** Split card.

Left side, dimmer:

```
Common question:
Which model is best?
```

Right side, brighter, with orange accent:

```
Better question:
Which model for which role?
```

**Voiceover:**

> "When people compare AI coding tools, they often ask: which model is best?"
>
> "That question has a place. But it's incomplete."
>
> "A software project isn't one task. It's specification, implementation, review, and acceptance — and each of those wants a different kind of judgment."

**On-screen text:**

```
Model ranking is not workflow design.
```

---

### 1:00–1:45 — Stage 1: Specification with peer review

**Visual:** Three-stage workflow diagram appears. Highlight Stage 1, dim Stages 2 and 3.

```
STAGE 1 — SPECIFICATION
Design docs → peer review → locked decisions
```

Cut to quick clips of:

- `docs/design_docs/` folder listing
- `wiki/Spec-First-Methodology.md`
- `docs/AI_Conversations/` directory (if available)

**Voiceover:**

> "Stage one was specification."
>
> "Before any implementation, the project had design documents, locked decisions, and review passes looking for gaps."
>
> "I didn't trust one model to create a perfect spec. Different models have different blind spots, so the specification was reviewed from multiple angles before code generation started."
>
> "That matters because a bug in a spec is more dangerous than a bug in one file. A bad assumption in the spec can spread into the code, the tests, and the acceptance criteria."

**On-screen text (first card):**

```
Specs make misalignment detectable.
```

**On-screen text (second card, appearing briefly):**

```
Spec review looked for:
• gaps
• contradictions
• ambiguity
• untested assumptions
```

---

### 1:45–2:35 — Stage 2: Implementation with role separation

**Visual:** Return to workflow diagram. Highlight Stage 2.

```
STAGE 2 — IMPLEMENTATION
Architect prompt → builder executes → gates run
```

Cut to quick clips of:

- A prompt file from `docs/prompts/`
- The implementation tracker
- Test command output
- Model assignment table from `wiki/Development-Timeline.md`

**Voiceover:**

> "Stage two was implementation."
>
> "One role acted as architect: reading the specs, designing the prompt, defining the files, and deciding what gates had to pass."
>
> "Another role acted as builder: making the code change and running the checks."
>
> "That split matters."
>
> "When the same agent owns both judgment and execution, it can explain away its own assumptions. When the architect and builder roles are separated, misalignment has somewhere to show up."
>
> "The model choice was not based on hype. It was based on decision density. Mechanical tasks went to a faster builder. Multi-constraint work went to the stronger reasoning model."

**On-screen text (first card):**

```
Architect: judgment
Builder: execution
Gates: evidence
```

**On-screen text (second card):**

```
Match the model to the decision density,
not the code volume.
```

---

### 2:35–3:20 — Stage 3: Review and audit trail

**Visual:** Return to workflow diagram. Highlight Stage 3, then cut to duplicate-value evidence.

```
STAGE 3 — REVIEW
Result → spec comparison → devlog → next phase
```

Cut to:

- The duplicate-value case study from `wiki/Misalignment-Case-Studies.md`
- Relevant devlog section
- Fixed app clip showing duplicate values now rendering correctly

**Voiceover:**

> "Stage three was review."
>
> "The result came back against the spec, the tests, and the devlog trail."
>
> "This didn't prevent every defect. Episode 2 proved that. But it made defects diagnosable."
>
> "The duplicate-value bug is the clean example."
>
> "The algorithms sorted correctly. The screen was wrong. Acceptance testing found the symptom."
>
> "The audit trail made the cause easier to isolate: this wasn't a sorting problem. It was a sprite identity problem."
>
> *[Beat]*
>
> "The memory was not in the AI. The memory was in the process."

**On-screen text (first card):**

```
Algorithm correct.
Visual explanation wrong.
```

**On-screen text (second card — the shareable line, hold 4-5 seconds):**

```
The memory was not in the AI.
The memory was in the process.
```

---

### 3:20–3:50 — The lesson

**Visual:** Full workflow diagram with all three stages visible. Feedback arrow loops back to implementation. Hold briefly, then transition to a clean lesson card.

```
Specification → Implementation → Review → Next Phase
                                       ↑
                                       └── feedback
```

**Voiceover:**

> "That's the real lesson."
>
> "Do not ask one AI model to be product owner, architect, implementer, reviewer, and QA."
>
> "Use AI inside a workflow where roles are separated, evidence is preserved, and the human still owns the decision."
>
> *[Beat]*
>
> "One model can generate code. A role-separated workflow decides whether that code belongs."

**On-screen text:**

```
AI can generate.
The workflow governs.
The human owns the decision.
```

---

### 3:50–4:10 — Episode 4 hook + outro

**Visual:** Quick cut to a file diff or terminal showing a truncated file. Could also be the devlog section where the truncation incidents are documented.

**Voiceover:**

> "But this workflow still couldn't prevent every failure."
>
> "Four times during this project, the AI silently truncated the files it was editing. Sometimes the truncation removed the tests that would have caught the truncation."
>
> "Episode 4 is about that failure mode."
>
> *[Beat]*
>
> "If you're working with AI tools and you're tired of the 'which model is best' conversation, subscribe."

**On-screen text:**

```
Next: When AI fails quietly.
4 truncation incidents.
0 caught by the AI.
```

---

## Total Runtime

~4:10 (realistic estimate, may stretch to 4:20-4:30 during edit)

---

## Voiceover Delivery Notes

### Overall tone

Same documentary-narrator approach as Episodes 1 and 2. Episode 3 is the most conceptually dense of the three so far — slow your pace slightly compared to Episode 2. Give viewers time to process the workflow diagram.

### Key delivery moments

**0:00 opening:** "I used four different AI models on this project." — flat, declarative, no enthusiasm. The full second of silence before "Not as a gimmick" is non-negotiable. That silence is the hook.

**0:35 the pivot:** "That question has a place. But it's incomplete." — quiet, peer-respectful. You're not dunking on the conversation; you're refining it.

**1:45 architect/builder split:** "That split matters." — short sentence, full stop, slight pause before continuing. This is the structural insight of the episode.

**2:35 the duplicate-value reveal:** Drop your pace noticeably. The viewer needs to feel that "acceptance testing found the symptom, the audit trail made the cause diagnosable" is *the answer to a real engineering problem*, not just methodology talk.

**3:00 the shareable line:** "The memory was not in the AI. The memory was in the process." — slowest delivery in the episode. Treat each sentence as its own beat. This is the line built for screenshots.

**3:20 the lesson:** "Do not ask one AI model to be product owner, architect, implementer, reviewer, and QA." — slight emphasis on each role as you list it. The accumulation is the point.

**3:50 Episode 4 hook:** "Four times during this project, the AI silently truncated the files it was editing." — slight shift to conspiratorial tone. You're letting the viewer in on something.

---

## What Needs Verification Before Recording

Three items from the revision's verification list, plus one I'd add:

**1. Exact model names** — If you can verify the specific versions (ChatGPT 5.4, Claude 4.7, Gemini 3.1, Claude Opus), use them. If not, say "ChatGPT, Claude, Gemini, and Claude Code models" in the cold open. The number "four" stays either way.

**2. Phase 10c attribution wording** — The script uses *"acceptance testing found the symptom; the audit trail made the cause diagnosable."* This is the safe phrasing. Don't claim the AI caught it on review unless you have specific evidence in the devlog supporting that.

**3. March 21 spec-review chain** — If you mention the spec review explicitly, make clear that the *nine traps* from March are a different category than Episode 2's *nine confirmed visual defects*. The script as written avoids citing the number "nine" for the spec traps to prevent confusion — it just says "review passes looking for gaps." That's deliberate.

**4. The four file truncation incidents** — The Episode 4 hook says "four times." Confirm this against the Phase 10 devlog. If it's three or five, change the number. The specificity is the credibility.

---

## YouTube Description

```
I used four different AI models on this project. Not as a gimmick. 
Because specification, implementation, and review are different jobs 
— and one model shouldn't own all of them.

This is Episode 3 of a six-part series on AI-assisted development. 
Episode 2 showed that 339 unit tests passed while acceptance testing 
still found nine confirmed visual defects. Episode 3 explains the 
workflow that made those defects findable instead of mysterious.

In this episode:
- Why specification, implementation, and review are different jobs
- Why one AI model shouldn't own the whole software process
- How role separation made the project auditable
- Why acceptance testing found the symptom, but the audit trail made 
  the cause diagnosable
- Why the human still owns the decision loop

📂 Project repository: https://github.com/StevenJUlbrich/Visual_Learning_Sorting
📖 Project wiki: https://github.com/StevenJUlbrich/Visual_Learning_Sorting/wiki

⏱️ Chapters:
0:00 Four AI models, one project
0:15 What Episode 2 showed
0:35 The better question
1:00 Stage 1 — Specification with peer review
1:45 Stage 2 — Implementation with role separation
2:35 Stage 3 — Review and audit trail
3:20 The lesson
3:50 What's next

🎯 Coming up:
Episode 4 — When AI fails quietly. Four file truncation incidents 
this workflow caught only because the gates existed.

Shareable line:
The memory was not in the AI. The memory was in the process.

Subscribe if you're working with AI tools and you're tired of the 
"which model is best" conversation.

#AIAssistedDevelopment #AIWorkflow #SoftwareEngineering #ClaudeCode #SpecDrivenDevelopment
```

---

## LinkedIn Post

```
Do not ask one AI model to own every role in the software process.

That's the central lesson from Episode 3 of my Visual Learning 
Sorting case study.

When people compare AI coding tools, they often ask: which model is 
best? That question has a place. But it's incomplete.

The better question is: which model is best for which role?

A software project is not one task. It includes specification, 
architecture, implementation, review, testing, acceptance, and 
maintenance. When one AI model owns too many of those roles, its 
assumptions become invisible.

For this project, the workflow separated the roles:

→ Specification and review defined what the system had to do.
→ Architecture and prompt design translated that into bounded 
   implementation work.
→ Builder models executed scoped changes and ran gates.
→ Review and acceptance compared the result against the intended 
   behavior.

Episode 2 showed the practical reason this mattered: 339 unit tests 
passed, but acceptance testing still found nine confirmed visual 
defects.

The algorithms sorted correctly. The screen was wrong.

The workflow didn't magically prevent every bug. That's not the claim.

The workflow made the bugs diagnosable.

The duplicate-value bug is the clean example. Acceptance testing 
found the symptom. The audit trail made the cause clear: it wasn't 
a sorting problem. It was a sprite identity problem.

The memory was not in the AI.
The memory was in the process.

One model can generate code. A role-separated workflow decides 
whether that code belongs.

Episode 3 is up: [YouTube link]

If you're working with AI tools and you're tired of the "which model 
is best" conversation, I'd be curious how your team handles role 
separation.

#AIAssistedDevelopment #AIWorkflow #SoftwareEngineering
```

---

## What Changed From the Revision

For your records, here are the specific edits applied:

| Section | Original (revision) | Edited version |
|---------|---------------------|----------------|
| 0:00 cold open | "I used multiple AI models on this project. Not as a gimmick..." | "I used four different AI models on this project. Not as a gimmick..." — restored specificity |
| 0:35 pivot | "Most conversations about AI coding ask, 'Which model is best?' That is the wrong question." | "When people compare AI coding tools, they often ask: which model is best? That question has a place. But it's incomplete." — peer-respectful tone |
| 3:50 Episode 4 hook | "Sometimes the AI did not misunderstand the spec. It silently damaged the files." | "Four times during this project, the AI silently truncated the files it was editing. Sometimes the truncation removed the tests that would have caught the truncation." — added specificity and the inversion line |

Everything else from the revised approach is preserved, including the central "role separation" reframe, the Phase 10c attribution wording, the bug count consistency, and the "memory in the process" shareable line.

---

Want me to draft the title card image prompt for Episode 3, or move on to Episode 4 planning while this is fresh?