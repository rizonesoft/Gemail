# Gemail Task Pane -- Design Spec

The behavior and rules for every surface of the Gemail task pane and ribbon. The approved look is [`mockup.md`](./mockup.md) (layout and composition, with renders) and [`tokens.json`](./tokens.json) (every value); where this file and they disagree on a visual point, they win and this file is corrected. Surface sections in `todo/` cite it by heading (`docs/design/taskpane.md#<anchor>`) on their `**Design:**` line; `validate` refuses an anchor that does not exist. Where a capture under `docs/captures/taskpane/` and this spec disagree, **this spec wins** and the capture is restaked.

Written 2026-09-27 from the shipped 1.3.2 task pane and revised the same day for the approved mockup (`src/taskpane/taskpane.html`, `src/taskpane/taskpane.css`, `src/styles/main.css`). It records what exists and names the gaps the plan closes; a rule marked *(target)* is not true of the code yet, and the section that makes it true is named beside it.

## Tokens

Every color, font, size, spacing, radius, and duration comes from [`tokens.json`](./tokens.json), which defines a light and a dark set with the same keys. `D03 T04 §1` generates `src/styles/tokens.css` from it (`--gm-color-<key>`, `--gm-<group>-<key>`) and points the existing `--color-aic-*` names at those properties; surfaces consume Tailwind utilities or `var(--gm-...)`. A literal color, font declaration, or inline SVG in `src/` fails `python scripts/design-lint.py` (the pre-existing ones sit on a shrink-only baseline that `D03 T04` empties).

| Group | Values (light / dark, from `tokens.json`) |
| --- | --- |
| Brand | `brand` `#1668c9` / `#4ba3ff`, `brandHover`, `brandTint`, `brandSelected`, `onBrand` `#ffffff` / `#0d1117` |
| AI | `ai`, `aiStrong`, `aiTint`, `aiIcon` (the spark only) |
| Text | `text` `#1b1d22` / `#eceef2`, `textSecondary` `#5e6470` / `#b3b9c4`, `textTertiary` `#686e7a` / `#9aa3b2` |
| Surfaces | `bg`, `surface`, `surfaceSunken`, `border`, `borderSubtle`, `borderInput`, `borderChip` |
| Status | `success`, `successTint`, `successBorder`, `danger`, `dangerTint`, `dangerBorder`, the four `diff*` colors |
| Type | Segoe UI Variable Text over the system stack (`font.family`); 12, 13, 14, and 16 px; regular and semibold |
| Space, radius, motion | space 4 to 24 px, radius 6 to 16 px, duration 150ms |

Every text pair passes WCAG 2.1 AA in both themes (operator decision 2026-09-27: darken rather than deviate): white on `brand` is 5.44:1 and `textTertiary` is at least 4.57:1 on every light background. The `aic-` prefix on existing CSS class names is kept: it is internal, never user-visible, and renaming roughly two thousand references buys nothing (recorded by the rename TODO in `todo/01-rebrand/`).

## Layout

A single column at the width Outlook gives the pane (320 to 450 px in new Outlook and Outlook on the web), scrolling vertically: the header, the tab bar, the active feature panel, its result card, and the footer. Horizontal scrolling is a defect at 320 px. The composition is [`mockup.md#reply-read-mode`](./mockup.md#reply-read-mode).

## Header

The app mark, the product name **Gemail**, and one icon button on the right: **Settings**. The header never shows a model or provider name (the footer does). Picture: [`mockup.md#header`](./mockup.md#header).

## Tab bar

Five equal tabs, each a 20 px icon over a 12 px label: **Reply**, **Draft**, **Summarize**, **Improve**, **More**. The active tab shows the filled icon, the `brand` color, a semibold label, and a 2 px underline; **More** opens Actions, Translate, and later features. Settings is the header button and Rules lives inside Settings, so neither is a tab (the 1.3.2 bar with two text tabs, three icon-only buttons, and a "More features" dropdown is replaced by `D03 T04 §3`). Picture: [`mockup.md#tab-bar`](./mockup.md#tab-bar).

*(target, owned by the accessibility TODO in `todo/05-quality/`)*: the bar is a `role="tablist"` with `role="tab"` children, `aria-selected`, roving `tabindex`, and Left and Right arrow navigation; **More** carries `aria-expanded` and `aria-controls`; every icon-only control has an `aria-label` equal to its tooltip.

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

Top to bottom (picture: [`mockup.md#settings`](./mockup.md#settings)): **OpenRouter** (the key field with a show toggle and **Test**, the connection status, the device-only note, and a link to get a key), **Model** (search plus recommended models from the live catalogue, and the full catalogue grouped by provider), **Writing** (Creativity, default tone, output language), **Privacy** (the data-collection switch, off by default), **Rules** (the preset rules and custom rules, moved here from their own tab), then **Save settings** and, separated below, **Clear all Gemail data...**, which opens a confirmation dialog. The key never appears in plain text unless the user toggles it visible.

## Rules panel

Preset rule checkboxes (no placeholders, no signature, no subject line, keep short, simple language) and a free-text custom rules box, then **Save**. Rules apply to every generating feature and to refine prompts *(target, owned by `todo/05-quality/`)*.

## Dialogs

Dialogs are inline panels inside the task pane, never `alert()` or `window.confirm()` (unsupported in Office add-ins). A dialog has a title, one paragraph, and at most two buttons, the safe choice first. The first-run privacy notice is a dialog.

## Themes

1.3.2 switches to `[data-theme="dark"]` once at startup from `Office.context.officeTheme`. *(target, owned by the appearance TODO in `todo/06-features/`)*: the pane follows the Office theme live (`OfficeThemeChanged`) and falls back to `prefers-color-scheme`; every token has a dark value, including the overlay, diff, and score colors.

## Motion

Transitions last `--duration-aic` (150ms). *(target, owned by `todo/05-quality/`)*: under `prefers-reduced-motion: reduce`, the spinner, `focusPulse`, and `slideIn` animations stop.

## Ribbon

Read mode: one group **Gemail** with **Open Gemail**. Compose mode: the same button plus an **AI Tools** menu (Fix grammar & spelling, Improve clarity, Make concise, Make professional, and My prompts once `D06 T02 §2` ships). Icons are the Fluent color set in [`icons.md`](./icons.md); results are reported through an Outlook notification message of at most 150 characters. Picture: [`mockup.md#ribbon`](./mockup.md#ribbon).

## Accessibility

Every control is reachable and operable by keyboard in the tab order of the layout above, every control has an accessible name, text contrast is at least 4.5:1 (3:1 for large text and UI boundaries) in every theme, and state changes the user did not cause by focus (errors, completion, saved) are announced through live regions. Owned by the accessibility TODO in `todo/05-quality/`.
