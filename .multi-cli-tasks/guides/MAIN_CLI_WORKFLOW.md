# Main CLI 工作规范与最佳实践

**文档版本**: v3.2
**创建日期**: 2025-12-29
**适用范围**: 所有使用Git Worktree进行多CLI并行开发的项目
**最后更新**: 2026-03-05
**v3.2更新说明**: main 角色收敛为“协调 + 验收”，所有功能开发改为 worktree/dev-*，PR 统一合并到 main 并通过三道门禁。
**维护者**: Main CLI (Manager)

---

## 📋 文档目的

本文档总结了在MyStocks项目Phase 3-6多CLI并行开发实施过程中积累的经验教训，制定了标准化的工作流程和最佳实践规范，供主CLI在未来项目中参考和遵循。

**核心价值**:
- ✅ 避免重复踩坑，提高启动效率
- ✅ 标准化工作流程，降低管理成本
- ✅ 确保所有CLI具备完整的开发和提交能力
- ✅ 建立可重复、可验证的并行开发框架

## v3.2 治理增补：Main CLI 合并门禁

本节用于落实当前主线治理：`main` 只做协调与验收，不直接做功能开发。

- **角色边界**: `main` 禁止直接承载功能开发提交。
- **分支入口统一**: 所有 Worker CLI 功能开发统一在 `worktree/dev-*` 分支进行。
- **PR 目标统一**: 主 CLI 审核时必须确认 PR `base=main`，若不是 `main` 则要求重提。
- **提交规范统一**: 检查提交信息格式 `type(scope): short description`，禁止 `update code` 等无意义描述。
- **PR 证据强制项**: 每个 PR 必须包含“变更范围 + 验证命令与结果 + 风险/回滚说明”。
- **三道门禁强制项**: 质量门（TS/Python/tests）、安全门（secrets/audit/SAST）、审查门（code review）必须全部通过。
- **Upstream 强制校验**: `main` 与活跃 `dev-*` 分支必须绑定对应 `origin/*` 上游，`(no-upstream)` 视为阻塞。

**主 CLI 快速核验命令**:
```bash
# 1) 检查当前分支（应在 main 的管理位）
git branch --show-current

# 2) 检查最近提交信息是否符合规范
git log --oneline -n 10

# 3) 抽查活跃 dev-* 分支相对 main 的差异窗口
git for-each-ref --format='%(refname:short)' refs/heads/dev-* | while read -r b; do
  echo "=== $b ==="
  git log --oneline "main..$b" | head -20
done

# 4) 抽查 upstream 绑定状态
git rev-parse --abbrev-ref --symbolic-full-name main@{upstream}
git for-each-ref --format='%(refname:short)' refs/heads/dev-* | while read -r b; do
  git rev-parse --abbrev-ref --symbolic-full-name "${b}@{upstream}"
done
```

---

## 🕹️ 运营中心：`/.multi-cli-tasks/` 指挥舱

本项目采用**集中式运营**模式。`/.multi-cli-tasks/` 是主 CLI 管理并行开发生命周期的唯一物理入口。

### 1. 目录结构规范

```text
/.multi-cli-tasks/
├── guides/                        # [立法] 核心规范与模板库
│   ├── MAIN_CLI_WORKFLOW.md       # 主CLI工作圣经
│   ├── WORKER_CLI_GUIDE.md        # Worker执行手册
│   └── templates/                 # 标准化模板
│
├── mystocks_phase3_frontend/      # [活跃单元] 对应物理 Worktree
│   ├── TASK.md                    # —— 任务书 (同步源)
│   ├── TASK-REPORT.md             # —— 进度报告 (定期同步/收割)
│   └── FEEDBACK_LOG.md            # —— 反馈记录
│
├── mystocks_phase6_gpu/           # [活跃单元] 另一个并行任务...
│
└── PHASE_3_SUMMARY.md             # [总结] 阶段性聚合报告
```

### 2. 标准操作流程 (SOP)

#### 阶段 A: 任务分发 (Dispatch)
1.  **创建管理单元**: `mkdir -p /.multi-cli-tasks/<worktree_name>/`
2.  **准备载荷**: 从 `guides/templates/TASK_TEMPLATE.md` 复制到该目录，命名为 `TASK.md` 并填充内容。
3.  **物理分发**: 创建 Worktree 后，将 `TASK.md` 复制到 Worktree 根目录。

#### 阶段 B: 监控与反馈 (Monitor & Feedback)
1.  **状态同步**: 定期将 Worktree 中的 `TASK-REPORT.md` 复制回 `/.multi-cli-tasks/<worktree_name>/` 目录进行查看。
2.  **反馈记录**: 所有的沟通记录、协调结果，记录在同目录下的 `FEEDBACK_LOG.md` 中，而不是散落在聊天记录里。

#### 阶段 C: 收割与结项 (Harvest & Archive)
1.  **终极收割**: 在删除 Worktree 前，执行最后一次同步，确保 `/.multi-cli-tasks/<worktree_name>/` 拥有最新的全套报告。
2.  **物理销毁**: 按照 Phase 5 流程删除 Worktree。
3.  **历史留存**: `/.multi-cli-tasks/<worktree_name>/` 目录**不删除**，直接作为历史归档保留。

---

## 🎯 核心原则

### 1. **完整优先** (Completeness First)

在启动任何Worker CLI之前，必须确保其具备完整的工作能力：

- ✅ Git worktree已创建并初始化
- ✅ TASK.md包含完整任务清单和工作流程规范
- ✅ 所有hook脚本具有执行权限
- ✅ 监控系统已配置并可正常追踪进度
- ✅ 提交流程和验收标准已明确

