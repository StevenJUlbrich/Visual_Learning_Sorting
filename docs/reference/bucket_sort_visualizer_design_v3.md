# Bucket Sort Visualizer — Design Approach v3

## Lightning Labs Style · Python 3.13 · UV · Windows OS

---

## 1. What We're Building

A Python application that generates an animated visualization of the **Bucket Sort** algorithm, matching the "Lightning Labs" dark-neon aesthetic. The animation progresses through three distinct phases — **Scatter**, **Sort**, **Gather** — with a synchronized pseudocode panel that highlights the active line of logic.

### Target Platform: Windows

- Primary development and runtime on Windows 10/11
- Fonts: Bundled (JetBrains Mono) + system fallbacks (Consolas, Courier New)
- Video export: ffmpeg via `winget install ffmpeg` or manual install
- Python 3.13 managed by UV

### Key Features

- **Three range presets:** Small (0–99), Medium (0–199), Large (0–999) with auto-scaled bucket counts
- **Configurable element count:** 10–15 elements, user-selectable
- **Dual interface:** Pygame menu screen for interactive use + CLI overrides for scripting
- **Reproducible demos:** `--seed` flag for deterministic random generation
- **Video export:** Produces mp4 via piped ffmpeg (no temp files)
- **Educational focus:** Pseudocode panel synced to animation, theory docs included
- **Optional sound effects:** Subtle audio cues per phase (Brick 14)

---

## 2. Reference Video Breakdown

| Phase | Visual Behavior | Color | Easing |
|-------|----------------|-------|--------|
| **READY** | N unsorted values in horizontal row; empty bucket outlines below with range labels | Gray circles | — |
| **Phase 1: SCATTER** | Each value arcs downward into its target bucket. Active element glows. | Cyan `#00FFD0` | `ease_in_out_sine` (arc feel) |
| **Phase 2: SORT BUCKETS** | Insertion sort within each bucket. Swapping elements pulse. | Yellow `#FFD700` | `ease_in_out_quad` (smooth swap) |
| **Phase 3: GATHER** | Sorted elements fly from buckets up to final sorted row. | Magenta `#FF3366` | `ease_in_back` (snap into place) |
| **SORTED** | Final sorted row pulses in celebration. | Green `#00FF88` | `ease_out_bounce` (celebration) |

Bottom panel: "LIGHTNING LABS" branding + "ALGORITHM LOGIC" pseudocode block with active-line highlight bar.

---

## 3. Technology Stack

| Tool | Version | Purpose |
|------|---------|---------|
| **Python** | 3.13 | Runtime (pinned via UV) |
| **UV** | latest | Package manager, venv, Python version management |
| **Pygame** | >=2.5.0 | Rendering, animation, menu UI, frame capture |
| **ffmpeg** | system | Video export (piped stdin, no temp files) |
| **argparse** | stdlib | CLI interface with preset/override/seed flags |
| **ruff** | dev dep | Linting for GitHub Actions CI |
| **pytest** | dev dep | Algorithm, step recording, CLI, and export tests |

---

## 4. UV Project Setup (Windows)

```powershell
# Create project
uv init bucket-sort-viz
cd bucket-sort-viz

# Pin Python 3.13
uv python install 3.13
uv python pin 3.13

# Add runtime dependencies
uv add pygame

# Add dev dependencies
uv add --dev ruff pytest

# Run the app
uv run python -m bucket_sort_viz
uv run python -m bucket_sort_viz --preset medium --count 12 --seed 42
```

### pyproject.toml

