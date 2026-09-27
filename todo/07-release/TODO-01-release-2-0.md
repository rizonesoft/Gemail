---
schema_version: 1
id: release-2-0
domain: 07-release
status: draft
title: "TODO-01 -- Release 2.0.0"
depends_on: []
---

# TODO-01 -- Release 2.0.0

> **Goal:** Gemail 2.0.0 ships: its manifests declare the Mailbox requirement sets the code actually needs for new Outlook and Outlook on the web, reference only icons that exist, are generated from one source and validated in CI, every icon size is rendered from committed SVG sources, the release process is written down and repeatable, the user guide covers installing and every feature, the `v2.0.0` tag is pushed and deployed to production by the operator's dispatch, and a clean Outlook profile that has never seen the add-in installs it from the production manifest and runs every feature.

> [!IMPORTANT]
> **Current state (verified 2026-09-27):** Both manifests declare `<Set Name="Mailbox" MinVersion="1.1"/>` (line 21), `VersionOverridesV1_0` with `DefaultMinVersion="1.3"`, and a nested `VersionOverridesV1_1` with `1.5`, while the code calls `item.from.getAsync` (Mailbox 1.7, guarded) and `addHandlerAsync` for `ItemChanged` (1.5, unguarded), and `D06 T03 §1` adds the attachment content API (1.8). Each manifest references `OpenPanel.16x16`, `.32x32`, and `.80x80` images (six entries, once in each `VersionOverrides` block) at `assets/tool-icons/open-panel-*.png`, which do not exist and which no control uses, and names the Fix Grammar icons `fix-grammer-spelling-*` (six references per manifest, matching the misspelled files). `manifest.dev.xml` is a hand-kept copy with its own Id and a stale version, and `.github/workflows/deploy.yml` also patches the built manifest with one `sed -i` block. `assets/icons/` holds 10 SVG feature icons that nothing references, and the PNG icons have no committed source. There is no `docs/user/` and no `docs/dev/`. `package.json` is at `1.3.2`, with `preversion` running `npm test` and `postversion` pushing the commit and tags; the last tag is `v1.3.2`.
<!-- claim: count "<Set Name=\"Mailbox\" MinVersion=\"1.1\"/>" manifest.xml = 1 -->
<!-- claim: count "open-panel" manifest.xml = 6 -->
<!-- claim: count "fix-grammer-spelling" manifest.xml = 6 -->
<!-- claim: absent docs/user -->
<!-- claim: absent docs/dev/release.md -->
<!-- claim: count "\"version\": \"1.3.2\"" package.json = 1 -->

## Inputs

