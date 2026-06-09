# TdxQuant 接入 MyStocks 可行性评估

**日期**: 2026-04-28
**评估人**: Codex
**评估目的**: 评估 `/opt/iflow/TdxQuant` 是否有必要接入 MyStocks，并给出建议的接入方式、边界和前置改进意见。
**当前结论**: 有接入价值，但不建议全量并入；建议把 TdxQuant 作为 `Windows 侧通达信能力提供者` 分阶段接入。

## 1. 评估范围

本次评估主要基于以下内容：

- TdxQuant 功能地图与接口组织
  - `/opt/iflow/TdxQuant/docs/TdxQuant_Project_Function_Map.md`
  - `/opt/iflow/TdxQuant/tdxquant/api/manager.py`
  - `/opt/iflow/TdxQuant/tdxquant/api/task.py`
  - `/opt/iflow/TdxQuant/tdxquant/api/formula.py`
  - `/opt/iflow/TdxQuant/tdxquant/api/bridge.py`
  - `/opt/iflow/TdxQuant/tdxquant/trade/manager.py`
- MyStocks 当前 TDX、实时订阅、交易、Windows bridge 相关实现
  - [web/backend/app/services/tdx_service.py](/opt/claude/mystocks_spec/web/backend/app/services/tdx_service.py:21)
  - [web/backend/app/api/tdx.py](/opt/claude/mystocks_spec/web/backend/app/api/tdx.py:1)
  - [src/adapters/tdx_realtime_manager.py](/opt/claude/mystocks_spec/src/adapters/tdx_realtime_manager.py:17)
  - [web/backend/app/api/trade/routes.py](/opt/claude/mystocks_spec/web/backend/app/api/trade/routes.py:1)
  - [web/backend/app/services/windows_bridge_adapter.py](/opt/claude/mystocks_spec/web/backend/app/services/windows_bridge_adapter.py:13)
- MyStocks 现有选股/指标能力
  - [web/backend/app/services/indicators/talib_adapter.py](/opt/claude/mystocks_spec/web/backend/app/services/indicators/talib_adapter.py:29)
  - [web/frontend/src/composables/market/useDataAnalysis.ts](/opt/claude/mystocks_spec/web/frontend/src/composables/market/useDataAnalysis.ts:171)
  - [web/frontend/src/views/data/Advanced.vue](/opt/claude/mystocks_spec/web/frontend/src/views/data/Advanced.vue:317)
- 项目治理约束
  - [architecture/STANDARDS.md](/opt/claude/mystocks_spec/architecture/STANDARDS.md:10)
  - [openspec/specs/trading-execution-safety/spec.md](/opt/claude/mystocks_spec/openspec/specs/trading-execution-safety/spec.md:13)

## 2. 总体判断

TdxQuant 的定位不是完整策略中心，也不是标准化券商交易 API，而是：

- 通达信本地数据与公式能力封装层
- 通达信实时订阅与客户端联动能力层
- 桌面自动化交易执行辅助层
- task / report / catalog 的统一日常入口层

这一定义与 MyStocks 并不冲突。MyStocks 的核心仍应保持为：

- 数据中台与双数据库体系
- Web API 与前端可视化
- 策略、风控、监控、回测、统一任务编排

因此，合理关系应是：

- MyStocks 作为上层系统
- TdxQuant 作为特定场景下的 TongDaXin 本地能力 provider

不建议把 TdxQuant 当作 MyStocks 的替代层，也不建议让其反向主导 MyStocks 的主架构。

## 3. 为什么有接入必要

### 3.1 通达信原生公式能力有明显补强价值

TdxQuant 在 `formula` 域已经覆盖：

- 指标计算
- 选股计算
- 专家公式计算
- 批量选股
- 批量指标计算

见 [TdxQuant_Project_Function_Map.md](/opt/iflow/TdxQuant/docs/TdxQuant_Project_Function_Map.md:61)。

