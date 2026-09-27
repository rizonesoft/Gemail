---
schema_version: 1
id: taskpane-split
domain: 03-architecture
status: draft
title: "TODO-01 -- Task Pane Split"
depends_on: []
---

# TODO-01 -- Task Pane Split

> **Goal:** `src/taskpane/taskpane.ts` stops being a 1570-line monolith: shared UI behavior (showing and hiding, loading, the error banner, copy to clipboard, HTML escaping) lives once in `src/ui/`, tab switching lives in `src/taskpane/tabs.ts`, each feature's wiring lives in its own module under `src/taskpane/panels/`, and `taskpane.ts` is a bootstrap under 200 lines. Helpers the feature modules duplicate exist once, and dead code is gone. Nothing a user sees changes: every section here is a behavior-preserving refactor that later sections (streaming, errors, accessibility, features) build on.

> [!IMPORTANT]
> **Current state (verified 2026-09-27):** `src/taskpane/taskpane.ts` is 1570 lines with no exports. Its helpers are `$` (line 76), `showElement` and `hideElement` (83-91), `showLoading` and `hideLoading` (93-128), `showError` and `hideError` (130-138), `setPreview` and `updatePreviewStats` (140-183); scoring is `scoreEmail` (196-271); mode and tabs are `adaptUIForMode` (279-342), `TAB_CONFIG` (348-357), and `switchTab` (359-391); then one block of handlers per feature (Draft 422-506, Reply 512-689, Summarize 695-761, Improve 767-832, Extract 838-897, Translate 903-967), and `Office.onReady` (973-1570) holds every event listener, the settings, rules, and templates wiring, and startup. Tab clicks are wired on `.aic-tabs > .aic-tab` (only Reply and Draft), the dropdown items through `.aic-dropdown__item`, and `#tab-settings` and `#tab-rules` by id with no `data-tab`. There is no `src/ui/` and no `src/taskpane/panels/`. The feature modules duplicate helpers: `escapeHtml` five times (draft-email, draft-reply, improve-writing, extract-actions, translate, each escaping only `& < >`), `copyToClipboard` four times (improve-writing, extract-actions, summarize-thread, translate), `bodyToHtml` twice, `formatThread` twice (summarize-thread, extract-actions), `SummaryStyle` twice (settings, summarize-thread), `FOCUS_LABELS` twice (commands, improve-writing), and the language `<option>` list four times in `taskpane.html`. `DROPDOWN_TABS` (line 1085) is unused, and `jest.config.js` runs only `testEnvironment: 'node'`.
<!-- claim: lines src/taskpane/taskpane.ts = 1570 -->
<!-- claim: absent src/ui -->
<!-- claim: absent src/taskpane/panels -->
<!-- claim: count "function escapeHtml" src/features/*.ts = 5 -->
<!-- claim: count "DROPDOWN_TABS" src/taskpane/taskpane.ts = 1 -->
<!-- claim: count "<option value=\"English\"" src/taskpane/taskpane.html = 4 -->

## Inputs

- [`src/taskpane/taskpane.ts`](../../src/taskpane/taskpane.ts) -- the monolith every section here carves up
- [`src/taskpane/taskpane.html`](../../src/taskpane/taskpane.html) -- the element ids the panels bind to; unchanged except `data-tab` (§2) and the generated language lists (§6)
- [`src/features/`](../../src/features/) -- the feature modules whose duplicated helpers §6 merges
- [`jest.config.js`](../../jest.config.js) -- gains a jsdom environment for `src/ui/` tests (§1)
- [`docs/design/taskpane.md`](../../docs/design/taskpane.md) -- the tab bar, feature panel, result card, and status rules the modules keep intact
- -> XREF: D00 T02 §3 -- the split starts from a lint-clean tree, so each move is a pure move in the diff
- -> XREF: D03 T02 §3 -- lazy loading imports the panel modules §3 to §5 create
- -> XREF: D03 T03 §1 -- actionable errors extend the error banner helper §1 creates
- -> XREF: D04 T01 §1 -- output rendering hardens the single `escapeHtml` §1 and §6 leave behind
- -> XREF: D05 T02 §1 -- accessible names are added to the panels §5 finishes
- -> XREF: D05 T03 §1 -- the Accept Changes fix lands in the Improve panel module §4 creates
- -> XREF: D06 T01 §3 -- the output language setting feeds the shared language list §6 creates and the panels §5 finishes
- -> XREF: D06 T02 §1 -- the custom prompt library is a new panel on the structure §5 finishes
- -> XREF: D06 T04 §1 -- live theming uses the shared UI helpers §1 creates

## Outcome

- `wc -l src/taskpane/taskpane.ts` prints fewer than 200 lines, and it only bootstraps: `Office.onReady`, mode detection, and one `init()` call per panel module.
- `src/ui/` holds the only `escapeHtml`, `copyToClipboard`, `showLoading`, `hideLoading`, `showError`, and `hideError` in `src/`, each covered by a jsdom test.
- Each feature tab's wiring is one module under `src/taskpane/panels/`, and `src/taskpane/tabs.ts` owns `TAB_CONFIG` and `switchTab`.
- Every language `<select>` is filled from one `LANGUAGES` list, and `formatThread`, `bodyToHtml`, `FOCUS_LABELS`, and `SummaryStyle` each exist once.
- `npx jest --ci` passes, and a sideload smoke drives every tab with the same results as before the split.

**Adjacency:** list=not-applicable (a refactor adds no browsable records); document=not-applicable (no generated artifact changes); settings=applicable @ D06 T01 §3; reporting=not-applicable (no summaries over data change); notifications=applicable; permissions=not-applicable (no refusal path changes in a behavior-preserving move; D03 T03 owns refusals); audit=not-applicable (no log or restore changes; D03 T03 §5 owns the log); exchange=not-applicable (no import or export); reverse=not-applicable (no new write, so no new reverse)

## Implementation Order

| Order | Section | Deliverable                                              | Depends On | Status |
| :---: | :-----: | -------------------------------------------------------- | ---------- | :----: |
|   1   |   §1    | Shared UI helpers                                        | D00 T02 §3 |  [ ]   |
|   2   |   §2    | The tab controller                                       | §1         |  [ ]   |
|   3   |   §3    | Draft and Reply panel modules                            | §2         |  [ ]   |
|   4   |   §4    | Summarize, Improve, Extract, and Translate panel modules | §2         |  [ ]   |
|   5   |   §5    | Settings, Rules, and Templates panels; a thin bootstrap  | §3, §4     |  [ ]   |
|   6   |   §6    | One copy of every shared helper                          | §5         |  [ ]   |
|   7   |   §7    | Remove dead code                                         | §6         |  [ ]   |

---

## 1. Shared UI Helpers

Every later UI section (streaming, errors, accessibility, dark mode) needs one place to change the loading state, the error banner, and the copy action. Today they live as private functions at the top of `taskpane.ts` and as copies in the feature modules. This section moves them into `src/ui/` unchanged in behavior and gives them tests.

- [ ] Add a jsdom Jest project: install `jest-environment-jsdom` at the jest major in use and add a second project to `jest.config.js` matching `src/ui/**/*.test.ts` with `testEnvironment: 'jsdom'`, keeping the existing `node` project for everything else. Done when: `npx jest --ci` runs both projects and the 35 existing tests still pass.
- [ ] Create `src/ui/dom.ts` exporting `$` (from `taskpane.ts` line 76), `showElement`, and `hideElement` (83-91), moved verbatim. Done when: `taskpane.ts` imports them and no longer defines them.
- [ ] Create `src/ui/status.ts` exporting `showLoading`, `hideLoading`, `showError`, and `hideError` (93-138), moved verbatim including the 350 ms fade in `hideLoading` (the race it causes is fixed by `D03 T03 §6`, not here). Done when: `grep -n "function showLoading\|function showError" src/taskpane/taskpane.ts` prints nothing.
- [ ] Create `src/ui/escape.ts` exporting one `escapeHtml(text)` that escapes `&`, `<`, `>`, `"`, and `'`, and `src/ui/clipboard.ts` exporting one `copyToClipboard(text)` with the fallback path of `src/features/improve-writing.ts` `copyToClipboard` (line 208). Done when: both exist with no callers changed yet (§6 repoints the feature copies).
- [ ] Write `src/ui/status.test.ts`, `src/ui/escape.test.ts`, and `src/ui/clipboard.test.ts` against a jsdom fixture of `#loading-overlay`, `#error-banner`, and `#error-message`: loading shows and hides the overlay, `showError` sets text through `textContent` (a message containing `<b>` renders literally), `escapeHtml` escapes all five characters, and the clipboard falls back when `navigator.clipboard` is undefined. Done when: `npx jest src/ui` passes with those cases named.
- [ ] Commit: `"architecture: move shared UI helpers into src/ui"`

