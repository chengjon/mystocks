## ADDED Requirements

### Requirement: Thread-Safe Smart Cache
The system SHALL provide a thread-safe smart cache mechanism with TTL (Time-To-Live) expiration, background refresh, and LRU eviction to optimize data source performance and reduce API costs.

#### Scenario: Cache hit returns fresh data
- **GIVEN** a SmartCache with TTL=3600 seconds and a cached entry that was created 1000 seconds ago
- **WHEN** the cache key is requested
- **THEN** the system SHALL return the cached value
- **AND** the entry SHALL be moved to the most-recently-used position
- **AND** the system SHALL NOT trigger a background refresh

#### Scenario: Cache hit triggers pre-refresh
- **GIVEN** a SmartCache with TTL=3600 seconds, refresh_ratio=0.8, and a cached entry that was created 3000 seconds ago
- **WHEN** the cache key is requested with a refresher function
- **THEN** the system SHALL return the cached value
- **AND** the system SHALL trigger a background refresh in a separate thread
- **AND** the refresh SHALL NOT block the calling thread

#### Scenario: Cache miss with soft expiration
- **GIVEN** a SmartCache with TTL=3600 seconds and a cached entry that was created 4000 seconds ago
- **WHEN** the cache key is requested with a refresher function
- **THEN** the system SHALL return the stale (expired) cached value
- **AND** the system SHALL trigger a background refresh
- **AND** a warning SHALL be logged indicating stale data was returned

#### Scenario: Cache miss with hard expiration
- **GIVEN** a SmartCache with TTL=3600 seconds and a cached entry that was created 4000 seconds ago
- **WHEN** the cache key is requested WITHOUT a refresher function
- **THEN** the system SHALL return None
- **AND** the entry SHALL remain in cache until accessed or evicted

#### Scenario: LRU eviction when cache is full
- **GIVEN** a SmartCache with maxsize=100 containing 100 entries
- **WHEN** a new entry is added
- **THEN** the system SHALL evict the least-recently-used entry
- **AND** the new entry SHALL be added
- **AND** the cache size SHALL remain at 100

#### Scenario: Thread-safe concurrent access
- **GIVEN** a SmartCache and 100 concurrent threads
- **WHEN** all threads simultaneously read/write the same cache key
- **THEN** no data corruption SHALL occur
- **AND** no deadlock SHALL occur
- **AND** all operations SHALL complete successfully

#### Scenario: Background refresh failure handling
- **GIVEN** a SmartCache with an entry marked for refresh
- **WHEN** the background refresh function raises an exception
- **THEN** the system SHALL log the error
- **AND** the entry SHALL be removed from the refreshing set
- **AND** the stale data SHALL remain available in cache

#### Scenario: Limited concurrent refresh threads
- **GIVEN** a SmartCache with refresh_executor max_workers=5
- **WHEN** 20 cache entries expire simultaneously
- **THEN** the system SHALL only run 5 concurrent refresh threads
- **AND** the remaining 15 refresh tasks SHALL queue in the thread pool
- **AND** no more than 5 refresh threads SHALL be active at any time

---

### Requirement: Thread-Safe Circuit Breaker
The system SHALL implement a Circuit Breaker pattern with three states (CLOSED, OPEN, HALF_OPEN) to prevent cascading failures and provide automatic recovery for external data source calls.

#### Scenario: Circuit remains closed under normal operation
- **GIVEN** a CircuitBreaker with failure_threshold=5 and timeout=60 in CLOSED state
- **WHEN** a function call succeeds
- **THEN** the system SHALL return the result
- **AND** the failure count SHALL be reset to 0
- **AND** the state SHALL remain CLOSED

#### Scenario: Circuit opens after threshold failures
- **GIVEN** a CircuitBreaker with failure_threshold=5 in CLOSED state
- **WHEN** 5 consecutive function calls fail
- **THEN** the system SHALL transition the state to OPEN
- **AND** the last failure time SHALL be recorded
- **AND** subsequent calls SHALL raise CircuitBreakerOpenError

#### Scenario: Circuit enters half-open after timeout
- **GIVEN** a CircuitBreaker in OPEN state with timeout=60 seconds
- **WHEN** 60 seconds have elapsed since the last failure
- **AND** a new function call is attempted
- **THEN** the system SHALL transition the state to HALF_OPEN
- **AND** the call SHALL be allowed to execute (probe)

#### Scenario: Circuit closes after successful probe
- **GIVEN** a CircuitBreaker in HALF_OPEN state
- **WHEN** a function call succeeds
- **AND** the number of successful calls reaches the half_open_max_calls threshold
- **THEN** the system SHALL transition the state to CLOSED
- **AND** the failure count SHALL be reset to 0

