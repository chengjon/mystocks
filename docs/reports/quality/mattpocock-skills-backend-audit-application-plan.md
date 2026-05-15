# mattpocock/skills 应用于 MyStocks 后端审计 — 具体方案

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **关联审计入口**: `docs/reports/quality/backend-audit-2026-05-14.md`
> **复核报告**: `docs/reports/quality/backend-audit-documents-review-2026-05-15.md`
> **方案日期**: 2026-05-15
> **Skill 来源**: [mattpocock/skills](https://github.com/mattpocock/skills) (MIT, 82K+ stars)

---

## 一、mattpocock/skills 核心能力与审计场景映射

mattpocock/skills 是一套面向 AI 编码代理（Claude Code / Codex）的可组合技能集，核心解决 4 类工程问题：

| 问题域 | Skill | 本项目对应审计发现 |
|--------|-------|-------------------|
| 需求对齐失败 | `/grill-with-docs` | 8 份子文档 Audit Health Score 8/20，需先对齐再执行 |
| 代码不工作 | `/diagnose` + `/tdd` | 健康端点事实过期（P0-1）、路由表需重测 |
| 架构泥球 | `/improve-codebase-architecture` | Core 68 文件平铺、32 个 singleton、flat/package 并存 |
| 过度冗长 | `/caveman` + `CONTEXT.md` | 审计文档 3000+ 行，缺少共享术语表 |

---

## 二、执行前准备（Phase 0）

### 2.1 安装 skills

```bash
npx skills@latest add mattpocock/skills
# 选择: diagnose, grill-with-docs, improve-codebase-architecture,
#        tdd, to-issues, to-prd, triage, zoom-out, caveman
# 安装目标: Claude Code
```

### 2.2 运行 `/setup-matt-pocock-skills`

首次使用前运行，配置：
- Issue tracker: **GitHub**（本项目使用 GitHub）
- Triage labels: `tech-debt`, `audit-finding`, `migration-blocked`, `needs-openspec`
- Docs output: `docs/reports/quality/`（对齐现有审计文档位置）

### 2.3 构建 CONTEXT.md（关键前置）

这是 mattpocock 方法的核心 — 建立项目共享语言。基于现有审计文档，提取以下术语表：

```
# MyStocks 后端共享术语

## 架构术语
- **canonical 路由**: VERSION_MAPPING.py 中定义的唯一权威路由路径
- **flat 文件**: app/api/ 下的单文件 .py 路由（迁移前形态）
- **package 目录**: app/api/xxx/ 下的包化路由（迁移目标形态）
- **双注册**: 同一功能域同时存在 flat + package 两种路由注册

## 治理术语
- **迁移收口**: STANDARDS.md §三要求的迁移必须有退出条件
- **删除判定**: 删除文件前必须完成代码路径判定 + 功能树判定
- **OpenSpec 审批**: 架构变更需经过 proposal → design → tasks 三步审批

## 模块术语
- **singleton 服务**: global _xxx + get_xxx_service() 的 lazy init 模式（32 处）
- **Core 目录**: app/core/，当前 68 文件 + 3 子目录，需按职责拆分
- **健康探针**: /health/ready + /api/health/services 体系，当前 21 个碎片端点

## 日志术语
- **日志双轨**: logging (stdlib) + structlog 两套日志体系并存
- **logger 入口**: STANDARDS 要求的 from app.core.logger import logger（尚未创建）
```

---

## 三、分阶段执行方案

### Phase 1: 审计文档对齐（对应复核报告 P0 修正）

**目标**: 将 Audit Health Score 从 8/20 提升到 14+，使文档可进入执行准备。

**使用的 Skill**: `/grill-with-docs`

**执行步骤**:

```
/grill-with-docs
```

**grill 聚焦问题**（向 AI 提问）:

1. **健康端点事实校准** (P0-1):
   - "当前 route table 中 `/api/health/services` 和 `/health/ready` 的实际注册来源是哪个文件？"
   - "review 文档指出 canonical URL 写法与代码不一致，请对照 `router_registry.py` 和 `main.py` 重新确认每个端点的当前路径"

2. **残留文件清册重扫** (P0-2):
   - "B 文档的文件清单是否反映当前工作树？请重新扫描 `web/backend/app/` 下的 `.bak`, `.backup`, `_new.py`, `.old.py` 文件"

3. **删除判定表补全** (P0-3):
   - "每个删除候选的代码路径判定（谁 import 它）和功能树判定（FUNCTION_TREE.md 中对应哪个域）是否完整？"

4. **OpenSpec 审批入口** (P0-4):
   - "C/F/H/I 四份文档涉及架构迁移，请为每份文档标注需要创建的 OpenSpec proposal 类型"

**产出**:
- 更新后的 CONTEXT.md（共享术语 + 校准后的事实）
- 修正后的子文档 A/B/G（事实校准）
- 4 份 OpenSpec proposal 草案入口（C/F/H/I）

---

### Phase 2: 架构深度分析

**目标**: 用系统级视角理解当前架构债务的全貌和优先级。

**使用的 Skill**: `/zoom-out` → `/improve-codebase-architecture`

#### Step 2a: 系统级架构视图

```
/zoom-out
```

**聚焦**:
- "解释 `app/core/` 68 个文件之间的依赖关系，哪些文件是其他所有文件的基础？"
- "32 个 singleton 服务的初始化顺序是什么？是否存在循环依赖风险？"
- "flat → package 迁移如果全部完成，`router_registry.py` 会变成什么样子？"

#### Step 2b: 深化机会识别

```
/improve-codebase-architecture
```

**逐域分析**:

| 域 | 分析焦点 | 对应子文档 |
|----|----------|-----------|
| 日志体系 | `logging` vs `structlog` 统一路径、`app/core/logger.py` 创建策略 | A |
| Core 目录 | 按职责（database/cache/security/websocket/middleware）的拆分方案 | F |
| Singleton | 32 个 singleton 按生命周期（per-request / per-app / per-session）分类 | E |
| API 路由 | flat/package 双注册的退出策略和 router_registry 重构 | C |
| 策略域 | 4 套入口的 canonical 选择和 shim 退场 | H |
| 风控域 | 5 个入口 + 2 个 service 版本的收敛路径 | I |
| 健康端点 | 21 个碎片端点的集中化策略 | G |

**产出**:
- 每个域的「当前 → 目标」架构图
- 深化机会（deepening opportunities）清单
- ADR 草案（架构决策记录）存入 `docs/adr/`

---

### Phase 3: 审计发现转 Issue

**目标**: 将审计发现转化为可独立抓取的 GitHub Issues，按优先级排序。

**使用的 Skill**: `/to-prd` + `/to-issues`

#### Step 3a: 生成 PRD

对每个高优先级修复，先运行 `/to-prd` 生成产品需求文档：

```
# 示例：日志整改 PRD
/to-prd
"基于 backend-logging-fix-2026-05-14.md，将后端日志体系统一为 structlog，
创建 app/core/logger.py 统一入口，消除 mock/ 目录下的 40+ 处 print() 调用"
```

#### Step 3b: 拆分为 Issues

```
/to-issues
```

**Issue 拆分策略**（按审计子文档 → vertical slices）:

**A - 日志整改** (3 issues):
1. `audit(A): 创建 app/core/logger.py 统一日志入口` — 1 文件, 无风险
2. `audit(A): 消除 mock/coverage_report.py 中 30+ 处 print()` — 1 文件, 无风险
3. `audit(A): 统一全模块为 structlog，淘汰 logging.getLogger` — 20+ 文件, 需 OpenSpec

**B - 残留文件清理** (2 issues):
1. `audit(B): 重扫工作树，更新残留文件清册` — 诊断性
2. `audit(B): 删除已确认的 4 个 .bak/.backup 文件` — 需判定表

**C - API 迁移** (5 issues，按功能域拆分):
1. `audit(C): 公告域 announcement flat→package 收口` — 最简单，1 flat + 1 package
2. `audit(C): 市场数据域 market flat→package 收口` — 中等复杂度
3. `audit(C): 监控域 monitoring 收口与 monitoring_old 退场`
4. `audit(C): 策略域 4 入口收敛` — 最复杂，需 H 文档
5. `audit(C): 风控域 5 入口收敛` — 最复杂，需 I 文档

**E - Singleton→DI** (2 issues):
1. `audit(E): 32 个 singleton 生命周期分类` — 诊断性
2. `audit(E): per-request 类 singleton 迁移到 FastAPI Depends` — 长期

**F - Core 拆分** (4 issues):
1. `audit(F): 提取 core/database/ 子目录` — 7 文件
2. `audit(F): 提取 core/cache/ 子目录` — 5 文件
3. `audit(F): 提取 core/security/ 子目录` — 3 文件
4. `audit(F): 提取 core/websocket/ 子目录` — 5 文件

**G - 健康端点** (2 issues):
1. `audit(G): 重测 route table，确认 21 个健康端点的当前实际路径`
2. `audit(G): 碎片端点收敛到 health.py 统一体系`

**H + I - 域治理** (4 issues):
1. `audit(H): 策略域 canonical 路由选择与 shim 退场计划`
2. `audit(H): 策略域测试引用更新`
3. `audit(I): 风控域 canonical 路由选择`
4. `audit(I): 风控域测试引用更新`

**总计约 22 个 issues**，每个可独立抓取和验证。

---

### Phase 4: 分批实现

**目标**: 按优先级逐个实现，每个 issue 使用 TDD 循环保证质量。

**使用的 Skill**: `/tdd` + `/diagnose`

#### 实现优先级排序

**第一批 — 无风险快速修复（本周）**:

| Issue | Skill | 预估 | 验证命令 |
|-------|-------|------|----------|
| A-1: 创建 logger.py | `/tdd` | 30 min | `pytest tests/unit/test_logger.py` |
| A-2: 消除 print() | `/tdd` | 20 min | `grep -r "print(" app/mock/` |
| B-2: 删除 .bak 文件 | 直接执行 | 10 min | `git status` + 功能树判定 |

**第二批 — 低风险改进（1-2 周）**:

| Issue | Skill | 预估 |
|-------|-------|------|
| G-1: 重测 route table | `/diagnose` | 2h |
| C-1: 公告域收口 | `/tdd` | 4h |
| F-1: Core/database/ 提取 | `/tdd` | 3h |

**第三批 — 中风险重构（2-4 周，需 OpenSpec）**:

| Issue | Skill | 前置条件 |
|-------|-------|----------|
| A-3: 统一 structlog | `/tdd` | OpenSpec 审批 |
| C-2~5: 其余域收口 | `/tdd` per issue | OpenSpec 审批 |
| E-2: Singleton→DI | `/tdd` | 生命周期分类完成 |
| G-2: 健康端点收敛 | `/tdd` | route table 重测完成 |

**第四批 — 长期优化（1-3 月）**:

| Issue | Skill |
|-------|-------|
| H/I: 策略域+风控域治理 | `/tdd` per vertical slice |
| Core 全部拆分完成 | `/improve-codebase-architecture` |

#### TDD 执行模板（每个 issue）

```
# Step 1: Red — 写失败测试
/tdd
"为 [issue 描述] 编写失败测试"

# Step 2: Green — 最小修复使测试通过
"修复代码使测试通过"

# Step 3: Refactor — 清理
"重构，保持测试通过"

# Step 4: 验证
pytest && ruff check && black --check .
```

---

### Phase 5: 进度跟踪与交接

**使用的 Skill**: `/triage` + `/handoff`

#### 持续 triage

```
/triage
```

每周运行一次，跟踪：
- `tech-debt` 标签的 issue 是否有进展
- `audit-finding` 标签的 issue 是否已验证
- `migration-blocked` 标签的 issue 是否已解除阻塞
- `needs-openspec` 标签的 issue 是否已获得审批

#### 会话交接

当需要切换上下文或在不同 worktree 之间切换时：

```
/handoff
```

生成紧凑的交接文档，包含：
- 当前正在处理的 issue 及状态
- 已完成的重构和验证结果
- 下一步需要处理的 issue
- 未解决的阻塞项

---

## 四、Skill 与现有工具链的集成

### 4.1 与 GitNexus 的配合

| 场景 | mattpocock Skill | GitNexus 工具 | 配合方式 |
|------|-----------------|---------------|----------|
| 编辑前影响分析 | `/tdd` 开始前 | `gitnexus_impact()` | impact 结果作为 TDD 的测试边界输入 |
| 提交前变更检查 | `/tdd` 完成后 | `gitnexus_detect_changes()` | detect_changes 替代手动 `git diff` 审查 |
| 重命名 | `/improve-codebase-architecture` | `gitnexus_rename()` | rename 命令确保跨文件安全重命名 |

### 4.2 与 OpenSpec 的配合

| 场景 | mattpocock Skill | OpenSpec 流程 | 配合方式 |
|------|-----------------|---------------|----------|
| 架构迁移规划 | `/grill-with-docs` | `openspec proposal` | grill 产出作为 proposal 输入 |
| 架构决策记录 | `/improve-codebase-architecture` | `docs/adr/` | ADR 草案进入 OpenSpec review |
| 变更审批 | `/to-prd` | `openspec design/tasks` | PRD 转为 design document |

### 4.3 与现有 STANDARDS.md 的优先级

```
优先级: CLAUDE.md / STANDARDS.md > mattpocock/skills > 默认行为
```

当 mattpocock skill 建议的做法与 STANDARDS.md 冲突时（如迁移收口规则），遵循 STANDARDS.md。

---

## 五、具体执行时间线

| 周次 | Phase | 关键产出 | 预估时间 |
|------|-------|----------|----------|
| W1 前半 | Phase 0 | skills 安装 + CONTEXT.md + setup | 2h |
| W1 前半 | Phase 1 | 审计文档校准，Health Score → 14+ | 3h |
| W1 后半 | Phase 2 | 架构分析 + ADR 草案 | 4h |
| W1 末 | Phase 3 | 22 个 GitHub Issues 创建 | 2h |
| W2 | Phase 4 第一批 | A-1, A-2, B-2 完成 | 4h |
| W2-W3 | Phase 4 第二批 | G-1, C-1, F-1 完成 | 9h |
| W3-W4 | Phase 4 第三批 | OpenSpec 审批 + 实施 | 12h |
| 持续 | Phase 5 | triage + handoff | 每周 1h |

---

## 六、风险与缓解

| 风险 | 缓解措施 |
|------|----------|
| `/grill-with-docs` 产出与 STANDARDS.md 冲突 | 优先级规则：STANDARDS.md > skills |
| `/improve-codebase-architecture` 建议过度重构 | 限定分析范围到审计子文档，不扩展到未审计域 |
| `/tdd` 对 Python 后端适配不佳 | 后端已有 pytest 基础，TDD 直接融入 |
| Issue 数量过多（22 个） | 分 4 批执行，每批有明确的完成标准 |
| OpenSpec 审批阻塞第三批 | 第二批不依赖 OpenSpec，可并行推进 |

---

*参考来源*:
- [mattpocock/skills GitHub](https://github.com/mattpocock/skills)
- [How To Use Matt Pocock's Skills: A Complete Guide](https://tosea.ai/blog/matt-pocock-skills-claude-code-guide)
- [How To De-Slop A Codebase Ruined By AI (YouTube)](https://www.youtube.com/watch?v=3MP8D-mdheA)
