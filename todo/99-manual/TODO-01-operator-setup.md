---
schema_version: 1
id: operator-setup
domain: 99-manual
status: draft
title: "TODO-01 -- Operator Setup and Human Checks"
depends_on: []
---

# TODO-01 -- Operator Setup and Human Checks

> **Goal:** Every step that needs the owner's accounts, money, taste, or ears is written down with its trigger and its proof, so no runner stalls on it or fakes it: a funded development key, the production deploy dispatch, the legacy redirect repository, a signed-in review CLI, the Gemail artwork, test mailboxes in both supported clients, a screen reader pass, and the update of organization deployments.

> [!IMPORTANT]
> **Current state (verified 2026-09-27):** `.env` exists (gitignored) and names one variable, `GEMINI_API_KEY`; nothing names `OPENROUTER_API_KEY` yet. `.github/workflows/deploy.yml` deploys production only on `workflow_dispatch` with the boolean input `deploy_prod`, and the last production deploy (2026-03-05) still serves manifests that name `/ai-email-writer/`. `https://rizonesoft.github.io/ai-email-writer/manifest.xml` returns 404 because the repository was renamed to `Gemail` and no repository named `ai-email-writer` exists under `rizonesoft`. `codex login status` prints `Logged in using ChatGPT` on this machine. `assets/icons/` holds 10 SVG files that no manifest or page references, `assets/banner.png` carries the old name, and no capture, screen reader pass, or test-mailbox record exists under `docs/`. Every section below carries `**Requires:** operator`, which no detector reports, so `query ready` lists these rows as runnable elsewhere.
<!-- claim: count "GEMINI_API_KEY" .github/workflows/deploy.yml = 0 -->
<!-- claim: count "deploy_prod" .github/workflows/deploy.yml = 2 -->
<!-- claim: exists assets/banner.png -->
<!-- claim: absent docs/captures/taskpane -->

## Inputs

- [`AGENTS.md`](../../AGENTS.md) -- the operator's decisions of 2026-09-27 these rows carry out (supported clients, OpenRouter under the user's key, the redirect, trunk deploys)
- [`.github/workflows/deploy.yml`](../../.github/workflows/deploy.yml) -- the `deploy_prod` dispatch §2 runs
- [`scripts/panel_slots.py`](../../scripts/panel_slots.py) -- runs the review slots through the codex CLI §4 signs in
- `assets/icons/*.svg` -- the icon sources §5 replaces and D07 T01 §3 renders
- -> XREF: D00 T01 §1 -- the URL fix §2 dispatches to production
- -> XREF: D00 T03 §2 -- the panel probe that needs the codex CLI §4 signs in
- -> XREF: D01 T01 §7 -- the redirect stub §3 publishes from the legacy repository
- -> XREF: D05 T02 §3 -- the live regions and focus management §7 listens to with a screen reader
- -> XREF: D07 T01 §6 -- the 2.0.0 release §8 rolls out to organization deployments

## Outcome

- A development OpenRouter key with a spending limit sits in `.env` as `OPENROUTER_API_KEY`, and the live smoke can run.
- Production at `https://rizonesoft.github.io/Gemail/` serves the fixed manifest, and `https://rizonesoft.github.io/ai-email-writer/` serves the redirect stub again.
- The review panel's CLI is signed in, the Gemail artwork is committed, and test mailboxes in new Outlook and Outlook on the web are recorded.
- A screen reader pass and the organization rollout are recorded with dates and results.

**Adjacency:** all=not-applicable (operator procedures on external accounts and human checks; the product surfaces they touch are owned by the sections they depend on)

## Implementation Order

