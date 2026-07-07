## 1. 接入层与配置

- [x] 1.1 新建 `src/services/openstock/__init__.py`, `client.py`, `category_mapping.py`
- [x] 1.2 实现 `OpenStockClient`:`fetch(category, params)`, `batch(requests)`, `bars(...)`, `snapshot(symbol)`, `routing_best(category)`, `sources()` 六个方法,统一 `X-API-Key` header
- [x] 1.3 实现错误 envelope 解析(`code`/`message`/`request_id`),按 `provider_unavailable` 触发重试,其余 4xx/5xx 抛 `OpenStockError`
- [x] 1.4 `.env.example` 加入 `OPENSTOCK_BASE_URL` 与 `OPENSTOCK_API_KEY`
- [x] 1.5 `web/backend/app/core/config.py` 加入 `openstock_base_url` / `openstock_api_key` 字段,Pydantic 校验非空
- [x] 1.6 `requirements.txt` 加入 `httpx>=0.27.0`;**不引入** akshare/baostock/tushare/efinance 任何 SDK
- [x] 1.7 单元测试 `tests/unit/services/openstock/test_client.py`(mock httpx)

## 2. 消费端直接调用迁移(按位置分批)

> **核心模式**:每处消费端把 `from src.adapters.X import YAdapter` + `adapter = YAdapter(); adapter.method(...)` 改写为 `from src.services.openstock import OpenStockClient, DataCategory` + `client = OpenStockClient(); client.fetch(DataCategory.X, params)`。
> 字段对齐在调用点用 `df.rename(columns={...})` 处理;若同位置多处需要相同映射,可在该位置加薄薄的 `_translate_*_row` helper(不重新引入 Adapter 类)。
> 每批 PR 切完且测试通过后,该批涉及的 `src/adapters/<domain>/**` 文件在本批 PR 内一并删除。

### 2.1 web/backend API/services 入口层(优先 — 解决 Byapi/Tushare 两个 ⚠️)

- [ ] 2.1.1 `web/backend/app/api/akshare_market/base.py` 切到 OpenStockClient
- [ ] 2.1.2 `web/backend/app/api/efinance.py` 切到 OpenStockClient
- [ ] 2.1.3 `web/backend/app/api/dashboard_data_source.py` 切到 OpenStockClient
- [ ] 2.1.4 `web/backend/app/api/stock_ratings_api.py` 切到 OpenStockClient
- [ ] 2.1.5 `web/backend/app/services/data_service.py` + `data_service_enhanced.py` + `tdx_service.py` 切到 OpenStockClient
- [ ] 2.1.6 `web/backend/app/tasks/data_sync.py` 切到 OpenStockClient
- [ ] 2.1.7 `web/backend/app/core/adapter_loader.py` 简化(只剩 openstock + mock 路径)
- [ ] 2.1.8 删除 `web/backend/app/services/adapters_split/{akshare,baostock,tushare,efinance}_adapter.py` + `data_adapter_new.py`(本批消费端切完后)
- [ ] 2.1.9 集成 smoke test `tests/integration/test_openstock_phase2_1_web_backend.py`(env-gated)

### 2.2 src/trading + src/database + src/storage(运行时关键路径)

- [ ] 2.2.1 `src/trading/live_trading_engine.py` 切到 OpenStockClient
- [ ] 2.2.2 `src/trading/realtime_strategy_executor.py` 切到 OpenStockClient
- [ ] 2.2.3 `src/database/service/adapter_queries.py` 切到 OpenStockClient
- [ ] 2.2.4 `src/storage/database/save_realtime_market_data.py` 切到 OpenStockClient
- [ ] 2.2.5 `src/storage/database/validate_mystocks_architecture.py` 切到 OpenStockClient(若需要)
- [ ] 2.2.6 集成 smoke test `tests/integration/test_openstock_phase2_2_runtime.py`

### 2.3 src/data_sources 直接 SDK import(4 处)

- [ ] 2.3.1 `src/data_sources/baostock_importer.py` 切到 OpenStockClient(`HISTORICAL_KLINES` / `STOCK_INDUSTRY` / `TRADE_DATES`)
- [ ] 2.3.2 `scripts/fetch_akshare_data.py` 切到 OpenStockClient
- [ ] 2.3.3 `scripts/populate_stock_info.py` 切到 OpenStockClient(`ALL_STOCKS` / `STOCK_BASIC`)
- [ ] 2.3.4 `scripts/maintenance/data_sync/base_data_source.py` 切到 OpenStockClient
- [ ] 2.3.5 集成 smoke test `tests/integration/test_openstock_phase2_3_scripts.py`

