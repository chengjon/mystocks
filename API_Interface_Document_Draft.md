# MyStocks API Interface Document (Draft)

**Purpose:** This document provides a comprehensive overview of the available API endpoints in the MyStocks project, including their functionality, implementation details, and key components. It serves as a reference for developers to understand the API structure and integration points.

**Overall Architecture Notes:**
*   The API is built using the FastAPI framework.
*   API endpoints are organized modularly across several Python files in `src/api/` and `src/routes/`.
*   A common pattern for data retrieval is the use of the `USE_MOCK_DATA` environment variable. When set to `true`, the API fetches data from mock modules located in `src/mock/`. Otherwise, it attempts to fetch data from a real database backend, primarily through `src/database/database_service.py`.
*   Database integration is noted as incomplete in several modules, especially for the Wencai-related endpoints where the `get_database_service()` currently returns `None`.

---

## 1. Stocks API

*   **File:** `src/routes/stocks_routes.py`
*   **Router Prefix:** `/api/stocks`

| Endpoint          | Method | Function Name       | Description                                  | Key Functions/Classes             | Implementation Logic                                       |
| :---------------- | :----- | :------------------ | :------------------------------------------- | :-------------------------------- | :--------------------------------------------------------- |
| `/list`           | GET    | `get_stock_list`    | Retrieves a list of available stocks.        | `check_use_mock_data()`, `get_stock_mock_data()` (from `src/mock/mock_Stocks.py`), `db_service.get_stock_list()` | Switches between mock data and `db_service` for stock list retrieval. |
| `/detail/{symbol}`| GET    | `get_stock_detail`  | Retrieves detailed information for a specific stock. | `check_use_mock_data()`, `get_stock_mock_data()`, `db_service.get_stock_detail()` | Switches between mock data and `db_service` for stock details. |

## 2. Alert History API

*   **File:** `src/api/alert_history_routes.py`
*   **Router Prefix:** `/api/alerts`

| Endpoint           | Method | Function Name        | Description                                  | Key Functions/Classes             | Implementation Logic                                       |
| :----------------- | :----- | :------------------- | :------------------------------------------- | :-------------------------------- | :--------------------------------------------------------- |
| `/history`         | GET    | `get_alert_history`  | Retrieves a paginated list of alert history. | `AlertHistoryDatabase.get_alert_history()` | Interacts with `AlertHistoryDatabase` to fetch historical alerts. |
| `/save`            | POST   | `save_alert_history` | Saves a new alert history entry.             | `AlertHistoryDatabase.save_alert_history()` | Interacts with `AlertHistoryDatabase` to persist alerts. |

## 3. Dashboard Data API

*   **File:** `src/routes/dashboard_routes.py`
*   **Router Prefix:** `/data/markets`

| Endpoint          | Method | Function Name       | Description                                  | Key Functions/Classes             | Implementation Logic                                       |
| :---------------- | :----- | :------------------ | :------------------------------------------- | :-------------------------------- | :--------------------------------------------------------- |
| `/overview`       | GET    | `get_market_overview`| Retrieves a high-level overview of market data. | `check_use_mock_data()`, `get_market_mock_data()` (from `src/mock/mock_Markets.py`), `db_service.get_market_overview()` | Switches between mock data and `db_service` for market overview. |
| `/heat`           | GET    | `get_market_heat`   | Retrieves market heat map data.              | `check_use_mock_data()`, `get_market_mock_data()`, `db_service.get_market_heat()` | Switches between mock data and `db_service` for market heat data. |

## 4. Monitoring API

*   **File:** `src/routes/monitoring_routes.py`
*   **Router Prefix:** `/api/monitoring`