- [`manifest.xml`](../../manifest.xml), [`manifest.dev.xml`](../../manifest.dev.xml) -- the requirement sets, icon references, and duplicated structure §1 and §2 fix
- [`.github/workflows/deploy.yml`](../../.github/workflows/deploy.yml) -- the dev patch §2 replaces and the `deploy_prod` dispatch §6 relies on
- [`scripts/sync-manifest-version.js`](../../scripts/sync-manifest-version.js) -- the `npm version` hook §4 documents
- [`assets/`](../../assets/) -- the icons §3 renders
- Microsoft Learn, "Outlook JavaScript API requirement sets" (https://learn.microsoft.com/javascript/api/requirement-sets/outlook/outlook-api-requirement-sets) and "Requirements element" (https://learn.microsoft.com/javascript/api/manifest/requirements) -- the sets §1 declares
- Microsoft Learn, "Deploy and publish Office Add-ins" (https://learn.microsoft.com/office/dev/add-ins/publish/publish) and "Centralized Deployment" (https://learn.microsoft.com/microsoft-365/admin/manage/centralized-deployment-of-add-ins) -- the install paths §5 documents
- -> XREF: D00 T01 §1 -- §1 starts from the manifests whose URLs that section fixed
- -> XREF: D00 T02 §4 -- §2 adds manifest validation to the CI build workflow that section writes
- -> XREF: D04 T01 §7 -- §6 ships only once the privacy and security docs are truthful
- -> XREF: D05 T01 §6 -- §6 ships only with the coverage ratchet in CI
- -> XREF: D05 T02 §4 -- §6 ships only once the accessibility sections have landed
- -> XREF: D06 T01 §5 -- §5 documents the settings upgrades
- -> XREF: D06 T02 §3 -- §5 documents custom prompts and keyboard shortcuts
- -> XREF: D06 T03 §4 -- §5 documents attachments, the timeline, and CC suggestions
- -> XREF: D06 T04 §3 -- §5 documents the theme behavior and the usage view
- -> XREF: D99 T01 §8 -- the operator updates organization deployments after §6 ships
- -> XREF: D03 T04 §5 -- the manifests already point at the approved icons in `assets/icons/png/`

## Outcome

- Both manifests declare the lowest Mailbox set the core features need, features above it are guarded with `isSetSupported` and say so to the user, and every image URL a manifest names exists under `dist/`.
- `manifest.dev.xml` is generated from `manifest.xml` by one script, and CI validates both with `office-addin-manifest validate`.
- `node scripts/render-icons.js` renders every PNG the manifests name from committed SVGs, and a check fails when a size is missing.
- `docs/dev/release.md` describes one release end to end, and `docs/user/` holds the install guide for new Outlook and the web, admin deployment, and one page per feature.
- The tag `v2.0.0` exists on `origin`, production serves `2.0.0.0` in `manifest.xml`, and a clean Outlook profile installs it and runs every feature.

**Adjacency:** list=not-applicable (a release has no collection to browse); document=not-applicable (the release produces no user document; the user guide of §5 is repository documentation); settings=not-applicable (release configuration is the manifest and the workflow, with no user-tunable value); reporting=applicable @ D07 T01 §4; notifications=applicable @ D07 T01 §1; permissions=applicable @ D07 T01 §1; audit=applicable @ D07 T01 §4; exchange=not-applicable (the release imports and exports no user data); reverse=applicable @ D07 T01 §4

**Adjacency rationale:** Permissions and notifications in §1 are the client-below-requirement-set path: a feature a client cannot run is disabled with a message rather than failing. Audit and reverse in §4 are the CHANGELOG and tag history and the documented rollback (redeploy the previous tag).

## Implementation Order

| Order | Section | Deliverable                                  | Depends On                                      | Status |
| :---: | :-----: | -------------------------------------------- | ----------------------------------------------- | :----: |
|   1   |   §1    | Requirement sets for new Outlook and the web | D00 T01 §1, D03 T04 §5 |  [ ]   |
|   2   |   §2    | One manifest source and validation in CI     | §1, D00 T02 §4                                  |  [ ]   |
|   3   |   §3    | Icons at every size from the SVG sources     | §1                                              |  [ ]   |
|   4   |   §4    | The release process                          | §2                                              |  [ ]   |
|   5   |   §5    | The user guide                               | D06 T01 §5, D06 T02 §3, D06 T03 §4, D06 T04 §3  |  [ ]   |
|   6   |   §6    | Ship v2.0.0                                  | §4, §5, D05 T01 §6, D05 T02 §4, D04 T01 §7      |  [ ]   |
|   7   |   §7    | Clean-install acceptance                     | §6                                              |  [ ]   |

---

## 1. Requirement Sets for New Outlook and the Web

The operator decided on 2026-09-27 to support new Outlook and Outlook on the web only. Both implement recent Mailbox sets, so the manifest can declare what the code needs instead of 1.1, and guard only the features above that floor. This section measures the APIs in use, chooses the floor, and cleans the icon references that point at nothing.

- [ ] Write `docs/dev/requirement-sets.md`: a table of every Office.js member the code calls (from `grep -rn "Office\.\|item\.\|mailbox\." src --include=*.ts`), the Mailbox set each needs (from the Microsoft Learn requirement set pages), and the feature that uses it. Done when: every call in the grep maps to a row with a source link. Source: https://learn.microsoft.com/javascript/api/requirement-sets/outlook/outlook-api-requirement-sets
- [ ] Set `<Set Name="Mailbox" MinVersion>` in `manifest.xml` to the highest set a core feature (Reply, Draft, Summarize, Improve, Extract, Translate) needs, and the `VersionOverrides` `DefaultMinVersion` values to match. Done when: `npm run validate` passes and the chosen set is justified in the table.
- [ ] Apply one client policy: guard every call above the floor with `Office.context.requirements.isSetSupported("Mailbox", "<set>")`, and when unsupported disable the control and notify the user with its reason ("Needs a newer Outlook"). Done when: a mock test per guarded feature asserts the disabled state and message on a client reporting only the floor.
- [ ] Remove the six `OpenPanel.*` image entries from `manifest.xml` and `manifest.dev.xml`. Done when: `grep -c open-panel manifest.xml` prints `0`.
- [ ] Confirm the misspelt icon is gone: `D03 T04 §5` replaced `assets/tool-icons/` with `assets/icons/png/menu/fix-grammar-and-spelling-*.png`. Done when: `grep -rc grammer manifest.xml manifest.dev.xml assets` prints only zeros. **Corrected 2026-09-27:** was "Rename `assets/tool-icons/fix-grammer-spelling-{16,32,80}.png` ... with `git mv`"; the whole directory was retired by the design import's icon set.
- [ ] Add `scripts/check-manifest-assets.js` that lists every `DefaultValue="https://localhost:3000/..."` image and page URL in `manifest.xml` and asserts the file exists under `dist/` after `npm run build`. Done when: it exits 0 now and exits 1 naming the file when an icon is deleted in a scratch copy.
- [ ] Commit: `"manifest: requirement sets for new Outlook and the web, and no dead icons"`

**Test checkpoint:** `npm run validate` passes; `node scripts/check-manifest-assets.js` exits 0 after `npm run build`, and exits 1 naming `assets/icons/png/app/gemail-80.png` when that file is removed in a scratch copy; the requirement-set tests pass under `npx jest src/services/outlook.test.ts -t "requirement"`. Cheaper substitute that fails: leaving `MinVersion="1.1"`, which the table shows is below the APIs called unguarded.

## 2. One Manifest Source and Validation in CI

Two hand-kept manifests drift (the dev one is already a version behind and carries its own Id), and `deploy.yml` patches the built manifest a second way. One generator from `manifest.xml` removes both kinds of drift, and CI validates what it generates.

- [ ] Add `scripts/make-dev-manifest.js` that reads `manifest.xml` and writes `manifest.dev.xml` with the dev Id (`b92d4e5f-6a78-4901-bc23-de45fa67bc89`), the `(Dev)` display name, and the dev description, and with `--pages <url>` rewrites the URL base for a deploy. Done when: running it reproduces the committed `manifest.dev.xml` byte for byte after its structure is regenerated once.
- [ ] Replace the `sed -i` block in `.github/workflows/deploy.yml` with `node scripts/make-dev-manifest.js --pages https://rizonesoft.github.io/Gemail/dev/ --out dist/manifest.xml`. Done when: `grep -c "sed -i" .github/workflows/deploy.yml` prints `0` and the dev deploy's manifest has the dev Id.
- [ ] Add a CI check in `.github/workflows/build.yml` that regenerates `manifest.dev.xml` and fails on a diff, and validates both manifests with `npx office-addin-manifest validate`. Done when: a scratch commit editing only `manifest.dev.xml` fails the check.
- [ ] Make `scripts/sync-manifest-version.js` update `manifest.xml` only and call the generator. Done when: `npm version prerelease --no-git-tag-version` in a scratch clone changes both manifests consistently.
- [ ] Commit: `"manifest: generate the dev manifest from one source and validate both in CI"`

**Test checkpoint:** `node scripts/make-dev-manifest.js --check` exits 0 on the committed tree and exits 1 after a hand edit to `manifest.dev.xml`; the `build` workflow run for the section's commit shows both validate steps green (`gh run view` output quoted). Cheaper substitute that fails: keeping two hand-kept files and validating both, which the drift probe shows passes while the versions differ.

## 3. Icons at Every Size From the SVG Sources

The PNG icons have no committed source, so every size is redrawn by hand or upscaled. This section commits SVG sources for the app icon and the ribbon tool icons and renders every size the manifests name, so the operator's new artwork (`D99 T01 §5`) lands by replacing one SVG and rerunning one command. Rendering needs a rasterizer: `@resvg/resvg-js` (a WebAssembly build, no native toolchain on Windows) is the chosen dev dependency, recorded here as the section's dependency decision.

- [ ] Confirm the sources are complete: `assets/icons/src/app/`, `ribbon/`, and `menu/` hold the app icon (48 and 16 px drawings), AI Tools, and the four menu icons imported from the approved mockup on 2026-09-27, and `D03 T04 §5` points both manifests at their renders. Done when: `node tools/design/icons.mjs --check` exits 0 and every icon URL in `manifest.xml` names a file under `assets/icons/png/`. **Corrected 2026-09-27:** was "Add `assets/icons/source/app.svg` and one SVG per ribbon tool icon ... tracing the current PNG"; the sources were drawn in the design mockup and imported (`docs/design/icons.md`).
- [ ] Run the icon check in CI: add `npm ci --prefix tools/design` and `node tools/design/icons.mjs --check` steps to `.github/workflows/build.yml`. Done when: the `build` run on the pushed commit shows the step passing (`gh run view --log` quoted). **Corrected 2026-09-27:** was "`npm install -D @resvg/resvg-js` and add `scripts/render-icons.js`"; the renderer is `tools/design/icons.mjs` with its own `package.json`, so the rasterizer never enters the add-in's dependencies. **Open 2026-09-27:** the steps and a true re-render (byte-identical PNGs, verified on Windows and Linux) shipped in `35fd3d5` (operator request 2026-09-27, shipped ahead of the row; the row still stamps through `review-todo-section`); the Done-when read-back waits for the first push.
- [x] Prove the check fails on a stale output: in a scratch copy delete `assets/icons/png/app/gemail-64.png`, and separately edit one byte of `assets/icons/src/menu/make-concise.svg`. Done when: `node tools/design/icons.mjs --check` and `python scripts/design-lint.py` each exit 1 naming the file in both cases. **Corrected 2026-09-27:** was "Add `--check`"; `--check` exists in `tools/design/icons.mjs`, and `scripts/design-lint.py` checks the same manifest without rendering. **Shipped 2026-09-27** (operator request 2026-09-27, shipped ahead of the row; the row still stamps through `review-todo-section`): deleting `assets/icons/png/app/gemail-64.png` makes `node tools/design/icons.mjs --check` exit 1 ("is missing") and `python scripts/design-lint.py` exit 1 naming it; editing `assets/icons/src/menu/make-concise.svg` makes both exit 1 ("changed since the last build").
- [x] Confirm the 256 px listing icon: `assets/icons/png/app/gemail-256.png` is rendered from the same source. Done when: `python -c "import struct;d=open('assets/icons/png/app/gemail-256.png','rb').read(24);print(struct.unpack('>II',d[16:24]))"` prints `(256, 256)`. **Corrected 2026-09-27:** was "Add a high-resolution `assets/icon-256.png`"; the icon build renders it at `assets/icons/png/app/gemail-256.png`. **Shipped 2026-09-27:** the struct probe prints `(256, 256)`.
- [ ] Commit: `"icons: render every icon size from committed SVG sources"`

**Test checkpoint:** `node tools/design/icons.mjs --check` exits 0 locally and in the `build` workflow; the scratch deletion of `gemail-64.png` and the scratch source edit each make it and `python scripts/design-lint.py` exit 1; `node scripts/check-manifest-assets.js` still exits 0 after `npm run build`. Cheaper substitute that fails: committing resized PNGs without their sources, which the manifest hashes refuse.

## 4. The Release Process

Releases today depend on remembering that `npm version` syncs the manifests, pushes the tag, and that production deploys only through the operator's `deploy_prod` dispatch. This section writes the process down once and makes the CHANGELOG part of it, so every release reports what changed and can be rolled back.

- [ ] Write `docs/dev/release.md`: preconditions (`pwsh scripts/check-all.ps1` green, CHANGELOG `[Unreleased]` filled), `npm version <major|minor|patch>` (what `preversion`, `version`, and `postversion` each do), reading back the dev deploy, the operator's production dispatch (`gh workflow run deploy.yml -f deploy_prod=true`), reading back production URLs, and the rollback (dispatch the previous tag's build). Done when: a scratch run of every command up to the tag, with `--no-git-tag-version`, matches the document.
- [ ] Add `scripts/check-changelog.js` that fails when `package.json`'s version has no `## [<version>]` heading in `CHANGELOG.md` with at least one entry, and run it in `preversion` after `npm test`. Done when: `npm version patch --no-git-tag-version` in a scratch clone with an empty `[Unreleased]` fails naming the missing section.
- [ ] Add a release-summary report to `docs/dev/release.md`: the table a release records (version, tag, commit, dev and production deploy run URLs, date). Done when: the table has columns and the 1.3.2 row filled from `gh run list` history as its example.
- [ ] Commit: `"release: document and check the release process"`

**Test checkpoint:** `node scripts/check-changelog.js` exits 0 on the committed tree (1.3.2 has a CHANGELOG entry) and exits 1 in a scratch clone after `npm version patch --no-git-tag-version` with no new entry; every command in `docs/dev/release.md` up to the tag runs in a scratch clone as written. Cheaper substitute that fails: a README paragraph, which the scratch run shows skips the CHANGELOG and the read-backs.

## 5. The User Guide

A user who installs Gemail from a manifest file needs to know how in each supported client, an administrator needs the centralized deployment steps, and every feature needs a page that says what it sends to OpenRouter and what it writes into mail. The guide ships before the release so 2.0.0 is learnable.

**Fidelity:** Gemail user guide pages under `docs/user/`, each with captures from docs/captures/taskpane/. Page structure per the guide spec: purpose, steps, what is sent, what is written, troubleshooting.
**Design:** docs/design/mockup.md#surfaces-the-mockup-does-not-draw, docs/design/mockup.md#pane-icons, new surface: docs/design/user-guide.md -- states: all in spec -- themes: n/a (Markdown pages rendered by GitHub) -- density: n/a (Markdown pages rendered by GitHub)
**Job:** A user can install Gemail and learn every feature from the guide documents without asking anyone. Consumer: the README links and the Settings panel help link.
**Treatment:** one page per feature plus Install (new Outlook, Outlook on the web), Administrator deployment, Privacy and your key, and Troubleshooting; each feature page states what data leaves the device. Cheaper substitute that fails the checkpoint: one long README section, which fails the page-per-feature link check.
**Chrome:** consume the captures under `docs/captures/taskpane/` and the privacy wording of `PRIVACY.md`; do not restate the privacy policy in a second wording.
**Needs:** Outlook client (sideload)
**Requires:** display-session -- the install pages are proven by following them in sideloaded new Outlook and Outlook on the web windows

- [ ] Write `docs/design/user-guide.md`: the page template (purpose, steps, what is sent, what is written, troubleshooting), capture naming, and tone. Done when: the file exists and the Design line above resolves under `python scripts/todo-graph.py validate`.
- [ ] Write `docs/user/install.md` for new Outlook and Outlook on the web from the production manifest URL, and `docs/user/admin-deployment.md` for the Microsoft 365 admin centre. Done when: following each on a test mailbox installs the add-in, recorded in the commit body.
- [ ] Write the feature documents, one page per feature (`reply.md`, `draft.md`, `summarize.md`, `improve.md`, `extract.md`, `translate.md`, `prompts.md`, `settings.md`, `shortcuts.md`, `attachments.md`, `timeline.md`, `usage.md`) with current captures. Done when: every tab and Settings group in the pane has a page.
- [ ] Write `docs/user/privacy-and-your-key.md` and `docs/user/troubleshooting.md` (one entry per error message the pane can show, from the error table of `D03 T03 §1`). Done when: every message in that table has an entry.
- [ ] Add `docs/user/README.md` as the index and `scripts/check-docs-links.js` that fails on a dead relative link or image under `docs/user/`. Done when: the check exits 0 and exits 1 after renaming a capture in a scratch copy.
- [ ] Link the guide from `README.md` and from the Settings panel footer. Done when: both links resolve on the deployed dev build.
- [ ] Hold the built surface to the approved mockup: render it (sideloaded, or in the jsdom harness for a component), compare it with the anchors on this section's `**Design:**` line in `docs/design/mockup.md` and their renders under `docs/design/mockup/renders/`, use only design tokens (`docs/design/tokens.json`) and registry icons (`iconSvg()` from `src/ui/icons.ts`), and commit a capture of the result under `docs/captures/taskpane/`. Done when: `python scripts/design-lint.py` exits 0 with the baseline no larger, every difference from the mockup is fixed or recorded as a `**Design deviation:**` naming its follow-up section, and the capture is committed. Cheaper substitute that fails: building from the prose alone, which the capture comparison at review refuses.
- [ ] Commit: `"docs: the Gemail user guide"`

**Test checkpoint:** `node scripts/check-docs-links.js` exits 0; a person following `docs/user/install.md` on a test mailbox in each supported client installs the add-in (recorded with a capture per client); the troubleshooting page has an entry for every error message, checked by a test that compares the page's headings to the error table. Cheaper substitute that fails: a single README section, which fails the one-page-per-feature and error-coverage checks.

## 6. Ship v2.0.0

The rename and the provider change break every installed configuration (a Gemini key does not work with OpenRouter), so the release is a major version. This section cuts it through the process of §4. The production deploy is the operator's dispatch (`AGENTS.md`), so the section is marked for the operator; an agent prepares everything up to it.

**Requires:** operator -- the production deploy is the operator's `deploy_prod` dispatch (AGENTS.md, Trunk and deploys), which no runner may trigger

- [ ] Fill `CHANGELOG.md` `## [2.0.0]` with the rename, the move to OpenRouter (and that existing users must enter an OpenRouter key), the supported clients, and every user-facing feature and fix, from `git log v1.3.2..HEAD`. Done when: `node scripts/check-changelog.js` passes after the version bump.
- [ ] Run `pwsh scripts/check-all.ps1` at the release commit and quote the gate table. Done when: every gate is `PASS`.
- [ ] Run `npm version major` to move `1.3.2` to `2.0.0`, which syncs both manifests to `2.0.0.0` and the footer. Done when: `package.json`, `manifest.xml`, and `manifest.dev.xml` all read 2.0.0.
- [ ] Push the tag `v2.0.0` and the commit (the `postversion` script does both). Done when: `git ls-remote --tags origin v2.0.0` prints the release commit.
- [ ] The operator dispatches the production deploy: `gh workflow run deploy.yml -f deploy_prod=true`. Done when: the run concludes `success` for the tagged commit.
- [ ] Read back production: `curl -s https://rizonesoft.github.io/Gemail/manifest.xml | grep -o "<Version>[^<]*"` and the taskpane, commands, and every icon URL return 200. Done when: `<Version>2.0.0.0` and every URL `200`, recorded in the release table of `docs/dev/release.md`.
- [ ] Commit: `"release: Gemail 2.0.0"`

**Test checkpoint:** `git ls-remote --tags origin v2.0.0` resolves to the release commit; the production manifest reports `2.0.0.0`; every URL it names returns 200 (the loop output quoted); the release row in `docs/dev/release.md` links both deploy runs. Cheaper substitute that fails: tagging without the production dispatch, which leaves production at `1.3.2.0` and fails the manifest read-back.

## 7. Clean-Install Acceptance

A developer's mailbox has the add-in's history: sideloads, cached settings, old keys. Only a profile that has never loaded Gemail shows whether a new user can install 2.0.0 from the production manifest and use every feature. `process-plan` re-runs this section at the end of the plan as the terminal acceptance.

**Needs:** Clean Outlook profile (install test)
**Requires:** display-session -- the acceptance drives new Outlook and Outlook on the web windows on a profile that has never loaded the add-in

- [ ] On a mailbox and browser profile that has never loaded the add-in, install from `https://rizonesoft.github.io/Gemail/manifest.xml` following `docs/user/install.md`, in Outlook on the web and in new Outlook. Done when: the ribbon shows the Gemail group in both, with captures.
- [ ] Complete first run: the privacy notice appears, a new OpenRouter key is entered, Test Connection succeeds. Done when: each step is captured and the key is absent from `Office.context.roamingSettings` (read in the dev tools console).
- [ ] Run every feature once in read and compose mode as the feature pages describe: Reply, Draft, Summarize (including Timeline and an attachment), Improve with Accept and restore, Extract, Translate, a custom prompt, a CC suggestion, and each ribbon AI Tools command. Done when: each result is recorded in a table in the commit body with pass or the defect filed through `add-todo`.
- [ ] Record the run in `docs/dev/release.md` (date, clients and versions, mailbox type, result). Done when: the acceptance row exists.
- [ ] Commit: `"release: clean-install acceptance for 2.0.0"`

**Test checkpoint:** the acceptance table shows every feature passing in both clients on a clean profile, with captures under `docs/captures/acceptance/2.0.0/`; any failure reopens the owning section rather than being noted and passed. Cheaper substitute that fails: running the acceptance in the developer's own mailbox, which already holds settings and a key and cannot show the first-run path.

## Verification

- [ ] `pwsh scripts/check-all.ps1` -- exits 0: production build, typecheck, lint, tests, manifest, icons, changelog, docs links, TODO gates green
- [ ] `node scripts/check-manifest-assets.js`, `node scripts/render-icons.js --check`, and `node scripts/make-dev-manifest.js --check` exit 0
- [ ] The production manifest reports `2.0.0.0` and the clean-install acceptance row is recorded in `docs/dev/release.md`
