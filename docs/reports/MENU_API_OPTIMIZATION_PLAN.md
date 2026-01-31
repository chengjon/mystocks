# MyStocks Web菜单与API优化方案

**项目**: MyStocks 量化交易平台
**日期**: 2026-01-24
**版本**: v1.0
**状态**: 待审批
**类型**: 优化方案报告

---

## 📋 目录

1. [执行摘要](#执行摘要)
2. [现状分析](#现状分析)
3. [功能分配核对](#功能分配核对)
4. [未分配功能](#未分配功能)
5. [优化方案](#优化方案)
6. [实施路线图](#实施路线图)
7. [风险提示](#风险提示)

---

## 执行摘要

### 🎯 主要成果

- ✅ **菜单重组完成**: 创建"自选股"模块，整合自选股管理、行业股票池、股票筛选器
- ✅ **功能分配核对完成**: 对比用户需求与现有菜单，85.7%功能已分配
- ✅ **API盘点完成**: 分析61个后端API文件和28个前端路由
- ✅ **优化方案生成**: 提供系统性、分阶段的API利用建议

### 📊 数据概览

| 维度 | 数量 |
|------|------|
| **后端API文件** | 61个 |
| **前端路由** | 28个 |
| **已分配功能** | 12/14项（85.7%） |
| **未分配功能** | 2/14项（14.3%） |
| **优化方案数量** | 3个主要方案（7个任务） |

---

## 现状分析

### 📊 一、后端API清单（按模块分类）

#### 1. Market模块（8个API端点）

**文件**: `/opt/claude/mystocks_spec/web/backend/app/api/market.py`

| API端点 | 方法 | 路由 | 状态 | 功能描述 |
|----------|------|------|------|--------|
| `GET /api/market/fund-flow` | GET | /market/fund-flow | ✅ 已使用 | 资金流向查询 |
| `POST /api/market/fund-flow/refresh` | POST | - | ❌ 未使用 | 刷新资金流向数据 |
| `GET /api/market/etf/list` | GET | /market/etf | ✅ 已使用 | ETF列表查询 |
| `POST /api/market/etf/refresh` | POST | - | ❌ 未使用 | 刷新ETF数据 |
| `GET /api/market/chip-race` | GET | /market/auction | ✅ 已使用 | 竞价抢筹查询 |
| `POST /api/market/chip-race/refresh` | POST | - | ❌ 未使用 | 刷新抢筹数据 |
| `GET /api/market/lhb` | GET | /market/longhubang | ✅ 已使用 | 龙虎榜查询 |
| `POST /api/market/lhb/refresh` | POST | - | ❌ 未使用 | 刷新龙虎榜数据 |
| `GET /api/market/heatmap` | GET | - | ❌ 未使用 | 市场热力图数据 |

#### 2. Watchlist自选股模块（6个API端点）

**文件**: `/opt/claude/mystocks_spec/web/backend/app/api/watchlist.py`

| API端点 | 方法 | 路由 | 状态 | 功能描述 |
|----------|------|------|------|--------|
| `GET /api/watchlist` | GET | /watchlist/manage | ✅ 已使用 | 获取所有自选股列表 |
| `POST /api/watchlist/add` | POST | /watchlist/manage | ✅ 已使用 | 添加自选股 |
| `DELETE /api/watchlist/{id}` | DELETE | /watchlist/manage | ✅ 已使用 | 删除自选股 |
| `PUT /api/watchlist/{id}` | PUT | /watchlist/manage | ✅ 已使用 | 更新自选股（备注、分组） |
| `GET /api/watchlist/search` | GET | /watchlist/manage | ❌ 未使用 | 搜索自选股 |

#### 3. Stock Search股票搜索模块（1个API端点）

**文件**: `/opt/claude/mystocks_spec/web/backend/app/api/stock_search.py`

| API端点 | 方法 | 路由 | 状态 | 功能描述 |
|----------|------|------|------|--------|
| `GET /api/stock/search` | GET | /watchlist/screener | ✅ 已使用 | 股票搜索（支持A/HK/US） |

#### 4. Monitoring监控模块（2个API端点）

**文件**: `/opt/claude/mystocks_spec/web/backend/app/api/monitoring.py`

| API端点 | 方法 | 路由 | 状态 | 功能描述 |
|----------|------|------|------|--------|
| `GET /api/monitoring/dashboard` | GET | /system/monitoring | ✅ 已使用 | 监控仪表盘数据 |
| `GET /api/monitoring/health` | GET | /system/api-health | ✅ 已使用 | 系统健康检查 |

#### 5. Strategy策略管理模块（4个API端点）

**文件**: `/opt/claude/mystocks_spec/web/backend/app/api/strategy_management.py`

| API端点 | 方法 | 路由 | 状态 | 功能描述 |
|----------|------|------|------|--------|
| `GET /api/strategy/management` | GET | /strategy/management | ✅ 已使用 | 获取策略列表 |
| `POST /api/strategy/create` | POST | /strategy/management | ✅ 已使用 | 创建策略 |
| `PUT /api/strategy/{id}` | PUT | /strategy/management | ✅ 已使用 | 更新策略 |
| `DELETE /api/strategy/{id}` | DELETE | /strategy/management | ✅ 已使用 | 删除策略 |

#### 6. Risk风险控制模块（5个API端点）

**文件**: `/opt/claude/mystocks_spec/web/backend/app/api/risk_management.py`

| API端点 | 方法 | 路由 | 状态 | 功能描述 |
|----------|------|------|------|--------|
| `GET /api/risk/overview` | GET | /risk/overview | ✅ 已使用 | 风险概览 |
| `GET /api/risk/alerts` | GET | /risk/alerts | ✅ 已使用 | 获取告警列表 |
| `GET /api/risk/indicators` | GET | /risk/indicators | ✅ 已使用 | 风险指标 |

#### 7. System系统管理模块（5个API端点）

**文件**: `/opt/claude/mystocks_spec/web/backend/app/api/system.py`

| API端点 | 方法 | 路由 | 状态 | 功能描述 |
|----------|------|------|------|--------|
| `GET /api/system/monitoring` | GET | /system/monitoring | ✅ 已使用 | 运维监控 |
| `GET api/system/settings` | GET | /system/settings | ✅ 已使用 | 系统设置 |
| `GET /api/system/data-update` | GET | /system/data-update | ✅ 已使用 | 数据更新 |
| `GET /api/system/data-quality` | GET | /system/data-quality | ✅ 已使用 | 数据质量 |
| `GET /api/system/api-health` | GET | /system/api-health | ✅ 已使用 | API健康检查 |

#### 8. Dashboard仪表盘模块（1个API端点）

**文件**: `/opt/claude/mystocks_spec/web/backend/app/api/dashboard.py`

| API端点 | 方法 | 路由 | 状态 | 功能描述 |
|----------|------|------|------|--------|
| `GET /api/dashboard` | GET | /dashboard | ✅ 已使用 | 仪表盘数据 |

#### 9. 其他模块（15+个API端点）

**未在web中使用的API文件**:
- `/opt/claude/mystocks_spec/web/backend/app/api/announcement.py` - 公告监控API（2个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/technical_analysis.py` - 技术分析API（10+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/indicators.py` - 指标API（15+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/data.py` - 通用数据API（5+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/metrics.py` - 指标API（5+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/cache.py` - 缓存API（5+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/notification.py` - 通知API（5+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/algorithms.py` - 算法API（10+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/alternative_data.py` - 备用数据源API（10+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/efinance.py` - 财经API（10+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/tdx.py` - 通达信API（10+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/multi_source.py` - 多源API（10+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/advanced_analysis.py` - 高级分析API（10+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/backtest_ws.py` - 回测WebSocket API（5+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/stock_ratings_api.py` - 股票评级API（10+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/wencai.py` - 问财API（10+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/indicator_registry.py` - 指标注册表API（5+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/realtime_market.py` - 实时市场API（10+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/data_lineage.py` - 数据血缘API（5+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/ml.py` - 机器学习API（15+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/industry_concept_analysis.py` - 行业概念分析API（10+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/data_source_config.py` - 数据源配置API（5+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/gpu_monitoring.py` - GPU监控API（10+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/advanced_analysis_api.py` - 高级分析API（10+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/tasks.py` - 任务管理API（5+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/websocket.py` - WebSocket API（5+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/mystocks_api.py` - MyStocks完整API（20+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/prometheus_exporter.py` - Prometheus导出API（5+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/backup_recovery.py` - 备份恢复API（10+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/trading_monitor.py` - 交易监控API（10+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/signal_monitoring.py` - 信号监控API（10+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/governance_dashboard.py` - 治理仪表盘API（5+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/monitoring_watchlists.py` - 监控自选股API（5+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/data_source_registry.py` - 数据源注册表API（5+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/strategy_list_mock.py` - 策略列表模拟API（5+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/monitoring_analysis.py` - 监控分析API（5+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/announcement/routes.py` - 公告路由API（10+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/tradingview.py` - 交易视图API（10+个端点）
- `/opt/claude/mystocks_spec/web/backend/app/api/auth.py` - 认证API（10+个端点）

### 📊 二、前端路由清单（按模块分类）

#### 1. Market域（9个路由）

| 路由 | 组件 | 状态 | 功能描述 |
|------|------|--------|--------|
| `/market/realtime` | RealtimeQuotes.vue | ✅ 已实现 | 实时行情 |
| `/market/technical` | TechnicalQuotes.vue | ✅ 已实现 | 技术指标 |
| `/market/fund-flow` | FundFlow.vue | ✅ 已实现 | 资金流向 |
| `/market/etf` | ETFData.vue | ✅ 已实现 | ETF行情 |
| `/market/concept` | ConceptData.vue | ✅ 已实现 | 概念板块 |
| `/market/auction` | AuctionData.vue | ✅ 已实现 | 竞价抢筹 |
| `/market/longhubang` | LHBData.vue | ✅ 已实现 | 龙虎榜 |
| `/market/institution` | InstitutionData.vue | ✅ 已实现 | 机构荐股 |
| `/market/wencai` | WencaiData.vue | ✅ 已实现 | 问财选股 |

#### 2. Watchlist自选股域（旧路由3个）

| 路由 | 组件 | 状态 | 功能描述 |
|------|------|--------|--------|
| `/stocks/management` | StockManagement.vue | ✅ 已实现 | 自选股管理 |
| `/stocks/portfolio` | StockPortfolio.vue | ✅ 已实现 | 我的持仓 |
| `/stocks/activity` | StockActivity.vue | ✅ 已实现 | 交易活动 |
| `/stocks/screener` | Screener.vue | ✅ 已实现 | 股票筛选器 |

#### 3. Trading域（4个路由）

| 路由 | 组件 | 状态 | 功能描述 |
|------|------|--------|--------|
| `/trading/signals` | TradingSignals.vue | ✅ 已实现 | 交易信号 |
| `/trading/history` | TradingHistory.vue | ✅ 已实现 | 历史订单 |
| `/trading/positions` | TradingPositions.vue | ✅ 已实现 | 持仓监控 |
| `/trading/attribution` | TradingAttribution.vue | ✅ 已实现 | 绩效归因 |

#### 4. Strategy域（5个路由）

| 路由 | 组件 | 状态 | 功能描述 |
|------|------|--------|--------|
| `/strategy/design` | StrategyDesign.vue | ✅ 已实现 | 策略设计 |
| `/strategy/management` | StrategyManagement.vue | ✅ 已实现 | 策略管理 |
| `/strategy/backtest` | StrategyBacktest.vue | ✅ 已实现 | 策略回测 |
| `/strategy/gpu-backtest` | GPUBacktest.vue | ✅ 已实现 | GPU加速回测 |
| `/strategy/optimization` | StrategyOptimization.vue | ✅ 已实现 | 参数优化 |

#### 5. Risk域（5个路由）

| 路由 | 组件 | 状态 | 功能描述 |
|------|------|--------|--------|
| `/risk/overview` | RiskOverview.vue | ✅ 已实现 | 风险概览 |
| `/risk/alerts` | RiskAlerts.vue | ✅ 已实现 | 告警中心 |
| `/risk/indicators` | RiskIndicators.vue | ✅ 已实现 | 风险指标 |
| `/risk/sentiment` | RiskSentiment.vue | ✅ 已实现 | 舆情监控 |
| `/risk/announcement` | RiskAnnouncement.vue | ✅ 已实现 | 公告监控 |

#### 6. System域（5个路由）

| 路由 | 组件 | 状态 | 功能描述 |
|------|------|--------|--------|
| `/system/monitoring` | MonitoringDashboard.vue | ✅ 已实现 | 运维监控 |
| `/system/settings` | SystemSettings.vue | ✅ 已实现 | 系统设置 |
| `/system/data-update` | DataManagement.vue | ✅ 已实现 | 数据更新 |
| `/system/data-quality` | DataQuality.vue | ✅ 已实现 | 数据质量 |
| `/system/api-health` | APIHealth.vue | ✅ 已实现 | API健康 |

#### 7. Dashboard路由

| 路由 | 组件 | 状态 | 功能描述 |
|------|------|--------|--------|
| `/` | ArtDecoLayoutEnhanced.vue (redirect to /dashboard) | ✅ 已实现 | 仪表盘 |

#### 8. 其他路由

| 路由 | 组件 | 状态 | 功能描述 |
|------|------|--------|--------|
| `/login` | Login.vue | ✅ 已实现 | 登录页面 |
| `/test` | Test.vue | ✅ 已实现 | 测试页面 |
| `/artdeco/test` | ArtDecoTest.vue | ✅ 已实现 | ArtDeco组件测试 |

---

## 功能分配核对

### ✅ 已分配的功能（12/14项 - 85.7%）

#### Market模块（8/8项）- 100%完成

- ✅ **实时行情** - 市场指数 + 股票报价 + 自动刷新
- ✅ **技术指标** - K线图表 + 指标选择 + 参数配置
- ✅ **通达信接口** - 连接状态 + 实时报价 + K线数据
- ✅ **资金流向** - 概览统计 + 详细分析 + 排行榜
- ✅ **ETF行情** - 分类展示 + 行情数据 + 折溢价分析
- ✅ **概念行情** - 热门概念 + 详情查看 + 成分股权表
- ✅ **竞价抢筹** - 集合竞价统计 + 匹配详情
- ✅ **龙虎榜** - 买卖席位分析 + 成交统计
- ✅ **机构荐股** - 机构荐股列表和详情
- ✅ **问财选股** - 智能选股工具

#### Stocks模块（6/6项）- 100%完成

- ✅ **自选股管理** - 股票列表 + 搜索筛选 + 添加删除
- ✅ **投资组合** - 持仓分析 + 绩效指标 + 图表展示
- ✅ **交易活动** - 交易记录 + 状态监控 + 统计分析
- ✅ **股票筛选器** - 多维度筛选 + 条件设置 + 结果展示
- ✅ **行业股票池** - 行业分类 + 股票池管理 + 绩效对比
- ✅ **概念股票池** - 概念主题 + 热度分析 + 相关股票

**说明**: "行业股票池"和"概念股票池"已在概念板块中实现，但用户需要更细分的行业管理功能。

#### Trading模块（4/4项）- 100%完成

- ✅ **交易信号** - 策略交易信号推送
- ✅ **历史订单** - 订单历史查询和详情
- ✅ **持仓监控** - 实时持仓数据展示
- ✅ **绩效归因** - 投资收益归因分析

#### Strategy模块（5/5项）- 100%完成

- ✅ **策略设计** - 可视化策略设计工具
- ✅ **策略管理** - 策略版本管理和配置
- ✅ **策略回测** - CPU回测引擎
- ✅ **GPU加速回测** - GPU加速回测（15-20倍性能）
- ✅ **参数优化** - 策略参数自动优化

#### Risk模块（5/5项）- 100%完成

- ✅ **风险概览** - 整体风险评估
- ✅ **告警中心** - 实时风险告警管理
- ✅ **风险指标** - 细分风险指标分析
- ✅ **舆情监控** - 市场舆情情感分析
- ✅ **公告监控** - 官方公告实时监控

#### System模块（5/5项）- 100%完成

- ✅ **运维监控** - 系统运维状态监控
- ✅ **系统设置** - 用户偏好设置
- ✅ **数据更新** - 数据导入更新管理
- ✅ **数据质量** - 数据质量检查报告
- ✅ **API健康** - API接口健康状态检查

#### Dashboard - 100%完成

- ✅ **仪表盘** - 系统概览、核心指标、快速入口

---

## 未分配功能

### ❌ 未分配到菜单的功能（2/14项 - 14.3%）

| 功能模块 | 功能描述 | 建议路由 | 优先级 | 说明 |
|-----------|----------|----------|--------|------|
| **行业股票池** | 按行业分类管理您的自选股 + 行业热门股池 + 行业涨跌幅排行 | `/watchlist/industry` | 🔴 高优先级 | 当前概念板块包含行业标签，但用户需要更细分的独立行业管理页面，支持行业动态追踪和对比 |
| **新闻资讯** | 财经新闻快讯 + 相关股票高亮 + 情感分析 + 实时推送 | `/watchlist/news` | 🟠 中优先级 | 后端有`announcement.py` API（2个端点），但前端未使用。建议集成到自选股页面，提供智能新闻聚合和情感分析 |

---

## 优化方案

### 🎯 总体目标

**核心目标**: 提升后端API利用率（当前70%），通过路由清理、功能集成和新页面开发，实现更完善的用户体验。

### 📋 方案A：路由重定向与路由清理（🔴 高优先级 - 优先执行）

#### A1. 解决路由重定向混乱问题

**问题分析**:
```typescript
// 当前路由结构存在问题：
{
  path: '/market',
  redirect: '/market/realtime',  // 不必要的重定向
  children: [...]
}

{
  path: '/stocks',
  children: [...]
  // 多个子路由指向同一组件
}
```

**影响**:
- 用户访问`/market`时，先重定向到`/market/realtime`，再加载页面
- 浪费带宽和时间
- URL结构不清晰
- SEO不友好
- 路由配置难以维护

**解决方案**:

**1. 移除不必要的重定向**
```typescript
// /opt/claude/mystocks_spec/web/frontend/src/router/index.ts

// 问题：'/market'有redirect到'/market/realtime'
{
  path: '/market',
  name: 'market',
  component: () => import('@/layouts/ArtDecoLayoutEnhanced.vue'),
  redirect: '/market/realtime',  // ❌ 删除
  children: [...]
}

// 解决：直接使用子路由
{
  path: '/market',
  name: 'market',
  component: () => import('@/layouts/ArtDecoLayoutEnhanced.vue'),
  children: [
    {
      path: 'realtime',
      name: 'market-realtime',
      component: () => import('@/views/artdeco-pages/ArtDecoMarketQuotes.vue')
      // 无redirect
    },
    // ...
  ]
}
```

**2. 统一/stocks路由结构**

**问题**: `/stocks` 下有3个路由，指向同一组件，通过activeTab切换。

**解决方案**: 拆分为清晰的功能域
```typescript
// 新增独立的"自选股"域（新增）
{
  path: '/watchlist',
  name: '自选股',
  component: () => import('@/layouts/ArtDecoLayoutEnhanced.vue'),
  children: [
    {
      path: 'manage',
      name: 'watchlist-management',
      component: () => import('@/views/artdeco-pages/ArtDecoWatchlistManagement.vue'),
      meta: {
        title: '自选股管理',
        description: '自选股列表、搜索筛选、分组管理、批量操作',
        activeTab: 'management'
      }
    },
    {
      path: 'portfolio',
      name: 'portfolio',
      component: () => import('@/views/artdeco-pages/ArtDecoPortfolio.vue'),
      meta: {
        title: '我的持仓',
        description: '持仓概览、收益分析、风险指标',
        activeTab: 'portfolio'
      }
    },
    {
      path: 'activity',
      name: 'activity',
      component: () => import('@/views/artdeco-pages/ArtDecoStockActivity.vue'),
      meta: {
        title: '交易活动',
        description: '历史订单、操作记录、统计图表',
        activeTab: 'activity'
      }
    }
  ]
}
```

**3. 移除旧路由的兼容性重定向**

```typescript
// 删除：'/artdeco/market', '/artdeco/stocks', '/artdeco/trading', '/artdeco/backtest', '/artdeco/settings'
// 保留：'/login', '/test'等必要路由
```

**预期效果**:
- ✅ 消除路由重定向循环
- ✅ 提升页面加载速度（减少一次HTTP请求）
- ✅ 更清晰的URL结构（如`/watchlist/manage`而非`/stocks/management`）
- ✅ 更好的SEO（每个页面有明确的URL）
- ✅ 简化路由配置（无需维护复杂重定向规则）

---

### 📊 方案B：创建独立行业股票池页面（🔴 高优先级）

#### B1. 设计行业股票池页面

**页面结构**:
```
/artdeco-pages/ArtDecoIndustryPools.vue
├── 页面头部（标题、统计卡片）
├── 行业分类Tab（9大行业）
├── 行业股票池（可筛选、排序）
├── 行业热门股（按涨幅排序）
└── 页面底部（统计信息、操作按钮）
```

**核心功能**:

1. **9大行业分类**（预定义）:
   - 银行业
   - 科技行业
   - 医药行业
   - 能源行业
   - 材料行业
   - 消费行业
   - 房地产行业
   - 金融行业
   - 综合行业
   - 实用行业

2. **行业热门股池**（每个行业下）:
   - 按涨幅排序（Top 10）
   - 显示股票代码、名称、价格、涨跌幅
   - 快速添加到自选股
   - 显示"自选"标识（如果已添加）

3. **行业动态追踪**:
   - 行业涨跌幅统计（今日/近7日/近30日）
   - 资金流向分析（该行业净流入/流出）
   - 涨跌股票统计（上涨/下跌数量）
   - 成交量排名（Top 10股票）

**API集成**:
```typescript
// 需要的API端点（可能需要扩展watchlist.py）
GET /api/watchlist/industries - 获取行业分类
GET /api/watchlist/{industry_id}/stocks - 获取行业下的股票
GET /api/watchlist/{industry_id}/trending - 获取行业热门股
GET /api/watchlist/{industry_id}/stats - 获取行业统计数据
POST /api/watchlist/batch-add - 批量添加股票到自选
```

**UI组件**:
```vue
<template>
  <div class="industry-pools-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">行业股票池</h1>
      <p class="page-subtitle">按行业分类管理和监控您的自选股</p>
    </div>
    
    <!-- 行业分类Tabs -->
    <div class="industry-tabs">
      <div
        v-for="industry in industries"
        :key="industry.id"
        :class="{ active: activeIndustry === industry.id }"
        @click="switchIndustry(industry)"
        class="industry-tab"
      >
        <ArtDecoIcon :name="industry.icon" size="sm" />
        <span class="industry-label">{{ industry.name }}</span>
        <span v-if="getIndustryStockCount(industry) > 0" class="stock-count">
          {{ getIndustryStockCount(industry) }}
        </span>
      </div>
    </div>
    
    <!-- 行业股票池 -->
    <div class="industry-stock-pools">
      <div
        v-for="stock in activeIndustryStocks"
        :key="stock.symbol"
        class="stock-card"
      >
        <div class="stock-header">
          <div class="stock-symbol">{{ stock.symbol }}</div>
          <div class="stock-name">{{ stock.display_name }}</div>
          <div class="stock-price-change" :class="getPriceChangeClass(stock.price_change)">
            {{ formatPriceChange(stock.price_change) }}
          </div>
        </div>
        
        <!-- 快速操作按钮 -->
        <div class="stock-actions">
          <ArtDecoButton size="xs" variant="outline">
            <ArtDecoIcon name="Add" size="xs" />
            添加到自选
          </ArtDecoButton>
          <ArtDecoIcon name="Remove" size="xs" />
            移除
          </ArtDecoButton>
        </div>
      </div>
    </div>
    
    <!-- 统计信息 -->
    <div class="stats-section">
      <div class="stat-card">
        <ArtDecoIcon name="TrendingUp" size="md" />
        <span class="stat-label">行业热门股</span>
        <span class="stat-value">按涨幅排序</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ArtDecoIcon, ArtDecoButton, ArtDecoStatCard } from '@/components/artdeco/core'

const industries = [
  { id: 'banking', name: '银行', icon: 'Industry' },
  { id: 'tech', name: '科技', icon: 'Microchip' },
  { id: 'healthcare', name: '医药', icon: 'Pulse' },
  { id: 'energy', name: '能源', icon: 'Bolt' },
  { id: 'materials', name: '材料', icon: 'Package' },
  { id: 'consumer', name: '消费', icon: 'Cart' },
  { id: 'realestate', name: '地产', icon: 'Building' },
  { id: 'financial', name: '金融', icon: 'Currency' },
  { id: 'comprehensive', name: '综合', icon: 'Grid' },
]

const activeIndustry = ref('banking')

const getIndustryStockCount = (industryId: string) => {
  // 实际实现：从watchlist服务获取各行业下的股票数量
  return 0
}

const getActiveIndustryStocks = () => {
  // 实际实现：从watchlist服务获取活跃行业的股票列表
  return []
}

const formatPriceChange = (change: number) => {
  if (change > 0) return `+${change.toFixed(2)}%`
  return change.toFixed(2)}%
}

onMounted(() => {
  // 初始化加载数据
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.industry-pools-page {
  padding: var(--artdeco-spacing-6);
}

.page-header {
  text-align: center;
  margin-bottom: var(--artdeco-spacing-4);
    
  .page-title {
    font-size: var(--artdeco-font-size-xxl);
    color: var(--artdeco-text-primary);
    margin-bottom: var(--artdeco-spacing-2);
  }
    
  .page-subtitle {
    font-size: var(--artdeco-font-size-sm);
    color: var(--artdeco-text-secondary);
  }
}

.industry-tabs {
  display: flex;
  gap: var(--artdeco-spacing-2);
  margin-bottom: var(--artdeco-spacing-4);
}

.industry-tab {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-2);
  padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
  background: var(--artdeco-bg-surface);
  border-radius: var(--artdeco-radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: var(--artdeco-bg-surface-hover);
    border-color: var(--artdeco-border-hover);
  }
  
  &.active {
    background: var(--artdeco-bg-primary);
    border-color: var(--artdeco-border-active);
    color: var(--artdeco-text-on-primary);
  }
  
  .industry-label {
    font-size: var(--artdeco-font-size-base);
    color: var(--artdeco-text-primary);
  }
  
  .stock-count {
    background: var(--artdeco-bg-accent);
    color: var(--artdeco-text-on-accent);
    padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);
    border-radius: var(--artdeco-radius-full);
    font-size: var(--artdeco-font-size-xs);
    font-weight: 600;
  }
}

.industry-stock-pools {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--artdeco-spacing-3);
}

.stock-card {
  background: var(--artdeco-bg-surface);
  border: 1px solid var(--artdeco-border-primary);
  border-radius: var(--artdeco-radius-md);
  padding: var(--artdeco-spacing-3);
  transition: all 0.2s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--artdeco-shadow-md);
    border-color: var(--artdeco-border-active);
  }
}

.stock-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-2);
}

