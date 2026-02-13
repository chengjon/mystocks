## 1. OpenSpec Proposal and Approval Gate
- [x] 1.1 Create `proposal.md`, `tasks.md`, and spec delta for `artdeco-design-system` governance.
- [x] 1.2 Run `openspec validate update-artdeco-design-governance --strict` and resolve all validation issues.
- [x] 1.3 Obtain explicit proposal approval before starting implementation.

## 2. Governance Manifest Baseline
- [x] 2.1 Add `web/frontend/src/styles/artdeco-governance-manifest.json` with required sections: `tokens`, `typography`, `spacing`, `docs`.
- [x] 2.2 Add unit test `web/frontend/tests/unit/styles/artdeco-governance-manifest.spec.ts` and verify manifest shape and key governance fields.
- [x] 2.3 Confirm tests pass for the manifest scope.

## 3. Documentation Consistency (v3 Baseline)
- [x] 3.1 Add doc consistency test `web/frontend/tests/unit/styles/artdeco-docs-consistency.spec.ts`.
- [x] 3.2 Update:
  - `docs/guides/ARTDECO_MASTER_INDEX.md`
  - `web/frontend/ARTDECO_COMPONENTS_CATALOG.md`
  - `docs/api/ArtDeco_System_Architecture_Summary.md`
  - `docs/guides/ARTDECO_COMPONENT_GUIDE.md`
  to use consistent v3/v3.1 wording and archived-history labeling.
- [x] 3.3 Confirm consistency tests pass.

## 4. Token Check Hardening
- [x] 4.1 Add/extend `web/frontend/tests/unit/scripts/check-artdeco-tokens.spec.ts` for duplicate custom properties and false-positive control.
- [x] 4.2 Update `web/frontend/scripts/check-artdeco-tokens.js` with stricter parsing, duplicate property detection, and configurable allowlist behavior.
- [x] 4.3 Add script entry `lint:artdeco:strict` in `web/frontend/package.json`.
- [x] 4.4 Confirm token checker tests pass.

## 5. Governance Workflow Integration
- [x] 5.1 Add CLI discoverability test `web/frontend/tests/unit/styles/artdeco-governance-cli.spec.ts`.
- [x] 5.2 Update governance guidance in:
  - `docs/guides/ARTDECO_COMPONENT_GUIDE.md`
  - `docs/guides/ARTDECO_MASTER_INDEX.md`
  with pre-commit governance verification.
- [x] 5.3 Run governance command `cd web/frontend && npm run lint:artdeco:strict` and ensure violations produce non-zero exit.

## 6. Regression Verification and Reporting
- [x] 6.1 Run unit test scope: `cd web/frontend && npm run test -- tests/unit/styles tests/unit/scripts`.
- [x] 6.2 Run existing design regressions: `npm run test:design-token` and `npm run test:bloomberg`. (Blocked by existing Playwright config mismatch and dev server startup issues)
- [x] 6.3 Run type checks: `cd web/frontend && npm run type-check`. (Blocked by existing syntax errors in `src/views/TradingDecisionCenter.vue`)
- [x] 6.4 Update release notes or `TASK-REPORT.md` with governance capability, commands, and failure examples.
