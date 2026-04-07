# MyStocks Web前端V2导航优化 - 实施路线图

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。


**更新日期**: 2026-01-20
**任务类型**: 路由集成（复用现有组件）
**核心策略**: 从"创建组件"转变为"集成路由"
**预期成果**: 完成度从24%→92%（3周）

---

## 📊 执行摘要

### 当前状态
- ✅ **已完成**: ArtDeco设计系统（64组件）、MenuConfig优化、PM2测试
- 🔄 **核心问题**: 30个ArtDeco子组件未集成到路由
- 📈 **完成度**: 24%（9/38规划页面）
- 🎯 **最快路径**: Strategy域（9子组件）+ Market域（4子组件）

### 实施策略调整

**原始计划** (2026-01-12):
```
创建动态侧边栏 → 创建8个Market页面 → 创建6个Stocks页面
预计时间: 4周
工作重心: 新建组件
```

**更新计划** (2026-01-20):
```
集成现有组件路由 → 配置菜单 → 测试验证
预计时间: 3周
工作重心: 路由集成（复用19个现有组件）
```

### 关键变化

| 方面 | 原计划 | 更新计划 | 变化原因 |
|------|--------|----------|----------|
| **组件创建** | 14个新组件 | 3-6个新组件 | ArtDeco组件已存在 |
| **主要工作** | 创建组件 | 集成路由 | 优先复用现有资源 |
| **第1周** | Market域8页面 | Strategy+Market域13页面 | Strategy域组件更丰富 |
| **预期工期** | 4周 | 3周 | 路由集成比创建快 |
| **完成度** | 100%新建 | 92%（集成+新建） | 实际需求调整 |

---

## 🎯 三周实施计划

### Week 1: P0优先级 - Strategy和Market域

**目标**: 完成度从24%→68%（+44%）

#### Day 1-2: Strategy域（9个子组件）

**集成清单**:
```
现有: 2个页面（trading, backtest）
新增: 7个路由
- /strategy/strategy-mgmt → ArtDecoStrategyManagement.vue
- /strategy/signals → ArtDecoSignalsView.vue
- /strategy/history → ArtDecoHistoryView.vue
- /strategy/attribution → ArtDecoAttributionAnalysis.vue
- /strategy/position → ArtDecoPositionMonitor.vue
- /strategy/performance → ArtDecoPerformanceAnalysis.vue
- /strategy/optimization → ArtDecoStrategyOptimization.vue

完成度: 40% → 180% (2/5 → 9/9页面)
```

**工作量**: 2天
- Day 1: 路由配置 + 菜单更新
- Day 2: 测试验证 + 问题修复

**验证**:
```bash
node scripts/test-pages.mjs  # 9个新页面全部HTTP 200
pm2 logs mystocks-frontend-prod  # 无错误
```

#### Day 3-4: Market域（4个子组件）

**集成清单**:
```
现有: 2个页面（data, quotes）
新增: 4个路由
- /market/realtime → ArtDecoRealtimeMonitor.vue
- /market/analysis → ArtDecoMarketAnalysis.vue
- /market/overview → ArtDecoMarketOverview.vue
- /market/industry → ArtDecoIndustryAnalysis.vue

完成度: 25% → 75% (2/8 → 6/8页面)
```

**工作量**: 2天
- Day 3: 路由配置 + WebSocket配置
- Day 4: 实时数据测试 + 性能验证

#### Day 5: 集成测试

**测试范围**:
- 16个页面全部HTTP 200
- 菜单跳转流畅
- 无控制台错误
- PM2进程稳定

**Week 1成果**:
- ✅ 11个新路由配置完成
- ✅ 完成度: 24% → 68%
- ✅ Strategy域: 9/9页面
- ✅ Market域: 6/8页面

---

### Week 2: P1优先级 - Risk和System域

**目标**: 完成度从68%→85%（+17%）

#### Day 6-7: Risk域（3个子组件）

**集成清单**:
```
现有: 1个页面（management）
新增: 3个路由
- /risk/monitor → ArtDecoRiskMonitor.vue
- /risk/alerts → ArtDecoRiskAlerts.vue
- /risk/announcement → ArtDecoAnnouncementMonitor.vue

完成度: 20% → 80% (1/5 → 4/5页面)
```

**特殊配置**:
- WebSocket实时预警
- 风险数据可视化
- 公告监控功能

#### Day 8-9: System域（3个子组件）

**集成清单**:
```
现有: 1个页面（monitoring）
新增: 3个路由
- /system/dashboard → ArtDecoMonitoringDashboard.vue
- /system/sys-settings → ArtDecoSystemSettings.vue
- /system/data-mgmt → ArtDecoDataManagement.vue

完成度: 20% → 80% (1/5 → 4/5页面)
```

#### Day 10: 集成测试和优化

**测试范围**:
- 22个页面全部HTTP 200
- WebSocket连接正常
- 实时数据更新
- 性能优化

**Week 2成果**:
- ✅ 6个新路由配置完成
- ✅ 完成度: 68% → 85%
- ✅ Risk域: 4/5页面
- ✅ System域: 4/5页面

