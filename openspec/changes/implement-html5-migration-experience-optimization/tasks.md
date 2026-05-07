## Phase 1: Frontend Architecture Optimization (Based on HTML5 Migration Experience)

> **使用说明**:
> 本文件用于记录当前 OpenSpec 变更的执行清单、操作步骤或协作约束，帮助跟踪实施过程。
> 其中勾选状态、执行顺序和局部说明仅代表任务推进视角，不应脱离 proposal、design、正式 specs、`architecture/STANDARDS.md` 与实际验证结果单独解读为最终事实。

> **Repo-Truth 对齐注记（2026-04-27）**:
> 本清单已按当前仓库实现复核，仅对有直接本地证据的项勾选。历史报告、备份文件、目标值、外部环境/UAT/上线结果不视为“已完成”。
> 当前关键事实漂移：
> - 菜单当前 canonical 配置是 `MenuConfig.ts` 的 **7 个业务域**，不是提案中的 6 个功能域。
> - PWA 基础文件、Service Worker、IndexedDB、部分 Worker 能力已存在，但 `vite.config.mts` 中 `vite-plugin-pwa` 当前仍被禁用。
> - `manifest.json` 引用了 `screenshots/*` 与 `shortcut-*.png`，但对应静态资源当前未在 `public/` 下齐备。
> - `@ant-design/icons-vue` 依赖与业务导入仍存在，依赖统一未完成。
> - Worker 协调层存在占位实现，不能把“有文件/有接口”机械等同为“完整生产能力已闭环”。
> - 关键资源预加载与性能监控面板已有局部实现，但 WebSocket 优化、配额管理、Web Vitals 跟踪仍需区分“活跃主链路”与“示例/并行实现”。

### 1.1 菜单系统完整实现
> **局部事实说明（2026-04-27）**:
> 当前菜单系统的本地证据已经比较明确：
> - `web/frontend/src/layouts/MenuConfig.ts` 已将 Market / Data / Watchlist / Strategy / Trade / Risk / System 作为 7 个业务域固化为 SSOT
> - `web/frontend/src/router/index.ts` 存在与上述 7 域对齐的路由组
> - `web/frontend/src/stores/menuStore.ts` 与 `web/frontend/src/stores/preferenceStore.ts` 已提供展开状态与侧边栏折叠状态的本地持久化
> - `web/frontend/tests/e2e/critical/menu-navigation-fixed.spec.ts`、`web/frontend/tests/e2e/artdeco-config-integration.spec.ts`、`web/frontend/tests/e2e/phase1-mainline-matrix.spec.ts` ~ `phase3-mainline-matrix.spec.ts` 已覆盖部分菜单/关键路由运行链路
> - `web/frontend/tests/base-layout-integration.spec.ts`、`web/frontend/tests/menu-e2e.spec.js` 已验证折叠切换与响应式宽度变化
> 2026-05-07 repo-truth 更新：
> - `env PLAYWRIGHT_EXTERNAL_FRONTEND=1 npx playwright test --config playwright.config.js --project=chromium tests/e2e/artdeco-config-integration.spec.ts tests/e2e/critical/menu-navigation-fixed.spec.ts` 现已实测 `8 passed`
> - 其中 `artdeco-config-integration.spec.ts` 已覆盖 `routeChecks`（5 条关键路由壳）、`nestedRoutes`（4 条嵌套路由）与 `domainRouteChecks`（4 条域入口），route-level 验证数已超过 11
> - `menu-navigation-fixed.spec.ts` 进一步覆盖 dashboard shell、侧边栏菜单跳转到 `/market/realtime` 以及失败回退可用性
> - 当前活跃布局链路的状态持久化真相源已是 `ArtDecoLayoutEnhanced.vue` + `ArtDecoCollapsibleSidebar.vue` 配合 `src/stores/preferenceStore.ts`（`artdeco-preferences`）与 `src/stores/menuStore.ts`（`artdeco-menu-expanded`），而不是 legacy `BaseLayout.vue` 中带 TODO 的本地 `sidebarCollapsed` ref
> - `cd web/frontend && npm run test -- tests/unit/stores/preferenceStore.spec.ts tests/unit/stores/menuStore.spec.ts tests/unit/layout/BaseLayout.navigation.test.ts tests/unit/layout/BaseLayout.test.ts` 现已实测 `21 passed`，新增 store 单测直接验证 expanded keys 与 `sidebarCollapsed` 的 localStorage 读取和回写

