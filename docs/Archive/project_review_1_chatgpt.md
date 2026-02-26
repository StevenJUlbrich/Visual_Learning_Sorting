## Project review: what you already have (and what’s strong)

You’ve already assembled most of what an agentic builder would need—especially for a “brick-by-brick” implementation workflow:

* **A clear product intent + constraints** (portfolio + educational, 4 algorithms side-by-side, numbers not bars, no custom arrays, etc.). 
* **A locked architecture**: strict MVC under `src/visualizer/`, “global tick” via generators, and the **Pure Result Pattern** (Go/Rust style explicit success/failure states).  
* **Implementation-ready guidance for an agentic coding tool** (directory structure, non-negotiables, UI principles, etc.). 
* **A full conceptual stack** from models → views → controller captured across Brick docs and handoff docs.    

This is already beyond what most projects have before coding starts.

---

## The main gaps to fix before handing this to an agentic model

These aren’t “code problems”—they’re **spec and contract clarity** problems. If you fix these at the document level, an agentic model will build with fewer wrong turns.

### 1) Single Source of Truth for the `SortResult` contract

You currently have a **contract mismatch across docs**:

* In Brick 2 / the model contract, `SortResult` includes `array_state`. 
* In the agentic guide, the contract snippet shown omits `array_state` (but other parts of the guide assume state rendering). 

This is the kind of inconsistency that causes an agentic builder to “correct” your design and drift.

**Fix (document-only):**
Create `docs/03_DATA_CONTRACTS.md` that declares:

* the definitive `SortResult` fields (including what can be `None`)
* the meaning of `highlight_indices`
* what constitutes a “tick”
* whether `message` is required for every tick
* whether additional metadata (like `op_type`) is required

### 2) UI control scope is still ambiguous

Your planning notes list **Start/Step, Restart, Pause/Resume, Speed selector**. 
But the controller doc emphasizes keyboard controls and paused-on-start behavior; it doesn’t explicitly “lock” a clickable UI or a step button. 

**Fix (document-only):**
Decide and document:

* Is this **keyboard-only** (minimal, faster to build)
  or
* Do you want **on-screen controls** (more polished, more work)?

If you don’t lock this, an agent might implement a UI layer you didn’t want.

### 3) Visual identity per algorithm vs global theme

Your reference-video notes call out **distinct colors per algorithm** (cyan/magenta/purple/red). 
Your theme doc defines a single global highlight/default/complete palette. 

**Fix (document-only):**
In a UI spec, lock one:

* **Option A (clean + modern):** global highlight colors only (simple, consistent)
* **Option B (educational clarity):** each panel has an accent color while still using shared semantics (default/highlight/complete) but tinted per algorithm

### 4) “Step counter” definition isn’t fully formalized

You mention step counters everywhere, but it’s not fully specified **what a “step” is**:

* every yielded `SortResult`?
* only comparisons?
* comparisons + swaps but not “status” ticks?
* merge sort bracket ticks count?

**Fix (document-only):**
Add a definition in the contracts doc:

* “Step = every yielded state where `success=True` and `is_complete=False`”
* or introduce explicit operation typing (`op_type: compare|swap|shift|merge|done`) and define step counting by type

### 5) Window orientation and capture target is unresolved

Your inspiration video is portrait-ish (720×996). 
Your grid/window doc uses 1280×720 landscape. 

This matters if the “portfolio output” is a recorded clip formatted for social/phone viewing.

**Fix (document-only):**
Lock:

* “Primary build target is landscape 1280×720”
* or “Primary build target is portrait 720×996”
* or “support both via a config flag”

---

## The initial role to use (right now): Spec Orchestrator

Since you explicitly said “do not build code” and want to prep documents for agentic implementation later, the first role should **not** be “coder.” It should be a role that:

1. consolidates all decisions,
2. resolves contradictions,
3. produces a canonical spec pack that a coding agent can execute.

### Initial Role: **Spec Orchestrator (Technical Product Owner + Lead Architect)**

**Mission:** produce a clean, contradiction-free “source of truth” document set that agentic builders must follow.

**Responsibilities**

* Merge Bricks + Planning Notes + Handoff docs into a unified spec
* Identify and resolve conflicting statements (especially data contracts)
* Maintain a **Decisions Log** (“Locked / Not decided / Deferred”)
* Define the acceptance criteria and “Definition of Done”
* Generate role-scoped prompts for later agentic work (implementation, QA, UI)

**Outputs (documents, not code)**

* `docs/01_PRD.md` (what it is, what it isn’t, user experience)
* `docs/02_ARCHITECTURE.md` (MVC boundaries, tick model, runtime)
* `docs/03_DATA_CONTRACTS.md` (SortResult + tick semantics)
* `docs/04_UI_SPEC.md` (layout, typography, colors, states)
* `docs/05_BEHAVIOR_SPEC.md` (controls, pause/speed/restart, completion behavior)
* `docs/06_ACCEPTANCE_TESTS.md` (human-checkable + automated-test intentions)
* `docs/DECISIONS.md` (single source of truth for locked decisions)
* `docs/AGENT_PROMPTS/…` (role prompts, guardrails)

This role is consistent with your existing “handoff” style and reinforces the strict architecture you already locked in.  

