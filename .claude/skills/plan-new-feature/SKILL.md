---
name: plan-new-feature
description: Plan a new Gemail feature, or a whole new task pane surface, from an idea to a distribution-ready TODO file -- job definition, competitor survey, full surface and behavior plan, finer details included. Use when a feature or an app needs creating from nothing.
---

# Plan New Feature

A feature planned as "a panel with the thing in it" ships as a demo with a version number, and an app planned as "a window with the features" ships as three demos. This skill exists to prevent that: it defines the job, surveys what the competition ships, and plans every surface, behavior, state, and string the feature needs to be whole, down to the tooltips, the empty states, and the undo entry.

It covers two sizes of the same work. A **feature** lands in an existing tab of the task pane or ribbon (a tone preset in Draft, a length control in Reply) or in `src/services/` when two features need it now. A **new surface** (a new tab, a new ribbon command, a new dialog) is a feature set with its own manifest entries, its own design spec, and its own user-guide page, planned the same way with the surface-level items in step 4 added.

## Workflow

### 1. Define the job

Write one paragraph: whose problem, in what situation, and what "done" looks like to them. Then write the non-goals: the adjacent problems this feature does not solve, so scope has a fence. Then search the tree (`add-todo`) for an existing section, file, or app that owns any of it; a feature that duplicates one is a defect at birth.

Record the working name, the one-line purpose (it will be quoted by the ribbon tooltip, the tab label, and the user guide), and the audience: a feature for someone answering fifty support emails a day and a feature for someone writing one careful message a week are specified differently.

Decide the home with a reason: the one feature module that needs it (`src/features/`), or `src/services/` because a second feature needs it now. "Might be shared one day" is not a reason; the day a second feature needs it, a section moves it.

### 2. Survey the competition

Find two or three applications that do this job today, from Microsoft Copilot in Outlook, Gmail's Help me write, Superhuman, Grammarly, Flowrite, and the leading AI add-ins in Microsoft AppSource, whichever genuinely do it. Use each one, and write the feature table: their surfaces, their behaviors, their finer details (empty states, failure messages, keyboard shortcuts, streaming and cancellation, first-run, presets, insert and replace behavior, what happens to the original text), and what each does badly. Every row names the version used. Where an application cannot be run here, cite its documentation page and say so in the row.

The table is the bar: the plan matches every detail that matters and names what beats each competitor, feature by feature. A plan written without touching the competition invents a market that does not exist.

### 3. Define the surfaces

Specify the feature control by control: the tool on the tool rail with its icon, cursor, and shortcut; its context toolbar or options bar with every control; the menu items and their shortcuts; panels and their docking; dialogs; the on-canvas handles, guides, and overlays; the Preferences page entries; the status strip text; and the log lines. For each surface name its controls, its strings, its states, and its empty, loading, busy, and failure presentations. No placeholder, no hardcoded string, no "details at build time": a builder who must invent a control inherits a gap, not a freedom.

Every surface names its capture home under `docs/captures/taskpane/`, its `Fidelity:` source, and a `**Design:**` line citing the `docs/design/mockup.md` anchors it builds to. A surface the mockup does not draw is designed in the operator's design artifact first (the `design-sync` skill adds the artboard and re-imports it), then cited; until then it cites `docs/design/mockup.md#surfaces-the-mockup-does-not-draw` plus the components it composes. Colors come from `docs/design/tokens.json` and icons from `docs/design/icons.md`; a new icon is drawn in the artifact and added to `assets/icons/src/` before a section uses it.

Decide document participation with a reason: if the feature changes a document it records an undo step for every edit, marks the document dirty, and survives save and reopen in every format that can carry it; if it cannot be carried by a format, the plan says what the save does instead (flatten, warn, or refuse) and why.

### 4. Define the behaviors

Every feature, no exceptions, plans its share of: settings keys with defaults through `src/features/settings.ts`, a debug-log line per user action that writes into a message or changes a setting, a preview before any write into the user's message and a way back to the original text, keyboard access that does not collide with Outlook's own shortcuts, performance on a long thread (name the size: a 40-message thread, a 50,000-character body) with the budget it must meet, streaming and cancellation for any model call, every OpenRouter failure mode (no key, invalid key, rate limit, credit exhausted, timeout, content refusal, offline), behavior in both supported clients (new Outlook and Outlook on the web) in read and compose mode, and the same-commit user-guide page under `docs/user/`. Anything genuinely not applicable carries a stated reason; silence is not a reason.

