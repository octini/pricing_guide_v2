---
name: portable-design-system
version: 1.1.0
wave: 5
status: v1.1-complete
source_of_truth: tokens/tokens.json
generator: style-dictionary@4.4.0
entry: src/styles/theme.css
fonts: [Bricolage Grotesque, Inter]
license_notes: Bricolage Grotesque + Inter via Fontsource variable packages (OFL). No third-party design-system code or brand assets.
---

# Design System v1.1 — Trio + Punch (Waves 1–5)

Docs: `docs/principles.md` (why) · `docs/accessibility.md` (contrast,
focus, motion, per-component notes) · `docs/content-voice.md` (voice)
· `docs/changelog.md` (v1.1 stamp). Lab + component index:
`src/pages/design.astro` (route `/design`). Copy-in set: see
AGENTS.md “Design System Usage (v1.1)” and `VERSION`.

## Overview

Original, portable design system. Voice: **cream paper, portfolio trio,
punch frames**. Warm-cream surfaces carry the layout; coral carries
every action, periwinkle and mint mark supporting fills; Button, Card,
and Badge ship with 2px ink borders and a small hard offset shadow.
Calm sections opt back into quiet (hairlines, soft shadow) with one
wrapper. Primitives land in Wave 2; lab, index, principles, and
accessibility pages land in Wave 3; Wave 4 prototypes were
decision-support only and are deleted; Wave 5 locks the verdict into
the base (see `docs/changelog.md`).

Rules that survive every wave:

1. `tokens/tokens.json` (DTCG) is the only source of truth. Never hand-edit
   `dist/tokens.css`; rebuild with `npm run tokens:build`.
2. Components consume **semantic** tokens only (`paper`, `ink`, `accent`,
   `support-1`, `support-2`…), never primitives (`paper-50`, `accent-300`).
3. Every color ships a light + dark pair. Dark mode is class-based
   (`.dark` on `<html>`). Every fill passes AA in both modes, resting
   and hover alike — no transient exceptions.
4. Max two font families. Trio only: the coral ramp is the single knob,
   supports stay fixed, no hue outside the trio. Two border widths
   (hairline quiet, punch default), one soft shadow, one motion pair.

## Colors

Base scale (cream paper, plum ink):

| Role | Light | Dark |
|---|---|---|
| `paper` (page) | `#fbf8f5` | `#241a2e` |
| `paper-raised` (cards, slabs) | `#ffffff` | `#332539` |
| `ink` (primary text) | `#30203a` | `#fbf8f5` |
| `muted` (secondary text) | `#6b5a78` | `#c4b3cc` |
| `border` (quiet lines) | `#e3d2cc` | `#4a3a56` |

Accent ramp (coral, 8 steps — the amp knob):

`100 #ffdbe4` → `200 #ffb3c6` → `300 #ff708f` (core) →
`400 #f06085` → `500 #b81f4d` → `600 #9c1743` → `700 #7a0e35` →
`800 #57233a` (dark soft background)

Semantic mapping: light `accent` = ramp `300`, dark `accent` = ramp
`300` (plum text on top both modes: 5.72:1 / 6.31:1).
`accent-strong` is the hover fill and the accent text color (`700`
light / `200` dark) — darkened past the Wave 4 preview value so the
resting pair AND the hover pair both pass AA. Primary-button hover
pairs the strong fill with `paper` text (10.22:1 / 9.92:1).
`accent-soft` is the tinted background (`100` light / `800` dark), and
`accent-ink` the text on solid accent fills (plum `#30203a` light /
deep plum `#241a2e` dark).

Supports (fixed — the knob never moves them):

| Token | Value | Pairs with |
|---|---|---|
| `support-1` (periwinkle) | `#7894ed` | `accent-ink` (5.21:1 / 5.75:1) |
| `support-1-soft` | `#dde5fd` | `accent-ink` (11.99:1 / 13.23:1) |
| `support-2` (mint) | `#66dfbf` | `accent-ink` (9.24:1 / 10.20:1) |
| `support-2-soft` | `#d3f5e8` | `accent-ink` (12.92:1 / 13.23:1+) |

Text, borders, and focus rings use `accent-strong`, never the coral
fill, so small text always passes: berry on cream 10.22:1, pale pink
on deep plum 9.92:1. Purple/yellow never entered the token set.

### Amp / tone the accent (single-knob path)

Open `tokens/tokens.json`, find `semantic.light.accent` and
`semantic.dark.accent`, and move each one step along the coral ramp:

