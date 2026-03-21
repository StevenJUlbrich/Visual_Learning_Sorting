# Conversation: Spec Updates for Agentic Implementation Readiness

**Date:** 2026-03-16
**Tool:** Claude Code (Opus 4.6)
**Branch:** `updates-to-the-visuals`
**Status:** Complete

## Purpose

Update all spec documents to reflect design decisions from the UI mock review session, ensuring an agentic AI can generate the solution without ambiguity or stale references.

## Stages

### Stage 1: `02_ARCHITECTURE.md` — Structure & Component Update
- Update directory tree with new View components
- Remove Option B accent references → universal orange
- Add Heap Sort tree layout to View responsibilities
- Add pointer assets, HUD, LimitLine to component list
- Update Sprite Identity for tree ↔ array mapping

### Stage 2: `07_ACCEPTANCE_TESTS.md` — Fix Stale Tests + Add New
- Fix all per-algorithm accent color references → universal orange
- Fix Heap Sort "no auxiliary row" → tree layout
- Add new ATs for: tree visualization, pointer arrows, KEY label, phase label, circular rings

### Stage 3: Heap Sort Tree Geometry Spec
- Add exact positioning formulas for tree nodes
- Define extraction swap animation path (tree → sorted row)
- Define sorted row layout beneath tree

### Stage 4: `AGENT_PROMPTS/IMPLEMENTER.md` — Fix References
- Fix 10_CI.md → 10_ANIMATION_SPEC.md
- Add screen_Ideas mocks as visual targets
- Remove Merge Sort reference
- Add Reference/ write-ups as behavior guides

### Stage 5: `08_TEST_PLAN.md` — New Test Cases
- Add test cases for tree layout, pointer assets, phase labels
- Update manual test pass for new visual expectations

### Stage 6: `03_DATA_CONTRACTS.md` — Minor Cleanup
- Update accent color references to universal orange

### Stage 7: `config.toml` + Font Assets
- Create config.toml with default values
- Document font asset fallback behavior

## Changes Log

### Stage 1 Complete
- `02_ARCHITECTURE.md` fully rewritten: new directory tree (tree_layout.py, pointer.py, limitline.py, hud.py), universal orange, Per-Panel View Components table, Heap Sort tree↔array mapping, circular ring sprites

### Stage 2 Complete
- `07_ACCEPTANCE_TESTS.md` updated: 6 stale references fixed (Option B → universal orange, green → orange, per-algorithm colors → universal, no auxiliary row → tree layout), 7 new acceptance tests added (AT-21 through AT-27) covering tree visualization, phase label, heap boundary, Selection pointers, Insertion KEY/gap, circular rings, no title dots

### Stage 3 Complete
- `04_UI_SPEC.md` Section 4.3.2 added: Heap Sort Tree Layout Geometry — exact formulas for tree area, node sizing, level positioning (vertical), node positioning (horizontal with binary subdivision), parent-child edges (default + active colors), sorted row layout, dim placeholders, heap boundary marker, phase label positioning

### Stage 4 Complete
- `AGENT_PROMPTS/IMPLEMENTER.md` rewritten: correct file references (10_ANIMATION_SPEC.md not 10_CI.md), added screen_Ideas mocks and Reference write-ups as inputs, removed Merge Sort reference, added Key Visual Decisions quick reference, added Algorithm-Specific View Requirements table, references AT-01 through AT-27

### Stage 5 Complete
- `08_TEST_PLAN.md` updated: 2 new P1 risks (tree layout geometry, pointer desync), manual test pass updated for universal orange + circular rings + 4 new observations (Selection pointers, Insertion KEY, Heap tree, ring sprites), 5 new test cases (TC-A20 through TC-A24) covering tree positioning, edge connectivity, tree shrinking, Selection pointer tracking, Insertion KEY lifecycle

### Stage 6 Complete
- `03_DATA_CONTRACTS.md` reviewed — no changes needed, accent color references are already generic or orange

### Stage 7 Complete
- `config.toml` created with default landscape orientation
- `assets/fonts/` directory created with README.md documenting font sources (Inter, FiraCode), download URLs, and fallback behavior
