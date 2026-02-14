# Worker CLI 工作流程指南

**文档版本**: v2.0
**最后更新**: 2025-12-30
**维护者**: Main CLI
**适用于**: 所有Worker CLI

---

## 📋 工作流程总览

```
1. 任务启动 → 2. 开发实现 → 3. 自测验证 → 4. Git提交 → 5. 更新TASK-REPORT → 6. 完成确认
```

**重要变更**: v2.0不再使用README.md记录进度，改用TASK-REPORT.md和TASK-*-REPORT.md
- ✅ 避免多CLI修改README.md导致合并冲突
- ✅ 任务说明（TASK.md）与进度报告（TASK-REPORT.md）分离
- ✅ 完成报告使用 TASK-*-REPORT.md
- ✅ 更清晰的文档结构

---

## 1️⃣ 任务启动阶段

### 1.1 阅读TASK.md

- ✅ 仔细阅读TASK.md中的任务描述
- ✅ 理解验收标准（Acceptance Criteria）
- ✅ 确认依赖关系和前置条件
- ✅ 确认文件所有权（查阅 `/opt/claude/mystocks_spec/.FILE_OWNERSHIP`）
- ✅ 如有疑问，在TASK-REPORT.md中记录问题并报告主CLI

**TASK.md位置**: worktree根目录
```bash
cd /opt/claude/mystocks_cli_x
cat TASK.md
```

### 1.2 创建TASK-REPORT.md

在worktree根目录创建TASK-REPORT.md（进度报告文件）：

```markdown
# CLI-X 任务进度报告

**Worker CLI**: CLI-X (描述)
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

## ⏳ 待开始

- [ ] 任务3: 描述 - 预计开始: YYYY-MM-DD

---

## 🚧 阻塞问题

无

---

## 📈 进度统计

- **已完成任务**: 0/Y (0%)
- **预计完成时间**: YYYY-MM-DD
- **实际用时**: 0小时（预计Y小时）

---

## 📝 备注

任务启动，开始理解任务
```

**多阶段任务示例**: 如果有TASK-1.md, TASK-2.md等

```bash
cd /opt/claude/mystocks_cli_x
# 当前在第一阶段
cat TASK-1.md
cat > TASK-REPORT.md << 'EOF'
# CLI-X 第一阶段进度报告

**Worker CLI**: CLI-X
**任务文档**: TASK-1.md
**报告文档**: TASK-1-REPORT.md
**当前阶段**: T+0h
**报告时间**: YYYY-MM-DD HH:MM
...
EOF
```

---

## 2️⃣ 开发实现阶段

### 2.1 开发原则

- ✅ **配置不占根目录** (Zero Root Config) ⭐ **2026-02-08 新增**
  - ❌ **禁止**在根目录新建任何 `.js`, `.ts`, `.yaml`, `.json` 配置文件。
  - ✅ **必须**存放在 `config/` 下的对应子目录（如 `config/playwright/`）。
  - ✅ 运行工具时显式指定配置：`npx playwright test -c config/playwright/playwright.config.ts`。
- ✅ **共享依赖开发** (Shared Dependencies)
  - 你的 `node_modules` 是软链接到主仓库的。
  - ❌ **禁止**直接运行 `npm install <package>` (会破坏共享目录)。
  - ✅ **必须**在主工作树或共享目录运行 `pnpm install`，或者联系 Main CLI 添加依赖。
- ✅ **逻辑下沉** (Logic Gravity)：业务代码必须在 `src/` 目录下，根目录 `.py` 文件仅作为入口外壳。
- ✅ 遵循项目的代码质量标准（见CLAUDE.md）
- ✅ 使用TODO注释标记临时代码
- ✅ 复杂逻辑添加注释说明
- ✅ 保持小步快跑，频繁提交

### 2.2 测试驱动开发

对于后端代码:
```bash
# 1. 先写测试
pytest tests/test_new_feature.py -xvs  # 预期失败

# 2. 实现功能
vim src/new_feature.py

# 3. 运行测试
pytest tests/test_new_feature.py -xvs  # 预期通过

# 4. 代码质量检查
ruff check src/new_feature.py
pylint src/new_feature.py
```

对于前端代码:
```bash
# 1. 编写组件测试
vim tests/unit/NewComponent.spec.ts

# 2. 运行测试
npm run test:unit

# 3. 类型检查
npx vue-tsc --noEmit
```

### 2.3 代码质量检查

在提交前必须执行:

```bash
# 后端代码
ruff check . --fix
black .
pylint src/

# 前端代码
npm run lint
npm run type-check
```

