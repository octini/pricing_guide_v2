# Reskin content freeze — Wave A (2026-09-10)

Baseline for the pricing-guide reskin. Wave C must reproduce every value
below exactly (hashes, counts, copy strings). Recorded on git `master`
at `85463ea` ("Shop restyle: Mistystep system (The Screen) over 11,941 items").

## 1. File hashes (sha256sum) + sizes (wc -l -c)

| File | sha256 | lines | bytes |
| --- | --- | --- | --- |
| `output/pricing_guide.csv` | `613fa1d3c439c084f87cd55de08ffdfd7cb411097c1bd11255be1428bbab442d` | 11942 | 2878894 |
| `items-data.js` | `bb0c38c1a53cd0dbbffee4e036c1b1c5b4a93c873f00f97ddd758949e86ffa27` | 0 (single line, no trailing newline) | 4947493 |
| `scripts/11_generate_html.py` | `0dac4d7fdde0777358aeb2d5251cce783e7a20badd6e048eaf941bf77c858111` | 1553 | 69273 |

Reproduce with:

```bash
sha256sum output/pricing_guide.csv items-data.js scripts/11_generate_html.py
wc -l -c output/pricing_guide.csv items-data.js scripts/11_generate_html.py
```

## 2. Row counts

- CSV data rows (`wc -l` minus header): **11941**
- `items-data.js` entries (`"name":` occurrences): **11941**
- `window.MISTYSTEP_ITEMS` tail marker ends with the Zulkoon entry (`...items.html#zulkoon_scag...`)
- Rendered initial count (index.html line 606 + generator line 873): **Showing 11,941 items**
- CSV header: `"Name","Source","Type Code","Type","Rarity","Attunement","Price (gp)","Price Formatted","Price Low","Price High","Confidence","Price Source","URL","Notes","Has Reference"`

## 3. Exact copy strings (index.html raw HTML; generator mirror noted)

- `<title>` (line 6; generator line 273): `Mistystep &mdash; Magic Item Pricing Guide`
- Wordmark (line 510): `Mistystep`
- H1 (line 511): `Magic Item Pricing Guide`
- Subtitle (line 512; generator line 779, `{len(df):,}` formatted): `11,941 items &middot; prices in gp`
- Results count, initial (line 606; generator line 873): `Showing 11,941 items`
- Results note (line 607): `50 per page &middot; select a row for details`
- Search placeholder (line 519): `Search name, type, source, rules&hellip;`
- Source dropdown search (line 535): `Search sources...`
- Type dropdown search (line 550): `Search types...`
- Empty state, data failed to load (line 797; generator line 1064): `Item data could not be loaded. Open this page next to items-data.js (same folder) or serve the folder over HTTP.` with count `Showing 0 items` (line 798; generator line 1065)
- Empty state, filters match nothing (line 811; generator line 1078): `No items match these filters. ` followed by buttons `Clear price` (`#empty-clear-price`) and `Reset filters` (`#empty-reset`), with count `Showing 0 of N items` (line 810; generator line 1077, `toLocaleString('en-US')`)
- Paged count format (lines 814-816; generator lines 1081+): `Showing X–Y of N items` (en-dash U+2013, `toLocaleString('en-US')`)
- Footer (line 650; generator line 917): `Mistystep shop system &middot; the screen &middot; prices in gp`
- Filter toggles: `Show filters` / `Hide filters` (line 521, JS line 917), `Reset filters` (line 597), `Undo reset` (line 598), attunement chips `Any` / `Requires attunement` / `No attunement`, sort options `Name A&ndash;Z`, `Price low&ndash;high`, `Rarity low&ndash;high`, `Source A&ndash;Z`, `Type A&ndash;Z`, `Attunement`
- Detail sheet: `Open on 5e.tools` (line 644), `Close` (line 645)

## 4. Pre-reskin status

All four content/template files (`output/pricing_guide.csv`,
`items-data.js`, `scripts/11_generate_html.py`, `index.html`) are
git-tracked and were `git status` clean at freeze time. Wave A adds only
`docs/reskin-freeze.md` (this file) and `design-system/` (unwired v1.1
copy-in, 30 files); no template, data, or config file is modified.
