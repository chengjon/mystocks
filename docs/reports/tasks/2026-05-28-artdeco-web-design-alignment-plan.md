# MyStocks Web ArtDeco Design Alignment Plan - 2026-05-28

> **权威来源声明**:
> 本文件是任务计划，不是仓库共享规则、当前实现状态或审批门禁的唯一事实来源。
> 仓库级规则以 `architecture/STANDARDS.md` 为准；ArtDeco 文档口径以 `docs/guides/web/ARTDECO_MASTER_INDEX.md` 的分层为入口；实际路由与运行状态以当前代码、验证结果和运行时探测为准。

## 1. Goal

使用 `impeccable` 技能审核当前项目已经实现的 Web 端 ArtDeco 设计，先产出设计文档和审核结论，提升页面设计、组件复用、视觉 token、运行时状态和验证门禁的规划质量，并对齐当前 ArtDeco 文档体系。

对于原设计或原文档中可以优化的地方，按影响范围、风险、复用价值和验证成本分级选择优化。本计划把 `impeccable` 作为一条 Web 端设计治理和页面打磨工作流，而不是一次性“美化全站”。

本计划不直接实施前端源码改造。当前阶段只允许输出设计文档、页面审核报告、shape brief、任务拆分、优先级、验收标准和文档对齐规则。只有在这些设计文档完成并获得审批后，才进入 `craft`、代码修改、组件抽取和运行验证阶段。

## 2. Scope

### In Scope

- Web 端 ArtDeco 视觉设计规范收口
- 页面设计规范性提升
- 设计文档、审核报告、shape brief 和验收清单产出
- canonical route 与 ArtDeco 页面资产边界确认
- `DESIGN.md` 与 ArtDeco 文档链的口径对齐
- 核心页面的 critique、shape、craft、audit、polish、extract 批次规划
- token 使用、组件复用、状态设计、A 股金融语义和可访问性验收标准

### Out of Scope

- 当前文档阶段不改 Vue 页面源码
- 当前文档阶段不改 SCSS、token、组件或路由实现
- 不重构路由结构
- 不删除 legacy / compatibility ArtDeco 文件
- 不替换 Element Plus 或图表库
- 不把 `views/artdeco-pages/**` 重新定义为全部活跃业务路由真相源
- 不跳过 OpenSpec 审批去落地跨路由架构模式变更

## 3. Source Documents

本计划参考并对齐以下 8 个目标文档：

| Path | Role In This Plan | Notes |
|---|---|---|
| `docs/guides/web/ARTDECO_MASTER_INDEX.md` | ArtDeco 文档入口和分层索引 | 明确 active docs、历史基线、兼容入口和维护规则 |
| `docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md` | 当前 ArtDeco Fintech 统一规格 | 定义设计身份、真值链、组件边界、运行时承载模式和工程铁律 |
| `web/frontend/ARTDECO_COMPONENTS_CATALOG.md` | 当前 ArtDeco 组件和页面资产目录 | 记录 reusable assets、domain components、page-level blocks 和 tab workbench blocks |
| `docs/api/ArtDeco_System_Architecture_Summary.md` | 当前运行时架构摘要 | 定义 router、layout、components、artdeco-pages、styles、shared runtime state 六层 |
| `docs/guides/web/ARTDECO_COMPONENT_GUIDE.md` | 组件放置和开发治理 | 定义 reusable asset、page fragment、tab block、canonical routed page 的目录决策 |
| `docs/reports/ARTDECO_V3_COMPLETE_SUMMARY.md` | 历史基线和演进摘要 | 记录 V3 初始升级、有效资产、运行时模式变化和当前口径变化 |
| `docs/guides/ARTDECO_FINTECH_UNIFIED_SPEC.md` | 兼容入口 | 指向 `docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md`，不是主内容源 |
| `docs/api/ARTDECO_SYSTEM_ARCHITECTURE_SUMMARY.md` | 兼容入口 | 指向 `docs/api/ArtDeco_System_Architecture_Summary.md`，不是主内容源 |

Related current context:

- `PRODUCT.md`: Web 端产品语境，register = `product`
- `DESIGN.md`: MyStocks Web ArtDeco Design System, version 4.1
- `docs/guides/frontend-structure.md`: 当前前端目录与路由真相源说明
- `web/frontend/src/router/index.ts`: active route truth
- `web/frontend/src/styles/artdeco-tokens.scss`: current ArtDeco token truth

