## 1. 市场总貌数据扩充 ✅ 完成

> **使用说明**:
> 本文件用于记录当前 OpenSpec 变更的执行清单、操作步骤或协作约束，帮助跟踪实施过程。
> 其中勾选状态、执行顺序和局部说明仅代表任务推进视角，不应脱离 proposal、design、正式 specs、`architecture/STANDARDS.md` 与实际验证结果单独解读为最终事实。

- [x] 1.1 实现上海证券交易所市场总貌数据 (akshare.stock_sse_summary)
- [x] 1.2 实现深圳证券交易所市场总貌数据 (akshare.stock_szse_summary)
- [x] 1.3 实现深圳证券交易所地区交易排序数据 (akshare.stock_szse_area_summary)
- [x] 1.4 实现深圳证券交易所股票行业成交数据 (akshare.stock_szse_sector_summary)
- [x] 1.5 实现上海证券交易所每日概况数据 (akshare.stock_sse_deal_daily)
- [x] 1.6 添加市场总貌数据到数据源配置注册表
- [x] 1.7 创建市场总貌数据的API端点
- [x] 1.8 编写市场总貌数据的单元测试

## 2. 个股信息数据扩充 ✅ 完成
- [x] 2.1 实现个股信息查询-东财 (akshare.stock_individual_info_em)
- [x] 2.2 实现个股信息查询-雪球 (akshare.stock_individual_basic_info_xq)
- [x] 2.3 实现主营介绍-同花顺 (akshare.stock_zyjs_ths)
- [x] 2.4 实现主营构成-东财 (akshare.stock_zygc_em)
- [x] 2.5 实现千股千评 (akshare.stock_comment_em)
- [x] 2.6 实现千股千评详情 (akshare.stock_comment_detail_zlkp_jgcyd_em)
- [x] 2.7 实现个股新闻 (akshare.stock_news_em)
- [x] 2.8 实现行情报价 (akshare.stock_bid_ask_em)
- [x] 2.9 添加个股信息数据到数据源配置注册表
- [x] 2.10 创建个股信息数据的API端点
- [x] 2.11 编写个股信息数据的单元测试

## 3. 资金流向数据扩充 ✅ 完成
- [x] 3.1 实现沪深港通资金流向 (akshare.stock_hsgt_fund_flow_summary_em)
- [x] 3.2 实现沪深港通资金流向明细 (akshare.stock_hsgt_fund_flow_detail_em)
- [x] 3.3 实现北向资金每日统计 (akshare.stock_hsgt_north_net_flow_in_em)
- [x] 3.4 实现南向资金每日统计 (akshare.stock_hsgt_south_net_flow_in_em)
- [x] 3.5 实现北向资金个股统计 (akshare.stock_hsgt_north_acc_flow_in_em)
- [x] 3.6 实现南向资金个股统计 (akshare.stock_hsgt_south_acc_flow_in_em)
- [x] 3.7 实现沪深港通持股明细 (akshare.stock_hsgt_hold_stock_em)
- [x] 3.8 实现资金流向大单统计 (akshare.stock_fund_flow_big_deal)
- [x] 3.9 实现筹码分布数据 (akshare.stock_cyq_em)
- [x] 3.10 添加资金流向数据到数据源配置注册表
- [x] 3.11 创建资金流向数据的API端点
- [x] 3.12 编写资金流向数据的单元测试

## 4. 预测和分析数据扩充 ✅ 完成
- [x] 4.1 实现盈利预测-东方财富 (akshare.stock_profit_forecast_em)
- [x] 4.2 实现盈利预测-同花顺 (akshare.stock_profit_forecast_ths)
- [x] 4.3 实现技术指标数据 (akshare.stock_technical_indicator_em)
- [x] 4.4 实现股票账户统计月度 (akshare.stock_account_statistics_em)
- [x] 4.5 添加预测和分析数据到数据源配置注册表
- [x] 4.6 创建预测和分析数据的API端点
- [x] 4.7 编写预测和分析数据的单元测试