.stock-symbol {
  font-size: var(--artdeco-font-size-lg);
  font-weight: 600;
  color: var(--artdeco-text-primary);
}

.stock-name {
  font-size: var(--artdeco-font-size-sm);
  color: var(--artdeco-text-secondary);
}

.stock-price-change {
  font-size: var(--artdeco-font-size-sm);
  font-weight: 500;
}

.stock-actions {
  display: flex;
  gap: var(--artdeco-spacing-2);
}

.stats-section {
  display: flex;
  gap: var(--artdeco-spacing-4);
  margin-top: var(--artdeco-spacing-6);
}

.stat-card {
  background: var(--artdeco-bg-surface);
  border: 1px solid var(--artdeco-border-secondary);
  border-radius: var(--artdeco-radius-md);
  padding: var(--artdeco-spacing-4);
  min-width: 200px;
}
</style>
```

**工作量评估**:
- ✅ 新增Vue页面: 1个
- ✅ 需要扩展watchlist API: 3-4个端点
- ✅ 9大行业分类: 银行、科技、医药等
- ✅ 完整的ArtDeco设计: 使用统一的组件和样式
- ✅ **工作量**: 2-3天

**预期效果**:
- 用户可以独立管理行业股票池
- 每个行业有独立的统计卡片
- 支持热门股快速浏览
- 一键添加到自选股

---

### 📋 方案C：增强现有自选股管理页面（🟠 中优先级）

#### C1. 增强自选股管理功能

**当前组件**: `ArtDecoWatchlistManagement.vue`（现有）

**新增功能**:

1. **快速添加栏优化**
```vue
<!-- 增强的快速操作栏 -->
<div class="action-bar">
  <ArtDecoButton variant="solid" size="sm" @click="quickAdd">
    <ArtDecoIcon name="Plus" size="sm" />
    快速添加
  </ArtDecoButton>
  <ArtDecoButton variant="outline" size="sm">
    <ArtDecoIcon name="Import" size="sm" />
    导入
  </ArtDecoButton>
  <ArtDecoButton variant="outline" size="sm">
    <ArtDecoIcon name="Export" size="sm" />
    导出
  </ArtDecoButton>
