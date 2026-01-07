# MyStocks 测试覆盖率改进计划

**日期**: 2026-01-03
**当前覆盖率**: 31.9% (101/317 模块)
**目标覆盖率**: 80%+ (254/317 模块)
**差距**: 需要补充 153 个模块的测试

---

## 📊 执行摘要

### 关键发现

1. **模块总数**: 317个源代码模块
2. **已测试模块**: 101个 (31.9%)
3. **未测试模块**: 216个 (68.1%)
4. **测试文件数**: 243个

### 按模块类型覆盖率

| 模块类型 | 总数 | 已测试 | 覆盖率 | 优先级 |
|---------|------|--------|--------|--------|
| **core** | 29 | 20 | **69.0%** | 🔴 高 |
| **data_access** | 9 | 7 | **77.8%** | 🟡 中 |
| **adapters** | 36 | 16 | **44.4%** | 🔴 高 |
| **monitoring** | 28 | 10 | **35.7%** | 🟢 低 |
| **gpu** | 55 | 7 | **12.7%** | 🟢 低 |
| **utils** | 20 | 14 | **70.0%** | 🟢 低 |
| **mock** | 27 | 1 | **3.7%** | 🟢 低 |
| **storage** | 30 | 6 | **20.0%** | 🟡 中 |

### Top 20 优先改进模块

| 优先级 | 模块路径 | 行数 | 测试 | 理由 |
|-------|---------|------|------|------|
| 1. (90) | `adapters/tdx/tdx_adapter.py` | 982 | ✗ | 大型适配器，核心功能 |
| 2. (80) | `core/database_metrics.py` | 318 | ✗ | 核心监控功能 |
| 3. (80) | `core/logging/structured.py` | 203 | ✗ | 核心日志系统 |
| 4. (75) | `data_access/interfaces.py` | 263 | ✗ | 数据访问接口 |
| 5. (75) | `data_access/routers/query_router.py` | 433 | ✗ | 查询路由逻辑 |
| 6. (70) | `monitoring/multi_channel_alert_manager.py` | 752 | ✗ | 告警管理器 |
| 7. (70) | `monitoring/intelligent_threshold_manager.py` | 862 | ✗ | 智能阈值管理 |
| 8. (70) | `monitoring/alert_notifier.py` | 577 | ✗ | 告警通知器 |
| 9. (70) | `monitoring/ai_alert_manager.py` | 634 | ✗ | AI告警管理 |
| 10. (70) | `monitoring/ai_realtime_monitor.py` | 574 | ✗ | AI实时监控 |

---

## 🎯 四阶段改进计划

### Phase 1: 修复测试基础设施 (1-2天)

**目标**: 确保测试可以正常运行

#### 任务清单
- [ ] 修复所有测试导入错误 (`src`模块导入)
  - 配置正确的 `PYTHONPATH`
  - 更新测试文件导入路径
  - 验证 `pytest.ini` 配置

- [ ] 配置测试覆盖率工具
  - 验证 `pytest-cov` 正常工作
  - 配置 `.coveragerc` 文件
  - 设置覆盖率目标为80%

- [ ] 运行完整测试套件验证
  - 修复所有阻止测试运行的错误
  - 确保至少有70%的现有测试可以运行
  - 生成覆盖率基线报告

**预期产出**:
- 所有测试文件可以正常导入和运行
- 生成的覆盖率报告准确反映代码覆盖情况
- 测试基础设施文档更新

#### 详细步骤

**1.1 修复PYTHONPATH配置**

在 `pytest.ini` 中添加:
```ini
[pytest]
pythonpath = .
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

**1.2 批量修复测试导入**

创建脚本 `scripts/quality_gate/fix_test_imports.py`:
```python
import os
from pathlib import Path

