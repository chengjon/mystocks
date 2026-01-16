# Design: Improve Backend Code Quality

## Overview

本文档详细说明后端Python代码质量改进的技术设计，包括代码拆分策略、测试架构、以及质量保证流程。

**Change ID**: improve-backend-code-quality
**设计日期**: 2026-01-03
**设计师**: Main CLI + Backend Architecture Agents

---

## 1. 当前架构分析

### 1.1 代码组织现状

```
src/
├── data_access.py (1,357行) ❌ 超长
├── adapters/
│   ├── tdx_adapter.py (1,058行) ❌ 超长
│   ├── financial_adapter.py (1,078行) ❌ 超长
│   └── ... (其他适配器)
├── core/
│   ├── unified_manager.py (792行) ⚠️ 接近限制
│   └── ...
└── ... (其他模块)

tests/ (仅5个测试文件, 0.16%覆盖率) ❌ 严重不足
```

### 1.2 技术债务根因分析

| 问题 | 根本原因 | 影响 |
|------|----------|------|
| **超长文件** | 历史演进，未及时重构 | 可读性差，维护困难 |
| **测试不足** | 重功能开发，轻测试 | 质量保证薄弱 |
| **Ruff问题多** | 缺乏自动化质量检查 | 代码风格不统一 |
| **TODO过多** | 临时实现未清理 | 功能完整性存疑 |

### 1.3 质量指标现状

| 指标 | 当前值 | 目标值 | 差距 |
|------|--------|--------|------|
| **测试覆盖率** | 0.16% | 80% | -79.84% |
| **Ruff问题** | 1,540 | <100 | -1,440 |
| **超长文件** | 4 | 0 | -4 |
| **TODO注释** | 266 | <50 | -216 |
| **Pylint评级** | 9.32/10 | >9.5/10 | -0.18 |

---

## 2. 设计原则

### 2.1 核心原则

1. **渐进式改进**: 分阶段完成，避免大爆炸式重构
2. **测试驱动**: 先补充测试，再重构代码
3. **向后兼容**: 保持API稳定，避免破坏性变更
4. **质量门禁**: 每个阶段完成后通过质量检查

### 2.2 SOLID原则应用

- **Single Responsibility**: 一个类/模块一个职责
- **Open/Closed**: 对扩展开放，对修改关闭
- **Liskov Substitution**: 子类可替换父类
- **Interface Segregation**: 接口小而专注
- **Dependency Inversion**: 依赖抽象而非具体实现

---

## 3. 代码拆分设计

### 3.1 data_access.py拆分方案

#### 3.1.1 当前结构问题

```
src/data_access.py (1,357行)
├── TDengineDataAccess类 (~500行)
├── PostgreSQLDataAccess类 (~500行)
├── DatabaseConnectionManager类 (~200行)
└── 工具函数 (~157行)
```

**问题**:
- 单文件包含多个数据库实现，违反单一职责原则
- 难以定位和修改特定数据库的代码
- 测试困难，无法独立测试每个实现

#### 3.1.2 拆分后结构

```
src/data_access/
├── __init__.py (统一导出接口)
├── base.py (基础接口和抽象类, ~400行)
│   ├── IDatabaseAccess (抽象接口)
│   ├── DatabaseConnectionConfig (配置类)
│   └── 工具函数
├── tdengine.py (TDengine实现, ~500行)
│   ├── TDengineDataAccess (主类)
│   ├── TDengineConnectionManager
│   └── TDengine工具函数
└── postgresql.py (PostgreSQL实现, ~500行)
    ├── PostgreSQLDataAccess (主类)
    ├── PostgreSQLConnectionManager
    └── PostgreSQL工具函数
```

#### 3.1.3 导入兼容性

**保持向后兼容**:
```python
# 旧代码继续有效
from src.data_access import TDengineDataAccess, PostgreSQLDataAccess

# 新代码推荐使用
from src.data_access import TDengineDataAccess
from src.data_access import PostgreSQLDataAccess
```