## 4. Alignment Principles

1. **Route truth and ArtDeco truth are separate**
   - Active route truth comes from `web/frontend/src/router/index.ts`.
   - Canonical business pages usually live under `web/frontend/src/views/<domain>/*.vue`.
   - `views/artdeco-pages/**` can contain route exceptions, wrappers, templates, workbench blocks, and compatibility layers.

2. **Token truth is implementation truth**
   - New visual work must use `web/frontend/src/styles/artdeco-tokens.scss` and `--ad-*` component state tokens.
   - `artdeco-main.css`, `artdeco-colors.css`, and `artdeco-variables.css` are compatibility paths, not the primary token source.
   - Raw hex values inside touched Vue or SCSS files are treated as legacy debt unless the value is a chart series or documented exception.

3. **Components must be placed by reuse boundary**
   - Reusable UI: `web/frontend/src/components/artdeco/base|core|business|charts/**`
   - Domain reusable components: `web/frontend/src/components/artdeco/trading|advanced|specialized/**`
   - ArtDeco page-system fragments: `web/frontend/src/views/artdeco-pages/components/**`
   - Domain tab workbench blocks: `web/frontend/src/views/artdeco-pages/*-tabs/**`
   - Active routed pages: `web/frontend/src/views/<domain>/*.vue`
   - Cross-layout/page shared state: `web/frontend/src/composables/**`

4. **Design serves task performance**
   - This is a product UI, not a brand site.
   - Decoration must not compete with price, risk, freshness, execution state, or chart readability.
   - ArtDeco drama is allowed in overview, onboarding, empty, and feature-introduction states, but operational surfaces stay restrained.

5. **A-share semantics are non-negotiable**
   - Red = up, profit, positive delta, buy pressure.
   - Green = down, loss, negative delta, sell pressure.
   - Color must be reinforced with sign, label, icon, or numeric delta.

6. **Runtime states are part of page design**
   - Loading, empty, stale, degraded backend, mock data, error, partial data, and success states must be specified before craft implementation.

## 5. Recommended Execution Strategy

Use `impeccable` as a Web design governance and page polishing workflow. The repository has many pages, historical ArtDeco layers and canonical route entries living together, so the safest route is to close the design context first, then improve route by route.

Recommended command sequence:

Document-first approval sequence:

1. `$impeccable document`
2. `$impeccable critique <target>`
3. `$impeccable shape <target>`
4. User approval of the design documents and implementation scope

Implementation sequence after approval:

1. `$impeccable craft <target>`
2. `$impeccable audit <target>`
3. `$impeccable polish <target>`
4. `$impeccable extract <target>`

Important rule:

- `document` is a baseline step, not a per-page requirement. Re-run it after meaningful design-system or token changes.
- `critique` audits the currently implemented design before code changes. It should produce page-level issues, not implementation edits.
- `shape` produces the design brief and implementation scope. It is still documentation work until the user approves it.
- `craft` must not start until `shape` has produced a task-specific brief and the user has explicitly confirmed it.
- `teach` / `PRODUCT.md` / `DESIGN.md` provide project context only. They are not a shape brief.

### Approval Boundary

Before approval, allowed outputs are:

- refreshed design context notes from `$impeccable document`
- ArtDeco documentation alignment findings
- route-level critique reports
- shape briefs
- page review checklists
- implementation task plans and verification plans

Before approval, disallowed outputs are:

- Vue, TypeScript, SCSS or route implementation changes
- token rewrites
- component extraction
- broad visual cleanup
- PM2, E2E or build-gate claims for unimplemented UI work

After approval, implementation must stay inside the confirmed shape scope and report the frontend quality gates required by `architecture/STANDARDS.md`.

Recommended first target:

```text
$impeccable critique web/frontend/src/views/market/Realtime.vue
```

Rationale: `market/Realtime.vue` is high-value, data-dense and user-facing. It exposes the core ArtDeco questions around real-time market state, data density, stale feedback, filter controls, table and chart structure, A-share color semantics and runtime degradation.

### Optimization Priority Model

Use this priority order when original design or documentation can be improved:

| Priority | Optimize When | Examples |
|---|---|---|
| P0 | The item contradicts route truth, token truth, runtime safety or verification gates | docs implying `views/artdeco-pages/**` is universal route truth, new hard-coded visual values, missing stale/error handling |
| P1 | The item affects high-use pages or task-critical workflows | realtime market data, trading workflow, risk monitoring, system operational state |
| P2 | The item can become a reusable page or component pattern after 2+ consumers | page header band, control row, status strip, data panel, route-level state pattern |
| P3 | The item is historical, cosmetic or low-risk documentation cleanup | old screenshots, V3 summary wording, compatibility pointer polish |

## 6. Workstreams

### Workstream A: Design Context and ArtDeco Documentation Alignment

Purpose: make `DESIGN.md` and the ArtDeco document chain reflect the actual implemented visual system before any page implementation begins.

Tasks:

- A0. Run `$impeccable document` to extract the current real visual system from code, especially:
  - `web/frontend/src/styles/artdeco-tokens.scss`
  - `web/frontend/src/styles/element-plus-artdeco.scss`
  - `web/frontend/src/styles/artdeco-global.scss`
  - `web/frontend/src/styles/artdeco-financial.scss`
  - `web/frontend/src/styles/bloomberg-terminal-override.scss`
- A1. Reconcile the extracted facts into `DESIGN.md` only where they clarify real tokens, reusable assets, active constraints or legacy boundaries.
- A2. Confirm `DESIGN.md` version 4.1 references the same truth chain as `ARTDECO_MASTER_INDEX.md`.
- A3. Compare extracted implementation facts against the eight ArtDeco source documents and mark optimizations by P0 to P3 priority.
- A4. Add a cross-reference from ArtDeco guide documents to the refreshed `PRODUCT.md` and `DESIGN.md` only if current governance allows it.
- A5. Verify that compatibility files remain pointers:
  - `docs/guides/ARTDECO_FINTECH_UNIFIED_SPEC.md`
  - `docs/api/ARTDECO_SYSTEM_ARCHITECTURE_SUMMARY.md`
- A6. Review whether `ARTDECO_MASTER_INDEX.md` should mention `DESIGN.md` version 4.1 and the updated Web page standards.
- A7. Keep historical documents historical. Do not rewrite `ARTDECO_V3_COMPLETE_SUMMARY.md` as current truth.

Acceptance:

- There is one clear reading path for ArtDeco work.
- Active docs, runtime docs, component docs, history docs, and compatibility docs are not conflated.
- No document says `views/artdeco-pages/**` is the universal active route truth.
- `DESIGN.md` records real available visual assets and known legacy boundaries, not only ideal future standards.

### Workstream B: Page Design Standardization

Purpose: convert the refreshed `DESIGN.md` page standards into a concrete route review checklist that can drive `impeccable critique` without changing implementation code.

Tasks:

- B1. Create or update a page review checklist covering:
  - page shell
  - header band
  - control row
  - primary work area
  - secondary context
  - runtime states
  - token usage
  - A-share color semantics
  - keyboard and focus behavior
- B2. Map current route domains to page pattern families:
  - market and data: dense market state and chart/table workflow
  - watchlist: list management and signal triage
  - strategy: workflow and job-state pages
  - trade: terminal and execution workflow
  - risk: alert, PnL, stop-loss and position state
  - system: operational configuration and health
- B3. Identify route exceptions and wrappers before selecting each implementation target.

Acceptance:

- A reviewer can audit any target page against the same page grammar.
- Each page family has explicit runtime states and density expectations.
- The checklist can be used with `$impeccable critique`.

### Workstream C: Core Page Pilot Batch

Purpose: audit representative high-value pages and produce design briefs before broad rollout or implementation.

Pilot order:

| Priority | Target | Why This Page |
|---:|---|---|
| 1 | `web/frontend/src/views/market/Realtime.vue` | Tests real-time market density, filters, freshness, tables and possible chart state |
| 2 | `web/frontend/src/views/trade/Center.vue` | Tests task-critical trade workflow, one-primary-action rule and terminal density |
| 3 | `web/frontend/src/views/risk/Center.vue` | Tests risk severity, alerts, stale state and A-share semantic conflict handling |
| 4 | `web/frontend/src/views/system/Health.vue` | Tests quieter operational surfaces, backend state and diagnostic clarity |
| 5 | `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue` | Tests intentional dashboard exception and stronger ArtDeco overview register |

Per-page tasks:

- Cx.1. Run `$impeccable critique <target>` to inspect the currently implemented page before code changes.
- Cx.2. Record findings as page-specific report under `docs/reports/tasks/` or `docs/reports/quality/`.
- Cx.3. Run `$impeccable shape <target>` to produce the page design brief and implementation scope.
- Cx.4. Get explicit user approval before any `craft` or source-code implementation.
- Cx.5. After approval, run `$impeccable craft <target>` with a narrow implementation scope.
- Cx.6. Run `$impeccable audit <target>`.
- Cx.7. Run `$impeccable polish <target>`.
- Cx.8. Run `$impeccable extract <target>` only after a pattern has proven reusable.

Recommended narrow craft scope for `market/Realtime.vue`:

- page header band
- control row
- primary market table or chart work area
- stale, loading, error and degraded states
- tokenized cleanup in touched scope

Acceptance:

- Each pilot page demonstrates the page grammar without inventing one-off chrome.
- Touched visual values use ArtDeco tokens or documented exceptions.
- Each pilot page has loading, empty, stale, error or degraded state coverage appropriate to its workflow.
- No pilot page introduces side-stripe borders, gradient text, nested cards, default glassmorphism, or decorative motion.

### Workstream D: Component Reuse and Extraction

Purpose: avoid repeating page-level fixes across 250+ views and 180+ components.

Candidate reusable assets:

- `ArtDecoPageHeader`
- `ArtDecoControlBar`
- `ArtDecoStatusStrip`
- `ArtDecoDataPanel`
- `ArtDecoRuntimeState`
- `ArtDecoFreshnessBadge`
- `ArtDecoRouteWorkbench`
- `ArtDecoMetricRow`
- `ArtDecoDenseTableShell`

Tasks:

- D1. Compare candidates against `ARTDECO_COMPONENT_GUIDE.md` placement rules.
- D2. Do not extract until two pilot pages need the same pattern.
- D3. Prefer existing components first:
  - `ArtDecoButton`
  - `ArtDecoBadge`
  - `ArtDecoStatus`
  - `ArtDecoHeader`
  - `ArtDecoKLineChartContainer`
  - `PerformanceTable`
  - `ArtDecoFilterBar`
  - `ArtDecoDateRange`
- D4. If extraction affects shared layout or multiple domains, assess whether OpenSpec is required before implementation.

Acceptance:

- Extracted components live in the correct directory by reuse boundary.
- No domain-specific page state is hidden inside `base`, `core`, or `business` components.
- Shared runtime state goes into `src/composables/**` only when there are 2+ real consumers.
- Extraction should move the project from one successful page to a reusable Web page standard.

### Workstream E: Token and Style Governance

Purpose: reduce visual drift and hard-coded styling in touched scope.

Tasks:

- E1. Treat `web/frontend/src/styles/artdeco-tokens.scss` as primary token truth.
- E2. For each touched Vue/SCSS file, replace newly touched hard-coded colors with `--ad-*` tokens where practical.
- E3. Do not migrate entire legacy files unless the task explicitly authorizes it.
- E4. Keep chart palette exceptions documented and local to chart configuration.
- E5. Run ArtDeco lint gates after visual changes.

Acceptance:

- `npm run lint:artdeco` or targeted changed-file ArtDeco lint is reported for implementation tasks.
- New hard-coded visual values are absent or justified.
- Component state tokens are used for hover, focus, active, disabled, selected, loading, error, warning and success.

### Workstream F: Verification and Quality Gates

Purpose: keep visual improvements aligned with project quality gates.

Required verification for frontend implementation tasks:

- Structural syntax errors: must be 0.
- Type errors: compare against `reports/analysis/tech-debt-baseline.json` and distinguish existing debt from new regressions.
- PM2 services: confirm `mystocks-backend` at `http://localhost:8020` and `mystocks-frontend` at `http://localhost:3020` when the task involves build, type check, E2E or service startup.
- E2E: report actual command, browser project, pass/fail/skip counts and whether it is full suite or smoke subset.
- Visual verification: use Playwright screenshots for crafted or polished pages where practical.
- Accessibility: verify focus states, color contrast and reduced-motion behavior in touched scope.

Recommended command set per implementation slice:

```bash
cd web/frontend
npm run lint:artdeco
npm run type-check
npm run test:e2e:business-smoke
```

Adjust the command set to the actual touched scope and current baseline.

## 7. Proposed Milestones

