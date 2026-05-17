# MyStocks 后端审计 Phase 2 总结与 Phase 3 计划

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **日期**: 2026-05-16
> **状态**: 待审核
> **前置文档**: `docs/reports/quality/backend-audit-2026-05-14.md`

---

## 一、已完成工作总览（Phase 0-2）

### Phase 0: 前置准备 ✅

| 产出 | 文件 | 说明 |
|------|------|------|
| 共享术语文档 | `web/backend/CONTEXT.md` | 建立架构术语、路由注册真相、健康端点体系、日志生态、残留文件清册、治理术语 |
| 应用方案 | `docs/reports/quality/mattpocock-skills-backend-audit-application-plan.md` | 5 阶段执行方案 |

### Phase 1: 审计文档事实校准 ✅

| 产出 | 说明 |
|------|------|
| 健康端点校准 | 确认 6 个 canonical 端点 + 18 个碎片端点，含代码行号定位 |
| 残留文件清册更新 | 重扫工作树，记录 9 个已删除文件 + 剩余待处理项 |
| 审计主文档更新 | §2.4 和 §5.5 事实校准 |

### Phase 4 第一批: 快速修复 ✅（提前执行）

| 产出 | 文件 | 说明 |
|------|------|------|
| 统一日志门面 | `web/backend/app/core/logger.py` | STANDARDS.md §1.4 要求的 `from app.core.logger import logger` |
| OpenTelemetry 修复 | `web/backend/app/core/logging/__init__.py` | tracing 导入改为 optional，消除 ImportError |
| print() 清理 | `mock/coverage_report.py`, `mock/simple_coverage_check.py`, `mock/mock_data/factory.py`, `schemas/base_schemas.py` | 合计 64 处 print() → logger.info/error |
| 残留文件删除 | 9 个 .bak/.backup/.old 文件 | 代码路径判定通过，无 import 引用 |

### Phase 2: 架构深度分析 ✅

| 产出 | 文件 | 说明 |
|------|------|------|
| 架构分析报告 | `docs/reports/quality/backend-architecture-analysis-2026-05-16.md` | Core 目录功能域分析、Singleton 全量分析、API 迁移状态、深化机会清单 |
| ADR-0001 | `docs/architecture/0001-core-directory-restructure.md` | Core 按职责拆分子目录 |
| ADR-0002 | `docs/architecture/0002-api-flat-to-package-migration.md` | API flat→package 迁移策略 |
| ADR-0003 | `docs/architecture/0003-singleton-to-di-migration.md` | Singleton→FastAPI Depends 迁移路径 |
| CONTEXT.md 更新 | `web/backend/CONTEXT.md` | 反映 singleton 118 处、Core 75 文件、API 迁移状态 |

### Git 提交

| 提交 | 内容 |
|------|------|
| `e60c68e7b` | Phase 0-1 + 第一批快速修复（12 文件：7 新增、5 修改） |
| 待提交 | Phase 2 产出（7 文件：1 新增报告、3 新增 ADR、1 更新 CONTEXT.md、2 boundary note） |

---

## 二、Phase 2 关键发现

### 2.1 Core 目录

| 指标 | 数值 |
|------|------|
| Python 文件 | 75 |
| 总行数 | 26,429 |
| Singleton 实例 | 45 |
| 重复文件组 | 5 组 |

最大类别是 **"other"（未分类）**：21 文件、6,429 行，需逐个归类。

重复文件组：
- exception ×3（`exception_handler.py` + `exception_handlers.py` + `global_exception_handlers.py`）
- validation ×3（`validation.py` + `validators.py` + `validation_messages.py`）
- cache ×12（根级 5 + 子目录 7）
- database_performance ×2
- tdengine ×2

### 2.2 Singleton 模式

全量统计从原始审计的"32 处"修正为 **118 处**：

| 层 | 数量 |
|----|------|
| Core | 45 |
| Services | 35 |
| Adapters | 5 |
| API | 12 |
| 其他（tasks/strategies/utils） | 21 |

所有 118 个 singleton 均为 **per-app** 生命周期，迁移到 FastAPI `Depends()` 风险较低。

### 2.3 API Flat/Package 迁移

