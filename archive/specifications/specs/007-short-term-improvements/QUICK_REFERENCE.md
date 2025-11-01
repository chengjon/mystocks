# Feature 007 Quick Reference Card

**Version**: v2.2.0
**Date**: 2025-10-16
**Purpose**: Quick reference for developers using Feature 007 improvements

---

## 🌐 New API Endpoints

### System Management

```bash
# System health check
GET http://localhost:8000/api/system/health
Response: { status, timestamp, databases, service, version }

# List data sources
GET http://localhost:8000/api/system/datasources
Response: { success, data[], total, timestamp }
```

### Market Data

```bash
# Real-time quotes (default 5 stocks)
GET http://localhost:8000/api/market/quotes
GET http://localhost:8000/api/market/quotes?symbols=000001,600519

# Stock list
GET http://localhost:8000/api/market/stocks?limit=100&offset=0
```

### Data Queries

```bash
# K-line data
GET http://localhost:8000/api/data/kline?symbol=000001&limit=100

# Financial data
GET http://localhost:8000/api/data/financial?symbol=000001&report_type=balance
# report_type: balance | income | cashflow
```

---

## 📊 Monitoring Endpoints

### Prometheus Metrics

```bash
# Metrics endpoint (Prometheus format)
GET http://localhost:8000/api/metrics

# Available metrics:
# - mystocks_http_requests_total
# - mystocks_http_request_duration_seconds
# - mystocks_db_connections_active
# - mystocks_cache_hit_rate
# - mystocks_api_health_status
```

---

## 🧪 Testing Commands

### Basic Testing

```bash
# Run all unit tests
pytest

# Verbose output
pytest -v

# Exclude integration tests
pytest -m "not integration"

# Run specific test file
pytest tests/test_akshare_adapter.py

# Run specific test method
pytest tests/test_akshare_adapter.py::TestAkshareAdapter::test_get_stock_daily_success
```

### Coverage Reports

```bash
# Generate coverage report
pytest --cov

# HTML coverage report
pytest --cov --cov-report=html
# Open: htmlcov/index.html

# Terminal + HTML
pytest --cov --cov-report=term --cov-report=html
```

### Advanced Testing

```bash
# Stop on first failure
pytest -x

# Run only failed tests from last run
pytest --lf

# Parallel execution (requires pytest-xdist)
pip install pytest-xdist
pytest -n auto

# Run integration tests only
pytest -m integration
```

---

## 🔧 Validation Tools

### API Health Check

```bash
# Check all 10 API endpoints
python utils/check_api_health_v2.py

# Expected output:
# ✅ Backend accessible
# ✅ 8/10 endpoints working
# Report: check_api_health_report_*.txt
```

### Database Health Check

```bash
# Check all 4 databases
python utils/check_db_health.py

# Expected output:
# ✅ MySQL 9.2.0
# ✅ PostgreSQL 17.6
# ✅ TDengine 3.x
# ✅ Redis 8.0.2
```

---

## 📁 Key Files Reference

### API Files
```
web/backend/app/api/
├── system.py         # System management endpoints
├── market.py         # Market data endpoints
├── data.py          # Data query endpoints
└── metrics.py       # Prometheus metrics endpoint
```

### Test Files
```
tests/
├── conftest.py                   # Shared fixtures
├── test_akshare_adapter.py       # AkShare adapter tests
├── test_tdx_adapter.py           # TDX adapter tests
├── test_database_manager.py      # DB manager tests
└── test_check_db_health.py       # Health check tests
```

### Configuration Files
```
pytest.ini                        # pytest configuration
monitoring/
├── prometheus/
│   ├── prometheus.yml           # Prometheus config
│   └── alerts/mystocks-alerts.yml  # Alert rules
└── grafana/dashboards/
    └── mystocks-overview.json   # Grafana dashboard
```

---

## 🚀 Quick Start Guide

### 1. Start Backend with New APIs

