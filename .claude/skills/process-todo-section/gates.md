# Section gates

The gate card for `process-todo-section`, `review-todo-section`, and `process-todo-file`. When `docs/dev/testing.md` exists and disagrees with this card, the file wins, and this card is corrected in the same commit.

Quote the exit code, the passed, failed, and skipped counts, and the last lines of output. Leave the full log under `build/` (gitignored), never in the context.

## Every section: the one-command sweep

```powershell
pwsh scripts/check-all.ps1
```

It runs the webpack production build, `tsc --noEmit`, `npm run lint` (office-addin-lint: ESLint and Prettier), `jest --ci`, `npm run validate` (the manifest), and the TODO gates (`todo-graph.py self-test`, `validate`, `plan --check`, `todo-claims.py`, `todo-findings.py --check`, `todo-runs.py --check`, `campaign_guard.py --self-test`, and the script tests `python -m unittest discover -s scripts/tests`). Every gate runs even after an earlier one fails, and it prints a table of gate results; green means exit 0 with every gate `PASS`. A `SKIP` row (no Python, a script absent) is not green: quote it and fix the cause. `-SkipBuild` reuses the last build while iterating, never for the commit-time run; `-SkipManifest` skips the online manifest validator and is quoted as a skip when used.

Until `D00 T02` ships, the typecheck and lint gates are red on the imported tree. A section that ships before them quotes both as known-red with their error counts, and must not raise either count.

## Every section: the design gate

```powershell
python scripts/design-lint.py
```

It is part of `check-all.ps1`, the commit hook, and CI, and it never baselines a plan defect: a surface section missing its `docs/design/mockup.md` citation or conformance item is FATAL, as is a stale icon output, a hand-edited artboard, or a stale render. The code rules (color literals, font declarations, inline `<svg>`, pre-2.0 icon paths) are ratcheted by `docs/design/.lint-baseline.json`: a section that removes a violation shrinks it in the same commit (`--update-baseline`), and nothing may raise it. A section that touches `assets/icons/src/` runs `node tools/design/icons.mjs` and commits the outputs; one that touches `docs/design/mockup/` goes through the `design-sync` skill.

## Every code section: the whole suite

```powershell
npx jest --ci
```

Green means zero failed. Skipped tests (`it.skip`, `describe.skip`) are quoted by name with their reason; a skip with no reason is a failure of the test, not a pass. While iterating, narrow to the touched tests:

```powershell
npx jest src/services/openrouter.test.ts -t "<name>"
```

The filtered run is iteration only. The commit-time quote comes from the unfiltered run at the commit being created.

## OpenRouter sections: API contract proof

A section that changes the request or response shape of the OpenRouter client re-runs its contract tests unfiltered: committed fixtures of real OpenRouter responses (JSON bodies and SSE streams, recorded with the key and any personal content redacted) replayed through the client with `fetch` mocked, and quotes the per-fixture result. A live smoke against the real endpoint (`npm run test:live`, `**Needs:** OpenRouter API key (live test)`) is a supplement, never the proof: a live model's output cannot be asserted.

## Surface sections: the mockup comparison

Every surface section captures what it built under `docs/captures/taskpane/` and compares it with the `docs/design/mockup/renders/` image of each anchor its `**Design:**` line cites: order, spacing, labels, icons, colors, and states. The comparison is quoted in the commit body (match, or each difference with the `**Design deviation:**` that records it).

## Surface sections: sideload smoke

Gemail has no automated UI suite yet. Until one ships, a section that builds or changes a surface owes a driven sideload smoke by hand, in a display session (`**Requires:** display-session`) with an Outlook client (`**Needs:** Outlook client (sideload)`):

1. `npm run dev-server`, then sideload `manifest.dev.xml` into Outlook on the web (aka.ms/olksideload) and into new Outlook; the dev certificates must be trusted (`pwsh tools/provision.ps1 -Verify`).
2. Open a message in read mode and a compose form, drive every control the section accounts for, including the failure paths it names (no key, offline, read mode).
3. Record the evidence: the task pane loaded in both clients, the browser console for the run carries no uncaught error (quote the count), and a capture of the changed surface is committed under `docs/captures/taskpane/`.

A sideload smoke is evidence of one run. It never substitutes for a unit test on the logic behind the surface, and when a UI suite lands this section of the card is replaced, not kept beside it.

## Manifest sections: validate both manifests

A section that changes `manifest.xml` or `manifest.dev.xml` runs `npx office-addin-manifest validate` on each and quotes the verdict, and re-reads every URL the manifest names (`curl -s -o /dev/null -w '%{http_code}'`) once the change is deployed.

The file-level full suite, every contract fixture, and the sideload smoke in both clients belong to `process-todo-file`.
