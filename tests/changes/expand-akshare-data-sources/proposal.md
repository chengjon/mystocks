# Change: expand-akshare-data-sources

> **专题方案说明**:
> 本文件用于描述某项测试能力、测试契约、测试规格或变更提案的边界与要求，服务于测试方案管理和差异追踪。
> 它不自动等同于当前已落地测试实现或当前运行结果；执行时需同时核对 `architecture/STANDARDS.md`、当前代码实现、测试脚本与最新验证结果。


## Why
MyStocks项目当前已支持akshare数据源的基础功能，但akshare库提供了丰富的金融数据接口，包括股票市场总貌、个股新闻、资金流向、筹码分布、盈利预测、概念板块、行业板块、股票热度、盘口异动、涨停板行情、技术指标等20+个重要数据类别。目前仅实现了融资融券、龙虎榜和股指期货等少数功能，缺失大量关键数据源，导致量化分析和策略开发能力受限。

## What Changes
- **数据源扩充**: 在akshare市场适配器中分批增加20+个新的数据接口
- **市场总貌**: 上海/深圳交易所统计数据、地区交易排序
- **个股信息**: 主营介绍、主营构成、千股千评、个股新闻、盘口报价
- **资金数据**: 沪深港通资金流向、大单统计、筹码分布
- **预测数据**: 盈利预测（东方财富、同花顺）、技术指标、股票账户统计
- **板块数据**: 概念板块、行业板块、行业热度排行、行业资金流向排行
- **行情/情绪扩充**: 财经内容精选、涨跌停股池、强弱股池、盘口异动、次新股池等后续接口
- **配置更新**: 在 `config/data_sources_registry.yaml` 中注册已实现接口，并为剩余接口保留扩充空间
- **API端点**: 为已实现数据类别创建 `/api/akshare/market/*` RESTful API端点

## Impact
- Affected specs: data-sources, market-data, financial-data, news-data
- Affected code: `src/adapters/akshare/market_adapter/`, `web/backend/app/api/akshare_market/`, `config/data_sources_registry.yaml`, `tests/adapters/test_akshare_adapter/`, `tests/api/test_akshare_market_file.py`
- New endpoints: `/api/akshare/market/sse/*`, `/api/akshare/market/szse/*`, `/api/akshare/market/stock-info/*`, `/api/akshare/market/fund-flow/*`, `/api/akshare/market/forecast/*`, `/api/akshare/market/sector/*`
- Data volume: 新增每日数百万条数据处理能力
- Performance: 需要评估对缓存和数据库性能的影响
