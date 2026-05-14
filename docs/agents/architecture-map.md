# MyStocks Architecture Map

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

> Status: Approved governance index
> Created: 2026-05-14
> Purpose: provide a lightweight navigation map for humans and agents. This file is not a replacement for project standards, OpenSpec specs, or implementation documentation.

## 1. Authority Order

Use these sources in this order when making architecture decisions:

1. `architecture/STANDARDS.md`
   - Engineering red lines.
   - Proposal-first approval gate.
   - Migration closure and technical-debt governance.
   - Shared rule source for agent entry documents.

2. `openspec/specs/*/spec.md`
   - Current capability truth.
   - Requirements and scenarios for implemented or accepted behavior.

3. `openspec/changes/*`
   - Proposed or in-progress changes.
   - Must be checked before opening new work in the same area.

4. Focused project guides
   - `docs/guides/frontend-structure.md` for current frontend directory and route truth.
   - `docs/standards/technical-debt-governance-charter-v1.md` for debt baseline and governance reporting.

5. zread wiki
   - `.zread/wiki/versions/2026-05-14-013747/`
   - Use as an architecture orientation layer, not as normative source text.

## 2. OpenSpec Routing

Create or attach to an OpenSpec change before implementing any work that changes:

- API, schema, OpenAPI contract, response semantics, authentication, or error shape.
- Frontend routing, canonical page ownership, navigation structure, or layout architecture.
- Data source behavior, adapter selection, health checks, storage routing, database table contracts, or cache semantics.
- Cross-cutting architecture patterns.
- Performance behavior that changes user-visible or operational semantics.

Prefer attaching to an existing active change when one already owns the area.

Current active changes relevant to architecture governance:

- `restructure-frontend-directory`
- `implement-html5-migration-experience-optimization`
- `enhance-api-contract-management-integration`
- `optimize-data-source-v2`
- `implement-optimized-html-vue-artdeco-conversion`
- `add-smart-quant-monitoring`
- `add-comprehensive-risk-management-system`

## 3. Capability Specs To Check First

Architecture and repository governance:

- `openspec/specs/architecture-governance/spec.md`
- `openspec/specs/directory-governance/spec.md`
- `openspec/specs/documentation-governance/spec.md`
- `openspec/specs/code-quality/spec.md`

Frontend:

- `openspec/specs/frontend-routing/spec.md`
- `openspec/specs/frontend-type-system/spec.md`
- `openspec/specs/api-integration/spec.md`
- `openspec/specs/03-adapter-pattern/spec.md`
- `openspec/specs/04-smart-dumb-components/spec.md`
- `openspec/specs/artdeco-design-governance/spec.md`

Backend and contracts:

- `openspec/specs/api-integration/spec.md`
- `openspec/specs/api-documentation/spec.md`
- `openspec/specs/01-unified-response-format/spec.md`
- `openspec/specs/02-type-safety-generation/spec.md`
- `openspec/specs/05-csrf-protection/spec.md`

Data and trading:

- `openspec/specs/data-sources/spec.md`
- `openspec/specs/data-quality-governance/spec.md`
- `openspec/specs/market-data/spec.md`
- `openspec/specs/financial-data/spec.md`
- `openspec/specs/quantitative-trading-algorithms-api/spec.md`
- `openspec/specs/portfolio-attribution-analysis/spec.md`

## 4. Current Runtime Truths

Backend composition:

