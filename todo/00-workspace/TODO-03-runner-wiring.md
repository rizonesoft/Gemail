---
schema_version: 1
id: runner-wiring
domain: 00-workspace
status: draft
title: "TODO-03 -- Runner Wiring and the First Green Push"
depends_on: []
---

# TODO-03 -- Runner Wiring and the First Green Push

> **Goal:** The plan polices itself on every clone and every push, and the machinery a section run leans on is proven before the first stamp depends on it: the commit hook refuses a broken staged tree, every review slot has answered a probe, the claims ratchet sits at what the tree measures, and the first push after the gates land comes back green from both `plan-gates` and `build`.

> [!IMPORTANT]
> **Current state (verified 2026-09-27):** The TODO tooling under `scripts/`, the skills under `.claude/skills/`, `.conclave/panel.toml`, `tools/githooks/pre-commit`, `tools/provision.ps1`, and `.github/workflows/plan.yml` were ported from Photon on 2026-09-27 and are untracked (`git status` lists them as `??`). `git ls-files -s tools/githooks/pre-commit` prints nothing, so the hook has no index mode and no clone runs it; `git config core.hooksPath` is unset on this clone. `git check-attr eol -- tools/githooks/pre-commit` already prints `eol: lf`. `python scripts/panel_slots.py validate` prints `panel slots ok: writer claude-opus-5-5 (claude), 7 slots, 7 registered models`, the slots being `bulk`, `signoff`, `depth`, `plan-primary`, `stamp-check`, `independent`, and `arch-primary`; `codex --version` prints `codex-cli 0.157.0` and `codex login status` prints `Logged in using ChatGPT`, but no review round has run in this repository and `docs/reviews/run-records.md` records none. `scripts/todo-claims.py` sets `COVERAGE_FLOOR = 1`, the value carried from Photon's port.
<!-- claim: exists tools/githooks/pre-commit -->
<!-- claim: exists .conclave/panel.toml -->
<!-- claim: count "^COVERAGE_FLOOR = 1$" scripts/todo-claims.py = 1 -->
<!-- claim: count "No runs are recorded yet" docs/reviews/run-records.md = 1 -->
<!-- claim: exists .github/workflows/plan.yml -->

## Inputs

- [`tools/githooks/pre-commit`](../../tools/githooks/pre-commit) -- the hook §1 wires in; it validates the staged tree in a temp checkout
- [`tools/provision.ps1`](../../tools/provision.ps1) -- its `hooks` leg sets `core.hooksPath` (§1)
- [`.conclave/panel.toml`](../../.conclave/panel.toml) and [`scripts/panel_slots.py`](../../scripts/panel_slots.py) -- the review panel §2 proves
- [`docs/reviews/run-records.md`](../../docs/reviews/run-records.md) and [`scripts/todo-runs.py`](../../scripts/todo-runs.py) -- where §2 records the probe
- [`scripts/todo-claims.py`](../../scripts/todo-claims.py) -- `COVERAGE_FLOOR`, which §3 raises
- [`.github/workflows/plan.yml`](../../.github/workflows/plan.yml) -- the `plan-gates` workflow §4 reads back
- [`scripts/review_prompt.py`](../../scripts/review_prompt.py) -- `ci-wait`, the read-back command §4 uses
- -> XREF: D00 T02 §4 -- creates the `build` workflow §4 reads back
- -> XREF: D99 T01 §4 -- the operator signs in the codex CLI when §2 finds it signed out

## Outcome

- `git ls-files -s tools/githooks/pre-commit` prints mode `100755`, and a provisioned clone refuses a commit whose staged tree fails `python scripts/todo-graph.py validate`.
- Every slot in `.conclave/panel.toml` has run once against a planted-typo probe, and the probe is recorded in `docs/reviews/run-records.md` with `python scripts/todo-runs.py --check` exiting 0.
- `COVERAGE_FLOOR` equals the number of `Current state` blocks carrying a claim on the day §3 ships.
- The first push after `D00 T02 §4` has a green `plan-gates` run and a green `build` run for the same sha, quoted by URL in `docs/dev/ci.md`.

**Adjacency:** all=not-applicable (repository plumbing: the commit hook, the review panel, the claims ratchet, and CI read-back, with no user-facing records, settings, documents, or reversible user actions)

