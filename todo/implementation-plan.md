# Gemail -- Implementation Plan to 100%

The order to run every section in, from today (a dead published add-in on Google Gemini, freshly moved from WSL to Windows) to Gemail 2.0.0 on OpenRouter, proven on a clean Outlook profile.

> **Progress:** **0 of 113 sections complete (0%).** 113 sections (0 discovered); backlog 10 of 500. Derived from the Implementation Order tables by `python scripts/todo-graph.py plan --sync` -- never edited by hand.

Seeded 2026-09-27 from the operator's decisions recorded in [`../AGENTS.md`](../AGENTS.md), the code inventory of the imported 1.3.2 tree, and every open item of the retired root `TODO.md`.

**How to use this.** The front door is the `process-plan` skill. It audits, then runs `process-phase` on the first phase that has a ready row, then the next ready phase after that closeout or park. One row is `process-todo-section` then `review-todo-section`. Do not invent a side loop.

**Copy a row and paste it.** The skills resolve a reference from whatever shape it arrives in, so this is a complete instruction:

```
process todo section: | [ ] | `D00 T01 §1` | Point every URL at the Gemail Pages path and redeploy | 6 |
```

> [!IMPORTANT]
> **The boxes are derived. Never tick one by hand.**
>
> They are a projection of each TODO's Implementation Order table, and those flip in exactly one place: `review-todo-section`, after a `Verified:` stamp exists.
>
> ```bash
> python scripts/todo-graph.py plan --sync     # rewrite the boxes, then re-align every table
> python scripts/todo-graph.py plan --check    # fail if they have gone stale
> ```

**Campaign discovery is bounded; operator planning is not.** Sections the operator asks for are never capped. A section a campaign files on its own carries an `**Origin:** discovered run=<run id> <YYYY-MM-DD>` line, and one run may file at most `per_run_discovered_sections` of them (in [`budget.json`](./budget.json)); `validate` refuses a breach. Discovered work that fails the admission test in [`README.md`](./README.md) goes to [`backlog.md`](./backlog.md).

**How phases are authored.** A phase is a `### Phase <N> -- <Title>` heading, one paragraph on why it runs where it does, and one table. Every section in the tree sits in exactly one phase row. A section's phase is never earlier than the phase of anything it depends on, and within a phase rows run in dependency order.

---

## The acceptance bar

Gemail 2.0.0 is **one Outlook add-in that behaves like one product**: installed from its manifest into new Outlook and Outlook on the web, calling only OpenRouter under the user's own key, never sending or overwriting mail without the user's click, keeping the key on the device, rendering model output as text, streaming and cancellable, readable and operable by keyboard and screen reader, built and checked by the same gates on every push, and served from the Gemail Pages path while the old path keeps existing installs alive. The count of sections is deliberately not repeated here: read it from `query stats`.

| Aim                                                        | Owned by                                                  |
| ---------------------------------------------------------- | --------------------------------------------------------- |
| The live add-in loads again                                | `D00 T01 §1` · `D01 T01 §7` · `D99 T01 §2` · `D99 T01 §3` |
| Every clone and every push is gated                        | `D00 T02 §1`-`§5` · `D00 T03 §1`-`§4`                     |
| It is called Gemail everywhere a user looks                | `D01 T01 §1`-`§6`                                         |
| OpenRouter only, over fetch, under the user's key          | `D02 T01 §1`-`§6` · `D02 T02 §1`-`§9`                     |
| Nothing is written into mail without a preview and a click | `D05 T03 §1` · `D03 T03 §6` · `D03 T02 §4`                |
| The key never leaves the device except to OpenRouter       | `D04 T01 §4` · `D06 T01 §1`                               |
| Model output is text, never HTML                           | `D04 T01 §1` · `D04 T01 §2` · `D04 T01 §3`                |
| Shared once, never copied                                  | `D03 T01 §1`-`§7`                                         |
| Fast, streamed, and cancellable                            | `D03 T02 §1`-`§8`                                         |
| Every failure tells the user what to do                    | `D03 T03 §1`-`§6`                                         |
| It works without a mouse or eyes                           | `D05 T02 §1`-`§5` · `D99 T01 §7`                          |
| Proven by tests, not by hope                               | `D05 T01 §1`-`§6`                                         |
| Users can learn it                                         | `D07 T01 §5`                                              |
| It installs clean                                          | `D07 T01 §6` · `D07 T01 §7`                               |