**Test checkpoint:** `npx jest --ci` passes in both projects, including `src/ui/escape.test.ts` asserting `escapeHtml('<a href="x">\'</a>')` equals `&lt;a href=&quot;x&quot;&gt;&#39;&lt;/a&gt;`; `grep -rn "function showLoading\|function showError" src/taskpane` prints nothing; `npm run build` exits `0`. Cheaper substitute that fails: re-exporting the helpers from `taskpane.ts` without moving them, which leaves the definitions there and fails the `grep`.

## 2. The Tab Controller

Tab switching is split across `TAB_CONFIG` and `switchTab` (348-391), click wiring on `.aic-tabs > .aic-tab` that covers only Reply and Draft, dropdown wiring on `.aic-dropdown__item`, and by-id wiring for `#tab-settings` and `#tab-rules`. One controller makes the accessibility work in `D05 T02 §2` a change in one file.

- [ ] Create `src/taskpane/tabs.ts` exporting `TAB_CONFIG`, `switchTab(tab)`, and `initTabs()`, moving `TAB_CONFIG`, `switchTab`, `toggleDropdown`, the outside-click close, and every tab listener from `taskpane.ts` (lines 348-391 and the tab block of `Office.onReady`, 1085-1141 and 1221-1245). Done when: `grep -n "switchTab\|TAB_CONFIG" src/taskpane/taskpane.ts` shows only an import and calls.
- [ ] Add `data-tab="settings"` to `#tab-settings` and `data-tab="rules"` to `#tab-rules` in `taskpane.html`, and wire all five tab buttons and four dropdown items through one delegated listener on `data-tab`. Done when: clicking any of the nine controls calls `switchTab` with its `data-tab` value, asserted by a jsdom test.
- [ ] Keep the Reply side effect: `switchTab('reply')` still calls `loadReplyContext()`, passed in to `initTabs` as a callback so `tabs.ts` does not import the Reply panel. Done when: a jsdom test asserts the callback runs on switching to Reply and not on switching to Draft.
- [ ] Write `src/taskpane/tabs.test.ts` (jsdom project) with a fixture of the tab bar and sections: switching shows the tab's form section, hides the others, leaves result sections as they were, moves `.aic-tab--active`, and calls `hideError`. Done when: `npx jest src/taskpane/tabs.test.ts` passes.
- [ ] Commit: `"architecture: one tab controller for every tab"`

