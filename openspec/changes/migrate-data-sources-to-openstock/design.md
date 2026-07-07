## Context

OpenStock 已作为 NAS Docker 服务运行(`openstock:nas`,端口 8040→8000,API key 鉴权),在内部封装了 eltdx/baostock/akshare/zzshare 四类 provider,对外暴露 70 个 source-neutral data_category,自带 5 秒 TTL 缓存、熔断器、自动 failover、字段 normalize、`X-API-Key` 鉴权。本项目历史上有 39+ 个文件直接 import 上述四个 SDK,自建 30+ Adapter,逻辑重复且散乱。

约束:
- 不能一次性全量替换 — Adapter 类签名被 70+ 处调用,级联修改风险高
- 必须可分域验证 — 每个业务域独立 PR + smoke test
- OpenStock 不覆盖的盲区(期货/融资融券/沪深交易所统计)需要显式落档,交 OpenStock 项目补全
- 期货/期权功能按用户决策暂不实现

利益相关方:
- 消费端:`web/backend/app/services/` 各业务 service、`scripts/` 数据同步脚本、`tests/`
- 提供端:OpenStock NAS 实例(192.168.123.104:8040)

## Goals / Non-Goals

**Goals**:
- 所有 A 股市场数据/基本面/财务/公告/资金流/板块/龙虎榜/涨停复盘/跨市场(HK/US/ETF/基金)数据通过 OpenStock 单一网关获取
- Adapter 类签名稳定,消费端代码零改动
- 配置(`OPENSTOCK_BASE_URL` / `OPENSTOCK_API_KEY`)从 `.env` 注入,零硬编码
- 删除 4 个外部 SDK 依赖,减少 requirements 体积与版本漂移风险

**Non-Goals**:
- **不**实现 OpenStock client 的复杂调度逻辑(重试/熔断/缓存)— OpenStock 已内置,本项目 client 只做超时与单次重试
- **不**改造 TDengine/PostgreSQL 入仓路径 — OpenStock 是数据网关,不入仓,消费端自行写库
- **不**实现期货/期权/交易执行 — 用户明确暂不做
- **不**做 OpenStock 字段到旧 Adapter 字段的逆向 reshape — 消费端按 OpenStock `fields_typed` 自适应

## Decisions

### 决策 1: 保留 Adapter 类作为外观层(facade),不一次性删除

- **选择**:保留 `AkshareAdapter`/`BaostockAdapter`/`EfinanceAdapter`/`TushareAdapter`/`ByapiAdapter`/`TdxAdapter` 等类名,内部实现改为 OpenStock client 调用
- **替代方案**:删除类,消费端直接用 `OpenStockClient.fetch(...)` — 改动面太大(70+ 处),且测试要全量重写
- **理由**:下游契约稳定,迁移可分域进行,失败时可单域回滚

### 决策 2: 单一 client,不做 provider 抽象

- **选择**:`src/services/openstock/client.py` 只暴露一个 `OpenStockClient` 类,内部按 `data_category` 路由(由 OpenStock 服务端决定 provider)
- **替代方案**:封装 `AkshareProvider`/`BaostockProvider` 等子类 — 多此一举,OpenStock 已经做了
- **理由**:消费端不该关心 provider,只该关心 category

### 决策 3: 配置走 `.env`,不入 `config/data_sources_registry.yaml`

- **选择**:OpenStock 网关地址与 API key 走 `.env` (`OPENSTOCK_BASE_URL` / `OPENSTOCK_API_KEY`),不写进 yaml registry
- **替代方案**:把 OpenStock 也作为一条 entry 写进 yaml — yaml 的 schema 是为多 provider 优先级/质量分设计,OpenStock 单网关不匹配
- **理由**:OpenStock 是单一外部依赖(网关),不是可枚举的数据源;`.env` + Pydantic settings 更合适

### 决策 4: 盲区数据保留旧实现占位,不删除不开发

- **选择**:期货/融资融券/沪深交易所统计/可转债详情这四类,保留现有 akshare/efinance 直调实现作为占位,**不删除不开发**。Adapter 上加 `# OPENSTOCK_GAP: <gap-name>` 注释,在 `docs/reports/openstock-coverage-gaps.md` 落档。
- **替代方案**:直接删除这些功能 — 用户没要求删除
- **理由**:用户明确指示"已有则保留占位、不开发、不删除";盲区清单交给 OpenStock 项目补全后再评估迁移

### 决策 5: OpenStock 配置用单 endpoint + 前置 LB(轻量方案)

