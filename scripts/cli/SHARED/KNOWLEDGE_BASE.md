# CLI知识库

**Purpose**: 在所有CLI之间共享经验、最佳实践和解决方案

**最后更新**: 2026-01-01

---

## 📚 知识分类

### 1. 问题解决方案 (Problem Solutions)

记录遇到的问题及其解决方案，避免重复踩坑。

#### 🔧 常见问题

**Q: TypeScript类型错误如何快速修复？**

A: 使用Ralph Wiggum迭代方法（参见 `docs/reports/` 中的相关报告）:
1. 运行 `npx vue-tsc --noEmit` 获取完整错误列表
2. 按错误类型分类（arg-type, union-attr等）
3. 每次迭代专注修复一类错误
4. 使用 `@ts-nocheck` 处理第三方库问题

**示例报告**: `docs/reports/RALPH_WIGGUM_ITERATION_SUMMARY.md`

---

**Q: 前端Mock数据切换到真实API时应该注意什么？**

A: 参考 `docs/guides/MOCK_REAL_DATA_SWITCHING_GUIDE.md`:
1. 使用环境变量驱动数据源切换（`VITE_USE_MOCK=true/false`）
2. API适配层统一处理数据格式转换
3. 保留Mock数据用于离线开发和测试
4. 使用类型定义确保前后端数据一致性

**关键文件**: `web/frontend/src/api/adapters/`

---

### 2. 最佳实践 (Best Practices)

#### ✅ 开发流程

**任务执行流程**:
1. 接收任务 → 查看TASK.md了解需求和依赖
2. 规划实现 → 使用TodoWrite工具创建检查点
3. 编码实现 → 遵循项目编码规范（见 `CLAUDE.md`）
4. 测试验证 → 运行相关测试确保质量
5. 文档更新 → 更新STATUS.md进度
6. 完成报告 → 生成REPORT.md总结工作

**代码质量保证**:
- **日常开发**: `ruff check --fix .`
- **提交前**: Pre-commit hooks自动运行9步检查
- **定期审查**: 每周运行Pylint深度分析

参考: `docs/guides/PYTHON_QUALITY_ASSURANCE_WORKFLOW.md`

---

#### ✅ 文档规范

**STATUS.md更新规范**:
- **State字段**: 🟢 Active / 🟡 Idle / 🔴 Blocked / 🟢 Done
- **Updated字段**: 每次进展都更新时间戳（格式: `YYYY-MM-DD HH:MM:SS`）
- **Current Task**: 明确当前正在执行的任务
- **Blocked On**: 如果阻塞，明确阻塞原因和依赖

**REPORT.md模板**:
```markdown
# 任务完成报告

**任务**: task-X.Y
**完成时间**: YYYY-MM-DD HH:MM
**执行者**: [CLI名称]

## 完成内容

[列出完成的主要工作]

## 技术细节

[关键技术实现细节]

## 测试验证

- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] ESLint/Pylint检查通过
- [ ] 功能验证通过

## 遇到的问题及解决方案

1. **问题描述**
   - 解决方案: [详细说明]

## 经验总结

[可复用的经验和最佳实践]

## 后续建议

[对下一步工作的建议]
```

---

### 3. 技术架构知识 (Technical Architecture)

#### 🏗️ 双数据库架构

**设计原则**: Right Database for Right Workload

**数据分类**:
- **高频时序数据** (Tick/分钟K线) → TDengine
  - 极致压缩比（20:1）
  - 超高写入性能
  - 自动数据保留策略

- **日线数据** → PostgreSQL + TimescaleDB
  - TimescaleDB超表优化
  - 支持复杂JOIN查询
  - ACID事务保证

- **参考/衍生/交易/元数据** → PostgreSQL标准表
  - 关系型数据完整性
  - 复杂索引和查询优化

**统一访问层**: `MyStocksUnifiedManager`
- 自动路由到正确的数据库
- 配置驱动的表管理
- 完整的监控和日志

参考: `src/core/unified_manager.py`

---

#### 🔄 Multi-CLI协作机制

**核心原则**: 主CLI提供指导，Worker CLI负责执行

**通信机制**: Mailbox异步通信
- **4种消息类型**: ALERT, REQUEST, RESPONSE, NOTIFICATION
- **事件监听**: mailbox_watcher.py（watchdog实现）
- **消息归档**: archive/目录自动清理

**协调机制**: Smart Coordinator
- **阻塞自动解决**: 识别依赖问题，协调资源
- **空闲资源分配**: 自动为空闲CLI分配任务
- **冲突自动预防**: 检测并预防资源冲突
- **健康检查**: 定期检查CLI状态

参考文档:
- `docs/architecture/MULTI_CLI_COLLABORATION_V2_IMPLEMENTATION.md`
- `docs/guides/MULTI_CLI_WORKTREE_MANAGEMENT.md`

---

### 4. 工具和脚本使用 (Tools & Scripts)

#### 🔧 开发工具

**健康检查**: `scripts/dev/health_check.py`
```bash
# 检查所有CLI状态
python scripts/dev/health_check.py --all

# 生成HEALTH.md报告
python scripts/dev/health_check.py --generate-report
```

