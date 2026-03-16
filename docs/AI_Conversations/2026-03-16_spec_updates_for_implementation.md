# Conversation: Spec Updates for Agentic Implementation Readiness

**Date:** 2026-03-16
**Tool:** Claude Code (Opus 4.6)
**Branch:** `updates-to-the-visuals`
**Status:** In Progress

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

_Updated after each stage completion._
