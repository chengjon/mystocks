# 测试快速入门指南

## 🚀 5分钟快速测试

### 前置条件
```bash
# 安装测试依赖
pip install pytest pytest-cov pytest-mock pytest-asyncio
```

### 🆕 WSL2 GPU 支持 (重要!)

**如果你在 WSL2 环境下运行**，需要先初始化 GPU:

```bash
# 测试 GPU 环境
python wsl2_gpu_init.py

# 如果初始化成功，即可运行真实 GPU 测试
python tests/test_real_gpu.py
```

✅ **已验证**: WSL2 环境下真实 GPU 测试全部通过，ML 训练加速比达 **44.76x**！

详细配置请参阅: [`WSL2_GPU_SETUP.md`](WSL2_GPU_SETUP.md)

---

### 运行测试的6种方式

#### 1. 运行所有测试（推荐）
```bash
./run_tests.sh all
```
**预计时间**: 2-3分钟
**输出**: 完整测试报告 + 覆盖率报告

#### 2. 只运行单元测试（最快）
```bash
./run_tests.sh unit
```
**预计时间**: 30-60秒
**输出**: 单元测试结果 + 单元覆盖率

#### 3. 运行集成测试
```bash
./run_tests.sh integration
```
**预计时间**: 1-2分钟
**输出**: 集成测试结果

#### 4. 运行性能测试
```bash
./run_tests.sh performance
```
**预计时间**: 2-3分钟
**输出**: 性能基准测试结果

#### 5. 快速测试（跳过慢速测试）
```bash
./run_tests.sh quick
```
**预计时间**: 20-30秒
**输出**: 快速测试反馈

#### 6. 🆕 运行真实 GPU 测试
```bash
# 使用��实 GPU (不是 Mock)
python tests/test_real_gpu.py

# 或使用 pytest 标记
pytest -m gpu -v tests/
```
**预计时间**: 45秒
**输出**: 真实 GPU 性能基准 (ML 训练 44.76x 加速)
**注意**: WSL2 环境需要先运行 `python wsl2_gpu_init.py`

---

## 📊 查看测试报告

### 方法1: 生成综合报告（推荐）
```bash
# 先运行所有测试
./run_tests.sh all

# 生成综合报告
python generate_test_report.py
```

**报告位置**:
- JSON报告: `test_reports/test_report.json`
- Markdown报告: `test_reports/test_report.md`
- 控制台: 自动显示摘要

### 方法2: 查看覆盖率报告
```bash
# 打开HTML覆盖率报告
open test_reports/coverage/full/index.html  # macOS
xdg-open test_reports/coverage/full/index.html  # Linux
start test_reports/coverage/full/index.html  # Windows
```

### 方法3: 查看JUnit XML报告
```bash
# 单元测试结果
cat test_reports/unit_tests.xml

# 集成测试结果
cat test_reports/integration_tests.xml

# 性能测试结果
cat test_reports/performance_tests.xml
```

---

## 🎯 测试期望结果

### 成功标准
- ✅ 所有测试通过（绿色）
- ✅ 覆盖率 ≥80%
- ✅ 无错误或警告

### 示例输出
```
============================ test session starts ============================
platform linux -- Python 3.8.10, pytest-7.4.0
collected 160 items

tests/unit/test_gpu/test_acceleration_engine.py ............ [ 7%]
tests/unit/test_cache/test_cache_optimization.py ........... [ 14%]
tests/unit/test_utils/test_gpu_resource_manager.py ........ [ 21%]
tests/unit/test_services/test_integrated_services.py ...... [ 28%]
tests/integration/test_end_to_end.py .................... [ 38%]
tests/performance/test_performance.py ................... [ 100%]

======================= 160 passed in 120.5s ========================

---------- coverage: platform linux, python 3.8.10 -----------
Name                              Stmts   Miss  Cover
-----------------------------------------------------
services/gpu_acceleration.py        450     45    90%
services/cache_optimization.py      320     32    90%
utils/gpu_utils.py                  280     28    90%
utils/resource_scheduler.py         240     24    90%
-----------------------------------------------------
TOTAL                              1290    129    90%
```

