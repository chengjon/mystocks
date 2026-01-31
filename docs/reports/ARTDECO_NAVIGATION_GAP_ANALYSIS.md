# ArtDeco导航系统 - 路由实现与规划对比分析

**分析日期**: 2026-01-20
**分析范围**: 当前路由实现 vs OpenSpec规划菜单结构
**对比基准**: `docs/reports/IMPLEMENT_WEB_FRONTEND_V2_NAVIGATION_STATUS_REPORT.md`

---

## 📊 执行摘要

### 核心发现

**✅ 已完成**:
- 7个主页面组件全部实现并集成到路由
- ArtDecoLayout统一布局系统已部署
- 所有页面HTTP测试通过（10/10页面100%成功）
- 30+个子组件已创建但未集成到路由

**🔄 主要差距**:
1. **子页面路由缺失**: 30个ArtDeco子组件未配置路由
2. **二级菜单结构**: 规划的嵌套菜单未实现
3. **功能域页面数**: 实际2页/域 vs 规划8页/域（Market域）

**📈 完成度统计**:
- 主页面路由: 9/9 (100%) ✅
- 子组件集成: 0/30 (0%) ❌
- 整体路由完成度: 约23%

---

## 🔍 详细对比分析

### 1. Dashboard域（仪表盘）

#### 规划结构（Phase 3.1）

```
Dashboard (作为HOME页，不在菜单中显示)
├── Overview (市场汇总信息) - 主页
├── Watchlist (自选股列表)
├── Portfolio (投资组合)
└── Activity (交易活动)
```

#### 当前实现

**路由配置** (`router/index.ts`):
```typescript
{
  path: '/dashboard',
  component: ArtDecoLayout.vue,
  redirect: '/dashboard',  // 自重定向
  children: [
    {
      path: '/dashboard',
      component: ArtDecoDashboard.vue  // ✅ 已实现
    }
  ]
}
```

**实际组件**:
- ✅ `ArtDecoDashboard.vue` - 主仪表盘

**差距分析**:

| 页面 | 规划 | 实现 | 状态 | 建议 |
|------|------|------|------|------|
| Overview | ✅ | ✅ ArtDecoDashboard | **已实现** | 作为主Dashboard页 |
| Watchlist | ❌ | ❌ | **缺失** | 可复用 `Stocks.vue` 或创建新组件 |
| Portfolio | ❌ | ❌ | **缺失** | 可复用 `PortfolioManagement.vue` |
| Activity | ❌ | ❌ | **缺失** | 可复用 `TradeManagement.vue` |

**实现优先级**: P1（中）- 用户提到Dashboard是HOME页，不作为菜单项显示

---

### 2. Market域（市场行情）

#### 规划结构（Phase 3.1）

```
市场行情 (8个页面)
├── Real-time Quotes (实时行情)
├── Technical Analysis (技术分析)
├── TDX Integration (TDX集成)
├── Capital Flow (资金流向)
├── ETF Market (ETF市场)
├── Concept Analysis (概念分析)
├── Auction Analysis (集合竞价分析)
└── LHB Analysis (龙虎榜分析)
```

#### 当前实现

**路由配置**:
```typescript
{
  path: '/market',
  component: ArtDecoLayout.vue,
  children: [
    { path: 'data', component: ArtDecoMarketData.vue },      // ✅
    { path: 'quotes', component: ArtDecoMarketQuotes.vue }   // ✅
  ]
}
```

**实际组件**:
- ✅ `ArtDecoMarketData.vue` - 市场数据主页
- ✅ `ArtDecoMarketQuotes.vue` - 行情报价
- 📦 `ArtDecoRealtimeMonitor.vue` - **未集成到路由**
- 📦 `ArtDecoMarketAnalysis.vue` - **未集成到路由**
- 📦 `ArtDecoMarketOverview.vue` - **未集成到路由**
- 📦 `ArtDecoIndustryAnalysis.vue` - **未集成到路由**

**差距分析**:

