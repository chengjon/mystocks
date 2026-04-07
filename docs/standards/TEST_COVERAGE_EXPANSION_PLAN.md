# 测试覆盖率扩展计划 (4-6小时目标: 80%)

> **历史计划说明**:
> 本文件是标准治理相关的阶段性计划、推进方案或后续行动材料，不是当前门禁基线或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码及现行标准文档一并复核。
>
> 文内时间线、任务状态和建议动作如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


**日期**: 2025-11-23
**当前覆盖率**: 7% (28,598 / 30,623 lines)
**目标覆盖率**: 80%
**需要新增**: 约 15,500 行测试代码

---

## 📊 当前覆盖率分析

### 整体概况
- **总代码行数**: 30,623 行
- **已覆盖行数**: 28,598 行
- **覆盖率**: 7%
- **单元测试**: 548 passed, 16 skipped

### 模块级别覆盖率

#### ✅ 高覆盖率模块 (> 80%)
- `src/core/data_classification.py` - 100%
- `src/core/data_manager.py` - 100%
- `src/core/logging.py` - 98%
- `src/core/exceptions.py` - 89%
- `src/core/batch_failure_strategy.py` - 86%

#### 🟡 中等覆盖率 (50-80%)
- `src/core/config_driven_table_manager.py` - 71%
- `src/core/unified_manager.py` - 70%
- `src/data_access/postgresql_access.py` - 69%
- `src/data_access/tdengine_access.py` - 69%
- `src/monitoring/alert_manager.py` - 50%

