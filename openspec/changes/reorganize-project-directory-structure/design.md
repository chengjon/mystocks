# 设计文档：项目目录结构全面重组

## 变更标识

- **Change ID**: `reorganize-project-directory-structure`
- **状态**: `proposed`
- **优先级**: `high`
- **创建日期**: 2025-07-25
- **关联文档**:
  - [项目文件目录整理具体方案](../../docs/plans/项目文件目录整理具体方案.md)
  - [文件目录整理方法论指南 v2.1](../../docs/guides/文件目录整理方法论指南.md)
  - [FILE_ORGANIZATION_RULES v1.3](../../docs/standards/FILE_ORGANIZATION_RULES.md)
- **前序变更**: `implement-file-directory-migration`（已完成，本次为其后续深度治理）

---

## 1. 背景与动机

### 1.1 问题陈述

项目根目录在经历 2025-11-09 首次重组（42→13 目录）后，随着开发迭代和 AI 工具链引入，目录再次膨胀：

| 指标 | 首次重组后目标 | 当前实际 | 差距 |
|------|---------------|---------|------|
| 根目录数（非隐藏） | 13 | 83 | +70（538%） |
| 根文件数（非隐藏） | ~10 | 50 | +40（500%） |
| 隐藏目录数 | ~5 | 23 | AI 工具链正常增长 |
| 磁盘占用异常 | 0 | ~237GB（logs/bak/htmlcov） | 需立即清理 |

### 1.2 根因分析

1. **开发过程副产物堆积**：TASK-*.md 报告、日志文件、覆盖率报告直接生成在根目录
2. **缺乏自动化防线**：git hook 和 CI 检查未强制执行目录规范
3. **一次性工具目录残留**：ai_test_optimizer_toolkit、ts-quality-guard 等完成使命后未清理
4. **备份目录膨胀**：bak/ 包含完整项目副本（含 node_modules），占 554MB
5. **AI 工具链扩张**：23 个隐藏目录为正常现象，但需明确保护

### 1.3 目标

将项目从 83 个根目录 + 50 个根文件精简至 **13 个根目录 + ~10 个根文件**，同时：
- 零功能回归（所有 import 路径、CI 流程、工具链正常工作）
- 释放 ~237GB 磁盘空间
- 建立长效防线防止再次膨胀

---

## 2. 设计方案

### 2.1 目标结构

```
mystocks_spec/
├── src/                    # 核心业务代码（8 子模块）
│   ├── adapters/
│   ├── core/
│   ├── data_access/
│   ├── storage/
│   ├── db_manager/
│   ├── monitoring/
│   ├── interfaces/
│   └── utils/
├── web/                    # 前端 + 后端（自治子模块）
│   ├── frontend/
│   └── backend/
├── config/                 # 所有配置文件
│   ├── docker/
│   ├── monitoring/
│   └── *.yaml / *.toml / *.ini
├── scripts/                # 脚本（按用途分类）
│   ├── dev/
│   ├── deploy/
│   ├── database/
│   └── tests/
├── docs/                   # 文档
│   ├── guides/
│   ├── architecture/
│   ├── api/
│   ├── standards/
│   ├── reports/
│   └── plans/
├── tests/                  # 测试
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── architecture/           # 架构设计资产
├── data/                   # 数据文件
├── openspec/               # OpenSpec 变更管理
├── reports/                # 生成的分析报告
├── .github/                # GitHub 配置
├── .claude/                # Claude 配置
└── [23 个工具链隐藏目录]   # 禁区，不触碰
```

根目录保留文件（白名单）：
```
README.md, CLAUDE.md, IFLOW.md, AGENTS.md
pyproject.toml, package.json, vitest.config.ts, tsconfig.json
requirements.txt, __init__.py
core.py, data_access.py, monitoring.py, unified_manager.py  # src/ 兼容入口
docker-compose.yml → config/docker/docker-compose.yml 的符号链接
```

### 2.2 六阶段执行策略

采用「先删后归再并」的渐进式策略，每阶段独立可回滚：

