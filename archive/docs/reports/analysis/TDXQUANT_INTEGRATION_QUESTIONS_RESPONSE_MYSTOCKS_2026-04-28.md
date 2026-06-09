# TdxQuant 集成问题回复（MyStocks 项目）

**日期**: 2026-04-28
**回复项目**: MyStocks
**回复对象**: `/opt/iflow/TdxQuant/docs/TdxQuant_Integration_Questions.md`
**说明**: 本文仅代表 MyStocks 项目的接入立场，不代表你提到的另一个 Rust 上层项目。Rust 侧问题需由对应项目单独确认。

## 0. 先给结论

MyStocks 认可 TdxQuant 的接入价值，但希望将其定位为：

- `TongDaXin 特定能力 provider`
- `Windows 侧能力扩展层`
- `按能力分阶段接入的外部集成面`

MyStocks 不希望把 TdxQuant 作为：

- MyStocks 主数据服务替代品
- MyStocks 主任务系统替代品
- Linux/WSL 主进程内嵌依赖
- 第一阶段就进入主线的桌面自动化交易引擎

当前更合适的关系是：

- MyStocks 负责策略、风控、投资组合、统一 API、前后端产品层
- TdxQuant 负责 TongDaXin 特有的数据、公式、板块、订阅、客户端联动能力

与该判断相关的本项目现状证据可见：

- 现有 TDX API 主要是 quote/kline/index/health：[tdx.py](/opt/claude/mystocks_spec/web/backend/app/api/tdx.py:1)
- 实时订阅当前仍是模拟/占位实现：[tdx_realtime_manager.py](/opt/claude/mystocks_spec/src/adapters/tdx_realtime_manager.py:1)
- 已存在 Windows provider/bridge 方向的适配槽位：[windows_bridge_adapter.py](/opt/claude/mystocks_spec/web/backend/app/services/windows_bridge_adapter.py:1)
- 当前 trade 路径主要是 runtime/backtest 语义，不是 TongDaXin 桌面执行语义：[trade/routes.py](/opt/claude/mystocks_spec/web/backend/app/api/trade/routes.py:1)

## 1. 对“复用方式”的回复

### 1.1 Python 项目准备怎样调用本项目

MyStocks 的首选方式不是直接在 Linux/WSL 主进程里 `import TdxQuant`，而是：

- 优先方式：`Windows sidecar / provider`
- 首选协议：`service-first` 或 `CLI + JSON`
- 消费位置：MyStocks 后端作为统一 consumer，再向前端输出本项目自己的 API 契约

也就是说，MyStocks 更希望调用的是“稳定协议面”，而不是把 TdxQuant 直接作为主进程内嵌 SDK。

### 1.2 Rust 项目准备怎样调用本项目

对 MyStocks 而言，这一项不适用。MyStocks 当前不是 Rust 主系统。

### 1.3 两个项目是否允许采用不同调用方式

从 MyStocks 的角度看，允许。

我们不要求所有上层项目必须共享同一种调用面。实际更合理的方式通常是：

- Python 项目可消费 service 或 provider
- 非 Python 项目优先消费语言无关协议，例如 `HTTP + JSON`、`CLI + JSON`、`JSONL event stream`

### 1.4 是否接受 Windows sidecar / provider 模式

接受，而且这是 MyStocks 当前最推荐的接入模型。

原因很直接：

- TdxQuant 的 TongDaXin 原生能力依赖 `native Windows Python`
- MyStocks 当前主运行环境更适合保持 Linux/WSL 主进程稳定
- 两边通过 provider 边界解耦，比直接内嵌更容易控制部署、升级、健康探测和失败隔离

### 1.5 是否希望把 TdxQuant 视为补充 TongDaXin 特有能力的 provider

是。

这是 MyStocks 对 TdxQuant 的推荐定位。MyStocks 不希望 TdxQuant 替代：

- 主数据仓储
- 主任务编排
- 主风控
- 主 API 契约

### 1.6 真实调用示例

建议以这种模式理解 MyStocks 的典型调用：

1. MyStocks 后端向 Windows provider 发起公式批量计算请求。
2. TdxQuant 在 Windows 侧调用 TongDaXin 能力执行。
3. TdxQuant 返回结构化 `JSON` 结果，或产出结果文件/事件流。
4. MyStocks 将结果写入自己的数据模型、watchlist、signal 或 API 响应。

优先场景不是“让前端或业务层直接依赖 TdxQuant 输出格式”，而是“由 MyStocks 后端消费并再封装”。

## 2. 对“运行环境与部署约束”的回复

### 2.1 上层项目运行环境

MyStocks 当前更适合按以下模型规划：

- 主系统：Linux/WSL
- TongDaXin 能力执行侧：Windows
- 前端/后端：继续保持当前 MyStocks 自身结构

