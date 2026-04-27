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
> 但当前仍未找到“严格按 11 个菜单跳转用例完成验证”与“专门验证菜单状态保持”的直接 closeout 证据，因此 1.1.4 / 1.1.5 暂不勾选。

- [x] 1.1.1 更新路由配置使用ArtDecoLayoutEnhanced (基于迁移路由经验)
- [x] 1.1.2 完善当前 canonical 菜单配置的业务域 (提案原文为6域；当前 repo truth 为7域)
- [x] 1.1.3 实现树形菜单的展开/折叠功能
- [ ] 1.1.4 基于11个路由测试用例验证菜单跳转 (学习迁移报告的测试方法)
- [ ] 1.1.5 测试菜单状态保持和响应式布局

### 1.2 依赖管理统一
- [ ] 1.2.1 审计当前依赖使用情况 (Element Plus + Ant Design Vue冲突分析)
- [ ] 1.2.2 移除ant-design-vue相关组件 (基于迁移报告的清理策略)
- [ ] 1.2.3 统一使用Element Plus + ArtDeco组件
- [ ] 1.2.4 更新构建配置移除冲突 (参考Vite配置优化经验)
- [ ] 1.2.5 验证样式一致性 (ArtDeco设计系统完整覆盖)

### 1.3 测试基础设施完善
- [x] 1.3.1 配置Vitest覆盖率报告 (基于228个测试文件的实际经验)
- [x] 1.3.2 编写核心组件单元测试 (ArtDeco组件优先)
- [x] 1.3.3 实现E2E自动化测试 (参考迁移报告的部署验证)
- [x] 1.3.4 配置CI/CD测试流水线
- [ ] 1.3.5 建立测试覆盖率基线 (目标60%)

### 1.4 Bundle大小优化
- [ ] 1.4.1 分析当前3.8MB Bundle构成 (vue-framework + echarts + vendor)
- [x] 1.4.2 实施精确的分包策略 (基于实际构建数据的优化)
- [ ] 1.4.3 移除未使用的依赖和死代码
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
- [ ] 1.5.5 验证首屏时间达到2.5s目标

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
> 因此 2.4.5 继续保留未完成。

- [x] 2.4.1 Create Web Worker for technical indicator calculations (253个指标计算)
- [ ] 2.4.2 Implement Web Worker for data processing tasks (K线数据处理)
- [x] 2.4.3 Add Web Worker communication protocol (基于Vue组件集成)
- [x] 2.4.4 Integrate Web Workers with Vue components
- [ ] 2.4.5 Add error handling and worker lifecycle management

### 2.5 Push Notifications
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
- [ ] 2.8.1 Audit and optimize HTML5 semantic elements (基于ArtDeco组件优化)
- [ ] 2.8.2 Add comprehensive ARIA attributes (菜单/图表/表单)
- [ ] 2.8.3 Implement keyboard navigation improvements (Tab顺序/快捷键)
- [ ] 2.8.4 Add screen reader optimizations (股票数据朗读)
- [ ] 2.8.5 Test with accessibility tools (WAVE, axe) (量化可访问性提升)

### 2.9 Performance Monitoring & Analytics
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
- [ ] 3.3.4 准备用户沟通和培训材料

### 3.4 文档和培训
- [ ] 3.4.1 更新开发文档 (PWA配置/IndexedDB使用/Web Workers)
- [ ] 3.4.2 创建用户指南 (PWA安装/离线使用/通知设置)
- [ ] 3.4.3 准备运维文档 (监控指标/故障排查)
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
- [ ] ✅ 首屏加载时间 ≤ 2.5s (当前~2.8s)
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