- **Amp up:** light `300 → 400`, dark `300 → 200`. Louder, same hue.
- **Tone down:** light `300 → 200`, dark `300 → 400`. Quieter, same hue.
- Keep the pair in step (both move the same direction) so modes stay in
  balance, then run `npm run tokens:build` and `node scripts/contrast.mjs`.
  If contrast drops below 4.5:1, step back — the script fails loudly
  (22/22 pairs, resting + hover, light + dark).
- Never add a hue outside the trio. Never move the supports.

Tailwind handles: `ds:bg-accent`, `ds:text-accent-strong`,
`ds:bg-accent-soft`, `ds:text-accent-ink`, `ds:bg-support-1`,
`ds:bg-support-1-soft`, `ds:bg-support-2`, `ds:bg-support-2-soft`,
`ds:border-border`, `ds:bg-paper`, `ds:bg-paper-raised`, `ds:text-muted`.

## Typography

Two families, both variable, both OFL, wired in `src/styles/theme.css`
via Fontsource (`@fontsource-variable/bricolage-grotesque`,
`@fontsource-variable/inter`):

- **Display — Bricolage Grotesque.** `h1/h2/h3` and `.ds-display`.
  Slightly tight (`-0.01em`). Headlines only.
- **Body — Inter.** Everything else; the `html` default.

Tailwind handles: `ds:font-display`, `ds:font-sans` (= Inter body).

## Layout

Single global entry: `src/styles/theme.css`, imported once per Astro Layout:

```astro
---
import '../styles/theme.css';
---
```

Page background and body text come from `@layer base` (`paper` / `ink`),
so unstyled markup already reads correctly in both modes. Space/scale
utilities are Tailwind defaults; spacing tokens arrive with
Wave 2 primitives if needed.

## Elevation

One soft shadow plus the punch default: `--shadow-soft`
(`0 8px 24px -8px rgb(28 20 12 / 0.8 alpha-hex cc)`). Quiet surfaces
and modal panels use it (`.ds-lift` on hover, `[data-voice="quiet"]`
restores it). Button, Card, and Badge ship the punch default instead:
`3px 3px 0 var(--ink)` (buttons, cards) and `2px 2px 0 var(--ink)`
(badges), collapsing to `0 0 0` on press. Tailwind handle:
`ds:shadow-soft`.

## Shapes

Round-flat scale, two border widths:

| Token | Value | Use |
|---|---|---|
| `radius-sm` | 4px | chips, small controls |
| `radius-card` | 8px | quiet cards, fields |
| `radius-punch` | 12px | punch cards (default) |
| `radius-slab` | 16px | large panels |
| `radius-pill` | 100px | pills, badges, toggles |
| `border-hairline` | 1px | quiet borders, fields, overlays |
| `border-punch` | 2px | default Button / Card / Badge borders |

Tailwind handles: `ds:rounded-sm/card/slab/pill`. Punch borders pair
the punch width with the `ink` color; quiet borders pair the hairline
with the `border` color token.

## Components (Waves 2 + 5)

Primitives live in `src/components/ui/` (one file each), patterns in
`src/components/patterns/`, layout in `src/layouts/Base.astro` (imports
`theme.css` once, renders `<slot />`). Every component styles from
semantic `var()` tokens only — no hard-coded hex, no primitive ramps in
component code. Shared motion stays `.ds-lift` (150ms ease-out +
`prefers-reduced-motion` fallback); components add their own guarded
transitions only where `.ds-lift` does not apply.

| Component | File | Notes |
|---|---|---|
| Button | `ui/Button.astro` | primary / secondary / outline × sm / md / lg; renders `<a>` when `href` is set, `<button>` otherwise; pill radius, 2px ink border, hard offset shadow; primary hover swaps to the strong fill with paper text |
| Card | `ui/Card.astro` | raised paper, 2px ink border, 12px radius, hard offset shadow; optional eyebrow/title; `lift` opts into `.ds-lift` |
| Badge / Tag | `ui/Badge.astro` | accent (coral tint) / neutral (quiet role) / outline (strong line); all with 2px ink borders and hard offset shadow; tag = Badge + leading icon |
| Icon | `ui/Icon.astro` | Phosphor wrapper, bounded `name` set, inherits `currentColor` |
| Input / Textarea / Select | `ui/Input.astro` etc. | label + help + error contract, `aria-invalid` / `aria-describedby`, native keyboard behavior; hairline borders, strong hover/focus |
| Nav | `ui/Nav.astro` | semantic list, `aria-current="page"` takes the strong underline |
| Table | `ui/Table.astro` | sortable columns via header buttons, `aria-sort` maintained by inline script |
| Modal | `ui/Modal.astro` | native `<dialog>` (platform focus trap + Escape); `[data-modal-open]` triggers, backdrop click closes; hairline panel, soft shadow |
| Tooltip | `ui/Tooltip.astro` | hover + focus-within reveal, Escape blurs; inverted ink/paper fill |
| PageHeader | `patterns/PageHeader.astro` | compact opener: eyebrow (strong), display `h1`, lede, action slot |
| Header / Footer | `patterns/Header.astro`, `patterns/Footer.astro` | sticky paper bar composing Nav; hairline footer, muted small print |
| AuthForm | `patterns/AuthForm.astro` | PageHeader + Card login (email/password/submit), `aria-live` error summary |
| Empty / Error | `patterns/EmptyState.astro`, `patterns/ErrorState.astro` | centered icon chip + headline + body + action slot |

