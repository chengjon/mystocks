# 新增页面开发指引（MyStocks Frontend）

> 版本：1.0 | 更新：2026-09-26
> 适用范围：`web/frontend/` 下新增业务页面
> 优先级：本文档遵守项目的 **PROJECT CLAUDE.md / architecture/STANDARDS.md** 所有红线；冲突时以两者为准。

---

## 0. 前置：先确认「是否需要新增页面」

本项目**已有 8 大业务域、约 48 个业务页面 + 2 个系统页**。因历史积累，仓库中存在大量 demo / 测试 / 废弃页面（`views/` 下的 `*Demo.vue`、`converted.archive`、`*.backup` 等），**新增需求前必须先做「现有能力盘点」**：

1. 检索 `web/frontend/src/views/`、`router/`、`layouts/` 是否存在相似页面（禁止未检索直接新建，避免重复造轮子）
2. 检索后端 `web/backend/app/api/` 是否存在可复用接口（`grep` / GitNexus `query` 均可）
3. 只有「现有实现确实不满足需求」时才进入本流程

> ⚠️ 清理 / 删除判定标准（强制）：「未引用 / 未使用」不等于「可删除」。删除任何文件、组件、路由前必须同时通过「代码路径判定」+「功能树判定」，且状态明确为「重复冗余」或「正式下线」才允许。

---

## 1. 需求与门禁

| 场景 | 流程 |
|---|---|
| 新增**能力 / 新接口 / 架构级变更**（含可能改 API 契约） | **先走 OpenSpec**：`openspec proposal` 创建 `change-id`（kebab-case、动词开头如 `add-*`），写 delta spec，`openspec validate --strict`，**approval 后才能实现** |
| 普通业务页面（复用现有 API、不改契约） | 本文档流程即可，但提交需关联 PR |

- **开发分支纪律**：功能在 `worktree / dev-*` 分支开发，通过 PR 合回 `main`；`main` 不直接承载功能提交。合并前需通过质量门（TS/Python/tests）、安全门、审查门。
- **影响面检查**：修改任何前端符号前 `gitnexus_impact`；提交前 `gitnexus_detect_changes` 校验改动范围。

---

## 2. 页面骨架分工（4 部分，缺一页面不可达/不可见）

新页面完整落地需要 4 处改动，缺一不可：

| # | 位置 | 作用 | 不做会怎样 |
|---|---|---|---|
| 1 | `views/` 下的 `.vue` 页面 + `styles/` SCSS | 页面本身 | 无内容可渲染 |
| 2 | `router/index.ts` 注册路由 `+ name + meta` | URL 直达、深链接 | 只能靠菜单点击、无法直接访问 |
| 3 | `layouts/MenuConfig.ts` 注册菜单项 | 侧边栏导航可见 | 页面「可达但不可见」 |
| 4 | （有「组内 tab 子页」时）挂到父布局/父页面的 tab 容器 | 组内切换 | 无法通过组内 tab 跳转 |

---

## 3. 第一步：创建页面组件

### 3.1 文件位置

```
web/frontend/src/views/
├── artdeco-pages/            # ArtDeco 主域页面（7 大业务域）
│   ├── ArtDecoDashboard.vue
│   ├── strategy-tabs/        # 策略组内子页（tab 容器 + 子页）
│   ├── trading-tabs/
│   ├── portfolio-tabs/
│   ├── risk-tabs/
│   └── system-tabs/
├── data/                     # 数据分析组
├── market/                   # 市场行情组
└── ...                       # 其余按域分目录
```

- 一律放在 `@/views/` 下的**对应业务域目录**（`@` 别名 = `src`）
- 组件级样式放**同级 `styles/` 子目录**（必选）

```
views/<domain>/MyNewPage.vue
views/<domain>/styles/MyNewPage.scss
```

### 3.2 组件骨架（Script Setup + Composition）

```vue
<template>
  <div class="my-new-page">
    <span class="my-new-page__title">{{ title }}</span>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useApiClient } from '@/services/apiClient'   // 参照项目现有 service 模式

const title = ref('')
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    // 复用统一 API 层，禁止 in-component 裸 fetch
  } finally {
    loading.value = false
  }
})
</script>

<style lang="scss" scoped>
@import './styles/MyNewPage.scss';
</style>
```

### 3.3 样式强制规范（CSS/SCSS 红线）