---

### Phase 0 -- Restore the Live Add-in and Move to Windows

The published add-in is dead for every user until its URLs follow the repository rename, and nothing else can be tested until the Windows clone sideloads.

|  ✔  | Section      | Deliverable                                              | Items |
| :-: | ------------ | -------------------------------------------------------- | :---: |
| [ ] | `D00 T01 §1` | Point every URL at the Gemail Pages path and redeploy    |   7   |
| [ ] | `D00 T01 §2` | Trust the dev certificates and provision a Windows clone |   5   |
| [ ] | `D00 T01 §3` | Normalize line endings after the move                    |   4   |
| [ ] | `D00 T01 §4` | Pin Node and prune dev dependencies                      |   4   |
| [ ] | `D00 T01 §5` | VS Code workspace for Windows and new Outlook            |   3   |

### Phase 1 -- Green Gates, the Runner, and the Test Backbone

Every later section cites these gates, so they must exist and be green before product work starts; the first tests characterize behavior the rename and the cutover must not break.

|  ✔  | Section      | Deliverable                                       | Items |
| :-: | ------------ | ------------------------------------------------- | :---: |
| [ ] | `D00 T02 §1` | Type check clean                                  |   6   |
| [ ] | `D00 T02 §2` | Prettier pass over the tree                       |   4   |
| [ ] | `D00 T02 §3` | Lint errors to zero                               |   5   |
| [ ] | `D00 T02 §4` | CI build workflow                                 |   6   |
| [ ] | `D00 T02 §5` | Strict TypeScript                                 |   6   |
| [ ] | `D00 T03 §1` | Wire the TODO gate into every clone               |   5   |
| [ ] | `D00 T03 §2` | Prove the review panel end to end                 |   7   |
| [ ] | `D00 T03 §3` | Raise the claims coverage floor                   |   4   |
| [ ] | `D00 T03 §4` | First push read back green                        |   6   |
| [ ] | `D00 T04 §1` | Move the curated agent skills into .claude/skills |   6   |
| [ ] | `D00 T04 §2` | An OpenRouter API skill                           |   7   |
| [ ] | `D05 T01 §1` | Jest configuration for UI and services            |   5   |
| [ ] | `D05 T01 §2` | An Office.js mock and outlook.ts tests            |   4   |
| [ ] | `D05 T01 §3` | Settings tests                                    |   4   |

### Phase 2 -- Rename to Gemail

The name changes before the provider does, so the cutover writes the new names once instead of twice.

|  ✔  | Section      | Deliverable                                      | Items |
| :-: | ------------ | ------------------------------------------------ | :---: |
| [ ] | `D01 T01 §1` | Package identity                                 |   4   |
| [ ] | `D01 T01 §2` | Manifest names and descriptions                  |   5   |
| [ ] | `D01 T01 §3` | Task pane and ribbon strings                     |   6   |
| [ ] | `D01 T01 §4` | Source identifiers and file headers              |   5   |
| [ ] | `D01 T01 §5` | Settings storage keys migrate to the Gemail keys |   6   |
| [ ] | `D01 T01 §6` | Documentation rebrand                            |   5   |
| [ ] | `D01 T01 §7` | Redirect stub for the old Pages path             |   6   |

### Phase 3 -- The OpenRouter Client

The client and its contract fixtures land beside the Gemini code before any caller moves.

|  ✔  | Section      | Deliverable                             | Items |
| :-: | ------------ | --------------------------------------- | :---: |
| [ ] | `D02 T01 §1` | Record the OpenRouter contract fixtures |   6   |
| [ ] | `D02 T01 §2` | Chat completions over fetch             |   7   |
| [ ] | `D02 T01 §3` | Streaming over SSE                      |   6   |
| [ ] | `D02 T01 §4` | Structured JSON output                  |   5   |
| [ ] | `D02 T01 §5` | The models catalogue                    |   5   |
| [ ] | `D02 T01 §6` | Key status                              |   3   |

### Phase 4 -- Provider Cutover

Every caller moves to OpenRouter and Gemini leaves the tree.