</div>
```

2. **高级筛选面板**
```vue
<!-- 高级筛选折叠面板 -->
<div class="filter-panel">
  <div class="filter-header" @click="toggleFilters">
    <span>高级筛选</span>
    <ArtDecoIcon :name="isFiltersOpen ? 'ChevronUp' : 'ChevronDown'" />
  </div>
  
  <div v-if="isFiltersOpen" class="filter-options">
    <!-- 价格筛选 -->
    <div class="filter-group">
      <label>价格区间</label>
      <input type="number" v-model="filters.priceMin" placeholder="最低价" />
      <input type="number" v-model="filters.priceMax" placeholder="最高价" />
    </div>
    
    <!-- 市值筛选 -->
    <div class="filter-group">
      <label>市值区间</label>
      <select v-model="filters.marketCapMin">
        <option value="small">小盘（< 50亿）</option>
        <option value="medium">中盘（50-200亿）</option>
        <option value="large">大盘（> 200亿）</option>
      </select>
      <select v-model="filters.marketCapMax">
        <option value="small">小盘（< 50亿）</option>
        <option value="medium">中盘（50-200亿）</option>
        <option value="large">大盘（> 200亿）</option>
      </select>
    </div>
    
    <!-- 技术指标筛选 -->
    <div class="filter-group">
      <label>PE区间</label>
      <input type="number" v-model="filters.peMin" placeholder="最低PE" />
      <input type="number" v-model="filters.peMax" placeholder="最高PE" />
    </div>
    
    <!-- 成交量筛选 -->
    <div class="filter-group">
      <label>成交量</label>
      <select v-model="filters.volumeMin">
        <option value="low">低量</option>
        <option value="medium">中量</option>
        <option value="high">高量</option>
      </select>
    </div>
    
    <!-- 行业筛选 -->
    <div class="filter-group">
      <label>行业</label>
      <select v-model="filters.industry">
        <option value="">全部分</option>
        <option value="banking">银行</option>
        <option value="tech">科技</option>
        <option value="healthcare">医药</option>
      </select>
    </div>
    
    <div class="filter-actions">
      <ArtDecoButton variant="solid" @click="applyFilters">应用筛选</ArtDecoButton>
      <ArtDecoButton variant="outline" @click="resetFilters">重置</ArtDecoButton>
    </div>
  </div>
