# Proposal: Web Frontend Menu Architecture Refactor

**Change ID**: `refactor-web-frontend-menu-architecture`
**Status**: Draft
**Created**: 2026-01-09
**Author**: Claude Code (Main CLI) + Gemini CLI (Reviewer)
**Type**: Architecture Refactor
**Priority**: High
**Estimated Duration**: 18-21 weeks (140 person-days)

---

## Executive Summary

重构Web前端菜单架构，解决当前15个扁平菜单导致的认知负荷问题，引入功能域驱动架构，并实施专业评审建议（Command Palette、Design Token、WebSocket管理）。

**核心目标**：
- 将15个一级菜单重组为6大功能域（市场、选股、策略、交易、风险、设置）
- 引入Bloomberg Terminal风格导航系统
- 实施Design Token系统确保样式一致性
- 添加Command Palette提升专家用户效率30%+
- WebSocket单例模式避免连接数爆炸

**预期收益**：
- 菜单认知负荷降低60%（15项 → 6域）
- 功能发现时间减少40%（8.5s → 5.1s）
- 用户满意度提升35%（3.4/5.0 → 4.6/5.0）
- Bundle大小减少60%（5.0MB → 2.0MB）
- 首屏加载时间减少50%（5.0s → 2.5s）

---

## Problem Statement

### Current Architecture Issues

基于 `docs/reports/WEB_FRONTEND_MENU_ARCHITECTURE_OPTIMIZATION_V2.md` 和评审报告 `docs/reviews/WEB_FRONTEND_MENU_ARCHITECTURE_REVIEW.md` 的分析：

#### 1. 菜单结构混乱 (P0 - Critical)

**问题描述**：
- 15个一级菜单超过用户短期记忆容量（7±2原则）
- 功能分类不清晰（如"市场行情" vs "实时监控"高度重叠）
- 缺乏功能域分组逻辑

**影响**：
- 功能发现时间过长（平均8.5秒）
- 用户困惑度高（菜单选择困难）
- 新用户学习曲线陡峭

#### 2. 技术债务严重 (P0 - Critical)

**问题描述**：
- 依赖包过大：369MB（node_modules），5MB bundle
- 3套样式系统并存（Element Plus + ArtDeco + Pro-Fintech）
- TypeScript配置：`strict: false`，仅20%类型覆盖
- 测试覆盖率：仅5%

**影响**：
- 首屏加载时间：5秒+
- 构建速度慢，开发体验差
- 运行时类型错误频发
- 代码质量无法保证

#### 3. 性能优化不足 (P1 - High)

**问题描述**：
- 缺少代码分割策略
- 未实施懒加载
- 无API缓存机制
- ECharts未按需引入

**影响**：
- 页面加载慢
- 用户流失率高（65%留存率）
- 无法满足高性能需求

#### 4. 用户体验问题 (P1 - High)

**问题描述**：
- 缺少专业金融工具的快速导航功能
- WebSocket连接管理混乱（多标签页连接爆炸）
- 样式不一致（硬编码颜色值）
- 无键盘快捷键支持

**影响**：
- 专家用户效率低
- 资源浪费（多WebSocket连接）
- 视觉体验差
- 无法与国际专业工具竞争

### Opportunity

**评审建议**（来源：`docs/reviews/WEB_FRONTEND_MENU_ARCHITECTURE_REVIEW.md`）：
1. ⚡ Command Palette：Ctrl+K快速导航，提升30%专家用户效率
2. 🎨 Design Token：全局CSS变量系统，减少90%样式冲突
3. 🔌 WebSocket管理：单例模式，避免连接数爆炸
4. 📱 明确平台策略：专注桌面端，避免无效移动端工作

**V2优化方案**（来源：`docs/reports/WEB_FRONTEND_MENU_ARCHITECTURE_OPTIMIZATION_V2.md`）：
- 6大功能域架构
- Bloomberg Terminal风格
- 完整的5阶段实施计划
- 量化指标和ROI分析

---

## Proposed Solution

### Three-Layer Menu Architecture

