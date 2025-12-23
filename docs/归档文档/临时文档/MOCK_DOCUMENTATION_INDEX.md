# Mock数据文件文档索引

**生成时间**: 2025-11-14
**总文件数**: 27

## 🏗️ 双层Mock架构说明

### JavaScript Mock文件 (前端)
- **位置**: `web/frontend/src/mock/`
- **用途**: Vue组件直接导入使用
- **格式**: JavaScript/ES6模块
- **状态**: 桥接文件已创建

### Python Mock文件 (后端)
- **位置**: `src/mock/`
- **用途**: 后端API开发和参考
- **格式**: Python源代码
- **状态**: 完整文档化 (27个文件)

## 📋 文件清单

| 序号 | 文件名 | 页面名称 | Vue文件 | 接口数量 | 状态 |
|------|--------|----------|---------|----------|------|
| 1 | `mock_Analysis.py` | Analysis | `Analysis.vue` | 3 | ✅ 已文档化 |
| 2 | `mock_BacktestAnalysis.py` | BacktestAnalysis | `BacktestAnalysis.vue` | 3 | ✅ 已文档化 |
| 3 | `mock_Dashboard.py` | Dashboard | `Dashboard.vue` | 10 | ✅ 已文档化 |
| 4 | `mock_IndicatorLibrary.py` | IndicatorLibrary | `IndicatorLibrary.vue` | 3 | ✅ 已文档化 |
| 5 | `mock_Login.py` | Login | `Login.vue` | 3 | ✅ 已文档化 |
| 6 | `mock_Market.py` | Market | `Market.vue` | 8 | ✅ 已文档化 |
| 7 | `mock_MarketData.py` | MarketData | `MarketData.vue` | 3 | ✅ 已文档化 |
| 8 | `mock_MarketDataView.py` | MarketDataView | `MarketDataView.vue` | 3 | ✅ 已文档化 |
| 9 | `mock_RealTimeMonitor.py` | RealTimeMonitor | `RealTimeMonitor.vue` | 3 | ✅ 已文档化 |
| 10 | `mock_RiskMonitor.py` | RiskMonitor | `RiskMonitor.vue` | 3 | ✅ 已文档化 |
| 11 | `mock_Settings.py` | Settings | `Settings.vue` | 3 | ✅ 已文档化 |
| 12 | `mock_StockSearch.py` | StockSearch | `StockSearch.vue` | 4 | ✅ 已文档化 |
| 13 | `mock_Stocks.py` | Stocks | `Stocks.vue` | 3 | ✅ 已文档化 |
| 14 | `mock_StrategyManagement.py` | StrategyManagement | `StrategyManagement.vue` | 6 | ✅ 已文档化 |
| 15 | `mock_TaskManagement.py` | TaskManagement | `TaskManagement.vue` | 3 | ✅ 已文档化 |
| 16 | `mock_TdxMarket.py` | TdxMarket | `TdxMarket.vue` | 3 | ✅ 已文档化 |
| 17 | `mock_TechnicalAnalysis.py` | TechnicalAnalysis | `TechnicalAnalysis.vue` | 4 | ✅ 已文档化 |
| 18 | `mock_TradeManagement.py` | TradeManagement | `TradeManagement.vue` | 3 | ✅ 已文档化 |
| 19 | `mock_TradingView.py` | TradingView | `TradingView.vue` | 6 | ✅ 已文档化 |
| 20 | `mock_Wencai.py` | Wencai | `Wencai.vue` | 4 | ✅ 已文档化 |
| 21 | `mock_strategy_BatchScan.py` | strategy_BatchScan | `strategy/BatchScan.vue` | 3 | ✅ 已文档化 |
| 22 | `mock_strategy_ResultsQuery.py` | strategy_ResultsQuery | `strategy/ResultsQuery.vue` | 3 | ✅ 已文档化 |
| 23 | `mock_strategy_SingleRun.py` | strategy_SingleRun | `strategy/SingleRun.vue` | 3 | ✅ 已文档化 |
| 24 | `mock_strategy_StatsAnalysis.py` | strategy_StatsAnalysis | `strategy/StatsAnalysis.vue` | 3 | ✅ 已文档化 |
| 25 | `mock_strategy_StrategyList.py` | strategy_StrategyList | `strategy/StrategyList.vue` | 3 | ✅ 已文档化 |
| 26 | `mock_system_Architecture.py` | system_Architecture | `system/Architecture.vue` | 3 | ✅ 已文档化 |
| 27 | `mock_system_DatabaseMonitor.py` | system_DatabaseMonitor | `system/DatabaseMonitor.vue` | 3 | ✅ 已文档化 |

