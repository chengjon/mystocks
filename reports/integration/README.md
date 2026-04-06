# Integration Test Artifacts

## Status

This directory is a retained integration-test result slice.

It currently contains generated result artifacts, not a hand-maintained current verdict board.

It is not a directory-wide proof that current integration tests pass or fail.

## Single Source of Truth

Use the narrowest canonical source that matches the test question:

- shared governance and metric wording rules:
  - `architecture/STANDARDS.md`
- current test truth:
  - the fresh command output and the exact generated artifact from the current run
- current active remediation or adoption state:
  - the task, report, or governance record that explicitly cites the result artifact

Do not cite `reports/integration/` generically as if the whole directory were one current integration verdict.

## Reading Rules

### 1. Generated result files are point-in-time evidence

Observed file:

- `test-results.xml`

This file is a point-in-time generated result artifact. Its failures, errors, skips, and timestamps must be read as dated evidence for that run, not as a standing truth for the current repo.

### 2. Historical failures do not prove current failure

- Historical collection failures, import errors, or syntax errors in a retained XML file do not prove the same failures still exist today.
- A historical passing result, if one appears later, would also not prove current health without a fresh rerun.

If current integration status matters, rerun the integration suite on current code and cite that specific run.

### 3. Do not spawn a second integration dashboard here

- Do not add hand-written “current integration status” summaries here unless an active task explicitly establishes one as canonical.
- Do not mirror current CI or local test state in parallel markdown files under this directory.
- If a historical result file still matters, its adoption should be recorded in the current task or governance artifact.

## Current Artifact Classes

Examples observed on `2026-04-06`:

- generated integration test result:
  - `test-results.xml`

This list is illustrative, not an exhaustive registry contract.

## Deletion Guard

No file in this directory is deletion-safe by default.

Before deleting or relocating any member, complete both:

- code-path verdict:
  - confirm it is not referenced by current docs, CI, artifact publishing, audits, or follow-up tasks
- function-tree verdict:
  - classify it as `historical test artifact`, `adopted test evidence`, `duplicate redundant`, or `pending classification`

Absence of recent edits is not enough to delete an integration-test artifact.

## Temporary Artifact Guard

- Do not normalize ad hoc rerun outputs into a permanent second history layer without an owning task.
- If a specific retained result file must stay for governance reasons, document why it stays and what would allow later retirement.

## Non-Goals

This README does not:

- certify current integration-test health
- replace fresh integration-test execution
- create a live test-status board
- authorize deletion or merging of existing artifacts