**Test checkpoint:** `npx jest src/taskpane/tabs.test.ts` passes, including the case that clicking `#tab-settings` (now carrying `data-tab`) shows `#settings-section` and hides `#reply-section`; `npx jest --ci` and `npm run build` pass. Cheaper substitute that fails: moving only `switchTab` and leaving the listeners in `taskpane.ts`, which the settings-click test does not reach through `initTabs`.

## 3. Draft and Reply Panel Modules

Draft (lines 422-506) and Reply (512-689) are the two primary tabs and the two with result cards, refine boxes, templates, and scoring. Each becomes one module exporting `init()`, wiring only its own element ids.

- [ ] Create `src/taskpane/panels/draft.ts` exporting `initDraftPanel()`, moving `handleGenerate`, `handleRegenerate`, `handleRefine`, `handleCopyToCompose`, and the listeners for `btn-generate`, `btn-regenerate`, `btn-refine`, `btn-copy-compose`, and the `refine-input` Enter key. Done when: `grep -n "handleGenerate\b" src/taskpane/taskpane.ts` prints nothing.
- [ ] Create `src/taskpane/panels/reply.ts` exporting `initReplyPanel()` and `loadReplyContext()`, moving the six Reply handlers (`handleGenerateReply` through `handleInsertReplyAll`) and their listeners, including `reply-refine-input` and the suggestion chips in `#reply-suggestions`. Done when: `grep -n "handleSuggestReplies" src/taskpane/taskpane.ts` prints nothing.
- [ ] Move `setPreview`, `updatePreviewStats`, and `scoreEmail` into `src/ui/result-card.ts`, since both panels use them, and have both panels import from there. Done when: neither panel defines them and `taskpane.ts` does not either.
- [ ] Write `src/taskpane/panels/draft.test.ts` with the feature module `src/features/draft-email.ts` mocked: clicking `#btn-generate` with `#draft-instructions` filled calls `generateDraft` with the tone, length, language, and goal read from their selects. Done when: `npx jest src/taskpane/panels/draft.test.ts` passes.
- [ ] Commit: `"architecture: Draft and Reply panels in their own modules"`

