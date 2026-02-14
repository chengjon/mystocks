# 多CLI并行开发 - 进度监控与里程碑管理指南

**版本**: 2.0
**适用场景**: 任何使用Git Worktree进行多CLI并行协作的项目
**维护者**: Main CLI
**最后更新**: 2025-12-30

> **注**：本文档为通用指南，具体项目可根据实际情况调整监控周期和里程碑设置。

---

## 📊 一、进度监控机制

### 1.1 监控原则

**核心原则**:
- **非侵入式**: 不干扰Worker CLI的正常工作
- **状态驱动**: 通过README和Git状态被动获取进度
- **问题导向**: 只在发现阻塞或偏离目标时介入
- **定期报告**: 每日T+2h/T+6h生成进度快照

### 1.2 监控数据源

**主要数据来源**:
1. **Worktree README.md** - Worker CLI的进度自报告
2. **Git提交记录** - 实际代码变更
3. **文件修改时间戳** - 最后活动时间
4. **测试运行结果** - CI/CD状态

**被动获取方式**:
```bash
# 主CLI监控脚本 (每2小时运行一次)
#!/bin/bash
# scripts/monitoring/check_worker_progress.sh

# 项目根目录（根据实际项目配置）
PROJECT_ROOT="${PROJECT_ROOT:-/opt/claude/project_name}"

# Worktree配置（根据实际项目配置）
# 格式：worktree路径:CLI名称
WORKTREES=(
  "${PROJECT_ROOT}_feature_auth:CLI-1"
  "${PROJECT_ROOT}_feature_api:CLI-2"
  "${PROJECT_ROOT}_feature_db:CLI-3"
  # 根据实际worktree添加更多...
)

echo "=== 进度监控快照 ($(date)) ==="

for item in "${WORKTREES[@]}"; do
  IFS=':' read -r worktree cli_name <<< "$item"

  echo ""
  echo "## $cli_name ($worktree)"

  # 检查TASK-REPORT.md更新时间
  if [ -f "$worktree/TASK-REPORT.md" ]; then
    last_update=$(stat -c %y "$worktree/TASK-REPORT.md" | cut -d' ' -f1-2)
    echo "  📄 TASK-REPORT更新: $last_update"

    # 提取进度信息
    progress=$(grep -A 5 "## 进度" "$worktree/TASK-REPORT.md" | tail -n 3)
    echo "  📊 进度: $progress"
  else
    echo "  ⚠️  TASK-REPORT.md不存在"
  fi

  # 检查Git提交
  cd "$worktree" || continue
  last_commit=$(git log -1 --format="%h - %s (%ar)")
  echo "  🔧 最后提交: $last_commit"

  # 检查文件修改数
  modified_files=$(git status --short | wc -l)
  echo "  📝 未提交文件: $modified_files"

  # 检查分支状态
  branch=$(git branch --show-current)
  echo "  🌿 分支: $branch"

  cd - > /dev/null
done
```

**输出示例**:
```
=== 进度监控快照 (2025-12-30 14:00:00) ===

## CLI-1 (/opt/claude/project_name_feature_auth)
  📄 TASK-REPORT更新: 2025-12-30 13:45
  📊 进度: - ✅ T1.1 用户认证完成
           - 🔄 T1.2 权限管理进行中
           - ⏳ T1.3 审计日志待开始
  🔧 最后提交: a1b2c3d - feat: implement user auth (2 hours ago)
  📝 未提交文件: 3
  🌿 分支: feature-auth

## CLI-2 (/opt/claude/project_name_feature_api)
  📄 TASK-REPORT更新: 2025-12-30 12:30
  📊 进度: - ✅ T2.1 API框架完成
           - ✅ T2.2 数据验证完成
           - 🔄 T2.3 错误处理进行中
  🔧 最后提交: b2c3d4e - feat: add validation (4 hours ago)
  📝 未提交文件: 1
  🌿 分支: feature-api
```

### 1.3 自动化监控流程

