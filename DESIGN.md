---
name: Mistystep Shop System
description: Generic-clean Carbon-based design system for the 12k-item TTRPG price guide; fantasy lives in tokens.
colors:
  vellum: "#f4f1ea"
  leaf: "#ffffff"
  leaf-deep: "#e8e2d4"
  ink: "#161616"
  faded-ink: "#525252"
  ruled-line: "#c6c0b2"
  coin-edge: "#6f6a5e"
  ember: "#9e2b1e"
  ember-deep: "#7c2117"
  ember-wash: "#f9e9e4"
  witchlight: "#0f62fe"
  blood-mark: "#b81922"
  rarity-common: "#525252"
  rarity-common-ground: "#e8e4d8"
  rarity-uncommon: "#1e6b34"
  rarity-uncommon-ground: "#e3ecdf"
  rarity-rare: "#0b4fa0"
  rarity-rare-ground: "#e0e9f5"
  rarity-very-rare: "#6b2fa0"
  rarity-very-rare-ground: "#e9e2f4"
  rarity-legendary: "#7a4a00"
  rarity-legendary-ground: "#f3e8cf"
  rarity-artifact: "#5c3d00"
  rarity-artifact-ground: "#efe3c2"
  rarity-unclassified-ground: "#e4e0d4"
typography:
  title:
    fontFamily: "-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, sans-serif"
    fontSize: "28px"
    fontWeight: 700
    lineHeight: 1.2
  body:
    fontFamily: "-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, sans-serif"
    fontSize: "12px"
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: "0.08em"
  price:
    fontFamily: "ui-monospace, SF Mono, Cascadia Code, Menlo, Consolas, Courier New, monospace"
    fontSize: "16px"
    fontWeight: 700
    lineHeight: 1.5
    fontFeature: "tnum"
  small:
    fontFamily: "-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.4
  section:
    fontFamily: "-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, sans-serif"
    fontSize: "20px"
    fontWeight: 600
    lineHeight: 1.3
rounded:
  sm: "2px"
  md: "4px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
components:
  button-primary:
    backgroundColor: "{colors.ember}"
    textColor: "{colors.leaf}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    padding: "8px 24px"
  button-primary-hover:
    backgroundColor: "{colors.ember-deep}"
    textColor: "{colors.leaf}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    padding: "8px 24px"
  input-search:
    backgroundColor: "{colors.leaf}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "8px 16px"
    height: "40px"
  chip-filter:
    backgroundColor: "{colors.leaf}"
    textColor: "{colors.faded-ink}"
    typography: "{typography.body}"
    rounded: "{rounded.sm}"
    padding: "4px 16px"
  chip-filter-active:
    backgroundColor: "{colors.ember}"
    textColor: "{colors.leaf}"
    typography: "{typography.body}"
    rounded: "{rounded.sm}"
    padding: "4px 16px"
  row-plate:
    backgroundColor: "{colors.leaf}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    padding: "0 16px"
    height: "44px"
  row-plate-active:
    backgroundColor: "{colors.ember-wash}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    padding: "0 16px"
    height: "44px"
---

# Design System: Mistystep Shop System

## Overview

**Creative North Star: "The Screen"**

The system takes its world from the DM screen: a dense, tabbed quick-reference instrument built for answers under pressure. Panels sit side by side like the leaves of a screen; the filter bar is the spine; rows are set in one fixed invariant measure so the eye never re-calibrates. Structure is generic-clean Carbon underneath — four-theme layering, state math, contrast table — so future sibling surfaces (feats, species, character sheets) inherit the skeleton untouched. Fantasy flavor is confined to tokens, never layout.

Material character is flat and instrumental: no chrome, no parchment costumes, no boxed-in ornament. Depth is expressed as a forward step — the active row brightens and weighs up rather than acquiring borders. One flat accent owns live state and nothing else. Motion is single-gesture and named: the detail sheet opens in one pull with legible states. Imagery stance is terse and tabular; numerals align, labels ride in small caps, and density is the aesthetic.

**Key Characteristics:**
- Screen-like: tabbed dense panels, spine filter bar, one-pull detail sheets.
- Invariant measure: every row shares one fixed rhythm (The Plate Measure).
- Forward-step state: selection brightens and weighs, never boxes (The Forward Step).
- Single accent law: one flat accent owns live state only (The Single Accent Law).
- Generic-clean bones, fantasy in tokens: reusable by sibling surfaces.

## Colors

Restrained single-accent strategy on warm paper neutrals (neutrals plus one accent): the visitor came to operate, and the palette spends its one color only where the shop is live.