| Order | Section | Deliverable                                   | Depends On | Status |
| :---: | :-----: | --------------------------------------------- | ---------- | :----: |
|   1   |   §1    | Fund an OpenRouter key for development        | --         |  [ ]   |
|   2   |   §2    | Dispatch the production deploy                | D00 T01 §1 |  [ ]   |
|   3   |   §3    | Create the legacy redirect repository         | D01 T01 §7 |  [ ]   |
|   4   |   §4    | Sign in the codex CLI                         | --         |  [ ]   |
|   5   |   §5    | Gemail artwork                                | --         |  [ ]   |
|   6   |   §6    | Test mailboxes in new Outlook and on the web  | --         |  [ ]   |
|   7   |   §7    | Screen reader pass                            | D05 T02 §3 |  [ ]   |
|   8   |   §8    | Update organization deployments               | D07 T01 §6 |  [ ]   |

---

## 1. Fund an OpenRouter Key for Development

The contract fixtures of `02-openrouter` are recorded from the real endpoint, and the live smoke calls it; both need a key only the owner can buy. Users bring their own keys; this one is for development and is never shipped, logged, or committed.

**Requires:** operator -- buying OpenRouter credits and creating a key needs the owner's OpenRouter account and payment method

- [ ] Create an OpenRouter key named `gemail-dev` at https://openrouter.ai/settings/keys with a credit limit (suggested: 5 USD). Done when: the key list shows `gemail-dev` with the limit set.
- [ ] Add `OPENROUTER_API_KEY=<key>` to `.env` in the repository root and remove the obsolete `GEMINI_API_KEY` line. Done when: `grep -c "^OPENROUTER_API_KEY=" .env` prints `1` and `git check-ignore .env` prints `.env`.
- [ ] Confirm the key works without printing it: `curl -s -o /dev/null -w '%{http_code}\n' -H "Authorization: Bearer $OPENROUTER_API_KEY" https://openrouter.ai/api/v1/key`. Done when: it prints `200`.
- [ ] Commit: `"manual: record the development OpenRouter key setup (no secret)"`

**Test checkpoint:** the `/api/v1/key` probe prints `200`; `git grep -c "sk-or-"` over tracked files prints nothing; the key's limit is visible in the OpenRouter dashboard. Cheaper substitute that fails: an unlimited key, which the dashboard check refuses.

## 2. Dispatch the Production Deploy

Production deploys only on the operator's dispatch (operator decision 2026-09-27). Until it runs after `D00 T01 §1`, installed users keep loading a manifest that names the dead path.

**Requires:** operator -- `workflow_dispatch` with `deploy_prod` is the owner's release decision on the `rizonesoft/Gemail` repository

- [ ] Run `gh workflow run deploy.yml -f deploy_prod=true` (or the Actions tab with **Deploy to production** ticked). Done when: `gh run list --workflow deploy.yml --limit 1 --json event,conclusion` shows `workflow_dispatch` and `success`.
- [ ] Read back production: `curl -s -o /dev/null -w '%{http_code}\n'` for `https://rizonesoft.github.io/Gemail/manifest.xml`, `/Gemail/taskpane.html`, and `/Gemail/commands.html`, and `curl -s https://rizonesoft.github.io/Gemail/manifest.xml | grep -c ai-email-writer`. Done when: three `200` lines and a count of `0`.
- [ ] Commit: `"manual: production deploy after the Pages path fix"`

**Test checkpoint:** the three production URLs return `200` and the production manifest names no `ai-email-writer`; a fresh sideload of `https://rizonesoft.github.io/Gemail/manifest.xml` in Outlook on the web opens the task pane. Cheaper substitute that fails: relying on the dev deploy, which serves `/Gemail/dev/` and leaves the production manifest naming the dead path.

## 3. Create the Legacy Redirect Repository

Users who installed from the old manifest file keep its URLs forever (a sideloaded manifest is not re-fetched), so their Outlook asks `https://rizonesoft.github.io/ai-email-writer/taskpane.html`. GitHub Pages serves that path again only from a repository named `ai-email-writer`; `D01 T01 §7` writes the same-origin redirect stub it serves.