**Cron任务配置** (主CLI服务器):
```bash
# 每2小时运行一次进度检查
0 */2 * * * /opt/claude/mystocks_spec/scripts/monitoring/check_worker_progress.sh >> /var/log/multi_cli_progress.log 2>&1

# 每天9:00生成进度报告
0 9 * * * /opt/claude/mystocks_spec/scripts/monitoring/generate_daily_report.sh
```

**进度报告生成脚本**:
```bash
#!/bin/bash
# scripts/monitoring/generate_daily_report.sh

REPORT_DIR="/opt/claude/mystocks_spec/reports/progress"
mkdir -p "$REPORT_DIR"

REPORT_FILE="$REPORT_DIR/daily_report_$(date +%Y%m%d).md"

cat > "$REPORT_FILE" <<EOF
# 多CLI并行开发 - 每日进度报告

**日期**: $(date +%Y-%m-%d)
**生成时间**: $(date +%H:%M:%S)
**监控周期**: Day $((($(date +%s) - $(date -d "2025-12-29" +%s)) / 86400 + 1))

---

## 📊 总体进度

| CLI | 任务 | 已完成 | 进行中 | 待开始 | 进度 | 状态 |
|-----|------|--------|--------|--------|------|------|
$(generate_cli_summary_table)

---

## 📝 详细进度

$(generate_cli_details)

---

## ⚠️ 风险与阻塞

$(identify_risks_and_blockers)

---

## 📅 下一步行动

$(suggest_next_actions)

EOF

echo "进度报告已生成: $REPORT_FILE"
```

### 1.4 问题上报机制

**Worker CLI问题上报格式** (在README中):
```markdown
## ⚠️ 阻塞问题

**问题级别**: 🔴 阻塞级 / 🟡 警告级 / 🟢 信息级

**问题描述**:
[详细描述遇到的问题]

**已尝试方案**:
1. 尝试方案1 - 失败原因...
2. 尝试方案2 - 失败原因...

**请求帮助**:
[需要主CLI提供什么支持]

**报告时间**: 2025-12-30 T+6h
```

**主CLI响应流程**:
1. **发现问题** (通过监控脚本)
2. **评估严重程度**
   - 🔴 阻塞级: 立即提供解决方案文档
   - 🟡 警告级: 24小时内回复
   - 🟢 信息级: 记录,不立即响应
3. **创建解决方案文档** (如需)
4. **跟踪问题解决** (下次监控验证)

---

## 🎯 二、里程碑管理

### 2.1 里程碑定义原则

**时间粒度建议**:
- 短期任务（<1天）：使用 `T+Xh` 格式
- 中期任务（1-7天）：使用 `Day X` 格式
- 长期项目（>7天）：使用 `阶段X` 或项目自定义格式

### 2.2 项目级里程碑模板

根据项目规模，设置相应级别的里程碑：

| 里程碑 | 时间点 | 验收标准 | 负责人 |
|--------|--------|----------|--------|
| M1: 项目启动 | Day 1 | 所有worktree创建完成，TASK.md分发 | 主CLI |
| M2: 阶段性检查 | Day X | Worker CLI进度达到预期 | 主CLI |
| M3: 阶段完成 | Day Y | 所有任务验收通过 | Worker CLIs |
| M4: 集成验证 | Day Z | 所有分支合并测试通过 | 主CLI |
| M5: 项目完成 | 最终 | 最终验收通过，部署完成 | 主CLI |

### 2.3 Worker CLI里程碑模板

为每个Worker CLI定义具体里程碑：

```markdown
### CLI-X 里程碑 ([任务名称])

| 里程碑 | 日期 | 验收标准 |
|--------|------|---------|
| MX.1: [子任务1] | Day X | [具体验收标准] |
| MX.2: [子任务2] | Day Y | [具体验收标准] |
| MX.3: [子任务3] | Day Z | [具体验收标准] |
```

### 2.4 里程碑管理流程

#### 项目启动 (M1)
- **主CLI任务**:
  - 创建所有worktree
  - 分发TASK.md任务文档
  - 确认Worker CLI已开始工作
