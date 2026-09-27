---
schema_version: 1
id: green-gates
domain: 00-workspace
status: draft
title: "TODO-02 -- Green Gates on the Imported Tree"
depends_on: []
---

# TODO-02 -- Green Gates on the Imported Tree

> **Goal:** Every gate `scripts/check-all.ps1` runs is green on the imported 1.3.2 tree and stays green on every push: `tsc --noEmit` exits 0, `npm run lint` reports zero problems, TypeScript runs in `strict` mode, and a CI workflow named `build` runs the build, type check, lint, tests, and manifest validation on every push and pull request, with the deploy gated on it.

> [!IMPORTANT]
> **Current state (verified 2026-09-27):** `npx tsc --noEmit` exits 2 with 9 errors, all inside `node_modules` (TS18028 "Private identifiers are only available when targeting ECMAScript 2015 and higher" in `google-auth-library` and `gtoken`, pulled in by `@google/genai`), because `tsconfig.json` sets `"target": "es5"` with `"lib": ["es2015", "dom"]`; it also carries `"jsx": "react"` and `"experimentalDecorators": true` that nothing uses, and no `strict`. There is no `typecheck` script: webpack compiles `.ts` through `babel-loader` only, so nothing type-checks the build. `npm run lint` (`office-addin-lint check`) reports 1204 problems, all errors, 971 of them auto-fixable: 971 `prettier/prettier`, 224 `no-undef` (Jest and browser globals such as `expect`, `it`, `document`, `HTMLSelectElement`, `localStorage`), 6 `@typescript-eslint/no-unused-vars`, and 3 `no-useless-escape`. `office-addin-lint` lints with its bundled `node_modules/office-addin-lint/config/eslint.config.mjs` unless the project root has an `eslint.config.mjs`, so the repository's `.eslintrc.json` is read by nothing (ESLint 9 ignores it). `npx jest --ci` passes 35 tests in 2 suites. `.github/workflows/deploy.yml` builds and deploys on every push to `main` with no test, type check, or lint step, and there is no other workflow that builds the product.
<!-- claim: count "target.: .es5" tsconfig.json = 1 -->
<!-- claim: count "experimentalDecorators" tsconfig.json = 1 -->
<!-- claim: count "strict" tsconfig.json = 0 -->
<!-- claim: count "\"typecheck\"" package.json = 0 -->
<!-- claim: absent eslint.config.mjs -->
<!-- claim: exists .eslintrc.json -->
<!-- claim: absent .github/workflows/build.yml -->

## Inputs

