## Context

The repository already has strong written governance for deletion:

- code-path judgment is required
- function-tree judgment is required
- compatibility and migration layers must not be removed on static-search intuition alone

What is missing is an automated brake tied to actual deletion actions.

## Goals

- Block tracked directory deletion unless exact, pre-existing machine-readable evidence approves it.
- Block deletion batches removing three or more documents unless exact, pre-existing machine-readable evidence approves each remaining document target.
- Allow emergency waivers through one fixed YAML registry with expiry.
- Reuse one shared engine across Stop hook and pre-commit flows.

## Non-Goals

- Approving deletion through free-form Markdown prose
- Allowing parent-directory or feature-domain fuzzy approvals
- Allowing same-commit evidence or same-commit waiver additions to authorize deletion
- Governing every single-file deletion in this batch

## Decisions

### 1. Use one canonical evidence registry

The gate reads deletion evidence from:

- `HEAD:governance/deletion-evidence.yaml`

This registry is the canonical machine-readable deletion truth source for automation.

### 2. Use one canonical waiver registry

The gate reads emergency waivers from:

- `HEAD:governance/waivers/deletion-evidence-waivers.yaml`

Waivers must be exact-path, explicitly user-approved, and time-bounded.

### 3. HEAD-only resolution prevents in-commit bypass

Both the evidence registry and waiver registry are read from `HEAD`, not from the current staged or
working copy state. That means:

- adding evidence and deleting in one commit does not pass
- adding a waiver and deleting in one commit does not pass

### 4. Directory deletion and document batch deletion are separate triggers

- Directory deletion is derived from tracked files in `HEAD`: when all tracked files under a directory
  are deleted, that directory is considered a deletion target.
- Document deletion only triggers when at least three document files are deleted outside already
  deleted directories.

### 5. Evidence validity is stricter than mere presence

An evidence entry only authorizes deletion when all of the following are true:

- exact `path` match
- exact `kind` match (`directory` or `document`)
- `status: approved`
- `code_path_verdict: safe_to_delete`
- `function_tree_verdict` is `重复冗余` or `正式下线`
- `owner` is present

### 6. Waivers remain exceptional

A waiver only authorizes deletion when all of the following are true:

- exact `path` match
- exact `kind` match
- no wildcard characters in `path`
- `approved_by_user`, `approved_on`, `expires_on`, `owner`, `reason`, and `ticket_or_context` exist
- `expires_on` has not passed

## Risks / Trade-offs

- The first rollout is intentionally strict and will block deletions until the registry is populated.
  This is acceptable because the goal is strong governance, not convenience.
- Existing governance Markdown audits are not directly machine-readable enough for automation. Teams
  must promote approved deletion decisions into the canonical registry first.

## Rollout

1. Add registry files and the shared engine.
2. Wire staged deletion checks into pre-commit and `.githooks/pre-commit`.
3. Wire worktree deletion checks into a dedicated Stop hook.
4. Populate registry entries only in follow-up governance batches as deletions are formally approved.
