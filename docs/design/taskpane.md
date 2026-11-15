# Gemail Task Pane -- Design Spec

The behavior and rules for every surface of the Gemail task pane and ribbon. The approved look is [`mockup.md`](./mockup.md) (layout and composition, with renders) and [`tokens.json`](./tokens.json) (every value); where this file and they disagree on a visual point, they win and this file is corrected. Surface sections in `todo/` cite it by heading (`docs/design/taskpane.md#<anchor>`) on their `**Design:**` line; `validate` refuses an anchor that does not exist. Where a capture under `docs/captures/taskpane/` and this spec disagree, **this spec wins** and the capture is restaked.

Written 2026-09-27 from the shipped 1.3.2 task pane, revised the same day for the first approved mockup, and revised on 2026-11-15 for the Fluent Native design that replaced it (operator decision: "Most definately A") (`src/taskpane/taskpane.html`, `src/taskpane/taskpane.css`, `src/styles/main.css`). It records what exists and names the gaps the plan closes; a rule marked *(target)* is not true of the code yet, and the section that makes it true is named beside it.

## Tokens

Every color, font, size, spacing, radius, and duration comes from [`tokens.json`](./tokens.json), which defines a light and a dark set with the same keys. `D03 T04 §1` generates `src/styles/tokens.css` from it (`--gm-color-<key>`, `--gm-<group>-<key>`) and points the existing `--color-aic-*` names at those properties; surfaces consume Tailwind utilities or `var(--gm-...)`. A literal color, font declaration, or inline SVG in `src/` fails `python scripts/design-lint.py` (the pre-existing ones sit on a shrink-only baseline that `D03 T04` empties).

| Group | Values (light / dark, from `tokens.json`) |
| --- | --- |
| Brand | `brand` `#0f6cbd` / `#479ef5` (text, links, indicators), `brandFill` `#0f6cbd` / `#115ea3` (filled buttons), `brandHover`, `brandTint`, `brandSelected`, `onBrand` `#ffffff` in both themes |
| AI | `ai` `#6d48c7` / `#b69df8`, `aiTint`, `aiIcon` (the spark and the model tags only) |
| Text | `text` `#242424` / `#ffffff`, `textSecondary` `#5c5c5c` / `#d6d6d6`, `textTertiary` `#6b6b6b` / `#adadad` |
| Surfaces | `bg`, `surface`, `surfaceSunken`, `border`, `borderSubtle`, `borderInput`, `borderChip` |
| Status | `success`, `successTint`, `successBorder`, `danger`, `dangerTint`, `dangerBorder`, the four `diff*` colors |
| Type | Segoe UI Variable Text over the system stack (`font.family`) on Fluent 2's ramp: title 20/28, subtitle 16/22, body 14/20, reading 14/22, caption 12/16; regular and semibold |
| Space, radius, motion | a 4 px grid (4 to 24 px, pane gutter 16, section gap 20), radius 4 (inputs, buttons), 8 (cards), 12 (dialogs), pill (chips), duration 150ms |

Every text pair passes WCAG 2.1 AA in both themes (operator decision 2026-09-27: darken rather than deviate), measured on 2026-11-15 over every text and background pair the artboards use: the lowest is 4.81:1 in the light theme and 5.18:1 in the dark theme. The dark theme splits `brand` (text) from `brandFill` (buttons) so that white on the fill and blue on the background both pass. The `aic-` prefix on existing CSS class names is kept: it is internal, never user-visible, and renaming roughly two thousand references buys nothing (recorded by the rename TODO in `todo/01-rebrand/`).

## Layout

The pane is three bands at the width Outlook gives it (320 to 450 px in new Outlook and Outlook on the web; the mockup draws 360): the header and the tab bar fixed at the top, the active feature's content scrolling in the middle, and the action bar fixed at the bottom. Only the middle band scrolls, so the primary action is always reachable. Horizontal scrolling is a defect at 320 px. The composition is [`mockup.md#reply-read-mode`](./mockup.md#reply-read-mode) and the frame rule is [`mockup.md#design-language`](./mockup.md#design-language).

## Header