---

### Week 3: P2优先级 - 复用和创建

**目标**: 完成度从85%→92%+（+7%）

#### Day 11-12: 复用现有组件

**复用清单**（10个）:
```
Dashboard域: 3个
- /dashboard/watchlist → Stocks.vue (复用)
- /dashboard/portfolio → PortfolioManagement.vue (复用)
- /dashboard/activity → TradeManagement.vue (复用)

Analysis域: 2个
- /analysis/technical → TechnicalAnalysis.vue (复用)
- /analysis/industry → IndustryConceptAnalysis.vue (复用)

Market域: 1个
- /market/tdx → TdxMarket.vue (复用, 临时)

System域: 2个
- /system/api → DatabaseMonitor.vue (复用)
- /system/performance → RiskDashboard.vue (复用)

标记为"临时使用"，待ArtDeco版本替换
```

#### Day 13-14: 创建新组件（按需）

**创建清单**（3-6个）:
```
必需创建（3个）:
1. ArtDecoCapitalFlow.vue - 资金流向分析
2. ArtDecoETFMarket.vue - ETF市场
3. ArtDecoAuctionAnalysis.vue - 集合竞价分析

可选创建（3个）:
4. ArtDecoLHBAnalysis.vue - 龙虎榜分析（已有部分）
5. ArtDecoIndustryScreener.vue - 行业选股
6. ArtDecoConceptScreener.vue - 概念选股
```

**创建原则**:
- 复用ArtDeco基础组件（Card, Chart, Table）
- 集成现有后端API
- 遵循ArtDeco设计规范

#### Day 15: 端到端测试

**测试范围**:
- 35+页面全部HTTP 200
- 所有用户流程测试
- 性能指标达标
- 浏览器兼容性

**Week 3成果**:
- ✅ 10个组件复用完成
- ✅ 3-6个新组件创建完成
- ✅ 完成度: 85% → 92%+
- ✅ 所有域功能完整

---

## 📈 预期成果对比

### 按域统计

| 功能域 | 原始规划 | 当前 | Week 1 | Week 2 | Week 3 | 最终完成度 |
|--------|----------|------|--------|--------|--------|-----------|
| **Dashboard** | 4 | 1 | 1 | 1 | 4 | **100%** |
| **Market** | 8 | 2 | **6** | 6 | 7 | **88%** |
| **Stocks** | 6 | 1 | 1 | 1 | 3 | **50%** |
| **Analysis** | 5 | 1 | 1 | 1 | 3 | **60%** |
| **Risk** | 5 | 1 | 1 | **4** | 4 | **80%** |
| **Strategy** | 5 | 2 | **9** | 9 | 9 | **180%** ✅ |
| **System** | 5 | 1 | 1 | **4** | 6 | **120%** ✅ |
| **总计** | **38** | **9** | **20** | **26** | **36** | **95%** |

### 按周统计

| 周次 | 新增路由 | 累计路由 | 完成度 | 主要工作 |
|------|----------|----------|--------|----------|
| **Week 0** | 0 | 9 | 24% | 初始状态 |
| **Week 1** | +11 | 20 | **53%** | Strategy+Market域 |
| **Week 2** | +6 | 26 | **68%** | Risk+System域 |
| **Week 3** | +10 | 36 | **95%** | 复用+创建 |

**注**: Strategy和System域超过100%是因为实现的页面数超过原规划

---

## 🔧 技术实施要点

### 路由集成模板

```typescript
// router/index.ts - 标准路由配置
{
  path: '/domain',
  component: () => import('@/layouts/ArtDecoLayout.vue'),
  children: [
    {
      path: 'subpage',
      name: 'domain-subpage',
      component: () => import('@/views/artdeco-pages/components/.../Component.vue'),
      meta: {
        title: '页面标题',
        icon: '🎯',
        breadcrumb: 'Domain > Subpage',
        requiresAuth: false
      }
    }
  ]
}
```

### 菜单配置模板

```typescript
// MenuConfig.ts - 标准菜单配置
{
  path: '/domain/subpage',
  label: '页面名称',
  icon: '🎯',
  description: '简短描述（10-12字）',
  apiEndpoint: '/api/domain/endpoint',
  apiMethod: 'GET',
  liveUpdate: true,
  wsChannel: 'domain:channel',
  priority: 'primary' | 'secondary' | 'tertiary'
}
```

### 验证流程

```bash
# 1. 添加路由配置
vim router/index.ts

# 2. 添加菜单配置
vim layouts/MenuConfig.ts

# 3. 测试页面访问
node scripts/test-pages.mjs

# 4. 检查浏览器控制台
# 手动访问页面，确认无错误

# 5. PM2重启验证
pm2 restart mystocks-frontend-prod
pm2 logs mystocks-frontend-prod --lines 20
```

---

## 🎯 成功标准

### Phase 1成功标准（Week 1）

- ✅ 11个新路由配置完成
- ✅ Strategy域9个页面可访问
- ✅ Market域6个页面可访问
- ✅ 所有页面HTTP 200响应
- ✅ 浏览器控制台无错误
- ✅ PM2进程稳定运行

