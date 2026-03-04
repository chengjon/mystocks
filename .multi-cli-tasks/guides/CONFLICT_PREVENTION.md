# Git Worktree协作冲突预防规范

**文档版本**: v3.1
**创建日期**: 2025-12-29
**问题来源**: Worker CLI反馈的实际问题
**最后更新**: 2026-03-04
**维护者**: Main CLI

---

## 📋 文档目的

本文档解决关键的Git Worktree协作问题（含 v3.1 新增治理冲突源）：

1. **Pre-commit配置冲突**：主CLI和Worker CLI同时修改pre-commit配置导致合并冲突
2. **任务分配冲突**：多个CLI修改同一文件导致协作冲突
3. **主CLI忘记同步已完成worktree**：主CLI在开始新工作前忘记合并已完成的worktree
4. **任务文档方式**：使用README.md vs TASK.md + TASK-REPORT.md导致冲突
5. **治理门禁冲突（v3.1）**：PR 目标错误（指向 main）、提交信息不规范、缺失验证证据

**核心原则**:
- ✅ **明确所有权**：每个文件有明确的拥有者
- ✅ **职责分离**：每个CLI有清晰的职责范围
- ✅ **配置集中管理**：pre-commit配置在主仓库统一管理
- ✅ **文件组织标准化**：通过目录结构避免冲突
- ✅ **任务文档分离**：TASK.md（任务说明）→ TASK-REPORT.md（进度报告）→ TASK-*-REPORT.md（完成报告）
- ✅ **治理门禁前置**：所有 Worker 变更统一 `base=dev`，`main` 仅接受 `dev -> main` 合并

---

## 🚨 v3.1 新增问题：治理门禁冲突（PR / Commit / Verification）

### **问题描述**

新增多 CLI 协作后，常见冲突已从“文件改同一处”扩展到“流程不一致”：

1. Worker 直接提交 PR 到 `main`，导致主干流程被绕过  
2. 提交信息不符合 `type(scope): short description`，审计困难  
3. PR / TASK-REPORT 缺失验证证据，无法判断质量门禁是否满足

### **解决方案（强制）**

- **PR 基线统一**: 所有 Worker PR 必须 `--base dev`。
- **提交规范统一**: 提交信息必须符合 `type(scope): short description`。
- **证据链统一**: 在 `TASK-REPORT.md` 与 PR 描述中记录验证命令与结果摘要。

**推荐检查命令**:

```bash
# 检查分支与提交
git branch --show-current
git log --oneline -n 10

# 检查 dev/main 差异窗口
git log --oneline main..dev
```

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

**角色边界提醒**:
- **Main CLI**: 维护 .pre-commit-config.yaml、.FILE_OWNERSHIP、全局流程与冲突协调
- **Worker CLI**: 仅在自己的worktree内执行任务与提交，不跨所有权修改文件

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

## 🚨 问题3：主CLI忘记同步已完成worktree (2025-12-30实战案例)

### **问题描述**

**场景**：
```
时间线：
2025-12-29 14:00 - CLI-2完成API契约管理平台，提交到phase6-api-contract-standardization分支
2025-12-29 18:00 - CLI-3完成K线图可视化，提交到cli3-kline-chart分支
2025-12-29 20:00 - CLI-5完成GPU监控，提交到cli5-gpu-monitoring分支
2025-12-30 00:00 - 主CLI开始API&Web集成工作，直接尝试使用契约管理工具
2025-12-30 00:05 - ❌ 失败：契约管理工具目录不存在
2025-12-30 00:10 - ⚠️  发现问题：主CLI忘记先pull已完成的worktree代码
```

**根本原因**:
- 主CLI在开始新工作前，**忘记**系统性检查并合并所有worker CLI的已完成工作
- 主CLI工作流程缺少明确的"Pre-flight检查清单"
- 导致主CLI尝试使用不存在的工具/代码，浪费时间创建临时解决方案

### **解决方案**

#### **方案A：主CLI Pre-flight检查清单** ✅ **强制执行**

**原则**: 主CLI开始任何新工作前，必须强制执行以下检查清单

