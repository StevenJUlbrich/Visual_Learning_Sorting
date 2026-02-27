# 09 DEV ENV - WSL/Windows Developer Environment

Scope: Reliable local development for Sorting Algorithm Visualizer on Windows 11 + Ubuntu WSL.
Grounded in handoff environment: Python 3.13, `uv`, `pygame`, `ruff`, `pyright`.

## 1) Supported Environment (Locked)
- Host OS: Windows 11.
- Dev shell: Ubuntu WSL.
- Python: 3.13.
- Package/env manager: `uv`.
- Core runtime lib: `pygame`.
- Quality tools: `ruff`, `pyright`.

## 2) One-Time Setup (WSL)
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

## 3) Reliable Run Commands
Use these commands from repo root:

```bash
# run app/module entry
uv run python -m visualizer.main

# fallback (if module path differs in implementation)
uv run python src/visualizer/main.py
```

## 4) Lint / Typecheck Commands (Locked)
From repo root:

```bash
# lint
uv run ruff check .

# optional auto-fix (local only)
uv run ruff check . --fix

# strict type checking
uv run pyright
```

## 5) Recommended Local QA Loop
```bash
uv sync
uv run ruff check .
uv run pyright
uv run pytest -q
```

## 6) Application Configuration (`config.toml`)

The app reads `config.toml` from the repo root at startup. If the file is missing, defaults are used.

```toml
[window]
# "landscape" (1280x720) or "portrait" (720x996)
orientation = "landscape"
```

- `orientation`: determines window resolution. Default is `"landscape"` (1280x720). Set to `"portrait"` for 720x996.
- The controller reads this file once at startup; changes require a restart.

## 7) WSL + Pygame Reliability Notes
- Preferred: Windows 11 + WSLg (GUI support enabled).
- If Pygame window does not open:
  - confirm WSLg is active (`echo $DISPLAY` should be set).
  - run `wsl --update` from Windows PowerShell and restart WSL.
- Keep repo on Windows drive path `/mnt/d/...` only if performance is acceptable; for faster heavy test cycles, a Linux-home clone may perform better.

## 8) Path and Shell Conventions
- `<REPO_ROOT>` refers to wherever the repository is cloned.
- Common locations:
  - WSL Linux home: `~/projects/Visual_Learning_Sorting`
  - WSL-mounted Windows drive: `/mnt/d/Visual_Learning_Sorting` (Windows: `d:\Visual_Learning_Sorting`)
- Canonical docs/commands assume execution from repo root.
- For best I/O performance in WSL, prefer cloning to the Linux filesystem (`~/`) over a mounted Windows drive (`/mnt/`).

## 9) Definition of Ready (Local)
Developer setup is ready when all pass:
- `uv sync` completes.
- `uv run ruff check .` returns no errors.
- `uv run pyright` returns no type errors.
- App launches via one of the run commands above.
