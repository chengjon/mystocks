# MyStocks 项目目录整理方案 v2.0

**版本**: v2.0
**创建日期**: 2026-03-22
**基于规范**: [目录与文件整理通用规则](../standards/DIRECTORY_AND_FILE_ORGANIZATION_RULES.md)
**状态**: 待审批

---

## 一、执行摘要

### 1.1 当前问题诊断

| 问题类别 | 当前状态 | 目标状态 |
|----------|----------|----------|
| **根目录** | 22个非必要文件/目录 | 仅保留允许清单文件 |
| **docs/** | 40+ 子目录，命名混乱 | 8-10 个规范子目录 |
| **归档目录** | `archive/` + `archived/` 重复 | 统一为 `archive/` |
| **scripts/** | 40+ 子目录，职责不清 | 10-12 个分类目录 |
| **配置文件** | 散落各处 | 统一到 `config/` |

### 1.2 整理目标

基于 [目录与文件整理通用规则](../standards/DIRECTORY_AND_FILE_ORGANIZATION_RULES.md)，实现：

1. **根目录极简化**: 仅保留核心入口文件
2. **目录结构标准化**: 按9大顶层目录组织
3. **命名规范化**: 统一使用英文 kebab-case
4. **归档统一化**: 合并重复归档目录

### 1.3 整理范围

| Phase | 内容 | 优先级 | 预估时间 |
|-------|------|--------|----------|
| Phase 0 | 根目录清理 | P0 | 2h |
| Phase 1 | docs/ 目录重组 | P1 | 4h |
| Phase 2 | 归档目录合并 | P1 | 2h |
| Phase 3 | scripts/ 目录整理 | P2 | 3h |
| Phase 4 | config/ 目录统一 | P2 | 1h |
| Phase 5 | 持续合规监控部署 | P3 | 2h |

---

## 二、当前目录结构分析

### 2.1 根目录现状

**实际存在的非必要文件/目录**:

```
根目录/
├── .FILE_OWNERSHIP          # → docs/guides/ 或删除
├── .agent/                  # → .claude/ 下或删除
├── .aider.conf.yml          # → config/tools/
├── .aider.model.*.json      # → config/tools/
├── .amazonq/                # → 删除或归档
├── .archive/                # → 合并到 archive/
├── .benchmarks/             # → reports/benchmarks/
├── .config/                 # → config/
├── .coverage                # → 删除 (应 gitignore)
├── .cursor/                 # 保留 (工具配置)
├── .env                     # 保留 (已在 gitignore)
├── .gemini/                 # 保留 (工具配置)
├── .githooks/               # → scripts/hooks/ 或保留
├── .gitnexus/               # 保留 (索引数据)
├── .migration/              # → docs/migration/ 或 archive/
├── .mypy_cache/             # → 删除 (应 gitignore)
├── .omc/                    # 保留 (OMC 状态)
├── .pytest_cache/           # → 删除 (应 gitignore)
├── .roo/                    # → 删除或归档
├── .shared/                 # → 评估后决定
├── .specify/                # 保留 (规范系统)
├── .symphony/               # → 删除或归档
├── .taskmaster/             # 保留 (任务管理)
├── .vscode/                 # 保留 (IDE配置)
├── .windsurf/               # → 删除或归档
├── .worktrees/              # 保留 (Git worktree)
├── .zenflow/                # → 删除或归档
├── .zencoder/               # → 删除或归档
├── FUNCTION_MAP.md          # → docs/architecture/
├── TASK.md                  # 保留 (Multi-CLI 约定)
├── TASK-REPORT.md           # 保留 (Multi-CLI 约定)
├── tui.json                 # → config/
├── opencode.json            # 保留 (工具配置)
└── ...
```

### 2.2 docs/ 目录现状

**当前子目录 (40+)**:

| 目录 | 建议 |
|------|------|
| `docs/04-测试/` | 重命名为 `docs/testing/` |
| `docs/ai_tools/` | 合并到 `docs/guides/` |
| `docs/api/` | ✅ 保留 |
| `docs/architecture/` | ✅ 保留 |
| `docs/ci-cd/` | 合并到 `docs/operations/` |
| `docs/cli_reports/` | 合并到 `docs/reports/` |
| `docs/code_quality/` | 合并到 `docs/standards/` |
| `docs/deployment/` | 合并到 `docs/operations/` |
| `docs/design/` | 合并到 `docs/architecture/` |
| `docs/design-references/` | 合并到 `docs/references/` |
| `docs/docs/` | ❌ 删除 (空聚合目录) |
| `docs/e2e/` | 合并到 `docs/testing/` |
| `docs/examples/` | ✅ 保留 |
| `docs/features/` | 合并到 `docs/guides/` |
| `docs/frontend/` | 合并到 `docs/guides/` |
| `docs/function-classification-manual/` | 合并到 `docs/references/` |
| `docs/guides/` | ✅ 保留 |
| `docs/legacy/` | 合并到 `archive/docs/` |
| `docs/media/` | 合并到 `docs/references/` |
| `docs/monitoring/` | 合并到 `docs/operations/` |
| `docs/openspec_cmd/` | 合并到 `docs/guides/` |
| `docs/operations/` | ✅ 保留 |
| `docs/overview/` | ✅ 保留 |
| `docs/performance/` | 合并到 `docs/reports/` |
| `docs/plans/` | 合并到 `docs/references/` |
| `docs/quality/` | 合并到 `docs/standards/` |
| `docs/reports/` | ✅ 保留 |
| `docs/reviews/` | 合并到 `docs/reports/` |
| `docs/security/` | 合并到 `docs/standards/` |
| `docs/standards/` | ✅ 保留 |
| `docs/superpowers/` | 合并到 `docs/guides/` |
| `docs/tasks/` | 合并到 `docs/reports/` |
| `docs/tdx_integration/` | 合并到 `docs/guides/` |
| `docs/technical_debt/` | 合并到 `docs/reports/` |
| `docs/testing/` | ✅ 保留 |
| `docs/ui-ux-pro-max/` | 合并到 `docs/guides/` |
| `docs/web/` | 合并到 `docs/guides/` |
| `docs/web-dev/` | 合并到 `docs/guides/` |
| `docs/worklogs/` | 合并到 `docs/reports/` |

### 2.3 归档目录重复问题

**当前状态**:
```
archive/          # 正确的归档目录
├── backups/
├── docs/
├── legacy-docs/
└── legacy-root-archived/

archived/         # ❌ 重复的归档目录
├── backtesting/
├── gpu_migration_backups_*/
├── services/
└── tools/
```

**目标状态**:
```
archive/
├── backups/           # 运维备份
├── code/              # 归档代码 (原 archived/*)
├── docs/              # 归档文档
├── legacy/            # 历史文件
└── migrations/        # 迁移记录
```

---

## 三、目标目录结构

### 3.1 标准九大顶层目录

```
Project_Root/
├── src/                    # 源代码 (已有)
├── tests/                  # 测试文件 (已有)
├── scripts/                # 脚本工具 (需整理)
├── config/                 # 配置文件 (需整合)
├── docs/                   # 文档 (需重组)
├── architecture/           # 架构文档 (已有)
├── reports/                # 生成报告 (需整合)
├── archive/                # 归档文件 (需合并)
└── data/                   # 数据文件 (已有)
```

### 3.2 docs/ 目标结构

```
docs/
├── INDEX.md                # 文档总索引
├── overview/               # 项目概述
│   ├── README.md
│   └── QUICKSTART.md
├── guides/                 # 开发指南
│   ├── DEVELOPMENT.md
│   ├── DEPLOYMENT.md
│   └── TROUBLESHOOTING.md
├── api/                    # API文档
│   └── REFERENCE.md
├── architecture/           # 架构设计
│   └── DATABASE.md
├── standards/              # 标准规范
│   ├── CODING_STANDARDS.md
│   └── SECURITY.md
├── testing/                # 测试文档
│   └── STRATEGY.md
├── operations/             # 运维文档
│   ├── MONITORING.md
│   └── CI_CD.md
├── reports/                # 项目报告
│   ├── performance/
│   └── technical_debt/
├── references/             # 参考文档
│   └── examples/
└── examples/               # 示例代码
```

### 3.3 scripts/ 目标结构

```
scripts/
├── runtime/                # 运行脚本 (run_*, save_*, monitor_*)
├── database/               # 数据库脚本 (check_*, verify_*, create_*)
├── dev/                    # 开发工具 (validate_*, analyze_*, generate_*)
├── maintenance/            # 维护脚本
├── deployment/             # 部署脚本
├── testing/                # 测试脚本
├── hooks/                  # Git hooks
├── tools/                  # 实用工具
└── utils/                  # 通用工具函数
```

---

## 四、详细迁移计划

### 4.1 Phase 0: 根目录清理

**操作清单**:

| 当前位置 | 目标位置 | 操作 | 风险 |
|----------|----------|------|------|
| `FUNCTION_MAP.md` | `docs/architecture/` | 移动 | 低 |
| `tui.json` | `config/` | 移动 | 低 |
| `.aider.conf.yml` | `config/tools/` | 移动 | 低 |
| `.aider.model.*.json` | `config/tools/` | 移动 | 低 |
| `.benchmarks/` | `reports/benchmarks/` | 移动 | 低 |
| `.archive/` | 合并到 `archive/` | 合并 | 低 |
| `.config/` | 合并到 `config/` | 合并 | 中 |
| `.migration/` | `docs/migration/` | 移动 | 低 |
| `.agent/`, `.amazonq/` | `archive/tools/` | 归档 | 低 |
| `.roo/`, `.symphony/` | `archive/tools/` | 归档 | 低 |
| `.windsurf/`, `.zenflow/` | `archive/tools/` | 归档 | 低 |
| `.coverage` | 删除 | 删除 | 无 |

**验证命令**:
```bash
# 清理后验证
ls -la *.md *.py *.json *.yaml *.yml 2>/dev/null | grep -v -E '(README|CLAUDE|AGENTS|LICENSE|CHANGELOG|requirements|package)'
```

### 4.2 Phase 1: docs/ 目录重组

**迁移映射表**:

| 原目录 | 目标目录 | 文件数 | 优先级 |
|--------|----------|--------|--------|
| `docs/04-测试/` | `docs/testing/` | ~5 | P0 |
| `docs/ci-cd/` | `docs/operations/` | ~3 | P1 |
| `docs/deployment/` | `docs/operations/` | ~5 | P1 |
| `docs/monitoring/` | `docs/operations/` | ~4 | P1 |
| `docs/code_quality/` | `docs/standards/` | ~3 | P1 |
| `docs/quality/` | `docs/standards/` | ~5 | P1 |
| `docs/security/` | `docs/standards/` | ~6 | P1 |
| `docs/design/` | `docs/architecture/` | ~4 | P1 |
| `docs/performance/` | `docs/reports/` | ~3 | P2 |
| `docs/reviews/` | `docs/reports/` | ~4 | P2 |
| `docs/technical_debt/` | `docs/reports/` | ~3 | P2 |
| `docs/worklogs/` | `docs/reports/` | ~10 | P2 |
| `docs/legacy/` | `archive/docs/` | ~20 | P3 |
| `docs/docs/` | 删除 | 0 | P3 |

**执行脚本**:
```bash
#!/bin/bash
# docs/reorganization_phase1.sh

