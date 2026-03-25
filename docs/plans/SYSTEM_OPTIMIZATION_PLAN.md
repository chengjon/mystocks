# 系统优化下一步任务计划 (System Optimization Next Steps)

**基于文档**: `technical_debt_assessment_report.md`, `technical_debt_remediation_plan.md`, `技术负债修复报告.md`
**当前状态**: Phase 1 (安全与配置修复) 已完成 ✅
**重点阶段**: Phase 2 (架构解耦与代码质量) & Phase 3 (性能优化)

---

## 📅 任务概览

根据之前的技术负债分析与修复进度，当前系统优化的重心从"紧急安全修复"转向"系统架构健壮性"和"核心性能提升"。

### 优先级图表

| 优先级 | 任务类别 | 涉及模块 | 预计耗时 | 目标 |
| :--- | :--- | :--- | :--- | :--- |
| 🔴 **P0 (本周)** | **架构解耦** | GPU加速模块, Web后端入口 | 3-5 天 | 降低核心模块耦合度，提升可测试性 |
| 🟡 **P1 (下周)** | **代码去重** | 测试套件 (TDX), 脚本工具 | 2-3 天 | 提取公共逻辑，减少维护成本 |
| 🟢 **P2 (两周内)** | **性能优化** | 数据分析器, 自动化工作流 | 3-5 天 | 引入异步IO，优化内存占用 |
| 🔵 **P3 (持续)** | **质量门禁** | CI/CD, 静态分析 | 持续 | 防止技术负债回滚 |

---

## 🚀 Phase 2: 架构解耦与代码质量 (当前重点)

**目标**: 解决报告中标识为 `High Coupling` (高耦合) 的关键文件，并减少 `Code Duplication` (代码重复)。

### 2.1 GPU 模块解耦与重构 (High Coupling)
**问题**: 以下文件被标记为高耦合，难以独立测试和扩展。
- `src/gpu/accelerated/data_processor_gpu.py`
- `src/gpu/api_system/utils/gpu_acceleration_engine.py`
- `src/gpu/api_system/services/integrated_realtime_service.py`

**执行任务**:
1.  **抽象接口层**: 为 GPU 加速引擎定义标准 Interface/Protocol，将具体实现与调用逻辑分离。
2.  **依赖注入**: 在 `integrated_realtime_service.py` 中移除对具体 GPU 类的直接实例化，改为依赖注入。
3.  **工厂模式**: 实现 `GPUProcessorFactory`，根据环境（有无 CUDA）动态返回合适的处理器实例。
4.  **单元测试**: 为解耦后的 GPU 逻辑补充 Mock 测试。

### 2.2 Web 后端入口重构 (High Coupling)
**问题**: `web/backend/app/main.py` 承担了过多的初始化和路由职责。

**执行任务**:
1.  **路由拆分**: 将路由定义移至 `web/backend/app/routers/` 目录下的独立模块。
2.  **应用工厂**: 实现 `create_app()` 工厂函数模式，分离配置加载和应用初始化。
3.  **中间件抽离**: 将 CORS、日志等中间件配置移至独立文件。

### 2.3 代码去重 (Code Duplication)
**问题**: 脚本和测试代码中存在大量重复逻辑 (223处重复)。
- 重点文件: `scripts/populate_lhb_data.py`, `tests/test_tdx_binary_read.py`

**执行任务**:
1.  **测试工具库**: 创建 `tests/utils/tdx_test_helpers.py`，提取 TDX 二进制读取的公共测试逻辑。
2.  **脚本公共库**: 提取数据填充脚本中的通用数据库连接和处理逻辑到 `scripts/common/`。

---

## ⚡ Phase 3: 性能优化 (准备启动)

**目标**: 解决 `technical_debt_analyzer.py` 和自动化工作流中的同步 I/O 瓶颈。

### 3.1 核心工具异步化改造
**问题**: 静态代码分析工具和数据处理脚本目前主要使用同步 I/O，处理大量文件时速度较慢。

**执行任务**:
1.  **技术负债分析器**: 改造 `technical_debt_analyzer.py`，使用 `asyncio` 和 `aiofiles` 并发读取文件。
2.  **自动化工作流**: 将 `scripts/ai_automation_workflow.py` 中的网络请求和数据库操作改为异步执行。

### 3.2 内存使用优化
**问题**: 处理大规模股票数据时存在内存峰值风险。

**执行任务**:
1.  **生成器改造**: 在 `data_processor_gpu.py` 中，将列表推导式改为生成器表达式，避免一次性加载过多数据。
2.  **Pandas 优化**: 审查 DataFrame 数据类型，将 `object` 类型列转换为 `category` 或具体数值类型以节省内存。

---

## 🛡️ 长期维护机制

### 自动化质量检查
建议将以下命令加入 git pre-commit hook 或 CI 流程：

```bash
# 安全扫描
bandit -r src/ -x tests/

# 复杂度检查 (圈复杂度 < 10)
radon cc src/ -a -nc

# 代码风格
ruff check src/
```

## ✅ 验收标准
1. `High Coupling` 问题数降至 0。
2. 核心模块 (GPU, Web) 单元测试覆盖率提升 10%。
3. `technical_debt_analyzer.py` 执行速度提升 30% 以上。
