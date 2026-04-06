# Troubleshooting Artifacts

## Status

This directory is a retained troubleshooting-artifact slice.

It currently contains diagnosis or failure-analysis writeups for specific incidents.

It is not a current runtime status board by itself.

## Single Source of Truth

Use the narrowest canonical source that matches the question:

- shared governance and migration rules:
  - `architecture/STANDARDS.md`
- current implementation and environment truth:
  - current code, current environment, and fresh verification output
- current adopted remediation state:
  - repository-root `TASK.md`
  - repository-root `TASK-REPORT.md`
  - the active task or governance record that cites the troubleshooting artifact

Files in `reports/troubleshooting/` are retained diagnosis materials. They do not automatically define today's root cause, runtime state, or remediation status.

## Reading Rules

### 1. Troubleshooting reports are historical analyses unless refreshed

Observed file:

- `white_screen_diagnostic_report.md`

This file is a point-in-time diagnosis artifact. Its hypotheses, root-cause reasoning, and recommendations must be read as historical unless they have been freshly re-verified.

### 2. Hypotheses are not standing facts

- A root-cause hypothesis in a troubleshooting report may have been reasonable for that incident.
- It does not automatically become current repo truth for later incidents or later environments.

If current root cause matters, re-run diagnosis on current code and current environment.

### 3. Do not turn troubleshooting into a live operations board

- Do not mirror current runtime state here with new summary wrappers.
- Do not treat one historical troubleshooting report as the current operational truth for the same symptom.
- If a troubleshooting artifact still drives work, adoption should be recorded in the current task or governance record.

## Current Artifact Classes

Examples observed on `2026-04-06`:

- incident-specific troubleshooting report:
  - `white_screen_diagnostic_report.md`

This list is illustrative, not an exhaustive registry contract.

## Deletion Guard

No file in this directory is deletion-safe by default.

Before deleting or relocating any member, complete both:

- code-path verdict:
  - confirm it is not referenced by current docs, tasks, handover materials, or incident follow-up workflows
- function-tree verdict:
  - classify it as `historical troubleshooting report`, `adopted troubleshooting input`, `duplicate redundant`, or `pending classification`

Absence of recent edits is not enough to delete a troubleshooting artifact.

## Temporary / Compatibility Guard

- Do not use this directory as a parking lot for temporary runtime notes, shims, or unmanaged backup files.
- If a troubleshooting artifact still needs to remain because a migration or remediation is incomplete, the owning current task should define the canonical source and exit condition outside this directory.

## Non-Goals

This README does not:

- certify current runtime health
- replace fresh troubleshooting on current code
- create a live incident tracker
- authorize deletion or merging of existing artifacts