| 阶段 | 名称 | 内容 | 预计释放 | 风险等级 |
|------|------|------|---------|---------|
| Phase 1 | 垃圾清除 | 删除 logs/、bak/、htmlcov/、临时文件 | ~237GB | 低 |
| Phase 2 | 根文件归位 | 移动 TASK-*.md、*.log、报告文件到 docs/reports/ | - | 低 |
| Phase 3 | 配置集中 | 移动散落的配置文件到 config/ | - | 中 |
| Phase 4 | 目录归并 | 合并同类目录（code_quality→docs/、scripts 散落→scripts/） | - | 中 |
| Phase 5 | 深度整合 | 处理 architecture/、data/、tests/ 等结构性调整 | - | 高 |
| Phase 6 | 防线建设 | 部署 git hook、CI 检查、定期审计 | - | 低 |

### 2.3 禁区规则

以下目录/文件在整理过程中 **绝对不可触碰**：

**隐藏目录（23 个）**：
`.amazonq`, `.archive`, `.benchmarks`, `.claude`, `.claude-trace`, `.config`, `.cursor`, `.gemini`, `.git`, `.github`, `.migration`, `.mypy_cache`, `.omc`, `.opencode`, `.playwright-mcp`, `.pytest_cache`, `.ruff_cache`, `.shared`, `.specify`, `.taskmaster`, `.vscode`, `.worktrees`, `.zencoder`, `.zenflow`

**隐藏文件（12 个）**：
`.FILE_OWNERSHIP`, `.coverage`, `.env`, `.env.async_monitoring`, `.env.example`, `.gitattributes`, `.gitignore`, `.mcp.json`, `.pre-commit-config.yaml`, `.pre-commit-hooks.yaml`, `.pylint.test.rc`, `.pylintrc`

**兼容入口文件（4 个）**：
`core.py`, `data_access.py`, `monitoring.py`, `unified_manager.py`

### 2.4 路径依赖处理

- 113+ 条 `from src.*` import 语句 → src/ 位置不变，无需修改
- 4 个根级兼容入口 → 保持不动
- GitHub Actions workflows → 引用 src/，无需修改
- docker-compose 移入 config/ 后 → 根目录创建符号链接
- 移动文件一律使用 `git mv` 保留历史

### 2.5 审查反馈整合

基于 `docs/reviews/PROJECT_STRUCTURE_PLAN_REVIEW.md` 的审查建议：

1. **根 package.json 非冗余**：它是 monorepo 根级工具配置（playwright/vitest），与 web/frontend/package.json 用途不同，保留
2. **logs 删除前检查进程**：执行 `lsof | grep logs/` 确认无活跃写入
3. **高频配置文件符号链接**：docker-compose.yml 等移入 config/ 后在根目录创建 symlink
4. **路径依赖已覆盖**：阶段 4 包含 import 路径验证步骤

---

## 3. 风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| import 路径断裂 | 低 | 高 | src/ 不动；每步后运行 `python -c "import src"` |
| CI 流程失败 | 低 | 高 | 每阶段后触发 CI 验证 |
| AI 工具链损坏 | 极低 | 高 | 禁区清单硬编码，hook 拦截 |
| 误删有用文件 | 中 | 中 | 整理前 `git tag backup/`；仅用 `git mv` |
| 符号链接兼容性 | 低 | 中 | Windows 环境需额外测试 |

---

## 4. 验收标准

- [ ] 根目录非隐藏目录数 ≤ 13
- [ ] 根目录非隐藏文件数 ≤ 15
- [ ] `python -c "from src.core import *"` 成功
- [ ] `cd web/frontend && npm run build` 成功
- [ ] 所有 GitHub Actions workflows 通过
- [ ] 23 个隐藏目录完整无损
- [ ] `git log --follow` 可追溯所有移动文件的历史
- [ ] DHI 健康度评分 ≥ 85 分
- [ ] git hook 拦截根目录新增文件生效
- [ ] 磁盘释放 ≥ 200GB