**Requires:** operator -- creating a repository and enabling Pages needs the owner's rights on the `rizonesoft` GitHub organization

- [ ] Create the public repository `rizonesoft/ai-email-writer` with a README pointing to `rizonesoft/Gemail`. Done when: `gh repo view rizonesoft/ai-email-writer --json name` prints the name.
- [ ] Copy the contents of `legacy/ai-email-writer/` from `rizonesoft/Gemail` to the root of the new repository and push. Done when: `gh api repos/rizonesoft/ai-email-writer/contents` lists `taskpane.html`, `commands.html`, and `manifest.xml`.
- [ ] Enable Pages from the `main` branch root. Done when: `gh api repos/rizonesoft/ai-email-writer/pages --jq .status` prints `built`.
- [ ] Read back: `curl -s -o /dev/null -w '%{http_code}\n' https://rizonesoft.github.io/ai-email-writer/taskpane.html`. Done when: it prints `200`, and an Outlook client with the old manifest installed opens the Gemail task pane.
- [ ] Commit: `"manual: publish the legacy redirect for the old Pages path"`

**Test checkpoint:** `https://rizonesoft.github.io/ai-email-writer/taskpane.html` returns `200` and, loaded in a browser, lands on `https://rizonesoft.github.io/Gemail/taskpane.html`; an Outlook profile with the 1.3.2 manifest installed opens a working task pane. Cheaper substitute that fails: asking users to reinstall in the README, which the old-manifest profile check does not satisfy.

## 4. Sign In the Codex CLI

Every review slot in `.conclave/panel.toml` runs through the `codex` CLI, and there are no fallback slots: a signed-out CLI parks every stamp. `D00 T03 §2` checks the sign-in first and stops when it is missing.

**Requires:** operator -- signing in needs the owner's ChatGPT or OpenAI account

- [ ] Run `codex login` and complete the browser sign-in. Done when: `codex login status` prints a signed-in line.
- [ ] Record `codex --version` and the sign-in date in `docs/reviews/run-records.md` beside the panel probe of `D00 T03 §2`, or in the commit body if that section has not run. Done when: the version is recorded.
- [ ] Commit: `"manual: sign in the codex CLI for the review panel"`

**Test checkpoint:** `codex login status` prints a signed-in line and `python scripts/panel_slots.py validate` exits 0. Cheaper substitute that fails: an API key exported in one shell, which the next session does not inherit and `codex login status` does not report.

## 5. Gemail Artwork

The name changes in `01-rebrand`, but the pictures carry the old one: the README banner, the social preview, and the icon sources. Artwork is a taste call. `D07 T01 §3` renders every manifest icon size from the SVG sources this section commits.

**Requires:** operator -- choosing the logo and banner is the owner's brand decision for Rizonesoft

- [ ] Commit the Gemail logo mark as `assets/icons/gemail.svg` (square, legible at 16 px) and replace the other `assets/icons/*.svg` sources the ribbon uses. Done when: `ls assets/icons/*.svg` lists `gemail.svg`.
- [ ] Replace `assets/banner.png` and `assets/social-preview.png` with Gemail versions at their current pixel sizes. Done when: `python -c` with the PNG header read prints the same width and height as before for each file.
- [ ] Upload the social preview in the repository settings (Settings, General, Social preview). Done when: `gh api repos/rizonesoft/Gemail --jq .open_graph_image_url` changes from its previous value.
- [ ] Commit: `"manual: Gemail artwork"`

**Test checkpoint:** the README renders the new banner on github.com; `assets/icons/gemail.svg` opens in a browser at 16 px and is recognizable; the repository's social preview shows the Gemail artwork. Cheaper substitute that fails: text-only banners with the new name, which the 16 px legibility check exposes when D07 T01 §3 renders the icon.

## 6. Test Mailboxes in New Outlook and on the Web

Gemail supports new Outlook and Outlook on the web (operator decision 2026-09-27: "New Outlook + web"). Driven runs and captures need a mailbox in each, signed in with an account that allows sideloading custom add-ins.