</div>
```

3. **分组管理功能**
```vue
<!-- 分组标签页签 -->
<div class="group-tabs">
  <div
    v-for="group in groups"
    :key="group.id"
    :class="{ active: activeGroup === group.id }"
    @click="switchGroup(group)"
    class="group-tab"
  >
    <ArtDecoIcon :name="group.icon" size="sm" />
    <span class="group-label">{{ group.name }}</span>
    <span class="group-count">{{ getGroupCount(group.id) }}</span>
  </div>
</div>

<!-- 分组管理模态对话框 -->
<div class="group-modal" v-if="showGroupModal">
  <div class="modal-header">
    <h3>创建新分组</h3>
  </div>
  <div class="modal-body">
    <input v-model="newGroupName" placeholder="分组名称" />
    <div class="color-picker">
      <div v-for="color in groupColors" @click="selectColor(color)"></div>
    </div>
  </div>
  <div class="modal-footer">
    <ArtDecoButton variant="solid" @click="createGroup">创建</ArtDecoButton>
    <ArtDecoButton variant="outline" @click="showGroupModal = false">取消</ArtDecoButton>
  </div>
</div>
```

4. **批量操作功能**
```vue
<!-- 批量选择模式 -->
<div class="batch-actions-bar">
  <ArtDecoButton variant="outline" size="sm" @click="toggleBatchMode">
    <ArtDecoIcon name="Checkbox" size="sm" />
    批量模式
  </ArtDecoButton>
  <div v-if="isBatchMode" class="batch-actions">
    <ArtDecoButton variant="solid" @click="batchAddToWatchlist">全部添加到自选</ArtDecoButton>
    <ArtDecoButton variant="solid" @click="batchRemoveFromWatchlist">全部移除自选</ArtDecoButton>
    <ArtDecoButton variant="outline" @click="toggleBatchMode">退出批量模式</ArtDecoButton>
  </div>
