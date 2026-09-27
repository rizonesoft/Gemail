---
schema_version: 1
id: agent-skills
domain: 00-workspace
status: draft
title: "TODO-04 -- Agent Skills Consolidation"
depends_on: []
---

# TODO-04 -- Agent Skills Consolidation

> **Goal:** One skills folder that Claude Code actually loads: the curated reference skills that lived under `.agent/skills/` sit beside the TODO runner skills in `.claude/skills/`, the Gemini skill is gone, and an OpenRouter API skill written from the OpenRouter documentation replaces it, so every later provider section has the wire format at hand.

> [!IMPORTANT]
> **Current state (verified 2026-09-27):** `.agent/skills/` holds 15 skills in 21 tracked files (`git ls-files .agent | wc -l` prints `21`): `accessibility-compliance-accessibility-audit`, `clean-code`, `code-review-excellence`, `debugging-strategies`, `email-systems`, `error-handling-patterns`, `gemini-api-dev`, `i18n-localization`, `javascript-pro`, `outlook-automation`, `prompt-engineering`, `security-audit`, `tailwind-design-system`, `typescript-pro`, and `web-performance-optimization`. Five carry a `resources/implementation-playbook.md` and `i18n-localization` carries `scripts/i18n_checker.py`. Each `SKILL.md` opens with YAML frontmatter naming `name` and `description`; `javascript-pro` and `typescript-pro` use a block-scalar (`|`) description. Claude Code loads project skills only from `.claude/skills/`, which holds the nine TODO runner skills ported from Photon (`add-todo`, `create-todo`, `groom-plan`, `plan-new-feature`, `process-phase`, `process-plan`, `process-todo-file`, `process-todo-section`, `review-todo-section`), so the `.agent` skills are loaded by nothing. No file outside `.agent/` references the folder. None of the `.agent` skills cites a section reference, so the skill-citation checks in `validate` (`skill-citation-unresolved`, `skill-citation-short-form`) will not fire when they move. `outlook-automation` describes the Composio Rube MCP, not Office.js.
<!-- claim: exists .agent/skills/gemini-api-dev/SKILL.md -->
<!-- claim: exists .agent/skills/i18n-localization/scripts/i18n_checker.py -->
<!-- claim: absent .claude/skills/typescript-pro/SKILL.md -->
<!-- claim: absent .claude/skills/openrouter-api/SKILL.md -->

## Inputs

