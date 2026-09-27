---
schema_version: 1
id: CHANGEME-unique-kebab-id
domain: CHANGEME-NN-domain
status: draft
title: "TODO-NN -- CHANGEME Title"
depends_on: []
track: CHANGEME
---

# TODO-NN -- CHANGEME Title

> **Goal:** CHANGEME: one paragraph. What is true when this file is finished, in plain terms.

> [!IMPORTANT]
> **Current state (verified CHANGEME-YYYY-MM-DD):** CHANGEME: what exists RIGHT NOW, before this TODO runs. Name real files and real gaps.
<!-- claim: exists CHANGEME/path/that/exists -->

## Inputs

- [CHANGEME spec or capture](CHANGEME-path) -- what this TODO consumes from it
- -> XREF: CHANGEME DNN TNN §N -- the related work and what flows each way (reciprocate in the target file)

## Outcome

- CHANGEME: observable end state, not an activity.
- CHANGEME: a second end state.

**Adjacency:** CHANGEME: all=not-applicable (reason) or all nine keys exactly once, separated by semicolons.

**Adjacency rationale:** CHANGEME: the substantive decisions behind the line above, in prose.

## Implementation Order

| Order | Section | Deliverable | Depends On | Status |
| :---: | :-----: | ----------- | ---------- | :----: |
|   1   |   §1    | CHANGEME deliverable | -- |  [ ]   |
|   2   |   §2    | CHANGEME deliverable | §1 |  [ ]   |

---

## 1. CHANGEME Section Title

CHANGEME: one paragraph of context: why this section exists and what it must not break.

- [ ] CHANGEME micro-step in `backtick/path`. Done when: CHANGEME observable end state. Cheaper substitute: CHANGEME the wrong thing.
- [ ] Commit: `"CHANGEME: one-line commit message"`

**Test checkpoint:** CHANGEME: the falsifiable command or drive that proves this section. It must be able to fail.

## 2. CHANGEME Section Title

CHANGEME: one paragraph of context.

(UI sections also carry `**Fidelity:**`, `**Design:**`, `**Job:**`, `**Treatment:**`, and `**Chrome:**` blocks. The Design line cites at least one anchor of the approved mockup first, for example `**Design:** docs/design/mockup.md#result-card, docs/design/taskpane.md#result-card -- states: all in spec -- themes: n/a (both token sets apply through tokens.css) -- density: n/a (one density in a fixed-width task pane)`, and the section carries the mockup conformance item below, word for word, before its `Commit:` item; `python scripts/design-lint.py` refuses a UI section missing either. Host-bound sections carry a `**Needs:**` line from the closed list in `todo/README.md`, e.g. `**Needs:** Outlook client (sideload)`.)

(The mockup conformance item for UI sections:)
- [ ] Hold the built surface to the approved mockup: render it (sideloaded, or in the jsdom harness for a component), compare it with the anchors on this section's `**Design:**` line in `docs/design/mockup.md` and their renders under `docs/design/mockup/renders/`, use only design tokens (`docs/design/tokens.json`) and registry icons (`iconSvg()` from `src/ui/icons.ts`), and commit a capture of the result under `docs/captures/taskpane/`. Done when: `python scripts/design-lint.py` exits 0 with the baseline no larger, every difference from the mockup is fixed or recorded as a `**Design deviation:**` naming its follow-up section, and the capture is committed. Cheaper substitute that fails: building from the prose alone, which the capture comparison at review refuses.

- [ ] CHANGEME micro-step in `backtick/path`. Done when: CHANGEME observable end state.
- [ ] Commit: `"CHANGEME: one-line commit message"`

**Test checkpoint:** CHANGEME: the falsifiable proof.

## Verification

- [ ] `pwsh scripts/check-all.ps1` -- exits 0: production build, typecheck, lint, tests, manifest, TODO gates green
- [ ] `npx jest --ci` exits 0 with this file's test files reporting
- [ ] `python scripts/design-lint.py` exits 0 (the design gate: mockup citations, tokens, icons, and no new baseline entry)
- [ ] CHANGEME: file-level checks this file owes as a whole (API contract fixtures, captures refreshed and compared with `docs/design/mockup/renders/`, sideload smoke in both supported clients)
- [ ] `python scripts/todo-graph.py validate` clean
