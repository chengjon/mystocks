## Context

> **设计方案说明**:
> 本文件用于记录某项变更的设计思路、结构拆分、实现取舍或技术路径，属于方案设计层材料。
> 它不是共享规则正文，也不直接代表当前仓库已落地状态；落地判断应结合 `architecture/STANDARDS.md`、对应 proposal/tasks、审批结果与实际代码验证。

`System-Config` currently mixes three incompatible realities:

1. The page presents a unified settings surface.
2. The frontend contract only has real backend support for `datasource`.
3. Notification preferences already exist as a user-scoped API and should not be promoted into a fake global system-settings truth.

The approved direction is to treat this as a new workstream rather than reopening the closed frontend-mainline batches.

## Goals / Non-Goals
- Goals:
  - Define a single, explicit page contract for `System-Config`.
  - Keep one canonical owner per section and forbid duplicate storage layers.
  - Preserve mixed scope truth instead of flattening everything into a global settings endpoint.
  - Provide migration completion criteria for removing local-storage degradation.
  - Make section status, scope, and evidence labeling explicit in API metadata.
- Non-Goals:
  - Implement backend/frontend behavior in this proposal batch.
  - Replace the existing notification preferences contract with a system-global clone.
  - Introduce a parallel `*_new.py`, shim service, or backup persistence path as a long-term layer.

## Approaches Considered
- Recommended: Unified page contract with section-routed backend ownership.
  - Keep one page-level shape for the frontend, but each section declares its canonical backend owner and scope.
  - Reuse datasource and notification truths, and add new canonical system-scoped support only where missing.
- Alternative: Single monolithic system-settings backend endpoint for every section.
  - Rejected because it would duplicate notification truth and encourage a second storage layer.
- Alternative: Split the page into separate pages with no page-level contract.
  - Rejected because it removes the intended operator workflow and does not solve current ambiguity about section ownership.

## Decisions
- Decision: Treat `general`, `datasource`, and `security` as system-scoped sections.
  - Why: These settings affect shared runtime behavior rather than per-user preference.
- Decision: Keep `notification` user-scoped.
  - Why: The existing backend contract is per-user, and forcing it into a system-global layer would create duplicate truth.
- Decision: The future contract MUST expose section metadata for `scope`, `owner`, `readStatus`, `writeStatus`, and `evidenceType`.
  - Why: The page already blends real, inferred, and historical information; the contract must prevent those states from being conflated.
- Decision: Migration closeout MUST be section-based.
  - Why: A section may be complete while another remains degraded; exit criteria must not be vague or page-wide by assumption.

## Proposed Architecture
- Frontend keeps a single page-level `SystemSettings` surface.
- The page contract becomes a composition contract, not a storage truth.
- Each section is mapped to one canonical owner:
  - `general` -> new system-scoped backend contract
  - `datasource` -> existing datasource config backend
  - `notification` -> existing user notification preferences backend
  - `security` -> new system-scoped backend contract
- The composition response exposes section metadata so the UI can distinguish:
  - real backend-backed values
  - inferred/derived display values
  - historical baseline values
  - temporarily unavailable sections

## Migration Plan
1. Add the `system-settings-contract` capability delta and approve it.
2. Implement canonical system-scoped support for `general` and `security` without creating duplicate persistence.
3. Compose datasource and notification through explicit section ownership metadata.
4. Update frontend services and page messaging to use section metadata rather than a blanket degraded state.
5. Remove the local-storage fallback only after all retirement criteria are met.

## Retirement / Exit Criteria
- Local-storage persistence for `System-Config` may be removed only when:
  - `general`, `datasource`, and `security` all have canonical backend read/write support.
  - `notification` is wired through the user-scoped canonical contract.
  - no duplicate write path remains in frontend service code.
  - the page-level metadata reports no section as `local-only`.
- Any compatibility layer introduced during rollout MUST be thin and time-bounded, with a named owner and explicit removal task.

## Risks / Trade-offs
- Risk: A page-level composition layer could quietly become a second source of truth.
  - Mitigation: Require per-section owner metadata and forbid composition-layer persistence.
- Risk: Operators may misread inferred or historical values as live runtime truth.
  - Mitigation: Require evidence labels that distinguish `measured`, `inferred`, and `historical-baseline`.
- Risk: Mixed-scope composition complicates authorization and testing.
  - Mitigation: Keep scope explicit per section and verify section flows independently.

## Open Questions
- Should the composition contract be served by a dedicated aggregator endpoint or assembled client-side from section owners, provided canonical ownership remains explicit?
- What exact system-scoped storage model should own `general` and `security` once implementation planning starts?
