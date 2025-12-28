# MyStocks项目 Worktree 管理方法

**文档版本**: v1.0
**创建时间**: 2025-12-28
**适用场景**: MyStocks项目多CLI协作开发
**基于**: Phase 6实际协作经验总结

---

## 📋 目录

1. [核心原则](#核心原则)
2. [角色定义](#角色定义)
3. [主CLI工作范围](#主cli工作范围)
4. [Worker CLI工作范围](#worker-cli工作范围)
5. [主CLI工作流程](#主cli工作流程)
6. [主次CLI交互规则](#主次cli交互规则)
7. [典型场景处理](#典型场景处理)
8. [反模式警告](#反模式警告)

---

## 核心原则

### 🎯 唯一原则

**主CLI不代替Worker CLI完成任务**

主CLI的核心职责是**协调和监控**，而不是**执行**。只有在以下情况才出手帮助：
1. Worker CLI遇到**无法独立解决**的阻塞问题
2. Worker CLI**明确请求**帮助
3. 发现Worker CLI**偏离任务目标**需要纠正

### 📊 协作模型

```
┌─────────────────────────────────────────────────────────────┐
│                        主CLI (Manager)                       │
│  职责: 任务分配、进度监控、问题协调、集成管理                   │
│  工作目录: /opt/claude/mystocks_spec (main分支)              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Worker CLI-1│  │ Worker CLI-2│  │ Worker CLI-3│  ...    │
│  │  专注领域A  │  │  专注领域B  │  │  专注领域C  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                             │
│  原则: 每个Worker CLI独立工作，主CLI只监控和协调              │
└─────────────────────────────────────────────────────────────┘
```

---

## 角色定义

### 主CLI (Manager)

**定位**: 项目协调者，不是执行者

**核心职责**:
1. **任务规划**: 将大任务拆分为可并行执行的子任务
2. **Worktree管理**: 创建、监控、清理worktree
3. **进度跟踪**: 定期检查各Worker CLI的进度
4. **问题协调**: 协调解决Worker CLI间的依赖和冲突
5. **集成管理**: 验证交付物，合并分支，生成报告

**不应该做的事** ❌:
- ❌ 代替Worker CLI编写代码
- ❌ 主动修改Worker CLI worktree中的文件
- ❌ 在Worker CLI未请求的情况下提供技术方案
- ❌ 过度干预Worker CLI的工作方式

### Worker CLI (执行者)

**定位**: 专注领域的执行者

**核心职责**:
1. **独立执行**: 在分配的worktree中独立完成任务
2. **自主决策**: 选择技术实现方案，无需等待主CLI批准
3. **进度汇报**: 定期更新README.md中的进度
4. **问题报告**: 遇到阻塞问题时及时报告主CLI

**应该做的事** ✅:
- ✅ 独立完成任务，不依赖主CLI的具体指导
- ✅ 在README.md中记录工作进展
- ✅ 遇到阻塞问题时主动联系主CLI
- ✅ 完成任务后提交到分配的分支

---

## 主CLI工作范围

### 1. 任务分配阶段 (T+0h)

**职责**: 为每个Worker CLI准备独立的工作环境

**具体任务**:
```bash
# 步骤1: 创建worktree
git worktree add /opt/claude/mystocks_phase6_monitor phase6-monitoring-verification
git worktree add /opt/claude/mystocks_phase6_e2e phase6-e2e-testing
git worktree add /opt/claude/mystocks_phase6_cache phase6-cache-optimization
git worktree add /opt/claude/mystocks_phase6_docs phase6-documentation

# 步骤2: 创建README任务文档
cat > /opt/claude/mystocks_phase6_monitor/README.md <<EOF
# Phase 6: 监控系统验证

## 任务目标
[清晰描述任务目标]

## 验收标准
- [ ] 标准1
- [ ] 标准2

## 完成时间
预计: T+6h

## 问题报告
如遇阻塞问题，联系主CLI。
EOF

# 步骤3: 通知Worker CLI开始工作
```

**关键点**:
- ✅ README文档必须清晰、具体、可执行
- ✅ 包含明确的验收标准
- ✅ 指定预计完成时间
- ❌ 不要指定具体的技术实现方案（留给Worker CLI自主决策）

### 2. 进度监控阶段 (T+0h → T+9h)

**职责**: 定期检查进度，不干预具体工作

**监控命令**:
```bash
# 每小时执行一次检查

# 1. 检查Git状态
git worktree list

# 2. 检查各分支的提交
git log --oneline --graph --all -10

# 3. 检查各CLI的README更新
for dir in /opt/claude/mystocks_phase6_*; do
    echo "=== $dir ==="
    tail -n 20 $dir/README.md  # 查看README最后20行（进度更新）
    echo ""
done

# 4. 统计修改文件数量（用于评估活跃度）
for dir in /opt/claude/mystocks_phase6_*; do
    cd $dir
    echo "=== $dir ==="
    git status --short | wc -l
    cd -
done
```

**监控指标**:
- **文件修改数量**: 评估工作活跃度
- **提交频率**: 评估工作进展
- **README更新**: 评估进度汇报情况

**生成进度报告**:
```bash
# 每2小时生成一次状态报告
cat > /tmp/phase6_progress_T+2h.md <<EOF
# Phase 6 进度报告 (T+2h)

## 总体进度
- 已完成: 1/4 (25%)
- 进行中: 3/4 (75%)

## CLI状态

### CLI-1: 监控系统验证
- 状态: 🔄 进行中
- 进度: ~30%
- 修改文件: 18个
- 最新提交: abc1234 - 添加Prometheus验证

### CLI-2: E2E测试
- 状态: ⚠️ 阻塞
- 进度: ~10%
- 阻塞问题: Pylint修改未提交
- 建议: 立即stash修改

## 下一步行动
- 主CLI: 继续监控CLI-1和CLI-3进度
- CLI-2: 清理工作目录后继续测试
EOF
```

**关键点**:
- ✅ 只读取状态，不修改Worker CLI的文件
- ✅ 发现问题后通过README更新或沟通解决
- ❌ 不要直接修改Worker CLI worktree中的代码

### 3. 问题协调阶段 (响应式)

**职责**: 协调解决Worker CLI间的依赖和冲突

**触发条件**:
1. Worker CLI报告阻塞问题
2. 发现多个CLI修改同一文件
3. 任务依赖关系需要协调

**处理流程**:
```bash
# 场景: CLI-2报告缺少E2E测试文件

# 步骤1: 主CLI评估问题
cd /opt/claude/mystocks_spec
git status  # 检查主分支是否有该文件

# 步骤2: 确认问题根因
ls -lh tests/e2e/test_architecture_optimization_e2e.py
# 发现: 文件存在但未提交到Git

# 步骤3: 提供解决方案（不是直接执行）
cat > /tmp/cli2_solution.md <<EOF
# CLI-2 问题解决方案

## 问题
E2E测试文件未同步到phase6-e2e-testing分支

## 根因
主分支的E2E测试文件未提交，导致创建worktree时缺失

## 解决方案
主CLI已将文件同步到CLI-2 worktree，请验证：
1. 文件已复制到 /opt/claude/mystocks_phase6_e2e/tests/e2e/
2. 后端修复已同步到 /opt/claude/mystocks_phase6_e2e/web/backend/
3. 请验证文件内容并继续测试

## 下一步
CLI-2: 启动后端服务并运行E2E测试
EOF

# 步骤4: 通知CLI-2（通过README更新或直接沟通）
```

**关键点**:
- ✅ 提供解决方案，让Worker CLI自主执行
- ✅ 记录问题和解决方案，便于后续回顾
- ❌ 不要直接修改Worker CLI的代码（除非紧急且获得许可）

### 4. 集成管理阶段 (T+9h → T+10h)

**职责**: 验证交付物，合并分支

**验证清单**:
```bash
# 检查每个CLI的交付物

# CLI-1: 监控系统验证
[ ] README.md 存在
[ ] MONITORING_VERIFICATION_REPORT.md 存在
[ ] 截图目录存在
[ ] Git提交成功
git log phase6-monitoring-verification --oneline -3

# CLI-2: E2E测试
[ ] README.md 存在
[ ] E2E_TEST_REPORT.md 存在
[ ] test-results/ 目录存在
[ ] 测试通过率 = 100%
cd /opt/claude/mystocks_phase6_e2e
cat E2E_TEST_REPORT.md | grep "通过率"

# CLI-3: 缓存优化
[ ] README.md 存在
[ ] CACHE_OPTIMIZATION_REPORT.md 存在
[ ] 性能报告存在
[ ] Git提交成功

# CLI-4: 文档
[ ] README.md 存在
[ ] DOCUMENTATION_COMPLETION_REPORT.md 存在
[ ] CHANGELOG.md 存在
[ ] 文档目录完整
```

**合并分支**:
```bash
# 步骤1: 切换到main分支
git checkout main

# 步骤2: 验证所有分支的提交
git branch -vv

# 步骤3: 按顺序合并分支
git merge phase6-monitoring-verification --no-ff -m "Merge phase6-monitoring-verification"
git merge phase6-e2e-testing --no-ff -m "Merge phase6-e2e-testing"
git merge phase6-cache-optimization --no-ff -m "Merge phase6-cache-optimization"
git merge phase6-documentation --no-ff -m "Merge phase6-documentation"

# 步骤4: 推送到远程
git push origin main

# 步骤5: 清理worktree
git worktree remove /opt/claude/mystocks_phase6_monitor
git worktree remove /opt/claude/mystocks_phase6_e2e
git worktree remove /opt/claude/mystocks_phase6_cache
git worktree remove /opt/claude/mystocks_phase6_docs
```

**关键点**:
- ✅ 验证交付物完整性后再合并
- ✅ 使用 `--no-ff` 保留分支历史
- ❌ 不要合并未经验证的分支

---

## Worker CLI工作范围

### 1. 任务理解阶段 (T+0h)

**职责**: 理解任务目标，规划工作方式

**行动清单**:
```bash
# 步骤1: 阅读README.md
cd /opt/claude/mystocks_phase6_<task>
cat README.md

# 步骤2: 理解验收标准
# 确认以下内容：
# - 任务目标是否清晰？
# - 验收标准是否具体？
# - 预计完成时间是否合理？

# 步骤3: 如果有疑问，联系主CLI
# 通过README更新或直接沟通
```

**关键点**:
- ✅ 充分理解任务后再开始
- ✅ 有疑问及时提出，不要猜测

### 2. 独立执行阶段 (T+0h → T+8.5h)

**职责**: 在worktree中独立完成任务

**工作流程**:
```bash
# 步骤1: 开始工作
cd /opt/claude/mystocks_phase6_<task>

# 步骤2: 选择技术方案（自主决策）
# 例如：
# - 选择测试框架
# - 选择实现方式
# - 选择工具库

# 步骤3: 执行工作
# 编写代码、运行测试、生成文档...

# 步骤4: 定期更新README进度
# 在README.md中添加：
# ## 进度更新 (T+2h)
# - ✅ 完成子任务1
# - 🔄 进行中: 子任务2
# - ⏳ 待开始: 子任务3

# 步骤5: 遇到问题时的处理
# 方案A: 独立解决（如果能够）
# 方案B: 联系主CLI（如果无法独立解决）
```

**关键点**:
- ✅ 自主选择技术方案
- ✅ 定期更新进度
- ✅ 遇到阻塞问题及时报告

### 3. 提交阶段 (T+9h)

**职责**: 提交工作成果到分支

**提交流程**:
```bash
# 步骤1: 验证完成度
# 对照README中的验收标准检查

# 步骤2: 生成完成报告
cat > COMPLETION_REPORT.md <<EOF
# Phase 6: <任务名称> 完成报告

## 完成时间
2025-12-28 T+9h

## 完成情况
- ✅ 验收标准1: 已完成
- ✅ 验收标准2: 已完成
- ⚠️  验收标准3: 部分完成（说明原因）

## 交付物
1. 文件1: 路径
2. 文件2: 路径
3. 报告: 路径

## 测试结果
- 测试通过率: 100%
- 性能指标: 达标

## 问题记录
[记录遇到的问题和解决方案]
EOF

# 步骤3: Git提交
git add .
git commit -m "feat(phase6): 完成<任务名称>

- 完成所有验收标准
- 测试通过率100%
- 生成完成报告

🤖 Generated with Claude Code
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# 步骤4: 推送到远程（如果需要）
git push origin phase6-<task-name>

# 步骤5: 通知主CLI
# 更新README.md标记为完成
```

**关键点**:
- ✅ 验证所有验收标准
- ✅ 生成完整的完成报告
- ✅ 清晰的Git提交信息

---

## 主CLI工作流程

### 完整时间线 (以Phase 6为例)

```bash
# ============================================
# T+0h: 任务分配阶段
# ============================================
主CLI:
  1. 创建4个worktree
  2. 创建4个README任务文档
  3. 通知Worker CLI开始工作

# ============================================
# T+0h → T+9h: 进度监控阶段
# ============================================
主CLI (每2小时执行一次):
  1. 检查所有worktree状态
  2. 统计修改文件数量
  3. 查看各分支提交情况
  4. 生成进度报告

Worker CLI (持续工作):
  1. 在各自worktree中独立工作
  2. 定期更新README进度
  3. 遇到问题报告主CLI

# ============================================
# T+2h: 第一次进度检查
# ============================================
主CLI:
  - 检查发现CLI-2有190个未暂存文件（Pylint修改）
  - 生成T+2h进度报告
  - 建议CLI-2: stash修改后继续

# ============================================
# T+6h: CLI-1预计完成里程碑
# ============================================
主CLI:
  - 验证CLI-1的交付物
  - 检查验收标准
  - 确认是否可以提前完成

# ============================================
# T+8h: CLI-2预计完成里程碑
# ============================================
主CLI:
  - 验证CLI-2的E2E测试结果
  - 检查测试通过率（目标100%）
  - 确认测试报告完整性

# ============================================
# T+9h: 所有CLI完成验证
# ============================================
主CLI:
  1. 验证所有CLI的交付物
  2. 检查所有Git提交
  3. 确认无遗留问题

# ============================================
# T+9.5h: 集成阶段
# ============================================
主CLI:
  1. 合并所有分支到main
  2. 解决冲突（如果有）
  3. 推送到远程

# ============================================
# T+10h: 报告阶段
# ============================================
主CLI:
  1. 生成Phase 6完成报告
  2. 清理所有worktree
  3. 总结经验教训
```

---

## 主次CLI交互规则

### 规则1: 主CLI只监控不干预

**描述**: 主CLI在进度监控阶段只读取状态，不修改Worker CLI的文件

**正确做法** ✅:
```bash
# 主CLI检查CLI-2进度
cd /opt/claude/mystocks_phase6_e2e
git status --short  # 只读取状态
tail -n 20 README.md # 只查看进度更新
```

**错误做法** ❌:
```bash
# 主CLI直接修改CLI-2的代码
cd /opt/claude/mystocks_phase6_e2e
vim tests/e2e/test_architecture_optimization_e2e.py  # ❌ 不要这样做
```

### 规则2: Worker CLI主动汇报进度

**描述**: Worker CLI需要定期在README.md中更新进度

**正确做法** ✅:
```markdown
# CLI-2 README.md

## 进度更新 (T+2h)
- ✅ 完成Pylint清理
- ✅ 验证20个E2E测试文件
- 🔄 正在实现5个新API端点
- ⏳ 待运行完整测试套件

## 预计完成时间
T+8h (按计划)

## 问题
当前无阻塞问题
```

**错误做法** ❌:
```markdown
# CLI-2 README.md

（没有任何进度更新，主CLI无法了解工作状态）
```

### 规则3: 问题报告流程

**描述**: Worker CLI遇到阻塞问题时，需要及时报告主CLI

**问题级别定义**:

| 级别 | 定义 | 示例 | 处理方式 |
|------|------|------|----------|
| 🟢 信息级 | 不影响工作的小问题 | 代码风格建议 | Worker CLI独立处理 |
| 🟡 警告级 | 可能影响进度 | 依赖版本冲突 | Worker CLI尝试解决，无法解决时报告主CLI |
| 🔴 阻塞级 | 完全无法继续工作 | 服务启动失败、测试环境崩溃 | 立即报告主CLI，请求帮助 |

**报告格式**:
```markdown
## 阻塞问题报告

**时间**: 2025-12-28 12:00
**CLI**: CLI-2 (E2E测试)
**级别**: 🔴 阻塞级

### 问题描述
后端服务无法启动，错误：
ModuleNotFoundError: No module named 'web.backend.app'

### 已尝试的解决方案
1. 检查import路径 - 确认路径错误
2. 尝试修改为相对导入 - 仍有其他错误

### 请求帮助
需要主CLI提供正确的后端服务配置或修复代码

### 附件
- 错误日志: /tmp/backend_error.log
- 相关文件: web/backend/app/schemas/backtest_schemas.py
```

**主CLI响应流程**:
```bash
# 主CLI收到问题报告后

# 步骤1: 评估问题严重程度
# 🔴 阻塞级 → 立即响应

# 步骤2: 提供解决方案
cat > /tmp/cli2_fix.md <<EOF
# CLI-2 后端启动问题解决方案

## 问题
ModuleNotFoundError: No module named 'web.backend.app'

## 根因
使用了绝对导入路径，应该使用相对导入

## 修复方案
修改文件: web/backend/app/schemas/backtest_schemas.py
行号: 15
修改前: from web.backend.app.mock.unified_mock_data import get_backtest_data
修改后: from app.mock.unified_mock_data import get_backtest_data

## 执行步骤
1. 应用修复
2. 重启后端服务
3. 验证服务正常启动
EOF

# 步骤3: 通知CLI-2
# 将解决方案文档路径告诉CLI-2

# 步骤4: 跟踪问题解决情况
# 等待CLI-2确认问题已解决
```

### 规则4: 技术方案自主决策

**描述**: Worker CLI有权自主选择技术实现方案，无需主CLI批准

**Worker CLI的权利** ✅:
- 选择测试框架（pytest vs unittest）
- 选择代码风格（函数式 vs 面向对象）
- 选择工具库（requests vs httpx）
- 选择实现方式（同步 vs 异步）

**主CLI不应该做的事** ❌:
- ❌ 指定具体的技术实现方案
- ❌ 要求Worker CLI使用特定的库或框架
- ❌ 审查Worker CLI的代码风格
- ❌ 干预Worker CLI的技术决策

**例外情况**:
- 技术方案影响其他CLI（需要主CLI协调）
- 技术方案违反项目架构原则（主CLI应该纠正）
- 技术方案引入安全风险（主CLI应该干预）

---

## 典型场景处理

### 场景1: 文件同步问题

**情况**: CLI-2报告缺少E2E测试文件

**Phase 6实际案例**:
```
背景:
- 主CLI之前在主分支创建了E2E测试文件
- 但文件未提交到Git
- CLI-2的worktree从主分支创建，缺少该文件

问题:
CLI-2无法运行E2E测试，因为测试文件缺失
```

**主CLI处理流程**:
```bash
# 步骤1: 确认问题
cd /opt/claude/mystocks_spec
ls -lh tests/e2e/test_architecture_optimization_e2e.py
# 文件存在但未提交

# 步骤2: 提供解决方案（不是直接执行）
cat > /tmp/cli2_sync_solution.md <<EOF
# CLI-2 文件同步解决方案

## 问题
phase6-e2e-testing分支缺少E2E测试文件

## 根因
主分支的E2E测试文件未提交到Git

## 解决方案
主CLI已将以下文件同步到CLI-2 worktree：
1. E2E测试文件 → /opt/claude/mystocks_phase6_e2e/tests/e2e/
2. 后端修复 → /opt/claude/mystocks_phase6_e2e/web/backend/

## 验证步骤
CLI-2请验证：
1. 文件已正确复制
2. 文件内容完整
3. 可以正常运行测试

## 下一步
CLI-2: 启动后端服务并运行E2E测试
EOF

# 步骤3: 执行文件同步（主CLI唯一的一次性操作）
cp /opt/claude/mystocks_spec/tests/e2e/test_architecture_optimization_e2e.py \
   /opt/claude/mystocks_phase6_e2e/tests/e2e/

cp /opt/claude/mystocks_spec/web/backend/app/schemas/backtest_schemas.py \
   /opt/claude/mystocks_phase6_e2e/web/backend/app/schemas/

# 步骤4: 通知CLI-2
echo "文件已同步，请CLI-2验证并继续测试"

# 步骤5: 记录到进度报告
# 在T+2.5h状态报告中记录此次同步操作
```

**关键点**:
- ✅ 主CLI只执行一次性文件同步
- ✅ 提供清晰的验证步骤
- ✅ 让CLI-2自主继续后续工作
- ❌ 不要代替CLI-2运行测试或修复测试失败

### 场景2: Pylint修改阻塞

**情况**: CLI-2有190个未暂存的Pylint修改，阻塞工作

**主CLI处理流程**:
```bash
# 步骤1: 检查CLI-2状态
cd /opt/claude/mystocks_phase6_e2e
git status --short | wc -l  # 190个文件

# 步骤2: 评估影响
# 190个文件会影响工作，但不属于E2E测试任务本身

# 步骤3: 提供建议（不是直接执行）
cat > /tmp/cli2_pylint_advice.md <<EOF
# CLI-2 Pylint修改阻塞建议

## 问题
190个文件有未暂存的Pylint修改

## 影响
- 无法清晰看到E2E测试相关的修改
- 可能干扰Git提交

## 建议方案
推荐使用git stash清理工作目录：

```bash
cd /opt/claude/mystocks_phase6_e2e
git stash save "WIP: Pylint自动修改 (有语法错误)"
git status --short  # 验证工作目录已清理
```

## 说明
- Pylint修改可以稍后统一处理
- 当前优先完成E2E测试任务
- 语法错误的修改不应提交

## 下一步
清理后继续E2E测试执行
EOF

# 步骤4: 更新进度报告
# 在T+2.5h状态报告中标记CLI-2为"阻塞中"
```

**CLI-2响应**:
```bash
# CLI-2执行建议
cd /opt/claude/mystocks_phase6_e2e
git stash save "WIP: Pylint自动修改 (有语法错误)"

# 验证清理结果
git status --short  # 0个文件（已清理）

# 更新README进度
echo "## 进度更新 (T+3h)" >> README.md
echo "- ✅ Pylint修改已清理" >> README.md
echo "- 🔄 开始运行E2E测试" >> README.md
```

**关键点**:
- ✅ 主CLI只提供建议，不直接执行stash
- ✅ 让CLI-2自主决定是否采纳建议
- ✅ CLI-2执行后更新进度，主CLI通过状态检查确认
- ❌ 不要主CLI直接执行git stash命令

### 场景3: 多CLI修改同一文件

**情况**: CLI-1和CLI-3都修改了`src/core/database_pool.py`

**主CLI处理流程**:
```bash
# 步骤1: 发现冲突
cd /opt/claude/mystocks_spec
git diff phase6-monitoring-verification phase6-cache-optimization -- src/core/database_pool.py
# 显示两个分支对同一文件的不同修改

# 步骤2: 分析修改内容
# CLI-1: 添加监控日志
# CLI-3: 优化连接池配置
# 两个修改不冲突，可以合并

# 步骤3: 协调合并策略
cat > /tmp/merge_strategy.md <<EOF
# 多CLI修改同一文件的合并策略

## 冲突文件
src/core/database_pool.py

## 修改内容
CLI-1 (监控验证):
- 添加性能监控日志
- 添加连接池状态查询接口

CLI-3 (缓存优化):
- 优化连接池大小配置
- 添加连接超时设置

## 合并策略
两个修改不冲突，采用"both"策略：
1. 保留CLI-1的监控日志
2. 保留CLI-3的优化配置
3. 合并时保留两个分支的所有修改

## 执行方式
主CLI在集成阶段手动合并，保留所有修改
EOF

# 步骤4: 在集成阶段处理
# 等到T+9h集成阶段时，主CLI手动合并这两个分支
git checkout main
git merge phase6-monitoring-verification --no-ff
git merge phase6-cache-optimization --no-ff
# 手动解决冲突，保留两个分支的修改
```

**关键点**:
- ✅ 主CLI在集成阶段统一处理冲突
- ✅ 提前分析冲突，准备合并策略
- ✅ 尽量保留所有CLI的修改（不丢失工作）
- ❌ 不要在Worker CLI工作期间干预

---

## 反模式警告

### 反模式1: 过度干预 ❌

**描述**: 主CLI主动修改Worker CLI的代码

**错误示例**:
```bash
# 主CLI看到CLI-2的测试代码有风格问题
cd /opt/claude/mystocks_phase6_e2e
vim tests/e2e/test_architecture_optimization_e2e.py  # ❌ 直接修改

# 提交修改
git add .
git commit -m "fix: 修复测试代码风格"  # ❌ 代替CLI-2提交
```

**正确做法**:
```bash
# 主CLI只记录问题，不直接修改
cat > /tmp/cli2_code_review.md <<EOF
# CLI-2 代码审查建议

## 问题
测试代码中有风格问题：
- 函数名过长
- 缺少类型注解

## 建议
CLI-2可以在完成任务后优化代码风格

## 说明
当前优先完成功能测试，代码风格可以后续优化
EOF

# 通知CLI-2（但不强制执行）
```

### 反模式2: 忽略阻塞 ❌

**描述**: Worker CLI遇到阻塞问题但不报告，主CLI也不过问

**错误示例**:
```markdown
# CLI-2 README.md (没有进度更新)
# Phase 6: E2E测试

## 任务目标
运行7个测试套件，达到100%通过率

（没有进度更新，主CLI不知道CLI-2已经阻塞3小时）
```

**正确做法**:
```markdown
# CLI-2 README.md
# Phase 6: E2E测试

## 任务目标
运行7个测试套件，达到100%通过率

## 进度更新 (T+2h)
- ✅ Pylint修改已清理
- ⚠️ 阻塞问题: 后端服务无法启动
  错误: ModuleNotFoundError: No module named 'web.backend.app'
  已尝试: 检查import路径，尝试修改为相对导入
  请求帮助: 需要主CLI提供正确的配置

## 预计完成时间
原计划T+8h，可能延迟到T+9h（取决于问题解决速度）
```

**主CLI响应**:
```bash
# 主CLI检查进度时发现阻塞
cd /opt/claude/mystocks_phase6_e2e
tail -n 20 README.md  # 看到"阻塞问题"报告

# 立即提供解决方案（参考"场景1"的处理流程）
```

### 反模式3: 技术方案强加 ❌

**描述**: 主CLI指定Worker CLI必须使用某种技术方案

**错误示例**:
```markdown
# 主CLI在README中指定技术方案
## 技术要求（强制）
- 必须使用pytest框架（不可以用unittest）
- 必须使用requests库（不可以用httpx）
- 必须使用函数式编程（不可以用类）
```

**正确做法**:
```markdown
# 主CLI在README中指定验收标准（不指定实现方式）
## 验收标准
- [ ] 所有7个测试套件通过（100%）
- [ ] 测试覆盖率 > 80%
- [ ] 生成测试报告（JSON格式）

## 技术建议（可选）
推荐使用pytest框架（但如果unittest更适合你的场景，也可以使用）
```

**关键区别**:
- ❌ "必须使用pytest" → 强制技术方案
- ✅ "推荐使用pytest" → 建议技术方案（Worker CLI可以自主决策）

### 反模式4: 缺少验收标准 ❌

**描述**: README中没有明确的验收标准，导致交付物质量不可控

**错误示例**:
```markdown
# CLI-2 README.md
# Phase 6: E2E测试

## 任务目标
运行测试，确保系统正常工作

（没有具体的验收标准，无法验证是否完成）
```

**正确做法**:
```markdown
# CLI-2 README.md
# Phase 6: E2E测试

## 任务目标
运行7个测试套件，验证系统功能

## 验收标准
- [ ] 所有7个测试套件通过（100%通过率）
- [ ] 测试覆盖率 > 80%
- [ ] 生成测试报告（test-results/目录）
- [ ] 性能基准测试通过（API响应 < 200ms p95）
- [ ] 生成E2E_TEST_REPORT.md完成报告

## 完成时间
预计T+8h

## 问题报告
如遇阻塞问题，联系主CLI。
```

---

## 附录: 快速参考

### 主CLI检查清单

**任务分配阶段**:
- [ ] 创建所有worktree
- [ ] 创建所有README任务文档
- [ ] README包含：任务目标、验收标准、完成时间、问题报告方式
- [ ] 通知Worker CLI开始工作

**进度监控阶段**:
- [ ] 每小时检查worktree状态
- [ ] 每2小时生成进度报告
- [ ] 发现问题后提供解决方案（不直接执行）
- [ ] 更新总体进度评估

**集成管理阶段**:
- [ ] 验证所有CLI的交付物
- [ ] 检查所有验收标准
- [ ] 合并所有分支到main
- [ ] 生成完成报告
- [ ] 清理所有worktree

### Worker CLI检查清单

**任务理解阶段**:
- [ ] 阅读并理解README
- [ ] 确认验收标准清晰
- [ ] 有疑问及时联系主CLI

**独立执行阶段**:
- [ ] 选择技术方案（自主决策）
- [ ] 在worktree中执行工作
- [ ] 定期更新README进度（每2小时）
- [ ] 遇到阻塞问题立即报告

**提交阶段**:
- [ ] 验证所有验收标准
- [ ] 生成完成报告
- [ ] Git提交到分支
- [ ] 通知主CLI

### 联系方式

**主CLI (Manager)**:
- 工作目录: `/opt/claude/mystocks_spec`
- 分支: `main`
- 职责: 整体协调和问题解决

**Worker CLIs**:
- CLI-1: `/opt/claude/mystocks_phase6_monitor` (监控验证)
- CLI-2: `/opt/claude/mystocks_phase6_e2e` (E2E测试)
- CLI-3: `/opt/claude/mystocks_phase6_cache` (缓存优化)
- CLI-4: `/opt/claude/mystocks_phase6_docs` (文档)

**问题报告流程**:
1. Worker CLI在README中更新进度和问题
2. 主CLI通过定期检查发现问题
3. 主CLI提供解决方案或协调资源
4. Worker CLI确认问题已解决

---

**文档版本**: v1.0
**最后更新**: 2025-12-28
**维护者**: Main CLI (Claude Code)
**基于**: Phase 6多CLI协作实际经验
