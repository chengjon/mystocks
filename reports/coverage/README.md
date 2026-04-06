# Coverage Artifacts

## Status

This directory is a generated coverage-artifact slice.

It currently contains a combination of:

- HTML coverage report assets
- machine-readable coverage outputs
- coverage tool internal state files

It is not a hand-maintained current-truth document by itself.

## Single Source of Truth

Use the narrowest canonical source that matches the coverage question:

- shared governance and metric wording rules:
  - `architecture/STANDARDS.md`
- current task-specific coverage evidence:
  - the exact artifact file cited by the active task or report
- current measured coverage truth:
  - fresh coverage command output and the specific generated artifact from that run

Do not cite `reports/coverage/` generically as if the whole directory were one current coverage baseline.

## Reading Rules

### 1. Generated artifacts must be read by file type

Observed files include:

- `index.html`
- `coverage.json`
- `coverage.xml`
- `status.json`
- many file-level HTML pages

These files have different purposes.

- `coverage.json` and `coverage.xml` are export artifacts for tooling or downstream analysis.
- `index.html` and related HTML files are human-facing generated report assets.
- `status.json` is a coverage.py internal implementation detail, not a stable public interface.

### 2. Current coverage requires fresh run context

Coverage numbers are only meaningful with:

- the command that produced them
- the date or run context
- the exact artifact file being cited

Historical generated files must not be restated as current measured truth without a fresh rerun.

### 3. This directory is mostly generated output

Observed local rule:

- `reports/coverage/.gitignore` contains `*`

This means the directory is primarily treated as generated output. Any tracked exception inside this directory should be deliberate and minimal.

### 4. Do not create a parallel coverage dashboard here

- Do not add hand-written summary files that duplicate CI or current test reports unless an active task explicitly establishes one as the canonical measured output.
- Do not treat the presence of generated HTML as proof that current coverage gates passed for unrelated work.
- If a task needs a coverage conclusion, record it in the owning report and cite the exact generated artifact.

## Current Artifact Classes

Examples observed on `2026-04-06`:

- machine-readable exports:
  - `coverage.json`
  - `coverage.xml`
- generated HTML entrypoints and assets:
  - `index.html`
  - `class_index.html`
  - `function_index.html`
  - file-level `z_*.html`
- internal tool state:
  - `status.json`
- local generated-output guard:
  - `.gitignore`

This list is illustrative, not an exhaustive inventory contract.

## Deletion Guard

Generated does not automatically mean deletion-safe.

Before deleting or relocating any member, complete both:

- code-path verdict:
  - confirm it is not referenced by current docs, CI, artifact publishing, audits, or local verification workflows
- function-tree verdict:
  - classify it as `active generated artifact`, `historical generated artifact`, `tooling state file`, `duplicate redundant`, or `pending classification`

Absence of recent edits is not enough to delete a tracked coverage artifact.

## Temporary / Compatibility Guard

- Do not normalize ad hoc coverage exports into a permanent second reporting layer without an owning task.
- If a specific coverage artifact must remain tracked for governance reasons, its retention reason and replacement or retirement condition should be recorded in the owning report.

## Non-Goals

This README does not:

- certify current repo coverage
- replace fresh coverage execution
- define a repo-wide universal coverage baseline
- authorize deletion or merging of existing artifacts
