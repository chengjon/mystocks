# Task 1 快速启动指南

## 立即执行的命令

### 1️⃣ 安装测试依赖（5分钟）
```bash
pip install pytest pytest-cov pytest-benchmark coverage
```

### 2️⃣ 分析当前测试覆盖率（5分钟）
```bash
# 生成覆盖率报告
pytest --cov=core --cov=db_manager --cov=adapters --cov-report=html

# 查看覆盖率报告
# 在浏览器中打开 htmlcov/index.html
```

### 3️⃣ 创建测试目录结构（5分钟）
```bash
mkdir -p tests/fixtures tests/benchmarks
touch tests/__init__.py
touch tests/conftest.py
touch tests/test_data_manager.py
touch tests/test_unified_manager.py
```

### 4️⃣ 更新任务状态（1分钟）
```bash
# 将 Task 1 标记为进行中
mcp__taskmaster-ai__set_task_status --id 1 --status in-progress
```

---

## 每天的工作流程

### 早晨（开始工作）
1. 查看今天的任务：
   ```bash
   cat .taskmaster/tasks/task_001.txt
   ```

2. 更新今天的子任务为进行中：
   ```bash
   mcp__taskmaster-ai__set_task_status --id 1.1 --status in-progress
   ```

3. 开始编写代码/测试

### 中午（进度检查）
1. 运行测试验证进度：
   ```bash
   pytest tests/ -v
   pytest --cov=core --cov=db_manager --cov-report=term-missing
   ```

2. 如需调整任务范围，更新任务描述：
   ```bash
   mcp__taskmaster-ai__update_subtask --id 1.1 --prompt "今天完成了 X，遇到了 Y 问题..."
   ```

### 晚间（提交进度）
1. 提交代码到 git：
   ```bash
   git add tests/
   git commit -m "feat(test): 实现 DataManager 单元测试 (Task 1.1)"
   ```

2. 标记完成的子任务：
   ```bash
   mcp__taskmaster-ai__set_task_status --id 1.1 --status done
   ```

3. 查看下一个子任务：
   ```bash
   mcp__taskmaster-ai__next_task
   ```

---

## 关键文件位置

📁 **任务相关**:
- `.taskmaster/tasks/task_001.txt` - Task 1 详细描述
- `.taskmaster/TASK_PLANNING_SUMMARY.txt` - 完整项目规划
- `docs/TASK_1_IMPLEMENTATION_GUIDE.md` - 详细实施指南（你正在读的）

📁 **代码相关**:
- `core/` - 核心模块（需要测试）
- `db_manager/` - 数据库管理（需要测试）
- `adapters/` - 适配器（需要测试）
- `tests/` - 测试代码（需要编写）

📁 **文档相关**:
- `README.md` - 项目概览（需要完善）
- `CLAUDE.md` - 开发指南（需要完善）

---

## 立即行动项 - 第一周计划

### 第1天：准备阶段（4h）
- [x] 安装测试依赖
- [x] 分析当前测试覆盖率
- [ ] 创建测试目录和基础配置
- [ ] 编写 conftest.py 和 fixtures
- [ ] 更新 Task 1 为 in-progress

### 第2-3天：DataManager 测试（8h）
- [ ] 测试 O(1) 路由性能
- [ ] 测试数据分类映射
- [ ] 测试错误处理
- [ ] 测试路由规则更新

### 第4-5天：数据访问层测试（8h）
- [ ] TDengineDataAccess 单元测试
- [ ] PostgreSQLDataAccess 单元测试
- [ ] 连接管理测试
- [ ] 错误恢复测试

### 第6天：统一接口和工具测试（4h）
- [ ] MyStocksUnifiedManager 测试
- [ ] ConfigDrivenTableManager 测试
- [ ] 其他工具类测试

### 第7天：检查和调整（2h）
- [ ] 验证覆盖率达到 80%
- [ ] 整理测试代码
- [ ] 提交第一周成果

---

## 常见问题

**Q: 如何运行特定的测试？**
```bash
# 运行单个测试文件
pytest tests/test_data_manager.py -v

# 运行单个测试类
pytest tests/test_data_manager.py::TestDataManager -v

# 运行单个测试方法
pytest tests/test_data_manager.py::TestDataManager::test_routing_o1_performance -v
```

**Q: 如何生成覆盖率报告并查看缺漏？**
```bash
# 生成带缺漏行的报告
pytest --cov=core --cov=db_manager --cov-report=term-missing

# 生成 HTML 报告
pytest --cov=core --cov=db_manager --cov-report=html
open htmlcov/index.html
```

**Q: 如何模拟数据库进行测试？**
```python
# 使用 pytest fixtures 和 mock
from unittest.mock import Mock, patch

@pytest.fixture
def mock_tdengine():
    with patch('data_access.tdengine_access.TDengineDataAccess') as mock:
        yield mock
```

**Q: 如何处理缓慢的集成测试？**
```python
# 为集成测试添加标记
@pytest.mark.integration
def test_integration():
    pass

# 运行时跳过集成测试
pytest -m "not integration"
```

---

## 进度追踪

将此表格复制到你的日志中，每天更新进度：

| 日期 | 子任务 | 预计(h) | 实际(h) | 状态 | 备注 |
|------|--------|--------|--------|------|------|
| 2025-10-28 | 1.1 准备阶段 | 4 | - | 进行中 | - |
| 2025-10-29 | 1.1 DataManager 测试 | 4 | - | 待开始 | - |
| 2025-10-30 | 1.1 DataManager 测试 | 4 | - | 待开始 | - |
| ... | ... | ... | ... | ... | ... |

---

## 需要帮助？

如果遇到问题：

1. **查看详细指南**：
   ```bash
   cat docs/TASK_1_IMPLEMENTATION_GUIDE.md | less
   ```

2. **查看示例代码**：
   在指南中搜索 "关键测试用例示例"

3. **查看现有测试**：
   ```bash
   find . -name "test_*.py" -type f
   ```

4. **更新任务状态为阻断**：
   ```bash
   mcp__taskmaster-ai__set_task_status --id 1 --status deferred
   # 然后描述遇到的问题
   mcp__taskmaster-ai__update_task --id 1 --prompt "遇到的问题描述"
   ```

---

**开始日期**: 2025-10-28  
**目标完成日期**: 2025-11-25（约 4 周）  
**预计工时**: 40 小时  

祝你开发顺利！🚀
