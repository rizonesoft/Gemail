# AGENTS.md

Agent instructions for this repository. Human orientation lives in `README.md`. Claude Code loads this file through the `CLAUDE.md` import stub.

## What this project is

**Gemail** is an open-source AI email assistant for Microsoft Outlook, published by Rizonesoft: a task pane and ribbon add-in that drafts, replies, summarizes, improves, translates, and extracts actions from email, with the model calls going to **OpenRouter** under the user's own API key. It was called "AI Compose" / "AI Email Writer" (`ai-email-writer`) and ran on Google Gemini until the operator's decisions of 2026-09-27; `todo/01-rebrand/` and `todo/02-openrouter/` carry that migration.

| Path | Purpose |
| ---- | ------- |
| `src/taskpane/` | The task pane: `taskpane.html` (markup), `taskpane.ts` (wiring), `taskpane.css` |
| `src/commands/` | Ribbon command handlers (`Office.actions.associate`) and their host page |
| `src/features/` | One module per feature (draft, reply, summarize, improve, translate, extract actions) plus `settings.ts`, the settings service |
| `src/services/` | Shared services: the AI provider client, the Outlook (Office.js) wrapper |
| `src/prompts/` | Prompt templates and the prompt builder |
| `src/styles/` | Tailwind CSS v4 entry |
| `manifest.xml`, `manifest.dev.xml` | The production and development add-in manifests (XML, Mailbox requirement sets) |
| `assets/` | Icons referenced by the manifests, the README banner |
| `scripts/` | `check-all.ps1` (every gate), `sync-manifest-version.js`, the live smoke script, the stdlib Python TODO tooling (`todo-graph.py`, validator, claims, findings, runs, review prompt, panel slots, the campaign guard and its Stop hook), the unattended launcher and preflight, `toolchain-check.py`, and their tests under `scripts/tests/` |
| `tools/` | `provision.ps1` (sets up a Windows clone: Node, deps, dev certs, the commit hook, Python), `githooks/pre-commit`, and `wsl-native.py` (adds the Linux native binaries the unattended run in WSL needs) |
| `todo/` | The live execution plan; read `todo/README.md` before authoring or implementing |
| `todo/implementation-plan.md` | Ordered phase plan; its boxes are synchronized through `scripts/todo-graph.py` |
| `todo/budget.json`, `todo/backlog.md` | The caps on campaign discovery and the backlog, with their history; the capped list of deferred ideas that are not sections |
| `docs/design/` | The approved design: `mockup.md` and the imported artboards and renders under `mockup/` (layout), `tokens.json` (every value), `icons.md` (the icon catalog), `taskpane.md` (behavior), `EDITING.md` (how to change it); every surface section cites `mockup.md` |
| `assets/icons/` | Icon sources (`src/`, canonical), rendered PNGs (`png/`), and the hash manifest; `src/ui/icons.ts` is the generated pane-icon registry |
| `tools/design/` | Design tooling with its own `package.json`: `icons.mjs` (icon build and check), `render-mockup.mjs` (mockup renders); never an add-in dependency |
| `docs/user/`, `docs/dev/` | The user guide and developer documentation |
| `docs/reviews/` | Per-section review findings, attestations, the derived findings ledger, run records |
| `docs/phase-runs/` | One findings file per phase run, written as the run goes |
| `docs/captures/taskpane/` | Committed captures of rendered surfaces, the visual reference for review |
| `.claude/` | Claude Code skills, subagents (`agents/`), rules, and settings (which wire the campaign Stop hook) |
| `.conclave/` | `panel.toml` (the review panel wiring: writer, model registry, and every review slot), `unattended.json` (the unattended run profile), `toolchain-web.json` (the Node pins), and `kits.json` (what the Conclave-SDK kits installed) |
| `dist/` | Webpack output; ignored, deployed by `.github/workflows/deploy.yml` to GitHub Pages, never authoritative |
| `build/` | Scratch, caches, and campaign guard state; ignored, never authoritative |

Development happens on Windows (the repository moved from WSL to Windows on 2026-09-27); CI runs on Linux. The TODO tooling is stdlib Python 3 (`python` on Windows) and needs no install step. Run `pwsh tools/provision.ps1` once after cloning.

## The decisions this project runs on