**错误示例**: 只创建worktree和复制任务文档，忽略工作流程和hooks

### 2. **文档驱动** (Documentation Driven)

所有规范、流程、标准必须文档化，并放在显眼位置：

- ✅ 工作流程指南必须链接在TASK.md中
- ✅ Git提交规范必须包含具体示例
- ✅ 进度更新格式必须提供模板
- ✅ 完成标准必须明确可衡量

### 3. **非侵入式监控** (Non-Invasive Monitoring)

主CLI通过被动方式监控进度，不主动干预Worker CLI工作：

- ✅ 通过TASK-REPORT.md更新时间判断活跃状态
- ✅ 通过Git提交历史了解进展
- ✅ 通过自动化脚本定期检查
- ❌ 不直接修改Worker CLI的代码或文件

### 4. **标准化复用** (Standardized Reuse)

所有CLI共享相同的工作流程、文档格式、提交规范：

- ✅ 统一的CLI工作流程指南
- ✅ 统一的TASK.md章节结构
- ✅ 统一的Git提交消息格式
- ✅ 统一的进度更新模板

### 5. **物理布局治理** (Physical Layout Governance) (2026-02-08 新增)

确保代码库的物理布局保持长效整洁，防止多 Worktree 开发导致的根目录污染：

- ✅ **零根目录配置**: 强制要求所有工具配置移入 `config/`（如 `config/playwright/`）。
- ✅ **逻辑重定向**: 确保根目录 `.py` 文件仅作为 `src/` 的 Re-export 外壳。
- ✅ **共享依赖**: 为 Node.js 项目建立共享 `node_modules` 软链接，避免磁盘浪费和版本冲突。

---

## 🛡️ 角色哲学：掌舵人原则 (The Helmsman Philosophy)

**主 CLI 是掌舵人，不是水手。**

在 Worker CLI 处于活跃状态（Active）期间，主 CLI **严禁**执行以下操作：
1.  ❌ **直接修改业务代码**: 即使发现小 Bug，也应通过 Issue 或 TASK 更新通知 Worker 修复。
2.  ❌ **替 Worker 跑测试**: 测试是 Worker 交付前的义务。
3.  ❌ **并行开发功能**: 主 CLI 的算力应保留给监控、审查和架构决策。

**主 CLI 的唯一职责**:
- **监控 (Monitor)**: 观察 `TASK-REPORT.md` 的增量更新。
- **调度 (Dispatch)**: 在阶段节点更新 `TASK.md` 下发新指令。
- **响应 (Respond)**: 接收 Worker 的“无法解决”反馈，进行架构级修复或资源协调。

---

## 🚨 Step -1: Pre-flight检查清单 ⭐ **强制执行**

**重要性**: 🔴 **极高** - 主CLI在开始任何新工作前，必须强制执行此检查清单

**为什么这很重要**:
- ❌ **不执行** → 主CLI使用过时代码/工具，浪费时间，可能引入严重bug
- ✅ **执行** → 主CLI始终使用最新代码，避免重复劳动，确保协作一致性

**实战教训**: 2025-12-30主CLI尝试使用API契约管理工具时，忘记先pull CLI-2的已完成代码，导致工具目录不存在，浪费30分钟排查问题。

### 快速检查命令

在主CLI目录开始任何工作前，必须执行：

```bash
# 1. 确认在主CLI目录
pwd  # 应该显示 /opt/claude/mystocks_spec

# 2. 检查文件所有权映射
cat .FILE_OWNERSHIP | head -20

# 3. 检查所有worktree
git worktree list

# 3.1 [可选，一次性迁移] 若发现历史 in-repo worktree（.worktrees/），手动执行：
# bash scripts/worktree/migrate_worktrees_to_parallel.sh --target-root /opt/claude
# git worktree list

# 4. 检查远程新提交（统一使用 origin）
git fetch --all
git log HEAD..origin/main --oneline

# 5. 物理路径审计 (Zero-Root-Config)
#    检查是否有新增文件非法占用根目录
find . -maxdepth 1 -name "*.js" -o -name "*.ts" -o -name "*.json" | grep -v "package.json" | grep -v "tsconfig.json"

# 6. 如果有worktree或新提交，处理它们
#    （见下方的"合并已完成分支流程"）

# 7. 检查关键分支 upstream（main + 当前活跃 dev-*）
git rev-parse --abbrev-ref --symbolic-full-name main@{upstream}
git for-each-ref --format='%(refname:short)' refs/heads/dev-* | while read -r b; do
  git rev-parse --abbrev-ref --symbolic-full-name "${b}@{upstream}"
done
```

若出现 `(no-upstream)`，必须先修复：

```bash
branch="$(git branch --show-current)"
git push -u origin "$branch"
```

### 合并已完成分支流程

**当检查发现已完成worktree时执行**：

#### 解决任务文件冲突规范 (2026-02-08)
**问题**: `TASK.md` 和 `TASK-REPORT.md` 在多分支合并时几乎 100% 产生冲突。
**处理规则**:
1. **优先 Worker 状态**: 若冲突行涉及子任务完成情况，优先保留 `Worker 分支` 的最新状态。
2. **使用命令**: `git checkout --theirs TASK.md TASK-REPORT.md` (或反之，取决于合并方向)。
3. **手动同步**: 合并后，Main CLI 必须立刻根据 `TASK-REPORT.md` 的内容更新全局看板。
4. **彻底清理**: 删除合并过程中可能产生的 `.bak`, `.backup` 文件。

