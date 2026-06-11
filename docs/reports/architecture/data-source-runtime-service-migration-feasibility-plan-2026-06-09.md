# 数据源运行时服务化迁移可行性方案

日期：2026-06-09

关联分析文档：

- `docs/reports/architecture/data-source-service-extraction-analysis-2026-06-09.md`
- `docs/reports/architecture/data-source-service-extraction-analysis-review-2026-06-09.md`
- `/opt/claude/eltdx/docs/ELTDX_MCP_ACCESS_MODES.md`

## 结论摘要

本方案建议把 MyStocks 的数据源管理与项目功能底座分开，但不要采用“直接把数据源目录搬进 Docker”的方式。正确做法是先定义主后端与数据源运行时之间的稳定 seam，再用不同 adapter 支撑本地、远程、mock、诊断工具和实时流。

核心设计：

- 主后端继续承担产品 API、认证、权限、`UnifiedResponse`、OpenAPI、前端兼容路径、策略、风控、交易和看板业务编排。
- 新增 `openstock` 数据源运行时，承担 provider adapter、registry、路由、健康检查、限流、缓存、熔断、调用指标和实时行情源订阅。
- `openstock` 作为迁出后的独立方案/仓库名，目标本地目录为 `/opt/claude/openstock`，目标私库为 `http://192.168.123.104:3001/john/openstock.git`。
- 主后端对外保留 `/api/v1/data-sources*`，先作为 facade/proxy，避免前端和第三方调用方跟随迁移。
- REST/OpenAPI 用于控制面和 pull 型数据。
- WebSocket 用于实时行情订阅。
- SSE 仅用于浏览器单向状态流。
- MCP 仅作为可选 agent/admin/diagnostics 工具面，不进入高频行情和批量 K 线热路径。
- `DataSourceClient` 必须先形成可测试 interface contract，再进入 remote/Docker 实现。
- 迁移关系上，本方案依赖并接续 active 的 `optimize-data-source-v2`，不替代其已沉淀的数据源治理能力。

最关键的原则：

> 这不是“把数据源搬进 Docker”，而是先把主后端和数据源之间的 interface 变深。只要 `DataSourceClient` 这个 seam 定得好，后面 local、remote、mock、MCP-admin、WebSocket-stream 都只是 adapter；业务功能底座不会再被 provider 细节拖着走。

## 1. 怎么拆，功能如何分布

### 1.1 拆分目标

当前数据源能力仍然和主后端运行时耦合：

- 主后端内直接存在 provider adapter 调用链。
- 数据源 registry、priority、mode、health、cache 等配置分散在多个文件和运行路径。
- provider 失败、凭证、限流、熔断和缓存策略容易穿透到业务后端。
- 主后端既要服务前端业务，又要处理外部数据源不稳定性。

拆分目标是：

- 让主后端专注业务功能底座。
- 让数据源运行时专注 provider 访问和数据源治理。
- 保持前端和外部调用方已有 API 路径稳定。
- 通过 Docker 让数据源运行时独立部署、独立监控、独立恢复。

### 1.2 推荐模块分布

| 模块 | 保留或承接功能 | 不应该承接 |
|---|---|---|
| `mystocks-backend` 主后端 | 产品 API、认证、权限、`UnifiedResponse`、OpenAPI、前端兼容路径、策略、风控、交易、看板业务编排 | 具体数据源 provider 调用、provider 凭证、provider 限流、provider 熔断 |
| `openstock` 数据源运行时 | registry、路由选择、provider adapter、凭证、限流、缓存、熔断、健康检查、调用指标、实时行情源订阅 | 用户业务、前端页面契约、策略决策、交易执行、业务数据归属 |
| DB、Redis、TDengine | PostgreSQL 存 registry/version/call history，Redis 存短 TTL 快照、分布式限流、stream 状态，TDengine/PostgreSQL 继续存市场和业务数据 | 不承担 provider 调用逻辑 |
| MCP 工具面，可选 | agent/admin 诊断：列数据源、测 endpoint、解释路由、reload registry、查健康 | 高频行情、批量 K 线、策略执行热路径 |

### 1.3 推荐 seam：`DataSourceClient`

核心 seam 应该放在主后端中：

