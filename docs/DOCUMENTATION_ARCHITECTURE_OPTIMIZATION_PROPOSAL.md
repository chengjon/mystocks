# MyStocks 文档 Canonical Trunk 收敛与历史文档归档方案

> 基于 eltdx 项目 `DOCS_METHODOLOGY.md` 的 reader-first 分层方法论，对齐本仓库现有 canonical trunk 文档治理体系，提出可执行的文档架构收敛方案。
>
> **生命周期分类**: 本文档为 `plan` 类，不是 canonical trunk。执行前需转化为 OpenSpec change。

---

## 0. 当前真相源

本方案以下列真相源为前提，所有建议必须与其保持一致：

| 真相源 | 位置 | 职责 |
|--------|------|------|
| 工程红线 | `architecture/STANDARDS.md` | 审批门禁、迁移收口、删除标准 |
| 文档 canonical trunk 地图 | `docs/README.md` | 文档入口、trunk 路由、reader routing |
| 文档系统定义 | `docs/overview/documentation-system.md` | trunk map、生命周期分类规则 |
| 文件组织规格 | `openspec/specs/file-organization/spec.md` | 目录结构、归档路径（`archive/`） |
| 目录治理规格 | `openspec/specs/directory-governance/spec.md` | 目录合并/删除审批门禁 |
| 文档治理规格 | `openspec/specs/documentation-governance/spec.md` | canonical/supporting/report 生命周期分类 |
| 产品真相 | 根目录 `PRODUCT.md` | 产品定位、能力范围、Web canon |
| 设计真相 | 根目录 `DESIGN.md` | 设计系统规范 |

**测量命令**（所有指标可复现）:

```bash
# Markdown 文件数（不含 .git / node_modules）
find docs/ -name "*.md" | wc -l

# 全部文件数
find docs/ -type f | wc -l

# 目录数
find docs/ -type d | wc -l

# INDEX.md 总数
find docs/ -name "INDEX.md" | wc -l

# 含绝对本地链接的文件数
grep -rn '\[.*\](/opt/' docs/ --include="*.md" -l | wc -l
```

---

## 1. 现状诊断

### 1.1 规模测量（2026-06-09）

测量口径: `find docs/` 下 Markdown 文件，不含 `.git` / `node_modules` / `.worktrees`。

| 指标 | eltdx (参考) | mystocks_spec | 倍数 |
|------|-------------|---------------|------|
| Markdown 文档数 | ~50 | **2,873** | 57x |
| 全部文件数（含图片/截图等） | ~60 | **5,331** | 89x |
| 目录数 | ~5 | **146** | 29x |
| 目录层级深度 | 2 层 | **6 段** | — |
| INDEX.md 文件数 | 0 | **78** | — |
| README.md 文件数 | 1 | **27** | — |
| 含绝对本地链接的 Markdown | 0 | **123 文件 / 737 链接** | — |

### 1.2 核心问题

> **诊断修正**: 本仓库已有 canonical trunk 体系（docs/README.md 为入口，docs/overview/documentation-system.md 定义 trunk map）。以下问题不否定现有体系，而是在其基础上识别收敛机会。

| # | 问题 | 现象 | 现有体系覆盖情况 |
|---|------|------|-----------------|
| P1 | **trunk 路由需压缩** | docs/README.md 已有 trunk map，但缺少 eltdx 式角色阅读路径 | 已有 trunk，缺角色分层辅助导航 |
| P2 | **reports/ 黑洞** | 1,971 个 Markdown（69%），quality/ 含 774 MD + 1,550 总文件 | 已识别为 `report` 生命周期类，未批量归档 |
| P3 | **INDEX.md 已降级但未清理** | 78 个 INDEX.md，docs/INDEX.md 已标注自动生成 | 已降级为辅助角色，需分类处理 |
| P4 | **命名不统一** | UPPER_SNAKE / kebab-case / 中文 / camelCase 混用 | 无命名规范约束 |
| P5 | **guides/ 膨胀** | 283 个 Markdown、23 个子目录 | 部分 trunk（如 frontend/）有 README，部分无 |
| P6 | **深度嵌套** | `reports/quality/myweb-audit/audit-*/pages/` 深达 6 段 | 无深度限制规则 |
| P7 | **缺少 docs 层面产品概览** | 根 PRODUCT.md 是产品真相，docs/ 缺少面向读者的精简概览 | 根 PRODUCT.md 已是 canonical，docs/ 缺 supporting 入口 |
| P8 | **绝对链接泛滥** | 123 个文件含 737 个 `/opt/claude/mystocks_spec/...` 绝对路径 | 无链接可移植性规则 |