### 2.4 Git命令快速参考

详细的Git Worktree命令请参考：[Git Worktree命令手册](./GIT_WORKTREE_MAIN_CLI_MANUAL.md)

常用命令：
```bash
# 查看状态
git status

# 添加文件
git add .

# 提交
DISABLE_DIR_STRUCTURE_CHECK=1 git commit -m "message"

# 推送到远程
git push origin <branch>
```

---

## 3️⃣ 自测验证阶段

### 3.1 功能验证

对照TASK.md中的验收标准逐项检查：

```markdown
### T+Xh (YYYY-MM-DD HH:MM)
- ✅ 功能自测完成
  - [x] 验收标准1: [具体描述] ✓ 通过
  - [x] 验收标准2: [具体描述] ✓ 通过
  - [x] 验收标准3: [具体描述] ✓ 通过
```

### 3.2 集成测试

确保与依赖的CLI/模块能够正常工作:

```bash
# 后端API测试
curl -X GET http://localhost:8000/api/endpoint

# 前端功能测试
npm run dev
# 手动测试或运行E2E测试
npm run test:e2e
```

---

## 4️⃣ Git提交阶段

### 4.1 提交前检查清单

- [ ] 代码通过所有测试 (`pytest` / `npm run test`)
- [ ] 代码质量检查通过 (`ruff` / `npm run lint`)
- [ ] 新增功能有对应的测试
- [ ] 复杂逻辑有注释说明
- [ ] 没有调试代码（console.log, print等）
- [ ] TASK-REPORT.md已更新

### 4.2 Git提交流程

#### 步骤1: 查看修改状态

```bash
cd /opt/claude/mystocks_<phase>_<name>
git status
```

#### 步骤2: 添加文件到暂存区

```bash
# 添加所有修改
git add .

# 或选择性添加
git add src/ tests/ TASK-REPORT.md
```

#### 步骤3: 创建提交

```bash
# 使用DISABLE_DIR_STRUCTURE_CHECK=1禁用目录结构检查
DISABLE_DIR_STRUCTURE_CHECK=1 git commit -m "$(cat <<'EOF'
feat: 简短描述本次改动（不超过50字符）

详细说明本次改动的内容:

- 实现了XX功能
- 修复了XX问题
- 添加了XX测试

关联任务: [任务编号]
验收标准: [X] 标准1 [X] 标准2 [ ] 标准3

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

**提交消息规范**:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type类型**:
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `test`: 测试相关
- `refactor`: 重构代码
- `chore`: 构建/工具链相关

**示例**:

```bash
# 功能开发
git commit -m "feat(kline): add ProKLineChart component with basic rendering

- Implement ProKLineChart.vue with klinecharts 9.6.0
- Add responsive layout for mobile/desktop
- Integrate with backend API for market data

Task: T3.1
Acceptance: [x] Basic rendering [x] Responsive [ ] Indicator overlay"

# Bug修复
git commit -m "fix(gpu): resolve memory leak in performance collector

- Fixed unclosed database connection in PerformanceCollector
- Added proper cleanup in __exit__ method
- Verified with memory profiling tools

Fixes: #123"

# 文档更新（更新TASK-REPORT.md）
git commit -m "docs: update TASK-REPORT progress to T+4h

- Completed: T3.1
- Current: T3.2 (50% progress)
- Blockers: None"
```

#### 步骤4: 推送到远程分支

```bash
# 首次推送（设置上游分支）
git push -u origin phase3-frontend-optimization

# 后续推送
git push
```

### 4.3 提交频率建议

- ✅ **小步提交**: 每完成一个子功能就提交
- ✅ **频繁提交**: 至少每天一次
- ✅ **原子提交**: 每次提交只包含一个逻辑改动
- ❌ **避免**: 积累大量改动后才一次性提交

**示例**:
```
✅ 好的实践:
  - Commit 1: 添加基础组件结构
  - Commit 2: 实现K线图渲染
  - Commit 3: 添加缩放功能
  - Commit 4: 添加平移功能
  - Commit 5: 编写单元测试

❌ 不好的实践:
  - Commit 1: 完成所有功能（1000+行代码）
