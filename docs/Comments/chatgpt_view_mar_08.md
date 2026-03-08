# Notes

That is the right move.

You are at the point where the **shared system docs are no longer enough by themselves**. The missing layer is a set of **animation behavior specs**, one per algorithm or motion pattern, that tells an AI agent exactly how Pygame should stage the visual teaching sequence.

Right now your main docs define:

* what the app is
* how the architecture works
* what each tick means
* what the UI looks like
* what tests should pass

What they do **not fully define** is:

* the exact **motion choreography**
* the exact **state-to-motion translation**
* the exact **Pygame-level interpretation** of each teaching moment

That is why you are still seeing ambiguity.

## My input

You should split the work into **three layers**.

## Layer 1: Core product/system docs

Keep your current main docs as the authoritative system layer:

* PRD
* Architecture
* Data Contracts
* UI Spec
* Behavior Spec
* Acceptance Tests
* Test Plan
* Dev Env
* CI
* Decisions

These should stay focused on the full application.

Do **not** overload them with too much per-algorithm choreography detail.

## Layer 2: Animation choreography docs

Create a separate family of documents dedicated to **teaching motion**.

This is the missing piece.

I would make one master animation framework doc, then one per algorithm.

### Recommended structure

* `10_ANIMATION_FRAMEWORK.md`
* `10A_BUBBLE_SORT_ANIMATION.md`
* `10B_SELECTION_SORT_ANIMATION.md`
* `10C_INSERTION_SORT_ANIMATION.md`
* `10D_MERGE_SORT_ANIMATION.md`

That is much better than trying to force everything into one generic animation spec.

Why this works:

* the framework doc defines the shared Pygame motion model
* each algorithm doc defines its own instructional choreography
* an AI agent can implement shared motion primitives once, then apply algorithm-specific rules cleanly

## Layer 3: Example-driven reference capture

This is the “store to the side” idea you mentioned, and I think it is exactly right.

For each example video you provide, create a **reference observation doc** first, before changing the main specs.

Example:

* `references/example_bubble_video_01.md`
* `references/example_insertion_video_01.md`

These are **not implementation authority**. They are analysis notes.

Each reference doc should capture:

* what the viewer sees
* what motion happens
* what is emphasized
* what teaching purpose the motion serves
* which parts should be adopted into your real spec
* which parts are just stylistic and should be ignored

That gives you a buffer between “example inspiration” and “locked implementation rule.”

That is smart, because otherwise you will pollute the core specs with accidental details from one sample video.

## The workflow I recommend

This is the clean process.

### Step 1

Review one example video.

### Step 2

Produce a **reference observation document** for that video.

That document should answer:

* what exactly happens visually
* what the algorithmic meaning is
* what the animation phases are
* what Pygame primitives would likely be needed
* what should become a spec requirement

### Step 3

Convert only the accepted behaviors into a **locked algorithm animation spec**.

### Step 4

Update the core documents only where necessary:

* data contracts
* behavior spec
* acceptance tests
* animation framework
* decisions

That keeps the system clean.

## Why this is the right approach for AI code generation

AI agents fail when the spec mixes:

* system architecture
* visual intent
* teaching choreography
* implementation hints
* reference inspiration

into one blob.

Your new plan separates them.

That will increase success because the AI agent will be able to answer these questions deterministically:

* What is the shared motion engine?
* What is bubble sort supposed to look like?
* What is insertion sort supposed to look like?
* What is required vs optional?
* What came from inspiration vs what is locked?

That is exactly how you reduce generation drift.

## What should go into the shared animation framework doc

Your master Pygame animation doc should define the common rules every algorithm uses.

It should include sections like:

### 1. Motion model

* sprite owns exact float position
* sprite has home position and optional transient target
* animation progresses using `dt`
* controller assigns motion duration
* view resolves interpolation every frame

### 2. Motion primitives

Define reusable primitives such as:

* highlight only
* lift
* drop
* horizontal slide
* swap arc
* move to auxiliary row
* return to primary row
* hold in place
* flash completion
* show cursor/arrow/limit marker

### 3. Animation lifecycle

For every motion:

* start condition
* in-flight state
* completion condition
* cancellation/pause behavior
* step behavior

### 4. Layering and z-order

Very important for Pygame:

* which sprite renders on top during overlap
* marker vs sprite draw order
* panel overlay order

### 5. Timing ownership

* controller owns logical duration
* view owns interpolation
* speed multiplier behavior
* pause behavior
* step behavior

### 6. Deterministic rendering rules

* left sprite arcs up, right arcs down
* compare row offset values
* auxiliary row offset values
* arrow anchor positions
* sorted boundary marker behavior

This becomes the reusable engine spec.

## What should go into each algorithm animation doc

Each algorithm doc should answer:

### Bubble sort

* how compare is shown
* whether compare lifts the pair
* how no-swap looks
* how swap looks
* where cursor arrow is
* how sorted suffix is shown
* how pass boundary moves

### Selection sort

* how current minimum is shown
* how scan candidate is shown
* how min change is shown
* how scan region is shown
* how final swap is staged

### Insertion sort

* how key pickup is shown
* how held key is displayed
* how shifted elements move
* how insertion target is shown
* how drop/placement occurs

### Merge sort

* how active range is shown
* when elements move to auxiliary row
* how compare/write looks
* how subrange grouping is shown
* how return to main row happens

That gives each algorithm its own teaching identity.

## Important caution

Do not make the algorithm-specific docs too poetic or too visual-language-heavy.

AI agents need:

* exact triggers
* exact movement
* exact offsets
* exact timing behavior
* exact state transitions

So avoid phrases like:

* “moves elegantly”
* “slides naturally”
* “feels smooth”
* “visually pleasing”

Replace them with:

* “lifts by 40 px”
* “holds for compare duration”
* “returns to baseline at operation completion”
* “draw arrow centered under left compared index”

That is what helps code generation.

## Best document pattern for each example review

When you bring me an example, I would suggest I produce this format every time:

### A. Example Observation

What the video literally shows.

### B. Inferred Teaching Intent

What that motion is trying to teach.

### C. Pygame Translation

What objects, states, and motion primitives are needed.

### D. Spec Adoption Recommendation

What should be added to locked docs.

### E. Patch Targets

Which files should be updated.

That will make the process repeatable.

## My recommendation in plain terms

Yes, build a separate animation-spec track.

Yes, keep example analysis documents separate from locked implementation docs.

Yes, repeat the process example by example.

Yes, then roll the accepted behaviors back into the official spec set.

That is the right design process now.

## What I would do next

I would create this doc set next:

* `10_ANIMATION_FRAMEWORK.md`
* `10A_BUBBLE_SORT_ANIMATION.md`
* `references/example_bubble_video_01.md`

Then use those to patch:

* `05_ALGORITHMS_VIS_SPEC.md`
* `06_BEHAVIOR_SPEC.md`
* `07_ACCEPTANCE_TESTS.md`
* `08_TEST_PLAN.md`
* `DECISIONS.md`

That gives you a clean pipeline from inspiration to implementation authority.

The main thing is this: you are no longer trying to describe an app only. You are now describing a **teaching-motion engine**. That deserves its own spec family.

I can draft the exact template for these new animation documents.
