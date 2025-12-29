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

**3. 更新工作流程指南**：
在每个CLI的README.md中添加明确说明：

```markdown
## Git提交流程

### Pre-commit配置说明
本worktree继承主仓库的pre-commit配置。
- ⚠️ **不要修改**`.pre-commit-config.yaml`
- ✅ 使用环境变量绕过不适用的检查：
  ```bash
  DISABLE_DIR_STRUCTURE_CHECK=1 git commit -m "message"
  ```

### 为什么不修改？
1. 避免与主仓库配置冲突
2. 保持配置一致性
3. 简化合并流程
```

**4. 添加到.gitignore（可选）**：
在Worker CLI的worktree中：
```bash
# 将.pre-commit-config.yaml添加到.gitignore
# 这样Worker CLI就不会意外提交配置修改
echo ".pre-commit-config.yaml" >> .gitignore
git add .gitignore
git commit -m "chore: ignore pre-commit config (managed by main repo)"
```

#### **方案B：Per-Cli配置文件（如果方案A不够用）**

**适用场景**：某个CLI确实需要特殊的pre-commit配置

**实施方法**：
```bash
# 在CLI-2的worktree中创建专属配置
cd /opt/claude/mystocks_phase6_api_contract

# 创建CLI-2专属的pre-commit配置
cat > .pre-commit-cli2.yaml << 'EOF'
# CLI-2特定的pre-commit配置
repos:
  - repo: local
    hooks:
      - id: mypy-check
        name: MyPy (Type Check)
        entry: mypy web/backend/
        language: system
        pass_filenames: false
        always_run: true
EOF

# 在.git/config中引用
git config pre-commit.config .pre-commit-cli2.yaml
```

**优点**：
- ✅ 每个CLI有独立的配置
- ✅ 不会与主仓库冲突
- ✅ 可以针对CLI需求定制

**缺点**：
- ❌ 增加维护复杂度
- ❌ 配置不一致

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
|------|----------|------|---------| `src/` | 主CLI（主仓库） | 核心业务逻辑 | ❌ 不可修改 |
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

#### **解决方案B：协调机制**

**1. 跨CLI修改申请流程**：

```
Worker CLI需要修改其他CLI拥有的文件时：
1. 向主CLI提交申请（包含修改原因和内容）
2. 主CLI评估影响范围
3. 主CLI协调相关CLI
4. 主CLI执行修改或授权Worker CLI修改
5. 主CLI通知所有相关CLI
```

**2. 冲突检测和预防**：

**在主CLI工作规范中添加**：
```markdown
## 任务分配前的冲突检查清单

主CLI在分配任务前必须确认：

- [ ] 文件所有权明确（每个文件属于哪个CLI）
- [ ] 职责范围清晰（目录职责划分）
- [ ] 没有重叠的修改目标（检查任务清单）
- [ ] 建立协调机制（如何处理跨CLI需求）
```

**3. 定期同步会议**：

```
频率：每天一次（Day 1-14）
参与方：主CLI + 所有活跃的Worker CLI
议程：
  - 汇报当天修改的文件
  - 识别潜在冲突
  - 协调第二天的工作
  - 确认文件所有权
```

#### **解决方案C：文件锁定机制（可选）**

**使用Git LFS或类似机制标记文件所有权**：

```bash
# 在主仓库中创建文件所有权映射
cat > .FILE_OWNERSHIP << 'EOF'
# 文件所有权映射
# 格式：目录路径: 拥有者CLI
src/                                main
web/frontend/src/components/Charts/ cli-1
docs/api/contracts/                  cli-2
src/gpu/                             cli-5
scripts/maintenance/                cli-6
tests/                               cli-6
.pre-commit-config.yaml              main
EOF

# 添加到.git
git add .FILE_OWNERSHIP
git commit -m "chore: add file ownership mapping"
```

**实施检查脚本**：
```bash
#!/bin/bash
# check-file-conflicts.sh - 检查潜在的文件冲突

echo "=== 检查文件冲突风险 ==="

# 扫描最近修改的文件
for cli in /opt/claude/mystocks_phase*; do
  if [ -d "$cli" ]; then
    cli_name=$(basename "$cli")
    echo "## $cli_name"

    # 检查是否有修改其他CLI拥有的文件
    cd "$cli"
    git diff --name-only | while read file; do
      # 检查文件所有权
      owner=$(grep "^$file:" /opt/claude/mystocks_spec/.FILE_OWNERSHIP 2>/dev/null | cut -d: -f2)
      if [ -n "$owner" ] && [ "$owner" != "$cli_name" ]; then
        echo "  ⚠️  $file 拥有者: $owner"
      fi
    done
  fi
done
```

---

## 📚 主CLI任务分配检查清单

### **Phase 0: 任务分配前检查** ⚠️ **关键步骤**

在创建和分配任务给Worker CLI之前，主CLI必须完成：

