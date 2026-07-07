## 1. 接入层与配置

- [x] 1.1 新建 `src/services/openstock/__init__.py`, `client.py`, `category_mapping.py`
- [x] 1.2 实现 `OpenStockClient`:`fetch(category, params)`, `batch(requests)`, `bars(...)`, `snapshot(symbol)`, `routing_best(category)`, `sources()` 六个方法,统一 `X-API-Key` header
- [x] 1.3 实现错误 envelope 解析(`code`/`message`/`request_id`),按 `provider_unavailable` 触发重试,其余 4xx/5xx 抛 `OpenStockError`
- [x] 1.4 `.env.example` 加入 `OPENSTOCK_BASE_URL` 与 `OPENSTOCK_API_KEY`
- [x] 1.5 `web/backend/app/core/config.py` 加入 `openstock_base_url` / `openstock_api_key` 字段,Pydantic 校验非空
- [x] 1.6 `requirements.txt` 加入 `httpx>=0.27.0`(若尚未有);**不引入** akshare/baostock/tushare/efinance 任何 SDK

## 2. Adapter 外观层迁移(按域分批)

### 2.1 domain-01 市场数据(优先 — 解决 Byapi/Tushare 两个 ⚠️)

- [x] 2.1.1 `src/adapters/akshare/market_data.py` 内部改为 `client.fetch(...)` (STOCK_INDUSTRY + TOPICS_CONCEPTS)
- [x] 2.1.2 `src/adapters/akshare/stock_info.py` → `ALL_STOCKS` / `SECTOR_QUOTES` (待 OpenStock 修复 SECTOR_QUOTES 上游)
- [x] 2.1.3 `src/adapters/baostock/baostock_adapter.py` → `HISTORICAL_KLINES` / `STOCK_INDUSTRY` / `TRADE_DATES`
- [x] 2.1.4 `src/adapters/byapi_adapter.py` 改为 OpenStock `REALTIME_QUOTES`(eltdx 后端),保留类名
- [x] 2.1.5 `src/adapters/tushare_adapter.py` 改为 OpenStock `STOCK_BASIC` + `FINANCIAL_STATEMENTS`,保留类名

### 2.2 domain-02 行情与图表

- [ ] 2.2.1 `src/adapters/akshare/market_adapter/market_overview.py` → `INDEX_QUOTES`
- [ ] 2.2.2 `src/adapters/tdx/realtime_service.py` → `REALTIME_QUOTES` + `MARKET_DEPTH`
- [ ] 2.2.3 `src/adapters/tdx/kline_data_service.py` → `KLINES` + `ADJUSTED_KLINES`

### 2.3 domain-03/04 基本面与财务

- [ ] 2.3.1 `src/adapters/akshare/financial_data.py` → `FINANCIAL_DATA` + `FINANCIAL_STATEMENTS`
- [ ] 2.3.2 `src/adapters/efinance_adapter/**` → `FINANCIAL_STATEMENTS` + `FORECAST_DATA` + `CONVERTIBLE_BONDS`(债券保留待 OpenStock 补)
- [ ] 2.3.3 `src/adapters/akshare/market_adapter/forecast_analysis.py` → `FORECAST_DATA`

### 2.4 domain-06 板块/资金流/龙虎榜

- [ ] 2.4.1 `src/adapters/akshare/market_adapter/board_sector.py` → `SECTOR_QUOTES` + `SECTOR_CONSTITUENTS`
- [ ] 2.4.2 `src/adapters/akshare/market_adapter/fund_flow.py` 与 `src/adapters/akshare/fund_flow.py` → `FUND_FLOW` + `SECTOR_FUND_FLOW` + `NORTHBOUND_FLOW`
- [ ] 2.4.3 龙虎榜相关 → `DRAGON_TIGER` + `DRAGON_TIGER_TRADER` + `DRAGON_TIGER_STOCK_HISTORY`

### 2.5 domain-10 公告

- [ ] 2.5.1 公告相关 Adapter → `ANNOUNCEMENTS` + `STOCK_NEWS` + `RESEARCH_REPORTS`

## 3. web/backend 入口层

- [ ] 3.1 `web/backend/app/services/adapters_split/akshare_adapter.py` 改为持有 OpenStock client
- [ ] 3.2 同上 `baostock_adapter.py` / `tushare_adapter.py` / `efinance_adapter.py`
- [ ] 3.3 `web/backend/app/services/data_adapter_new.py` 路由表更新:所有外部数据源指向 OpenStock
- [ ] 3.4 `web/backend/app/services/data_source_factory/data_source_factory.py` 工厂方法简化(只剩 openstock + mock 两条路径)

## 4. 注册表与脚本

- [ ] 4.1 `config/data_sources_registry.yaml`:删除 18 个 akshare entry,加入 1 个 `openstock_gateway` entry 指向 client
- [ ] 4.2 `scripts/fetch_akshare_data.py` 重写为 `scripts/fetch_openstock_data.py`(或保留旧名做 alias)
- [ ] 4.3 `scripts/populate_stock_info.py` 改为 OpenStock `ALL_STOCKS`
- [ ] 4.4 `scripts/maintenance/data_sync/base_data_source.py` 切换到 OpenStock

## 5. 覆盖盲区文档(交付给 OpenStock 项目)

- [ ] 5.1 创建 `docs/reports/openstock-coverage-gaps.md`,列出:
  - 期货(`futures_basis`/`futures_index_daily`/`futures_main_contract`/`futures_index_realtime`)
  - 融资融券(`margin_detail_sse`/`margin_detail_szse`/`margin_summary_sse`/`margin_summary_szse`/`margin_account_info`)
  - 沪深交易所成交统计(`sse_daily_deal`/`sse_market_summary`/`szse_area_trading`/`szse_market_summary`/`szse_sector_trading`)
  - 可转债 K 线与详情(`CONVERTIBLE_BONDS` 当前 OpenStock 只提供基础行)
- [ ] 5.2 每条需求写明:业务用途、字段清单、调用频率、是否需要历史回溯

## 6. 清理与验证

- [ ] 6.1 `requirements.txt` (root) 删除 `akshare>=1.11.0` / `baostock>=0.8.9` / `tushare>=1.3.0` / `efinance>=0.5.0`
- [ ] 6.2 `web/backend/requirements.txt` 同上
- [ ] 6.3 单元测试:`tests/unit/services/openstock/test_client.py`(mock httpx)
- [ ] 6.4 契约测试:每 Adapter 外观层方法对 OpenStock category 的映射断言
- [ ] 6.5 端到端 smoke test:对 `http://192.168.123.104:8040` 跑一次 10 个核心 category
- [ ] 6.6 `FUNCTION_TREE.md`:01-市场数据的 Byapi ⚠️ 与 Tushare ⚠️ 改为 ✅,在维护日志注明"由 OpenStock 替代"
- [ ] 6.7 `gitnexus detect_changes --scope=staged` 验证影响面符合预期

## 7. 关联 proposal 处置

- [ ] 7.1 评估是否 archive `expand-akshare-data-sources`(方向已被本 proposal 取代)
- [ ] 7.2 在 `optimize-data-source-v2` proposal 中标注"缓存/熔断由 OpenStock 提供,本项目层面只需轻量客户端"
