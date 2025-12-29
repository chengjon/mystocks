# Main CLI 工作规范与最佳实践

**文档版本**: v1.0
**创建日期**: 2025-12-29
**适用范围**: 所有使用Git Worktree进行多CLI并行开发的项目
**维护者**: Main CLI (主CLI)

---

## 📋 文档目的

本文档总结了在MyStocks项目Phase 3-6多CLI并行开发实施过程中积累的经验教训，制定了标准化的工作流程和最佳实践规范，供主CLI在未来项目中参考和遵循。

**核心价值**:
- ✅ 避免重复踩坑，提高启动效率
- ✅ 标准化工作流程，降低管理成本
- ✅ 确保所有CLI具备完整的开发和提交能力
- ✅ 建立可重复、可验证的并行开发框架

---

## 🎯 核心原则

### 1. **完整优先** (Completeness First)

在启动任何Worker CLI之前，必须确保其具备完整的工作能力：

- ✅ Git worktree已创建并初始化
- ✅ README.md包含完整任务清单和工作流程规范
- ✅ 所有hook脚本具有执行权限
- ✅ 监控系统已配置并可正常追踪进度
- ✅ 提交流程和验收标准已明确

**错误示例**: 只创建worktree和复制任务文档，忽略工作流程和hooks

### 2. **文档驱动** (Documentation Driven)

所有规范、流程、标准必须文档化，并放在显眼位置：

- ✅ 工作流程指南必须链接在README中
- ✅ Git提交规范必须包含具体示例
- ✅ 进度更新格式必须提供模板
- ✅ 完成标准必须明确可衡量

### 3. **非侵入式监控** (Non-Invasive Monitoring)

主CLI通过被动方式监控进度，不主动干预Worker CLI工作：

- ✅ 通过README更新时间判断活跃状态
- ✅ 通过Git提交历史了解进展
- ✅ 通过自动化脚本定期检查
- ❌ 不直接修改Worker CLI的代码或文件

### 4. **标准化复用** (Standardized Reuse)

所有CLI共享相同的工作流程、文档格式、提交规范：

- ✅ 统一的CLI工作流程指南
- ✅ 统一的README章节结构
- ✅ 统一的Git提交消息格式
- ✅ 统一的进度更新模板

---

## 📝 Phase 0: 准备阶段工作清单

在启动任何Worker CLI之前，主CLI必须完成以下步骤：

### 0.1 创建任务分配文档

**输出文件**: `docs/guides/multi-cli-tasks/CLI-N_PHASE_NAME_TASKS.md`

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

**输出文件**: `docs/guides/multi-cli-tasks/CLI_WORKFLOW_GUIDE.md`

**必须包含的章节**:
1. **任务启动阶段**: 如何确认任务理解、设置进度跟踪
2. **开发实现阶段**: 开发原则、TDD工作流
3. **自测验证阶段**: 如何验证验收标准
4. **Git提交阶段**: 提交前检查清单、提交频率建议
5. **README更新阶段**: 进度报告格式
6. **完成确认阶段**: 任务完成标准、合并流程

**质量标准**:
- ✅ 流程清晰，步骤明确
- ✅ 包含具体代码示例
- ✅ 提供常见问题处理指南
- ✅ 总长度1000+行，覆盖完整开发周期

### 0.3 创建监控机制文档

**输出文件**: `docs/guides/multi-cli-tasks/PROGRESS_MONITORING_AND_MILESTONES.md`

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

---

## 🚀 Phase 1: Git Worktree创建标准流程

### 1.1 创建Worktree

**标准命令**:
```bash
git worktree add /opt/claude/mystocks_<phase>_<name> -b <branch-name>

# 示例：
git worktree add /opt/claude/mystocks_phase3_frontend -b phase3-frontend-optimization
```

**验证步骤**:
```bash
git worktree list  # 确认worktree已创建
ls -la /opt/claude/mystocks_phase3_frontend  # 确认目录存在
```

### 1.2 初始化README

**步骤1**: 复制任务分配文档到README
```bash
cp /opt/claude/mystocks_spec/docs/guides/multi-cli-tasks/CLI-1_PHASE3_TASKS.md \
   /opt/claude/mystocks_phase3_frontend/README.md
```