#### 🔴 低覆盖率模块 (< 50%)
- `src/monitoring/monitoring_database.py` - 29%
- `src/monitoring/data_quality_monitor.py` - 18%
- **所有adapter模块 - 0%** (akshare, baostock, financial, tdx, etc.)
- **src/data_access.py - 0%** (514 lines)
- **src/monitoring/** - 大多数 0% (ai_alert_manager, alert_notifier, 等)
- **src/backup_recovery/** - 0%
- **src/contract_testing/** - 0%
- **web/backend/app/** - 大多数 0%

---

## 🎯 优先级分析与测试计划

### 优先级 1️⃣: 关键adapter模块 (预估: 3-4小时)

**模块列表**:
- `src/adapters/akshare_adapter.py` - 327 lines (0%)
- `src/adapters/financial_adapter.py` - 569 lines (0%)
- `src/adapters/tdx_adapter.py` - 472 lines (0%)
- `src/adapters/customer_adapter.py` - 268 lines (0%)
- `src/adapters/baostock_adapter.py` - 151 lines (0%)
- `src/adapters/tushare_adapter.py` - 113 lines (0%)
- `src/adapters/byapi_adapter.py` - 236 lines (0%)

**目标**: 至少覆盖每个adapter的关键方法（50%+ 覆盖率）

**测试策略**:
```python
# tests/unit/adapters/test_akshare_adapter.py
class TestAkshareAdapter:
    - test_init()  # 初始化
    - test_get_kline_data()  # K线数据获取
    - test_get_stock_list()  # 股票列表
    - test_error_handling()  # 错误处理
    - test_data_transformation()  # 数据转换

# 为每个主要adapter创建对应的测试文件
```

**预期效果**: 增加 ~2000-2500 行测试代码，覆盖率可提升 15-20%

---

### 优先级 2️⃣: 监控模块 (预估: 1.5-2小时)

**当前状态**:
- `src/monitoring/alert_manager.py` - 50%
- `src/monitoring/monitoring_database.py` - 29%
- `src/monitoring/data_quality_monitor.py` - 18%
- `src/monitoring/alert_notifier.py` - 0%
- `src/monitoring/gpu_integration_manager.py` - 0%

**关键测试**:
```python
# tests/unit/monitoring/test_alert_manager.py
class TestAlertManager:
    - test_send_alert()
    - test_alert_severity_levels()
    - test_alert_retry_logic()
    - test_multi_channel_notification()

# tests/unit/monitoring/test_monitoring_database.py
class TestMonitoringDatabase:
    - test_log_operation()
    - test_query_by_date_range()
    - test_performance_metrics()
    - test_data_retention_policy()

# tests/unit/monitoring/test_data_quality_monitor.py
class TestDataQualityMonitor:
    - test_completeness_check()
    - test_accuracy_validation()
    - test_freshness_check()
    - test_alert_on_violation()
```

**预期效果**: 增加 ~800-1000 行测试代码，覆盖率可提升 8-12%

---

### 优先级 3️⃣: 数据访问层 (预估: 1.5-2小时)

**当前状态**:
- `src/data_access.py` - 0% (514 lines - 可能是入口点)
- `src/data_access/postgresql_access.py` - 69% (205 lines)
- `src/data_access/tdengine_access.py` - 69% (178 lines)

**测试计划**:
```python
# tests/unit/data_access/test_data_access_integration.py
class TestDataAccessIntegration:
    - test_auto_routing_by_classification()
    - test_save_to_correct_database()
    - test_load_from_correct_database()
    - test_fallback_mechanisms()

# 完善 PostgreSQL 和 TDengine 的覆盖
# - 连接管理
# - 事务处理
# - 错误恢复
# - 性能优化
```

**预期效果**: 增加 ~600-800 行测试代码，覆盖率可提升 10-15%

---

### 优先级 4️⃣: 备份恢复模块 (预估: 0.5-1小时)

**模块列表**:
- `src/backup_recovery/backup_manager.py` - 230 lines (0%)
- `src/backup_recovery/recovery_manager.py` - 161 lines (0%)
- `src/backup_recovery/integrity_checker.py` - 121 lines (0%)

**测试策略**:
```python
# tests/unit/backup_recovery/test_backup_manager.py
class TestBackupManager:
    - test_create_backup()
    - test_incremental_backup()
    - test_backup_retention_policy()
    - test_compression()

# tests/unit/backup_recovery/test_recovery_manager.py
class TestRecoveryManager:
    - test_restore_from_backup()
    - test_point_in_time_recovery()
    - test_partial_recovery()
```

**预期效果**: 增加 ~400-500 行测试代码，覆盖率可提升 3-5%

---

## 📈 预期改进时间线

| 阶段 | 任务 | 预期耗时 | 预期覆盖提升 |
|------|------|---------|-----------|
| 1 | Adapter 模块测试 | 3-4h | +15-20% |
| 2 | 监控模块测试 | 1.5-2h | +8-12% |
| 3 | 数据访问层测试 | 1.5-2h | +10-15% |
| 4 | 备份恢复模块测试 | 0.5-1h | +3-5% |
| **总计** | **完整覆盖实现** | **6.5-9h** | **~36-52%** |

**预期最终覆盖率**: 7% + 36-52% = **43-59%** (第一阶段)

**注**: 达到80%目标可能需要额外的：
- Web后端API测试 (web/backend/app/) - 2-3小时
- 前端测试完善 - 1-2小时
- 集成测试 - 1-2小时

---

## 🛠️ 测试实现最佳实践

### 1. Mock 和 Fixture 设计

**使用 pytest fixtures** 管理依赖:
```python
# tests/conftest.py (全局配置)
@pytest.fixture
def mock_adapter():
    """Mock adapter fixture"""
    return MockAdapter()

@pytest.fixture
def db_session():
    """Database session fixture with rollback"""
    # Setup
    yield session
    # Cleanup: rollback all changes

@pytest.fixture
def monitoring_client():
    """Monitoring database client"""
    # Setup monitoring connection
    yield client
    # Cleanup: close connection
```

### 2. 参数化测试

```python
@pytest.mark.parametrize("symbol,expected", [
    ("000001", "平安银行"),
    ("600000", "浦发银行"),
    ("invalid", None),
])
def test_get_stock_info(adapter, symbol, expected):
    result = adapter.get_stock_info(symbol)
    assert result == expected
```

### 3. Mock 外部依赖

```python
@patch('src.adapters.akshare_adapter.requests.get')
def test_akshare_api_call(mock_get):
    mock_get.return_value.json.return_value = {
        "data": [...],
    }
    # Test implementation
```

---

## ✅ 测试质量检查清单

在提交新测试时确保：

- [ ] 所有测试都独立运行且通过
- [ ] 测试使用了 Mock 避免真实数据库访问
- [ ] 覆盖了正常路径和错误路径
- [ ] 包含边界条件测试
- [ ] 使用了清晰的测试命名 (test_[method]_[scenario])
- [ ] 有适当的 docstring 说明测试目的
- [ ] 不依赖于执行顺序
- [ ] 测试失败时提供有用的错误消息

---

## 🚀 立即行动步骤

### Step 1: 创建测试文件结构 (5分钟)
```bash
mkdir -p tests/unit/adapters
mkdir -p tests/unit/monitoring
mkdir -p tests/unit/backup_recovery
```

### Step 2: 从优先级1开始 (adapter模块)
```python
# tests/unit/adapters/test_akshare_adapter.py
# 实现基本的初始化和关键方法测试
```

### Step 3: 运行增量测试
```bash
# 运行新测试并检查覆盖率改进
pytest tests/unit/adapters/ --cov=src/adapters --cov-report=term-missing

# 比较之前的覆盖率
# 预期: akshare_adapter.py 从 0% → 40-50%
```

### Step 4: 使用覆盖率HTML报告追踪进度
```bash
# 生成HTML报告查看细节
pytest tests/unit/ --cov=src --cov-report=html

# 打开 htmlcov/index.html 查看进度
```

---

## 📝 测试模板

### Adapter 测试模板
```python
# tests/unit/adapters/test_{adapter_name}.py
import pytest
from unittest.mock import patch, MagicMock
from src.adapters.{adapter_name} import {AdapterClass}

class Test{AdapterClass}:
    @pytest.fixture
    def adapter(self):
        """创建adapter实例"""
        return {AdapterClass}()

    def test_initialization(self, adapter):
        """测试adapter初始化"""
        assert adapter is not None
        assert hasattr(adapter, 'key_method')

    @patch('src.adapters.{adapter_name}.external_api_call')
    def test_key_method(self, mock_api, adapter):
        """测试关键方法"""
        mock_api.return_value = {"data": "mock_data"}
        result = adapter.get_data("symbol")
        assert result is not None

    def test_error_handling(self, adapter):
        """测试错误处理"""
        with pytest.raises(ValueError):
            adapter.get_data("")  # Invalid input
```

### 监控模块测试模板
```python
# tests/unit/monitoring/test_{module_name}.py
import pytest
from datetime import datetime
from src.monitoring.{module_name} import {MonitoringClass}

class Test{MonitoringClass}:
    @pytest.fixture
    def monitor(self):
        """创建监控实例"""
        return {MonitoringClass}()

    def test_alert_generation(self, monitor):
        """测试告警生成"""
        alert = monitor.create_alert("high", "Test alert")
        assert alert.severity == "high"
        assert alert.timestamp is not None
```

---

## 🎯 成功指标

**第一阶段 (现在 - 3小时)**:
- [ ] Adapter 模块覆盖率达到 40-50%
- [ ] 新增 2000+ 行测试代码
- [ ] 所有新测试通过
- [ ] 总覆盖率提升至 15-20%

**第二阶段 (3-6小时)**:
- [ ] 监控模块覆盖率达到 60-70%
- [ ] 数据访问层覆盖率达到 80%+
- [ ] 总覆盖率达到 30-40%

**最终目标 (后续工作)**:
- [ ] 整体覆盖率达到 80%
- [ ] API 和服务模块覆盖率达到 70%+
- [ ] 建立 CI/CD 覆盖率检查 (最小80%)

---

## 📚 参考资源

- 📖 [代码质量标准](./CODE_QUALITY_STANDARDS.md)
- 📖 [Pytest 文档](https://docs.pytest.org/)
- 📖 [Mock 测试最佳实践](https://docs.python.org/3/library/unittest.mock.html)

---

**计划生成时间**: 2025-11-23 02:30 UTC
**计划作者**: Claude Code
**计划版本**: 1.0