**实现方式** (`src/data_access/__init__.py`):
```python
# 向后兼容导入
from .tdengine import TDengineDataAccess
from .postgresql import PostgreSQLDataAccess
from .base import DatabaseConnectionManager

__all__ = [
    'TDengineDataAccess',
    'PostgreSQLDataAccess',
    'DatabaseConnectionManager',
]
```

#### 3.1.4 测试策略

```python
# tests/data_access/test_base.py
def test_database_interface():
    """测试基础接口定义"""
    from src.data_access.base import IDatabaseAccess
    assert hasattr(IDatabaseAccess, 'connect')
    assert hasattr(IDatabaseAccess, 'query')

# tests/data_access/test_tdengine.py
def test_tdengine_access():
    """测试TDengine实现"""
    from src.data_access.tdengine import TDengineDataAccess
    # Mock TDengine连接
    # 测试查询、写入等操作

# tests/data_access/test_postgresql.py
def test_postgresql_access():
    """测试PostgreSQL实现"""
    from src.data_access.postgresql import PostgreSQLDataAccess
    # Mock PostgreSQL连接
    # 测试查询、写入等操作
```

---

### 3.2 tdx_adapter.py拆分方案

#### 3.2.1 当前结构问题

```
src/adapters/tdx_adapter.py (1,058行)
├── TdxDataSource类 (主类, ~400行)
├── 市场数据获取方法 (~300行)
├── K线数据获取方法 (~300行)
└── 工具函数 (~58行)
```

**问题**:
- 单个类承担过多职责 (市场数据 + K线数据 + 其他)
- 代码耦合严重，修改K线逻辑可能影响市场数据
- 难以独立测试各个功能模块

#### 3.2.2 拆分后结构

```
src/adapters/tdx/
├── __init__.py (统一导出)
├── base.py (基础类和配置, ~400行)
│   ├── TdxDataSource (基础类)
│   ├── TdxConnectionManager
│   └── 配置和工具函数
├── market.py (市场数据, ~300行)
│   ├── get_market_data()
│   ├── get_stock_list()
│   ├── get_index_data()
│   └── 其他市场数据方法
└── kline.py (K线数据, ~400行)
    ├── get_kline_data()
    ├── get_minute_data()
    ├── get_tick_data()
    └── 其他K线数据方法
```

#### 3.2.3 API设计

**主入口 (`base.py`)**:
```python
class TdxDataSource:
    """TDX数据源主入口"""

    def __init__(self):
        self.market_client = TdxMarketClient()
        self.kline_client = TdxKlineClient()

    # 委托给各个子模块
    def get_market_data(self, *args, **kwargs):
        return self.market_client.get_market_data(*args, **kwargs)

    def get_kline_data(self, *args, **kwargs):
        return self.kline_client.get_kline_data(*args, **kwargs)
```

**市场数据模块 (`market.py`)**:
```python
class TdxMarketClient:
    """TDX市场数据客户端"""

    def get_market_data(self, code, date):
        """获取市场数据"""
        pass

    def get_stock_list(self, market):
        """获取股票列表"""
        pass

    # ... 其他市场数据方法
```

**K线数据模块 (`kline.py`)**:
```python
class TdxKlineClient:
    """TDX K线数据客户端"""

    def get_kline_data(self, code, period, start_date, end_date):
        """获取K线数据"""
        pass

    def get_minute_data(self, code, date):
        """获取分钟数据"""
        pass

    # ... 其他K线数据方法
```

#### 3.2.4 测试策略

```python
# tests/adapters/tdx/test_base.py
def test_tdx_datasource_init():
    """测试TDX数据源初始化"""
    from src.adapters.tdx.base import TdxDataSource
    source = TdxDataSource()
    assert source.market_client is not None
    assert source.kline_client is not None

# tests/adapters/tdx/test_market.py
def test_tdx_market_data():
    """测试市场数据获取"""
    from src.adapters.tdx.market import TdxMarketClient
    client = TdxMarketClient()
    # Mock TDX连接
    # 测试市场数据获取

# tests/adapters/tdx/test_kline.py
def test_tdx_kline_data():
    """测试K线数据获取"""
    from src.adapters.tdx.kline import TdxKlineClient
    client = TdxKlineClient()
    # Mock TDX连接
    # 测试K线数据获取
```

