# Quant Validation Artifacts

## Status

This directory is a retained quant-validation artifact slice.

It currently contains machine-readable results from specific validation runs.

It is not a directory-wide proof of current quant-engine health, current strategy quality, or current regression status.

## Single Source of Truth

Use the narrowest canonical source that matches the quant-validation question:

- shared governance and metric wording rules:
  - `architecture/STANDARDS.md`
- current implementation truth:
  - current code, current strategy logic, and fresh validation output
- current adopted quant evidence:
  - the exact validation artifact cited by the active task, report, or governance record

Do not cite `reports/quant/` generically as if the whole directory were one current quant verdict.

## Reading Rules

### 1. Validation result files are point-in-time outputs

Observed files include:

- `quant_strategy_validation_results.json`

These files are retained outputs from a specific validation run. Their pass or fail state must be read as dated evidence, not as the current repo truth.

### 2. Historical pass or fail state does not prove current status

- A failed historical validation does not prove the same regression still exists today.
- A passed historical validation does not prove the current code still passes the same checks.

If current quant-validation status matters, rerun the relevant validation on current code and cite that exact run.

### 3. Do not create a second live quant gate here

- Do not add hand-written "current quant validation status" summaries here unless an active task explicitly establishes one as canonical.
- Do not mirror live release-gate or regression-gate status here when that truth already belongs to fresh verification output and the owning task.
- If a retained validation artifact still matters, its adoption should be recorded in the active task or governance record.

## Current Artifact Classes

Examples observed on `2026-04-06`:

- machine-readable quant validation output:
  - `quant_strategy_validation_results.json`

This list is illustrative, not an exhaustive registry contract.

## Deletion Guard

No file in this directory is deletion-safe by default.

Before deleting or relocating any member, complete both:

- code-path verdict:
  - confirm it is not referenced by current docs, tasks, governance reports, validation workflows, or follow-up analysis
- function-tree verdict:
  - classify it as `historical quant validation result`, `adopted validation evidence`, `duplicate redundant`, or `pending classification`

Absence of recent edits is not enough to delete a quant-validation artifact.

## Temporary Artifact Guard

- Do not normalize ad hoc validation reruns into a permanent parallel results layer without an owning task.
- If a specific validation artifact must remain tracked for governance reasons, document why it stays and what would allow later retirement.

## Non-Goals

This README does not:

- certify current quant-engine health
- replace fresh quant validation
- define a live repo-wide quant dashboard
- authorize deletion or merging of existing artifacts
