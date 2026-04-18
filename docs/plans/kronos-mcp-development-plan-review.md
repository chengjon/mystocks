# Kronos MCP Development Plan Review

> 审核对象：`/opt/claude/Kronos/docs/Kronos_MCP_Development_Plan.md`
>
> 立场：从 MyStocks 对接方视角审阅，只关注是否更利于本项目稳定接入、低延迟消费、统一契约和后续扩展。

## 总体评价

该计划的主方向是正确的：

- 采用 `MCP + HTTP` 双入口，但共用同一套 runtime
- 首阶段聚焦 `predict` 与 `encode` 两个核心能力
- 运行时内置批调度、模型管理、错误码和监控
- 明确在线推理与离线训练/回测隔离

这些设计与 MyStocks 当前的对接边界基本一致，可以作为 Kronos 侧实施基线。

但从实际对接和长期稳定性看，仍有 5 个需要尽快收敛的问题。

## 需要修正的关键问题

### 1. `code` 语义不一致

计划中的成功响应使用字符串错误码风格：

- 成功示例里是 `code: "OK"`
- 早期 MyStocks 指引文档里曾出现 `code: 0`
- MyStocks 自身 API 对外返回 `UnifiedResponse` 时，成功通常是 HTTP 语义数值码

建议 Kronos 侧固定为一套规则，不要混用：

- 如果是 Kronos 原生协议，建议成功固定为 `code: "OK"`，失败固定为字符串错误码
- 不建议在 Kronos 协议里再混入 `0/200/"OK"` 三种成功写法

这样 MyStocks 适配层可以稳定做一次映射，不会因为协议漂移增加兼容判断。

### 2. 参数硬限制需与 MyStocks 已实现契约对齐

MyStocks 当前已实现的约束是：

- `candles <= 2048`
- `pred_len <= 120`
- `sample_count <= 10`

如果 Kronos 侧计划后续采用更大的上限，建议仍满足以下原则：

- HTTP 文档里明确“服务端允许上限”
- 同时明确“对接方可采用更保守上限”
- 不要让 MCP 示例、HTTP 文档、运行时代码各写一套不同数字

否则 MyStocks 和其他 AI 工具会出现“请求能不能发”的判断漂移。

## 3. `priority` 在 HTTP 存在，但 MCP 工具签名缺失

当前计划中：

- HTTP `predict` 请求包含 `priority`
- MCP `predict_ohlcv(...)` 工具签名没有 `priority`

这会导致同一个 runtime 的调度语义在两个入口上不一致。

建议二选一：

- 要么两个入口都支持 `priority`
- 要么两个入口都不暴露，由 transport 层内部默认判定

如果保留 `priority`，建议固定枚举：

- `interactive`
- `batch`

并明确默认值。

### 4. `status` 契约还不够强

`GET /v1/kronos/status` 已经提供了基础可观测信息，但对 MyStocks 和其他消费方来说，建议进一步固定：

- `health` 的枚举值
- `loaded_models` 的含义
- `requests_total` 是否自启动累计
- `error_counts` 的统计窗口
- 是否需要区分 `ready` 与 `degraded`

建议补成“可依赖的状态契约”，而不是仅供人读的调试输出。

### 5. 交互请求与批请求的调度规则还不够明确

当前计划提出了：

- `interactive <= 1.5s`
- `batch <= 10s`
- GPU 压力高时先拒绝 `batch`

方向正确，但还缺可落地定义：

- 排队上限是按请求数、令牌数还是显存预算
- `interactive` 是否允许进入微批
- `batch` 被拒绝时返回什么固定错误码
- 调度窗口达到什么条件立即出队
- 当队列堆积时是否跳过缓存查找或切换小模型

建议把这些写成明确运行规则，否则不同开发者实现会出现行为漂移。

## 建议补充

### 1. 把错误结构与 HTTP 状态码映射单独成表

建议 Kronos 侧补一份正式文档，明确：

- 错误码
- HTTP 状态码
- 是否可重试
- 消费方建议动作

这会显著降低 MyStocks、MCP 客户端、其他 AI 工具的适配成本。

### 2. 增加版本兼容策略

建议明确：

- `/v1` 只做向后兼容新增
- 删除字段或重命名字段必须升 `/v2`
- `meta` 新增字段允许，但既有字段不得改语义

### 3. 给 `predict` 和 `encode` 各补一套最小契约测试

Kronos 侧最好直接维护：

- 成功响应 contract test
- 参数错误 contract test
- 超时/不可用 contract test
- 降级态 contract test

这样 MyStocks 只需验证消费契约，不必猜实现。

## 对 MyStocks 的结论

只要 Kronos 侧把以上 5 个点收敛清楚，当前 MyStocks 已实现的适配层可以稳定对接第一阶段能力：

- `POST /v1/kronos/predict`
- `POST /v1/kronos/encode`
- 本地 K 线标准化后转发
- `degraded` / `cached` / `latency_ms` 等状态透传
- 统一错误映射为 MyStocks `UnifiedResponse`

结论：该计划可继续推进，但建议在开发启动前先修订协议细节，优先解决“成功码语义、参数上限、priority 一致性、status 契约、调度规则”这 5 项。
