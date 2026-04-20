# DEVLOG — Visual Learning Sorting

**Purpose:** Chronological engineering journal. Each entry records the work performed, the decisions made (and their rationale), and the open questions remaining. This is the project's decision trail and the source material for the video journal.

**Format:** Newest entries at the top. Each session gets a dated heading. Within an entry: *Worked on*, *Decisions*, *Open questions*, *Next*. Entries are terse but complete — they should stand on their own when read six months from now or when scripted into narration.

**Archive structure:** Completed phases are archived into `docs/devlog/` to keep this file lean. Pre-action plans are preserved in the archives — they are valuable video journal material. The archive files are the authoritative record; this file carries only current-phase work and one-line summaries of archived phases.

---

## Archived Phases

| Phase | Archive file | Summary |
|-------|-------------|---------|
| 0 + 1 | [`docs/devlog/phase_00_01.md`](docs/devlog/phase_00_01.md) | Project state review, Phase 0 closeout (pyproject, config, pseudocode, implementation order, fonts helper), agentic risk assessment, mempalace post-mortem, context-pack adoption, Phase 1 contracts.py, Correction C verification, model strategy. |
| 2 | [`docs/devlog/phase_02.md`](docs/devlog/phase_02.md) | All four algorithm generators: Bubble Sort (2a, 20/26), Selection Sort (2b, 21/10), Insertion Sort (2c, 17/19), Heap Sort (2d, 20/30/35). Includes pre-action plans, post-action closeouts, corrections (bubble message format, selection yield timing), and the T3 contiguity spec bug discovery. |

---

## 2026-04-20 — DEVLOG restructure: archive-by-phase + tracker separation

### Worked on

Split the monolithic DEVLOG into an archive-by-phase structure to prevent context bloat as the project grows. Two archive files created under `docs/devlog/`:

- `phase_00_01.md` — all pre-Phase-2 entries (project state review through model strategy).
- `phase_02.md` — all Phase 2 entries (bubble 2a through heap 2d, including pre-action plans).

Main DEVLOG slimmed to: format guidance, archive summary table, current-phase entries, and the entry template. Pre-action plans preserved in archives for video journal use.

### Decisions

- **Archive by phase, not by date or size.** Phase boundaries are the natural unit of work in this project. Each archive file is self-contained and can be loaded independently.
- **Pre-action plans stay in the archive.** They are primary video journal material — showing the planning-before-coding methodology. Removing them would undercut the secondary project objective.
- **One-line summary per archived phase in main DEVLOG.** Gives orientation without forcing a full archive read. Links to archive files for drill-down.

### Open questions

- **IMPLEMENTATION_TRACKER needs Phase 2 completion evidence.** All four generators delivered but the tracker hasn't been updated yet.
- **T3 contiguity spec bug.** Needs resolution before Phase 3 TC-A19 authoring. Two resolution paths: message-prefix classification or sequencing-context classification.
- **libatomic1 resolved.** `sudo apt-get install libatomic1` was executed successfully. Pyright is now functional.
- **Fonts acquisition.** `scripts/fetch_fonts.sh` still needs to run on WSL host.

### Next

Update IMPLEMENTATION_TRACKER with Phase 2 completion. Then Phase 3 (algorithm unit tests) and Phase 4 (easing module) can begin — they are independent and can run in parallel per the implementation order.

---

## Entry Template (for future use)

```markdown
## YYYY-MM-DD — One-line session summary

### Worked on
Prose. What was touched, what was produced.

### Decisions
- What was decided.
- Why this path rather than alternatives.
- Decision-ID link if it was locked into DECISIONS.md.

### Open questions
- Unresolved items. Where they will be answered.

### Next
The single most concrete next action.
```