# 1. 创建目标目录
mkdir -p docs/{operations,testing,reports/{performance,reviews,technical_debt}}

# 2. 移动文件 (使用 git mv 保留历史)
git mv docs/04-测试/* docs/testing/
git mv docs/ci-cd/* docs/operations/
git mv docs/deployment/* docs/operations/
git mv docs/monitoring/* docs/operations/
git mv docs/code_quality/* docs/standards/
git mv docs/quality/* docs/standards/
git mv docs/security/* docs/standards/

# 3. 删除空目录
find docs -type d -empty -delete

# 4. 更新文档索引
python scripts/tools/docs_indexer.py --categories
```

### 4.3 Phase 2: 归档目录合并

**操作**:

```bash
# 1. 将 archived/* 移动到 archive/
git mv archived/backtesting archive/code/
git mv archived/services archive/code/
git mv archived/tools archive/code/

# 2. 处理带时间戳的备份目录
git mv archived/gpu_migration_backups_* archive/migrations/

# 3. 删除空的 archived/ 目录
rmdir archived/

# 4. 合并 .archive/ 内容
git mv .archive/* archive/
rmdir .archive/
```

**目标结构**:
```
archive/
├── backups/               # 运维备份
├── code/                  # 归档代码
│   ├── backtesting/
│   ├── services/
│   └── tools/
├── docs/                  # 归档文档
│   └── legacy-docs/
├── legacy/                # 历史文件
│   └── legacy-root-archived/
├── migrations/            # 迁移记录
│   └── gpu_migration_*/
└── tools/                 # 归档工具配置
```

### 4.4 Phase 3: scripts/ 目录整理

**当前问题**: 40+ 子目录，职责边界模糊

**目标**: 整理为 10-12 个分类目录

| 原目录 | 目标目录 | 说明 |
|--------|----------|------|
| `scripts/runtime/` | ✅ 保留 | 运行脚本 |
| `scripts/database/` | ✅ 保留 | 数据库脚本 |
| `scripts/dev/` | ✅ 保留 | 开发工具 |
| `scripts/hooks/` | ✅ 保留 | Git hooks |
| `scripts/tools/` | ✅ 保留 | 通用工具 |
| `scripts/tests/` | → `tests/` | 测试文件迁移 |
| `scripts/maintenance/` | ✅ 保留 | 维护脚本 |
| 散落的脚本 | 按功能分类 | 逐一评估 |

### 4.5 Phase 4: config/ 目录统一

**操作**:

```bash
# 1. 合并 .config/ 到 config/
git mv .config/* config/

# 2. 移动根目录配置文件
git mv tui.json config/

# 3. 移动工具配置
mkdir -p config/tools
git mv .aider.conf.yml config/tools/
git mv .aider.model.*.json config/tools/
```

---

## 五、禁止操作清单

### 5.1 禁止移动的目录/文件

| 路径 | 原因 |
|------|------|
| `.git/` | Git 版本控制核心 |
| `.github/` | CI/CD 配置 |
| `.claude/` | Claude Code 配置 |
| `.gemini/` | Gemini CLI 配置 |
| `.cursor/` | Cursor IDE 配置 |
| `.vscode/` | VS Code 配置 |
| `.gitnexus/` | GitNexus 索引数据 |
| `.omc/` | OMC 状态数据 |
| `.specify/` | 规范系统数据 |
| `.taskmaster/` | Task Master 数据 |
| `.worktrees/` | Git worktree 数据 |
| `.multi-cli-tasks/` | Multi-CLI 协作数据 |
| `TASK.md` | Multi-CLI 约定文件 |
| `TASK-REPORT.md` | Multi-CLI 约定文件 |
| `web/` | 独立子模块 |
| `services/` | 独立子模块 |
| `openspec/` | OpenSpec 规范系统 |
| `monitoring-stack/` | 监控栈配置 |

### 5.2 删除前需审批的文件

| 路径 | 类型 | 审批原因 |
|------|------|----------|
| `docs/docs/` | 空目录 | 确认无隐藏文件 |
| `src/temp/` | 临时目录 | 确认无重要文件 |
| `.coverage` | 覆盖率文件 | 确认已入库 gitignore |
| 任何 `.py` 文件 | 代码 | 需代码审查 |

---

## 六、持续合规监控

### 6.1 Pre-commit Hooks 配置

**已存在**: `.pre-commit-config.yaml`

**需新增检查项**:

```yaml
# 添加到 .pre-commit-config.yaml
- id: check-directory-structure
  name: 检查目录结构
  entry: python scripts/hooks/check_directory_structure.py
  language: system
  stages: [pre-commit]
  pass_filenames: false
```

### 6.2 目录结构检查脚本

**已存在**: `scripts/hooks/check_directory_structure.py`

**配置文件**: `governance/mainline/policies/directory-structure.yaml`

### 6.3 定期合规扫描

**建议频率**: 每周一

```bash
# 运行目录结构检查
python scripts/hooks/check_directory_structure.py --format json --output reports/compliance/

# 生成合规报告
python scripts/tools/docs_indexer.py --categories
```

---

## 七、验收标准

### 7.1 根目录验收

- [ ] 根目录仅包含允许清单中的文件
- [ ] 无中文命名的文件/目录
- [ ] 无临时文件 (`.log`, `.tmp`, `.bak`)
- [ ] 无覆盖率文件 (`.coverage`, `coverage.xml`)

### 7.2 docs/ 目录验收

- [ ] 子目录数量 ≤ 15 个
- [ ] 所有目录使用英文 kebab-case 命名
- [ ] 每个目录有明确的职责定义
- [ ] `INDEX.md` 索引文件已更新

### 7.3 整体验收

- [ ] 所有移动使用 `git mv` (保留历史)
- [ ] 所有文档链接已更新
- [ ] `git status` 显示移动而非删除+新增
- [ ] 测试通过
- [ ] CI/CD 流水线通过

---

## 八、执行规范

### 8.1 自动化优先

- 使用脚本执行批量操作
- 避免 `rm -rf`，使用 `rmdir` 删除空目录
- 每次操作后验证 `git status`

### 8.2 分阶段执行

1. **Phase 0-1**: 根目录 + docs/ (高优先级)
2. **Phase 2-3**: 归档 + scripts/ (中优先级)
3. **Phase 4-5**: 配置 + 监控 (低优先级)

### 8.3 回滚策略

```bash
# Git 回滚（推荐）
git checkout HEAD~1 -- docs/ scripts/ config/ archive/

# 或使用迁移映射表
python scripts/dev/rollback_migration.py --input migration_map.csv
```

---

## 九、时间估算

| Phase | 内容 | 预估时间 | 执行者 |
|-------|------|----------|--------|
| Phase 0 | 根目录清理 | 2h | AI Agent |
| Phase 1 | docs/ 重组 | 4h | AI Agent |
| Phase 2 | 归档合并 | 2h | AI Agent |
| Phase 3 | scripts/ 整理 | 3h | AI Agent |
| Phase 4 | config/ 统一 | 1h | AI Agent |
| Phase 5 | 监控部署 | 2h | AI Agent |
| **总计** | | **14h** | |

---

## 十、审批确认

### 10.1 待审批事项

- [ ] Phase 0: 根目录清理方案
- [ ] Phase 1: docs/ 重组方案
- [ ] Phase 2: 归档目录合并方案
- [ ] Phase 3: scripts/ 整理方案
- [ ] Phase 4: config/ 统一方案
- [ ] Phase 5: 持续合规监控方案
- [ ] 禁止移动清单确认
- [ ] 删除审批清单确认

### 10.2 审批人签字

**审批人**: ________________
**审批日期**: ________________
**审批状态**: ☐ 批准 ☐ 批准但有修改 ☐ 拒绝

---

**文档版本**: v2.0
**基于规范**: [目录与文件整理通用规则](../standards/DIRECTORY_AND_FILE_ORGANIZATION_RULES.md)
**创建日期**: 2026-03-22
**维护者**: Project Team
