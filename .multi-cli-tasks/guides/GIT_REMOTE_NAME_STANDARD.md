# Git 远程仓库名称标准化规范

**文档版本**: v3.1
**创建日期**: 2025-12-29
**问题发现**: Worker CLI多次遇到 `git push origin` 失败
**最后更新**: 2026-03-04
**维护者**: Main CLI

---

## 📋 问题描述

### **症状**

Worker CLI执行文档中的命令时遇到错误：

```bash
$ git push origin phase3-frontend-optimization
fatal: 'origin' does not appear to be a git remote
```

### **根本原因**

主仓库和所有Git worktree的远程仓库名称为 `mystocks` 而不是Git标准的 `origin`。

```bash
$ git remote -v
mystocks    https://github.com/chengjon/mystocks.git (fetch)
mystocks    https://github.com/chengjon/mystocks.git (push)
```

### **影响范围**

- ❌ 所有文档中的 `git push origin` 命令失败
- ❌ 所有文档中的 `git pull origin` 命令失败
- ❌ Worker CLI无法按文档推送代码
- ❌ 偏离Git标准命名约定

---

## v3.1 治理增补：远程与分支基线联动

远程命名统一为 `origin` 后，v3.1 要求进一步统一分支门禁：

- `origin/dev` 是所有 CLI 功能分支的唯一来源基线
- Worker PR 统一 `--base dev`，禁止以 `origin/main` 为目标
- 主 CLI 仅在 `dev` 验证通过后执行 `dev -> main` 合并

**推荐命令**:

```bash
# Worker 开工前：同步 dev 基线
git fetch origin
git switch dev
git pull --ff-only origin dev

# Worker 提交 PR（必须指向 dev）
gh pr create --base dev --head feat/<module>-<cli> \
  --title "feat(<module>): short description" \
  --body "AI CLI: <CLI_NAME> | 生成模块: <MODULE>"
```

---

## ✅ 解决方案

### **方案A: 统一改为 `origin`** ✅ 已采用

**理由**:
1. `origin` 是Git标准命名
2. 所有Git教程、工具、CI/CD系统默认使用 `origin`
3. 避免每次都要记住自定义名称
4. 符合行业最佳实践

### **执行步骤**

```bash
# 1. 修复主仓库
cd /opt/claude/mystocks_spec
git remote rename mystocks origin

# 2. 验证修复
git remote -v
# 预期输出:
# origin    https://github.com/chengjon/mystocks.git (fetch)
# origin    https://github.com/chengjon/mystocks.git (push)

# 3. 所有worktree自动继承
cd /opt/claude/mystocks_phase3_frontend
git remote -v
# 预期输出: origin (已自动继承)
```

### **验证结果**

- ✅ 主仓库: `mystocks` → `origin`
- ✅ CLI-1: `mystocks` → `origin` (自动继承)
- ✅ CLI-2: `mystocks` → `origin` (自动继承)
- ✅ CLI-5: `mystocks` → `origin` (自动继承)
- ✅ CLI-6: `mystocks` → `origin` (自动继承)

### **Git提交**

```bash
git commit -m "fix: standardize remote name from 'mystocks' to 'origin'

- Rename remote from 'mystocks' to 'origin' in main repository
- All worktrees automatically inherit the change
- This fixes the issue where all documentation used 'origin'
  but the actual remote name was 'mystocks'
- Worker CLIs can now use 'git push origin' as documented

Impact:
- ✅ All git push/pull commands now work as documented
- ✅ Standard Git naming convention applied
- ✅ No more 'origin does not exist' errors"
```

**实际提交**: `0a65718` (2025-12-29 18:29)

---

## 🚫 方案B: 更新所有文档使用 `mystocks` (不推荐)

### **为什么不推荐**

1. ❌ 违反Git标准命名约定
2. ❌ 所有工具和教程默认使用 `origin`
3. ❌ 增加认知负担（需要记住特殊命名）
4. ❌ 不利于团队协作和知识传承

### **如果坚持使用** (不推荐):

需要更新以下所有文件中的 `origin` 为 `mystocks`:
- `WORKER_CLI_GUIDE.md` (50+处)
- 所有CLI的TASK.md (30+处)
- `MAIN_CLI_WORKFLOW.md` (20+处)
- 其他Git相关文档

---

## 📚 最佳实践

### **1. 初始化新仓库时使用标准命名**

```bash
# ✅ 正确: 使用默认的origin
git clone https://github.com/user/repo.git
# 远程自动命名为origin

# ❌ 错误: 自定义远程名称
git clone https://github.com/user/repo.git myrepo
cd myrepo
git remote rename origin mystocks  # 不必要！
```

### **2. 创建Git Worktree时自动继承**