| 规则 | 约束 |
|---|---|
| `<style>` 块**仅含一行 `@import`** | 禁止直接写 CSS、禁止内联 `style=""`、禁止裸 `:style`（唯一例外是传 CSS 变量值） |
| **必须 `scoped`**；组件样式放 `styles/` 目录 | 新建组件若不建 `styles/` 目录 → CR 不通过 |
| **变量化（强制）** | **禁止硬编码色值 / 字号 / 间距**；一律使用设计令牌 `var(--artdeco-*)` / `var(--spacing-*)` / `var(--font-size-*)` 等 |
| **类名 BEM 风格** | 块 + `-修饰` 状态（如 `card--active`、`capital-flow__header`）；禁止裸短类名、避免全局污染 |
| SCSS **嵌套 ≤ 3 层** | `.a { .b { .c {} } }` 为上限，超出提取为独立类 |
| 单个 SCSS 文件 **≤ 500 行** | 超过拆 `_variables.scss` / `_mixins.scss` / `_layout.scss` |
| 单个 `.vue` **≤ 800 行**（本项目红线）；前端 TS **≤ 500 行** | 超过必须拆分（提取 SCSS / 拆 composables） |
| **仅桌面端**，最小 1280×720 | 禁止任何 `@media (max-width: ...)` 响应式规则 |
| 提交前 | `cd web/frontend && npx stylelint "src/**/*.{vue,scss,css}"` **零错误** |

样式引用唯一允许写法：

```vue
<style lang="scss" scoped>
@import './styles/MyNewPage.scss';
</style>
```

动态样式只用 **类名切换 / CSS 变量**，不使用内联：

```vue
<div :class="['card', { 'card--active': isActive }]"></div>
<div class="chart" :style="{ '--chart-height': h + 'px' }"></div>
```

```scss
// styles/MyNewPage.scss — 正确示例
.card {
  background: var(--artdeco-bg-card);
  color: var(--artdeco-fg-primary);
  border: 1px solid var(--artdeco-border-default);
  padding: var(--spacing-md);

  &--active {
    border-color: var(--artdeco-gold-primary);
    box-shadow: 0 0 12px var(--artdeco-gold-opacity-shadow);
  }
}
```

### 3.4 组件体积与拆分参考

- 可复用块（Header / KPI 条 / 表格 / tab 内容）拆成 `components/` 子组件
- 复杂逻辑拆到独立 ViewModel（参照 `strategy-tabs/.../backtestAnalysisViewModel.ts`）
- 优先复用 `@/components/artdeco/` 打包的 `ArtDecoButton / ArtDecoCard / ArtDecoTable / ArtDecoStatCard` 等（`index.ts` barrel 统一导出）

### 3.5 ArtDeco 设计语言（业务页面强制）

7 大业务域页面**必须保持 ArtDeco 风格**——路由 `meta.layout: 'ArtDeco'`、渲染在 `ArtDecoLayoutEnhanced.vue` 下（自动获得侧边栏 + 金色主题）。游离于 ArtDeco 布局之外的页面视为不规范。

**① 设计令牌（SSOT）**

| 构建 | 位置 | 说明 |
|---|---|---|
| ArtDeco 令牌（主） | `src/styles/artdeco-tokens.scss` | `ART DECO DESIGN TOKENS V3.0`：深黑（Obsidian）+ 金色强调「Gatsby 美学」 |
| 通用令牌（fallback） | `src/styles/design-tokens.scss` | `--color-*` / `--spacing-*` / `--font-*` / `--radius-*` / `--shadow-*` |
| 全局入口 | `src/styles/index.scss` | 统一导入所有全局 SCSS |

核心令牌速查：

| 令牌 | 值（示例） | 用途 |
|---|---|---|
| `--artdeco-bg-global` | `#0A0A0A` | 页底背景（最深黑） |
| `--artdeco-bg-base` / `-card` / `-elevated` | `#141414` / `#141414` / `#1a1a1a` | 表面 / 卡片 / 提升 |
| `--artdeco-fg-primary` | `#F2F0E4` | 主文本（香槟奶油） |
| `--artdeco-fg-muted` | `#A0A0A0` | 次要文本（已调 WCAG AA） |
| `--artdeco-gold-primary` | `#D4AF37` | ▲ 主品牌金：按钮 / 强调 / 图标 / hero |
| `--artdeco-gold-light` / `-bronze` / `-champagne` | `#F0E68C` / `#CD7F32` / `#F7E7CE` | 高亮 / 次要强调 / 柔和背景 |
| `--artdeco-border-default` / `-hover` | gold 30% / gold 100% | 边框（透明 30% → hover 100%） |
| `--artdeco-gold-opacity-*` | rgb(212 175 55 / 5-30%) | 悬停背景 / 阴影 / 点缀 |
| **红涨绿跌** | 涨 `--val-up: #26a69a`（绿）跌 `--val-down: #ef5350`（红） | **A 股约定，勿用西方配色** |

