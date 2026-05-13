# MyStocks 功能树 (Function Tree)

> **参考指南说明**:
> 本文件是项目功能版图、功能域导航、任务映射与边界对齐参考，用于帮助判断“当前在做什么、应该落在哪个功能域、是否超出既定边界”。
> 若涉及仓库级共享规则、审批门禁、治理口径或功能树事实源，请优先遵循 `architecture/STANDARDS.md`，并结合当前代码、菜单、路由、契约与验证结果使用；若涉及执行流程或协作约束，再补充参考根目录 `AGENTS.md`。
>
> 文内完成度、状态标签、功能归属和稳定 ID 如未重新复核，应视为阶段性快照；但凡本次改动已经改变功能边界、入口或状态，必须在同一变更批次同步更新本文件，不得让 `FUNCTION_TREE.md` 长期滞后于当前实现。


> **版本**: 1.1.6 | **更新日期**: 2026-05-10 | **维护者**: 开发团队
> **文档类型**: 功能管理 / 功能边界总览 | **状态**: 活跃维护

---

## 维护规则

1. 任何新增功能，必须在对应领域新增或补齐功能节点，并同步说明其主入口、依赖入口和验证入口。
2. 任何功能删除、废弃、合并、拆分、迁移或职责边界变化，必须在同一提交批次更新本文件，不能只改代码不改功能树。
3. 任何影响规范入口、API/契约入口、前端/交互入口、核心代码入口、测试与验证入口、运行与排障入口的改动，必须同步更新对应“领域入口”表。
4. 功能状态从 `📝/🚧/✅/⚠️/🔒/🧪` 发生变化时，必须同步更新状态与必要说明；完成度如未复核可保守处理，但不得保留明显过期的功能状态。
5. OpenSpec、任务卡、PR、评审或验收如引用功能域，必须优先引用本文件稳定 ID（如 `{#domain-xx}`、`{#domain-xx-node-yy}`），避免自由文本漂移。
6. 任何新增主路由目录 / 主页面、主 API 包路由或 canonical 后端入口时，必须在对应领域同步更新主入口与边界说明。
7. 任何兼容层、旧页面、旧 API 根入口、shim、re-export 或平行实现退役时，必须在同一提交中同步更新本文件，明确“已退役”“兼容保留”或“继任入口”。

## 使用方式

- 立项、评审或需求澄清时：先定位功能落在哪个领域和节点，确认是否属于既有能力扩展还是越界新增。
- 开发前：先检查目标领域的“领域入口”表，明确规范、代码、页面、测试和运行链路。
- 开发后：若实现改变了能力边界、入口路径、状态或新增了用户可感知能力，必须回写本文件。
- 文档核对时：把本文件视为“开发方向与边界总览”，再用代码、路由、契约和验证结果确认细节真相。

## 通用入口

- 共享治理入口默认参考 [架构红线与审批门禁](../architecture/STANDARDS.md)。
- 全局文档导航默认参考 [Docs 首页](./INDEX.md)。
- API 总览默认参考 [API 文档总览](./api/README.md)。
- 测试总览默认参考 [测试文档总览](./testing/README.md)。
- 运行与排障默认参考 [运维手册](./operations/OPS_MANUAL.md)。

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

## 功能状态图例

| 图标 | 状态 | 说明 |
|------|------|------|
| ✅ | 完成 | 已具备实现证据，且在需要时已具备验证/运行时证据；安全敏感节点还必须具备对应治理或安全证据，不能默认等同“生产可用” |
| 🚧 | 开发中 | 已有部分实现或入口，但验证、运行时真相源或治理证据未闭合 |
| 📝 | 计划中 | 已规划，尚未开始开发 |
| ⚠️ | 需修复 | 存在已知问题，需要修复 |
| 🔒 | 已废弃 | 功能已废弃，计划移除 |
| 🧪 | 实验性 | 已有实现或链路雏形，但运行时、稳定性或治理证据故意保持未闭合 |

### Q2 Evidence Interpretation

- 功能状态应优先结合四类证据理解：
  - implementation evidence
  - verification evidence
  - runtime evidence
  - safety/governance evidence
- 对交易、持仓变更、预执行风控、生产级实时主链路等安全敏感节点，`✅` 不能仅由 UI、接口或模型存在来支撑。
- 完成度百分比如未声明计算口径，应视为阶段性管理快照，不是硬门禁指标或生产 readiness 证明。

---

> 稳定 ID 规则：所有 `mirror_to_function_tree: true` 的业务域和节点都带 `{#domain-xx}` / `{#domain-xx-node-yy}` 锚点；`task card.function_tree` 必须引用这些稳定 ID，而不是自由文本标签。

## 01-市场数据与行情 {#domain-01}

**模块路径**: `src/adapters/`, `web/backend/app/api/market/`, `web/backend/app/api/akshare_market/`, `web/frontend/src/views/market/`, `web/frontend/src/views/data/`
**API前缀**: `/api/v1/market/*`, `/api/v2/market/*`, `/api/v1/tdx/*`, `/api/akshare/market/*`
**完成度**: 95%

### 领域入口

| 入口类型 | 链接/路径 | 用途 |
|---------|----------|------|
| 规范入口 | [架构红线与审批门禁](../architecture/STANDARDS.md) | 市场数据治理入口 |
| API/契约入口 | [市场包路由](../web/backend/app/api/market/__init__.py)<br>[市场请求路由](../web/backend/app/api/market/market_data_request.py)<br>[市场 V2 API](../web/backend/app/api/market_v2.py)<br>[AKShare Market API](../web/backend/app/api/akshare_market/)<br>[市场兼容入口](../web/backend/app/api/market.py) | 主路由以拆分包和 V2 接口为主；根级 `market.py` 更偏兼容入口；市场数据接口入口 |
| 前端/交互入口 | [市场主路由目录](../web/frontend/src/views/market/)<br>[资金流向页](../web/frontend/src/views/data/FundFlow.vue)<br>[ArtDeco 市场页](../web/frontend/src/views/artdeco-pages/market-data-tabs/) | 市场主路由入口；`FundFlow.vue` 承担资金流入口，ArtDeco tabs 更偏嵌入式展示层；市场数据交互入口 |
| 核心代码入口 | [数据适配器](../src/adapters/)<br>[市场数据应用层](../src/application/market_data/) | 市场数据实现入口 |
| 测试与验证入口 | [市场 API 测试](../tests/api/file_tests/test_market_api.py)<br>[E2E 市场数据](../tests/e2e/market-data.spec.ts)<br>[前端 E2E 行情](../web/frontend/tests/e2e/market-data.spec.ts) | 市场数据验证入口 |
| 运行与排障入口 | [测试指南](./testing/E2E_TEST_GUIDE.md)<br>[AKShare 市场专题索引](./guides/akshare/INDEX.md)<br>[AkShare 市场统一门禁](../scripts/dev/quality_gate/run_akshare_market_gates.py) | 市场数据与 AkShare 门禁排障入口 |

### 1.1 实时行情监控 {#domain-01-node-01}

