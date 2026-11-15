---
schema_version: 1
id: import-defects
domain: 05-quality
status: draft
title: "TODO-03 -- Behavior Defects from the Import"
depends_on: []
---

# TODO-03 -- Behavior Defects from the Import

> **Goal:** The features do what their controls say. **Accept Changes** replaces only the text that was improved, keeps formatting when it can, and can be undone in one step; the **Include original** checkbox changes what the model receives; **Refine** starts from the text the user edited, not the text the model first wrote; the user's writing rules apply to refinements as well as first drafts, and each Improve focus asks for that focus only; and Summarize and Extract say honestly that they read the open message and its quoted history, instead of pretending to read a thread they never load.

> [!IMPORTANT]
> **Current state (verified 2026-09-27):** In `src/features/improve-writing.ts`, `readSourceText` prefers the compose selection, but `acceptChanges` always calls `replaceComposeBody`, which writes the improved text over the whole body with `body.setAsync(text, { coercionType: Office.CoercionType.Text })`: improving one sentence erases the rest of the email, its HTML formatting, and the signature, with no way back. `DraftReplyOptions.includeOriginal` in `src/features/draft-reply.ts` is read from `#reply-include-original` by the task pane and never used by `generateReply`, which always sends the original email. `refineDraft` and `refineReply` refine the module variables `lastDraft` and `lastReply`, so edits the user typed into the `contenteditable` previews `#draft-preview` and `#reply-preview` are discarded. Rules are appended by `buildPrompt(..., true)` for first drafts and replies only; the inline refine prompts in both modules carry none. `IMPROVE_WRITING_PROMPT` in `src/prompts/templates.ts` always requires grammar, clarity, and length changes whatever `{{IMPROVEMENT_FOCUS}}` says. `getConversationMessages` in `src/services/outlook.ts` returns only the current message, and `summarizeThread` and `extractActionItems` wrap it in a try and catch whose fallback reads the same message again.
<!-- claim: count "body\.setAsync\(" src/features/improve-writing.ts = 1 -->
<!-- claim: count "includeOriginal" src/features/draft-reply.ts = 1 -->
<!-- claim: count "\$\{lastDraft\}" src/features/draft-email.ts = 1 -->
<!-- claim: count "\$\{lastReply\}" src/features/draft-reply.ts = 1 -->
<!-- claim: count "Fix grammar, spelling, and punctuation errors" src/prompts/templates.ts = 1 -->
<!-- claim: count "Fallback: read only the current email" src/features/summarize-thread.ts = 1 -->
<!-- claim: count "isClassicOutlook" src/services/outlook.ts = 0 -->
<!-- claim: count "In classic Outlook on Windows" README.md = 1 -->

## Inputs