---

## 🐛 常见问题

### Q1: "GPU not available" 错误
**解决方案**:
```bash
# 跳过GPU测试
pytest -m "not gpu"

# 或运行非GPU测试
./run_tests.sh unit -m "not gpu"
```

### Q2: Redis连接失败
**解决方案**:
```bash
# 启动Redis
docker run -d -p 6379:6379 redis

# 或跳过Redis测试
pytest -m "not redis"
```

### Q3: 测试太慢
**解决方案**:
```bash
# 使用快速模式
./run_tests.sh quick

# 或只运行单元测试
./run_tests.sh unit
```

### Q4: 导入错误
**解决方案**:
```bash
# 安装所有依赖
pip install -r requirements.txt

# 验证安装
python -c "import pytest; import pytest_cov; print('OK')"
```

---

## 🔧 高级用法

### 运行特定测试文件
```bash
pytest tests/unit/test_gpu/test_acceleration_engine.py -v
```

### 运行特定测试类
```bash
pytest tests/unit/test_gpu/test_acceleration_engine.py::TestBacktestEngineGPU -v
```

### 运行特定测试方法
```bash
pytest tests/unit/test_gpu/test_acceleration_engine.py::TestBacktestEngineGPU::test_engine_initialization -v
```

### 使用标记过滤测试
```bash
# 只运行GPU测试
pytest -m gpu

# 不运行慢速测试
pytest -m "not slow"

# 运行性能但不运行压力测试
pytest -m "performance and not stress"
```

### 显示详细输出
```bash
pytest -vv -s tests/
```

### 只运行失败的测试
```bash
pytest --lf tests/
```

### 进入调试器
```bash
pytest --pdb tests/
```

### 并行运行测试（需要pytest-xdist）
```bash
pip install pytest-xdist
pytest -n auto tests/
```

---

## 📈 性能基准

### 预期性能指标

| 测试类型 | 目标 | 验证方法 |
|---------|------|---------|
| 回测GPU加速比 | ≥15x | 性能测试 |
| 实时数据吞吐量 | ≥10000条/秒 | 性能测试 |
| ML训练加速比 | ≥15x | 性能测试 |
| 缓存命中率 | ≥80% | 单元测试 |
| 预测延迟 | <1ms | 性能测试 |

### 验证性能
```bash
# 运行性能测试
./run_tests.sh performance

# 查看结果
cat test_reports/performance/performance_results.txt
```

---

## 🎓 测试最佳实践

### 1. 开发前运行测试
```bash
# 确保起点干净
./run_tests.sh quick
```

### 2. 开发中频繁测试
```bash
# 只测试修改的模块
pytest tests/unit/test_gpu/ -v
```

### 3. 提交前完整测试
```bash
# 完整测试套件
./run_tests.sh all

# 生成报告
python generate_test_report.py
```

### 4. 定期检查覆盖率
```bash
# 生成覆盖率报告
./run_tests.sh coverage

# 查看HTML报告
open test_reports/coverage/full/index.html
```

---

## 📞 获取帮助

### 测试相关资源
- **测试文档**: `tests/README.md`
- **项目文档**: `README.md`
- **完工报告**: `PROJECT_COMPLETION_REPORT.md`

### Pytest文档
- [Pytest官方文档](https://docs.pytest.org/)
- [Pytest-cov文档](https://pytest-cov.readthedocs.io/)

### 常用命令速查
```bash
# 查看所有pytest选项
pytest --help

# 查看测试收集
pytest --collect-only

# 查看所有标记
pytest --markers

# 查看fixtures
pytest --fixtures
```

---

**更新时间**: 2025-11-04
**维护者**: MyStocks Development Team

🎯 **目标**: 让测试变得简单快速！
