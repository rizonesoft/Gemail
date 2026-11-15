---
schema_version: 1
id: prompts-and-shortcuts
domain: 06-features
status: draft
title: "TODO-02 -- Custom Prompts and Keyboard Shortcuts"
depends_on: []
---

# TODO-02 -- Custom Prompts and Keyboard Shortcuts

> **Goal:** A user can save their own prompts (an instruction with placeholders such as the selected text, the message body, the sender's name, and the output language), run one on the open message or the current selection from the Improve tab with the result shown in the same result card as every other feature, and drive the task pane's common actions from the keyboard with a help list that names every shortcut.

> [!IMPORTANT]
> **Current state (verified 2026-09-27):** The only user-saved text is the email template store (`aic_templates` in `src/features/settings.ts`, shape `{id, name, instructions, type}`), which prefills the Draft and Reply instruction boxes and cannot run on the message or a selection. The Improve tab offers four fixed focus radios (`name="improve-focus"`: fix_grammar, improve_clarity, make_concise, make_professional) and no custom action. `src/prompts/builder.ts` exports `buildPrompt(template, variables, appendRules)` and substitutes `{{NAME}}` placeholders sequentially, a defect `D04 T01 §2` fixes before this file runs. The task pane has three `keydown` listeners in `src/taskpane/taskpane.ts` (Enter in the two refine inputs and the template name input) and no other keyboard shortcut. Outlook-level add-in shortcuts need the unified manifest, which the operator kept in the backlog on 2026-09-27, so every shortcut here is scoped to the focused task pane.
<!-- claim: count "name=\"improve-focus\"" src/taskpane/taskpane.html = 4 -->
<!-- claim: count "keydown" src/taskpane/taskpane.ts = 3 -->
<!-- claim: absent src/features/custom-prompts.ts -->
<!-- claim: absent docs/design/custom-prompts.md -->

## Inputs

- [`src/features/settings.ts`](../../src/features/settings.ts) -- the template store pattern (`getTemplates`, `saveTemplate`, `deleteTemplate`) the prompt store follows
- [`src/prompts/builder.ts`](../../src/prompts/builder.ts) -- `buildPrompt`, which runs every custom prompt
- [`docs/design/taskpane.md`](../../docs/design/taskpane.md) -- the result card, dialogs, and accessibility rules the surfaces here answer to
- WAI-ARIA Authoring Practices, "Developing a Keyboard Interface" (https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/) -- the shortcut conventions §3 follows
- Microsoft Learn, "Add custom keyboard shortcuts to your Office Add-ins" (https://learn.microsoft.com/office/dev/add-ins/design/keyboard-shortcuts) -- why Outlook-level shortcuts are out of scope with the XML manifest
- -> XREF: D02 T02 §2 -- §1 runs custom prompts through the facade the cutover gave every caller
- -> XREF: D03 T01 §5 -- §1 adds its panel beside the Settings, Rules, and Templates panels the split created
- -> XREF: D05 T02 §2 -- §3 builds on the tab bar's arrow-key navigation and must not collide with it
- -> XREF: D07 T01 §5 -- the user guide documents the prompt library and the shortcut list
- -> XREF: D03 T04 §6 -- §3 binds `Ctrl+Enter` to the primary button of the action bar that section builds

## Outcome

- A **Prompts** panel lists the user's saved prompts, and a prompt can be created, edited, duplicated, and deleted (with confirmation); placeholders are validated as they are typed.
- The Improve tab offers the user's prompts beside the four fixed focuses, runs the chosen one on the selection (compose) or the message (read), and shows the output in the shared result card with the same Accept, Copy, and Regenerate actions.
- `Ctrl+Enter` runs the active tab's primary action, `Esc` stops a streaming response or closes the open dropdown or dialog, `Alt+1` to `Alt+6` switch tabs, and `?` opens the shortcut list; none collides with Outlook's shortcuts in new Outlook or Outlook on the web.

**Adjacency:** list=applicable @ D06 T02 §1; document=not-applicable (prompts produce text in the result card, never a document); settings=applicable @ D06 T02 §1; reporting=not-applicable (the library holds user text, nothing to summarize); notifications=applicable @ D06 T02 §2; permissions=applicable @ D06 T02 §2; audit=not-applicable (a prompt edit is the user own text, reversible by editing again); exchange=applicable @ D06 T01 §4; reverse=applicable @ D06 T02 §1

**Adjacency rationale:** Prompts travel in the settings backup of `D06 T01 §4`, which is their import and export. Permissions are the refusal paths of §2: a selection-only prompt in read mode, an empty selection, and a prompt whose placeholders cannot be filled.

## Implementation Order

| Order | Section | Deliverable                                     | Depends On             | Status |
| :---: | :-----: | ----------------------------------------------- | ---------------------- | :----: |
|   1   |   §1    | A custom prompt library                         | D03 T01 §5, D02 T02 §2 |  [ ]   |
|   2   |   §2    | Run a custom prompt on the message or selection | §1                     |  [ ]   |
|   3   |   §3    | Keyboard shortcuts in the task pane             | D05 T02 §2, D03 T04 §6 |  [ ]   |

---

## 1. A Custom Prompt Library

The legacy `TODO.md` asked to "let users save their own prompt templates". The existing email templates prefill an instruction box; a custom prompt is a reusable action ("Rewrite as bullet points", "Answer in Afrikaans, formal") that runs on the message. This section builds the store and its management panel; §2 runs them.

**Fidelity:** Gemail Prompts panel reached from the More features dropdown -- docs/captures/taskpane/prompts/. A list of rows with name and a one-line preview, then an editor below; spacing follows the Rules panel.
**Design:** docs/design/mockup.md#surfaces-the-mockup-does-not-draw, docs/design/mockup.md#ai-tools-menu, new surface: docs/design/custom-prompts.md, docs/design/taskpane.md#form-controls -- states: empty, list, editing, invalid, deleted -- themes: n/a (the pane has one light theme until D06 T04 ships dark mode) -- density: n/a (one density in a fixed-width task pane)
**Job:** The user can save, edit, and delete their own prompts. Consumer: the Improve tab prompt list of §2 and the settings backup of `D06 T01 §4`.
**Treatment:** a list with an empty state ("No prompts yet. Create one to run it from Improve."), a New button, and an editor with name, instruction text, a "Works on" choice (selection or whole message), and placeholder chips that insert `{{SELECTION}}`, `{{BODY}}`, `{{SENDER_NAME}}`, `{{LANGUAGE}}`. Cheaper substitute that fails the checkpoint: reusing the email template store, which cannot mark a prompt selection-only and fails the store test.
**Chrome:** consume the shared UI helpers in `src/ui/`, the inline dialog pattern for delete confirmation, and the settings storage helpers; do not invent a second list component or a second confirm.
**Needs:** Outlook client (sideload)
**Requires:** display-session -- the checkpoint drives the Prompts panel in a sideloaded Outlook on the web window

- [ ] Write `docs/design/custom-prompts.md` with headings for the list, the empty state, the editor, placeholder chips, and validation, before any markup. Done when: the file exists and the Design line above resolves under `python scripts/todo-graph.py validate`.
- [ ] Add `src/features/custom-prompts.ts` with `CustomPrompt { id, name, instruction, scope: "selection" | "message", createdAt }` and `listPrompts`, `savePrompt`, `deletePrompt`, `duplicatePrompt` over localStorage key `gemail_prompts`. Done when: tests cover create, edit, duplicate, delete, and a malformed stored value (returns an empty list, never throws).
- [ ] Add `validatePrompt(p)` accepting only `{{SELECTION}}`, `{{BODY}}`, `{{SENDER_NAME}}`, `{{LANGUAGE}}`, refusing an unknown placeholder, an empty instruction, a name over 60 characters, and `{{SELECTION}}` in a message-scoped prompt. Done when: a table-driven test covers each refusal with its message.
- [ ] Add `src/taskpane/panels/prompts.ts` and its `prompts-section` markup with the list, the editor, and the placeholder chips, reachable from the More features dropdown. Done when: the driven run below creates, edits, duplicates, and deletes a prompt. Cheaper substitute: a single textarea with no validation, which accepts `{{TYPO}}`.
- [ ] Cap the library at 50 prompts with a message at the cap. Done when: a test asserts the 51st save is refused with the message.
- [ ] Hold the built surface to the approved mockup: render it (sideloaded, or in the jsdom harness for a component), compare it with the anchors on this section's `**Design:**` line in `docs/design/mockup.md` and their renders under `docs/design/mockup/renders/`, use only design tokens (`docs/design/tokens.json`) and registry icons (`iconSvg()` from `src/ui/icons.ts`), and commit a capture of the result under `docs/captures/taskpane/`. Done when: `python scripts/design-lint.py` exits 0 with the baseline no larger, every difference from the mockup is fixed or recorded as a `**Design deviation:**` naming its follow-up section, and the capture is committed. Cheaper substitute that fails: building from the prose alone, which the capture comparison at review refuses.
- [ ] Commit: `"prompts: a custom prompt library"`

**Test checkpoint:** `npx jest src/features/custom-prompts.test.ts` passes the store, validation, and cap tests; the driven run creates "Bullet points" with `{{SELECTION}}`, sees an unknown `{{FOO}}` refused inline, duplicates it, deletes the copy after the confirm, and reloads the pane with the original still listed. Cheaper substitute that fails: storing prompts in the template store, which has no scope field and fails the selection-scope validation test.

## 2. Run a Custom Prompt on the Message or Selection

A saved prompt is only useful if it runs where the user is working. The Improve tab already reads the selection in compose mode and the body in read mode, and already has the result card with Accept Changes; custom prompts join its focus list so the write path, preview, and restore are the ones `D05 T03 §1` made safe. The run policy refuses before any model call when a prompt cannot run where the user is.

**Fidelity:** Gemail Improve tab, focus list extended with a "My prompts" group -- docs/captures/taskpane/improve/. The group sits below the four fixed focuses with the same radio style.
**Design:** docs/design/mockup.md#focus-cards, docs/design/mockup.md#diff-view, docs/design/mockup.md#surfaces-the-mockup-does-not-draw, docs/design/taskpane.md#result-card, docs/design/taskpane.md#form-controls -- states: no prompts, prompt chosen, running, result, refused -- themes: n/a (the pane has one light theme until D06 T04 ships dark mode) -- density: n/a (one density in a fixed-width task pane)
**Job:** The user can run one of their prompts on the current selection or message and insert the result. Consumer: the Improve result card and its Accept Changes write.
**Treatment:** a "My prompts" radio group listing each prompt by name, with a "Manage prompts" link to the Prompts panel; running fills the placeholders and streams into the result card. Cheaper substitute that fails the checkpoint: a separate result area for custom prompts, which duplicates the card and loses the restore.
**Chrome:** consume the Improve panel module, the shared result card, the facade's `streamText`, and the selection reader; do not add a second write path into the message.
**Needs:** Outlook client (sideload)
**Requires:** display-session -- the checkpoint runs a prompt in compose and read mode in a sideloaded Outlook on the web window

- [ ] Add `fillPrompt(prompt, context)` in `src/features/custom-prompts.ts` that builds the variables (`SELECTION`, `BODY`, `SENDER_NAME`, `LANGUAGE`) and calls `buildPrompt` once, appending the user's rules. Done when: a test asserts the filled text and that a `{{BODY}}` inside the email text is not substituted again.
- [ ] Refuse and notify before calling the model when the prompt cannot run: a selection-scoped prompt in read mode ("This prompt works on selected text in a message you are writing"), or an empty selection. Done when: tests cover both refusals and assert the facade is never called.
- [ ] Render the "My prompts" group in the Improve panel from `listPrompts()` and refresh it when the Prompts panel saves. Done when: a jsdom test adds a prompt and asserts the new radio appears without a reload.
- [ ] Route a chosen custom prompt through the Improve run path, so the result lands in the same result card and Accept Changes uses the selection-safe write of `D05 T03 §1`. Done when: the driven run below accepts a result into a selection and restores the original.
- [ ] Hold the built surface to the approved mockup: render it (sideloaded, or in the jsdom harness for a component), compare it with the anchors on this section's `**Design:**` line in `docs/design/mockup.md` and their renders under `docs/design/mockup/renders/`, use only design tokens (`docs/design/tokens.json`) and registry icons (`iconSvg()` from `src/ui/icons.ts`), and commit a capture of the result under `docs/captures/taskpane/`. Done when: `python scripts/design-lint.py` exits 0 with the baseline no larger, every difference from the mockup is fixed or recorded as a `**Design deviation:**` naming its follow-up section, and the capture is committed. Cheaper substitute that fails: building from the prose alone, which the capture comparison at review refuses.
- [ ] Commit: `"prompts: run a custom prompt from the Improve tab"`

**Test checkpoint:** `npx jest src/features/custom-prompts.test.ts -t "fillPrompt"` and `npx jest src/taskpane/panels/improve.test.ts` pass; the driven run selects one sentence in a compose form, runs "Bullet points", accepts, sees only that sentence replaced, restores it, and then opens a received message and sees the selection-only refusal message. Cheaper substitute that fails: replacing the whole body with the result, which the restore step and the one-sentence check catch.

## 3. Keyboard Shortcuts in the Task Pane

The legacy `TODO.md` asked for keyboard shortcuts for common actions. With the XML manifest, add-in shortcuts are limited to the focused task pane (Outlook-level shortcuts need the unified manifest, a backlog entry). The shortcuts must not collide with the arrow-key tab navigation of `D05 T02 §2` or with the browser and Outlook shortcuts a user relies on.

**Fidelity:** Gemail shortcut list dialog opened with `?` -- docs/captures/taskpane/shortcuts/. A two-column table of keys and actions inside the inline dialog.
**Design:** docs/design/mockup.md#write-action, docs/design/mockup.md#surfaces-the-mockup-does-not-draw, docs/design/taskpane.md#dialogs, docs/design/taskpane.md#accessibility -- states: closed, open -- themes: n/a (the pane has one light theme until D06 T04 ships dark mode) -- density: n/a (one density in a fixed-width task pane)
**Job:** The user can run, stop, and switch features without the mouse, and look up every shortcut. Consumer: none: this surface is the consumer.
**Treatment:** `Ctrl+Enter` (`Cmd+Enter` on Mac) runs the action bar's primary button (`D03 T04 §6`), whatever it currently is, `Esc` stops a stream or closes the dropdown or dialog, `Alt+1` to `Alt+6` switch to Reply, Draft, Summarize, Improve, Extract, Translate, and `?` outside a text field opens the list; buttons show their shortcut in their tooltip. Cheaper substitute that fails the checkpoint: a list with no handlers, which the handler tests reject.
**Chrome:** consume the tab controller (`src/taskpane/tabs.ts`), the inline dialog, and the stop control from `D03 T02 §4`; do not add a second tab-switching path.
**Needs:** Outlook client (sideload)
**Requires:** display-session -- the checkpoint drives the shortcuts in sideloaded new Outlook and Outlook on the web windows

- [ ] Add `src/taskpane/shortcuts.ts` with one `SHORTCUTS` table (`keys`, `action`, `label`) and one `keydown` listener on `document` that dispatches from it, ignoring `?` and `Alt+digit` while focus is in a text field. Done when: jsdom tests fire each shortcut and assert its action, and assert `?` typed in `draft-instructions` inserts a question mark.
- [ ] Check every shortcut against the Outlook on the web and new Outlook keyboard shortcut lists and record the check in the section's commit body. Done when: the commit body names the source page and states no collision. Source: https://support.microsoft.com/office/keyboard-shortcuts-for-outlook-3cdeb221-7ae5-4c1d-8c1d-9e63216c1efd
- [ ] Render the shortcut list dialog from `SHORTCUTS` and add each button's shortcut to its `title` and `aria-keyshortcuts`. Done when: a jsdom test asserts the dialog rows equal the table and the primary buttons carry `aria-keyshortcuts`.
- [ ] Make `Esc` stop an active stream through the Stop control and return focus to the primary button. Done when: a jsdom test with a pending `streamText` asserts the abort and the focus.
- [ ] Hold the built surface to the approved mockup: render it (sideloaded, or in the jsdom harness for a component), compare it with the anchors on this section's `**Design:**` line in `docs/design/mockup.md` and their renders under `docs/design/mockup/renders/`, use only design tokens (`docs/design/tokens.json`) and registry icons (`iconSvg()` from `src/ui/icons.ts`), and commit a capture of the result under `docs/captures/taskpane/`. Done when: `python scripts/design-lint.py` exits 0 with the baseline no larger, every difference from the mockup is fixed or recorded as a `**Design deviation:**` naming its follow-up section, and the capture is committed. Cheaper substitute that fails: building from the prose alone, which the capture comparison at review refuses.
- [ ] Commit: `"shortcuts: keyboard shortcuts and a shortcut list in the task pane"`

**Test checkpoint:** `npx jest src/taskpane/shortcuts.test.ts` passes every shortcut, text-field, dialog, and Esc-stop test; a driven run in new Outlook and Outlook on the web presses `Alt+2`, types an instruction, presses `Ctrl+Enter`, presses `Esc` mid-stream, and opens the list with `?`, with no Outlook action triggered by any of them. Cheaper substitute that fails: per-button listeners, which miss `Alt+digit` and fail the table-driven test.

## Verification

- [ ] `pwsh scripts/check-all.ps1` -- exits 0: production build, typecheck, lint, tests, manifest, TODO gates green
- [ ] `npx jest --ci` exits 0 with `custom-prompts`, `improve`, and `shortcuts` tests reporting
- [ ] A sideload smoke in new Outlook and Outlook on the web: create, run, accept, and restore a custom prompt, and drive every shortcut