### 1.3 当前目录 Markdown 文件分布

```
docs/
├── reports/        1,971 Markdown (4,379 总文件) (69%)  ← 需归档
├── guides/           283 Markdown (10%)  ← 需收敛
├── api/              214 Markdown (233 总文件) ( 7%)
├── architecture/     102 Markdown ( 4%)
├── plans/             78 Markdown ( 3%)
├── standards/         48 Markdown ( 2%)
├── operations/        41 Markdown ( 1%)  ← 结构较好
├── design/            28 Markdown ( 1%)
├── superpowers/       27 Markdown ( 1%)  ← AI 会话产物
├── testing/           24 Markdown ( 1%)
├── overview/          15 Markdown ( 1%)
├── references/        14 Markdown
├── worklogs/          10 Markdown
├── agents/             5 Markdown
├── project-exchange/   4 Markdown
├── changes/            4 Markdown
└── (root files)        6 Markdown
```

---

## 2. 目标架构（收敛方向）

参照 eltdx 方法论的 reader-first 原则，在现有 canonical trunk 体系上增加角色阅读辅助：

```
┌─────────────────────────────────────────────────────────────────┐
│  L1 产品层    docs/README.md (已有 trunk map)                   │
│               + docs/PRODUCT.md (supporting，指向根 PRODUCT.md) │
│               "这是什么项目，能做什么"                             │
├─────────────────────────────────────────────────────────────────┤
│  L2 使用层    docs/guides/ (收敛后)                             │
│               "我想做 X，怎么操作"                                │
├─────────────────────────────────────────────────────────────────┤
│  L3 参考层    docs/api/ + docs/references/                     │
│               "这个 API 参数是什么"                               │
├─────────────────────────────────────────────────────────────────┤
│  L4 底层参考  docs/standards/ + docs/architecture/              │
│               "设计系统 token / 架构约束"                         │
├─────────────────────────────────────────────────────────────────┤
│  L5 工程层    docs/operations/ + docs/testing/                  │
│               "怎么部署、监控、测试"                               │
└─────────────────────────────────────────────────────────────────┘
```

**关键约束**: 上层不定义新 canonical trunk。L1-L5 是 docs/README.md 的辅助阅读组织，与现有 trunk map 共存。

### 读者路径（作为 docs/README.md 的补充段落）

| 角色 | 推荐路径 |
|------|---------|
| 新开发者 | README → 根 PRODUCT.md → guides/onboarding → guides/frontend |
| 前端开发者 | guides/frontend → api/ → standards/ (设计系统) |
| 后端开发者 | guides/data-source → api/ → operations/ |
| 运维 | operations/ → testing/ |
| AI 助手 | README → STANDARDS.md → 按需进入各 trunk |

---

## 3. 目标目录结构

