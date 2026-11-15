# Gemail Icons

The catalog and the rules for every icon Gemail shows. The pictures are in [`mockup.md#icons`](./mockup.md#icons); the sources are canonical in [`assets/icons/src/`](../../assets/icons/src/).

## Rules

- **One source per icon.** Every icon is an SVG under `assets/icons/src/`. Nothing else draws an icon: no inline `<svg>` in `src/`, no hand-resized PNG, no icon font. `python scripts/design-lint.py` refuses a new inline `<svg>` in `src/` (outside the generated registry) and any output that does not match its source.
- **Build, never hand-edit, the outputs.** `node tools/design/icons.mjs` renders the PNGs under `assets/icons/png/`, regenerates `src/ui/icons.ts`, and records every hash in `assets/icons/manifest.json`. Run it after any source change and commit all three together. (`npm ci --prefix tools/design` once per clone installs its rasterizer; it never enters the add-in's dependencies.)
- **Two styles, by surface.**
  - **Fluent color** for Outlook's own chrome (the app icon, the ribbon, the AI Tools menu): flat two-tone shapes, no gradient. The ribbon and menu icons share one document base (a sheet with a folded corner and two text lines) and carry one round badge each, so the AI Tools family reads as a set beside Outlook's own ribbon icons.
  - **Fluent 2 regular** for the task pane: a 20 px grid, a 1.5 px stroke with round caps and joins, `currentColor`, a regular glyph at rest and a `-filled` glyph for the active tab (the same outline with `fill="currentColor" fill-opacity="0.2"`).
- **Purple means AI.** Only the spark carries the AI accent (`aiIcon` in `docs/design/tokens.json`), drawn as `stroke="#6d48c7" class="gm-icon-accent"` so the pane's CSS retints it per theme. No other glyph uses purple.
- **Accessible by construction.** `iconSvg(name)` marks an icon `aria-hidden` unless it gets a `label`; an icon-only button gets its name from the button's `aria-label`, never from the SVG.
- **Adding an icon.** Draw it in the design artifact first (the `design-sync` skill), then export it into `assets/icons/src/<group>/<name>.svg` on the grid and stroke above, add a row below, run the build, and use it through `iconSvg()` or the manifest. Where Microsoft's MIT-licensed Fluent UI System Icons has the glyph, match it.
- **A 16 px redraw where 16 px needs one.** A ribbon or menu icon may have a `<name>-16.svg` beside its `<name>.svg` (16 px box): the build renders the 16 px PNG from the redraw and 32 and 80 from the 32 px drawing. Every ribbon and menu icon has one (operator-approved 2026-11-15); the app icon has had one since the first import.
- **No envelope.** The app icon is a written letter with the AI spark, not an envelope, so Gemail never reads as another mail brand's mark (operator decision 2026-11-15).

## App

| Source | Box | Outputs | Used by |
| --- | --- | --- | --- |
| `app/gemail.svg` | 48 | `png/app/gemail-{32,64,80,128,256}.png` | Manifest `IconUrl` (64), `HighResolutionIconUrl` (128), **Open Gemail** ribbon button (32, 80), the pane header mark, the store listing (256, backlog B-002) |
| `app/gemail-16.svg` | 16 | `png/app/gemail-16.png` | **Open Gemail** at 16 px (redrawn: one text line and a larger spark) |

## Ribbon and AI Tools menu

| Source | Box | Outputs | Used by |
| --- | --- | --- | --- |
| `ribbon/ai-tools.svg`, `ribbon/ai-tools-16.svg` | 32, 16 | `png/ribbon/ai-tools-{16,32,80}.png` | The **AI Tools** menu button (compose mode) |
| `menu/fix-grammar-and-spelling.svg`, `-16.svg` | 32, 16 | `png/menu/fix-grammar-and-spelling-{16,32,80}.png` | Menu item **Fix grammar & spelling** (`fixGrammar`) |
| `menu/improve-clarity.svg`, `-16.svg` | 32, 16 | `png/menu/improve-clarity-{16,32,80}.png` | Menu item **Improve clarity** (`improveClarity`) |
| `menu/make-concise.svg`, `-16.svg` | 32, 16 | `png/menu/make-concise-{16,32,80}.png` | Menu item **Make concise** (`makeConcise`) |
| `menu/make-professional.svg`, `-16.svg` | 32, 16 | `png/menu/make-professional-{16,32,80}.png` | Menu item **Make professional** (`makeProfessional`) |
| `menu/my-prompts.svg`, `-16.svg` | 32, 16 | `png/menu/my-prompts-{16,32,80}.png` | Menu item **My prompts...** (planned, `D06 T02 §2`) |

## Task pane

Every glyph is a 20 px source in `pane/`, reached from code only as `iconSvg("<name>")`.

| Name | Meaning and where it is used |
| --- | --- |
| `reply`, `reply-filled` | Reply tab (rest, active: the outline with a 20 percent tint fill) |
| `draft`, `draft-filled` | Draft tab |
| `summarize`, `summarize-filled` | Summarize tab |
| `improve`, `improve-filled` | Improve tab |
| `more`, `more-filled` | More tab |
| `actions` | Extract action items |
| `translate` | Translate (a compose-mode tab, and under More in read mode) |
| `timeline` | Thread timeline (`D06 T03 §3`) |
| `attachments` | Attachment picker (`D06 T03 §2`) |
| `suggest-cc` | CC suggestions (`D06 T03 §4`) |
| `my-prompts` | Custom prompt library (`D06 T02 §1`) |
| `quick-replies` | Quick replies heading, when not using the spark |
| `rules` | Rules section in Settings |
| `settings` | Header Settings button |
| `api-key` | OpenRouter key field |
| `privacy` | Privacy switch and the "stored on this device" note |
| `copy`, `stop`, `undo`, `regenerate` | Action bar and result card actions (Copy, Stop, Undo, Regenerate and Try again) |
| `back`, `search`, `eye`, `check`, `error`, `chevron-down`, `selection` | Navigation, search, show key, success, error banner, disclosure, the selection context row |
| `theme` | Appearance setting (`D06 T04 §1`) |
| `usage` | Local usage stats (`D06 T04 §3`) |
| `offline` | Offline banner (`D03 T03 §2`) |
| `language` | Output language setting |
| `ai` | Outline spark with a small plus: the Model card heading, the refine input, and any AI action with no other glyph |
| `spark-filled` | **Write reply** and every primary AI action in the action bar, the Quick replies label |
| `focus-grammar`, `focus-clarity`, `focus-concise`, `focus-professional` | The Improve focus cards (outline versions of the menu icons) |
