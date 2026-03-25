# MyStocks 功能树 (Function Tree)

> **版本**: 1.0.0 | **更新日期**: 2026-03-12 | **维护者**: 开发团队
> **文档类型**: 功能管理 | **状态**: 活跃维护

---

## 快速导航

| 领域 | 状态 | 完成度 |
|------|------|--------|
| [01-市场数据与行情](#domain-01) | ✅ 完成 | 95% |
| [02-技术分析与指标](#domain-02) | ✅ 完成 | 90% |
| [03-策略管理与回测](#domain-03) | ✅ 完成 | 85% |
| [04-风险管理与监控](#domain-04) | ✅ 完成 | 80% |
| [05-投资组合与交易](#domain-05) | 🚧 开发中 | 70% |
| [06-监控与告警](#domain-06) | ✅ 完成 | 75% |
| [07-高级分析与AI](#domain-07) | 🧪 实验性 | 50% |
| [08-系统管理与配置](#domain-08) | ✅ 完成 | 85% |
| [09-数据存储与管理](#domain-09) | ✅ 完成 | 90% |
| [10-公告与信息](#domain-10) | ✅ 完成 | 80% |

> 使用方式：先读 [AI Quick Start](./guides/ai-tools/AI_QUICK_START.md) 或 [Docs 首页](./INDEX.md) 按任务类型定位入口，再进入本页对应功能域，最后下钻该领域的“领域入口”表。

---

## 功能状态图例

| 图标 | 状态 | 说明 |
|------|------|------|
| ✅ | 完成 | 功能已实现，测试通过，生产可用 |
| 🚧 | 开发中 | 正在开发，尚未完成 |
| 📝 | 计划中 | 已规划，尚未开始开发 |
| ⚠️ | 需修复 | 存在已知问题，需要修复 |
| 🔒 | 已废弃 | 功能已废弃，计划移除 |
| 🧪 | 实验性 | 实验功能，API 可能变化 |

---

> 稳定 ID 规则：所有 `mirror_to_function_tree: true` 的业务域和节点都带 `{#domain-xx}` / `{#domain-xx-node-yy}` 锚点；`task card.function_tree` 必须引用这些稳定 ID，而不是自由文本标签。

## 01-市场数据与行情 {#domain-01}

**模块路径**: `src/adapters/`, `web/frontend/src/views/market/`
**API前缀**: `/api/market/*`, `/api/tdx/*`, `/api/akshare_market/*`
**完成度**: 95%

### 领域入口

| 入口类型 | 链接/路径 | 用途 |
|---------|----------|------|
| 规范入口 | [架构红线与审批门禁](../architecture/STANDARDS.md)<br>[Docs 首页](./INDEX.md) | 市场数据任务路由和治理入口 |
| API/契约入口 | [市场 API](../web/backend/app/api/market.py)<br>[AKShare Market API](../web/backend/app/api/akshare_market/)<br>[API 文档总览](./api/README.md) | 市场 API 与契约接口入口 |
| 前端/交互入口 | [传统行情页](../web/frontend/src/views/market/)<br>[ArtDeco 市场页](../web/frontend/src/views/artdeco-pages/market-data-tabs/) | 页面、Tab 和交互入口 |
| 核心代码入口 | [数据适配器](../src/adapters/)<br>[市场数据应用层](../src/application/market_data/) | 行情接入和处理实现入口 |
| 测试与验证入口 | [市场 API 测试](../tests/api/file_tests/test_market_api.py)<br>[E2E 市场数据](../tests/e2e/market-data.spec.ts)<br>[前端 E2E 行情](../web/frontend/tests/e2e/market-data.spec.ts) | API、自测和页面验证入口 |
| 运行与排障入口 | [测试指南](./testing/E2E_TEST_GUIDE.md)<br>[运维手册](./operations/OPS_MANUAL.md) | 运行链路和排障入口 |

### 1.1 实时行情监控 {#domain-01-node-01}

| 功能点 | 状态 | 代码位置 | 说明 |
|--------|------|----------|------|
| TDX实时行情 | ✅ | `src/adapters/tdx/realtime_service.py` | 通达信实时行情接入 |
| 股票报价推送 | ✅ | `web/backend/app/api/market.py` | WebSocket实时推送 |
| 自选股行情 | ✅ | `web/frontend/src/views/Market.vue` | 自选股实时监控 |
| 板块行情 | ✅ | `src/adapters/akshare/market_adapter/board_sector.py` | 板块涨跌统计 |

### 1.2 资金流向分析 {#domain-01-node-02}

| 功能点 | 状态 | 代码位置 | 说明 |
|--------|------|----------|------|
| 主力资金 | ✅ | `src/adapters/akshare/market_adapter/` | 主力资金监控 |
| 板块资金 | ✅ | `web/frontend/src/views/artdeco-pages/market-data-tabs/FundFlow.vue` | 板块资金流向 |
| 个股资金 | ✅ | `src/adapters/efinance_adapter/` | 个股资金明细 |

### 1.3 多数据源集成 {#domain-01-node-03}

| 数据源 | 状态 | 优先级 | 说明 |
|--------|------|--------|------|
| TDX (通达信) | ✅ | 1 | 主数据源 |
| AKShare | ✅ | 2 | 综合数据源 |
| EFinance | ✅ | 3 | 东方财富 |
| BaoStock | ✅ | 4 | 历史数据 |
| SinaFinance | ✅ | 5 | 股票评级 |
| Tushare | ⚠️ | 6 | 需Token配置 |
| Byapi | ⚠️ | 7 | 403问题待修 |

### 1.4 K线数据服务 {#domain-01-node-04}

| 功能点 | 状态 | 代码位置 | 说明 |
|--------|------|----------|------|
| 日线数据 | ✅ | `src/adapters/tdx/kline_data_service.py` | 日K线获取 |
| 分钟线数据 | ✅ | `src/adapters/akshare/misc_data/` | 1/5/15/30/60分钟 |
| 复权处理 | ✅ | `src/core/` | 前后复权计算 |

---

## 02-技术分析与指标 {#domain-02}

**模块路径**: `src/indicators/`, `web/frontend/src/views/technical/`
**API前缀**: `/api/indicators/*`, `/api/technical/*`
**完成度**: 90%

### 领域入口

| 入口类型 | 链接/路径 | 用途 |
|---------|----------|------|
| 规范入口 | [架构红线与审批门禁](../architecture/STANDARDS.md)<br>[Docs 首页](./INDEX.md) | 技术分析任务路由和治理入口 |
| API/契约入口 | [指标 API](../web/backend/app/api/indicators.py)<br>[技术分析 API](../web/backend/app/api/technical/)<br>[API 文档总览](./api/README.md) | 技术分析接口入口 |
| 前端/交互入口 | [技术分析页](../web/frontend/src/views/technical/TechnicalAnalysis.vue)<br>[技术扫描 Tab](../web/frontend/src/views/artdeco-pages/technical-tabs/TechnicalScannerTab.vue) | 技术分析页面和扫描交互入口 |
| 核心代码入口 | [指标库](../src/indicators/)<br>[技术分析引擎](../src/advanced_analysis/technical_analyzer/) | 指标与分析核心实现入口 |
| 测试与验证入口 | [技术 API 测试](../tests/api/technical.spec.ts)<br>[技术分析 E2E](../tests/e2e/technical-analysis.spec.ts)<br>[K 线图 E2E](../web/frontend/tests/e2e/kline-chart.spec.ts) | 技术指标和图表验证入口 |
| 运行与排障入口 | [测试文档总览](./testing/README.md)<br>[运维手册](./operations/OPS_MANUAL.md) | 调试和运行排障入口 |

### 2.1 技术指标库 {#domain-02-node-01}

| 指标类型 | 状态 | 指标列表 |
|----------|------|----------|
| 趋势指标 | ✅ | MA, EMA, MACD, BOLL, SAR |
| 动量指标 | ✅ | RSI, KDJ, CCI, WR, DMI |
| 成交量指标 | ✅ | VOL, OBV, VR, VOL_MA |
| 波动率指标 | ✅ | ATR, STD, BOLL_WIDTH |
| 能量指标 | ✅ | CR, BR, AR |

### 2.2 K线图表分析 {#domain-02-node-02}

| 功能点 | 状态 | 代码位置 | 说明 |
|--------|------|----------|------|
| K线渲染 | ✅ | `web/frontend/src/components/technical/KLineChart.vue` | KLineCharts集成 |
| 指标叠加 | ✅ | `web/frontend/src/composables/useKLineData.ts` | 多指标叠加显示 |
| 十字光标 | ✅ | `web/frontend/src/utils/crosshair.ts` | 交互式十字线 |
| 画线工具 | 🚧 | - | 计划中 |

### 2.3 技术形态识别 {#domain-02-node-03}

| 形态类型 | 状态 | 说明 |
|----------|------|------|
| K线形态 | ✅ | 吞没、锤子线、十字星等 |
| 图表形态 | 🚧 | 头肩顶底、双顶双底 |
| 缺口识别 | 📝 | 计划中 |

---

## 03-策略管理与回测 {#domain-03}

**模块路径**: `src/backtesting/`, `src/ml_strategy/`, `web/frontend/src/views/strategy/`
**API前缀**: `/api/strategy_management/*`, `/api/backtest/*`
**完成度**: 85%

### 领域入口

| 入口类型 | 链接/路径 | 用途 |
|---------|----------|------|
| 规范入口 | [架构红线与审批门禁](../architecture/STANDARDS.md)<br>[OpenSpec 工作流](../openspec/AGENTS.md) | 策略能力和行为变更前的治理入口 |
| API/契约入口 | [策略管理 API](../web/backend/app/api/strategy_management/)<br>[策略 CRUD API](../web/backend/app/api/strategy_mgmt.py)<br>[回测 WebSocket API](../web/backend/app/api/backtest_ws.py) | 策略与回测接口入口 |
| 前端/交互入口 | [策略页面](../web/frontend/src/views/strategy/)<br>[ArtDeco 策略页](../web/frontend/src/views/artdeco-pages/strategy-tabs/) | 策略配置、回测和优化交互入口 |
| 核心代码入口 | [回测引擎](../src/backtesting/)<br>[机器学习策略](../src/ml_strategy/)<br>[策略应用层](../src/application/strategy/) | 策略与回测核心实现入口 |
| 测试与验证入口 | [策略 API 测试](../tests/api/strategy.spec.ts)<br>[策略管理 E2E](../tests/e2e/strategy-management.spec.ts)<br>[前端回测 E2E](../web/frontend/tests/e2e/strategy-backtest.spec.ts) | 策略管理和回测验证入口 |
| 运行与排障入口 | [测试文档总览](./testing/README.md)<br>[GPU 测试快速开始](../src/gpu/api_system/TESTING_QUICK_START.md)<br>[运维手册](./operations/OPS_MANUAL.md) | 回测、GPU 与运行排障入口 |

### 3.1 策略配置管理 {#domain-03-node-01}

| 功能点 | 状态 | 代码位置 | 说明 |
|--------|------|----------|------|
| 策略CRUD | ✅ | `web/backend/app/api/strategy_mgmt.py` | 策略增删改查 |
| 策略参数 | ✅ | `web/frontend/src/views/artdeco-pages/strategy-tabs/` | 参数配置界面 |
| 策略模板 | ✅ | `src/ml_strategy/strategy/templates/` | 预置策略模板 |

### 3.2 回测引擎 {#domain-03-node-02}

| 功能点 | 状态 | 代码位置 | 说明 |
|--------|------|----------|------|
| 历史回测 | ✅ | `src/ml_strategy/backtest/backtest_engine.py` | 向量回测引擎 |
| GPU加速 | ✅ | `src/gpu/acceleration/` | GPU并行计算 |
| 事件驱动 | ✅ | `web/backend/app/backtest/` | 事件驱动回测 |

### 3.3 回测分析 {#domain-03-node-03}

| 功能点 | 状态 | 说明 |
|--------|------|------|
| 收益分析 | ✅ | 累计收益、年化收益、超额收益 |
| 风险分析 | ✅ | 最大回撤、夏普比率、波动率 |
| 交易分析 | ✅ | 胜率、盈亏比、持仓周期 |
| 归因分析 | 🚧 | Brinson归因、因子归因 |

---

## 04-风险管理与监控 {#domain-04}

**模块路径**: `src/governance/risk_management/`, `web/frontend/src/views/risk/`
**API前缀**: `/api/risk/*`, `/api/risk/v31`
**完成度**: 80%

### 领域入口

| 入口类型 | 链接/路径 | 用途 |
|---------|----------|------|
| 规范入口 | [架构红线与审批门禁](../architecture/STANDARDS.md)<br>[Docs 首页](./INDEX.md) | 风控规则、任务路由和治理入口 |
| API/契约入口 | [风险 API](../web/backend/app/api/risk/)<br>[风险管理 API](../web/backend/app/api/risk_management.py)<br>[API 文档总览](./api/README.md) | 风险指标、止损和预警接口入口 |
| 前端/交互入口 | [风险页面](../web/frontend/src/views/risk/)<br>[ArtDeco 风险页](../web/frontend/src/views/artdeco-pages/risk-tabs/) | 风险总览、持仓风险和告警交互入口 |
| 核心代码入口 | [风险管理核心模块](../src/governance/risk_management/) | 风险计算、止损与告警实现入口 |
| 测试与验证入口 | [风险管理核心测试](../tests/backend/test_risk_management_core.py)<br>[风险回归测试](../tests/backend/test_risk_management_regression.py)<br>[风险 E2E](../tests/e2e/risk-monitor.spec.ts) | 风控功能验证入口 |
| 运行与排障入口 | [测试文档总览](./testing/README.md)<br>[运维手册](./operations/OPS_MANUAL.md) | 风险链路验证和排障入口 |

### 4.1 风险指标计算 {#domain-04-node-01}

| 指标 | 状态 | 说明 |
|------|------|------|
| VaR | ✅ | 风险价值 |
| CVaR | ✅ | 条件风险价值 |
| 最大回撤 | ✅ | 历史最大回撤 |
| Beta | ✅ | 贝塔系数 |
| 波动率 | ✅ | 年化波动率 |

### 4.2 止损止盈管理 {#domain-04-node-02}

| 功能点 | 状态 | 代码位置 | 说明 |
|--------|------|----------|------|
| 止损引擎 | ✅ | `src/governance/risk_management/services/stop_loss_engine/` | 自动止损 |
| 止盈规则 | ✅ | `src/governance/risk_management/` | 动态止盈 |
| 风控告警 | ✅ | `web/backend/app/api/risk/` | 风险预警 |

### 4.3 风险仪表板 {#domain-04-node-03}

| 功能点 | 状态 | 说明 |
|--------|------|------|
| 风险概览 | ✅ | 整体风险视图 |
| 持仓风险 | ✅ | 单只股票风险 |
| 历史风险 | ✅ | 风险趋势图 |

---

## 05-投资组合与交易 {#domain-05}

**模块路径**: `src/portfolio/`, `src/trading/`, `web/frontend/src/views/trade-management/`
**API前缀**: `/api/trade/*`, `/api/portfolio/*`
**完成度**: 70%

### 领域入口

| 入口类型 | 链接/路径 | 用途 |
|---------|----------|------|
| 规范入口 | [架构红线与审批门禁](../architecture/STANDARDS.md)<br>[功能管理工作流](./guides/governance/FEATURE_MANAGEMENT_WORKFLOW.md) | 交易链路和跨域治理入口 |
| API/契约入口 | [交易运行时 API](../web/backend/app/api/trading_runtime.py)<br>[交易监控 API](../web/backend/app/api/trading_monitor.py)<br>[交易数据 API](../web/backend/app/api/data/trading_api.py) | 交易、持仓和组合接口入口 |
| 前端/交互入口 | [交易页面](../web/frontend/src/views/trading/)<br>[ArtDeco 交易页](../web/frontend/src/views/artdeco-pages/trading-tabs/)<br>[交易决策页](../web/frontend/src/views/trading-decision/) | 持仓、历史、决策和交易交互入口 |
| 核心代码入口 | [组合应用层](../src/application/portfolio/)<br>[交易应用层](../src/application/trading/)<br>[交易领域模型](../src/domain/trading/) | 交易和持仓实现入口 |
| 测试与验证入口 | [交易路由 API 测试](../tests/api/file_tests/test_trade_routes_api.py)<br>[交易 E2E](../tests/e2e/trade-management.spec.ts)<br>[组合 DDD 测试](../tests/ddd/test_phase_5_portfolio.py) | 交易和组合验证入口 |
| 运行与排障入口 | [测试文档总览](./testing/README.md)<br>[运维手册](./operations/OPS_MANUAL.md) | 交易链路排障入口 |

### 5.1 持仓管理 {#domain-05-node-01}

| 功能点 | 状态 | 说明 |
|--------|------|------|
| 持仓查询 | ✅ | 实时持仓展示 |
| 盈亏计算 | ✅ | 浮动盈亏统计 |
| 持仓分析 | ✅ | 行业分布、集中度 |

### 5.2 交易记录 {#domain-05-node-02}

| 功能点 | 状态 | 说明 |
|--------|------|------|
| 交易流水 | ✅ | 历史交易记录 |
| 成交查询 | ✅ | 成交明细 |
| 对账单 | 🚧 | 计划中 |

### 5.3 交易决策 {#domain-05-node-03}

| 功能点 | 状态 | 说明 |
|--------|------|------|
| 决策中心 | ✅ | 交易决策面板 |
| 信号生成 | ✅ | 买卖信号 |
| 执行跟踪 | 🚧 | 订单执行状态 |

---

## 06-监控与告警 {#domain-06}

**模块路径**: `src/monitoring/`, `web/frontend/src/views/monitoring/`
**API前缀**: `/api/monitoring/*`, `/api/signal_monitoring/*`
**完成度**: 75%

### 领域入口

| 入口类型 | 链接/路径 | 用途 |
|---------|----------|------|
| 规范入口 | [架构红线与审批门禁](../architecture/STANDARDS.md)<br>[运维文档总览](./operations/README.md) | 监控、告警和可观测性治理入口 |
| API/契约入口 | [监控 API](../web/backend/app/api/monitoring.py)<br>[信号监控 API](../web/backend/app/api/signal_monitoring/)<br>[API 文档总览](./api/README.md) | 监控和告警接口入口 |
| 前端/交互入口 | [监控页面](../web/frontend/src/views/monitoring/)<br>[监控总览页](../web/frontend/src/views/monitor.vue) | 仪表板、告警和监控交互入口 |
| 核心代码入口 | [监控模块](../src/monitoring/)<br>[监控核心](../src/core/monitoring.py) | 告警、数据质量和监控实现入口 |
| 测试与验证入口 | [监控测试目录](../tests/monitoring/)<br>[监控仪表板 E2E](../tests/e2e/monitoring-dashboard.spec.ts)<br>[监控单元测试](../tests/unit/monitoring/test_monitoring_service.py) | 监控与告警验证入口 |
| 运行与排障入口 | [监控栈 README](../config/monitoring-stack/README.md)<br>[Grafana 设置](./operations/deployment/SETUP_GRAFANA.md)<br>[运维手册](./operations/OPS_MANUAL.md) | 监控部署和排障入口 |

### 6.1 系统监控 {#domain-06-node-01}

| 功能点 | 状态 | 说明 |
|--------|------|------|
| 性能监控 | ✅ | 系统性能指标 |
| 服务状态 | ✅ | 服务健康检查 |
| 资源使用 | ✅ | CPU/内存/磁盘 |

### 6.2 数据质量 {#domain-06-node-02}

| 功能点 | 状态 | 说明 |
|--------|------|------|
| 数据完整性 | ✅ | 数据缺失检测 |
| 数据一致性 | ✅ | 多源数据校验 |
| 异常检测 | ✅ | 异常数据告警 |

### 6.3 告警管理 {#domain-06-node-03}

| 功能点 | 状态 | 说明 |
|--------|------|------|
| 告警规则 | ✅ | 可配置告警规则 |
| 告警通知 | ✅ | 多渠道通知 |
| 告警历史 | ✅ | 告警记录查询 |

---

## 07-高级分析与AI {#domain-07}

**模块路径**: `src/advanced_analysis/`, `src/ml_strategy/`
**API前缀**: `/api/advanced_analysis/*`, `/api/algorithms/*`
**完成度**: 50%

### 领域入口

| 入口类型 | 链接/路径 | 用途 |
|---------|----------|------|
| 规范入口 | [架构红线与审批门禁](../architecture/STANDARDS.md)<br>[OpenSpec 工作流](../openspec/AGENTS.md) | AI、实验功能和架构治理入口 |
| API/契约入口 | [高级分析 API](../web/backend/app/api/advanced_analysis.py)<br>[算法 API](../web/backend/app/api/algorithms.py)<br>[机器学习 API](../web/backend/app/api/ml.py) | AI、分析和推理接口入口 |
| 前端/交互入口 | [GPU 回测页](../web/frontend/src/views/strategy/BacktestGPU.vue)<br>[策略优化页](../web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue)<br>[策略管理页](../web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue) | AI 和高级分析交互入口 |
| 核心代码入口 | [高级分析模块](../src/advanced_analysis/)<br>[机器学习策略模块](../src/ml_strategy/)<br>[GPU API 服务](../src/gpu/api_system/services/) | 分析、训练和 GPU 加速实现入口 |
| 测试与验证入口 | [机器学习 API 测试](../tests/api/test_ml_file.py)<br>[高级回测测试](../tests/unit/test_advanced_backtest_engine.py)<br>[GPU 测试 README](../src/gpu/api_system/tests/README.md) | AI 和分析功能验证入口 |
| 运行与排障入口 | [自动化说明](../src/ml_strategy/automation/README.md)<br>[GPU API README](../src/gpu/api_system/README.md)<br>[WSL2 GPU 设置](../src/gpu/api_system/WSL2_GPU_SETUP.md) | 训练、调度和 GPU 排障入口 |

### 7.1 机器学习策略 {#domain-07-node-01}

| 功能点 | 状态 | 说明 |
|--------|------|------|
| 特征工程 | ✅ | 技术特征提取 |
| 模型训练 | 🚧 | 模型训练框架 |
| 预测推理 | 🚧 | 实时预测 |

### 7.2 批量分析 {#domain-07-node-02}

| 功能点 | 状态 | 说明 |
|--------|------|------|
| 批量回测 | ✅ | 多策略批量回测 |
| 批量选股 | ✅ | 条件选股 |
| 批量监控 | ✅ | 多股票监控 |

### 7.3 情感分析 {#domain-07-node-03}

| 功能点 | 状态 | 说明 |
|--------|------|------|
| 新闻情感 | 🚧 | 新闻情感分析 |
| 舆情监控 | 📝 | 计划中 |

---

## 08-系统管理与配置 {#domain-08}

**模块路径**: `web/backend/app/api/auth.py`, `web/backend/app/api/system.py`
**API前缀**: `/api/auth/*`, `/api/system/*`, `/api/backup_recovery/*`
**完成度**: 85%

### 领域入口

| 入口类型 | 链接/路径 | 用途 |
|---------|----------|------|
| 规范入口 | [架构红线与审批门禁](../architecture/STANDARDS.md)<br>[运维文档总览](./operations/README.md) | 认证、系统配置和恢复治理入口 |
| API/契约入口 | [认证 API](../web/backend/app/api/auth.py)<br>[系统 API](../web/backend/app/api/system.py)<br>[备份恢复 API](../web/backend/app/api/backup_recovery.py) | 系统与认证接口入口 |
| 前端/交互入口 | [系统页面](../web/frontend/src/views/system/)<br>[ArtDeco 系统页](../web/frontend/src/views/artdeco-pages/system-tabs/) | 系统设置和系统监控交互入口 |
| 核心代码入口 | [备份恢复模块](../src/infrastructure/backup_recovery/)<br>[Docker 部署说明](../docker/README.md) | 备份恢复和环境配置实现入口 |
| 测试与验证入口 | [认证 API 测试](../tests/api/auth.spec.ts)<br>[系统 API 测试](../tests/api/system.spec.ts)<br>[JWT 安全测试](../tests/security/test_jwt_authentication.py) | 系统管理验证入口 |
| 运行与排障入口 | [部署文档总览](./operations/deployment/README.md)<br>[部署指南](./operations/deployment-guide.md)<br>[Docker README](../docker/README.md) | 系统运行、部署和排障入口 |

### 8.1 认证授权 {#domain-08-node-01}

| 功能点 | 状态 | 说明 |
|--------|------|------|
| 用户登录 | ✅ | JWT认证 |
| 权限管理 | ✅ | 角色权限 |
| 会话管理 | ✅ | Token刷新 |

### 8.2 系统配置 {#domain-08-node-02}

| 功能点 | 状态 | 说明 |
|--------|------|------|
| 数据源配置 | ✅ | 数据源管理 |
| 缓存配置 | ✅ | Redis配置 |
| 日志配置 | ✅ | 日志级别调整 |

### 8.3 备份恢复 {#domain-08-node-03}

| 功能点 | 状态 | 说明 |
|--------|------|------|
| 数据备份 | ✅ | 自动备份 |
| 数据恢复 | ✅ | 数据恢复 |
| 备份调度 | ✅ | 定时备份 |

---

## 09-数据存储与管理 {#domain-09}

**模块路径**: `src/storage/database/`, `src/data_access/`, `src/core/`
**API前缀**: `/api/data/*`, `/api/database/*`, `/api/storage/*`
**完成度**: 90%

### 领域入口

| 入口类型 | 链接/路径 | 用途 |
|---------|----------|------|
| 规范入口 | [架构红线与审批门禁](../architecture/STANDARDS.md)<br>[架构文档总览](./architecture/README.md) | 数据架构、分层和存储治理入口 |
| API/契约入口 | [API 文档总览](./api/README.md)<br>[统一管理器契约](../tests/001-readme-md-md/contracts/unified_manager_api.md)<br>[数据 API](../web/backend/app/api/data/market.py) | 数据 API 与契约接口入口 |
| 前端/交互入口 | [数据库监控页](../web/frontend/src/views/system/DatabaseMonitor.vue)<br>[数据管理页](../web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoDataManagement.vue) | 数据管理和监控交互入口 |
| 核心代码入口 | [数据库存储模块](../src/storage/database/)<br>[数据访问层](../src/data_access/)<br>[统一管理器](../src/core/unified_manager.py) | 数据路由和存储实现入口 |
| 测试与验证入口 | [数据 API 测试](../tests/api/test_data_file.py)<br>[API 集成测试](../tests/integration/test_api_integration.py)<br>[市场数据单元测试](../tests/unit/test_market_data.py) | 数据访问和存储验证入口 |
| 运行与排障入口 | [基础设施 Docker 说明](../docker/README.md)<br>[运维文档总览](./operations/README.md)<br>[架构文档总览](./architecture/README.md) | 数据存储运行与排障入口 |

### 9.1 数据库架构 {#domain-09-node-01}

| 组件 | 状态 | 说明 |
|------|------|------|
| PostgreSQL | ✅ | 关系型数据存储 |
| TDengine | ✅ | 时序数据存储 |
| Redis | ⚠️ | 缓存层(需启动服务) |
| MongoDB | ⚠️ | 监控存储(需启动服务) |

### 9.2 数据访问层 {#domain-09-node-02}

| 功能点 | 状态 | 代码位置 | 说明 |
|--------|------|----------|------|
| 统一管理器 | ✅ | `src/core/unified_manager.py` | 统一数据访问 |
| 分类路由 | ✅ | `src/core/data_classification.py` | 智能路由 |
| 表管理器 | ✅ | `src/storage/database/database_manager/` | 表结构管理 |

### 9.3 缓存管理 {#domain-09-node-03}

| 功能点 | 状态 | 说明 |
|--------|------|------|
| 查询缓存 | ✅ | 热点数据缓存 |
| 缓存失效 | ✅ | 自动失效策略 |
| 缓存统计 | ✅ | 命中率统计 |

---

## 10-公告与信息 {#domain-10}

**模块路径**: `web/backend/app/api/announcement.py`, `web/frontend/src/views/announcement/`
**API前缀**: `/api/announcement/*`
**完成度**: 80%

### 领域入口

| 入口类型 | 链接/路径 | 用途 |
|---------|----------|------|
| 规范入口 | [架构红线与审批门禁](../architecture/STANDARDS.md)<br>[Docs 首页](./INDEX.md) | 公告功能和信息路由治理入口 |
| API/契约入口 | [公告 API](../web/backend/app/api/announcement.py)<br>[公告路由](../web/backend/app/api/announcement/routes.py)<br>[API 文档总览](./api/README.md) | 公告和后端路由接口入口 |
| 前端/交互入口 | [公告监控页](../web/frontend/src/views/announcement/AnnouncementMonitor.vue)<br>[ArtDeco 公告组件](../web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoAnnouncementMonitor.vue) | 公告监控与交互入口 |
| 核心代码入口 | [公告服务](../web/backend/app/services/announcement_service.py)<br>[公告模型](../web/backend/app/models/announcement.py) | 公告处理实现入口 |
| 测试与验证入口 | [公告 API 测试](../tests/api/file_tests/test_announcement_api.py)<br>[后端公告 API 自测](../web/backend/app/api/test_announcement_api.py) | 公告功能验证入口 |
| 运行与排障入口 | [测试文档总览](./testing/README.md)<br>[运维手册](./operations/OPS_MANUAL.md) | 公告链路验证和排障入口 |

### 10.1 公告管理 {#domain-10-node-01}

| 功能点 | 状态 | 说明 |
|--------|------|------|
| 公告抓取 | ✅ | 自动抓取公告 |
| 公告分类 | ✅ | 按类型分类 |
| 公告搜索 | ✅ | 关键词搜索 |

### 10.2 公告监控 {#domain-10-node-02}

| 功能点 | 状态 | 说明 |
|--------|------|------|
| 实时监控 | ✅ | 新公告提醒 |
| 重大事件 | ✅ | 重大事件标记 |
| 订阅管理 | ✅ | 股票订阅 |

---

## 功能统计

| 统计项 | 数量 |
|--------|------|
| 功能领域 | 10 |
| 子功能模块 | 30+ |
| 已完成功能 | 85+ |
| 开发中功能 | 15+ |
| 计划中功能 | 10+ |
| API端点 | 60+ |
| 前端页面 | 50+ |

---

## 维护说明

### 更新规则

1. **新增功能**: 在对应领域下添加功能条目，标注状态为 `📝`
2. **开始开发**: 将状态从 `📝` 改为 `🚧`
3. **完成开发**: 将状态从 `🚧` 改为 `✅`，更新完成度
4. **发现问题**: 将状态改为 `⚠️`，在 CHANGELOG.md 中记录
5. **废弃功能**: 将状态改为 `🔒`，说明废弃原因
6. **入口变化**: 只要规范、API、前端、核心代码、测试或运行入口变化，就必须同步更新对应领域的“领域入口”表
7. **跨领域功能**: 主领域维护完整入口，其他领域只保留引用说明，避免双份维护

### 关联文档

- 更新日志: [CHANGELOG.md](../CHANGELOG.md)
- AI Quick Start: [guides/ai-tools/AI_QUICK_START.md](./guides/ai-tools/AI_QUICK_START.md)
- Docs 首页: [INDEX.md](./INDEX.md)
- 架构设计: [architecture/](./architecture/)
- API文档: [api/](./api/)
- 开发指南: [guides/](./guides/)

---

*最后更新: 2026-03-12*