**在主CLI目录下工作前必须执行**：
```bash
#!/bin/bash
# 主CLI Pre-flight 检查清单
# 使用场景：主CLI准备开始新工作，或在worktree删除前

echo "🔍 主CLI Pre-flight 检查清单"
echo "================================"

# 1. 检查所有worktree状态
echo "1️⃣  检查所有worktree状态..."
git worktree list

# 2. 检查远程分支是否有新提交
echo "2️⃣  检查远程分支..."
git fetch --all
git log HEAD..origin/main --oneline

# 3. 如果有worktree，检查它们的分支状态
echo "3️⃣  检查worktree分支状态..."
for worktree in $(git worktree list | grep -v '\[main\]' | awk '{print $1}'); do
    branch=$(cd $worktree && git branch --show-current)
    echo "   - $worktree ($branch)"
    (cd $worktree && git status --short)
done

# 4. 询问用户操作
echo ""
echo "⚠️  发现未处理的worktree或远程更新，请选择："
echo "1. 合并所有已完成分支到main，然后删除worktree"
echo "2. 仅拉取远程更新，不处理worktree"
echo "3. 取消，手动处理"
read -p "选择 [1/2/3]: " choice

case $choice in
    1)
        echo "🔄 开始合并已完成分支..."
        # 实现见 MAIN_CLI_WORKFLOW.md
        ;;
    2)
        echo "📥 仅拉取远程更新..."
        git pull origin main
        ;;
    3)
        echo "❌ 取消操作"
        exit 1
        ;;
esac
```

**主CLI工作流程更新**（添加到开始任何工作前）：
```markdown
## Step 0: Pre-flight检查（强制执行）

在开始任何新工作前，必须执行：

1. ✅ 检查所有worktree状态
   ```bash
   git worktree list
   ```

2. ✅ 检查远程分支新提交
   ```bash
   git fetch --all
   git log HEAD..origin/main --oneline
   ```

3. ✅ 如果有已完成的worktree：
   - 确认worker CLI已提交并推送
   - 合并分支到main
   - 删除worktree
   - 然后才开始新工作

4. ✅ 如果仅有远程更新：
   - 拉取更新
   - 解决冲突
   - 然后才开始新工作
```

**为什么这很重要**:
- ❌ **不执行** → 主CLI使用过时代码/工具，浪费时间，可能引入bug
- ✅ **执行** → 主CLI始终使用最新代码，避免重复劳动，确保协作一致性

---

## 🚨 问题4：任务文档方式 (2025-12-30实战案例)

### **问题描述**

**旧方式问题**：
```
时间线：
2025-12-29 10:00 - CLI-1创建任务，写入README.md（CLI-1 Phase 3 K线图任务）
2025-12-29 14:00 - CLI-2创建任务，写入README.md（CLI-2 API契约任务）
2025-12-30 00:00 - 主CLI尝试合并phase6-api-contract-standardization分支
2025-12-30 00:05 - ❌ 冲突：README.md Both modified
2025-12-30 00:10 - ⚠️  根本原因：多个CLI使用同一文件（README.md）记录任务和进度
```

**根本原因**:
- README.md是主仓库的共享文档
- 多个CLI同时修改README.md记录各自的任务和进度
- Git无法自动合并同一文件的多个版本
- 合并时必然产生冲突

### **解决方案**

#### **方案A：使用TASK.md + TASK-REPORT.md方式** ✅ **强烈推荐**

**原则**:
- ✅ 每个worktree有独立的TASK.md（任务说明）
- ✅ 每个worktree有独立的TASK-REPORT.md（进度报告）
- ✅ 多阶段任务用 TASK-1.md, TASK-2.md（任务）与 TASK-1-REPORT.md, TASK-2-REPORT.md（完成报告）
- ✅ README.md保留给项目级介绍，不放入CLI特定任务

**任务文档结构**：

