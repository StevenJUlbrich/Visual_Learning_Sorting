# Open Questions

**Purpose:** Consolidated live list of active uncertainties. Prevents open questions from being buried chronologically in DEVLOG entries where AI agents smooth over them. Items are promoted here when discovered; removed when resolved.

**Last updated:** 2026-05-02

---

## Active

- **Font assets pending.** `scripts/fetch_fonts.sh` has not been run on the WSL host. The app uses `pygame.font.SysFont` fallback until TTF fonts are placed in `assets/fonts/`. Non-blocking for development but required before acceptance testing (AT-01 through AT-27).

- **Git divergent branch.** `Phase-2-Work-(Algorithm-Generators)` branch has an unresolved divergent state from a prior session. Needs cleanup before any merge-to-main work.

## Watch Items

- **Context integrity at session boundaries.** CLAUDE.md, DEVLOG.md, and IMPLEMENTATION_TRACKER.md are susceptible to truncation, CRLF conversion, and null-byte padding when edited by Claude Code across session boundaries. The post-session closeout verification prompt mitigates this. See `docs/devlog/context_integrity.md` for the full pattern documentation.

- **NORTH_STAR.md drift.** Previously contained stale "pre-code blueprint phase" status. Fixed 2026-05-02. This file should contain only stable *what/why* — never current phase status.

## Deferred Features (v1 non-goals by decision)

These are explicitly excluded from v1 scope per `DECISIONS.md`:

- **F-001** User-provided custom arrays
- **F-002** Algorithm picker / dynamic algorithm set
- **F-003** More than four simultaneous algorithms
- **F-004** Audio cues
- **F-005** Dynamic playback speed modification