```bash
#!/bin/bash
# 对每个worktree执行：
for worktree in $(git worktree list | grep -v '\[main\]' | awk '{print $1}'); do
    branch=$(cd $worktree && git branch --show-current)

    # 1. 确认worker CLI已提交并推送
    (cd $worktree && git status --short)
    # 如果有未提交的更改，停止并要求先提交

    # 2. 拉取远程最新代码
    git fetch origin $branch

    # 3. 合并分支到main
    git merge origin/$branch --no-edit

    # 4. 如有冲突，解决冲突
    #    git status查看冲突文件
    #    手动解决后: git add . && git commit

    # 5. 推送到远程
    git push origin main

    # 6. 删除worktree
    git worktree remove $worktree

    # 7. 删除远程分支（可选）
    # git push origin --delete $branch
done
```

### 任务文档使用规则 ⭐ **重要**

**原则**:
- ✅ 使用独立的TASK.md任务文档（位于worktree根目录）
- ✅ 多阶段任务用TASK-1.md, TASK-2.md等递增命名
- ❌ **禁止**使用README.md记录CLI特定任务

**为什么**:
- README.md是主仓库的共享文档，多个CLI同时修改必然导致合并冲突
- TASK.md在worktree根目录，不合并到主仓库，避免冲突

**模板位置**: `docs/guides/.multi-cli-tasks/TASK_TEMPLATE.md`

**使用示例**:
```bash
# 1. 创建worktree时生成TASK.md
git worktree add -b cli-x-feature /opt/claude/mystocks_cli_x
cp docs/guides/.multi-cli-tasks/TASK_TEMPLATE.md /opt/claude/mystocks_cli_x/TASK.md

# 2. Worker CLI开始更新进度（TASK-REPORT.md）
cd /opt/claude/mystocks_cli_x
cat > TASK-REPORT.md << 'EOF'
# CLI-X 任务进度报告
...
EOF

# 3. 第一阶段完成，主CLI下发第二阶段任务
mv TASK.md TASK-1.md
cat > TASK-2.md << 'EOF'
# CLI-X 第二阶段任务
...
EOF

# 4. 继续后续阶段...
mv TASK-2.md TASK-2-completed.md
cat > TASK-3.md << 'EOF'
# CLI-X 第三阶段任务
...
EOF
```

**相关文档**:
- [任务文档模板](./TASK_TEMPLATE.md) - 详细的TASK.md和TASK-REPORT.md模板
- [协作冲突预防](./CONFLICT_PREVENTION.md) - 避免README.md冲突

---

## 📝 Phase 0: 准备阶段工作清单

在启动任何Worker CLI之前，主CLI必须完成以下步骤：

### 0.1 创建任务分配文档

**输出文件**: `docs/guides/.multi-cli-tasks/CLI-N_PHASE_NAME_TASKS.md`

**必须包含的章节**:
1. **基本信息**: 工作目录、Git分支、技术栈、任务数量、预计工期
2. **核心职责**: 明确的任务目标和范围
3. **依赖关系**: 输入依赖和输出依赖
4. **任务清单**: 详细的分阶段任务列表（至少包含任务编号、描述、验收标准）
5. **进度跟踪**: 进度更新章节模板
6. **工作流程与Git提交规范**: 包含每日工作流程、提交消息格式、完成标准检查清单

**质量标准**:
- ✅ 任务描述清晰，无歧义
- ✅ 验收标准可衡量、可验证
- ✅ 依赖关系明确，无循环依赖
- ✅ 工期估算合理（参考类似任务）

### 0.2 创建工作流程指南

**输出文件**: `docs/guides/.multi-cli-tasks/WORKER_CLI_GUIDE.md`

**必须包含的章节**:
1. **任务启动阶段**: 如何确认任务理解、设置进度跟踪
2. **开发实现阶段**: 开发原则、TDD工作流
3. **自测验证阶段**: 如何验证验收标准
4. **Git提交阶段**: 提交前检查清单、提交频率建议
5. **更新TASK-REPORT阶段**: 如何使用TASK-REPORT.md记录进度
6. **完成确认阶段**: 任务完成标准、合并流程

**质量标准**:
- ✅ 流程清晰，步骤明确
- ✅ 包含具体代码示例
- ✅ 提供常见问题处理指南
- ✅ 总长度1000+行，覆盖完整开发周期

### 0.3 创建监控机制文档

**输出文件**: `docs/guides/.multi-cli-tasks/PROGRESS_MONITORING_AND_MILESTONES.md`

**必须包含的章节**:
1. **监控原理**: 非侵入式监控的数据来源
2. **预警机制**: 黄色预警（24h）、红色预警（48h）
3. **自动化监控脚本**: 完整的Bash脚本实现
4. **里程碑管理**: 8个主要里程碑的定义和验收标准
5. **风险处理**: 如何处理阻塞问题

**质量标准**:
- ✅ 监控脚本可直接使用（无占位符）
- ✅ 预警阈值合理（避免频繁误报）
- ✅ 里程碑可衡量、可验证
- ✅ 风险处理流程明确

### 0.4 创建实施方案总览

**输出文件**: `openspec/changes/[change-name]/implementation-plan.md`

**必须包含的章节**:
1. **Executive Summary**: 项目背景、价值主张、时间节省
2. **架构图**: CLI依赖关系和数据流图
3. **资源分配**: 详细的任务分配表格（CLI名称、任务数、人天、优先级）
4. **Two-Round执行模型**: Round 1和Round 2的CLI划分
5. **交付清单**: 每个CLI的详细交付物和验收标准
6. **风险评估**: 5大风险和缓解措施
7. **成功指标**: 技术指标和业务指标

**质量标准**:
- ✅ 逻辑清晰，说服力强
- ✅ 数据准确（任务数、人天、时间线）
- ✅ 风险识别全面，缓解措施可行
- ✅ 成功指标可衡量