## 📊 统计信息

- **已文档化文件**: 27/27 (100.0%)
- **总接口数量**: 102
- **平均每文件接口数**: 3.8

## 📖 详细文档

### 1. mock_Analysis.py

**页面名称**: Analysis
**Vue文件**: `Analysis.vue`
**文件路径**: `src/mock/mock_Analysis.py`

**提供接口**:
  1. `get_data_list()` -> List[Dict]
     - 获取数据列表
  2. `get_data_detail()` -> Dict
     - 获取数据详情
  3. `get_data_table()` -> pd.DataFrame
     - 获取数据表格


### 2. mock_BacktestAnalysis.py

**页面名称**: BacktestAnalysis
**Vue文件**: `BacktestAnalysis.vue`
**文件路径**: `src/mock/mock_BacktestAnalysis.py`

**提供接口**:
  1. `get_data_list()` -> List[Dict]
     - 获取数据列表
  2. `get_data_detail()` -> Dict
     - 获取数据详情
  3. `get_data_table()` -> pd.DataFrame
     - 获取数据表格


### 3. mock_Dashboard.py

**页面名称**: Dashboard
**Vue文件**: `Dashboard.vue`
**文件路径**: `src/mock/mock_Dashboard.py`

**提供接口**:
  1. `get_market_stats()` -> Dict
     - 获取市场统计数据（仪表盘顶部4个统计卡片）
  2. `get_market_heat_data()` -> List[Dict]
     - 获取市场热度数据（图表）
  3. `get_leading_sectors()` -> List[Dict]
     - 获取领涨板块数据（图表）
  4. `get_price_distribution()` -> List[Dict]
     - 获取涨跌分布数据（图表）
  5. `get_capital_flow_data()` -> List[Dict]
     - 获取资金流向数据（图表）
  6. `get_industry_fund_flow()` -> Dict
     - 获取行业资金流向（图表）
  7. `get_favorite_stocks()` -> List[Dict]
     - 获取自选股板块表现数据
  8. `get_strategy_stocks()` -> List[Dict]
     - 获取策略选股板块表现数据
  9. `get_industry_stocks()` -> List[Dict]
     - 获取行业选股板块表现数据
  10. `get_concept_stocks()` -> List[Dict]
     - 获取概念选股板块表现数据


### 4. mock_IndicatorLibrary.py

**页面名称**: IndicatorLibrary
**Vue文件**: `IndicatorLibrary.vue`
**文件路径**: `src/mock/mock_IndicatorLibrary.py`

**提供接口**:
  1. `get_data_list()` -> List[Dict]
     - 获取数据列表
  2. `get_data_detail()` -> Dict
     - 获取数据详情
  3. `get_data_table()` -> pd.DataFrame
     - 获取数据表格


### 5. mock_Login.py

**页面名称**: Login
**Vue文件**: `Login.vue`
**文件路径**: `src/mock/mock_Login.py`

**提供接口**:
  1. `get_data_list()` -> List[Dict]
     - 获取数据列表
  2. `get_data_detail()` -> Dict
     - 获取数据详情
  3. `get_data_table()` -> pd.DataFrame
     - 获取数据表格


### 6. mock_Market.py

**页面名称**: Market
**Vue文件**: `Market.vue`
**文件路径**: `src/mock/mock_Market.py`