tests_dir = Path("tests")
for test_file in tests_dir.rglob("test_*.py"):
    content = test_file.read_text()
    # 将 from core.xxx 改为 from src.core.xxx
    content = content.replace("from core.", "from src.core.")
    content = content.replace("from adapters.", "from src.adapters.")
    content = content.replace("from db_manager.", "from src.db_manager.")
    # 保存
    test_file.write_text(content)
```

**1.3 验证测试运行**

```bash
# 快速验证
PYTHONPATH=. pytest tests/ --collect-only -q | head -20

# 运行一小部分测试验证
PYTHONPATH=. pytest tests/adapters/test_akshare_adapter.py -v
```

---

### Phase 2: 核心模块测试覆盖 (3-5天)

**目标**: 提升核心模块覆盖率到90%+

#### 2.1 data_access层 (PostgreSQL 67% → 90%+)

**待补充测试用例**:
- [ ] `postgresql_access.py` - 连接管理、查询优化
  - 连接池管理测试
  - 事务处理测试
  - 错误处理和重试机制

- [ ] `tdengine_access.py` - 时序数据访问
  - WebSocket连接测试
  - 批量写入性能测试
  - 数据压缩验证

- [ ] `interfaces.py` - 数据访问接口
  - 接口契约测试
  - 抽象方法实现验证

**优先级**: 🔴 高 (数据访问是系统核心)

#### 2.2 core层核心模块

**待补充测试用例**:
- [ ] `data_manager.py` - 数据管理器
  - 数据路由逻辑测试
  - 缓存机制测试
  - 并发访问测试

- [ ] `unified_manager.py` - 统一管理器
  - 端到端数据流测试
  - 数据完整性测试
  - 错误恢复测试

- [ ] `database_metrics.py` - 数据库指标
  - 指标收集测试
  - 性能监控测试
  - 告警触发测试

**优先级**: 🔴 高 (核心业务逻辑)

---

### Phase 3: 大型模块TDD (5-7天)

**目标**: 为大型复杂模块推广TDD实践

#### 3.1 tdx_adapter.py (982行)

**当前状态**: ✗ 无测试
**目标**: 80%+ 覆盖率

**测试策略**:
1. **接口测试** - 验证 `IDataSource` 接口实现
2. **功能测试** - 测试各个数据获取方法
   - `get_daily_data()` - 日线数据
   - `get_realtime_data()` - 实时行情
   - `get_minute_data()` - 分钟K线
3. **错误处理测试** - 网络错误、数据错误
4. **性能测试** - 批量数据获取性能
5. **Mock外部依赖** - TDX服务器连接

**测试文件结构**:
```
tests/adapters/test_tdx_adapter/
├── __init__.py
├── conftest.py                 # 共享fixtures
├── test_daily_data.py          # 日线数据测试
├── test_realtime_data.py       # 实时数据测试
├── test_minute_data.py         # 分钟数据测试
├── test_error_handling.py      # 错误处理测试
├── test_performance.py         # 性能测试
└── mocks/
    ├── __init__.py
    └── mock_tdx_connection.py  # TDX连接Mock
