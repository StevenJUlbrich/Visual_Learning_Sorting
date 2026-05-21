#!/usr/bin/env python3
"""Sandbox state manager for Episode 4 truncation incident recreation.

Builds a self-contained git sandbox at ./sandbox/ that reproduces the
Phase 10e pointer.py truncation incident. Used to record clips 01, 02,
05, and 06 from the Episode 4 v3 design doc.

Python 3.10+ is sufficient. Git 2.28+ is recommended for ``-b main``.

Usage
-----
    python sandbox.py setup       # one-time: build the sandbox
    python sandbox.py truncate    # apply the truncation pattern
    python sandbox.py verify      # sanity check: line count + parse
    python sandbox.py reset       # wipe sandbox and start over
    python sandbox.py status      # report current state
"""

from __future__ import annotations

import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
SANDBOX_DIR = SCRIPT_DIR / "sandbox"
POINTER_REL_PATH = "src/visualizer/views/pointer.py"
SANDBOX_POINTER = SANDBOX_DIR / POINTER_REL_PATH

# Commit 11b56ec is "The 10e prompt is ready" — the pre-edit baseline.
# At this commit, pointer.py is 144 lines, complete, and parses cleanly.
PRE_10E_COMMIT = os.environ.get("EP4_SANDBOX_BASELINE_COMMIT", "11b56ec")

# Cut at line 119: keep lines 1..118 of the baseline, append the partial
# assignment. The baseline's line 119 was inside _draw_jmin_pointer
# (label_rect = label_surf.get_rect()). Cutting it to "label_rect ="
# loses the last lines of the method and produces a real SyntaxError.
LINES_TO_KEEP = 118
PARTIAL_LAST_LINE = "        label_rect ="


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def run(cmd, cwd=None, check=True, capture=True):
    """Run a shell command. cmd may be a list or a shell string."""
    is_shell = isinstance(cmd, str)
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        shell=is_shell,
        check=check,
        capture_output=capture,
        text=True,
    )


def section(title):
    print()
    print("=== " + title + " ===")


def wc_line_count(path):
    """Return the number of newlines in the file, matching wc -l."""
    if not path.exists():
        return 0
    return path.read_bytes().count(b"\n")


def rmtree_force(path):
    """Remove a directory tree, handling read-only files (Windows .git)."""
    def onerror(func, target, exc_info):
        try:
            os.chmod(target, stat.S_IWRITE)
            func(target)
        except Exception:
            pass
    shutil.rmtree(path, onerror=onerror)


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------


def cmd_setup():
    if SANDBOX_DIR.exists():
        print("[!]  Sandbox already exists at " + str(SANDBOX_DIR))
        print("     Run: python " + Path(__file__).name + " reset")
        return 1

    section("Creating sandbox directory")
    SANDBOX_DIR.mkdir(parents=True)
    SANDBOX_POINTER.parent.mkdir(parents=True, exist_ok=True)
    print("  [+] " + str(SANDBOX_DIR))

    section("Extracting pre-10e pointer.py from project history (commit " + PRE_10E_COMMIT + ")")
    result = run(
        ["git", "show", PRE_10E_COMMIT + ":" + POINTER_REL_PATH],
        cwd=PROJECT_ROOT,
    )
    SANDBOX_POINTER.write_bytes(result.stdout.encode("utf-8"))
    print("  [+] pointer.py written (" + str(wc_line_count(SANDBOX_POINTER)) + " lines via wc -l)")

    section("Initializing git in sandbox")
    try:
        run("git init -q -b main", cwd=SANDBOX_DIR)
    except subprocess.CalledProcessError:
        run("git init -q", cwd=SANDBOX_DIR)
        run("git symbolic-ref HEAD refs/heads/main", cwd=SANDBOX_DIR)
    run("git config user.email demo@example.com", cwd=SANDBOX_DIR)
    run("git config user.name 'Recording Sandbox'", cwd=SANDBOX_DIR)
    print("  [+] git init")

    section("Commit 1 - baseline pointer.py (becomes HEAD~1)")
    run('git add "' + POINTER_REL_PATH + '"', cwd=SANDBOX_DIR)
    run('git commit -q -m "Pre-10e baseline: pointer.py complete, parses cleanly"',
        cwd=SANDBOX_DIR)
    print("  [+] committed baseline")

    section("Commit 2 - marker (so HEAD~1 reaches the baseline)")
    readme = SANDBOX_DIR / "README.md"
    readme.write_text(
        "# Episode 4 Recording Sandbox\n\n"
        "Reproduces the Phase 10e pointer.py truncation incident.\n"
        "See ../RECORDING_GUIDE.md for the recording walkthrough.\n"
    )
    run("git add README.md", cwd=SANDBOX_DIR)
    run('git commit -q -m "10e prompt is ready"', cwd=SANDBOX_DIR)
    print("  [+] committed marker")

    section("Sandbox state")
    log = run("git log --oneline", cwd=SANDBOX_DIR).stdout.strip()
    for line in log.splitlines():
        print("  " + line)
    print("  pointer.py: " + str(wc_line_count(SANDBOX_POINTER)) + " lines (wc -l), parses cleanly")

    section("[OK] Sandbox ready")
    print("  Next: python " + Path(__file__).name + " truncate")
    print("  Guide: " + str(SCRIPT_DIR / "RECORDING_GUIDE.md"))
    return 0