- [x] 1.1.1 更新路由配置使用ArtDecoLayoutEnhanced (基于迁移路由经验)
- [x] 1.1.2 完善当前 canonical 菜单配置的业务域 (提案原文为6域；当前 repo truth 为7域)
- [x] 1.1.3 实现树形菜单的展开/折叠功能
- [x] 1.1.4 基于11个路由测试用例验证菜单跳转 (学习迁移报告的测试方法)
- [x] 1.1.5 测试菜单状态保持和响应式布局

### 1.2 依赖管理统一
> **局部事实说明（2026-04-28）**:
> 当前依赖统一尚未完成：
> - `web/frontend/package.json` 仍保留 `@ant-design/icons-vue`
> - `web/frontend/src/views/monitoring/composables/useRiskDashboard.ts`
> - `web/frontend/src/components/monitoring/MonitoringAlertPanel.vue`
> - `web/frontend/src/components/monitoring/MonitoringDataTable.vue`
>   仍直接从 `@ant-design/icons-vue` 导入图标
> 因此最初 1.2.1-1.2.5 均保持未完成，避免把“主界面已大体迁移到 Element Plus + ArtDeco”误写成“依赖冲突已清理完毕”。
> 2026-05-07 repo-truth 更新：
> - 审计已确认 `ant-design-vue` 本体已经不在 `web/frontend/package.json` 的 runtime `dependencies` 中，当前残留的是 icon bridge `@ant-design/icons-vue`
> - `rg -n "@ant-design/icons-vue|ant-design-vue" web/frontend/src web/frontend/tests web/frontend/package.json` 当前命中表明，活跃源码里的残留导入集中在：
>   - `web/frontend/src/views/monitoring/composables/useRiskDashboard.ts`
>   - `web/frontend/src/components/monitoring/MonitoringAlertPanel.vue`
>   - `web/frontend/src/components/monitoring/MonitoringDataTable.vue`
> - 现有 `web/frontend/tests/unit/components/ant-design-migration.spec.ts` 已实测 `3 passed`，并直接守护：
>   - `ant-design-vue` 运行时不可用
>   - `element-plus` 与 `@element-plus/icons-vue` 仍在
>   - `@ant-design/icons-vue` 仍作为迁移过渡依赖保留
> - 非源码配置层的冲突收口也已具备直接证据：
>   - `web/frontend/vite.config.mts` 当前只接入 `ElementPlusResolver()` 与 `element-plus` 分包策略，未再包含 `ant-design-vue` 相关 resolver / plugin / alias
>   - `cd web/frontend && npm run build:no-types` 现已实测通过，说明当前构建配置本身未被 Ant Design 旧接线阻塞
> - 因此 1.2.1 与 1.2.4 已可按 repo-truth 勾选；但 1.2.2、1.2.3、1.2.5 继续保持未完成，因为真实残留导入与过渡依赖尚未移除。

- [x] 1.2.1 审计当前依赖使用情况 (Element Plus + Ant Design Vue冲突分析)
- [ ] 1.2.2 移除ant-design-vue相关组件 (基于迁移报告的清理策略)
- [ ] 1.2.3 统一使用Element Plus + ArtDeco组件
- [x] 1.2.4 更新构建配置移除冲突 (参考Vite配置优化经验)
- [ ] 1.2.5 验证样式一致性 (ArtDeco设计系统完整覆盖)