## 5. 板块和行业数据扩充 ✅ 完成
> **仓库事实校对（2026-04-27）**:
> `src/adapters/akshare/market_adapter/board_sector.py`、`web/backend/app/api/akshare_market/boards.py`、`config/data_sources_registry.yaml` 与 `tests/adapters/test_akshare_adapter/test_akshare_market_data_adapter_methods/part2.py` 已覆盖本节当前实现。
> 当前仓库落地的是 `akshare.stock_sector_spot_em` 与 `akshare.stock_sector_fund_flow_rank_em`，与 proposal 初稿中的 `stock_hot_follow_xq`、`stock_board_change_em` 存在 scope 漂移；原始情绪/异动接口转入第 6 节继续跟踪。

- [x] 5.1 实现概念板块成分股 (akshare.stock_board_concept_cons_em)
- [x] 5.2 实现概念板块行情 (akshare.stock_board_concept_hist_em)
- [x] 5.3 实现概念板块历史行情 (akshare.stock_board_concept_hist_min_em)
- [x] 5.4 实现行业板块成分股 (akshare.stock_board_industry_cons_em)
- [x] 5.5 实现行业板块行情 (akshare.stock_board_industry_hist_em)
- [x] 5.6 实现行业板块历史行情 (akshare.stock_board_industry_hist_min_em)
- [x] 5.7 实现热门行业排行 (akshare.stock_sector_spot_em)
- [x] 5.8 实现行业资金流向 (akshare.stock_sector_fund_flow_rank_em)
- [x] 5.9 添加板块和行业数据到数据源配置注册表
- [x] 5.10 创建板块和行业数据的API端点
- [x] 5.11 编写板块和行业数据的单元测试

## 6. 行情和情绪数据待补齐
> **仓库事实校对（2026-04-28）**:
> 在 2026-04-28 的盘点时，当前 AkShare 市场适配器 / API / 配置注册表 / 测试链路中，未检出 `stock_hot_follow_xq`、`stock_board_change_em`、`stock_news_main_em`、`stock_zt_pool_em`、`stock_dt_pool_em`、`stock_strong_pool_em`、`stock_weak_pool_em`、`stock_changes_em`、`stock_new_em` 的现行实现痕迹。
> `src/adapters/akshare/market_adapter/stock_sentiment.py` 当前仅覆盖第 2 节已完成的 `stock_comment_em`、`stock_comment_detail_zlkp_jgcyd_em`、`stock_news_em`、`stock_bid_ask_em`。
> 仓库虽在其他模块存在相邻能力（如 `byapi` 的涨跌停股池、`wencai` 的强势股查询），但它们不属于本 change 要求的 AkShare 市场适配器 / API / registry / test 闭环，不能外推为 6.1-6.12 已完成。
> **仓库事实校对（2026-05-03）**:
> 当前仓库已补齐本地 `akshare` 版本中可直接确认存在的 `stock_hot_follow_xq`、`stock_board_change_em`、`stock_zt_pool_em`、`stock_changes_em`，落点分别为 `src/adapters/akshare/market_adapter/stock_sentiment.py`、`web/backend/app/api/akshare_market/sentiment_monitor.py`、`config/data_sources_registry.yaml`，并由 `tests/unit/adapters/test_akshare_stock_sentiment_incremental.py` 与 `tests/backend/test_akshare_market_additional_routes.py` 提供 focused 验证。
> 当前 canonical truth 仍以 `435bc8f00` 落地的 same-name gate baseline 为起点；但本轮已单独批准并落地 `stock_dt_pool_em -> stock_zt_pool_dtgc_em` 的官方改名映射，因此 6.5 已转为完成状态。
> 在此基础上，本轮继续批准并落地 `stock_strong_pool_em -> stock_zt_pool_strong_em` 的官方改名映射，因此 6.6 也已转为完成状态。
> 当前本地 `akshare` 环境仍未检出 `stock_news_main_em`、`stock_weak_pool_em`、`stock_new_em` 的可接受实现；`help_candidates` 对这些条目仍只作为人工评估线索，不自动计为实现完成。

- [x] 6.1 实现股票热度数据 (akshare.stock_hot_follow_xq)
- [x] 6.2 实现板块异动详情 (akshare.stock_board_change_em)
- [ ] 6.3 实现财经内容精选 (akshare.stock_news_main_em)
- [x] 6.4 实现涨停板行情 (akshare.stock_zt_pool_em)
- [x] 6.5 实现跌停板行情 (akshare.stock_dt_pool_em)
- [x] 6.6 实现强势股池 (akshare.stock_strong_pool_em)
- [ ] 6.7 实现弱势股池 (akshare.stock_weak_pool_em)
  - Gap closure criteria：仅当本地 AkShare 恢复同名函数、或找到经单独批准的新官方候选、或业务明确决定下线该能力时，才允许退出当前 unresolved gap 状态
