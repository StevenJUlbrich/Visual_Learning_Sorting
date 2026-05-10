# Visual Learning Sorting

A real-time sorting algorithm visualizer built with Python and Pygame. Four algorithms — Bubble Sort, Selection Sort, Insertion Sort, and Heap Sort — race side-by-side in a 2x2 panel grid, driven by operation-weighted timing that reflects actual algorithmic cost.

<!-- TODO: Add screenshot or GIF of the running application here -->
<!-- Suggested captures: (1) all 4 panels mid-sort, (2) Heap Sort tree view, (3) completion state -->

## Features

- **Genuine race:** Operation timing (compare=150ms, swap=400ms) creates natural speed differences between algorithms — faster algorithms visibly finish first
- **Per-algorithm choreography:** Each sort has custom animation: Bubble Sort lift-and-swap, Insertion Sort key elevation, Selection Sort pointer arrows, Heap Sort binary tree with extraction arcs
- **Visual teaching aids:** Sorted regions turn steel-blue, active elements highlight orange, boundary markers show algorithm progress
- **Heap Sort tree layout:** Binary tree visualization with parent-child edges, sorted row grows as extractions proceed
- **Step-through mode:** Advance one operation at a time to study each algorithm move-by-move
- **Duplicate-safe:** Sprite identity tracking by unique ID (not value) handles arrays with repeated elements correctly

## Quick Start

```bash
# Requires Python 3.13+ and UV package manager
uv sync
uv run visual-sort
```

### Keyboard Controls

| Key | Action |
|-----|--------|
| Space | Play / Pause |
| Right Arrow | Step (advance one operation) |
| R | Restart (reset all panels) |
| Escape | Quit |

### Configuration

Edit `config.toml` to change the array or window preset:

```toml
[window]
preset = "desktop"    # or "tablet" (1024x768)

[sort]
# array = [3, 1, 3, 2, 1, 2, 3]   # uncomment to test duplicates
```

## Architecture

Strict MVC under `src/visualizer/`:

```
src/visualizer/
├── models/          # Algorithm generators yielding SortResult ticks
│   ├── contracts.py # SortResult dataclass, OpType enum, base class
│   ├── bubble.py    # BubbleSort (20 cmp, 26 writes)
│   ├── selection.py # SelectionSort (21 cmp, 10 writes)
│   ├── insertion.py # InsertionSort (17 cmp, 19 writes)
│   └── heap.py      # HeapSort (20 cmp, 30 writes, 35 steps)
├── views/           # Pygame rendering — sprites, overlays, layout
│   ├── sprite_manager.py  # Per-algorithm choreography + overlay classes
│   ├── sprite.py          # NumberSprite (circular ring, float coords)
│   ├── panel.py           # Panel frame + header rendering
│   ├── tree_layout.py     # Heap Sort binary tree positioning
│   ├── pointer.py         # Selection Sort i/j/min arrows
│   ├── limitline.py       # Bubble Sort boundary marker
│   ├── hud.py             # Counters + phase labels
│   └── easing.py          # Pure math (ease_in_out_quad, sine_arc)
├── controllers/
│   └── orchestrator.py    # Independent queues, operation timing, state machine
└── main.py                # Event loop, config loading, font fallback
```

Each algorithm is a Python generator yielding typed `SortResult` ticks. The controller manages independent queues per panel with integer-millisecond timing. The view layer animates sprites based on tick type with per-algorithm motion signatures.

## Testing

```bash
uv run pytest              # 345 tests (29 model + 21 easing + 185 view + 104 controller + 6 duplicate-value)
uv run ruff check src/ tests/    # lint
uv run ruff format --check src/ tests/  # format check
```

All acceptance tests (AT-01 through AT-27) pass visual verification. See `TODO/AT_READINESS_CHECKLIST.md` for the full walkthrough.

## How It Was Built — AI-Assisted Development

This project was built using a **two-agent workflow** as an experiment in AI-assisted software engineering:

1. **Cowork (Opus)** — Generates detailed, prescriptive prompts with exact code snippets, file paths, and exit criteria
2. **Claude Code (Sonnet/Opus)** — Executes the prompts mechanically, runs gates (lint, format, test), reports results

The entire development process is documented:

| Resource | What it shows |
|----------|--------------|
| [`docs/devlog/`](docs/devlog/) | Session-by-session engineering journal (Phases 0-10) |
| [`docs/prompts/`](docs/prompts/) | The exact prompts fed to Claude Code for each fix |
| [`docs/design_docs/`](docs/design_docs/) | 15 specification documents written before any code |
| [`docs/AI_Conversations/`](docs/AI_Conversations/) | Review sessions, gap analysis, agent trap identification |
| [`CLAUDE.md`](CLAUDE.md) | Agent context file — critical rules, architecture, build status |

Key lessons from the process: spec-first development prevents agent drift, model selection matters (Opus for judgment, Sonnet for mechanical execution), and file truncation is a recurring failure mode that requires manual verification.

## Tech Stack

Python 3.13+ | Pygame 2.5+ | UV package manager | Hatchling build system | Ruff (lint + format) | Pytest

## License

MIT License. See [LICENSE](LICENSE).