### Milestone 1: Document and Audit Baseline

Deliverables:

- This task plan
- `$impeccable document` result, including current token, style-layer and legacy-boundary findings
- Validated `DESIGN.md` facts or follow-up documentation findings
- Page review checklist
- First critique report for `market/Realtime.vue`

Exit criteria:

- `DESIGN.md` reflects real visual assets and legacy boundaries well enough to guide route work
- Pilot target confirmed
- Findings are tied to ArtDeco source docs and current route truth

### Milestone 2: Market Realtime Pilot

Deliverables:

- Confirmed shape brief for `market/Realtime.vue`
- Approved implementation scope
- Crafted page improvements after approval
- Audit and polish notes after implementation

Exit criteria:

- Page grammar is visible in the implementation
- Runtime states are covered
- ArtDeco token usage is improved in touched scope

### Milestone 3: Trade and Risk Expansion

Deliverables:

- Critique and shape briefs for `trade/Center.vue` and `risk/Center.vue`
- Narrow craft tasks for the highest-value fixes

Exit criteria:

- One-primary-action rule is visible in trade workflow
- Risk severity hierarchy is clearer than decorative gold treatment

### Milestone 4: System and Dashboard Alignment

Deliverables:

- `system/Health.vue` operational-state pass
- `ArtDecoDashboard.vue` exception-aware overview pass

Exit criteria:

- Quiet operational surfaces and stronger overview surfaces are both aligned with `DESIGN.md`
- Dashboard exception remains documented and does not blur route truth

### Milestone 5: Extraction and Governance Closeout

Deliverables:

- Extracted reusable components only where proven by 2+ pages
- Updated ArtDeco component catalog or guide entries if needed
- Final verification report

Exit criteria:

- Reusable assets are in correct directories
- Future page work has a clear pattern library and checklist

## 8. Immediate Next Actions

1. Run:

```text
$impeccable document
```

2. Compare the resulting `DESIGN.md` and documentation findings against:

```text
docs/guides/web/ARTDECO_MASTER_INDEX.md
docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md
web/frontend/ARTDECO_COMPONENTS_CATALOG.md
docs/api/ArtDeco_System_Architecture_Summary.md
docs/guides/web/ARTDECO_COMPONENT_GUIDE.md
docs/reports/ARTDECO_V3_COMPLETE_SUMMARY.md
docs/guides/ARTDECO_FINTECH_UNIFIED_SPEC.md
docs/api/ARTDECO_SYSTEM_ARCHITECTURE_SUMMARY.md
```

3. Run:

```text
$impeccable critique web/frontend/src/views/market/Realtime.vue
```

4. Save critique findings as:

```text
docs/reports/tasks/2026-05-28-artdeco-market-realtime-critique.md
```

5. Convert accepted critique findings into:

```text
$impeccable shape web/frontend/src/views/market/Realtime.vue
```

6. Treat the `shape` output as the design document for approval.

7. Wait for explicit user approval of the design documents and shape brief before any `craft` implementation, source-code edit, token rewrite or component extraction.

## 9. Open Decisions

- Should the first pilot page be `market/Realtime.vue`, or should the project start with `ArtDecoDashboard.vue` because it is the visible ArtDeco overview route?
- Should `$impeccable document` update `DESIGN.md` in place, or should it first produce a review report for approval?
- What exact approval wording should unlock implementation: `批准`, `同意实施`, or an explicit milestone approval comment?
- Should P0 or P1 ArtDeco document optimizations happen before the first pilot page, or only when a pilot finding proves the conflict?
- Should page review checklist live as a standalone guide under `docs/guides/web/`, or remain as a task artifact under `docs/reports/tasks/` until proven?
- Should future cross-domain page shell extraction be handled by OpenSpec before implementation?
- Should raw hex cleanup be opportunistic in touched files only, or tracked as a separate technical debt program?

## 10. Non-Goals and Guardrails

- Do not begin broad cosmetic changes without page-specific critique and shape approval.
- Do not implement frontend code from this plan until the design documents are approved.
- Do not extract new components from a single page unless there is a clear second consumer.
- Do not flatten the current ArtDeco document hierarchy into one file.
- Do not treat historical V3 documents as current implementation truth without re-verification.
- Do not make mobile support a design target.
- Do not use side-stripe borders, gradient text, nested cards, default glassmorphism, or decorative page-load animations.
