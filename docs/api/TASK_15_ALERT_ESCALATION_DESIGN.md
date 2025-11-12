# Task 15.1: Multi-Level Alert Escalation Rules Design

**Status**: ✅ COMPLETE
**Date**: 2025-11-12
**Task**: 多级告警规则设计 (Multi-Level Alert Escalation Design)

## 📋 Alert Escalation Framework Overview

This document defines the complete multi-level alerting architecture for MyStocks, including escalation logic, severity mapping, and response workflows.

## 🎯 Core Design Principles

1. **Progressive Escalation**: Alerts escalate through levels based on duration, count, and impact
2. **Context-Aware Routing**: Alert recipients determined by severity AND category
3. **Smart Suppression**: Prevent alert fatigue through intelligent inhibition
4. **Automatic Recovery**: Clear resolution notifications when conditions improve
5. **Audit Trail**: Complete history for post-incident analysis

## 🚨 Three-Tier Alert Level System

### Level 1 (L1): Critical - Immediate Action Required 🔴

**Characteristics**:
- Immediate business impact
- Requires on-call escalation
- Response time: < 5 minutes
- Escalates to: PagerDuty + SMS + Phone
- Repeat interval: Every 5 minutes until acknowledged

**L1 Alert Categories**:
1. **Infrastructure Failure** (系统基础设施故障)
   - Database connection pool exhausted
   - API service unavailable
   - Core service component unhealthy
   - Dependency critically unavailable

2. **Data Flow Blockage** (数据流中断)
   - Market data processing blocked (0 ops/min)
   - WebSocket service down
   - Critical datasource unavailable

3. **Security/Compliance** (安全合规)
   - Unauthorized access attempts (> 10/min)
   - Data integrity violation
   - Encryption key rotation failure

**L1 Thresholds & Durations**:
```
Alert Name                          | Metric                          | Threshold    | Duration | Escalation
DatabaseConnectionPoolExhausted     | connections_active >= total    | 100%        | 1m       | PagerDuty + SMS
APIServiceUnavailable              | /health response != 200        | 100% fail   | 1m       | PagerDuty + Phone
MarketDataProcessingBlocked        | processing_rate == 0/min      | 0 ops      | 2m       | PagerDuty + SMS
DependencyCriticallyUnavailable    | availability < 50%            | <50%       | 2m       | PagerDuty
ComponentCoreUnhealthy             | health_status == 0            | 0 (down)   | 1m       | PagerDuty + Phone
```

**L1 Response Workflow**:
```
Alert Fires
  ↓ (0 seconds)
PagerDuty Incident Created (High urgency)
  ↓ (Immediate phone/SMS)
On-Call Engineer Paged
  ↓
Engineering Lead Notified (CC'd)
  ↓ (5 minutes)
If no ACK → Escalate to Manager
  ↓ (Alert resolves when condition clears)
Automatic recovery notification sent
```

**SLA Targets**:
- Mean Time To Acknowledge (MTTA): < 5 minutes
- Mean Time To Resolution (MTTR): < 30 minutes
- Escalation to manager: 10 minutes

---

### Level 2 (L2): Warning - Investigate & Fix ⚠️

**Characteristics**:
- Degraded service quality
- Proactive action needed within 1 hour
- Response time: 30 minutes
- Escalates to: Email + Slack + Dashboard
- Repeat interval: Every 30 minutes

**L2 Alert Categories**:
1. **Performance Degradation** (性能下降)
   - API response time p95 > 1s
   - Database slow queries > 1/sec
   - Cache hit rate < 60%
   - WebSocket message latency > 500ms

2. **Resource Pressure** (资源压力)
   - CPU usage > 80% (but < 95%)
   - Memory usage > 2GB (but < 4GB)
   - Disk usage > 10% free (but > 5%)
   - Database connection pool > 80%

3. **Data Quality Issues** (数据质量问题)
   - Data completeness < 90%
   - Data freshness > 30 minutes (but < 60 minutes)
   - Anomaly detection score > 80%

4. **Operational** (运维问题)
   - Multiple alerts active (> 5)
   - Service degradation detected
   - Backup job slow (> 2x baseline)

