## Context

> **设计方案说明**:
> 本文件用于记录某项变更的设计思路、结构拆分、实现取舍或技术路径，属于方案设计层材料。
> 它不是共享规则正文，也不直接代表当前仓库已落地状态；落地判断应结合 `architecture/STANDARDS.md`、对应 proposal/tasks、审批结果与实际代码验证。

> **Current Repo-Truth Disposition（2026-05-11）**:
> 本设计文档保留原始方案设计与技术目标，不应直接视为当前实现承诺。当前执行事实以 `tasks.md`、`tasks-review.md` 的 2026-05-11 disposition、实际代码和验证命令为准。
>
> 当前设计执行边界：
> - 当前产品范围是 **Desktop-only**；移动端和设备 API 伸展项已从本变更当前闭合范围中移除。
> - 菜单架构的当前 repo-truth 是 `MenuConfig.ts` 的 7 个业务域，不再按原始 6-domain 设计作为完成判定。
> - PWA 已有 manifest / service worker / preview static asset 支撑的 repo-local 局部闭合，但 push 订阅、后端 Web Push 路由、完整离线菜单矩阵与生产部署签收仍未闭合。
> - Storage 当前只按 Desktop Chromium `MyStocksDB` v1 bootstrap 与 close/reopen persistence 局部闭合；自动 localStorage -> IndexedDB migration、生产数据迁移、跨浏览器持久性不是当前已完成事实。
> - Workers 当前只能按 worker files / protocol source / manager facade 描述；不能承诺完整 orchestration、真实业务数据流或同数据集性能收益。
> - Rollout、rollback、monitoring、training 当前有模板或 runbook，但没有真实执行记录、告警闭环、回滚演练或 release owner sign-off。

Based on the successful HTML5 History Mode migration completion report, we have identified critical opportunities to enhance the MyStocks frontend architecture while implementing advanced HTML5 features. The current architecture has solid foundations (HTML5 History routing, ArtDeco design system, Vue 3 + TypeScript) but requires optimization based on migration experience and modern web platform capabilities.

### HTML5 Migration Experience Insights
The recent HTML5 History migration revealed key optimization opportunities:
- **Bundle大小超标**: 3.8MB vs 目标2.5MB (-34%优化空间)
- **菜单系统不完整**: MenuConfig.enhanced.ts设计完善但实现滞后
- **依赖管理复杂**: Element Plus + Ant Design Vue冲突
- **测试覆盖不足**: 228个测试文件但覆盖率仅5%
- **服务器配置依赖**: HTML5 History需要回退配置

### Current Architecture Assessment
- ✅ **技术栈**: Vue 3 + TypeScript + Vite (现代化)
- ✅ **路由系统**: HTML5 History模式 (已迁移完成)
- ✅ **设计系统**: ArtDeco金色主题 (66组件)
- ⚠️ **菜单架构**: 功能域设计完善，实现不完整
- ⚠️ **性能表现**: Bundle偏大，测试覆盖不足
- ❌ **PWA支持**: 缺少离线功能和安装能力

## Goals / Non-Goals
### Goals
**Frontend Architecture Optimization (Based on HTML5 Migration Experience):**
- 完成MenuConfig.enhanced.ts的6功能域菜单系统实现
- 统一依赖管理 (移除ant-design-vue冲突)
- 提升测试覆盖率至60% (基于228个测试文件经验)
- Bundle大小优化: 3.8MB → 2.5MB (-34%)
- 首屏加载优化: ~2.8s → 2.5s目标

**Advanced HTML5 Features:**
- Implement comprehensive PWA functionality with offline support
- Add advanced storage solutions (IndexedDB, Cache API)
- Optimize performance with Web Workers and modern APIs
- Enhance accessibility and semantic HTML5 usage
- Maintain 99% backward compatibility with existing functionality
- Achieve measurable performance improvements (30-50% faster loading)

### Non-Goals
- Breaking changes to existing API contracts
- Replacing Vue.js with other frameworks
- Implementing native mobile apps (stays web-only)
- Adding server-side rendering (remains SPA)
- 放弃HTML5 History模式 (已成功迁移)

## Decisions

### Frontend Architecture Optimization Decisions

#### Menu System Architecture
**Decision**: Complete implementation of 6-domain menu system based on MenuConfig.enhanced.ts
- **Rationale**: HTML5迁移经验显示菜单系统是用户体验核心，现有实现不完整导致功能覆盖不足
- **Trade-off**: 实现复杂度 vs. 用户体验提升 (预期+40%)
- **Implementation**: ArtDecoLayoutEnhanced + 树形菜单 + 6功能域完整覆盖