#### Scenario: Circuit re-opens after failed probe
- **GIVEN** a CircuitBreaker in HALF_OPEN state
- **WHEN** a function call fails
- **THEN** the system SHALL transition the state back to OPEN
- **AND** the last failure time SHALL be updated
- **AND** subsequent calls SHALL raise CircuitBreakerOpenError

#### Scenario: Thread-safe state transitions
- **GIVEN** a CircuitBreaker and 10 concurrent threads
- **WHEN** all threads simultaneously trigger state transitions
- **THEN** no race conditions SHALL occur
- **AND** the final state SHALL be consistent
- **AND** no deadlock SHALL occur

#### Scenario: Circuit breaker provides remaining time feedback
- **GIVEN** a CircuitBreaker in OPEN state with timeout=60 seconds
- **WHEN** 30 seconds have elapsed since the last failure
- **AND** a call is attempted
- **THEN** the CircuitBreakerOpenError message SHALL include the remaining time (30 seconds)

#### Scenario: Configurable thresholds per data source
- **GIVEN** a data source with free tier pricing
- **WHEN** creating a CircuitBreaker for this source
- **THEN** the failure_threshold SHALL be configurable (default=5)
- **AND** the timeout SHALL be configurable (default=60)
- **AND** the half_open_max_calls SHALL be configurable (default=3)

---

### Requirement: Data Quality Validation
The system SHALL provide multi-layer data quality validation including logic checks, business rules, statistical anomaly detection, and cross-source verification to ensure data reliability.

#### Scenario: Basic OHLC logic validation passes
- **GIVEN** a DataFrame with valid OHLC data (low <= open,close <= high)
- **WHEN** the data is validated
- **THEN** the logic check SHALL pass
- **AND** no issues SHALL be reported

#### Scenario: Basic OHLC logic validation fails
- **GIVEN** a DataFrame with invalid OHLC data (open > high)
- **WHEN** the data is validated
- **THEN** the logic check SHALL fail
- **AND** issues SHALL include "开盘价违规记录"
- **AND** the validation result SHALL indicate is_valid=False

#### Scenario: Business rule detects extreme price change
- **GIVEN** a DataFrame with price changes > 20% between consecutive days
- **WHEN** the data is validated
- **THEN** the business check SHALL detect the extreme change
- **AND** issues SHALL include "检测到极端价格波动 (>20%)"
- **AND** the validation result SHALL indicate is_valid=False

#### Scenario: Business rule detects abnormal volume
- **GIVEN** a DataFrame with volume > 10x the mean volume
- **WHEN** the data is validated
- **THEN** the business check SHALL detect the abnormal volume
- **AND** issues SHALL include "检测到异常成交量 (>10倍均值)"
- **AND** the validation result SHALL indicate is_valid=False

#### Scenario: Business rule detects suspended trading data
- **GIVEN** a DataFrame with consecutive 3 days of zero volume and unchanged price
- **WHEN** the data is validated
- **THEN** the business check SHALL detect suspended trading
- **AND** issues SHALL include "停牌期间存在数据"
- **AND** the validation result SHALL indicate is_valid=False

#### Scenario: Statistical anomaly detection with 3-sigma
- **GIVEN** a DataFrame with close prices and a data point > 3 standard deviations from mean
- **WHEN** the data is validated
- **THEN** the statistical check SHALL detect the outlier
- **AND** the result SHALL include the number of outliers
- **AND** the result SHALL include the outlier details (date, price)

#### Scenario: Cross-source verification consistency check
- **GIVEN** data from akshare and tushare for the same stock and date range
- **WHEN** cross-source verification is enabled
- **THEN** the system SHALL compare price data between sources
- **AND** if price difference > 1%, the check SHALL fail
- **AND** issues SHALL include "跨源价格不一致"

#### Scenario: Validation summary report
- **GIVEN** a DataFrame that has been validated with all 4 checks (logic, business, statistical, cross-source)
- **WHEN** the validation is complete
- **THEN** the result SHALL include a summary with total_checks, passed_checks, and total_issues
- **AND** is_valid SHALL be True only if all checks pass
- **AND** the result SHALL include detailed issues for each failed check

#### Scenario: GPU-accelerated validation
- **GIVEN** a large DataFrame (100,000+ rows) and GPU available
- **WHEN** the data is validated with GPUValidator
- **THEN** the validation SHALL use cuDF for acceleration
- **AND** the validation time SHALL be < 1 second
- **AND** the validation SHALL automatically fall back to CPU if GPU is unavailable

---

### Requirement: Intelligent Routing with Multi-Dimensional Scoring
The system SHALL implement intelligent routing that considers performance, cost, load balancing, and location to select the optimal data source endpoint.