- [`src/features/improve-writing.ts`](../../src/features/improve-writing.ts) -- `acceptChanges`, `readSourceText`, `replaceComposeBody` (§1)
- [`src/features/draft-reply.ts`](../../src/features/draft-reply.ts), [`src/features/draft-email.ts`](../../src/features/draft-email.ts) -- `generateReply`, `refineReply`, `refineDraft` (§2, §3, §4)
- [`src/prompts/templates.ts`](../../src/prompts/templates.ts), [`src/features/settings.ts`](../../src/features/settings.ts) -- `IMPROVE_WRITING_PROMPT` and `buildRulesText` (§4)
- [`src/services/outlook.ts`](../../src/services/outlook.ts), [`src/features/summarize-thread.ts`](../../src/features/summarize-thread.ts), [`src/features/extract-actions.ts`](../../src/features/extract-actions.ts) -- the thread reading §5 makes honest
- [`src/test/office-mock.ts`](../../src/test/office-mock.ts) -- the shared Office.js mock the tests here use (written by the test backbone in Phase 1)
- Microsoft Learn, `Office.Body` (`getAsync`, `setAsync`, `setSelectedDataAsync`; https://learn.microsoft.com/javascript/api/outlook/office.body) and `Office.MessageCompose.getSelectedDataAsync` (https://learn.microsoft.com/javascript/api/outlook/office.messagecompose#outlook-office-messagecompose-getselecteddataasync-member(1)) -- the write and read calls §1 uses
- -> XREF: D02 T02 §2 -- the repointed callers whose refine prompts §4 changes
- -> XREF: D03 T01 §4 -- the Improve panel module §1 works in and the Summarize and Extract panels §5 relabel; the Draft and Reply panels of D03 T01 §3 are where §2 and §3 work
- -> XREF: D06 T03 §3 -- the thread timeline, which builds on the honest thread reading §5 defines
- -> XREF: D01 T01 §3 -- §6 writes its notice and ribbon notification after the task pane and ribbon strings carry the Gemail name
- -> XREF: D07 T01 §1 -- the manifest requirement sets for the supported clients; §6 is the runtime refusal the manifest cannot express
- -> XREF: D07 T01 §5 -- the user guide states where Gemail runs, from the policy §6 enforces
- Microsoft Learn, "Office.Diagnostics interface" (https://learn.microsoft.com/javascript/api/outlook/office.diagnostics) -- the `hostName` values §6 detects classic Outlook by

## Outcome

- Improving a selection and clicking **Accept Changes** replaces exactly that selection; improving the whole body asks before replacing it; either way **Restore original** puts the message back as it was, and a failed write leaves the body unchanged and says so.
- With **Include original** unchecked, the reply prompt carries the sender and subject but not the body, and the checkbox label says what it controls.
- **Refine** sends the text currently in the preview, including the user's edits.
- The preset and custom rules appear in refine prompts, and each Improve focus produces a prompt that asks for that focus only.
- Summarize and Extract read the open message once, with no fallback that repeats the read, and their panels say they cover "this message and the replies quoted in it".
- In classic Outlook for Windows the pane shows one notice and nothing else, every ribbon command notifies and completes without acting, and new Outlook, Outlook on Mac, and Outlook on the web are unaffected.

**Adjacency:** list=not-applicable (nothing browsable); document=applicable; settings=not-applicable (the rules already exist; §4 only makes refine consume them); reporting=not-applicable (no summaries of Gemail's own data); notifications=applicable @ D05 T03 §1; permissions=applicable @ D05 T03 §1; audit=not-applicable (the debug log is owned by the resilience TODO in 03-architecture); exchange=not-applicable (nothing imported or exported); reverse=applicable

**Adjacency rationale:** Document: §1 writes into the user's message, the most sensitive write the add-in makes. Notifications and permissions: a failed or refused write (read mode, a changed selection) is reported, not swallowed. Reverse: **Restore original** is the reverse of **Accept Changes**.

## Implementation Order

| Order | Section | Deliverable                                            | Depends On | Status |
| :---: | :-----: | ------------------------------------------------------ | ---------- | :----: |
|   1   |   §1    | Accept Changes replaces only what was improved         | D03 T01 §4 |  [ ]   |
|   2   |   §2    | Include original is honored                            | D03 T01 §3 |  [ ]   |
|   3   |   §3    | Refine starts from the edited preview                  | D03 T01 §3 |  [ ]   |
|   4   |   §4    | Rules reach refine prompts; Improve honors its focus   | D02 T02 §2 |  [ ]   |
|   5   |   §5    | Honest thread reading                                  | D03 T01 §4 |  [ ]   |
|   6   |   §6    | Classic Outlook is turned away                         | D01 T01 §3 |  [ ]   |

---

## 1. Accept Changes Replaces Only What Was Improved

The worst defect in the import: improving one sentence and accepting the change deletes the rest of the email. The operator's rule for writes into mail (`AGENTS.md`, "The user's mail first") is a preview, an explicit click, and a way back. This section makes Accept write only what was improved, snapshots the body before any write, and adds a one-step restore. When Outlook refuses the write (read mode, or an item the add-in has no write permissions on), the refusal is reported and nothing is written.

**Fidelity:** Gemail task pane Improve result card (diff, Accept Changes, Restore original, the whole-body confirmation) -- docs/captures/taskpane/improve/. Accept Changes keeps its place; Restore original appears beside it after an accept.

**Design:** docs/design/mockup.md#diff-view, docs/design/mockup.md#undo-confirmation, docs/design/taskpane.md#result-card -- states: improved, accepted, restored, confirm whole body, write failed, selection changed -- themes: n/a (the card uses the pane tokens) -- density: n/a (one density in a fixed-width task pane)

**Job:** a user writing an email can accept an improvement of the part they selected, or of the whole body after confirming, and undo it in one click. Consumer: the compose body of the open message, read back by the restore.

**Treatment:** selection source writes with `body.setSelectedDataAsync` after re-reading the selection and checking it still equals the text that was improved; whole-body source asks first and writes HTML paragraphs with `body.setAsync(..., { coercionType: Html })`; both take a snapshot of the body HTML first, and **Restore original** writes the snapshot back. Cheaper substitute that fails the checkpoint: replacing the body as plain text (today's behavior), which the selection test fails on the untouched surrounding text.

**Chrome:** consume the result card, buttons, and dialog pattern from `src/ui/` and `docs/design/taskpane.md#dialogs`, and the Office.js wrapper in `src/services/outlook.ts`. Do not call Office.js body methods from the panel module directly.

**Needs:** Outlook client (sideload)

**Requires:** display-session -- the write and the restore are proven in a real compose form in Outlook on the web and new Outlook, which needs a window

- [ ] Record the source of the last improvement in `src/features/improve-writing.ts` as `lastSource: { kind: 'selection' | 'body', text: string }` from `readSourceText`. Done when: a test with the compose mock and a non-empty selection asserts `kind: 'selection'` and the selected text, and with an empty selection asserts `kind: 'body'`.
- [ ] Add `snapshotBodyHtml()` and `restoreBodyHtml(html)` to `src/services/outlook.ts` using `body.getAsync(Office.CoercionType.Html)` and `body.setAsync(html, { coercionType: Office.CoercionType.Html })`, each rejecting on a failed callback. Done when: `src/services/outlook.test.ts` covers both, including the failure path.
- [ ] Rewrite `acceptChanges` for the selection source: snapshot, re-read the selection with `getSelectedDataAsync`, and if it still equals `lastSource.text` write the improved text with `body.setSelectedDataAsync(improved, { coercionType: Office.CoercionType.Text })`; if it differs, throw "Select the original text again, then Accept." without writing. Done when: a test asserts the mock recorded exactly one `setSelectedDataAsync` with the improved text and no `setAsync`, and a changed-selection test asserts no write at all. Cheaper substitute: skipping the re-read, which writes the improvement over whatever the user selected since.
- [ ] For the body source, show an inline confirmation ("Replace the whole message body? Formatting in the body will be simplified. You can restore it afterwards.") with **Cancel** first, then on confirm snapshot and write the improved text as HTML paragraphs through the shared `bodyToHtml`. Done when: a jsdom panel test asserts no write happens on **Cancel** and exactly one `setAsync` with `coercionType: Html` on confirm.
- [ ] Add **Restore original** (`#btn-restore-original`) to the Improve result card, shown after a successful accept and hidden on item change, writing the snapshot back with `restoreBodyHtml`. Done when: a test accepts, restores, and asserts the last recorded write is the snapshot HTML.
- [ ] Report a failed write through the shared error banner and keep the body unchanged (no partial second write). Done when: a test forcing `fail: ['body.setSelectedDataAsync']` asserts the banner text and a single failed call.
- [ ] Sideload into a compose form in Outlook on the web and new Outlook: write three paragraphs with a signature, select the middle sentence, improve and accept, then restore; then improve the whole body, confirm, and restore. Done when: captures under `docs/captures/taskpane/improve/` show the untouched first and last paragraphs and signature after the selection accept and the original after each restore.
- [ ] Hold the built surface to the approved mockup: render it (sideloaded, or in the jsdom harness for a component), compare it with the anchors on this section's `**Design:**` line in `docs/design/mockup.md` and their renders under `docs/design/mockup/renders/`, use only design tokens (`docs/design/tokens.json`) and registry icons (`iconSvg()` from `src/ui/icons.ts`), and commit a capture of the result under `docs/captures/taskpane/`. Done when: `python scripts/design-lint.py` exits 0 with the baseline no larger, every difference from the mockup is fixed or recorded as a `**Design deviation:**` naming its follow-up section, and the capture is committed. Cheaper substitute that fails: building from the prose alone, which the capture comparison at review refuses.
- [ ] Commit: `"fix: Accept Changes replaces only what was improved, with a one-step restore"`

**Test checkpoint:** `npx jest src/features/improve-writing.test.ts src/services/outlook.test.ts src/taskpane` passes the selection, changed-selection, whole-body confirm and cancel, restore, and failed-write tests; reverting `acceptChanges` to `replaceComposeBody` fails the selection test; the sideloaded run keeps the surrounding paragraphs and signature. Cheaper substitute that fails: writing the selection with `setSelectedDataAsync` but no snapshot, which fails the restore test.

## 2. Include Original Is Honored

The Reply panel shows an **Include original** checkbox, checked by default, that changes nothing. Outlook's own reply form already quotes the original message, so the checkbox cannot mean "quote it in the reply". The useful and privacy-respecting meaning is whether the original body is sent to the model. Default recorded here, cost of changing it is one label and one prompt branch: unchecked sends only the sender and subject, and the label becomes "Send the original message to the AI".

- [ ] Rename the label text beside `#reply-include-original` in `src/taskpane/taskpane.html` to "Send the original message to the AI" and add a one-line hint under it ("Unchecked: the AI sees only the sender and subject."). Done when: `grep -c "Send the original message to the AI" src/taskpane/taskpane.html` prints `1`.
- [ ] In `generateReply` in `src/features/draft-reply.ts`, when `options.includeOriginal` is false, build `ORIGINAL_EMAIL` from the sender and subject only. Done when: a feature test with `includeOriginal: false` asserts the prompt contains the subject and not a sentence from the mocked body, and with `true` asserts both.
- [ ] Carry `includeOriginal` through `regenerateReply` and `refineReply` so a regenerate or refine never sends a body the user opted out of. Done when: a test generates with `false`, then regenerates and refines, and asserts neither prompt contains the body.
- [ ] Commit: `"fix: Include original controls whether the message body reaches the model"`

**Test checkpoint:** `npx jest src/features/draft-reply.test.ts` passes the `false`, `true`, regenerate, and refine cases; deleting the `includeOriginal` branch fails the `false` case. Cheaper substitute that fails: removing the checkbox, which passes nothing here and leaves a privacy choice the operator can reasonably want unoffered; the label test fails on it.

## 3. Refine Starts from the Edited Preview

The Draft and Reply previews are editable, and users fix a name or a date there before asking for "shorter" or "friendlier". Refine then works from the model's original text and silently undoes the user's edits.

- [ ] Change `refineDraft(instructions)` in `src/features/draft-email.ts` and `refineReply(instructions)` in `src/features/draft-reply.ts` to take the current text as a parameter (`refineDraft(current, instructions)`), and store the refined result as the new last value. Done when: feature tests assert the prompt contains the passed text and not the stale module value.
- [ ] In the Draft and Reply panel modules, pass the preview's current text (`#draft-preview`, `#reply-preview`, read as text from the `contenteditable`) to refine. Done when: a jsdom panel test edits the preview, triggers refine, and asserts the facade received the edited text.
- [ ] Read the preview as plain text with paragraph breaks preserved (`innerText`, falling back to `textContent` with block elements joined by newlines). Done when: a test with two `div` paragraphs in the preview asserts the refine prompt carries them on separate lines.
- [ ] Commit: `"fix: refine works from the text the user edited"`

**Test checkpoint:** `npx jest src/features src/taskpane` passes the edited-text tests for both panels; restoring the use of `lastDraft` in `refineDraft` fails the draft test. Cheaper substitute that fails: disabling editing in the preview, which the panel test fails because the edit no longer changes the text sent.

## 4. Rules Reach Refine Prompts; Improve Honors Its Focus

The user's rules (no placeholders, no signature, keep short, and the custom rules) shape first drafts and replies but vanish on refine, so a refinement can reintroduce a signature the user banned. Separately, **Make Concise** still asks the model to fix grammar and keep the same length, because the Improve prompt carries fixed requirements for every focus.

- [ ] Append `buildRulesText()` from `src/features/settings.ts` to the refine prompts in `src/features/draft-email.ts` and `src/features/draft-reply.ts`, through the same `buildPrompt(..., true)` path the first drafts use. Done when: feature tests with the `noSignature` rule on assert the refine prompt contains that rule's text.
- [ ] Replace the fixed requirement list in `IMPROVE_WRITING_PROMPT` in `src/prompts/templates.ts` with a `{{FOCUS_REQUIREMENTS}}` placeholder, and add `IMPROVE_FOCUS_REQUIREMENTS` mapping `fix_grammar`, `improve_clarity`, `make_concise`, and `make_professional` to their own requirement lines (keeping "maintain the original meaning" and "return only the improved text" in every one). Done when: a builder or feature test asserts the `make_concise` prompt asks for a shorter text and does not say "keep the same general length", and the `fix_grammar` prompt does not ask to restructure sentences.
- [ ] Use the same map in `src/commands/commands.ts` so the ribbon's four commands and the Improve tab send identical requirements for the same focus. Done when: a test asserts the ribbon `makeConcise` prompt equals the tab's `make_concise` prompt for the same text.
- [ ] Commit: `"fix: rules apply to refinements, and each Improve focus asks for itself"`

**Test checkpoint:** `npx jest src/features src/prompts src/commands` passes the rules-in-refine, per-focus, and ribbon-parity tests; removing the rules from the reply refine fails its test. Cheaper substitute that fails: adding "follow the user's rules" as prose to the refine prompt, which carries no rule text and fails the `noSignature` assertion.

## 5. Honest Thread Reading

Summarize and Extract present themselves as thread tools, but `getConversationMessages` returns only the open message, and a try and catch "fallback" reads the same message again. The honest scope, without Microsoft Graph (out of scope: no server and no extra sign-in), is the open message plus the replies quoted inside its body. This section removes the pretense and states the scope in the UI.

- [ ] Rename `getConversationMessages` in `src/services/outlook.ts` to `getCurrentMessage` returning one `EmailMessage`, delete its Graph comment, and update every caller. Done when: `grep -rn "getConversationMessages" src` prints nothing and `npx tsc --noEmit` exits `0`.
- [ ] Delete the fallback branches in `summarizeThread` (`src/features/summarize-thread.ts`) and `extractActionItems` (`src/features/extract-actions.ts`) so each reads the message once and a read failure surfaces as an error. Done when: feature tests assert one body read per call and that a failed read rejects with its message.
- [ ] Change the intro lines of `#summarize-section` and `#extract-section` in `src/taskpane/taskpane.html` to say they work on "this message and the replies quoted in it". Done when: `grep -c "the replies quoted in it" src/taskpane/taskpane.html` prints `2`.
- [ ] Update the Summarize and Extract prompts in `src/prompts/templates.ts` to tell the model the content may contain quoted earlier replies and to attribute points to their senders where the quoting shows them. Done when: a builder test asserts both prompts contain that instruction.
- [ ] Commit: `"fix: Summarize and Extract read the open message honestly"`

**Test checkpoint:** `npx jest src/features src/services` passes the single-read and read-failure tests; `grep -rn "getConversationMessages\|Fallback: read only the current email\|Fallback to current email" src` prints nothing; the two intro lines are present. Cheaper substitute that fails: relabeling the panels without removing the fallbacks, which the single-read test fails.

## 6. Classic Outlook Is Turned Away

The operator discontinued classic Outlook for Windows on 2026-11-15 ("Outlook classic is giving us alot of issues, so discontinue the outlook classic plugin"). Until then it was unsupported but still loaded: the XML manifest's `DesktopFormFactor` covers classic Outlook, new Outlook, and Outlook on the web alike, and no manifest element separates them, so the add-in itself has to refuse. `Office.context.mailbox.diagnostics.hostName` is `Outlook` in classic Outlook on Windows and on Mac, `newOutlookWindows` in new Outlook on Windows, and `OutlookWebApp` on the web; `Office.context.diagnostics.platform` is `PC` only on Windows. Classic is therefore `hostName === "Outlook"` on platform `PC`, and Outlook on Mac (supported) is the same host name on platform `Mac`. This section must not turn away Mac, new Outlook, or the web, and must not call the model or read the message in classic. Source: https://learn.microsoft.com/javascript/api/outlook/office.diagnostics

**Fidelity:** Gemail task pane, the classic Outlook notice in place of the panels -- docs/captures/taskpane/classic/. The notice uses the error banner's two-line shape: what happened, then what to do.
**Design:** docs/design/mockup.md#error-banner, docs/design/mockup.md#surfaces-the-mockup-does-not-draw, docs/design/taskpane.md#status-and-errors -- states: classic, supported -- themes: n/a (existing status tokens; D06 T04 owns live theming) -- density: n/a (one density in a fixed-width task pane)
**Job:** A user who opens Gemail in classic Outlook learns in one sentence that it no longer runs there and where it does, instead of meeting a half-working pane. Consumer: none: this surface is the consumer.
**Treatment:** Detection once in the Office.js wrapper, a notice that replaces the tab bar and panels, and ribbon commands that notify and complete without acting. Cheaper substitute that fails the checkpoint: a dismissible warning above a working pane, which the no-model-call test fails.
**Chrome:** consume the existing `#error-banner` styles in `src/taskpane/taskpane.html` and `showNotification` in `src/commands/commands.ts`. Do not invent a second banner style or a second notification helper.

- [ ] Add `isClassicOutlook()` to `src/services/outlook.ts`: true only when `Office.context.mailbox.diagnostics.hostName` is `Outlook` and `Office.context.diagnostics.platform` is `Office.PlatformType.PC`; false when either value is missing. Done when: `npx jest src/services/outlook.test.ts -t "classic"` passes five cases: classic Windows true; Mac (`Outlook`, `Mac`), new Outlook (`newOutlookWindows`), the web (`OutlookWebApp`), and missing diagnostics all false. Cheaper substitute that fails: testing the host name alone, which the Mac case fails.
- [ ] In `src/taskpane/taskpane.ts`, check `isClassicOutlook()` first inside `Office.onReady`: when true, hide the tab bar and every panel, show one notice ("Gemail no longer runs in classic Outlook." and under it "Open this mailbox in new Outlook or in Outlook on the web to keep using Gemail." with a **How to switch** link to `https://support.microsoft.com/office/656bb8d9-5a60-49b2-a98b-ba7822bc7627`), and return before any settings read, message read, or event handler is registered. Done when: a jsdom test with classic diagnostics asserts the notice text, that no tab or action button is visible, and that the provider client and `Office.context.mailbox.item` were never touched.
- [ ] In `src/commands/commands.ts`, start each of the four ribbon command handlers with the same check: when true, call `showNotification` with "Gemail no longer runs in classic Outlook. Use new Outlook or Outlook on the web." and `event.completed()`, and do nothing else. Done when: a test per command with classic diagnostics asserts one notification, one `event.completed()`, and no provider call or body write.
- [ ] Remove the classic Outlook tip from `README.md` ("In classic Outlook on Windows, you can also access this via ...") and state under the install steps that Gemail runs in new Outlook for Windows and Mac and in Outlook on the web, and not in classic Outlook for Windows. Done when: `grep -c -i "classic" README.md` prints `1` and that line is the not-supported statement.
- [ ] Render the notice: load the built `dist/taskpane.html` in the headless browser `tools/design/render-mockup.mjs` drives, with `Office` stubbed to report `hostName` `Outlook` on platform `PC`, and capture it into `docs/captures/taskpane/classic/notice.png`. Done when: the capture is committed and shows the notice with no tab bar.
- [ ] Hold the built surface to the approved mockup: render it (sideloaded, or in the jsdom harness for a component), compare it with the anchors on this section's `**Design:**` line in `docs/design/mockup.md` and their renders under `docs/design/mockup/renders/`, use only design tokens (`docs/design/tokens.json`) and registry icons (`iconSvg()` from `src/ui/icons.ts`), and commit a capture of the result under `docs/captures/taskpane/`. Done when: `python scripts/design-lint.py` exits 0 with the baseline no larger, every difference from the mockup is fixed or recorded as a `**Design deviation:**` naming its follow-up section, and the capture is committed. Cheaper substitute that fails: building from the prose alone, which the capture comparison at review refuses.
- [ ] Commit: `"clients: classic Outlook is turned away with a notice"`

**Test checkpoint:** `npx jest src/services/outlook.test.ts -t "classic"` passes its five cases; `npx jest src/taskpane src/commands -t "classic"` passes the notice and the four command cases with the provider client never called; `grep -c -i "classic" README.md` prints `1`; `npm run build` and `npx tsc --noEmit` exit 0. Cheaper substitute that fails: hiding the ribbon button with CSS or a manifest edit, which leaves the commands callable and which the command tests fail.

## Verification

- [ ] `pwsh scripts/check-all.ps1` -- exits 0: production build, typecheck, lint, tests, manifest, TODO gates green
- [ ] `npx jest --ci` exits 0 with this file's test files reporting (improve, draft, reply, summarize, extract, commands, builder, outlook, panel tests)
- [ ] A sideload in new Outlook and in Outlook on the web repeats the §1 selection accept and restore on a message with a signature, recorded in the file closeout
