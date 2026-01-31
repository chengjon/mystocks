# Implementation Tasks for Web Frontend V2 Navigation（更新版）

**更新日期**: 2026-01-20
**任务性质**: 路由集成（非组件创建）
**核心策略**: 复用现有19个ArtDeco子组件
**预期成果**: 完成度从24%→92%（3周）

---

## 📊 任务概览

### 当前状态
- ✅ **已完成**: ArtDeco设计系统（64组件）、MenuConfig优化、PM2测试
- 🔄 **待集成**: 19个ArtDeco子组件到路由
- ❌ **待创建**: 6个新组件（P2优先级）
- 📈 **完成度**: 24% → 目标92%

### 任务优先级说明

- **P0（高）**: Strategy域 + Market域 - 第1周
- **P1（中）**: Risk域 + System域 - 第2周
- **P2（低）**: 复用旧组件 + 创建新组件 - 第3周

---

## Phase 1: P0优先级 - Strategy和Market域（第1周）

### Week 1, Day 1-2: Strategy域路由扩展

#### Task 1.1: 路由配置准备
- [ ] 备份当前 `router/index.ts`
- [ ] 分析现有Strategy域路由结构
- [ ] 确认9个子组件文件路径正确
- [ ] 创建路由配置草稿

**验证标准**:
```bash
# 验证组件文件存在
ls -la web/frontend/src/views/artdeco-pages/components/strategy/
ls -la web/frontend/src/views/artdeco-pages/components/trading/
```

#### Task 1.2: 添加Strategy域路由（7个新路由）
- [ ] 路由1: `/strategy/strategy-mgmt` → ArtDecoStrategyManagement.vue
- [ ] 路由2: `/strategy/signals` → ArtDecoSignalsView.vue
- [ ] 路由3: `/strategy/history` → ArtDecoHistoryView.vue
- [ ] 路由4: `/strategy/attribution` → ArtDecoAttributionAnalysis.vue
- [ ] 路由5: `/strategy/position` → ArtDecoPositionMonitor.vue
- [ ] 路由6: `/strategy/performance` → ArtDecoPerformanceAnalysis.vue
- [ ] 路由7: `/strategy/optimization` → ArtDecoStrategyOptimization.vue

**代码模板**:
```typescript
{
  path: 'strategy-mgmt',
  name: 'strategy-management',
  component: () => import('@/views/artdeco-pages/components/strategy/ArtDecoStrategyManagement.vue'),
  meta: {
    title: '策略管理',
    icon: '📚',
    breadcrumb: 'Strategy > Management'
  }
}
```

#### Task 1.3: 更新Strategy域菜单配置
- [ ] 在 `MenuConfig.ts` 中添加7个菜单项
- [ ] 配置API端点（使用现有后端API）
- [ ] 设置优先级和实时更新标记
- [ ] 添加WebSocket通道配置（如需要）

**菜单配置模板**:
```typescript
{
  path: '/strategy/strategy-mgmt',
  label: '策略管理',
  icon: '📚',
  description: '策略设计、管理、测试',
  apiEndpoint: '/api/strategy/list',
  apiMethod: 'GET',
  liveUpdate: false,
  priority: 'secondary'
}
```

#### Task 1.4: Strategy域测试验证
- [ ] 运行 `test-pages.mjs` 验证7个新页面
- [ ] 确认HTTP 200响应
- [ ] 检查浏览器控制台无错误
- [ ] 验证菜单点击跳转正确
- [ ] 确认ArtDecoLayout正确渲染

**测试命令**:
```bash
cd web/frontend
node scripts/test-pages.mjs
pm2 restart mystocks-frontend-prod
pm2 logs mystocks-frontend-prod --lines 20
```

**预期成果**: Strategy域完成度从40%→180%（2/5页→9/9页）

---

### Week 1, Day 3-4: Market域路由扩展

#### Task 1.5: Market域路由准备
- [ ] 分析现有Market域路由结构
- [ ] 确认4个子组件文件路径
- [ ] 检查API端点可用性
- [ ] 创建路由配置草稿

