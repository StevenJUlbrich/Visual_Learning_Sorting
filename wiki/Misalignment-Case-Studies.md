# Misalignment Case Studies

These are real incidents from the development process where AI agents drifted from specification. Each case study shows what the spec required, what the AI produced, how the gap was detected, and what the fix looked like. These aren't cherry-picked failures — they represent the kinds of drift that happen routinely when AI generates code against complex constraints.

## Case 1: The Duplicate-Value Blindspot (Phase 10c)

**Severity:** Critical — affected all four algorithms when the input array contained duplicate values.

### What the spec required

`compute_sprite_moves()` in the orchestrator must determine which sprites moved between two array states. The function compares old and new `array_state` snapshots and returns a mapping of sprite IDs to their new slot positions. Sprite identity must be tracked by unique ID, never by value (Critical Rule #1).

### What was built

The function used value-delta detection:
```python
changed = [i for i in range(len(old_state)) if old_state[i] != new_state[i]]
```

This works perfectly when all values are unique. When duplicate values exist — say the array `[3, 1, 3, 2]` swaps positions 0 and 2 to produce `[3, 1, 3, 2]` (identical!) — `changed` is an empty list. The function returns no sprite movements. Over a full sort with duplicates, sprites progressively diverge from their actual positions.

### How it was detected

Acceptance test AT-08 tests a configurable array. When tested with `[3, 1, 3, 2, 1, 2, 3]`, sprites ended up in wrong positions at completion. The counter targets still passed — the algorithm sorted correctly — but the visual output was wrong because the view layer lost track of which sprite was where.

### The fix

Added `operation_type` and `highlight_indices` as optional parameters to `compute_sprite_moves()`. When the value-delta detection finds zero changes but the tick is a SWAP or SHIFT with a 2-element `highlight_indices`, the function uses the highlight data to determine which slots exchanged sprites. The existing logic is unchanged for the common case (non-empty `changed` lists), preserving backward compatibility. Six new tests were added specifically for duplicate-value scenarios.

### The lesson

The original implementation was correct for unique values and passed all 339 existing tests. The spec (Critical Rule #1) explicitly warned against value-matching, but the function was written during Phase 6c when duplicate arrays weren't yet testable. The spec caught the category of bug; the acceptance test caught the instance.

---

## Case 2: The T3 Contiguity Collision (Phase 2d)

**Severity:** High — would have caused the view layer to misclassify 6 of 11 Logical Tree T3 ticks in Heap Sort.

### What the spec required

Heap Sort emits two variants of T3 (RANGE) ticks: Boundary Emphasis (showing the active heap region) and Logical Tree Highlight (showing the parent-child triangle during sift-down). The view layer needs to distinguish them because they render differently — boundary uses a staggered sweep, logical tree uses a simultaneous flash.

The original specification (pseudocode §4) stated that the two variants could be distinguished by contiguity: boundary T3 produces a contiguous range `(0, 1, 2, ..., heap_size-1)`, while logical tree T3 produces a non-contiguous tuple like `(1, 3, 4)`.

### What actually happens

During the Phase 2d Heap Sort implementation, a smoke test revealed that contiguity-based classification fails whenever the sift-down parent is index 0. The Logical Tree T3 at parent=0 with both children produces `(0, 1, 2)` — structurally identical to a 3-element boundary T3. This affects every Phase 2 sift-down (all start at the root after extraction) and the last Phase 1 sift-down.

For the default array, 6 of 11 Logical Tree T3 ticks would be misclassified.

### How it was detected

The developer's own smoke-test classifier caught the collision during Phase 2d implementation. The spec's claim was tested against actual generator output before any view code was written.

### The fix

Decision D-081 replaced contiguity-based classification with message-prefix classification: if `tick.message.startswith("Active heap")`, it's a boundary tick; if it starts with `"Evaluating tree level"`, it's a logical tree tick. This is deterministic, self-contained (no buffering or lookahead needed), and already implemented in the generator's message strings.

Five spec documents were amended to reflect the new classification rule. The test plan's TC-A19 helper was rewritten before it was ever coded — preventing the misclassification from propagating into the test suite.

### The lesson

Spec bugs are as real as code bugs, and they're more dangerous because they propagate into every implementation that reads the spec. This one would have caused a subtle rendering error that's hard to diagnose: the correct ticks fire, but the view animates them wrong. Catching it at the spec level (before view code existed) was far cheaper than debugging it from the visual output.

---

## Case 3: The False Extraction Detection (Phase 10f)

**Severity:** High — corrupted Heap Sort tree geometry during BUILD MAX-HEAP phase.

### What the spec required

During Heap Sort's Phase 2 (Extraction), each extraction swap moves the root to the sorted row and shrinks the active heap. The view layer detects extraction by checking if index 0 is in the swap's `highlight_indices`. When an extraction is detected, `_heap_size` decrements and the tree geometry recalculates.

### What the AI produced

The extraction detection logic — `is_extraction = hi is not None and 0 in hi` — was correct for Phase 2. But during Phase 1 (BUILD MAX-HEAP), sift-down at the root also produces SWAP ticks with index 0 in `highlight_indices`. The detection couldn't distinguish a root sift-down swap from an extraction swap.

The result: during BUILD MAX-HEAP, a root sift-down swap would prematurely decrement `_heap_size`, corrupt tree geometry, place sprites in the sorted row, draw boundary labels that shouldn't exist, and cause edges to disappear as the tree collapsed.

### How it was detected

Visual acceptance testing (AT-22). The boundary label appeared during BUILD MAX-HEAP when it should only appear during EXTRACTION. Tree edges disappeared mid-build.

### The fix

Added a `_heap_in_extraction: bool` flag to SpriteManager. The flag is set `True` when a Boundary T3 tick fires (message starts with "Active heap" — boundary ticks only occur in Phase 2). The extraction detection in the SWAP handler is gated on this flag. During BUILD MAX-HEAP, no boundary T3 ticks fire, so the flag stays `False` and root sift-down swaps are handled as normal sift-down swaps.

### The lesson

The view-layer code was logically reasonable — extraction swaps do involve index 0. But it assumed the only SWAP involving the root happens during extraction, which isn't true during the build phase. The spec's two-phase structure was clear, but the AI implementation treated the SWAP handler as phase-agnostic. The acceptance test (a human watching the animation) caught what unit tests couldn't — the visual symptom was obvious, even though the underlying data was being sorted correctly.

---

## Case 4: File Truncation — A Recurring Mechanical Failure

**Severity:** High — occurred 4 times during Phase 10, silently destroying code.

### What happened

During Phases 10d, 10e, 10h, and 10i, the Claude Code agent truncated files mid-write. `pointer.py` was cut at line 144 (mid-variable assignment: `label_rect = lab`). `test_pointer.py` was cut at line 216 (mid-function call: `pointer_set.draw(surf`). `sprite_manager.py` lost its final methods after line 1017.

In each case, the truncation happened silently — the agent reported success, the lint check passed (incomplete files can still be syntactically valid up to the truncation point), and the test suite caught some but not all truncations (tests for the missing methods failed, but tests that didn't exercise the missing code passed).

### How it was detected

AST parse verification caught the `pointer.py` truncation (syntax error at the cut point). Test failures caught the `sprite_manager.py` truncation (missing `reset()` method). Manual file inspection caught the others.

### The fix

Each truncation was fixed by restoring the file from git: `git show HEAD~1:path/to/file > path/to/file`, then re-applying the intended changes. AST parse was added as a standard gate for all subsequent phases.

### The lesson

File truncation is a mechanical failure mode of AI code agents — it's not a logic error or a misunderstanding of the spec. It happens more often with larger files (sprite_manager.py at ~1000 lines was truncated twice). The defense is: always verify file integrity after AI writes, keep files under version control, and include AST parse checks in your gate sequence. Never assume a "success" report means the file is complete.

This is the kind of failure that spec-driven development doesn't prevent but does make recoverable. Because every change has a defined scope (the prompt specifies exactly what should change), you can verify that the intended change exists and that nothing else was lost.
