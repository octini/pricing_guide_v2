# Principles

Why the system looks the way it does. Each principle ties to a taste
call visible in the gallery (`src/pages/design.astro`).

1. **Cream paper, trio, punch frames.** Surfaces stay warm cream so
   coral carries every action and periwinkle + mint mark supporting
   fills; Button, Card, and Badge frame content in 2px ink with a
   small hard shadow. Gallery proof: the lab's punch cards and trio
   swatches speak first, quiet sections second.
2. **Semantic tokens only.** Components name roles (`accent`,
   `paper-raised`), never values, so the whole voice retunes from one
   knob. Gallery proof: the dark band re-renders identical markup under
   `.dark` with no per-component overrides.
3. **Compact and round-flat, loud by default.** Tight header, pill
   buttons, 2px ink borders with a hard offset shadow on Button/Card
   Badge — and one wrapper (`data-voice="quiet"`) back to hairlines
   and soft shadow. Gallery proof: the quiet-voice demo section against
   the punch-default lab, plus the radius swatches (sm/card/slab/pill).
4. **Native before custom.** Real buttons, inputs, dialogs, and links
   carry keyboard behavior for free. Gallery proof: the sortable table
   (header buttons + `aria-sort`) and the native-dialog modal.
5. **Trio only, even for errors.** Failure states reuse the coral
   family instead of introducing red. Gallery proof: the error card and
   field errors render in `accent-strong` on `accent-soft` and still
   pass AA.
6. **Motion is a whisper.** A single 150ms lift/press pair, always with
   a `prefers-reduced-motion` fallback. Gallery proof: hover the lift
   card, then emulate reduced motion — all feedback goes static.