MyStocks 当前更强的是标准技术指标体系和 TA-Lib 计算，[talib_adapter.py](/opt/claude/mystocks_spec/web/backend/app/services/indicators/talib_adapter.py:29)。但前端选股目前仍主要是本地条件过滤，[useDataAnalysis.ts](/opt/claude/mystocks_spec/web/frontend/src/composables/market/useDataAnalysis.ts:171)，页面也明确暴露了“技术指标筛选能力未完全接入”的状态，[Advanced.vue](/opt/claude/mystocks_spec/web/frontend/src/views/data/Advanced.vue:317)。

结论：

- MyStocks 目前缺的是“通达信原生公式体系”
- TdxQuant 最有差异化价值的正是这部分

这块值得优先接。

### 3.2 实时订阅能力优于 MyStocks 当前占位实现

TdxQuant 已有持久订阅 session：

- `open_subscription_session`
- `subscribe_hq`
- `unsubscribe_hq`
- `get_subscribe_hq_stock_list`

见 [TdxQuant_Project_Function_Map.md](/opt/iflow/TdxQuant/docs/TdxQuant_Project_Function_Map.md:116) 和 [bridge.py](/opt/iflow/TdxQuant/tdxquant/api/bridge.py:188)。

MyStocks 当前的 `TdxRealtimeManager` 仍是模拟数据和模拟订阅逻辑，[tdx_realtime_manager.py](/opt/claude/mystocks_spec/src/adapters/tdx_realtime_manager.py:149)。它适合测试或占位，不足以支撑真正的 TongDaXin 实时订阅产品化。

结论：

- 若要把 `market realtime / watchlist signals / risk alerts / strategy signals` 做实
- TdxQuant 的 session 能力值得吸收

### 3.3 自定义板块能力可增强 watchlist 和策略落板块流程

TdxQuant 已形成完整 `block` 生命周期：

- 读取自定义板块
- 创建板块
- 删除板块
- 重命名板块
- 清空板块
- 写入板块成分

见 [TdxQuant_Project_Function_Map.md](/opt/iflow/TdxQuant/docs/TdxQuant_Project_Function_Map.md:77) 和 [manager.py](/opt/iflow/TdxQuant/tdxquant/api/manager.py:1016)。

MyStocks 现在有自己的 watchlist / monitoring watchlists，但主要是 PostgreSQL 内部模型，[monitoring_watchlists.py](/opt/claude/mystocks_spec/web/backend/app/api/monitoring_watchlists.py:1)。缺少与 TongDaXin 客户端自定义板块的联动层。

这意味着可以形成一个很实用的场景：

- MyStocks 选股结果
- 一键同步到通达信自定义板块
- 或把通达信板块拉回 MyStocks 作为 watchlist/monitoring group

### 3.4 桌面交易辅助执行有补位价值，但只能后置

TdxQuant 的桌面交易线已经形成 `TdxTradeManager`、profile、preset、结果回填和事件日志，[trade/manager.py](/opt/iflow/TdxQuant/tdxquant/trade/manager.py:112)，功能地图也明确将其定义为“辅助实盘执行”而非标准交易 API，[TdxQuant_Project_Function_Map.md](/opt/iflow/TdxQuant/docs/TdxQuant_Project_Function_Map.md:178)。

MyStocks 当前的 trade API 更偏：

- runtime session
- positions / portfolio / signals
- backtest trades 查询

见 [trade/routes.py](/opt/claude/mystocks_spec/web/backend/app/api/trade/routes.py:44)。

因此 TdxQuant 可以补充 `桌面执行能力`，但不应直接替换 MyStocks 现有交易语义层。

## 4. 可行性判断

## 4.1 接口组织本身适合集成

TdxQuant 的可复用接口已经比较清晰：

- 查询与运行时主线：`TdxApiManager`
- 场景任务主线：`TdxTaskManager`
- 桌面交易主线：`TdxTradeManager`
- CLI：可直接作为桥接协议入口

对应代码：

- [TdxApiManager](/opt/iflow/TdxQuant/tdxquant/api/manager.py:1113)
- [TdxTaskManager](/opt/iflow/TdxQuant/tdxquant/api/task.py:503)
- [FormulaApi](/opt/iflow/TdxQuant/tdxquant/api/formula.py:19)
- [TdxTradeManager](/opt/iflow/TdxQuant/tdxquant/trade/manager.py:112)