### 2.2 是否接受 Linux/WSL 主进程 + Windows provider

接受。这是首选模型。

### 2.3 是否允许依赖本地安装的通达信客户端

允许，但前提是：

- 该依赖被明确写入 capability/health 检查
- 不把这类桌面依赖误表述为“跨平台无差别可用”

### 2.4 是否接受 TongDaXin 原生能力只能在 native Windows Python 真正执行

接受。MyStocks 已将这点视为现实约束，而不是阻塞项。

### 2.5 是否允许本项目以常驻进程方式运行

允许，尤其是以下场景：

- 实时订阅 session
- 订阅事件转发
- capability doctor / runtime doctor
- 本地任务调度 worker

### 2.6 是否允许桌面前台自动化

MyStocks 的答复是：

- 默认主线：不依赖桌面前台自动化
- 实验线：可接受
- 条件：必须隔离到 `experimental / manual-confirmed / broker-specific`

### 2.7 是否需要支持远程主机调用本地通达信能力

需要。因为 MyStocks 更适合：

- 远程消费 Windows provider
- 而不是要求主业务进程直接迁移到 Windows

## 3. 对“核心能力优先级”的回复

MyStocks 当前建议的优先级如下：

1. `formula`
2. `market / meta / financial / transaction` 只读能力
3. `realtime subscription`
4. `block` 读写与 watchlist 同步
5. `client warn` 或其他客户端联动
6. `report / task` 类辅助入口
7. `desktop trade automation`

其中真正最想优先落地的是前三项。

MyStocks 接受以下分层顺序：

1. 只读能力优先，例如 `formula / market / meta / financial / transaction`
2. 实时订阅与事件流
3. 板块同步
4. 桌面自动化交易，仅作为 `experimental / manual-confirmed / broker-specific`

## 4. 对“结果契约与输出协议”的回复

### 4.1 返回结构偏好

MyStocks 的偏好非常明确：

- 同步调用结果：`JSON`
- 实时事件流：`JSONL` 或 `SSE`
- `CSV`：可以作为导出 artifact，但不建议作为主集成协议

### 4.2 是否需要固定 schema

需要，而且这项优先级很高。

MyStocks 希望 TdxQuant 在正式对外集成前，固定以下契约：

- success/error 基本包络
- `data` 字段结构
- 错误码
- capability 名称
- capability version
- schema version
- timing 元数据
- artifact path 命名

### 4.3 是否需要统一 metadata

需要。至少建议统一：

- `source`
- `runtime`
- `session_id`
- `profile`
- `started_at`
- `elapsed_ms`
- `capability`
- `capability_version`
- `schema_version`

### 4.4 实时事件流通道偏好

MyStocks 的优先偏好是：

1. `JSONL`
2. `HTTP stream / SSE`
3. `Redis` 作为内部桥接通道

也就是说，外部集成契约优先保持简单、可观察、可落盘；Redis 更适合作为内部实现细节，而不是必须暴露给所有消费方。

### 4.5 是否需要 canonical event envelope

需要。

尤其是订阅事件，建议从一开始就固定：

- event type
- schema version
- subscription session state
- provider instance id
- reconnect metadata
- generated_at

## 5. 对“稳定性与版本治理要求”的回复

MyStocks 需要长期稳定调用契约。

因此我们的立场是：

- 不接受接口名和输出字段长期无版本约束地频繁变动
- 接受演进，但需要版本治理
- 一旦某项 capability 对上层开放，就应给出兼容承诺

建议至少建立两层版本：

- 项目级语义化版本
- capability 级版本标记

对于以下入口，若将来作为集成面开放，建议提供兼容承诺：

- task
- preset
- catalog
- formula
- subscription
- block

## 6. 对“能力探测与健康检查要求”的回复

MyStocks 明确需要 `capability doctor / runtime doctor / health probe`。

这是高优先级需求，不建议后置。

我们希望在调用前就能判断：

- 当前平台是否支持
- TongDaXin 是否已启动
- `TPythClient.dll` 是否可用
- 实时订阅 runtime 是否可用
- 串口/HID 是否可用
- 窗口探测是否可用
- 当前 provider 暴露了哪些 capability

这类能力会直接影响 MyStocks 是否将某条能力暴露给用户或任务编排层。

## 7. 对“性能与吞吐要求”的回复

MyStocks 对性能的看法分两类：

- 低频人工调用：可以容忍一定延迟
- 高频程序调用：必须有明确吞吐与耗时信息

相对更需要关注的程序化场景包括：

- 批量公式计算
- 批量股票查询
- 批量板块同步
- 长驻订阅 session

我们希望 TdxQuant：

- 支持批量接口
- 输出 `elapsed_ms`
- 对订阅链路提供 session 级状态信息
- 在需要时支持简单缓存或长驻 session 复用