```text
业务代码 / FastAPI routes
        |
        v
DataSourceClient interface
        |
        +-- LocalDataSourceClient     # 迁移前，调用现有 DataSourceManagerV2
        |
        +-- RemoteDataSourceClient    # 迁移后，REST/WS 调 openstock
```

这样拆的好处：

- 调用方只学习一个 `DataSourceClient` interface。
- 今天 interface 背后是本地 `DataSourceManagerV2`。
- 明天可以换成远程 Docker 服务。
- 业务代码不需要大面积知道 provider、registry、handler、熔断器、限流器和远程协议细节。

#### 1.3.1 `DataSourceClient` interface contract

审核意见里最关键的问题是：`DataSourceClient` 不能只是一张图里的名字。它必须先成为可测试、可替换、可审计的契约，否则 local 到 remote 迁移时会把 provider 细节原样搬进 HTTP。

建议最小能力面：

| 能力 | 语义 | 热路径要求 |
|---|---|---|
| `resolve_route(request)` | 返回本次请求选中的 provider/endpoint、fallback 候选和 route reason | 快，不能触发慢 provider 请求 |
| `fetch_snapshot(request)` | 拉取单个 symbol/category 的一次性快照 | 必须有 timeout、freshness 和 typed error |
| `fetch_batch(request)` | 批量拉取历史/财务/参考数据 | 可异步化或分页，不能阻塞主后端无限等待 |
| `test_endpoint(endpoint_name)` | 诊断某个 endpoint 是否可用 | admin/diagnostics，不进入业务热路径 |
| `get_source_health(filter)` | 查询 provider、endpoint、category 健康状态 | 可缓存，返回观测指标 |
| `reload_registry(version)` | registry reload/version 切换 | 写操作必须有审计和回滚语义 |
| `subscribe_quotes(request)` | 仅用于 stream client，建立行情订阅 | WebSocket 专用，不走 MCP |

契约不变量：

1. 每个成功响应必须携带 `source`、`endpoint_name`、`route_decision_id`、`request_id`、`exchange_time`、`received_at`、`staleness_ms`、`cache_state`、`quality_flags`、`latency_ms`。
2. 陈旧数据不能静默返回。若允许降级返回 stale cache，必须标记 `cache_state=stale`，并带 `staleness_ms` 与降级原因。
3. 错误必须 typed，至少区分 `ProviderUnavailable`、`ProviderTimeout`、`RateLimited`、`CircuitOpen`、`RegistryNotFound`、`InvalidRequest`、`DataQualityFailed`。
4. 每次调用必须有明确 timeout budget；远程 client 不允许无限等待 provider。
5. 缓存语义必须显式：`cache_state=fresh|stale|miss|bypass`，调用方可以声明 freshness requirement。
6. registry/config 写操作必须通过运行时 owner 的 config API，不允许 fetch 类接口顺手改 provider 配置。
7. `LocalDataSourceClient` 与 `RemoteDataSourceClient` 必须跑同一套 contract tests。主后端业务代码只依赖契约，不依赖具体 provider adapter。

### 1.4 具体功能归属

| 功能 | 推荐归属 |
|---|---|
| `/api/v1/data-sources` 对外路径 | 主后端保留，先做 facade/proxy |
| `/api/v1/data-sources/config` 写操作 | 主后端保留外部契约，但内部代理给数据源运行时 |
| registry 真相源 | 尽早定为 PostgreSQL；YAML 只做 bootstrap/seed/emergency fallback |
| `config/data_sources.json` | 保留为主后端“业务模块 mock/real 模式”配置，不再承担 provider registry |
| `adapter_priority_config.yaml` | 迁移后退役，优先级进入 registry/routing policy |
| provider adapter | 数据源运行时 |
| health/cache/circuit breaker/rate limit | 数据源运行时 |
| strategy/risk/trade/portfolio | 主后端 |
| realtime market channel | 数据源运行时产出，主后端可转发到现有 `/ws/events` |

### 1.5 registry ownership 必须先定

迁移前最重要的设计决定是 registry ownership。它不能拖到最后。

建议在 Phase 0 就明确：

```text
PostgreSQL registry/version history = 唯一运行时真相源
YAML registry = 初始化 seed + 离线恢复材料
主后端 config API = 对外 facade
数据源运行时 = registry 写入、reload、route、health 的实际 owner
```