### 0.5 文件所有权和职责范围确认 ⚠️ **新增关键步骤**

**目的**: 防止多个CLI修改同一文件导致协作冲突

**输出文件**: `.FILE_OWNERSHIP` (主仓库根目录)

**必须完成的步骤**:

#### **0.5.1 创建文件所有权映射**
```bash
cd /opt/claude/mystocks_spec

cat > .FILE_OWNERSHIP << 'EOF'
# Git Worktree文件所有权映射
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

# ========== CLI-2: API契约标准化 ==========
docs/api/contracts/                  cli-2     | API契约文档
web/backend/app/schemas/            cli-2     | 数据模式定义
web/backend/openapi/                 cli-2     | OpenAPI规范

# ========== CLI-5: GPU监控仪表板 ==========
src/gpu/                            cli-5     | GPU相关代码
src/gpu_monitoring/                  cli-5     | GPU监控服务
scripts/start_gpu_monitoring.sh      cli-5     | GPU监控脚本

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
git commit -m "chore: add file ownership mapping for all CLIs"
```

#### **0.5.2 明确每个CLI的职责范围**
- ✅ 为每个CLI定义清晰的职责范围（参考上面的所有权映射）
- ✅ 确保职责不重叠（通过目录结构物理隔离）
- ✅ 记录在任务分配文档中
- ✅ 在CLI TASK.md中说明职责边界

#### **0.5.3 运行冲突检测脚本**
```bash
# 首次运行（检测潜在冲突）
bash scripts/maintenance/check_file_conflicts.sh

# 输出示例：
# ✅ 未发现文件冲突
# 或
# ⚠️  发现N个潜在文件冲突
#    建议与文件拥有者CLI协调
```

#### **0.5.4 建立协调机制**
- ✅ 定义跨CLI修改申请流程
- ✅ 建立定期同步会议机制（每天一次）
- ✅ 创建冲突报告流程
- ✅ 记录在主CLI工作规范中

**跨CLI修改申请流程**:
```
Worker CLI需要修改其他CLI拥有的文件时：
1. 向主CLI提交申请（包含修改原因和内容）
2. 主CLI评估影响范围
3. 主CLI协调相关CLI
4. 主CLI执行修改或授权Worker CLI修改
5. 主CLI通知所有相关CLI
```

**质量标准**:
- ✅ `.FILE_OWNERSHIP`文件已创建并提交
- ✅ 每个CLI有清晰的目录职责范围
- ✅ 冲突检测脚本已运行并记录结果
- ✅ 协调机制已建立并文档化

**预防措施**:
1. ✅ **在分配任务前**: 更新`.FILE_OWNERSHIP`文件
2. ✅ **在Worktree创建时**: 验证CLI专属工作目录不侵犯其他CLI
3. ✅ **在开发过程中**: 定期运行冲突检测脚本（每天一次）

**详细文档**: 参见 [Git Worktree协作冲突预防规范](./CONFLICT_PREVENTION.md)

---

## 🚀 Phase 1: Git Worktree创建标准流程

### 1.1 创建Worktree

**标准命令**:
```bash
git worktree add /opt/claude/mystocks_<phase>_<name> -b <branch-name>

# 示例：
git worktree add /opt/claude/mystocks_phase3_frontend -b phase3-frontend-optimization
```

**配置共享依赖 (Node.js 项目)**:
```bash
# 1. 确保主工作树已安装依赖
pnpm install

# 2. 为新 Worktree 创建软链接 (节省磁盘空间，保证版本一致)
cd /opt/claude/mystocks_phase3_frontend
ln -s ../mystocks_spec/node_modules ./node_modules
```

**验证步骤**:
```bash
git worktree list  # 确认worktree已创建
ls -la /opt/claude/mystocks_phase3_frontend  # 确认目录存在
ls -l /opt/claude/mystocks_phase3_frontend/node_modules  # 确认软链接指向正确
```

**详细命令参考**: [Git Worktree命令手册](./GIT_WORKTREE_MAIN_CLI_MANUAL.md)

### 1.2 初始化TASK.md

**步骤1**: 复制任务分配文档到TASK.md
```bash
cp /opt/claude/mystocks_spec/docs/guides/.multi-cli-tasks/CLI-1_PHASE3_TASKS.md \
   /opt/claude/mystocks_phase3_frontend/TASK.md
```

**步骤2**: 首次提交到Git
```bash
cd /opt/claude/mystocks_phase3_frontend
git add TASK.md
DISABLE_DIR_STRUCTURE_CHECK=1 git commit -m "feat: initialize CLI-1 Phase 3 frontend optimization tasks

- 20 tasks across 4 stages (12-14 working days)
- Enhanced K-line charts with klinecharts 9.6.0
- 161 technical indicators powered by TA-Lib backend
- GPU-accelerated indicator calculation (68.58x speedup)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

**关键注意**:
- ✅ 必须使用 `DISABLE_DIR_STRUCTURE_CHECK=1` 绕过目录结构检查（worktree环境不同）
- ✅ 提交消息必须清晰描述任务范围和技术栈
- ✅ Co-Authored-By 标记所有AI辅助生成的代码

### 1.3 修复Hook脚本权限（关键步骤！）⚠️

**问题**: Git worktree创建后，`.claude/hooks/` 目录下的脚本默认没有执行权限（644）

**症状**:
```
Stop hook error: Failed with non-blocking status code: /bin/sh: 1:
  /opt/claude/mystocks_phase6_api_contract/.claude/hooks/stop-python-quality-gate.sh: Permission denied
