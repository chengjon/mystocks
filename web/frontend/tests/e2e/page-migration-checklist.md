# Phase 2.5: 页面迁移验证清单

## 迁移状态说明

- ✅ **已验证**: 页面在新路由下正常工作
- ⚠️ **需注意**: 页面工作但有小问题
- ❌ **待修复**: 页面在新路由下不工作

## Dashboard域 (MainLayout)

| 页面 | 旧路由 | 新路由 | 状态 | 备注 |
|------|--------|--------|------|------|
| Dashboard | `/dashboard` | `/dashboard` | ✅ | 主仪表盘 |
| Watchlist | `/stocks` | `/dashboard/watchlist` | ⏳ | 股票列表 |
| Portfolio | `/portfolio` | `/dashboard/portfolio` | ⏳ | 投资组合管理 |
| Activity | `/trade` | `/dashboard/activity` | ⏳ | 交易活动 |

## Market Data域 (MarketLayout)

| 页面 | 旧路由 | 新路由 | 状态 | 备注 |
|------|--------|--------|------|------|
| Stock List | `/market` | `/market/list` | ✅ | 市场行情 |
| Realtime | `/realtime` | `/market/realtime` | ⏳ | 实时监控 |
| K-Line | `/stock-detail/:symbol` | `/market/kline/:symbol` | ⏳ | K线图表 |
| Depth | `/tdx-market` | `/market/depth` | ⏳ | 盘口深度 |
| Sector | `/analysis/industry-concept` | `/market/sector` | ⏳ | 板块分析 |

## Stock Analysis域 (DataLayout)

| 页面 | 旧路由 | 新路由 | 状态 | 备注 |
|------|--------|--------|------|------|
| Stock Screener | `/analysis` | `/analysis/screener` | ✅ | 选股器 |
| Industry | `/analysis/industry-concept` | `/analysis/industry` | ⏳ | 行业分析 |
| Concept | - | `/analysis/concept` | ⏳ | 概念股（新功能） |
| Fundamental | `/stock-detail/:symbol` | `/analysis/fundamental` | ⏳ | 基本面分析 |
| Technical | `/technical` | `/analysis/technical` | ⏳ | 技术分析 |

## Risk Monitor域 (RiskLayout)

| 页面 | 旧路由 | 新路由 | 状态 | 备注 |
|------|--------|--------|------|------|
| Overview | `/risk` | `/risk/overview` | ✅ | 风险概览 |
| Position Risk | `/trade` | `/risk/position` | ⏳ | 持仓风险 |
| Portfolio Risk | `/portfolio` | `/risk/portfolio` | ⏳ | 组合风险 |
| Alerts | `/announcement` | `/risk/alerts` | ⏳ | 风险告警 |
| Stress Test | `/backtest` | `/risk/stress` | ⏳ | 压力测试 |

## Strategy Management域 (StrategyLayout)

| 页面 | 旧路由 | 新路由 | 状态 | 备注 |
|------|--------|--------|------|------|
| My Strategies | `/strategy` | `/strategy/list` | ⏳ | 策略管理 |
| Market | `/market` | `/strategy/market` | ⏳ | 市场状态 |
| Backtest | `/backtest` | `/strategy/backtest` | ⏳ | 回测分析 |
| Signals | `/realtime` | `/strategy/signals` | ⏳ | 交易信号 |
| Performance | `/dashboard` | `/strategy/performance` | ⏳ | 策略绩效 |

## Monitoring Platform域 (MonitoringLayout)

| 页面 | 旧路由 | 新路由 | 状态 | 备注 |
|------|--------|--------|------|------|
| Dashboard | `/dashboard` | `/monitoring/dashboard` | ⏳ | 监控面板 |
| Data Quality | - | `/monitoring/data-quality` | ⏳ | 数据质量（新功能） |
| Performance | - | `/monitoring/performance` | ⏳ | 性能监控（新功能） |
| API Health | `/system/database-monitor` | `/monitoring/api` | ⏳ | API健康 |
| Logs | `/system/architecture` | `/monitoring/logs` | ⏳ | 系统日志 |

## 系统管理页

| 页面 | 旧路由 | 新路由 | 状态 | 备注 |
|------|--------|--------|------|------|
| Settings | `/settings` | `/settings/general` | ⏳ | 通用设置 |
| System | `/system/architecture` | `/settings/system` | ⏳ | 系统架构 |
| Database | `/system/database-monitor` | `/settings/database` | ⏳ | 数据库监控 |

## 迁移优先级

### P0 - 核心功能（必须验证）
- Dashboard
- Market List
- Stock Screener
- Risk Overview

### P1 - 重要功能（应该验证）
- Watchlist
- Portfolio
- Realtime Monitor
- Backtest

### P2 - 辅助功能（可以延后）
- Stress Test
- Signals
- Monitoring Dashboard

## 验证步骤

1. ✅ 路由配置正确
2. ⏳ 页面能正常加载
3. ⏳ 导航链接正常工作
4. ⏳ 面包屑正确显示
5. ⏳ 侧边栏菜单高亮正确
6. ⏳ Command Palette能搜索到页面

## 已知问题

1. **路由重定向**: 部分旧路由已配置重定向，需要验证是否正常工作
2. **页面组件**: 某些页面可能需要更新内部链接以使用新路由
3. **面包屑**: 需要验证BreadcrumbNav组件在所有页面正确显示
