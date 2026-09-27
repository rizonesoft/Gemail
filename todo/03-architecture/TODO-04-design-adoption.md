---
schema_version: 1
id: design-adoption
domain: 03-architecture
status: draft
title: "TODO-04 -- Design Adoption"
depends_on: []
---

# TODO-04 -- Design Adoption

> **Goal:** The code wears the approved design. Every color, font, and spacing value the pane uses comes from `docs/design/tokens.json` through one generated stylesheet; every icon in the pane comes from the generated registry `src/ui/icons.ts`; the header, tab bar, and footer match the Reply artboard; the ribbon and the manifests use the icons rendered from `assets/icons/src/`; and `docs/design/.lint-baseline.json` is empty, so `python scripts/design-lint.py` holds the code to the design with nothing grandfathered.

> [!IMPORTANT]
> **Current state (verified 2026-09-27):** The operator approved the design mockup on 2026-09-27 and it was imported the same day: the artboards under `docs/design/mockup/` (pinned to artifact version `1790526473-c417` by `docs/design/mockup/source.json`) with renders under `docs/design/mockup/renders/`, the tokens in `docs/design/tokens.json` (brand `#1668c9`, tertiary text `#686e7a`, Segoe UI Variable, a light and a dark set with the same keys), 50 icon sources in `assets/icons/src/`, 25 rendered PNGs in `assets/icons/png/`, and the generated registry `src/ui/icons.ts` with 42 pane icons behind `iconSvg()`. None of it is used by the add-in yet: `src/styles/main.css` still defines `--font-aic` as Poppins and the old `--color-aic-*` values (the brand is `#3b9eff`), `src/taskpane/taskpane.html` loads Google Fonts and carries 45 inline `<svg>` elements, and both manifests point at `assets/icon-*.png` and `assets/tool-icons/*.png`. `python scripts/design-lint.py` baselines what this file burns down: 54 color literals, 47 inline SVGs, 6 font declarations, and 88 legacy icon references.
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

## Outcome

- `src/styles/tokens.css` is generated from `docs/design/tokens.json` by `node tools/design/tokens.mjs`, defines every token as a `--gm-*` custom property for light and dark, and `python scripts/design-lint.py` refuses a stale copy.
- `src/taskpane/taskpane.html` loads no web font and contains no `<svg>`; every icon is rendered by `iconSvg()`.
- The header, tab bar, and footer match `docs/design/mockup.md#header`, `#tab-bar`, and `#footer`, with the capture committed under `docs/captures/taskpane/`.
- Both manifests reference only `assets/icons/png/` for images, and `assets/tool-icons/` and `assets/icon-*.png` are gone.
- `docs/design/.lint-baseline.json` has no entries, so any new color literal, font declaration, inline SVG, or legacy icon path fails the commit hook and CI.

**Adjacency:** list=not-applicable (no records to browse: this file restyles existing surfaces); document=not-applicable (nothing printed or exported); settings=not-applicable (no tunable value is added; the theme switch is D06 T04 §1); reporting=not-applicable (no summaries); notifications=not-applicable (no notification is added; the existing status and error messages only change color through the tokens of §1 and §4, and their mockup styling belongs to D03 T03 §1); permissions=not-applicable (no refusal path changes); audit=not-applicable (no write changes); exchange=not-applicable (no import or export); reverse=not-applicable (styling has no create to reverse)

## Implementation Order

| Order | Section | Deliverable                                     | Depends On  | Status |
| :---: | :-----: | ----------------------------------------------- | ----------- | :----: |
|   1   |   §1    | Tokens and the system font in the stylesheet    | D00 T02 §3  |  [ ]   |
|   2   |   §2    | Every pane icon from the registry               | D03 T01 §1  |  [ ]   |
|   3   |   §3    | Header, tab bar, and footer from the mockup     | §1, §2, D03 T01 §2 |  [ ]   |
|   4   |   §4    | No color literal left in the pane               | §1          |  [ ]   |
|   5   |   §5    | Ribbon and app icons from the icon set          | D01 T01 §2  |  [ ]   |

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

The pane's frame is the part every feature shares: today it is two text tabs, three icon-only buttons, and a "More features" dropdown, with Settings and Rules as tabs. The approved Reply artboard puts Settings in the header, five labelled icon tabs in the bar, and the model line in the footer. This section rebuilds the frame to match; the panels inside it stay as they are.

**Fidelity:** Gemail task pane frame (header, tab bar, footer) -- docs/captures/taskpane/frame/. Order, spacing, labels, and icons match the Reply artboard render; deviations only through a Design deviation line.

**Design:** docs/design/mockup.md#header, docs/design/mockup.md#tab-bar, docs/design/mockup.md#footer, docs/design/taskpane.md#layout -- states: rest, active, hover, focus -- themes: n/a (both token sets apply through tokens.css; the live switch is D06 T04 §1) -- density: n/a (one density in a fixed-width task pane)

**Job:** an Outlook user can reach every feature and Settings in one click from any tab, and see which model is answering. Consumer: none: this surface is the consumer.

**Treatment:** the five-tab bar with a 20 px icon over a 12 px label, filled icon and underline on the active tab, Settings as a header icon button, and the footer model line. Cheaper substitute that fails the checkpoint: restyling the old two-tab bar and dropdown, which the capture comparison against `docs/design/mockup/renders/Main.png` refuses.

