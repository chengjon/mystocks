# 数据源优化 V2 - 部署检查清单

**版本**: V2.0 (Phase 1 + Phase 2)
**最后更新**: 2026-01-09

---

## ✅ 交付成果验证

### 1. 代码组件 (6 个)

- [x] `src/core/data_source/smart_cache.py` - SmartCache (380 行)
- [x] `src/core/data_source/circuit_breaker.py` - CircuitBreaker (320 行)
- [x] `src/core/data_source/data_quality_validator.py` - DataQualityValidator (580 行)
- [x] `src/core/data_source/smart_router.py` - SmartRouter (420 行)
- [x] `src/core/data_source/metrics.py` - Prometheus Metrics (480 行)
- [x] `src/core/data_source/batch_processor.py` - BatchProcessor (360 行)

### 2. 测试文件 (4 个)

- [x] `tests/unit/test_smart_cache.py` - 16 个测试 (100% 通过)
- [x] `tests/unit/test_circuit_breaker.py` - 12 个测试 (100% 通过)
- [x] `tests/unit/test_data_quality_validator.py` - 15 个测试 (100% 通过)
- [x] `tests/unit/test_smart_router.py` - 12 个测试 (100% 通过)

**总计**: 55 个单元测试，全部通过 ✅

### 3. 文档文件 (4 个)

- [x] `docs/reports/DATA_SOURCE_OPTIMIZATION_PHASE1_COMPLETION_REPORT.md`
- [x] `docs/reports/DATA_SOURCE_OPTIMIZATION_PHASE2_COMPLETION_REPORT.md`
- [x] `docs/guides/DATA_SOURCE_OPTIMIZATION_QUICK_REFERENCE.md`
- [x] `docs/reports/DATA_SOURCE_OPTIMIZATION_FINAL_SUMMARY.md`

### 4. 监控配置 (2 个)

- [x] `grafana/dashboards/data-source-metrics.json` - Grafana 仪表板
- [x] `monitoring-stack/config/rules/data-source-alerts.yml` - Prometheus 告警规则

### 5. 代码集成

- [x] `src/core/data_source/base.py` - 集成 SmartCache 和 CircuitBreaker

---

## 📋 部署前检查清单

### 环境准备

- [ ] **Python 3.12+** 已安装
  ```bash
  python --version  # 应该 >= 3.12
  ```

- [ ] **依赖包** 已安装
  ```bash
  pip install prometheus-client
  pip install pandas numpy
  ```

- [ ] **FastAPI 后端** 正常运行
  ```bash
  # 检查后端是否运行
  curl http://localhost:8000/health
  ```

- [ ] **Prometheus** 正常运行
  ```bash
  # 检查 Prometheus 是否运行
  curl http://localhost:9090/-/healthy
  ```

- [ ] **Grafana** 正常运行
  ```bash
  # 检查 Grafana 是否运行
  curl http://localhost:3000/api/health
  ```

### 配置文件检查

- [ ] **Grafana 仪表板** 已导入
  ```bash
  # 文件位置: grafana/dashboards/data-source-metrics.json
  # 在 Grafana UI 中: Dashboards -> Import -> Upload JSON file
  ```

- [ ] **Prometheus 告警规则** 已加载
  ```bash
  # 文件位置: monitoring-stack/config/rules/data-source-alerts.yml
  # 检查 Prometheus 配置:
  curl http://localhost:9090/api/v1/rules | grep DataSource
  ```

### 代码验证

- [ ] **运行所有单元测试**
  ```bash
  pytest tests/unit/test_smart_cache.py -v
  pytest tests/unit/test_circuit_breaker.py -v
  pytest tests/unit/test_data_quality_validator.py -v
  pytest tests/unit/test_smart_router.py -v
  ```

- [ ] **检查导入路径**
  ```bash
  python -c "from src.core.data_source.smart_cache import SmartCache; print('OK')"
  python -c "from src.core.data_source.circuit_breaker import CircuitBreaker; print('OK')"
  python -c "from src.core.data_source.data_quality_validator import DataQualityValidator; print('OK')"
  python -c "from src.core.data_source.smart_router import SmartRouter; print('OK')"
  python -c "from src.core.data_source.metrics import get_metrics; print('OK')"
  python -c "from src.core.data_source.batch_processor import BatchProcessor; print('OK')"
  ```

---

## 🚀 部署步骤

### 步骤 1: 备份现有代码

```bash
# 备份现有实现
cp src/core/data_source/base.py src/core/data_source/base.py.backup
cp src/core/data_source/cache.py src/core/data_source/cache.py.backup
```

### 步骤 2: 安装依赖

```bash
# 安装 Prometheus 客户端
pip install prometheus-client

# 验证安装
python -c "from prometheus_client import Counter; print('Prometheus client installed')"
```

