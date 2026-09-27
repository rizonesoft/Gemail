---
schema_version: 1
id: provider-cutover
domain: 02-openrouter
status: draft
title: "TODO-02 -- Provider Cutover"
depends_on: []
---

# TODO-02 -- Provider Cutover

> **Goal:** Every model call in Gemail goes to OpenRouter under the user's own key, through one provider-neutral facade (`src/services/ai.ts`) that features, the task pane, and the ribbon commands share. The settings speak OpenRouter (key format, model ids, a fast model, the privacy-routing toggle), existing users are moved over without losing anything but a Google key that can no longer work, the model picker lists the live OpenRouter catalogue, Test Connection checks the key without spending credit, `@google/genai` and every Gemini string leave the tree, and each feature's token budget is re-derived so reasoning models do not return empty replies.

> [!IMPORTANT]
> **Current state (verified 2026-09-27):** Twelve call sites in `src/` call `generateText` or `generateJson` from `src/services/gemini.ts`: `src/commands/commands.ts` line 72; `src/features/draft-email.ts` lines 62 and 111; `src/features/draft-reply.ts` lines 122 and 170; `src/features/improve-writing.ts` line 78; `src/features/extract-actions.ts` line 65, `src/features/summarize-thread.ts` line 89, and `src/features/translate.ts` line 77 (the last three force `FAST_MODEL`, overriding the user's model); and `src/taskpane/taskpane.ts` lines 210 (`scoreEmail`, `generateJson` with a `Type` schema and a hard-coded `gemini-2.5-flash`), 611 (suggested replies), and 1363 (Test Connection). A thirteenth is `scripts/test-gemini.ts`. `src/commands/commands.ts` never calls `initGeminiClient`, so every ribbon command fails with "Gemini client not initialised". `src/features/settings.ts` line 10 imports `initGeminiClient` while `gemini.ts` imports `getSetting`, a circular import. `isValidApiKeyFormat` in `taskpane.ts` accepts only Google keys (`/^AIza[0-9A-Za-z_-]{35}$/`). Test Connection calls `initGeminiClient` with the unsaved key (line 1361), replacing the live client. The model `<select id="settings-model">` in `taskpane.html` hard-codes six `gemini-*` options, and the settings panel names Gemini in its key label, placeholder, the Google AI Studio link, the model label, and the model hint. `.env` holds `GEMINI_API_KEY` for `scripts/test-gemini.ts` only; webpack never reads it. There is no `src/services/ai.ts` and no `scripts/test-openrouter.ts`.
<!-- claim: count "FAST_MODEL" src/*/*.ts = 7 -->
<!-- claim: count "AIza" src/taskpane/taskpane.ts = 4 -->
<!-- claim: count "gemini-" src/taskpane/taskpane.html = 6 -->
<!-- claim: count "aistudio.google.com" src/taskpane/taskpane.html = 1 -->
<!-- claim: count "initGeminiClient" src/features/settings.ts = 2 -->
<!-- claim: exists scripts/test-gemini.ts -->
<!-- claim: absent src/services/ai.ts -->
<!-- claim: absent scripts/test-openrouter.ts -->

## Inputs

- [`src/services/gemini.ts`](../../src/services/gemini.ts), [`src/services/gemini.test.ts`](../../src/services/gemini.test.ts), [`scripts/test-gemini.ts`](../../scripts/test-gemini.ts) -- the code §6 removes
- [`src/features/settings.ts`](../../src/features/settings.ts) -- the settings shape, the circular import §1 breaks, and the migration §3 extends
- [`src/taskpane/taskpane.ts`](../../src/taskpane/taskpane.ts), [`src/taskpane/taskpane.html`](../../src/taskpane/taskpane.html) -- `scoreEmail`, suggested replies, Test Connection, `isValidApiKeyFormat`, and the settings panel markup §2, §4, §5, §7, and §9 change
- [`src/commands/commands.ts`](../../src/commands/commands.ts) -- the ribbon commands that never initialised a client
- [`docs/design/taskpane.md`](../../docs/design/taskpane.md) -- the Settings panel, Status and errors, and Loading and streaming rules
- OpenRouter provider routing (https://openrouter.ai/docs/guides/routing/provider-routing) -- `provider.data_collection` (`"allow"` default, `"deny"`), `require_parameters`
- OpenRouter reasoning tokens (https://openrouter.ai/docs/guides/reasoning-tokens) -- `reasoning.effort` (`"none"` to `"max"`), `reasoning.max_tokens`, `reasoning.exclude`, and that reasoning tokens count against `max_tokens`
- OpenRouter quickstart and keys (https://openrouter.ai/docs/quickstart) -- where users create a key (https://openrouter.ai/keys)
- -> XREF: D01 T01 §5 -- the `gemail_settings` key and `migrateStorageKey()` §3 builds on; D01 T01 §6 renamed the documents §7 now rewrites for the provider
- -> XREF: D02 T01 §2 -- `chat()`, `streamChat()` (D02 T01 §3), and `chatJson()` (D02 T01 §4) behind the facade; `listModels()` (D02 T01 §5) feeds §4 and `keyInfo()` (D02 T01 §6) feeds §5
- -> XREF: D03 T02 §4 -- streaming output consumes `streamText()` from §1; D03 T02 §7 pre-warms the catalogue §4 reads; D03 T02 §8 changes the score call §2 repoints
- -> XREF: D03 T03 §1 -- one actionable message per `AiErrorCode` §1 defines; D03 T03 §4 truncates to the context length through the facade
- -> XREF: D04 T01 §2 -- prompt-injection fencing wraps the prompts §2 routes; D04 T01 §4 moves the key §3 validates to its own device-only key; D04 T01 §5 rate-limits inside the facade; D04 T01 §7 documents the data flow §7 writes
- -> XREF: D05 T01 §4 -- feature tests mock the facade §2 routes every feature through; D05 T01 §5 tests the ribbon commands §2 fixes
- -> XREF: D05 T03 §4 -- rules reach the refine prompts §2 repoints
- -> XREF: D06 T01 §2 -- creativity and length settings feed the options §2 standardizes; D06 T01 §5 shows model info from the picker §4 builds
- -> XREF: D06 T02 §1 -- custom prompts run through the facade §2 establishes
- -> XREF: D06 T03 §2 -- attachment content parts ride the facade §1; D06 T03 §3 uses `generateJson` as §2 leaves it

## Outcome

- `grep -rn "@google/genai\|services/gemini\|GEMINI_API_KEY\|initGeminiClient" src scripts package.json` prints nothing, and `npm ls @google/genai` prints `(empty)`.
- Every generating feature, suggested replies, scoring, Test Connection, and all four ribbon commands work against OpenRouter in a sideloaded Outlook on the web and new Outlook with only the user's key in Settings.
- A profile that stored a Google key opens with the key field empty and a one-time notice explaining why; every other setting survives; a stored `gemini-*` model id becomes the matching `google/...` catalogue id or the default.
- The model picker lists the live OpenRouter catalogue with the recorded defaults first and still works offline from the cache or a built-in short list.
- No feature returns an empty reply because reasoning consumed its budget: each feature's `max_tokens` and `reasoning` settings are measured and recorded.

**Adjacency:** list=applicable; document=not-applicable (writes into the message are owned by D05 T03 §1 and the insert paths; this file changes which provider produces the text); settings=applicable; reporting=not-applicable (cost and usage reporting over model calls is owned by the settings-upgrades and usage-stats features in todo/06-features); notifications=applicable; permissions=applicable; audit=applicable @ D03 T03 §5; exchange=not-applicable (nothing imported or exported); reverse=applicable

**Adjacency rationale:** The list is the model catalogue in the picker (§4). Settings are the key, model, fast model, and privacy toggle (§3, §9). Notifications are the one-time key notice and the Test Connection result (§3, §5). Permissions are the refusals the provider returns (invalid key, no credit, moderation, no provider under the privacy filter), each surfaced by the error codes of §1 and messaged by D03 T03 §1. Reverse is clearing the key and resetting the model to the recorded default.

## Implementation Order

| Order | Section | Deliverable                                          | Depends On                         | Status |
| :---: | :-----: | ---------------------------------------------------- | ---------------------------------- | :----: |
|   1   |   §1    | A provider-neutral AI facade                         | D02 T01 §2, D02 T01 §3, D02 T01 §4 |  [ ]   |
|   2   |   §2    | Repoint every caller                                 | §1                                 |  [ ]   |
|   3   |   §3    | OpenRouter settings and the Gemini key migration     | §2, D01 T01 §5                     |  [ ]   |
|   4   |   §4    | The model picker                                     | §3, D02 T01 §5                     |  [ ]   |
|   5   |   §5    | Test Connection through the key endpoint             | §3, D02 T01 §6                     |  [ ]   |
|   6   |   §6    | Remove Google Gemini                                 | §2                                 |  [ ]   |
|   7   |   §7    | Provider copy in the UI and docs                     | §6, D01 T01 §6                     |  [ ]   |
|   8   |   §8    | Reasoning and token budgets                          | §2                                 |  [ ]   |
|   9   |   §9    | Privacy routing setting                              | §3                                 |  [ ]   |

---

## 1. A Provider-Neutral AI Facade

Features should not know which provider answers them. The facade keeps today's call shape (`generateText(prompt, options)`, `generateJson(prompt, options)`), adds `streamText()`, maps OpenRouter's errors to one `AiError` type the UI can message, and reads the key and model from settings at call time. Reading at call time is what fixes the ribbon: `commands.html` is a separate runtime that never ran the task pane's start-up, so a client created at start-up never existed there.

- [ ] Create `src/services/ai.ts` exporting `generateText(prompt, { model, temperature, maxTokens, systemInstruction, signal })`, `generateJson<T>(prompt, { schema, name, model, temperature, maxTokens, systemInstruction, signal })`, and `streamText(prompt, options)` (an `AsyncGenerator` of text deltas that returns the finish reason and usage), each building `messages` (a `system` message from `systemInstruction`, then the `user` prompt) and calling `chat()`, `chatJson()`, or `streamChat()` from `src/services/openrouter.ts`. Done when: `npx tsc --noEmit` exits `0` and `src/services/ai.test.ts` asserts the `messages` array for a call with and without `systemInstruction`.
- [ ] Define `AiErrorCode` (`NO_API_KEY`, `INVALID_API_KEY`, `INSUFFICIENT_CREDITS`, `RATE_LIMITED`, `MODERATION`, `CONTEXT_TOO_LONG`, `MODEL_UNAVAILABLE`, `NO_PROVIDER`, `TIMEOUT`, `CANCELLED`, `NETWORK`, `TRUNCATED`, `CONTENT_FILTERED`, `EMPTY_RESPONSE`, `INVALID_JSON`, `UNKNOWN`) and `AiError` (`code`, `retryable`, `status`, `cause`), and `toAiError(err)` mapping every `OpenRouterError` code one to one. Done when: a table-driven test covers every `OpenRouterError` code and a non-`OpenRouterError` throw (maps to `UNKNOWN`).
- [ ] Resolve the key and model per call: the key from `getApiKey()` in `src/features/settings.ts` (a missing key raises `NO_API_KEY` before any request), the model from `options.model ?? getSetting("defaultModel") ?? DEFAULT_MODEL`. Done when: tests named `no key raises NO_API_KEY without fetching` and `options.model overrides the setting` pass.
- [ ] Break the circular import: delete the `initGeminiClient` import and the re-initialise block from `saveSettings()` in `src/features/settings.ts`, so `settings.ts` imports nothing from `src/services/`. Done when: `grep -c "services/" src/features/settings.ts` prints `0` and `npx madge --circular --extensions ts src` (run once through `npx`, not added as a dependency) reports no cycle through `settings.ts`.
- [ ] Commit: `"ai: a provider-neutral facade over the OpenRouter client"`

**Test checkpoint:** `npx jest src/services/ai.test.ts` passes, with `fetch` mocked to replay `src/services/__fixtures__/openrouter/chat-completion.json` (the facade returns the fixture's content), `chat-stream.sse` (`streamText` yields the recorded deltas), and `error-402.json` (`AiError` with `INSUFFICIENT_CREDITS`, not retryable); `madge` reports no cycle through `settings.ts`. Cheaper substitute that fails: re-exporting `openrouter.ts` functions under the old names, which leaves callers catching `OpenRouterError` codes and fails the table-driven mapping test.

## 2. Repoint Every Caller

Every call site moves to the facade in one section, so there is never a build with half the features on Gemini. The options each call passes today (temperature, token budget, model) are carried over as they are; §8 re-derives the budgets afterwards.

- [ ] Change the import in `src/features/draft-email.ts`, `draft-reply.ts`, `improve-writing.ts`, `extract-actions.ts`, `summarize-thread.ts`, and `translate.ts` to `../services/ai`, renaming `maxOutputTokens` to `maxTokens` at each call. Done when: `grep -rn "services/gemini" src/features` prints nothing and the feature modules type-check.
- [ ] Replace `FAST_MODEL` with a `fastModel` setting read through `getSetting("fastModel")` in the three features that forced it, so the user's choice is respected (a fast model is still used for utility work by default, and the user can change it in §4). Done when: `grep -rn FAST_MODEL src` prints nothing and a test asserts `summarizeThread` sends the stored `fastModel`.
- [ ] Rewrite `scoreEmail` in `src/taskpane/taskpane.ts`: replace the `Type.OBJECT` / `Type.NUMBER` schema with a JSON Schema object (`type: "object"`, four `number` properties with `minimum: 0` and `maximum: 100`, all `required`, `additionalProperties: false`), drop the hard-coded `gemini-2.5-flash` for `getSetting("fastModel")`, and pass `supportsStructuredOutputs` from the cached catalogue. Done when: `grep -c "Type\." src/taskpane/taskpane.ts` prints `0` and a test feeding `chat-json-schema.json`-shaped content returns four numbers.
- [ ] Repoint suggested replies (`taskpane.ts` line 611) and `src/commands/commands.ts` line 72 to the facade; the ribbon commands now work because the facade reads the key per call. Done when: in a sideloaded compose window with a saved key, Fix Grammar & Spelling replaces the selected text and shows the Gemail notification.
- [ ] Replace the `testErr?.code === 'CONTENT_FILTERED'` string comparison in Test Connection with an `AiErrorCode` comparison (§5 rewrites the flow; this keeps it compiling). Done when: `grep -c "'CONTENT_FILTERED'" src/taskpane/taskpane.ts` prints `0`.
- [ ] Commit: `"ai: every feature, the task pane, and the ribbon call OpenRouter"`

**Needs:** Outlook client (sideload)
**Requires:** display-session -- the ribbon check drives a sideloaded compose window, which needs a window station

**Test checkpoint:** `grep -rn "services/gemini" src --include=*.ts | grep -v "gemini.test.ts"` prints nothing; `npx jest --ci` passes with the facade mocked in the feature tests; in Outlook on the web with the dev build and a real OpenRouter key, Draft, Reply, Summarize, Improve, Extract, Translate, suggested replies, scoring, and one ribbon command each produce a result, recorded in the commit body as a nine-line pass list. Cheaper substitute that fails: repointing only the six feature modules, which leaves the ribbon on the uninitialised Gemini client and fails the ribbon line of the pass list.

## 3. OpenRouter Settings and the Gemini Key Migration

A Google key cannot authenticate to OpenRouter, so it must not sit in the key field looking valid. The migration clears it once, tells the user why in plain words, and keeps everything else. Model ids change shape (`gemini-3-flash-preview` becomes an OpenRouter id such as `google/gemini-3-flash-preview`), and the defaults are chosen from the live catalogue on the day this section ships (operator decision: "Decide at build time").

- [ ] Replace `isValidApiKeyFormat` in `src/taskpane/taskpane.ts` with `isOpenRouterKey(key)` in `src/features/settings.ts`: `^sk-or-(v1-)?[A-Za-z0-9_-]{20,}$`, checked against the format of a key created at https://openrouter.ai/keys on the day, with the example (redacted) in the test. Done when: tests accept a redacted real-format key and reject an `AIza...` key and an empty string.
- [ ] Add a settings schema version: `GemailSettings.schemaVersion = 2`, `fastModel`, and `notices: { geminiKeyRemoved?: boolean }`; `migrateToV2()` in `loadSettings()` clears an `apiKey` matching `/^AIza/` and sets `notices.geminiKeyRemoved = true`, maps a stored `gemini-*` `defaultModel` to `google/<same id>` when the cached catalogue has it and to `DEFAULT_MODEL` otherwise, and writes back through `saveSettings()` with a readback. Done when: tests named `clears a Google key and sets the notice`, `maps gemini-3-flash-preview`, `falls back to DEFAULT_MODEL for an unknown id`, and `leaves an OpenRouter key alone` pass.
- [ ] Show the notice once in the error banner area as information: "Gemail now uses OpenRouter. Your Google Gemini key can't be used; add an OpenRouter key in Settings." with a link to https://openrouter.ai/keys; dismissing it clears `notices.geminiKeyRemoved`. Done when: a jsdom test asserts the notice renders once and not after dismissal. Cheaper substitute: clearing the key silently, which the test catches because no notice renders.
- [ ] Choose the defaults from the live catalogue (`listModels()` with the development key): `DEFAULT_MODEL` (the best quality-to-price general model with `structured_outputs` support) and `DEFAULT_FAST_MODEL` (the cheapest fast model with at least a 100k context and `structured_outputs`), plus `FALLBACK_MODELS` (six to eight ids across at least three providers for the offline picker), in a new `src/services/models.ts`. Done when: the file carries a comment with the date, the catalogue prices quoted for each chosen id, and the reason, and the commit body repeats them for the operator.
- [ ] Commit: `"settings: OpenRouter key format, v2 migration, and catalogue defaults"`

**Needs:** OpenRouter API key (live test)

**Test checkpoint:** `npx jest src/features/settings.test.ts` passes the new named tests alongside the D01 T01 §5 migration tests; a browser profile seeded from a committed fixture of 1.3.2 storage (with an `AIza...` key and `gemini-3-flash-preview`) opens a sideloaded dev build with an empty key field, the notice shown once, the tone, rules, and templates intact, and the model set to its `google/...` id. Cheaper substitute that fails: keeping the Google key and letting the first request fail with 401, which the seeded-profile check catches because the key field is not empty and no notice appears.

## 4. The Model Picker

The picker replaces six hard-coded Gemini options with the live OpenRouter catalogue. Hundreds of models make a plain `<select>` unusable, so the picker leads with the recorded defaults, groups by provider, filters as the user types, and shows what a user needs to choose: context window and price.

**Fidelity:** Gemail Settings panel, Model field -- docs/captures/taskpane/settings-model/. Field order and labels match the Settings panel rule; the picker sits where `#settings-model` sits today.
**Design:** docs/design/taskpane.md#settings-panel, docs/design/taskpane.md#form-controls -- states: loading, loaded, filtered, empty, offline, error -- themes: n/a (the theme work is owned by the appearance TODO in todo/06-features) -- density: n/a (one density in a fixed-width task pane)
**Job:** An Outlook user can pick which OpenRouter model writes their email, knowing its context size and price. Consumer: `getSetting("defaultModel")` and `getSetting("fastModel")` in `src/services/ai.ts`.
**Treatment:** a filterable list with "Recommended" (the two defaults) first, then provider groups, each row showing name, context (for example "128k"), and price per million input and output tokens. Cheaper substitute that fails the checkpoint: filling the existing `<select>` with every catalogue id, which cannot be filtered and shows no price.
**Chrome:** consume `listModels()` and its cache, the `aic-input` and `aic-select` styles, and the existing `#settings-saved-msg` confirmation. Do not invent a second settings writer.
**Needs:** Outlook client (sideload)
**Requires:** display-session -- the checkpoint drives the picker in a sideloaded task pane and captures it

- [ ] Replace the `<select id="settings-model">` block in `src/taskpane/taskpane.html` with a labelled text input (`#settings-model-filter`), a list container (`#settings-model-list`, `role="listbox"`), and a line showing the selected model (`#settings-model-selected`); add a second, identical control for the fast model (`#settings-fast-model-*`). Done when: `grep -c "gemini-" src/taskpane/taskpane.html` prints `0`.
- [ ] Write `src/taskpane/model-picker.ts` with `renderModelPicker(container, models, selectedId, onSelect)`: Recommended group from `DEFAULT_MODEL` and `DEFAULT_FAST_MODEL`, then provider groups (the prefix before `/`), filter on name and id, rows showing context as `Nk` and price as `$X / $Y per M tokens`, rendered with `textContent` only. Done when: jsdom tests assert group order, filtering to zero rows shows "No models match", and a model name containing `<b>` renders as text.
- [ ] Load the catalogue when the Settings tab opens: show "Loading models..." then the list; on failure show the cached list with "Showing saved list (offline)", and with no cache the `FALLBACK_MODELS` from §3. Done when: jsdom tests cover loaded, offline-with-cache, and offline-without-cache.
- [ ] Keyboard: arrow keys move through rows, Enter selects, the selected row carries `aria-selected="true"`. Done when: a jsdom test drives ArrowDown twice and Enter and asserts the selection and the saved setting. Source: WAI-ARIA listbox pattern (https://www.w3.org/WAI/ARIA/apg/patterns/listbox/).
- [ ] Save writes `defaultModel` and `fastModel` through `saveSettings()` and reads them back into the selected lines. Done when: after Save and a pane reload, both selected lines show the saved models.
- [ ] Sideload, capture the picker loaded, filtered, and offline into `docs/captures/taskpane/settings-model/`. Done when: three captures exist.
- [ ] Commit: `"settings: a model picker over the OpenRouter catalogue"`

**Test checkpoint:** `npx jest src/taskpane/model-picker.test.ts` passes the named cases; in a sideloaded pane, typing "claude" filters to Anthropic rows only, choosing one and saving survives a reload, and with the network disabled in the browser's developer tools the picker shows the cached list with the offline line. Cheaper substitute that fails: a fixed list of ids bundled into the page, which the offline-without-cache case matches but the loaded case fails because rows show no live price.

## 5. Test Connection Through the Key Endpoint

Test Connection today spends a request ("Say hello in one word.") and replaces the live client with whatever is typed, saved or not. The key endpoint answers the question without spending anything and tells the user how much credit is left.

**Fidelity:** Gemail Settings panel, API key row and `#test-connection-result` -- docs/captures/taskpane/test-connection/. Message wording follows the Status and errors rule.
**Design:** docs/design/taskpane.md#settings-panel, docs/design/taskpane.md#status-and-errors -- states: idle, checking, valid, valid-free-tier, invalid, offline -- themes: n/a (the theme work is owned by the appearance TODO in todo/06-features) -- density: n/a (one density in a fixed-width task pane)
**Job:** An Outlook user can check that the key they typed works, and see its remaining credit, before saving it. Consumer: none: this surface is the consumer.
**Treatment:** "Connected. Key 'label': $X.XX of $Y left." or "Connected (free tier)." on success; the §1 message for the failure code otherwise; the saved settings untouched either way. Cheaper substitute that fails the checkpoint: a one-token completion, which spends credit and cannot report the remaining limit.
**Chrome:** consume `keyInfo()` through a facade function `checkKey(key)` and the existing `#test-connection-result` element. Do not invent a second key-validation path.
**Needs:** Outlook client (sideload)
**Requires:** display-session -- the checkpoint drives the Settings panel in a sideloaded task pane

- [ ] Add `checkKey(key, { signal })` to `src/services/ai.ts`, calling `keyInfo()` and returning `{ label, remaining, limit, isFreeTier }` or an `AiError`. Done when: `src/services/ai.test.ts` replays `key.json` and `error-401.json` through it.
- [ ] Rewrite the `btn-test-connection` handler in `src/taskpane/taskpane.ts` to call `checkKey()` with the typed value, format the result with `formatKeyStatus()`, and never call `saveSettings()` or touch the saved key. Done when: a jsdom test types a key, clicks the button, and asserts the message text and that `localStorage` is unchanged. Cheaper substitute: saving before testing, which the unchanged-storage assertion catches.
- [ ] Disable the button while checking and show "Checking..."; a second click during a check does nothing. Done when: a jsdom test double-clicks and asserts one `fetch`.
- [ ] Capture valid, free-tier, and invalid results into `docs/captures/taskpane/test-connection/`. Done when: three captures exist.
- [ ] Commit: `"settings: Test Connection checks the key without spending credit"`

**Test checkpoint:** the jsdom tests above pass; in a sideloaded pane, a real key shows its label and remaining credit, a deliberately altered key shows the invalid-key message, and the saved key in `localStorage` is byte-identical before and after both checks (compared in the console). Cheaper substitute that fails: keeping the completion-based test, which changes the key's `usage` on the OpenRouter dashboard and shows no remaining-credit figure.

## 6. Remove Google Gemini

With every caller on the facade, the Gemini SDK and its code go. Removing `@google/genai` also removes the `google-auth-library` type errors that keep `tsc --noEmit` red on 2026-09-27, if D00 T02 §1 has not already worked around them.

- [ ] `npm uninstall @google/genai`, then delete `src/services/gemini.ts` and `src/services/gemini.test.ts`. Done when: `npm ls @google/genai` prints `(empty)` and `grep -rn "gemini" src --include=*.ts -il` lists no file except those whose only matches are `google/gemini-*` model ids.
- [ ] Replace `scripts/test-gemini.ts` with `scripts/test-openrouter.ts`: read `OPENROUTER_API_KEY` from `.env`, stream a one-sentence reply from `DEFAULT_FAST_MODEL` through `streamText()`, and print the model, the text, the token counts, and the cost from `usage`; point `test:live` in `package.json` at it. Done when: `npm run test:live` with the development key prints a reply and a cost line, and without the key exits `1` with a message naming `OPENROUTER_API_KEY`.
- [ ] Rename the variable in the local `.env` to `OPENROUTER_API_KEY` and add a committed `.env.example` with `OPENROUTER_API_KEY=` and a comment that the add-in never reads this file (only the live smoke does). Done when: `.env.example` exists, `.env` stays ignored (`git check-ignore .env` prints `.env`).
- [ ] Measure the production bundle before and after with `npm run build` and record `dist/taskpane.js` and `dist/commands.js` sizes in the commit body. Done when: both figures are quoted.
- [ ] Commit: `"ai: remove the Google Gemini SDK and client"`

**Needs:** OpenRouter API key (live test)

**Test checkpoint:** `grep -rn "@google/genai\|services/gemini\|GEMINI_API_KEY\|initGeminiClient" src scripts package.json` prints nothing; `npx tsc --noEmit` shows no `google-auth-library` error; `npx jest --ci` passes; `npm run test:live` prints a streamed reply and a cost line. Cheaper substitute that fails: leaving `@google/genai` installed "for later", which the `npm ls` check and the grep catch.

## 7. Provider Copy in the UI and Docs

The settings panel and the documents still describe Google Gemini and Google AI Studio. After the cutover they describe OpenRouter truthfully: where the key comes from, where the email text goes (to OpenRouter and on to the provider serving the chosen model), and what that costs.

**Fidelity:** Gemail Settings panel, API key row and Model hint -- docs/captures/taskpane/provider-copy/. Labels follow the Settings panel rule.
**Design:** docs/design/taskpane.md#settings-panel -- states: all in spec -- themes: n/a (copy change only; the theme work is owned by the appearance TODO in todo/06-features) -- density: n/a (one density in a fixed-width task pane)
**Job:** An Outlook user can get an OpenRouter key and understand where their email goes when they press a Gemail button. Consumer: none: this surface is the consumer.
**Treatment:** label "OpenRouter API key", placeholder "sk-or-...", link "Get a key at openrouter.ai" to https://openrouter.ai/keys, model hint "Prices are per million tokens. Your email text is sent to OpenRouter and the model's provider." Cheaper substitute that fails the checkpoint: replacing "Gemini" with "OpenRouter" word for word, which leaves "Google AI Studio" and the Google key format in the hint.
**Chrome:** consume the existing Settings panel markup and `aic-hint` style. Do not invent a second help text pattern.
**Needs:** Outlook client (sideload)
**Requires:** display-session -- the checkpoint captures the Settings panel in a sideloaded task pane

- [ ] Rewrite the key label, placeholder, key link, model label, and model hint in `src/taskpane/taskpane.html` as the Treatment line states. Done when: `grep -ci "gemini\|google ai studio\|aistudio" src/taskpane/taskpane.html` prints `0`.
- [ ] Rewrite `docs/setup-api-key.md` for OpenRouter: creating an account and a key at https://openrouter.ai/keys, setting a credit limit on the key, pasting it into Settings, Test Connection, and removing the wrong claim that `.env` configures the add-in. Done when: the file names OpenRouter, contains no "Gemini" or "GEMINI_API_KEY", and each step matches a sideload run.
- [ ] Update the provider sections of `README.md` (features table, prerequisites, development setup with `OPENROUTER_API_KEY` for `npm run test:live` only), `CONTRIBUTING.md`, and `SECURITY.md`. Done when: `grep -ci "gemini\|GEMINI_API_KEY" README.md CONTRIBUTING.md SECURITY.md` prints `0` for each, except for a CHANGELOG-style history line if one is kept.
- [ ] Rewrite the data-flow part of `PRIVACY.md`: email text goes from the add-in straight to OpenRouter (https://openrouter.ai/privacy) and on to the provider serving the chosen model; the key stays on the device; the optional data-collection filter of §9. The rest of the privacy truthfulness pass is D04 T01 §7. Done when: `PRIVACY.md` names OpenRouter and links its privacy policy, and no longer names Google as the recipient.
- [ ] Add the Unreleased `CHANGELOG.md` line: "Gemail now runs on OpenRouter. Add an OpenRouter key in Settings; your previous Google key was removed." Done when: the line exists under Unreleased.
- [ ] Capture the Settings panel into `docs/captures/taskpane/provider-copy/`. Done when: one capture exists.
- [ ] Commit: `"docs: Gemail runs on OpenRouter"`

**Test checkpoint:** `grep -rci "gemini" src/taskpane/taskpane.html README.md CONTRIBUTING.md SECURITY.md docs/setup-api-key.md` prints `0` for each file (model ids like `google/gemini-*` are not in these files); following `docs/setup-api-key.md` step by step in a sideloaded pane with a new key ends at a successful Test Connection. Cheaper substitute that fails: editing only the task pane, which leaves the setup guide telling users to create a Google key and fails the walkthrough.

## 8. Reasoning and Token Budgets

Reasoning models spend hidden tokens that count against `max_tokens`; when they use the whole budget, the reply is empty with `finish_reason: "length"` (https://openrouter.ai/docs/guides/reasoning-tokens). Gemini's JSON call disabled thinking with `thinkingBudget: 0`; OpenRouter's equivalent is the `reasoning` parameter. The budgets each feature passes today (for example 256 tokens for a brief summary) were set for Gemini and are re-derived here from measurement.

**Needs:** OpenRouter API key (live test)

- [ ] In `src/services/ai.ts`, send `reasoning: { effort: "none" }` for `generateJson` and for calls marked `utility: true` (summaries, extraction, translation, scoring) when the model's catalogue entry has `supportsReasoning`, and send nothing for models without it. Done when: request-body tests assert both cases.
- [ ] Handle an empty `TRUNCATED` reply once: retry the call with `maxTokens` doubled (capped at 8192), then raise `TRUNCATED`. Done when: a test replays a `finish_reason: "length"` empty reply followed by `chat-completion.json` and asserts two requests, the second with the doubled budget.
- [ ] Measure: `scripts/measure-budgets.ts` runs each feature's prompt from a committed sample email through `DEFAULT_MODEL` and `DEFAULT_FAST_MODEL` five times and prints the maximum `completion_tokens` and `reasoning_tokens` per feature. Done when: the table is committed as `docs/dev/token-budgets.md` with the date and model ids.
- [ ] Set each feature's `maxTokens` to the measured maximum visible output plus 50 percent, rounded up to a multiple of 256, in one constant table `FEATURE_BUDGETS` in `src/services/ai.ts`; features read from it instead of local literals (`getMaxTokensForLength()` in `draft-email.ts` and `summarize-thread.ts` included). Done when: `grep -rn "maxTokens: [0-9]" src/features` prints nothing.
- [ ] Commit: `"ai: reasoning control and measured token budgets"`

**Test checkpoint:** `npx jest src/services/ai.test.ts` passes the reasoning and truncation tests; `npx ts-node scripts/measure-budgets.ts` rerun on the day of review produces no feature whose measured visible output exceeds its budget; `docs/dev/token-budgets.md` exists with the measurements. Cheaper substitute that fails: raising every budget to 8192, which the measurement table exposes as untied to evidence and which leaves reasoning on for JSON calls, failing the request-body test.

## 9. Privacy Routing Setting

OpenRouter routes a request to any provider serving the model, including providers that may store prompts. `provider.data_collection: "deny"` restricts routing to providers that do not (https://openrouter.ai/docs/guides/routing/provider-routing). The operator chose to offer the filter off by default (2026-09-27: "No telemetry, ZDR off"), because turning it on narrows the models and providers available.

**Fidelity:** Gemail Settings panel, a Privacy group below Model -- docs/captures/taskpane/privacy-routing/. Placement and wording follow the Settings panel rule.
**Design:** docs/design/taskpane.md#settings-panel, docs/design/taskpane.md#form-controls -- states: off, on, no-provider-error -- themes: n/a (the theme work is owned by the appearance TODO in todo/06-features) -- density: n/a (one density in a fixed-width task pane)
**Job:** An Outlook user can require that only providers who do not store their prompts handle their email. Consumer: `generateText`, `generateJson`, and `streamText` in `src/services/ai.ts`, which add `provider.data_collection` to every request.
**Treatment:** a checkbox "Only use providers that don't store my prompts", off by default, with a one-line explanation that some models may become unavailable. Cheaper substitute that fails the checkpoint: a checkbox saved to settings that no request reads.
**Chrome:** consume `saveSettings()` and the `aic-checkbox` style used by the Rules panel. Do not invent a second settings writer.
**Needs:** Outlook client (sideload)
**Requires:** display-session -- the checkpoint toggles the setting in a sideloaded task pane

- [ ] Add `dataCollection: "allow" | "deny"` to `GemailSettings`, default `"allow"`, and the checkbox `#settings-data-collection` with its label and explanation in `src/taskpane/taskpane.html`. Done when: a settings test asserts the default is `"allow"` and a malformed stored value loads as `"allow"`.
- [ ] Add `provider: { data_collection: getSetting("dataCollection") }` to every request built in `src/services/ai.ts`, merged with `require_parameters` from `chatJson()`. Done when: request-body tests assert the field for both settings and for a JSON call (both fields present).
- [ ] Map a 503 `NO_PROVIDER` received while the filter is on to the message "No provider for this model meets your privacy setting. Choose another model or turn the setting off." Done when: a test replays `error-503.json` with the setting on and asserts the message key.
- [ ] Capture the setting off, on, and the no-provider message into `docs/captures/taskpane/privacy-routing/`. Done when: three captures exist.
- [ ] Commit: `"settings: an opt-in filter for providers that store prompts"`

**Test checkpoint:** `npx jest src/services/ai.test.ts src/features/settings.test.ts` passes the request-body and default tests; in a sideloaded pane with the setting on, the browser's network panel shows `"data_collection":"deny"` in the request body of a Summarize call, and with it off shows `"allow"`. Cheaper substitute that fails: sending the field only from the Settings tab's own calls, which the network-panel check on Summarize catches.

## Verification

- [ ] `pwsh scripts/check-all.ps1` -- exits 0: production build, typecheck, lint, tests, manifest, TODO gates green
- [ ] `npx jest --ci` exits 0 with `src/services/ai.test.ts`, `src/features/settings.test.ts`, and `src/taskpane/model-picker.test.ts` reporting
- [ ] A sideload smoke in new Outlook and in Outlook on the web: every feature, suggested replies, scoring, Test Connection, and all four ribbon commands succeed with only an OpenRouter key saved, and `npm run test:live` streams a reply