**Test checkpoint:** `npx jest --ci` passes including `draft.test.ts`; `npm run build` exits `0`; `wc -l src/taskpane/taskpane.ts` is lower than before by at least the 268 lines of the two handler blocks. Cheaper substitute that fails: moving the handlers but leaving the listeners in `Office.onReady`, which makes the panel test's click reach nothing.

## 4. Summarize, Improve, Extract, and Translate Panel Modules

The four dropdown features (lines 695-967) are the smaller half of the pane: one form, one action, one result, a copy button. Each becomes a module, which is where the Accept Changes defect (`D05 T03 §1`) and thread reading (`D05 T03 §5`) will be fixed.

- [ ] Create `src/taskpane/panels/summarize.ts`, `improve.ts`, `extract.ts`, and `translate.ts`, each exporting `init<Name>Panel()` and holding that feature's handlers (`handleSummarize` block 695-761, `handleImprove` block 767-832, `handleExtract` block 838-897, `handleTranslate` block 903-967) and their listeners. Done when: `grep -n "handleSummarize\|handleImprove\|handleExtract\|handleTranslate" src/taskpane/taskpane.ts` prints only four `init*Panel()` calls or nothing.
- [ ] Keep `getSelectedStyle` and `getSelectedFocus` private to their panels, and keep every `innerHTML` assignment exactly as it is (hardening is `D04 T01 §1`). Done when: `grep -c "innerHTML" src/taskpane/panels/*.ts` equals the count those blocks had in `taskpane.ts`, quoted in the commit body.
- [ ] Write `src/taskpane/panels/improve.test.ts` with `src/features/improve-writing.ts` mocked: the checked `improve-focus` radio reaches `improveWriting`, and `#btn-accept-changes` calls `acceptChanges` once. Done when: `npx jest src/taskpane/panels/improve.test.ts` passes.
- [ ] Commit: `"architecture: Summarize, Improve, Extract, and Translate panels in their own modules"`

**Test checkpoint:** `npx jest --ci` passes including `improve.test.ts`; `npm run build` exits `0`; the `innerHTML` count across `src/taskpane/` is unchanged from before the section (quoted before and after). Cheaper substitute that fails: one `panels/misc.ts` holding all four features, which the per-panel `grep` and test paths do not match.

## 5. Settings, Rules, and Templates Panels; a Thin Bootstrap

What remains in `Office.onReady` after §2 to §4 is settings (`btn-toggle-api-key`, `btn-save-settings`, `btn-test-connection`, `btn-clear-all-data`), rules (`btn-save-rules`), templates (lines 1419-1517), the character counters and clear buttons, the custom goal toggle, copy buttons, scroll to top, and startup. After this section `taskpane.ts` only boots.