- **Supported clients** (operator decision 2026-09-27: "New Outlook + web"): new Outlook for Windows and Mac, and Outlook on the web, which share one web runtime. Classic Outlook for Windows is discontinued (operator decision 2026-11-15: "Outlook classic is giving us alot of issues, so discontinue the outlook classic plugin"): the add-in detects it and shows a not-supported notice instead of running (`D05 T03 §6`), it is never tested beyond that notice, and nothing else spends effort on it. Mobile is out of scope.
- **AI provider** (operator decision 2026-09-27: "BYO key, fetch, live models"): OpenRouter only, called with plain `fetch` against `https://openrouter.ai/api/v1` (no SDK in the bundle), streaming over SSE, under the user's own OpenRouter API key, with the model picker populated from `/api/v1/models` around a curated default. The default models are chosen by the section that builds the picker from the live catalogue, not fixed here. No second provider and no server of our own.
- **Name and hosting** (operator decision 2026-09-27: "Full, with a redirect"): the product, package, UI, manifests, and docs are **Gemail**; the add-in is served from `https://rizonesoft.github.io/Gemail/` (production) and `/Gemail/dev/` (development). The manifest `<Id>` values stay unchanged so existing installs update in place, and the old `/ai-email-writer/` path is covered for the transition. Stored settings migrate from the old keys, never reset.
- **Stack:** TypeScript (strict), Office.js with vanilla DOM (no UI framework), Tailwind CSS v4, webpack 5, Babel, Jest 30, office-addin-lint (ESLint and Prettier). **A dependency is a decision:** adding a package records the reason in the section that adds it.
- **The user's mail first:** nothing is sent on the user's behalf; every write into a message is previewed and happens only on an explicit user action; replaced text stays recoverable. Model output is text until sanitized, never raw HTML.
- **The key is the user's:** the OpenRouter key lives only on the user's device and travels only to OpenRouter; it never enters a log, a URL, telemetry, or a tracked file.
- **The approved design is binding** (operator decisions 2026-09-27; the design itself replaced on 2026-11-15: "Most definately A", the Fluent Native direction, artifact https://claude.ai/artifact/Vc5xq9U5iRvq1AiZ1gm5YD): the mockup imported from the operator's design artifact (`docs/design/mockup.md`) is the visual source of truth, `docs/design/tokens.json` holds every value, and the icons are the Fluent-style set in `assets/icons/src/` (flat Fluent color on a shared document base for the ribbon, the menu, and the letter-with-spark app icon; Fluent 2 regular at a 1.5 px stroke for the pane). The pane is a fixed frame: header and tabs at the top, scrolling content, and an action bar pinned at the bottom that always holds the primary action. The contract is `docs/design/README.md` ("The contract"): one origin, the operator decides, tokens only, registry icons only, purple means AI, a capture proves it. The font is Segoe UI Variable, the system font; no web font is loaded. Enforcement is a hard gate: `python scripts/design-lint.py` in the commit hook, check-all, and CI refuses a surface section that does not cite the mockup, a hand-edited artboard, a stale icon output, and any new color literal, font declaration, inline `<svg>`, or legacy icon path in `src/`. The design changes only in the artifact and reaches the repository only through the `design-sync` skill.
- **Manifest:** stays the XML add-in manifest; the unified (JSON) manifest is a backlog entry, not planned work (operator decision 2026-09-27).
- **Trunk and deploys** (operator decision 2026-09-27): runners push to `main`; every push to `main` deploys the development build to `/Gemail/dev/`; production deploys only through the `deploy` workflow's manual `deploy_prod` dispatch, which is the operator's.
- **Plan-level calls** (operator decisions 2026-09-27): the brand blue and tertiary text tokens darken to the nearest shades that pass WCAG 4.5:1 (`D05 T02 §5`); the dev deploy runs only after the `build` workflow passes (`D00 T02 §4`); Reply's "Include original" decides whether the original message is sent to the model as context (`D05 T03 §2`).
- **Ownership:** copyright Rizonetech (Pty) Ltd; Rizonesoft is the publisher users see. MIT licensed.

## The TODO system

`todo/` is the live execution plan; **format spec: `todo/README.md`.** Markdown is canonical and `build/` holds derived, gitignored projections. The system was ported from Photon on 2026-09-27 (operator decision: "Photon"), with its skills, scripts, hook, and review panel.

Domains are flat-numbered from `00`, allocated in order, and read from the tree: `00-workspace` (toolchain, gates, CI, this system, the WSL-to-Windows move), `01-rebrand`, `02-openrouter`, `03-architecture`, `04-security`, `05-quality`, `06-features`, `07-release`, and `99-manual` (operator-only rows no agent session can perform). Numbers are stable addresses: a new domain appends after the last one. `todo/TODO-00-INDEX.md` is the authority for which exist.

**Operator planning is unbounded; campaign discovery is capped.** Sections the operator asks for in an attended session carry nothing extra and no limit applies to them. A section a campaign files on its own carries `**Origin:** discovered run=<run id> <YYYY-MM-DD>` under its heading, must pass the admission test in `todo/README.md` ("The budget and the backlog"), and counts against `per_run_discovered_sections` in `todo/budget.json` (15 per run); overflow goes into open sections as items or to `todo/backlog.md` (capped at 500, never runnable). Only the operator raises a cap, in words a new history entry quotes.

Files are `todo/NN-domain/TODO-NN-short-name.md`. The **Implementation Order table is the dependency graph**: every `## N.` section has exactly one row and vice versa, and a row flips to `[x]` only when a `Verified:` stamp covers it. Cross-references use section marks in the forms `§N`, `TNN §N`, and `DNN TNN §N` as spelled out in `todo/README.md`, and must be bidirectional. Every section sits in exactly one phase table of `todo/implementation-plan.md`.

## Choose the work contract

For TODO work, read the target section, `todo/README.md`, its dependencies, and the applicable skill under `.claude/skills/`: capture through `add-todo`, author a file through `create-todo`, change or import the design through `design-sync`, plan a new feature through `plan-new-feature`, build through `process-todo-section` (gate card: `.claude/skills/process-todo-section/gates.md`), stamp through `review-todo-section`, close a file through `process-todo-file`, run a phase or the plan through `process-phase` or `process-plan`, harden the tree through `groom-plan`.

The lifecycle is: capture, author, validate the plan and source claims, record `Started:`, implement, run the section's gates, commit, independent review, panel review and stamp, then sync the plan. Each section must be executable with zero conversation context. **One section = one commit.** Preserve section addresses and bidirectional cross-references. A TODO Implementation Order row turns `[x]` only with its `Verified:` stamp through the review skill. Do not rewrite a stamped checklist or transfer evidence across changed candidates. File new work with its own owner and dependency.

`/process-plan` is the campaign front door: it audits the plan, starts the run guard (the Stop hook in `.claude/settings.json`, the guard file under `build/`, and a heartbeat job), and runs phase after phase until every row is shipped, parked, or blocked.

**Unattended runs** (Conclave-SDK `unattended` kit, imported 2026-11-15) start `process-plan` in a tmux session in WSL on this checkout (`/mnt/d/Gemail`): `python3 scripts/unattended-run.py start | status | attach | stop`, or the `Gemail Claude campaign` desktop shortcut. The profile is `.conclave/unattended.json`, the seed prompt `docs/unattended-prompt.md`, and the operator's page `docs/unattended-run.md`; `python3 scripts/unattended-preflight.py` must print no FAIL first. After a Windows `npm ci`, run `python3 tools/wsl-native.py` in WSL again (the preflight's `linux-binaries` check names it). A run never restarts itself.

