# Editing the Gemail Design

The design has one origin: the operator's design artifact, https://claude.ai/artifact/GHuFwncPVxchLZaPLQvURu. Everything under `docs/design/` and `assets/icons/` descends from it. Change the origin, then re-import; never edit a copy.

## Change a screen or a component

1. Change it in the artifact (ask Claude: "update the Gemail design artifact: ..."). Keep every color a value from `docs/design/tokens.json`; add a token first when none fits.
2. Re-import with the `design-sync` skill ("sync the design into the repo"). It reads the artifact's files into `docs/design/mockup/`, re-pins `docs/design/mockup/source.json` (`python scripts/design-lint.py --relock-mockup <version>`), re-renders (`node tools/design/render-mockup.mjs`), updates `docs/design/mockup.md` where a component changed, and runs the gates.
3. If the change moves a component a section cites, `design-sync` files the follow-up through `add-todo` so the code catches up; a shipped surface that no longer matches becomes a `**Design deviation:**` with that follow-up.

## Change a value

Edit `docs/design/tokens.json` (both themes, same keys), check contrast (the `D05 T02 §5` script once it exists; until then the pairs in `mockup.md` by hand), update the artifact's boards to the new value, and re-import. After `D03 T04 §1` ships, also run `node tools/design/tokens.mjs` to regenerate `src/styles/tokens.css`.

## Change or add an icon

Draw it in the artifact's Icons board, then copy the SVG into `assets/icons/src/<app|ribbon|menu|pane>/<name>.svg` (20 px grid and 1.4 px stroke for pane icons; see `icons.md`), add its row to `icons.md`, and run:

```bash
npm ci --prefix tools/design      # once per clone
node tools/design/icons.mjs        # PNGs, src/ui/icons.ts, assets/icons/manifest.json
node tools/design/icons.mjs --sheet  # optional review sheet at build/icons-sheet.png
python scripts/design-lint.py
```

Commit the source, the outputs, and the manifest together.

## Re-render the mockup

```bash
node tools/design/render-mockup.mjs          # every board and state, 2x, into docs/design/mockup/renders/
```

It needs Google Chrome (or Edge where headless is allowed; set `BROWSER_PATH` for another Chromium) and fails when a board's content is taller than the board, so clipping cannot be committed.

## Burn down the baseline

When a change removes a baselined violation, `python scripts/design-lint.py` fails until the baseline shrinks with it: run `python scripts/design-lint.py --update-baseline` in the same commit. The baseline never grows: `--update-baseline` refuses a higher count.
