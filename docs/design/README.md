# Gemail Design

The approved design and the machinery that holds the plan and the code to it.

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
| `node tools/design/icons.mjs --check` | check-all when `tools/design/node_modules` exists; CI after `D07 T01 §3` | A PNG or registry that no longer renders identically from its source |
| `review-todo-section` | every stamp | A surface whose capture does not match the mockup render it cites |

## The plan side

Every `todo/` section that builds or changes a surface carries a `**Design:**` line citing its mockup anchors and a conformance item (the template is in `.claude/skills/create-todo/todo-template.md`). `D03 T04` adopts the design in code (tokens, icons, the pane frame, the ribbon icons) and empties the baseline.
