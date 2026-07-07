## Context

OpenStock 已作为 NAS Docker 服务运行(`openstock:nas`,端口 8040→8000,API key 鉴权),在内部封装了 eltdx/baostock/akshare/zzshare 四类 provider,对外暴露 70 个 source-neutral data_category,自带 5 秒 TTL 缓存、熔断器、自动 failover、字段 normalize、`X-API-Key` 鉴权。本项目历史上有 39+ 个文件直接 import 上述四个 SDK,自建 30+ Adapter,逻辑重复且散乱。

约束:
- 必须可分域验证 — 每个业务域独立 PR + smoke test
- OpenStock 不覆盖的盲区(期货/融资融券/沪深交易所统计)需要显式落档,交 OpenStock 项目补全
- 期货/期权功能按用户决策暂不实现
- 消费端改动必须分批进行 — 一次性大爆炸式改 100+ 处 import 风险高,每批独立可回滚

利益相关方:
- 消费端:`web/backend/app/services/` 各业务 service、`web/backend/app/api/` 路由、`scripts/` 数据同步脚本、`src/trading/`、`src/database/`、`src/storage/`
- 提供端:OpenStock NAS 实例(192.168.123.104:8040)

## Goals / Non-Goals

**Goals**:
- 所有 A 股市场数据/基本面/财务/公告/资金流/板块/龙虎榜/涨停复盘/跨市场(HK/US/ETF/基金)数据通过 OpenStock 单一网关获取
- 消费端代码直接 `from src.services.openstock import OpenStockClient, DataCategory` 调用 `client.fetch(...)`,**无 Adapter 中间层**
- 配置(`OPENSTOCK_BASE_URL` / `OPENSTOCK_API_KEY`)从 `.env` 注入,零硬编码
- 删除 4 个外部 SDK 依赖,减少 requirements 体积与版本漂移风险
- 删除整个 `src/adapters/**` 与 `src/interfaces/adapters/**` 目录(消费端切完后)

**Non-Goals**:
- **不**实现 OpenStock client 的复杂调度逻辑(重试/熔断/缓存)— OpenStock 已内置,本项目 client 只做超时与单次重试
- **不**改造 TDengine/PostgreSQL 入仓路径 — OpenStock 是数据网关,不入仓,消费端自行写库
- **不**实现期货/期权/交易执行 — 用户明确暂不做
- **不**保留 Adapter 类作为 facade — 用户明确否决"造轮子"方向,Adapter 类全部删除
- **不**做 OpenStock 字段到旧 Adapter 字段的逆向 reshape — 消费端按 OpenStock `fields_typed` 自适应,在调用点做最小字段映射

## Decisions

### 决策 1: 消费端直接调用 OpenStockClient,删除 Adapter 中间层

- **选择**:消费端 `from src.services.openstock import OpenStockClient, DataCategory` + `client.fetch(DataCategory.X, params)`。`src/adapters/**` 与 `src/interfaces/adapters/**` 在消费端切完后整体删除。
- **替代方案(已被否决)**:保留 Adapter 类作为 facade,内部实现改为 OpenStockClient 调用 — 维护两套抽象(OpenStockClient + Adapter 外壳),消费端被 Adapter 签名绑死,Adapter 反而成了一层无用的中间包装。用户原话"只消费 openstock,不自己造轮子"明确否决此方向。
- **理由**:
  1. OpenStock 已经是稳定的契约层(70 个 category + fields_typed),不需要再加一层 Adapter 抽象
  2. 直接消费让消费端代码更短、更直白,import 路径更清晰
  3. 删除 Adapter 后,`src/adapters/**` 的 30+ 类与 `src/interfaces/adapters/**` 的抽象基类全部消失,代码体积大幅下降
  4. 分批迁移仍可保证可回滚性(每批一个 PR,git revert 即可)

### 决策 2: 单一 client,不做 provider 抽象

- **选择**:`src/services/openstock/client.py` 只暴露一个 `OpenStockClient` 类,内部按 `data_category` 路由(由 OpenStock 服务端决定 provider)
- **替代方案**:封装 `AkshareProvider`/`BaostockProvider` 等子类 — 多此一举,OpenStock 已经做了
- **理由**:消费端不该关心 provider,只该关心 category

### 决策 3: 配置走 `.env`,不入 `config/data_sources_registry.yaml`

- **选择**:OpenStock 网关地址与 API key 走 `.env` (`OPENSTOCK_BASE_URL` / `OPENSTOCK_API_KEY`),不写进 yaml registry
- **替代方案**:把 OpenStock 也作为一条 entry 写进 yaml — yaml 的 schema 是为多 provider 优先级/质量分设计,OpenStock 单网关不匹配
- **理由**:OpenStock 是单一外部依赖(网关),不是可枚举的数据源;`.env` + Pydantic settings 更合适

### 决策 4: 盲区数据保留旧实现占位,不删除不开发

- **选择**:期货/融资融券/沪深交易所统计/可转债详情这四类,保留现有 akshare/efinance 直调实现作为占位,**不删除不开发**。源码顶部加 `# OPENSTOCK_GAP: <gap-name>` 注释,在 `docs/reports/openstock-coverage-gaps.md` 落档。
- **替代方案**:直接删除这些功能 — 用户没要求删除
- **理由**:用户明确指示"已有则保留占位、不开发、不删除";盲区清单交给 OpenStock 项目补全后再评估迁移

### 决策 5: OpenStock 配置用单 endpoint + 前置 LB(轻量方案)