| 功能点 | 状态 | 代码位置 | 说明 |
|--------|------|----------|------|
| TDX实时行情 | ✅ | `src/adapters/tdx/realtime_service.py` | 通达信实时行情接入 |
| 股票报价推送 | ✅ | `web/backend/app/api/market/market_data_request.py` | 行情查询与报价接口当前以市场包路由为主 |
| 自选股行情 | ✅ | `web/frontend/src/views/market/Realtime.vue` | 自选股与实时行情主路由页 |
| 板块行情 | ✅ | `src/adapters/akshare/market_adapter/board_sector.py` | 板块涨跌统计 |

### 1.2 资金流向分析 {#domain-01-node-02}

| 功能点 | 状态 | 代码位置 | 说明 |
|--------|------|----------|------|
| 主力资金 | ✅ | `src/adapters/akshare/market_adapter/` | 主力资金监控 |
| 板块资金 | ✅ | `web/frontend/src/views/data/FundFlow.vue`, `web/frontend/src/views/artdeco-pages/market-data-tabs/FundFlow.vue` | 主路由入口在 `data/FundFlow.vue`，ArtDeco 版本更多用于嵌入式展示 |
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

### 1.5 AkShare 市场门禁与 Repo-Truth 收口 {#domain-01-node-05}

边界说明：MyStocks 仅接入本地已存在的 AkShare 同名函数；缺失函数只记录官方同源改名候选和 gap，不在本仓库自研替代实现，也不复用异源接口补位。

| 功能点 | 状态 | 代码位置 | 说明 |
|--------|------|----------|------|
| 本地函数可用性探测 | ✅ | `scripts/dev/quality_gate/collect_akshare_market_function_availability.py` | 扫描当前环境 `akshare` 同名函数可用性，并输出 help candidates 供人工复核 |
| Repo-truth 一致性校验 | ✅ | `scripts/dev/quality_gate/validate_akshare_market_repo_truth.py` | 联动 OpenSpec、事实文档、注册配置与代码线索做对齐检查，只产出审计结果 |
| 统一门禁入口 | ✅ | `scripts/dev/quality_gate/run_akshare_market_gates.py` | 汇总 availability / repo-truth / summary 三份报告，供本地与 CI 复用 |
| 官方改名候选台账 | ⚠️ | `docs/api/AKSHARE_MARKET_ENDPOINTS_REPO_TRUTH.md` | 当前仅把 `stock_dt_pool_em -> stock_zt_pool_dtgc_em`、`stock_strong_pool_em -> stock_zt_pool_strong_em`、`stock_new_em -> stock_zt_pool_sub_new_em` 记为人工评估候选；`stock_news_main_em` 与 `stock_weak_pool_em` 仍未纳入闭环 |

---

## 02-技术分析与指标 {#domain-02}

**模块路径**: `src/indicators/`, `web/backend/app/api/indicators/`, `web/backend/app/api/technical/`, `web/frontend/src/views/data/`, `web/frontend/src/views/technical/`
**API前缀**: `/api/v1/indicators/*`, `/api/v1/technical/*`
**完成度**: 90%

### 领域入口

| 入口类型 | 链接/路径 | 用途 |
|---------|----------|------|
| 规范入口 | [架构红线与审批门禁](../architecture/STANDARDS.md) | 技术分析治理入口 |
| API/契约入口 | [指标包路由](../web/backend/app/api/indicators/__init__.py)<br>[技术分析包路由](../web/backend/app/api/technical/routes.py)<br>[技术分析兼容入口](../web/backend/app/api/technical_analysis.py)<br>[指标兼容入口](../web/backend/app/api/indicators.py) | 主接口以拆分包路由为主，根级兼容入口不再作为主真相源；技术分析接口入口 |
| 前端/交互入口 | [指标分析主路由页](../web/frontend/src/views/data/Advanced.vue)<br>[技术分析旧页](../web/frontend/src/views/technical/TechnicalAnalysis.vue)<br>[技术扫描 Tab](../web/frontend/src/views/artdeco-pages/technical-tabs/TechnicalScannerTab.vue) | 技术分析主路由入口；旧技术分析页更接近保留中的专项工作台；技术分析交互入口 |
| 核心代码入口 | [指标库](../src/indicators/)<br>[技术分析引擎](../src/advanced_analysis/technical_analyzer/) | 技术分析实现入口 |
| 测试与验证入口 | [技术 API 测试](../tests/api/technical.spec.ts)<br>[技术分析 E2E](../tests/e2e/technical-analysis.spec.ts)<br>[K 线图 E2E](../web/frontend/tests/e2e/kline-chart.spec.ts) | 技术分析验证入口 |
| 运行与排障入口 | [运维手册](./operations/OPS_MANUAL.md)<br>[技术分析旧页](../web/frontend/src/views/technical/TechnicalAnalysis.vue) | 技术分析排障入口 |

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
| 画线工具 | ✅ | `web/frontend/src/components/technical/KLineChart.vue` | 趋势线、水平线、矩形 |

### 2.3 技术形态识别 {#domain-02-node-03}

| 形态类型 | 状态 | 说明 |
|----------|------|------|
| K线形态 | ✅ | 吞没、锤子线、十字星等 |
| 图表形态 | ✅ | `web/backend/app/api/_technical_patterns_router.py`<br>头肩顶底、双顶双底 |
| 缺口识别 | ✅ | `web/backend/app/api/_technical_patterns_router.py`<br>`web/frontend/src/components/technical/KLineChart.vue`<br>reviewed `common / breakaway / runaway / exhaustion` 缺口识别与 K 线区间叠加 |

---

## 03-策略管理与回测 {#domain-03}

**模块路径**: `src/backtesting/`, `src/ml_strategy/`, `web/frontend/src/views/strategy/`
**API前缀**: `/api/v1/strategy/*`, `/api/strategy-mgmt/*`, `/ws/*`
**完成度**: 85%

### 领域入口

| 入口类型 | 链接/路径 | 用途 |
|---------|----------|------|
| 规范入口 | [架构红线与审批门禁](../architecture/STANDARDS.md)<br>[OpenSpec 工作流](../openspec/AGENTS.md) | 策略能力与变更治理入口 |
| API/契约入口 | [策略 V1 API](../web/backend/app/api/strategy.py)<br>[策略管理 API](../web/backend/app/api/strategy_management/)<br>[策略 CRUD API](../web/backend/app/api/strategy_mgmt.py)<br>[回测 WebSocket API](../web/backend/app/api/backtest_ws.py) | 策略与回测接口入口 |
| 前端/交互入口 | [策略主路由目录](../web/frontend/src/views/strategy/)<br>[ArtDeco 策略页](../web/frontend/src/views/artdeco-pages/strategy-tabs/) | 策略与回测主路由入口；ArtDeco 页偏嵌入式工作台；策略与回测交互入口 |
| 核心代码入口 | [回测引擎](../src/backtesting/)<br>[机器学习策略](../src/ml_strategy/)<br>[策略应用层](../src/application/strategy/) | 策略与回测实现入口 |
| 测试与验证入口 | [策略 API 测试](../tests/api/strategy.spec.ts)<br>[策略管理 E2E](../tests/e2e/strategy-management.spec.ts)<br>[前端回测 E2E](../web/frontend/tests/e2e/strategy-backtest.spec.ts) | 策略与回测验证入口 |
| 运行与排障入口 | [GPU 测试快速开始](../src/gpu/api_system/TESTING_QUICK_START.md) | 策略与回测排障入口 |

