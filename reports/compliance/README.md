# Compliance Artifacts

## Status

This directory is a retained compliance-artifact slice.

It currently contains a combination of:

- principle or release notes for governance rules
- execution or completion-style reports
- exception registries
- directory or repository scan artifacts

It is not the directory that owns the canonical rule text for the whole repo.

## Single Source of Truth

Use the narrowest canonical source that matches the question:

- shared governance and migration rules:
  - `architecture/STANDARDS.md`
- debt-governance execution rules, gates, baselines, and exception process:
  - `docs/standards/technical-debt-governance-charter-v1.md`
- active proposal or change truth:
  - the relevant change under `openspec/changes/`
- current implementation truth:
  - current code, current contracts, and fresh verification output

Files under `reports/compliance/` may document release notes, compliance evidence, or exception handling, but they do not replace the canonical rule sources above.

## Reading Rules

### 1. Rule release notes are not the master rule body

Observed files in this directory include:

- `large_file_splitting_principles_v1.0_release.md`
- `entrypoint_slimming_benefits.md`

These files may explain or summarize a governance topic, but they must not be treated as the repo-wide master rule text if the same topic is already governed by `architecture/STANDARDS.md` or the charter.

### 2. Compliance reports are historical unless freshly adopted

Observed report-style files include:

- `large_file_splitting_report.md`
- `top5_large_file_splitting_report.md`
- `web_usability_runner_core_splitting_report_20260223.md`

These are evidence or historical closeout artifacts.

They must not be restated as current measured truth without:

- a fresh rerun, or
- an active task that explicitly adopts them as the current cited artifact

### 3. Exception registries require current confirmation before reuse

Observed exception slice:

- `reports/compliance/exceptions/`

Exception files in this directory are retained records, not automatic perpetual approvals.

Before reusing any exception as current truth, confirm:

- owner or approving context is still valid
- exit condition or review cycle has not expired
- referenced files and paths still match current repo state

### 4. Scan artifacts are evidence, not universal deletion authority

Observed scan artifact:

- `full_directory_scan.json`

Scan outputs may help governance review, but they do not by themselves authorize:

- deletion
- relocation
- duplicate-layer removal
- current severity assignment

Deletion still requires both code-path verdict and function-tree verdict.

### 5. Do not spawn a second compliance rulebook here

- Do not duplicate the full governance rule body inside this directory.
- Do not create another “current compliance master index” here if current truth already lives in root governance docs.
- If a compliance artifact needs context, add minimal directory-level guidance or update the active canonical source instead of spawning more summary layers.

## Current Artifact Classes

Examples observed on `2026-04-06`:

- rule or principle release notes:
  - `large_file_splitting_principles_v1.0_release.md`
- compliance or execution reports:
  - `large_file_splitting_report.md`
  - `top5_large_file_splitting_report.md`
  - `web_usability_runner_core_splitting_report_20260223.md`
- exception registries:
  - `exceptions/*.md`
- machine-readable scan output:
  - `full_directory_scan.json`

This list is illustrative, not an exhaustive inventory contract.

## Deletion Guard

No file in this directory is deletion-safe by default.

Before deleting or relocating any member, complete both:

- code-path verdict:
  - confirm it is not referenced by current governance docs, tasks, scripts, audits, or exception workflows
- function-tree verdict:
  - classify it as `active exception record`, `historical compliance report`, `release note`, `scan artifact`, `duplicate redundant`, or `pending classification`

Absence of recent edits is not enough to delete a compliance artifact.

## Temporary / Compatibility Guard

- Do not use this directory as a parking lot for shim notes, `*_new.py` records, temporary entry files, or unmanaged backup copies.
- If a compatibility or migration artifact must be tracked, its canonical source, compatibility surface, verification command, and exit condition still belong in the owning governance record, not only here.

## Non-Goals

This README does not:

- certify current compliance status for the whole repo
- replace canonical rule texts
- grant deletion authority for any member
- serve as a generated index of every compliance artifact