**提供接口**:
  1. `get_market_heatmap()` -> List[Dict]
     - 获取市场热力图数据
  2. `get_real_time_quotes()` -> List[Dict]
     - 获取实时行情
  3. `get_fund_flow()` -> List[Dict]
     - 获取资金流向数据
  4. `get_etf_list()` -> List[Dict]
     - 获取ETF列表
  5. `get_chip_race()` -> List[Dict]
     - 获取竞价抢筹数据
  6. `get_lhb_detail()` -> List[Dict]
     - 获取龙虎榜数据
  7. `get_stock_list()` -> List[Dict]
     - 获取股票列表
  8. `get_kline_data()` -> List[Dict]
     - 获取K线数据


### 7. mock_MarketData.py

**页面名称**: MarketData
**Vue文件**: `MarketData.vue`
**文件路径**: `src/mock/mock_MarketData.py`

**提供接口**:
  1. `get_data_list()` -> List[Dict]
     - 获取数据列表
  2. `get_data_detail()` -> Dict
     - 获取数据详情
  3. `get_data_table()` -> pd.DataFrame
     - 获取数据表格


### 8. mock_MarketDataView.py

**页面名称**: MarketDataView
**Vue文件**: `MarketDataView.vue`
**文件路径**: `src/mock/mock_MarketDataView.py`

**提供接口**:
  1. `get_data_list()` -> List[Dict]
     - 获取数据列表
  2. `get_data_detail()` -> Dict
     - 获取数据详情
  3. `get_data_table()` -> pd.DataFrame
     - 获取数据表格


### 9. mock_RealTimeMonitor.py

**页面名称**: RealTimeMonitor
**Vue文件**: `RealTimeMonitor.vue`
**文件路径**: `src/mock/mock_RealTimeMonitor.py`

**提供接口**:
  1. `get_data_list()` -> List[Dict]
     - 获取数据列表
  2. `get_data_detail()` -> Dict
     - 获取数据详情
  3. `get_data_table()` -> pd.DataFrame
     - 获取数据表格


### 10. mock_RiskMonitor.py

**页面名称**: RiskMonitor
**Vue文件**: `RiskMonitor.vue`
**文件路径**: `src/mock/mock_RiskMonitor.py`

**提供接口**:
  1. `get_data_list()` -> List[Dict]
     - 获取数据列表
  2. `get_data_detail()` -> Dict
     - 获取数据详情
  3. `get_data_table()` -> pd.DataFrame
     - 获取数据表格


### 11. mock_Settings.py

**页面名称**: Settings
**Vue文件**: `Settings.vue`
**文件路径**: `src/mock/mock_Settings.py`

**提供接口**:
  1. `get_data_list()` -> List[Dict]
     - 获取数据列表
  2. `get_data_detail()` -> Dict
     - 获取数据详情
  3. `get_data_table()` -> pd.DataFrame
     - 获取数据表格


### 12. mock_StockSearch.py

**页面名称**: StockSearch
**Vue文件**: `StockSearch.vue`
**文件路径**: `src/mock/mock_StockSearch.py`

**提供接口**:
  1. `search_stocks()` -> List[Dict]
     - 搜索股票（支持按代码、名称、行业搜索）
  2. `get_stock_detail()` -> Dict
     - 获取股票详情
  3. `get_industry_list()` -> List[Dict]
     - 获取行业列表
  4. `get_stock_concept()` -> List[Dict]
     - 获取概念板块


### 13. mock_Stocks.py

**页面名称**: Stocks
**Vue文件**: `Stocks.vue`
**文件路径**: `src/mock/mock_Stocks.py`

**提供接口**:
  1. `get_stock_list()` -> List[Dict]
     - 获取股票列表（支持按交易所筛选，支持分页）
  2. `get_real_time_quote()` -> Dict
     - 获取实时行情（必填参数：股票代码）
  3. `get_history_profit()` -> pd.DataFrame
     - 获取历史收益（默认30天，返回DataFrame）


### 14. mock_StrategyManagement.py

**页面名称**: StrategyManagement
**Vue文件**: `StrategyManagement.vue`
**文件路径**: `src/mock/mock_StrategyManagement.py`

