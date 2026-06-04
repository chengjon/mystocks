# ArtDecoDynamicSidebar SCSS Style Split Report

## Scope

- Target: `web/frontend/src/components/artdeco/trading/styles/ArtDecoDynamicSidebar.scss`
- Consumer: `web/frontend/src/components/artdeco/trading/ArtDecoDynamicSidebar.vue`
- Change type: style-structure refactor only

## Split Boundary

- `ArtDecoDynamicSidebar.container.scss`: fixed sidebar container and decorative background pattern.
- `ArtDecoDynamicSidebar.header.scss`: header shell, corner ornaments, logo frame, and divider.
- `ArtDecoDynamicSidebar.modules.scss`: module tab layout and active/hover states.
- `ArtDecoDynamicSidebar.navigation.scss`: navigation sections, items, hover states, and active states.
- `ArtDecoDynamicSidebar.footer.scss`: footer ornament and footer label styling.
- `ArtDecoDynamicSidebar.motion-responsive.scss`: keyframe animation, animation utility, and responsive width rules.

## Notes

- The original imported entry path is retained.
- The consumer Vue file is intentionally unchanged.
- The entry keeps the file's existing Sass import style to avoid introducing unrelated `@use` migration semantics.

## Verification

- Partial content equivalence: each partial exactly matches the corresponding original line range.
- Sass CSS equivalence: old snapshot and new entry compile to identical CSS (`24184` bytes each).
- `git diff --check -- <changed files>`: passed.
- `node scripts/check-artdeco-tokens.js --target-file ...`: passed for the entry and all new partials.
- Focused component test: not run; no `ArtDecoDynamicSidebar` focused spec/test file exists in `web/frontend/src`, `web/frontend/tests`, or `tests`.
