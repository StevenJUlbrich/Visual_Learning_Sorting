# Episode 1 — Small App. Serious Engineering.

**Runtime:** 3:09
**Published:** [YouTube link]
**Series:** Visual Learning Sorting — AI-Assisted Development Case Study

---

## The Pitch

A six-part series on what AI-assisted development looks like when you take it seriously. Episode 1 establishes the project, the methodology, and the central tension that drives the rest of the series.

---

## The Core Claim

The project is a real-time sorting algorithm visualizer built with Python and Pygame. Four algorithms race side-by-side in a 2x2 panel grid, driven by operation-weighted timing.

About a thousand lines of code. Seven days of work.

The code wasn't the project. The methodology was.

---

## What the Episode Argues

**1. AI-assisted development is not vibe coding.**

Vibe coding means: ask AI, get code, ship it. The Visual Learning Sorting project is the opposite. AI wrote almost every line of code, but AI did not own a single decision. Specifications, architecture, and acceptance criteria guided the AI implementer the same way they would guide a human team.

**2. Specifications are the engineering artifact.**

Before the first line of code was written, the project produced 15 design documents and 81 locked decisions. These aren't aspirational outlines — they're binding contracts that lock specific behaviors. Each decision resolves a specific ambiguity that AI agents would otherwise resolve on their own (and often resolve incorrectly).

**3. The methodology is what made seven days possible.**

The work broke into 35 implementation phases. Each phase had model assignments, exit gates, and tests. Across all 35 phases, the AI produced 7 corrections — every one was lint formatting. Zero logic errors made it through.

That doesn't happen by accident. It happens because the specs caught the bugs before the code did.

---

## The Receipts

| Metric | Value |
|--------|-------|
| Total development time | 7 days of focused work |
| Lines of code | ~1,000 |
| Design documents | 15 |
| Locked decisions | 81 |
| Implementation phases | 35 |
| Tests in suite | 345 |
| AI corrections across all phases | 7 (all lint formatting) |
| Logic errors that reached production | 0 |

---

## The Hook

Episode 1 ends on a contradiction the rest of the series unpacks.

339 tests passed. The algorithms sorted correctly. But when run with duplicate values in the input array, sprites ended up in the wrong slots on screen. The math was right. The animation was wrong.

That bug lived in the gap between *correct output* and *correct behavior* — and that gap is where AI-assisted development lives or dies.

---

## Structure

| Segment | Time | Content |
|---------|------|---------|
| Cold open | 0:00–0:25 | The app running. Title card. Hook. |
| The real project | 0:25–0:45 | Wiki Home — methodology framing |
| Spec-first methodology | 0:45–1:10 | 15 docs, 81 decisions, AI as implementer |
| Development timeline | 1:10–1:35 | 35 phases, 7 corrections, 0 logic errors |
| When passing tests aren't enough | 1:35–2:15 | The duplicate-values bug reveal |
| Episode 2 setup + outro | 2:15–3:09 | The gap between output and behavior |

---

## Key Lines

> "Four sorting algorithms. One screen. Seven days of work. About a thousand lines of Python. Not because the code was easy — because the code wasn't the project."

> "AI wrote almost every line. But AI did not own a single decision."

> "Fifteen design documents. Eighty-one locked decisions. The human owned the intent. The AI was the implementer. That's why seven days was enough."

> "Across all 35 phases, the AI made seven corrections. Every one was lint formatting. Zero logic errors got through. That doesn't happen by accident. It happens because the specs caught the bugs before the code did."

> "The math was right. The animation was wrong. That bug lived in the gap between correct output and correct behavior — and that gap is where AI-assisted development lives or dies."

---

## Audience

- Developers using AI tools (Claude Code, GitHub Copilot, Cursor)
- Engineering managers evaluating AI-assisted workflows
- Hiring managers screening for AI literacy + engineering discipline
- Anyone skeptical of the "vibe coding" narrative

---

## What It Sets Up

Episode 2 — *339 Tests Passed. The Animation Was Still Broken.*

The acceptance test campaign that found the bugs the unit tests missed. The four categories every visual bug fell into. Why the definition of "done" had to change.