|  ✔  | Section      | Deliverable                                      | Items |
| :-: | ------------ | ------------------------------------------------ | :---: |
| [ ] | `D02 T02 §1` | A provider-neutral AI facade                     |   5   |
| [ ] | `D02 T02 §2` | Repoint every caller                             |   6   |
| [ ] | `D02 T02 §3` | OpenRouter settings and the Gemini key migration |   5   |
| [ ] | `D02 T02 §4` | The model picker                                 |   7   |
| [ ] | `D02 T02 §5` | Test Connection through the key endpoint         |   5   |
| [ ] | `D02 T02 §6` | Remove Google Gemini                             |   5   |
| [ ] | `D02 T02 §7` | Provider copy in the UI and docs                 |   7   |
| [ ] | `D02 T02 §8` | Reasoning and token budgets                      |   5   |
| [ ] | `D02 T02 §9` | Privacy routing setting                          |   5   |

### Phase 5 -- Task Pane Architecture and Import Defects

The split gives every later UI section a module to work in, and the defects are fixed in the modules rather than in the monolith.

|  ✔  | Section      | Deliverable                                              | Items |
| :-: | ------------ | -------------------------------------------------------- | :---: |
| [ ] | `D03 T01 §1` | Shared UI helpers                                        |   6   |
| [ ] | `D03 T01 §2` | The tab controller                                       |   5   |
| [ ] | `D03 T01 §3` | Draft and Reply panel modules                            |   5   |
| [ ] | `D03 T01 §4` | Summarize, Improve, Extract, and Translate panel modules |   4   |
| [ ] | `D03 T01 §5` | Settings, Rules, and Templates panels; a thin bootstrap  |   5   |
| [ ] | `D03 T01 §6` | One copy of every shared helper                          |   6   |
| [ ] | `D03 T01 §7` | Remove dead code                                         |   4   |
| [ ] | `D05 T03 §1` | Accept Changes replaces only what was improved           |   8   |
| [ ] | `D05 T03 §2` | Include original is honored                              |   4   |
| [ ] | `D05 T03 §3` | Refine starts from the edited preview                    |   4   |
| [ ] | `D05 T03 §4` | Rules reach refine prompts; Improve honors its focus     |   4   |
| [ ] | `D05 T03 §5` | Honest thread reading                                    |   5   |
| [ ] | `D05 T01 §4` | Feature module tests                                     |   5   |
| [ ] | `D05 T01 §5` | Ribbon command tests                                     |   5   |

### Phase 6 -- Performance and Resilience

With modules in place, streaming, lazy loading, and error recovery each touch one place.

|  ✔  | Section      | Deliverable                                 | Items |
| :-: | ------------ | ------------------------------------------- | :---: |
| [ ] | `D03 T02 §1` | Bundle baseline and budget                  |   5   |
| [ ] | `D03 T02 §2` | Production build hygiene                    |   6   |
| [ ] | `D03 T02 §3` | Lazy-load feature panels                    |   4   |
| [ ] | `D03 T02 §4` | Streaming output with Stop                  |   7   |
| [ ] | `D03 T02 §5` | One request at a time per action            |   4   |
| [ ] | `D03 T02 §6` | Email context cache per item                |   4   |
| [ ] | `D03 T02 §7` | Pre-warm the connection                     |   4   |
| [ ] | `D03 T02 §8` | Score on demand                             |   5   |
| [ ] | `D03 T03 §1` | Actionable errors with Retry                |   6   |
| [ ] | `D03 T03 §2` | Offline banner                              |   4   |
| [ ] | `D03 T03 §3` | Draft recovery after a reload               |   6   |
| [ ] | `D03 T03 §4` | Context-length handling                     |   5   |
| [ ] | `D03 T03 §5` | The debug log and response timing           |   6   |
| [ ] | `D03 T03 §6` | Office.js write callbacks and safe start-up |   5   |

### Phase 7 -- Security and Privacy

Hardening runs after the architecture settles so the CSP, the escaper, and the key storage are written against the final module layout.

|  ✔  | Section      | Deliverable                            | Items |
| :-: | ------------ | -------------------------------------- | :---: |
| [ ] | `D04 T01 §1` | Model output renders as text           |   5   |
| [ ] | `D04 T01 §2` | Prompt-injection fencing               |   5   |
| [ ] | `D04 T01 §3` | Content Security Policy                |   6   |
| [ ] | `D04 T01 §4` | The API key stays on the device        |   5   |
| [ ] | `D04 T01 §5` | Client-side rate limit and spend guard |   5   |
| [ ] | `D04 T01 §6` | First-run privacy notice               |   6   |
| [ ] | `D04 T01 §7` | Truthful privacy and security docs     |   5   |
| [ ] | `D04 T01 §8` | Dependency hygiene                     |   4   |