这样可以避免新增 Docker 服务后又多出一个平行 registry，造成更多真相源。

### 1.6 runtime state ownership matrix

这里必须把“数据源运行态”和“业务数据存储”拆清楚。拆服务不是迁移数据库，也不是把市场数据仓库搬走；第一阶段只迁移 provider 访问、路由和运行治理。

| 状态/数据 | 推荐 owner | 存储/生命周期 | 说明 |
|---|---|---|---|
| provider registry | 数据源运行时 | PostgreSQL 为运行时真相源；YAML 为 seed/fallback | 主后端只保留 facade，不再直接维护 provider registry |
| registry version history / rollback | 数据源运行时 | PostgreSQL | config 写操作必须审计、可回滚 |
| route decision history | 数据源运行时 | PostgreSQL 或短期日志 + metrics | 用于解释路由、回放故障、观察 fallback |
| provider health | 数据源运行时 | 进程内状态 + metrics；多实例时可接 Redis | 由 provider probe、熔断器和请求结果共同更新 |
| cache | 数据源运行时 | L1 memory + 可选 Redis L2 | 主后端不再自建 provider cache 主链 |
| rate limit state | 数据源运行时 | 单实例内存；多实例时 Redis namespace | 每个 provider/endpoint 独立预算 |
| circuit breaker state | 数据源运行时 | 单实例内存；多实例时可外置共享摘要 | 不能由 MCP 或主后端绕过 |
| metrics | 数据源运行时 emit；主后端可聚合/代理 | Prometheus `datasource_*` | latency、cache hit、fallback、rate limit、circuit open、quality failure |
| provider call audit/cost | 数据源运行时 | PostgreSQL/Prometheus，按实际需要取舍 | 用于成本、配额、问题追踪 |
| tick/minute/daily/indicator/reference market data | 现有数据仓库 owner | TDengine/PostgreSQL 现有路径 | 第一阶段不迁移业务数据仓库 |
| strategy/risk/trade/portfolio/user data | 主后端/现有业务域 | PostgreSQL/现有路径 | 不进入数据源运行时 |

因此，`openstock` 的职责是“取得、治理、解释数据源访问”，不是成为新的市场数据仓库或策略执行引擎。

## 2. 服务如何分层，保证速度与稳定

### 2.1 数据源运行时内部层次

`openstock` 内部建议按 5 层组织，不要让 REST handler 直接调用 AkShare、TDX 或 TuShare。

```text
Transport Layer
  REST / WebSocket / optional MCP

Application Layer
  DataSourceRuntime
  FetchSnapshot / FetchBatch / SubscribeQuotes / TestEndpoint / ReloadRegistry

Routing Layer
  RegistryReader
  RoutePolicy
  EndpointHealth
  Cost/Freshness/Latency scoring

Provider Adapter Layer
  AkShareAdapter
  TdxAdapter
  TuShareAdapter
  BaoStockAdapter
  BYAPIAdapter
  CustomerAdapter

Resilience + State Layer
  L1 memory cache
  Redis L2 cache
  Circuit breaker
  Adaptive rate limiter
  Bulkhead/concurrency limits
  Prometheus metrics
  Call history/version history
```

### 2.2 协议分工

协议不是单选，而是按数据类型和使用场景分层。

| 协议 | 推荐用途 | 不推荐用途 |
|---|---|---|
| REST/OpenAPI | registry、health、route selection、测试 endpoint、历史/财务/参考数据 fetch、batch fetch | 高频实时行情推送 |
| WebSocket | realtime quote、tick-like update、watchlist 订阅、strategy universe 订阅 | 大批量历史数据下载 |
| SSE | 浏览器单向状态流：同步进度、健康退化、dashboard 更新 | 双向订阅、高频行情主链路 |
| MCP Streamable HTTP | agent/admin 诊断工具：列数据源、解释路由、reload、测 endpoint | 高频行情、批量 K 线、策略执行热路径 |

### 2.3 借鉴 ELTDX 的 MCP 接入形态

参考 `/opt/claude/eltdx/docs/ELTDX_MCP_ACCESS_MODES.md` 后，本方案需要明确一个额外原则：

> MCP 的传输形态和数据服务能力不是同一个维度。MCP 可以作为工具入口，但不应成为 MyStocks 数据源运行时的能力底座。

