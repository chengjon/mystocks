# OpenSpec Active Frontier (2026-04-10)

> **治理纪要说明**:
> 本文件用于记录 2026-04-10 当前 OpenSpec active change 前沿态势、已完成收口和下一步优先级，不是仓库共享规则正文。
> 共享规则仍以 `architecture/STANDARDS.md` 为准；本文件只用于后续继续清理 active list 时避免回到失效 checklist。

## 1. Closed In This Round

### Archived as completed

- `audit-data-db-runtime`
  - Commit: `a8719aa68`
  - Action: repaired minimal delta, merged into `architecture-governance`, archived successfully
- `implement-api-file-level-testing`
  - Commit: `3694d6df3`
  - Action: realigned to repo-truth closeout, merged into `code-quality`, archived successfully

### Retired as stale residual

- `implement-optimized-testing-strategy`
  - Commit: `fb3d6f83c`
  - Action: removed from active set and replaced with triage record `reports/governance/2026-04-10-openspec-residual-testing-strategy-triage.md`
  - Reason: stale port/runtime assumptions, no current execution ledger, no mainline triage ownership

## 2. Keep Active

### `restructure-frontend-directory`
- Keep active.
- Reason: repo-truth shows phases 0-5 materially closed, but phases 6-9 remain external workflow / merge / deploy / archive gates.
- Constraint: do not continue by replaying the original checklist literally; continue only from current repo-truth frontier and replacement-task logic.

### `implement-optimized-html-vue-artdeco-conversion`
- Keep active.
- Reason: historical governance identified it as the primary frontend visual/design-system execution line.
- Current state: evidence exists, but audit still reports large gaps versus task claims.

### `frontend-optimization-six-phase`
- Keep active for now.
- Reason: not suitable as the sole design-system mainline, but still carries real implementation evidence (layouts, TS env, chart work).
- Constraint: treat as auxiliary/parallel roadmap, not as the canonical ArtDeco conversion line.

### `integrate-fullstack-platform`
- Keep active for now.
- Reason: partial wiring is present, but audit shows route/env/path drift and unverifiable integration goals.
- Constraint: cannot be archived as completed without a repo-truth closeout pass.

## 3. Conflict / Pending Adjudication

### `consolidate-technical-debt-remediation`
- Do not archive or delete yet.
- Conflict: some historical reports mark it “fully complete”, while current repo audit still shows major unfinished scope and missing source proposals.
- Needed next: explicit adjudication whether to retire as obsolete umbrella proposal, or rebuild as a narrower current-scope debt program.

## 4. Lower-Priority Active Changes Not Touched In This Round

- `optimize-data-source-v2`
- `refactor-web-frontend-menu-architecture`
- `implement-web-frontend-v2-navigation`
- `implement-pinia-api-standardization`
- `implement-typescript-type-extension-system`
- `implement-html5-migration-experience-optimization`
- `expand-akshare-data-sources`
- `enhance-api-contract-management-integration`
- `add-quantitative-trading-algorithms`
- `add-smart-quant-monitoring`
- `add-comprehensive-risk-management-system`

Current posture: leave untouched until their ownership, overlap, and repo-truth execution status are explicitly re-triaged.

## 5. Recommended Next Order

1. Adjudicate `consolidate-technical-debt-remediation` with an explicit keep/rebuild/retire decision.
2. Decide whether `frontend-optimization-six-phase` should remain active as an auxiliary roadmap or be rewritten as pure supporting documentation.
3. Re-triage `integrate-fullstack-platform` against current `3020/8020 + PM2 + router/menu` repo truth.
4. Re-triage `optimize-data-source-v2` because code evidence exists but core SmartCache / CircuitBreaker / SmartRouter wiring is still incomplete.

## 6. Validation Snapshot

- `openspec validate --specs` passed after the changes in this round (`19 passed, 0 failed`).
- All micro-batches committed in this round used `gitnexus_detect_changes(scope="staged")` and returned `risk_level=low`.