**提供接口**:
  1. `get_strategy_definitions()` -> Dict
     - 获取策略定义列表（对应/api/strategy/definitions）
  2. `run_strategy_single()` -> Dict
     - 单策略运行（对应/api/strategy/run/single）
  3. `run_strategy_batch()` -> Dict
     - 批量策略运行（对应/api/strategy/run/batch）
  4. `get_strategy_results()` -> Dict
     - 获取策略结果（对应/api/strategy/results）
  5. `get_matched_stocks()` -> Dict
     - 获取匹配的股票（对应/api/strategy/matched-stocks）
  6. `get_strategy_stats()` -> Dict
     - 获取策略统计（对应/api/strategy/stats/summary）


### 15. mock_TaskManagement.py

**页面名称**: TaskManagement
**Vue文件**: `TaskManagement.vue`
**文件路径**: `src/mock/mock_TaskManagement.py`

**提供接口**:
  1. `get_data_list()` -> List[Dict]
     - 获取数据列表
  2. `get_data_detail()` -> Dict
     - 获取数据详情
  3. `get_data_table()` -> pd.DataFrame
     - 获取数据表格


### 16. mock_TdxMarket.py

**页面名称**: TdxMarket
**Vue文件**: `TdxMarket.vue`
**文件路径**: `src/mock/mock_TdxMarket.py`

**提供接口**:
  1. `get_data_list()` -> List[Dict]
     - 获取数据列表
  2. `get_data_detail()` -> Dict
     - 获取数据详情
  3. `get_data_table()` -> pd.DataFrame
     - 获取数据表格


### 17. mock_TechnicalAnalysis.py

**页面名称**: TechnicalAnalysis
**Vue文件**: `TechnicalAnalysis.vue`
**文件路径**: `src/mock/mock_TechnicalAnalysis.py`

**提供接口**:
  1. `calculate_indicators()` -> Dict
     - 计算技术指标（对应/indicators/calculate API）
  2. `get_stock_kline()` -> List[Dict]
     - 获取股票K线数据
  3. `get_technical_indicators()` -> Dict
     - 获取技术指标数据
  4. `get_signal_analysis()` -> pd.DataFrame
     - 获取买卖信号分析


### 18. mock_TradeManagement.py

**页面名称**: TradeManagement
**Vue文件**: `TradeManagement.vue`
**文件路径**: `src/mock/mock_TradeManagement.py`

**提供接口**:
  1. `get_data_list()` -> List[Dict]
     - 获取数据列表
  2. `get_data_detail()` -> Dict
     - 获取数据详情
  3. `get_data_table()` -> pd.DataFrame
     - 获取数据表格


### 19. mock_TradingView.py

**页面名称**: TradingView
**Vue文件**: `TradingView.vue`
**文件路径**: `src/mock/mock_TradingView.py`

**提供接口**:
  1. `get_chart_config()` -> Dict
     - 获取TradingView图表配置
  2. `get_mini_chart_config()` -> Dict
     - 获取迷你图表配置
  3. `get_ticker_tape_config()` -> Dict
     - 获取滚动行情配置
  4. `get_market_overview_config()` -> Dict
     - 获取市场概览配置
  5. `get_screener_config()` -> Dict
     - 获取股票筛选器配置
  6. `convert_symbol()` -> Dict
     - 转换股票代码格式


### 20. mock_Wencai.py

**页面名称**: Wencai
**Vue文件**: `Wencai.vue`
**文件路径**: `src/mock/mock_Wencai.py`

**提供接口**:
  1. `get_wencai_queries()` -> Dict
     - 获取预定义查询列表（对应/api/market/wencai/queries）
  2. `execute_query()` -> Dict
     - 执行预定义查询（对应/api/market/wencai/query）
  3. `execute_custom_query()` -> Dict
     - 执行自定义查询（对应/api/market/wencai/custom-query）
  4. `get_query_results()` -> Dict
     - 获取查询结果（对应/api/market/wencai/results/{queryName}）


### 21. mock_strategy_BatchScan.py

**页面名称**: strategy_BatchScan
**Vue文件**: `strategy/BatchScan.vue`
**文件路径**: `src/mock/mock_strategy_BatchScan.py`