- Canonical FastAPI runtime entry: `web/backend/app/main.py`
- Compatibility test factory: `web/backend/app/app_factory.py`
- Router registration: `web/backend/app/router_registry.py`
- Versioned router entry: `web/backend/app/api/v1/router.py`
- Monitoring API thin-route pilot:
  - Route aggregator: `web/backend/app/api/monitoring.py`
  - Realtime and dragon-tiger route module: `web/backend/app/api/monitoring_market_routes.py`
  - OpenAPI response specs: `web/backend/app/api/monitoring_response_specs.py`
  - Summary use-case service: `web/backend/app/services/monitoring_summary_service.py`
  - Control lifecycle use-case service: `web/backend/app/services/monitoring_control_service.py`
  - Alert-rule use-case service: `web/backend/app/services/monitoring_alert_rule_service.py`
  - Alert-record use-case service: `web/backend/app/services/monitoring_alert_record_service.py`
  - Keep authentication, parameter parsing, response wrapping, route registration, and HTTP docs in route modules; keep reusable response examples in the response-spec module; keep summary assembly, monitoring lifecycle state, alert-rule persistence orchestration, alert-record pagination/read orchestration, and runtime fallback selection in the use-case services.

Frontend routing:

- Canonical router file: `web/frontend/src/router/index.ts`
- Current route truth must be checked against `docs/guides/frontend-structure.md`.
- Current repo-truth exceptions:
  - `/dashboard` is still provided by `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`.
  - `/trade/terminal` is still provided by `web/frontend/src/views/TradingDashboard.vue`.

Contract generation:

- Canonical frontend type generation command: `python scripts/generate_frontend_types.py`
- Canonical CLI helper: `scripts/_generate_frontend_types_cli.py`
- Legacy compatibility wrapper: `scripts/dev/generate-types/generate_ts_types.py`
  - Delegates to the canonical command.
  - Rejects old external-tool flags such as `--tool`, `--contracts-dir`, and `--output-dir`.
- Backend OpenAPI service: `web/backend/app/api/contract/services/openapi_generator.py`
  - Treat as backend schema/OpenAPI generation support, not a parallel frontend type generation path.
- Active governance change: `enhance-api-contract-management-integration`.

## 5. Architecture Terms

Use these terms consistently in governance proposals:

- `Data Source Runtime`: external source access, source priority, health checks, circuit breaking, rate limits, quality checks, failover, and recovery.
- `Storage Routing Runtime`: routing from `DataClassification` to TDengine/PostgreSQL, table configuration, transaction behavior, batch writes, and failure strategy.
- `Canonical route truth`: the route-to-component mapping accepted by current repository state, not by stale migration snapshots.
- `Generated contract artifact`: output derived from backend schema/OpenAPI generation and not intended for manual edits unless a spec says otherwise.
- `Compatibility layer`: temporary or legacy path that must carry a retirement condition.

## 6. Known Governance Risks

- The working tree may be dirty. Do not use unstaged whole-worktree analysis as a verdict for a specific governance batch.
- Archive and legacy directories contain old symbols that can confuse static analysis and AI navigation.
- Active migration files and compatibility wrappers must not be deleted only because text search finds no references.
- Frontend directory truth has changed over time. Check current router and `docs/guides/frontend-structure.md`, not old migration snapshots.
- Data-source concepts are spread across `src/adapters`, `src/data_sources`, `src/data_access`, `src/storage`, `src/database`, and `src/core`.
- `AdapterRegistry` currently appears in both `src/core/infrastructure/adapter_registry.py` and `web/backend/app/core/adapter_factory.py`; treat this as concept-scatter evidence until a canonical registry is approved.

## 7. Agent Workflow

Before proposing or implementing architecture work:

1. Read `architecture/STANDARDS.md`.
2. Check active changes with `openspec list`.
3. Check relevant specs with `openspec list --specs` and `openspec show <spec-id> --type spec`.
4. Attach to an existing active change when possible.
5. If no active change owns the area, create a new OpenSpec proposal and validate it before implementation.
6. For code edits, use GitNexus impact analysis before modifying symbols and staged `detect_changes` before commit.
7. For frontend build, type-check, E2E, or service-start tasks, report quality status using the mandatory project format in `AGENTS.md`.

## 8. Non-Goals

This document does not authorize:

- Code changes.
- Route changes.
- API or schema changes.
- Data source behavior changes.
- Legacy/archive deletion.
- Technical debt baseline updates.
- Creation of new OpenSpec changes without explicit approval for a concrete governance slice.
