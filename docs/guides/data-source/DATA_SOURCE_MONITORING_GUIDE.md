# 数据源监控系统集成指南

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


> **版本**: v2.0（当前仓库实现对齐）
> **最后更新**: 2026-05-01
> **相关组件**: DataSourceManagerV2, FastAPI `/metrics`, `src/core/data_source/metrics.py`, `src/monitoring/data_source_metrics.py`

---

## 📊 概述

当前仓库里的“数据源监控”是**双轨实现**，使用前必须区分：

1. **运行时主路径**：`web/backend/app/main.py` 暴露的 `GET /metrics`
   - 底层是 `src/core/middleware/performance.py`
   - 使用全局 Prometheus `REGISTRY`
   - 当前最稳定、最容易直接验证

2. **数据源局部指标链**：`src/core/data_source/metrics.py`
   - 由 `DataSourceManagerV2` 的 `_record_success()` / `_record_failure()` hook 记录
   - 默认使用独立 `CollectorRegistry`
   - 目前已能在本地导出 `datasource_*` exposition 文本

3. **独立 exporter / legacy 路径**：`src/monitoring/data_source_metrics.py` + `scripts/runtime/start_metrics_server.py`
   - 仍可单独启动 `8001` 端口 exporter
   - 适合做独立数据源观测实验或与旧 Prometheus 配置兼容
   - 不是当前仓库里唯一的监控真相源

> **Repo-truth（2026-05-01）**:
> - `GET /metrics` 已在 [main.py](/opt/claude/mystocks_spec/web/backend/app/main.py:735) 存在，但当前主要暴露的是 performance middleware 的全局 registry 指标。
> - `src/core/data_source/metrics.py` 已有 `datasource_api_latency_seconds`、`datasource_api_calls_total`、`datasource_cache_hits_total`、`datasource_circuit_breaker_state` 等指标，并已接到 `DataSourceManagerV2` hook。
> - `src/monitoring/data_source_metrics.py` 与 `scripts/runtime/start_metrics_server.py` 仍存在，但它们不再是唯一监控真相源。
> - 当前仓库已存在并维护数据源监控 dashboard / alert rule 的 canonical 配置：
>   - `config/monitoring-stack/grafana-dashboards/data_source_monitoring.json`
>   - `config/monitoring-stack/config/rules/data-source-alerts.yml`
> - 这些监控产物当前已对齐 `src/core/data_source/metrics.py` 的 `datasource_*` 指标族，并由 `tests/performance/test_validate_monitoring_prometheus_references.py::test_datasource_monitoring_assets_reference_declared_datasource_metrics` 做引用一致性验证。
> - 因此，本指南优先描述当前可直接验证的运行时 `/metrics` 与本地 exposition 用法，再把独立 exporter 标记为可选路径。

---

## 🎯 核心组件

### 1. 运行时 `/metrics` 主路径

**文件**:
- `web/backend/app/main.py`
- `src/core/middleware/performance.py`

**功能**:
- 暴露 FastAPI `GET /metrics`
- 返回全局 `REGISTRY` 的 Prometheus exposition 文本
- 当前主要覆盖 HTTP 请求延迟、请求计数、活跃请求、慢请求等运行时指标

### 2. 数据源局部指标模块

**文件**: `src/core/data_source/metrics.py`

**功能**:
- 定义 `datasource_*` 指标
- 提供 `record_api_call()`、`record_cache_hit()`、`record_circuit_breaker_state()` 等记录接口
- 通过 `generate_metrics()` 直接导出 exposition 文本

**当前已验证的指标**:

| 指标名称 | 类型 | 标签 | 说明 |
|---------|------|------|------|
| `datasource_api_latency_seconds` | Histogram | endpoint, data_category | 数据源 API 延迟 |
| `datasource_api_calls_total` | Counter | endpoint, data_category, status | 数据源 API 调用总数 |
| `datasource_data_quality` | Gauge | endpoint, check_type | 数据质量评分 |
| `datasource_cache_hits_total` | Counter | endpoint | 缓存命中次数 |
| `datasource_cache_misses_total` | Counter | endpoint | 缓存未命中次数 |
| `datasource_circuit_breaker_state` | Gauge | endpoint | 熔断器状态 |
| `datasource_api_cost_estimated` | Gauge | endpoint | 估算 API 成本 |

### 3. 独立 exporter（可选 / legacy）

**文件**:
- `src/monitoring/data_source_metrics.py`
- `scripts/runtime/start_metrics_server.py`

**功能**:
- 在独立端口 `8001` 启动 exporter
- 维护另一组 `data_source_*` 指标
- 适合需要单独抓取数据源指标的场景

