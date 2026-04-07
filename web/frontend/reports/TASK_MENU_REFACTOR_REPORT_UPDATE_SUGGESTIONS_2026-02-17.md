# 前端路由与菜单一致性盘点报告 (2026-02-17)

> **历史总结说明**:
> 本文件是某次 Web 功能开发、修复、集成、测试、验收或阶段性交付的历史总结快照，用于追溯当时的实施结论。
> 其中的完成度、通过数、状态和结论不应直接视为当前事实；引用前应结合 `architecture/STANDARDS.md`、当前实现、基线文件与最新验证结果重新确认。


## 1. 现状概述
当前系统已完成 ArtDeco v3.1 菜单重构，但在路由定义与菜单配置（`MenuConfig.ts`）之间仍存在若干不一致点，部分页面虽已实现但未对用户开放入口。

## 2. 详细盘点表

| 功能域 | 路由路径 | 对应组件 | 菜单状态 | 建议操作 |
| :--- | :--- | :--- | :--- | :--- |
| **市场** | `/market/realtime` | `MarketRealtimeTab` | ✅ 已接入 | 保持现状 |
| | `/market/overview` | `ArtDecoMarketOverview` | ✅ 已接入 | 保持现状 |
| | `/market/technical`| `MarketKLineTab` | ✅ 已接入 | 菜单标签建议改为"K线分析" |
| | `/market/etf` | `MarketETFTab` | ❌ 未接入 | **补全菜单项** |
| | `/market/concept` | `MarketConceptTab` | ❌ 未接入 | **补全菜单项** |
| **技术** | `/technical/indicators` | `TechnicalScannerTab` | ❌ 缺失域 | **新增"技术分析"菜单域** |
| | `/technical/analysis` | `ArtDecoTechnicalAnalysis` | ❌ 缺失域 | 合并入"技术分析"域 |
| **策略** | `/strategy/management` | `ArtDecoStrategyManagement` | ✅ 已接入 | 保持现状 |
| | `/strategy/backtest` | `ArtDecoBacktestAnalysis` | ✅ 已接入 | 保持现状 |
| | `/strategy/risk` | `StrategyParametersTab` | ❌ 隐藏 | 建议加入"策略中心"子菜单 |
| **交易** | `/trading/signals` | `StrategySignalsTab` | ✅ 已接入 | 保持现状 |
| | `/trading/positions`| `PortfolioOverviewTab` | ✅ 已接入 | 路径建议统一为 `/stocks/portfolio` |
| **自选** | `/stocks/management` | `ArtDecoStockManagement` | ⚠️ 路径冲突 | 菜单指向 `/watchlist/manage`，建议路由统一 |
| **风险** | `/risk/overview` | `RiskOverviewTab` | ✅ 已接入 | 保持现状 |
| | `/risk/alerts` | `ArtDecoRiskAlerts` | ✅ 已接入 | 保持现状 |
| | `/risk/announcement`| `ArtDecoAnnouncementMonitor` | ✅ 已接入 | 保持现状 |
| | `/monitoring/watchlists`| `StopLossMonitorTab` | ❌ 隐藏 | 建议并入"风险控制"或"止损监控" |
| **系统** | `/system/monitoring` | `SystemHealthTab` | ✅ 已接入 | 保持现状 |
| | `/system/settings` | `ArtDecoSystemSettings` | ❌ 隐藏 | **补全菜单项** |

## 3. 核心更新建议 (待批准)

### 3.1 菜单补全 (High)
在 `MenuConfig.ts` 中补全以下缺失项，确保用户能访问已实现的页面：
- **市场总览**: 增加 "ETF行情"、"概念板块"。
- **技术分析**: 新增一级域，包含 "技术指标"、"综合分析"。
- **风险控制**: 增加 "止损监控"。
- **系统管理**: 增加 "系统配置"。

### 3.2 路由规范化 (Medium)
- **自选股域**: 统一使用 `/stocks/` 或 `/watchlist/`。目前路由为 `/stocks` 而菜单引用 `/watchlist`，建议将路由重命名为 `/watchlist` 以匹配业务直觉。
- **交易/持仓**: 建议将 `/trading/positions` 统一为 `/stocks/portfolio` 或反之，减少 alias 维护成本。

### 3.3 UI 优化 (Low) - 已执行
- 移除了侧边栏冗余的 Header 标题显示，解决了菜单名双重显示的视觉 Bug。

## 4. 后续执行计划
1.  **Phase 1**: 修改 `MenuConfig.ts` 补全缺失项（待批准）。
2.  **Phase 2**: 执行路由重命名与规范化（涉及文件较多，需谨慎）。
3.  **Phase 3**: 验证所有页面跳转无 404。

---
**盘点人**: Gemini CLI Agent
**日期**: 2026-02-17
