# /dashboard Page Report

日期: 2026-04-24
范围: 仅 `http://localhost:3020/dashboard`
审查方式: 按 `route-inventory`、`functional-audit`、`data-state-audit`、`visual-artdeco-audit`、`responsive-a11y-audit` 五个固定角色执行

## 1. Route Inventory

- Router truth: [web/frontend/src/router/index.ts](/opt/claude/mystocks_spec/web/frontend/src/router/index.ts:30)
- Route path: `/dashboard`
- Route layout: [web/frontend/src/layouts/ArtDecoLayoutEnhanced.vue](/opt/claude/mystocks_spec/web/frontend/src/layouts/ArtDecoLayoutEnhanced.vue:1)
- Canonical page file: [web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue:1)
- Shared state bridge: [web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts:23) -> [web/frontend/src/composables/useHeaderSummary.ts](/opt/claude/mystocks_spec/web/frontend/src/composables/useHeaderSummary.ts:1) -> `ArtDecoLayoutEnhanced`
- Shared dependencies:
  - `ArtDecoHeader`
  - `ArtDecoCard`
  - `ArtDecoChart`
  - `ArtDecoStatCard`
  - `ArtDecoCollapsible`
  - `ArtDecoLongHuBang`
  - `ArtDecoBlockTrading`
  - `dashboardService`
  - `marketService`
  - `mockWebSocket`

结论:
- `/dashboard` 是明确声明的 ArtDeco 例外路由，不是从 `artdeco-pages/**` 目录推断出来的。
- 页面级摘要通过共享桥接上提到 layout header，属于当前运行时真值链的一部分。

## 2. Audit Findings

### Blocking

- 无

### High

1. 页面可见内容与真实数据链路不一致。
位置: [ArtDecoDashboard.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue:300), [useArtDecoDashboard.ts](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts:100)
问题:
- 股票池表现使用内置 mock 股票列表。
- 压力测试默认带预置结果对象，页面首屏会误导为已有真实测算结果。
处理:
- 去除 mock 股票池展示，改为真实接口未接入时的明确 empty notice。
- 压力测试默认改为 `null`，仅在用户显式执行且数据链路就绪后生成结果。

2. 页面 trace 元信息与 layout header 摘要桥接不完整。
位置: [ArtDecoDashboard.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue:12), [useArtDecoDashboard.ts](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts:38), [dashboardService.ts](/opt/claude/mystocks_spec/web/frontend/src/api/services/dashboardService.ts:22)
问题:
- `REQ/TIME` 展示依赖的状态原先未返回。
- layout header 在真实数据未就绪时会先显示占位摘要。
处理:
- 在 dashboard composable 中新增 `lastRequestId` 与 `displayProcessTime` 管理。
- 让 dashboard service 透传 `request_id/process_time`。
- 仅在首批摘要真实数据到位后再更新 layout header。

3. 图表颜色违背 A 股红涨绿跌语义。
位置: [useArtDecoDashboard.chart-options.ts](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.chart-options.ts:5)
问题:
- dashboard 图表使用西方语义颜色。
处理:
- 统一改为 `#FF5252` 上涨 / `#00E676` 下跌。

### Medium

1. fund flow / industry 图块错误态盲区。
位置: [ArtDecoDashboard.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue:39), [ArtDecoDashboard.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue:265)
问题:
- 部分卡片失败后只剩空图或默认值，无明确反馈。
处理:
- 增加页面级告警条与卡片级错误提示。

2. 压力测试按钮缺少 disabled 反馈。
位置: [ArtDecoDashboard.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue:300), [ArtDecoDashboard.scss](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/styles/ArtDecoDashboard.scss:734)
处理:
- 在市场或资金流未就绪时禁用按钮，并展示对应文案。

3. 可访问性与小屏稳定性不足。
位置: [ArtDecoDashboard.scss](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/styles/ArtDecoDashboard.scss:440), [ArtDecoDashboard.scss](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/styles/ArtDecoDashboard.scss:796)
问题:
- 缺少 `focus-visible`
- 小屏下 tab rail、压力测试区和 meta 行节奏不稳
处理:
- 补充 focus ring
- 收口 1024 / 768 / 390 断点布局
- request meta bar 改为可换行

### Low

1. dashboard header summary 与页面 header 有轻微信息重叠。
说明:
- 当前属于设计选择，不影响功能；本次未做结构性调整，避免扩散到 layout。

## 3. Functional Audit

- Header summary refresh:
  - layout 级刷新按钮仍由共享 `useHeaderSummary` 驱动。
  - dashboard 页面 trace bar 新增 `SYNC: READY/UPDATING` 反馈。
