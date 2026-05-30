# ArtDeco Impeccable Line: Function Tree Summary And Next Plan

Date: 2026-05-31

## 1. Purpose

This document summarizes the completed ArtDeco / impeccable Web design governance line, maps the work back to the current Function Tree, and defines the next safe implementation plan.

The line goal has been:

> Use impeccable as a Web-side design governance and route polish workflow to audit the already implemented ArtDeco design, improve page design quality, component reuse, visual token usage, runtime state presentation, and validation gates, while staying aligned with the current ArtDeco documentation system.

This line deliberately avoided a one-shot whole-site beautification pass. The implementation path used approved route pilots, evidence documents, OpenSpec gates, focused E2E checks, ArtDeco token validation, impeccable audits, and GitNexus scope checks.

## 2. Function Tree Position

Current Function Tree source:

- `docs/FUNCTION_TREE.md`

Function Tree governance status:

- Command: `node /root/.codex/skills/myskills/skills/function-tree/scripts/ft-governance.cjs status`
- Result: `programs: (none)`, `active gates: 0`

Therefore, this line is not currently represented as a standalone `.governance/programs/<program>/` Function Tree program. It should be interpreted as a cross-domain Web ArtDeco design governance line that attaches to existing product route nodes.

## 3. Function Tree Mapping

| Function Tree Area | Node / Position | Covered Route Or File | Work Completed In This Line |
|---|---|---|---|
| `01-市场数据与行情` | `1.1 实时行情监控` | `web/frontend/src/views/market/Realtime.vue` | Market realtime ArtDeco critique, shape brief, approval packet, implementation report, hook alignment, focused E2E, token gate, impeccable gate |
| `04-风险管理与监控` | `4.3 风险仪表板` | `web/frontend/src/views/risk/Alerts.vue` | Risk alerts critique, shape brief, implementation report, severity-first triage desk, runtime state hardening, route hooks |
| `06-监控与告警` | `6.3 告警管理` | `web/frontend/src/views/risk/Alerts.vue` | Alert rules / alert history route quality improvements and validation hooks |
| `05-投资组合与交易` | `5.1 持仓管理` | `web/frontend/src/views/trade/Center.vue`, route `/trade/positions` | Trade positions critique, shape brief, ArtDeco review desk implementation, segment hooks, filtered-empty hook, route header shell extraction |
| `05-投资组合与交易` | `5.1 持仓管理` | `web/frontend/src/views/trade/Portfolio.vue`, route `/trade/portfolio` | Route grammar hook alignment and evidence report; not yet migrated to shared route shell |
| `05-投资组合与交易` | `5.2 交易记录` | `web/frontend/src/views/trade/Reconciliation.vue` | Route grammar hook alignment and evidence report |
| `05-投资组合与交易` | `5.3 交易决策` | `web/frontend/src/views/trade/Signals.vue`, `web/frontend/src/views/trade/Execution.vue` | Trade signals implementation line and route grammar hook alignment for signals / execution |
| `07-高级分析与AI` | `7.2 批量分析` | `web/frontend/src/views/ai/BatchAnalysis.vue` | Route grammar hook alignment and evidence report |
| `07-高级分析与AI` | `7.3 情感分析` | `web/frontend/src/views/ai/Sentiment.vue` | Route grammar hook alignment and evidence report |
| Cross-domain governance | No standalone FT node yet | `openspec/specs/artdeco-design-governance/spec.md` and related reports | ArtDeco design governance is currently tracked through OpenSpec and task reports rather than a Function Tree program node |

## 4. Completed Work

### 4.1 Planning And Design Governance

Completed documents:

- `docs/reports/tasks/2026-05-28-artdeco-web-design-alignment-plan.md`
- `docs/reports/tasks/2026-05-28-artdeco-design-context-audit.md`
- `docs/reports/tasks/2026-05-28-artdeco-page-review-checklist.md`
- `docs/reports/tasks/2026-05-29-artdeco-impeccable-line-summary-and-next-plan.md`
- `docs/reports/tasks/2026-05-29-artdeco-impeccable-line-summary-review.md`

Outcome:

- Established the working goal for impeccable as a design governance workflow.
- Aligned the route work with the ArtDeco document set.
- Set the sequence: critique -> shape brief -> approval -> craft -> audit -> report -> extract only after repeated patterns are proven.
- Explicitly kept shared extraction out of early page craft work.

