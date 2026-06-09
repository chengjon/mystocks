# ArtDecoButton Variants SCSS Style Split Report

Date: 2026-06-05

## Scope

- Split `web/frontend/src/components/artdeco/base/styles/ArtDecoButton.variants.scss` into semantic SCSS partials.
- Preserved the existing module entry consumed by `ArtDecoButton.scss`.
- Did not change Vue, TypeScript, router, API, or runtime logic.

## Split Boundary

- `ArtDecoButton.variants-primary.scss`: default and solid variants.
- `ArtDecoButton.variants-outline-priority.scss`: outline, secondary, priority, and motion variants.
- `ArtDecoButton.variants-market-direction.scss`: rise and fall market-direction variants.
- `ArtDecoButton.variants-pulse.scss`: pulse variant and `pulse-ring` animation.
- `ArtDecoButton.variants-double-border.scss`: double-border variant.

The entry file keeps the original `ArtDecoButton.scss` consumer path intact and re-exports the partials with `@use ... as *` to avoid Sass namespace collisions between similarly named partial modules.

## GitNexus Note

`gitnexus impact ArtDecoButton -r mystocks --depth 2 --summary-only` timed out without returning an impact report. Per the current session constraint, `gitnexus analyze` was not run for this batch. Scope was checked with Git and this batch is style-only SCSS.

## Verification

- SCSS content equivalence: old `ArtDecoButton.variants.scss` body equals concatenated new partials.
- Sass compile equivalence: old and new entries compile to identical CSS.
- CSS SHA-256: `255b1092dbbcbaf2aa9cad554f67fecda538fe6c792218298c00717dee265865`.
- `git diff --check`: passed.
- ArtDeco token validation: passed.
- Focused test: `npm run test -- src/components/artdeco/base/__tests__/ArtDecoButton.spec.ts` passed, 1 test file and 4 tests.

