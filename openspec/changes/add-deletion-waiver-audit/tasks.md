## 1. Shared Waiver Audit Engine

- [x] 1.1 Extend `scripts/compliance/deletion_evidence_gate.py` with a dedicated waiver audit mode
- [x] 1.2 Reuse the existing HEAD-only waiver registry loading path for audit mode
- [x] 1.3 Classify valid waivers as `expired`, `expiring_soon`, or `healthy`
- [x] 1.4 Add a default 7-day warning window with explicit CLI override support
- [x] 1.5 Keep expired and soon-expiring findings non-blocking while failing on malformed registry content
- [x] 1.6 Emit stable text and JSON output for automation and human inspection

## 2. Scheduled Alerting Workflow

- [x] 2.1 Add `.github/workflows/deletion-waiver-audit.yml`
- [x] 2.2 Trigger the workflow daily and via `workflow_dispatch`
- [x] 2.3 Invoke the shared compliance engine instead of embedding waiver logic in workflow YAML
- [x] 2.4 Upload the machine-readable audit report as an artifact
- [x] 2.5 Publish GitHub Actions summary output for total, expired, expiring-soon, and healthy counts

## 3. Documentation and Verification

- [x] 3.1 Update `docs/guides/governance/DELETION_EVIDENCE_GATE.md` with a short waiver audit section
- [x] 3.2 Add unit tests for healthy, expiring-soon, expired, override-window, and invalid-registry audit cases
- [x] 3.3 Add workflow registration tests for schedule, `workflow_dispatch`, artifact upload, and summary generation
- [x] 3.4 Run `openspec validate add-deletion-waiver-audit --strict`