### 4.2 Page Pilots

Completed route pilots:

- `market/Realtime.vue`
  - Critique: `docs/reports/tasks/2026-05-28-artdeco-market-realtime-critique.md`
  - Shape brief: `docs/reports/tasks/2026-05-28-artdeco-market-realtime-shape-brief.md`
  - Approval packet: `docs/reports/tasks/2026-05-28-artdeco-market-realtime-approval-packet.md`
  - Implementation report: `docs/reports/tasks/2026-05-28-artdeco-market-realtime-implementation-report.md`
  - Commit evidence includes `de0c5b8c9 feat(web): add ArtDeco realtime design gate pilot`

- `risk/Alerts.vue`
  - Critique: `docs/reports/tasks/2026-05-29-artdeco-risk-alerts-critique.md`
  - Shape brief: `docs/reports/tasks/2026-05-29-artdeco-risk-alerts-shape-brief.md`
  - Implementation report: `docs/reports/tasks/2026-05-29-artdeco-risk-alerts-implementation-report.md`
  - Commit evidence includes `8ed6c91d0 feat(web): craft ArtDeco risk alerts triage desk`

- `trade/Center.vue` / `/trade/positions`
  - Critique: `docs/reports/tasks/2026-05-29-artdeco-trade-positions-critique.md`
  - Shape brief: `docs/reports/tasks/2026-05-29-artdeco-trade-positions-shape-brief.md`
  - Implementation report: `docs/reports/tasks/2026-05-29-artdeco-trade-positions-implementation-report.md`
  - Later hook alignment and route header shell extraction completed.

- `trade/Signals.vue`
  - Critique: `docs/reports/tasks/2026-05-29-artdeco-trade-signals-critique.md`
  - Shape brief: `docs/reports/tasks/2026-05-29-artdeco-trade-signals-shape-brief.md`
  - Approval packet: `docs/reports/tasks/2026-05-29-artdeco-trade-signals-implementation-approval-packet.md`
  - Implementation report: `docs/reports/tasks/2026-05-29-artdeco-trade-signals-implementation-report.md`

### 4.3 Route Grammar Governance

Completed OpenSpec and closeout work:

- OpenSpec change: `standardize-artdeco-route-grammar`
- Closeout checklist: `docs/reports/tasks/2026-05-30-artdeco-route-grammar-closeout-checklist.md`
- Closeout report: `docs/reports/tasks/2026-05-30-artdeco-route-grammar-closeout-report.md`
- Archived as: `openspec/changes/archive/2026-05-30-standardize-artdeco-route-grammar/`
- Canonical spec updated: `openspec/specs/artdeco-design-governance/spec.md`

Route hook alignment reports completed:

- `docs/reports/tasks/2026-05-30-artdeco-market-realtime-hook-alignment-report.md`
- `docs/reports/tasks/2026-05-29-artdeco-risk-alerts-hook-alignment-report.md`
- `docs/reports/tasks/2026-05-30-artdeco-trade-positions-hook-alignment-report.md`
- `docs/reports/tasks/2026-05-30-artdeco-trade-portfolio-hook-alignment-report.md`
- `docs/reports/tasks/2026-05-29-artdeco-trade-reconciliation-hook-alignment-report.md`
- `docs/reports/tasks/2026-05-30-artdeco-trade-execution-hook-alignment-report.md`
- `docs/reports/tasks/2026-05-30-artdeco-ai-batch-hook-alignment-report.md`
- `docs/reports/tasks/2026-05-30-artdeco-ai-sentiment-hook-alignment-report.md`

Key result:

- The route-level ArtDeco grammar is no longer just page-specific craft. It is now an OpenSpec-backed design governance rule set covering route hooks, runtime status, filtered-empty states, stable data hooks, and validation reports.

### 4.4 First Shared Route Shell Extraction

Completed OpenSpec change:

- `extract-artdeco-route-shell-components`

Implementation report:

- `docs/reports/tasks/2026-05-31-artdeco-route-header-extraction-report.md`

Code added:

- `web/frontend/src/components/artdeco/route-shell/ArtDecoRouteHeader.vue`
- `web/frontend/src/components/artdeco/route-shell/index.ts`
- `web/frontend/src/components/artdeco/route-shell/__tests__/ArtDecoRouteHeader.spec.ts`

