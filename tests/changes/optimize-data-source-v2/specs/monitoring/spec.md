## ADDED Requirements

### Requirement: Prometheus Metrics Integration
The system SHALL expose comprehensive Prometheus metrics for data source operations through the existing FastAPI `/metrics` endpoint, enabling monitoring of latency, success rate, data quality, cost, and circuit breaker state.

#### Scenario: API latency histogram
- **GIVEN** a data source API call completes with response time of 0.5 seconds
- **WHEN** the call is recorded
- **THEN** the datasource_api_latency_seconds histogram SHALL be observed with labels source, endpoint, status="success"
- **AND** the histogram SHALL include buckets [0.1, 0.5, 1.0, 2.0, 5.0, 10.0] seconds

#### Scenario: API call counter
- **GIVEN** a successful data source API call
- **WHEN** the call completes
- **THEN** the datasource_api_calls_total counter SHALL increment with labels source, endpoint, status="success"
- **AND** for a failed call, the counter SHALL increment with status="error"

#### Scenario: Data quality score gauge
- **GIVEN** a data quality validation completes with a score of 85/100
- **WHEN** the validation is recorded
- **THEN** the datasource_data_quality gauge SHALL be set to 85 with label source
- **AND** the gauge SHALL be queryable in Prometheus

#### Scenario: Cache hit/miss counters
- **GIVEN** a cache lookup operation
- **WHEN** the lookup results in a cache hit
- **THEN** the datasource_cache_hits_total counter SHALL increment with label source
- **WHEN** the lookup results in a cache miss
- **THEN** the datasource_cache_misses_total counter SHALL increment with label source
- **AND** the cache hit rate SHALL be calculable as hits / (hits + misses)

#### Scenario: Circuit breaker state gauge
- **GIVEN** a circuit breaker in OPEN state
- **WHEN** the state is recorded
- **THEN** the datasource_circuit_breaker_state gauge SHALL be set to 1 with label source
- **AND** the state mapping SHALL be: closed=0, open=1, half_open=2

#### Scenario: Metrics exposed via FastAPI /metrics endpoint
- **GIVEN** a FastAPI application with Prometheus metrics
- **WHEN** a GET request is made to /metrics
- **THEN** the response SHALL have content-type "text/plain"
- **AND** the response body SHALL contain Prometheus exposition format
- **AND** the response SHALL include all registered metrics

#### Scenario: Global metrics registry to avoid conflicts
- **GIVEN** multiple modules registering Prometheus metrics
- **WHEN** metrics are registered
- **THEN** all metrics SHALL use the global REGISTRY from prometheus_client
- **AND** no duplicate metric names SHALL be registered
- **AND** the /metrics endpoint SHALL return all registered metrics

#### Scenario: Estimated API cost tracking
- **GIVEN** a data source with pricing model $0.01 per 1000 calls
- **WHEN** 10,000 API calls are made
- **THEN** the datasource_api_cost_estimated gauge SHALL be set to $1.00 (10,000 / 1000 * $0.01)
- **AND** the cost SHALL be trackable per data source

---

### Requirement: Grafana Dashboard for Data Source Monitoring
The system SHALL provide a Grafana dashboard configuration that visualizes key metrics including latency, success rate, cache hit rate, circuit breaker state, and API cost.

#### Scenario: Dashboard displays API latency P95
- **GIVEN** the Grafana dashboard is configured
- **WHEN** viewing the "API Latency" panel
- **THEN** the panel SHALL display a graph of datasource_api_latency_seconds P95 over time
- **AND** the panel SHALL be grouped by source label

#### Scenario: Dashboard displays API success rate
- **GIVEN** the Grafana dashboard is configured
- **WHEN** viewing the "Success Rate" panel
- **THEN** the panel SHALL display a percentage calculated from rate(success) / rate(total) * 100
- **AND** the panel SHALL show a threshold line at 95% (green above, red below)

#### Scenario: Dashboard displays cache hit rate
- **GIVEN** the Grafana dashboard is configured
- **WHEN** viewing the "Cache Hit Rate" panel
- **THEN** the panel SHALL display a percentage calculated from hits / (hits + misses) * 100
- **AND** the panel SHALL be grouped by source label

#### Scenario: Dashboard displays circuit breaker state
- **GIVEN** the Grafana dashboard is configured
- **WHEN** viewing the "Circuit Breaker State" panel
- **THEN** the panel SHALL display a stat value (0=closed, 1=open, 2=half_open)
- **AND** the panel SHALL use value mapping to display text labels
- **AND** the panel SHALL be colored green for closed, red for open, yellow for half_open

#### Scenario: Dashboard displays estimated API cost
- **GIVEN** the Grafana dashboard is configured
- **WHEN** viewing the "API Cost" panel
- **THEN** the panel SHALL display the current estimated cost in CNY
- **AND** the panel SHALL show a trend comparison to the same period last week
- **AND** the panel SHALL be grouped by source label

---

### Requirement: Alerting Rules for Data Source Health
The system SHALL provide Prometheus alerting rules that trigger when key metrics exceed thresholds, enabling rapid response to degraded data source performance.

#### Scenario: Alert on low success rate
- **GIVEN** a data source with success rate < 95% for 5 minutes
- **WHEN** the alert rule is evaluated
- **THEN** an alert SHALL fire with severity=warning
- **AND** the alert SHALL include the source name and current success rate
- **AND** the alert SHALL recommend checking circuit breaker state

#### Scenario: Alert on high latency
- **GIVEN** a data source with P95 latency > 500ms for 5 minutes
- **WHEN** the alert rule is evaluated
- **THEN** an alert SHALL fire with severity=warning
- **AND** the alert SHALL include the source name and current P95 latency
- **AND** the alert SHALL recommend checking network connectivity or data source status

#### Scenario: Alert on circuit breaker open
- **GIVEN** a circuit breaker in OPEN state for > 1 minute
- **WHEN** the alert rule is evaluated
- **THEN** an alert SHALL fire with severity=critical
- **AND** the alert SHALL include the source name and time since opening
- **AND** the alert SHALL recommend checking data source status page

#### Scenario: Alert on low cache hit rate
- **GIVEN** a cache with hit rate < 50% for 15 minutes
- **WHEN** the alert rule is evaluated
- **THEN** an alert SHALL fire with severity=info
- **AND** the alert SHALL include the cache name and current hit rate
- **AND** the alert SHALL recommend reviewing TTL configuration or access patterns

#### Scenario: Alert on high API cost
- **GIVEN** estimated API cost increases by > 50% compared to last week
- **WHEN** the alert rule is evaluated
- **THEN** an alert SHALL fire with severity=warning
- **AND** the alert SHALL include the current cost and percentage increase
- **AND** the alert SHALL recommend reviewing caching strategy or routing configuration