**步骤2**: 首次提交到Git
```bash
cd /opt/claude/mystocks_phase3_frontend
git add README.md
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

### 1.4 验证Worktree完整性

**检查清单**:
```bash
# 1. Worktree已创建
git worktree list | grep phase3-frontend-optimization

# 2. README已初始化
cat /opt/claude/mystocks_phase3_frontend/README.md | head -20

# 3. Hooks有执行权限
ls -la /opt/claude/mystocks_phase3_frontend/.claude/hooks/ | grep "\.sh" | grep "rwx"

# 4. Git分支正确
cd /opt/claude/mystocks_phase3_frontend && git branch

# 5. 首次提交已完成
cd /opt/claude/mystocks_phase3_frontend && git log --oneline -1
```

**预期结果**: 所有5项检查都✅通过

---

## 📊 Phase 2: 监控系统设置

### 2.1 创建监控脚本

**文件位置**: `scripts/monitoring/check_worker_progress.sh`

**关键特性**:
- ✅ 非侵入式（只读README和Git历史）
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
- Active CLIs (< 24h): README更新时间在24小时内
- Warning CLIs (24-48h): README超过24小时未更新
- Alert CLIs (> 48h): README超过48小时未更新

**响应策略**:
- 🟢 正常: 无需干预
- 🟡 预警: 在README中记录，主CLI关注
- 🔴 告警: 主CLI主动联系Worker CLI了解阻塞原因

---

## 📚 Phase 3: 文档组织规范

### 3.1 文件组织标准

**主仓库文档结构**:
```
mystocks_spec/
├── docs/
│   └── guides/
│       └── multi-cli-tasks/        # 所有CLI相关文档集中存放
│           ├── CLI-1_PHASE3_TASKS.md
│           ├── CLI-2_API_CONTRACT_TASKS.md
│           ├── CLI-3_PHASE4_COMPLETE_TASKS.md
│           ├── CLI-4_PHASE5_AI_SCREENING_TASKS.md
│           ├── CLI-5_PHASE6_GPU_MONITORING_TASKS.md
│           ├── CLI-6_QUALITY_ASSURANCE_TASKS.md
│           ├── PROGRESS_MONITORING_AND_MILESTONES.md
│           ├── CLI_WORKFLOW_GUIDE.md
│           └── MAIN_CLI_WORKFLOW_STANDARDS.md  # 本文档
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
- 工作规范文档: `MAIN_CLI_WORKFLOW_STANDARDS.md`

### 3.2 README章节标准

**所有CLI的README必须包含以下章节**:

1. **基本信息**: 工作目录、Git分支、技术栈、任务数量、预计工期
2. **核心职责**: 明确的任务目标和范围
3. **依赖关系**: 输入依赖和输出依赖
4. **任务清单**: 详细的分阶段任务列表
5. **总体验收标准**: 功能完整性、性能指标、测试覆盖、文档完整性
6. **进度跟踪**: 任务进度统计和更新日志
7. **工作流程与Git提交规范**:
   - 📚 完整工作流程指南链接
   - ⚡ 快速参考（每日工作流程、提交消息格式、完成标准、进度更新格式）
   - 🎯 关键注意事项
   - 📞 需要帮助？（文档链接）

**禁止**:
- ❌ README中没有"工作流程与Git提交规范"章节
- ❌ 没有进度更新格式模板
- ❌ 没有Git提交消息规范和示例

---

## ✅ Phase 4: 验收与交付标准

### 4.1 Worktree就绪检查清单

主CLI在启动Worker CLI前必须确认:

- [ ] 任务分配文档已创建并审查通过
- [ ] Git worktree已创建并验证
- [ ] README.md已初始化并包含所有必需章节
- [ ] 工作流程指南已创建并链接在README中
- [ ] Hook脚本权限已修复（755）
- [ ] Hook脚本语法已验证（bash -n）
- [ ] 监控脚本已创建并可运行
- [ ] 实施方案文档已创建并获得批准

### 4.2 Round启动检查清单