| 类型 | 数量 |
|------|------|
| Flat 文件 | 64 |
| Package 目录 | 20 |
| 重叠域（双形态并存） | 10 |

**发现的 Bug**: `announcement` 在 `router_registry.py` 中被注册两次（第 78 行 via VERSION_MAPPING + 第 96 行直接注册）。前端和测试全部使用 `/api/announcement/*` 路径（来自第 96 行的直接注册），VERSION_MAPPING 创建的 `/api/v1/announcement/*` 路径几乎无消费者。修复前需确定 canonical 路径。

**混乱度最高的域**:
- 策略域: 3 个 flat 文件（`strategy.py` + `strategy_management.py` + `strategy_mgmt.py`）+ 1 个 package
- 风控域: 3 个 flat 文件 + 2 个 package 目录（`risk/` + `risk_v31/`）

### 2.4 深化机会清单（按优先级）

| # | 机会 | 严重度 | 复杂度 | 前置条件 |
|---|------|--------|--------|----------|
| D-1 | 修复 announcement 双注册 bug | 高 | 中 | 需确定 canonical 路径 |
| D-2 | 合并 Core exception ×3 → 1 canonical | 中 | 中 | OpenSpec |
| D-3 | 合并 Core validation ×3 → 1 canonical | 中 | 低 | 无 |
| D-4 | Core cache 根级文件移入 cache/ 子目录 | 中 | 中 | GitNexus impact |
| D-5 | Core database 文件提取 database/ 子目录 | 中 | 高 | GitNexus impact |
| D-6 | 低复杂度域 flat→package 收口（7 域） | 中 | 低-中 | 逐域双判定 |
| D-7 | market 域 flat→package 收口 | 中 | 中 | 功能对比 |
| D-8 | 策略域 3 flat → 1 canonical | 高 | 高 | OpenSpec |
| D-9 | 风控域 5 入口收敛 | 高 | 高 | OpenSpec |
| D-10 | Core singleton→Depends（database 层） | 中 | 中 | D-5 后 |
| D-11 | Services singleton→Depends | 中 | 高 | D-10 后 |
| D-12 | 健康端点 18 碎片收敛 | 中 | 中 | 路由表重测 |

---

## 三、Phase 3 计划：审计发现转 GitHub Issues

### 3.1 目标

将 Phase 2 深化机会清单 + 原始审计子文档 A/B/C/E/F/G/H/I 的发现转化为可独立抓取的 GitHub Issues。

### 3.2 Issue 拆分

#### 第一批 — 立即可修复（无 OpenSpec 依赖）

| # | Issue 标题 | 来源 | 严重度 | 预估 |
|---|-----------|------|--------|------|
| 1 | `audit(D-1): 确定 announcement canonical 路径并修复双注册` | D-1 | 高 | 1h |
| 2 | `audit(D-3): 合并 Core validation ×3 → 1 canonical` | D-3 | 中 | 2h |
| 3 | `audit(B): 重扫工作树，更新残留文件清册` | 子文档 B | 中 | 1h |
| 4 | `audit(B): 删除已确认的 4 个 _new.py 文件中的冗余副本` | 子文档 B | 中 | 2h |
| 5 | `audit(B): 确认 monitoring_old 无活跃引用后删除` | 子文档 B | 中 | 1h |

#### 第二批 — 低风险改进（2 周内）

| # | Issue 标题 | 来源 | 严重度 | 预估 |
|---|-----------|------|--------|------|
| 6 | `audit(G): 重测 route table，确认 24 个健康端点的当前实际路径` | 子文档 G | 中 | 3h |
| 7 | `audit(D-6): algorithms 域 flat→package 收口` | D-6 | 中 | 3h |
| 8 | `audit(D-6): indicators 域 flat→package 收口` | D-6 | 中 | 3h |
| 9 | `audit(D-6): stock_search 域 flat→package 收口` | D-6 | 中 | 3h |
| 10 | `audit(D-6): multi_source 域 flat→package 收口` | D-6 | 中 | 3h |
| 11 | `audit(D-6): system 域 flat→package 收口` | D-6 | 中 | 3h |
| 12 | `audit(D-6): backup_recovery_secure 域 flat→package 收口` | D-6 | 中 | 3h |
| 13 | `audit(D-6): signal_monitoring 域 flat→package 收口` | D-6 | 中 | 3h |
| 14 | `audit(D-4): Core cache 根级文件移入 cache/ 子目录` | D-4 | 中 | 4h |
| 15 | `audit(D-2): 合并 Core exception ×3 → 1 canonical` | D-2 | 中 | 4h |