### 1.3 测试基础设施完善
- [x] 1.3.1 配置Vitest覆盖率报告 (基于228个测试文件的实际经验)
- [x] 1.3.2 编写核心组件单元测试 (ArtDeco组件优先)
- [x] 1.3.3 实现E2E自动化测试 (参考迁移报告的部署验证)
- [x] 1.3.4 配置CI/CD测试流水线
- [ ] 1.3.5 建立测试覆盖率基线 (目标60%)
  - Repo-truth blocker（2026-05-07）: `cd web/frontend && npm run test:coverage` 当前未能产出覆盖率报告，命令以退出码 `1` 结束，且未生成 `web/frontend/coverage/` 目录，因此“覆盖率基线已建立”不能按当前事实勾选。
  - 本次实测汇总：`296` 个测试文件中 `293 passed / 3 failed`，测试用例 `1173 passed / 3 failed`。
  - 当前阻塞失败均为既有无关红测，而非本批新增实现：
    - `src/views/artdeco-pages/market-tabs/__tests__/MarketKLineTab.spec.ts` 仍断言 `period: "daily"`，但当前真实调用参数已是 `period: "1d"`。
    - `tests/unit/config/comprehensive-e2e-route-coverage.spec.ts` 仍断言 routed page inventory 为 `35`，但当前清单已增长到 `36`。
    - `tests/unit/workflows/ci-workflow-gates.spec.ts` 仍断言 workflow 文本包含 `validate_runtime_observability_drift.py`，但当前链路实际调用的是 `bash scripts/run_runtime_observability_drift_gate.sh`。
  - 因此 1.3.5 继续保持未完成；后续只有在覆盖率全量运行转绿并真正产出 report，或另行批准“按稳定子集建立基线”的新口径后，才能收口。

### 1.4 Bundle大小优化
- [x] 1.4.1 分析当前3.8MB Bundle构成 (vue-framework + echarts + vendor)
  - Repo-truth closeout（2026-05-07）: 当前 Vite `build:no-types` 的 bundle 结构已经重新测量，主体仍由 `echarts`、`element-plus`、`vendor`、`vue-core` 构成。最新构建输出显示：
    - `echarts` chunk 838.76 kB（gzip 258.95 kB）
    - `element-plus` chunk 535.32 kB（gzip 153.57 kB）
    - `vendor` chunk 308.38 kB（gzip 103.98 kB）
    - `vue-core` chunk 107.40 kB（gzip 40.49 kB）
  - 这说明当前 bundle 仍处于“分析已完成、优化余量仍显著”的状态；`1.4.5` 继续保持未完成，因为 2.5MB 目标尚未达成。
- [x] 1.4.2 实施精确的分包策略 (基于实际构建数据的优化)
- [ ] 1.4.3 移除未使用的依赖和死代码
  - Repo-truth blocker（2026-05-07）: 当前还不能把这项按事实勾选。
  - 依赖层面：`ant-design-vue` 本体虽已移出 runtime `dependencies`，但 `@ant-design/icons-vue` 仍在活跃源码中使用，至少包括：
    - `web/frontend/src/views/monitoring/composables/useRiskDashboard.ts`
    - `web/frontend/src/components/monitoring/MonitoringAlertPanel.vue`
    - `web/frontend/src/components/monitoring/MonitoringDataTable.vue`
  - 死代码层面：`web/frontend/src/_entry-archive/` 仍保留多份历史 `main*.js/ts` 资产；它们当前更接近 archive / retained assets，而不是已确认可删除的死代码。
  - 本次还同步修正了 `web/frontend/ENTRY-TRUTH.md`：当前唯一活跃浏览器入口是 `index.html -> src/main-standard.ts`，此前关于 `verify-mount.js -> src/main.js` 的说法已不符合当前树状态。
  - 因此 1.4.3 继续保持未完成；后续只有在 `@ant-design/icons-vue` 迁移完成、archive 资产的保留/删除边界被单独批准后，才能真正收口。
- [x] 1.4.4 优化ECharts按需引入
- [ ] 1.4.5 验证Bundle大小达到2.5MB目标

