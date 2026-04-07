## ADDED Requirements

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。


### Requirement: Data Quality Multi-Layer Validation
The data governance layer SHALL perform multi-layer validation including basic logic, business rules, statistical anomalies, and cross-source checks to ensure data reliability before use in quantitative strategies.

#### Scenario: Validation passes all layers
- **GIVEN** a DataFrame with valid OHLC data, normal price changes, normal volume, no outliers, and consistent cross-source data
- **WHEN** validated through all layers
- **THEN** all 4 validation checks SHALL pass
- **AND** is_valid SHALL be True
- **AND** summary SHALL show total_checks=4, passed_checks=4, total_issues=0

#### Scenario: Validation fails at business rule layer
- **GIVEN** a DataFrame with a price change of 25% (extreme)
- **WHEN** validated through all layers
- **THEN** the business rule check SHALL fail
- **AND** issues SHALL include "检测到极端价格波动 (>20%)"
- **AND** is_valid SHALL be False
- **AND** summary SHALL show total_checks=4, passed_checks=3, total_issues=1

#### Scenario: Validation detects outlier at statistical layer
- **GIVEN** a DataFrame with a price > 3 standard deviations from mean
- **WHEN** statistical check is performed
- **THEN** the check SHALL detect the outlier
- **AND** outliers_count SHALL be > 0
- **AND** outliers details SHALL include the date and price of the outlier

#### Scenario: Cross-source verification finds inconsistency
- **GIVEN** two data sources with price difference of 2% for the same stock and date
- **WHEN** cross-source verification is enabled
- **THEN** the verification SHALL fail
- **AND** issues SHALL include "跨源价格不一致: 差异=2%"
- **AND** is_valid SHALL be False

#### Scenario: GPU-accelerated validation for large datasets
- **GIVEN** a DataFrame with 100,000 rows and GPU available
- **WHEN** validation is performed with GPUValidator
- **THEN** cuDF SHALL be used for acceleration
- **AND** validation time SHALL be < 1 second
- **AND** if GPU is unavailable, validation SHALL fall back to CPU automatically

---

### Requirement: Governance Layer Batch Processing
The governance layer SHALL support concurrent batch processing of multiple stock data requests using ThreadPoolExecutor to improve throughput for quantitative workflows.

#### Scenario: Batch fetch with concurrent processing
- **GIVEN** a list of 50 stock symbols
- **WHEN** fetch_batch_kline is called with TimeFrame.DAILY and RoutePolicy.SMART_ROUTING
- **THEN** the system SHALL use ThreadPoolExecutor to fetch data concurrently
- **AND** all 50 symbols SHALL be fetched in parallel
- **AND** total time SHALL be < 5 seconds (vs 50 seconds serial)

#### Scenario: Batch fetch with timeout handling
- **GIVEN** a batch of 20 symbols with timeout=30 per request
- **WHEN** one request exceeds 30 seconds
- **THEN** that specific request SHALL raise TimeoutError
- **AND** the other 19 requests SHALL complete successfully
- **AND** the results Dict SHALL contain 19 entries

#### Scenario: Batch fetch with different route policies
- **GIVEN** a batch request with RoutePolicy.FASTEST
- **WHEN** selecting endpoints for each symbol
- **THEN** the system SHALL select endpoints based on lowest avg_response_time
- **AND** the selection SHALL be independent for each symbol

#### Scenario: Batch fetch results aggregation
- **GIVEN** a batch of 100 symbols with varying success rates
- **WHEN** fetch_batch_kline completes
- **THEN** the results Dict SHALL contain only successful symbols
- **AND** failed symbols SHALL be logged with errors
- **AND** the return type SHALL be Dict[str, pd.DataFrame]