> **当前边界**:
> - 当前已有本地证据证明 dashboard JSON 与 Prometheus 告警规则文件存在且引用的指标名与现行 `datasource_*` 指标族一致。
> - 但这仍不等同于 Grafana provisioning、服务启动和浏览器内实际渲染都已完成，因此 `6.11` 类“显示正常”验收项仍需部署环境验证。

---

## 🚀 快速开始

### 路径 A：验证运行时 `/metrics`（当前推荐）

```bash
curl http://localhost:8020/metrics | rg "http_request|slow_http_requests|datasource_"
```

如果当前运行时已经把 `src/core/data_source/metrics.py` 里的 registry 显式并入全局 `REGISTRY`，这里会看到 `datasource_*` 指标；如果没有并入，你至少仍应看到 `http_request_*`、`http_requests_*`、`slow_http_requests_total` 等运行时指标。

### 路径 B：直接验证数据源局部 exposition（本地验证）

```python
from prometheus_client import CollectorRegistry

from src.core.data_source.metrics import DataSourceMetrics

metrics = DataSourceMetrics(registry=CollectorRegistry())
metrics.record_api_call("demo.endpoint", "DAILY_KLINE", latency=0.25, success=True)

print(metrics.generate_metrics().decode("utf-8"))
```

当前仓库已经有对应验证：
- `tests/unit/test_metrics.py`
- `tests/unit/test_data_source_metrics_integration.py`

### 路径 C：启动独立 exporter（可选）

```bash
cd /opt/claude/mystocks_spec
python scripts/runtime/start_metrics_server.py
curl http://localhost:8001/metrics
```

这条路径适合：
- 你希望单独抓取 `src/monitoring/data_source_metrics.py` 的 `data_source_*` 指标
- 你有独立 Prometheus job 指向 `8001`

不适合把它误认为“当前唯一监控主路径”。

### 在代码中使用 metrics

#### 示例1：直接验证 `src/core/data_source/metrics.py`

```python
from prometheus_client import CollectorRegistry

from src.core.data_source.metrics import DataSourceMetrics

metrics = DataSourceMetrics(registry=CollectorRegistry())
metrics.record_api_call("akshare.stock_zh_a_hist", "DAILY_KLINE", latency=0.42, success=True)
metrics.record_cache_hit("akshare.stock_zh_a_hist")
metrics.record_circuit_breaker_state("akshare.stock_zh_a_hist", 0)

print(metrics.generate_metrics().decode("utf-8"))
```

#### 示例2：依赖 `DataSourceManagerV2` 自动 hook

```python
from src.core.data_source.base import DataSourceManagerV2

manager = DataSourceManagerV2()
result = manager.get_stock_daily(symbol="000001")

# 当前 repo-truth：
# - 调用链会进入 handler.py:_call_endpoint()
# - 成功/失败后会触发 _record_success() / _record_failure()
# - 这些 hook 会继续写入 src/core/data_source/metrics.py
```

#### 示例3：使用独立 exporter（可选 / legacy）

```python
from src.monitoring.data_source_metrics import update_call_metrics

update_call_metrics(
    endpoint_name="akshare.stock_zh_a_hist",
    source_name="akshare",
    data_category="DAILY_KLINE",
    success=True,
    response_time=0.42,
    record_count=1000,
)
```

---

## 📋 当前推荐口径

- **想确认服务是否有监控输出**：先看 `http://localhost:8020/metrics`
- **想确认 `DataSourceManagerV2` 是否真的打点**：看 `src/core/data_source/base.py` 的 `_record_success()` / `_record_failure()` hook，以及 `tests/unit/test_data_source_metrics_integration.py`
- **想确认 `datasource_*` exposition 是否可查询**：看 `tests/unit/test_metrics.py`
- **想单独实验旧 exporter**：再用 `python scripts/runtime/start_metrics_server.py`
- **想接 Prometheus / Grafana**：请先确认你的部署侧真的提供了抓取 job、dashboard 和 alert rules；当前仓库不应默认假设这些文件已经存在

---

## 📋 监控指标说明

### 当前两组指标族

| 指标族 | 主要来源 | 典型前缀 | 当前状态 |
|-------|---------|---------|---------|
| 运行时 / 数据源局部指标 | `src/core/middleware/performance.py` + `src/core/data_source/metrics.py` | `http_*`, `slow_http_requests_*`, `datasource_*` | 当前仓库最直接可验证 |
| 独立 exporter 指标 | `src/monitoring/data_source_metrics.py` | `data_source_*` | 可用，但属于 optional / legacy 路径 |

### `datasource_*` 指标（当前主说明对象）

- `datasource_api_latency_seconds`
- `datasource_api_calls_total`
- `datasource_cache_hits_total`
- `datasource_cache_misses_total`
- `datasource_circuit_breaker_state`
- `datasource_api_cost_estimated`