```

#### 3.2 database_service.py (1,454行)

**当前状态**: ✗ 无测试
**目标**: 80%+ 覆盖率

**测试策略**:
1. **单元测试** - 各个服务方法
2. **集成测试** - 数据库交互
3. **事务测试** - 事务回滚和提交
4. **性能测试** - 查询性能
5. **并发测试** - 多线程安全

**测试文件结构**:
```
tests/database/test_database_service/
├── __init__.py
├── conftest.py
├── test_connection_management.py
├── test_query_execution.py
├── test_transaction_handling.py
├── test_performance.py
└── test_concurrency.py
```

---

### Phase 4: 适配器层完善 (3-4天)

**目标**: 所有7个适配器100%测试覆盖

#### 适配器测试清单

- [ ] **AkshareDataSource** - 补充边界测试
  - [ ] 测试所有参数组合
  - [ ] 测试错误响应处理
  - [ ] 测试数据格式验证

- [ ] **BaostockDataSource** - 补充完整测试
  - [ ] 连接认证测试
  - [ ] 数据获取测试
  - [ ] 重试机制测试

- [ ] **TdxDataSource** - 完整测试套件 (参见Phase 3)

- [ ] **ByapiDataSource** - 基础测试补充
  - [ ] API调用测试
  - [ ] 响应解析测试

- [ ] **CustomerDataSource** - 完整测试
  - [ ] 客户数据管理测试
  - [ ] 数据验证测试

- [ ] **FinancialDataSource** - 财务数据测试
  - [ ] 财报数据获取
  - [ ] 数据完整性验证

- [ ] **TushareDataSource** - 专业数据源测试
  - [ ] API限流处理
  - [ ] 数据格式转换

---

## 🛠️ 测试基础设施

### 配置文件

#### `.coveragerc` (覆盖率配置)
```ini
[run]
source = src
omit =
    */tests/*
    */test_*.py
    */__pycache__/*
    */site-packages/*
    */dist-packages/*

[report]
precision = 2
show_missing = True
skip_covered = False

[html]
directory = htmlcov
```

#### `pytest.ini` (Pytest配置)
```ini
[pytest]
pythonpath = .
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --tb=short
    --strict-markers
    --cov=src
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=json:coverage.json
    --cov-fail-under=80

markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    network: Tests requiring network access
```

### 测试目录结构

```
tests/
├── adapters/              # 适配器测试
├── core/                  # 核心模块测试
├── data_access/           # 数据访问测试
├── monitoring/            # 监控模块测试
├── gpu/                   # GPU模块测试
├── utils/                 # 工具函数测试
├── integration/           # 集成测试
├── e2e/                   # 端到端测试
├── conftest.py            # 共享fixtures
└── __init__.py
```

### 共享Fixtures (`tests/conftest.py`)

```python
import pytest
import os
from pathlib import Path

# 项目根目录
@pytest.fixture
def project_root():
    return Path(__file__).parent.parent

# 测试数据目录
@pytest.fixture
def test_data_dir(project_root):
    return project_root / "tests" / "fixtures"

# Mock数据库连接
@pytest.fixture
def mock_postgresql_connection(monkeypatch):
    """Mock PostgreSQL连接"""
    from unittest.mock import MagicMock
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = MagicMock()
    monkeypatch.setenv("POSTGRESQL_HOST", "localhost")
    monkeypatch.setenv("POSTGRESQL_PORT", "5432")
    monkeypatch.setenv("POSTGRESQL_USER", "test_user")
    monkeypatch.setenv("POSTGRESQL_PASSWORD", "test_pass")
    monkeypatch.setenv("POSTGRESQL_DATABASE", "test_db")
    return mock_conn

# Mock TDengine连接
@pytest.fixture
def mock_tdengine_connection(monkeypatch):
    """Mock TDengine连接"""
    from unittest.mock import MagicMock
    mock_conn = MagicMock()
    monkeypatch.setenv("TDENGINE_HOST", "localhost")
    monkeypatch.setenv("TDENGINE_PORT", "6041")
    monkeypatch.setenv("TDENGINE_USER", "test_user")
    monkeypatch.setenv("TDENGINE_PASSWORD", "test_pass")
    monkeypatch.setenv("TDENGINE_DATABASE", "test_db")
    return mock_conn

# 测试配置
@pytest.fixture
def test_config(monkeypatch, tmp_path):
    """提供测试配置"""
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-for-testing-only")
    monkeypatch.setenv("TESTING", "true")
    return {
        "data_dir": tmp_path / "data",
        "log_level": "DEBUG",
    }
```

---

## 📈 进度跟踪

### 里程碑

| 里程碑 | 目标 | 截止日期 | 状态 |
|--------|------|----------|------|
| M1: 测试基础设施修复 | 所有测试可运行 | Day 2 | ⏳ 待开始 |
| M2: data_access层 | 90%+ 覆盖率 | Day 7 | ⏳ 待开始 |
| M3: core层 | 80%+ 覆盖率 | Day 12 | ⏳ 待开始 |
| M4: 大型模块TDD | tdx_adapter 80%+ | Day 19 | ⏳ 待开始 |
| M5: 适配器层 | 100% 适配器覆盖 | Day 23 | ⏳ 待开始 |
| **最终目标** | **整体80%+** | **Day 23** | ⏳ 待开始 |

### 每日报告模板

```markdown
## 日期: YYYY-MM-DD

### 今日完成
- [x] 任务1
- [x] 任务2

### 遇到的问题
- 问题描述
- 解决方案

### 明日计划
- [ ] 任务1
- [ ] 任务2

### 覆盖率更新
- 当前覆盖率: X.X%
- 新增测试数: N
- 修复Bug数: M
```

---

## 🎓 TDD最佳实践

### 测试命名规范

```python
def test_<功能>_<条件>_<期望结果>()

# 示例:
def test_get_daily_data_with_valid_symbol_returns_dataframe():
    """测试: 使用有效代码获取日线数据应返回DataFrame"""
    pass

def test_get_daily_data_with_invalid_symbol_raises_exception():
    """测试: 使用无效代码应抛出异常"""
    pass
```

### AAA模式 (Arrange-Act-Assert)

```python
def test_user_authentication_with_valid_credentials_succeeds():
    # Arrange (准备)
    username = "testuser"
    password = "testpass"
    auth_service = AuthService()

    # Act (执行)
    result = auth_service.authenticate(username, password)

    # Assert (断言)
    assert result.is_success == True
    assert result.user.username == username
```

### 测试隔离

```python
import pytest

@pytest.fixture(autouse=True)
def isolate_test(test_databases):
    """每个测试前清理数据库"""
    test_databases.clean()
    yield
    test_databases.clean()

def test_something_in_isolation():
    # 这个测试不会受到其他测试影响
    pass
```

---

## 🔧 工具和脚本

### 覆盖率分析脚本
```bash
# 生成详细覆盖率报告
python scripts/quality_gate/analyze_coverage.py

# 查看覆盖率HTML报告
open htmlcov/index.html
```

### 测试生成辅助脚本
```bash
# 为模块生成测试模板
python scripts/quality_gate/generate_test_template.py <module_path>

# 示例:
python scripts/quality_gate/generate_test_template.py src/adapters/tdx/tdx_adapter.py
```

---

## 📚 参考资料

### 内部文档
- [测试覆盖率分析报告](test_coverage_analysis.json)
- [Python质量保证工作流](../guides/PYTHON_QUALITY_ASSURANCE_WORKFLOW.md)
- [TDD实践指南](../guides/TDD_BEST_PRACTICES.md)

### 外部资源
- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)

---

## ✅ 检查清单

在完成每个Phase后，验证以下内容：

### Phase 1 完成标准
- [ ] 所有测试文件可以正常导入
- [ ] `pytest tests/` 可以运行
- [ ] 覆盖率报告生成正常
- [ ] 测试导入路径全部更新

### Phase 2 完成标准
- [ ] data_access层覆盖率达到90%+
- [ ] core层覆盖率达到80%+
- [ ] 所有核心模块都有测试
- [ ] 测试文档完整

### Phase 3 完成标准
- [ ] tdx_adapter.py覆盖率达到80%+
- [ ] database_service.py覆盖率达到80%+
- [ ] 所有大型模块都有完整测试套件

### Phase 4 完成标准
- [ ] 所有7个适配器100%覆盖
- [ ] 适配器测试文档完整
- [ ] 适配器集成测试通过

### 最终完成标准
- [ ] 整体覆盖率达到80%+
- [ ] 所有测试通过
- [ ] 测试文档完整
- [ ] CI/CD集成测试自动化

---

**报告生成时间**: 2026-01-03
**下次更新**: Phase 1 完成后
**负责人**: Main CLI (Claude Code)