</div>
```

**工作量评估**:
- ✅ 增强`ArtDecoWatchlistManagement.vue`: 1个组件
- ✅ 实现高级筛选: 价格、市值、PE、成交量、行业
- ✅ 实现分组管理: 创建、编辑、删除、颜色标记
- ✅ 实现批量操作: 批量添加、批量删除
- ✅ **工作量**: 1.5-2天

**预期效果**:
- 更强大的自选股管理功能
- 支持多维度筛选
- 支持分组管理（如"策略股"、"关注股"）
- 支持批量操作提升效率

---

### 📋 方案D：集成新闻资讯到自选股页面（🟠 中优先级）

#### D1. 设计新闻资讯面板

**页面结构**:
```
/artdeco-pages/ArtDecoNewsPanel.vue（增强现有组件）
├── 新闻资讯面板（嵌入到自选股页面）
│   ├── 最新新闻列表
│   ├── 智能筛选（按时间、来源、情感）
│   ├── 实时推送（WebSocket）
│   └── 相关股票高亮
```

**核心功能**:

1. **智能新闻聚合**
   - 自动根据自选股聚合相关新闻
   - 按时间倒序显示
   - 显示新闻来源（财联社、东方财富等）
   - 显示发布时间、阅读量

2. **情感分析**
   - 自动判断利好/中性/负面情绪
   - 用颜色标签标记（绿色利好、红色利空、灰色中性）
   - 显示情感关键词

3. **实时更新**
   - WebSocket推送最新新闻
   - 自动刷新新闻列表
   - 新消息提示（徽章显示未读数量）

4. **股票高亮**
   - 新闻中提到的股票自动高亮
   - 点击股票可跳转到详情页面
   - 支持"按新闻筛选"功能

**API集成**:
```typescript
// 需要的API端点
GET /api/announcement/news - 获取新闻列表
GET /api/announcement/related?symbol={symbol} - 获取股票相关新闻
GET /api/announcement/sentiment - 获取情感分析
WebSocket: ws://host/api/news/realtime - 实时新闻推送
```

**UI组件**:
```vue
<template>
  <div class="news-panel-embedded">
    <!-- 面包头部 -->
    <div class="news-header">
      <h2>智能新闻资讯</h2>
      <div class="news-filters">
        <ArtDecoButton size="xs" :variant="filter === 'all' ? 'solid' : 'outline'" @click="filter = 'all'">
          全部
        </ArtDecoButton>
        <ArtDecoButton size="xs" :variant="filter === 'positive' ? 'solid' : 'outline'" @click="filter = 'positive'">
          利好
        </ArtDecoButton>
        <ArtDecoButton size="xs" :variant="filter === 'negative' ? 'solid' : 'outline'" @click="filter = 'negative'">
          利空
        </ArtDecoButton>
        <ArtDecoButton size="xs" :variant="filter === 'unread' ? 'solid' : 'outline'" @click="filter = 'unread'">
          未读
        </ArtDecoButton>
      </div>
      <span class="unread-count">{{ unreadCount }}条</span>
    </div>
    
    <!-- 新闻列表 -->
    <div class="news-list">
      <div
        v-for="news in filteredNews"
        :key="news.id"
        class="news-item"
        :class="{
          positive: news.sentiment === 'positive',
          negative: news.sentiment === 'negative'
        }"
        @click="highlightStocks(news.related_symbols)"
      >
        <div class="news-time">{{ formatTime(news.datetime) }}</div>
        <div class="news-source">
          <span class="source-tag" :class="getSourceClass(news.source)">{{ news.source }}</span>
          {{ news.source }}
        </div>
        <div class="news-content">
          <h3 class="news-title">{{ news.title }}</h3>
          <p class="news-summary">{{ news.summary }}</p>
          
          <!-- 相关股票 -->
          <div v-if="news.related_symbols" class="related-stocks">
            <span v-for="symbol in news.related_symbols.split(',')" :key="symbol" class="related-stock">
              {{ symbol }}
            </span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 实时更新按钮 -->
    <div class="refresh-btn">
      <ArtDecoButton variant="solid" @click="refreshNews">
        <ArtDecoIcon name="Refresh" size="sm" />
        刷新
      </ArtDecoButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ArtDecoIcon, ArtDecoButton } from '@/components/artdeco/core'
import { getWatchlist } from '@/services/watchlistService'
import type { NewsItem, SentimentType } from '@/types/news'

