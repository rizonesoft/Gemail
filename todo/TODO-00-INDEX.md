# Gemail -- TODO Index

The live execution plan for Gemail. Format spec: [README.md](./README.md). Ordered plan: [implementation-plan.md](./implementation-plan.md).

## How to use this tree

- **This file** carries domain order and the active TODOs. Keep it at that altitude: no checklists.
- **Each domain's `INDEX.md`** lists its own TODO files and is the place to look for scope within a domain. Ideas that are not planned work live in [`backlog.md`](./backlog.md), never in a domain.
- Give every topic **one canonical home**. Cross-link with XREFs instead of duplicating scope.
- Numbering is local to a domain (`TODO-01`, `TODO-02`) and never reused.

## What this plan is

Gemail is the Outlook add-in formerly called AI Compose (AI Email Writer, `ai-email-writer`), version 1.3.2 on Google Gemini when this plan was seeded on 2026-09-27. The operator's decisions that day: port Photon's runner system ("Photon"), rename to Gemail with a redirect for existing installs ("Full, with a redirect"), move to OpenRouter over `fetch` under the user's own key with a live model list ("BYO key, fetch, live models"), support new Outlook and Outlook on the web only ("New Outlook + web"), plan every improvement area and the selected features, keep the key on the device, no telemetry with the data-collection filter off by default, and keep AppSource and the unified manifest in the backlog. They are recorded in [`../AGENTS.md`](../AGENTS.md).

## Domain order

Domains are numbered in **allocation order**. `DNN TNN §N` cross-references encode the domain number. A new domain appends after the last one. **Execution order lives in the dependency graph**: `python scripts/todo-graph.py query ready`.

| No. | Domain | Phase | Purpose |
| :-: | ------ | :---: | ------- |
| 00 | [Workspace](./00-workspace/INDEX.md) | 0, 1 | Toolchain, the move from WSL to Windows, green gates, CI, the TODO runner, and the agent skills. |
| 01 | [Rebrand](./01-rebrand/INDEX.md) | 2 | The rename from AI Compose / AI Email Writer to Gemail, and the transition off the old Pages path. |
| 02 | [OpenRouter](./02-openrouter/INDEX.md) | 3, 4 | The provider migration from Google Gemini to OpenRouter: the fetch client, streaming, structured output, the model catalogue, and the cutover. |
| 03 | [Architecture](./03-architecture/INDEX.md) | 5, 6 | The task pane split into modules, shared UI helpers, the approved design in code, performance, and resilience. |
| 04 | [Security](./04-security/INDEX.md) | 7 | Output rendering, prompt injection, CSP, the API key, rate limiting, consent, and privacy documentation. |
| 05 | [Quality](./05-quality/INDEX.md) | 1, 2, 5, 8 | The test backbone, accessibility, the behavior defects found in the imported code, and the classic Outlook refusal. |
| 06 | [Features](./06-features/INDEX.md) | 9 | New user-facing features: settings upgrades, custom prompts and shortcuts, message context, dark mode and local stats. |
| 07 | [Release](./07-release/INDEX.md) | 10 | Manifests for new Outlook and the web, icons, the release process, the user guide, v2.0.0, and the clean-install acceptance. |
| 99 | [Manual](./99-manual/INDEX.md) | 99 | Operator-only steps no agent session can perform: accounts, keys, repository settings, artwork, and human checks. |

`99-manual` is numbered apart from the allocation sequence on purpose: it is the operator's phase, not a build area.

## Active TODOs

| TODO | Domain | Title |
| ---- | ------ | ----- |
| [TODO-01](./00-workspace/TODO-01-windows-move.md) | 00-workspace | Move to Windows and Restore the Live Add-in |
| [TODO-02](./00-workspace/TODO-02-green-gates.md) | 00-workspace | Green Gates on the Imported Tree |
| [TODO-03](./00-workspace/TODO-03-runner-wiring.md) | 00-workspace | Runner Wiring and the First Green Push |
| [TODO-04](./00-workspace/TODO-04-agent-skills.md) | 00-workspace | Agent Skills Consolidation |
| [TODO-01](./99-manual/TODO-01-operator-setup.md) | 99-manual | Operator Setup and Human Checks |

Every other TODO is listed in its domain's `INDEX.md`; the files above hold the rows that are ready first (Phase 0) and the operator's rows.