### 3.1 策略配置管理 {#domain-03-node-01}

| 功能点 | 状态 | 代码位置 | 说明 |
|--------|------|----------|------|
| 策略CRUD | ✅ | `web/backend/app/api/strategy_mgmt.py` | 策略增删改查 |
| 策略参数 | ✅ | `web/frontend/src/views/strategy/Parameters.vue` | 主路由包装页，承载参数配置界面 |
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
| 归因分析 | ✅ | `GET /api/v1/backtest/{backtest_id}/attribution`、`web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`、`web/frontend/tests/e2e/strategy-backtest.spec.ts`；Brinson 归因与因子归因已接入回测报告归因面板 |

---

## 04-风险管理与监控 {#domain-04}

**模块路径**: `src/governance/risk_management/`, `web/frontend/src/views/risk/`
**API前缀**: `/api/v1/risk/*`
**完成度**: 80%

### 领域入口

| 入口类型 | 链接/路径 | 用途 |
|---------|----------|------|
| 规范入口 | [架构红线与审批门禁](../architecture/STANDARDS.md) | 风控规则治理入口 |
| API/契约入口 | [风险 API](../web/backend/app/api/risk/)<br>[风险管理 API](../web/backend/app/api/risk_management.py) | 风险指标、止损和预警接口入口 |
| 前端/交互入口 | [风险页面](../web/frontend/src/views/risk/)<br>[ArtDeco 风险页](../web/frontend/src/views/artdeco-pages/risk-tabs/) | 风控主路由入口；风控交互入口 |
| 核心代码入口 | [风险管理核心模块](../src/governance/risk_management/) | 风控实现入口 |
| 测试与验证入口 | [风险管理核心测试](../tests/backend/test_risk_management_core.py)<br>[风险回归测试](../tests/backend/test_risk_management_regression.py)<br>[风险 E2E](../tests/e2e/risk-monitor.spec.ts) | 风控验证入口 |
| 运行与排障入口 | [运维手册](./operations/OPS_MANUAL.md)<br>[风险页面](../web/frontend/src/views/risk/) | 风控排障入口 |

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

| 功能点 | 状态 | 代码位置 | 说明 |
|--------|------|----------|------|
| 风险概览 | ✅ | `web/frontend/src/views/risk/Overview.vue` | 整体风险视图 |
| 持仓风险 | ✅ | `web/frontend/src/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue` | 风险域 `/risk/pnl` 入口，包装持仓风险视图 |
| 历史风险 | ✅ | `web/frontend/src/views/risk/Overview.vue` | 风险趋势图 |

---

## 05-投资组合与交易 {#domain-05}

**模块路径**: `src/portfolio/`, `src/trading/`, `src/application/portfolio/`, `src/application/trading/`
`web/backend/app/api/trade/`, `web/frontend/src/views/trade/`, `web/frontend/src/views/TradingDashboard.vue`
**API前缀**: `/api/v1/trade/*`, `/api/trading/*`, `/api/v1/monitoring/watchlists/*`
**完成度**: 70%

Q2 closure note:
- 本域应按安全敏感域解释，不能把建模完成、页面存在或仓储持久化直接等同为生产级交易闭环
- 当前 inspected execution-capable path 应保守视为 `🧪 experimental` / `🚧 in-progress` 语义，而不是 `production-eligible`
- 涉及下单、执行跟踪、风控前置、交易确认、幂等与审计绑定的节点，必须结合 Phase D / Wave 3 证据理解
- 当前 broker-truth channel topology 已明确为：`miniQMT` 是第一条 `primary-candidate` 通道，Tongdaxin 半手工路径是 `supplemental / operator-assisted` 通道；仓库内现在已具备 primary-path submission classification、authenticated/versioned polling-first live bridge result retrieval、auth/version/method failure review evidence、deferred bridge-result re-entry、repo-owned Windows `qmt` reference service（`scripts/windows_qmt_agent/`）以及 explicit supplemental handoff evidence，但二者都还不能被解读为 production-ready broker adapter
- 与 `/mnt/d/MyCode3/miniQMT` 当前 v1 kernel 对齐后，本仓库已明确接受 `bridge-layer terminal result` 只表达 transport/task truth、`source_name=mock/live`、`broker_event_type=null` 的 Phase A 语义；这类结果当前必须保持 `review_required`，不能被解释为 broker acknowledgement

### 领域入口