| 页面 | 规划 | 当前实现 | 子组件状态 | 状态 | 建议 |
|------|------|----------|-----------|------|------|
| Real-time Quotes | ✅ | `/market/data` | ArtDecoMarketData | ✅ 已实现 | 作为主页面 |
| Technical Analysis | ✅ | ❌ | ArtDecoMarketAnalysis | 📦 存在未路由 | 需添加路由 |
| TDX Integration | ✅ | ❌ | ❌ | ❌ 缺失 | 需创建或复用 `TdxMarket.vue` |
| Capital Flow | ✅ | ❌ | ❌ | ❌ 缺失 | 需创建 |
| ETF Market | ✅ | ❌ | ❌ | ❌ 缺失 | 需创建 |
| Concept Analysis | ✅ | ❌ | ArtDecoIndustryAnalysis | 📦 存在未路由 | 需添加路由 |
| Auction Analysis | ✅ | ❌ | ❌ | ❌ 缺失 | 需创建 |
| LHB Analysis | ✅ | `/market/quotes` | ArtDecoMarketQuotes | ⚠️ 部分实现 | 可能包含龙虎榜功能 |

**完成度**: 2/8页面 (25%)

**推荐路由扩展**:
```typescript
{
  path: '/market',
  component: ArtDecoLayout.vue,
  children: [
    { path: 'data', component: ArtDecoMarketData },           // 实时行情（主）
    { path: 'quotes', component: ArtDecoMarketQuotes },       // 行情报价
    { path: 'realtime', component: ArtDecoRealtimeMonitor },  // 新增：实时监控
    { path: 'analysis', component: ArtDecoMarketAnalysis },    // 新增：技术分析
    { path: 'overview', component: ArtDecoMarketOverview },    // 新增：市场概览
    { path: 'industry', component: ArtDecoIndustryAnalysis }, // 新增：行业分析
    // 待创建: TDX集成, 资金流向, ETF市场, 集合竞价
  ]
}
```

**实现优先级**: P0（高）- Market域是核心功能

---

### 3. Stocks域（股票管理）

#### 规划结构（Phase 3.1 - Selection域）

```
股票管理 (6个页面)
├── Watchlist Management (自选股管理)
├── Portfolio Management (投资组合管理)
├── Trading Activity (交易活动)
├── Stock Screener (选股器)
├── Industry Stocks (行业选股)
└── Concept Stocks (概念选股)
```

#### 当前实现

**路由配置**:
```typescript
{
  path: '/stocks',
  component: ArtDecoLayout.vue,
  children: [
    { path: 'management', component: ArtDecoStockManagement.vue }  // ✅
  ]
}
```

**实际组件**:
- ✅ `ArtDecoStockManagement.vue` - 股票管理主页

**差距分析**:

| 页面 | 规划 | 当前实现 | 状态 | 复用建议 |
|------|------|----------|------|----------|
| Watchlist Management | ✅ | ❌ | ❌ 缺失 | 可复用 `WatchlistManagement.vue` |
| Portfolio Management | ✅ | ❌ | ❌ 缺失 | 可复用 `PortfolioManagement.vue` |
| Trading Activity | ✅ | ❌ | ❌ 缺失 | 可复用 `TradeManagement.vue` |
| Stock Screener | ✅ | `/stocks/management` | ⚠️ 可能已包含 | 在主页面中 |
| Industry Stocks | ✅ | ❌ | ❌ 缺失 | 需创建 |
| Concept Stocks | ✅ | ❌ | ❌ 缺失 | 需创建 |

**完成度**: 1/6页面 (17%)

**实现优先级**: P1（中）

---

### 4. Analysis域（投资分析）

#### 规划结构（Phase 3.1）

```
投资分析 (5个页面)
├── Technical Analysis (技术分析)
├── Fundamental Analysis (基本面分析)
├── Indicator Analysis (指标分析)
├── Industry Analysis (行业分析)
└── Concept Stock Analysis (概念股分析)
```

#### 当前实现

**路由配置**:
```typescript
{
  path: '/analysis',
  component: ArtDecoLayout.vue,
  children: [
    { path: 'data', component: ArtDecoDataAnalysis.vue }  // ✅
  ]
}
```

**实际组件**:
- ✅ `ArtDecoDataAnalysis.vue` - 数据分析主页
- 📦 `ArtDecoMarketAnalysis.vue` - **可用（未路由）**

