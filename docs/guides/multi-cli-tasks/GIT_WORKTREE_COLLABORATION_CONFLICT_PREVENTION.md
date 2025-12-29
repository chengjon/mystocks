# Git Worktree协作冲突预防规范

**文档版本**: v1.0
**创建日期**: 2025-12-29
**问题来源**: Worker CLI反馈的实际问题
**维护者**: Main CLI

---

## 📋 文档目的

本文档解决两个关键的Git Worktree协作问题：

1. **Pre-commit配置冲突**：主CLI和Worker CLI同时修改pre-commit配置导致合并冲突
2. **任务分配冲突**：多个CLI修改同一文件导致协作冲突

**核心原则**:
- ✅ **明确所有权**：每个文件有明确的拥有者
- ✅ **职责分离**：每个CLI有清晰的职责范围
- ✅ **配置集中管理**：pre-commit配置在主仓库统一管理
- ✅ **文件组织标准化**：通过目录结构避免冲突

---

## 🚨 问题1：Pre-commit配置冲突

### **问题描述**

**场景**：
```
时间线：
Day 1 10:00 - 主CLI修改主仓库的.pre-commit-config.yaml
Day 1 14:00 - Worker CLI-1修改自己worktree的.pre-commit-config.yaml
Day 1 18:00 - Worker CLI-2修改自己worktree的.pre-commit-config.yaml
Day 2 10:00 - 合并时产生冲突
```

**根本原因**:
- `.pre-commit-config.yaml`在所有仓库中都有
- 各个CLI根据自己的需求修改配置
- Git无法自动合并配置文件的修改

### **解决方案**

#### **方案A：Pre-commit配置只由主CLI管理** ✅ **强烈推荐**

**原则**:
- ✅ 主仓库：`.pre-commit-config.yaml`由主CLI维护
- ✅ Worker CLI：继承主仓库的pre-commit配置，**不修改**
- ✅ 环境变量绕过：Worker CLI使用`DISABLE_DIR_STRUCTURE_CHECK=1`

**实施步骤**：

**1. 主CLI职责**（在主仓库`/opt/claude/mystocks_spec`）:
```bash
# 主CLI唯一负责维护pre-commit配置
cd /opt/claude/mystocks_spec

# 修改.pre-commit-config.yaml
vim .pre-commit-config.yaml

# 提交修改
git add .pre-commit-config.yaml
git commit -m "chore(pre-commit): update configuration for all CLIs"
```

**2. Worker CLI职责**（在worktree中）:
```bash
# Worker CLI不修改.pre-commit-config.yaml
# 使用环境变量绕过不适用的检查

# 方式1: 绕过目录结构检查（推荐）
DISABLE_DIR_STRUCTURE_CHECK=1 git commit -m "message"

# 方式2: 完全跳过hooks（仅紧急情况）
git commit --no-verify -m "message"
```

---

## 🚨 问题2：任务分配冲突

### **问题描述**

**场景**：
```
时间线：
Day 1 10:00 - CLI-1修改了web/frontend/src/components/Chart.vue
Day 1 14:00 - CLI-6也在代码质量检查中修改了同一文件
Day 2 10:00 - 合并时产生冲突：Both modified
```

**根本原因**:
- 文件所有权不明确
- 职责范围重叠
- 缺少协调机制

### **解决方案**

#### **核心原则：清晰的文件所有权**

```
文件所有权规则：
1. 每个文件有明确的拥有者
2. 拥有者负责修改，其他人只读
3. 跨CLI修改需要主CLI协调
4. 使用目录结构物理隔离
```

#### **解决方案A：目录职责划分** ✅ **强烈推荐**

**原则**：通过目录结构物理隔离，避免冲突

**完整目录所有权表**：

| 目录 | 拥有者CLI | 说明 | 其他CLI |
|------|----------|------|---------|
| `src/` | 主CLI（主仓库） | 核心业务逻辑 | ❌ 不可修改 |
| `web/frontend/src/components/Charts/` | CLI-1 | K线图组件 | ❌ 只读 |
| `web/frontend/src/api/klineApi.ts` | CLI-1 | K线图API | ❌ 只读 |
| `web/frontend/src/api/indicatorApi.ts` | CLI-1 | 指标API | ❌ 只读 |
| `docs/api/contracts/` | CLI-2 | API契约文档 | ❌ 只读 |
| `src/gpu/` | CLI-5 | GPU相关代码 | ❌ 只读 |
| `scripts/maintenance/` | CLI-6 | 质量保证脚本 | ❌ 只读 |
| `tests/` | CLI-6 | 测试文件 | ❌ 只读 |
| `web/backend/app/schemas/` | CLI-2 | 数据模式定义 | ❌ 只读 |
| `.pre-commit-config.yaml` | 主CLI | Pre-commit配置 | ❌ 只读 |
| `pyproject.toml` | 主CLI | 项目配置 | ❌ 只读 |

**共享文件（协调修改）**：
- `README.md` - 主CLI和Worker CLI协调
- `CLAUDE.md` - 主CLI维护，Worker CLI建议
- `.env.example` - 主CLI维护

---

## 🎯 总结

### **Pre-commit配置冲突**

**问题**：主CLI和Worker CLI同时修改pre-commit配置
**解决**：
- ✅ Pre-commit配置只由主CLI管理
- ✅ Worker CLI使用环境变量绕过（`DISABLE_DIR_STRUCTURE_CHECK=1`）
- ✅ 不修改继承的配置文件

### **任务分配冲突**

**问题**：多个CLI修改同一文件
**解决**：
- ✅ 创建文件所有权映射（`.FILE_OWNERSHIP`）
- ✅ 明确职责范围（目录物理隔离）
- ✅ 建立协调机制（跨CLI修改申请）
- ✅ 冲突检测脚本（`check_file_conflicts.sh`）

### **执行优先级**

**立即执行（今天）**：
1. ✅ 创建`.FILE_OWNERSHIP`文件
2. ✅ 更新`MAIN_CLI_WORKFLOW_STANDARDS.md`
3. ✅ 创建冲突检测脚本
4. ✅ 提交到Git

**后续执行**：
1. 在每次分配新任务前检查文件所有权
2. 定期运行冲突检测脚本
3. 协调跨CLI修改需求

---

**文档版本**: v1.0
**创建日期**: 2025-12-29
**维护者**: Main CLI
**更新频率**: 每次分配新任务时更新

**核心原则**: 明确所有权 + 职责分离 + 协调机制 = 零冲突协作