```
docs/
├── README.md                          # canonical entrypoint (保留现有 trunk map + 新增角色阅读路径)
├── PRODUCT.md                         # supporting: 面向读者的精简产品概览，指向根 PRODUCT.md
│
├── guides/                            # L2 使用层（收敛后）
│   ├── README.md
│   ├── onboarding/
│   ├── frontend/
│   ├── backend/
│   ├── data-source/
│   ├── ai-tools/
│   ├── governance/
│   ├── hooks/
│   ├── mock-data/
│   └── web/
│
├── api/                               # L3 参考层
│   ├── README.md
│   ├── guides/
│   ├── specifications/
│   └── testing/
│
├── references/                        # L3 参考层
│   ├── README.md
│   └── function-classification-manual/
│
├── standards/                         # L4 底层参考
│   ├── README.md
│   ├── 01-DESIGN_SYSTEM/
│   ├── 02-COMPONENT_LIBRARY/
│   ├── 03-PAGE_DESIGNS/
│   └── 04-INTERACTION_FLOWS/
│
├── architecture/                      # L4 底层参考
│   ├── README.md
│   └── (架构设计文档)
│
├── operations/                        # L5 工程层（结构较好，保留）
│   ├── README.md
│   ├── deployment/
│   ├── monitoring/
│   └── ci-cd/
│
├── testing/                           # L5 工程层
│   ├── README.md
│   └── e2e/
│
├── design/                            # 设计相关（保留）
│   ├── README.md
│   └── new/
│
├── changes/                           # 变更记录
├── agents/                            # Agent 文档
│
└── INDEX.md                           # 自动生成辅助索引（已标注非权威）

归档区（遵循 openspec/specs/file-organization 规格的 archive/docs/ 路径）:

archive/docs/
├── reports/                           # 历史 reports 收敛
├── plans/                             # 已完成/过时计划
├── worklogs/                          # 历史 worklog
├── superpowers/                       # AI 会话产物
├── guides-merged/                     # 合并后的原目录（akshare/ 等）
└── indexes/                           # 归档的 INDEX.md
```

---

## 4. 具体优化措施

### 4.1 入口增强（P1 修复）

**现状**: docs/README.md 已是 canonical entrypoint，已有 trunk map 和 reader routing。docs/INDEX.md 已标注为自动生成辅助索引。

**方案**（保留现有 trunk map，不重写）:
- 在 docs/README.md 现有内容末尾新增 "Reader Paths" 段落，按角色提供 L1-L5 阅读路径表
- docs/INDEX.md 保持现状（已标注自动生成），不做额外操作
- 不删除或重写 docs/README.md 的现有 trunk map

### 4.2 新增 docs/PRODUCT.md（P7 修复）

**现状**: 根目录 PRODUCT.md 是 canonical 产品真相。docs/ 缺少面向读者的精简概览。

**方案**: 在 docs/ 下新建 PRODUCT.md，**生命周期分类为 `supporting`**，不是 canonical trunk。内容包含：
- 一句话定位 + 指向根 PRODUCT.md 的链接
- 目标用户表
- 核心能力表
- 技术栈概览
- 头部标注: `> 本文档为 supporting 文档，产品真相以 [根 PRODUCT.md](../PRODUCT.md) 为准`

**不新建 docs/ARCHITECTURE.md**: 架构真相分布在 `architecture/STANDARDS.md`、`openspec/specs/`、`docs/architecture/README.md`，不需要额外入口。

### 4.3 reports/ 归档（P2 修复）

**现状**: 1,971 个 Markdown 文件，4,379 总文件。docs/reports/README.md 已识别为 `report` 生命周期。

**方案**: 遵循 `openspec/specs/file-organization/spec.md`，归档到 `archive/docs/reports/`（不是 `docs/_archive/`）。

| 步骤 | 操作 | 生命周期分类 | 预估减少 |
|------|------|-------------|---------|
| 1 | `docs/reports/worklogs/` → `archive/docs/reports/worklogs/` | report → archived | -119 MD |
| 2 | `docs/reports/quality/` 审计证据 → `archive/docs/reports/quality/` | report → archived | ~-600 MD |
| 3 | `docs/reports/completion_reports/` → `archive/docs/reports/completion_reports/` | report → archived | -13 MD |
| 4 | `docs/reports/cleanup/` → `archive/docs/reports/cleanup/` | report → archived | -21 MD |
| 5 | `docs/reports/phase_reports/`, `phase4_6/` → `archive/docs/reports/` | report → archived | ~-10 MD |
| 6 | 保留 `docs/reports/README.md` + 有持续参考价值的分析报告 | canonical + report | 净减 ~750 MD |