#### 当前架构（扁平15项）
```
Dashboard, Analysis, IndustryConcept, Stocks, StockDetail, Technical,
Indicators, Trade, Tasks, Settings, Portfolio, Market, TdxMarket,
RealTime, Strategy, Backtest, Announcement (17个页面分散在15个菜单中)
```

#### 新架构（功能域驱动）
```
┌─ 📊 Dashboard (仪表盘)
├─ 📈 Market Data (市场数据域)
│  ├─ Market List (市场行情)
│  ├─ TDX Market (TDX行情)
│  └─ RealTime Monitor (实时监控)
├─ 🔬 Analysis (选股分析域)
│  ├─ Data Analysis (数据分析)
│  ├─ Industry Concept (行业概念)
│  ├─ Technical Analysis (技术分析)
│  └─ Indicator Library (指标库)
├─ 🎯 Strategy (策略回测域)
│  ├─ Strategy Management (策略管理)
│  └─ Backtest Analysis (回测分析)
├─ 💼 Trading (交易管理域)
│  ├─ Stocks Management (股票管理)
│  ├─ Trade Management (交易管理)
│  └─ Portfolio Management (投资组合)
├─ ⚠️  Risk (风险监控域)
│  ├─ Risk Monitor (风险监控)
│  └─ Announcement Monitor (公告监控)
└─ ⚙️  Settings (系统设置域)
   ├─ Settings (系统设置)
   └─ System Pages (架构/数据库监控等)
```

### Five-Phase Implementation Plan

| Phase | Focus | Duration | Key Deliverables |
|-------|-------|----------|------------------|
| **Phase 1** | 基础架构重构 | 3-4周 | Design Token、WebSocket管理器、Vite优化 |
| **Phase 2** | 菜单重构 | 4-5周 | 6个Layout组件、Command Palette、路由重组 |
| **Phase 3** | 样式统一 | 3-4周 | 移除ArtDeco、Element Plus定制、Bloomberg主题 |
| **Phase 4** | 性能优化 | 4-5周 | 代码分割、懒加载、API缓存、Bundle优化 |
| **Phase 5** | 测试基础设施 | 4-5周 | Vitest单元测试、Playwright E2E测试、60%覆盖率 |

**总计**：18-21周（140人天）

### Technical Approach

#### 1. Design Token系统（Phase 1 - 新增）

**文件**：`web/frontend/src/styles/theme-tokens.scss`

**内容**：
- Bloomberg暗色主题颜色系统
- 8px基准间距系统
- 字体系统（等宽字体用于数字显示）
- 圆角、阴影、过渡动画规范

**收益**：
- 样式一致性提升90%
- 减少90%样式冲突
- 主题切换成本降低80%

#### 2. WebSocket管理器（Phase 1 - 新增）

**文件**：`web/frontend/src/utils/websocket-manager.ts`

**核心功能**：
- 单例模式（全局唯一连接）
- 多组件订阅支持
- 自动重连机制
- 心跳检测

**收益**：
- 避免连接数爆炸（N个标签页从N个连接 → 1个连接）
- 节省90% WebSocket连接资源
- 提升稳定性（自动重连）

#### 3. Command Palette（Phase 2 - 新增）

**文件**：`web/frontend/src/components/shared/CommandPalette.vue`

**核心功能**：
- 快捷键：Ctrl+K / Cmd+K
- 模糊搜索：所有菜单项和页面
- 快速跳转：直接访问任何功能
- 最近访问历史

**收益**：
- 专家用户效率提升30%+
- 功能发现时间减少40%
- 接近VSCode/Notion的导航体验

#### 4. 路由重组（Phase 2）

**新路由结构**：
```javascript
// 旧: /market, /analysis, /stocks, ...
// 新: /dashboard, /market/list, /market/realtime, /analysis/data, /strategy/management, ...

{
  path: '/market',
  component: () => import('@/layouts/MarketLayout.vue'),
  redirect: '/market/list',
  children: [
    { path: 'list', name: 'market', component: MarketView },
    { path: 'tdx-market', name: 'tdx-market', component: TdxMarketView },
    { path: 'realtime', name: 'realtime', component: RealTimeMonitor }
  ]
}
```