---

### 3.3 financial_adapter.py拆分方案

#### 3.3.1 拆分后结构

```
src/adapters/financial/
├── __init__.py
├── base.py (基础类, ~400行)
│   ├── FinancialDataSource (基础类)
│   └── 配置和工具函数
├── report.py (财务报表, ~400行)
│   ├── get_balance_sheet()  # 资产负债表
│   ├── get_income_statement()  # 利润表
│   ├── get_cash_flow_statement()  # 现金流量表
│   └── 其他报表方法
└── indicator.py (财务指标, ~300行)
    ├── get_financial_indicators()  # 财务指标
    ├── get_ratios()  # 财务比率
    └── 其他指标方法
```

#### 3.3.2 API设计

类似TDX适配器，使用委托模式:

```python
class FinancialDataSource:
    """财务数据源主入口"""

    def __init__(self):
        self.report_client = FinancialReportClient()
        self.indicator_client = FinancialIndicatorClient()

    def get_balance_sheet(self, *args, **kwargs):
        return self.report_client.get_balance_sheet(*args, **kwargs)

    def get_financial_indicators(self, *args, **kwargs):
        return self.indicator_client.get_financial_indicators(*args, **kwargs)
```

---

### 3.4 unified_manager.py重构方案

#### 3.4.1 当前结构问题

```
src/core/unified_manager.py (792行)
├── MyStocksUnifiedManager类 (主要业务逻辑, ~600行)
├── AutomatedMaintenanceManager类 (维护逻辑, ~200行)
└── 工具函数 (~92行)
```

**问题**:
- 维护逻辑和业务逻辑混合
- 单个类职责过多

#### 3.4.2 重构后结构

```
src/core/
├── unified_manager.py (主要业务逻辑, ~600行)
│   └── MyStocksUnifiedManager类
└── maintenance_manager.py (维护逻辑, ~200行)
    └── AutomatedMaintenanceManager类
```

#### 3.4.3 依赖关系

```python
# unified_manager.py
class MyStocksUnifiedManager:
    """统一数据管理器 - 主要业务逻辑"""

    def __init__(self):
        self.maintenance_manager = AutomatedMaintenanceManager()
        # ... 其他初始化

    def save_data(self, data):
        """保存数据"""
        # 业务逻辑
        pass

    def load_data(self, query):
        """加载数据"""
        # 业务逻辑
        pass

# maintenance_manager.py
class AutomatedMaintenanceManager:
    """自动化维护管理器 - 维护逻辑"""

    def health_check(self):
        """健康检查"""
        pass

    def cleanup_expired_data(self):
        """清理过期数据"""
        pass

    def update_statistics(self):
        """更新统计信息"""
        pass
```

---

## 4. 测试架构设计

### 4.1 测试目录结构

```
tests/
├── unit/  (单元测试)
│   ├── data_access/
│   │   ├── test_base.py
│   │   ├── test_tdengine.py
│   │   └── test_postgresql.py
│   ├── adapters/
│   │   ├── test_akshare_adapter.py
│   │   ├── test_tdx/
│   │   │   ├── test_base.py
│   │   │   ├── test_market.py
│   │   │   └── test_kline.py
│   │   ├── test_financial/
│   │   │   ├── test_base.py
│   │   │   ├── test_report.py
│   │   │   └── test_indicator.py
│   │   └── test_other_adapters.py
│   └── core/
│       ├── test_classification.py
│       ├── test_storage_strategy.py
│       └── test_table_manager.py
├── integration/  (集成测试)
│   ├── test_database_integration.py
│   ├── test_adapter_integration.py
│   └── test_unified_manager_integration.py
└── e2e/  (端到端测试)
    ├── test_data_flow_e2e.py
    └── test_trading_workflow_e2e.py
```

### 4.2 测试覆盖率目标