```toml
[project]
name = "bucket-sort-viz"
version = "0.1.0"
description = "Animated Bucket Sort visualizer for visual learning — Lightning Labs style"
readme = "README.md"
license = { text = "MIT" }
requires-python = ">=3.13"
keywords = ["sorting", "algorithm", "visualization", "education", "bucket-sort"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Education",
    "Topic :: Education",
    "Topic :: Scientific/Engineering :: Visualization",
    "Programming Language :: Python :: 3.13",
    "Operating System :: Microsoft :: Windows",
]
dependencies = [
    "pygame>=2.5.0",
]

[project.scripts]
bucket-sort-viz = "bucket_sort_viz.main:main"

[tool.ruff]
line-length = 100
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "W"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

---

## 5. Project Structure

```
bucket-sort-viz/
│
├── .github/
│   └── workflows/
│       └── ci.yml                  # Ruff lint + pytest on push/PR
│
├── assets/
│   └── fonts/
│       ├── JetBrainsMono-Regular.ttf    # Bundled — code panel font
│       ├── JetBrainsMono-Bold.ttf       # Bundled — headings
│       └── OFL.txt                       # JetBrains Mono license (SIL Open Font)
│
├── docs/
│   ├── algorithm_theory.md         # Bucket sort explained: how, why, complexity
│   ├── design_decisions.md         # Why Pygame, step-recording, architecture
│   └── images/
│       └── bucket_sort_demo.gif    # Animated GIF for README embed
│
├── src/
│   └── bucket_sort_viz/
│       ├── __init__.py
│       ├── main.py                 # Entry point: CLI parsing → menu or direct run
│       ├── config.py               # All constants: colors, sizes, timing, fonts
│       ├── presets.py              # Small/Medium/Large preset definitions
│       │
│       ├── model/
│       │   ├── __init__.py
│       │   ├── bucket_sort.py      # Algorithm engine + step recording
│       │   └── step.py             # Step dataclass with Literal types
│       │
│       ├── view/
│       │   ├── __init__.py
│       │   ├── renderer.py         # Main Pygame drawing engine
│       │   ├── elements.py         # CircleElement, BucketRegion drawables
│       │   ├── code_panel.py       # Pseudocode panel with line highlighting
│       │   ├── menu_screen.py      # Interactive Pygame menu for settings
│       │   └── effects.py          # Glow, particles, celebration effects
│       │
│       ├── controller/
│       │   ├── __init__.py
│       │   ├── animator.py         # Replays Steps as Tweens, manages timing
│       │   └── tweens.py           # Tween class, easing functions (documented per phase)
│       │
│       └── export/
│           ├── __init__.py
│           └── video_export.py     # Piped ffmpeg export (no temp files)
│
├── tests/
│   ├── __init__.py
│   ├── test_bucket_sort.py         # Algorithm correctness tests
│   ├── test_step_recording.py      # Step sequence validation
│   ├── test_presets.py             # Preset config + bucket range edge cases
│   ├── test_cli_args.py            # Argparse validation
│   └── test_video_export.py        # Mock ffmpeg, check frame piping
│
├── output/                          # Generated videos land here (gitignored)
│   └── .gitkeep
│
├── .gitignore
├── .python-version                  # Created by `uv python pin 3.13`
├── pyproject.toml
├── uv.lock
├── LICENSE                          # MIT
├── DESIGN.md                        # This document — build roadmap
└── README.md                        # Hero GIF + description + install + usage
```

---

## 6. config.py — Complete Constants Reference

```python
"""Central configuration for Bucket Sort Visualizer."""

from pathlib import Path

# ──────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
OUTPUT_DIR = PROJECT_ROOT / "output"

# ──────────────────────────────────────────────
# Screen
# Dimensions match the reference video (1694×924).
# This fits cleanly on a 1920×1080 display with
# Windows taskbar visible and window chrome.
# ──────────────────────────────────────────────
SCREEN_WIDTH = 1694
SCREEN_HEIGHT = 924
FPS = 30
WINDOW_TITLE = "Bucket Sort — Lightning Labs"

# ──────────────────────────────────────────────
# Colors (RGB tuples)
# ──────────────────────────────────────────────
COLORS = {
    # Backgrounds
    "bg_dark":           (15, 20, 30),
    "bg_panel":          (20, 28, 40),
    "bg_menu":           (12, 16, 24),

    # Text
    "text_primary":      (200, 210, 220),
    "text_muted":        (80, 100, 120),
    "text_bright":       (240, 245, 250),

    # Phase colors
    "cyan_scatter":      (0, 255, 208),
    "yellow_sort":       (255, 215, 0),
    "magenta_gather":    (255, 51, 102),
    "green_sorted":      (0, 255, 136),

    # UI elements
    "bucket_outline":    (40, 55, 75),
    "bucket_fill":       (25, 35, 50),
    "branding_cyan":     (0, 200, 180),
    "menu_highlight":    (0, 180, 160),
    "menu_inactive":     (60, 75, 95),

    # Element states
    "element_default":   (100, 115, 135),
    "element_active":    (255, 255, 255),
}