```

**修复命令**:
```bash
# 为单个CLI修复
chmod +x /opt/claude/mystocks_phase3_frontend/.claude/hooks/*.sh

# 批量修复所有CLI
for cli in /opt/claude/mystocks_phase3_frontend \
          /opt/claude/mystocks_phase6_api_contract \
          /opt/claude/mystocks_phase6_monitoring \
          /opt/claude/mystocks_phase6_quality; do
  chmod +x "$cli/.claude/hooks/"*.sh
  echo "✅ $(basename $cli) hooks权限已修复"
done
```

**验证修复**:
```bash
# 检查权限
ls -la /opt/claude/mystocks_phase3_frontend/.claude/hooks/ | grep "\.sh"

# 预期输出（应该是755权限）:
# -rwxr-xr-x 1 root root  7702 Dec 29 14:45 post-tool-use-database-schema-validator.sh
# -rwxr-xr-x 1 root root 14581 Dec 29 14:45 post-tool-use-document-organizer.sh
# ...

# 验证语法
for hook in /opt/claude/mystocks_phase3_frontend/.claude/hooks/*.sh; do
  bash -n "$hook" && echo "✅ $(basename $hook)"
done
```

**根因分析**:
- Hook脚本在worktree初始化时从主仓库复制
- Git不跟踪文件权限位（除非显式使用 `git update-index --chmod=+x`）
- `.claude` 目录通常在 `.gitignore` 中，不会被提交

**预防措施**:
- ✅ 在Worktree创建后立即执行 `chmod +x` 修复
- ✅ 在主CLI工作流程中列出此步骤为必需项
- ✅ 在Worker CLI启动时验证hooks可执行性

### 1.4 验证Git远程仓库名称 ⚠️ **关键步骤**

**问题**: 主仓库的远程仓库名称可能不是Git标准的 `origin`，导致所有文档中的 `git push origin` 命令失败

**症状**:
```bash
$ git push origin phase3-frontend-optimization
fatal: 'origin' does not appear to be a git remote
```

**检查命令**:
```bash
# 检查主仓库的远程名称
git remote -v

# ❌ 如果输出:
# mystocks    https://github.com/user/repo.git (fetch)
# mystocks    https://github.com/user/repo.git (push)

# ✅ 应该输出:
# origin    https://github.com/user/repo.git (fetch)
# origin    https://github.com/user/repo.git (push)
```

**修复命令**:
```bash
# 修复主仓库（所有worktree会自动继承）
git remote rename mystocks origin

# 验证修复
git remote -v
# 预期输出: origin (而非 mystocks)
```

**验证修复**:
```bash
# 验证所有worktree已自动继承
for cli in /opt/claude/mystocks_phase3_frontend \
          /opt/claude/mystocks_phase6_api_contract \
          /opt/claude/mystocks_phase6_monitoring \
          /opt/claude/mystocks_phase6_quality; do
  echo "## $(basename $cli)"
  cd "$cli" && git remote -v | grep origin && echo "✅ OK" || echo "❌ Failed"
  echo ""
done
```

**实际修复案例**: Commit `0a65718` (2025-12-29 18:29)
- 主仓库从 `mystocks` 改为 `origin`
- 所有4个worktree自动继承

**预防措施**:
- ✅ **在Phase 1.1创建worktree前**: 确认主仓库使用 `origin`
  ```bash
  git remote -v | grep origin || git remote rename <当前名称> origin
  ```

- ✅ **在Phase 1.4验证中**: 检查所有worktree的远程配置
  ```bash
  cd /opt/claude/mystocks_phase3_frontend
  git remote -v | grep origin
  ```

- ✅ **在文档中**: 始终使用标准的 `origin` 命令示例

**详细文档**: 参见 [Git远程名称标准化规范](./GIT_REMOTE_NAME_STANDARD.md)

### 1.5 验证Worktree完整性

**检查清单**:
```bash
# 1. Worktree已创建
git worktree list | grep phase3-frontend-optimization

# 2. TASK.md已初始化
cat /opt/claude/mystocks_phase3_frontend/TASK.md | head -20

# 3. Hooks有执行权限
ls -la /opt/claude/mystocks_phase3_frontend/.claude/hooks/ | grep "\.sh" | grep "rwx"

# 4. Git远程仓库名称为origin ⚠️
cd /opt/claude/mystocks_phase3_frontend && git remote -v | grep origin

# 5. 文件所有权已确认 ⚠️ **新增**
cat /opt/claude/mystocks_spec/.FILE_OWNERSHIP | grep cli-1

# 6. Pre-commit配置已说明 ⚠️ **新增**
grep "Pre-commit配置" /opt/claude/mystocks_phase3_frontend/TASK.md

# 7. Git分支正确
cd /opt/claude/mystocks_phase3_frontend && git branch

# 8. 首次提交已完成
cd /opt/claude/mystocks_phase3_frontend && git log --oneline -1
```

**预期结果**: 所有8项检查都✅通过

---

## 📊 Phase 2: 监控系统设置

### 2.1 创建监控脚本

**文件位置**: `scripts/monitoring/check_worker_progress.sh`

**关键特性**:
- ✅ 非侵入式（只读TASK-REPORT.md和Git历史）
- ✅ 自动化（可配置cron定时执行）
- ✅ 预警机制（黄/红色预警）
- ✅ 报告生成（保存到 `/tmp/mystocks_progress_*.txt`）

**完整实现**: 参考已创建的监控脚本（包含400+行完整实现）

### 2.2 设置自动化监控

**手动运行**:
```bash
bash /opt/claude/mystocks_spec/scripts/monitoring/check_worker_progress.sh
```

**自动化（每2小时）**:
```bash
(crontab -l 2>/dev/null; echo "0 */2 * * * /opt/claude/mystocks_spec/scripts/monitoring/check_worker_progress.sh >> /tmp/mystocks_progress.log 2>&1") | crontab -
```

**验证crontab**:
```bash
crontab -l | grep check_worker
```

### 2.3 监控报告解读

**报告文件**: `/tmp/mystocks_progress_YYYYMMDD_HHMMSS.txt`

**关键指标**:
- Active CLIs (< 24h): TASK-REPORT.md更新时间在24小时内
- Warning CLIs (24-48h): TASK-REPORT.md超过24小时未更新
- Alert CLIs (> 48h): TASK-REPORT.md超过48小时未更新

**响应策略**:
- 🟢 正常: 无需干预
- 🟡 预警: 在TASK-REPORT.md中记录，主CLI关注
- 🔴 告警: 主CLI主动联系Worker CLI了解阻塞原因

---

## 📚 Phase 3: 文档组织规范

### 3.1 文件组织标准

**主仓库文档结构**:
```
mystocks_spec/
├── docs/
│   └── guides/
│       └── .multi-cli-tasks/        # 所有CLI相关文档集中存放
│           ├── CLI-1_PHASE3_TASKS.md
│           ├── CLI-2_API_CONTRACT_TASKS.md
│           ├── CLI-3_PHASE4_COMPLETE_TASKS.md
│           ├── CLI-4_PHASE5_AI_SCREENING_TASKS.md
│           ├── CLI-5_PHASE6_GPU_MONITORING_TASKS.md
│           ├── CLI-6_QUALITY_ASSURANCE_TASKS.md
│           ├── PROGRESS_MONITORING_AND_MILESTONES.md
│           ├── WORKER_CLI_GUIDE.md
│           ├── MAIN_CLI_WORKFLOW.md  # 本文档
│           ├── GIT_WORKTREE_MAIN_CLI_MANUAL.md
│           ├── CONFLICT_PREVENTION.md
│           ├── GIT_REMOTE_NAME_STANDARD.md
│           └── TASK_TEMPLATE.md
├── openspec/
│   └── changes/
│       └── frontend-optimization-six-phase/
│           └── implementation-plan.md
└── scripts/
    └── monitoring/
        └── check_worker_progress.sh
