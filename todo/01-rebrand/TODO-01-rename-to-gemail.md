---
schema_version: 1
id: rename-to-gemail
domain: 01-rebrand
status: draft
title: "TODO-01 -- Rename to Gemail"
depends_on: []
---

# TODO-01 -- Rename to Gemail

> **Goal:** Everything a user, an administrator, or a contributor reads says **Gemail**: the npm package, both manifests, the task pane and ribbon, the source identifiers and file headers, the stored settings keys, and the documentation, while the manifest Ids stay unchanged so existing installs update in place, stored settings migrate instead of resetting, and users whose installed manifest still names the old `/ai-email-writer/` path are carried to the new one by a redirect stub.

> [!IMPORTANT]
> **Current state (verified 2026-09-27):** The product still carries its two old names. `package.json` is `"name": "ai-email-writer"` with the repository URL `https://github.com/rizonesoft/ai-email-writer.git` (the GitHub repository itself is already `rizonesoft/Gemail`). `manifest.xml` and `manifest.dev.xml` each name "AI Compose" five times (DisplayName, two `GroupLabel` strings, two `TaskpaneButton.Tooltip` strings), the `<Description>` reads "AI-powered email writer and composer for Outlook, powered by Gemini.", and the ribbon button label is "Open Panel". `src/taskpane/taskpane.html` names "AI Compose" five times (the header comment, `<title>AI Compose — AI Email Writer</title>`, two hints, and the footer `AI Compose v<span id="app-version">`). `src/taskpane/taskpane.ts` shows "... with Gemini..." in four loading messages, and `src/commands/commands.ts` posts its ribbon notification under the key `AIComposeNotification`. The settings type is `AIComposeSettings` (eight occurrences in `src/features/settings.ts`, three in `src/taskpane/taskpane.ts`), and every `src/*/*.ts` file header starts `AI Compose --` (16 occurrences). Settings live under the localStorage key `ai_compose_settings` (with a one-time migration from `glide_settings`) and templates under `aic_templates`. `README.md` names `ai-email-writer` 15 times. There is no `legacy/` folder. The CSS class and token prefix `aic-` appears on roughly two thousand references and is internal only.
<!-- claim: count "ai-email-writer" package.json = 2 -->
<!-- claim: count "AI Compose" manifest.xml = 5 -->
<!-- claim: count "AI Compose" src/taskpane/taskpane.html = 5 -->
<!-- claim: count "with Gemini" src/taskpane/taskpane.ts = 4 -->
<!-- claim: count "AIComposeNotification" src/commands/commands.ts = 1 -->
<!-- claim: count "AIComposeSettings" src/features/settings.ts = 8 -->
<!-- claim: count "ai_compose_settings" src/features/settings.ts = 1 -->
<!-- claim: count "aic_templates" src/features/settings.ts = 1 -->
<!-- claim: count "ai-email-writer" README.md = 15 -->
<!-- claim: absent legacy/ai-email-writer/taskpane.html -->

## Inputs

