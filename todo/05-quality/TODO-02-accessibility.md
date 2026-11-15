---
schema_version: 1
id: accessibility
domain: 05-quality
status: draft
title: "TODO-02 -- Accessibility"
depends_on: []
---

# TODO-02 -- Accessibility

> **Goal:** The task pane meets WCAG 2.1 AA for everything it renders: every control has an accessible name, the tab bar behaves as a tab list under the keyboard, errors and completions are announced without stealing focus, focus lands where the work continues, animation stops for users who ask for less motion, a skip link reaches the active panel, and every text and UI color pair meets its contrast minimum, checked by a script instead of by eye. The screen-reader pass with Narrator and NVDA is the operator's (`D99 T01 §7`) and runs on what this file ships.

> [!IMPORTANT]
> **Current state (verified 2026-09-27):** `src/taskpane/taskpane.html` has no `aria-` attribute and no `role` attribute. The icon-only buttons `#tab-settings`, `#tab-rules`, `#tab-more`, the two `.aic-copy-btn` buttons, `#btn-scroll-top`, and `#btn-dismiss-error` are named only by `title`. The tab bar is a row of `<button class="aic-tab">` elements with no tab semantics, and `#more-dropdown` opens without `aria-expanded`. The radio groups `summary-style` and `improve-focus` have no `fieldset` or `legend`, and the "Preset Rules" `<label>` has no `for`. `#error-banner` and `#loading-overlay` are not live regions, and nothing moves focus after a result renders. `src/taskpane/taskpane.css` runs `spin`, `focusPulse`, and `slideIn` animations with no `prefers-reduced-motion` rule, and there is no skip link. Measured with the WCAG relative-luminance formula: `--color-aic-text-tertiary` `#8e95a2` on `#ffffff` is 3.01:1 and on `--color-aic-bg-panel` `#f8f9fb` is 2.86:1, and white text on `--color-aic-blue` `#3b9eff` (the primary button) is 2.79:1, all below the 4.5:1 text minimum.
<!-- claim: count "aria-" src/taskpane/taskpane.html = 0 -->
<!-- claim: count "role=" src/taskpane/taskpane.html = 0 -->
<!-- claim: count "prefers-reduced-motion" src/taskpane/taskpane.css = 0 -->
<!-- claim: count "--color-aic-text-tertiary: #8e95a2;" src/styles/main.css = 1 -->
<!-- claim: absent scripts/contrast-check.js -->

## Inputs

