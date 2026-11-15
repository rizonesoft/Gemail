---
schema_version: 1
id: design-adoption
domain: 03-architecture
status: draft
title: "TODO-04 -- Design Adoption"
depends_on: []
---

# TODO-04 -- Design Adoption

> **Goal:** The code wears the approved design. Every color, font, and spacing value the pane uses comes from `docs/design/tokens.json` through one generated stylesheet; every icon in the pane comes from the generated registry `src/ui/icons.ts`; the pane frame (header, tab bar, and the action bar pinned at the bottom with the footer line) matches the Reply artboard; the reply settings row, the folded instruction summary, the result card, and the Settings cards with their sticky Save bar are built once and shared; the ribbon and the manifests use the icons rendered from `assets/icons/src/`; and `docs/design/.lint-baseline.json` is empty, so `python scripts/design-lint.py` holds the code to the design with nothing grandfathered.

> [!IMPORTANT]
> **Current state (verified 2026-11-15):** The operator replaced the approved design on 2026-11-15 with the Fluent Native direction ("Most definately A") and it was imported the same day through `design-sync`: the six artboards under `docs/design/mockup/` (pinned to artifact version `1794766595-aa03` by `docs/design/mockup/source.json`) with renders under `docs/design/mockup/renders/`, the tokens in `docs/design/tokens.json` (brand `#0f6cbd` with a separate `brandFill`, tertiary text `#6b6b6b`, Fluent 2's type ramp in Segoe UI Variable, radius 4, 8, and 12, a light and a dark set with the same keys), 56 icon sources in `assets/icons/src/` redrawn for it (a letter-with-spark app icon, ribbon and menu icons on one document base with a 16 px redraw each, pane glyphs at a 1.5 px stroke), 25 rendered PNGs in `assets/icons/png/`, and the generated registry `src/ui/icons.ts` with 42 pane icons behind `iconSvg()`. The design also changed the pane's composition: the primary action sits in an action bar pinned at the bottom (§6), tone, length, and language are one row of dropdown buttons and the form folds into an instruction summary after a result (§7), Settings is grouped cards over a sticky Save bar (§8), and every control has five interaction states from tokens (§9). None of it is used by the add-in yet: `src/styles/main.css` still defines `--font-aic` as Poppins and the old `--color-aic-*` values (the brand is `#3b9eff`), `src/taskpane/taskpane.html` loads Google Fonts and carries 45 inline `<svg>` elements, and both manifests point at `assets/icon-*.png` and `assets/tool-icons/*.png`. `python scripts/design-lint.py` baselines what this file burns down: 54 color literals, 47 inline SVGs, 6 font declarations, and 88 legacy icon references.
<!-- claim: exists docs/design/tokens.json -->
<!-- claim: exists src/ui/icons.ts -->
<!-- claim: exists docs/design/mockup/source.json -->
<!-- claim: absent src/styles/tokens.css -->
<!-- claim: count "<svg" src/taskpane/taskpane.html = 45 -->
<!-- claim: count "Poppins" src/styles/main.css = 1 -->
<!-- claim: count "fonts\.googleapis\.com" src/taskpane/taskpane.html = 2 -->
<!-- claim: count "tool-icons/" manifest.xml = 36 -->

## Inputs

- [`docs/design/mockup.md`](../../docs/design/mockup.md) -- the approved design, its anchors, and how it binds the plan
- [`docs/design/tokens.json`](../../docs/design/tokens.json) -- the token values §1 generates the stylesheet from
- [`docs/design/icons.md`](../../docs/design/icons.md), [`src/ui/icons.ts`](../../src/ui/icons.ts) -- the icon catalog and the registry §2 wires in
- [`assets/icons/png/`](../../assets/icons/png/) -- the rendered ribbon and app icons §5 points the manifests at
- [`scripts/design-lint.py`](../../scripts/design-lint.py), [`docs/design/.lint-baseline.json`](../../docs/design/.lint-baseline.json) -- the gate and the baseline every section here shrinks
- -> XREF: D00 T02 §3 -- §1 edits stylesheets only after lint is green, so the Prettier pass does not rewrite the same lines
- -> XREF: D03 T01 §1 -- §2 hydrates icons through the shared UI helpers in `src/ui/` that section creates
- -> XREF: D01 T01 §2 -- §5 swaps the icon URLs in the manifests after the rename has settled their names
- -> XREF: D04 T01 §3 -- consumes §1: with no web font left, the policy allows no font host
- -> XREF: D05 T02 §5 -- consumes §1: the contrast check reads the tokens §1 wires in
- -> XREF: D06 T04 §1 -- consumes §1 and §4: the live theme switch toggles the token sets §1 generates
- -> XREF: D07 T01 §1 -- consumes §5: the asset check and the rename of the old grammar icon read the manifests §5 rewrites
- -> XREF: D03 T01 §5 -- §6 and §8 rework the panel modules and the Settings panel that section extracts
- -> XREF: D03 T02 §4 -- consumes §6: while streaming, **Stop** takes the action bar's primary slot
- -> XREF: D05 T03 §1 -- consumes §6: **Replace selection** is the action bar's primary action for Improve
- -> XREF: D06 T02 §3 -- consumes §6: `Ctrl+Enter` runs whatever the action bar's primary button currently is
- -> XREF: D06 T01 §1 -- consumes §8: the creativity and length settings are rows of the Writing card
- -> XREF: D05 T02 §2 -- consumes §9: the keyboard work relies on the focus ring §9 puts on every control

## Outcome

- `src/styles/tokens.css` is generated from `docs/design/tokens.json` by `node tools/design/tokens.mjs`, defines every token as a `--gm-*` custom property for light and dark, and `python scripts/design-lint.py` refuses a stale copy.
- `src/taskpane/taskpane.html` loads no web font and contains no `<svg>`; every icon is rendered by `iconSvg()`.
- The header, tab bar, and footer line match `docs/design/mockup.md#header`, `#tab-bar`, and `#footer`, with five tabs in read mode and four in compose mode, and the capture committed under `docs/captures/taskpane/`.
- Every feature's primary action, its insert actions, and **Stop** live in one action bar pinned at the bottom of the pane (`docs/design/mockup.md#action-bar`), driven by one controller in `src/ui/`, and no panel carries a primary button of its own.
- Tone, length, and language are one row of dropdown buttons shared by Reply and Draft, the form folds into an instruction summary when a result arrives, and the result card matches `docs/design/mockup.md#result-card`.
- Settings is grouped cards with the Rules row, the privacy card, and a sticky **Save settings** bar that counts unsaved changes (`docs/design/mockup.md#settings`).
- Every button, tab, dropdown, link, and input shows the rest, hover, pressed, focus, and disabled states of `docs/design/mockup.md#interaction-states` in both themes, from one stylesheet.
- Both manifests reference only `assets/icons/png/` for images, and `assets/tool-icons/` and `assets/icon-*.png` are gone.
- `docs/design/.lint-baseline.json` has no entries, so any new color literal, font declaration, inline SVG, or legacy icon path fails the commit hook and CI.

**Adjacency:** list=not-applicable (no records to browse: this file restyles existing surfaces); document=not-applicable (nothing printed or exported); settings=not-applicable (no tunable value is added: §8 regroups the existing settings and only counts unsaved changes; the theme switch is D06 T04 §1); reporting=not-applicable (no summaries); notifications=not-applicable (no notification is added; the existing status and error messages only change color through the tokens of §1 and §4, and their mockup styling belongs to D03 T03 §1); permissions=not-applicable (no refusal path changes); audit=not-applicable (no write changes); exchange=not-applicable (no import or export); reverse=not-applicable (styling has no create to reverse)

## Implementation Order

| Order | Section | Deliverable                                     | Depends On  | Status |
| :---: | :-----: | ----------------------------------------------- | ----------- | :----: |
|   1   |   §1    | Tokens and the system font in the stylesheet    | D00 T02 §3  |  [ ]   |
|   2   |   §2    | Every pane icon from the registry               | D03 T01 §1  |  [ ]   |
|   3   |   §3    | Header, tab bar, and footer from the mockup     | §1, §2, D03 T01 §2 |  [ ]   |
|   4   |   §4    | No color literal left in the pane               | §1          |  [ ]   |
|   5   |   §5    | Ribbon and app icons from the icon set          | D01 T01 §2  |  [ ]   |
|   6   |   §6    | The action bar holds every primary action       | §3, D03 T01 §5 |  [ ]   |
|   7   |   §7    | Reply settings row, instruction summary, and result card | §6 |  [ ]   |
|   8   |   §8    | Settings as cards with a sticky Save bar        | §3, D03 T01 §5 |  [ ]   |
|   9   |   §9    | Five interaction states on every control        | §6, §7, §8  |  [ ]   |

---

## 1. Tokens and the System Font in the Stylesheet

The tokens exist as data; the pane still paints with the old values. This section generates one stylesheet from `docs/design/tokens.json`, points the existing `--color-aic-*` names at it so no component changes in this commit, and drops Poppins and Google Fonts for the system font the operator chose (2026-09-27: "Yes, Segoe UI Variable").

- [ ] Add `tools/design/tokens.mjs` that reads `docs/design/tokens.json` and writes `src/styles/tokens.css`: `:root` with every light color as `--gm-color-<key>`, the font, size, space, radius, and motion tokens as `--gm-<group>-<key>`, and `[data-theme="dark"]` with every dark color, headed by a "GENERATED, do not edit" comment. Done when: `node tools/design/tokens.mjs` writes the file and running it twice leaves `git diff` empty.
- [ ] Add a `--check` mode to `tools/design/tokens.mjs` and a freshness check to `scripts/design-lint.py` (the sha256 of `docs/design/tokens.json` recorded in the generated header must match the file), with a self-test case. Done when: editing one token value without regenerating makes `python scripts/design-lint.py` exit 1 naming `src/styles/tokens.css`, and `python scripts/design-lint.py --self-test` reports the new case.
- [ ] Import `tokens.css` first in `src/styles/main.css` and redefine each `--color-aic-*` and `--font-aic` in the `@theme` block as `var(--gm-...)` of its token (brand to `--gm-color-brand`, text-tertiary to `--gm-color-textTertiary`, and so on). Done when: `grep -c "#[0-9a-fA-F]\{6\}" src/styles/main.css` prints `0` and `npm run build` exits 0.
- [ ] Remove the Google Fonts `<link>` elements from `src/taskpane/taskpane.html`. Done when: `grep -c "fonts.googleapis.com\|fonts.gstatic.com" src/taskpane/taskpane.html` prints `0`.
- [ ] Shrink the baseline: `python scripts/design-lint.py --update-baseline`. Done when: the `color-literal` entry for `src/styles/main.css` and the `font-family` entries are gone from `docs/design/.lint-baseline.json`, and `python scripts/design-lint.py` exits 0.
- [ ] Commit: `"design: generate the token stylesheet and use the system font"`

**Test checkpoint:** `node tools/design/tokens.mjs --check` and `python scripts/design-lint.py` exit 0; `npm run build` exits 0; the built `dist/taskpane.html` contains no `fonts.googleapis.com`; changing `color.light.brand` in `docs/design/tokens.json` without regenerating makes `python scripts/design-lint.py` exit 1. Cheaper substitute that fails: hand-editing the hex values in `main.css`, which leaves `tokens.css` absent and fails the freshness check.

## 2. Every Pane Icon From the Registry

The pane draws its icons as 45 hand-pasted inline SVGs in `taskpane.html` and two in `taskpane.ts`; the approved glyphs live in the registry. This section replaces every one with a placeholder the registry fills, so an icon has exactly one source.

- [ ] Add `hydrateIcons(root: ParentNode)` to `src/ui/icons-dom.ts`: for each element with `data-icon="<name>"` it sets `innerHTML` to `iconSvg(name, { size, label })` from `data-icon-size` and `data-icon-label`, and throws naming the element when the name is not an `IconName`. Done when: a jsdom test in `src/ui/icons-dom.test.ts` hydrates a labelled and a decorative icon and asserts the `role`, `aria-label`, and `aria-hidden` attributes, and an unknown name throws.
- [ ] Replace each inline `<svg>` in `src/taskpane/taskpane.html` with `<span class="gm-icon" data-icon="<name>"></span>`, choosing the registry name from `docs/design/icons.md` (settings, reply, draft, copy, and so on), and call `hydrateIcons(document)` first in `Office.onReady`. Done when: `grep -c "<svg" src/taskpane/taskpane.html` prints `0` and every `data-icon` value is an `IconName` (the jsdom test loads the real HTML and hydrates it without throwing).
- [ ] Replace the two inline SVG strings in `src/taskpane/taskpane.ts` with `iconSvg()` calls. Done when: `grep -c "<svg" src/taskpane/taskpane.ts` prints `0`.
- [ ] Style `.gm-icon` (inline-flex, `currentColor`, 20 px) and `.gm-icon-accent` (`stroke: var(--gm-color-aiIcon)`) in `src/taskpane/taskpane.css`. Done when: the spark accent follows the theme in both token sets.
- [ ] Shrink the baseline with `python scripts/design-lint.py --update-baseline`. Done when: the `inline-svg` rule has no entries.
- [ ] Commit: `"design: every pane icon from the registry"`

**Test checkpoint:** `npx jest src/ui/icons-dom.test.ts` passes, including the case that hydrates the real `taskpane.html`; `python scripts/design-lint.py` exits 0 with an empty `inline-svg` baseline; a sideloaded pane shows every former icon (captures before and after under `docs/captures/taskpane/icons/`). Cheaper substitute that fails: copying the registry's SVG markup into the HTML, which the `inline-svg` rule counts and refuses.

## 3. Header, Tab Bar, and Footer From the Mockup

The pane's frame is the part every feature shares: today it is two text tabs, three icon-only buttons, and a "More features" dropdown, with Settings and Rules as tabs. The approved Reply artboard puts Settings in the header, labelled icon tabs in the bar (five in read mode, four in compose mode), and the model line at the foot of the pane. This section rebuilds the frame as three bands (fixed header and tabs, scrolling content, a fixed bottom band that holds the footer line and that §6 turns into the action bar); the panels inside it stay as they are. **Corrected 2026-11-15:** was the 2026-09-27 frame (a 28 px mark, five tabs in both modes, a filled glyph with an underline, Rules as a Settings section); the Fluent Native design the operator approved on 2026-11-15 changed the header and tab metrics, gave compose mode its own four tabs, and pinned the footer inside a bottom band.

**Fidelity:** Gemail task pane frame (header, tab bar, footer line) -- docs/captures/taskpane/frame/. Order, spacing, labels, and icons match the Reply and Improve artboard renders; deviations only through a Design deviation line.

**Design:** docs/design/mockup.md#header, docs/design/mockup.md#tab-bar, docs/design/mockup.md#footer, docs/design/mockup.md#design-language, docs/design/taskpane.md#layout -- states: rest, active, hover, focus, read, compose -- themes: n/a (both token sets apply through tokens.css; the live switch is D06 T04 §1) -- density: n/a (one density in a fixed-width task pane)

**Job:** an Outlook user can reach every feature and Settings in one click from any tab, and see which model is answering. Consumer: none: this surface is the consumer.

**Treatment:** a 48 px header, a 52 px tab bar with a 20 px icon over a 12 px label, the tinted icon and a 2 px indicator on the active tab, five tabs when reading and four when composing, Settings as a header icon button, and the model line pinned at the bottom. Cheaper substitute that fails the checkpoint: restyling the old two-tab bar and dropdown, which the capture comparison against `docs/design/mockup/renders/Reply.png` refuses.

**Chrome:** consume `iconSvg()` from `src/ui/icons.ts`, the token stylesheet from §1, and the tab controller from `src/taskpane/tabs.ts`. Do not invent a second tab controller or icon source.

**Needs:** Outlook client (sideload)

**Requires:** display-session -- the frame is proven by a sideloaded capture compared with the mockup render, which needs a window

- [ ] Make the pane three bands in `src/taskpane/taskpane.html` and `src/taskpane/taskpane.css`: `#app-header` and the tab bar fixed at the top, `#app-body` as the only scrolling element, and `#app-bottom` fixed at the bottom on `--gm-color-bg` with a 1 px `--gm-color-border` top rule. Done when: a jsdom test asserts the three elements in that order and that only `#app-body` has `overflow-y: auto`, and at 320 px wide nothing scrolls horizontally.
- [ ] Rebuild the header to 48 px with the app mark (`assets/icons/png/app/gemail-32.png` at 24 px), the name **Gemail** in the subtitle size, and a Settings icon button (`data-icon="settings"`, `aria-label="Settings"`, 36 px). Done when: the header has exactly those three children.
- [ ] Rebuild the tab bar to icon-over-label tabs, 52 px tall: **Reply**, **Draft**, **Summarize**, **Improve**, **More** in read mode and **Draft**, **Improve**, **Translate**, **More** in compose mode, chosen from `getItemMode()` at start and on `ItemChanged`; move Summarize and Improve out of the dropdown; **More** lists the features that have no tab in the current mode. Done when: `src/taskpane/tabs.ts` switches every tab of both sets, and jsdom tests assert the five labels in read mode and the four in compose mode, in order.
- [ ] Show the `-filled` icon, `--gm-color-brand`, a semibold label, and a 2 px `--gm-color-brand` indicator on the bottom edge of the active tab from `switchTab()`, and the regular icon in `--gm-color-textSecondary` at rest. Done when: the jsdom test asserts the active tab's icon is the `-filled` glyph after each switch.
- [ ] Remove `#tab-rules` and reach the Rules panel from Settings instead (a plain link at the end of the Settings panel until §8 builds the Writing card's **Rules** row). Done when: `grep -c 'id="tab-rules"' src/taskpane/taskpane.html` prints `0` and the rules still save (the existing rules test passes).
- [ ] Add the footer line as the last row of `#app-bottom`: `<display name> via OpenRouter` with a **Change** link that opens Settings, and the version from `#app-version` on the right, in the caption size and `--gm-color-textTertiary`. Done when: the line shows the model the settings service returns (`getSetting("defaultModel")`), asserted in jsdom.
- [ ] Hold the built surface to the approved mockup: render it (sideloaded, or in the jsdom harness for a component), compare it with the anchors on this section's `**Design:**` line in `docs/design/mockup.md` and their renders under `docs/design/mockup/renders/`, use only design tokens (`docs/design/tokens.json`) and registry icons (`iconSvg()` from `src/ui/icons.ts`), and commit a capture of the result under `docs/captures/taskpane/`. Done when: `python scripts/design-lint.py` exits 0 with the baseline no larger, every difference from the mockup is fixed or recorded as a `**Design deviation:**` naming its follow-up section, and the capture is committed. Cheaper substitute that fails: building from the prose alone, which the capture comparison at review refuses.
- [ ] Commit: `"design: header, tab bar, and footer from the mockup"`

**Test checkpoint:** `npx jest src/taskpane/tabs.test.ts` passes with the read-mode, compose-mode, and filled-icon cases; `python scripts/design-lint.py` exits 0; the sideloaded frame in Outlook on the web and new Outlook, captured in read and compose mode under `docs/captures/taskpane/frame/`, matches `docs/design/mockup/renders/Reply.png` and `Improve.png` in order, labels, icons, and spacing. Cheaper substitute that fails: adding icons to the old tab bar, which keeps Settings and Rules as tabs and fails the label assertions.

## 4. No Color Literal Left in the Pane

After §1 the stylesheet reads tokens, but `taskpane.css` and `taskpane.ts` still carry their own colors: the loading overlay, the diff highlights, and the score bar. This section moves each to a token so the baseline for colors reaches zero and the dark theme can reach every pixel.

- [ ] Replace the diff colors in `src/taskpane/taskpane.css` with `var(--gm-color-diffRemovedBg)`, `diffRemovedText`, `diffAddedBg`, and `diffAddedText`. Done when: `grep -c "#ffeef0\|#b31d28\|#e6ffec\|#22863a" src/taskpane/taskpane.css` prints `0`.
- [ ] Replace the overlay background `rgba(255,255,255,0.85)` with the surface token at the same opacity through `color-mix(in srgb, var(--gm-color-bg) 85%, transparent)`. Done when: the rule has no literal.
- [ ] Replace the three score colors in `src/taskpane/taskpane.ts` (`#22c55e`, `#eab308`, `#ef4444`) with classes that use `--gm-color-success`, a new `warning` token added to `docs/design/tokens.json` in both themes (contrast-checked), and `--gm-color-danger`. Done when: `grep -c "#22c55e\|#eab308\|#ef4444" src/taskpane/taskpane.ts` prints `0`.
- [ ] Replace every remaining literal `python scripts/design-lint.py` counts under `color-literal`, then shrink the baseline with `--update-baseline`. Done when: the `color-literal` rule has no entries.
- [ ] Commit: `"design: every pane color is a token"`

**Test checkpoint:** `python scripts/design-lint.py` exits 0 with no `color-literal` entries left in `docs/design/.lint-baseline.json`; a scratch `color: #123456` added to `src/taskpane/taskpane.css` makes it exit 1 naming the file; `npm run build` exits 0. Cheaper substitute that fails: moving the literals into a new CSS file, which the rule scans too.

## 5. Ribbon and App Icons From the Icon Set

The ribbon and the manifest still show the pre-2.0 PNGs. The approved icons are rendered at every manifest size under `assets/icons/png/`. This section points both manifests at them and deletes the old files, so the icons the operator approved are the ones Outlook shows.

- [ ] Point every `bt:Image` and `IconUrl` / `HighResolutionIconUrl` in `manifest.xml` at `assets/icons/png/`: the add-in and Open Gemail at `app/gemail-{16,32,64,80,128}.png`, AI Tools at `ribbon/ai-tools-{16,32,80}.png`, and the four menu items at `menu/<name>-{16,32,80}.png` (names in `docs/design/icons.md`; each 16 px PNG is built from its `-16.svg` redraw, approved 2026-11-15, with no manifest change needed). Done when: `grep -c "tool-icons/\|assets/icon-" manifest.xml` prints `0` and `npm run validate` passes.
- [ ] Make the same change in `manifest.dev.xml`. Done when: the same grep on it prints `0`.
- [ ] Check that the webpack build copies `assets/icons/png/**` to `dist/` (the `CopyWebpackPlugin` pattern covers `assets/**/*`). Done when: after `npm run build`, every icon URL in `dist/manifest.xml` names a file under `dist/` (a loop with `test -f` quoted in the commit body).
- [ ] Delete `assets/tool-icons/` and `assets/icon-{16,32,64,80,128}.png` with `git rm`, and shrink the baseline with `--update-baseline`. Done when: `git ls-files assets/tool-icons assets/icon-16.png` prints nothing and the `legacy-icon` rule has no entries.
- [ ] Sideload the dev build and open the ribbon in compose mode in Outlook on the web and new Outlook. Done when: captures of the group and the open AI Tools menu are committed under `docs/captures/ribbon/` and match `docs/design/mockup/renders/Icons.png` (the ribbon column).
- [ ] Commit: `"design: ribbon and app icons from the approved icon set"`

**Needs:** Outlook client (sideload)

**Requires:** display-session -- the ribbon capture needs Outlook in a window

**Test checkpoint:** `npm run validate` passes; `python scripts/design-lint.py` exits 0 with an empty `legacy-icon` baseline; `node tools/design/icons.mjs --check` exits 0; the ribbon captures show the approved icons in both clients. Cheaper substitute that fails: copying the new PNGs over the old file names, which leaves the `tool-icons/` paths the `legacy-icon` rule counts.

## 6. The Action Bar Holds Every Primary Action

In the approved design the primary action is never in the scrolling content: it sits in a bar pinned at the bottom of the pane, and what the bar holds follows the state (the write action before a result, the insert actions after one, **Stop** while streaming). Today each panel carries its own generate, insert, and copy buttons at the bottom of its form and inside its result card. This section builds the bar once and moves every panel's actions into it, so a long email never pushes Write or Reply out of reach. It must not change what any action does, only where it lives.

**Fidelity:** Gemail task pane action bar in every state (write, result in read mode, result in compose mode) -- docs/captures/taskpane/action-bar/. Button order, sizes, and labels match the Reply and Improve artboard renders.

**Design:** docs/design/mockup.md#action-bar, docs/design/mockup.md#write-action, docs/design/mockup.md#footer, docs/design/taskpane.md#action-bar, docs/design/taskpane.md#buttons -- states: write, result, improved, busy, disabled -- themes: n/a (both token sets apply through tokens.css; the live switch is D06 T04 §1) -- density: n/a (one density in a fixed-width task pane)

**Job:** a user can always reach the one action that moves their task forward without scrolling, in every feature. Consumer: every feature panel, through the controller.

**Treatment:** one `#action-bar` in `#app-bottom`, driven by `setActions()` from the active panel: a 44 px primary button with the filled spark and the `Ctrl+Enter` hint before a result; the mode's insert button, a secondary button, and 44 px icon buttons after one. Cheaper substitute that fails the checkpoint: `position: sticky` on each panel's own button, which leaves a second primary button in the result card and fails the single-primary test.

**Chrome:** consume `#app-bottom` from §3, the button styles and `iconSvg()` from `src/ui/`, and the panel modules of `D03 T01 §3` to `§5`. Do not add a second bar, and do not leave a primary action in a panel.

**Needs:** Outlook client (sideload)

**Requires:** display-session -- the pinned bar is proven by scrolling a sideloaded pane with a long result, which needs a window

- [ ] Add `src/ui/action-bar.ts` with `setActions(actions)` and `clearActions()`: `actions` is `{ primary: { label, icon?, hint?, run }, secondary?: [{ label, run }], icons?: [{ icon, label, run }] }`, rendered into `#action-bar` above the footer line, the primary as `.aic-btn--primary` at 44 px, a secondary outlined at 44 px, and each icon action a 44 px square button whose `aria-label` is its label. Done when: jsdom tests in `src/ui/action-bar.test.ts` assert the rendered order and labels for a write set and a result set, that `run` fires on click, and that a second `setActions` replaces the first with exactly one primary button in the document.
- [ ] Have the tab controller call the active panel's `actions()` on every tab switch and whenever a panel calls `refreshActions()` after its state changes, and clear the bar for Settings (which owns its own bar in §8). Done when: a jsdom test switches Reply, Draft, Summarize, and Improve and asserts the primary label each time (**Write reply**, **Write draft**, **Summarize**, **Improve**).
- [ ] Move each panel's generate button into its `actions()` write set and delete the button from the panel markup: Reply and Draft with the filled spark and the `Ctrl+Enter` hint, Summarize, Improve, Extract, and Translate with their own verbs. Done when: `grep -c 'id="btn-generate"' src/taskpane/taskpane.html` prints `0` and each panel test triggers generation through the action bar's primary button.
- [ ] Move the result actions into each panel's result set and delete them from the result card: read mode **Reply** (primary), **Reply all** (secondary), **Copy** (icon); compose mode **Insert** (primary) and **Copy**; Improve **Replace selection** (primary), **Copy**, and **Try again** (icons, `regenerate`). Done when: a jsdom test per panel asserts the result set after a mocked result and that the result card holds no button other than **Regenerate** and the refine input.
- [ ] Disable the primary button while its call is in flight and restore it when the call settles, through the controller, so a panel never toggles `disabled` on a button itself. Done when: a jsdom test with a pending promise asserts the primary is disabled and re-enabled.
- [ ] Hold the built surface to the approved mockup: render it (sideloaded, or in the jsdom harness for a component), compare it with the anchors on this section's `**Design:**` line in `docs/design/mockup.md` and their renders under `docs/design/mockup/renders/`, use only design tokens (`docs/design/tokens.json`) and registry icons (`iconSvg()` from `src/ui/icons.ts`), and commit a capture of the result under `docs/captures/taskpane/`. Done when: `python scripts/design-lint.py` exits 0 with the baseline no larger, every difference from the mockup is fixed or recorded as a `**Design deviation:**` naming its follow-up section, and the capture is committed. Cheaper substitute that fails: building from the prose alone, which the capture comparison at review refuses.
- [ ] Commit: `"design: the action bar holds every primary action"`

**Test checkpoint:** `npx jest src/ui/action-bar.test.ts src/taskpane` passes the order, replace, per-panel, and in-flight cases; `grep -c 'id="btn-generate"' src/taskpane/taskpane.html` prints `0`; in a sideloaded pane with a result longer than the pane, the action bar stays visible while the content scrolls, captured in read and compose mode under `docs/captures/taskpane/action-bar/` and matching `docs/design/mockup/renders/Reply.png` and `Improve.png`. Cheaper substitute that fails: hiding the panel buttons with CSS and duplicating them in the bar, which the single-primary test fails.

## 7. Reply Settings Row, Instruction Summary, and Result Card

The approved form is short: the instruction, one row of three dropdown buttons for tone, length, and language, and the context checkbox. After a result arrives the form folds into a one-line summary with **Edit**, and the result card takes the space with its word count, **Regenerate**, the text, and the refine input. Today Reply and Draft each carry labelled selects, the form stays open above the result, and the card holds its own action row. This section builds the row, the fold, and the card once in `src/ui/` and uses them in Reply and Draft; it must keep every value the user chose when the form folds and unfolds.

**Fidelity:** Gemail task pane Reply and Draft, the form before writing and the folded summary with the result after -- docs/captures/taskpane/reply/ and docs/captures/taskpane/draft/. Both states match the two panes of the Reply artboard render.

**Design:** docs/design/mockup.md#reply-form, docs/design/mockup.md#reply-settings-row, docs/design/mockup.md#instruction-summary, docs/design/mockup.md#result-card, docs/design/mockup.md#quick-replies, docs/design/mockup.md#reply-context, docs/design/taskpane.md#form-controls, docs/design/taskpane.md#result-card -- states: form, folded, editing, regenerating, refined -- themes: n/a (both token sets apply through tokens.css; the live switch is D06 T04 §1) -- density: n/a (one density in a fixed-width task pane)

**Job:** a user sets how a reply should sound in one row, and after writing sees the result first, with their instruction one click away. Consumer: the Reply and Draft panels, and through them the prompt builder, which reads the same three values as before.

**Treatment:** an option row of three listbox dropdown buttons that show their current value, a `surface` summary card with **Edit**, and a bordered result card with a header row, the text, and the refine input. Cheaper substitute that fails the checkpoint: restyling the existing `<select>` elements side by side, which cannot show the value in a 32 px button row at 320 px and fails the listbox keyboard test.

**Chrome:** consume the dropdown, card, and button styles in `src/ui/`, the shared language list of `D03 T01 §6`, and the action bar of §6. Do not add a second language list or a second result card.

**Needs:** Outlook client (sideload)

**Requires:** display-session -- the fold and the dropdowns are proven in a sideloaded pane at 320 and 360 px, which needs a window

- [ ] Add `src/ui/option-row.ts` with `createOptionRow(options)`: each option is a 32 px button (`aria-haspopup="listbox"`, `aria-expanded`) showing its current value and a `chevron-down`, opening a `role="listbox"` of `role="option"` items; Up, Down, Home, End, Enter, and Escape work, and choosing an item updates the button and fires `onChange`. Done when: jsdom tests in `src/ui/option-row.test.ts` cover open, arrow navigation, select, and Escape returning focus to the button.
- [ ] Replace the tone, length, and language controls of Reply and Draft with one option row under the caption **Reply settings** (Draft: **Draft settings**), tone showing its name, length as **Short**, **Medium length**, or **Detailed**, and language as **Match the email** or the language name. Done when: `grep -c "<select" src/taskpane/taskpane.html` no longer counts those six selects, and panel tests assert the prompt builder receives the same tone, length, and language values as before for each choice.
- [ ] Rebuild the reply context and Quick replies to the mockup: the avatar row without a card, and pill buttons under the **Quick replies** label, hidden once a result exists. Done when: a jsdom test asserts the pills are present before and absent after a mocked result.
- [ ] Add `src/ui/instruction-summary.ts`: when a result arrives the panel hides its form and shows the summary (the caption **Your instruction · <tone> · <length>**, the instruction on one truncated line, and **Edit**); **Edit** shows the form again with every value kept and returns focus to the instruction. Done when: a jsdom test asserts the fold on a result, the three values in the caption, and that after **Edit** the instruction, tone, length, language, and checkbox hold what the user set.
- [ ] Rebuild the result card in `src/ui/result-card.ts` to a header row (word count and reading time, **Regenerate**), the text in the reading size, and the refine input with the outline spark; no action row. Done when: the Reply and Draft panels both render through it and a jsdom test asserts the header text for a 118-word result reads "118 words · under 1 min read".
- [ ] Hold the built surface to the approved mockup: render it (sideloaded, or in the jsdom harness for a component), compare it with the anchors on this section's `**Design:**` line in `docs/design/mockup.md` and their renders under `docs/design/mockup/renders/`, use only design tokens (`docs/design/tokens.json`) and registry icons (`iconSvg()` from `src/ui/icons.ts`), and commit a capture of the result under `docs/captures/taskpane/`. Done when: `python scripts/design-lint.py` exits 0 with the baseline no larger, every difference from the mockup is fixed or recorded as a `**Design deviation:**` naming its follow-up section, and the capture is committed. Cheaper substitute that fails: building from the prose alone, which the capture comparison at review refuses.
- [ ] Commit: `"design: the reply settings row, the folded instruction, and the result card"`

**Test checkpoint:** `npx jest src/ui/option-row.test.ts src/ui/instruction-summary.test.ts src/taskpane` passes the listbox keyboard, fold, kept-values, and prompt-equivalence cases; the sideloaded Reply and Draft panels, before and after writing, are captured under `docs/captures/taskpane/reply/` and `docs/captures/taskpane/draft/` and match the two panes of `docs/design/mockup/renders/Reply.png`; `python scripts/design-lint.py` exits 0. Cheaper substitute that fails: folding the form by clearing it, which the kept-values test fails.

## 8. Settings as Cards With a Sticky Save Bar

The approved Settings is four cards (the OpenRouter key, the model, writing, the privacy switch) and the clear button on a tinted canvas, over a bar pinned at the bottom that holds **Save settings** and the count of unsaved changes. Today Settings is one long uncarded list with Save at the end of it, and Rules was a tab. This section regroups what exists into the cards, adds the Rules row and the sticky bar, and counts unsaved changes; it adds no setting and must not change what Save writes.

**Fidelity:** Gemail Settings panel, the four cards, the clear button, and the sticky Save bar -- docs/captures/taskpane/settings/. Card order, headings, glyphs, and spacing match the Settings artboard render in both themes.

**Design:** docs/design/mockup.md#settings, docs/design/mockup.md#api-key, docs/design/mockup.md#model-picker, docs/design/mockup.md#writing, docs/design/mockup.md#privacy-switch, docs/design/mockup.md#save-and-clear, docs/design/taskpane.md#settings-panel, docs/design/taskpane.md#rules-panel -- states: clean, unsaved, saving, saved, leaving unsaved -- themes: n/a (both token sets apply through tokens.css; the live switch is D06 T04 §1) -- density: n/a (one density in a fixed-width task pane)

**Job:** a user finds each setting in a named group and always sees whether there is something to save. Consumer: the settings service, which Save calls exactly as before.

**Treatment:** cards on a `surface` canvas, the Rules row inside the Writing card, and one sticky bar with **Save settings** enabled only when something changed. Cheaper substitute that fails the checkpoint: saving on every change, which removes the Save bar the mockup draws and fails the unsaved-count test.

**Chrome:** consume the Settings panel module of `D03 T01 §5`, the key, model, and privacy controls built by `D02 T02 §4` to `§7`, the card and switch styles in `src/ui/`, and the dialog pattern of `docs/design/taskpane.md#dialogs`. Do not add a second settings writer.

**Needs:** Outlook client (sideload)

**Requires:** display-session -- the sticky bar and the cards are proven in a sideloaded Settings panel in both themes, which needs a window

- [ ] Regroup the Settings panel markup into four cards with a 14 px semibold heading and a 20 px glyph each: **OpenRouter key** (`api-key`), **Model** (`ai`), **Writing**, and the privacy switch card, on a `--gm-color-surface` canvas (`--gm-color-surfaceSunken` in the dark set), followed by **Clear all Gemail data...** as a full-width outlined danger button. Done when: a jsdom test asserts the four card headings in order and the clear button after them.
- [ ] Add the **Rules** row at the foot of the Writing card showing the number of active rules ("4 active") and opening the Rules panel, whose back button returns to Settings; remove the temporary link §3 added. Done when: a jsdom test with four rules enabled asserts the count and that the row opens the Rules panel.
- [ ] Add the sticky Save bar to Settings in `#app-bottom` (the action bar is cleared for Settings): **Save settings** as a 44 px primary button and, on its left, "Unsaved changes: <n>" counting the controls whose value differs from the stored settings; the button is disabled at zero. Done when: jsdom tests assert the count after one and two changes, zero after Save, and zero after changing a value back.
- [ ] Ask before leaving Settings with unsaved changes (back button or a tab switch) through the inline dialog pattern: **Keep editing** first, then **Discard changes**. Done when: a jsdom test asserts the dialog appears only when the count is above zero and that **Discard changes** restores the stored values.
- [ ] Hold the built surface to the approved mockup: render it (sideloaded, or in the jsdom harness for a component), compare it with the anchors on this section's `**Design:**` line in `docs/design/mockup.md` and their renders under `docs/design/mockup/renders/`, use only design tokens (`docs/design/tokens.json`) and registry icons (`iconSvg()` from `src/ui/icons.ts`), and commit a capture of the result under `docs/captures/taskpane/`. Done when: `python scripts/design-lint.py` exits 0 with the baseline no larger, every difference from the mockup is fixed or recorded as a `**Design deviation:**` naming its follow-up section, and the capture is committed. Cheaper substitute that fails: building from the prose alone, which the capture comparison at review refuses.
- [ ] Commit: `"design: Settings as cards with a sticky Save bar"`

**Test checkpoint:** `npx jest src/taskpane` passes the card-order, Rules-row, unsaved-count, and leave-dialog cases; the existing settings save tests pass unchanged; the sideloaded Settings panel is captured in light and dark under `docs/captures/taskpane/settings/` and matches `docs/design/mockup/renders/Settings.png`; `python scripts/design-lint.py` exits 0. Cheaper substitute that fails: restyling the list without the sticky bar, which the unsaved-count test fails.

## 9. Five Interaction States on Every Control

The approved States artboard gives every control five states in both themes: rest, hover, pressed, focus, and disabled, all from tokens. Today hover and focus styles are scattered through `taskpane.css` with their own values, several controls have no pressed or disabled style, and the focus ring differs from control to control. This section defines the states once per control kind and removes the scattered ones. It changes no behavior: what is disabled, and when, stays as each feature decides.

**Fidelity:** Gemail task pane controls in each state, light and dark -- docs/captures/taskpane/states/. Each state matches the States artboard render.

**Design:** docs/design/mockup.md#interaction-states, docs/design/taskpane.md#buttons, docs/design/taskpane.md#form-controls, docs/design/taskpane.md#accessibility -- states: rest, hover, pressed, focus, disabled -- themes: n/a (both token sets apply through tokens.css; the live switch is D06 T04 §1) -- density: n/a (one density in a fixed-width task pane)

**Job:** a user always sees which control the pointer or the keyboard is on, that a press registered, and which controls cannot be used right now. Consumer: every control in the pane.

**Treatment:** one block of state rules per control kind (primary, secondary and dropdown, text button and link, icon button and tab, text input) in the shared stylesheet, driven by `:hover`, `:active`, `:focus-visible`, and `:disabled` or `[aria-disabled="true"]`. Cheaper substitute that fails the checkpoint: an `opacity` change for every state, which fails the computed-color test and drops disabled text contrast unpredictably.

**Chrome:** consume the token stylesheet of §1 (`--gm-color-brandHover`, `brandPressed`, `linkHover`, `linkPressed`, `disabledText`, `surface`, `surfaceSunken`, `border`) and the button, tab, and option-row components of §3, §6, and §7. Do not add a color that is not a token.

**Needs:** Outlook client (sideload)

**Requires:** display-session -- hover, pressed, and focus are proven by driving a sideloaded pane with the pointer and the keyboard in both themes, which needs a window

- [ ] Write the state rules for the five control kinds in `src/taskpane/taskpane.css` (or the shared stylesheet `D03 T01 §1` names) from the table in `docs/design/mockup.md#interaction-states`. Done when: a jsdom test per kind reads the rule text for `:hover`, `:active`, and `:disabled` and asserts each names the token the table gives.
- [ ] Give every focusable control one focus style: `outline: 2px solid var(--gm-color-brand)` with `outline-offset: 2px` on `:focus-visible` (`-2px` for tabs), and remove every other `outline`, `box-shadow` focus ring, and `focusPulse` use on a control. Done when: `grep -c "outline: none" src/taskpane/taskpane.css` prints `0` and a jsdom test asserts the rule for buttons, tabs, inputs, and links.
- [ ] Style disabled controls as `--gm-color-surfaceSunken` with `--gm-color-disabledText` and no border, for both `:disabled` and `[aria-disabled="true"]`, and remove any `opacity` used to show a disabled state. Done when: `grep -c "opacity" src/taskpane/taskpane.css` no longer counts a disabled rule (the remaining uses are listed in the commit body).
- [ ] Drive each control kind in a sideloaded pane in light and dark: hover, press, Tab to it, and a disabled instance, and capture the five states of each into `docs/captures/taskpane/states/`. Done when: the captures are committed and match `docs/design/mockup/renders/States.png`.
- [ ] Hold the built surface to the approved mockup: render it (sideloaded, or in the jsdom harness for a component), compare it with the anchors on this section's `**Design:**` line in `docs/design/mockup.md` and their renders under `docs/design/mockup/renders/`, use only design tokens (`docs/design/tokens.json`) and registry icons (`iconSvg()` from `src/ui/icons.ts`), and commit a capture of the result under `docs/captures/taskpane/`. Done when: `python scripts/design-lint.py` exits 0 with the baseline no larger, every difference from the mockup is fixed or recorded as a `**Design deviation:**` naming its follow-up section, and the capture is committed. Cheaper substitute that fails: building from the prose alone, which the capture comparison at review refuses.
- [ ] Commit: `"design: five interaction states on every control"`

**Test checkpoint:** `npx jest src/taskpane` passes the per-kind state-rule and focus-ring tests; `grep -c "outline: none" src/taskpane/taskpane.css` prints `0`; `python scripts/design-lint.py` exits 0 with no new color literal; the captures under `docs/captures/taskpane/states/` match `docs/design/mockup/renders/States.png` in both themes. Cheaper substitute that fails: styling only the primary button, which the per-kind tests fail for tabs, dropdowns, and links.

## Verification

- [ ] `python scripts/design-lint.py` exits 0 and `docs/design/.lint-baseline.json` has no entries in any rule
- [ ] `node tools/design/icons.mjs --check`, `node tools/design/tokens.mjs --check`, and `pwsh scripts/check-all.ps1` exit 0
- [ ] The frame, action bar, reply form, result, Settings, and ribbon captures under `docs/captures/` match their mockup renders (`Reply.png`, `Improve.png`, `Settings.png`, `Icons.png`) in both supported clients and both themes