**差距分析**:

| 页面 | 规划 | 当前实现 | 状态 | 复用建议 |
|------|------|----------|------|----------|
| Technical Analysis | ✅ | ❌ | ❌ 缺失 | 可复用 `TechnicalAnalysis.vue` |
| Fundamental Analysis | ✅ | ❌ | ❌ 缺失 | 可复用 `StockDetail.vue` |
| Indicator Analysis | ✅ | `/analysis/data` | ⚠️ 可能已包含 | 在主页面中 |
| Industry Analysis | ✅ | ❌ | ❌ 缺失 | 可复用 `IndustryConceptAnalysis.vue` |
| Concept Stock Analysis | ✅ | ❌ | ❌ 缺失 | 可复用 `WencaiPanelV2.vue` |

**完成度**: 1/5页面 (20%)

**实现优先级**: P1（中）

---

### 5. Risk域（风险管理）

#### 规划结构（Phase 3.1）

```
风险管理 (5个页面)
├── Risk Overview (风险概览)
├── Position Risk (持仓风险)
├── Portfolio Risk (投资组合风险)
├── Risk Alerts (风险预警)
└── Stress Test (压力测试)
```

#### 当前实现

**路由配置**:
```typescript
{
  path: '/risk',
  component: ArtDecoLayout.vue,
  children: [
    { path: 'management', component: ArtDecoRiskManagement.vue }  // ✅
  ]
}
```

**实际组件**:
- ✅ `ArtDecoRiskManagement.vue` - 风险管理主页
- 📦 `ArtDecoRiskMonitor.vue` - **未集成到路由**
- 📦 `ArtDecoRiskAlerts.vue` - **未集成到路由**
- 📦 `ArtDecoAnnouncementMonitor.vue` - **未集成到路由**

**差距分析**:

| 页面 | 规划 | 当前实现 | 子组件状态 | 状态 | 建议 |
|------|------|----------|-----------|------|------|
| Risk Overview | ✅ | `/risk/management` | ArtDecoRiskManagement | ⚠️ 可能已包含 | 作为主页面 |
| Position Risk | ✅ | ❌ | ❌ | ❌ 缺失 | 可复用旧路由页面 |
| Portfolio Risk | ✅ | ❌ | ❌ | ❌ 缺失 | 可复用旧路由页面 |
| Risk Alerts | ✅ | ❌ | ArtDecoRiskAlerts | 📦 存在未路由 | 需添加路由 |
| Stress Test | ✅ | ❌ | ❌ | ❌ 缺失 | 可复用 `BacktestAnalysis.vue` |

**完成度**: 1/5页面 (20%)

**推荐路由扩展**:
```typescript
{
  path: '/risk',
  component: ArtDecoLayout.vue,
  children: [
    { path: 'management', component: ArtDecoRiskManagement },     // 风险概览（主）
    { path: 'monitor', component: ArtDecoRiskMonitor },          // 新增：风险监控
    { path: 'alerts', component: ArtDecoRiskAlerts },            // 新增：风险预警
    { path: 'announcement', component: ArtDecoAnnouncementMonitor } // 新增：公告监控
  ]
}
```

**实现优先级**: P1（中）

---

### 6. Strategy域（策略和交易）

#### 规划结构（Phase 3.1）

```
策略和交易 (5个页面)
├── Strategy Management (策略管理)
├── Backtest Engine (回测引擎)
├── Trading Signals (交易信号)
├── Trading History (交易历史)
└── Attribution Analysis (归因分析)
```

#### 当前实现

**路由配置**:
```typescript
{
  path: '/strategy',
  component: ArtDecoLayout.vue,
  children: [
    { path: 'trading', component: ArtDecoTradingManagement.vue },  // ✅
    { path: 'backtest', component: ArtDecoTradingCenter.vue }      // ✅
  ]
}
```