**② 组件库（复用优先）** — `src/components/artdeco/`（入口 `index.ts`）

| 分组 | 组件 |
|---|---|
| `base/` | `ArtDecoButton` `ArtDecoCard` `ArtDecoCardCompact` `ArtDecoInput` `ArtDecoSelect` `ArtDecoStatCard` `ArtDecoAlert` `ArtDecoBadge` `ArtDecoProgress` `ArtDecoDialog` `ArtDecoSwitch` `ArtDecoCollapsible` `ArtDecoSkipLink` `ArtDecoLanguageSwitcher` |
| `core/` | `ArtDecoHeader` `ArtDecoFooter` `ArtDecoBreadcrumb` `ArtDecoIcon` `ArtDecoLoading` `ArtDecoLoadingOverlay` `ArtDecoSkeleton` `ArtDecoStatusIndicator` `ArtDecoToast` `ArtDecoFunctionTree` `ArtDecoAnalysisDashboard` `ArtDecoTechnicalAnalysis` `ArtDecoFundamentalAnalysis` `ArtDecoRadarAnalysis` |
| `advanced/` | `ArtDecoMarketPanorama` `ArtDecoCapitalFlow` `ArtDecoChipDistribution` `ArtDecoTradingSignals` `ArtDecoAnomalyTracking` `ArtDecoFinancialValuation` `ArtDecoSentimentAnalysis` `ArtDecoBatchAnalysisView` `ArtDecoDecisionModels` 等 |
| `charts/` | `ArtDecoChart` `ArtDecoKLineChartContainer` `TimeSeriesChart` `CorrelationMatrix` `HeatmapCard` `DepthChart` `DrawdownChart` `PerformanceTable` `ArtDecoRomanNumeral` |
| `business/` | `ArtDecoAlertRule` `ArtDecoBacktestConfig` `ArtDecoButtonGroup` `ArtDecoCodeEditor` `ArtDecoDataSourceTable` `ArtDecoDateRange` `ArtDecoFilterBar` `ArtDecoInfoCard` `ArtDecoSlider` `ArtDecoStatus` 等 |
| `trading/` | **`ArtDecoTable`（表格通用）** `ArtDecoOrderBook` `ArtDecoPositionCard` `ArtDecoRiskGauge` `ArtDecoStrategyCard` `ArtDecoTicker` `ArtDecoTickerList` `ArtDecoTradeForm` `ArtDecoSidebar` `ArtDecoTopBar` 等 |
| `specialized/` | `ArtDecoBlockTrading` `ArtDecoLongHuBang` 等 |

> 表格：项目通用表格组件是 **`ArtDecoTable`（在 `trading/` 分组，barrel `index.ts` 统一导出）**，用法 `:data` + `:columns`。视图页已大量使用（如 `RiskOverviewTab.vue`、`WatchlistManager.vue`），新页面不要自研表格。`advanced/` 组件按需直接路径导入，避免顶层 barrel 被历史断链拖垮（见 `index.ts` 注释）。

写页面时**先搜 `@/components/artdeco/*` 再动手**；不够再手写，且手写部分必须套用令牌 + 组件样式规范（§3.3）。

**③ 风格要点**

- 深色底 + 金色强调 + 几何装饰（Gatsby / Art Deco 特征）；卡片块用 `border: 1px solid var(--artdeco-border-default)` + `background: var(--artdeco-bg-card)`
- 章节标题、KPI、按钮等视觉强调元素用 `var(--artdeco-gold-primary)`（V3.0 要求「大胆使用金色作为核心品牌元素」）
- 涨跌色使用 ArtDeco 金融色令牌（红涨绿跌），不要引入自定义色板
- 参照页：`views/artdeco-pages/ArtDecoDashboard.vue`、`ArtDecoRiskManagement.vue`（布局/卡片/shell 结构即最佳模板）

---

## 4. 第二步：注册路由

文件：`web/frontend/src/router/index.ts`

### 4.1 找到所属业务域 group；模式参考

