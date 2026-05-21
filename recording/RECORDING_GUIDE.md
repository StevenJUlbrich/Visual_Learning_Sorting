# Episode 4 — Terminal Recording Guide

This guide walks you through recording clips **01**, **02**, **05**, and **06** from the Episode 4 v3 design doc.

The clips are captured against a reproducible git sandbox built by `sandbox.py`. Every command you type during recording is documented below — verbatim, in the order you'll type them. Between takes you can wipe and rebuild the sandbox in seconds.

---

## What you'll record

| Clip | What's on screen | Length |
|---|---|---|
| 01 | `wc -l` showing the truncated file, then `python -c "import ast; ast.parse(...)"` failing with `SyntaxError` | 6–8 sec |
| 02 | `git diff --stat` showing 27 lines deleted | 3–5 sec |
| 05 | Same as 01 if you want a clean re-take of just the AST parse fail | 5–7 sec |
| 06 | `git show HEAD~1:... > ...` recovery, then `wc -l` and a clean parse | 8–10 sec |

You can capture all four in one continuous take, or split them. The sandbox makes either flow easy.

---

## Real numbers from the sandbox (use these when updating v3)

The investigation agent overstated the truncation size. The sandbox produces the honest numbers, which you should use when finalising the v3 script:

| Metric | v3 draft says | Real number from sandbox |
|---|---|---|
| File line count when truncated | 144 (intended: 217) | **118** (intended: 145) |
| Lines lost | 73 | **27** |
| Cut at line | 144 | **119** |
| Method affected | "_draw_jmin_pointer (tail) + full draw() + full reset()" | **tail of _draw_jmin_pointer** (the file has no separate `draw()`/`reset()` methods) |
| Visible last line | `label_rect = lab` | `label_rect =` (real) — see "Why not `lab`?" below |
| Parse error | `SyntaxError: unexpected EOF while parsing` | **`SyntaxError: invalid syntax`** (line 119) |

A v3 → v4 voiceover refresh that matches the actual recording:

> "Phase ten-e. A small refactor on the Selection Sort pointer code. Three constants. Two functions. Five test assertions. Bounded scope. Locked spec."
>
> "The AI returned a success message."
>
> "The next independent check disagreed. The file had been a hundred and forty-four lines. It was now a hundred and eighteen. Twenty-six lines short — the tail of one method, plus the partial line where the writing stopped."
>
> "AST parse caught it. That gate had been added one phase earlier, after the first truncation. This was the first incident it caught."

---

## Why not `label_rect = lab`?

The case study text in `wiki/Misalignment-Case-Studies.md` describes the cut as `label_rect = lab`. That exact partial line still **parses cleanly** in Python — `lab` is a valid identifier reference, so Python reads it as "assign the name `lab` to `label_rect`." That doesn't produce a `SyntaxError`.

The sandbox cuts the line at `label_rect =` (no right-hand side). That **does** produce a real `SyntaxError: invalid syntax (line 119)`. It's the closest faithful recreation of a true silent-truncation parse failure.

If you want the on-screen text to literally show `label_rect = lab` for visual continuity with the case study, hand-edit the truncated file before recording:

```bash
# After running `python sandbox.py truncate`:
cd sandbox
# Edit the last line to read "        label_rect = lab" instead of "        label_rect ="
# Note: this version will *not* fail ast.parse, so save it as a still image only.
```

The voiceover refresh above doesn't mention "lab" anywhere — so the cleanest path is to use the sandbox version as-is and skip the visual stylization.

---

## Prerequisites

- Python 3.10+
- Git 2.28+ (older versions may need a manual `git symbolic-ref` step — the script handles this automatically)
- A screen recorder of your choice — OBS, asciinema, SimpleScreenRecorder, Kazam, or just your OS's built-in capture
- A terminal you're happy to record from (default font, comfortable size — readable on a 1080p YouTube screen)
- This repo cloned locally with full git history (needed to extract pre-10e pointer.py from commit `11b56ec`)

---

## One-time setup

From the repo root:

```bash
cd recording
python sandbox.py setup
```

Expected output: the script extracts pre-10e `pointer.py` from project history, initializes a fresh git repo inside `recording/sandbox/`, and makes two commits so `HEAD~1` reaches the baseline file.

When it's done, you should see:

```
=== [OK] Sandbox ready ===
  Next: python sandbox.py truncate
```

You can verify state at any time with `python sandbox.py status`.

---

## Recording flow

### Step 1 — apply the truncation

```bash
python sandbox.py truncate
```

This rewrites `sandbox/src/visualizer/views/pointer.py`, cutting 27 lines off the end and leaving the file with `label_rect =` as the partial last line (no trailing newline). The script verifies the parse failure before returning.

### Step 2 — enter the sandbox and start your recorder

```bash
cd sandbox
```

Start your screen recorder pointed at the terminal window. Give it a one-second buffer before you type the first command.

### Step 3 — Clip 01 and Clip 05 (parse failure)

Type these commands exactly:

```bash
wc -l src/visualizer/views/pointer.py
```

Expected output:

```
118 src/visualizer/views/pointer.py
```

Then:

```bash
python3 -c "import ast; ast.parse(open('src/visualizer/views/pointer.py').read())"
```

Expected output:

```
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/usr/lib/python3.10/ast.py", line 50, in parse
    return compile(source, filename, mode, flags,
  File "<unknown>", line 119
    label_rect =
                ^
SyntaxError: invalid syntax
```

Hold on the `SyntaxError` line for ~2 seconds before continuing.

If you want Clips 01 and 05 captured as separate takes, stop recording here, then run `python ../sandbox.py reset` and `python ../sandbox.py setup` and `python ../sandbox.py truncate` again before re-recording.

### Step 4 — Clip 02 (diff stat)

Type:

```bash
git diff --stat
```

Expected output:

```
 src/visualizer/views/pointer.py | 28 +---------------------------
 1 file changed, 1 insertion(+), 27 deletions(-)
```

Hold for ~3 seconds — viewers need time to read the deletion count.

Optional flourish: type `tail -3 src/visualizer/views/pointer.py` next to show the literal last line `label_rect =` on screen. This is a strong visual receipt.

### Step 5 — Clip 06 (recovery)

Type the recovery command exactly as it appears in the v3 script:

```bash
git show HEAD~1:src/visualizer/views/pointer.py > src/visualizer/views/pointer.py
```

Then verify recovery on screen:

```bash
wc -l src/visualizer/views/pointer.py
```

Expected output:

```
144 src/visualizer/views/pointer.py
```

Then:

```bash
python3 -c "import ast; ast.parse(open('src/visualizer/views/pointer.py').read()); print('parses cleanly')"
```

Expected output:

```
parses cleanly
```

Hold for ~2 seconds, then stop recording.

---

## Between takes

If you need to redo any clip:

```bash
cd ..        # back to recording/
python sandbox.py reset
python sandbox.py setup
python sandbox.py truncate
cd sandbox
# resume recording
```

The whole reset → setup → truncate cycle takes about 3 seconds.

---

## Optional polish

### Make the prompt invisible or minimal

Your default shell prompt may have your username, hostname, path, and git branch — distracting in the recording. Before recording, switch to a clean prompt:

```bash
export PS1='$ '
```

That gives you `$ ` only. Restore your normal prompt later by starting a new shell.

### Clear the screen between clips

Between Clips 01/05 and Clip 02, hit `clear` (or `Ctrl+L`) so each clip starts on a fresh screen.

### Slow your typing

The temptation when recording terminal sessions is to type fast. Don't. Give yourself a half-beat between commands. The viewer needs time to read each line before the next one fires.

### Capture the error stack-trace verbatim

The `SyntaxError` output is long — five lines of traceback before the actual error message. That's fine. **Don't trim it in post.** The visible trace is part of why this looks like real evidence. Trimmed cleaner versions read as stylized and lose credibility.

### Optional alternate cold open

If you want the cold open to feel even more like an investigation, prepend a `pytest` run that hits the parse error inside collection:

```bash
pytest tests/unit/test_pointer.py -x 2>&1 | head -25
```

That shows pytest itself stopping at file collection because the file can't be imported — a more dramatic on-screen failure than the raw `ast.parse`. Caveat: you'll need to install the project's test dependencies in the sandbox for this to work (or just point pytest at the file's directory). The cleaner default path is the `ast.parse` command above.

---

## Cleanup

When you're done recording for good:

```bash
cd recording
python sandbox.py reset
```

The sandbox directory is removed. The script itself stays in `recording/` for future re-recordings.

---

## Troubleshooting

**`fatal: invalid object name '11b56ec'`** — Your local clone doesn't have full git history. Re-clone with `git clone --no-shallow` or fetch all branches.

**Permission errors on `python sandbox.py reset`** — If you're on a Windows-mounted filesystem (e.g., `/mnt/d/...` inside WSL) and `.git` directory deletion fails, run from native Windows Python instead, or manually delete `recording/sandbox/` with `rm -rf` from a Windows-aware shell.

**`git init -q -b main` fails** — Your git is older than 2.28. The script catches this and falls back to a manual `git init` + `git symbolic-ref HEAD refs/heads/main`. If that also fails, the only impact is your default branch will be `master` not `main` — everything else works.

**The parse error doesn't fire** — Run `python sandbox.py verify`. If `ast.parse: OK` shows up, the truncation didn't apply correctly. Try `python sandbox.py reset && python sandbox.py setup && python sandbox.py truncate`.

**`git diff --stat` shows no changes** — You either skipped `python sandbox.py truncate` or you've already committed the truncated state. Reset and retry.

---

## What about clips 03, 04, and 07?

The v3 design doc lists clips 03 (Episode 3 outro card), 04 (stylized "Edit applied" badge), and 07 (implementation tracker). Those are graphical assets, not terminal recordings — build them in your video editor. This guide only covers the four terminal clips.