### 1.5 首屏加载优化
> **局部事实说明（2026-04-27）**:
> 当前前端已具备缓存策略实现基础：
> - 活跃入口 `web/frontend/src/main-standard.ts` 会在 `load` 后注册 `/sw.js`
> - `web/frontend/public/sw.js` 已对静态资源、导航请求、API 请求分别实现 cache-first / network-first / offline fallback 策略
> - `web/frontend/src/utils/indexedDB.ts` 还补充了本地 `api_cache` TTL 缓存层
> 因此 1.5.4 可按“缓存策略已实施”勾选；但性能目标值验证仍需保留在 1.5.5。

- [x] 1.5.1 实施路由懒加载优化 (基于迁移报告的性能经验)
- [x] 1.5.2 关键资源预加载策略
  - Repo-truth：`web/frontend/index.html` 已对 Google Fonts 配置 `preconnect` + `preload as="style"`，形成当前活跃入口的关键资源预加载策略；`src/utils/performance/part-1.ts` 也提供了 `preloadResources()` 辅助能力。
- [ ] 1.5.3 图片和字体优化 (WebP + 响应式)
- [x] 1.5.4 缓存策略实施 (学习迁移报告的缓存配置)
- [x] 1.5.5 验证首屏时间达到2.5s目标
  - Repo-truth closeout（2026-05-08）: `cd web/frontend && npm run test:e2e:lighthouse` 已在当前仓库内实际跑通，构建 `dist-lighthouse` 后对 6 个认证路由执行了 Lighthouse smoke：
    - `/login`: `FCP 0.4s`, `LCP 0.6s`, `Performance 100`
    - `/dashboard`: `FCP 0.3s`, `LCP 0.5s`, `Performance 96`
    - `/market/realtime`: `FCP 0.2s`, `LCP 0.5s`, `Performance 100`
    - `/strategy/repo`: `FCP 0.2s`, `LCP 0.5s`, `Performance 100`
    - `/risk/overview`: `FCP 0.2s`, `LCP 0.4s`, `Performance 100`
    - `/trade/terminal`: `FCP 0.3s`, `LCP 0.5s`, `Performance 100`
  - 本次 `.lighthouseci/assertion-results.json` 为空数组，说明现行 assertion 没有失败；当前最慢 route 的 `LCP` 也仅 `0.6s`，明显低于 `2.5s` 目标。
  - 因此 `1.5.5` 现可按 repo-local 真实验证闭合。

### 1.6 运行时性能优化
> **局部事实说明（2026-04-28）**:
> 当前可直接确认：
> - `web/frontend/src/layouts/ArtDecoLayoutEnhanced.vue` 已集成全局 `@/components/common/PerformanceMonitor.vue`
> - `web/frontend/src/components/technical/KLineChart.vue` 已提供性能监控按钮，并挂接局部 `PerformanceMonitor`
> - `web/frontend/src/composables/usePerformanceMonitor.ts` 已通过 `requestAnimationFrame` 采集 FPS / JS heap 指标
> 但 WebSocket 优化仍存在主链路与增强链路分离：
> - `web/frontend/src/composables/useWebSocketEnhanced.ts` 与 `useWebSocketWithConfig.ts` 具备自动重连、心跳、路由订阅能力
> - 当前活跃 `web/frontend/src/layouts/BaseLayout.vue` 仍直接使用简化版 `useWebSocket.ts`
> 因此 1.6.5 可按“监控面板已集成”勾选，1.6.2 继续保留未完成。

- [ ] 1.6.1 虚拟滚动大数据表格 (基于实际使用场景)
- [ ] 1.6.2 WebSocket连接优化
- [ ] 1.6.3 内存泄漏检查和修复
- [ ] 1.6.4 基于RequestIdleCallback的非阻塞操作
- [x] 1.6.5 性能监控面板集成
  - Repo-truth：`web/frontend/src/layouts/ArtDecoLayoutEnhanced.vue` 已挂接全局 `PerformanceMonitor`，`web/frontend/src/components/technical/KLineChart.vue` 也已接入局部性能监控面板与切换按钮。