- 快捷导航:
  - `/market`、`/watchlist`、`/data`、`/trade`、`/strategy`、`/risk` 保持可用。
- 页面操作:
  - `flowTabs`、`poolTabs` 均补 `type="button"`，避免表单上下文误提交。
  - 压力测试仅在关键数据可用时可执行。
- 可交互反馈:
  - 页面级错误告警
  - 卡片级错误态
  - disabled 按钮样式
  - focus-visible

## 4. Data-State Audit

- Loading:
  - 保留 skeleton 与 chart loading shell。
- Empty:
  - 股票池无真实接口时显示明确 empty notice，不再回退到 mock。
  - 压力测试默认无结果，等待用户主动执行。
- Error:
  - `market`、`fundFlow`、`industry` 均有可见错误反馈。
- Disabled:
  - 压力测试按钮在行情链路未就绪时禁用。
- Extreme data:
  - 图表颜色与涨跌卡片语义已对齐 A 股规范。
  - `marketSentiment` 在无有效 breadth 时保持中性 50。

## 5. Visual ArtDeco Audit

对照文档:
- [docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md](/opt/claude/mystocks_spec/docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md:1)
- [DESIGN.md](/opt/claude/mystocks_spec/DESIGN.md:1)
- [docs/api/ArtDeco_System_Architecture_Summary.md](/opt/claude/mystocks_spec/docs/api/ArtDeco_System_Architecture_Summary.md:1)

结论:
- 标题层级保持 ArtDeco display + 金色几何语法。
- header summary / meta / panorama / content grid 的节奏已收口。
- 图表配色改回 A 股金融语义。
- 所有新增样式仍走 ArtDeco token，未引入新的硬编码 spacing 断点。

重点检查项:
- header summary: 已补 trace 与刷新状态反馈，避免“静默刷新”。
- 卡片层级: `market-panorama` 与 `content-grid` 间距统一。
- 数据密度: 去掉误导性 mock 后，页面信息更接近真实运行态。
- 图表比例: 保持现有 200px / 300px 比例，不做跨页重构。

## 6. Responsive & A11y Audit

- 1440 / 1280:
  - 维持多列密度，无新增视觉溢出点。
- 1024:
  - `flow-section` 与 `stress-test-metrics` 收敛为单列。
- 768:
  - 页面内边距收口，压力测试操作区改竖排。
- 390:
  - meta 行换行，tab rail 可折行，标题行高收紧。
- Focus:
  - tab、导航卡、压力测试按钮已补 `focus-visible`。
- Click target:
  - 快捷导航卡仍保持整卡可点。

## 7. Fixed Items

- 去除 `/dashboard` 页面 mock 股票池展示。
- 去除压力测试预置结果，改为按需生成。
- 补齐 dashboard trace bar 的 request id / process time / sync state。
- 修复 layout header summary 在数据未就绪时的摘要桥接时机。
- 补齐 fund flow / industry 错误态可见反馈。
- 修复 dashboard 图表颜色为 A 股红涨绿跌。
- 补齐压力测试 disabled 态与文案反馈。
- 补齐 tab / 按钮 / 导航卡的 focus-visible。
- 收口 1024 / 768 / 390 下的单页布局节奏。

## 8. Validation

执行结果:
- `npx eslint src/views/artdeco-pages/ArtDecoDashboard.vue src/views/artdeco-pages/composables/useArtDecoDashboard.ts src/views/artdeco-pages/composables/useArtDecoDashboard.chart-options.ts src/api/services/dashboardService.ts`
  - 结果: 通过
- `npm run type-check`
  - 结果: 通过
- `npm run lint:artdeco:changed`
  - 结果: 通过
- `npx playwright test --config=tests/visual/config/visual.config.ts tests/visual/pages/dashboard.spec.ts --project=chromium --reporter=line --output=/tmp/dashboard-visual-results`
  - 结果: 6 passed / 0 failed / 0 skipped
- `curl -I http://localhost:3020/dashboard`
  - 结果: `200 OK`
- `curl http://localhost:8020/health/ready`
  - 结果: ready

状态确认:
- 结构性语法错误: `0`
- 本批次新增类型错误: `0`
- `mystocks-backend`: online, `http://localhost:8020`
- `mystocks-frontend`: online, `http://localhost:3020`

## 9. Remaining Risks

- 股票池真实接口仍未接入，本次只消除了 mock 误导，不替代后续能力建设。
- 本次 Playwright 执行的是 dashboard visual 子集，不是完整多断点手工回归矩阵。
- layout 级 header 信息结构未重构，本次仅修复 dashboard 对共享摘要的输入质量。