### 2.4 scripts 运行时与示例(批量)

- [ ] 2.4.1 `scripts/runtime/run_realtime_market_saver.py` + `save_realtime_data.py` 切到 OpenStockClient
- [ ] 2.4.2 `scripts/examples/tdx_usage_examples.py` + `adapter_refactoring_example.py` 切到 OpenStockClient(或归档示例)
- [ ] 2.4.3 `scripts/_test_data_validator_phase6_tail.py` 切到 OpenStockClient(或归档)
- [ ] 2.4.4 `scripts/check_system_health.py` 若引用 Adapter,切到 OpenStockClient
- [ ] 2.4.5 集成 smoke test 覆盖 2.4

### 2.5 src/adapters 内部交叉引用清理

- [ ] 2.5.1 盘点 `src/adapters/**` 内部互相 import 的情况(如 `market_adapter` Mixin 之间)
- [ ] 2.5.2 若某 Adapter 仍被 2.1-2.4 之外的 Adapter 引用,把被引用方先切到 OpenStockClient 或直接删除被引用方
- [ ] 2.5.3 验证 `src/interfaces/adapters/**` 抽象基类是否有消费端直接依赖(若仅 src/adapters 内部用,与 src/adapters 一并删除)

## 3. 注册表与脚本清理

- [ ] 3.1 `config/data_sources_registry.yaml`:删除 18 个 akshare entry,加入 1 个 `openstock_gateway` entry 指向 client
- [ ] 3.2 验证 `mock_daily_kline` 与 `windows_distributed_bridge` 两个非外部源 entry 仍然可用
- [ ] 3.3 `web/backend/app/services/data_source_factory/data_source_factory.py` 工厂方法简化(只剩 openstock + mock 两条路径)

## 4. 覆盖盲区文档(交付给 OpenStock 项目)

- [ ] 4.1 创建 `docs/reports/openstock-coverage-gaps.md`,列出:
  - 期货(`futures_basis`/`futures_index_daily`/`futures_main_contract`/`futures_index_realtime`)
  - 融资融券(`margin_detail_sse`/`margin_detail_szse`/`margin_summary_sse`/`margin_summary_szse`/`margin_account_info`)
  - 沪深交易所成交统计(`sse_daily_deal`/`sse_market_summary`/`szse_area_trading`/`szse_market_summary`/`szse_sector_trading`)
  - 可转债 K 线与详情(`CONVERTIBLE_BONDS` 当前 OpenStock 只提供基础行)
- [ ] 4.2 每条需求写明:业务用途、字段清单、调用频率、是否需要历史回溯
- [ ] 4.3 保留 `src/adapters/efinance_adapter/efinance_bond_helpers.py`(可转债盲区)+ `akshare_futures_*` 入口(期货盲区),源码顶部加 `# OPENSTOCK_GAP: <gap-name>` 注释

## 5. 清理与验证

- [ ] 5.1 删除 `src/adapters/**` 整个目录(2.1-2.5 完成后,盲区保留项已独立)
- [ ] 5.2 删除 `src/interfaces/adapters/**`(若仅 src/adapters 内部使用)
- [ ] 5.3 `requirements.txt` (root) 删除 `akshare>=1.11.0` / `baostock>=0.8.9` / `tushare>=1.3.0` / `efinance>=0.5.0`
- [ ] 5.4 `web/backend/requirements.txt` 同上(若也列了)
- [ ] 5.5 pre-commit / CI 检查:新增 `import akshare/baostock/tushare/efinance` 在 `src/`, `web/backend/`, `scripts/` 下时被 lint 拦截(除盲区例外)
- [ ] 5.6 `FUNCTION_TREE.md`:01-市场数据的 Byapi ⚠️ 与 Tushare ⚠️ 改为 ✅,在维护日志注明"由 OpenStock 替代"
- [ ] 5.7 `gitnexus detect_changes --scope=staged` 验证影响面符合预期

## 6. 关联 proposal 处置

- [x] 6.1 `expand-akshare-data-sources` 已于 2026-07-07 archive(方向被本 proposal 取代)
- [x] 6.2 `migrate-akshare-fundflow-mixin-to-openstock` 已于 2026-07-07 archive(facade 方向被本直接消费方向取代)
- [x] 6.3 `migrate-akshare-market-adapter-modules-to-openstock` 已于 2026-07-07 archive(同上)
- [ ] 6.4 在 `optimize-data-source-v2` proposal 中标注"缓存/熔断由 OpenStock 提供,本项目层面只需轻量客户端"(task #11 单独处理)
