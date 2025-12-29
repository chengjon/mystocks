# 多CLI并行开发 - 进度监控与里程碑管理方案

**制定时间**: 2025-12-29
**适用项目**: MyStocks前端六阶段优化 (Phase 3-6)
**监控周期**: 2025-12-29 至 2026-01-28 (4周)
**主CLI**: Main CLI (Manager)
**Worker CLIs**: CLI-1 ~ CLI-6

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

WORKTREES=(
  "/opt/claude/mystocks_phase3_frontend:CLI-1"
  "/opt/claude/mystocks_phase6_api_contract:CLI-2"
  "/opt/claude/mystocks_phase4_complete:CLI-3"
  "/opt/claude/mystocks_phase5_ai_screening:CLI-4"
  "/opt/claude/mystocks_phase6_monitoring:CLI-5"
  "/opt/claude/mystocks_phase6_quality:CLI-6"
)

echo "=== 进度监控快照 ($(date)) ==="

for item in "${WORKTREES[@]}"; do
  IFS=':' read -r worktree cli_name <<< "$item"

  echo ""
  echo "## $cli_name ($worktree)"

  # 检查README更新时间
  if [ -f "$worktree/README.md" ]; then
    last_update=$(stat -c %y "$worktree/README.md" | cut -d' ' -f1-2)
    echo "  📄 README更新: $last_update"

    # 提取进度信息 (假设README中有"## 进度更新"章节)
    progress=$(grep -A 5 "## 进度更新" "$worktree/README.md" | tail -n 3)
    echo "  📊 进度: $progress"
  else
    echo "  ⚠️  README不存在"
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

## CLI-1 (/opt/claude/mystocks_phase3_frontend)
  📄 README更新: 2025-12-30 13:45
  📊 进度: - ✅ T3.1 ProKLineChart组件完成
           - 🔄 T3.2 技术指标集成进行中
           - ⏳ T3.3 多周期切换待开始
  🔧 最后提交: a1b2c3d - feat: implement ProKLineChart component (2 hours ago)
  📝 未提交文件: 3
  🌿 分支: phase3-kline-charts

## CLI-2 (/opt/claude/mystocks_phase6_api_contract)
  📄 README更新: 2025-12-30 12:30
  📊 进度: - ✅ T2.1 统一响应格式完成
           - ✅ T2.2 错误码系统完成
           - 🔄 T2.3 OpenAPI Schema生成中
  🔧 最后提交: b2c3d4e - feat: add error code enum (4 hours ago)
  📝 未提交文件: 1
  🌿 分支: phase6-api-contract
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

### 2.1 总体里程碑 (4周)

| 里程碑 | 时间 | 验收标准 | 负责CLI |
|--------|------|---------|---------|
| **M1: Round 1启动** | Day 1 (2025-12-29) | 4个CLI worktree创建完成 | CLI-1,2,5,6 |
| **M2: Round 1中期** | Day 7 (2026-01-04) | CLI-1,2,5,6 完成50%任务 | CLI-1,2,5,6 |
| **M3: Round 1完成** | Day 14 (2026-01-11) | CLI-1,2,5,6 所有任务完成 | CLI-1,2,5,6 |
| **M4: Round 2启动** | Day 15 (2026-01-12) | CLI-3,4 worktree创建完成 | CLI-3,4 |
| **M5: Round 2中期** | Day 21 (2026-01-18) | CLI-3,4 完成50%任务 | CLI-3,4 |
| **M6: Round 2完成** | Day 28 (2026-01-25) | CLI-3,4 所有任务完成 | CLI-3,4 |
| **M7: 集成验证** | Day 29 (2026-01-26) | 所有CLI集成测试通过 | 主CLI |
| **M8: 最终交付** | Day 30 (2026-01-27) | 生产部署,质量报告发布 | 主CLI |

### 2.2 CLI-1 里程碑 (Phase 3 K线图)

| 里程碑 | 日期 | 验收标准 |
|--------|------|---------|
| M1.1: ProKLineChart完成 | Day 3 | 组件渲染正常,60fps |
| M1.2: 技术指标集成 | Day 5 | 70+指标显示正确 |
| M1.3: 多周期切换 | Day 7 | 1m/5m/15m/1h/1d/1w切换流畅 |
| M1.4: A股特性完成 | Day 10 | 涨跌停/前复权/T+1标识 |
| M1.5: 性能优化 | Day 12 | Lighthouse > 90 |
| M1.6: 集成测试 | Day 14 | E2E测试通过 |