- [`.agent/skills/`](../../.agent/skills/) -- the 15 skills §1 moves (14) or drops (`gemini-api-dev`)
- [`.claude/skills/`](../../.claude/skills/) -- the destination, beside the runner skills
- [`scripts/todo-validate.py`](../../scripts/todo-validate.py) -- the skill-citation scan over `.claude/skills/*/SKILL.md`, which every moved file must pass
- [`todo/README.md`](../README.md) -- "Skills under `.claude/skills/` may cite only full `DNN TNN §N` refs, and only to live sections"
- Claude Code documentation, "Agent Skills" (https://docs.claude.com/en/docs/claude-code/skills) -- the folder layout and frontmatter fields a skill needs
- OpenRouter documentation (https://openrouter.ai/docs) -- the API reference pages §2 summarizes: API reference overview, streaming, errors, structured outputs, provider routing, models, and the key endpoint

## Outcome

- `.agent/` no longer exists, and `.claude/skills/` holds the 9 runner skills, the 14 moved skills, and `openrouter-api`: 24 folders, each with a `SKILL.md` whose frontmatter parses and whose `name` equals its folder name.
- `python scripts/todo-graph.py validate` reports no `skill-citation-*` finding.
- `.claude/skills/openrouter-api/SKILL.md` states, with a source URL per claim, the request and response shapes Gemail uses: chat completions, SSE streaming, error bodies and status codes, structured outputs, the models list, the key endpoint, and provider routing including `data_collection`.

**Adjacency:** all=not-applicable (agent reference material for developers, with no user-facing records, settings, documents, or reversible user actions)

## Implementation Order

| Order | Section | Deliverable                                          | Depends On | Status |
| :---: | :-----: | ---------------------------------------------------- | ---------- | :----: |
|   1   |   §1    | Move the curated agent skills into .claude/skills    | --         |  [ ]   |
|   2   |   §2    | An OpenRouter API skill                              | §1         |  [ ]   |

---

## 1. Move the Curated Agent Skills into .claude/skills

The `.agent/skills/` folder came from another agent harness and nothing in this repository loads it. Moving the useful skills into `.claude/skills/` makes them available to every session; the Gemini skill goes, because the provider leaves the tree in `02-openrouter` and a skill teaching the old SDK would mislead the sessions doing that work (operator decision 2026-09-27: "Migrate & retire").

- [ ] `git mv` each of the 14 kept skill folders from `.agent/skills/<name>` to `.claude/skills/<name>`, including their `resources/` and `scripts/` subfolders. Done when: `ls .claude/skills | wc -l` prints `23` and `git status --short | grep -c '^R'` counts one rename per moved file (20).
- [ ] `git rm -r .agent/skills/gemini-api-dev` and remove the now-empty `.agent/`. Done when: `test ! -e .agent` exits 0.
- [ ] Check every moved `SKILL.md` frontmatter parses and its `name` equals its folder: `python -c` over `.claude/skills/*/SKILL.md` reading the block between the first two `---` lines and asserting a `name:` equal to the folder and a non-empty `description:` (block scalars included). Done when: the check prints `23 ok`.
- [ ] Record the `outlook-automation` decision: it documents the Composio Rube MCP, which Gemail does not use; either keep it with one sentence added under its heading saying it is not the Office.js add-in API, or drop it, and say which in the commit body. Done when: the skill either carries that sentence or is absent.
- [ ] Run `python scripts/todo-graph.py validate`. Done when: it reports no `skill-citation-unresolved` or `skill-citation-short-form` finding.
- [ ] Commit: `"workspace: move the curated agent skills into .claude/skills"`

**Test checkpoint:** `test ! -e .agent` exits 0; `ls .claude/skills | wc -l` prints `23`; the frontmatter check prints `23 ok`; `python scripts/todo-graph.py validate` shows no `skill-citation-*` class; `git log --follow --oneline -1 -- .claude/skills/typescript-pro/SKILL.md` shows history carried through the rename. Cheaper substitute that fails: copying the folders and leaving `.agent/` in place, which fails the `test ! -e .agent` check and keeps a second, stale copy of every skill.

## 2. An OpenRouter API Skill

Every section in `02-openrouter` and several in `03-architecture` and `06-features` build against the OpenRouter wire format. A skill written once from the documentation, with a source URL on each claim, gives those sessions the shapes without each re-reading the site, and gives review one place to check against. It is reference material, not code: the contract fixtures of `02-openrouter` remain the proof of what the endpoint actually sends.

- [ ] Create `.claude/skills/openrouter-api/SKILL.md` with frontmatter `name: openrouter-api` and a `description` that says when to use it (building or reviewing any call to `https://openrouter.ai/api/v1`). Done when: the frontmatter check from §1 prints `24 ok`.
- [ ] Write the "Chat completions" part: `POST /api/v1/chat/completions`, the `Authorization: Bearer` header, the optional `HTTP-Referer` and `X-Title` attribution headers, the request fields Gemail uses (`model`, `messages`, `temperature`, `max_tokens`, `stream`, `response_format`, `reasoning`, `provider`, `usage`), and the response shape (`choices[0].message.content`, `finish_reason`, `usage`). Source: https://openrouter.ai/docs/api-reference/chat-completion. Done when: each field line carries its source URL.
- [ ] Write the "Streaming" part: SSE `data:` lines, the `: OPENROUTER PROCESSING` comment lines to ignore, `data: [DONE]`, the delta shape, a mid-stream error delivered as a chunk, and cancellation by aborting the request. Source: https://openrouter.ai/docs/api-reference/streaming. Done when: the part names all five behaviors with the source URL.
- [ ] Write the "Errors" part: the `{"error": {"code", "message", "metadata"}}` body and the status codes 400, 401, 402, 403, 408, 429, 502, and 503 with what each means for a caller (retryable or not). Source: https://openrouter.ai/docs/api-reference/errors. Done when: the table has eight rows, each with a retry verdict.
- [ ] Write the "Structured outputs", "Models", "Key", and "Provider routing" parts: `response_format` with `type: json_schema` and `strict`, the `supported_parameters` field of `GET /api/v1/models` that says which models accept it, the fields of a model entry Gemail reads (`id`, `name`, `context_length`, `pricing`, `architecture.output_modalities`), `GET /api/v1/key` and its fields, and `provider.data_collection: "deny"`. Sources: https://openrouter.ai/docs/features/structured-outputs, https://openrouter.ai/docs/api-reference/list-available-models, https://openrouter.ai/docs/api-reference/get-current-api-key, https://openrouter.ai/docs/features/provider-routing. Done when: each part cites its page and the date it was read.
- [ ] Add a closing "Gemail rules" part restating the `AGENTS.md` decisions the skill must not contradict: `fetch` only with no SDK, the user's own key kept on the device, no other host, and the fixtures as the proof of record. Done when: the part cites `AGENTS.md`.
- [ ] Commit: `"workspace: an OpenRouter API reference skill"`

**Test checkpoint:** `.claude/skills/openrouter-api/SKILL.md` exists with valid frontmatter (`24 ok`); `grep -c "https://openrouter.ai/docs" .claude/skills/openrouter-api/SKILL.md` prints at least `7`; `python scripts/todo-graph.py validate` shows no `skill-citation-*` class; every status code in the errors table appears on the cited errors page when read on the stamp date. Cheaper substitute that fails: renaming `gemini-api-dev` to `openrouter-api` with the provider name swapped, which leaves Gemini request shapes (`contents`, `generationConfig`) that the `grep` for the OpenRouter field names and the per-claim source URLs expose.

## Verification

- [ ] `pwsh scripts/check-all.ps1` -- the TODO gates pass, with no `skill-citation-*` finding
- [ ] `test ! -e .agent` and 24 folders under `.claude/skills/`, each with frontmatter whose `name` equals the folder
