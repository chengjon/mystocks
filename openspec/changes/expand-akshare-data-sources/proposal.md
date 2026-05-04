# Change: expand-akshare-data-sources

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。


## Why
MyStocks项目当前已支持akshare数据源的基础功能，但akshare库提供了丰富的金融数据接口，包括股票市场总貌、个股新闻、资金流向、筹码分布、盈利预测、概念板块、行业板块、股票热度、盘口异动、涨停板行情、技术指标等20+个重要数据类别。目前仅实现了融资融券、龙虎榜和股指期货等少数功能，缺失大量关键数据源，导致量化分析和策略开发能力受限。

## What Changes
- **数据源扩充**: 在 akshare 市场适配器中按本地可用性分批增加 20+ 个候选接口，但 MyStocks 仅接入当前环境里已存在的同名 AkShare 函数
- **市场总貌**: 上海/深圳交易所统计数据、地区交易排序
- **个股信息**: 主营介绍、主营构成、千股千评、个股新闻、盘口报价
- **资金数据**: 沪深港通资金流向、大单统计、筹码分布
- **预测数据**: 盈利预测（东方财富、同花顺）、技术指标、股票账户统计
- **板块数据**: 概念板块、行业板块、行业热度排行、行业资金流向排行
- **行情/情绪扩充**: 财经内容精选、涨跌停股池、强弱股池、盘口异动、次新股池等后续接口
- **配置更新**: 在 `config/data_sources_registry.yaml` 中注册已实现接口，并为剩余接口保留扩充空间
- **API端点**: 为已实现数据类别创建 `/api/akshare/market/*` RESTful API端点
- **边界门禁**: 新增本地 same-name 函数可用性探测与 repo-truth 一致性门禁，仅做校验 / 审计 / 报告，不自动生成业务代码
- **职责拆分**: 缺失函数保持 gap，不在 MyStocks 内用近似接口、第三方非同源接口或 `akquant` 逻辑替代实现
- **官方改名映射收口**: 已批准并落地 `stock_dt_pool_em -> stock_zt_pool_dtgc_em`、`stock_strong_pool_em -> stock_zt_pool_strong_em`、`stock_new_em -> stock_zt_pool_sub_new_em`
- **显式排除项**: `stock_news_main_em` 因候选能力漂移到财新来源而不纳入当前 runtime scope；`stock_weak_pool_em` 因业务已决定不再承接且当前未找到明确候选，转为 retired / removed with reason；`stock_zh_a_new_em` 因语义更接近“新股”而非“次新股池”不纳入 6.9 候选

## Impact
- Affected specs: data-sources, market-data, financial-data, news-data
- Affected code: `src/adapters/akshare/market_adapter/`, `web/backend/app/api/akshare_market/`, `config/data_sources_registry.yaml`, `scripts/dev/quality_gate/`, `tests/adapters/test_akshare_adapter/`, `tests/unit/scripts/`, `tests/performance/`
- New endpoints: `/api/akshare/market/sse/*`, `/api/akshare/market/szse/*`, `/api/akshare/market/stock-info/*`, `/api/akshare/market/fund-flow/*`, `/api/akshare/market/forecast/*`, `/api/akshare/market/sector/*`
- Data volume: 新增每日数百万条数据处理能力
- Performance: 需要评估对缓存和数据库性能的影响
- Proposal status: 当前 canonical truth 起点仍是 `435bc8f00` 落地的 same-name gate baseline；其后已完成 `dt / strong / new` 三条官方改名映射落地，并将 `stock_weak_pool_em` 正式收口为 retired item；当前仅 `stock_news_main_em` 继续保持 excluded