**指标收集**: `scripts/dev/metrics_collector.py`
```bash
# 生成METRICS.md报告
python scripts/dev/metrics_collector.py --generate-report

# 导出JSON格式
python scripts/dev/metrics_collector.py --export-json metrics.json
```

**智能协调器**: `scripts/dev/smart_coordinator.py`
```bash
# 手动执行协调
python scripts/dev/smart_coordinator.py --auto

# 查看协调规则
python scripts/dev/smart_coordinator.py --help
```

---

### 5. 性能优化经验 (Performance Optimization)

#### ⚡ GPU加速引擎

**成就**: 68.58x平均性能提升，662+ GFLOPS峰值性能

**适用场景**:
- 大规模矩阵运算（相关性计算、协方差矩阵）
- 批量技术指标计算
- Monte Carlo模拟

**使用方法**:
```python
from src.gpu.core.hardware_abstraction.resource_manager import GPUResourceManager
from src.gpu.core.kernels.matrix_kernels import MatrixKernelEngine

# 初始化GPU资源
gpu_mgr = GPUResourceManager()
if gpu_mgr.gpu_available:
    engine = MatrixKernelEngine(gpu_mgr)

    # 使用GPU加速计算
    result = engine.multiply_matrices(matrix_a, matrix_b)
```

参考: `docs/api/GPU开发经验总结.md`

---

#### ⚡ 前端性能优化

**ArtDeco主题系统性能优化**:
- ✅ 按需加载主题文件（仅加载当前主题）
- ✅ CSS变量缓存（减少重复计算）
- ✅ 组件懒加载（Vue 3 `<Suspense>`）
- ✅ 虚拟滚动（大数据列表）

**Lighthouse优化成果**:
- Performance: 95+
- Accessibility: 100
- Best Practices: 100
- SEO: 100

参考: `docs/reports/ARTDECO优化方案对比说明.md`

---

### 6. 安全和规范 (Security & Standards)

#### 🔒 安全编码规范

**JWT密钥管理**:
```bash
# 自动生成并更新JWT密钥
bash scripts/JWT_key_update.sh

# 或手动生成
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
openssl rand -hex 32
```

**环境变量管理**:
- ✅ 所有敏感信息通过 `.env` 文件配置
- ✅ `.env.example` 提供模板
- ✅ `.gitignore` 排除 `.env` 防止泄露
- ✅ 定期轮换密钥（见 `docs/guides/PHASE0_CREDENTIAL_ROTATION_GUIDE.md`）

**安全扫描**:
```bash
# Bandit安全扫描
bandit -r src/

# Safety依赖安全检查
safety check --json

# 生成安全报告
python scripts/dev/verify_security_simple.py
```

参考: `docs/reports/SECURITY_AUDIT_REPORT.md`

---

### 7. 调试技巧 (Debugging Tips)

#### 🐛 常用调试命令

**后端调试**:
```bash
# 查看后端日志
pm2 logs backend

# 检查API健康状态
python src/utils/check_api_health.py

# 测试API端点
curl -X GET http://localhost:8000/api/health
```

**前端调试**:
```bash
# 查看前端错误
npm run lint

# TypeScript类型检查
npx vue-tsc --noEmit

# 运行E2E测试
npx playwright test
```

**数据库调试**:
```bash
# TDengine连接测试
python scripts/database/check_tdengine_tables.py

# PostgreSQL连接测试
PGPASSWORD=c790414J psql -h localhost -U postgres -d mystocks
```

---

### 8. 术语表 (Glossary)

- **CLI**: Command Line Interface，在此项目中指独立的开发工作单元（如web CLI, api CLI）
- **Worker CLI**: 执行具体任务的工作CLI
- **Main CLI**: 协调和管理所有Worker CLI的主协调器
- **Mailbox**: CLI间异步通信的消息邮箱
- **Smart Coordinator**: 智能协调器，自动解决阻塞和分配资源
- **Task Pool**: 任务池，存储待分配的任务
- **Checkpoints**: 检查点，记录重要的里程碑状态
- **Ralph Wiggum**: 迭代式问题修复方法，专注于系统性解决错误

---

## 📝 贡献指南

### 如何添加知识条目

1. **确定类别**: 问题解决、最佳实践、架构知识、工具使用、性能优化、安全规范、调试技巧
2. **使用模板**: 遵循现有条目的格式
3. **清晰标题**: 使用具体、描述性的标题
4. **代码示例**: 提供可执行的代码示例
5. **交叉引用**: 链接到相关文档和报告

### 知识审查

- **准确性**: 确保技术信息准确无误
- **时效性**: 标注最后更新时间
- **可复用性**: 确保经验可复用于其他场景
- **完整性**: 提供完整的上下文和步骤

---

## 🔗 相关资源

- **项目指南**: `CLAUDE.md`
- **架构文档**: `docs/architecture/`
- **开发指南**: `docs/guides/`
- **完成报告**: `docs/reports/`
- **Multi-CLI v2实现**: `docs/architecture/MULTI_CLI_COLLABORATION_V2_IMPLEMENTATION.md`

---

**知识库维护者**: Main CLI
**审查频率**: 每周
**更新策略**: 按需更新 + 定期整理