- **选择**:`.env` 单条 `OPENSTOCK_BASE_URL` + `OPENSTOCK_API_KEY`。多 docker 部署时前面挂 nginx/HAProxy 做负载均衡,本项目无感。
- **替代方案**:配置升级为 endpoint 列表 + 策略(`OPENSTOCK_ENDPOINTS="url1,url2"` + `OPENSTOCK_STRATEGY=round_robin|failover|category_split`),client 内部维护列表与故障转移。
- **理由**:轻量方案 client 复杂度低,nginx/HAProxy 是工业标准;若后续证明 LB 不够再升级到 client 端策略。当前 OpenStock 单实例已满足需求。

### 决策 6: Adapter 外观层保留(下游零改动)

- **选择**:保留 `AkshareAdapter`/`BaostockAdapter`/`EfinanceAdapter`/`TushareAdapter`/`ByapiAdapter`/`TdxAdapter` 等类名,内部实现改为 OpenStock client 调用
- **替代方案**:删除类,消费端直接用 `OpenStockClient.fetch(...)` — 改动面 70+ 处,且测试要全量重写
- **理由**:
  1. 下游 70+ 处 `from src.adapters.akshare.market_data import AkshareMarketAdapter` + `adapter.get_realtime_quote(...)` 不需要改
  2. 字段对齐缓冲(OpenStock normalize 后字段名可能与现有消费端期望不一致)
  3. 测试隔离(现有 Adapter 契约测试可保留,只换实现)
  4. 分域回滚(每域一个 Adapter,出问题只回滚该域)
- **代价**:类名与实现语义不符,在每个 Adapter 文件顶部加 docstring:"This is a facade. Internal data fetching is delegated to OpenStock gateway. Class name retained for backward compatibility."

> **注**:`expand-akshare-data-sources` proposal 已于 2026-07-07 archive(归档至 `changes/archive/2026-07-07-expand-akshare-data-sources/`),方向被本 proposal 取代。

## Risks / Trade-offs

| 风险 | 缓解 |
|---|---|
| OpenStock 服务挂了,本项目的 A 股数据全断 | OpenStock 内部已有多 provider failover;本项目层面不另加冗余。可加 `/health/ready` 探针监控 |
| 字段 naming 漂移 — OpenStock normalize 后字段名与现有消费端期望不一致 | 客户端按 `GET /sources` 的 `fields_typed` 自适应;迁移时每个 Adapter 加字段映射 unit test |
| 大批量调用(如全市场 K 线)走 HTTP 比 SDK 函数调用慢 | OpenStock 已有 5 秒缓存 + `/data/batch`(最多 50 子请求);消费端可并发 4-8 连接 |
| `expand-akshare-data-sources` 已有 49/105 task 完成的投入被废弃 | 该 proposal 的 task 多为新增 endpoint,与 OpenStock 迁移后 endpoint 可复用;迁移完成后再决定是否复用 |
| Adapter 类名(如 `AkshareAdapter`)与实现(走 OpenStock)语义不符,引起混淆 | 在每个 Adapter 文件顶部加 docstring:"This is a facade. Internal data fetching is delegated to OpenStock gateway. Class name retained for backward compatibility." |

## Migration Plan

按 `tasks.md` 的 7 个阶段顺序推进,每阶段独立 PR:

1. **阶段 1**(接入层):无消费端影响,可独立合并
2. **阶段 2.1**(domain-01):优先迁移,因为它解决 `Byapi ⚠️ 403` 与 `Tushare ⚠️ Token` 两个 FUNCTION_TREE 长期问题
3. **阶段 2.2-2.5**:并行推进,每域一个 PR,验证后再合下一个
4. **阶段 3**(web/backend):必须在阶段 2 完成后
5. **阶段 4**(注册表/脚本):阶段 3 后
6. **阶段 5**(盲区文档):可与其他阶段并行,先交付给 OpenStock 项目
7. **阶段 6**(清理):最后,删依赖、跑 smoke test、更新 FUNCTION_TREE

**回滚策略**:
- 每阶段 PR 独立可回滚
- 旧 Adapter 实现移到 `archive/legacy-dot-archive/openstock-migration-backup/<timestamp>/`,保留 6 个月
- 出现严重故障时,通过 `data_source_factory` 配置开关切回旧实现(阶段 3 时埋下 feature flag)

## Open Questions

- `expand-akshare-data-sources` 是否同步 archive?(建议 yes,需用户确认)
- `optimize-data-source-v2` 的 SmartCache/CircuitBreaker 部分是否还要继续(OpenStock 已提供)?(建议该 proposal 缩减到只保留"数据质量验证"与"监控"两块)
- TDengine 入仓路径(消费端写)是否需要在 OpenStock 与 DB 之间加异步队列?(本次 proposal 不涉及,单独评估)
