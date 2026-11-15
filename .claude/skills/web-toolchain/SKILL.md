---
name: web-toolchain
description: Use the project's pinned PHP and Node runtimes, package managers and static tools. Use when an install, a build or a test fails for no reason the code explains, and before running a static tool.
---

# PHP and Node toolchain

The project pins its runtimes, package managers and static tools in `.conclave/toolchain-web.json`. `docs/toolchain-web.md` has every command.

## When something fails for no reason the code explains

Run the check first: `python scripts/toolchain-check.py --pins .conclave/toolchain-web.json`. An old PHP or Node looks like a broken dependency.

- Never install, upgrade or downgrade PHP, Node, Composer or a package manager. Report the tool, the version found and the version wanted, with the install line the check prints, and the operator installs it.
- Never change a pin to get past the check: do not lower a `min_version` or mark a tool `optional` to fit the machine.
- Never loosen `require.php` in `composer.json` or `engines.node` in `package.json` to fit the machine. They say what the project runs on in production. When a pin accepts less than a manifest requires, raise the pin.

## Use the project's own tools

- Run the tools the pin file's `search` names, from the app's folder (the pin file's `root`): `vendor/bin/phpstan`, `vendor/bin/pint`, `vendor/bin/phpcs`, `node_modules/.bin/<tool>`. They are at the versions the lock files hold. Do not run, or install, a copy for the machine.
- A tool under `vendor/bin` or `node_modules/.bin` that the check reports missing is installed by the project's own install (`composer install`, or the install of the project's package manager, below), which changes nothing outside the project. Do not add, remove or upgrade a dependency to get one.
- Use the project's package manager: the one `packageManager` in `package.json` names, else the one whose lock file the app holds (`pnpm-lock.yaml`: pnpm, `package-lock.json`: npm, `yarn.lock`: yarn). The check's `package-manager` line says which one is installed, not which one the project uses. Never install with another, and never switch a project from one to the other: a second lock file is a different set of dependencies. When the project's manager is not installed, report it.