### 步骤 3: 部署代码 (已完成 ✅)

所有代码文件已经创建，无需额外操作。

### 步骤 4: 配置 FastAPI 集成

在 `web/backend/app/main.py` 中添加 `/metrics` 端点:

```python
from fastapi import Response
from src.core.data_source.metrics import get_metrics

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    metrics_instance = get_metrics()
    return Response(
        content=metrics_instance.generate_metrics(),
        media_type=metrics_instance.get_content_type(),
    )
```

### 步骤 5: 导入 Grafana 仪表板

1. 打开 Grafana: http://localhost:3000
2. 登录 (默认: admin/admin)
3. 导航到: Dashboards → Import
4. 上传文件: `grafana/dashboards/data-source-metrics.json`
5. 选择 Prometheus 数据源
6. 保存仪表板

### 步骤 6: 加载 Prometheus 告警规则

```bash
# 方法1: 复制到 Prometheus 配置目录
cp monitoring-stack/config/rules/data-source-alerts.yml /etc/prometheus/rules/

# 方法2: 在 docker-compose 中挂载
# monitoring-stack/docker-compose.yml:
# volumes:
#   - ./config/rules:/etc/prometheus/rules

# 重启 Prometheus
docker-compose restart prometheus
```

### 步骤 7: 验证部署

```bash
# 1. 测试 FastAPI /metrics 端点
curl http://localhost:8000/metrics

# 2. 检查 Prometheus 指标
curl http://localhost:9090/api/v1/label/__name__/values | grep datasource

# 3. 检查告警规则
curl http://localhost:9090/api/v1/rules | grep DataSource

# 4. 打开 Grafana 仪表板
# http://localhost:3000 -> 选择 "Data Source Metrics" 仪表板
```

---

## 🧪 功能测试

### 测试 1: SmartCache 功能

```python
from src.core.data_source import DataSourceManagerV2

# 启用 SmartCache
manager = DataSourceManagerV2(use_smart_cache=True)

# 获取数据 (应该使用 SmartCache)
data = manager.get_stock_daily("000001", "2024-01-01", "2024-12-31")

# 检查缓存统计
cache = manager.registry.get("akshare.stock_zh_a_hist", {}).get("cache")
print(f"缓存统计: {cache.get_stats()}")
```

**预期结果**:
- 缓存命中率应该 > 0
- 第二次调用应该更快

### 测试 2: CircuitBreaker 功能

```python
from src.core.data_source.circuit_breaker import CircuitBreaker, CircuitBreakerOpenError

cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60, name="test")

# 模拟连续失败
for i in range(3):
    try:
        cb.call(lambda: 1/0)  # 故意失败
    except ZeroDivisionError:
        pass

# 检查状态
print(f"熔断器状态: {cb.get_state()}")  # 应该是 OPEN

# 尝试调用 (应该被拒绝)
try:
    cb.call(lambda: "success")
except CircuitBreakerOpenError as e:
    print(f"正确捕获熔断器异常: {e}")
```

**预期结果**:
- 熔断器状态: OPEN
- 正确抛出 CircuitBreakerOpenError

### 测试 3: Prometheus 指标

```bash
# 1. 生成一些 API 调用
curl http://localhost:8000/api/market/daily?symbol=000001

# 2. 等待几秒

# 3. 查询指标
curl http://localhost:8000/metrics | grep datasource_api_calls_total
```

**预期结果**:
- 应该看到 `datasource_api_calls_total` 指标
- 应该看到 `datasource_api_latency_seconds` 指标

### 测试 4: Grafana 仪表板

1. 打开 Grafana: http://localhost:3000
2. 选择 "Data Source Metrics" 仪表板
3. 检查面板是否正常显示

**预期结果**:
- API Rates 面板: 显示调用速率
- Latency (P95) 面板: 显示 P95 延迟
- Cache Hit/Miss 面板: 显示缓存命中率
- Data Quality 面板: 显示数据质量评分
- Circuit Breaker State 面板: 显示熔断器状态

---

## 📊 监控指标验证

### 关键指标目标

| 指标 | 目标 | 验证命令 |
|------|------|----------|
| 缓存命中率 | > 80% | 查询 Grafana "Cache Hit Rate" 面板 |
| API 成功率 | > 95% | 查询 Grafana "Success Rate" 面板 |
| P95 延迟 | < 200ms | 查询 Grafana "Latency (P95)" 面板 |
| 熔断器开启率 | < 5% | 查询 Grafana "Circuit Breaker State" 面板 |

### 告警验证

触发告警以验证通知是否正常工作:

```bash
# 1. 触发高失败率告警
# 修改数据源配置使其失败，观察是否收到告警

# 2. 检查 Prometheus AlertManager
curl http://localhost:9093/#/alerts
```

