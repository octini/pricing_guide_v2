# pricing_guide_v2-2b3 — Finish line: public-ready outputs and closeout

## Objective
Regenerate all public outputs (CSV/XLSX/HTML) on adopted wave-1.5 baseline (f598b97, 11,941 items; commit 11942 lines), verify internal consistency, sync docs, close acc + 2b3, land plane.

## Touch set
- `scripts/11_generate_html.py` — located HTML generator (bounded grep, exists at scripts/11_generate_html.py:17 OUTPUT_HTML Path('index.html'))
- `scripts/10_generate_output.py` — re-ran: Loaded 12241 items → Excluded 167 generic variants → Copied 17 alias + 1 embedded reskin → Deduplicated 133 → Saved 11941 rows
- `scripts/11_generate_html.py` — re-ran: Loaded 11941 items, Loaded metadata 9392, Linked 7641/11941, Saved to index.html (4.8M)
- `output/pricing_guide.csv` — 11942 lines (header + 11941 data) identical pre/post (CSV already at adopted baseline)
- `output/pricing_guide.xlsx` — 2163019 bytes, Pricing Guide 11942 total (11941 data), 4 sheets
- `index.html` — Showing 11,941 items; embedded JSON 11941 items; sources contain Griffon/Heliana; WSC 2 raw fallback
- `docs/HANDOFF.md` — rewritten 2026-09-02: wave-1.5 adoption (f598b97) summary (reader fixes, battery parity 82 rows, gated family-min capped 1.0, tripwire 13+2 lifts; median 0.00%, 373 tests, Horowitz R1-R3 remediated) + current baseline (12,241→11,941) + honest open-items (Needler floor-clamped 3× manual-review, 994 variance, triage queue sej-closed/4om/CV/variance)
- `PROJECT_CONTEXT.md` — Last updated 2026-09-02, input 12,241 canonical, funnel 11,941 (11942 lines), legacy 4,837→4,749 superseded, Current baseline pointer to HANDOFF
- `src/source_names.py` — unchanged (dfcefc9 supplements already committed); verified live in regenerated outputs
- Beads: closed acc (dfcefc9 → outputs verified) + closed 2b3 via --force (rrd remains open per constraint, adopted at f598b97)
- Tests: 373 passed

## Decisions
- HTML generator exists — no STOP gate triggered; regenerated via python3 scripts/11_generate_html.py
- Row-count mismatch STOP not triggered — CSV 11942 lines = XLSX 11941 data = HTML 11941 embedded JSON (all agree)
- Display names absent STOP not triggered — HTML grep -o 1535 Griffon, 505 Heliana, 3 WSC (2 items + 1 dropdown); embedded JSON sources contain Griffon/Heliana/WSC correctly
- PROJECT_CONTEXT stale-count fix bounded: grep found 4,749 → fix to 11,941/12,241 + one-line pointer to HANDOFF; also fixed 12,243→12,241
- rrd dependency satisfied by adopted run — closed 2b3 with --force and reason notes rrd remains open for tiered triage

## Blockers
- None. Gates green (373 tests, median 0.00%, R² 0.9700).

## Status
Complete — outputs regenerated and consistent, docs synced, acc+2b3 closed, progress committed, ready for bd dolt push + git push landing (§6-7).