```

---

## 5️⃣ 更新TASK-REPORT阶段

### 5.1 更新进度报告

在每次提交后，更新TASK-REPORT.md的进度章节。

> ℹ️ **重要提示**: 你的 `TASK-REPORT.md` 会被主 CLI 定期同步到 `/multi-cli-tasks/<your_worktree>/` 运营中心。这是你工作成果的唯一**永久记录**。请务必认真填写，它将在 Worktree 删除后作为你的绩效凭证保留。

```markdown
### T+Xh (YYYY-MM-DD HH:MM)
- ✅ [任务编号] [任务名称] 已完成
  - Git提交: abc1234
  - 验收标准: [x] 全部通过
  - 测试覆盖: 85%
  - 性能指标: 达标

- 📝 当前任务: [下一个任务编号]
- ⏳ 预计完成: YYYY-MM-DD
```

### 5.2 提交TASK-REPORT.md更新

```bash
git add TASK-REPORT.md
git commit -m "docs: update TASK-REPORT progress to T+Xh"
git push
```

### 5.3 多阶段任务的报告管理

**第一阶段完成时**:
```bash
# 1. 生成完成报告
cat > TASK-1-REPORT.md << 'EOF'
# 第一阶段完成报告

**Worker CLI**: CLI-X
**任务文档**: TASK-1.md
**报告文档**: TASK-1-REPORT.md
**完成时间**: YYYY-MM-DD HH:MM

---

## ✅ 验收标准

- [x] 标准1: 描述完成情况
- [x] 标准2: 描述完成情况
- [x] 标准3: 描述完成情况

---

## 📦 交付物

- 代码: X个文件，Y行代码
- 测试: X个测试用例，通过率Y%
- 文档: X个文档

---

## 📈 工作量

- 预计: X小时
- 实际: Y小时
- 差异: ±Z小时

---

## ✅ 下一步

等待主CLI验收，然后开始第二阶段
EOF

# 2. 提交完成报告
git add TASK-1-REPORT.md
git commit -m "docs: phase 1 completion report"
git push

# 3. 等待主CLI下发第二阶段任务
```

**第二阶段开始时**:
```bash
# 主CLI下发TASK-2.md后，开始第二阶段
cat TASK-2.md
cat > TASK-REPORT.md << 'EOF'
# CLI-X 第二阶段进度报告

**Worker CLI**: CLI-X
**任务文档**: TASK-2.md
**报告文档**: TASK-2-REPORT.md
**当前阶段**: T+0h
**报告时间**: YYYY-MM-DD HH:MM
...
EOF
```

---

## 6️⃣ 完成确认阶段

### 6.1 单个任务完成标准

一个任务被认为"完成"需要满足:

- ✅ 所有验收标准通过
- ✅ 代码已提交到Git
- ✅ 测试覆盖率达标（后端>80%, 前端>70%）
- ✅ 代码质量检查通过（Pylint>8.0, 无lint错误）
- ✅ TASK-REPORT.md已更新（进度+任务状态）
- ✅ 文档完整（API文档、组件说明等）
- ✅ 生成TASK-*-REPORT.md（完成报告）

### 6.2 CLI整体完成标准

整个CLI被认为"完成"需要满足:

- ✅ 所有阶段任务已完成
- ✅ 代码已推送到远程分支
- ✅ 所有完成报告已生成（TASK-1-REPORT.md, TASK-2-REPORT.md等）
- ✅ 通过主CLI的验收测试
- ✅ 等待主CLI合并到main分支（Worker CLI不执行合并）

### 6.3 等待主CLI验收

Worker CLI完成所有工作后：

```bash
# 1. 确认所有代码已推送
git status
git push

# 2. 生成最终完成报告
cat > TASK-X-FINAL-REPORT.md << 'EOF'
# CLI-X 最终完成报告

**Worker CLI**: CLI-X
**所有阶段完成**: 2025-12-30 HH:MM

---

## ✅ 所有阶段总结

- 阶段1: ✅ 完成 (TASK-1-REPORT.md)
- 阶段2: ✅ 完成 (TASK-2-REPORT.md)
- 阶段3: ✅ 完成 (TASK-3-REPORT.md)

---

## 📦 总体交付物

- 代码: X个文件，Y行代码
- 测试: X个测试用例，通过率Y%
- 文档: X个文档

---

## ✅ 等待主CLI验收

请主CLI验收所有交付物并合并到main分支
EOF