---

## Other roles to leverage (to produce the right documents)

Think of these as “document-producing specialists” that the Spec Orchestrator can call on. You can run them sequentially (or have an agentic system run them as separate passes) and then merge results.

### 1) **Product Designer (UX/UI)**

**Produces:** `docs/04_UI_SPEC.md`
Locks:

* layout dimensions + padding rules
* typography rules (font sizes, fallback behavior)
* per-panel composition (title, Big-O label, step counter, message line, array rendering, error state)
* algorithm color identity decision (global vs per-panel accent)

Grounded in your Brick 4 and planning notes.   

### 2) **Algorithm Visualization Specialist**

**Produces:** `docs/05_ALGORITHMS_VIS_SPEC.md`
Locks:

* what each algorithm must yield and when (tick taxonomy)
* highlight rules (compare vs swap vs merge-range)
* merge sort “bracket” / subarray emphasis requirements (if any)

Grounded in your Brick 3 algorithm behavior + planning notes.   

### 3) **QA / Test Designer**

**Produces:** `docs/06_ACCEPTANCE_TESTS.md` + `docs/07_TEST_PLAN.md`
Defines:

* minimum correctness checks (every algorithm ends fully sorted)
* generator contract checks (must emit final complete tick)
* “no shared mutable array” checks
* regression for the selection-sort bug you observed in the reference material (your spec should make that impossible). 

### 4) **Dev Experience / Build Engineer**

**Produces:** `docs/08_DEV_ENV.md` + `docs/09_CI.md`
Locks:

* how to run in WSL/Windows reliably
* lint/typecheck commands (ruff/pyright)
* optional CI pipeline expectations

Grounded in your handoff/environment choices. 

### 5) **Agent Prompt Engineer**

**Produces:** `docs/AGENT_PROMPTS/IMPLEMENTER.md`, `REVIEWER.md`, `QA.md`
Creates:

* a strict “coding agent” prompt (build-only later)
* a “review agent” prompt that checks drift from contracts
* a “no-exceptions-for-domain-flow” guardrail prompt

Grounded in your existing agentic guide (but corrected). 

---

## Recommended agentic workflow (document-first, then build later)

1. **Spec Orchestrator pass**

   * merges docs
   * resolves contradictions
   * publishes `DECISIONS.md`

2. **UX/UI pass**

   * locks visuals + layout + interaction rules

3. **Algorithm Visualization pass**

   * locks tick semantics + highlight semantics

4. **QA pass**

   * writes acceptance tests and edge cases

5. **Agent Prompt Engineer pass**

   * writes the “implementation prompt pack”

Only after these are complete do you hand the repo to a coding agent.

---

## Kickoff questions you still need to answer (to start *well*)

I’m only listing questions that are **not already locked** in your current documents. Where you already decided, I’m not re-asking.

### A) Product framing

1. What is the primary portfolio “wow” outcome?

   * a short recorded clip (TikTok/Shorts style)
   * a desktop demo people run locally
   * both (then orientation + controls matter more)

2. Do you want this to be a **one-shot demo** (always same array, same 4 algos), or a “mini app” with a tiny bit of selection?

### B) Window format and recording target

3. Landscape (1280×720) or portrait (720×996) as the **primary** format?
4. If portrait is primary, do you still want a 2×2 grid, or a 4×1 vertical stack (more readable on phones)?

### C) Controls and interaction scope

5. Keyboard-only controls, or on-screen buttons too?
6. Do you need a true **Step** mode (advance exactly one global tick per keypress), or is pause/resume enough?
7. Do you need a **Restart** control in v1 (it’s in your planning notes), or can restart be “close and rerun” for v1? 

### D) What exactly is a “step”?

8. Should the step counter increment on:

   * every yielded tick, or
   * only “operations” (compare/swap/shift/place), excluding “status” ticks?
9. Do you want to show multiple counters (e.g., comparisons vs writes), or keep it to one “ticks” number?

### E) What the panel must display (beyond numbers)

10. Should each panel display the `message` text (“Comparing X and Y”, “Placed …”)?

* always
* optional via a toggle
* never (colors only)

11. Should the panel show a “Complete” banner/state when done (beyond green highlights)?

12. When an algorithm finishes early, should the panel:

* freeze final state and show “Waiting…”
* or fade/dim to emphasize it’s finished?

### F) Algorithm identity and colors

13. Do you want distinct accent colors per algorithm (like the reference), or a single consistent theme across all?  
14. If per-algorithm accents: are colors assigned by algorithm name and never change?

### G) Merge sort visualization fidelity

15. Do you want a literal “bracket” visual for subarrays (lines/braces), or is “highlight range” sufficient?

### H) Documentation and repo polish

16. Do you want to include font files in-repo (assets committed) or require download?
17. Do you want a short “How it works” diagram in README (MVC + tick loop), or just text?
18. Do you want a short GIF/demo video embedded in README as part of the portfolio presentation?

---

## If you do only one thing next

Create **one canonical spec** file that resolves contradictions:

* `docs/DECISIONS.md` (Locked decisions list)
* `docs/03_DATA_CONTRACTS.md` (SortResult is definitive here)

That alone will make the later agentic implementation dramatically more reliable and reduce “spec drift.”
