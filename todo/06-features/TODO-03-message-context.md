---
schema_version: 1
id: message-context
domain: 06-features
status: draft
title: "TODO-03 -- Message Context"
depends_on: []
---

# TODO-03 -- Message Context

> **Goal:** Gemail reads more of what the user is looking at: the attachments of the open message (text and PDF, within stated size limits, only the ones the user picks) feed summaries and replies; a thread timeline lists the key decisions, requests, and dates found in the message and its quoted history; and while writing, Gemail suggests people named in the conversation who are not on To or CC, adding one only when the user clicks it.

> [!IMPORTANT]
> **Current state (verified 2026-09-27):** `src/services/outlook.ts` reads the body, subject, sender, and recipients and has no attachment code (no `attachments`, `getAttachmentsAsync`, or `getAttachmentContentAsync`). `getConversationMessages` returns only the current message (its comment defers a Graph implementation), so "thread" today means the open message and whatever history is quoted in its body; `D05 T03 §5` makes the code and labels say so honestly before this file runs. The Summarize tab offers three styles (`name="summary-style"`: bullets, paragraph, tldr) and no timeline. Nothing in `src/` writes recipients: no `addAsync` call exists in `src/services/outlook.ts` or `src/features/`. The manifest's `VersionOverridesV1_1` sets `DefaultMinVersion="1.5"`; the attachment content API needs Mailbox 1.8, which new Outlook and Outlook on the web support (the requirement-set pass is `D07 T01 §1`).
<!-- claim: count "attachment" src/services/outlook.ts = 0 -->
<!-- claim: count "addAsync" src/services/outlook.ts = 0 -->
<!-- claim: count "name=\"summary-style\"" src/taskpane/taskpane.html = 3 -->
<!-- claim: absent src/features/timeline.ts -->

## Inputs

