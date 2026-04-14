# Mempalace Experiment — Archived

**Status:** Shelved 2026-04-14. Preserved as teaching material.

## What Was Attempted

An early attempt to solve the same problem the project is still solving: how to route an agent or human researcher to the *relevant subset* of a large specification corpus rather than forcing them to read the whole thing.

The tool chosen was `mempalace` — a "memory palace" concept installed via UV as a Python dev dependency. The intended mechanic was a taxonomy of named **rooms**, each representing a category of project content, with documents classified into rooms so that queries could be routed to just the relevant ones.

Three artifacts survive:

- **`mempalace.yaml`** (117 lines) — The evolved, keyword-driven configuration. Nine rooms with keyword lists (`tick`, `optype`, `sprite`, `easing`, `mvc`, etc.) intended to drive automatic classification.
- **`mempalace.yaml.bak`** (24 lines) — The earlier prose-description version. Same nine rooms, but each described in natural language rather than keywords.
- **`entities.json`** — A nearly-empty entity registry (two project names, no people tracked). Suggests the entity-tracking side of the tool was never actively used.

## Why It Failed

The concept of retrieval routing is sound. The specific implementation failed for diagnosable reasons, each of which teaches something useful.

**Keyword ambiguity at scale.** A realistic query like *"what highlight indices does the T3 tick use on a Heap sift-down?"* matches at least four rooms simultaneously (`algorithm_contracts`, `animation_spec`, `acceptance_tests`, `decisions`). A bag-of-words classifier has no principled way to choose. The only right answer — "load all four, and follow the D-058 reference" — is precisely what the taxonomy cannot express.

**Taxonomy orthogonal to query intent.** The rooms organize by document *type* (architecture, contracts, decisions). Real queries organize by *task* (implement Insertion Sort, verify Heap counters, render Selection scan phase). A task-shaped question projected onto a type-shaped taxonomy produces weak hits, not strong ones. This is the core design miss.

**Keywords cannot follow references.** The spec contains 270 cross-references (D-NNN, AT-NN, TC-A numbers, section pointers). A classifier treats each document as a standalone bag of words, so it cannot traverse the graph of citations that a real research action needs to follow. Cross-reference chasing is a graph problem; keyword partitioning is a set problem. Wrong data structure for the job.

**Room coverage was incomplete.** The keyword-driven version had no home for `CLAUDE.md`, `NORTH_STAR.md`, `DEVLOG.md`, `pyproject.toml`, `config.toml`, `00_PSEUDOCODE.md`, or `13_IMPLEMENTATION_ORDER.md`. The largest and most load-bearing files fell into the `general` catch-all, which defeated the purpose.

**Wrong direction on iteration.** The `.bak` file's prose descriptions were arguably *better* signal than the current file's keyword lists, because natural-language descriptions carry disambiguating context that single-word keywords lose. The iteration from descriptions to keywords was a move toward mechanical matching, not toward accuracy. When a more mechanical approach produces less accurate results, that is evidence the mechanism is wrong, not that it needs more mechanization.

**No feedback loop.** No log was ever kept of queries attempted, classifications returned, or accuracy rates. Without measurement, there was no way to diagnose which keywords were over-firing or under-firing. The YAML was written once, broke silently on contact with real queries, and got shelved.

## Lessons Preserved for the Context-Pack Design

The active context-pack proposal under author review (see `DEVLOG.md` entry dated 2026-04-14, "Agentic-coder context and hallucination risk assessment") inherits four specific constraints from the mempalace post-mortem:

1. **Group by implementation phase, not by document type.** A phase-based pack matches the shape of real queries; a type-based taxonomy does not.
2. **Enumerate file paths explicitly.** No classifier. No keyword matching. Each pack lists the files it loads by path, deterministically.
3. **Allow cross-references to be named, not inferred.** If Phase 2's Insertion Sort work requires decisions D-060, D-064, D-071, D-072, those IDs appear in the pack entry. The tool fetches them by ID; no keyword inference step.
4. **Define a coverage test.** Before the pack design ships, a short list of archetypal queries must each be answerable from exactly one named pack. If any real query cannot be answered, the pack design is broken and the break is detected immediately.

## Disposition

These files are retained in this directory as historical artifact and teaching material. They are not on any load path and not referenced by the active spec corpus. They may be deleted in the future without impact if the lessons encoded here are sufficient on their own.

The `mempalace` package itself was removed as a dev dependency when `pyproject.toml` was rewritten on 2026-04-14.