**验证命令**:
```bash
# 验证组件存在
ls -la web/frontend/src/views/artdeco-pages/components/market/

# 验证API可用
curl -s http://localhost:8000/api/market/realtime-summary | jq '.success'
```

#### Task 1.6: 添加Market域路由（4个新路由）
- [ ] 路由1: `/market/realtime` → ArtDecoRealtimeMonitor.vue
- [ ] 路由2: `/market/analysis` → ArtDecoMarketAnalysis.vue
- [ ] 路由3: `/market/overview` → ArtDecoMarketOverview.vue
- [ ] 路由4: `/market/industry` → ArtDecoIndustryAnalysis.vue

#### Task 1.7: 更新Market域菜单配置
- [ ] 在 `MenuConfig.ts` 中添加4个菜单项
- [ ] 配置实时更新（Market域大部分需要WebSocket）
- [ ] 设置API端点和通道映射
- [ ] 添加优先级标记

**实时更新配置示例**:
```typescript
{
  path: '/market/realtime',
  label: '实时监控',
  icon: '⚡',
  description: '实时行情监控',
  apiEndpoint: '/api/market/realtime-summary',
  apiMethod: 'GET',
  liveUpdate: true,
  wsChannel: 'market:realtime',
  priority: 'primary'
}
```

#### Task 1.8: Market域测试验证
- [ ] 运行 `test-pages.mjs` 验证4个新页面
- [ ] 测试WebSocket连接（如配置）
- [ ] 验证实时数据更新
- [ ] 检查图表组件渲染
- [ ] 确认无控制台错误

**预期成果**: Market域完成度从25%→75%（2/8页→6/8页）

---

### Week 1, Day 5: Phase 1集成测试

#### Task 1.9: 完整集成测试
- [ ] 运行完整页面测试（16个页面）
- [ ] 验证Strategy域9个页面
- [ ] 验证Market域6个页面（含现有2个）
- [ ] 检查路由跳转流畅性
- [ ] 测试模块切换无卡顿

#### Task 1.10: 问题修复
- [ ] 修复发现的任何路由冲突
- [ ] 解决组件导入错误
- [ ] 修复菜单配置问题
- [ ] 优化加载性能
- [ ] 更新错误处理

#### Task 1.11: PM2部署验证
- [ ] PM2重启前端进程
- [ ] 验证所有页面HTTP 200
- [ ] 检查PM2日志无错误
- [ ] 确认内存使用正常
- [ ] 测试热重载功能

**验证清单**:
```bash
# 1. 测试所有页面
node scripts/test-pages.mjs

# 2. PM2状态检查
pm2 list
pm2 logs mystocks-frontend-prod --lines 50

# 3. 内存和性能
pm2 monit

# 4. 浏览器测试
# 手动访问所有16个页面，确认无404
```

**Phase 1完成标准**:
- ✅ 11个新路由全部配置完成
- ✅ 菜单配置更新完成
- ✅ 所有页面HTTP 200响应
- ✅ 整体完成度从24%→68%

---

## Phase 2: P1优先级 - Risk和System域（第2周）

### Week 2, Day 6-7: Risk域路由扩展

#### Task 2.1: Risk域路由准备
- [ ] 分析现有Risk域路由结构
- [ ] 确认3个子组件文件路径
- [ ] 检查风险相关API端点
- [ ] 创建路由配置草稿

**Risk域组件清单**:
```bash
web/frontend/src/views/artdeco-pages/components/risk/
├── ArtDecoRiskMonitor.vue       # 风险监控
├── ArtDecoRiskAlerts.vue         # 风险预警
└── ArtDecoAnnouncementMonitor.vue # 公告监控
```

#### Task 2.2: 添加Risk域路由（3个新路由）
- [ ] 路由1: `/risk/monitor` → ArtDecoRiskMonitor.vue
- [ ] 路由2: `/risk/alerts` → ArtDecoRiskAlerts.vue
- [ ] 路由3: `/risk/announcement` → ArtDecoAnnouncementMonitor.vue