A **new surface** additionally plans: its manifest entries (`manifest.xml` and `manifest.dev.xml`, the ribbon control, icons at every size the manifest names), its webpack entry or lazy chunk, its design spec under `docs/design/`, its first-run and empty state, the Mailbox requirement set it needs and what it shows on a client below it, and what it shares with the other tabs through `src/services/` and `src/ui/` versus what it owns.

### 5. Define acceptance

Each section is born complete per `create-todo`: context, micro-step checklist with Done-when per item, Test checkpoint with a cheaper-substitute-that-fails line, Fidelity/Job/Treatment/Chrome on UI sections, Commit item. New behavior has no baseline, so every Test checkpoint drives the behavior and quotes it, including the failure path: no API key, a revoked key, a 429, a 402 credit error, a stream cut mid-response, an empty selection, a compose-only action in read mode. Logic is proven by Jest tests run with `npx jest`; every change to the OpenRouter request or response shape owes an API contract proof (`todo/README.md`) against a committed fixture; UI sections owe the gate card's launch smoke (`.claude/skills/process-todo-section/gates.md`) and their captures as checkpoint evidence.

### 6. Finer-details pass

Walk every section and confirm each of these is owned somewhere: tooltips on every icon-only control, with the shortcut in the tooltip; accessible names (AutomationProperties) on everything; logical tab order and full keyboard operation of every dialog; DPI scaling at 100, 150, and 200 percent and every theme the app ships; high contrast; reduced motion for animated feedback; modifier keys on canvas tools (Shift constrains, Alt from center, and so on, matched to the competitor norm the survey recorded); first-run; upgrade from a previous version's settings and presets; export formats that match the rendered view, including color profile and bit depth; confirmation texts naming what, how many, and how large; and refusal texts naming the action and what it needed. Anything unowned gets an item on its section now, not a wish for later.

### 7. Author, wire, validate, commit

Author the file through `create-todo` in the domain that owns the home step 1 chose (`06-features` for a feature, `03-architecture` for shared services), creating the domain with its `INDEX.md` when it does not exist yet. Manifest, release, and store items land in `07-release`, and the user guide beside them, each as sections XREFed both ways. Wire the plan rows with Depends On edges so `src/services/` dependencies sequence first and distribution items sequence after the behavior they ship, and place every section in a phase of `todo/implementation-plan.md`. A feature the operator asked for is operator-directed: its sections carry no Origin line and no cap limits them, so plan the whole feature, and file as backlog entries in `todo/backlog.md` only what the operator deferred. When a campaign invokes this skill for a feature it discovered on its own, every section carries `**Origin:** discovered run=<run id> <YYYY-MM-DD>` and counts against the run's cap, and what does not fit goes to the backlog (`todo/README.md`, "The budget and the backlog"). Then:

```bash
python scripts/todo-graph.py validate
python scripts/todo-graph.py plan --sync
python scripts/todo-graph.py plan --check
```

Commit as one `todo:` commit. Report the file, its sections, the competitor table with what beats each rival, the backlog entries it added, and the size line the Progress block now shows.

## Guardrails

- Do not plan without the job paragraph and the non-goals. A feature without a fence grows until it ships nothing.
- Do not skip the competitors. An unbeaten rival the plan never looked at beats it by default.
- Do not plan a second implementation of anything another feature or `src/services/` already owns, and do not plan into `src/services/` what only one feature needs.
- Do not leave a surface half-specified. Empty, loading, busy, and failure presentations are part of the surface.
- Do not plan an edit without its undo, or a document change without its save-and-reopen behavior.
- Do not file a "polish" section. Finer details live as items on the sections that own them.
- Do not invent competitor features. The table comes from using the competitors, and each row names the version used.
- Do not plan a feature that needs a server of our own, a second AI provider, or a client outside new Outlook and Outlook on the web without the operator deciding it first (`AGENTS.md`).