| 文件类型 | 命名规范 | 用途 | 拥有者 | 合并时影响 |
|---------|---------|------|--------|-----------|
| 任务说明 | TASK.md, TASK-1.md, TASK-2.md | 主CLI生成任务文档 | 主CLI | 无冲突（worktree内） |
| 进度报告 | TASK-REPORT.md | Worker CLI更新进度 | Worker CLI | 无冲突（worktree内） |
| 完成报告 | TASK-*-REPORT.md | Worker CLI汇报完成 | Worker CLI | 无冲突（worktree内） |

**使用流程**：

**1. 主CLI创建任务**：
```bash
cd /opt/claude/mystocks_cli_x
cat > TASK.md << 'EOF'
# CLI-X 任务文档

**Worker CLI**: CLI-X (描述)
**Branch**: branch-name
**Worktree**: /path/to/worktree/
**Phase**: 描述阶段
**预计工作量**: X天

---

## 🎯 核心职责

描述这个CLI的核心职责和目标

---

## 📋 任务清单

### 阶段1: XXX (T1.1-T1.3, X天)

#### T1.1: 任务标题 (X天)

**目标**: 描述任务目标

**验收标准**:
- [ ] 标准1
- [ ] 标准2

**预计完成**: YYYY-MM-DD
EOF
```

**2. Worker CLI创建进度报告**：
```bash
cd /opt/claude/mystocks_cli_x
cat > TASK-REPORT.md << 'EOF'
# CLI-X 任务进度报告

**Worker CLI**: CLI-X
**任务文档**: TASK.md
**当前阶段**: T+0h
**报告时间**: YYYY-MM-DD HH:MM

---

## ✅ 已完成

- [ ] 任务1: 描述 - 完成时间: YYYY-MM-DD HH:MM

---

## 🔄 进行中

- [ ] 任务2: 描述 - 当前进度: 0%

---

## 🚧 阻塞问题

无

---

## 📈 进度统计

- **已完成任务**: 0/Y (0%)
- **预计完成时间**: YYYY-MM-DD
EOF
```

**3. Worker CLI生成完成报告**：
```bash
cd /opt/claude/mystocks_cli_x
cat > TASK-1-REPORT.md << 'EOF'
# 任务完成报告 - 第一阶段

**Worker CLI**: CLI-X
**任务文档**: TASK-1.md
**报告文档**: TASK-1-REPORT.md
**完成时间**: YYYY-MM-DD HH:MM

---

## ✅ 验收标准

- [x] 标准1: 描述完成情况
- [x] 标准2: 描述完成情况

---

## 📦 交付物

- 代码: X个文件，Y行代码
- 测试: X个测试用例，通过率Y%

---

## ✅ 等待主CLI验收

请主CLI验收第一阶段交付物并合并到main分支
EOF
```

**4. 主CLI合并时**：
```bash
# 主CLI合并分支时，无README.md冲突
git merge cli-x-branch

# ✅ TASK.md在worktree目录，不影响主仓库
# ✅ TASK-REPORT.md在worktree目录，不影响主仓库
# ✅ 主仓库的README.md保持干净，仅包含项目级介绍
```

**文件组织对比**：

| 方式 | 任务说明 | 进度报告 | 合并冲突 | 任务历史 | 推荐 |
|------|---------|---------|----------|----------|------|
| ❌ 旧方式 | README.md | README.md | 必然冲突 | 难以保留 | ❌ 不推荐 |
| ✅ 新方式 | TASK.md | TASK-REPORT.md | 无冲突 | TASK-1.md, TASK-2.md... | ✅ 强烈推荐 |

**实施检查清单**：
- [ ] 更新主CLI工作流程文档，使用TASK.md方式
- [ ] 更新Worker CLI工作流程，使用TASK-REPORT.md方式
- [ ] 创建TASK.md模板
- [ ] 在worktree创建时自动生成TASK.md
- [ ] 合并分支时检查无README.md冲突

**相关文档**：
- [任务文档模板](./templates/TASK_TEMPLATE.md) - 详细的TASK.md和TASK-REPORT.md模板
- [主CLI工作规范](./MAIN_CLI_WORKFLOW.md) - 主CLI任务分配方法
- [Worker CLI工作流程](./WORKER_CLI_GUIDE.md) - Worker CLI如何使用这些模板

---