### Voice: punch by default, quiet on request

Punch is the default component voice. Button, Card, and Badge render
2px ink borders with a small hard offset shadow; pressing a button
drives the shadow into the frame. Fields, overlays, tables, and nav
keep hairline precision in both voices — the punch strip never covered
them, and precision controls stay precise.

Quiet ships as the opt-in wrapper. Wrap any section:

```html
<div data-voice="quiet">
  <!-- Button, Card, Badge render hairlines + soft shadow here -->
</div>
```

The overrides live in `theme.css` (`[data-voice="quiet"]`): hairline
widths, quiet border colors back, card radius to 8px, hard shadows off.
The quiet block carries zero punch tokens (asserted by
`node scripts/smoke.mjs`); punch tokens appear only in the three
component files (sampled by the same script).

Island contracts: Modal, Table-sort, Tooltip, and AuthForm ship
framework-free progressive-enhancement `<script>` blocks today; each file
declares its upgrade path as `<X client:load … />` for Wave 3 framework
adoption. No framework renderer is added in this wave.

Error voice (trio rule): errors reuse the coral family
(`accent-strong` text/borders, `accent-soft` chips/fills) — never a
hue outside the trio. Verified AA: strong on paper 10.22:1 / 9.92:1,
on accent-soft 8.50:1 / 7.33:1 (light/dark).

Interaction rules: every interactive element is keyboard-reachable
(native controls preferred) with a 2px strong `focus-visible` ring;
primary hover swaps to the strong fill with paper text (both modes AA),
active presses into the frame; all motion honors
`prefers-reduced-motion`.

Icons: Phosphor via `phosphor-astro` 2.1.0 (`"phosphor-astro": "^2.1.0"`
in package.json). License MIT, SPDX-License-Identifier: MIT recorded in
`src/components/ui/Icon.astro`; icons © Phosphor Icons. No Fluent,
Atlassian, Material, or Carbon code, patterns, or brand assets anywhere
(the only matches for those names are this paragraph and the Wave 1
prohibition).

Breakout quarantine: the neobrutalist voice (thick borders, hard
shadows, stickers, drift, dot-grid) lives ONLY in
`src/components/demo/Breakout.astro`, gated by
`PUBLIC_DS_BREAKOUT="1"` (default off renders nothing). Core
components never import it; flag-off grep over `ui/`, `patterns/`, and
`layouts/` shows zero breakout tokens.

Tooling note: Astro `outDir` is `./build` (see `astro.config.mjs`) so
production builds never wipe `./dist/tokens.css`, which `theme.css`
imports and which is committed for consumers.

## Do's / Don'ts

Do:

- Reference semantic tokens; rebuild after edits; keep modes paired.
- Amp color by moving along the coral ramp (see above); leave supports fixed.
- Put `.dark` on `<html>` for dark mode; design mobile-first, paper-first.
- Run `node scripts/contrast.mjs` after any color change.
- Wrap calm sections in `data-voice="quiet"` when punch frames feel loud.

Don't:

- Don't consume primitives in components, don't add hues outside the
  trio, don't add font families, don't invent radii/shadows/durations.
- Don't hand-edit `dist/` or add `tailwind.config.*` (Tailwind v4 is
  CSS-first here; config file presence fails the Wave 1 gate).
- Don't copy Atlassian / Fluent / Material / Carbon patterns, code, or
  assets. This system is an original synthesis.
- Don't add icons yet — Phosphor arrives in Wave 2.

## Tooling

- **Generator: Style Dictionary v4** (`sd.config.js` + thin assemble step
  in `scripts/assemble-tokens.mjs`). Chosen over Terrazzo for its stable
  `css/variables` format with `selector` + `outputReferences`: semantic
  vars emit as `var()` aliases of primitive vars, which is what keeps the
  accent knob one line. Rebuild: `npm run tokens:build`. Known benign
  warning: SD reports "filtered out token references" for the light file
  because dark-mode tokens resolve against the same dictionary; verified
  harmless — every `var()` in `:root` resolves within `:root` (same for
  `.dark`), asserted by `node scripts/smoke.mjs`.