| 入口类型 | 链接/路径 | 用途 |
|---------|----------|------|
| 规范入口 | [架构红线与审批门禁](../architecture/STANDARDS.md)<br>[功能管理工作流](./guides/governance/FEATURE_MANAGEMENT_WORKFLOW.md)<br>[执行跟踪 OpenSpec change](../openspec/changes/archive/2026-05-09-add-trade-execution-tracking-workbench/)<br>[Broker Execution Truth Registry](./guides/quant-trading/broker-execution-truth-registry.md)<br>[Windows qmt Agent / Live Contract 审核稿](./guides/quant-trading/windows-qmt-agent-live-contract-requirements-review.md)<br>[Windows qmt Service Ready Checklist](./guides/quant-trading/windows-qmt-service-ready-checklist.md)<br>[Windows qmt Contract Acceptance Guide](./guides/quant-trading/windows-qmt-agent-contract-acceptance-guide.md) | 交易链路、外部执行触发观测、broker truth 通道拓扑、Windows `qmt` agent 对接要求，以及从 `WSL 上的 Ubuntu 24.04.4 LTS` 侧先做 readiness probe、再做本地 mock-mode 合同联调的治理入口 |
| API/契约入口 | [交易包路由](../web/backend/app/api/trade/__init__.py)<br>[交易主路由](../web/backend/app/api/trade/routes.py)<br>[执行跟踪聚合 API](../web/backend/app/api/trade/execution_tracking_routes.py)<br>[交易运行时 API](../web/backend/app/api/trading_runtime.py)<br>[交易监控 API](../web/backend/app/api/trading_monitor.py)<br>[旧交易数据实现](../web/backend/app/api/data/trading_api.py) | 主接口以 `trade/` 包路由、执行跟踪聚合 API 和运行时 API 为主；`data/trading_api.py` 更偏旧服务实现；`/api/v1/trade/execute` 仅作 legacy/compatibility，不作为执行跟踪 canonical 入口；交易执行与对账接口入口 |
| 前端/交互入口 | [交易主路由目录](../web/frontend/src/views/trade/)<br>[执行跟踪观测台](../web/frontend/src/views/trade/Execution.vue)<br>[交易终端](../web/frontend/src/views/TradingDashboard.vue)<br>[ArtDeco 交易页](../web/frontend/src/views/artdeco-pages/trading-tabs/)<br>[旧交易工作台](../web/frontend/src/views/trading/)<br>[旧交易决策组件](../web/frontend/src/views/trading-decision/) | 交易主路由入口；`/trade/execution` 是外部触发、状态观测、证据聚合与对账联动的 canonical 页面；旧目录更多承担历史工作台/组件角色；交易交互入口 |
| 核心代码入口 | [组合应用层](../src/application/portfolio/)<br>[交易应用层](../src/application/trading/)<br>[交易领域模型](../src/domain/trading/)<br>[Windows qmt reference service](../scripts/windows_qmt_agent/app.py) | 交易与持仓及 Windows `qmt` reference service 的实现入口 |
| 测试与验证入口 | [交易路由 API 测试](../tests/api/file_tests/test_trade_routes_api.py)<br>[执行跟踪 API 测试](../web/backend/tests/test_trade_execution_tracking_routes.py)<br>[执行跟踪页面 E2E](../web/frontend/tests/e2e/trade-execution-tracking.spec.ts)<br>[交易 E2E](../tests/e2e/trade-management.spec.ts)<br>[组合 DDD 测试](../tests/ddd/test_phase_5_portfolio.py)<br>[交易应用层 DDD 测试](../tests/ddd/test_phase_7_application.py)<br>[miniQMT live bridge contract 测试](../web/backend/tests/services/test_miniqmt_live_bridge.py)<br>[Windows qmt bridge adapter 测试](../web/backend/tests/services/test_windows_bridge_adapter.py)<br>[Windows qmt reference service 测试](../tests/unit/windows_qmt_agent/test_reference_service.py)<br>[Windows qmt readiness probe 测试](../tests/unit/scripts/test_probe_windows_qmt_service_readiness.py)<br>[Windows qmt acceptance harness 测试](../tests/unit/scripts/test_verify_windows_qmt_agent_contract.py)<br>[Windows qmt formal sequence 测试](../tests/unit/scripts/test_run_windows_qmt_contract_formal_sequence.py)<br>[Windows qmt readiness probe 脚本](../scripts/dev/probe_windows_qmt_service_readiness.py)<br>[Windows qmt acceptance harness 脚本](../scripts/dev/verify_windows_qmt_agent_contract.py)<br>[Windows qmt formal sequence 脚本](../scripts/dev/run_windows_qmt_contract_formal_sequence.py) | 交易与持仓、执行跟踪观测台、broker truth foundation、Windows `qmt` adapter 与 reference service 的验证入口 |
| 运行与排障入口 | [运维手册](./operations/OPS_MANUAL.md)<br>[交易终端](../web/frontend/src/views/TradingDashboard.vue) | 交易排障入口 |

### 5.1 持仓管理 {#domain-05-node-01}

| 功能点 | 状态 | 代码位置 | 说明 |
|--------|------|----------|------|
| 持仓查询 | ✅ | `web/frontend/src/views/trade/Center.vue` | 实时持仓展示 |
| 盈亏计算 | ✅ | `web/frontend/src/views/trade/Center.vue` | 浮动盈亏统计 |
| 持仓分析 | ✅ | `web/frontend/src/views/trade/Portfolio.vue` | 行业分布、集中度、持仓透视与 `GET /api/v1/positions/attribution` 当前/日期口径绩效归因 |

### 5.2 交易记录 {#domain-05-node-02}

| 功能点 | 状态 | 代码位置 | 说明 |
|--------|------|----------|------|
| 交易流水 | ✅ | `web/frontend/src/views/trade/History.vue` | 历史交易记录 |
| 成交查询 | ✅ | `web/frontend/src/views/trade/History.vue` | 成交明细 |
| 对账单 | ✅ | `web/frontend/src/views/trade/Reconciliation.vue`<br>`web/backend/app/api/trade/reconciliation_routes.py`<br>`web/backend/app/services/statement_reconciliation/` | 多账户切换、内部账单投影、`normalized_template` 与 `miniQMT` CSV 导入、自动对账状态与 CSV 导出 |

### 5.3 交易决策 {#domain-05-node-03}

| 功能点 | 状态 | 代码位置 | 说明 |
|--------|------|----------|------|
| 决策中心 | ✅ | `web/frontend/src/views/TradingDashboard.vue` | 交易决策面板；该状态不等同于真实交易执行闭环已达生产可用 |
| 信号生成 | ✅ | `web/frontend/src/views/trade/Signals.vue` | 买卖信号；表示信号能力存在，不代表预执行安全控制已闭合 |
| 执行跟踪 | ✅ | `web/frontend/src/views/trade/Execution.vue`, `web/frontend/src/api/tradeExecutionTracking.ts`, `web/backend/app/api/trade/execution_tracking_routes.py`, `web/frontend/src/views/trade/Reconciliation.vue`, `web/backend/app/services/miniqmt_live_bridge.py`, `web/backend/app/services/windows_bridge_adapter.py`, `src/application/trading/order_mgmt_service.py`, `src/application/trading/broker_reconciliation.py`, `src/application/trading/miniqmt_primary_runtime.py`, `scripts/windows_qmt_agent/app.py`, `scripts/windows_qmt_agent/service.py`, `scripts/dev/probe_windows_qmt_service_readiness.py`, `scripts/dev/verify_windows_qmt_agent_contract.py`, `scripts/dev/run_windows_qmt_contract_formal_sequence.py`, `scripts/templates/windows_task_node.py` | `/trade/execution` 已作为 canonical 执行跟踪 / 外部触发观测台闭合首批范围，聚合内部订单/交易记录、miniQMT bridge evidence、broker correlation 与对账状态；`GET /api/v1/trade/execution-tracking`、`GET /api/v1/trade/execution-tracking/{id}`、`POST /api/v1/trade/execution-tracking/trigger` 已形成查询、详情证据时间线与外部触发请求入口；页面支持筛选、执行链路表、证据抽屉、miniQMT task 状态、到 `/trade/reconciliation` 的上下文跳转，对账页可反向携带上下文回到执行链路。安全边界保持为：`mystocks` 只记录外部触发、回执、状态、证据和对账关系，不声明自身完成真实交易处理；bridge submission receipt 不等于券商确认；缺少 broker lifecycle identity 的 bridge-only terminal result 保持 `review_required`，不能提升为 broker truth。`/api/v1/trade/execute` 保留 legacy/compatibility，不作为新页面 canonical 执行入口；撤单、自动重试、人工处置闭环、production broker adapter 与 production proof 仍是后续范围 |

---

## 06-监控与告警 {#domain-06}

**模块路径**: `src/monitoring/`, `web/frontend/src/views/monitoring/`
**API前缀**: `/api/v1/monitoring/*`, `/api/v1/monitoring/analysis/*`, `/api/v1/monitoring/watchlists/*`, `/api/data-quality/*`, `/api/signals/*`
**完成度**: 75%

### 领域入口