**Round 1启动前** (CLI-1, CLI-2, CLI-5, CLI-6):
- [ ] 主CLI已完成Phase 0-4所有准备步骤
- [ ] 4个worktree已创建并验证
- [ ] 4个README已初始化并包含工作流程规范
- [ ] 4个hooks权限已修复并验证
- [ ] 监控脚本已测试运行成功
- [ ] 实施方案文档已获得项目组批准

**Round 2启动前** (CLI-3, CLI-4):
- [ ] Round 1所有CLI已完成≥80%任务
- [ ] CLI-2（API契约）已100%完成
- [ ] 2个worktree已创建并验证
- [ ] 2个README已初始化并包含工作流程规范
- [ ] 2个hooks权限已修复并验证
- [ ] 依赖验证通过（CLI-3可调用CLI-2的API）

### 4.3 CLI完成验收标准

**单个CLI完成标准**:
- [ ] 所有任务已完成（100%）
- [ ] 所有验收标准已通过（100%）
- [ ] 代码已推送到远程分支
- [ ] 测试覆盖率达标（后端>80%, 前端>70%）
- [ ] 代码质量检查通过（Pylint>8.0, 无高危漏洞）
- [ ] README中记录了完整的进度更新历史
- [ ] 完成报告已生成（如需要）

**Round完成标准**:
- [ ] Round内所有CLI已完成（100%）
- [ ] 集成测试已通过
- [ ] 主CLI已验收所有交付物
- [ ] 所有分支已合并到main（或准备合并）

---

## 🔧 常见问题与解决方案

### 问题1: Hook脚本权限错误

**症状**: `Permission denied` 错误在 `stop-python-quality-gate.sh` 或 `user-prompt-submit-skill-activation.sh`

**根因**: Hook脚本在worktree创建时没有执行权限（644而非755）

**解决方案**:
```bash
chmod +x /opt/claude/mystocks_<phase>_<name>/.claude/hooks/*.sh

# 验证
ls -la /opt/claude/mystocks_<phase>_<name>/.claude/hooks/ | grep "\.sh"
```

**预防**: 在所有Worktree创建流程中加入此步骤为必需项

### 问题2: README中没有工作流程规范

**症状**: Worker CLI不知道如何提交代码、更新进度

**根因**: README只包含任务清单，缺少工作流程章节

**解决方案**:
1. 在主仓库创建通用工作流程指南（`CLI_WORKFLOW_GUIDE.md`）
2. 在每个CLI的README中添加"工作流程与Git提交规范"章节
3. 包含快速参考和完整指南链接

**预防**: 在Worktree初始化检查清单中加入README章节验证

### 问题3: 监控脚本检测不到进度

**症状**: 所有CLI显示"尚未开始记录进度"

**根因**: Worker CLI没有在README中添加"进度更新"章节

**解决方案**:
1. 在README中提供进度更新模板
2. 在工作流程指南中明确要求添加"进度更新"章节
3. 监控脚本优先检测"进度更新"章节的存在

**预防**: 在Worker CLI启动指南中强调添加进度更新章节

### 问题4: Git提交被pre-commit hook阻止

**症状**: 提交时报告"项目根目录不存在: --quiet"

**根因**: Worktree环境与主仓库不同，`scripts/maintenance/check-structure.sh` 不存在

**解决方案**:
```bash
DISABLE_DIR_STRUCTURE_CHECK=1 git commit -m "message"
```

**预防**: 在所有提交示例中使用此环境变量

### 问题5: Worker CLI进度停滞

**症状**: 监控显示黄色或红色预警

**根因**: Worker CLI遇到阻塞问题未报告，或忘记更新README

**解决方案**:
1. 主CLI主动联系Worker CLI了解情况
2. 在README中记录阻塞问题
3. 调整任务优先级或提供帮助

**预防**: 监控脚本每2小时自动运行，主CLI每天检查报告

---

## 📖 最佳实践总结

### Do's（应该做的）

1. ✅ **完整准备**: 在启动任何Worker CLI前，完成所有准备阶段工作（Phase 0-4）
2. ✅ **文档驱动**: 所有流程、规范、标准都有文档记录，并在README中链接
3. ✅ **标准化**: 所有CLI使用相同的文档格式、工作流程、提交规范
4. ✅ **非侵入式**: 监控通过README更新和Git历史，不主动干预Worker CLI
5. ✅ **及时响应**: 遇到预警（黄/红）立即联系Worker CLI了解情况
6. ✅ **验证优先**: Worktree创建后立即验证hooks权限、README完整性
7. ✅ **工具自动化**: 使用监控脚本自动化进度检查，减少人工干预