# ──────────────────────────────────────────────
# Fonts (bundled + system fallbacks)
# ──────────────────────────────────────────────
FONTS = {
    "title": {
        "path": FONTS_DIR / "JetBrainsMono-Bold.ttf",
        "fallback": "Consolas",
        "size": 36,
    },
    "subtitle": {
        "path": FONTS_DIR / "JetBrainsMono-Regular.ttf",
        "fallback": "Consolas",
        "size": 18,
    },
    "code": {
        "path": FONTS_DIR / "JetBrainsMono-Regular.ttf",
        "fallback": "Consolas",
        "size": 16,
    },
    "branding": {
        "path": FONTS_DIR / "JetBrainsMono-Bold.ttf",
        "fallback": "Courier New",
        "size": 28,
    },
    "label": {
        "path": FONTS_DIR / "JetBrainsMono-Regular.ttf",
        "fallback": "Consolas",
        "size": 14,
    },
    "value": {
        "path": FONTS_DIR / "JetBrainsMono-Bold.ttf",
        "fallback": "Consolas",
        "size": 14,
    },
    "menu_title": {
        "path": FONTS_DIR / "JetBrainsMono-Bold.ttf",
        "fallback": "Consolas",
        "size": 48,
    },
    "menu_item": {
        "path": FONTS_DIR / "JetBrainsMono-Regular.ttf",
        "fallback": "Consolas",
        "size": 22,
    },
}

def load_font(font_key: str) -> "pygame.font.Font":
    """Load bundled font with system fallback for Windows compatibility."""
    import pygame
    spec = FONTS[font_key]
    try:
        return pygame.font.Font(str(spec["path"]), spec["size"])
    except FileNotFoundError:
        return pygame.font.SysFont(spec["fallback"], spec["size"])

# ──────────────────────────────────────────────
# Animation Timing (in seconds, converted to frames at runtime)
# ──────────────────────────────────────────────
TIMING = {
    "ready_hold":             1.5,    # Pause before scatter starts
    "scatter_per_element":    0.6,    # Duration of each scatter arc
    "scatter_stagger":        0.15,   # Delay between consecutive scatters
    "scatter_glow_warmup":    0.3,    # Glow before element moves
    "phase_transition_pause": 1.0,    # Pause between phases
    "sort_swap":              0.4,    # Duration of a swap animation
    "sort_compare_hold":      0.2,    # Highlight before swap decision
    "sort_bucket_pause":      0.3,    # Pause between buckets
    "gather_per_element":     0.5,    # Duration of each gather arc
    "gather_stagger":         0.12,   # Delay between consecutive gathers
    "celebration_hold":       2.5,    # Final sorted state display
    "celebration_pulse_rate": 0.4,    # Speed of green pulse cycle
}

def timing_to_frames(seconds: float) -> int:
    """Convert seconds to frame count based on FPS."""
    return max(1, round(seconds * FPS))

# ──────────────────────────────────────────────
# Element count
# ──────────────────────────────────────────────
ELEMENT_COUNT_MIN = 10
ELEMENT_COUNT_MAX = 15
ELEMENT_COUNT_DEFAULT = 10
```

---

## 7. Step Recording System

### Step Dataclass with Literal Types

```python
# model/step.py
from dataclasses import dataclass, field
from typing import Literal

StepType = Literal[
    "scatter",       # Element moves from input row to bucket
    "compare",       # Two elements highlighted for comparison (sort phase)
    "swap",          # Two elements swap positions within a bucket
    "no_swap",       # Comparison made, no swap needed (element stays)
    "gather",        # Element moves from bucket to output row
    "phase_change",  # Transition marker between phases
    "celebration",   # Final sorted state trigger
]

PhaseName = Literal["ready", "scatter", "sort", "gather", "done"]

@dataclass
class Step:
    step_type: StepType
    phase: PhaseName
    element_values: list[int]         # Which value(s) are involved
    source_positions: list[tuple[int, int]]   # Starting (x, y) per element
    target_positions: list[tuple[int, int]]   # Ending (x, y) per element
    bucket_index: int = -1            # Which bucket (-1 if N/A)
    code_line: int = -1               # Pseudocode line to highlight
    description: str = ""             # Human-readable note for debugging
