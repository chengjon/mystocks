# MyStocks Monitoring Guide

## Overview

This document describes the monitoring infrastructure and configuration for MyStocks Phase 5 production readiness.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Monitoring Stack                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │Prometheus│  │ Grafana  │  │   Loki   │  │  Tempo   │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │             │             │             │              │
│       └─────────────┴─────────────┴─────────────┘              │
│                         │                                      │
│              ┌──────────┴──────────┐                           │
│              │   MyStocks API      │                           │
│              │   (Metrics + Logs   │                           │
│              │    + Traces)        │                           │
│              └─────────────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### Prometheus

**Configuration:** `config/monitoring/prometheus.yml`

**Metrics Exposed:**
- `http_request_duration_seconds` - Request latency histogram
- `http_requests_total` - Request count by endpoint/method
- `http_requests_active` - Active requests gauge
- `slow_http_requests_total` - Slow requests counter (>300ms)
- `cache_hits_total` - Cache hit count
- `cache_misses_total` - Cache miss count
- `cache_evictions_total` - Cache eviction count

**Endpoint:** `/metrics`

### Grafana Dashboards

**Dashboard:** `config/monitoring/dashboards/api-overview.json`

**Panels:**
- Request Rate (RPS)
- P95 Latency
- Error Rate (%)
- Request Rate by Endpoint
- P95 Latency by Endpoint
- Cache Hit Rate
- Cache Evictions
- SLO Status (Availability, Latency, Error Rate)

### Loki (Log Aggregation)

**Configuration:** `config/monitoring/loki-config.yaml`

**Log Format:**
```json
{
  "timestamp": "2025-12-27T10:30:00.000Z",
  "level": "INFO",
  "message": "Request processed",
  "trace_id": "abc123",
  "request_id": "xyz789",
  "service": "mystocks-api",
  "environment": "production"
}
```

**Log Levels:**
- DEBUG: Detailed debugging information
- INFO: Normal operational events
- WARNING: Abnormal conditions
- ERROR: Failures affecting current request
- CRITICAL: System-level failures

### Tempo (Distributed Tracing)

**Configuration:** `config/monitoring/tempo-config.yaml`

**Trace Attributes:**
- `http.method`
- `http.url`
- `http.status_code`
- `http.request_id`
- `trace_id`

## Alert Rules

**Configuration:** `config/monitoring/rules/mystocks-alerts.yml`

### Critical Alerts
- **VeryHighErrorRate**: Error rate > 5% for 1 minute
- **VeryHighLatency**: P95 latency > 1s for 2 minutes

### Warning Alerts
- **HighErrorRate**: Error rate > 1% for 2 minutes
- **HighLatency**: P95 latency > 300ms for 5 minutes
- **HighCacheMissRate**: Cache miss rate > 50%
- **SlowRequestsDetected**: >10 slow requests in 5 minutes

## SLO Definitions

| Metric | Target | Measurement Period |
|--------|--------|-------------------|
| Availability | ≥99.9% | 30 days |
| P95 Latency | ≤300ms | 30 days |
| Error Rate | ≤0.1% | 30 days |

## Setup Instructions

### 1. Start Monitoring Stack

```bash
# Start Prometheus
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v $(pwd)/config/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

# Start Grafana
docker run -d \
  --name grafana \
  -p 3000:3000 \
  grafana/grafana

# Start Loki
docker run -d \
  --name loki \
  -p 3100:3100 \
  -v $(pwd)/config/monitoring/loki-config.yaml:/etc/loki/loki-config.yaml \
  grafana/loki

# Start Tempo
docker run -d \
  --name tempo \
  -p 3200:3200 \
  -p 4317:4317 \
  -p 4318:4318 \
  -v $(pwd)/config/monitoring/tempo-config.yaml:/etc/tempo/tempo-config.yaml \
  grafana/tempo
```

### 2. Import Dashboards

1. Access Grafana at http://localhost:3000
2. Add data sources (Prometheus, Loki, Tempo)
3. Import `config/monitoring/dashboards/api-overview.json`

### 3. Configure Alerting

1. In Grafana, go to Alerting > Contact points
2. Configure notification channels (email, Slack, etc.)
3. Import alert rules from `config/monitoring/rules/mystocks-alerts.yml`

## API Performance Monitoring

### Using /metrics Endpoint

```bash
# Get all metrics
curl http://localhost:8000/metrics

# Filter by endpoint
curl http://localhost:8000/metrics | grep http_request_duration_seconds

# Get P95 latency
curl http://localhost:8000/metrics | grep 'http_request_duration_seconds_bucket.*0\.3'
```

### Using Grafana

1. Access API Overview dashboard
2. Select time range
3. View per-endpoint metrics
4. Check SLO status indicators

## Troubleshooting

### High Latency
1. Check Slow Requests panel in Grafana
2. Identify slowest endpoints
3. Review cache hit rates
4. Check database query performance

### High Error Rate
1. Check Error Rate panel
2. Review recent logs in Loki
3. Identify error patterns
4. Check system resources

### Cache Issues
1. Check Cache Hit Rate panel
2. Review cache eviction metrics
3. Verify Redis connectivity
4. Adjust cache TTL if needed

## Maintenance

### Log Retention
- Debug logs: 7 days
- Error logs: 30 days
- Traces: 24 hours

### Dashboard Refresh
- Auto-refresh: 30 seconds
- Manual refresh available

## Best Practices

1. **Monitor SLOs Daily**: Review SLO status each day
2. **Act on Alerts**: Respond to warnings within 1 hour
3. **Review Metrics Weekly**: Analyze trends and patterns
4. **Update Thresholds**: Adjust based on production experience
5. **Document Incidents**: Record all alert responses