| Endpoint          | Method | Function Name       | Description                                  | Key Functions/Classes             | Implementation Logic                                       |
| :---------------- | :----- | :------------------ | :------------------------------------------- | :-------------------------------- | :--------------------------------------------------------- |
| `/alert-rules`    | GET    | `get_alert_rules`   | Retrieves a list of defined alert rules.     | `check_use_mock_data()`, `get_monitoring_mock_data()` (from `src/mock/mock_RealTimeMonitor.py`), `db_service.get_alert_rules()` | Switches between mock data and `db_service` for alert rules. |
| `/realtime-data`  | GET    | `get_realtime_data` | Retrieves real-time monitoring data.         | `check_use_mock_data()`, `get_monitoring_mock_data()`, `db_service.get_realtime_data()` | Switches between mock data and `db_service` for real-time monitoring data. |
| `/control/{action}`| POST   | `control_system_component` | Sends control commands to system components. | (Placeholder for actual control logic) | Currently uses mock data; real implementation would interact with system components. |

## 5. Strategy API

*   **File:** `src/routes/strategy_routes.py`
*   **Router Prefix:** `/api/strategy`

| Endpoint          | Method | Function Name       | Description                                  | Key Functions/Classes             | Implementation Logic                                       |
| :---------------- | :----- | :------------------ | :------------------------------------------- | :-------------------------------- | :--------------------------------------------------------- |
| `/definitions`    | GET    | `get_strategy_definitions`| Retrieves definitions of available trading strategies. | `check_use_mock_data()`, `get_strategy_mock_data()` (from `src/mock/mock_Strategy.py`), `db_service.get_strategy_definitions()` | Switches between mock data and `db_service` for strategy definitions. |
| `/run/{strategy_id}`| POST   | `run_single_strategy`| Executes a single trading strategy.         | `check_use_mock_data()`, `get_strategy_mock_data()`, `db_service.run_strategy()` | Switches between mock data and `db_service` for strategy execution. |
| `/results/{strategy_id}`| GET    | `get_strategy_results`| Retrieves results of a specific strategy execution. | `check_use_mock_data()`, `get_strategy_mock_data()`, `db_service.get_strategy_results()` | Switches between mock data and `db_service` for strategy results. |

## 6. Technical Analysis API

*   **File:** `src/routes/technical_routes.py`
*   **Router Prefix:** `/api/technical`

| Endpoint                 | Method | Function Name                | Description                      | Key Functions/Classes                  | Implementation Logic                                         |
| :----------------------- | :----- | :--------------------------- | :------------------------------- | :------------------------------------- | :----------------------------------------------------------- |
| `/{stock_code}/indicators`| GET    | `get_all_indicators`         | 获取所有技术指标 (Get all technical indicators) | `check_use_mock_data()`, `get_technical_mock_data()` (from `src/mock/mock_TechnicalAnalysis.py`), `db_service.get_technical_indicators()` | Switches between mock data and `db_service` for all technical indicators. Note: `db_service` implementation is via `db_service.get_technical_indicators({"symbol": stock_code})`. |
| `/{stock_code}/trend`    | GET    | `get_trend_indicators`       | 获取趋势指标 (Get trend indicators) | `check_use_mock_data()`, `get_technical_mock_data()`, `db_service.get_trend_indicators()` | Switches between mock data and `db_service` for trend indicators. |
| `/{stock_code}/momentum` | GET    | `get_momentum_indicators`    | 获取动量指标 (Get momentum indicators) | `check_use_mock_data()`, `get_technical_mock_data()`, `db_service.get_momentum_indicators()` | Switches between mock data and `db_service` for momentum indicators. |
| `/{stock_code}/volatility`| GET    | `get_volatility_indicators`  | 获取波动性指标 (Get volatility indicators) | `check_use_mock_data()`, `get_technical_mock_data()`, `db_service.get_volatility_indicators()` | Switches between mock data and `db_service` for volatility indicators. |
| `/{stock_code}/volume`   | GET    | `get_volume_indicators`      | 获取成交量指标 (Get volume indicators) | `check_use_mock_data()`, `get_technical_mock_data()`, `db_service.get_volume_indicators()` | Switches between mock data and `db_service` for volume indicators. |
| `/{stock_code}/signals`  | GET    | `get_trading_signals`        | 获取交易信号 (Get trading signals) | `check_use_mock_data()`, `get_technical_mock_data()`, `db_service.get_trading_signals()` | Switches between mock data and `db_service` for trading signals. |
| `/{stock_code}/history`  | GET    | `get_kline_data`             | 获取K线历史数据 (Get K-line history data) | `check_use_mock_data()`, `get_technical_mock_data()`, `db_service.get_stock_history()` | Switches between mock data and `db_service` for K-line history data. |
| `/patterns/{stock_code}` | GET    | `get_pattern_recognition`    | 获取形态识别结果 (Get pattern recognition results) | `check_use_mock_data()`, `get_technical_mock_data()`, `db_service.get_technical_indicators()` | Switches between mock data and `db_service` for pattern recognition. Real implementation uses technical indicators as a proxy, with a placeholder for actual pattern recognition. |
| `/batch/indicators`      | POST   | `batch_calculate_indicators` | 批量计算技术指标 (Batch calculate technical indicators) | `check_use_mock_data()`, `db_service.get_batch_indicators()` | Switches between mock data (simulated results) and `db_service` for batch indicator calculation. |
| `/{stock_code}/support-resistance`| GET    | `get_support_resistance_levels`| 获取支撑阻力位 (Get support/resistance levels) | `check_use_mock_data()`, `db_service.get_technical_indicators()` | Switches between mock data (simulated results) and `db_service`. Real implementation uses technical indicators as a proxy, with placeholder values for levels. |
| `/health`                | GET    | `check_technical_health`     | 检查技术分析服务健康状态 (Check technical analysis service health status) | `check_use_mock_data()`, `db_service` | Switches between mock health status and `db_service` for health check. |

