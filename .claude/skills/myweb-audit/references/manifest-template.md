# Minimal Manifest Template

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

Use this minimal manifest at the start of each batch.

```yaml
audit_run_id: audit-YYYYMMDD-01
batch_id: market-batch-01
module: market
scope:
  requested_by: user
  pages:
    - route: /market/overview
      page_key: market-overview
      route_class: canonical-page
      canonical_entry: web/frontend/src/views/market/MarketOverview.vue
    - route: /market/watchlist
      page_key: market-watchlist
      route_class: canonical-page
      canonical_entry: web/frontend/src/views/market/MarketWatchlist.vue
  compatibility_redirects: []
batch_rationale: Primary navigation market pages with shared table and filter patterns.
audit_roles:
  - route-inventory
  - functional-audit
  - data-state-audit
  - visual-artdeco-audit
  - responsive-a11y-audit
environment:
  frontend_url: http://localhost:3020
  backend_url: http://localhost:8020
  browser_tool: playwright
  execution_surface: live-audit
  frontend_runtime_mode: reuse-existing
  assumptions:
    - frontend dev or PM2 service is reachable
    - backend API is reachable for spot verification
  fallback_log: []
verification_plan:
  verification_strategy: full
  browser_project: chromium
  breakpoints: [1920, 1440, 1280]
  required_states: [default, loading, empty, error, disabled, extreme-data]
  notes:
    - verify primary table/filter flows first
    - state if external frontend reuse or partial verification is intentional
repair_approval:
  status: not_requested
  approved_findings: []
  deferred_findings: []
state_tracking:
  completed_pages: []
  pending_pages:
    - market-overview
    - market-watchlist
  fixed_files: []
  shared_impact:
    candidates: []
    confirmed: []
  validation_status:
    syntax: not-run
    typecheck: not-run
    pm2: not-run
    e2e: not-run
    gitnexus_staged_detect: not-run
  staged_scope:
    mode: not-started
    files: []
artifacts:
  page_reports: []
  raw_findings: null
  merged_findings: null
  batch_report: null
  closeout: null
status: in_progress
```

## Field Notes

- `audit_run_id`: stable id for the current audit request
- `batch_id`: must match `references/batching-rules.md`
- `canonical_entry`: use router truth, not wrapper assumptions
- `artifacts`: fill as files or inline outputs are produced
- `status`: use `in_progress`, `blocked`, `deferred`, or `complete`
- `execution_surface`: use `live-audit` or `code-review-only`
- `verification_strategy`: use `full`, `chromium-only`, or `code-review-only`
- `frontend_runtime_mode`: use `reuse-existing` or `start-new` to declare whether the batch reused an existing frontend surface
- `repair_approval`: use `not_requested` -> `pending` -> `approved` or `partial` after the merged-findings approval checkpoint
- `route_class`: use `canonical-page`, `detail-page`, or `compatibility-redirect`
- `fallback_log`: record any Playwright, PM2, dirty-worktree, or agent-capacity fallback that changed the intended execution mode
- `validation_status` and `staged_scope` are the closeout truth for the current batch
- This template is intentionally minimal, but it is expected to carry enough state for cross-session recovery and honest closeout.