#### Task 2.3: 更新Risk域菜单配置
- [ ] 在 `MenuConfig.ts` 中添加3个菜单项
- [ ] 配置风险相关API端点
- [ ] 设置实时更新（预警需要WebSocket）
- [ ] 添加优先级和描述

**Risk域菜单配置**:
```typescript
{
  path: '/risk/monitor',
  label: '风险监控',
  icon: '📊',
  description: '实时风险监控',
  apiEndpoint: '/api/risk/overview',
  liveUpdate: true,
  wsChannel: 'risk:overview',
  priority: 'secondary'
},
{
  path: '/risk/alerts',
  label: '风险预警',
  icon: '🔔',
  description: '个股预警设置',
  apiEndpoint: '/api/risk/alerts',
  liveUpdate: true,
  wsChannel: 'risk:alerts',
  priority: 'secondary'
},
{
  path: '/risk/announcement',
  label: '公告监控',
  icon: '📢',
  description: '公告舆情监控',
  apiEndpoint: '/api/announcement/list',
  liveUpdate: false,
  priority: 'secondary'
}
```

#### Task 2.4: Risk域测试验证
- [ ] 运行 `test-pages.mjs` 验证3个新页面
- [ ] 测试WebSocket实时预警
- [ ] 验证风险数据展示
- [ ] 检查公告加载功能
- [ ] 确认无控制台错误

**预期成果**: Risk域完成度从20%→80%（1/5页→4/5页）

---

### Week 2, Day 8-9: System域路由扩展

#### Task 2.5: System域路由准备
- [ ] 分析现有System域路由结构
- [ ] 确认3个子组件文件路径
- [ ] 检查系统相关API端点
- [ ] 创建路由配置草稿

**System域组件清单**:
```bash
web/frontend/src/views/artdeco-pages/components/system/
├── ArtDecoMonitoringDashboard.vue # 监控仪表板
├── ArtDecoSystemSettings.vue       # 系统设置
└── ArtDecoDataManagement.vue        # 数据管理
```

#### Task 2.6: 添加System域路由（3个新路由）
- [ ] 路由1: `/system/dashboard` → ArtDecoMonitoringDashboard.vue
- [ ] 路由2: `/system/sys-settings` → ArtDecoSystemSettings.vue
- [ ] 路由3: `/system/data-mgmt` → ArtDecoDataManagement.vue

#### Task 2.7: 更新System域菜单配置
- [ ] 在 `MenuConfig.ts` 中添加3个菜单项
- [ ] 配置系统相关API端点
- [ ] 设置监控数据刷新频率
- [ ] 添加优先级和描述

**System域菜单配置**:
```typescript
{
  path: '/system/dashboard',
  label: '监控仪表板',
  icon: '📊',
  description: '平台监控概览',
  apiEndpoint: '/api/monitoring/platform-status',
  liveUpdate: true,
  priority: 'secondary'
},
{
  path: '/system/sys-settings',
  label: '系统设置',
  icon: '⚙️',
  description: '系统参数配置',
  apiEndpoint: '/api/system/config',
  liveUpdate: false,
  priority: 'secondary'
},
{
  path: '/system/data-mgmt',
  label: '数据管理',
  icon: '💾',
  description: '数据质量管理',
  apiEndpoint: '/api/data-quality/summary',
  liveUpdate: false,
  priority: 'secondary'
}
```

#### Task 2.8: System域测试验证
- [ ] 运行 `test-pages.mjs` 验证3个新页面
- [ ] 测试监控数据加载
- [ ] 验证系统设置功能
- [ ] 检查数据管理界面
- [ ] 确认无控制台错误

**预期成果**: System域完成度从20%→80%（1/5页→4/5页）

---

### Week 2, Day 10: Phase 2集成测试