这说明它已经不只是脚本集合，而是具备被上层系统消费的基础形态。

## 4.2 直接在当前 WSL/Linux 主进程内嵌不可行

这是本次评估最重要的现实约束。

TdxQuant 在 `bridge.py` 中明确做了平台限制：

- 非 Windows 平台直接返回 `unsupported_platform`
- next action 明确要求从 `native Windows Python` 运行

见 [bridge.py](/opt/iflow/TdxQuant/tdxquant/api/bridge.py:29)。

我在当前环境实测了以下命令：

- `python -m tdxquant.cli tdx-data-snapshot --code 000001`
- `python -m tdxquant.cli tdx-formula-zb --formula-name MA --formula-arg 'N=5'`
- `python -m tdxquant.cli tdx-get-user-sector`
- `TdxApiManager().runtime.open_subscription_session()`

结果均返回 `unsupported_platform`，要求在 Windows Python 下运行。

依赖层也进一步证明了这一点：

- `pywin32` 仅 Windows 安装
- `pywinauto` 仅 Windows 安装

见 [requirements.txt](/opt/iflow/TdxQuant/requirements.txt:1)。

结论：

- 不能把 TdxQuant 当成“当前 Linux 进程可直接调用的通用库”
- 必须把它当成 `Windows sidecar / provider / bridge runtime`

## 4.3 走 Windows bridge 模式是现实且合理的

MyStocks 其实已经有相同方向的架构槽位：

- [windows_bridge_adapter.py](/opt/claude/mystocks_spec/web/backend/app/services/windows_bridge_adapter.py:13)
- [DISTRIBUTED_DATA_FACTORY_GUIDE.md](/opt/claude/mystocks_spec/docs/architecture/DISTRIBUTED_DATA_FACTORY_GUIDE.md:1)

这意味着从架构上看，最合理的接法不是：

- 在 MyStocks Linux 进程里直接 import 后硬跑

而是：

- 在 Windows 侧部署 TdxQuant provider
- 通过 CLI/HTTP/JSONL/本地文件协议提供能力
- 由 MyStocks 后端作为 consumer 调用

这与仓库现有的跨系统设计思想是一致的。

## 5. 不建议的接入方式

### 5.1 不建议直接替换现有 TDX 服务

MyStocks 当前已有 TDX quote/kline/index/health 入口，[tdx_service.py](/opt/claude/mystocks_spec/web/backend/app/services/tdx_service.py:21) 和 [tdx.py](/opt/claude/mystocks_spec/web/backend/app/api/tdx.py:1) 已经形成基本 API 面。

如果直接整体替换，会带来几个问题：

- 会冲击现有 API 契约
- 会把 Linux/Windows 运行语义混在一起
- 会让“基础行情服务”和“TongDaXin 特定本地能力”边界变模糊

更好的做法是新增一层：

- `tdxquant_bridge_service`
- `tdxquant_formula_service`
- `tdxquant_subscription_service`
- `tdxquant_block_sync_service`

### 5.2 不建议先接桌面交易

桌面交易能力风险最高，且 OpenSpec 已要求：

- 路径分类
- 风险阈值阻断
- 幂等控制
- 确认策略
- 审计落盘

见 [trading-execution-safety spec](/opt/claude/mystocks_spec/openspec/specs/trading-execution-safety/spec.md:13)。

因此，交易线不应作为第一批集成目标。

### 5.3 不建议让 TdxQuant 反向主导任务与目录治理

TdxQuant 的 `task / report / catalog` 很适合作为本地工具入口，但不应覆盖 MyStocks 现有：

- FastAPI 契约
- 前后端统一 API truth
- 监控、风控、任务编排、前端状态系统

应吸收其任务经验，而不是把 MyStocks 改造成 “TdxQuant 宿主”。

## 6. 建议的接入顺序

### Phase 0: 先做方案，不直接开工

按仓库规范，涉及新能力接入和架构调整，必须先走 proposal-first，[STANDARDS.md](/opt/claude/mystocks_spec/architecture/STANDARDS.md:12)。

建议先产出 OpenSpec 方案，定义：