```ts
// 域 = 一个带 children 的 group（如 /strategy），子页各自注册为 children
{
  path: '/strategy',
  meta: { title: '策略管理', group: 'strategy' },
  children: [
    {
      path: 'backtest',
      name: 'strategy-backtest',
      component: () => import('@/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue'),
      meta: { title: '回测引擎', requiresAuth: true, api: '/api/v1/...' }
    }
    // ... 新增页在这里加一项
  ]
}
```

### 4.2 新增子页面的最小记录

```ts
{
  path: 'my-new-page',                 // 相对当前 group 的 path（最终 URL = /<group>/my-new-page）
  name: 'group-my-new-page',           // 强制唯一；命名规范 = 「组名-页面名」
  component: () => import('@/views/<domain>/MyNewPage.vue'),
  meta: {
    title: '我的新页面',                // 必填：标题（侧栏/title 使用）
    requiresAuth: true,                // 缺省即 true；公用页才显式 false
    icon: 'SomeIcon',                  // 可选：菜单图标 key
    api: '/api/v1/...',                // 可选：页面主数据接口（用于按页展示）
    group: 'strategy'                  // 可选：所属域，深链/history 恢复用
  }
}
```

### 4.3 规则要点

- **`name` 全局唯一**：按 `业务域-页面` 命名（`market-realtime`、`strategy-backtest`…），不要用页面标题做 name
- 懒加载 `component: () => import('@/...')`：新页面使用 lazy import，禁止同步 import
- **`requiresAuth` 默认 true**：`authGuard` 用 `to.meta.requiresAuth !== false` 判断，未登录跳 `/login?redirect=...`
- 带参数的详情页模式参考：`stock-detail/:symbol`（group `detail`，child `graphics/:symbol`、`news/:symbol`）
- **禁止在 `main.ts` / 组件内硬编码新路由**；统一走 `index.ts`
- 后端新 API 同理：必须在 `web/backend/app/api/VERSION_MAPPING.py` 注册（`prefix + endpoints`），严禁在 `main.py` 硬编码前缀

---

## 5. 第三步：注册菜单（侧边栏可见性）

文件：`web/frontend/src/layouts/MenuConfig.ts`（**导航 SSOT，单一真实源**）

### 5.1 结构

```ts
// 1. 业务域：一个 MenuItem，含 children
const STRATEGY_DOMAIN: MenuItem = {
  path: '/strategy',
  label: '策略管理',
  icon: ARTDECO_ICONS.STRATEGY,
  businessKey: 'domain.strategy',
  children: [
    { path: '/strategy/backtest', label: '回测引擎', icon: ARTDECO_ICONS.BACKTEST, businessKey: 'strategy.backtest' },
    // 新增项加在这里
  ],
}

// 2. 把域加进导出数组
export const ARTDECO_MENU_ITEMS: MenuItem[] = [
  MARKET_DOMAIN, DATA_DOMAIN, WATCHLIST_DOMAIN,
  STRATEGY_DOMAIN, TRADE_DOMAIN, RISK_DOMAIN, SYSTEM_DOMAIN,
]
```

### 5.2 字段说明（`MenuItem`）

| 字段 | 必填 | 说明 |
|---|---|---|
| `path` | ✅ | **绝对路径**（如 `/strategy/backtest`），与路由一致 |
| `label` | ✅ | 侧边栏显示名 |
| `icon` | ✅ | 图标 key（`ARTDECO_ICONS` 常量或字符串，用已存在 icon；新 icon 需在图标库有实现） |
| `businessKey` | ✅ | 全局唯一业务键（`域.项`，如 `strategy.backtest`）；**重复会破坏导航高亮/权限映射** |
| `badge` | 可选 | 角标（如 `'LIVE'`、数字） |
| `featured` | 可选 | 标记重点域 |
| `apiEndpoint / apiMethod / apiParams / wsChannel / liveUpdate` | 可选 | API / WebSocket 配置（与 router `meta.api` 互相独立） |

- 若新增「页」但不挂菜单（如立足 tab 内嵌的子页），可在 `MenuConfig.ts` 顶部注释说明，避免遗漏

---

## 6. 第四步：挂入组内 tab（如需）

当新增的是「某域内的子页面」而非「新域」时，通常还需把该页作为 tab 挂进父页面的 tab 容器：