**Chrome:** consume `iconSvg()` from `src/ui/icons.ts`, the token stylesheet from §1, and the tab controller from `src/taskpane/tabs.ts`. Do not invent a second tab controller or icon source.

**Needs:** Outlook client (sideload)

**Requires:** display-session -- the frame is proven by a sideloaded capture compared with the mockup render, which needs a window

- [ ] Rebuild the header in `src/taskpane/taskpane.html` to the app mark (`assets/icons/png/app/gemail-32.png` at 28 px), the name **Gemail**, and a Settings icon button (`data-icon="settings"`, `aria-label="Settings"`). Done when: the header has exactly those three children.
- [ ] Rebuild the tab bar to five tabs, **Reply**, **Draft**, **Summarize**, **Improve**, **More**, each an icon over a label, and move Summarize and Improve out of the dropdown; **More** lists Actions and Translate. Done when: `src/taskpane/tabs.ts` switches all five, and a jsdom test asserts the five labels in order.
- [ ] Show the `-filled` icon, `--gm-color-brand`, semibold label, and a 2 px underline on the active tab from `switchTab()`, and the regular icon in `--gm-color-textSecondary` at rest. Done when: the jsdom test asserts the active tab's icon is the filled glyph after each switch.
- [ ] Move Rules into Settings as its own section and remove `#tab-rules`. Done when: `grep -c 'id="tab-rules"' src/taskpane/taskpane.html` prints `0` and the rules still save (the existing rules test passes).
- [ ] Add the footer: `Model: <display name> via OpenRouter` with a **Change** link that opens Settings, and the version from `#app-version`. Done when: the footer shows the model the settings service returns (`getSetting("defaultModel")`), asserted in jsdom.
- [ ] Hold the built surface to the approved mockup: render it (sideloaded, or in the jsdom harness for a component), compare it with the anchors on this section's `**Design:**` line in `docs/design/mockup.md` and their renders under `docs/design/mockup/renders/`, use only design tokens (`docs/design/tokens.json`) and registry icons (`iconSvg()` from `src/ui/icons.ts`), and commit a capture of the result under `docs/captures/taskpane/`. Done when: `python scripts/design-lint.py` exits 0 with the baseline no larger, every difference from the mockup is fixed or recorded as a `**Design deviation:**` naming its follow-up section, and the capture is committed. Cheaper substitute that fails: building from the prose alone, which the capture comparison at review refuses.
- [ ] Commit: `"design: header, tab bar, and footer from the mockup"`

**Test checkpoint:** `npx jest src/taskpane/tabs.test.ts` passes with the five-tab and filled-icon cases; `python scripts/design-lint.py` exits 0; the sideloaded frame in Outlook on the web and new Outlook, captured under `docs/captures/taskpane/frame/`, matches `docs/design/mockup/renders/Main.png` in order, labels, icons, and spacing. Cheaper substitute that fails: adding icons to the old tab bar, which keeps Settings and Rules as tabs and fails the five-label assertion.

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

- [ ] Point every `bt:Image` and `IconUrl` / `HighResolutionIconUrl` in `manifest.xml` at `assets/icons/png/`: the add-in and Open Gemail at `app/gemail-{16,32,64,80,128}.png`, AI Tools at `ribbon/ai-tools-{16,32,80}.png`, and the four menu items at `menu/<name>-{16,32,80}.png` (names in `docs/design/icons.md`). Done when: `grep -c "tool-icons/\|assets/icon-" manifest.xml` prints `0` and `npm run validate` passes.
- [ ] Make the same change in `manifest.dev.xml`. Done when: the same grep on it prints `0`.
- [ ] Check that the webpack build copies `assets/icons/png/**` to `dist/` (the `CopyWebpackPlugin` pattern covers `assets/**/*`). Done when: after `npm run build`, every icon URL in `dist/manifest.xml` names a file under `dist/` (a loop with `test -f` quoted in the commit body).
- [ ] Delete `assets/tool-icons/` and `assets/icon-{16,32,64,80,128}.png` with `git rm`, and shrink the baseline with `--update-baseline`. Done when: `git ls-files assets/tool-icons assets/icon-16.png` prints nothing and the `legacy-icon` rule has no entries.
- [ ] Sideload the dev build and open the ribbon in compose mode in Outlook on the web and new Outlook. Done when: captures of the group and the open AI Tools menu are committed under `docs/captures/ribbon/` and match `docs/design/mockup/renders/Icons.png` (the ribbon column).
- [ ] Commit: `"design: ribbon and app icons from the approved icon set"`

**Needs:** Outlook client (sideload)

**Requires:** display-session -- the ribbon capture needs Outlook in a window

**Test checkpoint:** `npm run validate` passes; `python scripts/design-lint.py` exits 0 with an empty `legacy-icon` baseline; `node tools/design/icons.mjs --check` exits 0; the ribbon captures show the approved icons in both clients. Cheaper substitute that fails: copying the new PNGs over the old file names, which leaves the `tool-icons/` paths the `legacy-icon` rule counts.

## Verification

- [ ] `python scripts/design-lint.py` exits 0 and `docs/design/.lint-baseline.json` has no entries in any rule
- [ ] `node tools/design/icons.mjs --check`, `node tools/design/tokens.mjs --check`, and `pwsh scripts/check-all.ps1` exit 0
- [ ] The frame and ribbon captures under `docs/captures/` match their mockup renders in both supported clients