ELTDX 可借鉴的是 access mode 分层，而不是把数据服务等同于 MCP 服务：

| MyStocks access mode | 推荐用途 | 强约束 |
|---|---|---|
| stdio MCP | 本地 agent/admin 诊断：列数据源、测 endpoint、解释路由 | 低频、本机、只返回摘要 |
| standalone MCP over Streamable HTTP/SSE | NAS/Docker/内网远程 AI 工具入口 | 只调用 `DataSourceClient` 或远程 REST，不维护 provider 连接池、缓存、熔断、限流 |
| mounted MCP | 挂在完整 `openstock` 内的诊断入口 | 必须复用同一个 `DataSourceRuntime`，不能绕过 runtime 直连 provider |

目标结构应写成：

```text
openstock = REST/OpenAPI + WebSocket data runtime + optional MCP diagnostics
```

实现顺序也应明确：REST/pull 和 WebSocket/realtime 稳定后，再进入 MCP。MCP 工具只覆盖 `list_data_sources`、`get_data_source_health`、`test_data_source_endpoint`、`explain_route_decision`、`reload_data_source_registry` 这类诊断和管理动作，不返回大批量行情、K 线或财务数据。

若保留 SSE compatibility，需要把部署约束写入 Docker / reverse proxy / OpenSpec：保持 stream 打开、关闭代理 buffering、`/sse` 与 `/messages` 路由到同一后端实例或外置 session state。若客户端支持 Streamable HTTP，应优先使用 Streamable HTTP，SSE 只作为兼容模式。

### 2.4 速度保障

#### 2.4.1 热路径不用 MCP

MCP 只做诊断和运维工具。行情、K 线、批量数据不要走 MCP。

当前官方 MCP 标准 transport 是 `stdio` 和 `Streamable HTTP`，但 MCP 仍然不适合作为量化系统高频数据热路径。ELTDX 的经验也说明：standalone HTTP MCP 是传输升级，不是数据能力升级；分时、逐笔、行情推送这类热数据应由完整 server runtime 承担。

#### 2.4.2 REST 只处理 pull 型数据

适合 REST 的数据：

- 日线 K 线
- 分钟 K 线
- 财务数据
- 参考数据
- 资金流向
- registry 查询
- health 查询
- route selection
- endpoint test

对大数据量结果，先支持：

- 分页
- 时间窗口
- batch request
- gzip 压缩
- 明确 timeout budget

后续如果 JSON 序列化成为瓶颈，再考虑：

- NDJSON
- Arrow
- Parquet
- 压缩二进制 payload

不建议第一阶段直接引入复杂二进制格式。

#### 2.4.3 实时行情走 WebSocket

`REALTIME_QUOTES`、tick-like updates、watchlist 订阅应走 WebSocket。

消息至少包含：

- `symbol`
- `source`
- `endpoint_name`
- `exchange_time`
- `received_at`
- `sequence`
- `staleness_ms`
- `quality_flags`

#### 2.4.4 主后端不要同步等慢 provider

外部 provider 慢时，主后端不应被拖死。

推荐策略：

- 有缓存快照时优先返回缓存快照。
- 返回结果必须标记 freshness/staleness。
- 必须拉取新数据时设置明确 timeout。
- 大任务或慢任务走异步 job。
- provider 失败返回 typed error，不返回随机 exception 文本。

#### 2.4.5 两级缓存

推荐缓存结构：

```text
L1 memory cache
  进程内短 TTL
  适合热点 quote/snapshot

Redis L2 cache
  多实例共享
  主后端快速读取
  服务重启后保留短期快照
```

缓存响应必须带 metadata：

- 数据源
- endpoint
- 生成时间
- 接收时间
- TTL
- 是否 stale
- 缓存层级

#### 2.4.6 provider 独立限流、熔断和并发池

不同 provider 的稳定性和成本不同：

- AkShare 慢不应该拖死 TDX。
- TuShare token 问题不应该影响 BaoStock。
- BYAPI 额度不足不应该影响本地 mock 或 TDX。

因此需要 provider-level bulkhead：

- 每个 provider 独立并发池。
- 每个 provider 独立超时。
- 每个 provider 独立失败计数。
- 每个 provider 独立熔断状态。
- 每个 provider 独立恢复探测。
- 每个 provider 独立 rate limit。