```bash
# 创建worktree
git worktree add /opt/claude/mystocks_phase3_frontend -b phase3-frontend-optimization

# worktree自动继承主仓库的远程配置
cd /opt/claude/mystocks_phase3_frontend
git remote -v
# 显示: origin (自动继承，无需手动配置)
```

### **3. 文档中使用标准命令**

```bash
# ✅ 正确: 文档中使用origin
git push origin <branch-name>
git pull origin <branch-name>
git clone <url>

# ❌ 错误: 文档中使用自定义名称
git push mystocks <branch-name>
git pull mystocks <branch-name>
```

---

## 🔍 检查清单

### **项目初始化时**

- [ ] 确认远程仓库名称为 `origin`
- [ ] 文档中所有Git命令使用 `origin`
- [ ] Worktree创建后验证远程配置

### **日常开发时**

- [ ] 推送代码前确认远程名称: `git remote -v`
- [ ] 遇到 `origin does not exist` 错误时检查远程配置
- [ ] 新增文档时使用标准的 `origin` 命令

### **主CLI创建Worktree时**

- [ ] 在创建worktree前确认主仓库使用 `origin`
  ```bash
  git remote -v | grep origin || git remote rename <当前名称> origin
  ```

- [ ] 在worktree创建后验证远程配置已自动继承
  ```bash
  cd /opt/claude/mystocks_phase3_frontend
  git remote -v | grep origin
  ```

- [ ] 在Worker CLI的TASK.md中使用 `origin` 示例

---

## 🛠️ 故障排查

### **问题1: `git push origin` 失败**

**症状**:
```bash
$ git push origin feature-branch
fatal: 'origin' does not appear to be a git remote
```

**诊断**:
```bash
$ git remote -v
mystocks    https://github.com/user/repo.git (fetch)
mystocks    https://github.com/user/repo.git (push)
```

**解决**:
```bash
# 方案1: 重命名为origin (推荐)
git remote rename mystocks origin

# 方案2: 临时使用mystocks (不推荐)
git push mystocks feature-branch
```

### **问题2: Worktree远程配置不正确**

**症状**:
```bash
$ cd /opt/claude/mystocks_phase3_frontend
$ git push origin feature-branch
fatal: 'origin' does not appear to be a git remote
```

**原因**: 主仓库的远程名称不是 `origin`

**解决**:
```bash
# 修复主仓库的远程名称
cd /opt/claude/mystocks_spec
git remote rename mystocks origin

# worktree会自动继承，无需单独修复
```

### **问题3: 文档与实际不符**

**症状**: 文档说使用 `git push origin`，但实际需要 `git push mystocks`

**解决**:
1. 修复远程名称为 `origin` (推荐)
2. 或更新所有文档为 `mystocks` (不推荐，工作量大)

### **问题4: CI/CD系统找不到 `origin`**

**症状**: GitHub Actions或其他CI系统报告 `origin does not exist`

**解决**:
```bash
# 修复主仓库的远程名称
git remote rename mystocks origin

# 推送到远程
git push origin main

# CI/CD系统将使用 origin
```

---

## 🔗 相关文档

### 核心文档
- [Git Worktree命令手册](./GIT_WORKTREE_MAIN_CLI_MANUAL.md) - Git worktree命令参考（包含 `git remote`）
- [主CLI工作规范](./MAIN_CLI_WORKFLOW.md) - Pre-flight检查和Worktree创建流程
- [Worker CLI工作流程](./WORKER_CLI_GUIDE.md) - Worker CLI如何使用Git命令
- [协作冲突预防](./CONFLICT_PREVENTION.md) - 文件所有权与任务文档规范

### 工作流程文档
- [协作冲突预防](./CONFLICT_PREVENTION.md) - 避免协作冲突
- [任务文档模板](./templates/TASK_TEMPLATE.md) - TASK.md和TASK-REPORT.md使用方式

---

## 📝 变更历史

- **v1.0** (2025-12-29): 初始版本
  - 记录远程名称问题
  - 提供标准解决方案
  - 添加最佳实践和故障排查

- **v2.0** (2025-12-30): 主要更新
  - 更新文档版本号为v2.0
  - 添加"相关文档"章节
  - 强化链接到其他核心文档
  - 优化文档结构

- **v3.1** (2026-03-04): 治理增补
  - 增加 dev/main 分支门禁与远程使用联动规则
  - 补充 Worker PR 目标分支与命令模板

---

## ✍️ 维护者

**创建者**: Main CLI
**最后更新**: 2026-03-04
**维护频率**: 每次创建新worktree时检查

**反馈**: 如果遇到远程名称相关问题，请更新本文档。

---

**核心原则**: 始终使用Git标准的 `origin` 命名，避免不必要的自定义，简化开发和协作。
