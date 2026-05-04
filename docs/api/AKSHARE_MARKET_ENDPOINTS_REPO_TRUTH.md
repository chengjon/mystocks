# AkShare 市场扩充接口 Repo-Truth 清单

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

> **当前实现说明**:
> 本文件用于描述 `expand-akshare-data-sources` 在当前仓库内已经落地的 AkShare 市场扩充接口，不是历史总结，也不是未来计划。
> 若与 `docs/api/AKSHARE_INTERFACE_MAPPING.md` 或历史报告冲突，应以当前代码、OpenSpec 台账与本文件为准。

**最后更新**: 2026-05-03

## 1. 市场总貌

| OpenSpec | AkShare | API 路径 | Adapter |
|---|---|---|---|
| 1.1 | `stock_sse_summary` | `/api/akshare/market/sse/overview` | `get_market_overview_sse()` |
| 1.2 | `stock_szse_summary` | `/api/akshare/market/szse/overview` | `get_market_overview_szse()` |
| 1.3 | `stock_szse_area_summary` | `/api/akshare/market/szse/area-trading` | `get_szse_area_trading_summary()` |
| 1.4 | `stock_szse_sector_summary` | `/api/akshare/market/szse/sector-trading` | `get_szse_sector_trading_summary()` |
| 1.5 | `stock_sse_deal_daily` | `/api/akshare/market/sse/daily-deal` | `get_sse_daily_deal_summary()` |

## 2. 个股信息

| OpenSpec | AkShare | API 路径 | Adapter |
|---|---|---|---|
| 2.1 | `stock_individual_info_em` | `/api/akshare/market/stock/individual-info/em` | `get_stock_individual_info_em()` |
| 2.2 | `stock_individual_basic_info_xq` | `/api/akshare/market/stock/individual-info/xq` | `get_stock_individual_basic_info_xq()` |
| 2.3 | `stock_zyjs_ths` | `/api/akshare/market/stock/business-intro/ths` | `get_stock_zyjs_ths()` |
| 2.4 | `stock_zygc_em` | `/api/akshare/market/stock/business-composition/em` | `get_stock_zygc_em()` |
| 2.5 | `stock_comment_em` | `/api/akshare/market/stock/comment/em` | `get_stock_comment_em()` |
| 2.6 | `stock_comment_detail_zlkp_jgcyd_em` | `/api/akshare/market/stock/comment-detail/em` | `get_stock_comment_detail_zlkp_jgcyd_em()` |
| 2.7 | `stock_news_em` | `/api/akshare/market/stock/news/em` | `get_stock_news_em()` |
| 2.8 | `stock_bid_ask_em` | `/api/akshare/market/stock/bid-ask/em` | `get_stock_bid_ask_em()` |

## 3. 资金流向

| OpenSpec | AkShare | API 路径 | Adapter |
|---|---|---|---|
| 3.1 | `stock_hsgt_fund_flow_summary_em` | `/api/akshare/market/fund-flow/hsgt-summary` | `get_stock_hsgt_fund_flow_summary_em()` |
| 3.2 | `stock_hsgt_fund_flow_detail_em` | `/api/akshare/market/fund-flow/hsgt-detail` | `get_stock_hsgt_fund_flow_detail_em()` |
| 3.3 | `stock_hsgt_north_net_flow_in_em` | `/api/akshare/market/fund-flow/north-daily` | `get_stock_hsgt_north_net_flow_in_em()` |
| 3.4 | `stock_hsgt_south_net_flow_in_em` | `/api/akshare/market/fund-flow/south-daily` | `get_stock_hsgt_south_net_flow_in_em()` |
| 3.5 | `stock_hsgt_north_acc_flow_in_em` | `/api/akshare/market/fund-flow/north-stock/{symbol}` | `get_stock_hsgt_north_acc_flow_in_em()` |
| 3.6 | `stock_hsgt_south_acc_flow_in_em` | `/api/akshare/market/fund-flow/south-stock/{symbol}` | `get_stock_hsgt_south_acc_flow_in_em()` |
| 3.7 | `stock_hsgt_hold_stock_em` | `/api/akshare/market/fund-flow/hsgt-holdings/{symbol}` | `get_stock_hsgt_hold_stock_em()` |
| 3.8 | `stock_fund_flow_big_deal` | `/api/akshare/market/fund-flow/big-deal` | `get_stock_fund_flow_big_deal()` |
| 3.9 | `stock_cyq_em` | `/api/akshare/market/chip-distribution/{symbol}` | `get_stock_cyq_em()` |

## 4. 预测和分析