**Requires:** operator -- the Microsoft 365 or Outlook.com accounts and their sign-in belong to the owner

- [ ] Sign in to Outlook on the web and to new Outlook for Windows with a mailbox that allows custom add-ins, and sideload `manifest.dev.xml` in each through https://aka.ms/olksideload. Done when: the **Gemail (Dev)** button (or, before the rename ships, **AI Compose (Dev)**) appears on a read message in both.
- [ ] Put three fixture messages in the mailbox: a short single message, a long thread (at least 10 quoted replies), and a message with a PDF and a text attachment. Done when: each is findable by the subject prefix `[gemail-fixture]`.
- [ ] Record the mailbox type, client versions (new Outlook: Help, About), and the fixture subjects in `docs/dev/test-mailboxes.md`, with no address or password. Done when: the file lists both clients and three fixtures.
- [ ] Commit: `"manual: test mailboxes for new Outlook and the web"`

**Test checkpoint:** `docs/dev/test-mailboxes.md` lists both clients with versions and the three fixture subjects; opening the long-thread fixture in each client shows the dev add-in button. Cheaper substitute that fails: testing only in the browser, which never exercises new Outlook's WebView2 host.

## 7. Screen Reader Pass

`05-quality` gives every control a name, the tab bar its semantics, and the pane its live regions, and proves them with DOM assertions. Whether a person using a screen reader can actually draft a reply is a human judgment no assertion replaces.

**Requires:** operator -- a screen reader pass needs a person listening to Narrator and NVDA, which no agent session can do

- [ ] With Narrator in new Outlook, open the task pane on the long-thread fixture, move through the tab bar with the arrow keys, generate a reply, and insert it, by keyboard only. Done when: each step is recorded as heard or not heard in `docs/dev/screen-reader-pass.md`.
- [ ] Repeat with NVDA (record its version) in Outlook on the web in Edge. Done when: the same table has an NVDA column.
- [ ] File every failure through `add-todo` against the owning section of `todo/05-quality/TODO-02-accessibility.md`, quoting what was heard. Done when: no failure is left only in the notes.
- [ ] Commit: `"manual: screen reader pass in new Outlook and on the web"`

**Test checkpoint:** `docs/dev/screen-reader-pass.md` records both readers with versions and a verdict per step, and every failing step names the section it was filed against. Cheaper substitute that fails: an automated axe run, which checks markup and cannot hear whether the streamed reply is announced.

## 8. Update Organization Deployments

Organizations that deployed the add-in through the Microsoft 365 admin center point it at a manifest URL. After 2.0.0 ships, deployments that still name `/ai-email-writer/manifest.xml` must be repointed to `/Gemail/manifest.xml`.

**Requires:** operator -- the Microsoft 365 admin center belongs to each tenant's administrator, reached through the owner's contacts

- [ ] In the admin center of every tenant the owner manages (Settings, Integrated apps), update the Gemail app's manifest URL to `https://rizonesoft.github.io/Gemail/manifest.xml`. Done when: the app details show the new URL and version 2.0.0.
- [ ] Publish a short notice for administrators (a GitHub release note paragraph and the README's organization deployment steps) naming the new URL. Done when: the 2.0.0 release notes contain the URL.
- [ ] Commit: `"manual: repoint organization deployments to the Gemail manifest"`

**Test checkpoint:** a user in a managed tenant sees **Gemail** 2.0.0 in Outlook within the admin center's propagation window (up to 72 hours), and the admin center lists the new manifest URL. Cheaper substitute that fails: relying on the legacy redirect alone, which keeps the tenant on the old manifest's version and name.

## Verification

- [ ] `python scripts/todo-graph.py query ready --context operator` lists every row of this file whose dependency has shipped
- [ ] Each section's record (the commit or the `docs/dev/` file it names) exists and carries a date