## Implementation Order

| Order | Section | Deliverable                          | Depends On     | Status |
| :---: | :-----: | ------------------------------------ | -------------- | :----: |
|   1   |   §1    | Wire the TODO gate into every clone  | --             |  [ ]   |
|   2   |   §2    | Prove the review panel end to end    | --             |  [ ]   |
|   3   |   §3    | Raise the claims coverage floor      | --             |  [ ]   |
|   4   |   §4    | First push read back green           | §1, D00 T02 §4 |  [ ]   |

---

## 1. Wire the TODO Gate into Every Clone

The hook is the only gate that runs before a commit exists, so a tree that fails `validate` never reaches the remote. It must stay a POSIX shell script with LF endings and index mode `100755`, because Git for Windows runs hooks under its own `sh` and does not keep the executable bit from the working tree.

- [ ] Stage `tools/githooks/pre-commit` and record it executable with `git update-index --add --chmod=+x tools/githooks/pre-commit`. Done when: `git ls-files -s tools/githooks/pre-commit` prints mode `100755`. Cheaper substitute: relying on the working-tree file mode, which Windows does not keep.
- [ ] Confirm `.gitattributes` pins `tools/githooks/**` to `eol=lf`. Done when: `git check-attr eol -- tools/githooks/pre-commit` prints `eol: lf` and `git show :tools/githooks/pre-commit | grep -c $'\r'` prints `0`.
- [ ] Run `pwsh tools/provision.ps1` so its `hooks` leg sets `git config core.hooksPath tools/githooks`. Done when: `git config core.hooksPath` prints `tools/githooks` and `pwsh tools/provision.ps1 -Verify` reports `ok` for `hooks`.
- [ ] Prove the refusal: stage a scratch edit to `todo/00-workspace/TODO-03-runner-wiring.md` that changes the §4 Depends On cell to `T07 §3` and run `git commit`. Done when: the commit exits non-zero with `pre-commit: todo-graph validate is red on the staged tree` after the validator's `does not resolve` FATAL, and the same commit succeeds once the edit is reverted; both outputs are quoted in the commit body.
- [ ] Commit: `"workspace: wire the TODO gate into every clone"`

**Test checkpoint:** `git ls-files -s tools/githooks/pre-commit` prints `100755`; `git check-attr eol -- tools/githooks/pre-commit` prints `eol: lf`; in this provisioned clone a staged unresolvable Depends On edge makes `git commit` exit non-zero with the hook's message, and the restored edge commits. Cheaper substitute that fails: running `validate` by hand before commits, which leaves `core.hooksPath` unset and lets the broken-edge commit through.

## 2. Prove the Review Panel End to End

Every section ships through `review-todo-section`, which runs review slots from `.conclave/panel.toml` through `python scripts/panel_slots.py exec <slot>`. There are no fallback slots: a slot that cannot run parks the campaign. Discovering that on the first real stamp wastes a whole section's context, so this section runs each slot once against a probe first. The slots run through the `codex` CLI, which must be signed in; signing in is the operator's (`D99 T01 §4`), so this section checks first and stops rather than trying to sign in.

- [ ] Run `codex login status`. Done when: it prints a signed-in line (on 2026-09-27: `Logged in using ChatGPT`); if it does not, stop this section, name `D99 T01 §4` as the blocker in the run file, and do not write `Started:`.
- [ ] Run `python scripts/panel_slots.py validate` and `python scripts/panel_slots.py show`. Done when: `validate` prints `panel slots ok` with the writer and slot counts, and the `show` table is quoted in the commit body.
- [ ] Build the probe in a scratch worktree under `build/panel-probe/` (`git worktree add build/panel-probe/wt HEAD`): one commit that plants a typo (`teh`) in `README.md`. Done when: `git -C build/panel-probe/wt log -1 --stat` shows the one-line change.
- [ ] For each slot (`bulk`, `signoff`, `depth`, `plan-primary`, `stamp-check`, `independent`, `arch-primary`), run `python scripts/panel_slots.py exec <slot>` against the probe commit, capturing stdout to `build/panel-probe/<slot>.txt` and the resolved-pin first stderr line beside it. Done when: every slot's output names the planted typo, or the failing slot is named with its error text.
- [ ] Record the probe in `docs/reviews/run-records.md` (date, slot names, the resolved pin per slot, `codex --version`, and whether each named the typo), in the format its header specifies. Done when: `python scripts/todo-runs.py --check` exits 0 with the record present.
- [ ] File any failing slot through `add-todo` as a new section of this file, with the error quoted, and name it in this section's stamp. Done when: no slot failure is left only in `build/`.
- [ ] Commit: `"workspace: prove every review slot against a probe"`

