# Change: Add deletion evidence governance

## Why

The repository already carries deletion and migration governance rules in `architecture/STANDARDS.md`,
but those rules still depend on human discipline. Directory deletions and multi-document cleanup batches
can still slip through local workflows without a machine-enforced brake.

This change introduces a strong, shared deletion gate that blocks:

- tracked directory deletion
- batches deleting three or more documents

The gate only accepts pre-existing, machine-readable governance evidence and exact-path emergency
waivers. This prevents "delete first, justify in the same commit later" behavior.

## What Changes

- Add a shared `deletion_evidence_gate` compliance engine for staged and worktree scopes.
- Add a canonical machine-readable evidence registry at `governance/deletion-evidence.yaml`.
- Add a canonical emergency waiver registry at `governance/waivers/deletion-evidence-waivers.yaml`.
- Wire the gate into local commit-time automation through `.pre-commit-config.yaml` and `.githooks/pre-commit`.
- Wire the gate into Claude Stop hooks through a dedicated wrapper script and `.claude/settings.json`.
- Enforce exact-path matching only: no wildcards, no fuzzy parent-scope approvals, no in-commit evidence.

## Impact

- Affected specs: `directory-governance`
- Affected code:
  - `scripts/compliance/deletion_evidence_gate.py`
  - `.pre-commit-config.yaml`
  - `.githooks/pre-commit`
  - `.claude/settings.json`
  - `.claude/hooks/stop-deletion-evidence-gate.sh`
  - `governance/deletion-evidence.yaml`
  - `governance/waivers/deletion-evidence-waivers.yaml`