#### Scenario: Performance-based routing selection
- **GIVEN** 3 data source endpoints with different performance metrics (p50, p95, p99 latency, success rate)
- **WHEN** selecting the best endpoint for a request
- **THEN** the system SHALL calculate a performance score for each endpoint
- **AND** the endpoint with the highest performance score SHALL be selected
- **AND** the score SHALL weight p50=20%, p95=30%, p99=30%, success_rate=20%

#### Scenario: Cost optimization prioritizes free sources
- **GIVEN** 2 endpoints with similar performance scores (endpoint A: free, endpoint B: paid)
- **WHEN** selecting the best endpoint
- **THEN** the free endpoint SHALL receive a 50% score bonus
- **AND** the paid endpoint SHALL receive no bonus
- **AND** the free endpoint SHALL be selected

#### Scenario: Cost optimization uses free quota first
- **GIVEN** 2 endpoints with similar performance (endpoint A: 1000 free quota remaining, endpoint B: paid only)
- **WHEN** selecting the best endpoint
- **THEN** endpoint A SHALL receive a 20% score bonus for having free quota
- **AND** endpoint A SHALL be selected

#### Scenario: Load balancing avoids overloaded endpoints
- **GIVEN** 2 endpoints with similar performance (endpoint A: 90% utilization, endpoint B: 10% utilization)
- **WHEN** selecting the best endpoint
- **THEN** endpoint A SHALL receive a 30% score penalty (high load)
- **AND** endpoint B SHALL receive no penalty
- **AND** endpoint B SHALL be selected

#### Scenario: Location-aware routing selects nearest endpoint
- **GIVEN** 2 endpoints with similar performance (endpoint A: same location as client, endpoint B: different location)
- **WHEN** the client location is provided in request context
- **THEN** endpoint A SHALL receive a 10% score bonus
- **AND** endpoint A SHALL be selected

#### Scenario: All dimensions combined for final decision
- **GIVEN** 3 endpoints with varying performance, cost, load, and location
- **WHEN** selecting the best endpoint with weights: performance=0.4, cost=0.3, load=0.2, location=0.1
- **THEN** the system SHALL calculate the final_score = perf_score * cost_bonus * load_penalty * location_bonus
- **AND** the endpoint with the highest final_score SHALL be selected
- **AND** a log message SHALL record the selected endpoint and score

#### Scenario: No healthy endpoints available
- **GIVEN** a request with data_category that has no healthy endpoints
- **WHEN** selecting the best endpoint
- **THEN** the system SHALL return None
- **AND** a warning SHALL be logged

---

### Requirement: Request Batching with Thread Pool Concurrency
The system SHALL support concurrent batch processing of multiple data source requests using ThreadPoolExecutor to improve throughput.

#### Scenario: Batch processing with ThreadPoolExecutor
- **GIVEN** a list of 100 stock symbols to fetch
- **WHEN** fetch_batch_kline is called with max_workers=10
- **THEN** the system SHALL create a ThreadPoolExecutor with 10 worker threads
- **AND** all 100 symbols SHALL be fetched concurrently
- **AND** the results SHALL be returned as a Dict[symbol, DataFrame]
- **AND** the total time SHALL be < 10 seconds (vs 100 seconds serial)

#### Scenario: Batch processing with timeout control
- **GIVEN** a batch of 50 requests with timeout=30 seconds per request
- **WHEN** one request takes > 30 seconds
- **THEN** that specific request SHALL raise a TimeoutError
- **AND** other requests SHALL continue normally
- **AND** the failed request SHALL NOT affect the batch results

#### Scenario: Batch processing with exception isolation
- **GIVEN** a batch of 50 requests where 5 requests fail
- **WHEN** the batch processing completes
- **THEN** the 45 successful requests SHALL return their data
- **AND** the 5 failed requests SHALL be logged with errors
- **AND** the results Dict SHALL contain only the 45 successful symbols

#### Scenario: Batch processing with graceful shutdown
- **GIVEN** a GovernanceDataFetcher with active batch processing
- **WHEN** shutdown() is called
- **THEN** the executor SHALL wait for all running tasks to complete
- **AND** no new tasks SHALL be accepted
- **AND** the thread pool SHALL be properly cleaned up

#### Scenario: DataSourceManager remains synchronous
- **GIVEN** a batch request with ThreadPoolExecutor
- **WHEN** individual workers call DataSourceManager methods
- **THEN** the DataSourceManager API SHALL remain synchronous (no async/await)
- **AND** the DataSourceManager SHALL be thread-safe for concurrent calls
- **AND** no blocking SHALL occur between worker threads
