Here is a comprehensive "Handoff Document." You can save this text into a file named `AI_CONTEXT_HANDOFF.md` or simply keep it in your notes.

When you are ready to resume working on this project—whether tomorrow or next month—you can paste this entire block into a new chat. It will immediately prime the AI with our established architecture, your design choices, and the specific mentor persona we are using.

---

```markdown
# AI Context & Handoff Document
**Project:** Sorting Algorithm Visualizer (Portfolio & Educational Tool)
**Current State:** Ready to begin "Brick 2" (Data Model & Interface)

## 1. AI Persona Instructions
Act as a Senior Technical Mentor & Pair Programmer. Your goal is to help the user build this project "brick by brick" to ensure it is a standout GitHub portfolio piece. Emphasize clean architecture, robust error handling, and cross-language design principles. Do not just write code; explain the *why* behind architectural decisions.

## 2. Project Overview
* **Purpose:** An educational tool to visualize sorting algorithms mechanics, doubling as a high-quality resume reference.
* **Environment:** Built in Ubuntu WSL, targeting Windows 11.
* **Tech Stack:** Python 3.13, `uv` (dependency management), `pygame` (rendering), `ruff` (linting/formatting), `pyright` (strict type checking).

## 3. Key Architectural Decisions (Locked In)
* **Simultaneous Execution:** Algorithms run side-by-side in a 2x2 grid. They use a generator/yield pattern, advancing one atomic operation per global "tick." Faster algorithms will visibly finish early and sit idle while slower ones complete.
* **Strict MVC Pattern:** The codebase is heavily decoupled into `models`, `views`, and `controllers` inside a `src/visualizer/` directory.
* **Modern UI:** Avoiding legacy Pygame looks. Using custom TTF fonts (e.g., Inter, Fira Code), anti-aliasing, and rounded geometry.
* **State Management (The Pure Result Pattern):** We are strictly avoiding standard Python Exception bubbling for logic flow. Instead, we are using a Go/Rust-inspired Pure Result Pattern. Every algorithm tick yields a `SortResult` dataclass that contains either the success state (with array data) or an explicit failure state. Algorithms must explicitly bubble up failures through recursive stacks.

## 4. Completed Milestones
* **Brick 1: Foundation & Setup** is complete. The repository structure is defined, UV commands are logged, and `BRICK_1_FOUNDATION.md` has been generated and saved by the user.

## 5. Immediate Next Steps
* **Start Brick 2: The Data Model & Interface.** * Define the `SortResult` dataclass using Python's `@dataclass`.
* Draft the `BaseSortAlgorithm` abstract base class (ABC) that dictates the required `__init__` and `sort_generator` methods for Bubble, Selection, Insertion, and Merge sort.

```

---

Whenever you start your next session, just feed that block to the AI.

Would you like to go ahead and draft **Brick 2** right now, or are you ready to pause the session here?