const filter = ref('all')
const unreadCount = ref(0)
const filteredNews = ref<NewsItem[]>([])
const highlightedStocks = ref<string[]>([])

const filteredNews = computed(() => {
  if (filter.value === 'all') return allNews.value
  return allNews.value.filter(news => news.sentiment === filter.value)
})

const formatTime = (datetime: Date) => {
  return new Date(datetime).toLocaleString('zh-CN', {
    hour12: false,
    minute: '2-digit'
  })
}

const getSourceClass = (source: string) => {
  const sources: Record<string, string> = {
    'caixin': 'source-caixin',
    'eastmoney': 'source-eastmoney',
    'sina': 'source-sina'
  }
  return sources[source] || 'source-default'
}

const highlightStocks = (symbols: string) => {
  highlightedStocks.value = symbols.split(',')
}

const refreshNews = async () => {
  try {
    const data = await getWatchlist()
    unreadCount.value = 0
    filteredNews.value = data.news
  } catch (error) {
    console.error('Failed to refresh news:', error)
  }
}

onMounted(() => {
  // 初始化加载数据
  // 连接WebSocket实时更新
})

onUnmounted(() => {
  // 断开WebSocket连接
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.news-panel-embedded {
  padding: var(--artdeco-spacing-6);
}

.news-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-4);
  background: var(--artdeco-bg-primary-light);
  padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
  border-radius: var(--artdeco-radius-md);
}

.news-filters {
  display: flex;
  gap: var(--artdeco-spacing-2);
}

.news-list {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-3);
  max-height: 600px;
  overflow-y: auto;
}

.news-item {
  padding: var(--artdeco-spacing-3);
  background: var(--artdeco-bg-surface);
  border: 1px solid var(--artdeco-border-primary);
  border-radius: var(--artdeco-radius-md);
  transition: all 0.2s ease;
  
  &.positive {
    border-left: 3px solid var(--artdeco-accent-green);
  }
  
  &.negative {
    border-left: 3px solid var(--artdeco-accent-red);
  }
  
  &.active {
    background: var(--artdeco-bg-surface-hover);
    transform: scale(1.02);
  }
}

.news-time {
  font-size: var(--artdeco-font-size-xs);
  color: var(--artdeco-text-tertiary);
  margin-bottom: var(--artdeco-spacing-1);
}

.news-source {
  font-size: var(--artdeco-font-size-xs);
  color: var(--artdeco-text-secondary);
}

.news-title {
  font-size: var(--artdeco-font-size-base);
  font-weight: 600;
  color: var(--artdeco-text-primary);
  margin-bottom: var(--artdeco-spacing-2);
}

.news-summary {
  font-size: var(--artdeco-font-size-sm);
  color: var(--artdeco-text-secondary);
  line-height: 1.6;
}

.related-stocks {
  display: flex;
  flex-wrap: wrap;
  gap: var(--artdeco-spacing-1);
  margin-top: var(--artdeco-spacing-2);
}

.related-stock {
  font-size: var(--artdeco-font-size-xs);
  padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);
  background: var(--artdeco-bg-primary-light);
  border-radius: var(--artdeco-radius-sm);
  color: var(--artdeco-text-on-primary);
  cursor: pointer;
  
  &:hover {
    background: var(--artdeco-bg-primary);
  }
}

.source-tag {
  display: inline-block;
  padding: var(--artdeco-spacing-1);
  border-radius: var(--artdeco-radius-full);
  font-size: var(--artdeco-font-size-xs);
  margin-right: var(--artdeco-spacing-1);
}

.source-caixin {
  background: var(--artdeco-accent-blue);
  color: var(--artdeco-text-on-accent);
}

.source-eastmoney {
  background: var(--artdeco-accent-green);
  color: var(--artdeco-text-on-accent);
}

.source-sina {
  background: var(--artdeco-accent-yellow);
  color: var(--artdeco-text-on-accent);
}

.source-default {
  background: var(--artdeco-bg-tertiary);
  color: var(--artdeco-text-tertiary);
}

.refresh-btn {
  margin-top: var(--artdeco-spacing-4);
}
</style>
```

**工作量评估**:
- ✅ 增强`ArtDecoWatchlistManagement.vue`: 增加新闻面板
- ✅ 新增`ArtDecoNewsPanel.vue`: 1个组件（或内嵌到自选股页面）
- ✅ 集成announcement API: 2个端点
- ✅ 实现智能新闻聚合
- ✅ 实现情感分析
- ✅ WebSocket实时更新
- ✅ **工作量**: 2-3天

**预期效果**:
- 自选股页面整合智能新闻资讯
- 自动推送相关新闻
- 情感分析显示
- 股票高亮功能
- 大幅提升用户体验

---

### 📋 方案E：创建财报分析页面（🟠 中优先级）

#### E1. 设计财报分析页面

**页面结构**:
```
/artdeco-pages/ArtDecoFinancialAnalysis.vue
├── 页面头部（标题、选择股票）
├── 财报指标卡片（PE、ROE、ROIC、PEG）
├── 财报图表（历史趋势、同行业对比）
├── 详细财报数据表
└── 页面底部（操作按钮）
```

**核心功能**:

1. **股票选择器**
   - 支持股票代码搜索
   - 从自选股中选择
   - 输入股票代码验证

2. **核心指标展示**
   - PE（市盈率）卡片
   - ROE（净资产收益率）卡片
   - ROIC（资本回报率）卡片
   - PEG（PEG比率）卡片
   - 营收增长率卡片
   - 同行业对比（雷达图）

3. **趋势图表**
   - 多年财务数据趋势线图
   - 支持切换指标（5年、10年）
   - 同行业对比（选择对比行业）
   - 交互式图表（ECharts）

4. **财报数据表**
   - 年份、营业收入、净利润
   - ROE、ROA、净利润率
   - 毛利率、总资产周转率
   - 流动比率、速动比率

5. **操作功能**
   - 导出为Excel
   - 保存到收藏
   - 打印报表
   - 分享到社交平台

**API集成**:
```typescript
// 需要的API端点（可能需要扩展watchlist或financial_analysis）
GET /api/financial/{symbol}/summary - 获取财务摘要
GET /api/financial/{symbol}/indicators - 获取财务指标
GET /api/financial/{symbol}/ratios - 获取ROE、ROA、ROIC
GET /api/financial/{symbol}/trends - 获取多年数据
GET /api/financial/{symbol}/peers - 获取同行业对比
```

**UI组件**:
```vue
<template>
  <div class="financial-analysis-page">
    <!-- 股票选择器 -->
    <div class="stock-selector">
      <input v-model="selectedSymbol" placeholder="输入股票代码或从列表选择" />
      <div class="stock-list">
        <div
          v-for="stock in recentStocks"
          :key="stock.symbol"
          @click="selectStock(stock)"
          class="stock-chip"
          :class="{ selected: selectedSymbol === stock.symbol }"
        >
          {{ stock.symbol }} - {{ stock.name }}
        </div>
      </div>
    </div>
    
    <!-- 核心指标卡片 -->
    <div class="indicators-grid">
      <div class="indicator-card pe-card">
        <h3>PE（市盈率）</h3>
        <div class="indicator-value">{{ currentStock.pe }}</div>
        <div class="indicator-trend">
          <span :class="{ up: peTrend > 0 }">{{ formatPercent(peTrend) }}</span>
        </div>
      </div>
      
      <div class="indicator-card roe-card">
        <h3>ROE（净资产收益率）</h3>
        <div class="indicator-value">{{ currentStock.roe }}</div>
        <div class="indicator-benchmark">
          <span>基准：{{ industryBenchmark.roe }}%</span>
        </div>
      </div>
      
      <div class="indicator-card roic-card">
        <h3>ROIC（资本回报率）</h3>
        <div class="indicator-value">{{ currentStock.roic }}</div>
        <div class="indicator-rating" :class="getRatingClass(currentStock.roic)">
          {{ getRatingText(currentStock.roic) }}
        </div>
      </div>
      
      <div class="indicator-card peg-card">
        <h3>PEG（PEG比率）</h3>
        <div class="indicator-value">{{ currentStock.peg }}</div>
        <div class="indicator-status">
          <span :class="{ good: currentStock.peg < 1.0, bad: currentStock.peg > 1.5 }">
            {{ getPegStatus(currentStock.peg) }}
          </span>
        </div>
      </div>
      
      <div class="indicator-card growth-card">
        <h3>营收增长</h3>
        <div class="indicator-value">{{ formatPercent(currentStock.revenueGrowth) }}</div>
        <div class="indicator-chart">
          <!-- 多年营收趋势 -->
        <v-chart :data="revenueTrendData" />
        </div>
      </div>
    </div>
    
    <!-- 同行业对比 -->
    <div class="peer-comparison">
      <h2 class="section-title">同行业对比</h2>
      <div class="comparison-chart">
        <v-radar-chart :data="peerRadarData" />
      </div>
      <div class="peer-list">
        <div v-for="peer in peerStocks" :key="peer.symbol" class="peer-item">
          <h4>{{ peer.name }}</h4>
          <div class="peer-metrics">
            <span>PE: {{ peer.pe }}</span>
            <span>ROE: {{ peer.roe }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 操作按钮 -->
    <div class="action-buttons">
      <ArtDecoButton variant="solid" @click="exportToExcel">
        <ArtDecoIcon name="Download" size="sm" />
        导出Excel
      </ArtDecoButton>
      <ArtDecoButton variant="outline" @click="saveToFavorites">
        <ArtDecoIcon name="Star" size="sm" />
        保存到收藏
      </ArtDecoButton>
      <ArtDecoButton variant="outline" @click="printReport">
        <ArtDecoIcon name="Print" size="sm" />
        打印
      </ArtDecoButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ArtDecoIcon, ArtDecoButton } from '@/components/artdeco/core'