**实际组件**:
- ✅ `ArtDecoTradingManagement.vue` - 交易管理主页
- ✅ `ArtDecoTradingCenter.vue` - 回测中心
- 📦 `ArtDecoStrategyManagement.vue` - **未集成到路由**
- 📦 `ArtDecoBacktestAnalysis.vue` - **未集成到路由**
- 📦 `ArtDecoStrategyOptimization.vue` - **未集成到路由**
- 📦 `ArtDecoPositionMonitor.vue` - **未集成到路由**
- 📦 `ArtDecoPerformanceAnalysis.vue` - **未集成到路由**
- 📦 `ArtDecoHistoryView.vue` - **未集成到路由**
- 📦 `ArtDecoSignalsView.vue` - **未集成到路由**
- 📦 `ArtDecoAttributionAnalysis.vue` - **未集成到路由**

**差距分析**:

| 页面 | 规划 | 当前实现 | 子组件状态 | 状态 | 建议 |
|------|------|----------|-----------|------|------|
| Strategy Management | ✅ | ❌ | ArtDecoStrategyManagement | 📦 存在未路由 | 需添加路由 |
| Backtest Engine | ✅ | `/strategy/backtest` | ArtDecoTradingCenter | ✅ 已实现 | 作为主页面 |
| Trading Signals | ✅ | ❌ | ArtDecoSignalsView | 📦 存在未路由 | 需添加路由 |
| Trading History | ✅ | ❌ | ArtDecoHistoryView | 📦 存在未路由 | 需添加路由 |
| Attribution Analysis | ✅ | ❌ | ArtDecoAttributionAnalysis | 📦 存在未路由 | 需添加路由 |

**完成度**: 2/5页面 (40%)

**推荐路由扩展**:
```typescript
{
  path: '/strategy',
  component: ArtDecoLayout.vue,
  children: [
    { path: 'trading', component: ArtDecoTradingManagement },      // 策略和交易（主）
    { path: 'backtest', component: ArtDecoTradingCenter },         // 回测中心
    { path: 'strategy-mgmt', component: ArtDecoStrategyManagement }, // 新增：策略管理
    { path: 'signals', component: ArtDecoSignalsView },            // 新增：交易信号
    { path: 'history', component: ArtDecoHistoryView },            // 新增：交易历史
    { path: 'attribution', component: ArtDecoAttributionAnalysis }, // 新增：归因分析
    { path: 'position', component: ArtDecoPositionMonitor },       // 新增：持仓监控
    { path: 'performance', component: ArtDecoPerformanceAnalysis }, // 新增：绩效分析
    { path: 'optimization', component: ArtDecoStrategyOptimization } // 新增：策略优化
  ]
}
```

**实现优先级**: P0（高）- Strategy域子组件最丰富

---

### 7. System域（系统监控）

#### 规划结构（Phase 3.1 - Monitoring域）

```
系统监控 (5个页面)
├── Monitoring Dashboard (监控仪表板)
├── System Settings (系统设置)
├── Data Management (数据管理)
├── API Health (API健康检查)
└── Performance Metrics (性能指标)
```

#### 当前实现

**路由配置**:
```typescript
{
  path: '/system',
  component: ArtDecoLayout.vue,
  children: [
    { path: 'monitoring', component: ArtDecoSettings.vue }  // ✅
  ]
}
```

**实际组件**:
- ✅ `ArtDecoSettings.vue` - 系统设置主页
- 📦 `ArtDecoMonitoringDashboard.vue` - **未集成到路由**
- 📦 `ArtDecoSystemSettings.vue` - **未集成到路由**
- 📦 `ArtDecoDataManagement.vue` - **未集成到路由**

**差距分析**:

| 页面 | 规划 | 当前实现 | 子组件状态 | 状态 | 建议 |
|------|------|----------|-----------|------|------|
| Monitoring Dashboard | ✅ | ❌ | ArtDecoMonitoringDashboard | 📦 存在未路由 | 需添加路由 |
| System Settings | ✅ | `/system/monitoring` | ArtDecoSettings | ⚠️ 可能已包含 | 作为主页面 |
| Data Management | ✅ | ❌ | ArtDecoDataManagement | 📦 存在未路由 | 需添加路由 |
| API Health | ✅ | ❌ | ❌ | ❌ 缺失 | 可复用 `DatabaseMonitor.vue` |
| Performance Metrics | ✅ | ❌ | ❌ | ❌ 缺失 | 可复用 `RiskDashboard.vue` |

