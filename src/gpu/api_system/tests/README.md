# GPU API系统测试套件

## 概述

本测试套件为GPU API系统提供完整的测试覆盖，包括单元测试、集成测试和性能测试。

## 测试结构

```
tests/
├── __init__.py                 # 测试套件入口
├── conftest.py                 # Pytest共享配置和fixtures
├── README.md                   # 本文件
├── unit/                       # 单元测试
│   ├── test_gpu/              # GPU加速引擎测试
│   │   └── test_acceleration_engine.py
│   ├── test_cache/            # 缓存系统测试
│   │   └── test_cache_optimization.py
│   ├── test_services/         # 服务层测试
│   │   └── test_integrated_services.py
│   └── test_utils/            # 工具类测试
│       └── test_gpu_resource_manager.py
├── integration/               # 集成测试
│   └── test_end_to_end.py    # 端到端测试
└── performance/               # 性能测试
    └── test_performance.py    # 性能基准测试
```

## 快速开始

### 安装依赖

```bash
pip install pytest pytest-cov pytest-mock pytest-asyncio
```

### 运行所有测试

```bash
# 使用测试脚本
./run_tests.sh all

# 或直接使用pytest
pytest tests/
```

### 运行特定类型的测试

```bash
# 单元测试
./run_tests.sh unit

# 集成测试
./run_tests.sh integration

# 性能测试
./run_tests.sh performance

# 快速测试（不包括慢速测试）
./run_tests.sh quick

# 仅生成覆盖率报告
./run_tests.sh coverage
```

## 测试标记

测试使用pytest标记进行分类：

- `@pytest.mark.unit` - 单元测试
- `@pytest.mark.integration` - 集成测试
- `@pytest.mark.performance` - 性能测试
- `@pytest.mark.benchmark` - 基准测试
- `@pytest.mark.stress` - 压力测试
- `@pytest.mark.slow` - 慢速测试
- `@pytest.mark.gpu` - 需要GPU的测试
- `@pytest.mark.redis` - 需要Redis的测试

### 使用标记运行测试

```bash
# 运行所有GPU测试
pytest -m gpu

# 运行所有不需要GPU的测试
pytest -m "not gpu"

# 运行性能测试但不运行压力测试
pytest -m "performance and not stress"
```

## 测试覆盖率

### 生成覆盖率报告

```bash
# HTML报告
./run_tests.sh coverage

# 查看HTML报告
open test_reports/coverage/full/index.html
```

### 覆盖率目标

- **总体覆盖率**: ≥80%
- **核心模块**: ≥90%
- **工具模块**: ≥70%

## Fixtures说明

### 环境Fixtures

- `gpu_available` - 检查GPU是否可用
- `redis_available` - 检查Redis是否可用
- `test_config` - 测试配置

### Mock Fixtures

- `mock_gpu_manager` - 模拟GPU资源管理器
- `mock_redis_queue` - 模拟Redis队列
- `mock_metrics_collector` - 模拟指标收集器

### 数据Fixtures

- `sample_market_data` - 样本市场数据
- `sample_strategy_config` - 样本策略配置
- `sample_ml_training_data` - 样本ML训练数据

## 编写测试指南

### 单元测试

```python
import pytest
from unittest.mock import Mock, patch

class TestMyComponent:
    """组件单元测试"""

    @pytest.fixture
    def component(self):
        """创建测试组件"""
        return MyComponent()

    def test_functionality(self, component):
        """测试核心功能"""
        result = component.do_something()
        assert result is not None
```

### 集成测试

```python
@pytest.mark.integration
def test_service_integration(grpc_channel):
    """测试服务集成"""
    # 设置
    stub = ServiceStub(grpc_channel)

    # 执行
    result = stub.CallMethod(request)

    # 验证
    assert result.status == 'SUCCESS'
```

### 性能测试

```python
@pytest.mark.performance
def test_throughput():
    """测试吞吐量"""
    start = time.time()

    # 执行操作
    for _ in range(1000):
        process()

    duration = time.time() - start
    throughput = 1000 / duration

    assert throughput >= target_throughput
```

## 测试报告

### 生成综合测试报告

```bash
python generate_test_report.py
```

报告将包括：
- 测试统计摘要
- 单元测试结果
- 集成测试结果
- 性能测试结果
- 代码覆盖率分析
- 改进建议

### 报告位置

- **HTML覆盖率**: `test_reports/coverage/full/index.html`
- **JSON报告**: `test_reports/test_report.json`
- **Markdown报告**: `test_reports/test_report.md`
- **JUnit XML**: `test_reports/*.xml`

## 持续集成

### GitHub Actions示例

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: ./run_tests.sh all
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 调试测试

### 运行单个测试

```bash
pytest tests/unit/test_gpu/test_acceleration_engine.py::TestBacktestEngineGPU::test_engine_initialization -v
```

### 显示详细输出

```bash
pytest -vv -s tests/unit/
```

### 进入调试器

```bash
pytest --pdb tests/unit/
```

### 只运行失败的测试

```bash
pytest --lf tests/
```

## 性能基准

### 预期性能指标

| 测试类型 | 目标 | 说明 |
|---------|------|------|
| 回测GPU加速比 | ≥15x | GPU vs CPU |
| 实时数据吞吐量 | ≥10000条/秒 | 流式处理 |
| ML训练加速比 | ≥15x | GPU vs CPU |
| 缓存命中率 | ≥80% | L1/L2/Redis |
| 预测延迟 | <1ms | 单次预测 |

## 故障排查

### 常见问题

**Q: 测试提示"GPU not available"**
A: 使用 `-m "not gpu"` 跳过GPU测试，或确保GPU环境配置正确

**Q: Redis连接失败**
A: 确保Redis服务正在运行：`docker run -d -p 6379:6379 redis`

**Q: 导入错误**
A: 确保已安装所有依赖：`pip install -r requirements.txt`

**Q: 覆盖率报告未生成**
A: 安装pytest-cov：`pip install pytest-cov`

## 贡献指南

1. 所有新功能必须包含单元测试
2. 测试覆盖率不得低于80%
3. 所有测试必须通过CI
4. 使用有意义的测试名称和文档字符串

## 参考资源

- [Pytest文档](https://docs.pytest.org/)
- [Pytest-cov文档](https://pytest-cov.readthedocs.io/)
- [GPU API系统文档](../README.md)

---

**维护者**: MyStocks Development Team
**更新时间**: 2025-11-04
