# Worker CLI 工作流程指南

本指南适用于所有Worker CLI，规定了从任务开始到最终合并的完整工作流程。

---

## 📋 工作流程总览

```
1. 任务启动 → 2. 开发实现 → 3. 自测验证 → 4. Git提交 → 5. 更新README → 6. 完成确认
```

---

## 1️⃣ 任务启动阶段

### 1.1 确认任务理解

- ✅ 仔细阅读README中的任务描述
- ✅ 理解验收标准（Acceptance Criteria）
- ✅ 确认依赖关系和前置条件
- ✅ 如有疑问，在README中记录问题并报告主CLI

### 1.2 创建进度跟踪章节

在README.md中添加（如果还没有）:

```markdown
## 进度更新

### T+0h (YYYY-MM-DD HH:MM)
- ✅ 任务启动
- 📝 当前任务: [任务编号] [任务名称]
- ⏳ 预计完成时间: YYYY-MM-DD
- 🚧 阻塞问题: 无（如有请记录）
```

---

## 2️⃣ 开发实现阶段

### 2.1 开发原则

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

---

## 3️⃣ 自测验证阶段

### 3.1 功能验证

对照README中的验收标准逐项检查:

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
- [ ] README进度已更新

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
git add src/ tests/ README.md
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

# 文档更新
git commit -m "docs(readme): update progress section with T3.1 completion

Task: T3.1
Status: ✅ Complete"
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

## 5️⃣ 更新README阶段

### 5.1 更新进度章节

在每次提交后，更新README的进度章节:

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

### 5.2 更新任务完成状态

在README的任务列表中标记完成:

```markdown
### T3.1 专业K线图组件 (12-15天)

**状态**: ✅ 完成 (T+24h)

**验收标准**:
- [x] 基础K线图渲染（开盘/收盘/最高/最低）
- [x] 支持多时间周期切换（日/周/月）
- [x] 响应式布局（移动端适配）
- [x] 性能优化：60fps流畅渲染

**Git提交**:
- abc1234: Implement ProKLineChart.vue
- def5678: Add responsive layout
- ghi9012: Performance optimization

**测试**: ✅ 单元测试 + E2E测试通过
```

---

## 6️⃣ 完成确认阶段

### 6.1 单个任务完成标准

一个任务被认为"完成"需要满足:

- ✅ 所有验收标准通过
- ✅ 代码已提交到Git
- ✅ 测试覆盖率达标（后端>80%, 前端>70%）
- ✅ 代码质量检查通过（Pylint>8.0, 无lint错误）
- ✅ README已更新（进度+任务状态）
- ✅ 文档完整（API文档、组件说明等）

### 6.2 CLI整体完成标准

整个CLI被认为"完成"需要满足:

- ✅ 所有任务已完成
- ✅ 代码已推送到远程分支
- ✅ 通过主CLI的验收测试
- ✅ 代码审查通过（如有）
- ✅ 文档齐全（README + 技术文档）
- ✅ 准备合并到main分支

### 6.3 合并到main分支

**合并条件**:
- ✅ Round 1所有CLI完成（CLI-1, 2, 5, 6）
- ✅ 主CLI确认可以合并
- ✅ 集成测试通过

**合并流程**:

```bash
# 1. 切换到main分支
cd /opt/claude/mystocks_spec
git checkout main

# 2. 拉取最新代码
git pull mystocks main

# 3. 合并CLI分支
git merge phase3-frontend-optimization --no-ff

# 4. 运行完整测试套件
pytest tests/
npm run test

# 5. 推送到远程
git push mystocks main
```

---

## 7️⃣ 常见问题处理

### Q1: 如果遇到阻塞问题怎么办？

1. 在README的进度章节中记录:
   ```markdown
   🚧 阻塞问题:
   - 等待CLI-2的API契约定义 (预计明天完成)
   - 缺少XX文档，需要主CLI提供
   ```

2. 尝试解决（可并行推进其他任务）
3. 超过4小时无法解决，报告主CLI

### Q2: 如果发现任务定义不合理怎么办？

1. 在README中记录问题
2. 提出调整建议
3. 继续推进可执行的部分
4. 等待主CLI确认调整

### Q3: 如果验收标准不清楚怎么办？

1. 查阅相关的技术文档
2. 参考类似的已完成任务
3. 在README中记录疑问
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

---

## 8️⃣ 主CLI的职责

主CLI应该:

1. **非侵入式监控**: 通过监控脚本被动采集数据
2. **及时响应**: Worker CLI报告阻塞问题后24小时内回应
3. **质量把关**: 合并前进行代码审查和测试验证
4. **协调资源**: 帮助解决跨CLI的依赖问题
5. **文档维护**: 更新总体进度和里程碑状态

---

## 9️⃣ 快速参考

### 每日工作流程

```bash
# 早上启动工作
cd /opt/claude/mystocks_<phase>_<name>
git pull  # 拉取最新代码
vim README.md  # 查看今日任务

# 开发过程中
vim src/feature.py
pytest tests/ -xvs  # 测试
git add .
git commit  # 频繁提交

# 晚上结束工作
vim README.md  # 更新进度
git add README.md
git commit -m "docs(readme): update daily progress"
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

# 文档更新
git commit -m "docs(readme): update progress to T+Xh

- Completed: TX.Y
- Current: TZ.A
- Blockers: None"
```

---

**文档版本**: v1.0
**最后更新**: 2025-12-29
**维护者**: Main CLI
**适用于**: 所有Worker CLI