**L2 Thresholds & Durations**:
```
Alert Name                  | Metric              | Threshold    | Duration | Team
HighAPIResponseTime         | p95 latency        | > 1s        | 5m       | Performance
SlowDatabaseQueries        | slow_query_rate    | > 1/sec     | 5m       | Database
LowCacheHitRate            | hit_rate           | < 60%       | 10m      | Platform
HighCPUUsage               | cpu_percent        | > 80%       | 5m       | Operations
HighMemoryUsage            | memory_mb          | > 2GB       | 5m       | Operations
LowDataCompleteness        | completeness       | < 90%       | 10m      | Data
StaleData                  | staleness_mins     | > 30        | 10m      | Data
HighWebSocketConnections   | active_conns       | > 1000      | 5m       | Platform
```

**L2 Response Workflow**:
```
Alert Fires
  ↓ (30 second wait)
Slack notification to appropriate team channel
  ↓ (Also sent to team email)
Team reviews in next 30 minutes
  ↓
Investigation on dashboard
  ↓ (If escalates to L1)
Escalate to on-call
  ↓ (If resolves naturally)
Recovery notification sent
```

**SLA Targets**:
- Investigation start: Within 30 minutes
- Action: Within 1 hour
- Escalation to L1: If threshold breached

---

### Level 3 (L3): Info - Monitor & Trend 📊

**Characteristics**:
- Informational or trending alerts
- No immediate action required
- Response time: No hard SLA
- Escalates to: Dashboard + Logs only
- Repeat interval: Once per hour (if persistent)

**L3 Alert Categories**:
1. **Trending Metrics** (趋势指标)
   - High connection count (but not exhausted)
   - Increasing error rate trend
   - Growing response time trend
   - Cache eviction rate increase

2. **Usage Patterns** (使用模式)
   - No active user sessions
   - Unusual API usage pattern
   - Off-hours data access
   - Resource allocation approaching limit

3. **Maintenance Reminders** (维护提醒)
   - Log rotation needed
   - Certificate expiry in 30 days
   - Database maintenance window
   - Configuration review recommended

**L3 Thresholds & Durations**:
```
Alert Name              | Metric                | Threshold    | Duration | Channel
NoActiveSessions       | user_sessions         | == 0 (for 5m)| 10m      | Dashboard
HighConnectionCount    | connections           | > 80% (< 100%)| 5m       | Dashboard
TrendingErrorRate      | error_rate_trend      | up > 20%     | 10m      | Dashboard
ApproachingMemoryLimit | memory_percent        | > 75%        | 10m      | Dashboard
```

**L3 Response**:
- No automatic notification
- Visible on dashboard
- May be automatically cleared when trend reverses
- Useful for capacity planning and trend analysis

---

## 🔄 Alert Escalation Logic

### Automatic Escalation Conditions

**L3 → L2 Escalation**:
```
IF Alert persists for > 30 minutes at L3 threshold
  AND showing consistent degradation
  THEN escalate to L2

Example: "No active user sessions" escalates if no users for 30+ minutes
```

**L2 → L1 Escalation**:
```
IF Alert crosses critical threshold
  OR Alert persists at L2 for > 60 minutes with worsening condition
  THEN escalate to L1

Examples:
- Cache hit rate drops from 60% to 30% (crosses critical)
- CPU stays above 80% and rises to 95% (worsening condition)
- Multiple L2 alerts fire simultaneously (service degradation)
```

**L2 → L1 Cascade Escalation**:
```
IF Multiple L2 alerts active (> 3)
  AND they share same root cause (e.g., all database-related)
  THEN escalate to L1 for database team

IF ServiceDegradationDetected = true
  (CPU high + Memory high + Slow queries + API latency)
  THEN escalate to L1 for operations team
```

### Escalation Rules Engine Implementation

```yaml
escalation_rules:
  - name: "performance_cascade"
    source_alert: "HighAPIResponseTime"
    escalation_triggers:
      - condition: "duration > 10m AND value > 5s"  # p99 > 5s for 10m
        action: "escalate_to_l1"
        recipients: ["performance_team_lead", "on_call"]
      - condition: "duration > 5m AND count(related_alerts) > 2"
        action: "escalate_to_l1"
        notify: ["performance_team", "operations_team"]

  - name: "resource_pressure_cascade"
    watch_alerts:
      - "HighCPUUsage"
      - "HighMemoryUsage"
      - "HighDiskUsage"
    escalation_triggers:
      - condition: "all_3_active OR any_2_critical"
        action: "escalate_to_l1"
        recipients: ["operations_lead", "on_call"]

  - name: "data_integrity_cascade"
    watch_alerts:
      - "LowDataCompleteness"
      - "StaleData"
      - "DataQualityAnomaly"
    escalation_triggers:
      - condition: "count > 2 OR any_critical"
        action: "escalate_to_l1"
        recipients: ["data_team_lead"]

  - name: "user_impact_cascade"
    watch_alerts:
      - "APIServiceUnavailable"
      - "MarketDataProcessingBlocked"
      - "DependencyCriticallyUnavailable"
    escalation_triggers:
      - condition: "any_active"
        action: "escalate_to_l1_immediately"
        recipients: ["on_call", "engineering_lead", "cto"]
```

