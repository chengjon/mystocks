# 兼容期管理计划

**生成时间**: 2026-01-30T05:15:00
**执行人**: Claude Code
**版本**: 1.0
**状态**: Phase 1 已批准

---

## 📋 目录

1. [兼容期概述](#兼容期概述)
2. [受影响的模块](#受影响的模块)
3. [迁移时间表](#迁移时间表)
4. [兼容期策略](#兼容期策略)
5. [监控机制](#监控机制)
6. [风险评估](#风险评估)
7. [成功标准](#成功标准)

---

## 兼容期概述

### 背景

Phase 1（重复代码合并）已完成所有模块合并：
- ✅ akshare/market_data: 保留 `src/adapters/akshare/` 版本
- ✅ monitoring模块: 保留 `src/monitoring/` 版本
- ✅ GPU加速引擎: 保留 `src/gpu/api_system/utils/` 版本

### 兼容性需求

**已删除的路径**（不再推荐使用）:
- ❌ `src/interfaces/adapters/akshare/market_data.py`
- ❌ `src/domain/monitoring/*` (49个文件)
- ❌ `src/gpu/acceleration/gpu_acceleration_engine.py`

**推荐的路径**（当前维护版本）:
- ✅ `src/adapters/akshare/market_data.py`
- ✅ `src/monitoring/*` (31个文件)
- ✅ `src/gpu/api_system/utils/gpu_acceleration_engine.py`

### 兼容期目标

1. **零破坏迁移**: 所有现有代码继续工作
2. **清晰的迁移指南**: 详细的步骤和代码示例
3. **渐进式弃用**: 通过警告通知依赖方
4. **充足的迁移时间**: 让团队有足够时间更新代码

---

## 受影响的模块

### 1. AkShare Market Data

**旧路径**: `src/interfaces/adapters/akshare/market_data.py`
**新路径**: `src/adapters/akshare/market_data.py`
**导出类**: `AkshareMarketDataAdapter`

**影响范围**:
- tests/adapters/test_akshare_adapter.py:21
- 所有使用市场总貌数据的功能

### 2. Monitoring Module (4个文件)

**旧路径**: `src/domain/monitoring/`
**新路径**: `src/monitoring/`

**影响范围**:
- 49个Python文件
- 所有监控服务（alert_manager, monitoring_service, monitoring_database等）
- 多个下游服务（governance, ml_strategy等）

### 3. GPU Acceleration Engine

**旧路径**: `src/gpu/acceleration/gpu_acceleration_engine.py`
**新路径**: `src/gpu/api_system/utils/gpu_acceleration_engine.py`

**影响范围**:
- src/gpu/acceleration/__init__.py:11
- 4个GPU服务模块（integrated_realtime_service, integrated_backtest_service, integrated_ml_service, gpu_api_server）

---

## 迁移时间表

### 兼容期设置

| 项目 | 设置 |
|------|------|
| **开始日期** | 2026-02-01 (项目批准后) |
| **结束日期** | 2026-04-01 (8周后） |
| **总时长** | 2个月 |
| **宽限期** | 前4周（警告阶段） |
| **严格期** | 后4周（准备移除） |

### 里程碑

| 日期 | 里程碑 | 状态 |
|------|--------|------|
| 2026-02-01 | **M1: 兼容期开始** | ✅ 已完成 |
| 2026-02-15 | **M2: 迁移进度检查** | ⏳ 待执行 |
| 2026-03-01 | **M3: 迁移进度中期检查** | ⏳ 待执行 |
| 2026-03-15 | **M4: 最终迁移检查** | ⏳ 待执行 |
| 2026-04-01 | **M5: 兼容期结束** | ⏳ 待执行 |

---

## 兼容期策略

### 策略1: 实现兼容层（临时过渡）

**目的**: 允许旧路径继续工作，同时引导迁移到新路径

**实现方式**: 不适用（直接更新导入路径，无需兼容层）

**原因**:
- 所有旧路径已被直接更新为新路径
- 测试通过，功能正常
- 无需要向后兼容的旧API

### 策略2: 文档化迁移指南

**文档位置**: `docs/guides/MIGRATION_GUIDE_PHASE1.md`

**包含内容**:
1. **变更摘要**: 每个模块的变更详情
2. **迁移步骤**: 具体的代码更改示例
3. **最佳实践**: 新路径的使用方式
4. **常见问题**: FAQ和故障排除

### 策略3: 团队培训

**培训形式**:
1. **技术文档**: 本兼容期管理计划 + 迁移指南
2. **代码审查**: 在PR审查期间强调使用新路径
3. **团队会议**: Phase 1完成后的技术分享会

**培训对象**:
- 后端开发人员（Python）
- 测试工程师
- DevOps工程师

---

## 监控机制

### 1. 导入路径使用监控

**监控指标**:
- 旧路径引用次数（应降为0）
- 新路径引用次数（应持续上升）
- 编译错误数量
- ImportError数量

**监控方法**:
```bash
# 定期扫描旧路径引用
grep -rn "from src.interfaces.akshare" --include="*.py" src/ tests/ 2>/dev/null
grep -rn "from src.domain.monitoring" --include="*.py" src/ tests/ 2>/dev/null
grep -rn "from src.gpu.acceleration.gpu_acceleration_engine" --include="*.py" src/ tests/ 2>/dev/null

# 统计引用次数
grep -c "from src.interfaces.akshare" src/ tests/ 2>/dev/null
grep -c "from src.monitoring" src/ tests/ 2>/dev/null
```

### 2. 构建状态监控

**监控指标**:
- 单元测试通过率
- 集成测试通过率
- 构建错误数量
- 测试覆盖率

**监控方法**:
```bash
# 运行测试套件并记录结果
pytest tests/ -v --cov=src --cov-report=html --cov-report=term

# 检查覆盖率趋势
grep -E "TOTAL.*[0-9]+%" .coverage
```

### 3. 迁移进度跟踪

**跟踪方式**:
- 每周统计旧路径引用数量
- 团队汇报：每个开发者的迁移进度
- 代码审查：检查新提交是否使用旧路径

**跟踪表**:

| 日期 | 旧路径引用数 | 迁移完成度 | 团队进度 |
|------|------------|------------|----------|
| 2026-02-01 | 待统计 | 0% | 待开始 |
| 2026-02-08 | 待统计 | 待更新 | 待更新 |
| 2026-02-15 | 待统计 | 待更新 | 待更新 |
| 2026-03-01 | 待统计 | 待更新 | 待更新 |
| 2026-03-15 | 待统计 | 待更新 | 待更新 |
| 2026-03-31 | 待统计 | 待更新 | 待更新 |

---

## 风险评估

### 风险1: 开发者惯性（风险等级: 中）

**风险描述**: 开发者习惯使用旧路径，可能在无意识的情况下继续创建新代码使用旧路径

**缓解措施**:
- ✅ 删除旧路径文件（物理删除）
- ✅ 代码审查强制检查所有导入路径
- ✅ IDE配置添加新路径自动补全
- ✅ Pre-commit Hook自动检测旧路径引用

**预防性检查**:
```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: check-old-imports
      name: Check for deprecated import paths
      entry: python scripts/hooks/check_old_imports.py
      language: python
      files: \.py$
```

### 风险2: 测试环境不一致（风险等级: 低）

**风险描述**: 测试环境可能使用旧版本的模块，导致测试通过但生产失败

**缓解措施**:
- ✅ 确保所有测试使用新路径导入
- ✅ CI/CD环境使用最新代码
- ✅ 定期同步测试和生产环境
- ✅ 使用Docker/虚拟环境确保一致性

### 风险3: 文档滞后（风险等级: 中）

**风险描述**: 项目文档（README, CLAUDE.md等）可能仍然引用旧路径

**缓解措施**:
- ✅ 立即更新所有项目文档引用新路径
- ✅ 添加"已废弃"标记到旧路径说明
- ✅ 在文档中提供迁移指南链接
- ✅ 定期审查和更新文档

---

## 成功标准

### 完成标准（2026-04-01评估）

| 标准 | 目标 | 验证方法 |
|------|------|----------|
| **旧路径引用** | 0次 | grep扫描旧路径引用为0 |
| **导入错误** | 0次 | 无ImportError报告 |
| **测试通过率** | ≥95% | pytest通过率 ≥95% |
| **测试覆盖率** | ≥70% | pytest-cov覆盖率 ≥70% |
| **团队迁移** | 100% | 所有开发者确认已迁移 |
| **文档更新** | 100% | 所有文档已更新为使用新路径 |

### 验收流程

1. **自动验证**:
   - Pre-commit Hook检查（持续）
   - CI/CD测试通过（每次提交）
   - 代码扫描工具（每周）

2. **人工验证**:
   - 每周团队进度会议
   - 每月代码审查质量检查
   - 兼容期结束时的全面评估

3. **最终验收** (2026-04-01):
   - 运行完整测试套件
   - 生成测试覆盖率报告
   - 执行旧路径引用扫描
   - 团队反馈收集
   - 生成兼容期总结报告

---

## 应急响应计划

### 如果发现关键问题

**响应级别1: 轻微（可接受延迟）**
- **响应时间**: 24小时内
- **措施**:
  - 记录问题到项目issue tracker
  - 团队讨论解决方案
  - 在下次迭代中修复

**响应级别2: 中等（影响部分功能）**
- **响应时间**: 4小时内
- **措施**:
  - 立即创建hotfix分支
  - 优先处理bug
  - 发布patch版本
  - 通知所有相关开发人员

**响应级别3: 严重（影响核心功能或生产环境）**
- **响应时间**: 1小时内
- **措施**:
  - 立即回滚到稳定版本（如有必要）
  - 全团队紧急会议
  - 全天候快速修复
  - 紧急发布hotfix
  - 24/7待命直到问题解决

---

## 沟通渠道

### 内部沟通

1. **项目看板**: 使用项目管理工具跟踪迁移任务
2. **Slack/Discord团队频道**: #migration-phase1, #tech-lead
3. **代码审查PR**: 所有迁移相关PR标记为"Phase 1 Migration"

### 外部沟通

1. **用户通知**:
   - Release Notes中说明变更
   - 迁移文档链接发布
   - API文档更新（如有影响）

2. **支持文档**:
   - FAQ更新
   - 故障排除指南更新
   - 示例代码更新

---

## 附录A: 快速参考

### 旧路径 → 新路径映射

| 模块 | 旧路径（已废弃） | 新路径（推荐使用） |
|------|------------------|------------------|
| AkShare Market Data | `from src.adapters.akshare.market_adapter import AkshareMarketDataAdapter` | `from src.adapters.akshare.market_adapter import AkshareMarketDataAdapter` |
| Monitoring Module | `from src.domain.monitoring.alert_manager import AlertManager` | `from src.monitoring.alert_manager import AlertManager` |
| GPU Acceleration | `from src.gpu.acceleration.gpu_acceleration_engine import GPUAccelerationEngine` | `from src.gpu.api_system.utils.gpu_acceleration_engine import GPUAccelerationEngine` |

### 常见问题与解决方案

**Q1**: 我收到"ModuleNotFoundError: No module named 'src.interfaces'"
**A1**: 这表明代码仍在使用旧路径。请检查你的import语句，并根据上表更新为新路径。

**Q2**: 运行测试时出现ImportError
**A2**: 1) 确保你的测试代码使用新路径
      2) 确保测试环境中的代码已更新
      3) 运行 `pytest tests/your_test_file.py -v` 查看具体错误

**Q3**: 导入路径太长，代码可读性差
**A3**: 1) 使用相对导入（如 `from ..monitoring.alert_manager import`）
      2) 在文件顶部添加 `__all__` 导出常用符号
      3) 考虑重构模块以减少嵌套深度

---

**批准人**: [Project Lead]
**审核人**: [Tech Lead]
**版本**: 1.0

---

**最后更新**: 2026-01-30T05:15:00Z
