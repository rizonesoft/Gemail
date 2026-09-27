---
schema_version: 1
id: settings-upgrades
domain: 06-features
status: draft
title: "TODO-01 -- Settings Upgrades"
depends_on: []
---

# TODO-01 -- Settings Upgrades

> **Goal:** The settings a user sets once follow them to every device they open Outlook on (except the API key, which never leaves the device), the user controls how creative and how long the output is, the output language they choose applies to every feature that writes, settings can be backed up to a file and restored, and the model picker shows what a model costs and how much it can read, with the real cost of each request shown after it runs.

> [!IMPORTANT]
> **Current state (verified 2026-09-27):** Settings live only in `localStorage` under `ai_compose_settings` (`src/features/settings.ts`), so a user who opens Outlook on the web on a second computer starts from defaults; nothing in `src/` uses `Office.context.roamingSettings`. The settings shape (`AIComposeSettings`) has no temperature or length field: every call site passes its own hard-coded `temperature` and `maxOutputTokens` (13 call sites, 0.1 to 0.9 and 20 to 4096). `defaultLanguage` is applied only to the Translate select (`taskpane.ts` line 1041) and the Settings select, never to `draft-language` or `reply-language`; the language `<option>` list is written four times in `taskpane.html`. There is no export or import. The model select (`settings-model`) is six hard-coded Gemini options with no price or context information; the OpenRouter catalogue and picker are owned by `D02 T01 §5` and `D02 T02 §4`, and the rename of the storage keys to `gemail_*` by `D01 T01 §5`.
<!-- claim: count "roamingSettings" src/features/settings.ts = 0 -->
<!-- claim: count "temperature" src/features/settings.ts = 0 -->
<!-- claim: count "<option value=\"English\"" src/taskpane/taskpane.html = 4 -->
<!-- claim: count "defaultLanguage" src/taskpane/taskpane.ts = 3 -->

## Inputs

