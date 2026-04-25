# Report Templates

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

Use these templates for every audit run.

## Per-Page Report

```md
# Page Audit Report: [route]

## Purpose
[What this page is for]

## Agent Findings

### route-inventory
- [finding]

### functional-audit
- [finding]

### data-state-audit
- [finding]

### visual-artdeco-audit
- [finding]

### responsive-a11y-audit
- [finding]

## Issue Summary
- Blocking: [n]
- High: [n]
- Medium: [n]
- Low: [n]

## Consolidated Issues
- [severity] [issue]
- Source roles:
- Why consolidated:
- Reproduction or trigger:
- Expected:
- Actual:

## Shared Impact
- Shared component or layout involved:
- Impact basis:
- Potentially affected related pages:
- Follow-up check needed:
- Decision timing: pre-repair
- Staged-scope follow-up needed:

## Repair Plan
- [what the main skill chose to fix now]
- [what was deferred and why]

## Fixes Applied
- [file or component] [what changed]
- [file or component] [what changed]

## Verification
- Verification policy:
- Browser project or runtime reuse:
- Verified at:
- Checked routes:
- Checked states:
- Checked breakpoints:
- Validation notes:

## Residual Risks
- [severity] [risk]
- Reason:
- Next action:
```

## Batch Report

```md
# Batch Audit Report: [batch-id]

## Scope
- Module:
- Pages:
- Batch rationale:

## Agent Summary

### route-inventory
- [batch scope or canonical-entry finding]

### functional-audit
- [batch-level functional finding]

### data-state-audit
- [batch-level data/state finding]

### visual-artdeco-audit
- [batch-level visual finding]

### responsive-a11y-audit
- [batch-level responsive or accessibility finding]

## Consolidated Issue Statistics
- Blocking: [n]
- High: [n]
- Medium: [n]
- Low: [n]

## Pattern Findings
- Repeated issue pattern:
- Occurrence basis:
- Shared component or token involved:
- Suggested follow-up scope:

## Main Skill Decisions
- duplicates merged:
- priority order applied:
- fixes applied:
- deferred items:

## Fix Summary
- [fix area]
- [fix area]

## Unresolved Items
- [item]

## Reasons Not Fixed
- [dependency / out of scope / needs clarification]

## Verification Summary
- Verification policy:
- Browser project or runtime reuse:
- Regression checks completed:
- Shared patterns verified:
- Risk notes:

## Next Batch Plan
- [next target]
```

## Naming Rules

Use these naming patterns:

- page report: `[module]-[route-key]-audit.md`
- batch report: `[module]-batch-[nn]-audit.md`

The batch report naming must match the `batch-id` rule in `references/batching-rules.md`.

## Archive Suggestion

Unless the user requests another location, store audit outputs under a project report path consistent with existing repository reporting conventions, and keep page reports grouped under the current batch identifier.

## Output Rules

- Order issues by severity first.
- Keep findings concrete and reproducible.
- Distinguish clearly between fixed items and deferred items.
- Preserve the distinction between audit-role findings and main-skill decisions.
- Do not claim verification that was not actually performed.
- Keep the report scoped to the audited batch.
- If a fix touches a shared component, record the related page impact explicitly.
- If verification is partial, state the missing verification surface.
- Batch summaries should include at least one repeated pattern when the same issue class appears in 2 or more pages, or when the same shared component/token causes the issue across the batch.
- `Impact basis` in `Shared Impact` should state why cross-page impact is suspected:
  - shared component change
  - layout change
  - global style or token change
  - shared composable or state bridge change