- **Stack:** Astro 7.3.2, Tailwind CSS 4.3.3 (`@tailwindcss/vite`,
  `prefix(ds)`, `@custom-variant dark`), `impeccable` 4.1.0
  (`npx impeccable doctor` clean, no drift).
- **Checks:** `npm run tokens:build` (regen clean) ·
  `node scripts/smoke.mjs` (theme compiles, 14 checks incl. support
  utilities, punch defaults, quiet block clean) ·
  `node scripts/contrast.mjs` (22/22 AA, resting + hover, light + dark)
  · grep: no `tailwind.config.*`,
  no Atlassian/Fluent/Material/Carbon references.

## Lab (Waves 3 + 5)

`src/pages/design.astro` (route `/design`) renders every component
with variants: color-trio swatches (solid + soft fills), buttons
(3 variants × 3 sizes + link/disabled + hover/active/focus-visible/
disabled notes), badges + icon set, cards (punch default), nav, full
field set (help/error/disabled), sortable table, modal + tooltip
triggers, auth form, empty/error states, type and spacing/shape scales,
a `.dark` dark-band section reusing the same markup, a quiet-voice demo
section (`data-voice="quiet"` wrapping Button/Card Badge), and the
component index (anatomy / states / do-don't per component).
`Breakout` renders only when `PUBLIC_DS_BREAKOUT="1"`
(default off renders nothing). Lab styles use semantic `var()` tokens
only. Wave 4 decision-support artifacts are deleted: no `ColorVoice`,
no preview pages, no `PreviewTrio` layout, no `preview-trio.css`.

## Verification (recorded 2026-09-09)

- `npm run tokens:build` exits 0, `dist/tokens.css` regenerates from source.
- Contrast spot-checks: light accent 5.45:1, dark accent 9.01:1, ink
  15.95:1 / 16.14:1, muted 5.47:1 / 6.71:1, accent-ink fills 5.82:1 /
  9.24:1 — all ≥ 4.5:1.
- `npx impeccable doctor` → "No drift found", exit 0.

## Verification — Wave 3 v1 close (recorded 2026-09-09)

- `npx astro build` exits 0; `/design` route emits with all 14
  `data-lab` markers present in built HTML; breakout content absent
  with the flag unset; dark-band section present; `.dark` vars resolve.
- `node scripts/smoke.mjs` 7/7 pass; `node scripts/contrast.mjs` 8/8
  AA (plus error-voice pairs in `docs/accessibility.md`).
- Greps clean: no hard hex, no primitive ramps, no breakout imports in
  `ui/` + `patterns/` + `layouts/` + lab; `src/` carries zero brand
  references (remaining matches are the Wave 1 prohibition paragraph
  and stack name in `DESIGN.md`/`docs/`, as in prior waves).
- `npx impeccable doctor` clean. Critique pass on `design.astro`:
  P1 fixed — tooltip trigger changed from nested Button to plain text
  (removed redundant tab stop); logged P2 — lab shows two `h1`s
  (page header + AuthForm demo header), accepted as demo artifact.
- No `.impeccable/design.json` sidecar: the generator (Style Dictionary)
  does not emit one and doctor requires none. Noted, not blocking.

## Verification — Wave 5 v1.1 lock-in (recorded 2026-09-10)

- `npm run tokens:build` exits 0, `dist/tokens.css` regenerates from the
  trio source (coral ramp + fixed supports, no happy-* aliases).
- `node scripts/contrast.mjs` 22/22 AA: resting + hover CTA pairs,
  text/focus/error pairs, support solid + soft pairs, all light + dark.
  Hover fix: light `accent-strong` deepened to `#7a0e35`, primary hover
  pairs the strong fill with `paper` text (10.22:1 / 9.92:1).
- `node scripts/smoke.mjs` 14/14: theme compiles, support utilities
  resolve, punch defaults sampled on Button/Card/Badge, quiet block
  present and carrying zero punch tokens.
- `npx astro build` exits 0; `/design` renders color-trio, quiet-voice,
  dark-band, and breakout-gate sections in punch default; deleted
  artifacts (`design-preview`, `design-preview-punch`, `ColorVoice`,
  `PreviewTrio`, `preview-trio.css`) absent from build output.
- Greps clean: no `tailwind.config.*`, no hard hex in components, no
  primitive ramps in component code, remaining `var(--accent)` usages
  are fills only (primary button, lab trio chip, quarantined breakout),
  no brand references beyond the standing prohibition.
- `npx impeccable doctor` clean.