注意：当前 V2 文档显示 `AdaptiveRateLimiter` 尚未默认接入 `DataSourceManagerV2` 主出站链。所以限流应写成迁移目标能力，不应写成已有主链能力。

### 2.5 稳定性保障

#### 2.5.1 健康检查分层

不要用一个 health 判断所有东西。

推荐分层：

```text
/health/live
  服务进程活着即可

/health/ready
  registry、Redis、PostgreSQL 等基础依赖可用

/sources/{name}/health
  provider 级健康
```

provider 失败不应该直接让整个服务 not ready。否则一个外部 provider 挂了，容器编排系统可能反复重启整个数据源服务，反而降低稳定性。

#### 2.5.2 主后端 contract 稳定

迁移期间，主后端对外 contract 必须保持稳定：

- `/api/v1/data-sources*`
- `UnifiedResponse`
- OpenAPI
- auth 行为
- error code
- status code
- request body
- response envelope
- version history
- rollback
- reload

这意味着主后端可以代理到远程数据源服务，但不能让前端和第三方调用方感知内部迁移。

#### 2.5.3 数据源 runtime contract 稳定

数据源运行时对主后端的 interface 必须稳定：

- fetch 返回 normalized records + metadata。
- route decision 始终可解释。
- stale data 必须标记，不能静默当作 fresh。
- provider failure 返回 typed error。
- config writes 必须 versioned。
- rollback 必须可验证。
- health 必须按 provider 分层。

#### 2.5.4 实时流必须定义失败和重连语义

WebSocket 不只是能连上就行。实时流需要明确：

- 每个 symbol/source 内消息有序。
- 每个 update 带 source timestamp 和 receive timestamp。
- reconnect 后返回 latest snapshot 或从已知 sequence 恢复。
- slow consumer 被降级或断开。
- stale quote 被标记。
- duplicate/out-of-order message 可处理。
- market close/open 状态明确。

## 3. 迁移路径

推荐迁移路径是：先 seam，后 Docker；先 REST/pull，后 WebSocket/realtime；先一个 provider/category，后全量数据源。

### Phase 0：OpenSpec 与关键决策

先创建 OpenSpec change，例如：

```text
extract-data-source-runtime-service
```

建议 affected specs：

- 新增 `data-source-runtime-service`
- 修改 `containerized-runtime-deployment`
- 修改 `data-sources`
- 如 pilot 改变市场数据行为，再修改 `market-data`

不要把 `03-adapter-pattern` 作为 provider runtime 的主规格，除非 delta 明确是前端 ViewModel adapter。当前 `03-adapter-pattern` 更偏前端 API-to-UI 数据转换，不适合承载后端 provider runtime。

Phase 0 必须先定：

1. registry 真相源：建议 PostgreSQL，YAML 只做 seed/fallback。
2. 主后端 facade：`/api/v1/data-sources*` 外部契约不变。
3. 数据源运行时职责：provider 调用、路由、健康、限流、缓存、熔断、metrics。
4. 首个 pilot：建议选 AkShare REST/pull 类 category，不要第一步就做 realtime。
5. MCP access modes：MCP 是诊断/工具入口，不是数据服务底座；区分 stdio MCP、standalone remote MCP、mounted MCP。
6. active OpenSpec 对齐：明确 `extract-data-source-runtime-service` 与未完成的 `optimize-data-source-v2` 是依赖、接续还是替代关系。

#### Phase 0.1：与 `optimize-data-source-v2` 的关系

推荐关系是“依赖并接续”，不是替代。

截至本方案日期，`openspec/changes/optimize-data-source-v2/tasks.md` 仍处于 active 状态，任务进度为 `235/253`，尚未 archive。它已经沉淀了 SmartRouter、CircuitBreaker、metrics、batch processing、fetcher bridge、runtime config 等数据源治理能力；本迁移方案应把这些能力作为本地运行时事实基础，再抽 `DataSourceClient` 和远程服务边界。

进入 `extract-data-source-runtime-service` proposal 前，应先完成一次 V2 对齐清单：

