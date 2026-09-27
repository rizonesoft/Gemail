---
schema_version: 1
id: performance
domain: 03-architecture
status: draft
title: "TODO-02 -- Performance"
depends_on: []
---

# TODO-02 -- Performance

> **Goal:** The task pane opens fast, shows text as the model writes it, and never does work twice. The production bundle has a measured size budget that CI enforces, ships no public source maps and no ES5 polyfill bloat for the two modern clients Gemail supports, and loads each feature panel only when its tab opens. A model call streams into the result card with a **Stop** button that keeps the partial text, every action runs one request at a time, the email context is read once per item, the connection to OpenRouter is warm before the first click, and the quality score is computed only when the user asks for it.

> [!IMPORTANT]
> **Current state (verified 2026-09-27):** `npm run build` (webpack 5.105.0, production) writes `dist/taskpane.js` at 438,469 bytes, `dist/commands.js` at 269,055 bytes, and `dist/polyfill.js` at 226,314 bytes, and warns that the bundles exceed webpack's performance recommendation; nothing records a budget. `webpack.config.js` sets `devtool: "source-map"` for every mode, so production publishes `.map` files to GitHub Pages, and its `polyfill` entry bundles all of `core-js/stable` plus `regenerator-runtime` while `babel.config.json` targets `esmodules: false` (ES5), although `.browserslistrc` names only the last two Chrome and Edge versions and the supported clients are new Outlook (Edge WebView2) and Outlook on the web. `package.json` has no `sideEffects` field. Every panel is imported statically into one `taskpane` chunk. There is no streaming: every feature waits for the whole response behind the full-pane `#loading-overlay`. Buttons are not disabled during a call, so a double click starts two requests. Only Reply caches the email context (`cachedContext` in `src/features/draft-reply.ts`); Summarize, Improve, Extract, and Translate re-read the body on every click. `taskpane.html` preconnects only to `fonts.googleapis.com` and `fonts.gstatic.com`. `scoreEmail` in `taskpane.ts` (line 196) waits 500 ms and makes a second model call after every generate, regenerate, and refine in Draft and Reply (six call sites).
<!-- claim: count "devtool: \"source-map\"" webpack.config.js = 1 -->
<!-- claim: count "core-js/stable" webpack.config.js = 1 -->
<!-- claim: count "\"esmodules\": false" babel.config.json = 1 -->
<!-- claim: count "void scoreEmail\(" src/taskpane/taskpane.ts = 6 -->
<!-- claim: absent scripts/bundle-budget.js -->
<!-- claim: count "openrouter.ai" src/taskpane/taskpane.html = 0 -->

## Inputs

