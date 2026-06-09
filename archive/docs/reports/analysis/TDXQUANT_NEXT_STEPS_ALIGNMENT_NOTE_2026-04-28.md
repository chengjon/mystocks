# TdxQuant Next Steps 边界对齐备忘

**日期**: 2026-04-28
**用途**: 记录 MyStocks 对 `/opt/iflow/TdxQuant/docs/TdxQuant_Next_Steps.md` 的读取结果，并将其作为后续 TdxQuant 接入 MyStocks 时的边界对齐输入。
**状态**: 仅作边界对齐备忘，不构成 MyStocks 的正式实施方案或 OpenSpec 提案。

## 1. 上游文档定位

已阅读：

- [TdxQuant_Next_Steps.md](/opt/iflow/TdxQuant/docs/TdxQuant_Next_Steps.md:1)

该文档是 TdxQuant 在吸收 MyStocks 与 Quantix-Rust 反馈后的上游路线收敛文档。对 MyStocks 而言，可以把它视为：

- TdxQuant 未来一段时间的 canonical capability 边界说明
- 后续接入前提的重要上游输入
- 未来 OpenSpec 接入提案需要参考的外部边界约束

但它不是 MyStocks 自身的实现方案，也不自动替代本仓库中的：

- `architecture/STANDARDS.md`
- `openspec/`
- MyStocks 自身 API / 数据 / 风控 /任务编排真相源

## 2. 已确认可对齐的边界

结合 [TdxQuant_Next_Steps.md](/opt/iflow/TdxQuant/docs/TdxQuant_Next_Steps.md:1) 与前期评估结论：

- [TDXQUANT_INTEGRATION_FEASIBILITY_ASSESSMENT_2026-04-28.md](/opt/claude/mystocks_spec/docs/reports/analysis/TDXQUANT_INTEGRATION_FEASIBILITY_ASSESSMENT_2026-04-28.md:1)
- [TDXQUANT_INTEGRATION_QUESTIONS_RESPONSE_MYSTOCKS_2026-04-28.md](/opt/claude/mystocks_spec/docs/reports/analysis/TDXQUANT_INTEGRATION_QUESTIONS_RESPONSE_MYSTOCKS_2026-04-28.md:1)

MyStocks 后续应按以下边界理解 TdxQuant。

### 2.1 TdxQuant 的正式定位

后续默认将 TdxQuant 视为：

- `Windows 侧 TongDaXin capability provider`
- 通达信特有能力扩展层
- machine-readable contract 提供层

后续默认不将其视为：

- MyStocks 主数据服务替代品
- MyStocks 主任务编排中心
- Linux/WSL 主进程内嵌库
- 当前阶段的主交易执行中心

### 2.2 默认接入模型

后续默认按以下模型对齐：

- `Windows provider` 为主
- `HTTP + JSON / JSONL` 为长期正式集成面
- `CLI + JSON` 仅作为早期 PoC、调试或桥接过渡路径

这意味着未来 MyStocks 若做接入，不应预设：

- 直接 `import TdxQuant` 到 Linux/WSL 主进程
- 以 CLI 文本输出作为长期正式协议

### 2.3 优先能力面

后续默认优先围绕以下能力做接入准备：

1. `formula`
2. `subscription`
3. `block`

并把以下能力视为后续补充：

- `market / meta / financial / transaction` 的 provider-ready 统一输出

### 2.4 不作为当前正式稳定 contract 的能力面

后续默认不把以下入口当作正式稳定集成契约：

- `task`
- `report`
- `catalog`

这些能力可以用于本地工具流或过渡期组织，但不应反向定义 MyStocks 的正式集成协议。

### 2.5 交易线边界

后续默认将 `desktop trade` 视为高风险独立能力线：

- 不进入当前 MyStocks 主执行链路
- 不作为第一批接入目标
- 仅在上游补齐风险治理后，才考虑 `experimental` 级接入

### 2.6 能力可发现性要求

后续默认认为 TdxQuant 需要先具备以下 machine-readable 能力，MyStocks 才适合开始稳定联调：

- `capabilities`
- `health`
- `doctor`
- `preflight`

同时，后续接入应消费其 capability 分级信息，包括：

- 副作用分级：`read_only` / `local_state_mutating` / `live_side_effecting`
- 稳定性分级：`stable` / `beta` / `experimental`

## 3. 对 MyStocks 后续接入的直接影响

基于这次边界对齐，MyStocks 后续若启动正式接入，应默认遵循以下约束。

### 3.1 不再以“直接内嵌库”作为默认假设

后续方案若仍假设：

- Linux/WSL 主进程直接 import TdxQuant
- 主流程依赖 Windows GUI 侧内部细节

则应视为偏离当前已对齐边界，需要重新论证。

### 3.2 接入前置条件应转向“contract 就绪”

后续是否开工，不再主要看“有无原子函数”，而主要看：

- 同步 JSON contract 是否固定
- capability discovery 是否可用
- `formula.screen` 是否 contract-ready
- `subscription-watch` 是否有稳定 JSONL schema
- `block` 写入是否有审计与失败反馈

### 3.3 MyStocks 需要预备的消费面

如果未来开始联调，MyStocks 应优先准备：

- watchlist 导入路径
- JSON contract test
- JSONL 事件消费路径
- capability probe 消费逻辑

### 3.4 交易相关能力继续后置

即使未来接入推进顺利，也不应把交易线纳入第一阶段接入目标。

只有在上游明确补齐以下项后，MyStocks 才适合讨论交易实验线：

- 幂等提交键
- pre-trade risk gate
- 二次确认
- durable audit log
- broker/runtime health check

## 4. 对未来 OpenSpec / 实施方案的影响

如果未来在 MyStocks 中推进 TdxQuant 接入，后续 OpenSpec 或技术方案应显式引用本次边界对齐，并至少满足：

1. 方案默认按 `Windows provider` 模型设计。
2. 方案默认按 `HTTP + JSON / JSONL` 作为长期协议预期。
3. 第一阶段默认只覆盖 `formula / subscription / block`。
4. 默认不把 `task / report / catalog` 当成稳定 contract。
5. 默认不让 `desktop trade` 进入主执行链路。

若后续方案偏离上述前提，应在 proposal 中单独说明偏离原因。

## 5. 当前仍未确定的事项

虽然边界已经明显收敛，但以下事项仍需等真正接入前再定：

- HTTP provider 的具体路由形态
- 身份认证与访问控制方式
- provider 部署拓扑
- contract versioning 细节
- MyStocks 侧适配层的具体模块边界

这些问题属于后续 OpenSpec / 设计阶段处理事项，不在本备忘中展开。

## 6. 一句话结论

从 2026-04-28 起，MyStocks 可将 `TdxQuant_Next_Steps.md` 视为 TdxQuant 对外能力边界的上游对齐依据：

- 先按 `Windows provider`
- 先按 `HTTP + JSON / JSONL`
- 先围绕 `formula / subscription / block`
- 继续隔离 `desktop trade`

后续真正接入时，应在此边界之内推进，而不是回到早期“主进程内嵌”或“交易先行”的旧假设。
