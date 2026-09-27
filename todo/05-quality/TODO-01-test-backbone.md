---
schema_version: 1
id: test-backbone
domain: 05-quality
status: draft
title: "TODO-01 -- Test Backbone"
depends_on: []
---

# TODO-01 -- Test Backbone

> **Goal:** Every module that decides something has a Jest test that can fail: services run in Node, DOM code runs in jsdom, Office.js is replaced by one shared mock that models read and compose mode, the settings service is pinned by characterization tests before the rename and the cutover change it, every feature module and every ribbon command is tested against a mocked AI facade, retry tests run on fake timers instead of real seconds, and CI refuses a coverage drop below the measured floor.

> [!IMPORTANT]
> **Current state (verified 2026-09-27):** `jest.config.js` uses the `ts-jest` preset with `testEnvironment: 'node'`, roots `<rootDir>/src`, and no coverage settings. Two test files exist: `src/prompts/builder.test.ts` and `src/services/gemini.test.ts`, 35 tests in all; `npx jest` takes about 26 seconds because the retry tests in `gemini.test.ts` wait on real timers (per-test timeouts of 15, 30, and 60 seconds). There is no Office.js mock and no test for `src/services/outlook.ts`, `src/features/settings.ts`, any feature module, `src/taskpane/taskpane.ts`, or `src/commands/commands.ts`. `jest` is at major 30 and `ts-jest` at major 29 (`D00 T01 §4` aligns them). `src/features/settings.ts` imports `initGeminiClient` from `src/services/gemini.ts`, and `gemini.ts` imports `getSetting` back, so testing settings in isolation needs the client mocked.
<!-- claim: count "testEnvironment: 'node'" jest.config.js = 1 -->
<!-- claim: count "coverageThreshold" jest.config.js = 0 -->
<!-- claim: absent src/test/office-mock.ts -->
<!-- claim: absent src/services/outlook.test.ts -->
<!-- claim: absent src/features/settings.test.ts -->
<!-- claim: absent src/commands/commands.test.ts -->

## Inputs

