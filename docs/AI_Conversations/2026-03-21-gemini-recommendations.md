To ensure the AI agent successfully navigates the identified traps and adheres to the strict architecture of the Sorting Algorithm Visualizer, you should implement a series of **"Immutable System Prompts"** and a **"Phased Workflow Instruction."** Here are the specific prompts and skill instructions you should inject into the agent's system context or task instructions:

### 1. Trap-Specific System Prompts

Inject these directly into the agent's context window as **CRITICAL RULES** before it writes any code.

**Prompt for Trap A: Sprite Identity (The Duplicate Value Trap)**
> **CRITICAL RULE - SPRITE IDENTITY:** When rendering array elements, you MUST NOT track or identify sprites by their integer values. You must assign a permanent, unique `sprite_id` to each `NumberSprite` at initialization. When a new `SortResult` array state is yielded, calculate motion by determining the index delta of the `sprite_id` between the old and new states. If you use value-matching, the `[3, 1, 3, 2, 1, 2, 3]` test case will fail due to visual teleportation.

**Prompt for Trap B: Independent Timing (The Blocking Trap)**
> **CRITICAL RULE - CONTROLLER TIMING:** Do not use `time.sleep()`, `yield from` delays, or any blocking logic. The Pygame `while True` loop must run continuously. Manage time by clamping the clock's delta-time (`dt = min(clock.tick(60), 33)`) and subtracting this integer `dt` from each panel's `current_operation_remaining_ms`. Only fetch the next `SortResult` when this remaining time reaches ≤ 0. All simulated time math must use integer milliseconds.

**Prompt for Trap C: Heap Sort Geometry**
> **CRITICAL RULE - HEAP SORT UI:** Heap Sort uses a unique 2D Binary Tree UI, not a flat row. You must implement the exact logarithmic positioning formulas provided in `docs/04_UI_SPEC.md` (`depth = floor(log2(i + 1))`). Furthermore, when performing a Phase 2 Extraction Swap (root to end), you MUST apply the elevated extraction arc multiplier: `extraction_arc_height = panel_height * 0.14`. 

**Prompt for Trap D: Tick Sequences & Visual Contracts**
> **CRITICAL RULE - TICK SEQUENCES:** Do not optimize away visual operations. 
> 1. **Heap Sort:** Every sift-down level MUST yield a `T3 Range Emphasis` tick (Logical Tree Highlight) BEFORE yielding any `T1 Compare` or `T2 Write` ticks. 
> 2. **Insertion Sort:** Elements must shift sequentially. Yield a `T1 Compare` then a `T2 Shift` for *each* element moving right. You are strictly forbidden from executing "block" or "batch" shifts in a single tick.

**Prompt for Trap E: Exception Handling**
> **CRITICAL RULE - FAILURES:** Never raise Python exceptions (like `ValueError` or `IndexError`) for domain errors like empty arrays, as this will crash the global Pygame loop. Instead, you must yield exactly one `SortResult(success=False, ...)` (a T0 Failure Tick) and immediately return to terminate the generator.

---

### 2. Phased Workflow Instructions (The "Agentic Skill" Sequence)

LLMs perform poorly when asked to build a full MVC architecture simultaneously. Force the agent to build and test the system in strict isolation using this sequence:

**Phase 1: Pure Mathematical Models (The Generators)**
* **Agent Task:** "Implement the four sorting algorithms in `src/visualizer/models/`. They must accept `list[int]` and yield `SortResult` dataclasses. They must have absolutely zero dependencies on Pygame."
* **Validation Gate:** Agent must run `uv run pytest -m unit` to pass `TC-A1` (Sortedness), `TC-A10` (Counter Accuracy), and `TC-A19` (Tick Sequence). Do not proceed to Phase 2 until this is 100% green.

**Phase 2: Easing and Math Utilities**
* **Agent Task:** "Implement `src/visualizer/views/easing.py`. Write standard ease-in-out mathematical functions. This file must be a pure-math module with NO Pygame imports."
* **Validation Gate:** Pass easing math unit tests (`TC-A5`). 

**Phase 3: The Headless Controller**
* **Agent Task:** "Implement `src/visualizer/controllers/orchestrator.py`. Write the `update(dt)` logic to process the queues and countdown the `current_operation_remaining_ms` using mock generators."
* **Validation Gate:** Pass integration tests (`TC-A4`, `TC-A15`) using the `SDL_VIDEODRIVER=dummy` headless testing constraint.

**Phase 4: Pygame View Binding**
* **Agent Task:** "Implement the `NumberSprite` class, the UI geometry layouts, and the `render()` loop. Hook the sprites to the Controller's index delta mapping."
* **Validation Gate:** Manual visual confirmation of the AAA WCAG contrast requirements (universal orange `(255, 140, 0)`) and smooth sprite tweening without teleportation.

By heavily constraining the agent with the **Immutable System Prompts** and forcing a **Phased Workflow**, you prevent the agent from mixing View logic into the Model layer and drastically reduce the chances of hallucinating frame-rate dependent physics.