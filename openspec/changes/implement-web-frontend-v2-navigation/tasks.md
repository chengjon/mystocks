# Implementation Tasks for Web Frontend V2 Navigation（2026-01-21更新版）

**更新日期**: 2026-01-21
**任务性质**: 路由集成 + API对接
**核心策略**: 复用现有29个ArtDeco组件
**预期成果**: 完成度从24%→92%（3周）

---

## 📋 任务概览

### 当前状态
- ✅ **ArtDeco组件**: 29个组件已实现，等待路由集成
- 🔄 **路由系统**: 基础框架就绪（ArtDecoLayout）
- ✅ **后端API**: 120+ API端点可用
- 📈 **完成度**: 24% → 目标92%

### 组件分布
- **Trading域**: 6个组件
- **Strategy域**: 3个组件
- **Market域**: 6个组件
- **Risk域**: 4个组件
- **System域**: 4个组件
- **其他**: 6个组件

---

## Phase 1: P0优先级 - Trading和Strategy域（第1周）

### Week 1, Day 1-2: Trading域路由集成

#### Task 1.1: 环境准备
- [ ] 备份当前路由配置 `cp src/router/index.ts src/router/index.ts.backup`
- [ ] 验证Trading域组件文件存在
  ```bash
  ls -la web/frontend/src/views/artdeco-pages/components/trading/
  ```
- [ ] 检查相关API端点可用性
  ```bash
  curl -s http://localhost:8000/api/trading/signals | jq '.success'
  curl -s http://localhost:8000/api/trading/history | jq '.success'
  ```

#### Task 1.2: 创建Trading域路由结构
- [ ] 路由1: `/trading/signals` → ArtDecoTradingSignals.vue
- [ ] 路由2: `/trading/history` → ArtDecoTradingHistory.vue
- [ ] 路由3: `/trading/positions` → ArtDecoTradingPositions.vue
- [ ] 路由4: `/trading/stats` → ArtDecoTradingStats.vue

**路由配置代码**：
```typescript
// router/index.ts - Trading域扩展
{
  path: '/trading',
  component: () => import('@/layouts/ArtDecoLayout.vue'),
  redirect: '/trading/signals',
  children: [
    {
      path: 'signals',
      name: 'trading-signals',
      component: () => import('@/views/artdeco-pages/components/trading/ArtDecoTradingSignals.vue'),
      meta: {
        title: '交易信号',
        icon: '📡',
        breadcrumb: 'Trading > Signals',
        requiresAuth: false
      }
    },
    {
      path: 'history',
      name: 'trading-history',
      component: () => import('@/views/artdeco-pages/components/trading/ArtDecoTradingHistory.vue'),
      meta: {
        title: '交易历史',
        icon: '📋',
        breadcrumb: 'Trading > History',
        requiresAuth: false
      }
    },
    {
      path: 'positions',
      name: 'trading-positions',
      component: () => import('@/views/artdeco-pages/components/trading/ArtDecoTradingPositions.vue'),
      meta: {
        title: '持仓监控',
        icon: '📊',
        breadcrumb: 'Trading > Positions',
        requiresAuth: false
      }
    },
    {
      path: 'stats',
      name: 'trading-stats',
      component: () => import('@/views/artdeco-pages/components/trading/ArtDecoTradingStats.vue'),
      meta: {
        title: '交易统计',
        icon: '📈',
        breadcrumb: 'Trading > Statistics',
        requiresAuth: false
      }
    }
  ]
}
```

#### Task 1.3: 更新MenuConfig.ts - Trading域
- [ ] 打开 `src/layouts/MenuConfig.ts`
- [ ] 在Trading域添加4个菜单项

**菜单配置模板**：
```typescript
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
},
{
  path: '/trading/history',
  label: '交易历史',
  icon: '📋',
  description: '历史交易记录',
  apiEndpoint: '/api/trading/history',
  apiMethod: 'GET',
  liveUpdate: false,
  wsChannel: undefined,
  priority: 'secondary'
},
{
  path: '/trading/positions',
  label: '持仓监控',
  icon: '📊',
  description: '当前持仓统计',
  apiEndpoint: '/api/api/mtm/portfolio',
  apiMethod: 'GET',
  liveUpdate: false,
  wsChannel: undefined,
  priority: 'secondary'
},
{
  path: '/trading/stats',
  label: '交易统计',
  icon: '📈',
  description: '交易数据分析',
  apiEndpoint: '/api/trading/statistics',
  apiMethod: 'GET',
  liveUpdate: false,
  wsChannel: undefined,
  priority: 'secondary'
}
```

