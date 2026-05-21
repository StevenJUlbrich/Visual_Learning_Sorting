# Episode 2 — 339 Tests Passed. The Animation Was Still Broken.

**Runtime:** ~3:25
**Video:** https://youtu.be/rawDZjxb4Vk
**Series:** Visual Learning Sorting — AI-Assisted Development Case Study

---

## The Pitch

Episode 1 ended on a bug that 339 unit tests couldn't catch. Episode 2 explains how to find bugs like that — and why unit tests aren't enough when the product is a visual experience.

---

## The Core Claim

When AI generates code, it satisfies the tests you wrote. It does not automatically discover the tests you forgot.

That responsibility stays with the human.

---

## What the Episode Argues

**1. Correct output is not the same as correct behavior.**

A unit test can tell you the array is sorted. It can tell you no values were lost. It can tell you duplicates are preserved. But it cannot tell you whether the viewer saw the right thing happen.

The visual layer is a separate state machine from the algorithm layer. When the algorithm advances but the screen still shows the previous truth, the unit test passes and the product is wrong.

**2. Unit tests check the output. Acceptance tests check the experience.**

The fix wasn't writing more unit tests. The fix was writing a different kind of test entirely — 27 acceptance tests that asked whether the behavior was believable, not whether the function returned the right value.

Those acceptance tests found nine confirmed defects in a project that already had 339 passing unit tests.

**3. AI satisfies the test you wrote. It does not find the test you forgot.**

This is the central thesis of the episode. AI is excellent at producing code that satisfies explicit specifications. It is not automatically good at discovering the specifications you didn't think to write. The human stays responsible for asking *what could go wrong that the tests don't check?*

**4. The definition of "done" has to change.**

By the end of the acceptance test campaign, a phase was no longer complete when the function returned the right output. It was complete when the viewer could follow the state change without being misled.

---

## The Four Bug Categories

The nine defects grouped into four categories. None of them were algorithm bugs.

| Category | Description | Example |
|----------|-------------|---------|
| **Identity bugs** | The right value moved, but the wrong object appeared to move | Duplicate values broke sprite tracking because the code identified sprites by numeric value instead of permanent ID |
| **Phase-state bugs** | The algorithm advanced, but the screen still showed the previous truth | Heap Sort's tree collapsed mid-build because a sift-down swap looked exactly like an extraction swap |
| **Layout bugs** | Visual elements crossed panel boundaries | The "heap boundary" label rendered in the Insertion Sort panel instead of the Heap Sort panel |
| **Lifecycle bugs** | Labels and lines that should have disappeared when the sort completed didn't | The EXTRACTION label persisted on screens showing already-completed sorts |

---

## The Receipts

| Metric | Value |
|--------|-------|
| Unit tests in suite | 339 (at time of campaign) |
| Acceptance tests written | 27 |
| Visual issues reviewed | 10 |
| Confirmed defects found | 9 |
| Algorithm bugs found | 0 |
| Behavior bugs found | 9 |

---

## The Cold Open

The episode opens on the green completion screenshot from Phase 10c — four arrays sorted, stats frozen, green completion state across the board. Every test passed.

Then four annotations fire in sequence:

- A row is misaligned
- A label is in the wrong panel
- A boundary line is still visible after completion
- A phase label says the algorithm is still extracting — on an array that's already done

The screenshot was clean by every code-level test. Every visual element was broken.

---

## Structure

| Segment | Time | Content |
|---------|------|---------|
| Cold open | 0:00–0:12 | "The screen says this is success." 339/339 ✓ Visual ✗ |
| Bug reveal | 0:12–0:25 | Four callouts fire on the broken screenshot |
| Title card | 0:25–0:28 | Episode title flash |
| Bridge + thesis | 0:28–0:55 | "AI satisfies the test you wrote, not the test you forgot" |
| Why unit tests missed it | 0:55–1:25 | Correct output ≠ correct behavior |
| Acceptance test campaign | 1:25–2:00 | 27 tests, 9 defects |
| Four bug categories | 2:00–2:40 | Identity, Phase-state, Layout, Lifecycle |
| Changed definition of done | 2:40–3:05 | Old: array sorted / New: behavior understandable |
| Episode 3 hook + outro | 3:05–3:25 | The 35-phase build plan |

---

## Key Lines

> "The screen says this is success. Four arrays sorted. Green completion state. Stats frozen. All 339 tests passed. Now look closer."

> "AI is very good at satisfying the test you wrote. It is not automatically good at discovering the test you forgot. That responsibility stays with the human."

> "A unit test can tell you the array is sorted. It can tell you no values were lost. It can tell you duplicates are preserved. But it cannot tell you whether the viewer saw the right thing happen."

> "Twenty-seven acceptance tests. Ten visual issues. Nine confirmed defects. None of them were algorithm bugs."

> "By the end, the definition of done had changed. A phase was no longer complete when the function returned the right output. It was complete when the viewer could follow the state change without being misled."

---

## The Shareable Line

> "AI satisfies the test you wrote. It does not find the test you forgot."

This is the line built for screenshots, quote tweets, and LinkedIn shares. It's the entire episode compressed into ten words.

---

## What It Sets Up

Episode 3 — *The 35-phase build plan. Four AI models, and the rules that kept the project from drifting.*

The phase structure that made the acceptance test campaign possible. How phase boundaries created the conditions for AI-assisted development to be auditable.
