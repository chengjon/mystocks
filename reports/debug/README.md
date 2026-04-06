# Debug Artifacts

## Status

This directory is a retained debug-artifact slice.

It currently contains one-off debug captures and raw inspection outputs.

It is not a current runtime truth board and not a long-lived product telemetry source.

## Single Source of Truth

Use the narrowest canonical source that matches the debugging question:

- shared governance and migration rules:
  - `architecture/STANDARDS.md`
- current system behavior truth:
  - current code, current service state, and fresh reproduction output
- current debugging workflow state:
  - the active task, report, or investigation record that cites the debug artifact

Files in `reports/debug/` are auxiliary captures. They do not automatically describe the current state of the application.

## Reading Rules

### 1. Raw captures are point-in-time evidence

Observed files:

- `cdp_dom_dump.json`
- `cdp_page_html.html`

These are raw browser-debugging or inspection artifacts from a specific debugging moment.

They must be read as point-in-time evidence, not current application truth.

### 2. Raw debug output does not prove current behavior

- A captured DOM tree or HTML snapshot may explain one past failure mode.
- It does not prove the same DOM or runtime state still exists today.

If current behavior matters, capture a fresh artifact from current code and current environment.

### 3. Do not build a second observability layer here

- Do not use this directory as a permanent mirror for current runtime monitoring.
- Do not add hand-maintained “latest debug status” files here.
- If a debug capture needs lasting context, record that context in the owning troubleshooting or governance artifact instead of generating more wrapper files here.

## Current Artifact Classes

Examples observed on `2026-04-06`:

- raw DOM capture:
  - `cdp_dom_dump.json`
- raw HTML capture:
  - `cdp_page_html.html`

This list is illustrative, not an exhaustive inventory contract.

## Deletion Guard

No file in this directory is deletion-safe by default.

Before deleting or relocating any member, complete both:

- code-path verdict:
  - confirm it is not referenced by current reports, tasks, debugging workflows, or forensic needs
- function-tree verdict:
  - classify it as `historical debug capture`, `adopted debug evidence`, `duplicate redundant`, or `pending classification`

Absence of recent edits is not enough to delete a debug artifact.

## Temporary Capture Guard

- Do not normalize ad hoc captures into a permanent parallel evidence layer without an owning task.
- If a future capture must stay, document why it stays and what would allow later retirement.

## Non-Goals

This README does not:

- certify current runtime behavior
- replace fresh debugging on current code
- create a live observability system
- authorize deletion or merging of existing artifacts