## Phase 2: Advanced HTML5 Features Implementation

### 2.1 PWA Foundation Setup
> **局部事实说明（2026-04-28）**:
> `web/frontend/public/manifest.json` 已引用多尺寸图标，且 `web/frontend/public/icons/` 现有 `icon-72/96/128/144/192/512.png`。
> 但 manifest 仍引用缺失的 `/screenshots/dashboard.png`、`/screenshots/analysis.png` 与 `shortcut-*.png`，`web/frontend/public/icons/README.md` 也明确写着当前仍是 placeholder 口径。
> 因此 2.1.2 继续保留未完成，避免把“基础图标文件存在”误写成“PWA icons + splash/shortcut 资源已闭环”。

- [x] 2.1.1 Create Web App Manifest (`public/manifest.json`) (基于迁移报告的标准配置)
- [ ] 2.1.2 Add PWA icons and splash screens (192x192, 512x512, etc.)
- [x] 2.1.3 Implement basic Service Worker registration
- [x] 2.1.4 Add PWA meta tags to index.html (参考HTML5语义化经验)
- [ ] 2.1.5 Configure Vite PWA plugin for build process

### 2.2 Service Worker Implementation
> **局部事实说明（2026-04-27）**:
> `web/frontend/public/sw.js` 已实现 `sync` 事件监听、`BackgroundSyncQueue`、失败重试与指数退避逻辑。
> 但当前尚未找到前端侧的 `registration.sync.register(...)` 调用，也未找到把失败请求显式写入该队列的现行链路。
> 因此 2.2.4 继续保留未完成，避免把“SW 端处理器存在”误写成“端到端 background sync 已闭环”。

- [x] 2.2.1 Create Service Worker for caching static assets (学习迁移报告的缓存策略)
- [x] 2.2.2 Implement runtime caching for API responses
- [x] 2.2.3 Add offline fallback pages and strategies (参考11个路由的离线支持)
- [ ] 2.2.4 Implement background sync for failed requests
- [x] 2.2.5 Add cache versioning and cleanup logic (基于迁移经验的版本管理)

### 2.3 IndexedDB Integration
- [x] 2.3.1 Create IndexedDB wrapper utility (基于localStorage现有经验扩展)
- [x] 2.3.2 Implement schema for market data storage (股票数据/技术指标)
- [x] 2.3.3 Add IndexedDB operations (CRUD) with promises
- [x] 2.3.4 Integrate with existing data management system
- [ ] 2.3.5 Add storage quota monitoring and management
  - [ ] Repo-truth：当前未发现 `navigator.storage.estimate()` / quota usage 之类的现行实现；`web/frontend/src/views/system/Settings.vue` 中的“配额使用率”仍是静态展示数据，不构成浏览器存储配额管理闭环。

### 2.4 Web Workers Implementation
> **局部事实说明（2026-04-27）**:
> 当前仓库可以确认：
> - `web/frontend/src/workers/indicatorDataWorker.worker.ts` 已实现技术指标计算 Worker
> - `web/frontend/src/workers/protocol.ts` 已定义通信协议
> - `web/frontend/src/stores/marketData.ts` 已通过 `workersManager.calculateIndicator(...)` 消费该能力
> 但 `web/frontend/src/utils/workersManager/workers-manager.ts` 的协调层仍以占位实现为主，`calculateIndicator()` 尚未形成真实 Worker 生命周期编排；`chartPerformanceUtils.ts` 虽有通用 `new Worker(...)` / `terminate()` / `onerror` 处理，也未成为当前 K 线处理的 canonical pipeline。
> 因此 2.4.2 与 2.4.5 继续保留未完成：前者缺少当前活跃 K 线数据处理 Worker 主链路，后者缺少真实 Worker 生命周期/错误恢复收口。