### Phase 8 -- Quality and Accessibility

Coverage is ratcheted and the pane meets WCAG 2.1 AA before new features add surface.

|  ✔  | Section      | Deliverable                       | Items |
| :-: | ------------ | --------------------------------- | :---: |
| [ ] | `D05 T01 §6` | Coverage ratchet in CI            |   4   |
| [ ] | `D05 T02 §1` | A name for every control          |   6   |
| [ ] | `D05 T02 §2` | Tab bar semantics and arrow keys  |   6   |
| [ ] | `D05 T02 §3` | Live regions and focus management |   6   |
| [ ] | `D05 T02 §4` | Reduced motion and a skip link    |   5   |
| [ ] | `D05 T02 §5` | Contrast check for the tokens     |   5   |

### Phase 9 -- Features

The operator-selected features build on the hardened, accessible pane.

|  ✔  | Section      | Deliverable                                     | Items |
| :-: | ------------ | ----------------------------------------------- | :---: |
| [ ] | `D06 T01 §1` | Settings sync through roamingSettings           |   6   |
| [ ] | `D06 T01 §2` | Creativity and length controls                  |   5   |
| [ ] | `D06 T01 §3` | Output language everywhere                      |   5   |
| [ ] | `D06 T01 §4` | Export and import settings                      |   5   |
| [ ] | `D06 T01 §5` | Model info and cost per request                 |   5   |
| [ ] | `D06 T02 §1` | A custom prompt library                         |   6   |
| [ ] | `D06 T02 §2` | Run a custom prompt on the message or selection |   5   |
| [ ] | `D06 T02 §3` | Keyboard shortcuts in the task pane             |   5   |
| [ ] | `D06 T03 §1` | Read attachments                                |   5   |
| [ ] | `D06 T03 §2` | Attachment-aware summaries and replies          |   5   |
| [ ] | `D06 T03 §3` | Thread timeline                                 |   5   |
| [ ] | `D06 T03 §4` | Smart CC suggestions                            |   6   |
| [ ] | `D06 T04 §1` | Follow the Office theme live                    |   6   |
| [ ] | `D06 T04 §2` | Dark theme contrast                             |   4   |
| [ ] | `D06 T04 §3` | Local usage stats                               |   5   |

### Phase 10 -- Release 2.0.0

Manifests, icons, the user guide, the tag, and the clean-install acceptance.

|  ✔  | Section      | Deliverable                                  | Items |
| :-: | ------------ | -------------------------------------------- | :---: |
| [ ] | `D07 T01 §1` | Requirement sets for new Outlook and the web |   7   |
| [ ] | `D07 T01 §2` | One manifest source and validation in CI     |   5   |
| [ ] | `D07 T01 §3` | Icons at every size from the SVG sources     |   5   |
| [ ] | `D07 T01 §4` | The release process                          |   4   |
| [ ] | `D07 T01 §5` | The user guide                               |   7   |
| [ ] | `D07 T01 §6` | Ship v2.0.0                                  |   7   |
| [ ] | `D07 T01 §7` | Clean-install acceptance                     |   5   |

### Phase 99 -- Operator

Steps only the operator can perform. Every row carries `**Requires:** operator`, so no runner takes one; each is done when its dependency has shipped and the operator has time.

|  ✔  | Section      | Deliverable                                  | Items |
| :-: | ------------ | -------------------------------------------- | :---: |
| [ ] | `D99 T01 §1` | Fund an OpenRouter key for development       |   4   |
| [ ] | `D99 T01 §2` | Dispatch the production deploy               |   3   |
| [ ] | `D99 T01 §3` | Create the legacy redirect repository        |   5   |
| [ ] | `D99 T01 §4` | Sign in the codex CLI                        |   3   |
| [ ] | `D99 T01 §5` | Gemail artwork                               |   4   |
| [ ] | `D99 T01 §6` | Test mailboxes in new Outlook and on the web |   4   |
| [ ] | `D99 T01 §7` | Screen reader pass                           |   4   |
| [ ] | `D99 T01 §8` | Update organization deployments              |   3   |