| 对齐项 | 处理口径 |
|---|---|
| SmartRouter / route decision | 作为 `DataSourceClient.resolve_route()` 的本地实现来源；补 route decision metadata contract |
| CircuitBreaker / RateLimit / Metrics | 作为数据源运行时内部能力；远程服务不得重新发明第二套不兼容状态 |
| BatchProcessor / fetcher bridge | 作为 `fetch_batch()` 和 provider bridge 的候选实现；确认是否适合跨进程调用 |
| registry/config runtime | 作为 Phase 0 ownership 决策的事实输入；不能继续产生 YAML/PostgreSQL 双真相源 |
| grey/production validation 尾项 | 按“阻塞迁移”与“可并行验证”分类，不得在未 archive 前宣称 V2 已生产验收完成 |

若 V2 中某项能力已经实现但缺少生产证据，本方案不回退设计；只把它列为 Phase 1/2 的 verification prerequisite。

#### Phase 0.2：`STANDARDS.md` 治理对齐

本方案属于架构拆分和服务边界变更，必须走 proposal-first，而不是直接改实现。执行口径：

1. 先写 OpenSpec change 和验收矩阵，再改代码。
2. 兼容层只能薄封装，不能长期形成 local/remote 两套主实现。
3. registry、runtime state、business storage 必须各有唯一 owner。
4. 旧路径退役必须有单独收口证据；不得用“搜不到引用”直接删除配置、shim、legacy wrapper。
5. 每个阶段必须有 rollback path、exit criteria 和可执行验证命令。
6. 若涉及删除/退役、兼容层收敛或批量迁移，另按 `architecture/STANDARDS.md` 与治理指南执行审批。

### Phase 1：进程内先抽 `DataSourceClient`

目标：不加 Docker，也能把调用方从 manager 细节里解耦出来。

新增 seam：

```text
DataSourceClient interface
LocalDataSourceClient -> DataSourceManagerV2
```

主后端和相关业务代码改为依赖 `DataSourceClient`，而不是直接依赖：

- `DataSourceManagerV2`
- `get_best_endpoint()`
- `handler.py:_call_endpoint()`
- 具体 provider adapter
- provider-specific config

验收：

- 现有 `/api/v1/data-sources*` 行为不变。
- config create/update/delete/version/rollback/reload 行为不变。
- Local client contract tests 通过。
- GitNexus impact 只落在预期文件。

### Phase 2：新增 `openstock` 容器，但前端路径不变

目标：数据源运行时服务化，主后端仍是对外 facade。

新增服务：

```text
openstock
```

建议 REST endpoints：

```text
GET  /health/live
GET  /health/ready
GET  /sources
GET  /sources/{endpoint_name}
POST /sources/{endpoint_name}/test
POST /registry/reload
GET  /routing/best
POST /data/fetch
POST /data/batch
```

主后端新增 adapter：

```text
RemoteDataSourceClient -> HTTP call openstock
```

通过配置切换：

```text
DATA_SOURCE_CLIENT_MODE=local | remote
```

验收：

- local/remote contract parity tests。
- `/api/v1/data-sources/config` 写操作兼容测试。
- Docker smoke 包含 data-source ready。
- 失败时可切回 local mode。
- 数据源服务失败不会导致主后端整体不可用。

### Phase 3：迁移首个真实数据源 category

推荐 first pilot：

```text
AkShare + 一个 REST/pull category
```

理由：

- 当前 registry 主要是 AkShare `api_library`。
- 这条链最接近现有 `DataSourceManagerV2`。
- 可以先验证服务拆分，不同时引入 WebSocket 生命周期问题。
- AkShare category 比全量数据源更容易控制回归范围。

不建议第一批迁移：

- 所有 AkShare 52 个 endpoint。
- 所有 7 类 provider。
- TDX realtime。
- WebSocket market stream。

验收：

- route decision 可解释。
- provider 失败触发熔断。
- cache hit/miss 有指标。
- 返回数据带 source、endpoint、latency、freshness metadata。
- 主后端 API 响应仍符合 `UnifiedResponse`。
- provider 慢时主后端不会无限等待。

### Phase 4：实时行情 WebSocket pilot

在 REST/pull 稳定后，再做 realtime。

数据源服务提供：

```text
openstock /ws/market
```

消息类型：

```text
subscribe
unsubscribe
snapshot
quote.update
heartbeat
error
```

