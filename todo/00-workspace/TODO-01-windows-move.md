---
schema_version: 1
id: windows-move
domain: 00-workspace
status: draft
title: "TODO-01 -- Move to Windows and Restore the Live Add-in"
depends_on: []
---

# TODO-01 -- Move to Windows and Restore the Live Add-in

> **Goal:** The published add-in loads again for every user, and the repository works on the Windows clone it moved to: every manifest URL follows the repository rename to `Gemail`, the dev certificates are trusted by Windows so `npm start` sideloads, text files are stored and checked out with the line endings the tooling expects, Node is pinned, and VS Code on Windows debugs the add-in in new Outlook.

> [!IMPORTANT]
> **Current state (verified 2026-09-27):** The GitHub repository was renamed from `ai-email-writer` to `Gemail`, which moved GitHub Pages from `https://rizonesoft.github.io/ai-email-writer/` (now 404) to `https://rizonesoft.github.io/Gemail/` (200). Every URL the add-in loads still names the old path: `urlProd` in `webpack.config.js` line 8 is `https://rizonesoft.github.io/ai-email-writer/`, the manifest CopyWebpackPlugin rewrites `https://localhost:3000/` to it, and the manifest served today at `/Gemail/manifest.xml` points its icons and pages at `/ai-email-writer/`, so the task pane and the ribbon commands fail for every installed user. `.github/workflows/deploy.yml` lines 63-64 (54-55 before the build gate of `35fd3d5`) patch the dev manifest with the old path and with the Id `b72d4e5f-6a89-4b01-cd23-ef45ab67cd89`, which is not the Id in `manifest.dev.xml` (`b92d4e5f-6a78-4901-bc23-de45fa67bc89`), and `manifest.dev.xml` still says Version `1.3.1.0` while `manifest.xml` says `1.3.2.0`. `/Gemail/dev/manifest.xml` returns 404 although the last `deploy` run (2026-03-05) succeeded; the cause is not established. On Windows, `npx office-addin-dev-certs verify` reports "You need to install certificates for trusted access to https://localhost" because the certificates were trusted inside WSL. `git config core.autocrlf` is `true` and 70 tracked text files check out CRLF; `.gitattributes` is new and untracked. There was no `.nvmrc` and no `engines` field; the pin (§4's first item) shipped early on 2026-09-27 in `2607bfb` because the type-check work needed it. `.vscode/tasks.json` carries Excel, PowerPoint, and Word debug tasks from the Office add-in template.
<!-- claim: count "rizonesoft.github.io/ai-email-writer/" webpack.config.js = 1 -->
<!-- claim: count "ai-email-writer" .github/workflows/deploy.yml = 2 -->
<!-- claim: count "b72d4e5f-6a89-4b01-cd23-ef45ab67cd89" .github/workflows/deploy.yml = 1 -->
<!-- claim: count "<Version>1.3.1.0</Version>" manifest.dev.xml = 1 -->
<!-- claim: exists .nvmrc -->
<!-- claim: exists tools/provision.ps1 -->
<!-- claim: count "Debug: Excel Desktop" .vscode/tasks.json = 1 -->

## Inputs

- [`webpack.config.js`](../../webpack.config.js) -- `urlDev`, `urlProd`, and the manifest rewrite §1 corrects
- [`.github/workflows/deploy.yml`](../../.github/workflows/deploy.yml) -- the dev patch and the two deploy jobs §1 corrects and reads back
- [`manifest.xml`](../../manifest.xml), [`manifest.dev.xml`](../../manifest.dev.xml) -- the Ids and versions §1 reconciles
- [`tools/provision.ps1`](../../tools/provision.ps1) -- the Windows provisioning legs §2 proves (node, deps, certs, hooks, python)
- [`.gitattributes`](../../.gitattributes), [`.editorconfig`](../../.editorconfig) -- the line-ending rules §3 applies
- [`package.json`](../../package.json) -- the `engines` field and dev dependencies §4 changes
- [`.vscode/`](../../.vscode/) -- the tasks and launch configurations §5 rewrites
- Microsoft Learn, "Sideload Outlook add-ins for testing" (https://learn.microsoft.com/office/dev/add-ins/outlook/sideload-outlook-add-ins-for-testing) -- the sideload paths §2 drives
- Microsoft Learn, "Debug add-ins using developer tools in Microsoft Edge (Chromium-based)" (https://learn.microsoft.com/office/dev/add-ins/testing/debug-add-ins-using-devtools-edge-chromium) -- the WebView2 attach §5 configures
- -> XREF: D00 T02 §1 -- the type check depends on the Node pin §4 writes
- -> XREF: D01 T01 §1 -- the rename starts from the Pages path §1 fixes; the legacy redirect in D01 T01 §7 covers users whose installed manifest still names the old path
- -> XREF: D07 T01 §1 -- the requirement-set pass starts from the manifests §1 reconciles
- -> XREF: D99 T01 §2 -- the operator dispatches the production deploy once §1 has shipped

## Outcome

- `curl -s -o /dev/null -w '%{http_code}'` returns `200` for `https://rizonesoft.github.io/Gemail/manifest.xml`, `/Gemail/taskpane.html`, `/Gemail/commands.html`, `/Gemail/dev/manifest.xml`, and `/Gemail/dev/taskpane.html`, and neither deployed manifest contains the string `ai-email-writer`.
- `pwsh tools/provision.ps1 -Verify` prints `ok` for every leg on the Windows clone, and `npm run dev-server` serves `https://localhost:3000/taskpane.html` to a sideloaded Outlook on the web without a certificate warning.
- `git ls-files --eol` shows no `i/crlf` entry, and the files `.gitattributes` pins to LF check out LF.
- `npm ci` refuses a Node below the pinned major, and the four unused dev dependencies are gone.
- `.vscode/` holds only Outlook tasks and an Edge WebView2 attach configuration for new Outlook.

**Adjacency:** all=not-applicable (repository plumbing: hosting URLs, certificates, line endings, the Node pin, and editor configuration, with no user records, settings, documents, or reversible user actions of its own)

## Implementation Order

| Order | Section | Deliverable                                               | Depends On | Status |
| :---: | :-----: | --------------------------------------------------------- | ---------- | :----: |
|   1   |   §1    | Point every URL at the Gemail Pages path and redeploy     | --         |  [ ]   |
|   2   |   §2    | Trust the dev certificates and provision a Windows clone  | --         |  [ ]   |
|   3   |   §3    | Normalize line endings after the move                     | --         |  [ ]   |
|   4   |   §4    | Pin Node and prune dev dependencies                       | §3         |  [ ]   |
|   5   |   §5    | VS Code workspace for Windows and new Outlook             | §2         |  [ ]   |

---

## 1. Point Every URL at the Gemail Pages Path and Redeploy

The operator's first priority (2026-09-27: "Plan it as D00 T01 §1"). Every installed copy of the add-in is broken because GitHub Pages does not redirect a renamed repository's site. This section fixes the URLs the build writes and the dev patch, deploys the dev build, and proves both paths serve; the production deploy is the operator's dispatch (`D99 T01 §2`), and users whose installed manifest still names `/ai-email-writer/` are covered by the redirect stub (`D01 T01 §7`). Names and display strings do not change here: that is the rename domain.

- [ ] Set `urlProd` in `webpack.config.js` to `https://rizonesoft.github.io/Gemail/`. Done when: `grep -c "rizonesoft.github.io/Gemail/" webpack.config.js` prints `1` and `npm run build` writes `dist/manifest.xml` in which `grep -c ai-email-writer dist/manifest.xml` prints `0`.
- [ ] In `.github/workflows/deploy.yml`, change the dev patch to rewrite `https://rizonesoft.github.io/Gemail/` to `https://rizonesoft.github.io/Gemail/dev/`, and change its Id substitution target from `b72d4e5f-6a89-4b01-cd23-ef45ab67cd89` to the Id in `manifest.dev.xml` (`b92d4e5f-6a78-4901-bc23-de45fa67bc89`), so a dev install and a sideload of `manifest.dev.xml` are the same add-in. Done when: `grep -c ai-email-writer .github/workflows/deploy.yml` prints `0` and the Id on line 64 equals the `<Id>` of `manifest.dev.xml`. Cheaper substitute: leaving the mismatched Id, which installs the dev build as a third add-in beside the other two.
- [ ] Set `<Version>` in `manifest.dev.xml` to the `manifest.xml` value (`1.3.2.0`), and confirm `scripts/sync-manifest-version.js` updates both files on the next `npm version`. Done when: both manifests carry the same `<Version>` and running `node scripts/sync-manifest-version.js` in a scratch copy changes both.
- [ ] Establish why `/Gemail/dev/manifest.xml` returns 404 after a successful `deploy-dev` run: list the `gh-pages` branch (`git ls-tree -r --name-only origin/gh-pages | grep '^dev/' | head`) and read the Pages settings (`gh api repos/rizonesoft/Gemail/pages`). Done when: the cause is written in the commit body (for example: the dev folder was never published, or the production deploy removed it) and fixed in `deploy.yml` if it is a workflow defect.
- [ ] Push `main` and read back the `deploy` run: `gh run list --workflow deploy.yml --limit 1 --json conclusion,headSha`. Done when: `conclusion` is `success` and `headSha` equals the pushed commit.
- [ ] Read back every dev URL: `curl -s -o /dev/null -w '%{http_code}\n'` for `https://rizonesoft.github.io/Gemail/dev/manifest.xml`, `/dev/taskpane.html`, `/dev/commands.html`, and `/dev/assets/icon-80.png`, and `curl -s https://rizonesoft.github.io/Gemail/dev/manifest.xml | grep -c ai-email-writer`. Done when: four `200` lines and a count of `0`.
- [ ] Commit: `"workspace: point every add-in URL at the Gemail Pages path"`

**Test checkpoint:** after the push, the four dev URLs above return `200` and the deployed dev manifest contains no `ai-email-writer`; `npm run build` locally writes a `dist/manifest.xml` with `0` occurrences of `ai-email-writer` and every `https://rizonesoft.github.io/Gemail/` URL it names exists under `dist/` (checked by a one-line loop over the URLs with `test -f`). The production URLs are proven by `D99 T01 §2` after the operator's dispatch. Cheaper substitute that fails: editing only `webpack.config.js`, which leaves the deployed dev manifest pointing at the dead path and fails the `grep -c` on it.

## 2. Trust the Dev Certificates and Provision a Windows Clone

The add-in is served from `https://localhost:3000` during development, and Outlook refuses a page whose certificate Windows does not trust. The certificates were trusted inside WSL, so on Windows nothing sideloads. `tools/provision.ps1` (written 2026-09-27 at the port) checks and repairs every leg a Windows clone needs; this section proves it on this machine and in the docs.

**Requires:** display-session -- the sideload in the last item drives Outlook on the web in a browser window, which a session without a window station cannot show (measured 2026-09-27: `office-addin-dev-certs verify` fails on this machine until the certificates are installed interactively)

- [ ] Run `pwsh tools/provision.ps1` and accept the one elevation prompt `office-addin-dev-certs install` raises. Done when: `pwsh tools/provision.ps1 -Verify` prints `ok` for `node`, `deps`, `certs`, `hooks`, and `python` and exits `0`.
- [ ] Check the repair path of each leg: in a scratch clone, delete `node_modules/.bin/webpack.cmd` and confirm `-Verify` reports `deps` FAIL naming the Windows shims, then repair. Done when: the FAIL line and the repaired `ok` line are quoted in the commit body.
- [ ] Add a "Windows setup" section to `CONTRIBUTING.md` naming `pwsh tools/provision.ps1`, what each leg does, and that the certificates must be re-trusted after moving a clone between WSL and Windows. Done when: `grep -c "tools/provision.ps1" CONTRIBUTING.md` prints at least `1`.
- [ ] Sideload the repository's `manifest.xml` (its URLs point at `https://localhost:3000/`) into Outlook on the web through https://aka.ms/olksideload while `npm run dev-server` runs, open a message, and open the task pane. Done when: the pane renders with no certificate error and the browser console shows no failed request to `localhost:3000`; the console count is quoted in the commit body.
- [ ] Commit: `"workspace: provision a Windows clone and trust the dev certificates"`

**Test checkpoint:** `pwsh tools/provision.ps1 -Verify` exits `0` with five `ok` lines; `npx office-addin-dev-certs verify` no longer prints "You need to install certificates"; the sideloaded task pane loads from `https://localhost:3000/taskpane.html` in Outlook on the web with zero failed requests in the console. Cheaper substitute that fails: running `office-addin-dev-certs install` by hand without the provisioning script, which leaves the next clone broken and fails the scratch-clone repair check.

## 3. Normalize Line Endings After the Move

The clone moved from WSL (LF) to Windows with `core.autocrlf=true`, so working-tree files check out CRLF, and the ported tooling expects LF for Python, PowerShell, hooks, Markdown, and JSON. `.gitattributes` (written 2026-09-27) pins those types to LF; the index still holds whatever each file was committed with. This section renormalizes once, in its own commit, so later diffs carry no line-ending noise.

- [ ] Stage `.gitattributes` and run `git add --renormalize .`. Done when: `git ls-files --eol | grep -c 'i/crlf'` prints `0`.
- [ ] Re-checkout the tree so the working copy follows the attributes: `git rm -r --cached -q . && git reset -q --hard` in a clean tree (after committing), or a fresh clone. Done when: `git ls-files --eol -- '*.py' '*.ps1' '*.md' '*.json' '*.yml' | grep -c 'w/crlf'` prints `0`.
- [ ] Confirm `.editorconfig` already says `end_of_line = lf` for `[*]` and leave it. Done when: `grep -n "end_of_line = lf" .editorconfig` prints one line.
- [ ] Commit: `"workspace: normalize line endings after the move from WSL"`

**Test checkpoint:** `git ls-files --eol | grep -c 'i/crlf'` prints `0`; `git diff HEAD~1 --stat --ignore-all-space` shows no content change beyond `.gitattributes` (the renormalization changes only line endings); `python scripts/todo-graph.py self-test` still reports `0 failed`. Cheaper substitute that fails: setting `core.autocrlf=false` on this machine only, which leaves the index mixed and fails the `i/crlf` count.

## 4. Pin Node and Prune Dev Dependencies

Nothing records which Node the project builds with, and the inventory of 2026-09-27 found four dev dependencies nothing references (`file-loader`, `source-map-loader`, `os-browserify`, `process`) and `ts-jest` at major 29 beside `jest` at major 30. This section pins Node and removes what is proven unused.

- [x] Add `"engines": { "node": ">=22 <25" }` to `package.json` and a `.nvmrc` containing `22`, and add `engine-strict=true` to a new `.npmrc`. Done when: `npm ci` under the installed Node exits `0`, and `node -e "process.exit(require('./package.json').engines ? 0 : 1)"` exits `0`. **Shipped:** `2607bfb` (operator request 2026-09-27, shipped ahead of the row; the row still stamps through `review-todo-section`): `engines.node` `>=22 <25`, `.nvmrc` `22`, `.npmrc` `engine-strict=true`; `npm ci` and `npm run build` exit 0 under Node 24.14.1.
- [ ] For each of `file-loader`, `source-map-loader`, `os-browserify`, and `process`, prove it unused with `grep -rn "<name>" webpack.config.js babel.config.json jest.config.js src scripts` returning nothing, then `npm uninstall <name>`. Done when: the four are gone from `package.json` and `npm run build` still exits `0`.
- [ ] Align `ts-jest` with `jest` 30 (`npm install -D ts-jest@^30` if a 30 release exists on npm; otherwise record the peer range `npm view ts-jest peerDependencies` prints and keep 29). Done when: `npx jest --ci` passes the 35 existing tests and `npm ls ts-jest` shows no peer warning, or the commit body quotes the peer range that justifies keeping 29.
- [ ] Commit: `"workspace: pin Node and drop unused dev dependencies"`

**Test checkpoint:** `npm ci && npm run build && npx jest --ci` exits `0` with 35 tests passing; `npm ls file-loader source-map-loader os-browserify process` prints `(empty)`; with `engine-strict=true`, `npm ci` under a Node 18 binary (for example `npx -p node@18 npm ci --dry-run`) exits non-zero naming the `engines` range. Cheaper substitute that fails: a README line naming the Node version, which the Node 18 probe does not trip.

## 5. VS Code Workspace for Windows and New Outlook

The `.vscode/` folder came from the Office add-in template and targets classic desktop hosts Gemail does not support (Excel, PowerPoint, Word, and classic Outlook). New Outlook runs the add-in in Edge WebView2, which VS Code attaches to over the Edge debug protocol.

- [ ] Remove the Excel, PowerPoint, and Word tasks from `.vscode/tasks.json` and rename the Outlook task to "Debug: new Outlook". Done when: `grep -c -i "excel\|powerpoint\|word desktop" .vscode/tasks.json` prints `0`.
- [ ] Replace the two classic Outlook attach configurations in `.vscode/launch.json` with one "Attach to new Outlook (WebView2)" configuration (`"type": "msedge"`, `"request": "attach"`, `"port": 9229`) and document in `CONTRIBUTING.md` that new Outlook must be started with `WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS=--remote-debugging-port=9229`. Done when: the configuration attaches and a breakpoint in `src/taskpane/taskpane.ts` inside `Office.onReady` is hit on pane open, recorded in the commit body.
- [ ] Commit: `"workspace: VS Code tasks and WebView2 attach for new Outlook"`

**Test checkpoint:** `grep -c -i "excel\|powerpoint\|word desktop" .vscode/tasks.json` prints `0`; `node -e "JSON.parse(require('fs').readFileSync('.vscode/launch.json','utf8').replace(/\/\/.*$/gm,''))"` exits `0`; the attach run above hits the `Office.onReady` breakpoint in new Outlook. Cheaper substitute that fails: deleting `.vscode/` entirely, which loses the debug path and fails the breakpoint check.

## Verification

- [ ] `pwsh scripts/check-all.ps1` -- the build, test, and TODO gates pass; the typecheck and lint gates are quoted as known-red until `D00 T02 §3` ships, with counts no higher than on 2026-09-27
- [ ] The five URLs in the Outcome return `200`, and neither deployed manifest names `ai-email-writer`
- [ ] `pwsh tools/provision.ps1 -Verify` exits `0` on the Windows clone