#### Task 1.4: Trading域测试验证
- [ ] 运行自动化测试 `node web/frontend/run-comprehensive-e2e.js`
- [ ] 手动验证4个新页面可访问
- [ ] 检查浏览器控制台无错误
- [ ] 验证ArtDecoLayout正确渲染
- [ ] 确认菜单点击跳转正确

**测试命令**：
```bash
cd web/frontend
npm run type-check
node run-comprehensive-e2e.js
pm2 restart mystocks-frontend-prod
pm2 logs mystocks-frontend-prod --lines 50
```

**预期成果**：Trading域完成度从25%→100%（4/4页面）

---

### Week 1, Day 3-4: Strategy域路由集成

#### Task 1.5: Strategy域环境准备
- [ ] 验证Strategy域组件文件
  ```bash
  ls -la web/frontend/src/views/artdeco-pages/components/strategy/
  ```
- [ ] 检查Strategy API端点
  ```bash
  curl -s http://localhost:8000/api/strategy/list | jq '.success'
  curl -s http://localhost:8000/api/strategy-mgmt/strategies | jq '.success'
  ```

#### Task 1.6: 创建Strategy域路由结构
- [ ] 路由1: `/strategy/management` → ArtDecoStrategyManagement.vue
- [ ] 路由2: `/strategy/optimization` → ArtDecoStrategyOptimization.vue
- [ ] 路由3: `/strategy/backtest` → ArtDecoBacktestAnalysis.vue

**路由配置代码**：
```typescript
{
  path: '/strategy',
  component: () => import('@/layouts/ArtDecoLayout.vue'),
  redirect: '/strategy/management',
  children: [
    {
      path: 'management',
      name: 'strategy-management',
      component: () => import('@/views/artdeco-pages/components/strategy/ArtDecoStrategyManagement.vue'),
      meta: {
        title: '策略管理',
        icon: '⚙️',
        breadcrumb: 'Strategy > Management',
        requiresAuth: false
      }
    },
    {
      path: 'optimization',
      name: 'strategy-optimization',
      component: () => import('@/views/artdeco-pages/components/strategy/ArtDecoStrategyOptimization.vue'),
      meta: {
        title: '策略优化',
        icon: '🎯',
        breadcrumb: 'Strategy > Optimization',
        requiresAuth: false
      }
    },
    {
      path: 'backtest',
      name: 'strategy-backtest',
      component: () => import('@/views/artdeco-pages/components/strategy/ArtDecoBacktestAnalysis.vue'),
      meta: {
        title: '回测分析',
        icon: '🔬',
        breadcrumb: 'Strategy > Backtest',
        requiresAuth: false
      }
    }
  ]
}
```

#### Task 1.7: 更新MenuConfig.ts - Strategy域
- [ ] 在Strategy域添加3个菜单项

**菜单配置模板**：
```typescript
{
  path: '/strategy/management',
  label: '策略管理',
  icon: '⚙️',
  description: '策略配置、测试、管理',
  apiEndpoint: '/api/strategy-mgmt/strategies',
  apiMethod: 'GET',
  liveUpdate: false,
  wsChannel: undefined,
  priority: 'secondary'
},
{
  path: '/strategy/optimization',
  label: '策略优化',
  icon: '🎯',
  description: '参数优化、性能评估',
  apiEndpoint: '/api/strategy/optimize',
  apiMethod: 'POST',
  liveUpdate: false,
  wsChannel: undefined,
  priority: 'secondary'
},
{
  path: '/strategy/backtest',
  label: '回测分析',
  icon: '🔬',
  description: '回测配置、结果分析',
  apiEndpoint: '/api/analysis/backtest',
  apiMethod: 'POST',
  liveUpdate: false,
  wsChannel: undefined,
  priority: 'secondary'
}
```