#### Dependency Management Strategy
**Decision**: Unified Element Plus + ArtDeco design system, remove Ant Design Vue conflicts
- **Rationale**: 迁移经验显示依赖冲突是主要技术债务源头
- **Trade-off**: 迁移工作量 vs. 维护成本降低 (预期-60%)
- **Implementation**: 渐进式替换 + 向后兼容保障

#### Testing Infrastructure Enhancement
**Decision**: Comprehensive testing strategy targeting 60% coverage based on 228 test files experience
- **Rationale**: 迁移报告强调测试是质量保障的基础，当前5%覆盖率严重不足
- **Trade-off**: 开发时间投入 vs. 长期质量保障
- **Implementation**: Vitest + Playwright + CI/CD集成

#### Performance Optimization Strategy
**Decision**: Bundle size optimization from 3.8MB to 2.5MB based on actual build analysis
- **Rationale**: 迁移经验量化了性能瓶颈的具体影响
- **Trade-off**: 优化复杂度 vs. 用户体验提升 (预期30-50%)
- **Implementation**: 精确分包策略 + 依赖清理 + 缓存优化

### Advanced HTML5 Features Decisions

#### PWA Architecture
**Decision**: Implement comprehensive PWA with Service Worker, Web App Manifest, and background sync
- **Rationale**: Enables offline functionality, installability, and push notifications for trading app
- **Trade-off**: Increased complexity vs. enhanced user experience (金融数据离线访问)
- **Implementation**: Use Vite PWA plugin for build-time optimization

#### Storage Strategy
**Decision**: Layered storage approach (Memory → IndexedDB → localStorage → Cache API)
- **Rationale**: Optimal performance for financial data types and real-time market data patterns
- **Trade-off**: Complexity vs. performance and offline capabilities (股票数据缓存)
- **Implementation**: Create unified storage manager with automatic fallback for market data

#### Web Workers Integration
**Decision**: Dedicated workers for technical indicator calculations (253 indicators) and K-line data processing
- **Rationale**: Prevents UI blocking during heavy financial computations
- **Trade-off**: Communication overhead vs. responsiveness (实时技术分析)
- **Implementation**: Message-passing protocol with error handling for trading algorithms

## Risks / Trade-offs

### Technical Risks
- **Service Worker Complexity**: Cache invalidation and versioning can be complex
- **Browser Compatibility**: Some APIs have limited support in older browsers
- **Storage Quota**: IndexedDB and Cache API have browser-imposed limits
- **Web Worker Debugging**: Harder to debug than main thread code

### Performance Risks
- **Initial Load**: PWA and Service Worker add to initial bundle size
- **Memory Usage**: Web Workers and advanced caching increase memory footprint
- **Cache Staleness**: Over-aggressive caching can serve stale data

### User Experience Risks
- **Permission Fatigue**: Push notification requests may annoy users
- **Storage Warnings**: Large IndexedDB usage may trigger browser warnings
- **Offline Confusion**: Users may not understand offline capabilities

## Implementation Strategy

### Phase 1: Foundation (PWA Core)
1. Web App Manifest and basic Service Worker
2. Core caching infrastructure
3. PWA installation prompts

### Phase 2: Storage Enhancement
1. IndexedDB integration
2. Enhanced caching strategies
3. Storage quota management

### Phase 3: Performance Optimization
1. Web Workers implementation
2. Advanced HTML5 APIs
3. Lazy loading and resource optimization

### Phase 4: Advanced Features
1. Push notifications
2. Background sync
3. Accessibility enhancements

### Phase 5: Testing & Polish
1. Cross-browser testing
2. Performance validation
3. Accessibility audit

## Migration Plan

### Backward Compatibility
- All existing functionality remains unchanged
- Graceful degradation for unsupported browsers
- Feature detection for optional enhancements

### Rollback Strategy
- Service Worker can be unregistered
- IndexedDB can be cleared via developer tools
- PWA can be uninstalled by users
- Feature flags for easy disabling

### Data Migration
- Existing localStorage data preserved
- Automatic migration from localStorage to IndexedDB
- Cache warming for improved initial load

## Open Questions
1. **Storage Quota Handling**: How to handle IndexedDB quota exceeded errors?
2. **Push Notification Strategy**: What notification types are most valuable for trading app?
3. **Offline Data Strategy**: Which data should be available offline vs. online-only?
4. **Web Worker Scope**: Which computations should move to workers vs. keep in main thread?
5. **Cache Invalidation**: How to handle real-time data updates with cached content?
