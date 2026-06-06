# Change: Implement HTML5 Migration Experience Optimization (Combined Architecture + Advanced Features)

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。

> **Current Repo-Truth Disposition（2026-05-11）**:
> 本提案正文保留原始目标与历史指标口径，不应直接读取为当前实现状态。当前执行状态以 `tasks.md`、`tasks-review.md` 的 2026-05-11 disposition、实际代码与验证命令为准。
>
> 当前已固化的执行边界：
> - 产品范围为 **Desktop-only**；Geolocation / Vibration / Battery、移动端 screenshots / splash screens / shortcuts、移动端响应式验收等历史伸展项已去作用域。
> - 菜单系统当前 canonical 事实为 `MenuConfig.ts` 中 Market / Data / Watchlist / Strategy / Trade / Risk / System **7 个业务域**，不是原始提案中的 6 个功能域。
> - `2.1.2` 仅按 Desktop-only manifest asset consistency 闭合：manifest 只引用当前存在的核心图标资源；不代表移动端安装资产闭合。
> - `3.2.3` 仅按 Desktop Chromium `MyStocksDB` version `1` schema bootstrap 与 close/reopen persistence 闭合；不代表 future schema upgrade、跨浏览器、生产数据迁移。
> - `3.3.1` 仅按 repo-local production preview static asset support 闭合；不代表生产部署、HTTPS/CDN/Nginx、release owner 签收。
> - Push Notifications、Accessibility、Worker + IndexedDB 真实业务数据流、Web Worker 性能基准、rollout / rollback / training 执行记录仍未闭合。
> - 原始文中的 30-50% faster loading、90%+ cache hit rate、60% coverage、用户留存等指标属于目标或历史口径；没有当前实测证据时不得写作已达成。

## Why
Based on the successful HTML5 History Mode migration completion report, we have identified critical opportunities to enhance the MyStocks frontend architecture while implementing advanced HTML5 features. The current architecture has solid foundations but lacks optimization based on migration experience and modern web platform capabilities.

Key gaps identified:

### Architecture Optimization Gaps (From HTML5 Migration Experience)
- **菜单系统实现不完整**: MenuConfig.enhanced.ts已设计但实际使用基础版
- **依赖管理复杂**: 同时使用Element Plus + Ant Design Vue导致冲突
- **测试覆盖不足**: 228个测试文件但覆盖率仅5%
- **Bundle大小超标**: 当前3.8MB，目标2.5MB
- **Layout系统冗余**: 8个Layout文件，职责不清

### Advanced HTML5 Features Gaps
- **No PWA support**: Missing offline functionality and installability
- **Limited storage**: Only localStorage, no IndexedDB or advanced caching
- **Performance bottlenecks**: No Web Workers for heavy computations
- **Accessibility issues**: Limited ARIA support and keyboard navigation
- **Modern APIs unused**: No Network Info, Battery, Geolocation APIs

## What Changes
Implement comprehensive HTML5 migration experience optimization combining both architectural improvements and advanced features:

### Phase 1: Frontend Architecture Optimization (Based on HTML5 Migration Experience)

1. **菜单系统完整实现**
   - 更新路由配置使用ArtDecoLayoutEnhanced
   - 完善MenuConfig.enhanced.ts的6个功能域
   - 实现树形菜单的展开/折叠功能
   - 基于11个路由测试用例验证

2. **依赖管理统一**
   - 移除ant-design-vue冲突
   - 统一Element Plus + ArtDeco组件
   - 基于迁移报告的清理策略

3. **测试基础设施完善**
   - 基于228个测试文件的经验优化
   - 建立测试覆盖率基线 (目标60%)
   - 配置Vitest + Playwright完整链

4. **性能优化专项**
   - Bundle大小: 3.8MB → 2.5MB (-34%)
   - 构建时间: ~45s → ~25s (-44%)
   - 基于实际构建数据的精确优化

### Phase 2: Advanced HTML5 Features Implementation

5. **PWA (Progressive Web App) Implementation**
   - Web App Manifest for installability
   - Service Worker for offline support and advanced caching
   - Background sync for failed requests
   - Push notification support

6. **Advanced Storage & Caching**
   - IndexedDB integration for complex data storage
   - Cache API utilization with Service Worker
   - Enhanced localStorage/sessionStorage usage
   - Storage quota management and monitoring

7. **Performance Optimizations**
   - Web Workers for heavy computations (technical indicators, data processing)
   - RequestIdleCallback for non-blocking operations
   - Intersection Observer for lazy loading
   - Modern image formats (WebP, AVIF) and lazy loading

8. **Enhanced HTML5 APIs**
   - Geolocation API for location-based features
   - Vibration API for haptic notifications
   - Battery API for power-aware features
   - Network Information API for adaptive loading

9. **Accessibility & Semantics Enhancement**
   - HTML5 semantic elements optimization
   - Comprehensive ARIA attributes implementation
   - Keyboard navigation improvements
   - Screen reader support and testing

10. **Performance Monitoring & Analytics**
    - Web Vitals tracking and reporting
    - Cache hit rate analytics
    - PWA usage metrics and engagement tracking
    - Real User Monitoring (RUM) integration

## Impact
- **Affected specs**: web-frontend, api-documentation, html5-platform-features
- **Affected code**: web/frontend/ (entire frontend application), new PWA/service worker files
- **Breaking changes**: None (additive features and optimizations)
- **Performance improvement**: 30-50% faster loading, 90%+ cache hit rate, Bundle size -34%
- **Architecture improvement**: 菜单系统6功能域完整实现，测试覆盖率提升至60%
- **User experience**: Offline functionality, push notifications, installable PWA, enhanced accessibility
- **Browser support**: Modern browsers (Chrome 80+, Firefox 75+, Safari 13.1+, Edge 80+)
- **Implementation approach**: Combined architecture optimization + advanced features based on proven migration experience