**约束**: 不删除文件，仅移动到 `archive/docs/reports/`。保留 `docs/reports/README.md` 作为路由索引，指向归档位置和保留的报告。

### 4.4 guides/ 收敛（P5 修复）

**现状**: 283 个 Markdown、23 个子目录。

**方案**（精确路径）:

| 操作 | 源路径 | 目标路径 | 生命周期分类 |
|------|--------|---------|-------------|
| **保留** | `docs/guides/frontend/` | 原位 | canonical |
| **保留** | `docs/guides/data-source/` | 原位 | canonical |
| **保留** | `docs/guides/ai-tools/` | 原位 | canonical |
| **保留** | `docs/guides/governance/` | 原位 | canonical |
| **保留** | `docs/guides/mock-data/` | 原位 | canonical |
| **保留** | `docs/guides/web/` | 原位 | canonical |
| **保留** | `docs/guides/hooks/` | 原位 | canonical |
| **保留** | `docs/guides/onboarding/` | 原位 | canonical |
| **合并** | `docs/guides/akshare/` | `docs/guides/data-source/` | supporting |
| **合并** | `docs/guides/tdx-integration/` | `docs/guides/data-source/` | supporting |
| **合并** | `docs/guides/buger/` | `docs/guides/ai-tools/` | supporting |
| **合并** | `docs/guides/chrome-devtools/` | `docs/guides/ai-tools/` | supporting |
| **合并** | `docs/guides/quant-trading/` | `docs/guides/data-source/` 或 `docs/references/` | supporting |
| **合并** | `docs/guides/wencai/` | `docs/guides/data-source/` | supporting |
| **合并** | `docs/guides/data-interface/` | `docs/guides/data-source/` | supporting |
| **合并** | `docs/guides/templates/` | 评估后归档或合并 | archive_candidate |
| **合并** | `docs/guides/pm2/` | `docs/operations/` | supporting |
| **归档** | `docs/guides/superpowers/` (3 MD) | `archive/docs/guides-merged/superpowers/` | archive_candidate |
| **归档** | `docs/guides/typescript/` | 评估后归档或保留 | 待分类 |
| **归档** | `docs/guides/multi-cli-tasks/` | 评估后归档或保留 | 待分类 |
| **归档** | `docs/superpowers/` (27 MD) | `archive/docs/superpowers/` | archive_candidate |

### 4.5 INDEX.md 分类处理（P3/P8 修复）

**现状**: 78 个 INDEX.md 文件，其中 20 个有同级 README.md。docs/INDEX.md 已标注自动生成。

**方案**: 逐个分类，不使用粗粒度规则。分类维度：

| 分类 | 标准 | 处理 |
|------|------|------|
| `generated_reference` | 自动生成、有工具依赖 | 保留原位，确认头部标注 |
| `compat` | 历史链接兼容（如 `docs/overview/INDEX.md`） | 保留，添加兼容标注 |
| `supporting` | 手动维护、与 README.md 互补 | 保留 |
| `redundant` | 与同级 README.md 内容重复 | 归档到 `archive/docs/indexes/`，检查入站链接后操作 |
| `delete_candidate` | 空文件或纯 placeholder | 入站链接检查后删除 |

**前置条件**: 每个 INDEX.md 操作前必须检查 `git grep -l "INDEX.md" docs/` 确认入站引用。

### 4.6 绝对链接修复（P8 修复）

**现状**: 123 个 Markdown 文件含 737 个绝对本地链接（`/opt/claude/mystocks_spec/...`）。

**方案**: 作为独立批次处理，不与其他批次混合。