- [`src/taskpane/taskpane.html`](../../src/taskpane/taskpane.html), [`src/taskpane/taskpane.css`](../../src/taskpane/taskpane.css), [`src/styles/main.css`](../../src/styles/main.css) -- the markup, animations, and tokens this file changes
- [`docs/design/taskpane.md`](../../docs/design/taskpane.md) -- the Tab bar, Status and errors, Motion, and Accessibility rules this file makes true
- WCAG 2.1 (https://www.w3.org/TR/WCAG21/) -- success criteria 1.3.1, 1.4.3, 1.4.11, 2.1.1, 2.3.3, 2.4.1, 2.4.3, 3.3.2, 4.1.2, 4.1.3, cited per item
- WAI-ARIA Authoring Practices, Tabs pattern (https://www.w3.org/WAI/ARIA/apg/patterns/tabs/) and Menu Button pattern (https://www.w3.org/WAI/ARIA/apg/patterns/menu-button/) -- the keyboard models §2 implements
- Microsoft Learn, "Accessibility guidelines for Office Add-ins" (https://learn.microsoft.com/office/dev/add-ins/design/accessibility-guidelines) -- the add-in specific expectations
- -> XREF: D03 T01 §5 -- the split panels and thin bootstrap §1 builds on; the tab controller of D03 T01 §2 is what §2 extends
- -> XREF: D06 T02 §3 -- the keyboard shortcuts, which build on the §2 keyboard model and must not collide with it
- -> XREF: D06 T04 §2 -- the dark theme contrast check, which runs the §5 script over the dark tokens
- -> XREF: D07 T01 §6 -- the release, which ships only with §1 to §4 done
- -> XREF: D99 T01 §7 -- the operator's screen-reader pass, which runs on what §3 ships
- -> XREF: D03 T04 §1 -- the token values the contrast check reads are wired into the stylesheet there

## Outcome

- Every button, input, select, and radio group in the pane has an accessible name, and a jsdom test fails on a new control without one.
- The tab bar is a `tablist` that Left, Right, Home, and End move through, and the **More features** button opens and closes its menu with Enter, Space, and Escape, returning focus to the button.
- Errors are announced as alerts, confirmations and progress as status messages, and focus moves to the result after a generation and back to the trigger after an error is dismissed.
- Under `prefers-reduced-motion: reduce` no animation runs, and a skip link is the first focusable element.
- `node scripts/contrast-check.js` passes for every text and UI pair in the light theme, and runs in `scripts/check-all.ps1`.

**Adjacency:** list=not-applicable (no browsable collection is added); document=not-applicable (nothing is written into a message); settings=not-applicable (motion follows the operating system setting, no Gemail setting); reporting=not-applicable (no summaries); notifications=applicable @ D05 T02 §3; permissions=not-applicable (refusals are owned by their features; §3 only announces them); audit=not-applicable (nothing is written or logged); exchange=not-applicable (nothing is imported or exported); reverse=not-applicable (no action here creates anything)

**Adjacency rationale:** Notifications is the one kind this file owns: §3 turns the pane's existing banners and confirmations into announced live regions, which is how a screen-reader user learns that a result arrived or a request failed.

## Implementation Order

| Order | Section | Deliverable                            | Depends On | Status |
| :---: | :-----: | -------------------------------------- | ---------- | :----: |
|   1   |   §1    | A name for every control               | D03 T01 §5 |  [ ]   |
|   2   |   §2    | Tab bar semantics and arrow keys       | §1         |  [ ]   |
|   3   |   §3    | Live regions and focus management      | §1         |  [ ]   |
|   4   |   §4    | Reduced motion and a skip link         | §1         |  [ ]   |
|   5   |   §5    | Contrast check for the tokens          | §1, D03 T04 §1 |  [ ]   |

---

## 1. A Name for Every Control

A control with no accessible name is announced as "button" and nothing else. The pane's icon-only buttons rely on `title`, which screen readers do not reliably announce and keyboard users never see. This section names every control and adds a test so a new unnamed control fails the build. Sources: WCAG 2.1 SC 4.1.2 Name, Role, Value; SC 1.3.1 Info and Relationships; SC 3.3.2 Labels or Instructions.

**Fidelity:** Gemail task pane controls (tab bar icons, copy buttons, scroll-to-top, error dismiss, form fields) -- docs/captures/taskpane/controls/. No visual change: names are added without moving or restyling any control.

**Design:** docs/design/mockup.md#header, docs/design/mockup.md#tab-bar, docs/design/mockup.md#pane-icons, docs/design/taskpane.md#accessibility -- states: all in spec -- themes: n/a (names are not themed) -- density: n/a (one density in a fixed-width task pane)

**Job:** a screen-reader or voice-control user can identify and operate every control in the pane by its name. Consumer: assistive technology reading the accessibility tree.

**Treatment:** an `aria-label` equal to the visible tooltip on each icon-only button, a `<label for>` on every input, and a `fieldset` with a `legend` around each radio group. Cheaper substitute that fails the checkpoint: keeping `title` only, which the accessible-name test rejects.

**Chrome:** consume the existing controls and classes in `src/taskpane/taskpane.html` and the naming rule of `docs/design/taskpane.md#tab-bar`. Do not invent a second tooltip system or hidden-text helper where `aria-label` serves.

**Needs:** Outlook client (sideload)

**Requires:** display-session -- the names are confirmed in the browser's accessibility tree of the sideloaded pane, which needs a window

- [ ] Add `aria-label` to `#tab-settings` ("Settings"), `#tab-rules` ("Rules"), `#tab-more` ("More features"), both `.aic-copy-btn` buttons ("Copy to clipboard"), `#btn-scroll-top` ("Scroll to top"), `#btn-dismiss-error` ("Dismiss error"), `#btn-toggle-api-key` ("Show API key", switching to "Hide API key"), and every `.aic-btn-clear` ("Clear"). Done when: `grep -c 'aria-label=' src/taskpane/taskpane.html` is at least the number of icon-only buttons listed by `grep -c 'aic-tab--icon\|aic-copy-btn\|aic-btn-clear\|btn-scroll-top\|btn-dismiss-error\|btn-toggle-api-key' src/taskpane/taskpane.html`.
- [ ] Wrap the `summary-style` and `improve-focus` radio groups in `<fieldset>` with a `<legend>` carrying their current visible heading text, and give the "Preset Rules" group the same treatment instead of its orphan `<label>`. Done when: `grep -c "<fieldset" src/taskpane/taskpane.html` prints at least `3`, and the visual layout is unchanged (the `fieldset` border and padding are reset in `src/taskpane/taskpane.css`).
- [ ] Give every `input`, `select`, and `textarea` a `<label for>` or an `aria-labelledby`. Done when: the test in the next item passes.
- [ ] Add `src/taskpane/a11y-names.test.ts` (jsdom project) that loads `src/taskpane/taskpane.html` and asserts every `button` has non-empty text or `aria-label`, every form control has a label, and every `input[type=radio]` is inside a `fieldset` with a `legend`. Done when: the test passes, and deleting one `aria-label` makes it fail naming the button id.
- [ ] Sideload the dev build into Outlook on the web and read the accessibility tree in the Edge DevTools Accessibility pane for each icon-only button. Done when: each shows the name above, captured in `docs/captures/taskpane/controls/`.
- [ ] Hold the built surface to the approved mockup: render it (sideloaded, or in the jsdom harness for a component), compare it with the anchors on this section's `**Design:**` line in `docs/design/mockup.md` and their renders under `docs/design/mockup/renders/`, use only design tokens (`docs/design/tokens.json`) and registry icons (`iconSvg()` from `src/ui/icons.ts`), and commit a capture of the result under `docs/captures/taskpane/`. Done when: `python scripts/design-lint.py` exits 0 with the baseline no larger, every difference from the mockup is fixed or recorded as a `**Design deviation:**` naming its follow-up section, and the capture is committed. Cheaper substitute that fails: building from the prose alone, which the capture comparison at review refuses.
- [ ] Commit: `"a11y: an accessible name for every control"`

**Test checkpoint:** `npx jest src/taskpane/a11y-names.test.ts` passes; removing `aria-label` from `#tab-more` fails it naming `tab-more`; the sideloaded pane's accessibility tree names every icon-only button. Cheaper substitute that fails: adding `aria-label` to the tab icons only, which the test fails on the copy and clear buttons.

## 2. Tab Bar Semantics and Arrow Keys

The tab bar looks like tabs but is announced as a row of unrelated buttons, and the **More features** dropdown is invisible to assistive technology until it opens. This section applies the WAI-ARIA Tabs and Menu Button patterns to the tab controller `D03 T01 §2` extracted. Sources: WCAG 2.1 SC 2.1.1 Keyboard and SC 4.1.2; the APG patterns in Inputs.

**Fidelity:** Gemail task pane tab bar (Reply, Draft, Settings, Rules, More features, and its menu) -- docs/captures/taskpane/tab-bar/. The tab bar looks exactly as before; only roles, states, and keyboard behavior change.

**Design:** docs/design/mockup.md#tab-bar, docs/design/taskpane.md#tab-bar -- states: active, inactive, focused, menu open, menu closed -- themes: n/a (roles and focus follow the pane theme) -- density: n/a (one density in a fixed-width task pane)

**Job:** a keyboard user can move between features with the arrow keys and open the extra features menu without a mouse. Consumer: `switchTab` in the tab controller, which the keyboard handlers call.

**Treatment:** `role="tablist"` on the bar, `role="tab"` with `aria-selected` and `aria-controls` on each tab, roving `tabindex` (only the active tab is in the tab order), Left and Right wrap, Home and End jump; the **More features** button has `aria-haspopup="menu"` and `aria-expanded`, its list is `role="menu"` with `role="menuitem"` children, Up and Down move within it, and Escape closes it and returns focus to the button. Cheaper substitute that fails the checkpoint: adding the roles without the keyboard handlers, which the arrow-key tests fail.

**Chrome:** consume `switchTab` and `TAB_CONFIG` from the tab controller of D03 T01 §2 and the focus ring of `docs/design/taskpane.md#buttons`. Do not invent a second tab-switching path for the keyboard.

**Needs:** Outlook client (sideload)

**Requires:** display-session -- the keyboard model is driven by hand in the sideloaded pane, which needs a window

- [ ] Add the tab and menu roles and states to the markup in `src/taskpane/taskpane.html`, and give each feature section the matching `role="tabpanel"` and `aria-labelledby`. Done when: the jsdom test below finds exactly one `aria-selected="true"` tab after load.
- [ ] Add a `keydown` handler to the tab list in the tab controller implementing Left, Right, Home, and End with roving `tabindex`, calling `switchTab` on move (automatic activation). Done when: a jsdom test presses Right from **Reply** and asserts **Draft** has focus, `aria-selected="true"`, and `tabindex="0"`, and Left from **Reply** wraps to the last tab.
- [ ] Add the menu button behavior: Enter, Space, and Down open the menu and focus its first item, Up and Down move, Enter activates, Escape and Tab close it; `aria-expanded` tracks the state. Done when: a jsdom test opens with Enter, moves with Down, closes with Escape, and asserts focus returned to `#tab-more` with `aria-expanded="false"`.
- [ ] Keep `switchTab` the only function that changes the active tab, and update `aria-selected` and `tabindex` inside it so mouse and keyboard stay in step. Done when: a test clicks **Draft** with the mouse event and asserts the same attribute state as the keyboard test.
- [ ] Drive the pane in Outlook on the web with the keyboard only: reach the tab bar, move through every tab, open the menu, choose **Translate**, and close it with Escape. Done when: the run is recorded in the commit body and a capture of the open menu with focus is committed under `docs/captures/taskpane/tab-bar/`.
- [ ] Hold the built surface to the approved mockup: render it (sideloaded, or in the jsdom harness for a component), compare it with the anchors on this section's `**Design:**` line in `docs/design/mockup.md` and their renders under `docs/design/mockup/renders/`, use only design tokens (`docs/design/tokens.json`) and registry icons (`iconSvg()` from `src/ui/icons.ts`), and commit a capture of the result under `docs/captures/taskpane/`. Done when: `python scripts/design-lint.py` exits 0 with the baseline no larger, every difference from the mockup is fixed or recorded as a `**Design deviation:**` naming its follow-up section, and the capture is committed. Cheaper substitute that fails: building from the prose alone, which the capture comparison at review refuses.
- [ ] Commit: `"a11y: tab bar and features menu follow the ARIA tabs and menu button patterns"`

**Test checkpoint:** `npx jest src/taskpane/tabs.test.ts` passes the arrow, wrap, Home, End, menu open, move, and Escape cases; removing the `keydown` handler fails the arrow cases; the keyboard-only drive in Outlook on the web reaches every feature. Cheaper substitute that fails: `tabindex="0"` on every tab, which lets Tab walk the bar but fails the roving-tabindex assertion.

## 3. Live Regions and Focus Management

A sighted user sees the error banner appear or the result card fill; a screen-reader user hears nothing, because neither is a live region and focus stays on the button that started the request. This section turns the banner into announced alerts and the confirmations into status notifications. Sources: WCAG 2.1 SC 4.1.3 Status Messages and SC 2.4.3 Focus Order.

**Fidelity:** Gemail task pane status surfaces (error banner, saved confirmations, loading overlay, result card heading) -- docs/captures/taskpane/status/. No visual change beyond a visible focus ring on the result heading when focus moves there.

**Design:** docs/design/mockup.md#streaming-and-stop, docs/design/mockup.md#error-banner, docs/design/mockup.md#undo-confirmation, docs/design/taskpane.md#status-and-errors -- states: error shown, error dismissed, saved, loading, result ready -- themes: n/a (announcements are not themed) -- density: n/a (one density in a fixed-width task pane)

**Job:** a screen-reader user can hear alerts and status notifications that a request failed, a setting saved, or a result is ready, and continues from the result without hunting for it. Consumer: assistive technology through the live regions and the focus moves.

**Treatment:** `role="alert"` on `#error-banner`, `role="status"` on every saved confirmation and on the loading message, focus moved to the result card heading (`tabindex="-1"`) when a result renders, and focus returned to the triggering button when the error is dismissed. Cheaper substitute that fails the checkpoint: `aria-live` on the whole pane, which announces every keystroke echo and fails the one-announcement-per-event test.

**Chrome:** consume `showError`, `hideError`, `showLoading`, and `hideLoading` from `src/ui/` (extracted by the task pane split) as the one place these attributes and focus moves live. Do not add announcements from inside feature panels.

**Needs:** Outlook client (sideload)

**Requires:** display-session -- announcements are checked with Narrator running against the sideloaded pane, which needs a window

- [ ] Add `role="alert"` to `#error-banner` and make `showError` in `src/ui/` replace the message text after the banner is shown, so the change is announced even when the same banner is reused. Done when: a jsdom test asserts the role and that a second `showError` call changes the text node.
- [ ] Add `role="status"` to `#rules-saved-msg`, `#settings-saved-msg`, `#clear-data-msg`, `#test-connection-result`, and the loading message element. Done when: `grep -c 'role="status"' src/taskpane/taskpane.html` prints at least `5`.
- [ ] Make each result card heading focusable with `tabindex="-1"` and move focus to it from the shared result helper when a result renders. Done when: a jsdom test renders a draft result and asserts `document.activeElement` is the draft result heading.
- [ ] Record the element that had focus when `showError` ran, and restore focus to it in `hideError` (the dismiss button path). Done when: a jsdom test focuses `#btn-generate`, shows and dismisses an error, and asserts focus is back on `#btn-generate`.
- [ ] Check the live regions with the accessibility tree instead of a screen reader: in Edge DevTools on the sideloaded pane, trigger a failure (an invalid key) and a save, and read the `alert` and `status` nodes and their text in the Accessibility pane. Done when: both nodes and their text are quoted in the commit body; the audible pass with Narrator and NVDA is the operator's (`D99 T01 §7`).
- [ ] Hold the built surface to the approved mockup: render it (sideloaded, or in the jsdom harness for a component), compare it with the anchors on this section's `**Design:**` line in `docs/design/mockup.md` and their renders under `docs/design/mockup/renders/`, use only design tokens (`docs/design/tokens.json`) and registry icons (`iconSvg()` from `src/ui/icons.ts`), and commit a capture of the result under `docs/captures/taskpane/`. Done when: `python scripts/design-lint.py` exits 0 with the baseline no larger, every difference from the mockup is fixed or recorded as a `**Design deviation:**` naming its follow-up section, and the capture is committed. Cheaper substitute that fails: building from the prose alone, which the capture comparison at review refuses.
- [ ] Commit: `"a11y: announced status and errors, and focus that follows the work"`

**Test checkpoint:** `npx jest src/ui src/taskpane` passes the role, re-announcement, result-focus, and focus-restore tests; removing the focus move from the result helper fails the result-focus test; the Narrator run announces both the error and the finished result. Cheaper substitute that fails: `aria-live="polite"` on the error banner without re-setting its text, which the re-announcement test fails.

## 4. Reduced Motion and a Skip Link

Some users get motion sickness from animation, and operating systems expose that preference; the pane ignores it. Keyboard users land on the header and tab bar before every panel. Sources: WCAG 2.1 SC 2.3.3 Animation from Interactions (AAA, adopted because the cost is one media query) and SC 2.4.1 Bypass Blocks.

**Fidelity:** Gemail task pane motion (spinner, focus pulse, slide-in) and the top of the pane -- docs/captures/taskpane/motion/. The skip link is invisible until focused, then appears at the top left in the focus style.

**Design:** docs/design/mockup.md#streaming-and-stop, docs/design/mockup.md#surfaces-the-mockup-does-not-draw, docs/design/taskpane.md#motion -- states: motion allowed, motion reduced, skip link focused -- themes: n/a (the skip link uses the pane focus tokens) -- density: n/a (one density in a fixed-width task pane)

**Job:** a user who asked the operating system for less motion sees no animation, and a keyboard user skips straight to the active panel. Consumer: the CSS engine for the media query; the active feature section for the skip target.

**Treatment:** one `@media (prefers-reduced-motion: reduce)` block that disables `spin`, `focusPulse`, and `slideIn` and replaces the spinner with a static indicator, and a "Skip to feature" link as the first focusable element targeting the active section. Cheaper substitute that fails the checkpoint: shortening the animation durations, which still animates and fails the computed-style test.

**Chrome:** consume the tokens and focus ring in `docs/design/taskpane.md#buttons` and the loading element from `src/ui/`. Do not invent a second loading indicator for reduced motion.

**Needs:** Outlook client (sideload)

**Requires:** display-session -- reduced motion is checked by enabling the Windows "Animation effects" off setting and watching the sideloaded pane, which needs a window

- [ ] Add a `@media (prefers-reduced-motion: reduce)` block to `src/taskpane/taskpane.css` setting `animation: none` on the elements using `spin`, `focusPulse`, and `slideIn`, and showing a static "working" indicator in place of the spinner. Done when: `grep -c "prefers-reduced-motion" src/taskpane/taskpane.css` prints at least `1`.
- [ ] Add an `<a class="aic-skip-link" href="#app-body">Skip to feature</a>` as the first child of `<body>` in `src/taskpane/taskpane.html`, styled visually hidden until `:focus`, and make its click move focus to the active feature section (via the tab controller). Done when: a jsdom test tabs to the link, activates it, and asserts focus is inside the active `role="tabpanel"`.
- [ ] Add a jsdom test that loads the stylesheet text and asserts the reduced-motion block names every keyframe used in the file (`spin`, `focusPulse`, `slideIn`). Done when: the test passes and fails if a new `@keyframes` is added without being listed.
- [ ] Turn off Windows animation effects, open the pane in new Outlook, and start a generation. Done when: no spinner rotation is visible, recorded with a capture under `docs/captures/taskpane/motion/`.
- [ ] Hold the built surface to the approved mockup: render it (sideloaded, or in the jsdom harness for a component), compare it with the anchors on this section's `**Design:**` line in `docs/design/mockup.md` and their renders under `docs/design/mockup/renders/`, use only design tokens (`docs/design/tokens.json`) and registry icons (`iconSvg()` from `src/ui/icons.ts`), and commit a capture of the result under `docs/captures/taskpane/`. Done when: `python scripts/design-lint.py` exits 0 with the baseline no larger, every difference from the mockup is fixed or recorded as a `**Design deviation:**` naming its follow-up section, and the capture is committed. Cheaper substitute that fails: building from the prose alone, which the capture comparison at review refuses.
- [ ] Commit: `"a11y: honor reduced motion and add a skip link"`

**Test checkpoint:** `npx jest src/taskpane` passes the skip-link and keyframe-coverage tests; adding a new `@keyframes pulse2` used by a class fails the coverage test; with animation effects off the sideloaded pane shows a static indicator. Cheaper substitute that fails: disabling only `spin`, which the keyframe-coverage test fails on `focusPulse` and `slideIn`.

## 5. Contrast Check for the Tokens

Contrast is arithmetic, so it is checked by a script, not by eye. Three pairs already fail (see Current state), including white on the brand blue of every primary button. This section writes the check, fixes the failing tokens, and makes the check a gate so the dark theme (`D06 T04 §2`) and every later color change run through it. Sources: WCAG 2.1 SC 1.4.3 Contrast (Minimum) and SC 1.4.11 Non-text Contrast.

- [ ] Add `scripts/contrast-check.js` (Node, no dependencies) that reads the color tokens of both themes from `docs/design/tokens.json`, reads the foreground and background pairs from `docs/design/contrast-pairs.json` (each with a minimum of `4.5`, or `3` for large text and UI boundaries, and a theme name), computes the WCAG ratio, prints one line per pair, and exits `1` on any failure. Done when: it prints one line per pair and exits 0. **Corrected 2026-09-27:** was "parses the `@theme` custom properties in `src/styles/main.css`"; `docs/design/tokens.json` is the canonical source since the design import, and `main.css` only references it.
- [ ] Write `docs/design/contrast-pairs.json` for both themes: every text token on `bg`, `surface`, and `surfaceSunken`, `onBrand` on `brandFill` and on `brandHover`, `brand` on `bg`, `surface`, and `brandTint`, `ai` on `bg` and `aiTint`, `success` on `successTint`, `danger` on `dangerTint`, both diff pairs, and the focus ring and input border against the background at `3`. Done when: every text color token in `docs/design/tokens.json` appears in at least one pair per theme. **Corrected 2026-09-27:** was light-theme pairs over `--color-aic-*`; the token names and the dark set come from `docs/design/tokens.json`.
- [ ] Run the check over the imported tokens and record the ratios: the Fluent Native import of 2026-11-15 set `brand` to `#0f6cbd` with `brandFill` for buttons and `textTertiary` to `#6b6b6b`, and a hand check that day over every text and background pair the artboards use found the lowest at 4.81:1 in the light set and 5.18:1 in the dark set. **Corrected 2026-11-15:** was "the design import already set `brand` to `#1668c9` (white on it 5.44:1) and `textTertiary` to `#686e7a` (4.57:1 on `surfaceSunken`)"; those were the 2026-09-27 design's values, and `aiStrong` no longer exists. Done when: `node scripts/contrast-check.js` exits `0` and the commit body quotes each pair's ratio; a failing pair is fixed in `docs/design/tokens.json` and the mockup together through the `design-sync` skill. **Corrected 2026-09-27:** was "Darken `--color-aic-text-tertiary` and the primary button background"; the operator's contrast decision (2026-09-27) was applied in `docs/design/tokens.json` at the design import, so this item verifies rather than invents the values.
- [ ] Add the check to `scripts/check-all.ps1` as a gate (`node scripts/contrast-check.js`) and add the new token values to the Tokens table of `docs/design/taskpane.md`. Done when: `pwsh scripts/check-all.ps1` lists a `contrast` gate with `PASS`.
- [ ] Commit: `"a11y: contrast check for every token pair, and the failing tokens fixed"`

**Test checkpoint:** `node scripts/contrast-check.js` exits `0` over both themes and exits `1` naming the pair when `color.light.textTertiary` is set back to `#8e95a2` in a scratch copy of `docs/design/tokens.json`; `pwsh scripts/check-all.ps1` shows the `contrast` gate. Cheaper substitute that fails: checking only body text on white, which misses the button pair and the dark theme.

## Verification

- [ ] `pwsh scripts/check-all.ps1` -- exits 0: production build, typecheck, lint, tests, manifest, contrast, TODO gates green
- [ ] `npx jest --ci` exits 0 with this file's test files reporting (`a11y-names`, `tabs`, the status and focus tests, the motion tests)
- [ ] A keyboard-only pass through every tab and control in the sideloaded pane in both supported clients, recorded in the file closeout; the screen-reader pass is `D99 T01 §7`