主后端可以先作为转发者，把数据源服务的 market stream 转到现有 `/ws/events` 的 `events:market` channel。这样前端不用马上重写。

验收至少包括：

- subscribe/unsubscribe。
- 首次 snapshot。
- update sequence。
- stale quote 标记。
- reconnect 行为。
- slow consumer 处理。
- duplicate/out-of-order 处理。
- market close/open 状态。

### Phase 5：增加 MCP 工具入口

在 REST/pull 和 WebSocket realtime 都稳定后，再增加 MCP 工具入口。

推荐分两类：

```text
standalone MCP
  只注册少量高价值、低风险工具
  list_data_sources
  get_data_source_health
  test_data_source_endpoint
  explain_route_decision
  reload_data_source_registry

mounted MCP
  挂在 openstock /mcp
  复用 DataSourceRuntime
  可暴露更完整诊断工具
```

standalone MCP 的定位是轻量远程 AI 工具，不是完整数据源服务。它可以通过 `RemoteDataSourceClient` 调用 `openstock`，但不应自己维护完整 provider 连接池、缓存、熔断和限流。

mounted MCP 的定位是完整数据源运行时的 AI 工具入口。它必须复用 `DataSourceRuntime`，不能绕过 runtime 直接调用 provider adapter。

验收至少包括：

- stdio MCP 可本地列数据源和测 endpoint。
- standalone MCP 可远程查 health、解释 route decision。
- mounted MCP 复用同一份 registry、metrics、cache 和 circuit breaker。
- MCP 工具返回摘要和诊断结果，不返回大批量行情或财务数据。
- SSE compatibility 如启用，代理层满足 session 粘性和 buffering 约束。

### Phase 6：收敛旧路径

remote 模式稳定后，再退役旧路径。

建议收口：

- `adapter_priority_config.yaml` 迁入 registry/routing policy。
- YAML registry 从运行时真相源降级为 seed/fallback。
- 旧 `DataSourceManager` 只保留兼容 wrapper，最终退役。
- `DataAdapter`/split adapters 中重复 provider 调用路径逐步收口。
- OpenSpec archive 已完成 change。

退役前必须满足：

- remote mode 稳定通过 contract tests。
- rollback/version/reload 已覆盖。
- provider health 和 metrics 已进入运行门禁。
- Docker smoke 通过。
- 主后端 public API parity 通过。
- 没有新增平行 registry 真相源。

## 4. 建议验收矩阵

以下命令是 proposal/implementation 的验收目标；标注为“新增”的测试文件需要在对应阶段创建。此表不表示当前仓库已经存在这些新增测试。

| 阶段 | 必跑命令 | 新增或重点测试 | 验收口径 |
|---|---|---|---|
| Phase 0 | `openspec validate extract-data-source-runtime-service --strict`；`openspec list` | OpenSpec proposal/spec delta | proposal 通过 strict validate；明确 V2 关系、registry owner、first pilot、rollback path |
| Phase 1 | `pytest tests/unit/test_smart_router.py tests/unit/test_smart_router_integration.py tests/unit/test_metrics.py tests/unit/test_data_source_metrics_integration.py src/governance/tests/test_fetcher_bridge.py tests/integration/test_batch_processing.py tests/unit/adapters/test_runtime_data_source_regressions.py -q --no-cov`；`pytest tests/unit/data_source/test_data_source_client_contract.py -q --no-cov` | 新增 `tests/unit/data_source/test_data_source_client_contract.py` | local client 满足响应 metadata、typed error、timeout、cache_state、config write boundary；现有 V2 主链证据不回退 |
| Phase 2 | `pytest tests/integration/data_source/test_remote_data_source_client_contract.py tests/api/file_tests/test_data_source_config_api.py tests/api/file_tests/test_data_source_registry_api.py -q --no-cov`；`bash scripts/run_data_source_runtime_smoke.sh` | 新增 remote contract parity、config facade parity、Docker smoke | local/remote 可切换；主后端 facade 兼容；数据源服务失败不拖垮主后端 |
| Phase 3 | `pytest tests/integration/data_source/test_akshare_runtime_pilot.py -q --no-cov` | 新增 AkShare REST/pull pilot contract | route 可解释；provider timeout/fallback/circuit/cache/metrics 可观测；返回数据含 freshness/source/latency |
| Phase 4 | `pytest tests/integration/data_source/test_market_stream_contract.py -q --no-cov` | 新增 WebSocket stream contract | subscribe/unsubscribe、snapshot、sequence、stale、reconnect、slow consumer、duplicate/out-of-order、market close/open 语义稳定 |
| Phase 5 | `pytest tests/integration/data_source/test_mcp_access_modes.py -q --no-cov` | 新增 MCP access modes contract | stdio/standalone/mounted 边界清楚；mounted MCP 复用 `DataSourceRuntime`；MCP 不返回大批量行情或财务数据；SSE compatibility 满足部署约束 |
| Phase 6 | `pytest tests/integration/data_source/test_data_source_public_api_parity.py -q --no-cov`；`openspec validate extract-data-source-runtime-service --strict` | 新增 public API parity 与旧路径退役检查 | 无平行 registry 真相源；旧 priority/config/manager 路径有退役证据；满足 archive 前验收 |