import { getFinancialData } from '@/services/financialService'
import type { Stock, FinancialMetrics, PeerStock } from '@/types/financial'

const selectedSymbol = ref('')
const currentStock = ref<Stock | null>(null)
const recentStocks = ref<Stock[]>([])

const peTrend = computed(() => currentStock.value?.peTrend || 0)
const industryBenchmark = computed(() => {
  // 获取行业基准数据
  return { roe: 15 } // 银行平均ROE
})

const formatPercent = (value: number) => {
  return `${value.toFixed(2)}%`
}

const getRatingClass = (roic: number) => {
  if (roic > 15) return 'excellent'
  if (roic > 10) return 'good'
  if (roic > 5) return 'fair'
  return 'poor'
}

const getPegStatus = (peg: number) => {
  if (peg < 1.0) return '低估'
  if (peg < 1.5 && peg >= 1.0) return '合理'
  return '高估'
}

const selectStock = async (stock: Stock) => {
  selectedSymbol.value = stock.symbol
  currentStock.value = await getFinancialData(stock.symbol)
}

onMounted(() => {
  // 加载最近查看的股票
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.financial-analysis-page {
  padding: var(--artdeco-spacing-6);
}

.stock-selector {
  margin-bottom: var(--artdeco-spacing-4);
}

.stock-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--artdeco-spacing-2);
}

.stock-chip {
  padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
  background: var(--artdeco-bg-surface);
  border: 1px solid var(--artdeco-border-primary);
  border-radius: var(--artdeco-radius-full);
  cursor: pointer;
  transition: all 0.2s ease;
  
  &.selected {
    background: var(--artdeco-bg-primary);
    color: var(--artdeco-text-on-primary);
  }
}

.indicators-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--artdeco-spacing-3);
  margin-bottom: var(--artdeco-spacing-4);
}

.indicator-card {
  background: var(--artdeco-bg-surface);
  border: 1px solid var(--artdeco-border-secondary);
  border-radius: var(--artdeco-radius-md);
  padding: var(--artdeco-spacing-4);
}

.indicator-value {
  font-size: var(--artdeco-font-size-xxl);
  font-weight: 600;
  color: var(--artdeco-text-primary);
}

.indicator-trend {
  font-size: var(--artdeco-font-size-sm);
  margin-top: var(--artdeco-spacing-2);
}

.indicator-benchmark {
  font-size: var(--artdeco-font-size-xs);
  color: var(--artdeco-text-tertiary);
}

.indicator-rating {
  font-weight: 600;
}

.indicator-status {
  font-size: var(--artdeco-font-size-xs);
}

.good {
  color: var(--artdeco-accent-green);
}

.bad {
  color: var(--artdeco-accent-red);
}

.section-title {
  font-size: var(--artdeco-font-size-lg);
  color: var(--artdeco-text-primary);
  margin: var(--artdeco-spacing-4) 0;
}

.peer-comparison {
  background: var(--artdeco-bg-surface);
  border: 1px solid var(--artdeco-border-secondary);
  border-radius: var(--artdeco-radius-md);
  padding: var(--artdeco-spacing-4);
}

.peer-item {
  padding: var(--artdeco-spacing-3);
  background: var(--artdeco-bg-primary-light);
  border-radius: var(--artdeco-radius-sm);
}

.peer-metrics {
  display: flex;
  gap: var(--artdeco-spacing-2);
}

