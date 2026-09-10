# Accessibility

## Contrast (verified 2026-09-10, `node scripts/contrast.mjs`, 22/22 AA)

| Pair | Ratio |
|---|---|
| Light ink on paper | 14.24:1 |
| Dark ink on paper | 15.72:1 |
| Light ink on paper-raised | 15.07:1 |
| Dark ink on paper-raised | 13.55:1 |
| Light muted on paper | 5.91:1 |
| Dark muted on paper | 8.45:1 |
| Light accent-ink on accent (resting CTA) | 5.72:1 |
| Dark accent-ink on accent (resting CTA) | 6.31:1 |
| Light paper on accent-strong (hover CTA) | 10.22:1 |
| Dark paper on accent-strong (hover CTA) | 9.92:1 |
| Accent-strong on paper (text, focus, error) | 10.22:1 / 9.92:1 |
| Accent-strong on accent-soft (badge, error chip) | 8.50:1 / 7.33:1 |
| Accent-ink on support-1 | 5.21:1 / 5.75:1 |
| Accent-ink on support-2 | 9.24:1 / 10.20:1 |
| Accent-ink on support-1-soft | 11.99:1 / 13.23:1 |
| Accent-ink on support-2-soft | 12.92:1 / 14.26:1 |

All pairs meet WCAG AA (≥ 4.5:1), resting and hover alike — no
transient exceptions. Primary-button hover pairs the strong fill with
paper text; every other accent-text usage reads `accent-strong` on
paper or soft. Re-run the script after any color change; it exits
non-zero on failure.

## Focus order

Tab order follows source order: header nav → page header actions →
lab sections top to bottom. Every interactive element shows a 2px
strong `focus-visible` ring. Verify on `/design` by tabbing from the
top: brand link, nav links, index button, then each section's controls.

## Reduced motion

All transitions, the punch press, and the quarantined breakout drift
ship a `prefers-reduced-motion: reduce` fallback that removes
transforms and animation. The lab's `<style>` block additionally
freezes lab-level animation under reduced motion. The quiet wrapper
adds no motion of its own.

## Notes per component (WAG-style)

- **Button:** native element (or anchor for navigation); disabled uses
  `disabled` / `aria-disabled`; label is always visible text. Punch
  frame (2px ink border, hard shadow) is decorative; the label contrast
  carries meaning.
- **Card / Badge / Icon:** static; icons are `aria-hidden` unless given
  a label; badges are never interactive.
- **Input / Textarea / Select:** visible label, `aria-invalid` and
  `aria-describedby` on error, `role="alert"` error text.
- **Nav:** semantic list; current page uses `aria-current="page"`.
- **Table:** sortable headers are `<button>`s; `aria-sort` maintained
  by the inline script.
- **Modal:** native `<dialog>` — platform focus trap, Escape, backdrop
  close; labelled by its title.
- **Tooltip:** appears on hover and focus-within; Escape blurs the
  trigger; content is short plain text via `role="tooltip"`.
- **AuthForm:** invalid submit writes an `aria-live` summary and moves
  focus to it.
- **Empty / Error:** error state uses `role="alert"`; both offer the
  next action as a real button.