- [`package.json`](../../package.json), [`package-lock.json`](../../package-lock.json) -- the package name and repository URL §1 changes
- [`manifest.xml`](../../manifest.xml), [`manifest.dev.xml`](../../manifest.dev.xml), [`.github/workflows/deploy.yml`](../../.github/workflows/deploy.yml) -- the display strings §2 changes; the `<Id>` values stay
- [`src/taskpane/taskpane.html`](../../src/taskpane/taskpane.html), [`src/taskpane/taskpane.ts`](../../src/taskpane/taskpane.ts), [`src/commands/commands.ts`](../../src/commands/commands.ts) -- the user-visible strings §3 changes
- [`src/features/settings.ts`](../../src/features/settings.ts) -- `AIComposeSettings`, `STORAGE_KEY`, `LEGACY_STORAGE_KEY`, and `TEMPLATES_KEY`, which §4 and §5 change
- [`README.md`](../../README.md), [`CONTRIBUTING.md`](../../CONTRIBUTING.md), [`SECURITY.md`](../../SECURITY.md), [`PRIVACY.md`](../../PRIVACY.md), [`CHANGELOG.md`](../../CHANGELOG.md), [`docs/setup-api-key.md`](../../docs/setup-api-key.md) -- the documents §6 renames
- [`docs/design/taskpane.md`](../../docs/design/taskpane.md) -- the Header and Ribbon rules §3 builds to, and the `aic-` prefix decision under Tokens
- Microsoft Learn, "Outlook add-in manifests" (https://learn.microsoft.com/office/dev/add-ins/outlook/manifests) -- `DisplayName`, `Description`, and why the `<Id>` must not change for an in-place update
- Microsoft Learn, "Show notifications in Outlook add-ins" `notificationMessages.replaceAsync` (https://learn.microsoft.com/javascript/api/outlook/office.notificationmessages) -- the key §3 renames
- -> XREF: D00 T01 §1 -- the Pages path this file renames around and the redirect in §7 targets
- -> XREF: D02 T02 §3 -- the OpenRouter settings migration builds on the `gemail_settings` key §5 writes, and D02 T02 §7 rewrites the provider copy in the documents §6 renames
- -> XREF: D99 T01 §3 -- the operator publishes the redirect stub §7 writes
- -> XREF: D03 T04 §5 -- swaps the manifest icon URLs after the names settle here

## Outcome

- `grep -rn "AI Compose\|AI Email Writer\|ai-email-writer" --include=*.ts --include=*.html --include=*.json --include=*.xml --include=*.yml --include=*.md .` (excluding `node_modules/`, `todo/`, `CHANGELOG.md` history entries, and `legacy/`) prints nothing.
- Both manifests validate with `npx office-addin-manifest validate` and keep their original `<Id>` values, so an installed 1.3.2 updates in place.
- A browser profile holding `ai_compose_settings` and `aic_templates` (or the older `glide_settings`) opens Gemail with every setting and template intact under `gemail_settings` and `gemail_templates`, and the old keys are gone.
- `legacy/ai-email-writer/` holds a stub that sends a page loaded from the old path to the same page under `/Gemail/`, ready for the operator to publish.

**Adjacency:** list=not-applicable (a rename adds no collection a user browses); document=not-applicable (the rename writes nothing into a message); settings=applicable; reporting=not-applicable (no summaries over the domain's data); notifications=applicable; permissions=not-applicable (a rename changes no refusal path); audit=not-applicable (no write into a message or setting beyond the one-time migration, which §5 tests); exchange=not-applicable (no imported or exported data); reverse=not-applicable (the migration is one-way by design: the old keys are removed only after the new ones are written and read back)

**Adjacency rationale:** Settings apply because §5 moves every stored preference and template to new keys; notifications apply because §3 renames the ribbon notification key and the loading messages.

## Implementation Order

| Order | Section | Deliverable                               | Depends On | Status |
| :---: | :-----: | ----------------------------------------- | ---------- | :----: |
|   1   |   §1    | Package identity                          | D00 T01 §1 |  [ ]   |
|   2   |   §2    | Manifest names and descriptions           | §1         |  [ ]   |
|   3   |   §3    | Task pane and ribbon strings              | §2         |  [ ]   |
|   4   |   §4    | Source identifiers and file headers       | §3         |  [ ]   |
|   5   |   §5    | Settings storage keys migrate to the Gemail keys | §4         |  [ ]   |
|   6   |   §6    | Documentation rebrand                     | §3         |  [ ]   |
|   7   |   §7    | Redirect stub for the old Pages path      | D00 T01 §1 |  [ ]   |

---

## 1. Package Identity

The package name and repository URL are the first thing a contributor sees and what `npm` and GitHub badges resolve against. The repository is already `rizonesoft/Gemail`; the package still says `ai-email-writer`. This section changes the identity only: no display string and no URL the add-in loads.

- [ ] Set `"name": "gemail"` and `"repository.url": "https://github.com/rizonesoft/Gemail.git"` in `package.json`. Done when: `node -p "require('./package.json').name"` prints `gemail` and `grep -c ai-email-writer package.json` prints `0`.
- [ ] Regenerate the lockfile header with `npm install --package-lock-only`. Done when: `node -p "require('./package-lock.json').name"` prints `gemail` and `git diff --stat package-lock.json` touches only the two `name` lines.
- [ ] Point the two badges at the top of `README.md` (License and Deploy) at `https://github.com/rizonesoft/Gemail/...`. Done when: both badge images render on the GitHub README page (the Deploy badge shows a status, not "repo not found").
- [ ] Commit: `"rebrand: rename the npm package to gemail"`

**Test checkpoint:** `node -p "require('./package.json').name + ' ' + require('./package-lock.json').name"` prints `gemail gemail`; `npm ci && npm run build` exits `0`; `curl -s -o /dev/null -w '%{http_code}' https://github.com/rizonesoft/Gemail/actions/workflows/deploy.yml/badge.svg` prints `200`. Cheaper substitute that fails: editing `package.json` without the lockfile, which leaves `package-lock.json` naming `ai-email-writer` and fails the first command.

## 2. Manifest Names and Descriptions

The manifest strings are what Outlook shows in the Add-ins dialog and on the ribbon. The `<Id>` values must not change: Outlook identifies an installed add-in by its Id, and a new Id would install Gemail beside the old add-in instead of updating it (Microsoft Learn, Outlook add-in manifests). The Description stops naming a provider, so D02 T02 does not have to touch the manifests again.

- [ ] In `manifest.xml`, set `<DisplayName DefaultValue="Gemail"/>`, both `GroupLabel` strings to `Gemail`, both `TaskpaneButton.Tooltip` strings to `Open the Gemail assistant panel.`, both `TaskpaneButton.Label` strings from `Open Panel` to `Open Gemail` (the Ribbon rule in `docs/design/taskpane.md`), and `<Description>` to `AI email assistant for Outlook: draft, reply, summarize, improve, translate, and extract action items.`. Done when: `grep -c "AI Compose\|Gemini" manifest.xml` prints `0` and `grep -c "<Id>a81c3d4e-5f67-4890-ab12-cd34ef56ab78</Id>" manifest.xml` prints `1`.
- [ ] Make the same edits in `manifest.dev.xml` with `Gemail (Dev)` for the DisplayName and the two `GroupLabel` strings. Done when: `grep -c "AI Compose\|Gemini" manifest.dev.xml` prints `0` and its `<Id>` is unchanged.
- [ ] Update the dev patch strings in `.github/workflows/deploy.yml` (`DefaultValue="AI Compose"` and the tooltip text) to the new values so the patched dev manifest reads `Gemail (Dev)`. Done when: `grep -c "AI Compose" .github/workflows/deploy.yml` prints `0` and, in a scratch run of the sed lines against `dist/manifest.xml`, the output DisplayName is `Gemail (Dev)`.
- [ ] Validate both manifests: `npx office-addin-manifest validate manifest.xml` and `npx office-addin-manifest validate manifest.dev.xml`. Done when: both print that the manifest is valid; the verdicts are quoted in the commit body.
- [ ] Commit: `"rebrand: manifests say Gemail, Ids unchanged"`

**Test checkpoint:** `grep -c "AI Compose" manifest.xml manifest.dev.xml .github/workflows/deploy.yml` prints `0` for all three; both `validate` runs succeed; `git diff HEAD~1 -- manifest.xml manifest.dev.xml | grep -c "^[-+].*<Id>"` prints `0` (no Id line changed). Cheaper substitute that fails: a find-and-replace across the manifests that also rewrites the `<Id>` or the dev patch's Id target, which the `<Id>` diff check catches.

## 3. Task Pane and Ribbon Strings

The strings the user reads inside Outlook: the page title, two hints, the footer, the four loading messages, and the ribbon notification key. Loading messages stop naming a provider or model now (the Loading and streaming rule in `docs/design/taskpane.md`), so the provider change in D02 T02 needs no copy edit here.

**Fidelity:** Gemail task pane footer, hints, and loading overlay, and the compose ribbon group -- docs/captures/taskpane/rename/. Terminology matches the Ribbon and Loading and streaming rules; layout unchanged.
**Design:** docs/design/mockup.md#header, docs/design/mockup.md#footer, docs/design/mockup.md#streaming-and-stop, docs/design/mockup.md#ribbon, docs/design/mockup.md#ai-tools-menu, docs/design/taskpane.md#loading-and-streaming, docs/design/taskpane.md#ribbon -- states: loading, idle, notification -- themes: n/a (string changes only; the theme work is owned by the appearance TODO in todo/06-features) -- density: n/a (one density in a fixed-width task pane)
**Job:** An Outlook user can see which add-in is working for them: the pane, the ribbon, and every progress message say Gemail. Consumer: none: this surface is the consumer.
**Treatment:** product name "Gemail" in the title and footer, action-named loading messages ("Writing your draft...", "Writing your reply...", "Summarizing...", "Improving your text..."). Cheaper substitute that fails the checkpoint: replacing "AI Compose" with "Gemail" but leaving "with Gemini" in the loading messages.
**Chrome:** consume the existing `showLoading()` helper and `#app-version` footer span. Do not invent a second loading message mechanism.
**Needs:** Outlook client (sideload)
**Requires:** display-session -- the checkpoint sideloads the dev build into Outlook on the web and captures the pane, which needs a window station

- [ ] In `src/taskpane/taskpane.html`, set `<title>Gemail</title>`, change the header comment, the two hints at the Improve and Extract panels ("... or Gemail will use the full body.", "Gemail will scan the current email ..."), the footer to `Gemail v<span id="app-version">`, and the overlay default text at the `aic-loading__text` paragraph to `Working...`. Done when: `grep -c "AI Compose\|AI Email Writer" src/taskpane/taskpane.html` prints `0` and the only `Gemini` strings left are the settings-panel ones D02 T02 §7 owns.
- [ ] In `src/taskpane/taskpane.ts`, replace the four `showLoading('... with Gemini...')` messages at `handleGenerate`, `handleGenerateReply`, `handleSummarize`, and `handleImprove` with `Writing your draft...`, `Writing your reply...`, `Summarizing...`, and `Improving your text...`. Done when: `grep -c "with Gemini" src/taskpane/taskpane.ts` prints `0`.
- [ ] In `src/commands/commands.ts`, rename the notification key `AIComposeNotification` to `GemailNotification` in `showNotification()`. Done when: `grep -c GemailNotification src/commands/commands.ts` prints `1`. Source: `notificationMessages.replaceAsync` replaces by key (Microsoft Learn, Office.NotificationMessages).
- [ ] Confirm `scripts/sync-manifest-version.js` still finds the footer span after the edit by running it in a scratch copy. Done when: it rewrites `<span id="app-version">` and exits `0`.
- [ ] Sideload the dev build into Outlook on the web, open the pane, trigger one Summarize, and run one ribbon command in compose. Commit captures of the footer, the loading overlay, and the ribbon notification to `docs/captures/taskpane/rename/`. Done when: three PNG files exist there and show "Gemail" and a provider-free loading message.
- [ ] Hold the built surface to the approved mockup: render it (sideloaded, or in the jsdom harness for a component), compare it with the anchors on this section's `**Design:**` line in `docs/design/mockup.md` and their renders under `docs/design/mockup/renders/`, use only design tokens (`docs/design/tokens.json`) and registry icons (`iconSvg()` from `src/ui/icons.ts`), and commit a capture of the result under `docs/captures/taskpane/`. Done when: `python scripts/design-lint.py` exits 0 with the baseline no larger, every difference from the mockup is fixed or recorded as a `**Design deviation:**` naming its follow-up section, and the capture is committed. Cheaper substitute that fails: building from the prose alone, which the capture comparison at review refuses.
- [ ] Commit: `"rebrand: task pane and ribbon say Gemail"`

**Test checkpoint:** `grep -rc "AI Compose\|AI Email Writer\|with Gemini" src/taskpane/taskpane.html src/taskpane/taskpane.ts src/commands/commands.ts` shows no "AI Compose", "AI Email Writer", or "with Gemini" match outside file header comments (which §4 owns); `npm run build` exits `0`; the three captures under `docs/captures/taskpane/rename/` show the new strings. Cheaper substitute that fails: changing only `<title>`, which leaves the footer and the loading overlay saying AI Compose and fails the grep.

## 4. Source Identifiers and File Headers

Contributors meet the old name in every file header (`AI Compose -- <module>`) and in the settings type `AIComposeSettings`. This section renames TypeScript identifiers and headers, and records the decision to keep the `aic-` CSS prefix: it is never user-visible, it appears on roughly two thousand class and token references, and renaming it buys nothing but a risky diff (recorded under Tokens in `docs/design/taskpane.md`).

- [ ] Rename the interface `AIComposeSettings` to `GemailSettings` in `src/features/settings.ts` and every consumer in `src/taskpane/taskpane.ts`. Done when: `grep -rc AIComposeSettings src` prints `0` for every file and `npx jest --ci` passes.
- [ ] Remove the never-defined `window.__AICompose_API_KEY__` fallback at `src/taskpane/taskpane.ts` (the inventory of 2026-09-27 found no writer of it anywhere). Done when: `grep -c __AICompose_API_KEY__ src/taskpane/taskpane.ts` prints `0`.
- [ ] Rewrite the first line of every file header comment under `src/` and `scripts/` from `AI Compose -- ...` to `Gemail -- ...`, keeping the copyright line. Done when: `grep -rn "AI Compose" src scripts --include=*.ts --include=*.css --include=*.html` prints nothing.
- [ ] Record in `src/styles/main.css` (one comment above the `@theme` block) that the `aic-` prefix is kept on purpose, citing `docs/design/taskpane.md#tokens`. Done when: the comment exists and `grep -c "aic-" src/taskpane/taskpane.css` is unchanged from before the section.
- [ ] Commit: `"rebrand: Gemail identifiers and file headers"`

**Test checkpoint:** `grep -rn "AI Compose\|AIComposeSettings\|__AICompose" src scripts` prints nothing; `npm run build` exits `0`; `npx jest --ci` passes with the same test count as before the section. Cheaper substitute that fails: a global replace of `aic` with `gemail`, which breaks the Tailwind tokens the CSS consumes and changes the `grep -c "aic-"` count the checkpoint holds constant.

## 5. Settings Storage Keys Migrate to the Gemail Keys

A user's preferences, preset rules, custom rules, and saved templates live under `ai_compose_settings` and `aic_templates` (and, for the oldest installs, `glide_settings`). Renaming the keys must never reset anyone: a user who opens Gemail after the update sees every setting and template they had. The migration writes the new key, reads it back, and only then removes the old one. The API key moves with the settings here; separating it onto its own device-only key is D04 T01 §4.

**Fidelity:** no surface of its own (a storage migration; the Settings and Rules panels show the same values before and after, which the checkpoint compares)

- [ ] In `src/features/settings.ts`, set `STORAGE_KEY = "gemail_settings"` and replace `LEGACY_STORAGE_KEY` with an ordered list `LEGACY_STORAGE_KEYS = ["ai_compose_settings", "glide_settings"]`; `loadSettings()` reads the first key that holds a value. Done when: `grep -c '"gemail_settings"' src/features/settings.ts` prints `1`.
- [ ] Write the migration as `migrateStorageKey(from, to)`: parse the old value (skip and keep it if it does not parse), write it under the new key, read the new key back and compare, then remove the old key. Done when: a unit test in `src/features/settings.test.ts` named `migrates ai_compose_settings to gemail_settings and removes the old key` passes. Cheaper substitute: `setItem` then `removeItem` without the readback, which a test with a throwing `setItem` (quota exceeded) catches because the old key must survive.
- [ ] Set `TEMPLATES_KEY = "gemail_templates"` and migrate `aic_templates` through the same `migrateStorageKey()`. Done when: a test named `migrates aic_templates to gemail_templates` passes.
- [ ] Cover the legacy chain and the failure paths in `src/features/settings.test.ts`: a profile holding only `glide_settings`; a profile holding both `gemail_settings` and `ai_compose_settings` (the new key wins and the old is removed); malformed JSON under the old key (kept, defaults loaded, no throw); `setItem` throwing (old key kept). Done when: the four tests pass under `npx jest src/features/settings.test.ts`.
- [ ] Record in the section's commit body that this is the first write path the plan will propose for the frozen set (`todo/README.md`, Frozen behavior), for the operator to confirm at stamp time. Done when: the commit body carries the proposal line.
- [ ] Commit: `"rebrand: migrate stored settings and templates to gemail keys"`

**Test checkpoint:** `npx jest src/features/settings.test.ts` passes the six named tests; in a sideloaded dev build, a browser profile seeded with the 1.3.2 keys (`localStorage.setItem('ai_compose_settings', ...)` and `aic_templates` with two templates from a committed fixture) opens with the same tone, model, rules, and both templates in their dropdowns, and `Object.keys(localStorage)` then lists `gemail_settings` and `gemail_templates` and neither old key. Cheaper substitute that fails: changing the key constant without a migration, which opens the seeded profile with defaults and fails the dropdown comparison.

## 6. Documentation Rebrand

Every document a user or contributor reads names the old product and the old repository path. This section changes names and links only; the provider text (Gemini to OpenRouter) is rewritten once, after the cutover, by D02 T02 §7, so no document is rewritten twice.

- [ ] In `README.md`, rename the title to `Gemail`, the product mentions from AI Compose and AI Email Writer to Gemail, every `rizonesoft/ai-email-writer` link and every `rizonesoft.github.io/ai-email-writer/` URL to the Gemail equivalents, the clone commands to `git clone https://github.com/rizonesoft/Gemail.git` and `cd Gemail`, and the dev build name to `Gemail (Dev)`, and update the banner `alt` text. Done when: `grep -c "ai-email-writer\|AI Compose\|AI Email Writer" README.md` prints `0`.
- [ ] Make the same name and link changes in `CONTRIBUTING.md`, `SECURITY.md`, `PRIVACY.md`, and `docs/setup-api-key.md`, and in the privacy link inside `src/taskpane/taskpane.html` (`github.com/rizonesoft/Gemail/blob/main/PRIVACY.md`). Done when: `grep -c "ai-email-writer\|AI Compose\|AI Email Writer" CONTRIBUTING.md SECURITY.md PRIVACY.md docs/setup-api-key.md src/taskpane/taskpane.html` prints `0` for each.
- [ ] Add a `CHANGELOG.md` entry under an Unreleased heading: "Renamed to Gemail. Existing installs update in place; settings and templates migrate automatically." Leave older entries' historical names as written. Done when: the entry exists above the 1.3.2 entry.
- [ ] Check every rewritten link resolves: `grep -o 'https://[^) "]*' README.md CONTRIBUTING.md SECURITY.md PRIVACY.md | sort -u` then `curl -s -o /dev/null -w '%{http_code}'` each. Done when: every link returns `200` or a documented redirect (`301`/`302`); failures are listed and fixed.
- [ ] Commit: `"rebrand: documentation says Gemail"`

**Test checkpoint:** the `grep -c` commands above print `0`; the link check prints no `404`; a README rendered on GitHub shows the Gemail title and working install links to `https://rizonesoft.github.io/Gemail/manifest.xml`. Cheaper substitute that fails: renaming only the README title, which leaves the install links on the dead `/ai-email-writer/` path and fails the link check.

## 7. Redirect Stub for the Old Pages Path

A user who installed 1.3.2 from a downloaded `manifest.xml` keeps that file's URLs forever: Outlook never re-reads a sideloaded manifest, so their add-in loads `https://rizonesoft.github.io/ai-email-writer/taskpane.html` and the icons under `/ai-email-writer/assets/`, which have returned 404 since the repository rename. The operator's decision ("Full, with a redirect") keeps them working through a stub site at the old path: a repository named `rizonesoft/ai-email-writer` whose Pages site sends each page to the same page under `/Gemail/`. Both paths share the origin `https://rizonesoft.github.io`, so the redirect needs no new `AppDomain`. This section writes the stub; the operator creates the repository and publishes it (D99 T01 §3).

- [ ] Create `legacy/ai-email-writer/taskpane.html`: a minimal page that loads `office.js` from `https://appsforoffice.microsoft.com/lib/1/hosted/office.js` and runs `location.replace('/Gemail/taskpane.html' + location.search + location.hash)`, with a `<meta http-equiv="refresh" content="0; url=/Gemail/taskpane.html">` fallback. Done when: opening the file from a local static server at `/ai-email-writer/taskpane.html` lands on `/Gemail/taskpane.html` with the query string kept. Source: Microsoft Learn, AppDomains (https://learn.microsoft.com/javascript/api/manifest/appdomains): a same-origin navigation needs no AppDomain entry.
- [ ] Create `legacy/ai-email-writer/commands.html` the same way, targeting `/Gemail/commands.html`, so the ribbon's function file registers the Gemail command handlers after the redirect. Done when: a local static-server check lands on `/Gemail/commands.html`.
- [ ] Copy the icons the 1.3.2 manifest names (`assets/icon-16.png`, `-32`, `-64`, `-80`, `-128`, and `assets/tool-icons/*`) into `legacy/ai-email-writer/assets/` by a script, `scripts/build-legacy-stub.js`, so the ribbon icons keep loading from the old path. Done when: `node scripts/build-legacy-stub.js` copies them and every icon URL in the 1.3.2 manifest (`git show v1.3.2:manifest.xml`, rewritten to the old Pages path) maps to a file under `legacy/ai-email-writer/`.
- [ ] Copy the current production `manifest.xml` (Gemail URLs, unchanged Id) to `legacy/ai-email-writer/manifest.xml` in the same script, so an administrator whose organization deployment points at the old manifest URL is upgraded to the new URLs on Outlook's next manifest refresh. Done when: the copied manifest contains `rizonesoft.github.io/Gemail/` and no `ai-email-writer`.
- [ ] Add `legacy/ai-email-writer/README.md` saying what the stub is for, that it is published from the `rizonesoft/ai-email-writer` repository by the operator, and when it can be retired (when no installed 1.x remains). Exclude `legacy/` from webpack and lint. Done when: `npm run build` and `npm run lint` behave as before the section.
- [ ] Commit: `"rebrand: redirect stub for the old ai-email-writer Pages path"`

**Test checkpoint:** with `npx http-server legacy -p 8081` serving the folder, `curl -s http://localhost:8081/ai-email-writer/taskpane.html | grep -c "/Gemail/taskpane.html"` prints at least `1`, and a browser opened at `http://localhost:8081/ai-email-writer/taskpane.html?et=1` ends at `/Gemail/taskpane.html?et=1`; every icon path of the 1.3.2 manifest exists under `legacy/ai-email-writer/`. The live proof (a 1.3.2 install loading Gemail) is D99 T01 §3's checkpoint. Cheaper substitute that fails: a stub holding only `index.html`, which leaves the manifest's `taskpane.html`, `commands.html`, and icon URLs at 404 and fails the per-path checks.

## Verification

- [ ] `pwsh scripts/check-all.ps1` -- exits 0: production build, typecheck, lint, tests, manifest, TODO gates green
- [ ] `npx jest --ci` exits 0 with `src/features/settings.test.ts` reporting
- [ ] The Outcome's repository-wide `grep` for the old names prints nothing outside the named exclusions, and a sideloaded dev build seeded with 1.3.2 storage opens with every setting and template intact
