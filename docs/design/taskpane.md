# Gemail Task Pane -- Design Spec

The binding spec for every surface of the Gemail task pane and ribbon. Surface sections in `todo/` cite it by heading (`docs/design/taskpane.md#<anchor>`) on their `**Design:**` line; `validate` refuses an anchor that does not exist. Where a capture under `docs/captures/taskpane/` and this spec disagree, **this spec wins** and the capture is restaked.

Written 2026-09-27 from the shipped 1.3.2 task pane (`src/taskpane/taskpane.html`, `src/taskpane/taskpane.css`, `src/styles/main.css`). It records what exists and names the gaps the plan closes; a rule marked *(target)* is not true of the code yet, and the section that makes it true is named beside it.

## Tokens

Every color, spacing, radius, font, and duration a surface uses comes from the `@theme` block in `src/styles/main.css`, consumed through Tailwind utilities or `var(--...)` in `src/taskpane/taskpane.css`. A literal color in a `.ts`, `.html`, or `.css` file outside that block is a defect.

| Token group | Tokens (1.3.2 values) |
| --- | --- |
| Brand | `--color-aic-blue` `#3b9eff`, `--color-aic-blue-hover` `#2188ed`, `--color-aic-blue-light` `#e8f3ff`, `--color-aic-purple` `#7b61db`, `--color-aic-purple-hover` `#6b51c8` |
| Accents | `--color-aic-green` `#22c55e`, `--color-aic-amber` `#f59e0b`, `--color-aic-teal` `#14b8a6` |
| Text | `--color-aic-text` `#1a1d23`, `--color-aic-text-secondary` `#5e6470`, `--color-aic-text-tertiary` `#8e95a2` |
| Status | `--color-aic-error-text` `#d1242f`, `--color-aic-success` `#1a7f37` |
| Spacing | xs 4px, sm 8px, md 12px, lg 22px, xl 24px |
| Motion | `--duration-aic` 150ms |
| Font | Poppins, then the system UI stack *(target: self-hosted or system-only, owned by the CSP section of `todo/04-security/`)* |

The `aic-` prefix on CSS classes and tokens is kept after the rename to Gemail: it is internal, never user-visible, and renaming roughly two thousand class references buys nothing (operator-visible decision recorded by the rename TODO in `todo/01-rebrand/`).

Known literal colors that violate this rule in 1.3.2: the loading overlay `rgba(255,255,255,0.85)` (`taskpane.css`), the diff colors `#ffeef0`, `#b31d28`, `#e6ffec`, `#22863a` (`taskpane.css`), and the score colors `#22c55e`, `#eab308`, `#ef4444` (`taskpane.ts`). The dark theme section of `todo/06-features/` moves them to tokens.

## Layout

The task pane is a single column at the width Outlook gives it (320 to 450 px in new Outlook and Outlook on the web), scrolling vertically. From top to bottom: the header, the tab bar, the active feature panel, its result card, and the footer with the version. Horizontal scrolling is a defect at 320 px.

## Header

The product name **Gemail** and the logo mark, left aligned; nothing else. The header never shows a model name or a provider name.

## Tab bar

Two primary tabs (**Reply**, **Draft**) as text buttons, then three icon-only buttons (**Settings**, **Rules**, **More features**). **More features** opens a dropdown listing **Summarize**, **Improve Writing**, **Extract Action Items**, and **Translate**. The active tab carries `.aic-tab--active`.

*(target, owned by the accessibility TODO in `todo/05-quality/`)*: the bar is a `role="tablist"` with `role="tab"` children, `aria-selected`, roving `tabindex`, Left and Right arrow navigation, and the dropdown button carries `aria-expanded` and `aria-controls`. Every icon-only button has an `aria-label` equal to its tooltip.

## Feature panel

Each feature is one `<section>` with the id `<feature>-section`: a short intro line, the inputs, and the primary action button at the bottom, full width. Inputs keep their values when the user switches tabs and comes back.

## Form controls