- [`webpack.config.js`](../../webpack.config.js), [`babel.config.json`](../../babel.config.json), [`.browserslistrc`](../../.browserslistrc) -- the build §1 to §3 measure and change
- [`src/taskpane/panels/`](../../src/taskpane/panels/) -- the panel modules (from the split) §3 loads lazily and §4 to §6 change
- [`src/ui/result-card.ts`](../../src/ui/result-card.ts) -- the result card helpers (from the split) §4 streams into and §8 removes the automatic score from
- [`docs/design/taskpane.md`](../../docs/design/taskpane.md) -- the result card, buttons, and loading and streaming rules §4 and §8 build to
- OpenRouter API reference, "Streaming" (https://openrouter.ai/docs/api-reference/streaming) -- cancellation by aborting the request, which §4 relies on
- webpack documentation, "Lazy Loading" and "Tree Shaking" (https://webpack.js.org/guides/lazy-loading/, https://webpack.js.org/guides/tree-shaking/) -- §2 and §3
- -> XREF: D00 T02 §4 -- the budget check runs as a step of the CI build workflow that section creates
- -> XREF: D02 T02 §1 -- `streamText` and `AiError` in `src/services/ai.ts`, which §4 consumes; the catalogue picker (D02 T02 §4) is what §7 pre-warms; the scoring call §8 changes was repointed in D02 T02 §2
- -> XREF: D03 T01 §5 -- the panel modules and the thin bootstrap §3 to §6 build on
- -> XREF: D04 T01 §3 -- the CSP is written against the production build hygiene of §2 (no inline source maps, known chunk names)

## Outcome

- `node scripts/bundle-budget.js` exits `0` against a committed budget in `scripts/bundle-budget.json` and exits `1` naming the chunk when any chunk grows past it; the CI build workflow runs it.
- `dist/` contains no `.map` file after `npm run build`, `dist/polyfill.js` is gone or under 20 KB, and `dist/taskpane.js` is smaller than the 438,469 bytes measured on 2026-09-27.
- Opening the pane loads only the Reply or Draft panel chunk; the Summarize, Improve, Extract, Translate, Settings, Rules, and Templates chunks load on first open of their tab.
- A model call writes text into the result card as it streams; **Stop** ends it and keeps the partial text; a second click on a busy action does nothing.
- The body of the current item is read once per item and re-read after `ItemChanged`.
- The quality score appears only when the user clicks **Score**.

**Adjacency:** list=not-applicable (no browsable records are added); document=applicable; settings=not-applicable (no new setting: the score becomes a button, not a preference); reporting=applicable; notifications=applicable; permissions=applicable @ D03 T03 §1; audit=applicable @ D03 T03 §5; exchange=not-applicable (nothing is imported or exported); reverse=applicable

## Implementation Order

| Order | Section | Deliverable                      | Depends On             | Status |
| :---: | :-----: | -------------------------------- | ---------------------- | :----: |
|   1   |   §1    | Bundle baseline and budget       | D00 T02 §4             |  [ ]   |
|   2   |   §2    | Production build hygiene         | §1                     |  [ ]   |
|   3   |   §3    | Lazy-load feature panels         | §1, D03 T01 §5         |  [ ]   |
|   4   |   §4    | Streaming output with Stop       | D02 T02 §1, D03 T01 §5 |  [ ]   |
|   5   |   §5    | One request at a time per action | D03 T01 §5             |  [ ]   |
|   6   |   §6    | Email context cache per item     | D03 T01 §5             |  [ ]   |
|   7   |   §7    | Pre-warm the connection          | D02 T02 §4             |  [ ]   |
|   8   |   §8    | Score on demand                  | D02 T02 §2             |  [ ]   |

---

## 1. Bundle Baseline and Budget

Size work without a measurement is guessing, and a size win without a gate regresses on the next dependency. This section records the sizes of the production chunks at the time it runs (they will differ from 2026-09-27 once the OpenRouter cutover has removed `@google/genai`) and makes CI refuse growth past a budget.

- [ ] Write `scripts/bundle-budget.js` (Node, no dependencies) that reads every `dist/*.js` and `dist/*.css`, prints a table of raw and gzip sizes (`zlib.gzipSync`), compares each against `scripts/bundle-budget.json`, and exits `1` naming each chunk over budget or missing from the budget file. Done when: `node scripts/bundle-budget.js` after `npm run build` prints the table and exits `0` with a budget file present.
- [ ] Measure the current production build and write `scripts/bundle-budget.json` with each chunk's gzip size plus 5 percent, rounded up to the next KB, and the measurement date. Done when: the file exists and the commit body quotes the measured table.
- [ ] Add `"size": "node scripts/bundle-budget.js"` to `package.json` and a `npm run size` step after the build step in `.github/workflows/build.yml`. Done when: the workflow file names the step and a CI run shows its table.
- [ ] Add a self-check: `node scripts/bundle-budget.js --self-test` builds a temp `dist` with one oversized file and asserts exit `1` naming it. Done when: the self-test exits `0`.
- [ ] Commit: `"performance: measure the bundle and enforce a budget"`

**Test checkpoint:** `npm run build && npm run size` exits `0` and prints every chunk; appending 10 KB of random text to `dist/taskpane.js` makes `npm run size` exit `1` naming `taskpane.js`; `node scripts/bundle-budget.js --self-test` exits `0`. Cheaper substitute that fails: webpack's `performance.hints: "error"` with its default 244 KB limit, which the current chunks already exceed and which ignores gzip size.

## 2. Production Build Hygiene

Production publishes source maps to a public site, transpiles to ES5 for browsers Gemail does not support, and ships the whole of `core-js`. New Outlook runs Edge WebView2 and Outlook on the web runs in current Edge, Chrome, Firefox, or Safari, so an ES2020 target with no global polyfill bundle is sufficient.

- [ ] Set `devtool` in `webpack.config.js` to `"source-map"` only in development and `false` in production. Done when: `npm run build && ls dist/*.map` finds nothing and `npm run build:dev` still writes maps.
- [ ] Set the Babel target in `babel.config.json` from `"esmodules": false` to the `.browserslistrc` query (remove the `targets` override so preset-env reads `.browserslistrc`), and add `last 2 Firefox versions` and `last 2 Safari versions` to `.browserslistrc` for Outlook on the web. Done when: `npx browserslist` prints only those four browser families.
- [ ] Remove the `polyfill` entry (`core-js/stable`, `regenerator-runtime/runtime`) from `webpack.config.js` and its `<script>` from both HTML templates, and use `useBuiltIns: "usage"` with `corejs: 3` in `@babel/preset-env` so only needed polyfills are included. Done when: `dist/polyfill.js` no longer exists and the sideload smoke of every tab in Outlook on the web shows no `ReferenceError` in the console.
- [ ] Add `"sideEffects": ["*.css"]` to `package.json` and set `minify` options on both `HtmlWebpackPlugin` instances in production (`collapseWhitespace`, `removeComments`). Done when: `dist/taskpane.html` is smaller than before, quoted in the commit body.
- [ ] Re-measure and lower `scripts/bundle-budget.json` to the new sizes plus 5 percent. Done when: the budget file shows smaller numbers than §1 wrote and `npm run size` exits `0`.
- [ ] Commit: `"performance: modern targets, no public source maps, no polyfill bundle"`

**Needs:** Outlook client (sideload)
**Requires:** display-session -- the no-ReferenceError proof drives the sideloaded task pane in a browser window

**Test checkpoint:** after `npm run build`, `ls dist/*.map dist/polyfill.js` finds nothing and `npm run size` exits `0` with the lowered budget; the sideload smoke opens every tab in Outlook on the web and new Outlook with `0` console errors (quoted per client). Cheaper substitute that fails: `devtool: "hidden-source-map"`, which still writes `.map` files into `dist/` and fails the `ls`.

## 3. Lazy-Load Feature Panels

Most users open Reply or Draft; Translate or Extract may never be opened in a session. With each tab in its own module (`D03 T01 §5`), webpack can split them into chunks loaded on first open of their tab.

- [ ] In `src/taskpane/tabs.ts`, map each tab to a loader (`() => import(/* webpackChunkName: "panel-summarize" */ "./panels/summarize")` and so on) and call its `init*Panel()` on first `switchTab` to that tab, once. Keep Reply and Draft static imports because one of them is the startup tab. Done when: `npm run build` writes one `panel-*.js` chunk per lazy tab.
- [ ] Show the existing loading state while a panel chunk loads and report a chunk load failure through `showError` with a retry. Done when: a jsdom test with the loader rejecting asserts the error message and that a second `switchTab` retries the import.
- [ ] Add each `panel-*.js` chunk to `scripts/bundle-budget.json`. Done when: `npm run size` lists them and exits `0`.
- [ ] Commit: `"performance: load feature panels on first open"`

**Test checkpoint:** `npm run build` writes `panel-summarize.js`, `panel-improve.js`, `panel-extract.js`, `panel-translate.js`, `panel-settings.js`, `panel-rules.js`, and `panel-templates.js`, and `dist/taskpane.js` is smaller than after §2 (both sizes quoted); in a sideloaded Outlook on the web session the DevTools network log shows `panel-translate.js` requested only after the Translate tab is first opened; `npx jest src/taskpane/tabs.test.ts` passes the chunk-failure case. Cheaper substitute that fails: `splitChunks: { chunks: "all" }` alone, which splits vendor code but still loads every panel at startup.

## 4. Streaming Output with Stop

Today every feature waits for the complete response behind a full-pane overlay. With `streamText` in the facade (`D02 T02 §1`, over the SSE client of `D02 T01 §3`), the result card can show text as it arrives, and the user can stop a response that is going the wrong way. Stopping keeps what arrived: the user decides whether to insert it.

**Fidelity:** Gemail task pane, result card while streaming and after Stop, in Draft, Reply, Summarize, Improve, and Translate -- docs/captures/taskpane/streaming/. The card layout, action order, and text match the spec; the overlay no longer covers a streaming card.
**Design:** docs/design/mockup.md#result-card, docs/design/mockup.md#streaming-and-stop, docs/design/taskpane.md#result-card, docs/design/taskpane.md#loading-and-streaming, docs/design/taskpane.md#buttons -- states: idle, streaming, stopped, complete, error -- themes: n/a (colors come from existing tokens and D06 T04 owns live theming) -- density: n/a (one density in a fixed-width task pane)
**Job:** A user can watch the email being written and stop it at any point, keeping the partial text. Consumer: the insert, copy, and refine actions of each panel, which read the card's final text.
**Treatment:** Chunks appended to the preview through `textContent` as they arrive, with **Stop** replacing **Regenerate** while streaming. Cheaper substitute that fails the checkpoint: a typewriter animation over a completed response, which cannot be stopped mid-request and shows nothing until the whole response has arrived.
**Chrome:** consume `streamText` from `src/services/ai.ts`, `src/ui/result-card.ts`, and `src/ui/status.ts`. Do not invent a second loading indicator or a second abort mechanism.
**Needs:** Outlook client (sideload)
**Requires:** display-session -- the streaming and Stop proof drives a sideloaded task pane and captures it

- [ ] Add `streamIntoCard(cardId, request)` to `src/ui/result-card.ts`: it creates an `AbortController`, iterates `streamText(prompt, { signal })`, appends each chunk to the preview with `textContent`, updates the word count, and resolves with the final text and whether it was stopped. Done when: a jsdom test with a fake async iterator of three chunks asserts the preview text after each chunk.
- [ ] Add the **Stop** button to each streaming card in `taskpane.html` (hidden unless streaming) and wire it to the controller's `abort()`; while streaming, hide **Regenerate** and disable the insert action. Done when: a jsdom test asserts Stop aborts the iterator, keeps the partial text, and re-enables the insert action.
- [ ] Replace the full-pane overlay with the inline streaming indicator for streaming calls (the overlay stays for non-streaming calls such as JSON extraction), with the neutral text from the spec ("Writing your reply..."). Done when: a jsdom test asserts `#loading-overlay` stays hidden during `streamIntoCard`.
- [ ] Switch Draft, Reply, Summarize, Improve, and Translate generation to `streamIntoCard`; Extract and the suggested replies stay non-streaming because they parse JSON. Done when: `grep -rn "generateText(" src/taskpane/panels` finds only the non-streaming callers, listed in the commit body.
- [ ] Map an `AiError` raised mid-stream (for example a stream cut) to the error banner while keeping the text received so far. Done when: a jsdom test whose iterator throws after two chunks asserts both the banner and the two chunks in the preview.
- [ ] Drive each streaming feature in Outlook on the web: start, stop midway, insert the partial text into a compose form, and capture into `docs/captures/taskpane/streaming/`. Done when: captures of the streaming and stopped states are committed and the inserted text equals the stopped preview.
- [ ] Hold the built surface to the approved mockup: render it (sideloaded, or in the jsdom harness for a component), compare it with the anchors on this section's `**Design:**` line in `docs/design/mockup.md` and their renders under `docs/design/mockup/renders/`, use only design tokens (`docs/design/tokens.json`) and registry icons (`iconSvg()` from `src/ui/icons.ts`), and commit a capture of the result under `docs/captures/taskpane/`. Done when: `python scripts/design-lint.py` exits 0 with the baseline no larger, every difference from the mockup is fixed or recorded as a `**Design deviation:**` naming its follow-up section, and the capture is committed. Cheaper substitute that fails: building from the prose alone, which the capture comparison at review refuses.
- [ ] Commit: `"performance: stream results into the card with Stop"`

**Test checkpoint:** `npx jest src/ui/result-card.test.ts` passes the three-chunk, Stop, overlay-hidden, and mid-stream-error cases; in the sideload the first text appears before the response completes (the time to first chunk and to completion are quoted from the debug log or DevTools timing for one Reply), and Stop leaves the partial text insertable. Cheaper substitute that fails: disabling the overlay and awaiting the full response, which the three-chunk test (asserting text after the first chunk) fails.

## 5. One Request at a Time per Action

No button is disabled while its request runs, so a double click, or Enter held in a refine box, starts two model calls that race to fill one card and bill twice. One guard in `src/ui/` covers every action.

- [ ] Add `runExclusive(button, fn)` to `src/ui/actions.ts`: if the button's action is already running it returns without calling `fn`; otherwise it disables the button, sets `aria-busy="true"`, awaits `fn`, and restores both in `finally`. Done when: a jsdom test asserts two rapid calls invoke `fn` once and that the button is re-enabled after `fn` rejects.
- [ ] Wrap every model-calling handler in the panels with `runExclusive` (generate, regenerate, refine, suggest, summarize, improve, extract, translate, and Test Connection). Done when: `grep -c "runExclusive(" src/taskpane/panels/*.ts` covers every handler listed in the commit body.
- [ ] Guard the Enter-key refine paths (`refine-input`, `reply-refine-input`) through the same guard as their buttons. Done when: a jsdom test pressing Enter twice asserts one call.
- [ ] Commit: `"performance: one request at a time per action"`

**Test checkpoint:** `npx jest src/ui/actions.test.ts` passes the double-call, rejection, and Enter-key cases; a panel test for Draft double-clicks `#btn-generate` and asserts the mocked `streamText` was called once. Cheaper substitute that fails: a 300 ms click debounce, which lets a second click after 300 ms start a second call while the first is still streaming.

## 6. Email Context Cache per Item

Reading the body through Office.js (`body.getAsync`) is asynchronous and can take hundreds of milliseconds on long threads; four features re-read it on every click, while Reply alone caches it. One cache keyed by the item makes every feature read once and makes the invalidation rule explicit.

- [ ] Create `src/services/context-cache.ts` exporting `getItemContext()`, which returns `{ subject, body, sender }` for the current item, cached by `Office.context.mailbox.item.itemId` in read mode and by a per-open token in compose mode (whose body changes as the user types, so compose reads are never cached across actions). Done when: a test with the Office.js mock asserts one `body.getAsync` for two read-mode calls on the same item.
- [ ] Clear the cache in the `ItemChanged` handler and make `cachedContext` in `src/features/draft-reply.ts` use this service instead of its own variable. Done when: `grep -n "let cachedContext" src/features/draft-reply.ts` prints nothing and a test firing the mock `ItemChanged` asserts a fresh read.
- [ ] Point Summarize, Improve (read mode only), Extract, and Translate at `getItemContext()`. Done when: `grep -rn "getCurrentEmailBody(" src/features` lists only compose-mode paths, named in the commit body.
- [ ] Commit: `"performance: read the email context once per item"`

**Test checkpoint:** `npx jest src/services/context-cache.test.ts` passes the same-item, `ItemChanged`, and compose-never-cached cases; the Office.js mock records one `body.getAsync` call across Summarize then Translate on one read-mode item. Cheaper substitute that fails: a module-level variable that is never cleared, which the `ItemChanged` case fails by returning the previous message's body.

## 7. Pre-Warm the Connection

The first model call pays DNS, TLS, and the model catalogue fetch. A `preconnect` hint and an idle-time catalogue refresh move that cost before the first click without sending any email content.

- [ ] Add `<link rel="preconnect" href="https://openrouter.ai" crossorigin>` to `src/taskpane/taskpane.html`. Done when: `grep -c 'href="https://openrouter.ai"' src/taskpane/taskpane.html` prints `1`.
- [ ] After `Office.onReady` settles, schedule one catalogue refresh through the model picker's loader (`D02 T02 §4`) in `requestIdleCallback` (falling back to `setTimeout(…, 2000)`), only when the cached catalogue is past its TTL. Done when: a jsdom test with a fresh cache asserts no fetch, and with an expired cache asserts one fetch after idle.
- [ ] Confirm the pre-warm sends no API key and no email content: the catalogue endpoint needs no auth. Done when: the test asserts the mocked `fetch` was called without an `Authorization` header.
- [ ] Commit: `"performance: pre-warm the OpenRouter connection"`

**Test checkpoint:** `npx jest src/taskpane/prewarm.test.ts` passes the fresh-cache, expired-cache, and no-auth cases; in the sideload DevTools shows the `openrouter.ai` connection established before the first action, and the first Reply's time to first chunk is quoted before and after the change. Cheaper substitute that fails: sending a dummy chat completion at startup, which spends the user's credit and fails the no-auth assertion.

## 8. Score on Demand

After every generate, regenerate, and refine in Draft and Reply, `scoreEmail` waits 500 ms and makes a second model call to fill `#draft-score` or `#reply-score`. That doubles the calls, cost, and rate-limit pressure for a panel many users never read. The score becomes a button.

**Fidelity:** Gemail task pane, Draft and Reply result cards with the score card collapsed and after **Score** -- docs/captures/taskpane/score/. The score card layout is unchanged; only its trigger changes.
**Design:** docs/design/mockup.md#result-card, docs/design/taskpane.md#result-card, docs/design/taskpane.md#buttons -- states: idle, scoring, scored, error -- themes: n/a (the score colors move to tokens in D06 T04) -- density: n/a (one density in a fixed-width task pane)
**Job:** A user can ask for a clarity and professionalism score of the draft in front of them. Consumer: none: this surface is the consumer.
**Treatment:** A **Score** secondary button in the result card actions that scores the current preview text, including the user's edits. Cheaper substitute that fails the checkpoint: keeping the automatic call and hiding the score card, which still makes the second request.
**Chrome:** consume `src/ui/result-card.ts`, `src/ui/actions.ts` (`runExclusive`), and `generateJson` from `src/services/ai.ts`. Do not invent a second score renderer.
**Needs:** Outlook client (sideload)
**Requires:** display-session -- the capture and the network-count proof drive a sideloaded task pane

- [ ] Remove the six automatic `scoreEmail` calls from the Draft and Reply panels and the 500 ms wait inside `scoreEmail`. Done when: `grep -rn "scoreEmail(" src/taskpane/panels` finds only the button handler.
- [ ] Add a **Score** button to the Draft and Reply result card actions in `taskpane.html` that scores the preview's current text (not the last generated text) through `runExclusive`. Done when: a jsdom test edits the preview, clicks **Score**, and asserts the mocked `generateJson` received the edited text.
- [ ] Hide a stale score when the preview text changes after scoring. Done when: a jsdom test asserts `#draft-score` hides on the preview's `input` event.
- [ ] Capture the collapsed and scored states in Outlook on the web into `docs/captures/taskpane/score/`. Done when: both captures are committed.
- [ ] Hold the built surface to the approved mockup: render it (sideloaded, or in the jsdom harness for a component), compare it with the anchors on this section's `**Design:**` line in `docs/design/mockup.md` and their renders under `docs/design/mockup/renders/`, use only design tokens (`docs/design/tokens.json`) and registry icons (`iconSvg()` from `src/ui/icons.ts`), and commit a capture of the result under `docs/captures/taskpane/`. Done when: `python scripts/design-lint.py` exits 0 with the baseline no larger, every difference from the mockup is fixed or recorded as a `**Design deviation:**` naming its follow-up section, and the capture is committed. Cheaper substitute that fails: building from the prose alone, which the capture comparison at review refuses.
- [ ] Commit: `"performance: score a draft only when asked"`

**Test checkpoint:** a Draft panel test generates once and asserts the mocked facade saw exactly one call (no score call), then clicks **Score** and asserts a second call with the edited preview text; in the sideload the DevTools network log shows one `chat/completions` request per generate. Cheaper substitute that fails: debouncing the automatic score, which still issues the second request and fails the one-call assertion.

## Verification

- [ ] `pwsh scripts/check-all.ps1` -- exits 0: production build, typecheck, lint, tests, manifest, TODO gates green
- [ ] `npm run build && npm run size` exits 0 and the committed budget is below the 2026-09-27 sizes
- [ ] `npx jest --ci` exits 0 with `src/ui/result-card.test.ts`, `src/ui/actions.test.ts`, `src/services/context-cache.test.ts`, and `src/taskpane/prewarm.test.ts` reporting
- [ ] A sideload smoke in new Outlook and Outlook on the web streams, stops, and inserts in every streaming feature, with `0` console errors per client
