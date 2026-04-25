# frontend-audit-orchestration Specification

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。

## ADDED Requirements

### Requirement: Page-Audit Batch Manifest
The page-audit workflow SHALL treat each audit batch as a first-class state object with a resumable manifest that records scope, status, validation progress, and shared-impact context.

#### Scenario: Batch manifest is created
- **WHEN** a page-audit batch starts
- **THEN** it SHALL record a stable audit-run id, batch id, requested route set, and canonical page entries
- **AND** it SHALL record current environment assumptions, verification policy, and audit-role participation
- **AND** it SHALL track completed pages, pending pages, fixed files, validation status, staged scope, and artifact outputs

#### Scenario: Batch is resumed or handed off
- **WHEN** an audit batch is resumed across sessions or handed off between agents
- **THEN** the manifest SHALL provide enough state to distinguish completed work, deferred work, blocked work, and closeout prerequisites
- **AND** the workflow SHALL NOT rely only on the main agent's transient conversation memory

### Requirement: Structured Role Outputs
The page-audit workflow SHALL normalize role findings into a shared structured schema for the four finding-producing audit roles and a compatible structured scope model for `route-inventory`.

#### Scenario: Finding-producing role emits an issue
- **WHEN** `functional-audit`, `data-state-audit`, `visual-artdeco-audit`, or `responsive-a11y-audit` reports an issue
- **THEN** the issue SHALL include role, route, canonical entry, severity, finding summary, evidence, fixability, shared-impact candidacy, and dedupe identity
- **AND** the issue SHALL be suitable for merge, deduplication, and severity ordering without requiring free-text reinterpretation

#### Scenario: Route inventory emits scope data
- **WHEN** `route-inventory` completes the current batch scope pass
- **THEN** it SHALL emit structured scope data for canonical pages, detail pages, and compatibility redirect or alias routes
- **AND** that output SHALL remain distinguishable from finding-producing role outputs while still being mergeable by the orchestrator

### Requirement: Orchestrator And Sub-Agent Boundaries
The page-audit workflow SHALL distinguish read-only audit work from closeout orchestration and SHALL keep staged-scope, git, and verification closure responsibilities in the main orchestrator.

#### Scenario: Audit roles participate in a batch
- **WHEN** sub-agents are used for route or page auditing
- **THEN** they SHALL collect findings, evidence, and repair suggestions only within their assigned audit role
- **AND** they SHALL NOT own staged git changes, final verification closure, or repository-wide closeout decisions

#### Scenario: Main orchestrator closes the batch
- **WHEN** findings are merged and repair work is approved
- **THEN** the main orchestrator SHALL decide shared impact, edit files, run validations, manage staged scope, and record closeout evidence
- **AND** it SHALL NOT delegate those responsibilities to sub-agents implicitly

### Requirement: Environment Fallback Branches
The page-audit workflow SHALL define explicit fallback behavior for common environment failures so batch execution can degrade honestly instead of stalling silently.

#### Scenario: Browser or Playwright environment is unavailable
- **WHEN** Playwright permissions, browser artifact paths, or browser tooling availability block live audit
- **THEN** the batch SHALL downgrade to a declared fallback such as `code-review-only` or alternative browser tooling
- **AND** verification output SHALL mark the downgraded surface explicitly

#### Scenario: Runtime or agent environment is constrained
- **WHEN** PM2 or frontend port conflicts, dirty worktree staged-scope switching, or agent-capacity exhaustion prevents the preferred execution mode
- **THEN** the workflow SHALL record the constraint and follow a declared fallback branch
- **AND** it SHALL preserve honest closeout status rather than implying full verification

### Requirement: Compatibility Redirect Audit Model
The page-audit workflow SHALL model compatibility redirects and alias routes as a first-class audit object separate from canonical pages.

#### Scenario: Compatibility redirect is included in a batch
- **WHEN** a route such as a legacy alias or auth-sensitive redirect is part of the requested audit scope
- **THEN** the audit SHALL classify it as a compatibility redirect or alias route rather than a canonical page
- **AND** it SHALL record the canonical target, query preservation, hash preservation, auth-guard interaction, and post-login destination behavior

### Requirement: Verification Policy Declaration
The page-audit workflow SHALL declare verification policy parameters per batch instead of treating live verification strategy as implicit convention.

#### Scenario: Batch uses constrained verification
- **WHEN** a batch runs with Chromium-only validation, external frontend reuse, or code-review-only fallback
- **THEN** the manifest and closeout evidence SHALL state that policy explicitly
- **AND** reports SHALL distinguish that policy from full cross-browser or freshly started frontend verification

### Requirement: Closeout Evidence Model
The page-audit workflow SHALL use a standardized closeout checklist that records audit completion, fix accounting, runtime verification, staged git scope, and residual risk.

#### Scenario: Audit scope is declared complete
- **WHEN** the requested page-audit scope is closed out
- **THEN** the closeout record SHALL include syntax and type-check status, PM2 or runtime service status, executed Chromium or targeted verification, and staged GitNexus scope detection
- **AND** it SHALL distinguish complete, partial, deferred, and blocked outcomes truthfully