| 步骤 | 操作 |
|------|------|
| 1 | 扫描所有绝对链接: `grep -rn '\[.*\](/opt/' docs/ --include="*.md"` |
| 2 | 定义范围: reader-facing 文档全部转换; generated 文档暂缓 |
| 3 | 批量替换为相对路径 |
| 4 | 验证: 运行 markdown link checker，确认前后 count |
| 5 | 验证命令: `grep -c '/opt/claude/mystocks_spec' docs/**/*.md` 前后对比 |

### 4.7 plans/ 归档

**现状**: 78 个 Markdown 文件。

**方案**:
- 已完成/过时的计划移入 `archive/docs/plans/`
- 保留活跃计划在 `docs/plans/`
- 保留 `docs/plans/README.md` 作为活跃计划索引
- 每个移动前检查入站链接

---

## 5. 单页模板规范

参照 eltdx 第 7 节，**新增**或**重构**的指南/参考类文档遵循：

```markdown
# {标题}

## 概述
一段话说明本文回答什么问题、适合什么场景。

## 快速开始 / 示例
可直接复制的最小示例。

## 详细说明
按需展开的参数、步骤、选项。

## 另见
- [相关文档](../other/doc.md)
```

已有文档不强制重写模板，仅在新写或大改时应用。

---

## 6. 交叉引用规则

| 场景 | 写法 |
|------|------|
| 引用同目录文件 | `[显示文本](文件名.md)` |
| 引用上级目录 | `[显示文本](../文件名.md)` |
| 引用子目录 | `[显示文本](子目录/文件名.md)` |
| 引用代码位置 | 反引号路径 `` `src/xxx.py` `` |
| 引用根目录标准 | `[STANDARDS.md](../../architecture/STANDARDS.md)` |

**策略**: reader-facing 文档禁止绝对本地路径（`/opt/...`）。generated 文档暂缓，后续批次处理。

---

## 7. 执行计划

### 前置: OpenSpec Change 注册

在执行任何结构性操作前，必须创建 OpenSpec change:

```bash
openspec create refactor-documentation-architecture \
  --title "文档 canonical trunk 收敛与历史文档归档" \
  --affects documentation-governance file-organization
```

涉及 spec delta:
- `documentation-governance/spec.md`: 新增角色阅读路径段落、单页模板规范
- `file-organization/spec.md`: 确认 `archive/docs/` 归档路径、新增目录深度限制建议

### Batch 0: 测量与盘点（无副作用）

| 步骤 | 操作 | 产出 |
|------|------|------|
| 0.1 | 运行测量命令，记录基准数据 | 基准计数表 |
| 0.2 | 盘点 78 个 INDEX.md，逐个分类为 generated/compat/supporting/redundant/delete_candidate | `INDEX_INVENTORY.md` |
| 0.3 | 扫描 737 个绝对链接，按 generated/reader-facing 分类 | `ABSOLUTE_LINK_INVENTORY.md` |
| 0.4 | 盘点 docs/superpowers/ (27 MD) 和 docs/guides/superpowers/ (3 MD) 的入站引用 | 入站引用报告 |
| 0.5 | 创建 OpenSpec change，提交 spec delta | OpenSpec change ID |

**验证**: 无文件系统修改，仅产出盘点文档。

### Batch 1: 入口增强（低风险）

| 步骤 | 操作 | 验证 |
|------|------|------|
| 1.1 | docs/README.md 末尾新增 "Reader Paths" 段落 | `openspec validate <change-id> --strict` |
| 1.2 | 新建 docs/PRODUCT.md (supporting，指向根 PRODUCT.md) | 头部标注正确、链接可达 |
| 1.3 | 确认 docs/INDEX.md 已有自动生成标注 | 无需操作 |

**验收**: `openspec validate <change-id> --strict`；docs/README.md 原有 trunk map 未被修改。

### Batch 2: reports/ 归档波

