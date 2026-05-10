# Visual Learning Sorting — Wiki Home

A real-time sorting algorithm visualizer built with Python and Pygame. Four algorithms race side-by-side in a 2x2 panel grid, driven by operation-weighted timing that reflects actual algorithmic cost.

This wiki documents the engineering methodology, architecture, and lessons learned from building this project using spec-driven AI-assisted development.

## Start Here

**If you're a hiring manager** reviewing this as a portfolio piece, start with the [Architecture Overview](Architecture-Overview) to see the system design, then read the [Spec-First Methodology](Spec-First-Methodology) to understand the engineering process. The [Misalignment Case Studies](Misalignment-Case-Studies) page demonstrates debugging discipline applied to AI-generated code.

**If you're learning AI-assisted development,** start with the [Spec-First Methodology](Spec-First-Methodology) to understand why specifications matter when working with AI agents. Then read the [Misalignment Case Studies](Misalignment-Case-Studies) for concrete examples of what goes wrong and how to catch it. The [Tick Taxonomy](Tick-Taxonomy-Explained) and [Algorithm Contracts](Algorithm-Contracts) pages show what "testable specifications" look like in practice.

## Pages

| Page | What you'll find |
|------|-----------------|
| [Architecture Overview](Architecture-Overview) | MVC structure, data flow, independent queue semantics, sprite identity system |
| [Spec-First Methodology](Spec-First-Methodology) | How 15 design documents and 81 locked decisions governed AI code generation |
| [Misalignment Case Studies](Misalignment-Case-Studies) | Four real incidents where AI agents drifted from spec, and how the specs caught them |
| [Tick Taxonomy Explained](Tick-Taxonomy-Explained) | The T0-T3 operation type system that drives the generator-to-animation pipeline |
| [Algorithm Contracts](Algorithm-Contracts) | Per-algorithm tick sequences, counter targets, and highlight rules |
| [Development Timeline](Development-Timeline) | Phase-by-phase build history with model assignments and correction counts |

## Quick Reference

- **Source code:** [`src/visualizer/`](../src/visualizer/)
- **Design documents:** [`docs/design_docs/`](../docs/design_docs/)
- **Devlog archives:** [`docs/devlog/`](../docs/devlog/)
- **Prompts fed to Claude Code:** [`docs/prompts/`](../docs/prompts/)
- **Test suite:** 345 tests — `uv run pytest`
- **Acceptance tests:** AT-01 through AT-27 — [`TODO/AT_READINESS_CHECKLIST.md`](../TODO/AT_READINESS_CHECKLIST.md)
