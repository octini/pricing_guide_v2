# Changelog

## v1.1.0 — 2026-09-10 — Trio + punch lock-in (Wave 5)

The Wave 4 verdict, locked into the base. Decision-support artifacts are
deleted; the single-knob discipline returns.

- **Color: portfolio trio becomes base tokens.** Coral `#ff708f` is the
  primary accent (8-step coral ramp, the amp/tone knob), periwinkle
  `#7894ed` is support-1, mint `#66dfbf` is support-2 (both fixed),
  on cream paper `#fbf8f5` + plum ink `#30203a`. Purple/yellow never
  entered the token set. The Wave 4 `happy-*` vibrant/pastel aliases
  collapse into the 3 fills (accent, support-1, support-2 + softs);
  every fill ships light + dark and passes AA with its ink.
- **Voice reversed: punch is the default, quiet is opt-in.** Button,
  Card, and Badge ship 2px ink borders with a small hard offset shadow
  (3px buttons/cards, 2px badges, 12px punch card radius) exactly where
  the Wave 4 punch strip had them. Wrap any section in
  `data-voice="quiet"` to restore hairlines + soft shadow for the
  Button, Card, and Badge inside it. Fields, overlays, tables, and nav
  keep hairline precision in both voices.
- **Hover-contrast fix, no exceptions.** Light `accent-strong` deepens to
  `#7a0e35` and primary-button hover pairs the strong fill with `paper`
  text, so resting (5.72:1 / 6.31:1) and hover (10.22:1 / 9.92:1) both
  pass AA in light and dark. Text, borders, and focus rings use
  `accent-strong` throughout; the coral fill is fills-only.
- **Dark mode** carries the derived trio values forward (deep plum paper,
  pale-pink strong, plum-rose soft).
- **Deleted:** `src/components/demo/ColorVoice.astro` + its lab section,
  `src/pages/design-preview.astro`, `src/pages/design-preview-punch.astro`,
  `src/layouts/PreviewTrio.astro`, `src/styles/preview-trio.css`.
  The `/design` lab gains color-trio swatches + a quiet-voice demo section.
- **Gates:** `contrast.mjs` 22/22 (resting + hover, light + dark),
  `smoke.mjs` 14/14 (support utilities, punch defaults sampled, quiet
  block clean), `astro build` 0, `impeccable doctor` clean.

## Wave 4 prototype (decision-support, not lock-in — superseded by v1.1.0)

- **Color question, shown not asked:** three supporting happy hues
  (pink, blue, green) added to `tokens/tokens.json` alongside the
  cream paper and warm accent, which stay as one option. Two demo
  themes render side by side in the `/design` lab: VIBRANT (saturated
  fills, white/espresso accent-ink text) and PASTEL (soft fills, dark
  happy-ink text in both modes). Every new fill ships a light+dark
  pair and every pair passes AA at 4.5:1 or better.
- **Voice dial, middle ground:** a punch strip in the lab shows core
  `Button`, `Card`, and `Badge` at a middle setting (2px ink borders,
  3px hard offset shadow, 12px card radius) between quiet core
  (hairline, soft shadow) and quarantined breakout (3px+ borders,
  6px/4px shadows). Core defaults are untouched; all punch styling is
  scoped overrides in `src/components/demo/ColorVoice.astro`.
- **Trio preview, quiet + punch (decision-support, not lock-in):** two
  preview-only pages reuse every lab section in the proposed portfolio
  trio (paper `#fbf8f5`, ink `#30203a`, coral `#ff708f` primary,
  periwinkle `#7894ed` support-1, mint `#66dfbf` support-2; purple/yellow
  excluded). `/design-preview` re-skins the full lab in the trio with the
  quiet core voice (hairlines, soft shadow); `/design-preview-punch` is
  identical content with the punch wrapper page-wide (2px ink borders,
  small hard offset shadow). Trio values live only in the scoped preview
  theme (`src/styles/preview-trio.css` under `[data-theme="trio"]` via
  `src/layouts/PreviewTrio.astro`); base tokens, theme, components, and
  the `/design` lab are untouched. Vibrant-vs-pastel resolution: trio
  fills render at full saturation (Wave 4 chip slots remap to the exact
  trio hexes); CTA/body fill pairs pass AA in light and the dark band.
- **How the winner locks in (Wave 5):** the user picks one color theme
  and one voice in the lab. The winner becomes the base (tokens and
  component defaults rewritten to it), the loser is deleted from
  tokens, theme, lab, and changelog. No second hue and no second
  voice ship together; the single-knob discipline returns after the
  pick.

## v1.0.0 — 2026-09-09

Comprehensive v1 close (Waves 1–3).

- **Wave 1 foundation:** DTCG tokens (`tokens/tokens.json`), generated
  `dist/tokens.css`, Tailwind v4 CSS-first theme entry
  (`src/styles/theme.css`), Bricolage Grotesque + Inter, single
  vermilion accent ramp with the amp/tone knob.
- **Wave 2 components:** 11 primitives (`Button`, `Card`, `Badge`,
  `Icon`, `Input`, `Textarea`, `Select`, `Nav`, `Table`, `Modal`,
  `Tooltip`), 6 patterns (`PageHeader`, `Header`, `Footer`,
  `AuthForm`, `EmptyState`, `ErrorState`), quarantined `Breakout`
  demo behind `PUBLIC_DS_BREAKOUT`. Phosphor icons (MIT) only.
- **Wave 3 close:** `src/pages/design.astro` lab (all components,
  variants, states, type/spacing scales, dark band, gated breakout,
  component index), `docs/` (principles, accessibility,
  content-voice, changelog), copy-in stamp (`VERSION`, AGENTS.md
  usage), full gate suite green.