### Phase 2成功标准（Week 2）

- ✅ 6个新路由配置完成
- ✅ Risk域4个页面可访问
- ✅ System域4个页面可访问
- ✅ WebSocket实时数据正常
- ✅ 整体完成度达到68%→85%

### Phase 3成功标准（Week 3）

- ✅ 10个组件复用完成
- ✅ 3-6个新组件创建完成
- ✅ 所有用户流程测试通过
- ✅ 性能指标达标（首屏<2s，切换<200ms）
- ✅ 整体完成度达到92%+

---

## ⚠️ 风险和缓解措施

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| **组件依赖缺失** | 中 | 中 | 提前验证组件导入路径 |
| **路由冲突** | 低 | 中 | 使用命名路由，添加重定向 |
| **API集成问题** | 低 | 低 | 复用已验证的API端点 |
| **菜单配置错误** | 低 | 低 | TypeScript类型检查 |
| **性能下降** | 低 | 低 | 懒加载，代码分割 |
| **WebSocket连接失败** | 中 | 低 | 添加降级处理 |

---

## 📚 相关文档

### 规划文档
- `openspec/changes/implement-web-frontend-v2-navigation/proposal-updated.md` - 更新版提案
- `openspec/changes/implement-web-frontend-v2-navigation/tasks-updated.md` - 更新版任务清单

### 分析文档
- `docs/reports/ARTDECO_NAVIGATION_GAP_ANALYSIS.md` - 路由差距分析
- `docs/reports/IMPLEMENT_WEB_FRONTEND_V2_NAVIGATION_STATUS_REPORT.md` - 原始状态报告
- `docs/reports/MENU_DESCRIPTION_OPTIMIZATION_REPORT.md` - 菜单优化报告

### 实施文档
- `web/frontend/src/router/index.ts` - 路由配置
- `web/frontend/src/layouts/MenuConfig.ts` - 菜单配置
- `web/frontend/ARTDECO_COMPONENTS_CATALOG.md` - ArtDeco组件目录

### 测试文档
- `web/frontend/scripts/test-pages.mjs` - 页面测试脚本
- `docs/reports/RALPH_LOOP_COMPLETION_SUMMARY.md` - Ralph测试报告

---

## 🚀 立即行动

### Week 1 Day 1 - 第一步

**上午**（2小时）:
1. ✅ 备份 `router/index.ts` 和 `MenuConfig.ts`
2. ✅ 分析Strategy域现有路由结构
3. ✅ 验证9个子组件文件存在
4. ✅ 创建路由配置草稿

**下午**（4小时）:
1. ✅ 添加7个Strategy域新路由
2. ✅ 更新MenuConfig.ts菜单配置
3. ✅ 本地测试验证
4. ✅ PM2部署验证

**验证命令**:
```bash
# 验证组件存在
ls -la web/frontend/src/views/artdeco-pages/components/strategy/
ls -la web/frontend/src/views/artdeco-pages/components/trading/

# 测试页面
cd web/frontend
node scripts/test-pages.mjs

# PM2验证
pm2 restart mystocks-frontend-prod
pm2 logs mystocks-frontend-prod --lines 50
```

**预期Day 1成果**:
- ✅ Strategy域 7个新路由配置完成
- ✅ Strategy域 9个页面全部可访问
- ✅ 所有页面HTTP 200响应
- ✅ 完成度: 24% → 40%

---

## 📊 进度跟踪

### 实时进度仪表板

```
══════════════════════════════════════════════════════════
Week 1: P0优先级 (Strategy + Market域)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Day 1-2: Strategy域 ████████░░ 80% (8/10 tasks)
Day 3-4: Market域   ░░░░░░░░░░░ 0% (0/10 tasks)
Day 5:   集成测试   ░░░░░░░░░░░ 0% (0/5 tasks)

Week 1进度: ██████░░░░░░ 40% (8/25 tasks)
完成度目标: 24% → 68%
══════════════════════════════════════════════════════════

Week 2: P1优先级 (Risk + System域)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
待开始

Week 3: P2优先级 (复用 + 创建)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
待开始
```

### 里程碑

- [ ] **M1** (Day 2): Strategy域9个页面完成 - 完成度40%
- [ ] **M2** (Day 4): Market域6个页面完成 - 完成度53%
- [ ] **M3** (Day 5): Week 1集成测试完成 - 完成度68%
- [ ] **M4** (Day 9): Risk+System域完成 - 完成度85%
- [ ] **M5** (Day 14): 复用组件完成 - 完成度90%
- [ ] **M6** (Day 15): 端到端测试完成 - 完成度92%+

---

**路线图版本**: v2.0 (Updated 2026-01-20)
**更新原因**: 结合ArtDeco组件和API实际情况
**核心变化**: 从"创建组件"转变为"集成路由"
**预期工期**: 3周（原计划4周）
**完成度目标**: 24% → 92%+
**立即开始**: Week 1 Day 1 - Strategy域路由扩展