#### 第三批 — 中风险重构（需 OpenSpec 审批，2-4 周）

| # | Issue 标题 | 来源 | 严重度 | 预估 |
|---|-----------|------|--------|------|
| 16 | `audit(D-7): market 域 flat→package 收口` | D-7 | 中 | 6h |
| 17 | `audit(D-5): Core database 文件提取 database/ 子目录` | D-5 | 中 | 6h |
| 18 | `audit(D-5): Core security 文件提取 security/ 子目录` | ADR-0001 | 中 | 4h |
| 19 | `audit(D-5): Core socketio 文件提取 socketio/ 子目录` | ADR-0001 | 中 | 4h |
| 20 | `audit(D-8): 策略域 3 flat → 1 canonical 路由选择` | 子文档 H | 高 | 8h |
| 21 | `audit(D-9): 风控域 5 入口 → canonical 收敛` | 子文档 I | 高 | 8h |
| 22 | `audit(D-12): 健康端点碎片收敛到 health.py 统一体系` | 子文档 G | 中 | 6h |
| 23 | `audit(F): schema/ + schemas/ 双目录合并` | 子文档 F | 中 | 4h |

#### 第四批 — 长期优化（1-3 月）

| # | Issue 标题 | 来源 | 严重度 | 预估 |
|---|-----------|------|--------|------|
| 24 | `audit(D-10): Core 层 singleton→FastAPI Depends（database 批次）` | ADR-0003 | 中 | 8h |
| 25 | `audit(D-11): Services 层 singleton→FastAPI Depends` | ADR-0003 | 中 | 16h |
| 26 | `audit(E): Core "other" 21 文件分类与归属` | Phase 2 | 中 | 4h |

### 3.3 Issue 模板

每个 Issue 使用以下标签和格式：

```
Labels: tech-debt, audit-finding
Milestone: Backend Audit 2026-Q2

## 来源
[审计子文档 / 深化机会编号]

## 当前状态
[代码事实描述]

## 目标状态
[期望的 canonical 状态]

## 验收标准
- [ ] 双判定表完成（代码路径 + 功能树）
- [ ] 相关测试通过
- [ ] router_registry.py 更新（如涉及路由）
- [ ] CONTEXT.md 更新（如涉及术语变更）

## 前置条件
[如有 OpenSpec 审批需求则标注]
```

### 3.4 执行约束

- 第一批 Issue 可立即创建并开始执行
- 第二批 Issue 创建后按优先级顺序执行，每个 Issue 完成后再开始下一个
- 第三批 Issue 创建时需同步创建 OpenSpec proposal，审批通过后才能开始实现
- 第四批 Issue 创建为 draft，待第三批完成后再排期

---

## 四、风险与待确认项

| # | 风险 | 缓解措施 |
|---|------|----------|
| 1 | Announcement 双注册修复可能影响前端路径 | 需先确认 `versionNegotiationPolicy.ts` 是否将 v1 路径重定向到非 v1 路径 |
| 2 | flat→package 收口可能破坏测试引用 | 每个 Issue 的验收标准包含测试更新 |
| 3 | Core 子目录迁移 import 路径变更面大 | 使用 `__init__.py` re-export 保持向后兼容 |
| 4 | 策略域/风控域 3+ 入口选择 canonical 可能有争议 | 需 OpenSpec 审批确定，不凭单方面判断 |

---

*关联文档*:
- 审计主文档: `docs/reports/quality/backend-audit-2026-05-14.md`
- 架构分析: `docs/reports/quality/backend-architecture-analysis-2026-05-16.md`
- ADR-0001: `docs/architecture/0001-core-directory-restructure.md`
- ADR-0002: `docs/architecture/0002-api-flat-to-package-migration.md`
- ADR-0003: `docs/architecture/0003-singleton-to-di-migration.md`
