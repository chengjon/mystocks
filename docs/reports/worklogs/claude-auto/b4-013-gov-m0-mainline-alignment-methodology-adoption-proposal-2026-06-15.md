# B4.013-GOV-M0 Mainline Alignment Methodology Adoption Proposal

Date: 2026-06-15

## Scope

Authorized work:

- Create OpenSpec proposal artifacts for adopting the project mainline alignment methodology.
- Create spec deltas that translate the methodology into repository governance requirements.
- Create this worklog.
- Run OpenSpec strict validation.

Explicitly excluded:

- No edits to `architecture/STANDARDS.md`.
- No edits to `AGENTS.md` or `CLAUDE.md`.
- No edits to FUNCTION_TREE or `.governance`.
- No source, runtime, test, or configuration changes.

## Inputs

- External methodology: `项目主线对齐标准化开发方法论.md`.
- User-added fallback rules:
  - Visible result axiom: development outcomes must be visible and reproducible.
  - No premature future-feature repair: inactive future code must not consume mainline capacity.
  - Rolling cycle rule: unresolved blockers from each five-day mainline cycle feed the next cycle.
- Architecture framing from Matt Pocock skills:
  - Treat mainline alignment as a deep governance Module.
  - Keep a small Interface: task classification, visible result evidence, active mainline node, blocker rollover.
  - Put implementation details behind that governance Interface through OpenSpec, FUNCTION_TREE, worklogs, and gates.

## Artifacts Created

- `openspec/changes/adopt-mainline-alignment-governance/proposal.md`
- `openspec/changes/adopt-mainline-alignment-governance/tasks.md`
- `openspec/changes/adopt-mainline-alignment-governance/specs/architecture-governance/spec.md`
- `openspec/changes/adopt-mainline-alignment-governance/specs/function-tree-governance/spec.md`

## Governance Semantics Captured

- P0/P2/P3 task admission is mandatory before implementation.
- Runtime usability and visible results outrank file-level cleanup.
- Code diff, documents, worklogs, and green gates alone are not completion.
- Future inactive feature repair is prohibited unless separately authorized with its own visible-result acceptance target.
- Five-day cycles roll unresolved blockers into the next runtime mainline iteration.
- FUNCTION_TREE must maintain one active mainline node and require visible runtime evidence for closeout.

## Validation

Passed:

- `openspec validate adopt-mainline-alignment-governance --strict`
- Result: `Change 'adopt-mainline-alignment-governance' is valid`

## Result

B4.013-GOV-M0 proposal artifacts prepared and validated as a no-source governance proposal package.
