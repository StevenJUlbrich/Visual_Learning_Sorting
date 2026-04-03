# 09 DEV ENV - WSL/Windows Developer Environment

Scope: Reliable local development and headless CI testing for the Pygame Sorting Algorithm Visualizer on Windows 11 + Ubuntu WSL.

## 1) Supported Environment (Locked)

* **Host OS:** Windows 11.
* **Dev shell:** Ubuntu WSL.
* **Python:** 3.13 (CI target). Local development also supported on 3.11+.
* **Package/env manager:** `uv` (or your preferred manager, such as Poetry, if you choose to migrate).
* **Core runtime lib:** `pygame >=2.5`.
* **Quality tools:** `ruff`, `pyright`, `pytest`.

## 2) WSL + Pygame Display Setup

Running a graphical game engine inside a Linux subsystem requires specific display routing.

* **Preferred:** Windows 11 + WSLg (GUI support is enabled by default in modern Windows 11).
* **Verification:** Run `echo $DISPLAY` in your Ubuntu terminal. It should return a value (usually `:0`).
* **Troubleshooting:** If the Pygame window fails to open, run `wsl --update` from Windows PowerShell, restart WSL, and verify your graphics drivers are up to date.

## 3) Headless Testing (CI/CD & Local)

Because Pygame expects a monitor, running `pytest` in a standard CI pipeline (or a raw WSL shell without WSLg) will crash when it attempts to initialize the display. Two layers of protection ensure headless mode is always active during tests:

### Layer 1: conftest.py (safety net)

The root `tests/conftest.py` sets environment variables at module level before any Pygame import:

```python
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
```

This catches the common case where a developer runs `uv run pytest` locally without remembering the environment variable prefix. It also sets `SDL_AUDIODRIVER=dummy` to suppress audio subsystem errors.

### Layer 2: Shell environment (primary)

Always prefer setting the variables at the shell level for maximum safety. This ensures they are active before Python even starts, covering edge cases where Pygame is imported at module level during test collection:

```bash
# Recommended local test command
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy uv run pytest -q

# Or with selective markers
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy uv run pytest -m unit -q
```

### Layer 3: CI pipeline

The GitHub Actions workflow (see `docs/11_CI.md`) sets `SDL_VIDEODRIVER` and `SDL_AUDIODRIVER` at the job level via `env:`, ensuring all steps (including type checking) run headlessly.

### What the dummy driver provides

* `pygame.init()` succeeds, initializing all subsystems (display, font, mixer) without a physical monitor.
* `pygame.font.Font` and `pygame.font.SysFont` produce valid `Surface` objects with correct dimensions.
* `pygame.display.set_mode()` returns a valid `Surface` that can be blitted to (though pixels are not rendered to any physical output).
* All coordinate math, easing calculations, and sprite positioning logic works identically to a real display.

### What the dummy driver does NOT provide

* No visible window — manual/exploratory testing requires a real display (WSLg or native).
* No GPU acceleration — irrelevant for correctness tests.
* No pixel-accurate screenshot comparison — not part of the v1 test plan.

## 4) One-Time Setup (WSL)

Run inside Ubuntu WSL:

```bash
# verify WSL distro and shell
uname -a

# install uv if missing
curl -LsSf https://astral.sh/uv/install.sh | sh

# restart shell, then verify
uv --version
python3 --version
```

Project bootstrap/sync:

```bash
cd <REPO_ROOT>
uv sync
```

## 5) Reliable Run Commands

Use these commands from the repo root:

```bash
# run app/module entry (requires display — use WSLg or native)
uv run python -m visualizer.main

# fallback (if module path differs in implementation)
uv run python src/visualizer/main.py
```

## 6) Test Commands

```bash
# full test suite (headless)
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy uv run pytest -q

# unit tests only (fast feedback — algorithm correctness)
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy uv run pytest -m unit -q

# integration tests only (Controller/timer/state machine)
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy uv run pytest -m integration -q

# verbose output with per-test timing
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy uv run pytest -v --tb=short
```

## 7) Lint / Typecheck Commands (Locked)

From repo root:

```bash
# lint
uv run ruff check .

# strict type checking
uv run pyright
```

## 8) Application Configuration (`config.toml`)

The app reads `config.toml` from the repo root at startup. If the file is missing, defaults are used.

```toml
[window]
# "desktop" (1280x720) or "tablet" (1024x768)
preset = "desktop"
```

* `preset`: determines window resolution. Default is `"desktop"` (1280×720). Set to `"tablet"` for 1024×768.
* Portrait orientation (720×996) has been removed (D-079). Both presets are landscape-oriented with panel widths ≥ 489px.
* The window size is locked at startup and cannot be resized during runtime (D-077). The View layer calculates all geometry once at startup. Changes require a restart.

## 9) Path and Shell Conventions

* `<REPO_ROOT>` refers to wherever the repository is cloned.
* For best I/O performance and compilation speed in WSL, prefer cloning the project directly to the Linux filesystem (`~/projects/...`) rather than a mounted Windows drive (`/mnt/c/...`). Canonical docs/commands assume execution from the repo root.
