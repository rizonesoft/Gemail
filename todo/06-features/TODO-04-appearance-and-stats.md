---
schema_version: 1
id: appearance-and-stats
domain: 06-features
status: draft
title: "TODO-04 -- Dark Mode and Local Usage Stats"
depends_on: []
---

# TODO-04 -- Dark Mode and Local Usage Stats

> **Goal:** The task pane follows the Office theme as it changes (and the system color scheme where Office reports none), every color on every surface comes from a token with a dark value, the dark theme passes the same contrast check as the light one, and the user can see how much they have used Gemail (counts per feature, tokens, and cost) from statistics that are kept on the device, never sent anywhere, and can be reset.

> [!IMPORTANT]
> **Current state (verified 2026-09-27):** `src/taskpane/taskpane.ts` reads `Office.context.officeTheme` once at startup (line 1076) and sets `data-theme="dark"` on `<html>` when the body background is dark; there is no `OfficeThemeChanged` handler and no `prefers-color-scheme` rule in `src/styles/main.css` or `src/taskpane/taskpane.css`, so a theme change needs a reload. `main.css` has one `[data-theme="dark"]` block that remaps surfaces and text but not the brand, success, or error colors. Literal colors bypass the tokens: the loading overlay `rgba(255,255,255,0.85)` and the diff colors `#ffeef0`, `#b31d28`, `#e6ffec`, `#22863a` in `taskpane.css`, and the score colors `#22c55e`, `#eab308`, `#ef4444` in `taskpane.ts` line 235. Nothing records usage, and the operator decided on 2026-09-27 that there is no telemetry ("No telemetry, ZDR off"), so any statistics stay local.
<!-- claim: count "officeTheme" src/taskpane/taskpane.ts = 1 -->
<!-- claim: count "prefers-color-scheme" src/styles/main.css = 0 -->
<!-- claim: count "#ffeef0" src/taskpane/taskpane.css = 1 -->
<!-- claim: count "#eab308" src/taskpane/taskpane.ts = 1 -->
<!-- claim: absent src/features/usage-stats.ts -->

## Inputs