**提供接口**:
  1. `get_data_list()` -> List[Dict]
     - 获取数据列表
  2. `get_data_detail()` -> Dict
     - 获取数据详情
  3. `get_data_table()` -> pd.DataFrame
     - 获取数据表格


### 22. mock_strategy_ResultsQuery.py

**页面名称**: strategy_ResultsQuery
**Vue文件**: `strategy/ResultsQuery.vue`
**文件路径**: `src/mock/mock_strategy_ResultsQuery.py`

**提供接口**:
  1. `get_data_list()` -> List[Dict]
     - 获取数据列表
  2. `get_data_detail()` -> Dict
     - 获取数据详情
  3. `get_data_table()` -> pd.DataFrame
     - 获取数据表格


### 23. mock_strategy_SingleRun.py

**页面名称**: strategy_SingleRun
**Vue文件**: `strategy/SingleRun.vue`
**文件路径**: `src/mock/mock_strategy_SingleRun.py`

**提供接口**:
  1. `get_data_list()` -> List[Dict]
     - 获取数据列表
  2. `get_data_detail()` -> Dict
     - 获取数据详情
  3. `get_data_table()` -> pd.DataFrame
     - 获取数据表格


### 24. mock_strategy_StatsAnalysis.py

**页面名称**: strategy_StatsAnalysis
**Vue文件**: `strategy/StatsAnalysis.vue`
**文件路径**: `src/mock/mock_strategy_StatsAnalysis.py`

**提供接口**:
  1. `get_data_list()` -> List[Dict]
     - 获取数据列表
  2. `get_data_detail()` -> Dict
     - 获取数据详情
  3. `get_data_table()` -> pd.DataFrame
     - 获取数据表格


### 25. mock_strategy_StrategyList.py

**页面名称**: strategy_StrategyList
**Vue文件**: `strategy/StrategyList.vue`
**文件路径**: `src/mock/mock_strategy_StrategyList.py`

**提供接口**:
  1. `get_data_list()` -> List[Dict]
     - 获取数据列表
  2. `get_data_detail()` -> Dict
     - 获取数据详情
  3. `get_data_table()` -> pd.DataFrame
     - 获取数据表格


### 26. mock_system_Architecture.py

**页面名称**: system_Architecture
**Vue文件**: `system/Architecture.vue`
**文件路径**: `src/mock/mock_system_Architecture.py`

**提供接口**:
  1. `get_data_list()` -> List[Dict]
     - 获取数据列表
  2. `get_data_detail()` -> Dict
     - 获取数据详情
  3. `get_data_table()` -> pd.DataFrame
     - 获取数据表格


### 27. mock_system_DatabaseMonitor.py

**页面名称**: system_DatabaseMonitor
**Vue文件**: `system/DatabaseMonitor.vue`
**文件路径**: `src/mock/mock_system_DatabaseMonitor.py`

**提供接口**:
  1. `get_data_list()` -> List[Dict]
     - 获取数据列表
  2. `get_data_detail()` -> Dict
     - 获取数据详情
  3. `get_data_table()` -> pd.DataFrame
     - 获取数据表格


## 🔧 使用说明

### 导入方式

#### JavaScript Mock文件 (前端Vue组件使用)
```javascript
// 在Vue组件中导入JavaScript Mock数据
import { function_name } from '@/mock/mockDashboard'
```

#### Python Mock文件 (后端API开发使用)
```python
# 在Python后端中使用Mock数据
from src.mock.mock_system_DatabaseMonitor import get_data_list
```

### 数据格式
- `List[Dict]`: 字典列表，用于表格数据
- `Dict`: 单个字典，用于单个对象
- `pd.DataFrame`: Pandas数据框，用于复杂数据表
- `str`: 字符串，用于简单文本
- `int/float`: 数值类型

### 开发规范
- ✅ 所有函数必须有类型注释
- ✅ 所有参数必须有说明
- ✅ 返回值格式必须与前端期望一致
- ✅ 严禁硬编码数据到UI组件
- ✅ 股票价格保留2位小数
- ✅ 百分比保留4位小数