### 2.3 CLI-2 里程碑 (API契约)

| 里程碑 | 日期 | 验收标准 |
|--------|------|---------|
| M2.1: 统一响应格式 | Day 2 | UnifiedResponse实现 |
| M2.2: 错误码系统 | Day 3 | ErrorCode枚举完整 |
| M2.3: OpenAPI Schema | Day 5 | 200+接口Schema完成 |
| M2.4: Pydantic模型 | Day 7 | 所有DTO模型验证通过 |
| M2.5: 契约管理平台 | Day 10 | api-contract-sync-manager上线 |
| M2.6: CLI工具 | Day 12 | api-contract-sync命令可用 |
| M2.7: CI/CD集成 | Day 14 | Pre-commit hook验证契约 |

### 2.4 CLI-3 里程碑 (Phase 4完整)

**依赖**: CLI-2完成 (需要API契约)

| 里程碑 | 日期 | 验收标准 |
|--------|------|---------|
| M3.1: A股规则引擎 | Day 17 | T+1/涨跌停/100股验证通过 |
| M3.2: 指标注册表 | Day 19 | 161个指标元数据完整 |
| M3.3: TA-Lib封装 | Day 21 | 所有指标计算准确 |
| M3.4: 批量计算引擎 | Day 23 | 100股×161指标<5s |
| M3.5: GPU加速验证 | Day 24 | 加速比>50x |
| M3.6: PostgreSQL缓存 | Day 25 | 缓存命中率>80% |
| M3.7: 集成测试 | Day 26 | API端点测试通过 |

### 2.5 CLI-4 里程碑 (AI筛选)

**依赖**: CLI-3完成 (需要161指标数据)

| 里程碑 | 日期 | 验收标准 |
|--------|------|---------|
| M4.1: 查询解析器 | Day 18 | 解析准确率>85% |
| M4.2: 9个模板 | Day 19 | 所有模板可用 |
| M4.3: 推荐引擎 | Day 21 | 综合评分算法实现 |
| M4.4: 推荐API | Day 22 | 响应时间<3s |
| M4.5: 告警规则引擎 | Day 24 | 4种告警正常触发 |
| M4.6: SSE推送 | Day 25 | 实时推送稳定 |
| M4.7: 集成测试 | Day 26 | E2E测试通过 |

### 2.6 CLI-5 里程碑 (GPU监控)

| 里程碑 | 日期 | 验收标准 |
|--------|------|---------|
| M5.1: GPU监控后端 | Day 3 | pynvml采集成功 |
| M5.2: 性能指标采集 | Day 4 | GFLOPS/加速比准确 |
| M5.3: 历史数据服务 | Day 5 | PostgreSQL持久化成功 |
| M5.4: 前端状态卡片 | Day 7 | 实时更新(2s刷新) |
| M5.5: 性能图表 | Day 8 | ECharts趋势图正常 |
| M5.6: 优化建议引擎 | Day 9 | 5类建议准确 |
| M5.7: SSE推送 | Day 10 | 实时推送稳定 |
| M5.8: 告警系统 | Day 11 | 4种告警触发 |
| M5.9: 集成测试 | Day 12 | 测试覆盖率>80% |

### 2.7 CLI-6 里程碑 (质量保证)

**贯穿整个周期**

| 里程碑 | 日期 | 验收标准 |
|--------|------|---------|
| M6.1: 单元测试 | Day 4 | 后端覆盖率>80% |
| M6.2: 前端测试 | Day 5 | 组件测试覆盖率>70% |
| M6.3: 集成测试 | Day 6 | API端点测试通过 |
| M6.4: E2E测试 | Day 7 | Playwright测试通过 |
| M6.5: 代码质量 | Day 9 | Pylint>8.0 |
| M6.6: 安全审计 | Day 10 | 无高危漏洞 |
| M6.7: 性能测试 | Day 12 | API RPS>500, 前端>90 |
| M6.8: 文档检查 | Day 13 | 文档100%完整 |
| M6.9: 最终报告 | Day 14 | 质量报告生成 |

