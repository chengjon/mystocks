# Q2 Wave 4 Batch Plan: Function Tree Evidence Hardening

Date: 2026-04-26
Mode: single-CLI execution planning
Related change: `openspec/changes/plan-q2-optimization-closure-program/`
Primary inputs:
- `docs/reports/quality/Q2_PHASE_E_FUNCTION_TREE_EVIDENCE_HARDENING_2026-04-25.md`
- `docs/reports/quality/Q2_CORE_CLOSURE_EXECUTION_SEQUENCE_2026-04-25.md`
- `openspec/changes/plan-q2-optimization-closure-program/specs/function-tree-governance/spec.md`
- `openspec/changes/plan-q2-optimization-closure-program/specs/code-quality/spec.md`

## Objective

Wave 4 is the evidence-hardening wave for function-tree governance. Its job is not to rebuild the catalog system. Its job is to ensure that function-tree statuses, completion percentages, and completion wording are backed by declared evidence classes rather than narrative confidence.

## Scope

### In scope
- criteria-backed status semantics for function-tree states
- evidence-layer model for implementation, verification, runtime, and safety or governance
- safety-sensitive downgrade and completion rules
- closure-wave evidence linkage to function-tree status updates
- explicit treatment of completion percentages as evidence-backed or snapshot-only

### Out of scope
- broad redesign of catalog structure
- unrelated domain decomposition changes
- new product roadmap creation
- implementation of runtime controls outside the already planned Waves 1 to 3
- speculative re-scoring of every historical domain without evidence review

## Current Truth To Preserve

- `governance/function-tree/catalog.yaml` and `schema.json` are already the structural truth for stable IDs and scope mapping
- the current gap is evidence-backed completion semantics, not identifier governance
- Q2 Phases A to D already produced the first usable closure-wave evidence set
- safety-sensitive nodes must not be allowed to imply production-grade readiness without matching safety proof

## Recommended Batch Sequence

### Batch 1: Status Semantics And Evidence Layer Lock

Goal:
- make every function-tree status interpretable through one declared evidence model

Expected edits:
- function-tree legend and guidance
- governance notes for status meanings
- evidence-layer definition for implementation, verification, runtime, and safety or governance

Success criteria:
- each completion state has declared meaning
- `✅ 完成` is no longer interpreted as a narrative default without evidence support

Verification:
- docs and governance text use one status model
- evidence layers are stated where completion semantics are described

### Batch 2: Safety-Sensitive Rule And Downgrade Logic

Goal:
- stop safety-sensitive nodes from being overstated

Expected edits:
- safety-sensitive classification rule
- downgrade or block rules for completion wording
- guidance for trading, risk, and execution-related nodes

Success criteria:
- capabilities involving funds movement, position change, or pre-execution risk decisions are treated as safety-sensitive
- safety-sensitive nodes cannot claim `✅ 完成` without the required safety or governance evidence

Verification:
- function-tree guidance explicitly ties safety-sensitive status to Phase D style control evidence
- no guidance implies that UI or modeled logic alone is enough for production-grade completion claims

### Batch 3: Closure-Wave Evidence Binding

Goal:
- connect Waves 1 to 3 evidence outputs to function-tree updates

Expected edits:
- closure-wave evidence references
- guidance for what artifacts must be cited during status upgrades
- review checklist for status changes

Success criteria:
- status upgrades identify canonical truth source, executed validations, runtime evidence, and unresolved gaps
- Q2 A-D audit outputs are recognized as admissible evidence inputs for relevant domains

Verification:
- function-tree update guidance and closure-wave evidence contract are mutually consistent
- reviewers can reject narrative-only status upgrades

### Batch 4: Percentage Interpretation And Snapshot Policy

Goal:
- prevent percentages from being mistaken for audited hard metrics

Expected edits:
- percentage interpretation notes
- snapshot labeling guidance
- distinction between auditable metric and managerial snapshot

Success criteria:
- completion percentages are explicitly classified as evidence-backed metrics or informative snapshots
- percentages without declared calculation rules are not presented as hard readiness proof

Verification:
- function-tree docs distinguish snapshot values from evidence-backed status claims
- no percentage language implies stronger certainty than its declared evidence model supports

### Batch 5: Residual Historical Review Capture

Goal:
- record where evidence backfill is still needed

Expected outputs:
- explicit follow-up list for:
  - historical node evidence review
  - selective status downgrades where evidence is incomplete
  - future evidence automation or checklist support

Success criteria:
- the repo does not pretend all historical percentages and statuses are already fully audited
- remaining review debt is visible as follow-up

## Suggested Commit Cadence

Recommended micro-batch rhythm:

1. status semantics and evidence layer lock
2. safety-sensitive rule and downgrade logic
3. closure-wave evidence binding
4. percentage interpretation and snapshot policy
5. residual historical review capture

Practical commit count:
- minimum: 3 commits
- likely: 4 to 6 commits

## Validation Standard For Wave 4

Wave 4 should claim evidence-hardening closure only when:

1. function-tree statuses map to declared evidence layers
2. safety-sensitive nodes have explicit stricter completion rules
3. closure-wave evidence artifacts are required for status upgrades
4. completion percentages are distinguished between evidence-backed metrics and informative snapshots
5. historical review debt remains visible where evidence has not yet been backfilled

## Risks During Execution

### 1. Cosmetic-only risk
If Wave 4 only changes legend wording without binding status updates to evidence artifacts, the underlying governance gap remains.

### 2. Over-audit risk
Trying to fully re-audit every historical node in the same wave would stall the closure program. This wave should define the rules first and capture remaining review debt explicitly.

### 3. False downgrade risk
Statuses should become more defensible, not arbitrarily pessimistic. Downgrades should follow missing evidence, not stylistic preference.

## Recommended Next Action After Planning

If implementation starts, begin with Batch 1 and Batch 2. Do not mix Wave 4 evidence-hardening with new cross-cutting runtime refactors outside the closure sequence.