- **Worker CLI任务**:
  - 阅读TASK.md，理解任务
  - 创建TASK-REPORT.md
  - 开始执行任务

#### 阶段性检查 (M2-MX)
- **主CLI任务**:
  - 检查所有Worker CLI进度
  - 生成进度报告
  - 处理Worker CLI的问题
- **Worker CLI任务**:
  - 继续执行任务
  - 定期更新TASK-REPORT.md

#### 项目完成 (最终)
- **主CLI任务**:
  - 合并所有分支到main
  - 运行完整测试套件
  - 部署到生产环境
  - 生成最终报告
- **Worker CLI任务**:
  - 完成所有任务
  - 生成TASK-*-REPORT.md完成报告

---

## 📅 三、时间线可视化

### 3.1 甘特图模板 (Markdown格式)

根据项目实际情况填充：

```
Week 1 (Day 1-7):
├─ CLI-1: ████████░░░░░░ ([任务描述])
├─ CLI-2: ████████░░░░░░ ([任务描述])
├─ CLI-3: ████████░░░░░░ ([任务描述])
└─ CLI-4: ████████████░░ ([任务描述])

Week 2 (Day 8-14):
├─ CLI-1: ░░░░░░████████ ([任务描述])
├─ CLI-2: ░░░░░░████████ ([任务描述])
├─ CLI-3: ░░░░░░████████ ([任务描述])
└─ CLI-4: ░░░░░░████████ ([任务描述])

集成阶段 (Day X-Y):
└─ 主CLI: ████████ (集成验证 + 部署)
```

### 3.2 依赖关系图模板

```
        CLI-A ([功能A])
            ↓
        CLI-B ([功能B])
            ↓
        CLI-C ([功能C])

CLI-X ([功能X]) ─┐
CLI-Y ([功能Y]) ─┼─→ CLI-Z (集成测试) ─→ 主CLI (部署)
                 │
         其他CLI ─┘
```

---

## 🚨 四、风险预警机制

### 4.1 自动预警触发条件

**黄色预警 🟡** (警告级):
- TASK-REPORT.md超过24小时未更新
- Git提交超过48小时无新记录
- 任务进度偏离计划>20%
- 测试覆盖率低于目标值

**红色预警 🔴** (阻塞级):
- TASK-REPORT.md明确标注阻塞问题
- 关键里程碑延期超过预期
- 集成测试失败率过高
- 依赖CLI未按时交付

### 4.2 预警通知方式

1. **控制台输出**: 监控脚本直接打印警告
2. **日志记录**: 写入项目日志文件
3. **进度报告高亮**: 红色/黄色标注问题CLI

**示例预警输出**:
```
🚨 RED ALERT - CLI-X 阻塞
  问题: [问题描述]
  影响: [影响范围]
  建议: 主CLI立即提供解决方案
  详情: [worktree路径]/TASK-REPORT.md

🟡 YELLOW WARNING - CLI-Y 进度慢
  问题: TASK-REPORT.md长时间未更新
  影响: 可能影响里程碑进度
  建议: 检查Worker CLI状态
```

---

## 📋 五、进度报告模板

### 5.1 每日进度快照 (自动生成)

```markdown
# 每日进度快照 - Day X

**日期**: YYYY-MM-DD
**总体进度**: XX% (已完成XX/YY任务)

## 当前活跃CLI

| CLI | 进度 | 状态 | 最后更新 | 阻塞问题 |
|-----|------|------|---------|---------|
| CLI-1 | XX% (X/Y) | 🔄 正常 | Xh ago | 无 |
| CLI-2 | XX% (X/Y) | 🔄 正常 | Xh ago | 无 |
| CLI-3 | XX% (X/Y) | 🟡 慢 | Xh ago | [问题描述] |

## 关键里程碑

- [x] M1: 项目启动
- [ ] M2: 阶段性检查 - 状态
- [ ] M3: 阶段完成 - 预计状态

## ⚠️ 风险与建议

- [风险描述和建议]
```

### 5.2 周报模板 (人工总结)