## 5. 风险与处理

| 风险 | 处理 |
|---|---|
| registry 真相源继续分裂 | Phase 0/1 先定 ownership，PostgreSQL 作为运行时真相源，YAML 降级为 seed/fallback |
| 主后端 API 兼容破坏 | 保留 `/api/v1/data-sources*` facade，增加 public API parity tests |
| provider 拖慢主后端 | 主后端只调用 `DataSourceClient`，设置 timeout，优先返回缓存快照，慢任务异步化 |
| `DataSourceClient` 变成浅 wrapper | Phase 1 先写 interface contract tests，强制响应 metadata、typed error、timeout、cache_state、config write boundary |
| runtime state 与业务数据仓库混淆 | 使用 ownership matrix：数据源运行时只管 provider 访问治理；TDengine/PostgreSQL 业务数据仓库不在第一阶段迁移 |
| 与 `optimize-data-source-v2` 冲突或重复造轮子 | Phase 0.1 定义为依赖并接续；V2 active 尾项按 verification prerequisite 处理 |
| Docker 服务变成浅 pass-through | 用 `DataSourceRuntime` 隐藏路由、缓存、熔断、限流、metrics，不把内部 handler 直接暴露给调用方 |
| realtime 一开始过复杂 | 第一 pilot 选 AkShare REST/pull，WebSocket 放到 Phase 4 |
| rate limit 被误认为已落地 | 明确写成目标能力，先用 mock provider 做限流测试 |
| MCP 被滥用到热路径 | MCP 仅做 diagnostics/admin，行情和批量数据走 REST/WebSocket |
| standalone MCP 变成第二套数据源运行时 | standalone MCP 只调用 `DataSourceClient` 或远程 REST，不维护完整 provider 连接池、缓存、熔断和限流 |
| SSE compatibility 被代理层打散 session | 如启用 SSE transport，要求 `/sse` 和 `/messages` 同实例路由或外置 session state，并关闭代理 buffering |
| 绕过 `STANDARDS.md` 直接开工 | Phase 0.2 写入 proposal-first、owner 唯一、兼容层薄封装、退役单独审批、阶段验收命令 |
| 验收停留在概念层 | 第 4 节把每个 phase 绑定到命令和新增测试文件，OpenSpec proposal 需继承这些验收项 |

## 6. 推荐审核结论

建议批准进入 OpenSpec proposal 编写，但仍不建议直接实现。

本版方案已在可行性层补齐以下审核项：

1. `DataSourceClient` interface contract 与契约不变量。
2. runtime state ownership 与 business storage ownership 的拆分矩阵。
3. 与 active `optimize-data-source-v2` 的“依赖并接续”关系。
4. ELTDX MCP access modes 的可借鉴边界：MCP 是诊断工具面，不是数据服务底座。
5. `STANDARDS.md` 治理对齐：proposal-first、owner 唯一、兼容层薄封装、退役单独审批。
6. 每个 migration phase 的可执行验收命令和新增测试目标。

进入实现前，仍需要把这些内容正式落入 `extract-data-source-runtime-service` OpenSpec change，并由用户审核 affected specs、阶段范围、first pilot 和 rollback path。实现阶段应优先做 Phase 1 的进程内 `DataSourceClient`，确认本地契约稳定后再启动 Docker/remote 服务化。