```
src/views/artdeco-pages/strategy-tabs/    # 策略域 7 页均为独立 tab 页
src/views/artdeco-pages/trading-tabs/     # 交易域 5 页
src/views/artdeco-pages/risk-tabs/        # 风险域子页
src/views/artdeco-pages/system-tabs/
```

参照现有实现：父页面（如 `ArtDecoStrategyManagement.vue`）用 tab 组件 `<el-tabs>`/ArtDeco tab，`router-link` 或 `<router-view>` 渲染子页。新增子页 = 路由 children + 在父 tab 容器加一项。

---

## 7. 前端 TS / Vue 编码规范（新增代码强制）

| 规范 | 要求 |
|---|---|
| 模块系统 | 使用 ES modules；**本地导入必须带扩展名**（如 `./styles/X.scss`、`../api/client.ts`）；第三方包保持包名 |
| 导入顺序 | 三方包 → 别名/本地模块 → 样式文件；同组稳定排序 |
| 函数形式 | 顶层纯工具/服务函数用 `function`；回调/闭包用箭头函数；composables/`defineStore` 用 `const xxx = () =>` |
| 类型标注 | `api/`、`services/`、`utils/` 导出函数**必须显式标注返回类型**；优先显式类型/接口/泛型/`unknown`，**禁止新增裸 `any`** |
| 组合式 API | 默认 `<script setup lang="ts">` |
| API 调用 | 统一走项目 service/api 层，参照现有 `services/`、`api/` 模式；禁止页面内散落裸 fetch |

---

## 8. 数据访问与后端

### 8.1 数据网关（强制）

所有行情/财务等证券数据**必须经 OpenStock 数据网关**（`http://192.168.123.104:8040`）获取：
- **禁止**在新代码直接 `import` akshare / baostock / tushare / byapi / efinance
- 覆盖盲区（futures / options / execution 等）先报告用户再决定
- 若前端需要新数据接口 → 遵循 `docs/guides/NEW_API_SOURCE_INTEGRATION_GUIDE.md`

### 8.2 新后端 API（如需要）

- 必须在 `web/backend/app/api/VERSION_MAPPING.py` 登记 `prefix + endpoints`（SSOT），禁止 `main.py` 硬编码前缀
- 路由前缀规范：统一 `/api/v{版本}/{域}`；版本升级用 `market_v2` 式新组，不改旧前缀

### 8.3 API 契约（响应信封 / 错误码 / 请求规范）

> 新页面调接口必须遵守本项目**统一响应信封**；未经批准不得返回/消费旧格式。

**① 响应信封 — 唯一权威定义**

| 角色 | 文件 |
|---|---|
| 后端 SSOT | `web/backend/app/core/responses.py` → `UnifiedResponse`（第 35-50 行） |
| 前端镜像类型 | `web/frontend/src/types/unified-api.ts` → `UnifiedResponse<T>`（逐字段对齐） |

```jsonc
{
  "success": true,        // false 时为失败
  "code": 200,            // 业务码：200 成功
  "message": "操作成功",
  "data": { },            // 业务负载；失败时为 null
  "timestamp": "2026-09-26T08:00:00Z",  // UTC
  "request_id": "uuid",   // 日志追踪
  "errors": null          // 仅失败时存在：[{field, code, message}]
}
```

- 成功：`success:true`、`code:200`、负载放 `data`
- 失败：`success:false`、`errors:[{field, code, message}]`、`data:null`
- 分页必须用 `PaginatedResponse`（前端 `UnifiedPaginatedResponse<T>`）：`data` + `pagination:{page, page_size, total, ...}`
- 旧 `APIResponse` / `ErrorResponse` 已标 **`@deprecated`**；新页面/新接口一律用 `UnifiedResponse`
- 页面调用：统一走 `src/api/request.ts`（axios 拦截器已解信封并处理错误提示），消费 `data` 即可，无需手动解 `code`

**② 错误码规范（`code` 字段语义，按模块千位分组）**

权威来源：`web/backend/app/core/error_codes.py` + `docs/api/error-codes.md`

| dossier HTTP | 业务码 | 含义 |
|---|---|---|
| 200 | 0 / 200 | 成功 |
| 400 | 400 | 请求参数错误（1xxx 认证 / 2xxx 市场 / 3xxx 策略…） |
| 401 | 401 | 未认证 |
| 403 | 403 | 权限不足 |
| 404 | 404 | 资源不存在 |
| 422 | 422 | 数据验证错误 |
| 429 | 429 | 请求过于频繁 |
| 500 | 500 | 服务器内部错误 |