---

## 🔧 故障排查

### 问题 1: Prometheus 指标未出现

**症状**: `/metrics` 端点返回空数据

**排查**:
```bash
# 1. 检查 prometheus_client 是否安装
pip list | grep prometheus

# 2. 检查是否正确调用 record_api_call
# 添加日志: logger.info("Recording API call...")

# 3. 检查 Prometheus 配置
# 确保 scrape_configs 包含 FastAPI 服务
```

### 问题 2: Grafana 仪表板无数据

**症状**: 面板显示 "No data"

**排查**:
```bash
# 1. 检查 Prometheus 是否有指标
curl http://localhost:9090/api/v1/label/__name__/values | grep datasource

# 2. 检查 Grafana 数据源配置
# 确保 Prometheus URL 正确: http://localhost:9090

# 3. 检查时间范围
# 确保 Grafana 查询时间范围正确 (Last 5 minutes)
```

### 问题 3: 告警未触发

**症状**: 达到告警条件但未收到通知

**排查**:
```bash
# 1. 检查 Prometheus 告警规则是否加载
curl http://localhost:9090/api/v1/rules | grep DataSource

# 2. 检查告警状态
curl http://localhost:9090/api/v1/alerts

# 3. 检查 AlertManager 配置
# 确保 AlertManager 正确连接到 Prometheus
```

### 问题 4: SmartCache 未启用

**症状**: 缓存命中率为 0

**排查**:
```python
# 检查是否启用了 SmartCache
manager = DataSourceManagerV2(use_smart_cache=True)

# 检查缓存类型
from src.core.data_source.base import DataSourceManagerV2
manager = DataSourceManagerV2()
print(f"使用 SmartCache: {manager.use_smart_cache}")

# 检查缓存实例
cache = manager.registry.get("endpoint_name", {}).get("cache")
print(f"缓存类型: {type(cache).__name__}")  # 应该是 SmartCache
```

---

## 🎯 部署后验证

### 验收标准

- [ ] 所有单元测试通过 (55/55)
- [ ] Prometheus 指标正常采集
- [ ] Grafana 仪表板正常显示
- [ ] 告警规则正常工作
- [ ] 缓存命中率 > 80%
- [ ] API 成功率 > 95%
- [ ] P95 延迟 < 200ms

### 性能基准

运行性能测试，验证优化效果:

```bash
# 1. 测试单个股票获取时间 (预期 < 100ms)
time python -c "
from src.core.data_source import DataSourceManagerV2
manager = DataSourceManagerV2()
manager.get_stock_daily('000001', '2024-01-01', '2024-01-31')
"

# 2. 测试批量获取性能 (预期提升 3-5 倍)
# TODO: 添加批量获取性能测试脚本

# 3. 测试缓存命中率 (预期 > 80%)
# TODO: 添加缓存命中率统计脚本
```

---

## 📝 回滚计划

如果部署后发现问题，执行以下步骤回滚:

### 快速回滚 (< 5 分钟)

```bash
# 1. 恢复原有代码
cp src/core/data_source/base.py.backup src/core/data_source/base.py

# 2. 重启 FastAPI 服务
# 使用您的部署工具 (docker-compose / kubectl / systemd)

# 3. 验证回滚成功
curl http://localhost:8000/health
```

### 配置回滚

```python
# 禁用 SmartCache (使用传统 LRUCache)
manager = DataSourceManagerV2(use_smart_cache=False)

# 禁用 SmartRouter (使用传统路由)
# 不调用 router.route()，直接选择第一个端点
```

---

## ✅ 部署完成

恭喜！如果您完成了以上所有步骤，数据源优化 V2 已经成功部署！

### 下一步行动

1. **监控运行状态**: 持续观察 Grafana 仪表板
2. **收集性能数据**: 记录优化前后的对比数据
3. **优化配置**: 根据实际情况调整 TTL、阈值等参数
4. **收集反馈**: 记录用户反馈和问题

### 支持

如有问题，请参考:
- **快速参考**: `docs/guides/DATA_SOURCE_OPTIMIZATION_QUICK_REFERENCE.md`
- **Phase 1 报告**: `docs/reports/DATA_SOURCE_OPTIMIZATION_PHASE1_COMPLETION_REPORT.md`
- **Phase 2 报告**: `docs/reports/DATA_SOURCE_OPTIMIZATION_PHASE2_COMPLETION_REPORT.md`
- **项目总结**: `docs/reports/DATA_SOURCE_OPTIMIZATION_FINAL_SUMMARY.md`

---

**祝您部署顺利！** 🚀

**检查清单版本**: 1.0
**最后更新**: 2026-01-09
**维护者**: Claude Code