---

## 🎯 Alert Routing Matrix

### By Severity & Category

```
┌─────────────────┬────────────────┬──────────────────┬──────────────┐
│ Severity        │ Category       │ Primary Receiver │ Escalation   │
├─────────────────┼────────────────┼──────────────────┼──────────────┤
│ L1 (Critical)   │ Infra/Data     │ PagerDuty        │ SMS + Phone  │
│                 │ Security       │ On-call + CTO    │ Phone Call   │
│                 │ Any            │ Engineering Lead │ WhatsApp     │
├─────────────────┼────────────────┼──────────────────┼──────────────┤
│ L2 (Warning)    │ Performance    │ Slack #perf      │ L1 after 1h  │
│                 │ Database       │ Slack #db        │ L1 after 1h  │
│                 │ Data Quality   │ Slack #data      │ L1 after 1h  │
│                 │ Operations     │ Slack #ops       │ L1 after 1h  │
├─────────────────┼────────────────┼──────────────────┼──────────────┤
│ L3 (Info)       │ All            │ Dashboard only   │ L2 after 30m │
└─────────────────┴────────────────┴──────────────────┴──────────────┘
```

---

## 📊 Complete Alert Mapping

### Production Alert Definitions

#### Category: Infrastructure (基础设施) - L1/L2

| Alert Name | L1 Condition | L2 Condition | Root Cause Detector |
|---|---|---|---|
| DatabaseConnectionPoolExhausted | >= 100% | >= 80% | Check slow queries, connection leak detection |
| APIServiceUnavailable | /health fails | Response time > 5s | Check service logs, dependency status |
| DependencyCriticallyUnavailable | < 50% uptime | < 90% uptime | Check external service status |
| ComponentUnhealthy | Any down | Flapping (up/down) | Check component logs, restart count |
| HighMemoryUsage | > 4GB | > 2GB | Check process memory, cache size, connection count |
| CriticalCPUUsage | > 95% | > 80% | Check slow queries, API requests, computation |
| CriticalDiskSpace | < 5% free | < 10% free | Check log rotation, database size |

#### Category: Data Processing (数据处理) - L1/L2

| Alert Name | L1 Condition | L2 Condition | Root Cause |
|---|---|---|---|
| MarketDataProcessingBlocked | 0 ops/min for 2m | < 10 ops/min | Check datasource, processor health |
| SlowMarketDataProcessing | p95 > 5s | p95 > 2s | Check processor load, network latency |
| StaleData | > 60 min | > 30 min | Check data pipeline, datasource |
| LowDataCompleteness | < 70% | < 90% | Check data source, validation rules |

#### Category: API Performance (API性能) - L1/L2

| Alert Name | L1 Condition | L2 Condition | Root Cause |
|---|---|---|---|
| CriticalAPIErrorRate | > 20% (500 errors) | > 5% | Check recent deployments, dependency status |
| CriticalAPIResponseTime | p99 > 10s | p95 > 1s | Check database load, cache efficiency |
| HighAPIErrorRate | > 10% | > 5% | Check error logs for patterns |

#### Category: Cache (缓存) - L2/L3

| Alert Name | L2 Condition | L3 Condition | Root Cause |
|---|---|---|---|
| CriticalCacheHitRate | < 30% | < 60% | Check cache size, eviction policy |
| HighCacheMemoryUsage | > 500MB | > 300MB | Check cache eviction, TTL settings |

---

## 🔗 Alert Dependency & Correlation

### Alert Clusters (Groups of Related Alerts)

```
Cluster 1: "Database Performance Crisis"
├── HighDatabaseConnections (L2)
├── SlowDatabaseQueries (L2)
├── HighDatabaseQueryTimeout (L2)
└── Escalates to L1 if any 2+ active

Cluster 2: "Data Integrity Issue"
├── LowDataCompleteness (L2)
├── StaleData (L2)
├── DataQualityAnomaly (L2)
└── Escalates to L1 if > 2 active OR any critical

Cluster 3: "Service Degradation"
├── CriticalAPIErrorRate (L1)
├── CriticalAPIResponseTime (L1)
├── MarketDataProcessingBlocked (L1)
└── Escalates to all-hands if any active

Cluster 4: "Resource Saturation"
├── HighCPUUsage (L2)
├── HighMemoryUsage (L2)
├── HighDiskUsage (L2)
└── Escalates to L1 if all 3 active
```

