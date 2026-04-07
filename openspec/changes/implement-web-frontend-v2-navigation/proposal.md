# Web Frontend V2导航优化方案（2026-01-21更新版）

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。


**Change ID**: `implement-web-frontend-v2-navigation`
**Status**: 🔄 Ready for Implementation
**Created**: 2026-01-12
**Updated**: 2026-01-21
**Author**: Claude Code (Main CLI)
**Type**: Frontend Enhancement
**Priority**: High
**Estimated Duration**: 2-3 weeks

---

## 📊 Executive Summary（最新状态）

### 当前环境优势

**✅ ArtDeco设计系统**：
- 64个组件完整实现（Base 13 + Core 11 + Specialized 30 + Advanced 10）
- 统一布局系统：`ArtDecoLayout.vue`（已集成面包屑和跳转链接）
- 设计令牌系统完整（金色#D4AF37、几何装饰）

**✅ 后端API丰富**：
- Strategy域：`/api/strategy/list`, `/api/strategy-mgmt/strategies`
- Market域：`/api/market/realtime-summary`, `/api/market/v2/fund-flow`
- Trading域：`/api/trading/signals`, `/api/api/mtm/portfolio`
- Risk域：`/api/v1/risk/alerts`, `/api/monitoring/watchlists`

**✅ 前端基础设施**：
- TypeScript迁移基本完成（90个错误，持续优化中）
- PM2进程管理稳定（生产环境测试通过）
- 自动化测试脚本：`test-pages.mjs`, `run-comprehensive-e2e.js`

### 现有ArtDeco组件清单（29个）

**Strategy域**（3个组件）：
1. `ArtDecoStrategyManagement.vue` - 策略管理
2. `ArtDecoStrategyOptimization.vue` - 策略优化
3. `ArtDecoBacktestAnalysis.vue` - 回测分析

**Trading域**（6个组件）：
1. `ArtDecoTradingSignals.vue` - 交易信号
2. `ArtDecoTradingSignalsControls.vue` - 信号控制
3. `ArtDecoTradingHistory.vue` - 交易历史
4. `ArtDecoTradingHistoryControls.vue` - 历史控制
5. `ArtDecoTradingPositions.vue` - 持仓监控
6. `ArtDecoTradingStats.vue` - 交易统计

**Market域**（6个组件）：
1. `ArtDecoRealtimeMonitor.vue` - 实时监控
2. `ArtDecoMarketAnalysis.vue` - 市场分析
3. `ArtDecoMarketOverview.vue` - 市场概览
4. `ArtDecoIndustryAnalysis.vue` - 行业分析
5. `ArtDecoPerformanceOverview.vue` - 绩效概览
6. `ArtDecoSignalMonitoringOverview.vue` - 信号监控概览

**Risk域**（4个组件）：
1. `ArtDecoRiskAlerts.vue` - 风险告警
2. `ArtDecoRiskMonitor.vue` - 风险监控
3. `ArtDecoAnnouncementMonitor.vue` - 公告监控
4. `ArtDecoAttributionAnalysis.vue` - 归因分析

**System域**（4个组件）：
1. `ArtDecoMonitoringDashboard.vue` - 监控面板
2. `ArtDecoDataManagement.vue` - 数据管理
3. `ArtDecoPositionCard.vue` - 位置卡片
4. `ArtDecoSignalHistory.vue` - 信号历史

**其他组件**（6个）：
- ArtDecoCollapsibleSidebar, ArtDecoFilterBar等

### 当前完成度

- **路由集成度**: 9/38页面（24%）
- **组件准备度**: 29个组件已实现，等待路由集成
- **最大提升潜力**: Strategy域（3个组件）+ Trading域（6个组件）= 立即可用

---

## 🎯 核心目标

### Phase 1: P0优先级（第1周）- Trading域 + Strategy域

**原因**：
1. Trading域组件最完整（6个），API端点已就绪
2. Strategy域核心组件齐全（3个），业务价值高
3. 立即提升用户体验，快速见效

**预期成果**：
- 新增9个路由页面
- 完成度从24%→48%（+24%）
- 验证ArtDeco组件路由集成流程

### Phase 2: P1优先级（第2周）- Market域 + Risk域

**预期成果**：
- 新增10个路由页面
- 完成度达到74%

### Phase 3: P2优先级（第3周）- System域 + 优化

**预期成果**：
- 新增剩余组件
- 完成度达到92%+

---

## 🚀 技术方案

### 路由集成模式

```typescript
// 标准路由配置模板
{
  path: '/trading/signals',
  name: 'trading-signals',
  component: () => import('@/layouts/ArtDecoLayout.vue'),
  redirect: '/trading/signals',
  children: [
    {
      path: 'signals',
      name: 'trading-signals-view',
      component: () => import('@/views/artdeco-pages/components/trading/ArtDecoTradingSignals.vue'),
      meta: {
        title: '交易信号',
        icon: '📡',
        breadcrumb: 'Trading > Signals',
        requiresAuth: false
      }
    }
  ]
}
```

### 菜单配置集成

```typescript
// MenuConfig.ts - 标准菜单项模板
{
  path: '/trading/signals',
  label: '交易信号',
  icon: '📡',
  description: '实时交易信号监控',
  apiEndpoint: '/api/trading/signals',
  apiMethod: 'GET',
  liveUpdate: true,
  wsChannel: 'trading:signals',
  priority: 'primary'
}
```

### TypeScript类型安全

遵循`Typescript_BEST_PRACTICES.md`核心原则：
1. **从源头修复**：在接口定义时使用精确类型
2. **避免any类型**：使用联合类型和泛型
3. **显式优于隐式**：添加明确的类型注解

---

## 📋 实施计划

### Week 1: Trading域 + Strategy域集成

**Day 1-2**: Trading域（6个组件）
- ArtDecoTradingSignals.vue
- ArtDecoTradingHistory.vue
- ArtDecoTradingPositions.vue
- ArtDecoTradingStats.vue
- ArtDecoTradingSignalsControls.vue
- ArtDecoTradingHistoryControls.vue

**Day 3-4**: Strategy域（3个组件）
- ArtDecoStrategyManagement.vue
- ArtDecoStrategyOptimization.vue
- ArtDecoBacktestAnalysis.vue

**Day 5**: 测试验证
- 运行`test-pages.mjs`验证所有新页面
- PM2环境测试
- TypeScript类型检查（目标<80错误）

### Week 2-3: 其他域集成

按照P1、P2优先级继续集成Market、Risk、System域组件。

---

## ✅ 成功标准

1. **路由完整性**: 所有29个组件可访问
2. **类型安全**: TypeScript错误<80
3. **功能验证**: PM2测试全部通过
4. **性能标准**: 页面加载时间<2秒

---

## 🔗 相关文档

- **设计文档**: `docs/api/ARTDECO_TRADING_CENTER_DESIGN.md`
- **组件目录**: `web/frontend/ARTDECO_COMPONENTS_CATALOG.md`
- **质量指南**: `docs/guides/typescript/Typescript_BEST_PRACTICES.md`
- **测试脚本**: `web/frontend/run-comprehensive-e2e.js`