---

## 📅 三、时间线可视化

### 3.1 甘特图 (Markdown格式)

```
Week 1 (Day 1-7):
├─ CLI-1: ████████░░░░░░ (ProKLineChart + 指标集成)
├─ CLI-2: ████████░░░░░░ (统一响应 + 错误码 + Schema)
├─ CLI-5: ████████░░░░░░ (GPU监控后端 + 前端卡片)
└─ CLI-6: ████████████░░ (单元测试 + 前端测试 + E2E)

Week 2 (Day 8-14):
├─ CLI-1: ░░░░░░████████ (多周期 + A股特性 + 性能优化)
├─ CLI-2: ░░░░░░████████ (Pydantic模型 + 管理平台 + CLI工具)
├─ CLI-5: ░░░░░░████████ (性能图表 + 优化建议 + SSE + 告警)
└─ CLI-6: ░░░░░░████████ (代码质量 + 安全审计 + 文档检查)

Week 3 (Day 15-21):
├─ CLI-3: ████████████░░ (A股规则 + 指标注册 + TA-Lib + 批量计算)
└─ CLI-4: ████████████░░ (查询解析 + 模板 + 推荐引擎 + API)

Week 4 (Day 22-28):
├─ CLI-3: ░░░░░░████████ (GPU加速 + 缓存 + 集成测试)
└─ CLI-4: ░░░░░░████████ (告警引擎 + SSE + 集成测试)

Week 4+ (Day 29-30):
└─ 主CLI: ████████ (集成验证 + 生产部署)
```

### 3.2 依赖关系图

```
        CLI-2 (API契约)
            ↓
        CLI-3 (Phase 4)
            ↓
        CLI-4 (AI筛选)

CLI-1 (K线图) ─┐
CLI-5 (GPU监控)─┼─→ CLI-6 (质量保证) ─→ 主CLI (集成)
                │
        CLI-3,4 ─┘
```

---

## 🚨 四、风险预警机制

### 4.1 自动预警触发条件

**黄色预警 🟡** (警告级):
- README超过24小时未更新
- Git提交超过48小时无新记录
- 任务进度偏离计划>20%
- 测试覆盖率<70%

**红色预警 🔴** (阻塞级):
- README明确标注阻塞问题
- 关键里程碑延期>2天
- 集成测试失败率>30%
- 依赖CLI未按时交付

### 4.2 预警通知方式

1. **控制台输出**: 监控脚本直接打印警告
2. **日志记录**: 写入`/var/log/multi_cli_alerts.log`
3. **进度报告高亮**: 红色/黄色标注问题CLI

**示例预警输出**:
```
🚨 RED ALERT - CLI-3 阻塞
  问题: 后端服务无法启动
  影响: Day 17里程碑M3.1可能延期
  建议: 主CLI立即提供解决方案
  详情: /opt/claude/mystocks_phase4_complete/README.md

🟡 YELLOW WARNING - CLI-1 进度慢
  问题: README 36小时未更新
  影响: 可能影响Day 7里程碑M1.3
  建议: 检查Worker CLI状态
```

---

## 📋 五、进度报告模板

### 5.1 每日进度快照 (自动生成)

```markdown
# 每日进度快照 - Day X

**日期**: 2025-12-XX
**总体进度**: XX% (已完成XX/YY任务)

## Round 1 (CLI-1,2,5,6)

| CLI | 进度 | 状态 | 最后更新 | 阻塞问题 |
|-----|------|------|---------|---------|
| CLI-1 | 45% (9/20) | 🔄 正常 | 2h ago | 无 |
| CLI-2 | 60% (10/17) | 🔄 正常 | 1h ago | 无 |
| CLI-5 | 30% (5/18) | 🟡 慢 | 8h ago | 显存监控API错误 |
| CLI-6 | 50% (10/20) | 🔄 正常 | 3h ago | 无 |

## Round 2 (CLI-3,4)

⏳ 待启动 (Day 15)

## 关键里程碑

- [x] M1: Round 1启动 (Day 1)
- [ ] M2: Round 1中期 (Day 7) - 预计正常
- [ ] M3: Round 1完成 (Day 14) - 预计正常

## ⚠️ 风险与建议

- 🟡 CLI-5进度偏慢,建议加快GPU监控后端开发
- ✅ 其他CLI进度正常
```