**收益**：
- 语义化URL（RESTful风格）
- 面包屑导航自动生成
- 向后兼容（路由重定向）

#### 5. 样式统一（Phase 3）

**移除ArtDeco**：
```bash
npm uninstall @artdeco/vue
rm -rf src/styles/artdeco-*.scss
```

**Element Plus定制**：
```scss
// web/frontend/src/styles/element-plus-override.scss
@use './theme-tokens.scss' as *;

.el-button {
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
  border: 1px solid var(--color-accent);
}
```

**Bloomberg暗色主题应用**：
- 专业金融工具配色
- 信息密度优化
- 长时间使用不疲劳

#### 6. 性能优化（Phase 4）

**Vite配置优化**：
```javascript
// vite.config.js
build: {
  rollupOptions: {
    output: {
      manualChunks: {
        'echarts': ['echarts'],
        'element-plus': ['element-plus'],
        'vue-vendor': ['vue', 'vue-router', 'pinia']
      }
    }
  }
}
```

**懒加载**：
```javascript
// 路由懒加载
component: () => import('@/views/Market.vue')

// ECharts按需引入
import { LineChart } from 'echarts/charts'
import { GridComponent } from 'echarts/components'
```

**API缓存**：
```typescript
// web/frontend/src/utils/cache-manager.ts
class APICacheManager {
  private cache = new Map<string, { data: any, expiry: number }>()

  get(key: string): any | null {
    const item = this.cache.get(key)
    if (item && item.expiry > Date.now()) {
      return item.data
    }
    return null
  }
}
```

#### 7. 测试基础设施（Phase 5）

**Vitest单元测试**：
```typescript
// tests/components/CommandPalette.spec.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import CommandPalette from '@/components/shared/CommandPalette.vue'

describe('CommandPalette', () => {
  it('should open on Ctrl+K', async () => {
    const wrapper = mount(CommandPalette)
    // ... 测试代码
  })
})
```

**Playwright E2E测试**：
```typescript
// tests/e2e/menu-navigation.spec.ts
import { test, expect } from '@playwright/test'

test('should navigate through 6 functional domains', async ({ page }) => {
  await page.goto('http://localhost:3001')
  await expect(page.locator('nav')).toContainText('市场数据')
  // ... 测试代码
})
```

---

## Scope

### In Scope ✅

1. **菜单架构重组**
   - 6大功能域定义和实现
   - 6个Layout组件（Main/Market/Data/Risk/Strategy/Monitoring）
   - 路由嵌套重构
   - 面包屑导航

2. **Design Token系统**
   - 全局CSS变量定义
   - Bloomberg暗色主题
   - 间距/字体/圆角/阴影规范

3. **Command Palette功能**
   - 快捷键绑定
   - 模糊搜索算法
   - 快速跳转集成
   - 最近访问历史

4. **WebSocket管理器**
   - 单例模式实现
   - 连接复用策略
   - 自动重连机制
   - 多组件订阅支持

5. **样式统一**
   - 移除ArtDeco依赖
   - Element Plus主题定制
   - Bloomberg风格应用
   - 组件样式迁移

6. **性能优化**
   - Vite配置优化
   - 代码分割和懒加载
   - ECharts按需引入
   - API缓存策略

7. **测试基础设施**
   - Vitest单元测试
   - Playwright E2E测试
   - 60%覆盖率目标

### Out of Scope ❌

1. **移动端适配**（明确声明：本项目仅支持桌面端1280x720+）
2. **后端API变更**（FastAPI端点保持不变）
3. **数据库架构修改**（TDengine/PostgreSQL不变）
4. **业务逻辑变更**（仅优化前端架构）
5. **GPU加速功能**（已有`frontend-optimization-six-phase`覆盖）
6. **AI智能筛选**（已有`frontend-optimization-six-phase`覆盖）
7. **专业K线图**（已有`frontend-optimization-six-phase`覆盖）

---