- [`src/services/outlook.ts`](../../src/services/outlook.ts) -- the Office.js wrapper §1 and §4 extend
- [`src/features/summarize-thread.ts`](../../src/features/summarize-thread.ts), [`src/features/draft-reply.ts`](../../src/features/draft-reply.ts) -- the consumers of attachment text (§2) and the timeline's home (§3)
- [`docs/design/taskpane.md`](../../docs/design/taskpane.md) -- the feature panel and result card rules the surfaces answer to
- Microsoft Learn, "Office.MessageRead.getAttachmentContentAsync" (https://learn.microsoft.com/javascript/api/outlook/office.messageread#outlook-office-messageread-getattachmentcontentasync-member(1)) and "Outlook API requirement sets" (https://learn.microsoft.com/javascript/api/requirement-sets/outlook/outlook-api-requirement-sets) -- the Mailbox 1.8 APIs §1 uses
- Microsoft Learn, "Office.Recipients.addAsync" (https://learn.microsoft.com/javascript/api/outlook/office.recipients#outlook-office-recipients-addasync-member(1)) -- the CC write §4 makes
- OpenRouter, "PDF inputs" (https://openrouter.ai/docs/features/multimodal/pdfs) -- the `file` content part and the `file-parser` plugin §2 sends
- -> XREF: D02 T02 §1 -- §2 sends file content parts through the facade; §3 uses its JSON output
- -> XREF: D05 T01 §2 -- §1 and §4 test against the Office.js mock the test backbone ships
- -> XREF: D05 T03 §5 -- §3 builds on the honest thread reading that fix establishes
- -> XREF: D07 T01 §5 -- the user guide documents attachments, the timeline, and CC suggestions

## Outcome

- `listAttachments()` and `readAttachment(id)` return the open message's file attachments with name, type, and size, and the text of `.txt`, `.md`, `.csv`, `.html`, and `.eml` files or the base64 of a PDF, refusing anything over 5 MB and any other type with a named reason.
- Summarize and Reply show an "Include attachments" list with a checkbox per supported attachment (none checked by default); checked text attachments join the prompt and checked PDFs go to OpenRouter as `file` content parts.
- Summarize offers a Timeline style that lists each decision, request, and deadline with its date and who said it, as structured JSON rendered as a list.
- In compose mode, the Reply and Draft tabs show up to three CC suggestions (name and address from the quoted thread, not already on To or CC); clicking one adds it with `item.cc.addAsync` and nothing is added without a click.

**Adjacency:** list=applicable @ D06 T03 §2; document=applicable @ D06 T03 §2; settings=not-applicable (the size limit and supported types are fixed, documented constants, not user preferences); reporting=applicable @ D06 T03 §3; notifications=applicable @ D06 T03 §4; permissions=applicable @ D06 T03 §1; audit=not-applicable (nothing here writes except the CC add, which the user makes and can remove in Outlook); exchange=applicable @ D06 T03 §1; reverse=applicable @ D06 T03 §4

**Adjacency rationale:** Exchange is reading files somebody else authored (the attachments). Permissions are the refusals: an attachment over the limit, an unsupported type, a cloud attachment, and a client below Mailbox 1.8. Reverse for §4 is that a suggestion added by mistake is removed in Outlook's own CC field; §4 adds nothing silently.

## Implementation Order

| Order | Section | Deliverable                                | Depends On             | Status |
| :---: | :-----: | ------------------------------------------ | ---------------------- | :----: |
|   1   |   §1    | Read attachments                           | D05 T01 §2             |  [ ]   |
|   2   |   §2    | Attachment-aware summaries and replies     | §1, D02 T02 §1         |  [ ]   |
|   3   |   §3    | Thread timeline                            | D02 T02 §2, D05 T03 §5 |  [ ]   |
|   4   |   §4    | Smart CC suggestions                       | D05 T01 §2             |  [ ]   |

---

## 1. Read Attachments

The legacy `TODO.md` asked for attachment awareness ("summarize attached PDFs or documents"). This section is the reading layer only: list, size-check, and read, with every refusal named, tested against the Office.js mock. It imports attachment content only on request, and its refusal policy (size, type, cloud, client) is decided here, not in each consumer. It adds no surface.

- [ ] Add `listAttachments(): Promise<AttachmentInfo[]>` to `src/services/outlook.ts` using `item.attachments` in read mode and `item.getAttachmentsAsync` in compose mode (Mailbox 1.8), returning `{ id, name, contentType, size, isInline, kind }` and skipping inline images. Done when: mock tests cover read mode, compose mode, and an item with no attachments. Source: https://learn.microsoft.com/javascript/api/outlook/office.messageread#outlook-office-messageread-attachments-member
- [ ] Add `readAttachment(id)`, which imports one attachment's content through `item.getAttachmentContentAsync`, returning text for `Office.MailboxEnums.AttachmentContentFormat.Base64` decoded text types and base64 for PDF, and handling the `Eml` and `ICalendar` formats as text. Done when: mock tests cover a text file, a PDF, and an `.eml`. Source: https://learn.microsoft.com/javascript/api/outlook/office.attachmentcontent
- [ ] Enforce the refusal policy with an `AttachmentError` code and message: over 5 MB (`TOO_LARGE`), a cloud attachment (`CLOUD`), an unsupported type (`UNSUPPORTED`), and a client without Mailbox 1.8 (`UNSUPPORTED_CLIENT`, detected with `Office.context.requirements.isSetSupported("Mailbox", "1.8")`). Done when: a test per code asserts the message and that no content read was attempted.
- [ ] Cap total attachment text sent per request at 100,000 characters and truncate with `truncateContext` from `src/prompts/builder.ts`, returning `truncated: true`. Done when: a test with two 80,000-character files asserts the cap and the flag.
- [ ] Commit: `"outlook: list and read message attachments"`

**Test checkpoint:** `npx jest src/services/outlook.test.ts -t "attachment"` passes every mode, format, and refusal case against the Office.js mock. Cheaper substitute that fails: reading `item.attachments` only, which returns nothing in compose mode and fails the compose-mode test.

## 2. Attachment-Aware Summaries and Replies

With the reading layer in place, the user chooses which attachments join a summary or a reply. Nothing is sent by default: an attachment leaves the device only when the user ticks it, because it may hold more than the message does. PDFs go to OpenRouter as `file` content parts so a model without native PDF support is served by the `file-parser` plugin.

**Fidelity:** Gemail Summarize and Reply panels, new "Include attachments" list above the primary button -- docs/captures/taskpane/summarize/ and docs/captures/taskpane/reply/. One checkbox row per attachment with name and size.
**Design:** docs/design/mockup.md#surfaces-the-mockup-does-not-draw, docs/design/mockup.md#reply-form, docs/design/taskpane.md#feature-panel, docs/design/taskpane.md#form-controls -- states: no attachments, list, some checked, refused, truncated -- themes: n/a (the pane has one light theme until D06 T04 ships dark mode) -- density: n/a (one density in a fixed-width task pane)
**Job:** The user can include chosen attachments in a summary or reply. Consumer: the Summarize and Reply prompts sent through the facade.
**Treatment:** a collapsed "Include attachments (N)" row that expands to checkboxes, unchecked by default; refused attachments show disabled with their reason; a truncation note appears in the result card when the cap applied. Cheaper substitute that fails the checkpoint: always including every attachment, which sends files the user never chose and fails the default-unchecked test.
**Chrome:** consume the shared form-control styles, the facade's content-part support, and the status line for the truncation note; do not add a second file reader.
**Needs:** Outlook client (sideload)
**Requires:** display-session -- the checkpoint opens a message with attachments in a sideloaded Outlook on the web window

- [ ] Extend the facade message type in `src/services/ai.ts` to accept `{ type: "file", file: { filename, file_data } }` content parts and a `plugins: [{ id: "file-parser", pdf: { engine: "pdf-text" } }]` option. Done when: a contract test asserts the request body against the OpenRouter PDF example. Source: https://openrouter.ai/docs/features/multimodal/pdfs
- [ ] Add `src/ui/attachment-picker.ts` rendering the list from `listAttachments()` with refusals disabled and every box unchecked. Done when: a jsdom test asserts the unchecked default and the disabled refused rows.
- [ ] Mount the picker in the Summarize and Reply panel modules and pass the chosen attachments to `summarizeThread` and `generateReply`. Done when: feature tests assert text attachments join the prompt inside the untrusted-content fence of `D04 T01 §2` and PDFs become file parts.
- [ ] Show the truncation note in the result card when `truncated` is true. Done when: a jsdom test asserts the note.
- [ ] Hold the built surface to the approved mockup: render it (sideloaded, or in the jsdom harness for a component), compare it with the anchors on this section's `**Design:**` line in `docs/design/mockup.md` and their renders under `docs/design/mockup/renders/`, use only design tokens (`docs/design/tokens.json`) and registry icons (`iconSvg()` from `src/ui/icons.ts`), and commit a capture of the result under `docs/captures/taskpane/`. Done when: `python scripts/design-lint.py` exits 0 with the baseline no larger, every difference from the mockup is fixed or recorded as a `**Design deviation:**` naming its follow-up section, and the capture is committed. Cheaper substitute that fails: building from the prose alone, which the capture comparison at review refuses.
- [ ] Commit: `"attachments: include chosen attachments in summaries and replies"`

**Test checkpoint:** `npx jest src/ui/attachment-picker.test.ts src/features/summarize-thread.test.ts src/features/draft-reply.test.ts` passes; a driven run opens a message with a PDF and a `.txt`, ticks the PDF only, summarizes, and the summary cites content found only in the PDF, while the network request carries one `file` part and no `.txt` text. Cheaper substitute that fails: pasting PDF base64 into the text prompt, which the contract test rejects.

## 3. Thread Timeline

The legacy `TODO.md` asked for "a visual timeline of a conversation showing key decisions". Since the add-in reads the open message and its quoted history (not the mailbox, which would need Graph), the timeline is built from that text: each decision, request, or deadline with its date and author, as structured JSON rendered as a list.

**Fidelity:** Gemail Summarize tab, a fourth style "Timeline" -- docs/captures/taskpane/summarize/. The result card renders a vertical list: date, who, what, with the kind as a small label.
**Design:** docs/design/mockup.md#surfaces-the-mockup-does-not-draw, docs/design/mockup.md#result-card, docs/design/taskpane.md#result-card -- states: empty, list, no dated items -- themes: n/a (the pane has one light theme until D06 T04 ships dark mode) -- density: n/a (one density in a fixed-width task pane)
**Job:** The user can see who decided or asked for what, and when, in a long thread. Consumer: none: this surface is the consumer; Copy puts a plain-text version on the clipboard.
**Treatment:** entries sorted oldest first, each `{ date, author, kind: decision | request | deadline, text }`; entries without a date sort last under "Undated"; an empty result says "No decisions, requests, or deadlines found in this message." Cheaper substitute that fails the checkpoint: a free-text bullet summary labeled Timeline, which fails the schema test.
**Chrome:** consume `generateJson` from the facade, the shared result card, and the one escaper; do not render model text as HTML.
**Needs:** Outlook client (sideload)
**Requires:** display-session -- the checkpoint summarizes a long quoted thread in a sideloaded Outlook on the web window

- [ ] Add `TIMELINE_PROMPT` to `src/prompts/templates.ts` and `TIMELINE_SCHEMA` (JSON Schema, `strict`) in `src/features/timeline.ts`. Done when: a test asserts the schema validates the recorded fixture and rejects an entry without `kind`. Source: https://openrouter.ai/docs/features/structured-outputs
- [ ] Add `buildTimeline(thread)` calling `generateJson` with the schema and sorting entries by parsed date, undated last. Done when: tests over a fixture response assert order and the undated group.
- [ ] Add `value="timeline"` to the `summary-style` radios and render entries through `src/ui/` with text nodes only. Done when: a jsdom test asserts the list and that a `<script>` in an entry renders as text.
- [ ] Make Copy produce `YYYY-MM-DD, author: text` lines. Done when: a test asserts the copied text.
- [ ] Hold the built surface to the approved mockup: render it (sideloaded, or in the jsdom harness for a component), compare it with the anchors on this section's `**Design:**` line in `docs/design/mockup.md` and their renders under `docs/design/mockup/renders/`, use only design tokens (`docs/design/tokens.json`) and registry icons (`iconSvg()` from `src/ui/icons.ts`), and commit a capture of the result under `docs/captures/taskpane/`. Done when: `python scripts/design-lint.py` exits 0 with the baseline no larger, every difference from the mockup is fixed or recorded as a `**Design deviation:**` naming its follow-up section, and the capture is committed. Cheaper substitute that fails: building from the prose alone, which the capture comparison at review refuses.
- [ ] Commit: `"summarize: a thread timeline of decisions, requests, and deadlines"`

**Test checkpoint:** `npx jest src/features/timeline.test.ts` passes schema, ordering, and rendering tests; a driven run on a message quoting a five-message history shows at least one decision and one deadline with the dates found in the quoted headers (both quoted in the commit body). Cheaper substitute that fails: a Summarize prompt asking for a timeline in prose, which fails the schema test.

## 4. Smart CC Suggestions

The legacy `TODO.md` asked to "suggest who should be CC'd based on email content". Suggestions come from people named with an address in the quoted thread who are not already on To or CC. They are computed locally from the text (no model call and nothing sent), and a person is added only when the user clicks.

**Fidelity:** Gemail Reply and Draft panels in compose mode, a "Suggested CC" chip row above the result card -- docs/captures/taskpane/reply/. Chips match the suggestion chips of Suggest replies.
**Design:** docs/design/mockup.md#surfaces-the-mockup-does-not-draw, docs/design/mockup.md#quick-replies, docs/design/taskpane.md#feature-panel, docs/design/taskpane.md#buttons -- states: none, suggestions, added, refused -- themes: n/a (the pane has one light theme until D06 T04 ships dark mode) -- density: n/a (one density in a fixed-width task pane)
**Job:** The user can add a person from the conversation to CC with one click. Consumer: the compose item's CC field through `item.cc.addAsync`.
**Treatment:** up to three chips "Add Name <address>", hidden in read mode; clicking adds and turns the chip into "Added · Undo", where Undo removes that person again; failures notify the user through the error banner. Cheaper substitute that fails the checkpoint: adding suggestions automatically, which writes recipients without a click and fails the no-auto-add test.
**Chrome:** consume the suggestion-chip style from Reply, the error banner, and `src/services/outlook.ts` recipients; do not write recipients anywhere else.
**Needs:** Outlook client (sideload)
**Requires:** display-session -- the checkpoint clicks a suggestion in a sideloaded compose form

- [ ] Add `extractPeople(text)` in `src/features/cc-suggestions.ts` parsing `Name <address>` and `From:`, `To:`, `Cc:` header lines of quoted history. Done when: tests over fixtures of Outlook and Gmail quote formats assert the parsed people.
- [ ] Add `suggestCc(people, current)` excluding the user (`Office.context.mailbox.userProfile.emailAddress`), everyone on To and CC (read through `getEmailRecipients`), and duplicates, returning at most three in order of mentions. Done when: tests assert each exclusion and the cap.
- [ ] Add `addCc(recipient)` to `src/services/outlook.ts` over `item.cc.addAsync` with its callback surfaced. Done when: mock tests assert success and the failure message. Source: https://learn.microsoft.com/javascript/api/outlook/office.recipients#outlook-office-recipients-addasync-member(1)
- [ ] Render the chips in the Reply and Draft panel modules in compose mode only and call `addCc` on click. Done when: a jsdom test asserts no `addAsync` call happens until a chip is clicked.
- [ ] Add the chip's Undo: `removeCc(address)` in `src/services/outlook.ts` reads `item.cc.getAsync` and writes the list back without that address through `item.cc.setAsync`. Done when: a mock test adds then undoes and asserts the CC list equals the original.
- [ ] Hold the built surface to the approved mockup: render it (sideloaded, or in the jsdom harness for a component), compare it with the anchors on this section's `**Design:**` line in `docs/design/mockup.md` and their renders under `docs/design/mockup/renders/`, use only design tokens (`docs/design/tokens.json`) and registry icons (`iconSvg()` from `src/ui/icons.ts`), and commit a capture of the result under `docs/captures/taskpane/`. Done when: `python scripts/design-lint.py` exits 0 with the baseline no larger, every difference from the mockup is fixed or recorded as a `**Design deviation:**` naming its follow-up section, and the capture is committed. Cheaper substitute that fails: building from the prose alone, which the capture comparison at review refuses.
- [ ] Commit: `"compose: suggest people from the thread for CC"`

**Test checkpoint:** `npx jest src/features/cc-suggestions.test.ts src/services/outlook.test.ts -t "cc"` passes; a driven run replies to a message whose quoted history names a third person, sees the chip, confirms the CC field is unchanged, clicks, sees the person in CC, clicks Undo, and sees the CC field as it was. Cheaper substitute that fails: asking the model for suggestions, which sends the thread for no gain and can invent addresses; the extraction tests pin addresses to the text.

## Verification

- [ ] `pwsh scripts/check-all.ps1` -- exits 0: production build, typecheck, lint, tests, manifest, TODO gates green
- [ ] `npx jest --ci` exits 0 with `outlook`, `attachment-picker`, `timeline`, and `cc-suggestions` tests reporting
- [ ] A sideload smoke in new Outlook and Outlook on the web: summarize with a chosen PDF, build a timeline, and add a suggested CC