## 8. 对“状态、日志与审计要求”的回复

MyStocks 希望 TdxQuant 尽快统一机器可读的状态与日志约定。

优先建议统一：

- 日志目录
- 状态目录
- 结果目录
- 文件命名规则

对于以下场景，建议分别建台账：

- subscription
- report/task
- write/block mutation
- desktop trade

MyStocks 也希望这些能力具备：

- 机器可读日志
- 失败重试所需的上下文
- 对长任务/订阅的恢复信息

## 9. 对“责任边界”的回复

MyStocks 建议边界明确如下。

### 9.1 希望 TdxQuant 负责

- TongDaXin 能力适配
- 标准化查询入口
- 公式能力
- 板块能力
- 订阅能力
- 客户端联动能力
- 桌面自动化交易能力本身

### 9.2 必须留在 MyStocks 的逻辑

- 策略逻辑
- 风控逻辑
- 投资组合管理
- 业务级决策
- 主任务编排
- Web API 契约真相源
- 用户态权限与产品交互
- 多数据源融合后的最终业务语义

### 9.3 其他边界确认

MyStocks 的立场是：

- 是，把 TdxQuant 当成 TongDaXin 特定能力 provider
- 是，不让 TdxQuant 替代 MyStocks 主数据服务和主 API 契约
- 是，接受 `query path` 与 `trade path` 在接入策略上完全分离

## 10. 对“跨语言复用问题”的回复

对 MyStocks 当前版本，这一项没有直接约束，因为 MyStocks 不是 Rust 主系统。

但从上层集成设计角度，MyStocks 仍建议：

- 不要把 Python import 作为唯一正式集成面
- 至少同时维护一个语言无关协议层

更现实的公共协议层通常是：

- `HTTP + JSON`
- `CLI + JSON`
- `JSONL event stream`

## 11. 对“写入类与交易类风险偏好”的回复

MyStocks 对写入类和交易类能力的接受程度是分层的。

### 11.1 可以较早进入接入路线的

- 只读查询
- 公式计算
- 订阅事件流
- 板块读能力

### 11.2 可以接，但应在只读能力之后

- 自定义板块创建、重命名、清空、写入

前提是：

- 有明确 audit
- 有失败反馈
- 有幂等或重复写入防护

### 11.3 不建议早期进入主线的

- `send_warn`
- 桌面自动化交易

### 11.4 桌面交易若将来接入，MyStocks 的底线要求

- 仅进入 `experimental`
- `manual-confirmed`
- `broker-specific`
- 有 `idempotent submission key`
- 有 `pre-trade risk gate`
- 有二次确认
- 有 durable audit log
- 有 broker/runtime health check

## 12. MyStocks 可先确认的最小信息集

如果你们希望先快速形成接入结论，MyStocks 这边已经可以明确给出以下答复：

1. Python 项目准备怎样调用本项目  
   答：优先 `Windows provider`，协议优先 `service-first` 或 `CLI + JSON`。

2. Rust 项目准备怎样调用本项目  
   答：对 MyStocks 不适用。

3. MyStocks 最常用的 3 个能力  
   答：`formula`、`realtime subscription`、`block/watchlist sync`。

4. 期望返回结果协议  
   答：同步 `JSON`，事件流 `JSONL/SSE`，`CSV` 只作为导出。

5. 是否允许本地常驻进程或 daemon  
   答：允许，而且对订阅场景是推荐形态。

6. 哪些逻辑必须留在上层项目  
   答：策略、风控、投资组合、任务编排、主 API 契约、业务决策。

7. 是否接受 `Windows sidecar / provider`  
   答：接受，而且这是首选模型。

8. 是否接受“只读能力 -> 订阅 -> 板块同步 -> 交易实验线”的顺序  
   答：接受。

9. 实时事件流优先走什么通道  
   答：优先 `JSONL`，其次 `SSE`。

10. 是否需要 `capability doctor / runtime doctor`  
   答：需要，且优先级高。

## 13. MyStocks 给 TdxQuant 的额外建议

如果要让 MyStocks 更顺畅地接入，建议 TdxQuant 优先稳定以下几类东西：

1. 固定 `JSON` 结果包络、错误码、schema version、capability version。
2. 正式产品化 `subscription session`，而不是只停留在函数能力。
3. 尽快提供 `capability doctor / runtime doctor / health probe`。
4. 明确分离 `query path` 和 `trade path`。
5. 对交易线尽早补齐风险治理与审计能力。

## 14. 一句话总结

MyStocks 愿意接入 TdxQuant，但接入前提是：

- 把它当作 `Windows 侧 TongDaXin provider`
- 先稳定只读、公式、订阅、板块能力
- 再逐步考虑写入和交易实验线
- 不改变 MyStocks 自身作为上层系统的职责边界
