# OpenStock 覆盖盲区清单

> Status: living document
> Last updated: 2026-07-07
> Owner: mystocks_spec 项目 → 转交 OpenStock 项目实现

本文档登记 mystocks_spec 项目当前需要、但 OpenStock 网关 (`http://192.168.123.104:8040`) 当前**未提供**的数据需求。每条新增 category 实现后,OpenStock 项目方通知本项目,本项目负责迁移对应 Adapter 并从本清单移除条目。

OpenStock 当前能力清单参见 `/opt/claude/openstock/docs/DATA_CAPABILITY_SCOPE.md` 与 `GET /sources` 实测结果。

---

## 当前盲区

### 1. 期货数据 (FUTURES_*) — 暂不实现

| 字段 | 值 |
|---|---|
| 业务用途 | 量化策略中的股指期货对冲、基差套利、跨期套利 |
| 当前实现 | `config/data_sources_registry.yaml` 中 `akshare_futures_*` 4 个 entry |
| 状态 | 📝 项目按用户决策暂不实现期货功能,等 OpenStock 补全后再启用 |
| 期望 OpenStock category | `FUTURES_QUOTES` / `FUTURES_KLINES` / `FUTURES_BASIS` / `FUTURES_MAIN_CONTRACT` |
| 字段清单 | symbol, time, open, high, low, close, volume, amount, open_interest, settle, pre_settle |
| 调用频率 | 低(日级,非高频) |
| 历史回溯 | 是,至少 5 年 |
| 上游 akshare 接口参考 | `akshare.futures_zh_daily_sina`, `akshare.futures_main_sina`, `akshare.futures_basis` |

### 2. 融资融券数据 (MARGIN_*) — 待迁移

| 字段 | 值 |
|---|---|
| 业务用途 | 衡量市场杠杆情绪、做空压力、资金面分析 |
| 当前实现 | `config/data_sources_registry.yaml` 中 5 个 entry: `akshare_margin_account_info` / `akshare_margin_detail_sse` / `akshare_margin_detail_szse` / `akshare_margin_summary_sse` / `akshare_margin_summary_szse` |
| 状态 | 🚧 待 OpenStock 补 category 后迁移 |
| 期望 OpenStock category | `MARGIN_DETAIL_SSE` / `MARGIN_DETAIL_SZSE` / `MARGIN_SUMMARY_SSE` / `MARGIN_SUMMARY_SZSE` / `MARGIN_ACCOUNT_INFO` |
| 字段清单 | date, symbol, rzye(融资余额), rzmre(融资买入额), rqye(融券余额), rqmcl(融券卖出量), rzrqye(融资融券余额) |
| 调用频率 | 日级(每个交易日收盘后) |
| 历史回溯 | 是,至少 3 年 |
| 上游 akshare 接口参考 | `akshare.stock_margin_account_info`, `akshare.stock_margin_detail_sse`, `akshare.stock_margin_detail_szse`, `akshare.stock_margin_underlying_info_szse` |

### 3. 沪深交易所成交统计 (EXCHANGE_STATS_*) — 待迁移

| 字段 | 值 |
|---|---|
| 业务用途 | 市场总貌分析、板块轮动识别、地区交易热度排名 |
| 当前实现 | `config/data_sources_registry.yaml` 中 5 个 entry: `akshare_sse_daily_deal` / `akshare_sse_market_summary` / `akshare_szse_area_trading` / `akshare_szse_market_summary` / `akshare_szse_sector_trading` |
| 状态 | 🚧 待 OpenStock 补 category 后迁移 |
| 期望 OpenStock category | `SSE_DAILY_DEAL` / `SSE_MARKET_SUMMARY` / `SZSE_AREA_TRADING` / `SZSE_MARKET_SUMMARY` / `SZSE_SECTOR_TRADING` |
| 字段清单 | date, total_turnover, total_volume, up_count, down_count, flat_count, limit_up_count, limit_down_count, area_name, sector_name |
| 调用频率 | 日级 |
| 历史回溯 | 是,至少 5 年 |
| 上游 akshare 接口参考 | `akshare.sse_daily_deal`, `akshare.sse_market_summary`, `akshare.szse_area_trading`, `akshare.szse_market_summary`, `akshare.szse_sector_summary` |

### 4. 可转债详情 (CONVERTIBLE_BOND_DETAILS) — 不再列入

按 2026-07-07 用户决策,本项目暂不开发可转债新功能。现有 `src/adapters/efinance_adapter/efinance_bond_helpers.py` 等占位代码**保留但不开发、不删除**,等 OpenStock 补 `CONVERTIBLE_BOND_KLINES` / `CONVERTIBLE_BOND_TERMS` 后再评估是否迁移。本条不构成对 OpenStock 的强需求。

---

## 已退出盲区(归档)

_(暂无。OpenStock 项目补全后,在此处记录迁移日期与对应 PR。)_

---

## 新增盲区的流程

1. **登记**: 在上方表格添加新条目,字段必填(业务用途、字段清单、调用频率、历史回溯、上游参考)
2. **加注释**: 在源码对应 import 处加 `# OPENSTOCK_GAP: <gap-name> — see docs/reports/openstock-coverage-gaps.md`
3. **告知**: 提 issue 到 OpenStock 项目(或在协作群同步)
4. **迁移**: OpenStock 实现后,改 Adapter 调用,从本清单移到"已退出盲区"

## 例外: 永不迁移项

以下数据需求**永远不走 OpenStock**,因为 OpenStock 文档明确不在其范围:

- **本地终端数据源**(TdxQuant / miniQMT)— 由 `windows_distributed_bridge` registry entry 单独处理
- **交易执行**(下单/撤单/持仓/资金/账户状态)— 项目自有交易模块
- **TDengine 入仓** — 消费端自行写库,OpenStock 只负责拉数