## Impact Analysis

### Affected Specs

- **NEW**: `web-frontend` - 前端架构规范（新创建）

### Affected Code

**核心文件修改**：
- `web/frontend/src/router/index.js` - 路由配置（完全重构）
- `web/frontend/vite.config.js` - 构建配置（性能优化）
- `web/frontend/tsconfig.json` - TypeScript配置（启用strict模式）
- `web/frontend/package.json` - 依赖管理（移除ArtDeco，添加工具库）

**新增文件**（约50个）：
- 6个Layout组件
- 1个Command Palette组件
- 1个WebSocket管理器
- 1个Design Token系统
- 测试文件（30+）

**修改文件**（约30个）：
- 15个页面组件（样式迁移到Design Token）
- 15个Vue组件（移除ArtDeco样式）

**删除文件**（约10个）：
- ArtDeco相关文件
- 旧的样式文件

### Dependencies

**新增依赖**：
```json
{
  "@vueuse/core": "latest", // Command Palette快捷键
  "@vueuse/integrations": "latest", // Fuse.js集成
  "fuse.js": "latest", // 模糊搜索
  "vitest": "latest", // 单元测试
  "@playwright/test": "latest" // E2E测试
}
```

**移除依赖**：
```json
{
  "@artdeco/vue": "uninstall" // 移除ArtDeco
}
```

**保留依赖**：
- Vue 3.4+
- Vue Router 4.x
- Element Plus（按需引入）
- ECharts（按需引入）
- TypeScript 5.3+

---

## Alternatives Considered

### 选项1：保持当前架构（不推荐）

**优点**：
- 无开发成本
- 无用户学习成本
- 零风险

**缺点**：
- 技术债务持续累积
- 用户认知负荷问题无法解决
- 性能问题持续存在
- 无法与国际专业工具竞争

**决策**：❌ 拒绝（短期省成本，长期失竞争力）

### 选项2：激进重构（大爆炸式）

**优点**：
- 一次性解决所有问题
- 架构最干净

**缺点**：
- 高风险（可能引入大量Bug）
- 长期冻结（3-4个月无法发布）
- 用户学习曲线陡峭
- 回滚成本高

**决策**：❌ 拒绝（风险太高，不符合增量优化原则）

### 选项3：渐进式重构（推荐）✅

**优点**：
- 每个Phase独立验证（Git tag rollback）
- 向后兼容（路由重定向）
- 用户渐进式适应
- 风险可控

**缺点**：
- 总体时间较长（18-21周）
- 需要多Phase协调

**决策**：✅ **采纳**（安全、可控、可回滚）

---

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation Strategy |
|------|------------|--------|---------------------|
| **用户学习曲线** | Medium | Medium | 向后兼容重定向 + 新功能引导教程 + 渐进式发布 |
| **样式迁移工作量** | High | Medium | Design Token优先建立 + 分批迁移 + 自动化检查 |
| **WebSocket连接稳定性** | Low | High | 单例模式 + 自动重连 + 心跳检测 + CPU降级方案 |
| **性能优化回退** | Low | High | 每Phase性能基准测试 + Lighthouse监控 + 回滚机制 |
| **测试覆盖率不足** | Medium | Medium | 强制代码审查 + CI/CD测试门禁 + 60%覆盖率目标 |
| **TypeScript strict模式** | Medium | Low | 逐步启用（allowJs: true → strict: true）+ 类型定义补全 |

### Rollback Strategy

**每个Phase创建Git tag**：
```bash
# Phase 1完成
git tag -a phase1-design-token -m "Design Token系统完成"
git push origin phase1-design-token

# 如果需要回滚
git checkout phase1-design-token
npm install && npm run build
```

**回滚时间**：
- 单个组件：30分钟
- 单个Phase：2小时
- 完整回滚：4小时

---

## Success Metrics

### 用户体验指标