- [`tsconfig.json`](../../tsconfig.json) -- the compiler options §1 and §5 change
- [`package.json`](../../package.json) -- the `lint`, `lint:fix`, and new `typecheck` scripts
- [`.eslintrc.json`](../../.eslintrc.json) -- the dead ESLint 8 config §3 replaces
- `node_modules/office-addin-lint/lib/lint.js` line 33 -- reads `eslint.config.mjs` from the project root when it exists, else its bundled config
- [`.github/workflows/deploy.yml`](../../.github/workflows/deploy.yml) -- the deploy §4 gates on the new build workflow
- [`scripts/check-all.ps1`](../../scripts/check-all.ps1) -- the local sweep whose gates this file turns green
- [`.claude/skills/process-todo-section/gates.md`](../../.claude/skills/process-todo-section/gates.md) -- names the typecheck and lint gates as known-red until §3 ships
- TypeScript handbook, "TSConfig Reference" (https://www.typescriptlang.org/tsconfig) -- `target`, `lib`, `module`, `moduleResolution`, `strict`
- ESLint, "Configuration Files" (https://eslint.org/docs/latest/use/configure/configuration-files) -- the flat config §3 writes
- -> XREF: D00 T01 §4 -- the Node pin §1 builds on; §2 runs after the line-ending renormalization of D00 T01 §3
- -> XREF: D00 T03 §4 -- reads back the `build` workflow §4 creates
- -> XREF: D03 T01 §1 -- the task pane split starts from the lint-clean tree §3 leaves
- -> XREF: D03 T02 §1 -- the bundle budget runs as a step of the workflow §4 creates
- -> XREF: D04 T01 §8 -- the dependency audit step joins the workflow §4 creates
- -> XREF: D05 T01 §1 -- the Jest configuration builds on the compiler options §1 sets; D05 T01 §6 adds coverage to the workflow §4 creates
- -> XREF: D07 T01 §2 -- manifest validation of both manifests extends the workflow §4 creates

## Outcome

- `npx tsc --noEmit` exits 0, and `npm run typecheck` runs it.
- `npm run lint` exits 0 with zero problems, driven by a project `eslint.config.mjs`, and `.eslintrc.json` is gone.
- `tsconfig.json` sets `"strict": true` and the tree type-checks under it.
- `.github/workflows/build.yml` (workflow name `build`) runs `npm ci`, `npm run build`, `npm run typecheck`, `npm run lint`, `npx jest --ci`, and `npm run validate` on every push and pull request to `main`, and the deploy jobs in `deploy.yml` run only after it succeeds.
- `pwsh scripts/check-all.ps1 -SkipManifest` reports every gate `PASS`.

**Adjacency:** all=not-applicable (compiler, linter, and CI configuration with no user-facing records, settings, documents, or reversible user actions)

## Implementation Order

| Order | Section | Deliverable                | Depends On | Status |
| :---: | :-----: | -------------------------- | ---------- | :----: |
|   1   |   §1    | Type check clean           | D00 T01 §4 |  [ ]   |
|   2   |   §2    | Prettier pass over the tree | D00 T01 §3 |  [ ]   |
|   3   |   §3    | Lint errors to zero        | §2         |  [ ]   |
|   4   |   §4    | CI build workflow          | §1, §3     |  [ ]   |
|   5   |   §5    | Strict TypeScript          | §4         |  [ ]   |

---

## 1. Type Check Clean

Nothing type-checks the product today: webpack strips types through Babel, and `tsc --noEmit` fails before it reaches `src/` because `target: es5` cannot read the private identifiers in `@google/genai`'s dependencies. The code already uses ES2017 APIs (`Object.entries` in `src/features/settings.ts` and `src/taskpane/taskpane.ts`), so the `lib` is wrong as well as the target. Babel still owns the emitted JavaScript through `.browserslistrc`; `tsconfig.json` only has to describe the code truthfully.

- [ ] In `tsconfig.json`, set `"target": "ES2020"`, `"lib": ["ES2020", "DOM", "DOM.Iterable"]`, `"module": "ESNext"`, `"moduleResolution": "bundler"`, and `"noEmit": true`, and remove `"jsx"`, `"experimentalDecorators"`, `"outDir"`, and `"sourceMap"`. Done when: `node -e "JSON.parse(require('fs').readFileSync('tsconfig.json','utf8'))"` exits 0 and none of the removed keys remain.
- [ ] Add `"types": ["office-js", "jest", "node"]` to `compilerOptions` so the Office, Jest, and Node globals resolve without `/// <reference>` lines. Done when: `npx tsc --noEmit` reports no `Cannot find name 'Office'` or `Cannot find name 'expect'` error.
- [ ] Fix every remaining `tsc --noEmit` error inside `src/` and `scripts/` at its source, without `// @ts-ignore` or `any` casts added to silence one. Done when: `npx tsc --noEmit` exits 0; the per-file error count before the fix is quoted in the commit body.
- [ ] Add `"typecheck": "tsc --noEmit"` to the `scripts` of `package.json`. Done when: `npm run typecheck` exits 0.
- [ ] Confirm the emitted bundle is unchanged in behavior: `npm run build` exits 0 and `npx jest --ci` still passes 35 tests. Done when: both are quoted in the commit body.
- [ ] Commit: `"workspace: type-check the tree with an honest tsconfig"`

**Test checkpoint:** `npm run typecheck` exits 0; `npm run build` exits 0; `npx jest --ci` passes 35 tests in 2 suites; introducing `const n: number = "x";` into `src/prompts/builder.ts` in a scratch copy makes `npm run typecheck` exit non-zero naming that line. Cheaper substitute that fails: adding `"skipLibCheck": true` alone, which hides the `node_modules` errors but leaves `lib: es2015` rejecting `Object.entries` and leaves no `typecheck` script for CI to run.

## 2. Prettier Pass Over the Tree

971 of the 1204 lint problems are `prettier/prettier` formatting, all auto-fixable. Landing them as one mechanical commit, separate from any hand edit, keeps later diffs readable and lets `git blame --ignore-rev` skip it. It runs after the line-ending renormalization so Prettier and Git agree on LF.

- [ ] Run `npm run lint:fix` and confirm the only rules it changed are formatting: `npm run lint` afterwards reports zero `prettier/prettier` problems. Done when: the before and after problem totals are quoted in the commit body (1204 before; 233 or fewer after).
- [ ] Check the diff is formatting only: `git diff --ignore-all-space --stat` lists no file whose non-whitespace content changed beyond quote style, trailing commas, and wrapping, spot-checked on `src/taskpane/taskpane.ts` and `src/services/gemini.ts`. Done when: `npx jest --ci` still passes 35 tests and `npm run build` exits 0.
- [ ] Create `.git-blame-ignore-revs` listing this commit's hash with a one-line comment, in a follow-up commit (the hash exists only after this one lands). Done when: `git blame --ignore-revs-file .git-blame-ignore-revs src/taskpane/taskpane.ts | head -1` names a commit other than the formatting commit.
- [ ] Commit: `"workspace: apply Prettier across the tree (mechanical)"`

**Test checkpoint:** `npm run lint 2>&1 | grep -c prettier/prettier` prints `0`; `npx jest --ci` passes 35 tests; `npm run build` exits 0; `.git-blame-ignore-revs` names the formatting commit. Cheaper substitute that fails: disabling the `prettier/prettier` rule in the lint config, which drops the count to zero without formatting anything and leaves `npx prettier --check src` failing.

## 3. Lint Errors to Zero

After the Prettier pass, the remaining problems measured on 2026-09-27 are 224 `no-undef`, 6 `@typescript-eslint/no-unused-vars`, and 3 `no-useless-escape`. The `no-undef` hits are false positives: the bundled `office-addin-lint` config does not declare browser or Jest globals, and typescript-eslint recommends turning `no-undef` off for TypeScript because the compiler already checks undefined names. The repository's `.eslintrc.json` has been dead since ESLint 9; `office-addin-lint` reads a project `eslint.config.mjs` when one exists (`node_modules/office-addin-lint/lib/lint.js` line 33).

- [ ] Create `eslint.config.mjs` at the repository root that imports the `office-addins` plugin's recommended flat config and typescript-eslint's recommended config, declares `globals.browser` for `src/**/*.ts`, `globals.jest` for `src/**/*.test.ts`, and `globals.node` for `scripts/**` and the root config files, and sets `no-undef` off for `**/*.ts`. Source: https://typescript-eslint.io/troubleshooting/faqs/eslint#i-get-errors-from-the-no-undef-rule-about-global-variables-not-being-defined-even-though-there-are-no-typescript-errors. Done when: `npm run lint 2>&1 | grep -c no-undef` prints `0`.
- [ ] Delete `.eslintrc.json`, carrying its two deliberate rules into `eslint.config.mjs`: `@typescript-eslint/no-unused-vars` with `argsIgnorePattern: "^_"` and `@typescript-eslint/no-explicit-any` at `warn`. Done when: `test ! -f .eslintrc.json` and both rules appear in `eslint.config.mjs`.
- [ ] Fix the 6 `@typescript-eslint/no-unused-vars` problems by removing the unused binding (or prefixing an intentionally unused argument with `_`). Done when: `npm run lint 2>&1 | grep -c no-unused-vars` prints `0`.
- [ ] Fix the 3 `no-useless-escape` problems by removing the needless backslash without changing what the regular expression matches, each covered by an existing test or a one-line assertion added beside it. Done when: `npm run lint 2>&1 | grep -c no-useless-escape` prints `0` and `npx jest --ci` passes.
- [ ] Commit: `"workspace: a flat ESLint config and zero lint problems"`

**Test checkpoint:** `npm run lint` exits 0 reporting 0 problems; `npm run typecheck` exits 0; `npx jest --ci` passes; adding `const unused = 1;` to `src/prompts/builder.ts` in a scratch copy makes `npm run lint` report exactly one `@typescript-eslint/no-unused-vars` problem, proving the project config is the one being read. Cheaper substitute that fails: `/* eslint-disable */` at the top of each file, which zeroes the count but lets the scratch-copy probe pass silently.

## 4. CI Build Workflow

The only workflow that builds the product is `deploy.yml`, and it deploys without running a single check, so a red tree reaches `/Gemail/dev/` on every push. `process-todo-section` reads CI back after each SHIP push with `python scripts/review_prompt.py ci-wait <sha> --workflow build --workflow-path .github/workflows/build.yml`, which needs a workflow named `build`.

- [ ] Create `.github/workflows/build.yml` with `name: build`, triggered on `push` and `pull_request` to `main` and on `workflow_dispatch`, one `ubuntu-latest` job that runs `actions/checkout`, `actions/setup-node` with `node-version-file: .nvmrc` and `cache: npm`, then `npm ci`, `npm run build`, `npm run typecheck`, `npm run lint`, `npx jest --ci`, and `npm run validate`. Done when: `python -c "import sys,re; t=open('.github/workflows/build.yml').read(); sys.exit(0 if re.search(r'^name: build$', t, re.M) else 1)"` exits 0 and every command above appears in it.
- [ ] Make `npm run validate` in CI tolerate the online validator being unreachable only by failing loudly: no `continue-on-error`. Done when: `grep -c continue-on-error .github/workflows/build.yml` prints `0`.
- [ ] Gate deploys on the build: change `deploy.yml` to trigger on `workflow_run` of `build` completing on `main` with `conclusion == 'success'` (keeping `workflow_dispatch` for the production deploy), and remove its own `push` trigger. Source: https://docs.github.com/actions/using-workflows/events-that-trigger-workflows#workflow_run. Done when: `grep -n "workflow_run" .github/workflows/deploy.yml` prints the trigger and `grep -c "^  push:" .github/workflows/deploy.yml` prints `0`.
- [ ] Add `.github/workflows/build.yml` to the `paths` lists of `.github/workflows/plan.yml` only if `plan.yml` must re-run on it; otherwise leave `plan.yml` untouched and say so in the commit body. Done when: the decision is recorded.
- [ ] Push and read back: `python scripts/review_prompt.py ci-wait <SHIP_SHA> --workflow build --workflow-path .github/workflows/build.yml`. Done when: it reports the `build` run green for the pushed sha, and `gh run list --workflow deploy.yml --limit 1 --json event,conclusion` shows a `workflow_run` event.
- [ ] Commit: `"workspace: a CI build workflow that gates the deploy"`

**Test checkpoint:** the `build` run for the SHIP commit concludes `success` with all six steps executed (`gh run view <id> --json jobs --jq '.jobs[0].steps[].name'`); the following `deploy` run's event is `workflow_run`; a scratch branch pushed with a deliberate lint error (`const unused = 1;` in `src/prompts/builder.ts`) opens a pull request whose `build` check fails at the lint step and triggers no deploy. Cheaper substitute that fails: adding `npm test` to `deploy.yml`, which still deploys when lint or the type check is red and gives `ci-wait` no `build` workflow to read.

## 5. Strict TypeScript

With the type check running in CI, `strict` can be turned on without the next edit silently undoing it. Strict null checks matter here because Office.js returns `null` or `undefined` for fields the item does not have in the current mode (a read item has no `body.setAsync`, a compose item has no string `subject`).

- [ ] Set `"strict": true` in `tsconfig.json` and record the error count per file from `npx tsc --noEmit` in the commit body. Done when: the count table is in the commit body.
- [ ] Fix the strict errors in `src/services/` and `src/prompts/` with real guards (narrowing, explicit return types, `unknown` in `catch` handled), not non-null assertions. Done when: `npx tsc --noEmit 2>&1 | grep -c "src/services\|src/prompts"` prints `0`.
- [ ] Fix the strict errors in `src/features/` and `src/commands/`. Done when: `npx tsc --noEmit 2>&1 | grep -c "src/features\|src/commands"` prints `0`.
- [ ] Fix the strict errors in `src/taskpane/taskpane.ts`, typing every `document.getElementById` lookup through one helper that throws a named error when the element is missing. Done when: `npx tsc --noEmit` exits 0.
- [ ] Count non-null assertions added by this section: `git diff <base>..HEAD -- src | grep -c '^+.*[a-zA-Z)]!\.'`. Done when: the count is quoted in the commit body and each one carries a comment naming why the value cannot be null.
- [ ] Commit: `"workspace: strict TypeScript across the tree"`

**Test checkpoint:** `npm run typecheck` exits 0 with `"strict": true` in `tsconfig.json`; `npx jest --ci` passes; `npm run build` exits 0; the `build` workflow is green on the pushed commit; in a scratch copy, `let s: string = null;` in `src/prompts/builder.ts` makes `npm run typecheck` fail. Cheaper substitute that fails: `"strict": true` with `"strictNullChecks": false`, which the scratch-copy null probe does not trip.

## Verification

- [ ] `pwsh scripts/check-all.ps1` -- exits 0 with every gate `PASS`, including the typecheck and lint gates
- [ ] The `build` workflow is green on `main` and the latest `deploy` run was triggered by it
- [ ] `npx jest --ci` passes with the same test count as before this file started, or more