### Root Cause Analysis Hints

Each alert includes common root causes for faster diagnosis:

```json
{
  "alert": "SlowDatabaseQueries",
  "probable_causes": [
    "Missing database index",
    "Table scan on large table",
    "Slow network to database",
    "Database CPU saturation",
    "Connection pool exhaustion"
  ],
  "investigation_steps": [
    "Check pg_stat_statements for slow query details",
    "Review EXPLAIN ANALYZE output",
    "Check system CPU and disk I/O",
    "Verify index usage",
    "Check connection pool status"
  ],
  "quick_fixes": [
    "Add missing index",
    "Kill long-running queries",
    "Scale database vertically",
    "Restart connection pool"
  ]
}
```

---

## 📈 Escalation Timeline

### Example Scenario: Data Pipeline Issue

```
Time    | Event                           | Alert Level | Status
--------|--------------------------------|-------------|--------
00:00   | Data source update slower     | L3 Info     | Noticed on dashboard
00:15   | Slowness persists, latency 2s | L2 Warning  | Slack notification sent
00:30   | Latency jumps to 15s           | L1 Critical | PagerDuty triggered, on-call paged
00:32   | On-call acknowledges incident  | L1          | Investigation begins
00:45   | Root cause identified (slow AP) | L1          | Incident being worked
01:00   | Issue resolved, data flowing   | L1→Resolving| Alert clears automatically
01:02   | Recovery notification sent     | Cleared     | Team notified via Slack
```

---

## 🔧 Configuration Structure

### AlertManager Escalation Rules (YAML)

```yaml
escalation_config:
  version: "1.0"

  levels:
    critical:
      wait_time: 0s
      repeat_interval: 5m
      receivers:
        - type: "pagerduty"
          urgency: "high"
        - type: "sms"
          recipients: ["on_call_phone"]
        - type: "slack"
          channels: ["#mystocks-critical"]
        - type: "email"
          recipients: ["eng_lead@mystocks.com"]

    warning:
      wait_time: 30s
      repeat_interval: 30m
      receivers:
        - type: "slack"
          channels: ["#mystocks-warnings", "#team-{category}"]
        - type: "email"
          recipients: ["team_lead@mystocks.com"]

    info:
      wait_time: 60s
      repeat_interval: 1h
      receivers:
        - type: "dashboard"
        - type: "logs"

  escalation_rules:
    - name: "l3_to_l2"
      source: "info"
      condition: "duration > 30m AND degrading"
      target: "warning"

    - name: "l2_to_l1"
      source: "warning"
      condition: "value > critical_threshold OR duration > 60m"
      target: "critical"

    - name: "cascade_escalation"
      source: "warning"
      condition: "active_count > 3 AND related"
      target: "critical"
      notifiers: ["related_team_lead"]
```

---

## ✅ Design Validation

- [x] Clear severity definitions with measurable thresholds
- [x] Automatic escalation logic for progressive urgency
- [x] Multiple notification channels per level
- [x] Root cause guidance for each alert
- [x] SLA targets defined
- [x] Cascade detection for correlated failures
- [x] Configuration-driven ruleset
- [x] Integration with Task 13 alert rules

---

## 📚 Summary

**Task 15.1 Deliverables**:

| Item | Details |
|------|---------|
| Alert Levels Defined | L1 (Critical), L2 (Warning), L3 (Info) |
| L1 Alerts | 6 critical categories, immediate escalation |
| L2 Alerts | 12+ warning conditions, investigation-focused |
| L3 Alerts | 4+ informational metrics, trend-based |
| Escalation Rules | 5+ automatic escalation conditions defined |
| Routing Matrix | Complete severity × category mapping |
| Response Times | MTTA < 5min (L1), 30min (L2), async (L3) |
| Root Cause Info | Probable causes for each alert category |
| Configuration Schema | YAML-based ruleset definition |

**Status**: ✅ COMPLETE - Multi-level alert escalation design fully specified

---

**Next Task**: 15.2 - Alert Aggregation and Suppression Mechanism