| 模块 | 单元测试 | 集成测试 | 总计 |
|------|---------|---------|------|
| **data_access** | 60% | 10% | 70% |
| **adapters** | 50% | 10% | 60% |
| **core** | 60% | 10% | 70% |
| **其他模块** | 40% | 5% | 45% |
| **整体项目** | - | - | 80% |

### 4.3 Mock策略

#### 4.3.1 数据库Mock

```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_tdengine_connection():
    """Mock TDengine连接"""
    with patch('src.data_access.tdengine.taos_connect') as mock_connect:
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        yield mock_conn

def test_tdengine_query(mock_tdengine_connection):
    """测试TDengine查询"""
    from src.data_access.tdengine import TDengineDataAccess
    access = TDengineDataAccess()
    result = access.query("SELECT * FROM test_table")
    assert result is not None
```

#### 4.3.2 API Mock

```python
@pytest.fixture
def mock_akshare_api():
    """Mock Akshare API"""
    with patch('akshare.stock_zh_a_hist') as mock_api:
        mock_api.return_value = pd.DataFrame({
            'date': ['2023-01-01'],
            'close': [10.5]
        })
        yield mock_api

def test_akshare_adapter(mock_akshare_api):
    """测试Akshare适配器"""
    from src.adapters.akshare_adapter import AkshareDataSource
    adapter = AkshareDataSource()
    result = adapter.get_kline_data('000001', 'daily')
    assert len(result) > 0
```

### 4.4 测试配置