The app mark, the product name **Gemail**, and one icon button on the right: **Settings**. The header never shows a model or provider name (the footer does). Picture: [`mockup.md#header`](./mockup.md#header).

## Tab bar

Equal tabs, each a 20 px icon over a 12 px label. Read mode shows five: **Reply**, **Draft**, **Summarize**, **Improve**, **More**. Compose mode shows four: **Draft**, **Improve**, **Translate**, **More** (Reply and Summarize need a received message). The active tab shows the tinted icon, the `brand` color, a semibold label, and a 2 px indicator; **More** opens Actions, Translate in read mode, and later features. Settings is the header button and Rules lives inside Settings, so neither is a tab (the 1.3.2 bar with two text tabs, three icon-only buttons, and a "More features" dropdown is replaced by `D03 T04 §3`). Picture: [`mockup.md#tab-bar`](./mockup.md#tab-bar).

*(target, owned by the accessibility TODO in `todo/05-quality/`)*: the bar is a `role="tablist"` with `role="tab"` children, `aria-selected`, roving `tabindex`, and Left and Right arrow navigation; **More** carries `aria-expanded` and `aria-controls`; every icon-only control has an `aria-label` equal to its tooltip.

## Feature panel

Each feature is one `<section>` with the id `<feature>-section` in the scrolling band: the context row, the inputs, and after a result the folded instruction summary and the result card. Its primary action is not in the panel: it is in the action bar. Inputs keep their values when the user switches tabs and comes back, and when the form is folded and unfolded with **Edit**.

## Form controls

Every input has a visible `<label for>`; radio groups sit in a `<fieldset>` with a `<legend>`. Text areas auto-grow and show a character counter (`.aic-char-count`) and a clear button (`.aic-btn-clear`). Tone, length, and language are one wrapping row of dropdown buttons that each show their current value and open a listbox ([`mockup.md#reply-settings-row`](./mockup.md#reply-settings-row)); there is no segmented control. Languages come from one shared list, never a copy per panel *(target, owned by the task pane split in `todo/03-architecture/`)*.

## Buttons

Primary (`.aic-btn--primary`, `brandFill` with `onBrand` text), secondary (outlined, `borderInput`), text (`brand`, semibold, no border), and icon-only (`.aic-btn--icon`) buttons, all `radius.sm`. Action bar buttons are 44 px tall; buttons in the content are 32 px, compact ones 28 px. A button that starts a model call disables itself until the call settles, and shows the in-flight state on itself as well as in the loading area *(target, owned by `todo/03-architecture/`)*. Focus is always visible (`:focus-visible` ring in `brand`).

## Result card

The output of a feature: a header row with the word count and reading time and **Regenerate**, the generated text in an editable preview (`contenteditable` for Draft and Reply, read-only elsewhere), and a refine box where the feature supports refining. The insert actions are in the action bar, in this order: the insert action for the mode (**Insert**, **Reply**, **Reply all**, **Replace selection**), then **Copy** and, for Improve, **Try again**. When a result arrives the form folds into the instruction summary, and **Edit** unfolds it. Model output is rendered as text, never as HTML from the model. Picture: [`mockup.md#result-card`](./mockup.md#result-card).

*(target)*: output streams into the card as it arrives, with a **Stop** button taking the place of the action bar's primary button while streaming; stopping keeps the partial text (owned by the performance TODO in `todo/03-architecture/`).

## Action bar

A bar pinned to the bottom of the pane that holds the active feature's primary action and, under it, the footer line (the model name with a **Change** link, and the version). Before a result it holds the one write action (**Write reply**, **Write draft**, **Summarize**, **Improve**, and so on) with its `Ctrl+Enter` hint; after a result it holds the insert actions; while streaming it holds **Stop**. It is never empty and never scrolls. `Ctrl+Enter` triggers whatever the primary button currently is. Picture: [`mockup.md#action-bar`](./mockup.md#action-bar).

## Status and errors

One error banner (`#error-banner`) in the content band, with a message that names the cause and the fix (for example "Your OpenRouter key was rejected. Check it in Settings."), a **Retry** action when retrying can help, and a dismiss button. Confirmations of a write into the message (the undo confirmation) are a `successTint` card at the top of the content with an **Undo** action; other confirmations ("Settings saved.") appear inline beside the action for three seconds. Picture: [`mockup.md#error-banner`](./mockup.md#error-banner).

*(target, owned by `todo/05-quality/` and `todo/03-architecture/`)*: the banner is `role="alert"`, confirmations are `role="status"`, and an offline banner appears while `navigator.onLine` is false.

## Loading and streaming

1.3.2 shows a full-pane overlay (`#loading-overlay`) with a spinner, a message, and a time estimate. *(target)*: while a response streams, the overlay is replaced by an inline indicator in the result card so the text stays readable, and the message never names a provider or model ("Writing your reply..." not "Generating with Gemini...").

## Settings panel

Grouped cards, top to bottom (picture: [`mockup.md#settings`](./mockup.md#settings)): **OpenRouter key** (the key field with a show toggle and **Test**, the connection status, the device-only note, and a link to get a key), **Model** (search plus recommended models from the live catalogue, and the full catalogue grouped by provider), **Writing** (Creativity, default tone, output language, and the **Rules** row, which opens the Rules panel), the privacy switch in its own card (the data-collection switch, off by default), then **Clear all Gemail data...**, which opens a confirmation dialog. **Save settings** sits in a sticky bar at the bottom of the pane with the count of unsaved changes; settings are saved only on that click, and leaving with unsaved changes asks first. The key never appears in plain text unless the user toggles it visible.

## Rules panel

Opened from the **Rules** row of the Settings **Writing** card, with a back button to Settings. Preset rule checkboxes (no placeholders, no signature, no subject line, keep short, simple language) and a free-text custom rules box, saved by the same sticky **Save settings** bar. Rules apply to every generating feature and to refine prompts *(target, owned by `todo/05-quality/`)*.

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