```

**命名规范**:
- 任务分配文档: `CLI-N_PHASE_NAME_TASKS.md`
- 流程指南文档: `*_WORKFLOW_GUIDE.md`
- 监控相关文档: `PROGRESS_MONITORING_AND_MILESTONES.md`
- 工作规范文档: `MAIN_CLI_WORKFLOW.md`
- Git命令文档: `*_MANUAL.md`
- 冲突预防文档: `CONFLICT_PREVENTION.md`
- 远程名称文档: `GIT_REMOTE_NAME_STANDARD.md`
- 任务模板文档: `TASK_TEMPLATE.md`

### 3.2 TASK.md章节标准

**所有CLI的TASK.md必须包含以下章节**:

1. **基本信息**: 工作目录、Git分支、技术栈、任务数量、预计工期
2. **核心职责**: 明确的任务目标和范围
3. **依赖关系**: 输入依赖和输出依赖
4. **任务清单**: 详细的分阶段任务列表
5. **总体验收标准**: 功能完整性、性能指标、测试覆盖、文档完整性
6. **进度跟踪**: 任务进度统计和更新日志（链接到TASK-REPORT.md）

**禁止**:
- ❌ TASK.md中没有"进度跟踪"章节
- ❌ 没有链接到TASK-REPORT.md
- ❌ 没有Git提交规范和示例

---

## ✅ Phase 4: 验收与交付标准

### 4.1 Worktree就绪检查清单

主CLI在启动Worker CLI前必须确认:

- [ ] 任务分配文档已创建并审查通过
- [ ] **文件所有权映射已创建（.FILE_OWNERSHIP）** ⚠️ **新增**
- [ ] Git worktree已创建并验证
- [ ] **Git远程仓库名称为 `origin`**
- [ ] TASK.md已初始化并包含所有必需章节
- [ ] 工作流程指南已创建并链接在TASK.md中
- [ ] Hook脚本权限已修复（755）
- [ ] Hook脚本语法已验证（bash -n）
- [ ] **Pre-commit配置已说明（继承主仓库，不修改）** ⚠️ **新增**
- [ ] **共享依赖已链接 (Node.js) ⚠️ **新增**
- [ ] 监控脚本已创建并可运行
- [ ] **冲突检测脚本已创建并测试运行** ⚠️ **新增**
- [ ] 实施方案文档已创建并获得批准

### 4.2 Round启动检查清单

**Round 1启动前** (CLI-1, CLI-2, CLI-5, CLI-6):
- [ ] 主CLI已完成Phase 0-4所有准备步骤
- [ ] **文件所有权映射已创建并验证** ⚠️ **新增**
- [ ] 4个worktree已创建并验证
- [ ] 4个worktree的远程仓库名称为 `origin`
- [ ] 4个TASK.md已初始化并包含工作流程规范
- [ ] 4个hooks权限已修复并验证
- [ ] **4个Pre-commit配置已说明** ⚠️ **新增**
- [ ] **4个共享依赖已链接** ⚠️ **新增**
- [ ] **4个冲突检测脚本已运行并记录结果** ⚠️ **新增**
- [ ] 监控脚本已测试运行成功
- [ ] 实施方案文档已获得项目组批准

**Round 2启动前** (CLI-3, CLI-4):
- [ ] Round 1所有CLI已完成≥80%任务
- [ ] CLI-2（API契约）已100%完成
- [ ] **文件所有权映射已更新（包含CLI-3, CLI-4）** ⚠️ **新增**
- [ ] 2个worktree已创建并验证
- [ ] 2个worktree的远程仓库名称为 `origin`
- [ ] 2个TASK.md已初始化并包含工作流程规范
- [ ] 2个hooks权限已修复并验证
- [ ] **2个Pre-commit配置已说明** ⚠️ **新增**
- [ ] **2个共享依赖已链接** ⚠️ **新增**
- [ ] 依赖验证通过（CLI-3可调用CLI-2的API）

### 4.3 CLI完成验收标准

**单个CLI完成标准**:
- [ ] 所有任务已完成（100%）
- [ ] 所有验收标准已通过（100%）
- [ ] 代码已推送到远程分支
- [ ] 测试覆盖率达标（后端>80%, 前端>70%）
- [ ] 代码质量检查通过（Pylint>8.0, 无高危漏洞）
- [ ] TASK-REPORT.md已更新（完整进度）
- [ ] 完成报告已生成（TASK-*-REPORT.md）
- [ ] 文档完整（API文档、组件说明等）

**Round完成标准**:
- [ ] Round内所有CLI已完成（100%）
- [ ] 集成测试已通过
- [ ] 主CLI已验收所有交付物
- [ ] 所有分支已合并到main（或准备合并）

## ✅ Phase 5: 结项与资源回收 (Closure & Cleanup) ⭐ **强制执行**

**唯一负责人**: 主 CLI (Manager)
**执行时机**: 代码合并成功且冲突解决后立即执行。

### 5.1 原子化清理与归档流程

主 CLI 必须按以下顺序执行清理，严禁遗漏任何一步：

1.  **文档收割 (Document Harvesting)**: ⚠️ **最关键一步**
    *   在删除 Worktree 前，必须将 Worker 的过程文档归档到主仓库，否则历史将永久丢失。
    ```bash
    # 创建归档目录
    mkdir -p docs/archive/phase_x_reports/
    
    # 收割报告
    cp /opt/claude/mystocks_cli_x/TASK-REPORT.md docs/archive/phase_x_reports/CLI-X_PROGRESS.md
    cp /opt/claude/mystocks_cli_x/TASK-*-REPORT.md docs/archive/phase_x_reports/ 2>/dev/null
    
    # 提交归档
    git add docs/archive/
    git commit -m "docs: archive CLI-X reports before worktree deletion"
    ```

2.  **物理删除 Worktree**:
    ```bash
    # 强制清理未跟踪的缓存文件
    git worktree remove -f /opt/claude/mystocks_cli_x
    ```
    *   **目的**: 释放磁盘空间，防止 `.pytest_cache` 等垃圾文件堆积。

3.  **清理逻辑引用 (分支)**:
    ```bash
    # 删除远程分支，宣告任务终结
    git push origin --delete branch-name
    # 删除本地分支，保持引用树整洁
    git branch -d branch-name
    ```

4.  **元数据兜底 Prune**:
    ```bash
    # 清理 .git/worktrees 下的无效记录
    git worktree prune
    ```
    *   **目的**: 修复任何因手动 `rm -rf` 导致的元数据损坏。

### 5.2 成功结项定义
一个任务被认为完全“结项”的标志是：
- ✅ 分支已合并至 `main`。
- ✅ 远程分支已消失。
- ✅ `git worktree list` 中不再显示该路径。
- ✅ 根目录无污染（Zero-Root-Config 审计通过）。

## 📚 Phase 6: 聚合报告与归档总结 (Final Review)

当所有 Worker CLI 完成使命并清理后，主 CLI 需生成最终的“项目结项书”。

### 6.1 聚合报告结构
主 CLI 应创建一个 `PHASE_X_COMPLETION_SUMMARY.md`，内容来源于之前收割的 `docs/archive/` 文件：

1.  **任务执行概览**:
    *   分配了多少任务？完成了多少？
    *   实际工时 vs 预计工时（数据来自各 CLI 的 `TASK-REPORT`）。
2.  **配置清单快照**:
    *   记录本次开发中各 Worktree 使用的 `config/` 路径和依赖版本，以便未来回溯复现。
3.  **问题与反馈复盘**:
    *   汇总所有 Worker 在 `🚧 阻塞问题` 章节提交的反馈。
    *   记录主 CLI 的响应措施及效果。
4.  **遗留债务**:
    *   任何被标记为“本次不修”的问题，转入全局 `TECHNICAL_DEBT.md`。

---

## 💡 最佳实践总结

### 会话标记规范 ⭐ **新增（借鉴iflow）**

在Claude Code会话中，使用一致的标识符来维护上下文。

**使用方法**:
```bash
# 启动 Claude 时使用清晰的会话标识符
claude