```bash
cd web/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Test New Endpoints

```bash
# Terminal 1: Backend running
# Terminal 2: Run health check
python utils/check_api_health_v2.py
```

### 3. Run Unit Tests

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock pytest-asyncio

# Run tests
pytest -v -m "not integration"

# Generate coverage
pytest --cov --cov-report=html
open htmlcov/index.html
```

### 4. Deploy Monitoring (Optional)

```bash
# Create docker-compose.yml for Prometheus + Grafana
# (See MONITORING_SETUP.md for details)

docker-compose up -d prometheus grafana

# Access Grafana: http://localhost:3000
# Default credentials: admin/admin
# Import dashboard: monitoring/grafana/dashboards/mystocks-overview.json
```

---

## 📊 Metrics Quick Reference

### HTTP Metrics
```python
# Counter
mystocks_http_requests_total{method="GET", endpoint="/api/market/quotes", status="200"}

# Histogram
mystocks_http_request_duration_seconds_bucket{method="GET", endpoint="/api/market/quotes", le="0.5"}
```

### Database Metrics
```python
# Gauge
mystocks_db_connections_active{database="mysql"} 5
mystocks_db_connections_active{database="postgresql"} 8
mystocks_db_connections_active{database="tdengine"} 3
mystocks_db_connections_active{database="redis"} 10
```

### Cache Metrics
```python
# Gauge (0.0 - 1.0)
mystocks_cache_hit_rate{cache_type="redis"} 0.85
```

### Health Metrics
```python
# Gauge (1=healthy, 0=down)
mystocks_api_health_status{service="backend"} 1
mystocks_api_health_status{service="database"} 1
mystocks_api_health_status{service="cache"} 1
```

---

## 🔔 Alert Rules Summary

| Alert | Condition | Duration | Severity |
|-------|-----------|----------|----------|
| HighAPILatency | P95 > 0.5s | 2m | warning |
| HighErrorRate | Error rate > 5% | 5m | critical |
| DatabaseConnectionLow | Connections < 2 | 3m | warning |
| CacheHitRateLow | Hit rate < 0.5 | 5m | warning |
| DatabaseDown | Health = 0 | 1m | critical |
| BackendDown | Health = 0 | 1m | critical |
| HighRequestRate | Rate > 1000/s | 2m | warning |
| SlowDatabaseQueries | Query time > 1s | 3m | warning |

---

## 🐛 Common Issues & Solutions

### Issue: Tests failing with "module not found"
```bash
# Solution: Add project to path
import sys
sys.path.insert(0, '/opt/claude/mystocks_spec')
```

### Issue: Mock not working
```python
# Wrong: Mock at import location
@patch('akshare.stock_zh_a_hist')

# Correct: Mock where it's used
@patch('adapters.akshare_adapter.ak.stock_zh_a_hist')
```

### Issue: Coverage report shows 0%
```bash
# Solution: Clean old data
rm -rf .coverage htmlcov/
pytest --cov
```

### Issue: Integration tests failing
```bash
# Solution: Skip integration tests
pytest -m "not integration"
```

---

## 📚 Documentation Links

- **API Documentation**: `specs/007-short-term-improvements/API_IMPROVEMENTS.md`
- **Monitoring Setup**: `specs/007-short-term-improvements/MONITORING_SETUP.md`
- **Testing Guide**: `specs/007-short-term-improvements/TESTING_GUIDE.md`
- **Feature Summary**: `specs/007-short-term-improvements/FEATURE_007_SUMMARY.md`
- **Changelog**: `CHANGELOG.md` (v2.2.0 section)

---

## 📞 Support

For detailed information, refer to the full documentation:
```bash
ls specs/007-short-term-improvements/
# API_IMPROVEMENTS.md
# MONITORING_SETUP.md
# TESTING_GUIDE.md
# FEATURE_007_SUMMARY.md
# QUICK_REFERENCE.md (this file)
```

---

**Version**: v1.0
**Last Updated**: 2025-10-16
**Maintained By**: MyStocks Development Team