#### **0.1 文件所有权确认**
- [ ] 创建`.FILE_OWNERSHIP`映射文件
- [ ] 明确每个目录的拥有者
- [ ] 明确共享文件的使用规则
- [ ] 记录在主CLI工作规范中

#### **0.2 职责范围确认**
- [ ] 为每个CLI定义清晰的职责范围
- [ ] 确保职责不重叠
- [ ] 记录在任务分配文档中
- [ ] 在CLI README中说明职责边界

#### **0.3 潜在冲突检查**
- [ ] 运行冲突检测脚本
- [ ] 识别可能冲突的文件
- [ ] 调整任务分配避免冲突
- [ ] 建立协调机制

#### **0.4 协调机制建立**
- [ ] 定义跨CLI修改申请流程
- [ ] 建立定期同步会议机制
- [ ] 创建冲突报告流程
- [ ] 记录在主CLI工作规范中

### **Phase 1: Worktree创建时检查**

创建每个Worktree时必须确认：

#### **1.1 基础配置**
- [ ] Worktree已创建
- [ ] README.md已初始化
- [ ] Hooks权限已修复
- [ ] Git远程名称已标准化

#### **1.2 配置文件处理**
- [ ] `.pre-commit-config.yaml`继承主仓库
- [ ] 添加到`.gitignore`（可选）或明确说明不修改
- [ ] 环境变量绕过方法已记录在README中

#### **1.3 工作目录确认**
- [ ] CLI专属工作目录已创建
- [ ] 不侵犯其他CLI的目录
- [ ] 文件所有权已明确

---

## 🔧 实施方案

### **立即行动（今天）**

#### **1. 创建文件所有权映射**

```bash
cd /opt/claude/mystocks_spec

cat > .FILE_OWNERSHIP << 'EOF'
# Git Worktree文件所有权映射
# 维护者：Main CLI
# 更新频率：每次分配新任务时更新

# 格式：目录/文件模式: 拥有者CLI | 说明

# ========== 主仓库（主CLI）==========
src/                               main      | 核心业务逻辑
config/                            main      | 配置文件
scripts/dev/                       main      | 开发工具
pyproject.toml                     main      | 项目配置
.pre-commit-config.yaml            main      | Pre-commit配置（所有CLI继承）
requirements.txt                   main      | Python依赖

# ========== CLI-1: Phase 3前端K线图 ==========
web/frontend/src/components/Charts/  cli-1     | K线图组件
web/frontend/src/api/klineApi.ts     cli-1     | K线图API
web/frontend/src/api/indicatorApi.ts cli-1     | 技术指标API
web/frontend/src/api/astockApi.ts    cli-1     | A股规则API
web/frontend/src/utils/chartRenderer.ts cli-1     | 图表渲染
web/frontend/src/utils/indicatorRenderer.ts cli-1 | 指标绘制

# ========== CLI-2: API契约标准化 ==========
docs/api/contracts/                  cli-2     | API契约文档
web/backend/app/schemas/            cli-2     | 数据模式定义
web/backend/openapi/                 cli-2     | OpenAPI规范

# ========== CLI-5: GPU监控仪表板 ==========
src/gpu/                            cli-5     | GPU相关代码
src/gpu_monitoring/                  cli-5     | GPU监控服务
scripts/start_gpu_monitoring.sh      cli-5     | GPU监控脚本
docs/guides/GPU_MONITORING*          cli-5     | GPU监控文档

# ========== CLI-6: 质量保证 ==========
tests/                              cli-6     | 测试文件
scripts/maintenance/                cli-6     | 质量保证脚本
docs/guides/CODE_QUALITY*            cli-6     | 质量标准文档
docs/guides/TESTING*                 cli-6     | 测试指南文档

# ========== 共享文件（协调修改）==========
README.md                           main+clis | 主CLI维护，CLI可建议
CLAUDE.md                           main      | 主CLI维护
CHANGELOG.md                        main      | 主CLI维护

# ========== 规则说明 ==========
# 1. 拥有者CLI可以修改其拥有的文件
# 2. 其他CLI只读这些文件，修改需要协调
# 3. 共享文件需要主CLI协调修改
# 4. 未知所有权的文件默认属于主CLI
EOF

git add .FILE_OWNERSHIP
git commit -m "chore: add file ownership mapping for all CLIs

- Define clear file ownership for each CLI
- Prevent modification conflicts
- Establish coordination mechanism
- Document shared file usage rules

This solves the conflict prevention problem where multiple
CLIs modify the same files simultaneously.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

#### **2. 更新主CLI工作规范**

在`MAIN_CLI_WORKFLOW_STANDARDS.md`中添加新的章节：

**在"Phase 0: 准备阶段工作清单"中添加0.5节**：
```markdown
### 0.5 文件所有权和职责范围确认

