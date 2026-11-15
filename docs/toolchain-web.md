# The PHP and Node toolchain

How this project pins its runtimes, its package managers and its static tools, and how to tell which are missing or too old. The files came from the Conclave-SDK `toolchain-web` kit once and are the project's own now: change them as the project needs.

Nothing here installs a runtime or a dependency.

## What is here

| File | What it is for |
| --- | --- |
| `.conclave/toolchain-web.json` | The pin file: each tool, the commands that satisfy it, the least version |
| `scripts/toolchain-check.py` | Says which pinned tools are missing or too old; installs nothing |

## Are the tools there?

```text
python scripts/toolchain-check.py --pins .conclave/toolchain-web.json
python scripts/toolchain-check.py --pins .conclave/toolchain-web.json --json
```

One line per tool: `ok` with the path found and its version, or why not (not installed, with the line that installs it; too old, with both versions; or what went wrong when it was run). The word after the tool's name is `ok`, `setup_required` for a required tool that is not ok, or `optional` for a tool the pin marks optional that is not ok: an `optional` line is information, not setup the project needs. It exits 0 when every required tool is ok, 3 when one is not, and 2 when the pin file does not load. A tool marked `optional` (the seed marks `phpstan`, `pint` and `phpcs`) is shown and never fails the check.

Run it first when an install, a build or a test fails for a reason the code does not explain: an old PHP or Node looks like a broken dependency.

When a runtime or a package manager is missing or too old, the answer is to install it, and that is the operator's to do: the check prints the line. Do not lower a `min_version` to fit the machine, and do not loosen `require.php` in `composer.json` or `engines.node` in `package.json` for it either: those say what the project runs on in production.

## Where the tools are looked for

Two keys at the top of the pin file say where the project keeps tools of its own:

```json
{
  "schema_version": 1,
  "root": "platform",
  "search": ["vendor/bin", "node_modules/.bin"],
  "tools": []
}
```

`root` is the app's folder inside the project (`.` when left out). `search` lists folders inside it. A command is looked for in those folders first, then on `PATH`, and never in the working directory. So `phpstan`, `pint`, `phpcs` and a project's own `pnpm` are the ones Composer and the package manager installed for this project, at the versions its lock files hold. Run those, not a copy installed for the machine: `vendor/bin/phpstan`, `node_modules/.bin/tsc`.

A tool under `vendor/bin` or `node_modules/.bin` that is reported missing is installed by the project's own install (`composer install`, or the install of the project's package manager), which changes nothing outside the project.

## Which package manager

The project's package manager is the one it names itself: `packageManager` in `package.json`, else the lock file the app holds (`pnpm-lock.yaml`: pnpm, `package-lock.json`: npm, `yarn.lock`: yarn). The check's `package-manager` line says which of the pin's commands is installed, the first it finds, and that is not the same question: on a machine with both pnpm and npm, a pin that names `pnpm` first reports pnpm for an npm project. Install with the project's manager only. Installing with another writes a second lock file and resolves a different set of dependencies.

In an npm project, put `npm` first in the `package-manager` pin's `commands`. The doctor's `constraint:package-manager` says when the pin and the project disagree.

### Changing a pin

Edit `.conclave/toolchain-web.json`. Each tool has a `name`, an `install` line, an optional `optional`, and `commands` in order of preference (`pnpm`, then `npm`); each command has its own `version_args`, `version_pattern` (one group that captures dotted numbers) and `min_version`. `command` is a bare program name, never a path. Raise a `min_version` when the project needs a newer release, and keep it at or above what the project's own manifests require. The check refuses a pin file that breaks these rules and names the file, the tool and the key.

## The doctor

From a Conclave-SDK checkout, `python forge.py doctor <project> toolchain-web` reports each file, each pinned tool, and two comparisons the check alone does not make:

- `constraint:php`: the least PHP the pin accepts against `require.php` in the app's `composer.json`;
- `constraint:node`: the least Node the pin accepts against `engines.node` in its `package.json`.

Each is `unexpected` when the pin accepts a version the project's own manifest refuses, and names the pin to raise. Raise the pin; the manifest is right.

- `constraint:package-manager`: the manager the project names (`packageManager`, or its lock file) against the pin's first command. It is `unexpected` when they differ, naming the command to put first, and when the project holds the lock files of two managers.

## Language servers

With the Conclave `lsp` kit in the project, the install added the stack's servers to `.conclave/lsp.json`: Intelephense for an app with `composer.json`, the TypeScript and Tailwind servers for one with `package.json`. `python scripts/lsp-diagnostics.py --all --changed` checks a change with them (`docs/language-servers.md`).

## What is left to the project

- Installing PHP, Node, Composer and the package manager: a person does that.
- Installing dependencies: `composer install` and the package manager's own install.
- Every build, test and lint command, and the configuration of each tool (`phpstan.neon`, `pint.json`, `phpcs.xml`).