| 步骤 | 操作 | 验证 |
|------|------|------|
| 2.1 | `docs/reports/worklogs/` → `archive/docs/reports/worklogs/` | `git grep -l "reports/worklogs/" docs/` 入站检查 |
| 2.2 | `docs/reports/quality/` → `archive/docs/reports/quality/` | 同上 |
| 2.3 | `docs/reports/completion_reports/` → `archive/docs/reports/completion_reports/` | 同上 |
| 2.4 | 其他归档项按 Batch 0 盘点结果执行 | 每项入站检查 |
| 2.5 | 更新 `docs/reports/README.md` 添加归档位置路由 | 链接可达 |

**验收**:
- `find docs/reports/ -name "*.md" | wc -l` 记录前后对比
- `git grep -l "archive/docs/reports/" docs/` 确认路由索引已更新
- 无断裂链接

### Batch 3: guides/ 分类波

| 步骤 | 操作 | 验证 |
|------|------|------|
| 3.1 | 按 4.4 表执行合并（每项检查入站链接后操作） | `git grep` 入站检查 |
| 3.2 | `docs/superpowers/` (27 MD) → `archive/docs/superpowers/` | 入站检查 |
| 3.3 | `docs/guides/superpowers/` (3 MD) → `archive/docs/guides-merged/superpowers/` | 入站检查 |
| 3.4 | 更新各子目录 README.md 索引 | 链接可达 |

**验收**: `find docs/guides/ -type d | wc -l` 前后对比；无断裂链接。

### Batch 4: INDEX.md 处理波

| 步骤 | 操作 | 验证 |
|------|------|------|
| 4.1 | 按 Batch 0 盘点的 `INDEX_INVENTORY.md` 分类执行 | 每项入站检查 |
| 4.2 | redundant 类 → `archive/docs/indexes/` | `git grep -l "INDEX.md"` 确认无断裂 |
| 4.3 | delete_candidate 类 → 删除（需审批） | 入站引用为 0 |

**验收**: `find docs/ -name "INDEX.md" | wc -l` 前后对比；无断裂链接。

### Batch 5: 绝对链接转换波

| 步骤 | 操作 | 验证 |
|------|------|------|
| 5.1 | 按 `ABSOLUTE_LINK_INVENTORY.md` 中 reader-facing 分类批量转换 | 每文件验证 |
| 5.2 | markdown link checker 全扫描 | 零断裂 |
| 5.3 | 记录前后绝对链接计数 | 目标: reader-facing 文档零绝对链接 |

**验收**: `grep -rn '\[.*\](/opt/' docs/ --include="*.md" -c` 前后对比。

---

## 8. 预期效果

| 指标 | 当前（基准） | 目标 | 改善 |
|------|-------------|------|------|
| docs/ 活跃 Markdown 数 | 2,873 | ~300-400 | **~-85%** |
| docs/reports/ Markdown 数 | 1,971 | ~50 (保留高价值) + archive | **~-97%** |
| docs/guides/ 子目录数 | 23 | ~9 | **~-60%** |
| 绝对本地链接（reader-facing） | 737 | 0 | **-100%** |
| INDEX.md 总数 | 78 | 按分类收敛 | 待 Batch 0 盘点 |
| 角色阅读路径 | 不存在 | docs/README.md 新增段落 | 建立 |

**注意**: 以上预期效果需在 Batch 0 完成后用实测数据校准。

---

## 9. 风险与缓解

| 风险 | 缓解措施 |
|------|---------|
| 归档后找不到历史报告 | `archive/docs/` 保留完整目录结构 + `docs/reports/README.md` 路由 |
| 合并目录后引用断裂 | 每项操作前 `git grep` 入站检查，操作后验证 |
| INDEX.md 删除影响兼容链接 | compat 类保留；redundant 类先归档不删 |
| 过度删除丢失有用文档 | 全部先归档到 `archive/docs/`，不直接删除 |
| OpenSpec change 审批未通过 | Batch 0 盘点产出仍可用于后续方案修订 |
| 绝对链接转换引入错误 | 独立批次 + link checker 全扫描 |
| CLAUDE.md 文档引用不一致 | 同步更新 CLAUDE.md 中受影响的文档路径 |

---

## 10. 设计决策记录

