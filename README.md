# Visual Learning Sorting

A Python/Pygame sorting algorithm visualizer where Bubble, Selection, Insertion, and Heap Sort race side-by-side in a 2x2 panel grid. Each algorithm is driven by operation-weighted timing so the race reflects algorithmic cost, not frame parity.

Built as both a pedagogical artifact and an engineering journal — the blueprint-first methodology is documented for video narration alongside the code itself.

## Start Here

- **Current build status:** `CLAUDE.md` (Build Status section)
- **Project north star:** `NORTH_STAR.md` (what and why)
- **Implementation tracker:** `TODO/IMPLEMENTATION_TRACKER.md` (phase-by-phase progress)
- **Locked decisions:** `docs/design_docs/DECISIONS.md` (D-001 through D-081)
- **Architecture:** `docs/design_docs/02_ARCHITECTURE.md`
- **Context packs:** `docs/design_docs/14_CONTEXT_PACKS.md` (phase-specific reading lists)
- **Engineering journal:** `DEVLOG.md` + `docs/devlog/` (session-by-session decision trail)
- **Open questions:** `docs/OPEN_QUESTIONS.md`

## Quick Start

```bash
# Requires Python 3.13+, UV package manager
uv sync
uv run visual-sort
```

## Stack

Python 3.13+ | Pygame 2.5+ | UV | Ubuntu (WSL) | Hatchling build system