- [`src/styles/main.css`](../../src/styles/main.css) -- the `@theme` tokens and the dark block §1 completes
- [`src/taskpane/taskpane.css`](../../src/taskpane/taskpane.css), [`src/taskpane/taskpane.ts`](../../src/taskpane/taskpane.ts) -- the literal colors §1 moves to tokens
- [`docs/design/taskpane.md`](../../docs/design/taskpane.md) -- the Tokens and Themes sections §1 makes true
- Microsoft Learn, "Office.EventType" (https://learn.microsoft.com/javascript/api/office/office.eventtype) and "Use Office themes in your Office Add-ins" (https://learn.microsoft.com/office/dev/add-ins/design/add-in-color-schemes) -- `OfficeThemeChanged` and `officeTheme` §1 uses
- -> XREF: D03 T01 §1 -- §1 applies the theme through the shared UI helpers the split created
- -> XREF: D05 T02 §5 -- §2 runs the contrast script the accessibility TODO ships, over the dark tokens
- -> XREF: D06 T01 §5 -- §3 accumulates the per-request cost that section returns
- -> XREF: D07 T01 §5 -- the user guide documents the theme behavior and the usage page
- -> XREF: D03 T04 §1 -- the generated token stylesheet with its dark set, and D03 T04 §4 that removed every color literal

## Outcome

- Switching the Office theme in new Outlook or Outlook on the web restyles the open pane within a second, without a reload; with no Office theme reported, the pane follows `prefers-color-scheme`.
- `grep -rnE "#[0-9a-fA-F]{3,8}\b|rgba?\(" src/taskpane src/ui src/features --include=*.ts --include=*.css` prints nothing outside the token definitions in `src/styles/main.css`.
- `node scripts/contrast-check.js --theme dark` exits 0 with every text pair at 4.5:1 or better.
- A **Usage** view in Settings shows, per feature, the number of runs, total tokens, and total cost since a start date, with **Reset** behind a confirm; the stats live in `localStorage` only and no code path sends them.

**Adjacency:** list=not-applicable (stats are a fixed per-feature table, not a collection); document=not-applicable (nothing is exported from the usage view); settings=not-applicable (the theme follows Outlook own appearance choice and Gemail adds no second switch); reporting=applicable @ D06 T04 §3; notifications=not-applicable (a theme switch and a counter update are silent by design); permissions=not-applicable (no refusal path: reading the theme and writing local counters cannot be refused); audit=not-applicable (usage counters are the audit, local to the device); exchange=not-applicable (nothing is imported or exported); reverse=applicable @ D06 T04 §3

## Implementation Order

| Order | Section | Deliverable                 | Depends On     | Status |
| :---: | :-----: | --------------------------- | -------------- | :----: |
|   1   |   §1    | Follow the Office theme live | D03 T01 §1, D03 T04 §1, D03 T04 §4 |  [ ]   |
|   2   |   §2    | Dark theme contrast         | §1, D05 T02 §5 |  [ ]   |
|   3   |   §3    | Local usage stats           | D06 T01 §5     |  [ ]   |

---

## 1. Follow the Office Theme Live

The operator selected dark mode on 2026-09-27. New Outlook and Outlook on the web both report the Office theme and fire `OfficeThemeChanged` when it changes; the pane must follow without a reload, and every color must come from a token that has a dark value, or the dark theme shows white overlays and unreadable diff colors.

**Fidelity:** Gemail task pane in light and dark, every tab -- docs/captures/taskpane/themes/. Paired light and dark captures of each tab, the result card, the diff, and the loading overlay.
**Design:** docs/design/mockup.md#dark-theme, docs/design/taskpane.md#themes, docs/design/taskpane.md#tokens -- states: light, dark, switching -- themes: n/a (the Design grammar names four themes and Gemail ships two, light and dark, as its Themes section states) -- density: n/a (one density in a fixed-width task pane)
**Job:** The user can use Gemail in dark mode that matches Outlook. Consumer: none: this surface is the consumer.
**Treatment:** a `setTheme("light" | "dark")` helper sets `data-theme` on `<html>`; it runs at start, on `OfficeThemeChanged`, and on `prefers-color-scheme` changes when Office reports no theme. Cheaper substitute that fails the checkpoint: a `prefers-color-scheme` media query alone, which ignores Outlook's own theme switch.
**Chrome:** consume the `@theme` tokens in `src/styles/main.css` and the shared UI helpers in `src/ui/`; do not add a second theme switch or a literal color.
**Needs:** Outlook client (sideload)
**Requires:** display-session -- the checkpoint switches the Outlook theme in a sideloaded new Outlook and Outlook on the web window

- [ ] Add `src/ui/theme.ts` with `resolveTheme(officeTheme, prefersDark)` (luminance of `bodyBackgroundColor` below 0.5 means dark) and `setTheme()`. Done when: jsdom tests cover a dark Office theme, a light one, and none with `prefersDark` true and false.
- [ ] Register `Office.context.mailbox.addHandlerAsync(Office.EventType.OfficeThemeChanged, ...)` when `Office.context.requirements.isSetSupported("Mailbox", "1.13")` is true (the handler's documented requirement), else listen to `matchMedia("(prefers-color-scheme: dark)")`. Done when: mock tests assert the handler on a 1.13 client and the media listener otherwise. Source: https://learn.microsoft.com/javascript/api/office/office.eventtype
- [ ] Confirm every pane color is a token with a dark value: `python scripts/design-lint.py` reports no `color-literal` baseline (`D03 T04 §4`) and `src/styles/tokens.css` defines every `--gm-color-*` under `[data-theme="dark"]`. Done when: both hold and a jsdom test asserts `setTheme("dark")` sets `data-theme="dark"` on `document.documentElement`. **Corrected 2026-09-27:** was "Add tokens `--color-aic-overlay`, ... to `src/styles/main.css` with light and dark values, and replace the literals"; the design import put both token sets in `docs/design/tokens.json` and `D03 T04 §4` replaced the literals.
- [ ] Make `setTheme()` in `src/ui/theme.ts` switch the token set by toggling `data-theme` on `document.documentElement`, which `src/styles/tokens.css` keys its dark block on. Done when: a jsdom test asserts the computed `--gm-color-brand` is `#479ef5` after `setTheme("dark")` and `#0f6cbd` after `setTheme("light")`, and `--gm-color-brandFill` is `#115ea3` and `#0f6cbd`. **Corrected 2026-11-15:** the values were `#4ba3ff` and `#1668c9`, the 2026-09-27 design's brand. **Corrected 2026-09-27:** was "Remap the brand, success, and error tokens in the dark block"; the dark values are defined in `docs/design/tokens.json` and generated by `D03 T04 §1`.
- [ ] Update `docs/design/taskpane.md#themes` and the Tokens table to the shipped behavior, and remove the *(target)* marker. Done when: the Themes section describes the live switch.
- [ ] Hold the built surface to the approved mockup: render it (sideloaded, or in the jsdom harness for a component), compare it with the anchors on this section's `**Design:**` line in `docs/design/mockup.md` and their renders under `docs/design/mockup/renders/`, use only design tokens (`docs/design/tokens.json`) and registry icons (`iconSvg()` from `src/ui/icons.ts`), and commit a capture of the result under `docs/captures/taskpane/`. Done when: `python scripts/design-lint.py` exits 0 with the baseline no larger, every difference from the mockup is fixed or recorded as a `**Design deviation:**` naming its follow-up section, and the capture is committed. Cheaper substitute that fails: building from the prose alone, which the capture comparison at review refuses.
- [ ] Commit: `"theme: follow the Office theme live, with every color a token"`

**Test checkpoint:** `npx jest src/ui/theme.test.ts` passes; the Outcome grep prints nothing; a driven run in new Outlook switches Settings > Appearance from light to dark with the pane open and the pane restyles without a reload (before and after captures committed under `docs/captures/taskpane/themes/`). Cheaper substitute that fails: setting the theme once at startup as 1.3.2 does, which the live-switch capture shows stale.

## 2. Dark Theme Contrast

Dark themes fail contrast silently: a secondary text color that reads well on white can drop below 3:1 on a dark surface. The contrast script of `D05 T02 §5` checks the light tokens; this section runs it over the dark tokens and fixes what fails.

- [ ] Extend `scripts/contrast-check.js` with `--theme dark`, reading the `[data-theme="dark"]` block of `src/styles/main.css` and checking the same pairs as the light run. Done when: `node scripts/contrast-check.js --theme dark` prints one line per pair with its ratio.
- [ ] Adjust every dark token that fails (4.5:1 for text, 3:1 for large text, focus rings, and control borders) and record each old and new value in the commit body. Done when: the dark run exits 0.
- [ ] Add the dark run beside the light run in `scripts/check-all.ps1` and `.github/workflows/build.yml`. Done when: both files name `--theme dark` and `pwsh scripts/check-all.ps1` shows the gate.
- [ ] Commit: `"theme: dark tokens pass the contrast check"`

**Test checkpoint:** `node scripts/contrast-check.js --theme dark` and `node scripts/contrast-check.js --theme light` both exit 0; lowering `--color-aic-text-secondary` in the dark block to `#444a55` in a scratch copy makes the dark run exit 1 naming that pair. Cheaper substitute that fails: an eyeball check of the dark captures, which the scratch probe shows cannot catch a 2.9:1 pair.

## 3. Local Usage Stats

The legacy `TODO.md` asked for "local-only stats (emails drafted, summaries generated)", and the operator's no-telemetry decision makes local the only kind allowed. Each completed request adds to per-feature counters with its tokens and cost from `D06 T01 §5`; the numbers never leave the device and are not part of roaming or of the settings export.

**Fidelity:** Gemail Settings panel, "Usage" group below Backup -- docs/captures/taskpane/settings/. A small table: feature, runs, tokens, cost; a "since" date and a Reset link.
**Design:** docs/design/mockup.md#surfaces-the-mockup-does-not-draw, docs/design/mockup.md#settings, docs/design/taskpane.md#settings-panel, docs/design/taskpane.md#dialogs -- states: empty, populated, reset confirm -- themes: n/a (the Design grammar names four themes and Gemail ships two, light and dark, as its Themes section states) -- density: n/a (one density in a fixed-width task pane)
**Job:** The user can see how much they have used each feature and what it cost. Consumer: none: this surface is the consumer.
**Treatment:** a table per feature (Draft, Reply, Summarize, Improve, Extract, Translate, Custom prompts, Ribbon) with runs, tokens, and cost, a total row, "Since <date>", and Reset behind the inline confirm; an empty state reads "No usage yet on this device." Cheaper substitute that fails the checkpoint: a single total counter, which fails the per-feature test.
**Chrome:** consume the per-request `usage` the facade returns, `formatCost` from `D06 T01 §5`, and the inline dialog; do not add a network call or a second cost formatter.
**Needs:** Outlook client (sideload)
**Requires:** display-session -- the checkpoint runs features and reads the Usage table in a sideloaded Outlook on the web window

- [ ] Add `src/features/usage-stats.ts` with `recordUsage(feature, usage)`, `getUsage()`, and `resetUsage()` over localStorage key `gemail_usage` (`{ since, byFeature: { [feature]: { runs, promptTokens, completionTokens, cost } } }`). Done when: tests cover record, sum, reset, and a malformed stored value.
- [ ] Call `recordUsage` once per completed request in the facade (`src/services/ai.ts`), including streamed requests on their final chunk and stopped streams with the usage received so far. Done when: facade tests assert one record per call and none for a request that failed before any response.
- [ ] Add a test asserting `gemail_usage` is excluded from `writeRoaming` payloads and from `exportSettings()`, and that `usage-stats.ts` imports nothing from `src/services/openrouter.ts` or `fetch`. Done when: the test fails if either export includes the key.
- [ ] Render the Usage group, the local usage report, in the Settings panel module with the empty state, the total row, and Reset with its confirm, which can be canceled. Done when: a jsdom test asserts the table, the empty state, and that cancel leaves the counters unchanged.
- [ ] Hold the built surface to the approved mockup: render it (sideloaded, or in the jsdom harness for a component), compare it with the anchors on this section's `**Design:**` line in `docs/design/mockup.md` and their renders under `docs/design/mockup/renders/`, use only design tokens (`docs/design/tokens.json`) and registry icons (`iconSvg()` from `src/ui/icons.ts`), and commit a capture of the result under `docs/captures/taskpane/`. Done when: `python scripts/design-lint.py` exits 0 with the baseline no larger, every difference from the mockup is fixed or recorded as a `**Design deviation:**` naming its follow-up section, and the capture is committed. Cheaper substitute that fails: building from the prose alone, which the capture comparison at review refuses.
- [ ] Commit: `"usage: local usage stats per feature, never sent"`

**Test checkpoint:** `npx jest src/features/usage-stats.test.ts src/services/ai.test.ts -t "usage"` passes, including the not-exported and not-roamed tests; a driven run drafts two emails and summarizes one, the table shows Draft 2 and Summarize 1 with costs summing to the result-card costs, and the network log of the session shows no request carrying the counters. Cheaper substitute that fails: counting button clicks, which counts failed requests and fails the facade test.

## Verification

- [ ] `pwsh scripts/check-all.ps1` -- exits 0: production build, typecheck, lint, tests, manifest, the light and dark contrast checks, TODO gates green
- [ ] `npx jest --ci` exits 0 with `theme` and `usage-stats` tests reporting
- [ ] A sideload smoke in new Outlook and Outlook on the web: switch the theme live and read the Usage table after three requests