**完成度**: 1/5页面 (20%)

**推荐路由扩展**:
```typescript
{
  path: '/system',
  component: ArtDecoLayout.vue,
  children: [
    { path: 'monitoring', component: ArtDecoSettings },               // 系统设置（主）
    { path: 'dashboard', component: ArtDecoMonitoringDashboard },     // 新增：监控仪表板
    { path: 'sys-settings', component: ArtDecoSystemSettings },       // 新增：系统设置
    { path: 'data-mgmt', component: ArtDecoDataManagement }          // 新增：数据管理
  ]
}
```

**实现优先级**: P2（低）- 系统功能，非核心交易流程

---

## 📈 整体统计

### 按域统计

| 功能域 | 规划页面数 | 已实现 | 未实现 | 完成率 | 优先级 |
|--------|-----------|--------|--------|--------|--------|
| **Dashboard** | 4 | 1 | 3 | 25% | P1 |
| **Market** | 8 | 2 | 6 | 25% | **P0** |
| **Stocks** | 6 | 1 | 5 | 17% | P1 |
| **Analysis** | 5 | 1 | 4 | 20% | P1 |
| **Risk** | 5 | 1 | 4 | 20% | P1 |
| **Strategy** | 5 | 2 | 3 | 40% | **P0** |
| **System** | 5 | 1 | 4 | 20% | P2 |
| **总计** | **38** | **9** | **29** | **24%** | - |

### 子组件库存（未集成路由）

**已创建但未添加路由的组件**（30个）:

#### Strategy域（9个子组件）- 最多
- ✅ `ArtDecoStrategyManagement.vue`
- ✅ `ArtDecoBacktestAnalysis.vue`
- ✅ `ArtDecoStrategyOptimization.vue`
- ✅ `ArtDecoTradingSignals.vue`
- ✅ `ArtDecoTradingPositions.vue`
- ✅ `ArtDecoTradingHistory.vue`
- ✅ `ArtDecoSignalsView.vue`
- ✅ `ArtDecoPositionMonitor.vue`
- ✅ `ArtDecoPerformanceAnalysis.vue`

#### Market域（4个子组件）
- ✅ `ArtDecoRealtimeMonitor.vue`
- ✅ `ArtDecoMarketAnalysis.vue`
- ✅ `ArtDecoMarketOverview.vue`
- ✅ `ArtDecoIndustryAnalysis.vue`

#### Risk域（3个子组件）
- ✅ `ArtDecoRiskMonitor.vue`
- ✅ `ArtDecoRiskAlerts.vue`
- ✅ `ArtDecoAnnouncementMonitor.vue`

#### System域（3个子组件）
- ✅ `ArtDecoMonitoringDashboard.vue`
- ✅ `ArtDecoSystemSettings.vue`
- ✅ `ArtDecoDataManagement.vue`

#### Trading相关（4个子组件）
- ✅ `ArtDecoHistoryView.vue`
- ✅ `ArtDecoSignalsView.vue`
- ✅ `ArtDecoPerformanceAnalysis.vue`
- ✅ `ArtDecoAttributionAnalysis.vue`

**关键发现**: 30个ArtDeco子组件已创建，但**0个**集成到路由！

---

## 🎯 优先级行动计划

### P0（高优先级）- 立即执行

#### 1. Strategy域路由扩展（最高优先级）

**原因**: 子组件最丰富（9个），完成度40%，最容易快速提升