## What counts as proof

A Test checkpoint cites one or more of five proofs, spelled out in `todo/README.md`:

1. **Builds clean**: `npm run build` with no new warning, and `npx tsc --noEmit` exit 0.
2. **Static analysis clean**: nothing new from `npm run lint` on the touched files.
3. **Unit test**: a Jest test, cited by name.
4. **Driven run with evidence**: the add-in sideloaded into new Outlook or Outlook on the web, the surface driven, and a console line, a settings readback, the inserted text, or a capture under `docs/captures/taskpane/` recorded.
5. **API contract proof**: a committed OpenRouter response fixture (JSON or SSE) replayed through the client with `fetch` mocked, and the parsed result asserted. Every change to the request or response shape owes this one.

A checkpoint citing a gate that does not exist yet is unfalsifiable and is not allowed.

## Working rules

- **Output discipline:** bound every command (`npm run build` filtered to errors, `npx jest <path>`, `tail`/`head` on logs, field extraction on JSON). Keep full logs in ignored scratch under `build/`.
- **Act, then report:** complete authorized work and report evidence. Explicit operator stop instructions take effect immediately.
- **Ask when it is the operator's call:** the operator asked for questions over guesses (2026-09-27). A decision that changes what ships (a dependency, a supported client, a default model, a data-handling rule) is asked in an attended session; an unattended run records a justified default instead and carries on.
- **One writer, and it never reviews itself:** Claude Code is the only writer (operator decision); every other model takes part only as a headless reviewer through a slot in `.conclave/panel.toml`, run by `python scripts/panel_slots.py exec <slot>` (GPT review slots run through the `codex` CLI). `scripts/panel_slots.py` refuses a table where any slot shares the writer's family. There are no fallback slots: a failed round waits for the operator. Skills name slots, never models.
- **Writes are serial:** one session owns the working tree. Check `git status` before building over unfamiliar work.
- **Section atomicity is the candidate range:** one section ships as one logical change, and review fix-loop commits append to that range (never amend); the stamp names the whole range.
- **Shared deliberately:** a behavior two features need moves into `src/services/` or `src/ui/` once, and is never reimplemented in a second feature module; nothing moves there speculatively.
- **Every surface answers to the approved mockup** (`docs/design/mockup.md` and its renders; the contract is in `docs/design/README.md`), built from tokens (`docs/design/tokens.json`) and registry icons (`iconSvg()` in `src/ui/icons.ts`), and proven by a capture under `docs/captures/taskpane/` compared with the render it cites. A surface never hardcodes a color, font, size, spacing value, or icon.
- **No em dashes** in authored prose; use `--`, a colon, or a new sentence. One line per paragraph and list item in Markdown.
- **Source of truth:** OpenRouter behavior via its API reference (openrouter.ai/docs); Office.js and manifest behavior via Microsoft Learn; competitor behavior via a driven run with its version; plan state via `todo/`. Disagreements are recorded decisions, not silent reinterpretations.
- **Completion-first, no partial ships:** a section is complete only when every micro-step is `[x]`, its checkpoint is quoted from a real run, and review stamped it. Anything genuinely unshippable now files through `add-todo` with an owner.

