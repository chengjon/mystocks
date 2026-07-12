# Security Artifacts

## Status

This directory is a security-topic container, not a directory-wide live security verdict by itself.

It currently contains topic-specific security artifacts under subdirectories, including:

- `hardcoding/`

Topic directories may contain baselines, weekly reports, or other retained evidence for a specific security governance line.

## Single Source of Truth

Use the narrowest canonical source that matches the security question:

- shared governance and metric wording rules:
  - `architecture/STANDARDS.md`
- current implementation truth:
  - current code, current config, and fresh verification output
- current topic-specific security evidence:
  - the exact file under the relevant topic subdirectory cited by the active task
- current active remediation or governance state:
  - the owning task, plan, or governance record that has adopted the security artifact

Do not treat `reports/security/` as a universal current security baseline for the repo.

## Reading Rules

### 1. Topic subdirectories are scoped, not global

Observed topic:

- `hardcoding/`

Artifacts under a topic directory describe that topic's baseline or historical reporting context. They do not automatically represent the repo's entire current security posture.

### 2. Security baselines are historical unless refreshed

Observed hardcoding artifacts include:

- `baseline-2026-02-15.json`
- `baseline-2026-02-15.md`
- `governance-weekly-20260215.md`

These files are useful evidence, but their numbers and findings must be read as dated artifacts unless freshly rerun or explicitly adopted by a current task.

### 3. Weekly or baseline files do not replace live verification

- A historical baseline does not prove the current issue count.
- A historical weekly report does not prove the current remediation state.
- A topic report may guide follow-up work, but current risk must come from fresh verification on current code.

### 4. Do not spawn a second security control plane here

- Do not mirror current issue tracking, current exception tracking, or current remediation status with ad hoc summary files in this directory.
- Do not promote one topic directory into a parallel repo-wide security dashboard unless an active task explicitly defines it as canonical.
- If a topic artifact needs context, prefer a directory-level README or the owning governance record over repeated per-file wrapper notes.

## Current Artifact Classes

Examples observed on `2026-04-06`:

- topic-scoped baseline artifacts:
  - `hardcoding/baseline-2026-02-15.json`
  - `hardcoding/baseline-2026-02-15.md`
- topic-scoped weekly governance report:
  - `hardcoding/governance-weekly-20260215.md`

This list is illustrative, not an exhaustive topic registry contract.

## Deletion Guard

No file in this directory is deletion-safe by default.

Before deleting or relocating any member, complete both:

- code-path verdict:
  - confirm it is not referenced by current docs, tasks, governance reports, CI, scanners, or audit workflows
- function-tree verdict:
  - classify it as `active topic baseline`, `historical security artifact`, `topic report`, `duplicate redundant`, or `pending classification`

Absence of recent edits is not enough to delete a tracked security artifact.

## Topic Expansion Guard

- If new security topics are added, prefer one subdirectory per topic rather than mixing unrelated security lines together at the root.
- Each new topic should keep its own dated artifacts and should not silently redefine the meaning of existing topic baselines.

## Non-Goals

This README does not:

- certify current repo security posture
- replace fresh security scanning
- define a repo-wide universal security baseline
- authorize deletion or merging of existing artifacts
