# Analysis Artifacts

## Status

This directory is a mixed analysis-artifact slice, not a repo-wide current-truth board.

It currently contains a combination of:

- measured baseline files
- historical measured snapshots
- inferred or derived analysis outputs
- historical closeout or phase reports
- generated helper artifacts and retained backup-style files

Do not treat the directory itself as a single canonical status source.

## Single Source of Truth

Use the narrowest canonical source that matches the question:

- shared governance rules:
  - `architecture/STANDARDS.md`
- debt-governance execution rules:
  - `docs/standards/technical-debt-governance-charter-v1.md`
- current technical-debt baseline file:
  - `reports/analysis/tech-debt-baseline.json`
- current product or code truth:
  - current code, current contracts, and fresh verification output

Files in this directory may support analysis, audit, or traceability, but they do not automatically become current truth just because they live under `reports/analysis/`.

## Reading Rules

### 1. Separate measured, baseline, inferred, and historical

When reading any number from this directory, classify it before reuse:

- measured:
  - a value produced by a dated command or captured execution result
- baseline:
  - a frozen comparison point such as `tech-debt-baseline.json`
- inferred:
  - a conclusion, prioritization, or synthesis derived from measured inputs
- historical:
  - any prior snapshot, closeout, weekly report, or generated output that has not been freshly re-verified

Historical files must not be restated as current measured truth without a fresh rerun.

### 2. File names are hints, not proof of currentness

Observed naming in this directory includes:

- `*-baseline*`
- `*-current*`
- `*-weekly*`
- `*-closeout*`
- `*-status*`
- `*-real*`
- `*.backup*`

These names help classify artifacts, but they do not override date, command provenance, or current canonical source.

### 3. Do not spawn duplicate summary layers

- Do not add another directory index that re-summarizes every analysis file.
- Do not create a second "overall current status" markdown file here when an existing canonical source already exists elsewhere.
- If a new artifact needs context, prefer adding that context to the artifact itself or to this directory README, not to a parallel summary file.

## Current Artifact Classes

Examples observed on `2026-04-06`:

- baseline:
  - `tech-debt-baseline.json`
- historical measured or periodic snapshots:
  - `tech-debt-current.json`
  - `tech-debt-current-real-week*.json`
  - `ttl-gate-report*.json`
  - `frontend-mainline-phase-*-status.json`
- historical closeout or matrix-style narrative reports:
  - `frontend-mainline-overall-closeout.md`
  - `frontend-mainline-phase-*-matrix.md`
  - `tech-debt-weekly-report*.md`
- inferred or derived analysis outputs:
  - `frontend_integration_derived.json`
  - `frontend_restructure_dataset_20260302.json`
  - `views_inventory_20260302.json`
- backup or retained tool residue:
  - `CLAUDE.md.backup-20251226-125825`
  - `bug-reports-backup.jsonl`
  - local `package.json`
  - local `package-lock.json`

This list is illustrative, not an exhaustive registry.

## Backup / Temporary Artifact Rule

- Backup-style and generated helper artifacts retained here are not deletion-safe by default.
- Before deleting any member, complete both:
  - code-path verdict:
    - confirm it is not used by scripts, reports, audits, exporters, or documented workflows
  - function-tree verdict:
    - classify it as `active baseline`, `historical snapshot`, `derived analysis`, `retained backup`, `duplicate redundant`, or `pending classification`

Absence of recent edits is not enough to delete a file from this directory.

## Package Metadata Guard

This directory contains local `package.json` and `package-lock.json`.

- They must not be treated as repository-root frontend or workspace package truth.
- If they are kept, they are analysis-local artifacts or retained tool residue.
- Any future cleanup must document why they are safe to remove or why they remain needed.

## Migration / Compatibility Guard

- Do not introduce `*_new.py`, shim notes, temporary entry files, or mechanical split files here as a long-lived pattern.
- If a migration or compatibility artifact must temporarily land in this directory, its owner, reason, verification command, and exit condition must be recorded in governance artifacts.

## Non-Goals

This README does not:

- certify every file here as valid current output
- replace the contents of any specific analysis artifact
- authorize deletion, relocation, or merging of existing files
- act as a generated inventory of all members