| 入口类型 | 链接/路径 | 用途 |
|---------|----------|------|
| 规范入口 | [架构红线与审批门禁](../architecture/STANDARDS.md)<br>[运维文档总览](./operations/README.md) | 监控、告警与可观测性治理入口 |
| API/契约入口 | [监控 API](../web/backend/app/api/monitoring.py)<br>[监控组合分析 API](../web/backend/app/api/monitoring_analysis.py)<br>[监控自选组合 API](../web/backend/app/api/monitoring_watchlists.py)<br>[数据质量 API](../web/backend/app/api/data_quality.py)<br>[信号监控 API](../web/backend/app/api/signal_monitoring/) | 监控、告警与质量接口入口 |
| 前端/交互入口 | [系统遥测页](../web/frontend/src/views/system/API.vue)<br>[告警中心页](../web/frontend/src/views/risk/Alerts.vue)<br>[监控目录](../web/frontend/src/views/monitoring/)<br>[独立监控页](../web/frontend/src/views/monitor.vue) | 监控与告警主路由入口；监控与告警交互入口 |
| 核心代码入口 | [监控模块](../src/monitoring/)<br>[数据质量监控器](../src/monitoring/data_quality_monitor.py)<br>[监控核心](../src/core/monitoring.py) | 监控与告警实现入口 |
| 测试与验证入口 | [监控测试目录](../tests/monitoring/)<br>[监控仪表板 E2E](../tests/e2e/monitoring-dashboard.spec.ts)<br>[监控单元测试](../tests/unit/monitoring/test_monitoring_service.py) | 监控与告警验证入口 |
| 运行与排障入口 | [监控栈 README](../config/monitoring-stack/README.md)<br>[Grafana 设置](./operations/deployment/SETUP_GRAFANA.md) | 监控与告警排障入口 |

### 6.1 系统监控 {#domain-06-node-01}

| 功能点 | 状态 | 代码位置 | 说明 |
|--------|------|----------|------|
| 性能监控 | ✅ | `web/frontend/src/views/system/Settings.vue`, `web/frontend/src/views/system/API.vue` | 当前主事实是 API 性能表、健康探针与遥测面板 |
| 服务状态 | ✅ | `web/frontend/src/views/system/API.vue`, `web/frontend/src/views/monitor.vue` | 已有后端健康、中间件状态与前后端/数据库连通性检查 |
| 资源使用 | ✅ | `web/frontend/src/views/system/Resources.vue`, `web/backend/app/api/v1/system/resources.py` | 已形成独立资源使用工作台，提供 host / process / dependency 快照、短窗口趋势、阈值状态与轮询控制 |

### 6.2 数据质量 {#domain-06-node-02}

Q2 closure note:
- `✅` here should be interpreted conservatively until data-quality ownership closure is fully evidenced
- canonical split is:
  - validation
  - monitoring
  - governance/reporting
  - repair/backfill remains an explicit gap
- this node should not be read as proof that repair or backfill workflows are already first-class

| 功能点 | 状态 | 代码位置 | 说明 |
|--------|------|----------|------|
| 数据完整性 | ✅ | `src/monitoring/data_quality_monitor.py`, `web/backend/app/api/data_quality.py` | 完整性、新鲜度、准确性检查与运维接口均已存在 |
| 数据一致性 | ✅ | `src/core/data_quality_validator.py`, `web/frontend/src/views/artdeco-pages/market-data-tabs/DataQualityPanel.vue` | 多源校验由验证器主导；前端仅见市场数据工作台中的嵌入式质量面板 |
| 异常检测 | ✅ | `src/monitoring/data_quality_monitor.py`, `web/backend/app/api/data_quality.py` | 质量异常可落到告警与确认/解决接口；repair/backfill 仍是显式 gap |

### 6.3 告警管理 {#domain-06-node-03}

| 功能点 | 状态 | 代码位置 | 说明 |
|--------|------|----------|------|
| 告警规则 | ✅ | `web/frontend/src/views/risk/Alerts.vue`, `web/backend/app/api/monitoring.py` | 当前活跃入口是 `/risk/alerts`，可查看规则状态并读取告警规则接口 |
| 告警通知 | ✅ | `src/monitoring/alert_manager.py`, `config/monitoring/alerting.yaml` | 应用层告警与 Prometheus/Grafana 路由配置均存在 |
| 告警历史 | ✅ | `web/frontend/src/views/risk/Alerts.vue`, `web/backend/app/api/monitoring.py` | 告警记录、未读状态和历史查询已形成工作台入口 |

---

## 07-高级分析与AI {#domain-07}

**模块路径**: `src/advanced_analysis/`, `src/ml_strategy/`
**API前缀**: `/api/v1/advanced-analysis/*`, `/api/v1/algorithms/*`, `/api/ml/*`, `/api/gpu/*`
**完成度**: 50%

### 领域入口

| 入口类型 | 链接/路径 | 用途 |
|---------|----------|------|
| 规范入口 | [架构红线与审批门禁](../architecture/STANDARDS.md)<br>[OpenSpec 工作流](../openspec/AGENTS.md) | AI 与实验能力治理入口 |
| API/契约入口 | [高级分析 API](../web/backend/app/api/advanced_analysis.py)<br>[机器学习兼容 API](../web/backend/app/api/ml.py)<br>[v1 机器学习策略 API](../web/backend/app/api/v1/strategy/machine_learning.py)<br>[AI 批量分析 API](../web/backend/app/api/v1/strategy/batch_analysis.py)<br>[GPU 监控 API](../web/backend/app/api/gpu_monitoring.py)<br>[情感分析 API](../web/backend/app/api/v1/analysis/sentiment.py)<br>[算法兼容入口](../web/backend/app/api/algorithms.py) | AI 与高级分析接口入口 |
| 前端/交互入口 | [AI 情感分析页](../web/frontend/src/views/ai/Sentiment.vue)<br>[AI 模型训练 / 预测页](../web/frontend/src/views/ai/MlWorkbench.vue)<br>[AI 批量分析页](../web/frontend/src/views/ai/BatchAnalysis.vue)<br>[策略主路由目录](../web/frontend/src/views/strategy/)<br>[GPU 回测页](../web/frontend/src/views/strategy/BacktestGPU.vue)<br>[策略信号页](../web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue) | AI 与高级分析主路由入口；AI 与高级分析交互入口 |
| 核心代码入口 | [高级分析模块](../src/advanced_analysis/)<br>[机器学习策略模块](../src/ml_strategy/)<br>[情感分析模块](../src/advanced_analysis/sentiment_analyzer/)<br>[GPU API 服务](../src/gpu/api_system/services/) | AI 与高级分析实现入口 |
| 测试与验证入口 | [v1 ML workbench 契约测试](../web/backend/tests/test_v1_ml_workbench_contract.py)<br>[AI ML workbench E2E](../web/frontend/tests/e2e/ai-ml-workbench.spec.ts)<br>[机器学习 API 测试](../tests/api/test_ml_file.py)<br>[高级回测测试](../tests/unit/test_advanced_backtest_engine.py)<br>[GPU 测试 README](../src/gpu/api_system/tests/README.md) | AI 与高级分析验证入口 |
| 运行与排障入口 | [自动化说明](../src/ml_strategy/automation/README.md)<br>[GPU API README](../src/gpu/api_system/README.md)<br>[WSL2 GPU 设置](../src/gpu/api_system/WSL2_GPU_SETUP.md) | AI 与高级分析排障入口 |