- TdxQuant 在 MyStocks 中的正式定位
- 是否采用 Windows provider
- 对外 API 契约和错误模型
- 实时传输 canonical path
- 审计与运行边界

### Phase 1: 先接只读能力

优先级建议：

1. `formula`
2. `market/meta/financial/transaction`
3. `block` 读接口

目标：

- 不改交易路径
- 不碰桌面自动化
- 先验证 TongDaXin 数据与公式域是否稳定可消费

### Phase 2: 再接订阅能力

建议形态：

- Windows 侧常驻 `subscription worker`
- 持有 TdxQuant session
- 事件落到 JSONL / Redis / SSE 桥
- MyStocks 后端只消费标准化事件流

这一步比直接把 callback 绑定进 Linux 主进程更稳。

### Phase 3: 接板块与 watchlist 同步

建议先做单向，再做双向：

1. MyStocks watchlist/screener result -> TongDaXin block
2. TongDaXin custom block -> MyStocks monitoring/watchlist

避免一开始就做复杂双向冲突合并。

### Phase 4: 最后接交易辅助执行

只建议作为：

- `experimental`
- `manual-confirmed`
- `broker-specific`

路径存在。

且必须先补：

- 幂等 submission key
- pre-trade risk gate
- 二次确认
- durable audit log
- broker/runtime health check

## 7. 对 TdxQuant 本身的完善建议

如果目标是让 TdxQuant 成为多个上层系统共用的 TongDaXin 中间层，我建议优先补以下内容。

### 7.1 补稳定 JSON 契约

现在 TdxQuant 已经有 `Result` 模型，但还需要进一步统一：

- 各命令 `data` 字段的结构
- 错误码全集
- artifact path 字段命名
- timing 字段命名
- capability version

这样 MyStocks 才能把它当成正式 provider，而不是半结构化脚本输出。

### 7.2 增加 capability doctor / runtime doctor

建议统一提供：

- 当前平台是否支持
- TongDaXin 是否启动
- `TPythClient.dll` 是否可用
- 串口/HID 是否可用
- 窗口探测是否可用
- 哪些 capability 当前可调用

这样上层就能在运行前做能力探测，而不是调用失败后再猜。

### 7.3 尽快把订阅能力产品化

你的功能图已经指出下一步应做 `subscription-watch`。这件事非常关键。

如果未来要服务 MyStocks，这部分最好具备：

- 持久 session 管理
- Ctrl+C 优雅退出
- JSONL 输出
- 状态文件
- stop/status/list
- reconnect policy
- event schema version

### 7.4 强化 query path 与 trade path 的边界

建议在目录、文档、配置上更明确地区分：

- `data/query/formula/block/subscription`
- `desktop trade`

让上层系统可以只接前者，而不默认背负交易自动化复杂度。

### 7.5 提前补交易安全治理

如果未来要进入 MyStocks 主线，桌面交易线必须补：

- execution path classification
- capital/exposure gate
- idempotent submission
- confirmation policy
- durable audit retention

否则最多只能停留在实验工具层。

## 8. 当前建议的最终结论

建议接入，但方式要收敛：

- **接什么**：优先接 `formula`、`subscription`、`block sync`
- **怎么接**：走 `Windows sidecar / bridge provider`
- **不该怎么接**：不直接全量替换 MyStocks 当前 TDX 服务，不先接桌面交易
- **接入顺序**：公式与只读能力 -> 订阅 -> 板块同步 -> 实验性交易辅助

一句话总结：

> TdxQuant 很适合成为 MyStocks 的 TongDaXin 本地能力扩展层，但它应作为 Windows 侧能力提供者被分阶段接入，而不是直接并入当前 Linux 主进程或替代 MyStocks 主架构。

## 9. 审核建议

建议你审核时重点看这几个决策点：

1. 是否认同 TdxQuant 在 MyStocks 中的定位是 `Windows provider` 而不是 `主进程内嵌库`
2. 是否认同第一批只接 `formula / subscription / block`
3. 是否认同交易辅助执行必须后置，并且只放在 `experimental` 路径
4. 是否希望下一步由我基于这份评估继续产出 OpenSpec 接入方案

