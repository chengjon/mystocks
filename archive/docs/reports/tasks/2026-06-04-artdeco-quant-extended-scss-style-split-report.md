# ArtDeco Quant Extended SCSS Style Split Report

Date: 2026-06-04

## Scope

- Target: `web/frontend/src/styles/artdeco-quant-extended.scss`
- Consumers verified before split:
  - `web/frontend/src/components/artdeco/specialized/ArtDecoLongHuBang.vue`
  - `web/frontend/src/components/artdeco/specialized/ArtDecoBlockTrading.vue`
- Change type: style-structure-only refactor.
- Behavior scope: no Vue template/script changes, no route changes, no API changes, no selector/value edits.

## Split Result

The original 447-line stylesheet now remains as a stable import entrypoint:

- `artdeco-quant-extended.foundations.scss`: font import, typography tokens, quant color tokens, dense spacing, quant layout variables.
- `artdeco-quant-extended.utilities.scss`: animation keyframes, realtime flash utilities, semantic color utilities, signal and indicator helpers.
- `artdeco-quant-extended.components.scss`: compact stat cards, DOM panel, and indicator panel styles.
- `artdeco-quant-extended.responsive-a11y.scss`: responsive rules, screen-reader utility, high-contrast support, and print handling.

## Verification Notes

- Mechanical equivalence check: concatenating the four partials matches the original `HEAD` content after trailing-whitespace normalization.
- `git diff --check` on the touched files passed.
- Sass smoke compile for `src/styles/artdeco-quant-extended.scss` passed.
- ArtDeco token checker with `--skip-literal-checks` passed on the entrypoint and partials.
- Full literal token checker still reports 56 hardcoded literal findings; the same 56 findings are present in the original `HEAD` file, so this split does not add new literal token debt.
- The entrypoint path remains unchanged, so existing component imports continue to target `@/styles/artdeco-quant-extended`.
- No cleanup or deletion was performed beyond replacing the original file body with partial imports.
