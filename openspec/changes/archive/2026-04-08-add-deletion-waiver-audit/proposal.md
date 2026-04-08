# Change: Add deletion waiver audit

## Why

The repository now has a strong deletion evidence gate, but waiver expiry is only evaluated when a
governed deletion is attempted. That leaves expired or soon-to-expire waivers invisible during normal
operation.

This change adds proactive, non-blocking waiver audit and alerting so emergency waivers do not become
silent long-lived debt.

## What Changes

- Extend the shared `deletion_evidence_gate` engine with a waiver audit mode.
- Audit only `HEAD:governance/waivers/deletion-evidence-waivers.yaml` as canonical truth.
- Classify waivers as `expired`, `expiring_soon`, or `healthy`, with a default 7-day warning window.
- Add a dedicated GitHub Actions workflow that runs daily and on `workflow_dispatch`.
- Publish GitHub Actions summary output plus a machine-readable artifact.
- Keep expired and soon-expiring waiver findings non-blocking for ordinary development flow.

## Impact

- Affected specs: `directory-governance`
- Affected code:
  - `scripts/compliance/deletion_evidence_gate.py`
  - `.github/workflows/deletion-waiver-audit.yml`
  - `tests/unit/scripts/test_deletion_evidence_gate.py`
  - `tests/unit/scripts/test_deletion_waiver_audit_workflow.py`
  - `docs/guides/governance/DELETION_EVIDENCE_GATE.md`