- [x] 2.4.1 Create Web Worker for technical indicator calculations (253个指标计算)
- [ ] 2.4.2 Implement Web Worker for data processing tasks (K线数据处理)
- [x] 2.4.3 Add Web Worker communication protocol (基于Vue组件集成)
- [x] 2.4.4 Integrate Web Workers with Vue components
- [ ] 2.4.5 Add error handling and worker lifecycle management

### 2.5 Push Notifications
> **局部事实说明（2026-04-28）**:
> 当前通知能力停留在“偏好契约与客户端封装已存在”的阶段：
> - 后端已有 `web/backend/app/api/notification.py` 的 `GET/POST /preferences`
> - 前端已有 `web/frontend/src/api/user.ts` 中的 `getNotificationSettings()` / `updateNotificationSettings()`
> - `web/frontend/src/api/__tests__/user.notification-settings.spec.ts` 已校验调用到 `/api/notification/preferences`
> 但当前活跃 `web/frontend/src/views/system/Settings.vue` 只在说明文案中提到该契约，并未提供通知偏好表单；同时未找到 `Notification.requestPermission`、`PushManager` / `serviceWorkerRegistration.pushManager` 的现行实现，也未找到后端 `/subscribe` / `/unsubscribe` push 订阅管理路由。
> 因此 2.5.1-2.5.5 暂不勾选。

- [ ] 2.5.1 Implement push notification permission handling
- [ ] 2.5.2 Create notification service for market alerts (股价异动/技术信号)
- [ ] 2.5.3 Add backend API for push subscription management
- [ ] 2.5.4 Integrate with existing alert system
- [ ] 2.5.5 Add notification preferences in settings

### 2.6 Advanced Caching Strategy
> **局部事实说明（2026-04-27）**:
> 当前仓库已存在直接可核对的缓存失效逻辑：
> - `web/frontend/public/sw.js` 实现了按 cache type 区分的 `expirationTimes` / `maxEntries`、周期性 `cleanup()` 与激活时清理
> - `web/frontend/src/utils/indexedDB.ts` 为 `api_cache` 建立了 `expiresAt` 索引，并在 `getCache()` / `clearExpiredCache()` 中执行 TTL 失效与过期清理
> 因此 2.6.2 可按“已实现智能失效/清理逻辑”勾选；但 cache warming、监控分析等后续项仍未形成闭环。

- [x] 2.6.1 Implement Cache API for static assets (基于Service Worker)
- [x] 2.6.2 Add intelligent cache invalidation logic (市场数据实时性考虑)
- [x] 2.6.3 Create cache-first/network-fallback strategy
- [ ] 2.6.4 Implement cache warming for hot data (热门股票数据)
- [ ] 2.6.5 Add cache analytics and monitoring

### 2.7 HTML5 APIs Integration
- [ ] 2.7.1 Add Geolocation API for location-based features (附近券商/市场分析)
- [ ] 2.7.2 Implement Vibration API for haptic feedback (交易确认/告警通知)
- [ ] 2.7.3 Add Battery API for power-aware optimizations (低电量模式)
- [ ] 2.7.4 Implement Network Information API for adaptive loading (网络质量自适应)
- [ ] 2.7.5 Add Device Orientation API support (移动端图表交互)

### 2.8 Accessibility Enhancements
> **局部事实说明（2026-04-28）**:
> 当前仓库已存在可访问性基础能力与局部验证：
> - `web/frontend/src/composables/useAria/*` 与多个活跃页面/组件已接入 `aria-*`、`role`、`tabindex`
> - `web/frontend/tests/e2e/accessibility-smoke.spec.ts` 使用 `@axe-core/playwright`
> - `web/frontend/package.json` 暴露 `test:e2e:axe`
> - `.github/workflows/frontend-testing.yml` 已运行 `npm run test:e2e:axe`
> 但当前未发现 WAVE 相关现行实现，`axe` 也主要覆盖有限 smoke 页面而不是完整业务域闭环，因此 2.8.1-2.8.5 继续保持未完成。

