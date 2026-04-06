# Type-Check Artifacts

## Status

This directory is a retained type-check artifact slice.

It currently contains historical type-check output snapshots from specific rounds.

It is not a directory-wide proof of current type-check health.

## Single Source of Truth

Use the narrowest canonical source that matches the typing question:

- shared governance and metric wording rules:
  - `architecture/STANDARDS.md`
- debt-governance execution rules and current baseline policy:
  - `docs/standards/technical-debt-governance-charter-v1.md`
- current frontend type baseline:
  - `reports/analysis/tech-debt-baseline.json`
- current type-check truth:
  - the fresh type-check command output and the exact artifact from that run

Do not cite `reports/type_check/` generically as if the whole directory were one current typing verdict.

## Reading Rules

### 1. Round files are point-in-time snapshots

Observed files include:

- `type_check_round_3.txt`
- `type_check_round_6.txt`
- `type_check_round_7.txt`

These files are retained outputs from specific rounds. Their errors and counts must be read as dated snapshots, not as current repo truth.

### 2. Historical type errors do not prove current type state

- A historical error in one round file does not prove the same error still exists today.
- Differences between rounds do not, by themselves, establish the current baseline unless a current task explicitly adopts that comparison.

If current type-check status matters, rerun the relevant command on current code and cite that specific run.

### 3. Do not build a second type-debt dashboard here

- Do not add hand-written “current type-check status” summaries here unless an active task explicitly establishes one as canonical.
- Do not mirror current baseline or current debt counts here when that truth already lives in current governance artifacts and fresh command output.
- If a historical round file still matters, adoption should be recorded in the current task or governance record.

## Current Artifact Classes

Examples observed on `2026-04-06`:

- round-based type-check snapshots:
  - `type_check_round_3.txt`
  - `type_check_round_6.txt`
  - `type_check_round_7.txt`

This list is illustrative, not an exhaustive registry contract.

## Deletion Guard

No file in this directory is deletion-safe by default.

Before deleting or relocating any member, complete both:

- code-path verdict:
  - confirm it is not referenced by current docs, tasks, baselines, audits, or follow-up work
- function-tree verdict:
  - classify it as `historical type-check snapshot`, `adopted type evidence`, `duplicate redundant`, or `pending classification`

Absence of recent edits is not enough to delete a type-check artifact.

## Temporary Artifact Guard

- Do not normalize ad hoc rerun outputs into a permanent parallel history layer without an owning task.
- If a specific round output must stay for governance reasons, document why it stays and what would allow later retirement.

## Non-Goals

This README does not:

- certify current type-check health
- replace fresh type-check execution
- create a live type-debt board
- authorize deletion or merging of existing artifacts