# 始终在提示中使用清晰的上下文标签
Human: [CLI-1-Phase3] 让我们继续处理K线图实现...
Human: [CLI-2-API] 让我们继续处理API契约定义...
```

**好处**:
- ✅ 避免不同CLI的上下文混淆
- ✅ 每个会话有明确的身份标识
- ✅ 便于主CLI区分和跟踪

### 终端提示符配置 ⭐ **新增（借鉴iflow）**

在shell提示符中添加分支信息，避免忘记当前worktree。

**Bash配置**:
```bash
# 添加到 ~/.bashrc
parse_git_branch() {
  git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/(\1)/'
}
export PS1="\[\e[36m\]\w\[\e[91m\]\$(parse_git_branch)\[\e[00m\] $ "
```

**Zsh配置**:
```bash
# 在主题或 .zshrc 中包含 git 分支信息
```

**iTerm颜色区分**:
```bash
# 在iTerm中为不同worktree使用不同的终端颜色
echo -e "\033]0;Claude: CLI-1 Phase 3\007"
```

### 进度跟踪的协调文件 ⭐ **新增（借鉴iflow）**

创建项目协调目录来跟踪所有worktree的进度。

**创建协调目录**:
```bash
# 创建项目协调目录
mkdir -p ~/projects/feature-coordination
cd ~/projects/feature-coordination