Route migrated:

- `/trade/positions`
- `web/frontend/src/views/trade/Center.vue`

Commit:

- `0693629f9 feat(web): extract ArtDeco route header shell`

Boundary:

- No router changes.
- No backend API contract changes.
- No frontend API client changes.
- No shared business state extraction.
- No shared runtime-state abstraction yet.

## 5. Verification Evidence Summary

Recent completed verification across the line includes:

- Focused Vitest for `ArtDecoRouteHeader`: `1 passed`.
- Focused Chromium E2E for `Trade-Positions`: `5 passed`.
- Focused Chromium E2E for route grammar closeout: `Trade-Positions` route checks passed.
- `npm run type-check -- --pretty false`: passed in the latest route shell slice.
- `npx eslint` focused file checks: passed in the latest route shell slice.
- `node scripts/check-artdeco-tokens.js`: passed for the latest route shell slice.
- `npx impeccable --json`: returned `[]` for `Center.vue` and `ArtDecoRouteHeader.vue` in the latest slice.
- `openspec validate extract-artdeco-route-shell-components --strict`: passed.
- PM2 status confirmed:
  - `mystocks-backend`: online at `http://localhost:8020`
  - `mystocks-frontend`: online at `http://localhost:3020`
- GitNexus staged scope gate for the latest slice: low risk, 6 changed files, 0 affected processes.
- GitNexus CLI index refresh completed: 234,189 nodes, 321,490 edges, 300 flows.

Known tool note:

- GitNexus MCP metadata still reported `stale=true` after CLI index refresh during the last slice. The staged scope result still returned low risk and no affected processes; this was recorded as a tool metadata warning, not as scope expansion.

## 6. Current Status

OpenSpec status:

- `add-artdeco-impeccable-design-gate`: complete.
- `standardize-artdeco-route-grammar`: archived and validated.
- `extract-artdeco-route-shell-components`: archived as `openspec/changes/archive/2026-05-30-extract-artdeco-route-shell-components/` and validated.

Function Tree status:

- A dedicated Function Tree governance program now exists at `.governance/programs/artdeco-web-design-governance/`.
- Active node: `artdeco-web-design-governance/route-header-shell-trade-portfolio`.
- Node status: `approved-for-implementation`.
- Next allowed action: implement within the authorized paths for the `/trade/portfolio` header-shell-only migration.
- The line also maps to existing domain nodes, especially:
  - `1.1 实时行情监控`
  - `4.3 风险仪表板`
  - `6.3 告警管理`
  - `5.1 持仓管理`
  - `5.2 交易记录`
  - `5.3 交易决策`
  - `7.2 批量分析`
  - `7.3 情感分析`

Implementation status:

- The first shared route shell component is implemented and proven on `/trade/positions`.
- Broader route shell rollout has intentionally stopped at the first slice until the new Function Tree gate is used for the next route.
- The next route shell slice is authorized only for `/trade/portfolio` header-shell migration and the supporting docs / tests listed in `.governance/active-gates.md`.

## 7. Recommended Next Plan

### Phase 1: Review And Archive Current Route Shell Extraction

Priority: P0. Status: complete.

Recommended tasks:

- Reviewed `docs/reports/tasks/2026-05-31-artdeco-route-header-extraction-report.md` as the closeout evidence for the first route shell extraction.
- Archived `extract-artdeco-route-shell-components`.
- Ran `openspec validate --all --strict`.

Exit criteria:

- OpenSpec change archived: `openspec/changes/archive/2026-05-30-extract-artdeco-route-shell-components/`.
- Validation result: `63 passed`, `0 failed`.

### Phase 2: Function Tree Governance Decision

Priority: P1. Status: complete.

Decision:

- Create a formal Function Tree governance program for Web ArtDeco design governance.

Program identity:

- Program: `artdeco-web-design-governance`
- Reference: `docs/FUNCTION_TREE.md#cross-domain-artdeco-web-design-governance`
- Positioning: cross-domain governance, with references to affected product nodes rather than claiming a single product feature node.

Generated outputs:

- `.governance/programs/artdeco-web-design-governance/`
- `.governance/active-gates.json`
- `.governance/active-gates.md`
- Active gate for `route-header-shell-trade-portfolio`

Exit criteria:

- Function Tree program exists.
- Governance validation passed.
- Active gate status is `approved-for-implementation`.

### Phase 3: Second Route Header Shell Migration

Priority: P1.

Recommended candidate:

- `web/frontend/src/views/trade/Portfolio.vue`
- Function Tree node: `05-投资组合与交易 / 5.1 持仓管理`

Reason:

- It is close to `/trade/positions` in domain language and page grammar.
- It is lower risk than jumping directly to `risk/Alerts.vue`.
- It validates whether `ArtDecoRouteHeader` generalizes across related trading / portfolio surfaces.

Scope limits:

- Replace only the route header shell.
- Preserve route hooks and copy.
- Do not change router config.
- Do not change API contracts.
- Do not extract runtime strips, segments, or data panels yet.

Required gates:

- GitNexus impact before editing.
- Focused E2E for `/trade/portfolio`.
- ArtDeco token gate.
- `npx impeccable --json`.
- Focused ESLint.
- `npm run type-check -- --pretty false`.
- GitNexus staged scope gate before commit.

### Phase 4: Third Route Header Shell Migration

Priority: P2.

Recommended candidate:

- `web/frontend/src/views/risk/Alerts.vue`
- Function Tree nodes:
  - `04-风险管理与监控 / 4.3 风险仪表板`
  - `06-监控与告警 / 6.3 告警管理`

Reason:

- This validates the route shell outside the trading domain.
- It should happen only after one more trading/portfolio route proves the component boundary.

Scope limits:

- Header shell only.
- Preserve risk severity hierarchy.
- Do not move alert state logic into shared components.

### Phase 5: Separate Proposal For Runtime And Segment Components

Priority: P2.

Do not implement immediately.

Candidates:

- `ArtDecoRuntimeStatusStrip`
- `ArtDecoReviewSegments`
- `ArtDecoDataPanel`

Reason:

- These are more behavior-adjacent than the route header.
- They touch runtime state vocabulary, filtered-empty logic, table states, and route-local review lenses.
- They need a separate shape brief / OpenSpec proposal before code.

Required preconditions:

- Compare at least three routes after the second route shell migration.
- Document exact props / slots / events / non-goals.
- Explicitly define what remains route-owned.

## 8. Recommended Immediate Next Action

The next safest action after this update is:

1. Commit the governance archive, Function Tree program, and this summary update.
2. Start the authorized `route-header-shell-trade-portfolio` node.
3. Run GitNexus impact before editing `web/frontend/src/views/trade/Portfolio.vue`.
4. Migrate only the `/trade/portfolio` header shell to `ArtDecoRouteHeader`.

This keeps the line aligned with the Function Tree: improve real product route nodes first, keep shared components small, and only create broader design-system abstractions after repeated route evidence proves the boundary.

## 9. Continuation Evidence

Commands completed after this document was first created:

- `openspec archive extract-artdeco-route-shell-components --yes`
  - Result: archived as `2026-05-30-extract-artdeco-route-shell-components`.
  - Spec update: `artdeco-design-governance`, `+1` requirement.
- `openspec validate --all --strict`
  - Result: `63 passed`, `0 failed`.
- `node /root/.codex/skills/myskills/skills/function-tree/scripts/ft-governance.cjs init artdeco-web-design-governance ... --no-doc`
  - Result: created `.governance/programs/artdeco-web-design-governance/` without generating a root-level `FUNCTION_TREE.md`.
- `node /root/.codex/skills/myskills/skills/function-tree/scripts/ft-governance.cjs new-node artdeco-web-design-governance route-header-shell-trade-portfolio ...`
  - Result: created the next implementation node.
- `node /root/.codex/skills/myskills/skills/function-tree/scripts/ft-governance.cjs observe ...`
  - Result: recorded this summary document as baseline evidence.
- `node /root/.codex/skills/myskills/skills/function-tree/scripts/ft-governance.cjs authorize ...`
  - Result: prepared an authorization draft with explicit allowed paths, non-goals, commit gates, and closeout gates.
- `node /root/.codex/skills/myskills/skills/function-tree/scripts/ft-governance.cjs transition ... --to approved-for-implementation`
  - Result: active gate now allows implementation within authorized paths.
- `node /root/.codex/skills/myskills/skills/function-tree/scripts/ft-governance.cjs validate --steward`
  - Result: governance validation passed.