- JS：HTTP 状态表达协议语义，`code` 表达具体业务错误，`message` 面向终端用户（中文）
- 后端实现：`ErrorCode` 枚举 + `get_http_status()` + `create_error_response(...)` + 全局异常处理器（`app.core.exception_handler`，自动携带 `request_id`）
- ❌ 禁止回归旧混用格式（如 `return {"success": true, "msg": "OK"}`）——见 `docs/api/API_RESPONSE_UNIFICATION_REPORT_2025-12-03.md`

**③ 请求与路由契约**

- BASE URL：`web/frontend/src/config/runtime-endpoints.ts` 的 `API_BASE_URL`（经 vite proxy / runtime 注入，前端代码不写死后端 URL + 端口）
- 认证：session cookie（`request.ts` `withCredentials:true`）；CSRF 由拦截器对非 GET 请求自动附加 `X-CSRF-Token`，页面新增写接口无需自行处理
- 路径：所有新接口先在 `VERSION_MAPPING.py` 登记（见 §8.2），前缀 `/api/v{n}/{域}`
- 状态上报：路由 `meta.api` 填主数据接口路径；详情/子页用带参路由（`stock-detail/:symbol` 模式）与 `query` 传参，禁止页面自行拼接后端 URL

**④ 官方接口文档来源**

| 来源 | 位置 |
|---|---|
| Swagger UI（运行时） | `http://localhost:8020/docs`（后端 `BACKEND_PORT`） |
| OpenAPI 静态归档 | `docs/api/openapi/` + `docs/api/openapi.json` / `openapi.yaml`（akshare 版 `openapi_akshare.yaml`） |
| 错误码表 | `docs/api/error-codes.md` |
| 契约专项 | `docs/api/API_CONTRACT_ARCHITECTURE_ANALYSIS.md`、`docs/api/contracts/`、`CONTRACT_MANAGEMENT_API.md`、`CONTRACT_TESTING_API.md` |
| 集成指南 | `docs/guides/NEW_API_SOURCE_INTEGRATION_GUIDE.md` |

---

## 9. 提交前验证清单（Checklist）

在 `web/frontend` 下执行：

```bash
# 1) 风格检查（必须零错误）
npx stylelint "src/**/*.{vue,scss,css}"

# 2) TS / Vue 类型与编译
npx vue-tsc --noEmit   # 或项目现有 typecheck 脚本

# 3) 功能验证
npm run dev -- --port "${FRONTEND_PORT}"   # 3020（备用 3021；QM 用 3030）
# 手动验证：直达 URL、菜单跳转、tab 切换、向后兼容深链

# 4) 单测（如涉及纯逻辑/ViewModel）
npx vitest run
```

- **端口纪律**：`FRONTEND_PORT`（3020）/ `FRONTEND_BACKUP_PORT`（3021）由 `.env` 注入，禁止运行时硬编码端口；前端服务只在 3020-3029 范围
- **提交前 `gitnexus_detect_changes()`** 确认改动范围仅预期文件
- **PR 必需**：在 `worktree/dev-*` 分支提交 → 合回 `main`；PR 描述附变更范围、验证命令与结果、风险与回滚说明
- **路线图关联**：若属已规划能力，PR 需附 `openspec.change_id` 且 `approval_status=approved`

---

## 10. 常用参照（照着抄最快）

| 参照物 | 用途 |
|---|---|
| `views/artdeco-pages/ArtDecoDashboard.vue` | 主域页面整体结构 + ArtDeco 风格模板 |
| `views/artdeco-pages/ArtDecoRiskManagement.vue` | 布局 / 卡片 / shell 结构模板 |
| `views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue` | 组内 tab 子页 + ViewModel 模式 |
| `views/artdeco-pages/strategy-tabs/components/BacktestHeader.vue` | 子组件拆分 |
| `layouts/MenuConfig.ts` | 菜单 SSOT 结构 |
| `router/index.ts`（strategy 域块） | 路由注册 + meta |
| `styles/artdeco-tokens.scss` | ArtDeco 设计令牌全量 |
| `components/artdeco/` | 组件库（base/core/business/charts/…） |
| `docs/guides/frontend/css-scss-development-guide.md` | CSS/SCSS 规范全文 |
| 已有 `services/`、`api/` 模块 | API 调用封装模式 |
| `src/types/unified-api.ts` | 统一响应信封类型 |