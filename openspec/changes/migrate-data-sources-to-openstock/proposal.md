# Change: 将所有外部市场数据源统一收敛到 OpenStock 网关

## Why

本项目当前在 `src/adapters/`, `src/interfaces/adapters/`, `web/backend/app/services/adapters_split/`, `scripts/` 下散落 39+ 个文件直接 `import akshare / baostock / tushare / efinance`,自建 30+ 个 Adapter 类。这导致:

1. **重复实现 OpenStock 已具备的能力** — OpenStock 已经把 eltdx/baostock/akshare/zzshare 四类 provider 包装为 70 个 data_category,带统一 failover、5 秒 TTL 缓存、熔断器、字段 normalize、`X-API-Key` 鉴权。本项目再写一遍同逻辑纯属浪费。
2. **维护负担集中** — `FUNCTION_TREE.md` 的 01-市场数据域长期挂着 `Byapi ⚠️ 403` 与 `Tushare ⚠️ Token 配置` 两个未修复项,迁到 OpenStock 后这两类问题被 baostock/eltdx 自动替代,自然消失。
3. **行为不一致** — 不同 adapter 各自实现重试/缓存/字段命名,消费端无法依赖稳定契约。
4. **`config/data_sources_registry.yaml`** (2014 行) 只注册了 18 个 akshare entry + 2 个 mock/bridge,既不完整也与 OpenStock 的 category 模型脱节。

OpenStock 已部署在 NAS Docker (192.168.123.104:8040,镜像 `openstock:nas`),70 个 category 全量可用。本项目必须把所有 A 股市场/基本面/公告/资金流/板块/龙虎榜/涨停复盘/跨市场 数据访问切换为通过 OpenStock,以消除重复实现并统一治理。

## What Changes

### 阶段 1 — 网关接入层

- **新增** `src/services/openstock/client.py`:单一 HTTP 客户端,从 `.env` 读取 `OPENSTOCK_BASE_URL` + `OPENSTOCK_API_KEY`,封装 `POST /data/fetch` / `/data/batch` / `/data/bars` / `/data/snapshot` / `POST /routing/best` / `GET /sources`,统一错误 envelope 解码与超时重试。
- **新增** `src/services/openstock/category_mapping.py`:把现有 Adapter 方法签名映射到 OpenStock `data_category` 常量。
- **新增** `.env.example` 条目:`OPENSTOCK_BASE_URL=http://192.168.123.104:8040`, `OPENSTOCK_API_KEY=<密钥>`。
- **更新** `web/backend/app/core/config.py`:加入 OpenStock 配置字段与 Pydantic 校验。

### 阶段 2 — Adapter 外观层改造(无下游影响)

- **保留** 现有 Adapter 类名(`AkshareAdapter`, `BaostockAdapter`, `EfinanceAdapter`, `TushareAdapter`, `ByapiAdapter`, `TdxAdapter` 等)作为外观层,内部实现改为调用 OpenStock client,以避免下游 70+ 处调用的级联修改。
- **逐域迁移**: domain-01 市场数据 → 02 行情 → 03 策略输入 → 04 基本面 → 06 板块/资金流 → 10 公告,每域一个 PR + 端到端验证。
- **删除** Adapter 内部对 `akshare`/`baostock`/`tushare`/`efinance` SDK 的直接 import。

### 阶段 3 — 注册表与脚本清理

- **重写** `config/data_sources_registry.yaml`:移除 18 个 `source_name: akshare` entry,改为引用 OpenStock category 映射表。
- **保留** `mock_daily_kline` 与 `windows_distributed_bridge` 两个非外部源 entry(分别用于测试与本地终端桥)。
- **迁移** `scripts/fetch_akshare_data.py`, `scripts/populate_stock_info.py`, `scripts/maintenance/data_sync/base_data_source.py` 三个脚本到 OpenStock 调用。

### 阶段 4 — 不迁移项(显式排除)

以下数据需求 OpenStock 当前**不提供**,按 2026-07-07 用户决策处置:

- **期货数据** — `akshare_futures_*` 4 个 entry **保留占位、不删除、不开发**。源码顶部加 `# OPENSTOCK_GAP: futures` 注释,等 OpenStock 补 `FUTURES_*` category 后再迁。
- **期权数据** — 项目当前未实现,**不开发**。
- **可转债详情** — 现有 `src/adapters/efinance_adapter/efinance_bond_helpers.py` **保留占位、不删除、不开发**。OpenStock 当前 `CONVERTIBLE_BONDS` 只提供基础行,本项目不主动要求扩展。
- **融资融券** / **沪深交易所成交统计** — 这两类需求写入 `docs/reports/openstock-coverage-gaps.md`(本 proposal 一并产出),交由 OpenStock 项目补全后再迁。现有实现保留占位。

### 阶段 5 — 验证与归档

- 单元测试:OpenStock client 的 mock 测试 + 每 Adapter 外观层的契约测试。
- 集成测试:对 NAS 上 OpenStock 实例做端到端 smoke test。
- 删除 `requirements.txt` 中 `akshare>=1.11.0` / `baostock>=0.8.9` / `tushare>=1.3.0` / `efinance>=0.5.0` 四个依赖。
- `FUNCTION_TREE.md` 01-市场数据的 `Byapi ⚠️` 与 `Tushare ⚠️` 两条移到归档说明。

## Impact

- **Affected specs**: `data-sources`, `market-data`(若存在);新增 capability `openstock-gateway`。
- **Affected code**:
  - 新增:`src/services/openstock/{client,category_mapping}.py`, `docs/reports/openstock-coverage-gaps.md`
  - 改造(~30 文件):`src/adapters/{akshare,baostock,efinance_adapter,byapi_adapter,tdx,tushare_adapter}/**`, `src/interfaces/adapters/**` 对应实现
  - 改造(5 文件):`web/backend/app/services/adapters_split/{akshare,baostock,tushare,efinance}_adapter.py` + `data_adapter_new.py`
  - 重写:`config/data_sources_registry.yaml`
  - 清理:`requirements.txt`, `requirements.txt` (root)
- **依赖关系**:`expand-akshare-data-sources` proposal 已于 2026-07-07 archive(方向被本 proposal 取代)。`optimize-data-source-v2` 建议缩减范围至"数据质量验证 + 监控"两块(OpenStock 已提供缓存/熔断)。
- **BREAKING**:无对外 API 变化。Adapter 类签名保持稳定。仅内部数据获取路径改变。
- **回滚策略**:保留旧 Adapter 实现于 `archive/legacy-dot-archive/openstock-migration-backup/`,回滚时恢复并切换 factory 路由。

## Open Questions

- `optimize-data-source-v2` 的 SmartCache/CircuitBreaker 部分是否还要继续(OpenStock 已提供)?(建议该 proposal 缩减到只保留"数据质量验证"与"监控"两块)
- TDengine 入仓路径(消费端写)是否需要在 OpenStock 与 DB 之间加异步队列?(本次 proposal 不涉及,单独评估)
- OpenStock 多 docker 部署时,配置层是否升级为 endpoint 列表 + 策略(round_robin / failover / category_split)?当前 proposal 先用单 `OPENSTOCK_BASE_URL` + 前置 nginx/HAProxy 负载均衡的轻量方案,后续按需升级。