- [ ] 2.8.1 Audit and optimize HTML5 semantic elements (基于ArtDeco组件优化)
- [ ] 2.8.2 Add comprehensive ARIA attributes (菜单/图表/表单)
- [ ] 2.8.3 Implement keyboard navigation improvements (Tab顺序/快捷键)
- [ ] 2.8.4 Add screen reader optimizations (股票数据朗读)
- [ ] 2.8.5 Test with accessibility tools (WAVE, axe) (量化可访问性提升)

### 2.9 Performance Monitoring & Analytics
> **局部事实说明（2026-04-28）**:
> 当前仓库可以确认两层性能监控能力：
> - 活跃布局链路：`web/frontend/src/layouts/ArtDecoLayoutEnhanced.vue` 挂接 `components/common/PerformanceMonitor.vue`，通过 `usePerformanceMonitor.ts` 提供 FPS / JS Heap 监控
> - 独立页面实现：`web/frontend/src/views/system/PerformanceMonitor.vue` 已编写 `PerformanceObserver` 监听 `largest-contentful-paint`、`first-input`、`layout-shift`，并提供趋势/预算面板
> 但当前 `router/index.ts` 与 `layouts/MenuConfig.ts` 都未把 `views/system/PerformanceMonitor.vue` 暴露为活跃路由，活跃链路中的全局监控面板也尚未承接 cache hit、PWA usage、RUM 等指标。
> 因此 2.9.1、2.9.2、2.9.3、2.9.4、2.9.5 暂不勾选，避免把“孤立页面实现”误写成“现行性能分析体系已接入完成”。

- [ ] 2.9.1 Implement Web Vitals tracking (LCP/FID/CLS) (基于迁移报告的性能基准)
- [ ] 2.9.2 Add cache hit rate analytics (PWA缓存效果监控)
- [ ] 2.9.3 Implement PWA usage metrics (安装率/使用时长)
- [ ] 2.9.4 Add Real User Monitoring (RUM) integration
- [ ] 2.9.5 Create performance dashboard (基于技术指标)

## Phase 3: Integration & Validation

### 3.1 架构集成验证
- [ ] 3.1.1 验证菜单系统与PWA的集成 (离线菜单功能)
- [ ] 3.1.2 测试Web Workers与IndexedDB的数据流
- [ ] 3.1.3 验证缓存策略与实时数据的一致性
- [ ] 3.1.4 测试HTML5 APIs与现有功能的兼容性

### 3.2 端到端测试
- [ ] 3.2.1 实施11个路由的PWA离线测试 (学习迁移报告)
- [ ] 3.2.2 测试跨浏览器的PWA功能 (Chrome/Firefox/Safari/Edge)
- [ ] 3.2.3 验证IndexedDB数据持久化和迁移
- [ ] 3.2.4 测试Web Workers性能提升量化

### 3.3 生产部署准备
- [ ] 3.3.1 配置服务器PWA支持 (Service Worker + Manifest)
- [ ] 3.3.2 实施渐进式部署策略 (基于迁移经验的风险控制)
- [ ] 3.3.3 建立回滚机制和监控告警
- [x] 3.3.4 准备用户沟通和培训材料
> 已由 `docs/guides/frontend/HTML5_RUNTIME_ROLLOUT_COMMUNICATION_GUIDE.md` 回写当前 repo-truth 的沟通与培训材料草案，明确：
> - 当前对外口径只能描述为“基础 HTML5 runtime 能力与 supporting guides 已具备，仍处于灰度与验收前阶段”
> - 当前不能对外承诺“完整 PWA 闭环”“完整离线业务能力”“通知设置已完整开放”
> - 当前材料准备已完成，但 `3.3.1-3.3.3` 的真实部署准备，以及 `3.4.4` 的实际团队培训和技术分享仍继续保持未完成
> 因此 `3.3.4` 可按“repo-local 材料已准备”勾选，但部署和培训执行链路不被提前视为完成。

