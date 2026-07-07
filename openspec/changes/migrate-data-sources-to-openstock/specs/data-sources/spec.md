## ADDED Requirements

### Requirement: OpenStock 作为单一外部数据网关

系统 SHALL 通过 OpenStock HTTP 网关(`POST /data/fetch` + `data_category` + `X-API-Key` header)获取所有 A 股市场、基本面、财务、公告、资金流、板块、龙虎榜、涨停复盘、跨市场(HK/US/ETF/基金/可转债)数据,而非直接调用 akshare/baostock/tushare/efinance SDK。

#### Scenario: 通过 OpenStock 获取实时行情

- **WHEN** 业务代码需要实时行情
- **THEN** 调用方直接 `from src.services.openstock import OpenStockClient, DataCategory` + `client = OpenStockClient()` + `client.fetch(DataCategory.REALTIME_QUOTES, {"symbol": "000001"})`
- **AND** 内部发起 `POST {OPENSTOCK_BASE_URL}/data/fetch` 请求, body 包含 `{"data_category": "REALTIME_QUOTES", "params": {"symbol": "000001"}}`, header 包含 `X-API-Key: ${OPENSTOCK_API_KEY}`
- **AND** 返回数据按 OpenStock `fields_typed` 规范的字段名传递给消费端

#### Scenario: OpenStock provider 失败时自动 failover

- **WHEN** OpenStock 内部 eltdx provider 不可用
- **THEN** OpenStock 自动切到 akshare provider,响应中 `source` 字段反映实际 provider
- **AND** 本项目 client 不感知 provider 切换,只关心 HTTP 状态码与响应体

#### Scenario: 配置缺失时启动失败

- **WHEN** `.env` 未设置 `OPENSTOCK_BASE_URL` 或 `OPENSTOCK_API_KEY`
- **THEN** 后端启动时 Pydantic settings 校验失败,抛出明确错误
- **AND** 不进入运行时

### Requirement: 消费端直接调用 OpenStockClient(不通过 Adapter)

消费端代码(`web/backend/`, `scripts/`, `src/trading/`, `src/database/`, `src/storage/`, `src/data_sources/`)SHALL 直接 `from src.services.openstock import OpenStockClient, DataCategory` 并调用 `client.fetch(DataCategory.X, params)`,MUST NOT 通过 `src/adapters/**` 的 Adapter 类间接调用。迁移完成后 `src/adapters/**` 与 `src/interfaces/adapters/**` 目录整体删除。

#### Scenario: 消费端 import 路径

- **WHEN** 消费端代码需要 A 股市场数据
- **THEN** import 语句为 `from src.services.openstock import OpenStockClient, DataCategory`
- **AND** **不**出现 `from src.adapters.akshare.market_data import AkshareMarketAdapter` 或 `from src.interfaces.adapters import ...` 等 Adapter 路径

#### Scenario: 字段对齐在调用点

- **WHEN** OpenStock 返回的字段名与消费端期望不同(如 `time` vs `datetime`)
- **THEN** 消费端在调用点用 `df.rename(columns={"time": "datetime"})` 显式对齐
- **AND** **不**通过 Adapter 类或 `OpenStockClient` 上层的字段映射中间件做隐式 reshape

#### Scenario: src/adapters 目录被删除

- **WHEN** 阶段 2.1-2.5 全部完成且盲区保留项已独立
- **THEN** `src/adapters/**` 与 `src/interfaces/adapters/**` 目录从仓库中删除
- **AND** 仓库内 `git grep "from src.adapters"` 仅命中盲区保留文件(若该文件未迁移到 `src/services/openstock/` 之外的位置)

### Requirement: 不再直接 import 外部数据源 SDK

`src/`, `web/backend/`, `scripts/` 下的代码 MUST NOT 包含 `import akshare` / `import baostock` / `import tushare` / `import efinance`(以及对应的 `from ... import`)语句,除非该数据需求显式登记在 `docs/reports/openstock-coverage-gaps.md` 中。

#### Scenario: 新增代码引入外部 SDK 时被 lint 拦截

- **WHEN** 开发者在新代码中加入 `import akshare`
- **THEN** pre-commit hook 或 CI 检查报错,指向 `docs/reports/openstock-coverage-gaps.md` 流程
- **AND** 提示开发者改用 `from src.services.openstock import OpenStockClient, DataCategory`

#### Scenario: 已有的盲区例外被显式登记

- **WHEN** 某数据需求确实在 OpenStock 盲区中(如期货)
- **THEN** 该 import 语句保留,文件顶部加 `# OPENSTOCK_GAP: futures — see docs/reports/openstock-coverage-gaps.md` 注释
- **AND** 该文件路径在盲区文档中可被检索

### Requirement: OpenStock 配置通过环境变量注入

OpenStock 网关地址与 API key SHALL 通过 `.env` 的 `OPENSTOCK_BASE_URL` 与 `OPENSTOCK_API_KEY` 注入,MUST NOT 硬编码于源码或 yaml 配置中。

#### Scenario: 默认开发环境

- **WHEN** 开发者克隆仓库并复制 `.env.example` 为 `.env`
- **THEN** `.env` 包含 `OPENSTOCK_BASE_URL=http://192.168.123.104:8040` 与 `OPENSTOCK_API_KEY=<占位符>` 两条
- **AND** 启动文档明确说明需替换占位符为实际 key

#### Scenario: 后端 config 校验

- **WHEN** FastAPI 启动并加载 `Settings`
- **THEN** `openstock_base_url` 与 `openstock_api_key` 字段均为非空字符串
- **AND** 校验失败时不启动服务

### Requirement: OpenStock 覆盖盲区显式登记

OpenStock 当前不提供但本项目需要的数据需求(期货、融资融券、沪深交易所成交统计、可转债详情等)SHALL 登记在 `docs/reports/openstock-coverage-gaps.md`,每条包含业务用途、字段清单、调用频率、是否需要历史回溯。

#### Scenario: 新增盲区需求时更新文档

- **WHEN** 开发者发现某需求 OpenStock 不覆盖
- **THEN** 在 `docs/reports/openstock-coverage-gaps.md` 添加新条目,说明业务用途与字段
- **AND** 在源码对应 import 处加 `# OPENSTOCK_GAP: <gap-name>` 注释引用文档

#### Scenario: 盲区被 OpenStock 补全后迁移

- **WHEN** OpenStock 项目实现了某盲区 category
- **THEN** 本项目该 import 处改为 OpenStock client 调用
- **AND** 从盲区文档移除对应条目
- **AND** 在 CHANGELOG 记录
