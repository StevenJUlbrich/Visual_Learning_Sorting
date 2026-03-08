# 09 DEV ENV - WSL/Windows Developer Environment

Scope: Reliable local development and headless CI testing for the Pygame Sorting Algorithm Visualizer on Windows 11 + Ubuntu WSL.

## 1) Supported Environment (Locked)

* **Host OS:** Windows 11.
* **Dev shell:** Ubuntu WSL.
* **Python:** 3.11+
* **Package/env manager:** `uv` (or your preferred manager, such as Poetry, if you choose to migrate).
* **Core runtime lib:** `pygame >=2.5`.
* **Quality tools:** `ruff`, `pyright`, `pytest`.

## 2) WSL + Pygame Display Setup

Running a graphical game engine inside a Linux subsystem requires specific display routing.

* **Preferred:** Windows 11 + WSLg (GUI support is enabled by default in modern Windows 11).
* **Verification:** Run `echo $DISPLAY` in your Ubuntu terminal. It should return a value (usually `:0`).
* **Troubleshooting:** If the Pygame window fails to open, run `wsl --update` from Windows PowerShell, restart WSL, and verify your graphics drivers are up to date.

## 3) Headless Testing (CI/CD & Local)

Because Pygame expects a monitor, running `pytest` in a standard CI pipeline (or a raw WSL shell without WSLg) will crash when it attempts to initialize the display. You must bypass the display driver for tests.

Run your test suite with the `SDL_VIDEODRIVER` environment variable set to `dummy`:

```bash
# Run tests headlessly (vital for CI/CD pipelines)
SDL_VIDEODRIVER=dummy uv run pytest -q

```

*Note: You can also enforce this within your `conftest.py` file by setting `os.environ["SDL_VIDEODRIVER"] = "dummy"` before initializing any Pygame modules.*

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
# run app/module entry
uv run python -m visualizer.main

# fallback (if module path differs in implementation)
uv run python src/visualizer/main.py

```

## 6) Lint / Typecheck Commands (Locked)

From repo root:

```bash
# lint
uv run ruff check .

# strict type checking
uv run pyright

```

## 7) Application Configuration (`config.toml`)

The app reads `config.toml` from the repo root at startup. If the file is missing, defaults are used.

```toml
[window]
# Option C: "landscape" (1280x720) or "portrait" (720x996)
orientation = "landscape"

```

* `orientation`: determines window resolution. Default is `"landscape"` (1280x720). Set to `"portrait"` for 720x996.
* The controller reads this file once at startup; the View layer calculates its `y_home` baselines dynamically based on this setting. Changes require a restart.

## 8) Path and Shell Conventions

* `<REPO_ROOT>` refers to wherever the repository is cloned.
* For best I/O performance and compilation speed in WSL, prefer cloning the project directly to the Linux filesystem (`~/projects/...`) rather than a mounted Windows drive (`/mnt/c/...`). Canonical docs/commands assume execution from the repo root.