- [`jest.config.js`](../../jest.config.js), [`package.json`](../../package.json) -- the configuration and scripts §1 extends
- [`src/services/outlook.ts`](../../src/services/outlook.ts) -- the Office.js wrapper §2 tests
- [`src/features/settings.ts`](../../src/features/settings.ts) -- the settings service §3 characterizes
- [`src/features/`](../../src/features/) and [`src/commands/commands.ts`](../../src/commands/commands.ts) -- the modules §4 and §5 test
- Jest documentation, "Configuring Jest" (`projects`, `testEnvironment`, `coverageThreshold`; https://jestjs.io/docs/configuration) and "Timer Mocks" (https://jestjs.io/docs/timer-mocks) -- the settings §1 and §6 use
- Microsoft Learn, Outlook JavaScript API reference (`Office.MessageRead`, `Office.MessageCompose`, `Office.AsyncResult`; https://learn.microsoft.com/javascript/api/outlook) -- the shapes the §2 mock reproduces
- -> XREF: D00 T02 §1 -- the clean type check §1 builds on; §4 of that file is the CI workflow §6 adds the coverage step to
- -> XREF: D02 T02 §2 -- the repointed callers and the facade §4 and §5 mock
- -> XREF: D06 T03 §1 -- attachment reading, which extends the §2 mock with attachments; smart CC in D06 T03 §4 uses its recipients
- -> XREF: D07 T01 §6 -- the release, which ships only with the §6 ratchet green

## Outcome

- `npx jest` runs a `services` project in Node and a `ui` project in jsdom, and the whole suite finishes in under 10 seconds because no test waits on a real timer.
- `src/test/office-mock.ts` builds a read-mode or compose-mode `Office.context.mailbox.item` in one call, and `src/services/outlook.ts` is tested in both modes including every failure callback.
- The settings service has tests for its defaults, a malformed stored value, and each storage migration, written before the rename changes the keys.
- Every feature module and every ribbon command is tested against a mocked facade, asserting the prompt it builds, the options it passes, and how it parses and reports results.
- CI runs `npm run test:coverage`, and a change that lowers line coverage below the recorded floor fails the build.

**Adjacency:** all=not-applicable (test infrastructure: no user records, settings, documents, or reversible user actions of its own; the behaviors it pins belong to the modules under test)

## Implementation Order

| Order | Section | Deliverable                               | Depends On          | Status |
| :---: | :-----: | ----------------------------------------- | ------------------- | :----: |
|   1   |   §1    | Jest configuration for UI and services    | D00 T02 §1          |  [ ]   |
|   2   |   §2    | An Office.js mock and outlook.ts tests    | §1                  |  [ ]   |
|   3   |   §3    | Settings tests                            | §1                  |  [ ]   |
|   4   |   §4    | Feature module tests                      | §2, D02 T02 §2      |  [ ]   |
|   5   |   §5    | Ribbon command tests                      | §2, D02 T02 §2      |  [ ]   |
|   6   |   §6    | Coverage ratchet in CI                    | §4, §5, D00 T02 §4  |  [ ]   |

---

## 1. Jest Configuration for UI and Services

The suite runs everything in Node, so nothing that touches `document` can be tested, and the retry tests spend real seconds waiting. This section splits the suite into two Jest projects, adds coverage, and moves the slow tests to fake timers. Decision recorded here: `jest-environment-jsdom` is added as a dev dependency because Jest 28 and later no longer bundle jsdom, and the task pane is DOM code that the accessibility, security, and architecture sections all test.

- [ ] Add `jest-environment-jsdom` at the major matching `jest` (`npm install -D jest-environment-jsdom@^30`). Done when: `npm ls jest-environment-jsdom` prints a 30.x version with no peer warning.
- [ ] Rewrite `jest.config.js` with two `projects`: `services` (`testEnvironment: 'node'`, `testMatch` for `src/services/**`, `src/prompts/**`, `src/features/**`, `src/commands/**`) and `ui` (`testEnvironment: 'jsdom'`, `testMatch` for `src/ui/**` and `src/taskpane/**`), sharing the existing `ts-jest` transform. Done when: `npx jest --listTests` lists both existing test files and a scratch `src/taskpane/probe.test.ts` that reads `document.body` passes under `ui`.
- [ ] Add `collectCoverageFrom: ['src/**/*.ts', '!src/**/*.test.ts', '!src/test/**', '!src/types/**']` and an npm script `"test:coverage": "jest --ci --coverage"`. Done when: `npm run test:coverage` prints a coverage table and writes `coverage/lcov.info` (already gitignored).
- [ ] Convert the retry and backoff tests in `src/services/gemini.test.ts` to `jest.useFakeTimers()` with `jest.advanceTimersByTimeAsync`, and delete their long per-test timeouts. Done when: `npx jest src/services/gemini.test.ts` finishes in under 3 seconds with the same test count.
- [ ] Commit: `"test: jsdom and node projects, coverage, and fake timers"`

**Test checkpoint:** `npx jest --ci` passes all 35 existing tests plus the probe in under 10 seconds wall time (quote the `Time:` line); `npm run test:coverage` writes `coverage/lcov.info`; deleting `testEnvironment: 'jsdom'` from the `ui` project makes the probe fail with `document is not defined`. Cheaper substitute that fails: switching the whole suite to jsdom, which passes the probe but still takes 26 seconds and fails the time bound.

## 2. An Office.js Mock and outlook.ts Tests

`src/services/outlook.ts` decides the item mode and reads every piece of mail the features use, and it has no test. Every later section that touches mail (the Accept Changes fix in D05 T03 §1, attachments, smart CC, write callbacks) needs the same fake mailbox, so the mock is one shared module.

- [ ] Add `src/test/office-mock.ts` exporting `installOffice({ mode: 'read' | 'compose', body?, subject?, from?, to?, cc?, selection?, fail?: string[] })` that sets `globalThis.Office` with `context.mailbox.item`, `CoercionType`, `AsyncResultStatus`, and callback-style `getAsync`, `setAsync`, `prependAsync`, `getSelectedDataAsync`, and `setSelectedDataAsync` whose failure is chosen by name through `fail`; and `uninstallOffice()`. Done when: a self-test in `src/test/office-mock.test.ts` asserts a compose item's `body.getAsync` calls back with the given body and a name listed in `fail` calls back with `Failed`.
- [ ] Record every write the mock receives (`calls: { method, args }[]`) so tests can assert what would have been written into a message. Done when: the self-test asserts a `setSelectedDataAsync` call is recorded with its text and coercion type.
- [ ] Add `src/services/outlook.test.ts` covering `getItemMode` in both modes, `getCurrentEmailBody`, `getCurrentEmailSubject` (string in read mode, `getAsync` in compose), `getEmailSender` including its `userProfile` fallback, `getOriginalSender`, and the rejection path of each on a failed callback. Done when: the file passes with at least one success and one failure case per exported function it covers.
- [ ] Commit: `"test: a shared Office.js mock and outlook.ts tests"`

**Test checkpoint:** `npx jest src/test src/services/outlook.test.ts` passes; changing `getItemMode` to always return `'read'` fails the compose-mode cases; forcing `fail: ['body.getAsync']` makes `getCurrentEmailBody` reject in the test. Cheaper substitute that fails: a per-test inline `Office` stub, which the later mail sections would each rewrite; the checkpoint's requirement of a shared module with a self-test is what fails it.

## 3. Settings Tests

The rename (`D01 T01 §5`) moves the storage keys and the cutover (`D02 T02 §3`) migrates the key and the model ids. Both are changes to user data, so the current behavior is pinned first, and those sections change the tests deliberately.

- [ ] Add `src/features/settings.test.ts`, mocking `../services/gemini` so the circular import does not initialise a client, and resetting `localStorage` and the module cache (`jest.resetModules()`) between tests. Done when: the file runs in the `services` project with jsdom's `localStorage` available through `@jest-environment jsdom` in its docblock, or with a minimal in-memory `localStorage` shim in `src/test/`.
- [ ] Test `loadSettings` defaults on empty storage, a malformed JSON value (falls back to defaults without throwing), a partial stored object (merged over defaults), and the one-time `glide_settings` migration (moved, then the legacy key removed). Done when: four named tests pass.
- [ ] Test `saveSettings` round trip, `getSetting`, `resetSettings`, `buildRulesText` with presets and custom rules, and the templates functions `getTemplates`, `saveTemplate`, `deleteTemplate` including a malformed templates value. Done when: each function has at least one named test.
- [ ] Commit: `"test: characterize the settings service before the rename"`

**Test checkpoint:** `npx jest src/features/settings.test.ts` passes; editing `loadSettings` to drop the `glide_settings` migration fails the migration test, and making `JSON.parse` errors propagate fails the malformed-value test. Cheaper substitute that fails: testing only the default path, which leaves the migration edit undetected.

## 4. Feature Module Tests

The six feature modules decide what the model is asked and how its answer is read, and none is tested. After `D02 T02 §2` every feature calls the provider-neutral facade (`src/services/ai.ts`), which is the one seam to mock.

- [ ] Add a test file beside each of `draft-email.ts`, `draft-reply.ts`, `summarize-thread.ts`, `improve-writing.ts`, `extract-actions.ts`, and `translate.ts`, mocking `src/services/ai.ts` and using `src/test/office-mock.ts` for mail. Done when: six `*.test.ts` files exist under `src/features/` and pass.
- [ ] In each, assert the prompt the feature builds carries the user's inputs (instructions, tone, language, focus, style) and the email content, and assert the options it passes (model choice, temperature, token budget) match the module's constants. Done when: each file has a prompt test and an options test.
- [ ] Test the parsers directly: `parseSubjectAndBody` in `draft-email.ts` (with and without a `Subject:` line) and `parseActionItems` in `extract-actions.ts` (a well-formed list, an empty answer, and free text). Done when: at least three cases per parser pass.
- [ ] Test that a facade rejection propagates as a rejection with its message, and that the module's "last result" state is not overwritten by a failed call. Done when: each feature file has one failure test.
- [ ] Commit: `"test: every feature module against a mocked facade"`

**Test checkpoint:** `npx jest src/features` passes; changing the temperature constant in `improve-writing.ts` fails its options test, and making `parseActionItems` return `[]` for a well-formed list fails its parser test. Cheaper substitute that fails: snapshot tests of whole prompts, which pass after any change once re-recorded and name no behavior.

## 5. Ribbon Command Tests

`src/commands/commands.ts` runs in its own runtime and the inventory of 2026-09-27 found it never initialised the client, so every ribbon command failed without any test noticing. This section tests each registered command end to end against the mock and the mocked facade.

- [ ] Add `src/commands/commands.test.ts` that installs the compose mock, stubs `Office.actions.associate` to capture registrations, imports the module, and triggers `Office.onReady`. Done when: the test asserts exactly `fixGrammar`, `improveClarity`, `makeConcise`, and `makeProfessional` are registered.
- [ ] For each command, test the happy path: the selection is read, the facade is called with that text and the command's focus, the result is written back through `setSelectedDataAsync`, and `event.completed()` is called once. Done when: four tests pass and each asserts the recorded write.
- [ ] Test the refusal paths: an empty selection, a facade rejection, and a failed `setSelectedDataAsync`, each showing a notification through `notificationMessages.replaceAsync` and still calling `event.completed()`. Done when: three tests pass.
- [ ] Assert every notification message is at most 150 characters, truncating long error messages. Source: Microsoft Learn, `Office.NotificationMessageDetails.message` ("maximum length is 150 characters"; https://learn.microsoft.com/javascript/api/outlook/office.notificationmessagedetails). Done when: a test with a 400-character error message asserts the notification text length is 150 or less.
- [ ] Commit: `"test: ribbon commands, refusals, and notification length"`

**Test checkpoint:** `npx jest src/commands` passes; removing the `event.completed()` call from the failure path fails the refusal tests, and removing the truncation fails the length test. Cheaper substitute that fails: testing the handlers' helpers in isolation, which never catches a handler that forgets `event.completed()`.

## 6. Coverage Ratchet in CI

Coverage is a ratchet, not a target: it is set to what the suite measures once §2 to §5 have landed, and it may rise but never fall.

- [ ] Run `npm run test:coverage` and read the global line, branch, function, and statement percentages. Done when: the four numbers are quoted in the commit body.
- [ ] Set `coverageThreshold.global` in `jest.config.js` to each measured value rounded down to the whole percent, with a comment dated the day of measurement saying it is a ratchet. Done when: `npm run test:coverage` exits `0` at the threshold.
- [ ] Replace the test step of `.github/workflows/build.yml` (from `D00 T02 §4`) with `npm run test:coverage`. Done when: the next `build` run on `main` shows the coverage table in its log, read back with `gh run view --log`.
- [ ] Commit: `"test: coverage ratchet at the measured floor, enforced in CI"`

**Test checkpoint:** `npm run test:coverage` exits `0`; deleting `src/services/outlook.test.ts` in a scratch copy makes it exit non-zero naming the global threshold; the `build` run for the commit is `success` with the coverage step executed. Cheaper substitute that fails: a coverage report with no threshold, which the scratch deletion does not fail.

## Verification

- [ ] `pwsh scripts/check-all.ps1` -- exits 0: production build, typecheck, lint, tests, manifest, TODO gates green
- [ ] `npx jest --ci` exits 0 with both projects reporting and a `Time:` under 10 seconds
- [ ] `npm run test:coverage` exits 0 at the recorded thresholds, and the latest `build` run on `main` ran the same command