### Primary
- **Hearth Ember** (#9e2b1e): the one flat accent, reserved for live state only — the pressed filter chip, the stepped row's kin, the primary action. White text on ember reads 7.45:1; ember text on vellum reads 6.61:1. Its darker step **Banked Ember** (#7c2117) carries hover and active (Carbon state math: darken the accent, never invent a second hue).

### Neutral
- **Vellum** (#f4f1ea): page background; the paper warmth is the fantasy, and every text pair is verified against it.
- **Leaf** (#ffffff): layer-01 — panels, rows, inputs sit one step above vellum.
- **Leaf Deep** (#e8e2d4): layer-02 — row hover ground.
- **Ink** (#161616): primary text (16.04:1 on vellum).
- **Faded Ink** (#525252): secondary text and small-caps labels (6.93:1 on vellum).
- **Ruled Line** (#c6c0b2): dividers only, decorative; never a state signal, never a text ground.
- **Coin Edge** (#6f6a5e): strong borders — input strokes and panel edges (5.39:1 on leaf).
- **Ember Wash** (#f9e9e4): the stepped-row ground; ink on wash reads 15.34:1.
- **Witchlight** (#0f62fe): focus ring only, 2px with 2px offset (5.00:1 on leaf; 3:1 minimum honored with margin).
- **Blood Mark** (#b81922): error text only, always paired with label text or icon, never color alone (5.82:1 on vellum).

### Rarity (label plus pattern, never color alone)
- **Common, unmarked solid** (#525252 on #e8e4d8, 6.15:1): flat ground, no pattern — the quiet default.
- **Uncommon, diagonal hatch** (#1e6b34 on #e3ecdf, 5.40:1): repeating 45-degree hatch over tinted ground.
- **Rare, vertical rule** (#0b4fa0 on #e0e9f5, 6.49:1): repeating vertical rules over tinted ground.
- **Very rare, dotted** (#6b2fa0 on #e9e2f4, 6.56:1): dot grid over tinted ground.
- **Legendary, crosshatch** (#7a4a00 on #f3e8cf, 6.15:1): double diagonal crosshatch over tinted ground.
- **Artifact, flat deep coin** (#5c3d00 on #efe3c2, 7.74:1): solid ground, no pattern — the closed vault; documented 2026-09-09, previously an undocumented implementation value.
- **Unclassified, quiet ground** (#525252 on #e4e0d4, 5.92:1): solid ground for Mundane, Unknown, and Varies — data-honest bands for rows outside the five standard rarities; Unknown Magic wears Rare ink (#0b4fa0, 6.03:1) on the same ground. The word on the band is the signal; these never merge into a standard rarity.
- Every band carries its written label ("Common" … "Legendary"); pattern and hue are redundant cues, the word is the signal.

### Named Rules
**The Single Accent Law.** Ember appears on active filters, the stepped row's kin, and the primary action — nowhere decorative. Its rarity is the point.

## Typography

**Display Font:** none; this is an Operate surface and ships no display face.
**Body Font:** system sans (-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, sans-serif) — zero-asset, incumbent-matched, weight-budget native.
**Label/Mono Font:** system ledger stack (ui-monospace, SF Mono, Cascadia Code, Menlo, Consolas, Courier New, monospace) with tabular figures; extends the incumbent Courier New price face into a full system stack.

**Character:** Workhorse pairing in the Operate register: plainspoken sans for rows and sheets, tabular ledger numerals for every price and numeric column so the measure never shifts, compact uppercase-tracked labels throughout.

### Hierarchy
- **Title** (700, 28px/1.2): panel titles only; one step, never scaled decoratively.
- **Body** (400, 16px/1.5): row text and sheet prose; max line length 65ch in sheets.
- **Label** (600, 12px/1.4, +0.08em tracking, uppercase): filter labels, band words, eyebrows, footer line; always Faded Ink or a rarity ink, never the accent.
- **Price** (700, 16px/1.5, tnum): every price and numeric column; `font-variant-numeric: tabular-nums` plus `font-feature-settings: "tnum"` so columns align across all 11,941 rows.
- **Small** (400, 14px/1.4): dense control text — dropdown buttons, checkbox lists, numeric price fields, pagination, helper notes. Promoted from repeated implementation use (review 2026-09-09).
- **Section** (600, 20px/1.3): component-index section headings only; the shop page itself uses Title for its single panel title.

### Named Rules
**The Ledger Rule.** Any numeral a DM compares across rows — price above all — is set in the price face with tabular figures. Proportional numerals never appear in columns.

## Layout

Screen grammar: a sticky filter-bar spine anchors the top on mobile (leading edge on wide desktop); dense panels tile below in a strict single-column grid at catalogue density; 50 rows per page in the invariant measure, any filter change resetting to page 1. Mobile lands search-first with one-handed reach; desktop adds sortable columns and shareable URL query-param state.

Spacing rides one ramp (4 · 8 · 16 · 24 · 32px): 4px inside bands and chips, 8px control padding, 16px panel padding and row gutters, 24–32px between panels. Rows keep 0 vertical padding and center content in the 44px measure; breathing room comes from the measure itself, not from padding variation.

## Elevation & Depth

Flat by default with forward-step state — no shadows anywhere in the system. Surfaces rest flat on tonal layering (vellum → leaf → leaf-deep); selection and hover respond by stepping the row forward in brightness and weight (leaf-deep on hover, ember-wash plus semibold on the stepped row), never by acquiring boxes, rules, or shadows. The detail sheet is the one lifted plane, and even it lifts by position and gesture rather than by shadow: it docks to the viewport edge and opens in a single committed pull.

### Named Rules
**The Flat-By-Default Rule.** No `box-shadow` in the token set. Depth is conveyed by tonal steps and the forward step; a shadow is a regression, not an upgrade.
**The Forward Step.** Selection brightens and weighs; it never boxes.

## Shapes

Minimal rectangular form language: square rows with no enclosing rules, near-square 2px control corners, 4px panel corners. Borders appear only where the measure demands them — row dividers in ruled-line, input strokes in coin-edge. No pills, no circles, no clipping tricks; rarity bands inherit the 2px corner. The silhouette of the system is the grid of plates, not any single curve.

## Components

### Buttons
- **Character:** one flat command key; uppercase-tracked label, ember ground, no shadow.
- **Shape:** near-square corners (2px); padding 8px 24px.
- **Primary:** ember ground, leaf label text; hover and active step to ember-deep, active adding a 1px press; disabled falls to ruled-line ground with faded-ink text.
- **Hover / Focus:** hover darkens (state math); focus-visible draws a 2px witchlight ring with 2px offset on every variant — the Horowitz FIX, carried, never dropped.

### Chips
- **Style:** leaf ground, coin-edge 1px stroke, faded-ink text; 4px 16px padding, 2px corners.
- **State:** unselected rests quiet; selected (`aria-pressed="true"`) fills ember with leaf text and semibold weight — the accent spending its single vote. Focus-visible takes the witchlight ring.

### Price Row Plate (signature)
- **Character:** the invariant plate — every row one 44px measure, band + name + source note + right-aligned ledger price.
- **Background:** leaf at rest, leaf-deep on hover, ember-wash plus semibold weight when stepped.
- **Border:** ruled-line divider below only; no enclosing rules, no cards.
- **Internal Padding:** 0 vertical, 16px horizontal; numerals tabular so prices align down the page.

### Rarity Bands (signature)
- **Style:** label word always present; tinted ground per rarity with a distinct CSS pattern (solid, diagonal hatch, vertical rule, dot grid, crosshatch); 2px corners, 4px 8px padding.
- **State:** bands carry no interactive state; they are read-only encodings that survive color-blindness because the word does the work.

### Inputs / Fields
- **Style:** leaf ground, 1px coin-edge stroke, ink text; 40px height, 8px 16px padding, 2px corners.
- **Focus:** witchlight 2px ring plus 2px offset; the stroke never shifts color to signal focus (rings do that job).
- **Error / Disabled:** error text in blood-mark paired with a written message; disabled uses ruled-line ground with faded-ink text.

### Navigation
- **Style:** the shop chrome is minimal — leaf header bar with wordmark and section label over a ruled-line divider; small-caps faded-ink footer line. The spine filter bar is sticky (top on mobile) and behaves as the screen's spine: search lands first, chips answer instantly.
- **Mobile treatment:** search-first landing, one-handed reach, row activation opens the one-pull sheet. Below 700px the spine keeps search plus a Filters (N) disclosure sticky while the remaining groups collapse; the results table shows Name/Rarity/Price with Source/Type/Attunement kept in the sheet.

### Detail Sheet (signature)
- **Character:** the one lifted plane; grab handle, rarity eyebrow, title, ledger price, key rules facts at 65ch.
- **Behavior:** closed → pulling → open → dismissed in one committed gesture; no intermediate resting states.

## Do's and Don'ts

### Do:
- **Do** keep fantasy in tokens; structure stays generic-clean for sibling reuse.
- **Do** give every row the same 44px invariant measure (The Plate Measure).
- **Do** encode rarity with label plus pattern, never color alone.
- **Do** let one flat accent own live state and nothing else (The Single Accent Law).
- **Do** set every compared numeral in tabular ledger figures (The Ledger Rule).
- **Do** draw focus-visible as a 2px witchlight ring with 2px offset on every interactive component.
- **Do** verify every text pair against the contrast table (4.5:1 text, 3:1 large and indicators) before baking a value.

### Don't:
- **Don't** box rows in chrome, rules, or cards to signal state — step forward instead.
- **Don't** amalgamate token systems; Carbon structure governs, others inform.
- **Don't** spend the accent decoratively; its rarity is the point.
- **Don't** promote the shop page's composition into the global world.
- **Don't** ship a webfont or image asset for system chrome; weight is a feature.
- **Don't** signal error, rarity, or state by color alone — pair every color with a word, pattern, or ring.
