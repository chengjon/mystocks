# ArtDecoSidebar SCSS Style Split Report

## Scope

- Target: `web/frontend/src/components/artdeco/trading/styles/ArtDecoSidebar.scss`
- Consumer: `web/frontend/src/components/artdeco/trading/ArtDecoSidebar.vue`
- Change type: style-structure refactor only

## Split Boundary

- `ArtDecoSidebar.container.scss`: fixed sidebar container and decorative background pattern.
- `ArtDecoSidebar.header.scss`: header shell, corner ornaments, logo frame, logo text, and divider.
- `ArtDecoSidebar.navigation.scss`: navigation sections, nav items, hover state, and active state.
- `ArtDecoSidebar.footer.scss`: footer shell, ornament, and label.
- `ArtDecoSidebar.motion.scss`: fade-in keyframe, animation helper, and desktop-only design note.

## Notes

- The original imported entry path is retained.
- The consumer Vue file is intentionally unchanged.
- The entry keeps the file's existing Sass import style to avoid introducing unrelated `@use` migration semantics.
- GitNexus impact lookup for `ArtDecoSidebar` returned `not_found`; this change only edits SCSS selectors and does not modify Vue/TS symbols.

## Verification

- Partial content equivalence: each partial exactly matches the corresponding original line range.
- Sass CSS equivalence: old `HEAD` entry and new entry compile to identical CSS (`22793` bytes each).
- `git diff --check -- <changed files>`: passed.
- `node scripts/check-artdeco-tokens.js --target-file ...`: passed for the entry and all new partials.
- Focused component test: not run; `web/frontend/tests/unit/components/ArtDecoSidebarV3.spec.ts` imports `ArtDecoCollapsibleSidebar.vue`, not this component.