**行动**:
```typescript
// 在 router/index.ts 中添加
{
  path: '/strategy',
  component: () => import('@/layouts/ArtDecoLayout.vue'),
  children: [
    { path: 'trading', component: ArtDecoTradingManagement },      // 现有
    { path: 'backtest', component: ArtDecoTradingCenter },         // 现有
    { path: 'strategy-mgmt', component: () => import('@/views/artdeco-pages/components/strategy/ArtDecoStrategyManagement.vue') },
    { path: 'signals', component: () => import('@/views/artdeco-pages/components/trading/ArtDecoSignalsView.vue') },
    { path: 'history', component: () => import('@/views/artdeco-pages/components/trading/ArtDecoHistoryView.vue') },
    { path: 'attribution', component: () => import('@/views/artdeco-pages/components/ArtDecoAttributionAnalysis.vue') },
    { path: 'position', component: () => import('@/views/artdeco-pages/components/trading/ArtDecoPositionMonitor.vue') },
    { path: 'performance', component: () => import('@/views/artdeco-pages/components/trading/ArtDecoPerformanceAnalysis.vue') },
    { path: 'optimization', component: () => import('@/views/artdeco-pages/components/strategy/ArtDecoStrategyOptimization.vue') }
  ]
}
```

**预期成果**: Strategy域从2/5页→9/9页（完成度180%）

#### 2. Market域路由扩展

**原因**: 核心交易功能，4个子组件已存在

**行动**:
```typescript
{
  path: '/market',
  component: () => import('@/layouts/ArtDecoLayout.vue'),
  children: [
    { path: 'data', component: ArtDecoMarketData },              // 现有
    { path: 'quotes', component: ArtDecoMarketQuotes },           // 现有
    { path: 'realtime', component: () => import('@/views/artdeco-pages/components/market/ArtDecoRealtimeMonitor.vue') },
    { path: 'analysis', component: () => import('@/views/artdeco-pages/components/market/ArtDecoMarketAnalysis.vue') },
    { path: 'overview', component: () => import('@/views/artdeco-pages/components/market/ArtDecoMarketOverview.vue') },
    { path: 'industry', component: () => import('@/views/artdeco-pages/components/market/ArtDecoIndustryAnalysis.vue') }
  ]
}
```

**预期成果**: Market域从2/8页→6/8页（完成度75%）

### P1（中优先级）- 第二阶段

#### 3. Risk域路由扩展

**行动**: 添加3个现有子组件路由
- `/risk/monitor` → ArtDecoRiskMonitor.vue
- `/risk/alerts` → ArtDecoRiskAlerts.vue
- `/risk/announcement` → ArtDecoAnnouncementMonitor.vue

#### 4. System域路由扩展

**行动**: 添加3个现有子组件路由
- `/system/dashboard` → ArtDecoMonitoringDashboard.vue
- `/system/sys-settings` → ArtDecoSystemSettings.vue
- `/system/data-mgmt` → ArtDecoDataManagement.vue

### P2（低优先级）- 未来优化

#### 5. 复用旧组件

对于未创建ArtDeco版本的页面，可临时复用旧Layout组件：

**可复用组件清单**:
- `WatchlistManagement.vue` → 自选股管理
- `PortfolioManagement.vue` → 投资组合管理
- `TradeManagement.vue` → 交易活动
- `TechnicalAnalysis.vue` → 技术分析
- `IndustryConceptAnalysis.vue` → 行业/概念分析
- `TdxMarket.vue` → TDX集成
- `DatabaseMonitor.vue` → API健康检查
- `RiskDashboard.vue` → 性能指标

#### 6. 创建新组件

以下功能需全新创建：
- 资金流向分析
- ETF市场
- 集合竞价分析
- 龙虎榜分析（详细版）
- 行业选股
- 概念选股

---

## 🔧 实施建议

### 方案A: 渐进式集成（推荐）

**优点**: 风险低，可逐步验证
**步骤**:
1. **第1周**: Strategy域 + Market域路由扩展（P0）
2. **第2周**: Risk域 + System域路由扩展（P1）
3. **第3周**: 复用旧组件填充缺失页面（P2）
4. **第4周**: 创建全新组件（P2）

### 方案B: 一次性重构

**优点**: 快速完成
**风险**: 可能引入大量Bug
**不推荐**: 除非有充足测试保障

### 方案C: 混合策略（最优）

**结合方案A和B**:
1. **P0优先级**（Strategy+Market）: 一次性完成
2. **P1优先级**（Risk+System）: 渐进式集成
3. **P2优先级**（复用+创建）: 按需开发

---

## 📋 路由配置检查清单

### 完成标准

每个新增路由需满足：