def cmd_truncate():
    if not SANDBOX_POINTER.exists():
        print("[!]  Sandbox not set up. Run: python " + Path(__file__).name + " setup")
        return 1

    diff = run("git diff --quiet", cwd=SANDBOX_DIR, check=False)
    if diff.returncode != 0:
        print("[!]  Working directory already has uncommitted changes.")
        print("     Run: python " + Path(__file__).name + " reset")
        return 1

    section("Applying truncation pattern")
    data = SANDBOX_POINTER.read_bytes().decode("utf-8")
    parts = data.split("\n")
    kept = parts[:LINES_TO_KEEP]
    new_text = "".join(line + "\n" for line in kept) + PARTIAL_LAST_LINE
    SANDBOX_POINTER.write_bytes(new_text.encode("utf-8"))

    new_count = wc_line_count(SANDBOX_POINTER)
    print("  [+] pointer.py truncated to " + str(new_count) + " lines (wc -l)")
    print("  [+] last line: '" + PARTIAL_LAST_LINE.strip() + "' (mid-statement, no newline)")

    section("Verifying the truncation breaks parsing")
    parse = run(
        ["python3", "-c",
         "import ast; ast.parse(open('" + POINTER_REL_PATH + "').read())"],
        cwd=SANDBOX_DIR,
        check=False,
    )
    if parse.returncode != 0:
        print("  [+] File no longer parses (this is the failure we want).")
        for ln in parse.stderr.strip().splitlines():
            if "SyntaxError" in ln or "line " in ln:
                print("      " + ln.strip())
    else:
        print("  [!] Warning: file unexpectedly still parses.")
        return 1

    section("Ready to record")
    print("  cd " + str(SANDBOX_DIR))
    print("  # then type recording commands from RECORDING_GUIDE.md")
    return 0


def cmd_verify():
    if not SANDBOX_POINTER.exists():
        print("[!]  Sandbox not set up. Run: python " + Path(__file__).name + " setup")
        return 1
    section("Verify")
    print("  wc -l: " + str(wc_line_count(SANDBOX_POINTER)))
    parse = run(
        ["python3", "-c",
         "import ast; ast.parse(open('" + POINTER_REL_PATH + "').read())"],
        cwd=SANDBOX_DIR,
        check=False,
    )
    if parse.returncode == 0:
        print("  ast.parse: OK")
    else:
        print("  ast.parse: FAILED")
        for ln in parse.stderr.strip().splitlines():
            if "SyntaxError" in ln or "line " in ln:
                print("    " + ln.strip())
    return 0


def cmd_reset():
    if not SANDBOX_DIR.exists():
        print("[!]  No sandbox to reset.")
        return 0
    section("Removing sandbox at " + str(SANDBOX_DIR))
    rmtree_force(SANDBOX_DIR)
    print("  [+] removed")
    print("\n  Next: python " + Path(__file__).name + " setup")
    return 0


def cmd_status():
    section("Sandbox status")
    if not SANDBOX_DIR.exists():
        print("  Not set up.")
        print("  Run: python " + Path(__file__).name + " setup")
        return 0

    print("  Path: " + str(SANDBOX_DIR))
    print("  pointer.py: " + str(wc_line_count(SANDBOX_POINTER)) + " lines (wc -l)")

    section("Git log")
    log = run("git log --oneline", cwd=SANDBOX_DIR).stdout.strip()
    for line in log.splitlines():
        print("  " + line)

    section("Working directory")
    diff = run("git diff --quiet", cwd=SANDBOX_DIR, check=False)
    if diff.returncode == 0:
        print("  Clean - at baseline.")
        print("  To apply truncation: python " + Path(__file__).name + " truncate")
    else:
        stat_out = run("git diff --stat", cwd=SANDBOX_DIR).stdout
        for line in stat_out.strip().splitlines():
            print("  " + line)
        parse = run(
            ["python3", "-c",
             "import ast; ast.parse(open('" + POINTER_REL_PATH + "').read())"],
            cwd=SANDBOX_DIR,
            check=False,
        )
        if parse.returncode != 0:
            print("\n  pointer.py does not parse - truncation is currently applied.")
            print("  Restore: git show HEAD~1:" + POINTER_REL_PATH + " > " + POINTER_REL_PATH)
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

COMMANDS = {
    "setup": cmd_setup,
    "truncate": cmd_truncate,
    "verify": cmd_verify,
    "reset": cmd_reset,
    "status": cmd_status,
}


def main(argv):
    if len(argv) < 2 or argv[1] not in COMMANDS:
        print(__doc__)
        print("Available subcommands: " + ", ".join(COMMANDS.keys()))
        return 1
    return COMMANDS[argv[1]]()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