**Fidelity:** Gemail task pane, every tab (header, tab bar, feature panel, result card, status line) -- docs/captures/taskpane/split-before/ (captured by this section before its first move) and docs/captures/taskpane/split-after/. Control order, spacing, text, and behavior identical; no deviation is allowed in a refactor.
**Design:** docs/design/taskpane.md#layout, docs/design/taskpane.md#settings-panel, docs/design/taskpane.md#rules-panel -- states: all in spec -- themes: n/a (the refactor changes no color and D06 T04 owns live theming) -- density: n/a (one density in a fixed-width task pane)
**Job:** A user can use every tab exactly as before. Consumer: none: this surface is the consumer.
**Treatment:** A move of code into modules with no visible change. Cheaper substitute that fails the checkpoint: rewriting the panels while moving them, which changes captured text or order.
**Chrome:** consume `src/ui/dom.ts`, `src/ui/status.ts`, `src/ui/result-card.ts`, and `src/taskpane/tabs.ts`. Do not invent a second loading helper or tab switcher.
**Needs:** Outlook client (sideload)
**Requires:** display-session -- the before and after captures and the smoke drive a sideloaded task pane in a browser window

- [ ] Before moving anything, capture every tab in Outlook on the web in read and compose mode into `docs/captures/taskpane/split-before/`. Done when: one PNG per tab and mode is committed.
- [ ] Create `src/taskpane/panels/settings.ts`, `rules.ts`, and `templates.ts`, each exporting `init<Name>Panel()`, and `src/ui/inputs.ts` for the character counters, clear buttons, auto-grow, and `.aic-copy-btn[data-copy-target]` wiring. Done when: `Office.onReady` in `taskpane.ts` contains no `addEventListener` call.
- [ ] Reduce `src/taskpane/taskpane.ts` to `Office.onReady`: mode detection (`adaptUIForMode`, moved to `src/taskpane/mode.ts`), theme detection as it is today, the `ItemChanged` registration as it is today, and one `init*Panel()` per module. Done when: `wc -l src/taskpane/taskpane.ts` prints fewer than `200`.
- [ ] Drive a sideload smoke of every tab in read and compose mode (generate, regenerate, copy, insert where offered, save settings, save rules, save and delete a template) and capture into `docs/captures/taskpane/split-after/`. Done when: every action behaves as in the before run and the browser console shows no new error, with the console count quoted.
- [ ] Commit: `"architecture: settings, rules, and templates panels; taskpane.ts only boots"`

**Test checkpoint:** `wc -l src/taskpane/taskpane.ts` prints fewer than `200`; `grep -c addEventListener src/taskpane/taskpane.ts` prints `0`; `npx jest --ci` and `npm run build` pass; the before and after captures match tab for tab and the smoke's console error count is `0`. Cheaper substitute that fails: moving `Office.onReady`'s body into one `src/taskpane/init.ts`, which passes the line count but fails the `addEventListener` rule in that file's per-panel review and leaves the monolith renamed.

## 6. One Copy of Every Shared Helper

With the panels split, the duplicates in the feature modules become visible and each gets exactly one home. Behavior converges on the safest copy: the escaper from §1 escapes quotes too, which none of the five copies did.

