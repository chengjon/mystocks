# HTML5 Runtime Capability Guide

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

> **边界说明**:
> 本文档是 `docs/guides/frontend/` 下的 current-state supporting guide，用于记录当前前端 HTML5 runtime capability 真相，不是仓库共享规则、OpenSpec 验收结论或部署完成证明。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 [`architecture/STANDARDS.md`](/opt/claude/mystocks_spec/architecture/STANDARDS.md)；若涉及任务完成状态，请回到对应 OpenSpec task 与验证结果核对。

> **当前状态说明**:
> 本文档记录 `implement-html5-migration-experience-optimization` 在线仓库中的 HTML5 runtime capability 真相，包括 PWA runtime surface、IndexedDB 使用面和 Web Workers 当前接线。
> 它是 current-state supporting guide，不等于“PWA/离线/性能目标已全部验收通过”的证明。

## Scope

本文只回答三个问题：

1. 当前前端 runtime 里，哪些 HTML5 能力已经有真实代码入口。
2. 这些能力现在由哪些文件承载、被哪些活跃模块消费。
3. 哪些能力仍然只是部分落地，不能被误写成“已完整闭合”。

## 1. Canonical Runtime Entry

- 当前浏览器入口是 [index.html](/opt/claude/mystocks_spec/web/frontend/index.html)，加载：
  - `/src/main-standard.ts`
- 当前活跃运行时入口是 [main-standard.ts](/opt/claude/mystocks_spec/web/frontend/src/main-standard.ts)。
- `src/_entry-archive/` 下的 `main.js`、`main-debug.js`、`main-original.js` 等变体属于保留档案，不是当前 runtime entry。

## 2. PWA Runtime Surface

### 2.1 Current Wiring

- [index.html](/opt/claude/mystocks_spec/web/frontend/index.html)
  - 已接入 `manifest.json`
  - 已配置 `theme-color`、Apple mobile web app meta、touch icon 和 `msapplication` meta
- [main-standard.ts](/opt/claude/mystocks_spec/web/frontend/src/main-standard.ts)
  - 在 `window.load` 后手动注册 `/sw.js`
  - 在检测到 `controllerchange` 时触发页面刷新
- [manifest.json](/opt/claude/mystocks_spec/web/frontend/public/manifest.json)
  - 已声明 `name`、`short_name`、`display`、`theme_color`、`icons`、`shortcuts`
- [sw.js](/opt/claude/mystocks_spec/web/frontend/public/sw.js)
  - 已实现静态资源缓存
  - API 采用 network-first + cache fallback
  - 字体与静态资源采用 cache-first
  - 导航请求带离线 fallback

### 2.2 Current Boundaries

- [vite.config.mts](/opt/claude/mystocks_spec/web/frontend/vite.config.mts) 中 `vite-plugin-pwa` 仍然处于注释禁用状态。
- 因此当前 PWA 是“手动 manifest + 手动 service worker 注册”模式，不是插件托管的完整构建链路。
- `manifest.json` 引用的截图资源当前并不完整：
  - `public/screenshots/dashboard.png` 不存在
  - `public/screenshots/analysis.png` 不存在
- 所以本 guide 不能被解读成：
  - `2.1.2 Add PWA icons and splash screens` 已完成
  - `3.2.x` 的离线 / 跨浏览器 PWA 验证已完成

### 2.3 Testing Caveat

- 多个 Playwright spec 当前显式使用 `serviceWorkers: 'block'`。
- 这意味着仓库里的 Chromium 绿灯，不能自动等价为“PWA 离线能力已验收”。
- 当前 full Chromium 基线主要证明的是页面交互稳定，不是 service worker 安装 / 离线缓存全闭环。

## 3. IndexedDB Runtime Surface

### 3.1 Canonical Implementation

- 当前 IndexedDB wrapper 是 [indexedDB.ts](/opt/claude/mystocks_spec/web/frontend/src/utils/indexedDB.ts)
- 对外暴露 singleton：
  - `indexedDBManager`
  - `indexedDB`

### 3.2 Data Model

当前 object stores 包括：

- `market_data`
- `technical_indicators`
- `user_preferences`
- `api_cache`

当前实现已覆盖：

- 初始化与 schema 创建
- Market data CRUD
- Technical indicator persistence
- User preferences persistence
- API cache 读写与 TTL

### 3.3 Active Consumer

- 当前活跃消费点是 [marketData.ts](/opt/claude/mystocks_spec/web/frontend/src/stores/marketData.ts)
- 该 store 当前实际使用 IndexedDB 做：
  - `market_overview` 缓存
  - `market_analysis` 缓存
  - 个股 market data 持久化
  - technical indicator 结果缓存与持久化

### 3.4 Validation Surface

- 当前直接单测入口是 [indexedDB.spec.ts](/opt/claude/mystocks_spec/web/frontend/tests/unit/utils/indexedDB.spec.ts)
- 这能证明 wrapper 与主要 API surface 存在 repo-local 验证，但不等于 IndexedDB 迁移、升级、跨浏览器持久化全部完成。

## 4. Web Workers Runtime Surface

### 4.1 Canonical Files

- 协议层：[protocol.ts](/opt/claude/mystocks_spec/web/frontend/src/workers/protocol.ts)
- 指标 worker：[indicatorDataWorker.worker.ts](/opt/claude/mystocks_spec/web/frontend/src/workers/indicatorDataWorker.worker.ts)
- 管理器实现：[workers-manager.ts](/opt/claude/mystocks_spec/web/frontend/src/utils/workersManager/workers-manager.ts)
- 兼容导出 shim：[workersManager.ts](/opt/claude/mystocks_spec/web/frontend/src/utils/workersManager.ts)

### 4.2 Current Capability

- `protocol.ts` 已定义标准消息类型、优先级、响应结构和消息队列工具。
- `indicatorDataWorker.worker.ts` 已实现技术指标计算 worker，包括：
  - `MA`
  - `EMA`
  - `BOLL`
  - `MACD`
  - `RSI`
  - `KDJ`
- `marketData.ts` 当前通过 `workersManager.calculateIndicator()` 调用该能力路径。

### 4.3 Current Limitation

- [workers-manager.ts](/opt/claude/mystocks_spec/web/frontend/src/utils/workersManager/workers-manager.ts) 当前仍是轻量 façade。
- 文件内注释和实现都表明：
  - 当前 `calculateIndicator()` 返回的是 placeholder 风格管理层结果
  - 健康状态也是简化版
- 因此当前 repo-truth 应理解为：
  - Web Worker protocol / worker file / manager surface 已存在
  - 活跃 store 已接入该表面
  - 但它还不是完整的多 worker orchestration / 深度健康治理平台

## 5. Practical Developer Guidance

- 讨论当前 HTML5 runtime 能力时，优先引用本文档与实际代码，不再默认引用历史总结。
- 讨论“是否已经完成 PWA / 离线 / 安装 / 跨浏览器验收”时，必须回到 OpenSpec `2.1.x / 3.2.x / 3.3.x` 的未闭合任务，不能用本文替代验收记录。
- 若要继续推进 HTML5 迁移线，优先按低风险 repo-local truth 收口；涉及完整 PWA 构建链、跨浏览器离线验证或生产部署支持时，必须单独按对应 task 推进。