- [x] 6.8 实现盘口异动 (akshare.stock_changes_em)
- [ ] 6.9 实现次新股池 (akshare.stock_new_em)
  - Repo-truth 方案说明：当前仅把以下映射视为“可讨论的官方改名候选”，尚未批准实现：
    - `stock_new_em` -> `stock_zt_pool_sub_new_em`
    - `stock_zt_pool_previous_em`、`stock_zt_pool_zbgc_em` 已纳入评估，但当前没有对应 OpenSpec 条目
    - `stock_news_main_em` -> `stock_news_main_cx` 明确排除
    - `stock_weak_pool_em` 继续保持无候选 gap
  - Promotion rule：若未来批准任一 retained candidate，必须单独微批同时更新 OpenSpec、repo-truth、gate、runtime code 与 focused tests
- [ ] 6.10 添加行情和情绪数据到数据源配置注册表
- [ ] 6.11 创建行情和情绪数据的API端点
- [ ] 6.12 编写行情和情绪数据的单元测试
  - [ ] Repo-truth：当前 registry / API / focused tests 已闭合 6.1 / 6.2 / 6.4 / 6.5 / 6.6 / 6.8；在 6.3 / 6.7 / 6.9 仍未实现前，不将本节统一收口任务勾选完成。
  - [ ] Promotion sequencing：如继续启动 retained candidate 提升，顺序固定为 `6.9 new`；`6.3` 维持 excluded，`6.7` 维持 unresolved gap，直到另有单独批准

## 7. 系统集成和优化
> **仓库事实校对（2026-04-27）**:
> 适配器聚合入口已在 `src/adapters/akshare/market_adapter/adapter.py` 完成 mixin 组合，API 路由已在 `web/backend/app/api/akshare_market/__init__.py` 与 `web/backend/app/router_registry.py` 注册。
> 本节保持未完成，直到第 6 节剩余接口补齐并重新验证所有集成收口项。
> 另据 `tests/api/file_tests/test_akshare_market_api.py`，现有 `test_smart_cache_integration()` 仍是注释型占位断言，不足以证明第 6 节新增接口的缓存策略优化已经落地；当前也未见面向这些剩余接口的多股票批量请求实现/测试闭环，因此 7.4 / 7.5 继续保留未完成。
> **仓库事实校对（2026-05-03）**:
> `scripts/dev/quality_gate/run_akshare_market_gates.py` 已将“本地同名函数可用性探测 + repo-truth 一致性校验”收口为统一 audit-only 入口，并接入 `scripts/run_runtime_delivery_summary_local.sh`、`.github/workflows/frontend-testing.yml` 与 `scripts/dev/quality_gate/build_runtime_ci_bundle.py` 的汇总链路。
> 该门禁只产出校验 / 审计报告，不自动生成业务代码，也不代表 7.4 / 7.5 的缓存 / 批量优化已经落地。

- [x] 7.1 更新适配器聚合入口，纳入新增市场 mixin
- [ ] 7.2 更新数据源配置注册表，补齐剩余接口的质量规则
- [x] 7.3 更新API路由文件，注册已实现端点
- [ ] 7.4 实现数据缓存策略优化，避免重复API调用
- [ ] 7.5 实现批量数据请求优化，支持多股票同时查询
- [x] 7.6 更新项目文档，添加新数据源的使用说明
  - [x] Repo-truth：通用接入指南不再是唯一依据；当前专题使用说明已明确落到 `docs/guides/akshare/AKSHARE_MARKET_EXTENSION_GUIDE.md`，历史 `docs/api/AKSHARE_INTERFACE_MAPPING.md` 仅作为快照 / 设计材料保留，不能单独充当完成证据。
  - [x] Repo-truth：当前专题使用说明已落到 `docs/guides/akshare/AKSHARE_MARKET_EXTENSION_GUIDE.md`，并由 `docs/guides/akshare/INDEX.md` 与 `docs/guides/data-source/INDEX.md` 提供入口。