### Don'ts（不应该做的）

1. ❌ **不完整启动**: 只创建worktree和复制任务文档，忽略工作流程和hooks
2. ❌ **侵入式管理**: 直接修改Worker CLI的代码或文件，除非被请求
3. ❌ **忽视权限**: 忘记修复hook脚本权限，导致Worker CLI无法正常工作
4. ❌ **文档缺失**: README中没有工作流程、Git提交规范、进度更新格式
5. ❌ **缺少监控**: 没有设置自动化监控，无法及时发现停滞或阻塞
6. ❌ **不验收交付**: Worker CLI声称完成但主CLI未验收就合并到main
7. ❌ **重复造轮**: 每次项目都重新设计流程，而不是复用已验证的模板

---

## 🎯 快速参考检查清单

### 主CLI准备阶段（启动Worker CLI前）

```
Phase 0: 文档准备
  [ ] 任务分配文档 (CLI-N_PHASE_NAME_TASKS.md)
  [ ] 工作流程指南 (CLI_WORKFLOW_GUIDE.md)
  [ ] 监控机制文档 (PROGRESS_MONITORING_AND_MILESTONES.md)
  [ ] 实施方案文档 (implementation-plan.md)

Phase 1: Worktree创建
  [ ] Git worktree已创建
  [ ] README.md已初始化
  [ ] Hooks权限已修复 (chmod +x)
  [ ] Hooks语法已验证 (bash -n)
  [ ] 首次提交已完成

Phase 2: 监控设置
  [ ] 监控脚本已创建
  [ ] 监控脚本已测试运行
  [ ] 自动化监控已设置 (crontab)

Phase 3: 验证
  [ ] 所有检查项通过
  [ ] 准备启动Worker CLI
```

### Worker CLI启动检查（30秒快速验证）

```bash
# 1. Worktree存在
git worktree list | grep <branch-name>

# 2. README完整
grep "工作流程与Git提交规范" /opt/claude/mystocks_*/README.md

# 3. Hooks可执行
ls -la /opt/claude/mystocks_*/.claude/hooks/*.sh | grep "rwx"

# 4. 监控可运行
bash /opt/claude/mystocks_spec/scripts/monitoring/check_worker_progress.sh
```

---

## 📚 相关文档索引

**流程文档**:
- [Worker CLI工作流程指南](./CLI_WORKFLOW_GUIDE.md) - Worker CLI必读
- [进度监控与里程碑](./PROGRESS_MONITORING_AND_MILESTONES.md) - 监控机制
- [Git Worktree手册](../GIT_WORKTREE_MAIN_CLI_MANUAL.md) - Git worktree命令

**任务分配文档**:
- [CLI-1: Phase 3前端K线图优化](./CLI-1_PHASE3_TASKS.md)
- [CLI-2: API契约标准化](./CLI-2_API_CONTRACT_TASKS.md)
- [CLI-3: Phase 4完整实现](./CLI-3_PHASE4_COMPLETE_TASKS.md)
- [CLI-4: AI智能筛选](./CLI-4_PHASE5_AI_SCREENING_TASKS.md)
- [CLI-5: GPU监控仪表板](./CLI-5_PHASE6_GPU_MONITORING_TASKS.md)
- [CLI-6: 质量保证](./CLI-6_QUALITY_ASSURANCE_TASKS.md)

**实施方案**:
- [Frontend Six-Phase实施方案](../../openspec/changes/frontend-optimization-six-phase/implementation-plan.md)

---

## 🔄 文档维护

**版本历史**:
- v1.0 (2025-12-29): 初始版本，基于Phase 3-6多CLI并行开发经验

**维护者**: Main CLI
**更新频率**: 每个项目结束后总结经验教训，更新本文档

**反馈渠道**: 如果在遵循本规范过程中遇到问题或有改进建议，请在项目复盘会议上提出。

---

**本文档是主CLI的工作圣经** - 严格遵循可避免重复踩坑，提高并行开发效率，确保项目成功交付！