## 7. Wencai API

*   **File:** `src/routes/wencai_routes.py`
*   **Router Prefix:** `/api/market/wencai`

| Endpoint                 | Method | Function Name                | Description                                  | Key Functions/Classes                      | Implementation Logic                                         |
| :----------------------- | :----- | :--------------------------- | :------------------------------------------- | :----------------------------------------- | :----------------------------------------------------------- |
| `/queries`               | GET    | `get_wencai_queries`         | 获取预定义查询列表 (Get predefined query list) | `check_use_mock_data()`, `get_wencai_mock_data()` (from `src/mock/mock_Wencai.py`), `get_database_service()` | Switches between mock data and `db_service`. Note: `db_service` currently returns `None` for Wencai. |
| `/query`                 | POST   | `execute_predefined_query`   | 执行预定义查询 (Execute predefined query)   | `check_use_mock_data()`, `get_wencai_mock_data()`, `db_service.execute_wencai_query()` | Switches between mock data and `db_service`. Note: `db_service` currently returns `None` for Wencai. |
| `/custom-query`          | POST   | `execute_custom_wencai_query`| 执行自定义问财查询 (Execute custom Wencai query) | `check_use_mock_data()`, `get_wencai_mock_data()`, `db_service.execute_wencai_query()` | Switches between mock data and `db_service`. Note: `db_service` currently returns `None` for Wencai. |
| `/results/{query_name}`  | GET    | `get_wencai_query_results`   | 获取问财查询结果 (Get Wencai query results) | `check_use_mock_data()`, `get_wencai_mock_data()`, `db_service.execute_wencai_query()` | Switches between mock data and `db_service`. Note: `db_service` currently returns `None` for Wencai. |
| `/refresh/{query_name}`  | POST   | `refresh_wencai_query`       | 刷新问财查询结果 (Refresh Wencai query results) | `check_use_mock_data()`, `db_service` | Switches between mock data and `db_service`. Note: `db_service` currently returns `None` for Wencai. |
| `/history/{query_name}`  | GET    | `get_wencai_query_history`   | 获取问财查询历史记录 (Get Wencai query history) | `check_use_mock_data()`, `db_service.execute_wencai_query()` | Switches between mock data and `db_service`. Note: `db_service` currently returns `None` for Wencai. |
| `/health`                | GET    | `check_wencai_health`        | 检查问财服务健康状态 (Check Wencai service health status) | `check_use_mock_data()`, `db_service` | Switches between mock health status and `db_service`. Note: `db_service` currently returns `None` for Wencai. |
