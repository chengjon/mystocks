# ArtDecoButton SCSS Style Split Report

Date: 2026-06-05

## Scope

- Target: `web/frontend/src/components/artdeco/base/styles/ArtDecoButton.scss`
- Consumer: `web/frontend/src/components/artdeco/base/ArtDecoButton.vue`
- Change type: style-structure-only refactor.
- Behavior scope: no Vue template/script changes, no route changes, no API changes, no selector/value edits.

## Split Result

The original 418-line stylesheet now remains as a stable `@use` entrypoint:

- `ArtDecoButton.base.scss`: token imports, base button reset, layout, focus, disabled/loading/block states.
- `ArtDecoButton.icon.scss`: icon, spinner, and text alignment.
- `ArtDecoButton.variants.scss`: default, solid, outline/secondary, priority, motion, rise/fall, pulse, and double-border variants.
- `ArtDecoButton.sizes.scss`: small, medium, large sizing and spinner keyframes.
- `ArtDecoButton.note.scss`: desktop-only design note retained from the original file.

## Verification Notes

- Content equivalence check: concatenating the five partials matches the original `HEAD` content after removing the original style-block indentation.
- CSS equivalence check: compiling the original `HEAD` file and the new entrypoint through Sass with the Vite `@/` alias resolved produced identical CSS (`27374` bytes each).
- `git diff --check` on the touched style files passed.
- ArtDeco token checker passed on the entrypoint and partials, including literal checks.
- Focused Vitest passed: `src/components/artdeco/base/__tests__/ArtDecoButton.spec.ts` (`4/4` tests).
- The consumer import path remains unchanged: `<style scoped lang="scss" src="./styles/ArtDecoButton.scss"></style>`.
- No cleanup or deletion was performed beyond replacing the original file body with partial `@use` statements.

