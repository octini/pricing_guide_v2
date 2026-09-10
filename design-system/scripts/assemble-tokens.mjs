import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';

// Assembles the two Style Dictionary outputs (light :root + dark .dark)
// into the single dist/tokens.css entry that theme.css imports.
const header = `/**
 * DO NOT EDIT. Generated from tokens/tokens.json via Style Dictionary v4.
 * Rebuild with: npm run tokens:build
 * Source of truth: tokens/tokens.json (DTCG format).
 */
`;

const light = readFileSync(new URL('../.sd-tmp/tokens-light.css', import.meta.url), 'utf8');
const dark = readFileSync(new URL('../.sd-tmp/tokens-dark.css', import.meta.url), 'utf8');

mkdirSync(new URL('../dist/', import.meta.url), { recursive: true });
writeFileSync(
  new URL('../dist/tokens.css', import.meta.url),
  `${header}\n${light.trim()}\n\n${dark.trim()}\n`,
);
console.log('dist/tokens.css written');
