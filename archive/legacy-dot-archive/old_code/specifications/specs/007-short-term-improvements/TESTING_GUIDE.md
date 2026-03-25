# MyStocks 单元测试指南

## 📋 目录

1. [测试环境设置](#测试环境设置)
2. [运行测试](#运行测试)
3. [覆盖率报告](#覆盖率报告)
4. [编写新测试](#编写新测试)
5. [测试最佳实践](#测试最佳实践)
6. [常见问题](#常见问题)

---

## 测试环境设置

### 1. 安装测试依赖

```bash
# 安装pytest和相关插件
pip install pytest pytest-cov pytest-mock pytest-asyncio

# 或从requirements-test.txt安装（如果存在）
pip install -r requirements-test.txt
```

### 2. 验证安装

```bash
# 检查pytest版本
pytest --version

# 输出示例：
# pytest 7.4.3
```

### 3. 测试配置

项目根目录的 `pytest.ini` 包含所有测试配置：

```ini
[pytest]
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

testpaths =
    tests
    adapters
    db_manager
    utils

addopts =
    -v
    --strict-markers
    --cov=adapters
    --cov=db_manager
    --cov=utils
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=70

markers =
    integration: marks tests as integration tests (deselect with '-m "not integration"')
    slow: marks tests as slow (deselect with '-m "not slow"')
```

---

## 运行测试

### 基本命令

#### 1. 运行所有测试

```bash
pytest
```

**输出示例：**
```
========================= test session starts =========================
platform linux -- Python 3.12.0, pytest-7.4.3
rootdir: /opt/claude/mystocks_spec
configfile: pytest.ini
plugins: cov-4.1.0, mock-3.12.0, asyncio-0.21.0
collected 45 items

tests/test_akshare_adapter.py ................          [ 35%]
tests/test_tdx_adapter.py .............                 [ 64%]
tests/test_database_manager.py ..........               [ 86%]
tests/test_check_db_health.py ......                    [100%]

========================= 45 passed in 2.34s ==========================
```

#### 2. 运行特定测试文件

```bash
# 测试单个文件
pytest tests/test_akshare_adapter.py

# 测试多个文件
pytest tests/test_akshare_adapter.py tests/test_tdx_adapter.py
```

#### 3. 运行特定测试类或方法

```bash
# 运行特定测试类
pytest tests/test_akshare_adapter.py::TestAkshareAdapter

# 运行特定测试方法
pytest tests/test_akshare_adapter.py::TestAkshareAdapter::test_get_stock_daily_success

# 使用-k匹配测试名称
pytest -k "akshare"  # 运行所有名称包含akshare的测试
pytest -k "success"  # 运行所有名称包含success的测试
```

#### 4. 详细输出模式

```bash
# 显示详细信息
pytest -v

# 显示测试输出（print语句）
pytest -s

# 组合使用
pytest -vs
```

### 高级命令

#### 1. 跳过集成测试（仅运行单元测试）

```bash
# 排除integration标记的测试
pytest -m "not integration"

# 排除slow测试
pytest -m "not slow"

# 排除多个标记
pytest -m "not integration and not slow"
```

#### 2. 只运行集成测试

```bash
pytest -m integration
```

#### 3. 失败时立即停止

```bash
# 第一个失败后停止
pytest -x

# 3个失败后停止
pytest --maxfail=3
```

#### 4. 重新运行失败的测试

```bash
# 第一次运行
pytest

# 只重新运行上次失败的测试
pytest --lf

# 先运行失败的，再运行成功的
pytest --ff
```

#### 5. 并行运行测试（需要pytest-xdist）

```bash
# 安装插件
pip install pytest-xdist

# 使用4个CPU核心
pytest -n 4

# 自动检测CPU数量
pytest -n auto
```

---

## 覆盖率报告

### 1. 生成覆盖率报告

```bash
# 运行测试并生成覆盖率
pytest --cov

# 指定要测试的模块
pytest --cov=adapters --cov=db_manager

# 生成HTML报告
pytest --cov --cov-report=html

# 生成多种格式
pytest --cov --cov-report=html --cov-report=term --cov-report=xml
```

### 2. 查看覆盖率报告

#### 终端报告

运行 `pytest --cov` 后，终端会显示：

```
----------- coverage: platform linux, python 3.12.0-final-0 -----------
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
adapters/__init__.py                  5      0   100%
adapters/akshare_adapter.py         145     15    90%   78-82, 156-162
adapters/tdx_adapter.py             178     25    86%   45-48, 89-95, 201-210
db_manager/database_manager.py      234     45    81%   67-72, 145-156, 289-302
utils/check_db_health.py            125     18    86%   45-48, 112-118
---------------------------------------------------------------
TOTAL                               687     103   85%
```

**字段说明：**
- **Stmts**: 代码总行数
- **Miss**: 未覆盖的行数
- **Cover**: 覆盖率百分比
- **Missing**: 未覆盖的具体行号

#### HTML报告

```bash
# 生成HTML报告
pytest --cov --cov-report=html

# 在浏览器中打开
# Linux/Mac
open htmlcov/index.html

# Windows
start htmlcov/index.html
```

HTML报告提供：
- 整体覆盖率统计
- 每个文件的详细覆盖情况
- 高亮显示未覆盖的代码行
- 分支覆盖分析

### 3. 覆盖率目标

项目配置要求最低覆盖率 **70%**：

```ini
--cov-fail-under=70
```

如果覆盖率低于70%，pytest会返回失败状态。

**当前覆盖率目标：**
- ✅ **adapters**: 目标 85%+
- ✅ **db_manager**: 目标 80%+
- ✅ **utils**: 目标 80%+
- 🎯 **整体**: 目标 75%+

---

## 编写新测试

### 1. 测试文件结构

```python
"""
测试模块的简短描述
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
sys.path.insert(0, '/opt/claude/mystocks_spec')

# 导入要测试的模块
from adapters.your_adapter import YourAdapter


class TestYourAdapter:
    """YourAdapter测试类"""

    def setup_method(self):
        """每个测试方法执行前调用"""
        self.adapter = YourAdapter()

    def teardown_method(self):
        """每个测试方法执行后调用"""
        # 清理资源
        pass

    def test_basic_functionality(self):
        """测试基本功能"""
        # Arrange (准备)
        expected_result = "expected"

        # Act (执行)
        result = self.adapter.some_method()

        # Assert (断言)
        assert result == expected_result

    @patch('adapters.your_adapter.external_dependency')
    def test_with_mock(self, mock_dependency):
        """测试使用Mock"""
        # 配置Mock行为
        mock_dependency.return_value = "mocked_value"

        # 执行测试
        result = self.adapter.method_using_dependency()

        # 验证
        assert result == "mocked_value"
        mock_dependency.assert_called_once()

    @pytest.mark.integration
    @pytest.mark.slow
    def test_integration(self):
        """集成测试（需要真实连接）"""
        try:
            result = self.adapter.real_connection_test()
            assert result is not None
        except Exception as e:
            pytest.skip(f"Integration test failed: {str(e)}")
```

### 2. 使用Fixtures

#### 使用共享fixtures (conftest.py)

```python
def test_with_fixture(self, sample_stock_data):
    """使用共享fixture"""
    # sample_stock_data 来自 conftest.py
    assert len(sample_stock_data) == 10
    assert 'close' in sample_stock_data.columns
```

#### 创建自定义fixture

```python
@pytest.fixture
def custom_adapter():
    """创建自定义适配器fixture"""
    adapter = YourAdapter(config={'key': 'value'})
    yield adapter
    # 清理代码
    adapter.close()

def test_with_custom_fixture(self, custom_adapter):
    """使用自定义fixture"""
    result = custom_adapter.get_data()
    assert result is not None
```

### 3. Mock最佳实践

#### Mock外部API调用

```python
@patch('adapters.akshare_adapter.ak.stock_zh_a_hist')
def test_api_call(self, mock_api):
    """Mock外部API"""
    # 配置Mock返回值
    mock_api.return_value = pd.DataFrame({
        'date': ['2024-01-01'],
        'close': [10.0]
    })

    # 测试
    result = self.adapter.get_stock_daily("000001")

    # 验证调用
    assert result is not None
    mock_api.assert_called_once_with(
        symbol="000001",
        start_date=ANY,
        end_date=ANY
    )
```

#### Mock异常情况

```python
@patch('adapters.akshare_adapter.ak.stock_zh_a_hist')
def test_api_exception(self, mock_api):
    """测试异常处理"""
    # Mock抛出异常
    mock_api.side_effect = Exception("API Error")

    # 测试应该优雅处理异常
    result = self.adapter.get_stock_daily("000001")

    # 验证错误处理
    assert result is None or result.empty
```

#### Mock数据库连接

```python
@patch('db_manager.database_manager.pymysql.connect')
def test_database_operation(self, mock_connect):
    """Mock数据库操作"""
    # 创建Mock连接和cursor
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [('test',)]

    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    # 测试
    result = self.manager.query_data()

    # 验证
    assert result is not None
    mock_cursor.execute.assert_called()
```

### 4. 参数化测试

```python
@pytest.mark.parametrize("symbol,expected_market", [
    ("000001", 0),  # 深圳
    ("600519", 1),  # 上海
    ("300001", 0),  # 创业板
    ("688001", 1),  # 科创板
])
def test_market_detection(self, symbol, expected_market):
    """测试市场检测（参数化）"""
    result = self.adapter.detect_market(symbol)
    assert result == expected_market
```

### 5. 异步测试

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_function():
    """测试异步函数"""
    result = await async_function()
    assert result is not None
```

---

## 测试最佳实践

### 1. AAA模式

每个测试应该遵循 **Arrange-Act-Assert** 模式：

```python
def test_example(self):
    # Arrange: 准备测试数据和环境
    symbol = "000001"
    expected_columns = ['date', 'close']

    # Act: 执行被测试的操作
    result = self.adapter.get_stock_daily(symbol)

    # Assert: 验证结果
    assert result is not None
    assert list(result.columns) == expected_columns
```

### 2. 测试命名规范

- ✅ 好的命名：`test_get_stock_daily_returns_dataframe_when_valid_symbol()`
- ✅ 好的命名：`test_connection_raises_exception_when_invalid_host()`
- ❌ 差的命名：`test_function1()`
- ❌ 差的命名：`test_works()`

**命名模式：** `test_<method>_<condition>_<expected_result>`

### 3. 一个测试一个断言原则

尽量每个测试只验证一个行为：

```python
# ✅ 好的做法
def test_get_stock_daily_returns_dataframe(self):
    result = self.adapter.get_stock_daily("000001")
    assert isinstance(result, pd.DataFrame)

def test_get_stock_daily_contains_required_columns(self):
    result = self.adapter.get_stock_daily("000001")
    assert 'date' in result.columns
    assert 'close' in result.columns

# ❌ 避免这样（除非断言高度相关）
def test_get_stock_daily(self):
    result = self.adapter.get_stock_daily("000001")
    assert isinstance(result, pd.DataFrame)
    assert 'date' in result.columns
    assert len(result) > 0
    assert result['close'].dtype == float
```

### 4. 测试独立性

每个测试应该能够独立运行，不依赖其他测试：

```python
# ✅ 好的做法 - 使用setup_method
class TestAdapter:
    def setup_method(self):
        self.adapter = Adapter()  # 每个测试都有新实例

    def test_method_a(self):
        self.adapter.method_a()
        assert True

    def test_method_b(self):
        self.adapter.method_b()  # 不受method_a影响
        assert True
```

### 5. 避免测试实现细节

测试应该关注行为，而不是实现：

```python
# ✅ 好的做法 - 测试行为
def test_get_stock_daily_returns_valid_data(self):
    result = self.adapter.get_stock_daily("000001")
    assert result is not None
    assert len(result) > 0

# ❌ 避免 - 测试实现细节
def test_get_stock_daily_uses_specific_library(self):
    # 不要测试内部使用了什么库
    assert self.adapter._library == "akshare"
```

### 6. 测试边界条件

确保测试覆盖边界情况：

```python
@pytest.mark.parametrize("count", [0, 1, 100, 1000, 10000])
def test_get_kline_with_various_counts(self, count):
    """测试各种数量参数"""
    result = self.adapter.get_kline_data("000001", count=count)
    # 验证结果
```

### 7. 使用明确的断言消息

```python
# ✅ 好的做法
assert len(result) > 0, f"Expected non-empty result, got {len(result)} rows"

# ❌ 不够清晰
assert len(result) > 0
```

---

## 常见问题

### Q1: 测试运行时找不到模块

**问题：**
```
ModuleNotFoundError: No module named 'adapters'
```

**解决方案：**
```python
# 在测试文件开头添加
import sys
sys.path.insert(0, '/opt/claude/mystocks_spec')
```

### Q2: Mock不生效

**问题：** Mock了函数但实际还是调用了真实函数

**解决方案：** 确保Mock路径正确

```python
# ❌ 错误 - Mock了导入路径
@patch('akshare.stock_zh_a_hist')

# ✅ 正确 - Mock了实际使用路径
@patch('adapters.akshare_adapter.ak.stock_zh_a_hist')
```

### Q3: 集成测试失败导致整体失败

**问题：** 没有数据库连接时集成测试失败

**解决方案：** 使用pytest.skip或排除集成测试

```python
# 方式1: 在测试中skip
@pytest.mark.integration
def test_real_connection(self):
    try:
        result = self.adapter.connect()
        assert result is not None
    except Exception as e:
        pytest.skip(f"Connection failed: {str(e)}")

# 方式2: 运行时排除
pytest -m "not integration"
```

### Q4: 覆盖率报告不准确

**问题：** 覆盖率显示为0%或异常低

**解决方案：**
1. 确保 pytest.ini 中配置了正确的模块路径
2. 检查是否有 `.coveragerc` 冲突
3. 清除旧的覆盖率数据：
```bash
rm -rf .coverage htmlcov/
pytest --cov
```

### Q5: 异步测试报错

**问题：**
```
RuntimeError: no running event loop
```

**解决方案：**
```bash
# 安装pytest-asyncio
pip install pytest-asyncio

# 使用装饰器
@pytest.mark.asyncio
async def test_async():
    result = await async_function()
    assert result is not None
```

### Q6: Mock数据库连接失败

**问题：** Mock了connect但还是尝试真实连接

**解决方案：** Mock要在类初始化之前

```python
@patch('db_manager.database_manager.pymysql.connect')
def test_connection(self, mock_connect):
    mock_connect.return_value = MagicMock()

    # 在Mock之后创建对象
    manager = DatabaseManager()
    result = manager.connect()
```

### Q7: 测试数据污染

**问题：** 一个测试影响了另一个测试

**解决方案：**
```python
class TestAdapter:
    def setup_method(self):
        """每个测试前重新初始化"""
        self.adapter = Adapter()

    def teardown_method(self):
        """每个测试后清理"""
        self.adapter.close()
        self.adapter = None
```

---

## 快速参考

### 常用命令速查

| 命令 | 说明 |
|------|------|
| `pytest` | 运行所有测试 |
| `pytest -v` | 详细输出 |
| `pytest -k "pattern"` | 运行匹配模式的测试 |
| `pytest -m "not integration"` | 跳过集成测试 |
| `pytest --cov` | 生成覆盖率报告 |
| `pytest --cov-report=html` | 生成HTML覆盖率报告 |
| `pytest -x` | 第一个失败后停止 |
| `pytest --lf` | 只运行上次失败的测试 |
| `pytest -n auto` | 并行运行测试 |

### Mock常用方法

| 方法 | 说明 |
|------|------|
| `Mock()` | 创建Mock对象 |
| `MagicMock()` | 支持魔术方法的Mock |
| `@patch('module.function')` | Mock函数或方法 |
| `mock.return_value = x` | 设置返回值 |
| `mock.side_effect = Exception()` | 设置抛出异常 |
| `mock.assert_called()` | 验证被调用 |
| `mock.assert_called_once()` | 验证只被调用一次 |
| `mock.assert_called_with(args)` | 验证调用参数 |

### 覆盖率目标

| 模块 | 当前 | 目标 |
|------|------|------|
| adapters/ | 88% | 85%+ |
| db_manager/ | 81% | 80%+ |
| utils/ | 86% | 80%+ |
| **整体** | **85%** | **75%+** |

---

## 下一步

完成测试设置后，建议：

1. ✅ 运行测试验证环境：`pytest -v`
2. ✅ 查看覆盖率：`pytest --cov --cov-report=html`
3. ✅ 设置CI/CD自动测试（如GitHub Actions）
4. ✅ 定期审查和更新测试用例
5. ✅ 编写新功能时先写测试（TDD）

---

**文档版本**: v1.0
**最后更新**: 2025-10-16
**维护者**: MyStocks开发团队
