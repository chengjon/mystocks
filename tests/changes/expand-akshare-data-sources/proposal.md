# Change: expand-akshare-data-sources

## Why
MyStocks项目当前已支持akshare数据源的基础功能，但akshare库提供了丰富的金融数据接口，包括股票市场总貌、个股新闻、资金流向、筹码分布、盈利预测、概念板块、行业板块、股票热度、盘口异动、涨停板行情、技术指标等20+个重要数据类别。目前仅实现了融资融券、龙虎榜和股指期货等少数功能，缺失大量关键数据源，导致量化分析和策略开发能力受限。

## What Changes
- **数据源扩充**: 在akshare适配器中增加20个新的数据接口
- **市场总貌**: 上海/深圳交易所统计数据、地区交易排序
- **个股信息**: 主营介绍、主营构成、千股千评、个股新闻
- **资金数据**: 沪深港通资金流向、资金流向、筹码分布
- **预测数据**: 盈利预测(东方财富、同花顺)、技术指标
- **板块数据**: 概念板块、行业板块、股票热度、盘口异动
- **行情数据**: 涨停板行情、财经内容精选
- **配置更新**: 在data_sources_registry.yaml中注册所有新接口
- **API端点**: 为所有新数据创建对应的RESTful API端点

## Impact
- Affected specs: data-sources, market-data, financial-data, news-data
- Affected code: src/adapters/akshare/, web/backend/app/api/efinance.py, config/data_sources_registry.yaml
- New endpoints: 20+个新API端点 (/api/efinance/stock/market-overview, /api/efinance/stock/main-business等)
- Data volume: 新增每日数百万条数据处理能力
- Performance: 需要评估对缓存和数据库性能的影响</content>
<parameter name="filePath">openspec/changes/expand-akshare-data-sources/proposal.md