**Test checkpoint:** `python scripts/panel_slots.py validate` exits 0; each `build/panel-probe/<slot>.txt` names the planted `teh`; `python scripts/todo-runs.py --check` exits 0 with the probe record in `docs/reviews/run-records.md`. Cheaper substitute that fails: `validate` alone, which checks the table's shape and never starts a reviewer, so a signed-out or retired model passes it.

## 3. Raise the Claims Coverage Floor

`COVERAGE_FLOOR` in `scripts/todo-claims.py` is a ratchet: coverage may rise, never fall. It was carried from Photon at 1; the Gemail tree authored on 2026-09-27 carries a claim in every `Current state` block, so the floor must rise to what is measured or the ratchet protects nothing.

- [ ] Run `python scripts/todo-claims.py --coverage` and read the covered-block count `N`. Done when: `N` and the total are quoted in the commit body.
- [ ] Set `COVERAGE_FLOOR = N` in `scripts/todo-claims.py` and extend the comment above it with the date and the measurement, keeping its "measured, not wished" wording. Done when: `python scripts/todo-claims.py` prints `floor N` and exits 0.
- [ ] Run `python scripts/todo-claims.py --self-test`. Done when: it reports `0 failed`.
- [ ] Commit: `"workspace: raise the claims coverage floor to the measured value"`

**Test checkpoint:** `python scripts/todo-claims.py` exits 0 and prints `coverage N/N, floor N`; deleting the claim lines from one TODO's `Current state` block in a scratch copy of the tree makes it exit 1 naming coverage below the floor. Cheaper substitute that fails: leaving the floor at 1, which the scratch deletion does not trip.

## 4. First Push Read Back Green

Two workflows guard `main` once `D00 T02 §4` lands: `plan-gates` (`.github/workflows/plan.yml`: the TODO self-test, `validate`, the plan projection, the hook integrity, and the campaign guard) and `build` (the product gates). Neither has run on GitHub yet. A workflow nobody has seen green is a guess, so the first push is read back rather than assumed.

**Needs:** Node.js (build/test)

- [ ] Before pushing, capture the remote head: `BEFORE=$(git ls-remote origin refs/heads/main | cut -f1)`. Done when: `$BEFORE` is a 40-character sha, quoted in the run file.
- [ ] Push `main` with the ported tooling, the gates, and this file committed. Done when: `git status -sb` shows `main` level with `origin/main`.
- [ ] Read back `plan-gates`: `python scripts/review_prompt.py ci-wait <SHA> --since $BEFORE`. Done when: it reports the run green for the pushed sha; a failure is repaired in this section and re-pushed, never waited on.
- [ ] Read back `build`: `python scripts/review_prompt.py ci-wait <SHA> --since $BEFORE --workflow build --workflow-path .github/workflows/build.yml`. Done when: it reports the run green for the same sha.
- [ ] Create `docs/dev/ci.md` with a table of the two workflows (name, file, trigger, what it runs) and the first recorded green run of each (URL, sha, date). Done when: the table cites both run URLs.
- [ ] Commit: `"workspace: record the first green CI runs"`

**Test checkpoint:** `gh run list --workflow plan.yml --limit 1 --json conclusion,headSha` and `gh run list --workflow build.yml --limit 1 --json conclusion,headSha` both return `success` with `headSha` equal to `git rev-parse HEAD` at the pushed commit, and `docs/dev/ci.md` cites both run URLs. Cheaper substitute that fails: a local `pwsh scripts/check-all.ps1`, which proves this machine and not the runner, and cannot show the campaign-guard job on `windows-2025`.

## Verification

- [ ] `pwsh scripts/check-all.ps1` -- exits 0 with every gate `PASS`
- [ ] `python scripts/panel_slots.py validate` and `python scripts/todo-runs.py --check` exit 0
- [ ] The latest `plan-gates` and `build` runs on `main` are green for the same sha
