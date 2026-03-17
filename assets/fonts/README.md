# Font Assets

This directory should contain the following font files:

- `Inter-Bold.ttf` — Title font (size 24)
- `Inter-Regular.ttf` — Body/metrics/message font (size 16)
- `FiraCode-Regular.ttf` — Number font (size 28, monospace)

## Obtaining Fonts

Both fonts are free and open source:

- **Inter**: https://github.com/rsms/inter/releases — download the latest release, extract `Inter-Bold.ttf` and `Inter-Regular.ttf`
- **Fira Code**: https://github.com/tonsky/FiraCode/releases — download the latest release, extract `FiraCode-Regular.ttf`

Place the `.ttf` files directly in this directory.

## Fallback Behavior

If font files are missing, the app falls back to system fonts (see `04_UI_SPEC.md` Section 3.3):
- Title/body → `pygame.font.SysFont("segoeui, arial", size)`
- Number → `pygame.font.SysFont("consolas, courier", 28)`

The app will not crash on missing fonts.
