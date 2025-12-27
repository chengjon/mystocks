# MyStocks API Performance Benchmark

## Executive Summary

This document establishes performance baselines for MyStocks API endpoints, defining acceptable performance thresholds and identifying optimization targets for Phase 5 production readiness.

## Performance Targets (SLA)

| Metric | Target | Measurement | Owner |
|--------|--------|-------------|-------|
| Availability | ≥99.9% | 30-day rolling | Platform |
| P95 Latency | ≤300ms | HTTP request duration | API Team |
| P99 Latency | ≤1000ms | HTTP request duration | API Team |
| Error Rate | ≤0.1% | 5xx responses / total | API Team |
| Cache Hit Rate | ≥80% | cache_hits / total | Platform |
| DB Query P95 | ≤100ms | Per-query duration | Database |

## Endpoint Performance Baselines

### Tier 1: Critical Endpoints (P95 ≤ 100ms)

| Endpoint | Method | P95 Target | P99 Target | Notes |
|----------|--------|------------|------------|-------|
| `/health` | GET | 10ms | 50ms | Health check |
| `/metrics` | GET | 20ms | 100ms | Prometheus metrics |
| `/api/v1/stock/{code}/quote` | GET | 50ms | 100ms | Real-time quote |

### Tier 2: High-Traffic Endpoints (P95 ≤ 300ms)

| Endpoint | Method | P95 Target | P99 Target | Notes |
|----------|--------|------------|------------|-------|
| `/api/v1/market/overview` | GET | 150ms | 300ms | Market summary |
| `/api/v1/market/index` | GET | 100ms | 200ms | Index data |
| `/api/v1/portfolio/summary` | GET | 200ms | 400ms | Portfolio overview |

### Tier 3: Standard Endpoints (P95 ≤ 500ms)

| Endpoint | Method | P95 Target | P99 Target | Notes |
|----------|--------|------------|------------|-------|
| `/api/v1/stock/{code}/kline` | GET | 300ms | 500ms | K-line data |
| `/api/v1/market/fund-flow` | GET | 300ms | 500ms | Capital flow |
| `/api/v1/market/dragon-tiger` | GET | 400ms | 600ms | Top traders |

### Tier 4: Heavy Operations (P95 ≤ 1000ms)

| Endpoint | Method | P95 Target | P99 Target | Notes |
|----------|--------|------------|------------|-------|
| `/api/v1/strategy/backtest` | POST | 800ms | 1500ms | Backtest execution |
| `/api/v1/reports/generate` | POST | 1000ms | 2000ms | Report generation |
| `/api/v1/data/export` | POST | 500ms | 1000ms | Data export |

## Performance Budget Allocation

For a typical API request, the total latency budget is distributed as:

```
Total Budget: 300ms (P95)

├── Load Balancer: 10ms (3.3%)
├── Authentication: 20ms (6.7%)
├── Request Processing: 30ms (10%)
├── Cache Lookup: 5ms (1.7%)
├── Database Query: 100ms (33.3%)
│   ├── Connection acquire: 5ms
│   ├── Query execution: 80ms
│   └── Result processing: 15ms
├── Response Serialization: 10ms (3.3%)
├── Response Compression: 20ms (6.7%)
├── Network Transit: 50ms (16.7%)
└── Client Processing: 55ms (18.3%)
```

## Optimization Strategies

### Database Indexes

```sql
CREATE INDEX idx_market_data_date ON market_daily_kline(trade_date);
CREATE INDEX idx_stock_quote_symbol ON stock_quote(stock_code, updated_at);
CREATE INDEX idx_fund_flow_date ON fund_flow(flow_date, flow_type);
```

### Caching Strategy

| Data Type | Cache Level | TTL | Invalidation |
|-----------|-------------|-----|--------------|
| Market Overview | L1 + L2 | 15s | On market event |
| Stock Quote | L1 + L2 | 5s | Real-time |
| K-line Data | L2 | 5min | EOD update |
| User Portfolio | L1 | 30s | User action |
| Dragon Tiger | L2 | 1min | Daily |

### Connection Pool Configuration

```python
POOL_CONFIG = {
    "min_size": 10,
    "max_size": 50,
    "max_idle_time": 300,
    "connection_timeout": 10,
    "command_timeout": 30,
}
```

## Performance Monitoring

### Key Metrics

```prometheus
http_request_duration_seconds_bucket{endpoint, le}
rate(http_requests_total{status_code=~"5.."}[5m])
cache_hits_total{layer}
db_query_duration_seconds_bucket{query_type, le}
```

### Alert Thresholds

| Alert | Condition | Severity |
|-------|-----------|----------|
| HighLatency | P95 > 500ms for 5m | warning |
| VeryHighLatency | P95 > 1s for 2m | critical |
| HighErrorRate | Error rate > 1% for 2m | warning |
| CacheMissStorm | Cache miss > 50% for 5m | warning |

## Performance Regression Detection

### Regression Thresholds

| Metric | Warning | Blocking |
|--------|---------|----------|
| P95 Latency | +10% | +20% |
| Error Rate | +0.1% | +0.5% |
| Throughput | -10% | -20% |

## Tools

| Tool | Purpose |
|------|---------|
| Locust | Load testing |
| k6 | Load testing |
| py-spy | Profiling |
| Prometheus | Metrics |
| Grafana | Visualization |

## Appendix: Test Scenarios

```python
scenarios = [
    {"name": "Light Load", "users": 10, "duration": "5m"},
    {"name": "Normal Load", "users": 50, "duration": "10m"},
    {"name": "Peak Load", "users": 200, "duration": "15m"},
    {"name": "Stress Test", "users": 500, "duration": "10m"},
]
```
