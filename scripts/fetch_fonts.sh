#!/usr/bin/env bash
# fetch_fonts.sh — One-shot font acquisition for Visual Learning Sorting.
#
# Downloads Inter-Bold.ttf, Inter-Regular.ttf, and FiraCode-Regular.ttf
# from their canonical OFL-licensed GitHub releases into assets/fonts/.
#
# Usage (from repo root):
#   bash scripts/fetch_fonts.sh
#
# Requires: bash, curl, unzip. Safe to re-run (idempotent — skips files
# that already exist). Closes Phase 0.2 "assets/fonts/" tracker item.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FONT_DIR="$REPO_ROOT/assets/fonts"
mkdir -p "$FONT_DIR"

# -- Inter (Regular + Bold) --
# Source: https://github.com/rsms/inter/releases (pinned to v4.0 for reproducibility)
INTER_VERSION="4.0"
INTER_ZIP_URL="https://github.com/rsms/inter/releases/download/v${INTER_VERSION}/Inter-${INTER_VERSION}.zip"
INTER_TMP="$(mktemp -d)"

need_inter=false
for f in Inter-Bold.ttf Inter-Regular.ttf; do
    [ -f "$FONT_DIR/$f" ] || need_inter=true
done

if $need_inter; then
    echo "→ Downloading Inter v${INTER_VERSION}..."
    curl -fsSL -o "$INTER_TMP/inter.zip" "$INTER_ZIP_URL"
    unzip -q "$INTER_TMP/inter.zip" -d "$INTER_TMP/inter"
    # The v4 zip layout places static TTFs under extras/ttf/
    find "$INTER_TMP/inter" -type f -name "Inter-Bold.ttf"    -exec cp {} "$FONT_DIR/" \;
    find "$INTER_TMP/inter" -type f -name "Inter-Regular.ttf" -exec cp {} "$FONT_DIR/" \;
    rm -rf "$INTER_TMP"
    echo "  ✓ Inter-Bold.ttf, Inter-Regular.ttf"
else
    echo "✓ Inter fonts already present"
fi

# -- Fira Code (Regular) --
# Source: https://github.com/tonsky/FiraCode/releases (pinned to 6.2 for reproducibility)
FIRA_VERSION="6.2"
FIRA_ZIP_URL="https://github.com/tonsky/FiraCode/releases/download/${FIRA_VERSION}/Fira_Code_v${FIRA_VERSION}.zip"
FIRA_TMP="$(mktemp -d)"

if [ ! -f "$FONT_DIR/FiraCode-Regular.ttf" ]; then
    echo "→ Downloading Fira Code v${FIRA_VERSION}..."
    curl -fsSL -o "$FIRA_TMP/fira.zip" "$FIRA_ZIP_URL"
    unzip -q "$FIRA_TMP/fira.zip" -d "$FIRA_TMP/fira"
    find "$FIRA_TMP/fira" -type f -name "FiraCode-Regular.ttf" -exec cp {} "$FONT_DIR/" \;
    rm -rf "$FIRA_TMP"
    echo "  ✓ FiraCode-Regular.ttf"
else
    echo "✓ FiraCode-Regular.ttf already present"
fi

echo ""
echo "Installed fonts:"
ls -la "$FONT_DIR"/*.ttf 2>/dev/null || echo "  (none — something went wrong)"