#### Task 2.9: 完整集成测试
- [ ] 运行完整页面测试（22个页面）
- [ ] 验证Risk域4个页面
- [ ] 验证System域4个页面
- [ ] 测试域间导航
- [ ] 验证菜单展开/收起

#### Task 2.10: 性能优化
- [ ] 检查路由懒加载工作正常
- [ ] 验证组件缓存效果
- [ ] 测试首屏加载时间
- [ ] 优化大组件加载
- [ ] 减少不必要的重渲染

#### Task 2.11: 文档更新
- [ ] 更新 `ARTDECO_COMPONENTS_CATALOG.md`
- [ ] 记录新增路由配置
- [ ] 更新API端点映射
- [ ] 创建测试报告
- [ ] 更新用户指南

**Phase 2完成标准**:
- ✅ 6个新路由全部配置完成
- ✅ Risk和System域菜单配置完成
- ✅ 所有页面HTTP 200响应
- ✅ 整体完成度从68%→85%

---

## Phase 3: P2优先级 - 复用和创建（第3周）

### Week 3, Day 11-12: 复用现有组件

#### Task 3.1: 分析可复用组件
- [ ] 识别未使用ArtDecoLayout的页面
- [ ] 确认组件功能完整性
- [ ] 评估适配工作量
- [ ] 创建复用优先级清单

**可复用组件清单**（10个）:
```typescript
// Dashboard域
{ path: '/dashboard/watchlist', component: () => import('@/views/Stocks.vue') },
{ path: '/dashboard/portfolio', component: () => import('@/views/PortfolioManagement.vue') },
{ path: '/dashboard/activity', component: () => import('@/views/TradeManagement.vue') },

// Analysis域
{ path: '/analysis/technical', component: () => import('@/views/TechnicalAnalysis.vue') },
{ path: '/analysis/industry', component: () => import('@/views/IndustryConceptAnalysis.vue') },

// Market域（临时复用）
{ path: '/market/tdx', component: () => import('@/views/TdxMarket.vue') },

// System域
{ path: '/system/api', component: () => import('@/views/system/DatabaseMonitor.vue') },
{ path: '/system/performance', component: () => import('@/views/monitoring/RiskDashboard.vue') }
```

#### Task 3.2: 添加复用组件路由（10个）
- [ ] Dashboard域: 3个路由
- [ ] Analysis域: 2个路由
- [ ] Market域: 1个路由
- [ ] System域: 2个路由
- [ ] Stocks域: 2个路由（如需要）

#### Task 3.3: 配置复用组件菜单
- [ ] 在 `MenuConfig.ts` 中添加菜单项
- [ ] 标记为"临时使用"（待ArtDeco版本替换）
- [ ] 配置API端点映射
- [ ] 添加样式适配层（如需要）

**临时复用标记**:
```typescript
{
  path: '/market/tdx',
  label: '通达信接口',
  icon: '📡',
  description: '通达信数据接口',
  apiEndpoint: '/api/market/tdx',
  liveUpdate: true,
  priority: 'tertiary',
  temporary: true,  // 标记为临时
  note: '待ArtDeco版本替换'
}
```

#### Task 3.4: 测试复用组件
- [ ] 运行 `test-pages.mjs` 验证10个新页面
- [ ] 检查布局兼容性
- [ ] 验证功能完整性
- [ ] 测试API集成
- [ ] 确认无控制台错误

**预期成果**: 复用10个组件，完成度从85%→90%

---

### Week 3, Day 13-14: 创建新组件（按需）

#### Task 3.5: 确定新组件需求
- [ ] 资金流向分析（Market域）- 必需
- [ ] ETF市场（Market域）- 可选
- [ ] 集合竞价分析（Market域）- 可选
- [ ] 龙虎榜分析（Market域）- 已有部分实现
- [ ] 行业选股（Stocks域）- 可选
- [ ] 概念选股（Stocks域）- 可选

#### Task 3.6: 创建优先级最高的新组件
- [ ] **资金流向分析页面** (`ArtDecoCapitalFlow.vue`)
  - 集成 `/api/market/capital-flow` API
  - 显示资金流向图表
  - 使用ArtDecoCard和ArtDecoChart组件