```

### Step-to-Code-Line Mapping

```python
# Pseudocode line indices (0-based)
PSEUDOCODE_LINES = [
    "# 1. Scatter into Buckets",      # 0 — comment
    "for x in input:",                 # 1 — keyword
    "    idx = floor(x * k)",          # 2 — code
    "    buckets[idx].push(x)",        # 3 — code (scatter highlight)
    "# 2. Sort Buckets",              # 4 — comment
    "for b in buckets:",               # 5 — keyword
    "    insertionSort(b)",            # 6 — code (sort highlight)
    "# 3. Gather",                     # 7 — comment
    "output = []",                     # 8 — code
    "for b in buckets:",               # 9 — keyword
    "    output.concat(b)",            # 10 — code (gather highlight)
]

STEP_TO_CODE_LINE: dict[StepType, int] = {
    "scatter":      3,    # buckets[idx].push(x)
    "compare":      6,    # insertionSort(b)
    "swap":         6,    # insertionSort(b)
    "no_swap":      6,    # insertionSort(b)
    "gather":       10,   # output.concat(b)
    "phase_change": -1,   # No highlight during transitions
    "celebration":  -1,   # No highlight during celebration
}
```

---

## 8. Preset System

```python
# presets.py
from dataclasses import dataclass

@dataclass(frozen=True)
class SortPreset:
    name: str
    label: str
    value_range: tuple[int, int]     # (min, max) inclusive
    num_buckets: int
    bucket_size: int                  # range width per bucket
    circle_radius: int
    description: str

    def generate_bucket_ranges(self) -> list[tuple[int, int]]:
        """Generate (low, high) range tuples for each bucket."""
        ranges = []
        for i in range(self.num_buckets):
            low = self.value_range[0] + i * self.bucket_size
            high = low + self.bucket_size - 1
            ranges.append((low, high))
        return ranges

    def validate(self) -> bool:
        """Verify bucket ranges fully cover the value range with no gaps."""
        total_coverage = self.num_buckets * self.bucket_size
        value_span = self.value_range[1] - self.value_range[0] + 1
        return total_coverage == value_span


PRESETS: dict[str, SortPreset] = {
    "small": SortPreset(
        name="small",
        label="Small (0–99)",
        value_range=(0, 99),
        num_buckets=4,
        bucket_size=25,               # 0-24, 25-49, 50-74, 75-99
        circle_radius=22,
        description="Classic 4-bucket sort. Great for understanding the basics.",
    ),
    "medium": SortPreset(
        name="medium",
        label="Medium (0–199)",
        value_range=(0, 199),
        num_buckets=8,
        bucket_size=25,               # 0-24, 25-49, ... 175-199
        circle_radius=18,
        description="Wider range with 8 buckets. Shows how bucket count scales.",
    ),
    "large": SortPreset(
        name="large",
        label="Large (0–999)",
        value_range=(0, 999),
        num_buckets=10,
        bucket_size=100,              # 0-99, 100-199, ... 900-999
        circle_radius=15,
        description="Big range, 10 buckets. Demonstrates real-world distribution.",
    ),
}

DEFAULT_PRESET = "small"
```

---

## 9. Dual Interface Design

### 9A — CLI with Seed Support

```python
# main.py
import argparse
import sys

def parse_args():
    parser = argparse.ArgumentParser(
        prog="bucket-sort-viz",
        description="Animated Bucket Sort visualizer — Lightning Labs style",
    )
    parser.add_argument(
        "--preset",
        choices=["small", "medium", "large"],
        default=None,
        help="Value range preset (skips menu if combined with --count)",
    )
    parser.add_argument(
        "--count",
        type=int,
        choices=range(10, 16),
        metavar="10-15",
        default=None,
        help="Number of elements to sort (10–15)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible demos (e.g. --seed 42)",
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="Export animation as mp4 video",
    )
    parser.add_argument(
        "--no-code-panel",
        action="store_true",
        help="Hide the algorithm pseudocode panel",
    )
    # Note: --headless was considered but removed.
    # Pygame on Windows requires SDL_VIDEODRIVER=dummy for headless,
    # which is unreliable. Export mode always shows the window.
    return parser.parse_args()


