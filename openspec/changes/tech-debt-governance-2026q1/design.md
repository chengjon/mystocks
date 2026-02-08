## Context
The project has multiple technical debt reports but lacks a consistent governance loop. This design introduces a minimal, repeatable artifact set.

## Goals / Non-Goals
- Goals:
  - Single source of truth for architecture references.
  - Visible, owned backlog of debt items.
  - Weekly execution cadence with measurable evidence.
- Non-Goals:
  - Refactoring implementation code.
  - Changing runtime architecture in this change.

## Decisions
- Use OpenSpec deltas for governance requirements.
- Maintain debt artifacts under `technical_debt/governance/`.
- Track execution via root-level `TASK*.md` files.

## Risks / Trade-offs
- Risk: Governance artifacts become stale.
  - Mitigation: Weekly rollup and explicit owners/DDL fields.

## Migration Plan
1. Create baseline documents and indexes.
2. Assign owners and DDLs.
3. Start weekly reporting cadence.

## Open Questions
- Which team owns final approval of SoT updates?