### 7.1 机器学习策略 {#domain-07-node-01}

| 功能点 | 状态 | 代码位置 | 说明 |
|--------|------|----------|------|
| 特征工程 | ✅ | `src/ml_strategy/feature_engineering.py`, `web/backend/app/api/ml.py` | 特征生成与样本构造接口已存在 |
| 模型训练 | ✅ | `web/backend/app/api/v1/strategy/machine_learning.py`, `web/backend/app/api/v1/strategy/ml_workbench.py`, `web/frontend/src/views/ai/MlWorkbench.vue`, `web/frontend/src/api/mlWorkbench.ts` | 首批 canonical 入口为 `/api/v1/strategies/ml/train` 与 `/ai/ml`；缺少模型族必需后端依赖时返回明确 service-unavailable；旧 `/api/ml/models/*` 保留为兼容面 |
| 预测推理 | ✅ | `web/backend/app/api/v1/strategy/machine_learning.py`, `web/backend/app/api/v1/strategy/ml_workbench.py`, `web/frontend/src/views/ai/MlWorkbench.vue`, `web/frontend/src/api/mlWorkbench.ts` | 首批 canonical 入口为 `/api/v1/strategies/ml/predict` 与 `/ai/ml`；预测结果明确为分析输出，不代表交易指令或成交事实；缺少模型族必需后端依赖时不生成预测 |

### 7.2 批量分析 {#domain-07-node-02}

| 功能点 | 状态 | 代码位置 | 说明 |
|--------|------|----------|------|
| 批量回测 | ✅ | `web/backend/app/api/v1/strategy/batch_analysis.py`, `web/frontend/src/views/ai/BatchAnalysis.vue`, `web/frontend/src/api/batchAnalysis.ts`, `web/frontend/src/views/strategy/Backtest.vue`, `src/ml_strategy/backtest/backtest_engine.py` | `/ai/batch` 与 `/api/v1/strategies/batch-analysis/*` 已作为 7.2 canonical 批量分析观测入口，聚合批量回测证据；首批只返回运行时任务证据与分析摘要，不替代既有回测引擎 |
| 批量选股 | ✅ | `web/backend/app/api/v1/strategy/batch_analysis.py`, `web/frontend/src/views/ai/BatchAnalysis.vue`, `src/ml_strategy/strategy/stock_screener.py` | canonical 工作台支持 `batch_screening` 任务提交、列表与详情；结果为分析证据，不是交易指令或自动调仓建议 |
| 批量监控 | ✅ | `web/backend/app/api/v1/strategy/batch_analysis.py`, `web/frontend/src/views/ai/BatchAnalysis.vue`, `src/ml_strategy/automation/scheduler.py`, `src/ml_strategy/strategy/strategy_executor.py` | canonical 工作台暴露 `batch_monitoring` 扩展位与底层 evidence modules；首批不做 production scheduler mutation、实时流式进度或自动化处置闭环 |

### 7.3 情感分析 {#domain-07-node-03}

| 功能点 | 状态 | 代码位置 | 说明 |
|--------|------|----------|------|
| 新闻情感 | ✅ | `web/frontend/src/views/ai/Sentiment.vue`, `web/backend/app/api/v1/analysis/sentiment.py`, `src/advanced_analysis/sentiment_analyzer/` | AI 域独立入口 `/ai/sentiment` 已落地，并整合文本分析、个股趋势与市场情绪概览 |
| 舆情监控 | ✅ | `web/frontend/src/views/ai/Sentiment.vue`, `web/frontend/src/views/risk/News.vue`, `web/backend/app/api/v1/analysis/sentiment.py` | AI 域 canonical 工作台已接管公告/舆情主入口；`/risk/news` 保留为风险域包装页并复用共享工作台逻辑 |

---

## 08-系统管理与配置 {#domain-08}

**模块路径**: `web/backend/app/api/auth.py`, `web/backend/app/api/v1/system/`, `web/frontend/src/views/Login.vue`, `web/frontend/src/stores/auth.ts`, `web/frontend/src/router/guards.ts`, `web/frontend/src/api/apiClient.ts`, `web/frontend/src/views/system/`, `web/frontend/src/api/types/`, `web/frontend/scripts/`, `scripts/_generate_frontend_types_cli.py`
**API前缀**: `/api/v1/auth/*`, `/api/v1/system/settings/*`, `/api/v1/system/health/*`, `/api/backup-recovery/*`
**完成度**: 85%

### 领域入口

| 入口类型 | 链接/路径 | 用途 |
|---------|----------|------|
| 规范入口 | [架构红线与审批门禁](../architecture/STANDARDS.md)<br>[运维文档总览](./operations/README.md) | 认证、系统配置与恢复治理入口 |
| API/契约入口 | [认证 API](../web/backend/app/api/auth.py)<br>[系统设置 API](../web/backend/app/api/v1/system/settings.py)<br>[系统健康 API](../web/backend/app/api/v1/system/health.py)<br>[备份恢复 API](../web/backend/app/api/backup_recovery.py) | 认证、系统与恢复接口入口 |
| 前端/交互入口 | [登录页](../web/frontend/src/views/Login.vue)<br>[系统主路由目录](../web/frontend/src/views/system/) | 系统管理主路由入口；`Login.vue` 承担认证入口；系统管理交互入口 |
| 核心代码入口 | [认证 Store](../web/frontend/src/stores/auth.ts)<br>[认证路由守卫](../web/frontend/src/router/guards.ts)<br>[路由权限工具](../web/frontend/src/router/utils.js)<br>[前端 API Client](../web/frontend/src/api/apiClient.ts)<br>[备份恢复模块](../src/infrastructure/backup_recovery/)<br>[前端类型主索引](../web/frontend/src/api/types/index.ts)<br>[前端类型扩展目录](../web/frontend/src/api/types/extensions/)<br>[前端类型生成器](../scripts/_generate_frontend_types_cli.py)<br>[类型治理脚本目录](../web/frontend/scripts/)<br>[Docker 部署说明](../docker/README.md) | 系统管理与工程治理实现入口 |
| 测试与验证入口 | [认证 API 测试](../tests/api/auth.spec.ts)<br>[前端认证 API 测试](../web/frontend/src/api/__tests__/authApi.spec.ts)<br>[前端 API Client 测试](../web/frontend/src/api/apiClient.spec.ts)<br>[前端认证守卫测试](../web/frontend/src/stores/__tests__/auth-guard.spec.ts)<br>[前端认证路由元数据测试](../web/frontend/src/stores/__tests__/auth-guard-route-meta.spec.ts)<br>[前端路由权限工具测试](../web/frontend/src/router/__tests__/utils.spec.ts)<br>[系统 API 测试](../tests/api/system.spec.ts)<br>[JWT 安全测试](../tests/security/test_jwt_authentication.py)<br>[扩展类型工具链测试](../tests/unit/scripts/test_frontend_type_extension_tooling.py)<br>[扩展类型兼容性测试](../tests/unit/scripts/test_frontend_type_extension_compatibility.py) | 系统管理与工程治理验证入口 |
| 运行与排障入口 | [部署文档总览](./operations/deployment/README.md)<br>[部署指南](./operations/deployment-guide.md)<br>[Docker README](../docker/README.md) | 系统管理排障入口 |