| OpenSpec | AkShare | API 路径 | Adapter |
|---|---|---|---|
| 4.1 | `stock_profit_forecast_em` | `/api/akshare/market/forecast/profit/em/{symbol}` | `get_stock_profit_forecast_em()` |
| 4.2 | `stock_profit_forecast_ths` | `/api/akshare/market/forecast/profit/ths/{symbol}` | `get_stock_profit_forecast_ths()` |
| 4.3 | `stock_technical_indicator_em` | `/api/akshare/market/technical/indicators/em/{symbol}` | `get_stock_technical_indicator_em()` |
| 4.4 | `stock_account_statistics_em` | `/api/akshare/market/market/account-statistics` | `get_stock_account_statistics_em()` |

## 5. 板块和行业

| OpenSpec | AkShare | API 路径 | Adapter |
|---|---|---|---|
| 5.1 | `stock_board_concept_cons_em` | `/api/akshare/market/board/concept/cons/{symbol}` | `get_stock_board_concept_cons_em()` |
| 5.2 | `stock_board_concept_hist_em` | `/api/akshare/market/board/concept/history/{symbol}` | `get_stock_board_concept_hist_em()` |
| 5.3 | `stock_board_concept_hist_min_em` | `/api/akshare/market/board/concept/minute/{symbol}` | `get_stock_board_concept_hist_min_em()` |
| 5.4 | `stock_board_industry_cons_em` | `/api/akshare/market/board/industry/cons/{symbol}` | `get_stock_board_industry_cons_em()` |
| 5.5 | `stock_board_industry_hist_em` | `/api/akshare/market/board/industry/history/{symbol}` | `get_stock_board_industry_hist_em()` |
| 5.6 | `stock_board_industry_hist_min_em` | `/api/akshare/market/board/industry/minute/{symbol}` | `get_stock_board_industry_hist_min_em()` |
| 5.7 | `stock_sector_spot_em` | `/api/akshare/market/sector/hot-ranking` | `get_stock_sector_spot_em()` |
| 5.8 | `stock_sector_fund_flow_rank_em` | `/api/akshare/market/sector/fund-flow-ranking` | `get_stock_sector_fund_flow_rank_em()` |

## 6. 行情和情绪

| OpenSpec | AkShare | API 路径 | Adapter | 状态 |
|---|---|---|---|---|
| 6.1 | `stock_hot_follow_xq` | `/api/akshare/market/stock/hot-follow/xq` | `get_stock_hot_follow_xq()` | 已实现 |
| 6.2 | `stock_board_change_em` | `/api/akshare/market/board/change/em` | `get_stock_board_change_em()` | 已实现 |
| 6.3 | `stock_news_main_em` | - | - | 本地 `akshare` 未检出同名函数 |
| 6.4 | `stock_zt_pool_em` | `/api/akshare/market/stock/zt-pool/em` | `get_stock_zt_pool_em()` | 已实现 |
| 6.5 | `stock_dt_pool_em` | `/api/akshare/market/stock/dt-pool/em` | `get_stock_dt_pool_em()` | 已实现（官方改名映射：stock_zt_pool_dtgc_em） |
| 6.6 | `stock_strong_pool_em` | `/api/akshare/market/stock/strong-pool/em` | `get_stock_strong_pool_em()` | 已实现（官方改名映射：stock_zt_pool_strong_em） |
| 6.7 | `stock_weak_pool_em` | - | - | 本地 `akshare` 未检出同名函数 |
| 6.8 | `stock_changes_em` | `/api/akshare/market/stock/changes/em` | `get_stock_changes_em()` | 已实现 |
| 6.9 | `stock_new_em` | - | - | 本地 `akshare` 未检出同名函数 |

## 7. 历史文档边界

以下文档不应再直接当作当前 repo-truth：

- `docs/api/AKSHARE_INTERFACE_MAPPING.md`
- `docs/reports/AKSHARE_DATA_SOURCE_API_SUMMARY.md`

它们可用来理解历史设计或交付快照，但当前实现事实应回到本文件、OpenSpec 台账和当前代码。

## 8. 推荐验证入口

在推进 `expand-akshare-data-sources` 第 6 节相关工作前，优先运行 wrapper：

```bash
python scripts/dev/quality_gate/run_akshare_market_gates.py \
  --output-dir /tmp/akshare-market-gates
```

解释：

- `akshare-market-function-availability.json` 回答“当前本地 `akshare` 有哪些同名函数”
- `akshare-market-repo-truth-gate.json` 回答“当前仓库的 OpenSpec / repo-truth / registry / adapter / route / focused tests 是否与这个现实一致”
- `akshare-market-gates-summary.json` 给出统一 pass/fail 汇总，供 runtime / CI 直接消费

如需拆分诊断，再单独运行叶子脚本：

```bash
python scripts/dev/quality_gate/collect_akshare_market_function_availability.py \
  --output /tmp/akshare-market-function-availability.json
python scripts/dev/quality_gate/validate_akshare_market_repo_truth.py \
  --output /tmp/akshare-market-repo-truth-gate.json
```

wrapper 通过以后，才适合把某个 `False -> True` 的函数拉入单接口微批次。
