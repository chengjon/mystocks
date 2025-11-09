# Monitoring & Quality API Contract

**创建人**: Claude (自动生成)
**版本**: 1.0.0
**创建日期**: 2025-10-11

## API概述

监控与质量保证API提供独立的可观测性接口,记录所有操作日志、性能指标和数据质量检查结果。所有数据存储在独立的监控数据库(PostgreSQL),与业务数据库物理分离。

---

## 1. MonitoringDatabase API

### 1.1 log_operation()

记录数据库操作日志。

```python
def log_operation(
    operation_type: str,
    classification: DataClassification,
    database_target: str,
    table_name: str,
    record_count: int,
    success: bool,
    duration_ms: float,
    error_message: Optional[str] = None,
    operation_details: Optional[Dict] = None
) -> str:
    """
    记录操作日志

    Returns:
        operation_id: str - 操作记录ID
    """
```

---

## 2. PerformanceMonitor API

### 2.1 track_query_performance()

跟踪查询性能。

```python
def track_query_performance(
    query_type: str,
    database_target: str,
    execution_time_ms: float,
    threshold_ms: float = 5000
) -> None:
    """
    跟踪查询性能,超过阈值自动告警
    """
```

---

## 3. DataQualityMonitor API

### 3.1 check_data_completeness()

检查数据完整性。

```python
def check_data_completeness(
    classification: DataClassification,
    expected_count: int,
    actual_count: int
) -> Dict[str, Any]:
    """
    检查数据完整性

    Returns:
        {
            'completeness_rate': float,
            'missing_count': int,
            'check_result': str  # PASS/WARNING/FAIL
        }
    """
```

---

## 4. AlertManager API

### 4.1 send_alert()

发送告警通知。

```python
def send_alert(
    alert_level: str,  # INFO/WARNING/ERROR/CRITICAL
    alert_source: str,
    alert_message: str,
    context: Optional[Dict] = None
) -> None:
    """
    发送多渠道告警
    """
```

---

**文档版本**: 1.0.0