- [ ] **ETF市场页面** (`ArtDecoETFMarket.vue`)
  - 集成 `/api/market/etf` API
  - 显示ETF行情列表
  - 使用ArtDecoTable组件

- [ ] **集合竞价分析页面** (`ArtDecoAuctionAnalysis.vue`)
  - 集成 `/api/market/auction` API
  - 显示竞价分析图表
  - 使用ArtDecoChart组件

**组件创建模板**:
```vue
<template>
  <div class="artdeco-capital-flow">
    <ArtDecoCard variant="chart">
      <template #header>
        <h2>资金流向分析</h2>
      </template>
      <template #default>
        <!-- 图表组件 -->
        <CapitalFlowChart :data="flowData" />
      </template>
    </ArtDecoCard>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMarketAPI } from '@/api/market'

const { getCapitalFlow } = useMarketAPI()
const flowData = ref([])

onMounted(async () => {
  const response = await getCapitalFlow()
  flowData.value = response.data
})
</script>
```

#### Task 3.7: 添加新组件路由和菜单
- [ ] 添加新组件路由配置
- [ ] 更新 `MenuConfig.ts`
- [ ] 配置API端点
- [ ] 设置实时更新（如需要）

#### Task 3.8: 测试新组件
- [ ] 运行 `test-pages.mjs` 验证新页面
- [ ] 测试数据加载和展示
- [ ] 验证图表交互
- [ ] 检查响应式布局
- [ ] 确认无控制台错误

**预期成果**: 创建3-6个新组件，完成度从90%→92%+

---

### Week 3, Day 15: 端到端测试和文档

#### Task 3.9: 完整端到端测试
- [ ] 运行完整页面测试（35+页面）
- [ ] 手动测试所有用户流程
- [ ] 验证域间导航
- [ ] 测试实时数据更新
- [ ] 检查错误处理

**用户流程测试清单**:
```
1. 登录 → Dashboard → 查看概览
2. Market → 实时监控 → 查看行情
3. Market → 技术分析 → 查看指标
4. Strategy → 策略管理 → 创建策略
5. Strategy → 回测中心 → 运行回测
6. Risk → 风险监控 → 查看预警
7. System → 监控仪表板 → 查看状态
```

#### Task 3.10: 性能和兼容性测试
- [ ] 测试首屏加载时间（目标<2秒）
- [ ] 测试路由切换速度（目标<200ms）
- [ ] 检查内存泄漏
- [ ] 测试跨浏览器兼容性
- [ ] 验证移动端基本可用性（仅桌面端优化）

#### Task 3.11: 文档和交付
- [ ] 更新所有相关文档
- [ ] 创建用户使用指南
- [ ] 编写开发者文档
- [ ] 准备演示材料
- [ ] 创建发布说明

**Phase 3完成标准**:
- ✅ 10个复用组件集成完成
- ✅ 3-6个新组件创建完成
- ✅ 所有页面HTTP 200响应
- ✅ 整体完成度达到92%+

---

## Quality Assurance Tasks

### 代码质量标准

**路由配置质量**:
- [ ] 所有路由使用懒加载
- [ ] 路由命名规范统一
- [ ] 元数据配置完整
- [ ] 重定向配置合理
- [ ] 无路由冲突

**菜单配置质量**:
- [ ] 描述文本10-12字
- [ ] API端点配置正确
- [ ] WebSocket通道准确
- [ ] 优先级设置合理
- [ ] 类型检查无错误

**组件集成质量**:
- [ ] 组件导入路径正确
- [ ] Props传递完整
- [ ] 事件处理正确
- [ ] 错误边界完善
- [ ] 加载状态友好

### 测试覆盖率要求

**页面访问测试**:
- [ ] 100%页面HTTP 200响应
- [ ] 100%菜单点击可跳转
- [ ] 100%返回按钮可返回
- [ ] 0%页面404错误
- [ ] 0%控制台错误