#### Task 1.8: Strategy域测试验证
- [ ] 运行自动化测试
- [ ] 手动验证3个新页面
- [ ] 检查TypeScript错误数量
- [ ] 验证组件功能正常

**预期成果**：Strategy域完成度从60%→100%（3/3页面）

---

### Week 1, Day 5: Phase 1测试与总结

#### Task 1.9: 综合测试
- [ ] 运行完整测试套件
  ```bash
  cd web/frontend
  npm run type-check
  node run-comprehensive-e2e.js
  ```
- [ ] PM2环境测试
- [ ] 性能测试（页面加载时间<2s）
- [ ] TypeScript错误检查（目标<90）

#### Task 1.10: Phase 1文档
- [ ] 更新路由集成文档
- [ ] 记录遇到的问题和解决方案
- [ ] 更新完成度统计

**预期成果**：Phase 1完成，整体完成度24%→48%

---

## Phase 2: P1优先级 - Market和Risk域（第2周）

### Week 2, Day 1-2: Market域路由集成

#### Task 2.1: Market域组件验证
- [ ] 验证6个Market域组件
- [ ] 检查Market API端点
- [ ] 创建路由配置草稿

#### Task 2.2: 添加Market域路由（6个）
- [ ] `/market/realtime` → ArtDecoRealtimeMonitor.vue
- [ ] `/market/analysis` → ArtDecoMarketAnalysis.vue
- [ ] `/market/overview` → ArtDecoMarketOverview.vue
- [ ] `/market/industry` → ArtDecoIndustryAnalysis.vue
- [ ] `/market/performance` → ArtDecoPerformanceOverview.vue
- [ ] `/market/signals` → ArtDecoSignalMonitoringOverview.vue

#### Task 2.3: 更新Market域菜单配置
- [ ] 添加6个菜单项到MenuConfig.ts
- [ ] 配置实时更新（market域需要WebSocket）
- [ ] 设置API端点映射

#### Task 2.4: Market域测试验证
- [ ] 自动化测试
- [ ] 手动验证
- [ ] 性能测试

**预期成果**：Market域完成度从25%→100%（6/6页面）

### Week 2, Day 3-4: Risk域路由集成

#### Task 2.5: Risk域组件集成
- [ ] 4个Risk域组件路由配置
- [ ] 菜单配置更新
- [ ] 测试验证

**预期成果**：Risk域完成度从20%→100%（4/4页面）

---

## Phase 3: P2优先级 - System域和优化（第3周）

### Week 3: System域 + 最终优化

- System域4个组件集成
- 剩余组件集成
- 全面测试和优化
- TypeScript错误优化（目标<70错误）

---

## 🎯 验收标准

### 功能验收
- [ ] 所有29个组件可通过URL访问
- [ ] 菜单点击正确跳转
- [ ] ArtDecoLayout正确渲染
- [ ] 面包屑导航正确显示

### 质量验收
- [ ] TypeScript错误 < 80
- [ ] 页面加载时间 < 2秒
- [ ] 无浏览器控制台错误
- [ ] PM2进程稳定运行

### 文档验收
- [ ] 路由配置文档更新
- [ ] API集成文档更新
- [ ] 测试报告完成

---

## 📊 进度跟踪

| Phase | 域 | 组件数 | 完成度 | 目标 |
|-------|-----|--------|--------|------|
| Phase 0 | - | - | 24% | - |
| Phase 1 | Trading | 6 | 25% → 100% | +9% |
| Phase 1 | Strategy | 3 | 60% → 100% | +6% |
| Phase 2 | Market | 6 | 25% → 100% | +9% |
| Phase 2 | Risk | 4 | 20% → 100% | +6% |
| Phase 3 | System | 4 | 0% → 100% | +6% |
| **Total** | **All** | **29** | **24% → 92%** | **+68%** |

---

## 🔗 相关资源

- **组件目录**: `web/frontend/ARTDECO_COMPONENTS_CATALOG.md`
- **设计文档**: `docs/api/ARTDECO_TRADING_CENTER_DESIGN.md`
- **API文档**: `docs/api/README_PLATFORM.md`
- **测试脚本**: `web/frontend/run-comprehensive-e2e.js`
- **TypeScript最佳实践**: `docs/guides/Typescript_BEST_PRACTICES.md`