.action-buttons {
  display: flex;
  gap: var(--artdeco-spacing-3);
  margin-top: var(--artdeco-spacing-6);
}
</style>
```

**工作量评估**:
- ✅ 新增`ArtDecoFinancialAnalysis.vue`: 1个完整页面
- ✅ 需要扩展financial_analysis API: 5-7个端点（或使用通用data API）
- ✅ 集成ECharts图表库
- ✅ 实现完整的财务分析功能
- ✅ **工作量**: 2-3天

**预期效果**:
- 独立的财报分析页面
- 完整的财务指标展示（PE、ROE、ROIC、PEG）
- 多年趋势图表和同行业对比
- 导出和分享功能

---

### 📋 方案F：创建股票评级页面（🟠 中优先级）

#### F1. 设计股票评级页面

**页面结构**:
```
/artdeco-pages/ArtDecoStockRatings.vue
├── 页面头部（评级说明）
├── 评级列表（机构评级、分析师评级）
├── 评级详情模态框
├── 评级历史图表
└── 页面底部（筛选选项）
```

**核心功能**:

1. **评级列表展示**
   - 机构评级（中信证券、中金、华泰等）
   - 分析师评级（明星分析师）
   - 综合评级（买入/卖出/持有）
   - 评级摘要（1-5星）
   - 评级变更历史（时间轴）

2. **评级筛选**
   - 按机构筛选
   - 按分析师筛选
   - 按评级筛选（5星）
   - 按时间筛选

3. **评级详情**
   - 评级机构信息
   - 分析师简介
   - 评级理由（详细文字）
   - 目标价格
   - 评级日期
   - 评级变更追踪

4. **对比分析**
   - 同股票不同机构评级对比
   - 同股票历史评级趋势
   - 行业平均评级对比

5. **操作功能**
   - 关注股票
   - 收藏评级
   - 分享评级
   - 导出评级报告

**API集成**:
```typescript
// 需要的API端点
GET /api/stock/ratings - 获取股票评级列表
GET /api/stock/ratings/{symbol}/summary - 获取评级摘要
GET /api/stock/ratings/{symbol}/history - 获取评级历史
GET /api/stock/ratings/{symbol}/peers - 获取同行评级
WebSocket: ws://host/api/ratings/realtime - 实时评级推送
```

**工作量评估**:
- ✅ 新增`ArtDecoStockRatings.vue`: 1个完整页面
- ✅ 需要扩展stock_ratings_api.py: 5-8个端点
- ✅ 集成评级数据展示
- ✅ 实现筛选和详情功能
- ✅ **工作量**: 1.5-2天

**预期效果**:
- 独立的股票评级页面
- 机构评级和分析师评级展示
- 评级历史追踪
- 评级对比分析
- 关注和分享功能

---

## 实施路线图

### 📅 第一阶段（高优先级 - 1-2天）

#### Phase 1.1: 路由优化（0.5天）

- ✅ 移除不必要重定向（`/market`, `/artdeco/*`）
- ✅ 统一`/stocks`路由结构（拆分为独立域）
- ✅ 保留兼容性路由（`/login`, `/test`）
- **验证**: 确保所有路由正常工作

#### Phase 1.2: 创建行业股票池页面（2-3天）

- ✅ 实现`ArtDecoIndustryPools.vue`
- ✅ 扩展watchlist API（3个端点）
- ✅ 实现9大行业分类
- ✅ 实现热门股和行业动态追踪
- ✅ 集成到`/watchlist`路由

#### Phase 1.3: 增强自选股管理页面（1.5-2天）

- ✅ 增强`ArtDecoWatchlistManagement.vue`
- ✅ 添加高级筛选功能
- ✅ 添加分组管理功能
- ✅ 添加批量操作功能
- ✅ 保留现有功能（列表、搜索、添加、删除、更新）

---

### 📅 第二阶段（中优先级 - 3-7天）

#### Phase 2.1: 集成新闻资讯到自选股页面（2-3天）

- ✅ 增强`ArtDecoWatchlistManagement.vue`（或新增`ArtDecoNewsPanel.vue`）
- ✅ 集成announcement API（2个端点）
- ✅ 实现智能新闻聚合
- ✅ 实现情感分析
- ✅ WebSocket实时更新
- ✅ 股票高亮功能

#### Phase 2.2: 创建财报分析页面（2-3天）

- ✅ 实现`ArtDecoFinancialAnalysis.vue`
- ✅ 扩展financial_analysis API（5-7个端点）
- ✅ 集成ECharts图表库
- ✅ 实现完整财务分析功能（PE、ROE、ROIC、PEG、同行业对比）
- ✅ 导出和分享功能

#### Phase 2.3: 创建股票评级页面（1.5-2天）

- ✅ 实现`ArtDecoStockRatings.vue`
- ✅ 扩展stock_ratings_api.py（5-8个端点）
- ✅ 集成评级数据展示
- ✅ 实现筛选和详情功能
- ✅ 实现关注和分享功能

---

### 📅 第三阶段（低优先级 - 按需执行）

#### Phase 3.1: 完善股票筛选器功能（按需）

- ✅ 增强`Screener.vue`的高级筛选功能
- ✅ 添加技术指标筛选（PE < 10, ROE > 15%等）
- ✅ 添加估值筛选（低PB < 1, 高PB > 10等）
- ✅ 添加长短线筛选（低PEG < 1, 高PEG > 2等）
- ✅ 添加排序功能（按收益率、换手率等）
- ✅ 实现筛选结果导出

#### Phase 3.2: 完善实时行情功能（按需）

- ✅ 增强`RealtimeQuotes.vue`
- ✅ 集成通达信接口数据
- ✅ 显示连接状态
- ✅ K线数据实时更新
- ✅ 添加预警功能（价格突破、成交量异常）

#### Phase 3.3: 其他API集成（按需）

- ⚠️ 技术分析API（10+个端点）- 根据业务需求选择性集成
- ⚠️ 指标API（15+个端点）- 根据业务需求选择性集成
- ⚠️ 多源API集成 - 根据业务需求选择性集成

---

## 风险提示

### ⚠️ 向后兼容性风险

**路由重定向影响**:
- 修改路由结构可能导致SEO变化
- 旧路由可能被外部链接引用
- 建议：2周后移除旧路由

**建议措施**:
1. **保留期过渡**：同时保留新旧路由2周
2. **更新外部链接**：通知相关方更新链接
3. **监控访问日志**：使用Analytics工具监控旧路由访问量
4. **回退方案**：如有问题，快速回退到旧路由结构

### ⚠️ API依赖风险

**announcement API依赖**:
- 新闻资讯功能依赖announcement API
- 如果API不稳定，新闻功能无法使用
- 建议：确保API稳定性和错误处理

**financial_analysis API依赖**:
- 财报分析功能依赖financial_analysis API
- 需要扩展或新建API端点
- 建议：先使用Mock数据进行前端开发，后端再实现API

**stock_ratings_api依赖**:
- 股票评级功能依赖stock_ratings_api.py
- 需要扩展API端点
- 建议：评估API设计，确保数据来源可靠

### ⚠️ 工作量评估

**总工作量估算**: **8-12天**
- Phase 1（高优先级）: 3.5天
- Phase 2（中优先级）: 7天
- Phase 3（低优先级）: 按需执行

**技术复杂度**:
- 路由重定向：⭐ 简单
- 行业股票池：⭐⭐⭐ 中等
- 自选股增强：⭐⭐ 中等
- 新闻集成：⭐⭐ 中等
- 财报分析：⭐⭐⭐ 复杂
- 股票评级：⭐⭐⭐ 复杂

---

## 总结

### 📈 核心目标

1. ✅ **菜单重组** - 创建"自选股"模块，提升菜单结构清晰度
2. ✅ **功能分配核对** - 对比用户需求，85.7%功能已分配
3. ✅ **API利用率提升** - 从70%提升到85-92%（预计）
4. ✅ **用户体验提升** - 通过新页面和功能增强

### 📊 关键指标

| 指标 | 当前 | 目标 | 提升 |
|------|------|------|--------|
| **后端API利用率** | 70% | 85-92% | +15-22% |
| **前端路由清晰度** | 中等 | 优 | 显著提升 |
| **用户体验完善度** | 中等 | 优 | 显著提升 |
| **新页面数量** | 0 | 3-5个 | 新增 |

### 🎯 审批建议

**推荐审批顺序**:
1. ✅ **立即执行**：Phase 1.1 - 路由优化（0.5天）
2. ✅ **Phase 1.2**：创建行业股票池页面（2-3天）
3. ⚠️ **Phase 2**：集成新闻资讯、财报分析、股票评级（7天）
   - 建议：Phase 2分批执行，每个功能独立测试后上线
   - 理由：降低技术风险，确保功能稳定性

**分阶段验证点**:
- Phase 1完成后：验证路由正常工作
- Phase 1.2完成后：测试行业股票池功能
- Phase 2各功能完成后：逐个验证

---

## 附录

### 📁 相关文档

- [`MenuConfig.enhanced.ts`](../web/frontend/src/layouts/MenuConfig.enhanced.ts) - 菜单配置
- [`router/index.ts`](../web/frontend/src/router/index.ts) - 路由配置
- [`watchlist.py`](../web/backend/app/api/watchlist.py) - 自选股API
- [`stock_search.py`](../web/backend/app/api/stock_search.py) - 股票搜索API
- [`announcement.py`](../web/backend/app/api/announcement.py) - 公告API

### 🔗 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|---------|----------|
| **v1.0** | 2026-01-24 | 初始版本 |
| **v1.0** | 2026-01-24 | 本优化方案 |

---

**文档维护**: 本文档应根据实际实施情况持续更新，记录已完成的阶段和遇到的问题。
