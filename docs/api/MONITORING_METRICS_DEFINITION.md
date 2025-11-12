# Task 13.1: Custom Monitoring Metrics Definition

**Status**: ✅ COMPLETE
**Date**: 2025-11-12
**Task**: 定义自定义监控指标

## 📊 Monitoring Metrics Framework

### I. Business Metrics (业务指标)

#### 1. 市场数据相关指标
- **mystocks_market_data_points_processed**
  - Type: Counter
  - Description: 已处理的市场数据点数
  - Labels: [datasource, data_type]
  - Unit: count
  - Purpose: Track data ingestion volume

- **mystocks_market_data_latency_seconds**
  - Type: Histogram
  - Description: 市场数据处理延迟
  - Labels: [datasource, data_type]
  - Buckets: [0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
  - Unit: seconds
  - Purpose: Monitor data freshness

- **mystocks_daily_kline_update_count**
  - Type: Counter
  - Description: 日线数据更新数
  - Labels: [data_source]
  - Unit: count
  - Purpose: Track daily update statistics

- **mystocks_tick_data_write_rate**
  - Type: Gauge
  - Description: Tick数据写入速率
  - Labels: [database]
  - Unit: points/second
  - Purpose: Monitor write performance

#### 2. 用户行为相关指标
- **mystocks_user_portfolio_updates_total**
  - Type: Counter
  - Description: 用户组合更新总数
  - Labels: [user_id, action]
  - Unit: count
  - Purpose: Track user activity

- **mystocks_user_watch_list_changes_total**
  - Type: Counter
  - Description: 自选股列表变更总数
  - Labels: [user_id, action]
  - Unit: count
  - Purpose: Monitor watch list activity

- **mystocks_user_active_sessions**
  - Type: Gauge
  - Description: 活跃用户会话数
  - Labels: [platform]
  - Unit: count
  - Purpose: Track concurrent users

#### 3. 交易相关指标
- **mystocks_trade_orders_total**
  - Type: Counter
  - Description: 交易订单总数
  - Labels: [order_type, status]
  - Unit: count
  - Purpose: Track order statistics

- **mystocks_trade_order_latency_seconds**
  - Type: Histogram
  - Description: 订单处理延迟
  - Labels: [order_type]
  - Buckets: [0.01, 0.05, 0.1, 0.5, 1.0]
  - Unit: seconds
  - Purpose: Monitor order processing speed

### II. Technical Metrics (技术指标)

#### 1. API 相关指标
- **mystocks_http_requests_total**
  - Type: Counter
  - Description: HTTP请求总数
  - Labels: [method, endpoint, status]
  - Unit: count
  - Purpose: Track API usage

- **mystocks_http_request_duration_seconds**
  - Type: Histogram
  - Description: HTTP请求延迟
  - Labels: [method, endpoint]
  - Buckets: [0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0]
  - Unit: seconds
  - Purpose: Monitor API response time

- **mystocks_api_error_rate**
  - Type: Gauge
  - Description: API错误率
  - Labels: [endpoint, error_type]
  - Unit: percentage
  - Purpose: Track error rates

#### 2. WebSocket 相关指标
- **mystocks_websocket_connections_active**
  - Type: Gauge
  - Description: 活跃WebSocket连接数
  - Labels: [namespace, version]
  - Unit: count
  - Purpose: Monitor concurrent WebSocket clients

- **mystocks_websocket_messages_sent_total**
  - Type: Counter
  - Description: WebSocket消息发送总数
  - Labels: [message_type, namespace]
  - Unit: count
  - Purpose: Track message traffic

- **mystockets_websocket_messages_received_total**
  - Type: Counter
  - Description: WebSocket消息接收总数
  - Labels: [message_type]
  - Unit: count
  - Purpose: Track incoming messages

- **mystocks_websocket_connection_errors_total**
  - Type: Counter
  - Description: WebSocket连接错误总数
  - Labels: [error_type]
  - Unit: count
  - Purpose: Monitor connection issues

#### 3. 缓存相关指标
- **mystocks_cache_hits_total**
  - Type: Counter
  - Description: 缓存命中总数
  - Labels: [cache_type, key_pattern]
  - Unit: count
  - Purpose: Track cache effectiveness

- **mystocks_cache_misses_total**
  - Type: Counter
  - Description: 缓存未命中总数
  - Labels: [cache_type, key_pattern]
  - Unit: count
  - Purpose: Track cache misses

- **mystocks_cache_hit_rate**
  - Type: Gauge
  - Description: 缓存命中率
  - Labels: [cache_type]
  - Unit: percentage
  - Purpose: Monitor cache efficiency

- **mystocks_cache_evictions_total**
  - Type: Counter
  - Description: 缓存驱逐总数
  - Labels: [cache_type, reason]
  - Unit: count
  - Purpose: Track cache eviction patterns

- **mystocks_cache_memory_usage_bytes**
  - Type: Gauge
  - Description: 缓存内存使用量
  - Labels: [cache_type]
  - Unit: bytes
  - Purpose: Monitor memory consumption

#### 4. 数据库相关指标
- **mystocks_db_connections_active**
  - Type: Gauge
  - Description: 活跃数据库连接数
  - Labels: [database, pool_name]
  - Unit: count
  - Purpose: Monitor connection pool usage

- **mystocks_db_connections_idle**
  - Type: Gauge
  - Description: 空闲数据库连接数
  - Labels: [database, pool_name]
  - Unit: count
  - Purpose: Monitor idle connections

- **mystocks_db_connections_total**
  - Type: Gauge
  - Description: 数据库总连接数
  - Labels: [database]
  - Unit: count
  - Purpose: Track connection limits

- **mystocks_db_query_duration_seconds**
  - Type: Histogram
  - Description: 数据库查询延迟
  - Labels: [database, query_type, table]
  - Buckets: [0.001, 0.01, 0.1, 1.0, 5.0, 10.0]
  - Unit: seconds
  - Purpose: Monitor query performance

- **mystocks_db_connection_errors_total**
  - Type: Counter
  - Description: 数据库连接错误总数
  - Labels: [database, error_type]
  - Unit: count
  - Purpose: Track connection failures

- **mystocks_db_slow_queries_total**
  - Type: Counter
  - Description: 慢查询总数
  - Labels: [database, table]
  - Unit: count
  - Purpose: Monitor slow queries

- **mystocks_db_query_errors_total**
  - Type: Counter
  - Description: 数据库查询错误总数
  - Labels: [database, error_type]
  - Unit: count
  - Purpose: Track query failures

#### 5. 系统资源指标
- **mystocks_process_memory_usage_bytes**
  - Type: Gauge
  - Description: 进程内存使用量
  - Labels: [component]
  - Unit: bytes
  - Purpose: Monitor memory consumption

- **mystocks_process_cpu_usage_percentage**
  - Type: Gauge
  - Description: 进程CPU使用率
  - Labels: [component]
  - Unit: percentage
  - Purpose: Monitor CPU usage

- **mystocks_system_uptime_seconds**
  - Type: Gauge
  - Description: 系统运行时间
  - Labels: [service]
  - Unit: seconds
  - Purpose: Track service availability

- **mystocks_disk_usage_bytes**
  - Type: Gauge
  - Description: 磁盘使用量
  - Labels: [mount_point]
  - Unit: bytes
  - Purpose: Monitor disk space

#### 6. 数据质量指标
- **mystocks_data_completeness_percentage**
  - Type: Gauge
  - Description: 数据完整性百分比
  - Labels: [data_type, source]
  - Unit: percentage
  - Purpose: Monitor data completeness

- **mystocks_data_freshness_minutes**
  - Type: Gauge
  - Description: 数据新鲜度（距最后更新时间）
  - Labels: [data_type]
  - Unit: minutes
  - Purpose: Monitor data staleness

- **mystocks_data_anomalies_detected**
  - Type: Counter
  - Description: 检测到的数据异常数
  - Labels: [data_type, anomaly_type]
  - Unit: count
  - Purpose: Track data quality issues

### III. Alerting Metrics (告警指标)

#### 1. 告警相关指标
- **mystocks_alerts_fired_total**
  - Type: Counter
  - Description: 告警触发总数
  - Labels: [alert_name, severity]
  - Unit: count
  - Purpose: Track alert frequency

- **mystocks_alerts_active**
  - Type: Gauge
  - Description: 当前活跃告警数
  - Labels: [severity]
  - Unit: count
  - Purpose: Monitor ongoing alerts

- **mystocks_alert_resolution_time_seconds**
  - Type: Histogram
  - Description: 告警解决时间
  - Labels: [alert_name]
  - Buckets: [60, 300, 900, 3600, 86400]
  - Unit: seconds
  - Purpose: Track MTTR (Mean Time To Resolution)

#### 2. 系统健康指标
- **mystocks_health_status**
  - Type: Gauge
  - Description: 系统健康状态
  - Labels: [component, status_type]
  - Unit: 1=healthy, 0=unhealthy
  - Purpose: Track component health

- **mystocks_dependency_availability**
  - Type: Gauge
  - Description: 依赖项可用性
  - Labels: [dependency_name]
  - Unit: percentage
  - Purpose: Monitor external dependencies

## 📋 Metrics Collection Strategy

### Collection Hierarchy
```
System Metrics (系统级)
  ├── Infrastructure (基础设施)
  │   ├── CPU, Memory, Disk
  │   └── Network I/O
  │
  ├── Application (应用级)
  │   ├── API Response Time
  │   ├── WebSocket Connections
  │   └── Cache Hit Rate
  │
  ├── Database (数据库级)
  │   ├── Connection Pool
  │   ├── Query Performance
  │   └── Slow Queries
  │
  └── Business (业务级)
      ├── Market Data Processing
      ├── User Activity
      └── Trade Orders
```

### Metric Naming Convention
```
mystocks_<domain>_<metric_name>_<unit>

Examples:
- mystocks_http_request_duration_seconds
- mystocks_db_connections_active
- mystocks_cache_hit_rate
- mystocks_user_active_sessions
```

### Label Strategy
```
Core Labels (必须标签):
- timestamp: 时间戳
- instance: 实例标识
- environment: 环境（prod/staging/dev）

Business Labels (业务标签):
- user_id: 用户ID
- portfolio_id: 组合ID
- datasource: 数据源

Technical Labels (技术标签):
- database: 数据库类型（PostgreSQL/TDengine）
- cache_type: 缓存类型（redis/memory）
- endpoint: API端点路径
```

## 📊 Metric Collection Implementation

### 1. Built-in Metrics (内置指标)
- Prometheus Client Library 自动收集
- Go Client (Golang-based) 或 Python Client

### 2. Custom Application Metrics (自定义应用指标)
- 使用 prometheus_client 库
- 在关键操作处埋点
- 异步上报减少性能影响

### 3. Infrastructure Metrics (基础设施指标)
- Node Exporter (CPU, Memory, Disk)
- PostgreSQL Exporter
- TDengine Exporter (custom)

## 🎯 Key Metrics Priorities

### Critical (P0) - 必须收集
1. **API Response Time** - HTTP端点延迟
2. **Database Connections** - 连接池状态
3. **WebSocket Active Connections** - 实时连接数
4. **System Health** - 系统健康状态
5. **Cache Hit Rate** - 缓存效率

### High (P1) - 应该收集
1. API Error Rate
2. Slow Query Count
3. Data Freshness
4. User Active Sessions
5. Market Data Processing Latency

### Medium (P2) - 可以收集
1. Database Connections (Idle)
2. Memory Usage
3. Disk Usage
4. Trade Order Latency
5. Data Quality Metrics

### Low (P3) - 可选收集
1. Detailed Query Metrics
2. Granular User Activity
3. Component-level CPU Usage
4. Detailed Cache Patterns

## 🔄 Metric Update Frequency

| Metric Type | Frequency | Batch Size |
|------------|-----------|-----------|
| API Metrics | Per Request | N/A |
| WebSocket | Per Message | N/A |
| Cache | Per Operation | N/A |
| Database | Per Query | N/A |
| System Resource | Every 60s | N/A |
| Data Quality | Every 3600s (1h) | N/A |
| Business Metrics | Every 300s (5m) | Batched |

## 📝 Metrics Storage & Retention

### Prometheus Retention Policy
- **Raw Metrics**: 15 days (default)
- **High-resolution**: 24 hours
- **Aggregated**: 1 year (via Thanos)

### Metric Cardinality Limits
- Per metric: < 10,000 unique label combinations
- Total unique series: < 100,000
- Labels per metric: ≤ 5 high-cardinality labels

## ✅ Deliverables Checklist

- [x] Business metrics defined (市场数据、用户行为、交易)
- [x] Technical metrics defined (API、WebSocket、缓存、数据库)
- [x] Alerting metrics defined (告警、健康状态)
- [x] Collection strategy designed
- [x] Naming conventions established
- [x] Priorities defined
- [x] Update frequencies specified
- [x] Storage retention policy defined

## 🔗 Integration Points

### Next Steps (Task 13.2)
- Implement Prometheus Exporter to collect these metrics
- Integrate with existing monitoring infrastructure
- Add instrumentation to key components

### Related Tasks
- **Task 12**: Contract Testing (Completed)
- **Task 13.2**: Prometheus Exporter Development
- **Task 13.3**: Grafana Dashboard Creation
- **Task 13.4**: Alerting Rules Configuration

---

**Task 13.1 Status**: ✅ COMPLETE
**Metrics Defined**: 40+ custom metrics
**Coverage**: Business + Technical + Alerting
**Next**: Implement Prometheus Exporter (Task 13.2)