### D1: 为什么归档到 `archive/docs/` 而不是 `docs/_archive/`？

**决策**: 遵循 `openspec/specs/file-organization/spec.md` 已定义的 `archive/` 生命周期目录。

**理由**: OpenSpec file-organization 规格 104-106 行明确指定历史资产归档到 `archive/`，120-121 行要求 stale 文档收敛到 `archive/docs/`。创建 `docs/_archive/` 会与现有规格冲突。除非通过 OpenSpec change 修改规格，否则必须使用 `archive/docs/`。

### D2: 为什么不重写 docs/README.md？

**决策**: 保留 docs/README.md 现有 trunk map 和 reader routing，仅新增角色阅读路径段落。

**理由**: docs/README.md 已是 canonical entrypoint，`docs/overview/documentation-system.md` 已定义其权威地位。按 eltdx 模板完全重写会丢失现有 trunk-first 治理信息。新增补充段落既满足 reader-first 需求，又保持现有治理真相。

### D3: 为什么 guides/ 不按 eltdx 的 helpers/ + methods/ 双入口模式？

**决策**: guides/ 保持按主题子目录组织。

**理由**: eltdx 是 SDK/库项目，读者按"我要做什么"和"这个方法是什么"两种心智模型查找。mystocks_spec 是服务/应用项目，开发者按技术领域（前端/后端/数据源）查找更自然。双入口在 20+ 子目录规模下维护成本超过收益。

### D4: 为什么 docs/PRODUCT.md 定为 supporting 而非 canonical？

**决策**: docs/PRODUCT.md 标注为 `supporting`，头部指向根 PRODUCT.md。

**理由**: 根 PRODUCT.md 已是 canonical 产品真相。如果 docs/PRODUCT.md 也声明为 canonical，将产生并行真相。supporting 角色既为 docs/ 读者提供便捷概览，又不破坏 single-source-of-truth 原则。

### D5: 为什么 INDEX.md 不能用"有 README 就删"的规则？

**决策**: 78 个 INDEX.md 逐个分类后再操作。

**理由**: INDEX.md 存在多种角色：自动生成（如 docs/INDEX.md）、兼容链接（如 docs/overview/INDEX.md）、手动维护的补充索引。粗粒度删除会破坏兼容链接或自动工具依赖。必须先分类为 generated_reference / compat / supporting / redundant / delete_candidate，再按分类处理。

---

## 附录 A: 与 eltdx 方法论的适配差异

| eltdx 规范 | mystocks_spec 适配 | 原因 |
|------------|-------------------|------|
| helpers/ + methods/ 双入口 | 不采用 | 服务项目非库项目 |
| 扁平目录（2 层） | 适度嵌套（3 层） | 文档量大，需要子目录分组 |
| 无归档机制 | `archive/docs/` 归档区 | 遵循 OpenSpec file-organization 规格 |
| 全英文命名 | 中英混用 | 项目为中文语境 |
| COMMANDS_*.md | 不需要 | 无底层协议映射 |
| releases/ | 不采用 | 版本记录由 git 管理 |
| docs/README.md 入口模板 | 保留现有 trunk map + 增补 | 已有 canonical entrypoint |

## 附录 B: 生命周期分类清单（Batch 0 产出模板）

| 文档族 | 当前路径 | 当前 trunk | 生命周期分类 | 建议操作 | 入站链接数 | 保留义务 | 验证命令 |
|--------|---------|-----------|-------------|---------|-----------|---------|---------|
| reports/worklogs | docs/reports/worklogs/ | docs/reports/README.md | report → archived | 移至 archive/docs/reports/worklogs/ | (待盘点) | 无 | `git grep -l "reports/worklogs/" docs/` |
| ... | ... | ... | ... | ... | ... | ... | ... |

---

*提案日期: 2026-06-09*
*修订日期: 2026-06-09（v2 — 对齐审查报告 findings）*
*状态: 待审核（v2）*
*OpenSpec change ID: 待创建*