def check_ffmpeg() -> bool:
    """Verify ffmpeg is available on the system (Windows-friendly)."""
    import subprocess
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            check=True,
        )
        return True
    except FileNotFoundError:
        return False


def main():
    args = parse_args()

    # Validate ffmpeg if export requested
    if args.export and not check_ffmpeg():
        print("⚠️  ffmpeg not found. Video export requires ffmpeg.")
        print("")
        print("Install on Windows:")
        print("  winget install ffmpeg")
        print("  — or —")
        print("  Download from https://ffmpeg.org/download.html")
        print("")
        print("After installing, restart your terminal and try again.")
        sys.exit(1)

    if args.preset and args.count:
        # CLI mode — skip menu, run directly
        run_visualization(
            preset_name=args.preset,
            count=args.count,
            seed=args.seed,
            export=args.export,
            show_code_panel=not args.no_code_panel,
        )
    else:
        # Interactive mode — show Pygame menu
        settings = show_menu_screen(default_seed=args.seed)
        if settings:
            run_visualization(**settings)
```

### 9B — Pygame Menu Screen

```
┌──────────────────────────────────────────┐
│                                          │
│          B U C K E T   S O R T           │
│          Lightning Labs Visualizer       │
│                                          │
│   ┌──────────────────────────────────┐   │
│   │  SELECT PRESET                   │   │
│   │                                  │   │
│   │  [●] Small (0–99)    4 buckets   │   │
│   │  [ ] Medium (0–199)  8 buckets   │   │
│   │  [ ] Large (0–999)  10 buckets   │   │
│   └──────────────────────────────────┘   │
│                                          │
│   ┌──────────────────────────────────┐   │
│   │  NUMBER OF ELEMENTS              │   │
│   │                                  │   │
│   │  ◄  12  ►                        │   │
│   │  (10 – 15)                       │   │
│   └──────────────────────────────────┘   │
│                                          │
│   ┌──────────────────────────────────┐   │
│   │  OPTIONS                         │   │
│   │                                  │   │
│   │  [✓] Export video (mp4)          │   │
│   │  [✓] Show code panel             │   │
│   │  Seed: [______] (blank=random)   │   │
│   └──────────────────────────────────┘   │
│                                          │
│          [ ▶  START VISUALIZATION ]      │
│                                          │
│   ESC to quit  ·  Arrow keys to adjust   │
└──────────────────────────────────────────┘
```

**Interaction:** Arrow keys or mouse to select preset, Left/Right to adjust count, Tab to move between fields, Enter or click START to begin, ESC exits.

---

## 10. Video Export — Piped ffmpeg (No Temp Files)

```python
# export/video_export.py
import subprocess
import pygame

class VideoExporter:
    """Pipes raw frame bytes directly to ffmpeg stdin.
    
    No temporary files are written to disk. This is significantly
    faster on Windows than saving thousands of PNGs.
    """

    def __init__(self, width: int, height: int, fps: int, output_path: str):
        self.width = width
        self.height = height
        self.fps = fps
        self.output_path = output_path
        self.process = None
        self.frame_count = 0

    def start(self):
        """Launch ffmpeg process with stdin pipe."""
        self.process = subprocess.Popen(
            [
                "ffmpeg", "-y",
                "-f", "rawvideo",
                "-vcodec", "rawvideo",
                "-pix_fmt", "rgb24",
                "-s", f"{self.width}x{self.height}",
                "-r", str(self.fps),
                "-i", "-",                  # Read from stdin
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-crf", "18",               # High quality
                "-preset", "fast",          # Good speed/quality balance
                self.output_path,
            ],
            stdin=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )

    def capture_frame(self, surface: pygame.Surface):
        """Write one frame's raw bytes to ffmpeg."""
        if self.process and self.process.stdin:
            frame_bytes = pygame.image.tobytes(surface, "RGB")
            self.process.stdin.write(frame_bytes)
            self.frame_count += 1

    def finish(self):
        """Close the pipe and wait for ffmpeg to finish encoding."""
        if self.process and self.process.stdin:
            self.process.stdin.close()
            self.process.wait()
            print(f"✅ Exported {self.frame_count} frames → {self.output_path}")
```

---

## 11. Easing Functions Reference

```python
# controller/tweens.py
import math

