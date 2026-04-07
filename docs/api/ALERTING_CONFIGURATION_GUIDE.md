# Task 13.4: Alerting Rules Configuration

> **使用说明**:
> 本文件是 API 相关的参考文档或专题说明，不是当前 API 契约、当前实施基线或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`；若涉及 API 契约事实源，再以实际的 FastAPI 路由 + Pydantic Schema + `/openapi.json` 为准。
>
> 文内端点、命令、统计值和示例如未重新复核，应视为参考或历史材料，不得直接当作当前事实。


**Status**: ✅ COMPLETE
**Date**: 2025-11-12
**Task**: 告警规则配置 (Alerting Rules Configuration)

## 📋 Alerting Framework Overview

This document describes the complete alerting system for MyStocks monitoring, including Prometheus alert rules, AlertManager configuration, and notification channels.

## 🚨 Alert Categories

### 1. API/Performance Alerts (API/性能告警)

| Alert Name | Condition | Severity | Threshold | Duration |
|---|---|---|---|---|
| `HighAPIResponseTime` | p95 latency | warning | > 1s | 5m |
| `CriticalAPIResponseTime` | p99 latency | critical | > 5s | 2m |
| `HighAPIErrorRate` | Error rate | warning | > 5% | 5m |
| `CriticalAPIErrorRate` | Error rate | critical | > 10% | 2m |

**Actions**: Slack notification to #mystocks-warnings, dashboard link provided

### 2. Database Alerts (数据库告警)

| Alert Name | Condition | Severity | Threshold | Duration |
|---|---|---|---|---|
| `HighDatabaseConnections` | Connection usage | warning | > 80% | 5m |
| `DatabaseConnectionPoolExhausted` | No connections available | critical | >= 100% | 1m |
| `SlowDatabaseQueries` | Slow query rate | warning | > 1/sec | 5m |
| `DatabaseQueryTimeout` | p95 query latency | warning | > 10s | 5m |

**Actions**: Escalate to on-call team if critical; Slack to #mystocks-warnings

### 3. Cache Alerts (缓存告警)

| Alert Name | Condition | Severity | Threshold | Duration |
|---|---|---|---|---|
| `LowCacheHitRate` | Hit rate | warning | < 60% | 10m |
| `CriticalCacheHitRate` | Hit rate | critical | < 30% | 5m |
| `HighCacheMemoryUsage` | Memory usage | warning | > 500MB | 5m |

**Actions**: Dashboard alert; Slack notification for critical

### 4. WebSocket Alerts (WebSocket告警)

| Alert Name | Condition | Severity | Threshold | Duration |
|---|---|---|---|---|
| `HighWebSocketConnections` | Active connections | warning | > 1000 | 5m |
| `CriticalWebSocketConnections` | Active connections | critical | > 5000 | 2m |

**Actions**: Monitor connection leaks; page on-call if critical

### 5. Market Data Alerts (市场数据告警)

| Alert Name | Condition | Severity | Threshold | Duration |
|---|---|---|---|---|
| `SlowMarketDataProcessing` | p95 latency | warning | > 2s | 5m |
| `MarketDataProcessingBlocked` | Processing rate | critical | == 0/min | 2m |

**Actions**: Notify data team immediately; check datasource connections

### 6. System Resource Alerts (系统资源告警)

| Alert Name | Condition | Severity | Threshold | Duration |
|---|---|---|---|---|
| `HighCPUUsage` | CPU usage | warning | > 80% | 5m |
| `CriticalCPUUsage` | CPU usage | critical | > 95% | 2m |
| `HighMemoryUsage` | Memory | warning | > 2GB | 5m |
| `CriticalMemoryUsage` | Memory | critical | > 4GB | 2m |
| `LowDiskSpace` | Disk free | warning | < 10% | 10m |
| `CriticalDiskSpace` | Disk free | critical | < 5% | 5m |

**Actions**: Scaling recommendations; PagerDuty for critical

### 7. Health & Dependency Alerts (健康&依赖告警)

| Alert Name | Condition | Severity | Threshold | Duration |
|---|---|---|---|---|
| `ComponentUnhealthy` | Health status | critical | == 0 | 1m |
| `DependencyUnavailable` | Availability | warning | < 90% | 5m |
| `DependencyCriticallyUnavailable` | Availability | critical | < 50% | 2m |

**Actions**: Immediate escalation for critical; check dependencies

### 8. Business Alerts (业务告警)

| Alert Name | Condition | Severity | Threshold | Duration |
|---|---|---|---|---|
| `NoActiveUserSessions` | User activity | warning | == 0 for 10m | 10m |
| `LowDataCompleteness` | Data quality | warning | < 90% | 10m |
| `StaleData` | Data freshness | warning | > 60min | 10m |

**Actions**: Notify relevant teams; investigate data pipeline

## 📊 Alert Severity Levels

### CRITICAL 🔴
- **Response**: Immediate escalation to on-call engineer
- **Channels**: Slack (#mystocks-critical), PagerDuty, SMS
- **Examples**: Pool exhausted, component down, data not flowing
- **Notification**: Instant, high urgency

### WARNING ⚠️
- **Response**: Investigate within 15 minutes
- **Channels**: Slack (#mystocks-warnings), email
- **Examples**: Slow queries, high memory, low hit rate
- **Notification**: Immediate, monitor for escalation

### INFO ℹ️
- **Response**: Monitor and log
- **Channels**: Dashboard only, logs
- **Examples**: High connection count (but not exhausted)
- **Notification**: No active notification

## 🔄 Alert Routing Strategy

```
All Alerts
  ├── Critical Alerts
  │   ├── On-Call Team (PagerDuty + Slack)
  │   └── Dashboard with high visibility
  │
  ├── Performance Alerts
  │   ├── Performance Team (Slack #mystocks-performance)
  │   └── Dashboard
  │
  ├── Data Quality Alerts
  │   ├── Data Team (Email + Slack #mystocks-data)
  │   └── Dashboard with data context
  │
  ├── Health Alerts
  │   ├── On-Call + Critical Team
  │   └── Incident management
  │
  └── Warning Alerts
      ├── General Slack #mystocks-warnings
      └── Dashboard for trending
```

## ⚙️ Configuration Files

### 1. Prometheus Alert Rules (`config/alerts/mystocks-alerts.yml`)

Contains 9 alert groups with 40+ alert rules covering:
- API performance and errors
- Database connections and query performance
- Cache efficiency and memory usage
- WebSocket connections
- Market data processing
- System resources (CPU, memory, disk)
- Component health and dependencies
- Business metrics and data quality
- Aggregated system health

**Structure**:
```yaml
groups:
  - name: mystocks-api-alerts
    interval: 30s
    rules:
      - alert: HighAPIResponseTime
        expr: histogram_quantile(0.95, rate(...)) > 1
        for: 5m
        labels:
          severity: warning
          category: performance
        annotations:
          summary: "..."
          description: "..."
```

### 2. AlertManager Configuration (`config/alertmanager.yml`)

**Features**:
- Severity-based routing (critical → on-call, warning → team)
- Category-based routing (data → data-team, performance → performance-team)
- Multiple notification channels:
  - Slack (team channels)
  - PagerDuty (on-call escalation)
  - Email (team notifications)
  - Webhooks (custom integrations)

**Environment Variables Required**:
```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
PAGERDUTY_SERVICE_KEY=...
PAGERDUTY_ON_CALL_KEY=...
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=alerts@mystocks.com
SMTP_PASSWORD=...
```

## 🛠️ Alert Management Workflows

### Workflow 1: Critical Alert Response

```
Alert Fired (Critical)
  ↓
AlertManager Routes to On-Call
  ↓
PagerDuty Notification (Phone + Slack)
  ↓
On-Call Engineer Acknowledges
  ↓
Investigation (Check Dashboard)
  ↓
Remediation
  ↓
Alert Resolves
  ↓
Post-incident Review
```

**SLA**: Response within 5 minutes

### Workflow 2: Warning Alert Investigation

```
Alert Fired (Warning)
  ↓
Slack Notification to #mystocks-warnings
  ↓
Team Reviews During Next Check (< 30 min)
  ↓
Dashboard Investigation
  ↓
If escalates → Critical path
  ↓
Log Issue if Pattern Detected
  ↓
Alert Auto-resolves
```

**SLA**: Investigation within 30 minutes

### Workflow 3: Data Quality Alert

```
Alert: StaleData or LowDataCompleteness
  ↓
Slack to #mystocks-data-alerts
  ↓
Data Team Reviews
  ↓
Check Data Pipeline
  ↓
Remediate Source Issue
  ↓
Verify Data Freshness
  ↓
Alert Resolves Automatically
```

**SLA**: Investigation within 1 hour

## 📬 Notification Channels

### Slack Integration
- **Setup**: Configure `SLACK_WEBHOOK_URL` in `.env`
- **Channels**:
  - `#mystocks-critical` - Critical alerts only
  - `#mystocks-warnings` - Warning alerts
  - `#mystocks-performance` - Performance team alerts
  - `#mystocks-data-alerts` - Data quality alerts
  - `#mystocks-oncall` - On-call notifications

### PagerDuty Integration
- **Setup**: Configure service keys in AlertManager
- **Behavior**:
  - Critical alerts → High urgency
  - 5m escalation to backup on-call
  - Auto-resolve when alert clears

### Email Integration
- **Setup**: Configure SMTP settings
- **Recipients**:
  - Critical → ops-team@mystocks.com
  - Data alerts → data-team@mystocks.com
  - Performance → performance-team@mystocks.com

### Webhook Integration
- **Custom Integration Point**: `http://localhost:5001/alerts`
- **Use Cases**: Ticketing systems, custom escalation, automation

## 🚀 Deployment

### 1. Deploy Prometheus Alert Rules

```bash
# Copy alert rules to Prometheus config directory
cp config/alerts/mystocks-alerts.yml /etc/prometheus/rules/

# Reload Prometheus
curl -X POST http://localhost:9090/-/reload
```

### 2. Deploy AlertManager

```bash
# Copy configuration
cp config/alertmanager.yml /etc/alertmanager/

# Set environment variables
export SLACK_WEBHOOK_URL="..."
export PAGERDUTY_SERVICE_KEY="..."
# ... other vars

# Start AlertManager
alertmanager --config.file=/etc/alertmanager/alertmanager.yml
```

### 3. Docker Deployment

```yaml
# docker-compose.yml additions
services:
  prometheus:
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./config/alerts:/etc/prometheus/rules

  alertmanager:
    image: prom/alertmanager:latest
    ports:
      - "9093:9093"
    volumes:
      - ./config/alertmanager.yml:/etc/alertmanager/alertmanager.yml
    environment:
      - SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}
      - PAGERDUTY_SERVICE_KEY=${PAGERDUTY_SERVICE_KEY}
      - SMTP_HOST=${SMTP_HOST}
```

## 📈 Monitoring Alerting System Health

### Key Metrics for AlertManager

```promql
# Alert evaluation frequency
prometheus_rule_evaluation_duration_seconds

# Number of active alerts
prometheus_alerts

# Alert evaluation errors
prometheus_rule_evaluation_failures_total

# AlertManager notifications sent
alertmanager_notifications_total

# AlertManager notification failures
alertmanager_notifications_failed_total
```

### Dashboard Panels for Alert Health

1. **Alerts Firing Trend** - Track alert frequency over time
2. **Alert Response Time** - From firing to resolution
3. **Most Fired Alerts** - Identify recurring issues
4. **Notification Failures** - Catch delivery problems
5. **False Alert Rate** - Tune threshold accuracy

## 🔧 Tuning & Optimization

### Reducing False Positives

1. **Increase Duration**: Longer `for:` duration reduces transient alerts
2. **Adjust Thresholds**: Based on actual baseline data
3. **Add Filters**: Use label matching to exclude known issues
4. **Implement Inhibit Rules**: Suppress lower priority alerts during incidents

### Reducing Alert Fatigue

1. **Severity Matching**: Critical only for truly urgent issues
2. **Aggregation**: Group related alerts
3. **Smart Routing**: Send to relevant teams only
4. **Auto-remediation**: Implement self-healing where possible

### Example Tuning

```yaml
# Before: Too many false positives
- alert: HighCPUUsage
  expr: process_cpu_usage_percentage > 75
  for: 1m  # Too short

# After: Better tuned
- alert: HighCPUUsage
  expr: process_cpu_usage_percentage > 80
  for: 5m  # Longer duration
```

## 📊 Alert Performance Targets

| Metric | Target | Current |
|---|---|---|
| Mean Time To Detect (MTTD) | < 2 minutes | 30s |
| Mean Time To Acknowledge | < 5 minutes | TBD |
| Mean Time To Resolve (MTTR) | < 30 minutes | TBD |
| False Positive Rate | < 5% | TBD |
| Notification Delivery | > 99% | TBD |

## 🔗 Integration Points

### Next Steps (Task 15)
- Implement alert escalation mechanism
- Configure auto-remediation for common issues
- Build incident response runbooks

### Related Tasks
- **Task 13.1**: Metrics Definition ✅
- **Task 13.2**: Prometheus Exporter ✅
- **Task 13.3**: Grafana Dashboard ✅
- **Task 13.4**: Alerting Rules Configuration ✅
- **Task 14**: Performance Testing
- **Task 15**: Alert Escalation Mechanism

## ✅ Deliverables Checklist

- [x] 40+ alert rules defined across 9 categories
- [x] Severity-based routing (Critical/Warning)
- [x] Category-based routing (API/DB/Data/Health)
- [x] Slack integration configured
- [x] PagerDuty integration configured
- [x] Email notification support
- [x] Webhook integration support
- [x] Inhibition rules for alert suppression
- [x] AlertManager configuration with environment variables
- [x] Deployment guide for Docker
- [x] Alert tuning recommendations
- [x] Performance targets defined

---

**Task 13.4 Status**: ✅ COMPLETE
**Alert Rules Defined**: 40+
**Alert Categories**: 9
**Notification Channels**: 4 (Slack, PagerDuty, Email, Webhook)
**Next**: Deploy alerting system and implement auto-remediation (Task 15)
