import StyleDictionary from 'style-dictionary';

// Choice: Style Dictionary v4 over Terrazzo. Both read DTCG ($value/$type)
// natively, but Style Dictionary v4 has the stable css/variables format with
// selector + outputReferences options this build relies on (semantic vars
// emitted as var() aliases of primitive vars, so the accent knob stays a
// one-line change). Terrazzo was evaluated and deferred; revisit if the
// system ever needs multi-platform (iOS/Android) output from one source.

// Strip the structural segments (primitive/semantic/light/dark) so both
// modes emit identical variable names: :root carries primitives + light
// semantics, .dark overrides with dark semantics.
StyleDictionary.registerTransform({
  name: 'ds/strip-group',
  type: 'name',
  transform: (token) =>
    token.path.filter((seg) => !['primitive', 'semantic', 'light', 'dark'].includes(seg)).join('-'),
});

const isDark = (token) => token.path.includes('dark');
const isNotDark = (token) => !isDark(token);

export default {
  source: ['tokens/tokens.json'],
  platforms: {
    css: {
      transformGroup: 'css',
      transforms: ['ds/strip-group'],
      buildPath: '.sd-tmp/',
      files: [
        {
          destination: 'tokens-light.css',
          format: 'css/variables',
          filter: isNotDark,
          options: {
            selector: ':root',
            outputReferences: true,
          },
        },
        {
          destination: 'tokens-dark.css',
          format: 'css/variables',
          filter: isDark,
          options: {
            selector: '.dark',
            outputReferences: true,
          },
        },
      ],
    },
  },
};