### 5.2 周报模板 (人工总结)

```markdown
# 多CLI并行开发 - 周报 Week X

**周期**: 2025-12-XX ~ 2025-12-YY
**总体进度**: XX%

## 本周完成

### CLI-1
- ✅ ProKLineChart组件完成
- ✅ 70+技术指标集成

### CLI-2
- ✅ 统一响应格式实现
- ✅ 错误码系统完成

### CLI-5
- ✅ GPU监控后端完成
- 🔄 前端仪表板进行中

### CLI-6
- ✅ 单元测试覆盖率达80%
- ✅ E2E测试框架搭建

## 下周计划

### CLI-1
- [ ] 完成多周期数据切换
- [ ] 实现A股特性 (涨跌停/前复权)

### CLI-2
- [ ] 完成OpenAPI Schema生成
- [ ] 实现契约管理平台

### CLI-5
- [ ] 完成前端性能图表
- [ ] 实现优化建议引擎

### CLI-6
- [ ] 完成代码质量检查
- [ ] 完成安全审计

## 风险与问题

- 无重大阻塞问题

## 里程碑状态

- ✅ M1: Round 1启动 (Day 1)
- 🔄 M2: Round 1中期 (Day 7) - 进行中

**下周重点**: 确保Round 1所有CLI达到50%进度
```

---

## 🛠️ 六、工具与脚本

### 6.1 监控脚本集合

**位置**: `/opt/claude/mystocks_spec/scripts/monitoring/`

```
scripts/monitoring/
├── check_worker_progress.sh          # 检查Worker进度
├── generate_daily_report.sh          # 生成每日报告
├── identify_risks.sh                 # 识别风险和阻塞
├── validate_milestones.sh            # 验证里程碑达成
├── collect_metrics.sh                # 收集性能指标
└── send_alerts.sh                    # 发送预警通知
```

### 6.2 Git Hooks集成

**Pre-commit Hook** (每个worktree):
```bash
#!/bin/bash
# .git/hooks/pre-commit

# 更新README的最后提交时间
sed -i "s/最后更新:.*/最后更新: $(date '+%Y-%m-%d %H:%M')/" README.md
git add README.md

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

- [ ] 自动化脚本每2小时运行成功
- [ ] 每日进度报告自动生成
- [ ] 预警机制能正确识别阻塞问题
- [ ] Git Hooks正常运行

### 7.2 里程碑管理验收

- [ ] 所有8个总体里程碑定义清晰
- [ ] 每个CLI的子里程碑可追踪
- [ ] 里程碑验收标准量化可测
- [ ] 依赖关系明确标注

---

## 📚 八、相关文档

- **[Multi-CLI Worktree Management](./MULTI_CLI_WORKTREE_MANAGEMENT.md)** - 多CLI协作手册
- **[Git Worktree Main CLI Manual](./GIT_WORKTREE_MAIN_CLI_MANUAL.md)** - Git Worktree命令参考
- **各CLI任务分配文件**:
  - [CLI-1 Phase 3 Tasks](./CLI-1_PHASE3_TASKS.md)
  - [CLI-2 API Contract Tasks](./CLI-2_API_CONTRACT_TASKS.md)
  - [CLI-3 Phase 4 Complete Tasks](./CLI-3_PHASE4_COMPLETE_TASKS.md)
  - [CLI-4 Phase 5 AI Screening Tasks](./CLI-4_PHASE5_AI_SCREENING_TASKS.md)
  - [CLI-5 Phase 6 GPU Monitoring Tasks](./CLI-5_PHASE6_GPU_MONITORING_TASKS.md)
  - [CLI-6 Quality Assurance Tasks](./CLI-6_QUALITY_ASSURANCE_TASKS.md)

---

**文档版本**: v1.0
**最后更新**: 2025-12-29
**维护者**: Main CLI (Manager)

---

**重要提醒**:
- 主CLI的角色是**监控和协调**,不是执行
- 只在发现**阻塞问题**时主动介入
- 信任Worker CLI的**自主决策能力**
- 通过**被动监控**获取进度,避免干扰