## The commit hook

`tools/githooks/pre-commit` refuses a commit whose **staged** tree fails `python scripts/todo-graph.py validate`, checked in a temp checkout of the index. It must stay a POSIX shell script with LF endings and index mode `100755`. `tools/provision.ps1` points `core.hooksPath` at `tools/githooks`; run it once after cloning. A red hook is a defect to fix, never a gate to skip.

## A measurement recorded is a measurement re-checked

`validate` proves the tree is internally consistent. It cannot tell whether a `Current state` block is still **true**. So **a TODO that measures something records it as a claim**, and `scripts/todo-claims.py` re-measures it:

```
<!-- claim: exists src/services/gemini.ts -->
<!-- claim: absent src/services/openrouter.ts -->
<!-- claim: lines src/taskpane/taskpane.ts = 1570 -->
```

**When a claim goes stale the TODO is wrong, not the repository.** Fix the claim and the sentence it supports in the same commit.

## Unknowns and questions

Answer from source first: the code, the OpenRouter API reference, Microsoft Learn, or a driven run. When an unanswered question would change implementation, ask the operator in an attended session; in an unattended run take a justified default, record that it is a default with its cost of changing, and carry on.

## Validation

```powershell
pwsh scripts/check-all.ps1                   # build, typecheck, lint, tests, manifest, and every TODO gate
npm run build                                # the webpack production build alone
npx jest --ci                                # the whole suite; iterate with a path or -t
pwsh tools/provision.ps1 -Verify             # the Windows toolchain, dev certs, and hook
```

```bash
python scripts/todo-graph.py self-test       # must stay green; the run prints its own total
python scripts/todo-graph.py validate        # FATAL blocks; new WARN blocks until fixed or accepted
python scripts/todo-graph.py plan --sync     # re-derive the plan projection after TODO edits
python scripts/todo-graph.py plan --check    # fail if the projection went stale
python scripts/todo-graph.py query ready     # dependency-safe work right now
python scripts/todo-graph.py query stats     # tree health
python scripts/todo-graph.py resolve 'DNN TNN §N'   # ref -> file, section, deps, status
python scripts/todo-claims.py                # re-measure what the TODOs claim about the repo
python scripts/todo-findings.py --check      # fail if docs/reviews/findings.md is stale
python scripts/todo-runs.py --check          # run records agree with the review files
python scripts/campaign_guard.py --self-test # the wired Stop hook command against a scratch run
python -m unittest discover -s scripts/tests  # the run guard, the CI repair ledger, the unattended kit, wsl-native
python3 scripts/unattended-preflight.py      # in WSL: every precondition of an unattended run
python scripts/panel_slots.py validate       # the review panel wiring holds
python scripts/design-lint.py                # the design gate: mockup citations, tokens, icons, baseline
node tools/design/icons.mjs --check          # icon outputs match their sources (npm ci --prefix tools/design once)
node tools/design/render-mockup.mjs          # re-render the mockup after a design-sync
```

Run checks owed by the task. Report only commands actually run, and distinguish static evidence, test output, driven-run output, contract output, and review proof.

Use trunk-based `main` for routine work and concise imperative commits. Never bypass hooks with `--no-verify`, amend a recorded candidate, or force-push.

## Credentials

Credentials never enter tracked files, arguments, logs, or handoff prose. The developer's OpenRouter key for the live smoke lives in `.env` (gitignored) as `OPENROUTER_API_KEY`; a user's key lives only in their Outlook client.