### 8.1 认证授权 {#domain-08-node-01}

| 功能点 | 状态 | 代码位置 | 说明 |
|--------|------|----------|------|
| 用户登录 | ✅ | `web/frontend/src/views/Login.vue`, `web/frontend/src/stores/auth.ts`, `web/frontend/src/api/apiClient.ts`, `web/backend/app/api/auth.py` | 当前登录链路以 JWT 登录、Pinia 持久化、登录页和请求头 token 过滤为主；空白或畸形 token 不进入有效会话或请求头 |
| 权限管理 | ✅ | `web/frontend/src/stores/auth.ts`, `web/frontend/src/router/guards.ts`, `web/frontend/src/router/utils.js`, `web/backend/app/api/auth.py` | 角色、权限和 route meta 已进入 store / guard / route utility 三层校验；畸形 payload 与畸形 route meta 按拒绝访问处理 |
| 会话管理 | ✅ | `web/frontend/src/stores/auth.ts`, `web/frontend/src/api/apiClient.ts`, `web/backend/app/api/auth.py` | 已有登出、本地持久化初始化、token 刷新、401 清理与兼容 storage key 清理契约 |

### 8.2 系统配置 {#domain-08-node-02}

| 功能点 | 状态 | 代码位置 | 说明 |
|--------|------|----------|------|
| 通用配置 | ✅ | `web/frontend/src/views/system/Settings.vue`, `web/backend/app/api/v1/system/settings.py` | `general` 分段已有真实读写契约，并持久化到 `system_config` |
| 安全配置 | ✅ | `web/backend/app/api/v1/system/settings.py` | `security` 分段已有 canonical API，前端由系统配置中心承载 |
| 数据源配置 | ✅ | `web/frontend/src/views/system/DataSource.vue`, `web/backend/app/api/data_source_config.py` | 数据源启停、端点配置与写回面板已在 |

### 8.3 备份恢复 {#domain-08-node-03}

| 功能点 | 状态 | 代码位置 | 说明 |
|--------|------|----------|------|
| 数据备份 | ✅ | `web/backend/app/api/backup_recovery.py`, `src/infrastructure/backup_recovery/backup_manager.py` | 备份 API 与 TDengine/PostgreSQL 备份管理器已在 |
| 数据恢复 | ✅ | `web/backend/app/api/backup_recovery.py`, `src/infrastructure/backup_recovery/recovery_manager.py` | 恢复任务、恢复日志与状态查询能力存在 |
| 备份调度 | ✅ | `src/infrastructure/backup_recovery/backup_scheduler.py` | 已有全量/增量备份调度，当前未见独立前台入口 |

### 8.4 前端类型扩展与治理 {#domain-08-node-04}

| 功能点 | 状态 | 代码位置 | 说明 |
|--------|------|----------|------|
| 扩展命名空间入口 | ✅ | `web/frontend/src/api/types/index.ts`, `web/frontend/src/api/types/extensions/index.ts` | 当前以 `export * as extensions from './extensions'` 暴露 frontend-only 类型扩展面，并保留 root-level shim 兼容旧导入 |
| canonical 子目录结构 | ✅ | `web/frontend/src/api/types/extensions/strategy/index.ts`, `web/frontend/src/api/types/extensions/common/index.ts`, `web/frontend/src/api/types/extensions/ui/index.ts`, `web/frontend/src/api/types/extensions/market/index.ts`, `web/frontend/src/api/types/extensions/api/index.ts`, `web/frontend/src/api/types/extensions/utils/index.ts` | 当前 canonical 结构已从 root-level 域文件切换为子目录入口；`strategy.ts`、`common.ts`、`ui.ts` 仅作为薄兼容 shim 保留 |
| 兼容性与编译烟测 | ✅ | `web/frontend/src/api/types/compatibility-smoke.ts`, `tests/unit/scripts/test_frontend_type_extension_compatibility.py` | compile-time smoke 会同时覆盖 legacy root exports 与 extension public surface，证明扩展命名空间未破坏既有主索引消费方 |
| 类型治理报告与 dashboard | ✅ | `web/frontend/scripts/generate-type-validation-report.js`, `web/frontend/scripts/generate-type-health-dashboard.js`, `reports/analysis/typescript-extension-validation/` | 当前已具备 validation/conflicts/naming/jsdoc/coverage/typecheck 汇总报告与静态 dashboard，`coverage.percent=100`、`unused.count=0` 为 2026-05-03 实测值 |

---

## 09-数据存储与管理 {#domain-09}

**模块路径**: `src/core/`, `src/core/infrastructure/`, `src/data_access/`, `src/storage/database/`, `web/backend/app/api/`
**API前缀**: `/api/v1/data/*`, `/api/v1/data-sources/*`, `/api/v1/data-sources/config/*`, `/api/v1/lineage/*`, `/api/cache/*`
**完成度**: 90%

### 领域入口

| 入口类型 | 链接/路径 | 用途 |
|---------|----------|------|
| 规范入口 | [架构红线与审批门禁](../architecture/STANDARDS.md)<br>[架构文档总览](./architecture/README.md) | 数据架构、分层和存储治理入口 |
| API/契约入口 | [统一管理器契约](../tests/001-readme-md-md/contracts/unified_manager_api.md)<br>[数据路由 API](../web/backend/app/api/v1/system/routing.py)<br>[数据源注册 API](../web/backend/app/api/data_source_registry.py)<br>[数据源配置 API](../web/backend/app/api/data_source_config.py)<br>[数据血缘 API](../web/backend/app/api/data_lineage.py)<br>[缓存治理 API](../web/backend/app/api/cache.py) | 数据存储与治理接口入口 |
| 前端/交互入口 | [数据源管理页](../web/frontend/src/views/system/DataSource.vue)<br>[系统主路由目录](../web/frontend/src/views/system/) | 数据存储与治理主路由入口；数据存储与治理交互入口 |
| 核心代码入口 | [统一管理器](../src/core/unified_manager.py)<br>[核心协调器](../src/core/data_manager.py)<br>[数据路由器](../src/core/infrastructure/data_router.py)<br>[数据分类枚举](../src/core/data_classification.py)<br>[数据库存储模块](../src/storage/database/)<br>[数据访问层](../src/data_access/) | 数据存储与治理实现入口 |
| 测试与验证入口 | [数据 API 测试](../tests/api/test_data_file.py)<br>[API 集成测试](../tests/integration/test_api_integration.py)<br>[市场数据单元测试](../tests/unit/test_market_data.py) | 数据存储与治理验证入口 |
| 运行与排障入口 | [基础设施 Docker 说明](../docker/README.md)<br>[运维文档总览](./operations/README.md)<br>[架构文档总览](./architecture/README.md) | 数据存储与治理排障入口 |