#### 4.4.1 pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-report=json
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow-running tests
```

#### 4.4.2 .coveragerc

```ini
[run]
source = src
omit =
    */tests/*
    */test_*.py
    */__pycache__/*
    */site-packages/*
    */migrations/*

[report]
precision = 2
show_missing = True
skip_covered = False

[html]
directory = htmlcov
```

---

## 5. 质量保证流程

### 5.1 阶段质量门禁

#### 阶段1: 快速修复

**验收标准**:
- [ ] Ruff问题 < 700
- [ ] 测试配置修复完成
- [ ] 所有现有测试通过

**质量检查命令**:
```bash
ruff check . --statistics
pytest tests/ -v
coverage report
```

#### 阶段2: 测试提升

**验收标准**:
- [ ] 测试覆盖率 ≥ 40%
- [ ] 所有新测试通过
- [ ] Code review通过

**质量检查命令**:
```bash
coverage run -m pytest
coverage report
coverage html  # 查看详细报告
```

#### 阶段3: 结构优化

**验收标准**:
- [ ] 无文件 > 1000行
- [ ] 所有测试通过
- [ ] 导入无错误
- [ ] 性能无退化

**质量检查命令**:
```bash
find src -name "*.py" -exec wc -l {} + | sort -rn | head -20
pytest tests/ -v
python -c "from src.data_access import TDengineDataAccess"
python -c "from src.adapters.tdx import TdxDataSource"
```

#### 阶段4: 深度改进

**验收标准**:
- [ ] Ruff问题 < 100
- [ ] TODO < 50
- [ ] 测试覆盖率 ≥ 80%
- [ ] Manager类 < 30 (可选)

**质量检查命令**:
```bash
ruff check . --statistics
grep -r "TODO\|FIXME" src/ | wc -l
coverage run -m pytest
coverage report
```

### 5.2 CI/CD集成

#### 5.2.1 Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.10
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest tests/ -v
        language: system
        pass_filenames: false

      - id: coverage
        name: coverage
        entry: coverage report --fail-under=40
        language: system
        pass_filenames: false
```

#### 5.2.2 GitHub Actions Workflow

```yaml
# .github/workflows/code-quality.yml
name: Code Quality

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install ruff pytest coverage

      - name: Run Ruff
        run: ruff check .

      - name: Run tests
        run: pytest tests/ -v

      - name: Check coverage
        run: |
          coverage run -m pytest
          coverage report --fail-under=40
```

---

## 6. 风险分析与缓解

### 6.1 技术风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| **拆分文件导致导入错误** | 中 | 高 | 1. 充分测试<br>2. 使用__init__.py保持向后兼容<br>3. 逐步迁移导入 |
| **测试编写工作量超预期** | 高 | 中 | 1. 分阶段完成<br>2. 优先核心模块<br>3. 使用测试生成工具辅助 |
| **Ruff自动修复改变逻辑** | 低 | 中 | 1. 仔细审查git diff<br>2. 逐文件验证<br>3. 运行完整测试套件 |
| **性能退化** | 低 | 高 | 1. 性能基准测试<br>2. 拆分前后对比<br>3. 优化关键路径 |

### 6.2 流程风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| **阶段延期** | 中 | 中 | 1. 预留buffer时间<br>2. 可选任务延后<br>3. 调整优先级 |
| **资源不足** | 低 | 高 | 1. 分阶段执行<br>2. 使用Agent自动化<br>3. 外部协助(可选) |
| **质量门禁失败** | 中 | 中 | 1. 提前验证<br>2. 预留修复时间<br>3. 回滚计划 |

---

## 7. 成功指标

### 7.1 定量指标

| 指标 | 当前值 | 目标值 | 测量方法 |
|------|--------|--------|----------|
| **测试覆盖率** | 0.16% | 80% | coverage.py |
| **Ruff问题数** | 1,540 | <100 | ruff check |
| **超长文件数** | 4 | 0 | find + wc -l |
| **TODO注释数** | 266 | <50 | grep TODO/FIXME |
| **平均文件行数** | ~500 | <300 | 统计分析 |
| **测试通过率** | - | >95% | pytest |

### 7.2 定性指标

- [ ] 代码可读性显著提升
- [ ] 模块职责清晰
- [ ] 测试覆盖核心功能
- [ ] 代码风格统一
- [ ] 文档完善

---

## 8. 实施时间表

### 8.1 阶段时间线

```
Week 1:  阶段1 - 快速修复
  ├─ Day 1-2:  Ruff自动修复
  ├─ Day 3:    调查测试问题
  └─ Day 4-5:  修复测试配置

Week 2-4:  阶段2 - 测试提升
  ├─ Week 2:   data_access层测试
  ├─ Week 3:   adapters层测试
  └─ Week 4:   core层测试 + 验证

Week 5-8:  阶段3 - 结构优化
  ├─ Week 5:   拆分data_access.py
  ├─ Week 6:   拆分tdx_adapter.py
  ├─ Week 7:   拆分financial_adapter.py
  └─ Week 8:   重构unified_manager.py + 验证

Week 9-16:  阶段4 - 深度改进
  ├─ Week 9-11:   手动修复Ruff问题
  ├─ Week 12-13:  清理TODO注释
  ├─ Week 14-15:  继续提升测试覆盖率
  └─ Week 16:     最终验收 + 报告
```

### 8.2 里程碑

| 里程碑 | 日期 | 交付物 |
|--------|------|--------|
| **M1: 快速修复完成** | Week 1 | Ruff问题<700, 测试配置修复 |
| **M2: 测试提升完成** | Week 4 | 测试覆盖率≥40% |
| **M3: 结构优化完成** | Week 8 | 无超长文件 |
| **M4: 深度改进完成** | Week 16 | 测试覆盖率≥80%, Ruff<100 |

---

## 9. 附录

### 9.1 相关文档

- 技术负债报告: `docs/reports/TECHNICAL_DEBT_STATUS_2026-01-03.md`
- 提案文档: `openspec/changes/improve-backend-code-quality/proposal.md`
- 任务列表: `openspec/changes/improve-backend-code-quality/tasks.md`

### 9.2 工具和资源

**代码质量工具**:
- Ruff: https://docs.astral.sh/ruff/
- Pylint: https://pylint.org/
- Black: https://black.readthedocs.io/

**测试工具**:
- pytest: https://docs.pytest.org/
- coverage.py: https://coverage.readthedocs.io/

**相关指南**:
- Python测试最佳实践: https://docs.python-guide.org/writing/tests/
- SOLID原则: https://en.wikipedia.org/wiki/SOLID

---

**设计文档版本**: v1.0
**最后更新**: 2026-01-03
**设计师**: Main CLI + Backend Architecture Agents
