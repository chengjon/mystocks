## ADDED Requirements

### Requirement: ArtDeco Batch Verification Evidence
ArtDeco P0/P1 optimization work SHALL produce batch-level verification evidence instead of generic pass/fail summaries.

#### Scenario: Batch verification execution
- **WHEN** an optimization batch completes implementation
- **THEN** it SHALL run `npm --prefix web/frontend run type-check`
- **AND** it SHALL run the batch's targeted Playwright suites
- **AND** any route or layout touching batch SHALL also run `scripts/run_e2e_pm2.sh`

#### Scenario: Batch verification reporting
- **WHEN** verification results are reported for an optimization batch
- **THEN** the report SHALL include the executed command, browser project, suite names, and pass/fail/skip counts
- **AND** it SHALL identify whether each failure is newly introduced or pre-existing debt

### Requirement: ArtDeco Token Compliance
ArtDeco page optimization SHALL preserve token-based styling as the only allowed source for visual primitives.

#### Scenario: Page style cleanup
- **WHEN** an ArtDeco page or shared ArtDeco component is modified during optimization
- **THEN** colors, spacing, and semantic rise/fall styles SHALL reference `web/frontend/src/styles/artdeco-tokens.scss`
- **AND** newly introduced hardcoded visual values SHALL be treated as quality regressions