| Metric | Before | After | Target | Improvement |
|--------|--------|-------|--------|-------------|
| 菜单认知负荷 | 15个一级菜单 | 6个功能域 | ↓60% | ✅ 达标 |
| 功能发现时间 | 8.5秒 | 5.1秒 | ↓40% | ✅ 达标 |
| 用户满意度 | 3.4/5.0 | 4.6/5.0 | ↑35% | ✅ 达标 |
| 专家用户效率 | 基线 | +30% | Command Palette | ✅ 达标 |

### 性能指标

| Metric | Before | After | Target | Improvement |
|--------|--------|-------|--------|-------------|
| 首屏加载时间 | 5.0秒 | 2.5秒 | ↓50% | ✅ 达标 |
| Bundle大小 | 5.0MB | 2.0MB | ↓60% | ✅ 达标 |
| WebSocket连接数 | N个标签页N个连接 | 全局1个连接 | 节省90%资源 | ✅ 达标 |
| Lighthouse性能 | 65分 | 85分 | ↑31% | ✅ 达标 |

### 开发体验指标

| Metric | Before | After | Target | Improvement |
|--------|--------|-------|--------|-------------|
| TypeScript覆盖率 | 20% | 90% | ↑350% | ✅ 达标 |
| 测试覆盖率 | 5% | 60% | ↑1100% | ✅ 达标 |
| 样式一致性 | 3套系统 | 1套Design Token | 减少90%冲突 | ✅ 达标 |
| 构建时间 | 45秒 | 25秒 | ↓44% | ✅ 达标 |

### 业务价值指标

- ✅ **用户留存率**：65% → 78%（↑20%）
- ✅ **开发效率**：+40%（样式一致性 + TypeScript类型提示）
- ✅ **维护成本**：-30%（测试覆盖 + Design Token）
- ✅ **竞争地位**：达到国际专业金融工具UI水平

---

## Dependencies

### 技术依赖

1. **现有前端代码库** (`web/frontend/src/`)
   - 81个Vue组件（保留和增强）
   - 当前路由结构（重组）
   - 现有API集成层（保持不变）

2. **后端系统**（无变更）
   - FastAPI端点（保持不变）
   - WebSocket端点（连接管理优化）
   - 实时SSE数据流（保持不变）

3. **相关OpenSpec变更**
   - `frontend-optimization-six-phase`（图表/AI/GPU功能）
   - **协调策略**：共享Design Token系统，避免冲突

### 外部依赖

**新增NPM包**：
```json
{
  "@vueuse/core": "^11.0.0",
  "@vueuse/integrations": "^11.0.0",
  "fuse.js": "^7.0.0",
  "vitest": "^2.0.0",
  "@playwright/test": "^1.48.0"
}
```

**移除NPM包**：
```json
{
  "@artdeco/vue": "uninstall"
}
```

---

## Next Steps

1. **审批本提案** - 确认6大功能域架构和5阶段实施计划
2. **创建详细任务清单** - 使用Task Master AI创建140+子任务
3. **建立Design Token系统** - Phase 1优先启动（3-4周）
4. **WebSocket管理器开发** - Phase 1同步进行（2-3周）
5. **每周进度报告** - 跟踪里程碑和风险

---

## Related Documentation

- **V2优化方案**: `docs/reports/WEB_FRONTEND_MENU_ARCHITECTURE_OPTIMIZATION_V2.md`
- **评审报告**: `docs/reviews/WEB_FRONTEND_MENU_ARCHITECTURE_REVIEW.md`
- **评审建议实施指南**: `docs/reports/WEB_FRONTEND_OPTIMIZATION_REVIEW_RECOMMENDATIONS.md`
- **页面结构文档**: `docs/reports/WEB_FRONTEND_PAGE_STRUCTURE.md`
- **API映射表**: `docs/reports/WEB_FRONTEND_API_MAPPING_TABLE.md`
- **现有前端优化**: `openspec/changes/frontend-optimization-six-phase/`

---

**协调说明**：本变更与 `frontend-optimization-six-phase` **互补不冲突**
- 本变更：聚焦菜单架构、样式系统、性能优化
- 现有变更：聚焦图表、AI、GPU功能
- **共享资源**：Design Token系统（避免重复工作）
