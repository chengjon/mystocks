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
> 在当前 AkShare 市场适配器 / API / 配置注册表 / 测试链路中，未检出 `stock_hot_follow_xq`、`stock_board_change_em`、`stock_news_main_em`、`stock_zt_pool_em`、`stock_dt_pool_em`、`stock_strong_pool_em`、`stock_weak_pool_em`、`stock_changes_em`、`stock_new_em` 的现行实现痕迹。
> `src/adapters/akshare/market_adapter/stock_sentiment.py` 当前仅覆盖第 2 节已完成的 `stock_comment_em`、`stock_comment_detail_zlkp_jgcyd_em`、`stock_news_em`、`stock_bid_ask_em`。
> 仓库虽在其他模块存在相邻能力（如 `byapi` 的涨跌停股池、`wencai` 的强势股查询），但它们不属于本 change 要求的 AkShare 市场适配器 / API / registry / test 闭环，不能外推为 6.1-6.12 已完成。

- [ ] 6.1 实现股票热度数据 (akshare.stock_hot_follow_xq)
- [ ] 6.2 实现板块异动详情 (akshare.stock_board_change_em)
- [ ] 6.3 实现财经内容精选 (akshare.stock_news_main_em)
- [ ] 6.4 实现涨停板行情 (akshare.stock_zt_pool_em)
- [ ] 6.5 实现跌停板行情 (akshare.stock_dt_pool_em)
- [ ] 6.6 实现强势股池 (akshare.stock_strong_pool_em)
- [ ] 6.7 实现弱势股池 (akshare.stock_weak_pool_em)
- [ ] 6.8 实现盘口异动 (akshare.stock_changes_em)
- [ ] 6.9 实现次新股池 (akshare.stock_new_em)
- [ ] 6.10 添加行情和情绪数据到数据源配置注册表
- [ ] 6.11 创建行情和情绪数据的API端点
- [ ] 6.12 编写行情和情绪数据的单元测试

## 7. 系统集成和优化
> **仓库事实校对（2026-04-27）**:
> 适配器聚合入口已在 `src/adapters/akshare/market_adapter/adapter.py` 完成 mixin 组合，API 路由已在 `web/backend/app/api/akshare_market/__init__.py` 与 `web/backend/app/router_registry.py` 注册。
> 本节保持未完成，直到第 6 节剩余接口补齐并重新验证所有集成收口项。
> 另据 `tests/api/file_tests/test_akshare_market_api.py`，现有 `test_smart_cache_integration()` 仍是注释型占位断言，不足以证明第 6 节新增接口的缓存策略优化已经落地；当前也未见面向这些剩余接口的多股票批量请求实现/测试闭环，因此 7.4 / 7.5 继续保留未完成。

- [x] 7.1 更新适配器聚合入口，纳入新增市场 mixin
- [ ] 7.2 更新数据源配置注册表，补齐剩余接口的质量规则
- [x] 7.3 更新API路由文件，注册已实现端点
- [ ] 7.4 实现数据缓存策略优化，避免重复API调用
- [ ] 7.5 实现批量数据请求优化，支持多股票同时查询
- [ ] 7.6 更新项目文档，添加新数据源的使用说明
  - [ ] Repo-truth：当前可确认的现行文档主要是 `docs/guides/NEW_API_SOURCE_INTEGRATION_GUIDE.md` 与 `docs/guides/data-source/NEW_API_SOURCE_INTEGRATION_GUIDE.md` 这类通用接入指南；`docs/api/AKSHARE_INTERFACE_MAPPING.md` 已明确标注为历史快照/设计映射，不足以作为本 change“新增数据源使用说明已更新完成”的闭环证据。

## 8. 测试和验证
> **仓库事实校对（2026-04-27）**:
> 适配器层已有 `tests/adapters/test_akshare_adapter/test_akshare_market_data_adapter_methods/part1.py`、`part2.py`、`part3.py`，API侧已有 `tests/api/test_akshare_market_file.py` 覆盖已实现子集。
> 由于第 6 节原始 scope 仍未落地，本节继续保留为未完成状态。

- [ ] 8.1 补齐完整的单元测试套件，覆盖剩余接口与收口场景
- [ ] 8.2 执行集成测试，确保API端点正常工作
- [ ] 8.3 进行性能测试，评估新增接口对系统性能的影响
- [ ] 8.4 进行数据质量测试，确保返回数据的准确性和完整性
- [ ] 8.5 执行端到端测试，验证从数据获取到前端展示的完整流程

## 9. 文档和维护
> **仓库事实校对（2026-04-27）**:
> 当前与本 change 直接相关的文档层可分为三类：
> - 当前契约真相源：`docs/api/openapi.json` 已为 1-5 节已实现端点提供路径与描述
> - 当前接入/开发指引入口：`docs/guides/NEW_API_SOURCE_INTEGRATION_GUIDE.md` 与 `docs/guides/data-source/NEW_API_SOURCE_INTEGRATION_GUIDE.md`
> - 历史/设计/总结材料：`docs/api/AKSHARE_INTERFACE_MAPPING.md`、`docs/reports/AKSHARE_DATA_SOURCE_API_SUMMARY.md`
> 由于第 6 节原始 scope 仍未落地，且当前未找到专门覆盖“更新频率与缓存策略 / 故障排除 / 维护手册”的现行 AkShare 专题文档闭环，本节继续保留未完成状态。

- [ ] 9.1 更新API文档，添加所有新端点的详细说明
- [ ] 9.2 创建数据源使用指南，帮助开发者理解各个接口的用途
  - [ ] Repo-truth：仓库当前存在的是通用 API / 数据源接入指南，而不是面向本次 AkShare 扩充接口集合的现行专题使用手册；历史 `AKSHARE_INTERFACE_MAPPING.md` 不能直接当作当前完成证据。
- [ ] 9.3 编写数据更新频率和缓存策略说明
- [ ] 9.4 创建故障排除指南，帮助处理常见问题
- [ ] 9.5 编写维护手册，包括数据源更新和版本兼容性说明