## 8. 测试和验证
> **仓库事实校对（2026-04-27）**:
> 适配器层已有 `tests/adapters/test_akshare_adapter/test_akshare_market_data_adapter_methods/part1.py`、`part2.py`、`part3.py`，API侧已有 `tests/api/test_akshare_market_file.py` 覆盖已实现子集。
> 由于第 6 节原始 scope 仍未落地，本节继续保留为未完成状态。
> **仓库事实校对（2026-05-03）**:
> `tests/unit/scripts/test_collect_akshare_market_function_availability.py`、`tests/unit/scripts/test_validate_akshare_market_repo_truth.py`、`tests/unit/scripts/test_run_akshare_market_gates.py`、`tests/unit/scripts/test_frontend_testing_akshare_runtime_gate.py`、`tests/performance/test_build_runtime_ci_bundle.py`、`tests/performance/test_runtime_delivery_summary_local_script.py` 已覆盖门禁叶子脚本、wrapper 入口以及 runtime / CI 汇总链路的审计能力。
> 这些验证只证明“校验 / 报告闭环”可运行，不外推为剩余 AkShare 业务接口、缓存优化、批量请求优化或端到端展示链路已经完成，因此 8.1-8.5 继续保留未完成。

- [ ] 8.1 补齐完整的单元测试套件，覆盖剩余接口与收口场景
- [ ] 8.2 执行集成测试，确保API端点正常工作
- [ ] 8.3 进行性能测试，评估新增接口对系统性能的影响
- [ ] 8.4 进行数据质量测试，确保返回数据的准确性和完整性
- [ ] 8.5 执行端到端测试，验证从数据获取到前端展示的完整流程

## 9. 文档和维护
> **仓库事实校对（2026-05-03）**:
> 当前与本 change 直接相关的文档层可分为三类：
> - 当前契约真相源：`docs/api/openapi.json` 已为 1-5 节已实现端点提供路径与描述
> - 当前专题真相源 / 维护入口：`docs/api/AKSHARE_MARKET_ENDPOINTS_REPO_TRUTH.md`、`docs/guides/akshare/AKSHARE_MARKET_EXTENSION_GUIDE.md`、`docs/guides/akshare/AKSHARE_MARKET_TROUBLESHOOTING.md`、`docs/guides/akshare/AKSHARE_MARKET_MAINTENANCE.md`、`docs/guides/akshare/INDEX.md`
> - 当前接入/开发通用指引入口：`docs/guides/NEW_API_SOURCE_INTEGRATION_GUIDE.md` 与 `docs/guides/data-source/NEW_API_SOURCE_INTEGRATION_GUIDE.md`
> - 历史/设计/总结材料：`docs/api/AKSHARE_INTERFACE_MAPPING.md`、`docs/reports/AKSHARE_DATA_SOURCE_API_SUMMARY.md`
> 文档层当前已经形成面向本 change 的专题闭环，并补充了 wrapper-first 的门禁执行口径；但这不外推为第 6 节剩余接口或第 7-8 节未完成能力已经实现。

- [x] 9.1 更新API文档，添加所有新端点的详细说明
- [x] 9.2 创建数据源使用指南，帮助开发者理解各个接口的用途
  - [x] Repo-truth：面向本次 AkShare 扩充接口集合的现行专题使用手册已落到 `docs/guides/akshare/AKSHARE_MARKET_EXTENSION_GUIDE.md`，并由 `docs/guides/akshare/INDEX.md` 暴露入口；历史 `AKSHARE_INTERFACE_MAPPING.md` 不能直接当作当前完成证据。
- [x] 9.3 编写数据更新频率和缓存策略说明
- [x] 9.4 创建故障排除指南，帮助处理常见问题
- [x] 9.5 编写维护手册，包括数据源更新和版本兼容性说明
  - [x] Repo-truth：当前专题文档入口为：
    - `docs/api/AKSHARE_MARKET_ENDPOINTS_REPO_TRUTH.md`
    - `docs/guides/akshare/AKSHARE_MARKET_EXTENSION_GUIDE.md`
    - `docs/guides/akshare/AKSHARE_MARKET_TROUBLESHOOTING.md`
    - `docs/guides/akshare/AKSHARE_MARKET_MAINTENANCE.md`