git add TASK-X-FINAL-REPORT.md
git commit -m "docs: final completion report"
git push
```

---

## 7️⃣ 常见问题处理

### Q1: 如果遇到阻塞问题怎么办？

1. 在TASK-REPORT.md中记录:
   ```markdown
   🚧 阻塞问题:
   - 等待CLI-2的API契约定义 (预计明天完成)
   - 缺少XX文档，需要主CLI提供
   ```

2. 尝试解决（可并行推进其他任务）
3. 超过4小时无法解决，报告主CLI

### Q2: 如果发现任务定义不合理怎么办？

1. 在TASK-REPORT.md中记录问题
2. 提出调整建议
3. 继续推进可执行的部分
4. 等待主CLI确认调整

### Q3: 如果验收标准不清楚怎么办？

1. 查阅相关的技术文档
2. 参考类似的已完成任务
3. 在TASK-REPORT.md中记录疑问
4. 向主CLI寻求澄清

### Q4: Git提交遇到pre-commit hook失败怎么办？

```bash
# 查看hook失败原因
git commit

# 修复问题后重新提交
# 如果是目录结构检查问题，使用:
DISABLE_DIR_STRUCTURE_CHECK=1 git commit ...

# 如果是代码格式问题，运行:
ruff check . --fix
black .
git add .
git commit
```

### Q5: 多阶段任务如何管理？

参考文档：[任务文档模板-多阶段任务管理](./TASK_TEMPLATE.md#part-c-多阶段任务管理)

简述：
1. 第一阶段：TASK-1.md → TASK-1-REPORT.md
2. 第一阶段完成后，重命名TASK-1.md为TASK-1-completed.md
3. 主CLI下发第二阶段：TASK-2.md
4. 重复上述流程

---

## 8️⃣ 主CLI的职责

主CLI应该:

1. **非侵入式监控**: 通过监控脚本被动采集数据
2. **及时响应**: Worker CLI报告阻塞问题后24小时内回应
3. **质量把关**: 合并前进行代码审查和测试验证
4. **协调资源**: 帮助解决跨CLI的依赖问题
5. **文档维护**: 更新总体进度和里程碑状态

主CLI工作流程参考：[主CLI工作规范](./MAIN_CLI_WORKFLOW_STANDARDS.md)

---

## 9️⃣ 快速参考

### 每日工作流程

```bash
# 早上启动工作
cd /opt/claude/mystocks_<phase>_<name>
git pull  # 拉取最新代码
cat TASK.md  # 查看任务
cat TASK-REPORT.md  # 查看当前进度

# 开发过程中
vim src/feature.py
pytest tests/ -xvs  # 测试
git add .
git commit  # 频繁提交

# 晚上结束工作
vim TASK-REPORT.md  # 更新进度
git add TASK-REPORT.md
git commit -m "docs: update daily progress"
git push  # 推送到远程
```

### 提交消息模板

```bash
# 功能开发
git commit -m "feat(scope): description

- Implementation detail 1
- Implementation detail 2

Task: TX.Y
Acceptance: [x] C1 [x] C2 [ ] C3"

# Bug修复
git commit -m "fix(scope): description

- Root cause analysis
- Fix implementation
- Verification steps

Fixes: #issue"

# 文档更新（更新TASK-REPORT.md）
git commit -m "docs: update TASK-REPORT progress to T+Xh

- Completed: TX.Y
- Current: TZ.A
- Blockers: None"

# 阶段完成
git commit -m "docs: phase X completion report

- All acceptance criteria met
- Tests: 100% pass rate
- Code coverage: 90%"
```

### 常用Git命令速查

详细命令参考：[Git Worktree命令手册](./GIT_WORKTREE_MAIN_CLI_MANUAL.md)

```bash
# 查看状态
git status

# 查看分支
git branch

# 添加文件
git add .
git add <file>

# 提交
DISABLE_DIR_STRUCTURE_CHECK=1 git commit -m "message"

# 推送
git push origin <branch>

# 拉取
git pull origin <branch>
```

---

## 🔗 相关文档

### 核心文档
- [任务文档模板](./templates/TASK_TEMPLATE.md) - TASK.md和TASK-REPORT.md模板
- [主CLI工作规范](./MAIN_CLI_WORKFLOW.md) - 主CLI工作流程
- [协作冲突预防](./CONFLICT_PREVENTION.md) - 冲突处理

### Git命令参考
- [Git Worktree命令手册](./GIT_WORKTREE_MAIN_CLI_MANUAL.md) - 完整的Git Worktree命令

### 快速参考
- [Git远程名称标准](./GIT_REMOTE_NAME_STANDARD.md) - 远程配置（统一使用 origin）
- [主CLI工作规范-快速参考](./MAIN_CLI_WORKFLOW.md#快速参考)

---

**文档版本**: v2.0
**最后更新**: 2025-12-30
**维护者**: Main CLI
**适用于**: 所有Worker CLI