## 🚨 问题5：依赖同步问题 (JavaScript/TypeScript)

### **问题描述**

**场景**：
```
在多个worktree中工作时，node_modules可能会不同步：
- Worktree-1安装了依赖A@1.0.0
- Worktree-2安装了依赖A@1.2.0
- 导致版本冲突，难以管理
```

**根本原因**:
- 每个worktree独立的node_modules
- 依赖版本不一致
- 磁盘空间浪费

### **解决方案**

#### **方案A：使用符号链接共享node_modules** ✅ **强烈推荐**

**实施步骤**：

```bash
# 1. 创建共享的node_modules目录
mkdir -p ~/shared/node_modules

# 2. 删除现有worktree的node_modules并链接到共享目录
cd ~/projects/project-worktree-1
rm -rf node_modules
ln -s ~/shared/node_modules ./node_modules

# 对其他worktree执行相同操作
cd ~/projects/project-worktree-2
rm -rf node_modules
ln -s ~/shared/node_modules ./node_modules

# 3. 在一个位置安装依赖
cd ~/shared
npm install
```

**优势**:
- ✅ 所有worktree共享相同的依赖版本
- ✅ 节省磁盘空间
- ✅ 避免版本冲突
- ✅ 依赖更新更简单

**注意事项**:
- ⚠️ 确保所有worktree的package.json兼容
- ⚠️ 安装新依赖时在共享目录执行
- ⚠️ 删除worktree前先取消链接

**相关文档**:
- [主CLI工作规范](./MAIN_CLI_WORKFLOW.md) - Pre-flight检查
- [文件所有权说明](./MAIN_CLI_WORKFLOW.md#phase-05-文件所有权和职责范围确认)

---

## 🚨 问题6：物理路径污染冲突 (Zero-Root-Config)

### **问题描述**
不同 CLI 在各自 Worktree 开发时，习惯性地在项目根目录创建工具配置文件（如 `playwright.config.ts`, `vitest.config.ts`），导致合并后根目录出现大量碎片文件及冲突。

**解决方案：零根目录配置原则 (Zero-Root-Config)** ✅
- ✅ **配置收敛**: 严禁在根目录新增工具配置。所有配置文件必须存放在 `config/` 下的对应子目录（如 `config/playwright/`）。
- ✅ **逻辑下沉**: 业务逻辑禁止在根目录 `.py` 文件中编写，必须放入 `src/`。根目录文件仅作为 Re-export 外壳。
- ✅ **显式指定**: 执行工具时必须显式指定路径，如 `npx playwright test -c config/playwright/playwright.config.ts`。

---

## 🚨 问题7：依赖膨胀与同步 (Node.js/Python)

### **问题描述**
每个 Worktree 独立安装 `node_modules` 或 `venv` 导致磁盘空间迅速耗尽且版本不一致。

**解决方案：共享依赖策略** ✅
- **Node.js**: 使用 `pnpm` 软链接机制或手动创建共享 `node_modules` 并使用 `ln -s` 链接到各 Worktree。
- **Python**: 所有 Worktree 共享同一个虚拟环境（VENV），除非任务涉及依赖项本身的大幅变更。

---

## 🎯 总结与执行

### **执行优先级**
1. ✅ **主 CLI Pre-flight 检查**: 开始任何集成工作前必须执行。
2. ✅ **Zero-Root-Config**: 强制将配置收敛至 `config/` 目录。
3. ✅ **TASK.md 体系**: 放弃 README 记录任务，改用独立的 TASK 报告文件。

---

## 🔗 相关文档
- [Git Worktree 命令手册 (v3.1)](./GIT_WORKTREE_MAIN_CLI_MANUAL.md) - 最新命令与修复技巧
- [多 CLI 协作管理手册](../README.md) - 角色与职责定义

---

**文档版本**: v3.1
**创建日期**: 2025-12-29
**最后更新**: 2026-03-04
**维护者**: Main CLI
**更新频率**: 持续更新

**核心原则**: 明确所有权 + 职责分离 + 协调机制 + Pre-flight检查 + 独立任务文档 + 依赖同步 + 零配置污染 = 零冲突协作