### 3.4 文档和培训
- [x] 3.4.1 更新开发文档 (PWA配置/IndexedDB使用/Web Workers)
> 已由 `docs/guides/frontend/HTML5_RUNTIME_CAPABILITY_GUIDE.md` 和 `docs/guides/frontend/INDEX.md` 回写当前 repo-truth：
> - 浏览器入口是 `index.html -> src/main-standard.ts`
> - Service Worker / manifest / IndexedDB / worker 协议与 manager 当前都已有真实运行时代码面
> - `vite-plugin-pwa` 仍禁用，`manifest` 截图资源缺失，多个 Playwright spec 显式 `serviceWorkers: 'block'`
> 因此开发文档已更新，但 `2.1.x / 3.2.x / 3.3.x` 的 PWA 完整验收和部署链路仍继续保持未闭合。
- [x] 3.4.2 创建用户指南 (PWA安装/离线使用/通知设置)
> 已由 `docs/guides/frontend/HTML5_RUNTIME_USER_GUIDE.md` 回写 current-state 用户说明，明确：
> - 当前 PWA 安装体验属于“基础安装面已存在”，但不是完整产品化验收闭环
> - 当前离线使用属于 best-effort cache / fallback，不等价于核心业务全离线可用
> - 当前通知偏好契约与前端预留能力已存在，但活跃 `system/Settings.vue` 尚未暴露完整通知偏好表单
> 因此“用户指南”已具备 current-state supporting guide，但 `2.5.x / 3.2.x / 3.3.x` 等能力闭环任务仍继续保持未完成。
- [x] 3.4.3 准备运维文档 (监控指标/故障排查)
> 已由 `docs/guides/frontend/HTML5_RUNTIME_OPERATIONS_GUIDE.md` 回写当前 repo-truth 运维入口，明确了：
> - PWA / Service Worker / IndexedDB / Web Workers 当前可观察的 runtime surface
> - 共享 PM2 前端下的最小 reachability 检查命令
> - 浏览器侧 `Manifest / Service Workers / IndexedDB / Console` 排查路径
> - 当前不能误写成生产级闭环的边界：`vite-plugin-pwa` 仍禁用、manifest 截图缺失、多个 E2E spec 显式 `serviceWorkers: 'block'`、worker manager 仍是轻量 façade
> 因此“运维文档”已具备 current-state supporting guide，但 `3.2.x / 3.3.x / 2.9.x` 的验收与监控闭环仍继续保持未完成。
- [ ] 3.4.4 组织团队培训和技术分享

## Success Metrics & Validation

### Functional Validation
- [ ] ✅ 7个业务域菜单完整实现并正常工作 (提案原文为6域)
- [ ] ✅ PWA可安装和离线功能正常
- [ ] ✅ IndexedDB数据存储和检索正常
- [ ] ✅ Web Workers性能提升量化验证
- [ ] ✅ HTML5 APIs在支持浏览器中正常工作

### Performance Validation
- [ ] ✅ Bundle大小 ≤ 2.5MB (当前3.8MB → 目标)
- [x] ✅ 首屏加载时间 ≤ 2.5s (当前已由 2026-05-08 Lighthouse smoke 验证)
- [ ] ✅ Lighthouse评分 ≥ 90 (性能/可访问性/PWA)
- [ ] ✅ 测试覆盖率 ≥ 60% (当前~5%)
- [ ] ✅ Web Vitals各项指标达标

### User Experience Validation
- [ ] ✅ PWA安装成功率 > 80%
- [ ] ✅ 离线功能覆盖核心使用场景
- [ ] ✅ 通知系统用户接受率 > 60%
- [ ] ✅ 移动端响应式体验完善
- [ ] ✅ 可访问性WCAG 2.1 AA标准达标

### Business Impact Validation
- [ ] ✅ 用户留存率提升 > 25%
- [ ] ✅ 页面加载性能提升 > 35%
- [ ] ✅ 移动端使用率提升 > 40%
- [ ] ✅ 技术债务减少 > 60%
- [ ] ✅ 开发效率提升 > 40%