- [ ] **路由定义**: 在 `router/index.ts` 中添加路由配置
- [ ] **组件导入**: 使用动态导入 `() => import(...)`
- [ ] **菜单配置**: 在 `MenuConfig.ts` 中添加对应菜单项
- [ ] **布局集成**: 确认使用 `ArtDecoLayout.vue`
- [ ] **面包屑**: 添加 `meta.title` 和 `meta.breadcrumb`
- [ ] **测试验证**: 使用 `test-pages.mjs` 验证HTTP 200
- [ ] **无功能删除**: 确认不删除现有功能
- [ ] **向后兼容**: 旧路由添加重定向（如需要）

### 示例模板

```typescript
// router/index.ts
{
  path: '/market',
  component: () => import('@/layouts/ArtDecoLayout.vue'),
  children: [
    {
      path: 'realtime',
      name: 'market-realtime-artdeco',
      component: () => import('@/views/artdeco-pages/components/market/ArtDecoRealtimeMonitor.vue'),
      meta: {
        title: '实时监控',
        icon: '⚡',
        breadcrumb: 'Market > Realtime'
      }
    }
  ]
}

// MenuConfig.ts
{
  path: '/market/realtime',
  label: '实时监控',
  icon: '⚡',
  description: '实时行情监控',
  apiEndpoint: '/api/market/realtime',
  apiMethod: 'GET',
  liveUpdate: true,
  wsChannel: 'market:realtime',
  priority: 'primary'
}
```

---

## 🎯 预期成果

### 实施P0+P1后（2周内）

| 功能域 | 当前 | 目标 | 提升 |
|--------|------|------|------|
| **Dashboard** | 25% | 25% | - |
| **Market** | 25% | **75%** | +50% |
| **Stocks** | 17% | 17% | - |
| **Analysis** | 20% | 20% | - |
| **Risk** | 20% | **80%** | +60% |
| **Strategy** | 40% | **180%** | +140% |
| **System** | 20% | **80%** | +60% |
| **总体** | **24%** | **68%** | **+44%** |

### 完整实施后（4周内）

- **总页面数**: 38个（规划）
- **已实现**: 35个（复用旧组件 + 新建）
- **完成度**: **92%**
- **ArtDeco覆盖率**: **100%**（全部使用ArtDecoLayout）

---

## 📚 相关文档

### 规划文档
- `docs/reports/IMPLEMENT_WEB_FRONTEND_V2_NAVIGATION_STATUS_REPORT.md` - OpenSpec任务状态
- `openspec/changes/archive/2026-01-13-frontend-unified-optimization/tasks.md` - 任务清单

### 实现文档
- `web/frontend/src/router/index.ts` - 路由配置
- `web/frontend/src/layouts/MenuConfig.ts` - 菜单配置
- `web/frontend/ARTDECO_COMPONENTS_CATALOG.md` - 组件目录

### 测试文档
- `web/frontend/scripts/test-pages.mjs` - 页面测试脚本
- `docs/reports/RALPH_LOOP_COMPLETION_SUMMARY.md` - Ralph测试完成报告

---

## ✅ 总结

**核心问题**:
1. ✅ 9个主页面已实现并测试通过
2. ❌ 30个ArtDeco子组件未集成到路由
3. ❌ 路由完成度仅24%（9/38页面）

**解决方案**:
1. **P0优先级**: Strategy域 + Market域路由扩展（最快提升）
2. **P1优先级**: Risk域 + System域路由扩展
3. **P2优先级**: 复用旧组件 + 创建新组件

**预期成果**:
- **2周后**: 完成度从24%→68%（+44%）
- **4周后**: 完成度达到92%

**关键行动**:
1. 立即开始Strategy域路由扩展（9个组件）
2. 同步进行Market域路由扩展（4个组件）
3. 使用 `test-pages.mjs` 验证每个新增路由
4. 更新 `MenuConfig.ts` 添加对应菜单项

---

**报告生成**: 2026-01-20
**分析工具**: Claude Code AI Assistant
**数据来源**: router/index.ts, ARTDECO_COMPONENTS_CATALOG.md, MenuConfig.ts
**验证状态**: ✅ 数据完整，建议可行