# 创建进度跟踪文件
echo "# 项目进度跟踪" > README.md
echo "- [ ] CLI-1: K线图优化 (../mystocks_phase3_frontend)" >> README.md
echo "- [ ] CLI-2: API契约 (../mystocks_phase6_api_contract)" >> README.md
echo "- [ ] CLI-5: GPU监控 (../mystocks_phase6_monitoring)" >> README.md

# 随着工作进展更新状态
sed -i 's/- \[ \] CLI-1/- [x] CLI-1/' README.md
git commit -am "CLI-1完成"
```

### Do's（应该做的）

1. ✅ **完整准备**: 在启动任何Worker CLI前，完成所有准备阶段工作（Phase 0-4）
2. ✅ **文档驱动**: 所有流程、规范、标准都有文档记录，并在TASK.md中链接
3. ✅ **标准化**: 所有CLI使用相同的文档格式、工作流程、提交规范
4. ✅ **非侵入式**: 监控通过TASK-REPORT.md更新和Git历史，不主动干预Worker CLI
5. ✅ **及时响应**: 遇到预警（黄/红）立即联系Worker CLI了解情况
6. ✅ **验证优先**: Worktree创建后立即验证hooks权限、TASK.md完整性
7. ✅ **工具自动化**: 使用监控脚本自动化进度检查，减少人工干预
8. ✅ **会话标记**: 使用[CLI-X-PhaseY]标识不同会话
9. ✅ **终端配置**: 配置shell提示符显示分支信息
10. ✅ **进度协调**: 创建协调文件跟踪所有worktree进度

### Don'ts（不应该做的）

1. ❌ **不完整启动**: 只创建worktree和复制任务文档，忽略工作流程和hooks
2. ❌ **侵入式管理**: 直接修改Worker CLI的代码或文件，除非被请求
3. ❌ **忽视权限**: 忘记修复hook脚本权限，导致Worker CLI无法正常工作
4. ❌ **文档缺失**: TASK.md中没有工作流程、Git提交规范、进度更新格式
5. ❌ **缺少监控**: 没有设置自动化监控，无法及时发现停滞或阻塞
6. ❌ **不验收交付**: Worker CLI声称完成但主CLI未验收就合并到main
7. ❌ **重复造轮**: 每次项目都重新设计流程，而不是复用已验证的模板
8. ❌ **README任务**: 使用README.md记录CLI特定任务，导致合并冲突
9. ❌ **忘记Pre-flight**: 开始新工作前不检查worktree和远程更新
10. ❌ **忽略所有权**: 不创建文件所有权映射，导致协作冲突

---

## 🔗 相关文档

### 流程文档
- [Worker CLI工作流程指南](./WORKER_CLI_GUIDE.md) - Worker CLI必读
- [Git Worktree协作冲突预防](./CONFLICT_PREVENTION.md) - 冲突处理
- [任务文档模板](./templates/TASK_TEMPLATE.md) - TASK.md和TASK-REPORT.md模板

### Git命令文档
- [Git Worktree手册](./GIT_WORKTREE_MAIN_CLI_MANUAL.md) - Git worktree命令参考
- [Git远程名称标准](./GIT_REMOTE_NAME_STANDARD.md) - 远程配置规范

### 任务分配文档
- [CLI-1: Phase 3前端K线图优化](../../docs/guides/.multi-cli-tasks/CLI-1_PHASE3_TASKS.md)
- [CLI-2: API契约标准化](../../docs/guides/.multi-cli-tasks/CLI-2_API_CONTRACT_TASKS.md)
- [CLI-3: Phase 4完整实现](../../docs/guides/.multi-cli-tasks/CLI-3_PHASE4_COMPLETE_TASKS.md)
- [CLI-4: Phase 5 AI智能筛选](../../docs/guides/.multi-cli-tasks/CLI-4_PHASE5_AI_SCREENING_TASKS.md)
- [CLI-5: Phase 6 GPU监控](../../docs/guides/.multi-cli-tasks/CLI-5_PHASE6_GPU_MONITORING_TASKS.md)
- [CLI-6: 质量保证](../../docs/guides/.multi-cli-tasks/CLI-6_QUALITY_ASSURANCE_TASKS.md)

### 实施方案
- [Frontend Six-Phase实施方案](../../openspec/changes/frontend-optimization-six-phase/implementation-plan.md)

---

## 🔄 文档维护

**版本历史**:
- v1.0 (2025-12-29): 初始版本，基于Phase 3-6多CLI并行开发经验
- v2.0 (2025-12-30): 重大更新
  - 添加Step -1: Pre-flight检查清单（强制执行）
  - 更新任务文档方式为TASK.md + TASK-REPORT.md
  - 添加文件所有权确认步骤
  - 添加会话标记规范
  - 添加终端提示符配置
  - 添加进度跟踪协调文件
  - 增强文档链接矩阵
  - 减少Git命令详解，链接到命令手册
- v3.2 (2026-03-05): 治理升级
  - `main` 角色收敛为“协调 + 验收”，不直接做功能开发
  - 功能开发统一迁移到 `worktree/dev-*` 分支
  - PR 统一 `base=main`，并强制三道合并门禁

**维护者**: Main CLI
**更新频率**: 每个项目结束后总结经验教训，更新本文档

---

**本文档是主CLI的工作圣经** - 严格遵循可避免重复踩坑，提高并行开发效率，确保项目成功交付！
