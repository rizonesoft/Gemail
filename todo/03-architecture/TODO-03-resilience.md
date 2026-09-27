---
schema_version: 1
id: resilience
domain: 03-architecture
status: draft
title: "TODO-03 -- Resilience and Diagnostics"
depends_on: []
---

# TODO-03 -- Resilience and Diagnostics

> **Goal:** Every failure tells the user what happened and what to do, and nothing the user typed or the model wrote is lost to a failure. Each `AiError` code has its own message and a **Retry** where retrying can help; an offline banner appears while the device is offline; draft inputs survive a task pane reload; long emails are truncated to the chosen model's context window with a notice instead of failing; an opt-in debug log records timings and error codes without ever recording email content or the key; and every Office.js write reports its failure instead of failing silently.

> [!IMPORTANT]
> **Current state (verified 2026-09-27):** `showError` in `src/taskpane/taskpane.ts` (line 130) puts `err.message` into `#error-message` through `textContent`; no handler inspects an error code (the only code check is the string literal `'CONTENT_FILTERED'` in the Test Connection handler), and the banner has only a dismiss button (`#btn-dismiss-error`), no retry. Nothing listens for `online` or `offline`. No draft input is persisted: a reload of the pane loses `#draft-instructions`, `#reply-instructions`, and both previews. Input truncation uses fixed budgets through `truncateContext` in `src/prompts/builder.ts` (4 characters per token): 6000 tokens in `draft-reply.ts` and `extract-actions.ts`, 8000 in `summarize-thread.ts`, and none in `translate.ts` or `improve-writing.ts`, and the user is never told. `taskpane.ts` has three `console.log` calls, two of which print model output derived from email content (lines 230 and 616). The `body.prependAsync` calls in `src/features/draft-email.ts` (line 137) and `src/features/draft-reply.ts` (lines 232 and 261), and `subject.setAsync` (draft-email.ts line 145), pass no callback, so a failed write is silent. `Office.context.mailbox.addHandlerAsync(Office.EventType.ItemChanged, ...)` (taskpane.ts line 1008) needs Mailbox 1.5 and is not guarded, while the manifest's `VersionOverridesV1_0` declares 1.3. `hideLoading` hides the overlay after a 350 ms `setTimeout` (line 127), which can hide an overlay a quick follow-up call re-showed.
<!-- claim: count "console.log" src/taskpane/taskpane.ts = 3 -->
<!-- claim: count "'online'" src/taskpane/taskpane.ts = 0 -->
<!-- claim: count "body\.prependAsync\(" src/features/draft-reply.ts = 2 -->
<!-- claim: count "setTimeout\(cleanup, 350\)" src/taskpane/taskpane.ts = 1 -->
<!-- claim: absent src/services/log.ts -->
<!-- claim: count "MAX_CONTENT_TOKENS = " src/features/*.ts = 3 -->

## Inputs

- [`src/ui/status.ts`](../../src/ui/status.ts) -- the error banner and loading helpers (from the split) §1, §2, and §6 extend
- [`src/services/outlook.ts`](../../src/services/outlook.ts), [`src/features/draft-email.ts`](../../src/features/draft-email.ts), [`src/features/draft-reply.ts`](../../src/features/draft-reply.ts) -- the Office.js write paths §6 makes report
- [`src/prompts/builder.ts`](../../src/prompts/builder.ts) -- `truncateContext`, which §4 drives from the model's context window
- [`docs/design/taskpane.md`](../../docs/design/taskpane.md) -- the status and errors, dialogs, and settings panel rules §1, §2, §3, and §5 build to
- Microsoft Learn, "Understanding Outlook API requirement sets" (https://learn.microsoft.com/javascript/api/requirement-sets/outlook/outlook-api-requirement-sets) and `Office.context.requirements.isSetSupported` -- the guard §6 adds
- Microsoft Learn, `Office.AsyncResult` (https://learn.microsoft.com/javascript/api/office/office.asyncresult) -- the callback status §6 checks
- -> XREF: D02 T01 §5 -- the model catalogue's `context_length`, which §4 reads for the selected model
- -> XREF: D02 T02 §1 -- the `AiError` codes §1 maps to messages and §4 maps `CONTEXT_TOO_LONG` from
- -> XREF: D03 T01 §1 -- the shared status helpers §1 builds the actionable banner on; the panels of D03 T01 §5 are where §3, §5, and §6 land

## Outcome

- For each `AiError` code the banner shows one specific message naming the fix, and a **Retry** button for the retryable codes that re-runs the failed action with the same inputs.
- While `navigator.onLine` is false an offline banner shows and model actions are disabled; it clears on `online`.
- Reloading the pane on the same item offers to restore the unsent instructions and preview; the restore is one click and dismissible.
- An input longer than the selected model's context window is truncated to fit with a visible notice saying how much was kept.
- With **Debug log** on in Settings, each model call logs its feature, model id, status, timing, and token counts to the console; the log never contains email text, prompt text, model output, or the key; with it off (the default) nothing is logged.
- Every Office.js write reports failure through the banner, start-up survives a client without Mailbox 1.5, and a quick second action never has its loading state hidden by the first.

**Adjacency:** list=not-applicable (no browsable records); document=applicable; settings=applicable; reporting=applicable; notifications=applicable; permissions=applicable @ D03 T03 §1; audit=applicable @ D03 T03 §5; exchange=not-applicable (nothing is imported or exported); reverse=applicable

## Implementation Order

| Order | Section | Deliverable                                  | Depends On             | Status |
| :---: | :-----: | -------------------------------------------- | ---------------------- | :----: |
|   1   |   §1    | Actionable errors with Retry                 | D02 T02 §1, D03 T01 §1 |  [ ]   |
|   2   |   §2    | Offline banner                               | §1                     |  [ ]   |
|   3   |   §3    | Draft recovery after a reload                | D03 T01 §5             |  [ ]   |
|   4   |   §4    | Context-length handling                      | D02 T01 §5, D02 T02 §1 |  [ ]   |
|   5   |   §5    | The debug log and response timing            | D03 T01 §5             |  [ ]   |
|   6   |   §6    | Office.js write callbacks and safe start-up  | D03 T01 §5             |  [ ]   |

---

## 1. Actionable Errors with Retry

The legacy `TODO.md` asked for "specific, actionable error messages (not generic 'Failed to generate')" and a "Retry button directly in error messages". The facade's `AiError` codes (`D02 T02 §1`) make the cause machine-readable; this section turns each code into one sentence the user can act on. It is also the add-in's refusal path when permissions are denied: a rejected key (authorization), a forbidden moderation refusal, and an out-of-credit account each get their own message instead of a hidden button.

**Fidelity:** Gemail task pane, error banner for each error code, with and without Retry -- docs/captures/taskpane/errors/. Banner position, text style, and button order match the spec.
**Design:** docs/design/mockup.md#error-banner, docs/design/taskpane.md#status-and-errors -- states: hidden, error, error-retryable -- themes: n/a (the banner uses existing status tokens and D06 T04 owns live theming) -- density: n/a (one density in a fixed-width task pane)
**Job:** A user who hits a failure can tell what went wrong and fix it or retry in one click. Consumer: the failed action, re-run by Retry.
**Treatment:** One message per `AiError` code from a single table, a **Retry** button for retryable codes, and a **Open Settings** link for key and credit codes. Cheaper substitute that fails the checkpoint: showing `err.message` from the provider, which is not a stable sentence and has no Retry.
**Chrome:** consume `showError` and `hideError` from `src/ui/status.ts` and the codes from `src/services/ai.ts`. Do not invent a second banner.
**Needs:** Outlook client (sideload)
**Requires:** display-session -- the per-code captures drive a sideloaded task pane

- [ ] Create `src/ui/error-messages.ts` exporting `messageFor(error)`, a table from every `AiError` code (as `D02 T02 §1` defines them: at least invalid key, insufficient credits, rate limited, context too long, moderation, provider error, network, timeout, cancelled, unknown) to one sentence naming the fix, with `retryable` and `settingsLink` flags, and a fallback for non-`AiError` values. Done when: a unit test asserts every exported code has an entry (iterating the enum) and no message contains the word "Gemini".
- [ ] Extend `showError(message, options)` in `src/ui/status.ts` with an optional `retry` callback rendered as a **Retry** button inside `#error-banner` and an optional **Open Settings** action that calls `switchTab('settings')`. Done when: a jsdom test asserts the Retry button appears only with a callback and clicking it hides the banner and calls it once.
- [ ] In every panel, pass the failed handler as `retry` for retryable codes, re-running with the same inputs through `runExclusive` when it exists (`D03 T02 §5`), or directly otherwise. Done when: `grep -rn "showError(" src/taskpane/panels` shows every call passing `messageFor(err)`.
- [ ] Report `CANCELLED` (the user pressed Stop) as no error at all. Done when: a jsdom test asserts the banner stays hidden for a cancelled call.
- [ ] Capture the banner for the invalid-key, rate-limited, and network codes in Outlook on the web into `docs/captures/taskpane/errors/` (forcing each with a wrong key, a mocked 429 through DevTools request blocking, and offline mode). Done when: three captures are committed.
- [ ] Hold the built surface to the approved mockup: render it (sideloaded, or in the jsdom harness for a component), compare it with the anchors on this section's `**Design:**` line in `docs/design/mockup.md` and their renders under `docs/design/mockup/renders/`, use only design tokens (`docs/design/tokens.json`) and registry icons (`iconSvg()` from `src/ui/icons.ts`), and commit a capture of the result under `docs/captures/taskpane/`. Done when: `python scripts/design-lint.py` exits 0 with the baseline no larger, every difference from the mockup is fixed or recorded as a `**Design deviation:**` naming its follow-up section, and the capture is committed. Cheaper substitute that fails: building from the prose alone, which the capture comparison at review refuses.
- [ ] Commit: `"resilience: one actionable message per error, with Retry"`

**Test checkpoint:** `npx jest src/ui/error-messages.test.ts src/ui/status.test.ts` passes the every-code, Retry, Open Settings, and cancelled cases; in the sideload a wrong key shows the invalid-key sentence with **Open Settings** and no Retry, and a blocked request shows the network sentence with **Retry**, which succeeds after unblocking. Cheaper substitute that fails: a generic "Something went wrong. Retry" for every code, which the every-code test (asserting distinct messages per code) fails.

## 2. Offline Banner

In an offline browser every model action fails after its timeout with a network error. The legacy `TODO.md` asked for an offline detection banner ("You're offline -- features unavailable"). The banner is immediate and the actions are disabled while it shows.

**Fidelity:** Gemail task pane, offline banner shown and cleared -- docs/captures/taskpane/offline/. Banner position and style match the error banner.
**Design:** docs/design/mockup.md#error-banner, docs/design/mockup.md#surfaces-the-mockup-does-not-draw, docs/design/taskpane.md#status-and-errors -- states: online, offline -- themes: n/a (existing status tokens; D06 T04 owns live theming) -- density: n/a (one density in a fixed-width task pane)
**Job:** A user who is offline sees it before clicking and knows the actions will work again when the connection returns. Consumer: none: this surface is the consumer.
**Treatment:** A persistent banner driven by `online` and `offline` events, disabling every model action while shown. Cheaper substitute that fails the checkpoint: showing the network error only after a failed request, which leaves the actions enabled.
**Chrome:** consume `src/ui/status.ts` and `src/ui/actions.ts`. Do not invent a second banner element.
**Needs:** Outlook client (sideload)
**Requires:** display-session -- the offline toggle is driven in DevTools of a sideloaded task pane

- [ ] Add `initConnectivity()` in `src/ui/connectivity.ts`: on start and on each `online` and `offline` event, show or hide an offline notice ("You're offline. Gemail will work again when your connection returns.") above the panel, and toggle a `data-offline` attribute on `#app-body`. Done when: a jsdom test dispatching `offline` then `online` asserts the notice shows then hides.
- [ ] Disable every model-action button while `data-offline` is set, restoring each to its prior state on `online`. Done when: a jsdom test asserts `#btn-generate` is disabled offline and re-enabled online, and a button disabled for another reason stays disabled.
- [ ] Toggle offline in DevTools on a sideloaded pane in Outlook on the web and capture both states into `docs/captures/taskpane/offline/`. Done when: two captures are committed.
- [ ] Hold the built surface to the approved mockup: render it (sideloaded, or in the jsdom harness for a component), compare it with the anchors on this section's `**Design:**` line in `docs/design/mockup.md` and their renders under `docs/design/mockup/renders/`, use only design tokens (`docs/design/tokens.json`) and registry icons (`iconSvg()` from `src/ui/icons.ts`), and commit a capture of the result under `docs/captures/taskpane/`. Done when: `python scripts/design-lint.py` exits 0 with the baseline no larger, every difference from the mockup is fixed or recorded as a `**Design deviation:**` naming its follow-up section, and the capture is committed. Cheaper substitute that fails: building from the prose alone, which the capture comparison at review refuses.
- [ ] Commit: `"resilience: an offline banner that disables model actions"`

**Test checkpoint:** `npx jest src/ui/connectivity.test.ts` passes the show-hide and prior-state cases; in the sideload, DevTools offline shows the banner and disables Generate within one second, and going online clears it. Cheaper substitute that fails: checking `navigator.onLine` once at start-up, which the event-driven test fails.

## 3. Draft Recovery After a Reload

The task pane reloads when Outlook recycles it, when the user switches items with the pane unpinned, or after a crash, and everything typed into the instruction boxes and edited in the previews is lost. The legacy `TODO.md` asked to "save draft-in-progress to localStorage (recover after crash/reload)". Recovery offers, it never overwrites: the user chooses to restore.

**Fidelity:** Gemail task pane, the restore prompt above the Draft and Reply panels -- docs/captures/taskpane/recovery/. Prompt style matches the dialog rules; the panels behind it are unchanged.
**Design:** docs/design/mockup.md#surfaces-the-mockup-does-not-draw, docs/design/mockup.md#reply-form, docs/design/taskpane.md#dialogs, docs/design/taskpane.md#feature-panel -- states: none-saved, restore-offered, restored, dismissed -- themes: n/a (existing tokens; D06 T04 owns live theming) -- density: n/a (one density in a fixed-width task pane)
**Job:** A user whose pane reloaded can get back what they had typed and generated for this message in one click. Consumer: the Draft and Reply panels, whose inputs and previews are refilled.
**Treatment:** Debounced saves of instructions, selects, and preview text keyed by item, and an inline restore prompt with **Restore** and **Dismiss**. Cheaper substitute that fails the checkpoint: silently refilling the fields, which overwrites what the user started typing after the reload.
**Chrome:** consume `src/ui/dom.ts` and the dialog pattern of the spec. Do not invent a second storage wrapper: persist through one `src/services/draft-store.ts`.
**Needs:** Outlook client (sideload)
**Requires:** display-session -- the reload proof drives a sideloaded task pane

- [ ] Create `src/services/draft-store.ts` exporting `saveDraft(key, state)`, `loadDraft(key)`, and `clearDraft(key)`, storing JSON under `gemail_draft:<key>` in `localStorage` with a timestamp, keeping at most 20 entries (oldest evicted) and dropping entries older than 7 days on load, and surviving a malformed stored value by discarding it. Done when: unit tests cover save and load, eviction at 21 entries, expiry, and malformed JSON.
- [ ] Key the draft by `Office.context.mailbox.item.itemId` in read mode and by the conversation id plus "compose" in compose mode (new messages without either use "new-compose"). Done when: a test with the Office.js mock asserts the key for each mode.
- [ ] In the Draft and Reply panels, save instructions, tone, length, language, goal, and preview text 500 ms after the last input, and clear the entry when the user inserts or copies the result. Done when: a jsdom test types, advances fake timers, and asserts one save; inserting asserts a clear.
- [ ] On panel init, if an entry exists and the fields are empty, show the restore prompt; **Restore** refills the fields and preview, **Dismiss** clears the entry. Done when: a jsdom test asserts both paths and that nothing is refilled without a click.
- [ ] Type an instruction, generate, edit the preview, reload the pane in Outlook on the web, and restore. Done when: the restored text equals the pre-reload text and captures of the prompt and the restored state are committed under `docs/captures/taskpane/recovery/`.
- [ ] Hold the built surface to the approved mockup: render it (sideloaded, or in the jsdom harness for a component), compare it with the anchors on this section's `**Design:**` line in `docs/design/mockup.md` and their renders under `docs/design/mockup/renders/`, use only design tokens (`docs/design/tokens.json`) and registry icons (`iconSvg()` from `src/ui/icons.ts`), and commit a capture of the result under `docs/captures/taskpane/`. Done when: `python scripts/design-lint.py` exits 0 with the baseline no larger, every difference from the mockup is fixed or recorded as a `**Design deviation:**` naming its follow-up section, and the capture is committed. Cheaper substitute that fails: building from the prose alone, which the capture comparison at review refuses.
- [ ] Commit: `"resilience: offer to restore a draft after the pane reloads"`

**Test checkpoint:** `npx jest src/services/draft-store.test.ts src/taskpane/panels/draft.test.ts` passes the storage, keying, debounce, clear-on-insert, restore, and dismiss cases; the sideload reload restores the exact instruction and edited preview text. Cheaper substitute that fails: saving only on `beforeunload`, which the pane does not reliably receive when Outlook recycles it and which the debounce test does not exercise.

## 4. Context-Length Handling

Inputs are truncated to fixed budgets (6000 or 8000 tokens) that ignore the model the user picked, and Translate and Improve are not truncated at all, so a long email either wastes a large model's window or fails a small one with a provider error. The legacy `TODO.md` asked to "handle token limit exceeded gracefully (auto-truncate and inform user)". The catalogue (`D02 T01 §5`) knows each model's `context_length`.

- [ ] Add `inputBudget(modelId, maxOutputTokens)` to `src/services/ai.ts`: the model's `context_length` from the catalogue minus `maxOutputTokens` minus a fixed prompt allowance, falling back to 8000 tokens when the model is not in the catalogue. Done when: unit tests cover a known model, an unknown model, and a model whose window is smaller than the output budget (which returns a minimum and flags it).
- [ ] Replace the three `MAX_CONTENT_TOKENS` constants and add truncation to `translate.ts` and `improve-writing.ts`, all through `truncateContext(text, inputBudget(...))`, returning whether truncation happened and the kept percentage. Done when: `grep -rn "MAX_CONTENT_TOKENS" src` prints nothing and a test per feature asserts truncation of an over-long input.
- [ ] Show a notice in the result card when truncation happened ("This email was too long for the selected model; Gemail used the first 62 percent."). Done when: a jsdom test asserts the notice text with the percentage.
- [ ] Map a provider `CONTEXT_TOO_LONG` error (our estimate was low) to one automatic retry at 75 percent of the previous input, then to the actionable error of §1. Done when: a test with the facade mocked to fail once with `CONTEXT_TOO_LONG` asserts a second call with a shorter input.
- [ ] Commit: `"resilience: fit long emails to the selected model's context window"`

**Test checkpoint:** `npx jest src/services/ai.test.ts src/features` passes the budget, per-feature truncation, and retry-at-75-percent cases, using a replayed catalogue fixture of `D02 T01 §1` for `context_length`; `grep -rn "MAX_CONTENT_TOKENS" src` prints nothing. Cheaper substitute that fails: raising the fixed constants, which still ignores the selected model and fails the small-window test.

## 5. The Debug Log and Response Timing

The legacy `TODO.md` asked for an optional debug console and response-time logging. Today the only logging is three unconditional `console.log` calls, two of which print model output derived from the user's email, which `PRIVACY.md` says does not happen. One logger, off by default, logs metadata only. It is the audit trail of model calls: one history entry per call and per write into a message, never content.

**Fidelity:** Gemail task pane, Settings panel with the Debug log toggle -- docs/captures/taskpane/settings-debug/. The toggle follows the settings panel's control style and order.
**Design:** docs/design/mockup.md#settings, docs/design/mockup.md#surfaces-the-mockup-does-not-draw, docs/design/taskpane.md#settings-panel -- states: off, on -- themes: n/a (existing tokens; D06 T04 owns live theming) -- density: n/a (one density in a fixed-width task pane)
**Job:** A user or developer diagnosing a problem can turn on a log of what Gemail did and how long it took, without the log exposing any email. Consumer: `src/services/log.ts`, which reads the setting before every write.
**Treatment:** A `debugLog` boolean setting (default false) and a logger whose entries are a fixed set of metadata fields. Cheaper substitute that fails the checkpoint: wrapping the existing `console.log` calls in an `if`, which still prints model output when on.
**Chrome:** consume the settings service (`src/features/settings.ts`) and the Settings panel module. Do not invent a second settings writer.
**Needs:** Outlook client (sideload)
**Requires:** display-session -- the console proof reads DevTools of a sideloaded task pane

- [ ] Create `src/services/log.ts` exporting `logEvent(event)` where `event` is `{ feature, action, model?, status, ms?, promptTokens?, completionTokens?, code? }` and nothing else, writing one `console.info("[Gemail]", ...)` line only when the `debugLog` setting is true. Done when: a unit test asserts no output with the setting off and one line with it on, and a type test (`// @ts-expect-error`) proves a `text` field is rejected.
- [ ] Log one event per model call from the facade (`src/services/ai.ts`) with timing from `performance.now()` and usage from the response, and one per Office.js write outcome from §6. Done when: a facade test with the setting on asserts the event fields for one call.
- [ ] Remove the three `console.log` calls in `taskpane.ts` (now in the panels) and add an ESLint `no-console` rule allowing only `src/services/log.ts`. Done when: `grep -rn "console.log" src` prints nothing and `npm run lint` passes.
- [ ] Add the `debugLog` setting (default `false`) to the settings service and a **Debug log** checkbox to `#settings-section` with the help text "Logs timings and errors to the browser console. Never logs email content or your key." Done when: a settings test asserts the default and round trip, and a jsdom test asserts the checkbox reflects the saved value.
- [ ] With the log on, generate a reply in Outlook on the web and search the console output for the email subject, a phrase from the body, the generated text, and the key prefix `sk-or-`. Done when: the four searches return nothing, quoted in the commit body.
- [ ] Hold the built surface to the approved mockup: render it (sideloaded, or in the jsdom harness for a component), compare it with the anchors on this section's `**Design:**` line in `docs/design/mockup.md` and their renders under `docs/design/mockup/renders/`, use only design tokens (`docs/design/tokens.json`) and registry icons (`iconSvg()` from `src/ui/icons.ts`), and commit a capture of the result under `docs/captures/taskpane/`. Done when: `python scripts/design-lint.py` exits 0 with the baseline no larger, every difference from the mockup is fixed or recorded as a `**Design deviation:**` naming its follow-up section, and the capture is committed. Cheaper substitute that fails: building from the prose alone, which the capture comparison at review refuses.
- [ ] Commit: `"resilience: an opt-in debug log that never logs content"`

**Test checkpoint:** `npx jest src/services/log.test.ts src/services/ai.test.ts` passes the off, on, field-set, and facade-event cases; `grep -rn "console.log" src` prints nothing; the sideload console search for subject, body phrase, output, and `sk-or-` finds nothing while the timing line is present. Cheaper substitute that fails: logging the whole response object, which the console search for the generated text catches.

## 6. Office.js Write Callbacks and Safe Start-Up

Three writes into the user's message (`body.prependAsync` in Draft and Reply, `subject.setAsync` in Draft) pass no callback, so a refused write (read mode, a locked item, a size limit) is silent and the user believes the text was inserted. Start-up registers `ItemChanged` without checking Mailbox 1.5, and if that throws the rest of the wiring never runs. The loading overlay's delayed hide can hide a newer overlay.

- [ ] Add `asyncCall(fn)` to `src/services/outlook.ts`: it wraps an Office.js `*Async` call in a promise that resolves on `Office.AsyncResultStatus.Succeeded` and rejects with the `asyncResult.error` otherwise. Done when: a test with the Office.js mock asserts resolve on success and reject carrying `error.code` on failure.
- [ ] Route the `prependAsync` calls in `src/features/draft-email.ts` and `src/features/draft-reply.ts` and the `subject.setAsync` call through `asyncCall`, and report a rejection through `showError` with the §1 message for a write failure; the preview keeps its text so nothing is lost. Done when: a test with the mock failing `prependAsync` asserts the banner and that the preview is unchanged.
- [ ] Guard the `ItemChanged` registration with `Office.context.requirements.isSetSupported("Mailbox", "1.5")` and wrap it so a failure is logged (§5) and start-up continues. Done when: a jsdom start-up test with `isSetSupported` returning false asserts every panel still initializes.
- [ ] Replace the delayed hide in `hideLoading` with a generation counter so a hide scheduled by an earlier call never hides an overlay a later `showLoading` opened. Done when: a jsdom test with fake timers calls show, hide, show within 350 ms and asserts the overlay is visible after the timers run.
- [ ] Commit: `"resilience: report every Office.js write and start safely"`

**Test checkpoint:** `npx jest src/services/outlook.test.ts src/ui/status.test.ts src/taskpane` passes the async-wrapper, failed-prepend, unsupported-requirement-set, and overlay-race cases; `grep -rn "prependAsync(\|subject.setAsync(" src/features` shows each call inside `asyncCall`. Cheaper substitute that fails: adding empty callbacks to satisfy the grep, which the failed-prepend test (asserting the banner) fails.

## Verification

- [ ] `pwsh scripts/check-all.ps1` -- exits 0: production build, typecheck, lint, tests, manifest, TODO gates green
- [ ] `npx jest --ci` exits 0 with `src/ui/error-messages.test.ts`, `src/ui/connectivity.test.ts`, `src/services/draft-store.test.ts`, `src/services/log.test.ts`, and `src/services/outlook.test.ts` reporting
- [ ] A sideload smoke in new Outlook and Outlook on the web forces a bad key, offline, a reload mid-draft, and an over-long email, and each shows the behavior of its section with `0` uncaught console errors