**必须完成**：
- [ ] 创建.FILE_OWNERSHIP映射文件
- [ ] 明确每个CLI的职责范围
- [ ] 检查潜在的文件冲突
- [ ] 建立协调机制
```

**在"常见问题与解决方案"中添加问题7**：
```markdown
### 问题7: 多CLI修改同一文件产生冲突

**症状**: Git合并时产生"Both modified"冲突

**根因**: 多个CLI同时修改同一文件

**预防**:
1. 创建文件所有权映射(.FILE_OWNERSHIP)
2. 明确每个CLI的职责范围
3. 使用目录结构物理隔离

**解决**:
1. 查看.FILE_OWNERSHIP确认文件拥有者
2. 与拥有者CLI协调修改
3. 或通过主CLI申请修改
```

#### **3. 创建冲突检测脚本**

```bash
cat > /opt/claude/mystocks_spec/scripts/maintenance/check_file_conflicts.sh << 'EOF'
#!/bin/bash
# 检查Git Worktree文件冲突
# 使用方法：bash scripts/maintenance/check_file_conflicts.sh

echo "=== Git Worktree文件冲突检测 ==="
echo ""

OWNERSHIP_FILE="/opt/claude/mystocks_spec/.FILE_OWNERSHIP"
CONFLICTS_FOUND=0

for cli_path in /opt/claude/mystocks_phase*/; do
  if [ -d "$cli_path" ]; then
    cli_name=$(basename "$cli_path")
    echo "## 检查 $cli_name"

    cd "$cli_path"

    # 检查已修改但未提交的文件
    git diff --name-only | while read file; do
      # 跳过已删除的文件
      [ ! -f "$file" ] && continue

      # 检查文件所有权
      owner=$(grep "^$file:" "$OWNERSHIP_FILE" 2>/dev/null | cut -d: -f2 | cut -d: -f1)

      if [ -z "$owner" ]; then
        # 未知所有权，默认归主CLI
        owner="main"
      fi

      # 如果文件不属于当前CLI
      if [ "$owner" != "$cli_name" ] && [ "$owner" != "main+clis" ]; then
        echo "  ⚠️  潜在冲突: $file"
        echo "     拥有者: $owner"
        echo "     修改者: $cli_name"
        CONFLICTS_FOUND=$((CONFLICTS_FOUND + 1))
      fi
    done

    echo ""
  fi
done

if [ $CONFLICTS_FOUND -eq 0 ]; then
  echo "✅ 未发现文件冲突"
  exit 0
else
  echo "🚨 发现 $CONFLICTS_FOUND 个潜在文件冲突"
  echo ""
  echo "建议："
  echo "1. 查看文件所有权映射: cat /opt/claude/mystocks_spec/.FILE_OWNERSHIP"
  echo "2. 与文件拥有者CLI协调"
  echo "3. 或通过主CLI申请修改权限"
  exit 1
fi
EOF

chmod +x /opt/claude/mystocks_spec/scripts/maintenance/check_file_conflicts.sh
```

#### **4. 更新所有CLI的README**

在每个Worker CLI的README.md中添加：

```markdown
## ⚠️ 文件修改限制

**重要**：本worktree中的某些文件属于其他CLI或主仓库，**不可随意修改**。

**查看文件所有权**：
```bash
cat /opt/claude/mystocks_spec/.FILE_OWNERSHIP
```

**本CLI可修改的文件**：
- 列出本CLI拥有的文件路径

**需要修改其他CLI的文件时**：
1. 向主CLI提交申请
2. 说明修改原因和内容
3. 等待协调和批准
4. 由主CLI或文件拥有者执行修改

**违反规则的后果**：
- Git合并冲突
- 工作重复
- 版本控制混乱
```

---

## 📋 任务分配前检查清单（更新版）

### **Phase 0: 准备阶段（增强版）**

- [ ] **0.1 任务分配文档已创建并审查通过**
- [ ] **0.2 工作流程指南已创建**
- [ ] **0.3 监控机制文档已创建**
- [ ] **0.4 实施方案文档已创建**
- [ ] **0.5 文件所有权映射已创建** ⚠️ **新增**
- [ ] **0.6 职责范围已明确** ⚠️ **新增**
- [ ] **0.7 潜在冲突已检查** ⚠️ **新增**
- [ ] **0.8 协调机制已建立** ⚠️ **新增**

### **Phase 1: Git Worktree创建（增强版）**

- [ ] 1.1 创建Worktree
- [ ] 1.2 初始化README
- [ ] **1.3 文件所有权已确认** ⚠️ **新增**
- [ ] 1.4 修复Hook脚本权限
- [ ] 1.5 验证Git远程仓库名称
- [ ] 1.6 验证Worktree完整性
- [ ] **1.7 Pre-commit配置已说明** ⚠️ **新增**
- [ ] 1.8 首次提交已完成

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
