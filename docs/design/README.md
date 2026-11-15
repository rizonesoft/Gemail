# Gemail Design

The approved design, **Fluent Native** (operator decision 2026-11-15, artifact https://claude.ai/artifact/Vc5xq9U5iRvq1AiZ1gm5YD), and the machinery that holds the plan and the code to it.

| File | What it is | Authority |
| --- | --- | --- |
| [`mockup.md`](./mockup.md) | Every artboard and component of the approved mockup, with renders and anchors | Layout and composition |
| [`mockup/`](./mockup/) | The imported artboards (`*.dc.html`, `canvas.json`), pinned by `source.json`, and their renders | The pictures behind `mockup.md` |
| [`tokens.json`](./tokens.json) | Every color (light and dark), font, size, space, radius, and duration | Values |
| [`icons.md`](./icons.md) | The icon catalog and rules; sources in `assets/icons/src/` | Icons |
| [`taskpane.md`](./taskpane.md) | Behavior and rules that are not visual (what a control does, accessibility, errors) | Behavior |
| [`EDITING.md`](./EDITING.md) | How to change any of the above | Process |
| `.lint-baseline.json` | Code that predates the gate and still breaks it; may only shrink | Debt |

When two of them disagree, the authority column decides, and the losing file is corrected in the same commit.

## What enforces it

| Gate | Where it runs | What it refuses |
| --- | --- | --- |
| `python scripts/design-lint.py` | `pwsh scripts/check-all.ps1`, the commit hook (`tools/githooks/pre-commit`), and CI (`.github/workflows/plan.yml`) | A surface section in `todo/` without a `docs/design/mockup.md#` citation or without its mockup conformance item; a hand-edited artboard; a stale render; a mockup color that is not a token; a malformed token file; an icon output that does not match its source; any new color literal, font declaration, inline `<svg>`, or pre-2.0 icon path in `src/` or the manifests |
| `python scripts/design-lint.py --self-test` | check-all and CI | A gate that no longer catches what it claims to |
| `python scripts/todo-graph.py validate` | the same three places | A `**Design:**` line whose anchor or file does not exist, a surface section without its Design, Job, Treatment, or Chrome lines |
| `node tools/design/icons.mjs --check` | check-all and CI (`.github/workflows/build.yml`) | A PNG that is not byte-identical to a fresh render of its source, or a stale registry (resvg is deterministic; verified identical on Windows and Linux) |
| `review-todo-section` | every stamp | A surface whose capture does not match the mockup render it cites |

## The contract

These hold for every surface and every change, and a section, a review, or a campaign that breaks one is wrong, not creative:

1. **One origin.** The design changes only in the operator's artifact and reaches the repository only through the `design-sync` skill. Nothing under `mockup/`, `assets/icons/png/`, `src/ui/icons.ts`, or `assets/icons/manifest.json` is edited by hand.
2. **The operator decides.** A new look, a new component, a moved control, a new color, or a replaced design is the operator's decision, recorded with its date. An unattended run never changes the design: it builds what is drawn, composes an undrawn surface only from drawn components, and files anything else for the operator.
3. **Tokens only.** A surface takes every color, font, size, space, and radius from `tokens.json`. Both themes carry the same keys, and every text pair passes WCAG 2.1 AA (4.5:1) in both.
4. **Registry icons only.** A pane icon comes from `iconSvg()`; a ribbon or menu icon is a PNG built from its source. No inline `<svg>`, no icon font, no hand-resized PNG.
5. **The frame is fixed.** Header and tab bar at the top, scrolling content, the action bar pinned at the bottom with the primary action in it.
6. **Purple means AI, and the app icon is a letter.** Purple marks only the spark and the model tags; the app icon is a written letter with the spark, never an envelope.
7. **A capture proves it.** A surface section ships with a capture under `docs/captures/taskpane/` compared with the render it cites; a difference is fixed or recorded as a `**Design deviation:**` with its follow-up section.
8. **Authority.** `tokens.json` decides a value, `mockup.md` and its renders decide layout and composition, `taskpane.md` decides behavior; the losing file is corrected in the same commit.

## The plan side

Every `todo/` section that builds or changes a surface carries a `**Design:**` line citing its mockup anchors and a conformance item (the template is in `.claude/skills/create-todo/todo-template.md`). `D03 T04` adopts the design in code (tokens, icons, the pane frame, the ribbon icons) and empties the baseline.
