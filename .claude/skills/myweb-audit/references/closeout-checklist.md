# Closeout Checklist Template

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

Run this checklist before declaring the requested audit scope complete.

```md
# Audit Closeout Checklist: [audit-run-id]

## Scope Closure
- [ ] All requested batches were audited or explicitly deferred.
- [ ] Every audited page has a page report or equivalent inline record.
- [ ] Every batch has a batch report or equivalent inline record.

## Artifact Completeness
- [ ] Each completed batch has a manifest.
- [ ] Findings were normalized before merge and deduplication.
- [ ] Deferred items include severity, reason, and dependency.

## Fix Accounting
- [ ] User approval for repaired findings was recorded.
- [ ] Fixes applied are separated clearly from findings only recorded.
- [ ] Out-of-scope issues are marked as deferred, not silently skipped.
- [ ] Shared-component or token changes record related-page impact.

## Verification Closure
- [ ] Verification surfaces are stated honestly.
- [ ] Verification policy (`full`, `chromium-only`, `code-review-only`) is recorded honestly.
- [ ] Checked routes are listed.
- [ ] Checked states are listed.
- [ ] Checked breakpoints are listed.
- [ ] Partial verification, if any, is explained.
- [ ] Executed browser project or external frontend reuse policy is recorded.

## Runtime And Repo Gates
- [ ] Frontend syntax check result is recorded.
- [ ] Frontend type-check result is recorded.
- [ ] PM2 or equivalent runtime service status is recorded.
- [ ] Chromium E2E or targeted live regression result is recorded.
- [ ] Staged GitNexus scope detection result is recorded.
- [ ] Dirty worktree staging decisions are recorded when closeout depended on staged-scope isolation.

## Rule Compliance
- [ ] Scope stayed within approved frontend repair boundaries.
- [ ] No backend/API redesign was introduced implicitly.
- [ ] Existing route truth and ArtDeco repository truth were respected.
- [ ] No verification result was fabricated.

## Residual Risk Summary
- [ ] Remaining risks are listed with severity.
- [ ] Next actions or dependencies are recorded.

## Final Status
- Status: [complete | partial | deferred | blocked]
- Notes:
```

## Usage Notes

- Use one checklist result per requested audit scope, not per page.
- `partial` is valid when some pages were audited and others were blocked or deferred.
- `blocked` means completion was prevented by route truth, app readiness, or environment issues.
- The runtime gate section should distinguish `not-run`, `passed`, `failed`, and `blocked-by-environment` rather than implying everything was executed.
- If the same issue was reported at different severities by different roles, use the highest severity after consolidation.