- [`src/features/settings.ts`](../../src/features/settings.ts) -- the settings service every section here extends
- [`src/taskpane/taskpane.html`](../../src/taskpane/taskpane.html) -- the Settings panel (`settings-section`) and the language selects
- [`docs/design/taskpane.md`](../../docs/design/taskpane.md) -- the Settings panel and form-control rules every surface here answers to
- Microsoft Learn, "Office.RoamingSettings" (https://learn.microsoft.com/javascript/api/outlook/office.roamingsettings) -- the 32 KB per-add-in limit and `saveAsync` semantics §1 builds on
- OpenRouter, "List available models" (https://openrouter.ai/docs/api-reference/list-available-models) and "Usage accounting" (https://openrouter.ai/docs/use-cases/usage-accounting) -- the `context_length`, `pricing`, and `usage.cost` fields §5 shows
- -> XREF: D02 T02 §2 -- §2 changes the per-feature options every caller passes after the cutover repointed them; §5 reads the picker of D02 T02 §4
- -> XREF: D03 T01 §5 -- §3 wires the default language in the Settings panel module the split creates
- -> XREF: D04 T01 §4 -- §1 roams only after the key has moved to its own device-only storage
- -> XREF: D06 T04 §3 -- local usage stats accumulate the per-request cost §5 reads
- -> XREF: D07 T01 §5 -- the user guide documents every setting this file adds

## Outcome

- Changing the tone on one device and opening the pane on another shows the new tone; the API key is absent from `Office.context.roamingSettings` on every device, proven by a test that asserts it.
- `creativity` and `responseLength` are settings with named consumers: the facade call options of every generating feature derive from them.
- The default output language preselects the Draft and Reply language selects, and all four language selects render from one list.
- **Export settings** downloads a versioned JSON file without the key; **Import settings** validates it and refuses a malformed or newer-schema file with a message naming the problem.
- The model picker shows each model's context window and price per million tokens, and each result card shows the request's cost in dollars from OpenRouter's usage accounting.

**Adjacency:** list=not-applicable (settings are a fixed form, not a collection to browse); document=not-applicable (the only file produced is the settings backup, declared under exchange); settings=applicable; reporting=applicable @ D06 T04 §3; notifications=applicable @ D06 T01 §1; permissions=applicable @ D06 T01 §4; audit=not-applicable (settings changes are the user own choices and reversible in the same panel, and the debug log records them); exchange=applicable @ D06 T01 §4; reverse=applicable

**Adjacency rationale:** Permissions here means refusal paths: `roamingSettings` over its 32 KB limit, a `saveAsync` failure, and an import file that is malformed or from a newer schema. Reverse is reset to defaults per setting group and restoring from an exported file.

## Implementation Order

| Order | Section | Deliverable                          | Depends On | Status |
| :---: | :-----: | ------------------------------------ | ---------- | :----: |
|   1   |   §1    | Settings sync through roamingSettings | D04 T01 §4 |  [ ]   |
|   2   |   §2    | Creativity and length controls       | D02 T02 §2 |  [ ]   |
|   3   |   §3    | Output language everywhere           | D03 T01 §5 |  [ ]   |
|   4   |   §4    | Export and import settings           | §1         |  [ ]   |
|   5   |   §5    | Model info and cost per request      | D02 T02 §4 |  [ ]   |

---

## 1. Settings Sync Through roamingSettings

The legacy `TODO.md` asked for settings in `Office.context.roamingSettings` for cross-device sync. RoamingSettings are stored in the user's mailbox and follow the add-in to every client, which is exactly why the key must never go there (operator decision 2026-09-27: "This device only"). By the time this runs, `D04 T01 §4` has moved the key into its own device-only storage, so the settings object this section roams holds nothing secret.

- [ ] Add `src/services/roaming.ts` with `readRoaming(): Partial<GemailSettings> | null` and `writeRoaming(s: RoamingSettings): Promise<void>` over `Office.context.roamingSettings.get/set/saveAsync` under one key `gemail_settings`, where `RoamingSettings` is `GemailSettings` minus every secret field. Done when: the type excludes the key field at compile time (`// @ts-expect-error` test on assigning an `apiKey`) and `npx tsc --noEmit` exits 0. Source: https://learn.microsoft.com/javascript/api/outlook/office.roamingsettings
- [ ] Make `saveSettings` in `src/features/settings.ts` write `localStorage` first (the device copy) and then `writeRoaming`, and notify the user of a `saveAsync` failure through the settings panel's saved message ("Saved on this device; could not sync: <reason>"). Done when: a test with the Office mock (`src/test/office-mock.ts`) failing `saveAsync` asserts the local copy was written and the message names the sync failure. Cheaper substitute: writing only to roaming, which loses every setting when the mailbox is unreachable.
- [ ] Make `loadSettings` merge in this order: defaults, then roaming, then device-only fields from `localStorage`; on first run after this ships, copy the existing local non-secret settings up to roaming once. Done when: tests cover a first run with local settings only, a second device with roaming only, and a malformed roaming value (falls back to local, never throws).
- [ ] Guard the 32 KB limit: `writeRoaming` refuses a payload over 30,000 characters of JSON and keeps the local save. Done when: a test with a 40,000-character custom rules string asserts the refusal and the message.
- [ ] Add a test that serializes every `writeRoaming` payload across the suite and asserts no field named `apiKey` or matching `/^sk-or-/` ever appears. Done when: the test fails if `apiKey` is added to `RoamingSettings`.
- [ ] Commit: `"settings: roam non-secret settings through roamingSettings"`

**Test checkpoint:** `npx jest src/services/roaming.test.ts src/features/settings.test.ts` passes, including the no-key-in-roaming test, the saveAsync-failure test, and the 32 KB refusal test; a driven run in two browsers signed in to the same mailbox in Outlook on the web shows a tone changed in one appear in the other after reopening the pane, while the key field stays empty on the second. Cheaper substitute that fails: storing the whole settings object in roaming, which the no-key test rejects.

## 2. Creativity and Length Controls

Every caller hard-codes its own `temperature` and `maxOutputTokens` today, so a user who wants plainer or shorter output has no lever. This section adds two settings with named consumers: `creativity` (Precise, Balanced, Creative) and `responseLength` (Short, Standard, Long), mapped per feature in one table in the facade, so the per-feature defaults the cutover chose stay the Balanced/Standard row.

**Fidelity:** Gemail Settings panel, new "Output" group beneath the model picker -- docs/captures/taskpane/settings/. Control order, spacing, and wording follow the capture; the group matches the existing default-tone select.
**Design:** docs/design/mockup.md#writing, docs/design/mockup.md#reply-form, docs/design/taskpane.md#settings-panel -- states: default, changed, saved, reset -- themes: n/a (the pane has one light theme until D06 T04 ships dark mode) -- density: n/a (one density in a fixed-width task pane)
**Job:** The user can make every feature's output more precise or more creative, and shorter or longer, once. Consumer: the facade call options of every generating feature.
**Treatment:** two three-option segmented selects labeled Creativity and Response length, with a one-line hint under each. Cheaper substitute that fails the checkpoint: a raw 0.0 to 2.0 temperature slider, which exposes a number users cannot reason about and fails the mapping test.
**Chrome:** consume the `.aic-select` and label styles and the settings service; do not invent a second settings writer.
**Needs:** Outlook client (sideload)
**Requires:** display-session -- the checkpoint drives the Settings panel in a sideloaded Outlook on the web window

- [ ] Add `creativity: "precise" | "balanced" | "creative"` and `responseLength: "short" | "standard" | "long"` to `GemailSettings` with defaults `balanced` and `standard`. Done when: `loadSettings()` on empty storage returns both defaults in a test.
- [ ] Add `resolveGenerationOptions(feature, settings)` in `src/services/ai.ts` returning `{ temperature, max_tokens }` from one table keyed by feature, where the `balanced`/`standard` row equals the values each caller passed after `D02 T02 §2`. Done when: a table-driven test asserts every feature's Balanced/Standard values are unchanged and that `precise` lowers and `creative` raises temperature for every feature. Source: https://openrouter.ai/docs/api-reference/parameters
- [ ] Replace the per-call-site `temperature` and `max_tokens` literals in `src/features/*.ts` and `src/commands/commands.ts` with `resolveGenerationOptions`. Done when: `grep -rn "temperature:" src/features src/commands` prints nothing.
- [ ] Add the Output group to the Settings panel in `src/taskpane/taskpane.html` (`settings-creativity`, `settings-response-length`) with `<label for>` on each. Done when: both controls render, persist through Save, and reload with the saved values.
- [ ] Hold the built surface to the approved mockup: render it (sideloaded, or in the jsdom harness for a component), compare it with the anchors on this section's `**Design:**` line in `docs/design/mockup.md` and their renders under `docs/design/mockup/renders/`, use only design tokens (`docs/design/tokens.json`) and registry icons (`iconSvg()` from `src/ui/icons.ts`), and commit a capture of the result under `docs/captures/taskpane/`. Done when: `python scripts/design-lint.py` exits 0 with the baseline no larger, every difference from the mockup is fixed or recorded as a `**Design deviation:**` naming its follow-up section, and the capture is committed. Cheaper substitute that fails: building from the prose alone, which the capture comparison at review refuses.
- [ ] Commit: `"settings: creativity and response length controls"`

**Test checkpoint:** `npx jest src/services/ai.test.ts -t "resolveGenerationOptions"` passes; `grep -rn "temperature:" src/features src/commands` prints nothing; a driven run sets Response length to Short, drafts an email, and the result has fewer words than the same prompt at Long (both word counts quoted). Cheaper substitute that fails: adding the controls without wiring the consumers, which leaves the grep non-empty.

## 3. Output Language Everywhere

`defaultLanguage` is a setting with one consumer (Translate). A user who writes in German sets it and still gets English drafts. This section makes the default preselect the Draft and Reply language selects and renders every language select from one list.

**Fidelity:** Gemail Draft, Reply, Translate, and Settings language selects -- docs/captures/taskpane/draft/ and docs/captures/taskpane/settings/. Option order and labels identical in all four.
**Design:** docs/design/mockup.md#reply-form, docs/design/mockup.md#writing, docs/design/taskpane.md#form-controls -- states: default, preselected, changed -- themes: n/a (the pane has one light theme until D06 T04 ships dark mode) -- density: n/a (one density in a fixed-width task pane)
**Job:** The user can set the language once and get every draft and reply in it. Consumer: `draft-language`, `reply-language`, and `translate-language` initial values.
**Treatment:** the three feature selects open preselected to the default; Reply keeps its "Auto-detect (match email)" option first and preselects the default only when the user chose one explicitly. Cheaper substitute that fails the checkpoint: preselecting Translate only, as today.
**Chrome:** consume the one `LANGUAGES` list the task pane split created (`D03 T01 §6`) and the settings service; do not write a fifth option list.
**Needs:** Outlook client (sideload)
**Requires:** display-session -- the checkpoint opens the Draft and Reply tabs in a sideloaded Outlook on the web window

- [ ] Add `defaultReplyLanguage: "auto" | string` to `GemailSettings` (default `auto`), shown as a second select in Settings, so Reply's auto-detect survives. Done when: a settings test asserts the default is `auto`.
- [ ] In the Draft panel module, preselect `draft-language` from `defaultLanguage` on panel init. Done when: a jsdom test with `defaultLanguage: "German"` asserts the select value.
- [ ] In the Reply panel module, preselect `reply-language` from `defaultReplyLanguage`. Done when: a jsdom test asserts `auto` and an explicit language both preselect correctly.
- [ ] Assert that every language select is rendered from the shared list: a jsdom test compares the option values of all four selects. Done when: the test fails if one select gains an option the others lack.
- [ ] Hold the built surface to the approved mockup: render it (sideloaded, or in the jsdom harness for a component), compare it with the anchors on this section's `**Design:**` line in `docs/design/mockup.md` and their renders under `docs/design/mockup/renders/`, use only design tokens (`docs/design/tokens.json`) and registry icons (`iconSvg()` from `src/ui/icons.ts`), and commit a capture of the result under `docs/captures/taskpane/`. Done when: `python scripts/design-lint.py` exits 0 with the baseline no larger, every difference from the mockup is fixed or recorded as a `**Design deviation:**` naming its follow-up section, and the capture is committed. Cheaper substitute that fails: building from the prose alone, which the capture comparison at review refuses.
- [ ] Commit: `"settings: apply the default output language to every feature"`

**Test checkpoint:** `npx jest src/taskpane/panels/draft.test.ts src/taskpane/panels/reply.test.ts` passes the preselect tests; a driven run with the default language set to German opens Draft and shows German selected, generates, and the draft is in German. Cheaper substitute that fails: setting the Settings select only, which the Draft preselect test rejects.

## 4. Export and Import Settings

The legacy `TODO.md` asked for backup and restore. A user moving to a new mailbox or recovering after "Clear all data" needs their rules, templates, and custom prompts back. The key is never exported: the file is something a user may email to themselves. The import policy is refuse-by-default: a file that is malformed, from a newer schema, or unconfirmed changes nothing.

**Fidelity:** Gemail Settings panel, "Backup" group above Clear all data -- docs/captures/taskpane/settings/. Two secondary buttons side by side, consistent with Test Connection.
**Design:** docs/design/mockup.md#settings, docs/design/mockup.md#save-and-clear, docs/design/mockup.md#surfaces-the-mockup-does-not-draw, docs/design/taskpane.md#settings-panel -- states: default, exporting, imported, refused -- themes: n/a (the pane has one light theme until D06 T04 ships dark mode) -- density: n/a (one density in a fixed-width task pane)
**Job:** The user can save their settings, rules, templates, and custom prompts to a file and restore them later. Consumer: the settings service, the templates store, and the custom prompt store on import.
**Treatment:** **Export settings** downloads `gemail-settings-YYYY-MM-DD.json`; **Import settings** opens a file picker, shows what will be replaced, and applies only after the user confirms in an inline dialog. Cheaper substitute that fails the checkpoint: a textarea of raw JSON, which fails the validation-message test.
**Chrome:** consume the inline dialog pattern (`docs/design/taskpane.md#dialogs`), the secondary button style, and the settings service; do not add a second settings writer.
**Needs:** Outlook client (sideload)
**Requires:** display-session -- the checkpoint downloads and picks a file in a sideloaded Outlook on the web window

- [ ] Add `exportSettings(): string` in `src/features/settings-backup.ts` producing `{ "schema": 1, "exportedAt", "settings", "rules", "templates", "prompts" }` with no key field. Done when: a test asserts the output parses, carries `schema: 1`, and contains no `/sk-or-/` or `apiKey`.
- [ ] Add `importSettings(json: string): ImportResult` that validates the shape, refuses `schema` greater than 1 ("This file is from a newer Gemail"), refuses malformed JSON with the parse position, and returns what will change without writing. Done when: tests cover valid, malformed, newer-schema, and a file carrying an `apiKey` (ignored, and the result says so).
- [ ] Add `applyImport(result)` that writes through `saveSettings` and the template and prompt stores in one pass. Done when: a test asserts a round trip `applyImport(importSettings(exportSettings()))` leaves every store equal.
- [ ] Wire `btn-export-settings` (download through a Blob URL) and `btn-import-settings` (hidden `<input type="file" accept="application/json">`) in the Settings panel module, with the confirm dialog before apply. Done when: both work in the driven run below. Cheaper substitute: applying the import without the confirm, which the driven run records as a defect.
- [ ] Hold the built surface to the approved mockup: render it (sideloaded, or in the jsdom harness for a component), compare it with the anchors on this section's `**Design:**` line in `docs/design/mockup.md` and their renders under `docs/design/mockup/renders/`, use only design tokens (`docs/design/tokens.json`) and registry icons (`iconSvg()` from `src/ui/icons.ts`), and commit a capture of the result under `docs/captures/taskpane/`. Done when: `python scripts/design-lint.py` exits 0 with the baseline no larger, every difference from the mockup is fixed or recorded as a `**Design deviation:**` naming its follow-up section, and the capture is committed. Cheaper substitute that fails: building from the prose alone, which the capture comparison at review refuses.
- [ ] Commit: `"settings: export and import a settings backup"`

**Test checkpoint:** `npx jest src/features/settings-backup.test.ts` passes the round-trip, malformed, newer-schema, and no-key tests; a driven run exports settings, clicks Clear all data, imports the file, confirms, and the rules and templates are back while the key field stays empty. Cheaper substitute that fails: exporting `localStorage` wholesale, which the no-key test rejects.

## 5. Model Info and Cost Per Request

The legacy `TODO.md` asked to show model capabilities in the selector. OpenRouter publishes each model's `context_length` and `pricing` in the catalogue, and returns the request's cost when usage accounting is requested (`usage: { include: true }`). Showing both lets a user choose a cheaper model knowingly and see what each draft cost.

**Fidelity:** Gemail model picker rows and the result card footer -- docs/captures/taskpane/settings/ and docs/captures/taskpane/result-card/. The cost sits beside word count and reading time, same style.
**Design:** docs/design/mockup.md#model-picker, docs/design/mockup.md#footer, docs/design/mockup.md#result-card, docs/design/taskpane.md#result-card, docs/design/taskpane.md#settings-panel -- states: cost known, cost unknown, free model -- themes: n/a (the pane has one light theme until D06 T04 ships dark mode) -- density: n/a (one density in a fixed-width task pane)
**Job:** The user can see what a model costs before choosing it and what a request cost after running it. Consumer: none: this surface is the consumer; `D06 T04 §3` also reads the per-request cost.
**Treatment:** each picker row shows "128K context · $0.15 / $0.60 per 1M tokens" (input / output); each result card footer shows "≈ $0.0004" from `usage.cost`, or "Free" for a zero-priced model, or nothing when usage is absent. Cheaper substitute that fails the checkpoint: estimating the cost locally from the price table, which disagrees with the billed figure and fails the fixture test.
**Chrome:** consume the catalogue from `listModels()` (`D02 T01 §5`), the picker from `D02 T02 §4`, and the result card stats line; do not compute prices in a second place.
**Needs:** Outlook client (sideload)
**Requires:** display-session -- the checkpoint reads the picker and a result card in a sideloaded Outlook on the web window

- [ ] Add `formatModelInfo(model)` in `src/ui/model-info.ts` rendering context length (K or M) and per-million input and output prices from `pricing.prompt` and `pricing.completion` (USD per token). Done when: a test over the committed models fixture asserts the strings for a paid, a free, and a missing-pricing model. Source: https://openrouter.ai/docs/api-reference/list-available-models
- [ ] Show `formatModelInfo` on every picker row and under the selected model. Done when: the driven run below shows it.
- [ ] Request usage accounting on every call (`usage: { include: true }` in the facade request) and return `usage.cost` from `generateText`, `generateJson`, and the final chunk of `streamText`. Done when: a contract test replays the recorded completion and SSE fixtures and asserts the parsed `cost`. Source: https://openrouter.ai/docs/use-cases/usage-accounting
- [ ] Render the cost in the result card footer next to word count through one `formatCost(cost)` helper. Done when: a jsdom test asserts "Free", a dollar figure, and the absent case.
- [ ] Hold the built surface to the approved mockup: render it (sideloaded, or in the jsdom harness for a component), compare it with the anchors on this section's `**Design:**` line in `docs/design/mockup.md` and their renders under `docs/design/mockup/renders/`, use only design tokens (`docs/design/tokens.json`) and registry icons (`iconSvg()` from `src/ui/icons.ts`), and commit a capture of the result under `docs/captures/taskpane/`. Done when: `python scripts/design-lint.py` exits 0 with the baseline no larger, every difference from the mockup is fixed or recorded as a `**Design deviation:**` naming its follow-up section, and the capture is committed. Cheaper substitute that fails: building from the prose alone, which the capture comparison at review refuses.
- [ ] Commit: `"models: show context and price, and the cost of each request"`

**Test checkpoint:** `npx jest src/ui/model-info.test.ts src/services/ai.test.ts -t "cost"` passes against the committed fixtures; a driven run drafts an email and the footer cost matches the `usage.cost` in the network response (both quoted). Cheaper substitute that fails: a locally estimated cost, which differs from the response's `usage.cost` in the driven run.

## Verification

- [ ] `pwsh scripts/check-all.ps1` -- exits 0: production build, typecheck, lint, tests, manifest, TODO gates green
- [ ] `npx jest --ci` exits 0 with `roaming`, `settings`, `settings-backup`, and `model-info` tests reporting
- [ ] A sideload smoke in new Outlook and Outlook on the web: roam a setting, change creativity and length, export and import, and read a request cost