```markdown
# 多CLI并行开发 - 周报 Week X

**周期**: YYYY-MM-DD ~ YYYY-MM-DD
**总体进度**: XX%

## 本周完成

### CLI-1
- ✅ [完成的任务1]
- ✅ [完成的任务2]

### CLI-2
- ✅ [完成的任务1]
- 🔄 [进行中的任务]

## 下周计划

### CLI-1
- [ ] [计划任务1]
- [ ] [计划任务2]

### CLI-2
- [ ] [计划任务1]

## 风险与问题

- [风险描述和解决方案]

## 里程碑状态

- ✅ M1: [里程碑1] - 已完成
- 🔄 M2: [里程碑2] - 进行中

**下周重点**: [重点任务描述]
```

---

## 🛠️ 六、工具与脚本

### 6.1 监控脚本集合

**推荐目录结构**: `<项目根目录>/scripts/monitoring/`

```
scripts/monitoring/
├── check_worker_progress.sh          # 检查Worker进度
├── generate_daily_report.sh          # 生成每日报告
├── identify_risks.sh                 # 识别风险和阻塞
├── validate_milestones.sh            # 验证里程碑达成
├── collect_metrics.sh                # 收集性能指标
└── send_alerts.sh                    # 发送预警通知
```

> **注**：具体脚本实现请参考完整监控脚本模板文档。

### 6.2 Git Hooks集成

**Pre-commit Hook** (每个worktree):
```bash
#!/bin/bash
# .git/hooks/pre-commit

# 更新TASK-REPORT.md的最后提交时间
if [ -f "TASK-REPORT.md" ]; then
  sed -i "s/报告时间:.*/报告时间: $(date '+%Y-%m-%d %H:%M')/" TASK-REPORT.md
  git add TASK-REPORT.md
fi

# 运行测试 (如果有)
if [ -f "tests/run_tests.sh" ]; then
  ./tests/run_tests.sh || exit 1
fi
```

### 6.3 仪表板可视化 (可选)

**Grafana Dashboard配置** (实时监控):
```json
{
  "dashboard": {
    "title": "多CLI并行开发监控",
    "panels": [
      {
        "title": "总体进度",
        "type": "gauge",
        "targets": [
          {"expr": "sum(cli_tasks_completed) / sum(cli_tasks_total) * 100"}
        ]
      },
      {
        "title": "CLI任务完成率",
        "type": "bar",
        "targets": [
          {"expr": "cli_tasks_completed{cli=~'CLI-.*'} / cli_tasks_total * 100"}
        ]
      },
      {
        "title": "里程碑达成状态",
        "type": "table",
        "targets": [
          {"expr": "milestone_status"}
        ]
      }
    ]
  }
}
```

---

## ✅ 七、验收标准

### 7.1 监控机制验收

- [ ] 自动化脚本按预期频率运行成功
- [ ] 每日进度报告自动生成
- [ ] 预警机制能正确识别阻塞问题
- [ ] Git Hooks正常运行

### 7.2 里程碑管理验收

- [ ] 项目级里程碑定义清晰
- [ ] 每个Worker CLI的子里程碑可追踪
- [ ] 里程碑验收标准量化可测
- [ ] 依赖关系明确标注

---

## 📚 八、相关文档

- **[多 CLI 协作管理手册 (Master Guide)](./MULTI_CLI_WORKTREE_MANAGEMENT.md)** - 体系总纲
- **[Git Worktree 命令手册](./GIT_WORKTREE_MAIN_CLI_MANUAL.md)** - Git Worktree命令参考
- **[任务文档模板](./templates/TASK_TEMPLATE.md)** - TASK.md和TASK-REPORT.md模板

---

**文档版本**: v2.0
**最后更新**: 2025-12-30
**维护者**: Main CLI (Manager)

---

**重要提醒**:
- 主CLI的角色是**监控和协调**,不是执行
- 只在发现**阻塞问题**时主动介入
- 信任Worker CLI的**自主决策能力**
- 通过**被动监控**获取进度,避免干扰