def ease_in_out_sine(t: float) -> float:
    """Smooth arc motion — used for SCATTER phase.
    Elements arc from input row down to buckets with a natural gravity feel.
    """
    return -(math.cos(math.pi * t) - 1) / 2

def ease_in_out_quad(t: float) -> float:
    """Smooth acceleration/deceleration — used for SORT SWAP phase.
    Elements slide past each other with even motion.
    """
    if t < 0.5:
        return 2 * t * t
    return 1 - (-2 * t + 2) ** 2 / 2

def ease_in_back(t: float) -> float:
    """Slight overshoot then settle — used for GATHER phase.
    Elements snap into their final sorted position with a satisfying click.
    """
    c1 = 1.70158
    c3 = c1 + 1
    return c3 * t * t * t - c1 * t * t

def ease_out_bounce(t: float) -> float:
    """Bouncy landing — used for CELEBRATION pulse.
    The sorted row bounces into its final green glow.
    """
    n1 = 7.5625
    d1 = 2.75
    if t < 1 / d1:
        return n1 * t * t
    elif t < 2 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    elif t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    else:
        t -= 2.625 / d1
        return n1 * t * t + 0.984375

def ease_out_cubic(t: float) -> float:
    """Fast start, gentle stop — general purpose fallback."""
    return 1 - (1 - t) ** 3
```

---

## 12. Bucket Overflow Handling

When many elements land in a single bucket (worst case: all 15 in one), the visual needs to handle vertical stacking gracefully.

**Strategy:** Elements stack from the bottom of the bucket upward. If the stack exceeds the bucket's visual height, element spacing compresses proportionally so all elements remain visible. The circle radius shrinks slightly only if absolutely necessary.

```python
def calculate_stack_positions(
    bucket_x: int,
    bucket_bottom_y: int,
    bucket_height: int,
    num_elements: int,
    circle_radius: int,
) -> list[tuple[int, int]]:
    """Calculate (x, y) positions for stacked elements in a bucket."""
    ideal_spacing = circle_radius * 2 + 4  # diameter + gap
    total_needed = num_elements * ideal_spacing

    if total_needed <= bucket_height:
        spacing = ideal_spacing
    else:
        # Compress spacing to fit
        spacing = bucket_height / num_elements

    positions = []
    for i in range(num_elements):
        y = bucket_bottom_y - (i * spacing) - circle_radius
        positions.append((bucket_x, int(y)))
    return positions
```

---

## 13. Distribution Warning

For the Large preset (0–999 range, 10 buckets, 10–15 elements), most buckets will be empty in any given run. This is actually a valid teaching moment about bucket sort's behavior with sparse data.

We'll add a note in the `docs/algorithm_theory.md`:

> **Note on sparse distributions:** When the number of elements is much smaller than the
> number of buckets, most buckets remain empty. This is expected and demonstrates why
> bucket sort performs best when data is **uniformly distributed** across the range.
> Try running with `--seed 42` to see a spread that hits more buckets, or use the
> Small preset for the clearest visualization of the algorithm's mechanics.

---

## 14. GitHub Repository Extras

### README.md Hero Section

```markdown
# 🪣 Bucket Sort Visualizer

> An animated, educational visualization of the Bucket Sort algorithm.
> Built with Python 3.13, Pygame, and the Lightning Labs dark-neon aesthetic.

![Bucket Sort Demo](docs/images/bucket_sort_demo.gif)

## ✨ What This Shows

Bucket Sort is a **non-comparison sorting algorithm** that works by:
1. **Scattering** elements into range-based buckets
2. **Sorting** each bucket individually (via insertion sort)
3. **Gathering** the sorted buckets into a final list

