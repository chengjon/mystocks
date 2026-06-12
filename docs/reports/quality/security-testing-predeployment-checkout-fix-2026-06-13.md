# Security Testing Pre-Deployment Checkout Fix

Date: 2026-06-13

## Scope

This report records G2.334, a MyStocks-only CI gate fix for `.github/workflows/security-testing.yml`.

The change adds `actions/checkout@v4` to the `pre-deployment-security` job before it downloads security artifacts and runs the final inline verification script.

## Trigger

PR #480 exposed a Security Testing Pipeline failure in the `Pre-Deployment Security Verification` job.

The failing step attempted to read `src/core/config_loader.py` without first checking out the repository in that job:

- workflow: `.github/workflows/security-testing.yml`
- job: `pre-deployment-security`
- failing step: `Final security verification`
- observed failure: `FileNotFoundError: [Errno 2] No such file or directory: 'src/core/config_loader.py'`

The file exists on both the PR head and `origin/main`; the missing file was a job workspace wiring issue.

## Decision

Add a checkout step to the pre-deployment job:

1. `Checkout code`
2. `Download final security reports`
3. `Final security verification`

This preserves the existing security checks and thresholds. It only restores repository availability before the existing script reads source files.

## Boundary

No MyStocks application source, tests, dependency manifests, OpenSpec implementation files, runtime files, or OpenStock repository files are changed.

This task is intentionally separate from G2.332 so the technical-analysis provider injection PR remains limited to its approved source/test/governance scope.

## Validation Plan

- Assert the pre-deployment job checks out the repository before artifact download and final verification.
- Run the mainline scope gate against `governance/mainline/task-cards/g2-334.yaml`.
- Run `git diff --check`.
- Run GitNexus change detection before commit.
- Use GitHub PR checks as the final CI evidence after opening the G2.334 pull request.

## Rollback

Revert the G2.334 commit. That removes the checkout step and returns the workflow to its previous shape.