- [ ] Replace the five feature-module `escapeHtml` functions (draft-email, draft-reply, improve-writing, extract-actions, translate) with imports from `src/ui/escape.ts`. Done when: `grep -rn "function escapeHtml" src` prints only `src/ui/escape.ts`.
- [ ] Replace the four `copyToClipboard` functions (improve-writing, extract-actions, summarize-thread, translate) with imports from `src/ui/clipboard.ts`. Done when: `grep -rn "function copyToClipboard" src` prints only `src/ui/clipboard.ts`.
- [ ] Move `bodyToHtml` (draft-email, draft-reply) and `formatThread` (summarize-thread, extract-actions) into `src/features/shared.ts`, and keep one `SummaryStyle` type (in `src/features/settings.ts`) and one `FOCUS_LABELS` (in `src/features/improve-writing.ts`, imported by `src/commands/commands.ts`). Done when: `grep -rn "function bodyToHtml\|function formatThread\|type SummaryStyle\|FOCUS_LABELS =" src` prints one line each.
- [ ] Export one `LANGUAGES` list from `src/features/translate.ts` (it exists there, line 29, unused) and fill the four language `<select>` elements from it at init, replacing the four hard-coded `<option>` lists in `taskpane.html` with an empty select plus the default. Done when: `grep -c '<option value="English"' src/taskpane/taskpane.html` prints `0` and a jsdom test asserts each select has `LANGUAGES.length` options with the saved default selected.
- [ ] Add a unit test for `formatThread` and `bodyToHtml` in `src/features/shared.test.ts` covering an empty thread, a two-message thread, and a body with `<script>` (escaped). Done when: `npx jest src/features/shared.test.ts` passes.
- [ ] Commit: `"architecture: one copy of every shared helper"`

**Test checkpoint:** the five `grep` checks above print one definition each (and `0` for the hard-coded English option); `npx jest --ci` passes including `shared.test.ts` and the language-select test; `npm run build` exits `0`. Cheaper substitute that fails: re-exporting the old copies from a barrel file, which leaves five definitions for the `grep` to find.

## 7. Remove Dead Code

The 2026-09-27 inventory found exports nothing calls and state nothing reads. Dead code misleads the next reader into preserving it, and some of it (for example `insertIntoReply`, which writes the whole body with `body.setAsync`) is a write path that should not exist unreviewed.

- [ ] Delete the unused exports after confirming each with `grep -rn "<name>" src scripts` showing only its definition (and tests): `CHANGE_TONE_PROMPT` (templates.ts), `getLastDraft`, `hasPreviousDraft` (draft-email.ts), `insertIntoReply`, `getLastReply`, `hasPreviousReply` (draft-reply.ts), `getTexts` (improve-writing.ts), `getLastSummary` (summarize-thread.ts), `getApiKey`, `setApiKey` (settings.ts), `getCurrentEmailBodyHtml`, `getEmailRecipients`, `getConversationId`, `stripHtml` (outlook.ts). Done when: each is gone and `npm run build` and `npx tsc --noEmit` exit `0`.
- [ ] Delete write-only and unused locals: `lastRawResponse` (extract-actions.ts), `unchanged` in `generateDiffHtml` (improve-writing.ts), `DROPDOWN_TABS` (moved with the tab code), and the unused `reject` and `hasError` in `getComposeModeRecipients` (outlook.ts). Done when: `npx eslint src --rule '{"@typescript-eslint/no-unused-vars":"error"}'` reports nothing for these files.
- [ ] Replace the needless dynamic imports of already-imported modules (the `import()` calls that were at `taskpane.ts` line 309, now in `src/taskpane/mode.ts`, and line 599, now in the Reply panel) with the static imports, dropping the unused `getCurrentEmailSubject` binding. Done when: `grep -rn "import('" src/taskpane` prints nothing (lazy panel loading arrives later, in `D03 T02 §3`).
- [ ] Commit: `"architecture: remove dead code found in the import inventory"`

**Test checkpoint:** `grep -rn "insertIntoReply\|CHANGE_TONE_PROMPT\|DROPDOWN_TABS\|lastRawResponse" src` prints nothing; `npx tsc --noEmit`, `npm run lint`, `npx jest --ci`, and `npm run build` exit `0`. Cheaper substitute that fails: prefixing the names with `_` to silence the linter, which leaves them for the `grep` to find.

## Verification

- [ ] `pwsh scripts/check-all.ps1` -- exits 0: production build, typecheck, lint, tests, manifest, TODO gates green
- [ ] `npx jest --ci` exits 0 with `src/ui/*.test.ts`, `src/taskpane/tabs.test.ts`, and `src/taskpane/panels/*.test.ts` reporting
- [ ] `wc -l src/taskpane/taskpane.ts` prints fewer than 200, and the sideload smoke of §5 is repeated at file close with the console error count `0`