Average time complexity: **O(n + k)** when data is evenly distributed.

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- [UV](https://docs.astral.sh/uv/) package manager
- ffmpeg (optional, for video export)

### System Requirements (Windows)
```powershell
# Install UV
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install ffmpeg (optional, for video export)
winget install ffmpeg
```

### Install & Run
```powershell
git clone https://github.com/YOUR_USERNAME/bucket-sort-viz.git
cd bucket-sort-viz
uv sync
uv run python -m bucket_sort_viz
```

### CLI Options
```powershell
# Interactive menu
uv run python -m bucket_sort_viz

# Direct run with preset
uv run python -m bucket_sort_viz --preset medium --count 12

# Reproducible demo
uv run python -m bucket_sort_viz --preset small --count 10 --seed 42

# Export video
uv run python -m bucket_sort_viz --preset small --count 10 --export
```

## 📐 Presets

| Preset | Range | Buckets | Best For |
|--------|-------|---------|----------|
| Small  | 0–99  | 4       | Learning the basics |
| Medium | 0–199 | 8       | Seeing bucket scaling |
| Large  | 0–999 | 10      | Real-world distribution |
```

### GitHub Actions CI (`.github/workflows/ci.yml`)

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint-and-test:
    strategy:
      matrix:
        os: [windows-latest, ubuntu-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4

      - name: Install UV
        uses: astral-sh/setup-uv@v4
        with:
          version: "latest"

      - name: Set up Python 3.13
        run: uv python install 3.13

      - name: Install dependencies
        run: uv sync

      - name: Lint with Ruff
        run: uv run ruff check src/ tests/

      - name: Run tests
        run: uv run pytest tests/ -v
```

### .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/

# UV
.venv/

# Output
output/*.mp4
output/*.gif
!output/.gitkeep

# IDE
.vscode/
.idea/

# OS
Thumbs.db
Desktop.ini
```

---

## 15. Updated Brick-by-Brick Build Plan

| Brick | Focus | Deliverable | Test Criteria |
|-------|-------|-------------|---------------|
| **1** | UV init + data model + presets + step recording | `uv run pytest` passes | Algorithm produces sorted output; steps are correctly sequenced for all 3 presets |
| **2** | Static layout renderer | Pygame window shows READY state | Screenshot matches reference frame 1 layout |
| **3** | Drawable classes (CircleElement, BucketRegion) | Elements render with glow at arbitrary positions | Visual inspection of positioned elements |
| **4** | Tween engine + easing functions | Single circle arcs across screen | Easing curves produce smooth motion |
| **5** | Phase 1: Scatter animation | Elements arc into correct buckets | All values land in mathematically correct bucket |
| **6** | Phase 2: Sort Buckets animation | Insertion sort swaps visible per bucket | Bucket contents sorted correctly after phase |
| **7** | Phase 3: Gather animation | Elements collect into sorted output row | Final row matches expected sorted order |
| **8** | Celebration + glow effects | Green pulse on sorted state | Visual polish matches reference |
| **9** | Code panel + branding + line sync | Highlight bar syncs with active phase | Correct line highlighted per step type |
| **10** | Pygame menu screen | Interactive preset/count/seed selection | All controls work via mouse and keyboard |
| **11** | CLI argument parsing + dual interface | Menu when no args; direct run with args | All flag combinations work correctly |
| **12** | Video export (piped ffmpeg) | `--export` produces clean mp4 | Output file plays correctly, no temp files left |
| **13** | GitHub polish: README, docs, CI, GIF | Repo is showcase-ready | CI passes on push; README renders correctly |
| **14** | *(Optional)* Sound effects | Subtle audio cues per phase | Audio plays without frame drops |

---

## 16. Summary of Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Package manager | UV | Fast, modern, pins Python 3.13 cleanly |
| Rendering | Pygame | Full pixel control, frame capture, no browser dependency |
| Architecture | MVC + step recording | Decouples algorithm from visuals; testable independently |
| Video export | Piped ffmpeg stdin | No temp files, faster on Windows |
| Fonts | Bundled JetBrains Mono + system fallback | Consistent look across machines |
| Easing | Phase-specific functions | Each phase has a distinct motion personality |
| Presets | 3 fixed presets | Covers educational range without overwhelming options |
| Target OS | Windows 10/11 | Primary dev/demo environment |
| Headless mode | Removed (v2 had it) | Pygame headless on Windows requires `SDL_VIDEODRIVER=dummy` which is unreliable; export always shows window |
| CI | GitHub Actions matrix (Windows + Ubuntu) | Windows matches target; Ubuntu is faster/cheaper for algorithm + lint checks |

---

## 17. Next Step

Open VS Code, run these commands in PowerShell:

```powershell
uv init bucket-sort-viz
cd bucket-sort-viz
uv python install 3.13
uv python pin 3.13
uv add pygame
uv add --dev ruff pytest
```

Drop this `DESIGN.md` into the project root, then start **Brick 1** with Claude Code.
