# Shop PRD — shop.mistystep.net restyle

Status: draft for sign-off. Gates token work: no token values until this PRD
plus `docs/design_principles.md` are signed off (per n1y.4 gate).
Direction: The Screen (locked by user 2026-09-09; replaces provisional).
Grounding: PRODUCT.md, seed DESIGN.md, `.impeccable/surfaces/index-html.md`.

## Problem

~12,000 priced magic items exist as data, but the current page does not let a
DM or player find an item's price and key rules facts in seconds — on a phone
mid-session or on desktop while planning.

## Users / jobs

- DM in session (mobile, one-handed): search-first quick lookup at the table.
- DM or player between sessions (desktop): compare and filter across the
  catalogue while planning.

## Scope

Restyle of the generated `index.html` only, rendered by
`scripts/11_generate_html.py` from `output/pricing_guide.csv` (11,941 rows).
No pipeline, data, or publish-config changes. Single static page, inline
style, no build step; Cloudflare Pages serves the committed root file.

## Requirements (from n1y.5 Q5–Q8)

1. Search: debounced client-side full-text over name + type + source + key
   rules text (Q5).
2. Filters: price-range slider, attunement toggle, rarity, type, source; sort
   by price / name / rarity (Q6).
3. Pagination: 50 items per page; any filter change resets to page 1.
4. Mobile: search-first landing, sticky filter bar, tap-row detail sheet,
   one-handed use (Q7).
5. Weight budget: load well under the current ~5MB single file, or split the
   data payload (Q7).
6. Desktop: shareable filtered views via URL query params; sortable columns
   (Q8).

## Non-goals

- Saved lists (deferred unless a day-one need emerges).
- Design-system global extraction (waits for a second consumer).
- Further filter refinements: expected as follow-up iteration after hands-on
  use, not gold-plated now.
