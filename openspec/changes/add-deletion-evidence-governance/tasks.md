## 1. Shared Deletion Evidence Engine

- [x] 1.1 Add `scripts/compliance/deletion_evidence_gate.py` with staged/worktree scope support
- [x] 1.2 Detect top-level tracked directory deletion from `HEAD` plus deleted tracked files
- [x] 1.3 Detect document batch deletion only when three or more documents are deleted outside already-deleted directories
- [x] 1.4 Load deletion evidence only from `HEAD` `governance/deletion-evidence.yaml`
- [x] 1.5 Load emergency waivers only from `HEAD` `governance/waivers/deletion-evidence-waivers.yaml`
- [x] 1.6 Enforce exact-path matching, fixed schema, approved status, safe deletion verdicts, and waiver expiry

## 2. Hook Integration

- [x] 2.1 Register `deletion-evidence-gate` in `.pre-commit-config.yaml`
- [x] 2.2 Delegate `.githooks/pre-commit` to the staged deletion evidence gate with explicit skip toggles
- [x] 2.3 Add `.claude/hooks/stop-deletion-evidence-gate.sh`
- [x] 2.4 Register the Stop hook in `.claude/settings.json`

## 3. Governance Registry Bootstrap

- [x] 3.1 Add empty canonical evidence registry at `governance/deletion-evidence.yaml`
- [x] 3.2 Add empty canonical waiver registry at `governance/waivers/deletion-evidence-waivers.yaml`
- [x] 3.3 Ensure the gate rejects in-commit evidence and in-commit waiver changes by resolving both registries from `HEAD`

## 4. Verification

- [x] 4.1 Add unit tests for directory deletion, document batch deletion, exact evidence matching, in-commit evidence rejection, and waiver expiry
- [x] 4.2 Add integration tests for `.pre-commit-config.yaml`, `.githooks/pre-commit`, and `.claude/settings.json`
- [x] 4.3 Add Stop hook tests for blocking and pass-through behavior
- [x] 4.4 Run `openspec validate add-deletion-evidence-governance --strict`