### 9.1 数据库架构 {#domain-09-node-01}

| 组件 | 状态 | 代码位置 | 说明 |
|------|------|----------|------|
| PostgreSQL | ✅ | `src/core/data_classification.py`, `src/core/infrastructure/data_router.py`, `src/core/data_manager.py` | 当前 canonical 主数据仓库，承载日线、参考、衍生、交易与系统配置 |
| TDengine | ✅ | `src/core/data_classification.py`, `src/core/infrastructure/data_router.py`, `src/core/data_manager.py` | 当前 canonical 高频时序库，主要承载 Tick、分钟 K 线与深度行情 |
| Redis | ⚠️ | `web/frontend/src/views/system/Architecture.vue`, `web/frontend/src/views/system/DatabaseMonitor.vue`, `web/backend/app/api/system/get_system_architecture.py` | 更接近历史架构/兼容说明项；当前缓存能力以应用层实现为主 |
| MongoDB | ⚠️ | `src/services/maestro/collab/backends/mongo/store.py`, `src/services/symphony/service.py`, `config/mongodb/mongod.conf` | 仍服务于协作运行时子系统，但不属于市场数据双库主拓扑 |

### 9.2 数据访问层 {#domain-09-node-02}

| 功能点 | 状态 | 代码位置 | 说明 |
|--------|------|----------|------|
| 统一管理器 | ✅ | `src/core/unified_manager.py` | 统一数据访问 |
| 分类路由 | ✅ | `src/core/data_classification.py`, `src/core/infrastructure/data_router.py`, `web/backend/app/api/v1/system/routing.py` | 分类枚举、运行时路由器与查询路由 API 已闭环 |
| 表管理器 | ✅ | `src/storage/database/database_manager/` | 表结构管理 |

### 9.3 缓存管理 {#domain-09-node-03}

| 功能点 | 状态 | 代码位置 | 说明 |
|--------|------|----------|------|
| 查询缓存 | ✅ | `web/backend/app/api/cache.py`, `web/backend/app/api/_cache_basic_routes.py` | 已有读写、状态查询与按标的读取接口；当前以后端治理为主 |
| 缓存失效 | ✅ | `web/backend/app/api/cache.py`, `web/backend/app/api/_cache_eviction_routes.py` | 已有单标的失效、全量清理、手动淘汰和淘汰统计能力 |
| 缓存统计 | ✅ | `web/backend/app/api/_cache_basic_routes.py`, `web/backend/app/api/_cache_prewarming_routes.py`, `web/backend/app/core/cache_prewarming.py` | 已有命中率、延迟、健康与预热接口，当前定位偏运维后台 |

---

## 10-公告与信息 {#domain-10}

**模块路径**: `web/backend/app/api/announcement/`, `web/frontend/src/views/risk/`, `web/frontend/src/views/announcement/`
**API前缀**: `/api/announcement/*`, `/api/v1/announcement/*`
**完成度**: 80%

### 领域入口

| 入口类型 | 链接/路径 | 用途 |
|---------|----------|------|
| 规范入口 | [架构红线与审批门禁](../architecture/STANDARDS.md) | 公告与信息治理入口 |
| API/契约入口 | [公告包路由](../web/backend/app/api/announcement/routes.py)<br>[公告包导出](../web/backend/app/api/announcement/__init__.py)<br>[旧版平行实现](../web/backend/app/api/announcement.py) | 公告真实导出位于包路由；根级 `announcement.py` 更接近历史平行实现；公告接口入口 |
| 前端/交互入口 | [风险公告页](../web/frontend/src/views/risk/News.vue)<br>[公告工作台目录](../web/frontend/src/views/announcement/)<br>[ArtDeco 公告组件](../web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoAnnouncementMonitor.vue) | 公告主路由入口；`views/announcement/` 偏详情/规则工作台；公告交互入口 |
| 核心代码入口 | [公告服务](../web/backend/app/services/announcement_service.py)<br>[公告模型](../web/backend/app/models/announcement.py) | 公告实现入口 |
| 测试与验证入口 | [公告 API 测试](../tests/api/file_tests/test_announcement_api.py)<br>[后端公告 API 自测](../web/backend/app/api/test_announcement_api.py) | 公告验证入口 |
| 运行与排障入口 | [运维手册](./operations/OPS_MANUAL.md)<br>[公告详情页](../web/frontend/src/views/announcement/AnnouncementMonitor.vue) | 公告排障入口 |

### 10.1 公告管理 {#domain-10-node-01}

| 功能点 | 状态 | 代码位置 | 说明 |
|--------|------|----------|------|
| 公告抓取 | ✅ | `web/backend/app/api/announcement/routes.py`, `web/backend/app/services/announcement_service.py` | 包路由已暴露 `fetch/list/today/important` 等能力，服务层负责抓取入库 |
| 公告分类 | ✅ | `web/backend/app/models/announcement.py`, `web/backend/app/services/announcement_service.py`, `web/frontend/src/views/risk/News.vue` | 模型已含类型、重要性、情绪字段，风险页可按类型与重要性展示 |
| 公告搜索 | ✅ | `web/backend/app/api/announcement/routes.py`, `web/frontend/src/views/announcement/AnnouncementMonitor.vue`, `web/frontend/src/views/announcement/composables/useAnnouncementMonitor.ts` | 详情页工作台已支持股票、类型、重要性与日期筛选 |

### 10.2 公告监控 {#domain-10-node-02}

| 功能点 | 状态 | 代码位置 | 说明 |
|--------|------|----------|------|
| 实时监控 | ✅ | `web/frontend/src/views/risk/News.vue`, `web/frontend/src/api/index.ts`, `web/backend/app/api/announcement/routes.py` | 主监控入口位于风险域公告工作台，通过 `/api/announcement/list` 刷新列表 |
| 重大事件 | ✅ | `web/backend/app/api/announcement/routes.py`, `web/backend/app/services/announcement_service.py`, `web/frontend/src/views/risk/News.vue` | 重要性与情绪判断已进入后端服务和前端风险视图 |
| 订阅管理 | ✅ | `web/backend/app/api/announcement/routes.py`, `web/backend/app/models/announcement.py`, `web/frontend/src/views/announcement/AnnouncementMonitor.vue` | 规则、触发记录与规则评估已在，当前更偏规则工作台 |

---

## 功能统计

| 统计项 | 数量 |
|--------|------|
| 功能领域 | 10 |
| 子功能模块 | 30 |
| 领域入口表 | 10 |
| 当前统计口径 | 文档结构计数 |
| 运行时指标口径 | 不在本页维护 |

---

## 文档补充

- 更新日志: [CHANGELOG.md](../CHANGELOG.md)
- 架构设计: [architecture/](./architecture/)
- API 文档: [api/](./api/)
- 开发指南: [guides/](./guides/)

---

*最后更新: 2026-05-05*