- **选择**:`.env` 单条 `OPENSTOCK_BASE_URL` + `OPENSTOCK_API_KEY`。多 docker 部署时前面挂 nginx/HAProxy 做负载均衡,本项目无感。
- **替代方案**:配置升级为 endpoint 列表 + 策略(`OPENSTOCK_ENDPOINTS="url1,url2"` + `OPENSTOCK_STRATEGY=round_robin|failover|category_split`),client 内部维护列表与故障转移。
- **理由**:轻量方案 client 复杂度低,nginx/HAProxy 是工业标准;若后续证明 LB 不够再升级到 client 端策略。当前 OpenStock 单实例已满足需求。

### 决策 6: 字段对齐在消费端做,不引入字段映射中间层

- **选择**:OpenStock `fields_typed` 与旧 Adapter 字段名差异(如 `time` vs `date`、`symbol` vs `股票代码`),由消费端在调用点用 `df.rename(columns={...})` 或薄薄的 `_translate_*_row` helper 处理。**不**在 `src/services/openstock/` 内做字段映射,也**不**重新引入 Adapter 类做字段对齐。
- **替代方案**:在 `OpenStockClient` 上层加 `FieldMapper` 中间件 — 又是一层抽象,违背"直接消费"原则
- **理由**:
  1. 不同消费端期望的字段名可能不同(有的要 `date`,有的要 `datetime`),统一映射反而僵化
  2. 调用点 `df.rename` 显式、可读、易测
  3. 若同位置多处用相同映射,helper 函数足够;跨位置共享的映射放进 `src/services/openstock/field_mappings.py`(纯函数,非类)

> **注**:`expand-akshare-data-sources` proposal 已于 2026-07-07 archive(归档至 `changes/archive/2026-07-07-expand-akshare-data-sources/`)。`migrate-akshare-fundflow-mixin-to-openstock` 与 `migrate-akshare-market-adapter-modules-to-openstock` 两个 facade 方向 proposal 亦于 2026-07-07 archive(归档至 `changes/archive/2026-07-07-migrate-akshare-*-to-openstock/`),方向被本直接消费 proposal 取代。

## Risks / Trade-offs

| 风险 | 缓解 |
|---|---|
| OpenStock 服务挂了,本项目的 A 股数据全断 | OpenStock 内部已有多 provider failover;本项目层面不另加冗余。可加 `/health/ready` 探针监控 |
| 字段 naming 漂移 — OpenStock normalize 后字段名与现有消费端期望不一致 | 消费端按 `GET /sources` 的 `fields_typed` 自适应;每个迁移 PR 在调用点用 `df.rename` 显式对齐,加单元测试 |
| 大批量调用(如全市场 K 线)走 HTTP 比 SDK 函数调用慢 | OpenStock 已有 5 秒缓存 + `/data/batch`(最多 50 子请求);消费端可并发 4-8 连接 |
| 消费端改动面大(~30 处运行代码 + ~70 处测试) — 一次性大爆炸风险高 | 按 2.1-2.5 分批:web/backend → src/trading+database+storage → src/data_sources+scripts 根 → scripts 运行时 → src/adapters 内部交叉引用。每批独立 PR,可独立回滚 |
| 删除 `src/adapters/**` 后,旧测试套件可能大量失败 | 测试一并改写:旧 Adapter 契约测试删除,新增 OpenStockClient 集成 smoke test;每批 PR 内测试同步更新 |
| 已有的两个 facade 方向 proposal(`migrate-akshare-fundflow-mixin`/`migrate-akshare-market-adapter-modules`)已 archive,但其 tasks.md 中部分已完成的工作可能被废弃 | 这些 proposal 在 archive 前未实际落地代码(都是文档),archive 即可;若有已落地的 Mixin 改造,在新 Phase 2 中重新评估是否保留 |

## Migration Plan

按 `tasks.md` 的 6 个阶段顺序推进,每阶段独立 PR:

1. **阶段 1**(接入层,已实现):`src/services/openstock/` + 单元测试。本 PR 一并交付。
2. **阶段 2.1**(web/backend):优先迁移,因为它解决 `Byapi ⚠️ 403` 与 `Tushare ⚠️ Token` 两个 FUNCTION_TREE 长期问题,且影响面最大(13 处)
3. **阶段 2.2**(src/trading+database+storage):运行时关键路径,6 处
4. **阶段 2.3**(src/data_sources+scripts 根直接 SDK):4 处直接 import,删依赖前必须切完
5. **阶段 2.4**(scripts 运行时与示例):批量,可并行
6. **阶段 2.5**(src/adapters 内部交叉引用):清理内部依赖,为阶段 5 删除做准备
7. **阶段 3**(注册表/脚本):必须在阶段 2 完成后
8. **阶段 4**(盲区文档):可与其他阶段并行,先交付给 OpenStock 项目
9. **阶段 5**(清理):最后,删 `src/adapters/**`、删依赖、跑 smoke test、更新 FUNCTION_TREE

**回滚策略**:
- 每阶段 PR 独立可回滚(`git revert`)
- 旧 Adapter 实现保留在 git 历史,不另存 `archive/legacy-dot-archive/` 副本
- 出现严重故障时,直接 revert 对应 PR 即可恢复

## Open Questions

- `optimize-data-source-v2` 的 SmartCache/CircuitBreaker 部分是否还要继续(OpenStock 已提供)?(建议该 proposal 缩减到只保留"数据质量验证"与"监控"两块)
- TDengine 入仓路径(消费端写)是否需要在 OpenStock 与 DB 之间加异步队列?(本次 proposal 不涉及,单独评估)
- OpenStock 多 docker 部署时,配置层是否升级为 endpoint 列表 + 策略(round_robin / failover / category_split)?当前 proposal 先用单 `OPENSTOCK_BASE_URL` + 前置 nginx/HAProxy 负载均衡的轻量方案,后续按需升级。