Every input has a visible `<label for>`; radio groups sit in a `<fieldset>` with a `<legend>`. Text areas auto-grow and show a character counter (`.aic-char-count`) and a clear button (`.aic-btn-clear`). Selects list languages from one shared list, never a copy per panel *(target, owned by the task pane split in `todo/03-architecture/`)*.

## Buttons

Primary (`.aic-btn--primary`, brand blue), secondary (outlined), and icon-only (`.aic-btn--icon`) buttons. A button that starts a model call disables itself until the call settles, and shows the in-flight state on itself as well as in the loading area *(target, owned by `todo/03-architecture/`)*. Focus is always visible (`:focus-visible` ring in brand blue).

## Result card

The output of a feature: the generated text in an editable preview (`contenteditable` for Draft and Reply, read-only elsewhere), word count and reading time, then the actions in this order: the insert action for the mode (**Insert**, **Reply**, **Reply All**, **Accept Changes**), **Copy**, **Regenerate**, and a refine box where the feature supports refining. Model output is rendered as text, never as HTML from the model.

*(target)*: output streams into the card as it arrives, with a **Stop** button replacing **Regenerate** while streaming; stopping keeps the partial text (owned by the performance TODO in `todo/03-architecture/`).

## Status and errors

One error banner (`#error-banner`) above the panel, with a message that names the cause and the fix (for example "Your OpenRouter key was rejected. Check it in Settings."), a **Retry** action when retrying can help, and a dismiss button. Success confirmations ("Settings saved.") appear inline beside the action for three seconds.

*(target, owned by `todo/05-quality/` and `todo/03-architecture/`)*: the banner is `role="alert"`, confirmations are `role="status"`, and an offline banner appears while `navigator.onLine` is false.

## Loading and streaming

1.3.2 shows a full-pane overlay (`#loading-overlay`) with a spinner, a message, and a time estimate. *(target)*: while a response streams, the overlay is replaced by an inline indicator in the result card so the text stays readable, and the message never names a provider or model ("Writing your reply..." not "Generating with Gemini...").

## Settings panel

Top to bottom: **OpenRouter API key** (password field with a show and hide toggle, a link to get a key, and **Test Connection**), **Model** (picker populated from the OpenRouter catalogue), default tone, default summary style, default language, then **Save** and, separated below, **Clear all data** (a destructive action with a confirmation). The key never appears in plain text unless the user toggles it visible.

## Rules panel

Preset rule checkboxes (no placeholders, no signature, no subject line, keep short, simple language) and a free-text custom rules box, then **Save**. Rules apply to every generating feature and to refine prompts *(target, owned by `todo/05-quality/`)*.

## Dialogs

Dialogs are inline panels inside the task pane, never `alert()` or `window.confirm()` (unsupported in Office add-ins). A dialog has a title, one paragraph, and at most two buttons, the safe choice first. The first-run privacy notice is a dialog.

## Themes

1.3.2 switches to `[data-theme="dark"]` once at startup from `Office.context.officeTheme`. *(target, owned by the appearance TODO in `todo/06-features/`)*: the pane follows the Office theme live (`OfficeThemeChanged`) and falls back to `prefers-color-scheme`; every token has a dark value, including the overlay, diff, and score colors.

## Motion

Transitions last `--duration-aic` (150ms). *(target, owned by `todo/05-quality/`)*: under `prefers-reduced-motion: reduce`, the spinner, `focusPulse`, and `slideIn` animations stop.

## Ribbon

Read mode: one group **Gemail** with **Open Gemail**. Compose mode: the same button plus an **AI Tools** menu (Fix Grammar & Spelling, Improve Clarity, Make Concise, Make Professional). Ribbon results are reported through an Outlook notification message of at most 150 characters.

## Accessibility

Every control is reachable and operable by keyboard in the tab order of the layout above, every control has an accessible name, text contrast is at least 4.5:1 (3:1 for large text and UI boundaries) in every theme, and state changes the user did not cause by focus (errors, completion, saved) are announced through live regions. Owned by the accessibility TODO in `todo/05-quality/`.