**功能测试**:
- [ ] API数据正常加载
- [ ] 实时数据正常更新
- [ ] 图表组件正常渲染
- [ ] 表格组件正常显示
- [ ] 表单组件正常提交

**性能测试**:
- [ ] 首屏加载<2秒
- [ ] 路由切换<200ms
- [ ] 内存使用<500MB
- [ ] 无明显卡顿
- [ ] Bundle大小优化

### 浏览器兼容性

**支持的浏览器**:
- [ ] Chrome 90+ ✅
- [ ] Firefox 88+ ✅
- [ ] Safari 14+ ✅
- [ ] Edge 90+ ✅

**兼容性测试**:
- [ ] 布局一致性
- [ ] 功能完整性
- [ ] 性能可接受
- [ ] 控制台无错误

---

## 验证清单总览

### Phase 1验证（第1周末）
- [ ] 11个新路由配置完成
- [ ] 11个菜单项配置完成
- [ ] 16个页面HTTP 200（Strategy 9 + Market 6 + 现有1）
- [ ] PM2日志无错误
- [ ] 浏览器控制台无错误
- [ ] 完成度24%→68%

### Phase 2验证（第2周末）
- [ ] 6个新路由配置完成
- [ ] 6个菜单项配置完成
- [ ] 22个页面HTTP 200（+ Risk 4 + System 4）
- [ ] WebSocket连接正常
- [ ] 实时数据更新正常
- [ ] 完成度68%→85%

### Phase 3验证（第3周末）
- [ ] 10个复用组件集成完成
- [ ] 3-6个新组件创建完成
- [ ] 35+页面HTTP 200
- [ ] 所有用户流程测试通过
- [ ] 性能指标达标
- [ ] 完成度85%→92%+

---

## Dependencies & Prerequisites

### 环境要求（已满足）
- [x] Vue 3.4+ 项目环境
- [x] Vue Router 4.x 已配置
- [x] TypeScript 5.x 已配置
- [x] ArtDeco组件库（64组件）
- [x] PM2进程管理
- [x] 后端API（120个文件）

### API依赖（已就绪）
- [x] 市场数据API (`/api/market/*`)
- [x] 策略管理API (`/api/strategy/*`)
- [x] 交易相关API (`/api/trading/*`)
- [x] 风险管理API (`/api/risk/*`)
- [x] 监控平台API (`/api/monitoring/*`)
- [x] WebSocket实时数据

### 开发工具（已就绪）
- [x] Node.js 18+ 和npm
- [x] Vite 5.x 构建工具
- [x] VS Code开发环境
- [x] 浏览器开发者工具
- [x] PM2进程管理器

---

## 附录：快速参考

### 常用命令

```bash
# 测试所有页面
cd web/frontend && node scripts/test-pages.mjs

# PM2操作
pm2 restart mystocks-frontend-prod
pm2 logs mystocks-frontend-prod --lines 50
pm2 monit

# 开发模式
npm run dev -- --port 3001

# 构建生产版本
npm run build
```

### 文件路径

```bash
# 路由配置
web/frontend/src/router/index.ts

# 菜单配置
web/frontend/src/layouts/MenuConfig.ts

# ArtDeco组件
web/frontend/src/views/artdeco-pages/

# 测试脚本
web/frontend/scripts/test-pages.mjs
```

### 相关文档

- `docs/reports/ARTDECO_NAVIGATION_GAP_ANALYSIS.md` - 差距分析
- `web/frontend/ARTDECO_COMPONENTS_CATALOG.md` - 组件目录
- `docs/reports/MENU_DESCRIPTION_OPTIMIZATION_REPORT.md` - 菜单优化
- `docs/reports/RALPH_LOOP_COMPLETION_SUMMARY.md` - 测试完成报告

---

**任务清单版本**: v2.0 (Updated 2026-01-20)
**任务性质**: 路由集成（非组件创建）
**预期工期**: 3周
**完成度目标**: 24%→92%