这些指标当前由 `src/core/data_source/metrics.py` 定义，并由 `DataSourceManagerV2` hook 链记录。

### `data_source_*` 指标（独立 exporter 指标族）

- `data_source_up`
- `data_source_response_time_seconds`
- `data_source_calls_total`
- `data_source_success_rate`
- `data_source_health_status`
- `data_source_quality_score`

这组指标来自 `src/monitoring/data_source_metrics.py`，适合旧 exporter 路径或单独实验，不应机械视为当前运行时 `/metrics` 的默认输出。

---

## 🔍 故障排查

### 问题1：`/metrics` 无法访问

**症状**: `curl http://localhost:8020/metrics` 失败或返回非 Prometheus 文本

**排查步骤**:

1. 确认后端服务已启动
   ```bash
   curl -I http://localhost:8020/health
   curl http://localhost:8020/metrics | head
   ```

2. 核对 `web/backend/app/main.py` 中 `/metrics` 路由仍存在

3. 核对 `src/core/middleware/performance.py:metrics_endpoint()` 是否仍使用 `generate_latest()`

### 问题2：看不到 `datasource_*` 指标

**症状**: `/metrics` 只有 `http_*` 等运行时指标，没有 `datasource_*`

**排查步骤**:

1. 先确认数据源调用链确实执行过
2. 直接运行 `tests/unit/test_data_source_metrics_integration.py`
3. 直接实例化 `DataSourceMetrics(...).generate_metrics()`，确认局部 registry 能导出指标

> **当前边界**:
> - 当前仓库并没有本地证据证明所有部署都会把 `src/core/data_source/metrics.py` 的 registry 自动并入运行时全局 `REGISTRY`。
> - 所以“局部指标可记录”与“运行时 `/metrics` 必然直接暴露这些指标”要分开判断。

### 问题3：独立 exporter 无法启动

**症状**: `python scripts/runtime/start_metrics_server.py` 启动失败，或 `8001` 端口冲突

**排查步骤**:

```bash
lsof -i :8001
METRICS_PORT=8002 python scripts/runtime/start_metrics_server.py
curl http://localhost:8002/metrics | head
```

这只说明 optional / legacy exporter 路径是否可用，不影响 `http://localhost:8020/metrics` 主路径本身。

---

## 📈 当前部署建议

### 1. 默认观测顺序

1. 先看运行时 `/metrics`
2. 再看 `DataSourceMetrics.generate_metrics()` 的局部 exposition
3. 最后才考虑独立 exporter

### 2. 关于 PM2 / Prometheus / Grafana

- 当前仓库里没有直接本地证据证明 Prometheus job、Grafana dashboard、告警规则文件已经作为现行部署资产随仓库闭环提供
- 因此这份指南不再把 `pm2 start scripts/runtime/start_metrics_server.py`、`monitoring-stack/config/prometheus.yml`、Grafana dashboard JSON 视为默认生产部署前提
- 如果你的部署环境另行提供这些资产，应把它们视为部署侧扩展，而不是当前 repo-truth

### 3. 建议保留的验证命令

```bash
curl http://localhost:8020/metrics | rg "http_request|slow_http_requests|datasource_"
pytest tests/unit/test_metrics.py tests/unit/test_data_source_metrics_integration.py -q --no-cov
python scripts/runtime/start_metrics_server.py
```

---

## 🎓 扩展接入建议

### 如果你需要接 Prometheus

- 为运行时 `/metrics` 和独立 exporter 分别定义 scrape job
- 不要默认它们输出同一组指标族
- 在抓取配置里显式区分 `datasource_*` 与 `data_source_*`

### 如果你需要接 Grafana / Alerting

- 先根据当前指标族重建 dashboard / alert rules
- 不要直接照搬旧文档里提到但仓库中缺失的 dashboard / provisioning 路径
- 优先以实际 `generate_latest()` 输出为仪表板与告警表达式的事实来源

---

## 📚 相关文档

- **数据源管理V2设计文档**: `docs/architecture/DATA_SOURCE_MANAGEMENT_V2.md`
- **实施报告**: `docs/reports/DATA_SOURCE_V2_IMPLEMENTATION_REPORT.md`
- **SmartRouter 快速参考**: `docs/guides/data-source/DATA_SOURCE_OPTIMIZATION_QUICK_REFERENCE.md`

---

## 🔗 快速链接

- **运行时 Metrics**: http://localhost:8020/metrics
- **独立 exporter Metrics（可选）**: http://localhost:8001/metrics

---

**文档版本**: v2.0（当前仓库实现对齐）
**最后更新**: 2026-05-01
**维护者**: Main CLI
