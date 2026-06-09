# MyStocks 后端质量审计文档二次审核

> **权威来源声明**:
> 本文件是对 `docs/reports/quality/backend-audit-2026-05-14.md` 及其 8 份子文档的审核意见汇总，不是新的仓库共享规则来源。
> 涉及迁移收口、删除判定、指标口径、审批门禁时，以 `architecture/STANDARDS.md`、`openspec/AGENTS.md`、`docs/standards/technical-debt-governance-charter-v1.md` 与当前代码事实为准。
> 本文件仅作为执行前复核清单和整改建议，不能替代 OpenSpec proposal、design、tasks 或代码评审。

> **审核日期**: 2026-05-15
> **审核方式**: `$impeccable audit` 口径适配到 Markdown 治理文档，重点检查信息结构、证据链、可执行性、治理口径和反模式。
> **审核结论**: 当前这组文档不应直接作为执行依据。必须先修正代码事实、补齐 OpenSpec 审批入口、补全删除判定表，再进入实现。

## 一、审核对象

| 编号 | 文档 | 定位 | 当前建议状态 |
|------|------|------|--------------|
| 主 | `docs/reports/quality/backend-audit-2026-05-14.md` | 总体审计入口 | 需补导航与治理边界 |
| A | `docs/reports/quality/backend-logging-fix-2026-05-14.md` | 日志整改 | 已完成关键事实修正，`print()` 门禁复核为 0 |
| B | `docs/reports/quality/backend-residual-files-inventory-2026-05-14.md` | 残留文件清册 | 已重扫当前工作树，剩余候选需双判定 |
| C | `docs/reports/quality/api-flat-to-package-migration-2026-05-14.md` | API flat 到 package 迁移 | 已复核当前事实，只能作为 OpenSpec 输入 |
| E | `docs/reports/quality/backend-singleton-to-di-2026-05-14.md` | Singleton 到 DI | 已补生命周期分类，只能作为 OpenSpec 输入 |
| F | `docs/reports/quality/backend-core-split-plan-2026-05-14.md` | Core 目录拆分 | 需修正兼容层设计并进入 OpenSpec |
| G | `docs/reports/quality/health-endpoint-consolidation-2026-05-14.md` | 健康端点收敛 | 阻塞，验收 URL 与当前代码不一致 |
| H | `docs/reports/quality/backend-strategy-domain-governance-2026-05-14.md` | 策略域治理 | 需重测 router_registry 与测试依赖 |
| I | `docs/reports/quality/backend-risk-domain-governance-2026-05-14.md` | 风控域治理 | 需重测 router_registry 与测试依赖 |

## 二、Impeccable Audit 结果

本次不是前端界面 audit，因此将 `$impeccable audit` 的五个维度映射到文档质量和执行风险。

评分说明：本分数是本次 review 专用的启发式评分，不是仓库正式技术债门禁分。正式门禁仍以 `docs/standards/technical-debt-governance-charter-v1.md` 和 CI 结果为准。

| # | 维度 | 分数 | 主要问题 |
|---|------|------|----------|
| 1 | 信息可达性 | 2/4 | 主文档未链接 A/B/C/E/F/G/H/I，读者无法从主文档进入完整治理链路 |
| 2 | 执行性能 | 2/4 | 多个方案可执行步骤存在，但会测错 URL 或跳过审批门禁 |
| 3 | 治理主题一致性 | 1/4 | 删除清单与 `STANDARDS.md` 删除判定要求不一致 |
| 4 | 适配性 | 2/4 | 文档适合审计阅读，但还不能适配到 OpenSpec 执行流 |
| 5 | 反模式控制 | 1/4 | 存在“删除清单先行”“历史快照冒充当前状态”“未审批架构迁移”三类反模式 |

**Audit Health Score**: 8/20，阻塞级。  
**Anti-Patterns Verdict**: 未通过。当前文档可作为问题线索，不可作为实现指令。

分数阈值：

| 分数 | 判定 |
|------|------|
| 0-8 | 阻塞，必须重测或重写后再审 |
| 9-13 | 草案可用，但必须按阻塞项修正后再执行 |
| 14-17 | 可进入执行准备，仍需完成门禁 |
| 18-20 | 可作为执行输入，但不替代 OpenSpec 审批 |

## 三、P0 阻塞问题

### P0-1：健康端点事实曾与当前代码不一致（Batch 7 已修正）

**影响文档**: 主文档、A、G。

原始主文档曾把 canonical 健康体系写成根路径服务探针和旧 readiness 变体；A/G 文档也曾沿用错误验收路径。

Batch 1 和 Batch 7 已将相关文档修正为当前代码事实：

当前代码事实：

| 事实 | 当前位置 |
|------|----------|
| `health.router` 以 `/api` prefix 注册 | `web/backend/app/router_registry.py:97` |
| `api/health.py` 内部定义 `/health/services` | `web/backend/app/api/health.py:145` |
| 当前就绪探针是 `/health/ready` | `web/backend/app/main.py:674` |
| 当前兼容就绪探针是 `/api/health/ready` | `web/backend/app/main.py:689` |

结论：`/api/health/services` 与 `/api/health/detailed` 才是当前注册路径；`/health/readiness` 未在当前代码中发现；`/health/ready` 与 `/api/health/ready` 是当前就绪探针。

**当前处理状态**:

| 项 | 状态 |
|----|------|
| 主文档 | 已改为当前代码事实，并注明是否收敛到单一 canonical router 需进入 G / OpenSpec 判定 |
| G 文档 | 已补 route table、OpenAPI diff、消费者矩阵和 OpenSpec 前置要求 |
| A 文档 | 已将服务验收 URL 收敛到 `/api/health/services` |

### P0-2：B 清册的“精确扫描”结论过期（Batch 3 已修正）

**影响文档**: B、主文档。

B 文档原先混用了旧快照和当前结论，曾把备份文件状态写成可执行清理依据。Batch 3 已按当前工作树重扫后修正为：

| 复核项 | 当前结论 |
|--------|----------|
| `.bak` / `.backup` / `.old.py` / `.before_*` 文件 | 当前扫描为 0 |
| `_new.py` 过渡文件 | 当前 4 个，需逐项补双判定 |
| `api/monitoring_old/` | 当前存在，需确认 route table 与功能树状态 |
| `api/auth_compat.py` | 功能性兼容 shim，不纳入残留删除候选 |

结论：B 文档已不再使用执行性清理结论。它现在只能作为事实清册和判定模板，不能替代实施审批。

**修正要求**:

| 项 | 修改 |
|----|------|
| B 文档 | 已重写为当前扫描结果、候选清单、GitNexus 预检和双判定模板 |
| 主文档 | 已同步为“当前备份文件扫描为 0，剩余候选需双判定” |
| 执行前 | 仍需对 5 个候选对象逐项补代码路径判定和功能树判定 |

### P0-3：删除清单未满足 `STANDARDS.md` 删除判定

**影响文档**: 主文档、G、H、I。B 已在 Batch 3 中修正为判定入口。

`architecture/STANDARDS.md` 明确要求：

| 规则 | 来源 |
|------|------|
| “未引用 / 未使用”不等于“可删除” | `architecture/STANDARDS.md:110` |
| 删除前必须做代码路径判定 | `architecture/STANDARDS.md:112` |
| 删除前必须做功能树判定 | `architecture/STANDARDS.md:113` |
| 仅当代码路径安全且功能树状态为重复冗余或正式下线时才允许删除 | `architecture/STANDARDS.md:114` |
| 状态无法明确时默认不删除 | `architecture/STANDARDS.md:115` |

当前删除建议多处只有“对象 + 理由”，缺少完整判定：

| 文档 | 问题位置 |
|------|----------|
| 主文档 | `docs/reports/quality/backend-audit-2026-05-14.md:234` 到 `docs/reports/quality/backend-audit-2026-05-14.md:236` |
| G | `docs/reports/quality/health-endpoint-consolidation-2026-05-14.md:109` 到 `docs/reports/quality/health-endpoint-consolidation-2026-05-14.md:132` |
| H | `docs/reports/quality/backend-strategy-domain-governance-2026-05-14.md:175` 到 `docs/reports/quality/backend-strategy-domain-governance-2026-05-14.md:184` |
| I | `docs/reports/quality/backend-risk-domain-governance-2026-05-14.md:143` 到 `docs/reports/quality/backend-risk-domain-governance-2026-05-14.md:152` |

**修正要求**: 所有删除清单统一替换为下面的判定表结构：

| 对象 | 功能节点 | 当前状态 | 代码路径判定 | 功能树判定 | 兼容职责 | 删除或保留依据 | 验收命令 |
|------|----------|----------|--------------|------------|----------|----------------|----------|
| 待填 | 待填 | 有效 / 失效但兼容保留 / 实验灰度 / 重复冗余 / 待判定 | 待填 | 待填 | 待填 | 待填 | 待填 |

### P0-4：跨模块架构变更未绑定 OpenSpec 审批入口

**影响文档**: C、E、F、G、H、I。

OpenSpec 要求 proposal、tasks、必要时 design，并且审批后才能实现，见 `openspec/AGENTS.md:10`、`openspec/AGENTS.md:13`、`openspec/AGENTS.md:57`。跨模块或新架构模式需要 `design.md`，见 `openspec/AGENTS.md:207`。

当前 active changes 中未发现与这组后端质量审计收口直接绑定的 change-id。C/E/F/G/H/I 都涉及 API 路由、DI 生命周期、core 拆分、健康端点删除或领域治理，不能只靠 Markdown 报告进入实现。

**修正要求**:

| 方案组 | 建议 OpenSpec |
|--------|---------------|
| C + H + I | `consolidate-backend-api-domain-routers` |
| E | `migrate-backend-singletons-to-lifecycle-di` |
| F | `split-backend-core-modules-with-compatibility-wrappers` |
| G | `consolidate-backend-health-endpoints` |
| A + B | 可作为技术债任务进入同一治理 change，或拆为 `cleanup-backend-logging-and-residual-files` |

## 四、P1 主要问题

### P1-1：H/I 的 router_registry 描述曾需重测（Batch 8/9 已修正）

H 原始文档曾把 `strategy_management.router` 描述为 flat shim 和 package 两次注册。Batch 8 已按当前 `router_registry.py` 修正为：`VERSION_MAPPING["strategy"]`、`strategy_mgmt.router`、`strategy_management.router`、`strategy_list_mock.router` 多入口并存，但当前直接 `strategy_management.router` include 为 1 处。

H 的后续执行入口已收敛为 endpoint parity、OpenAPI diff、消费者矩阵和 OpenSpec design，不再作为删除清单。

I 原始文档曾把 `risk_management.py`、`risk_management_core.py`、`risk_management_v31.py` 描述为 `router_registry.py` import 列表中的直接引用。

Batch 9 已按当前代码修正为：`router_registry.py` 只看到 `from .api import risk` 与 `app.include_router(risk.router)`，但 `risk_management`、`app.api.risk`、`/api/v1/risk`、`/api/risk`、`/risk/` 仍有大量代码/测试/前端/脚本文本引用，需要消费者矩阵和 OpenSpec 判定。

**当前处理状态**: H/I 都已把“当前注册事实”重测为最新状态，并区分了“直接运行时注册风险”和“测试、文档、兼容 import 风险”。

### P1-2：F 的 core 兼容层设计不成立

F 计划把 `cache_manager.py` 移到 `core/cache/manager.py`，见 `docs/reports/quality/backend-core-split-plan-2026-05-14.md:249`。

但又说旧路径 `from app.core.cache_manager import get_cache_manager` 可由 `cache/__init__.py` 重导出兼容，见 `docs/reports/quality/backend-core-split-plan-2026-05-14.md:323`。

这个兼容方式不成立。`cache/__init__.py` 只能兼容 `app.core.cache`，不能让 `app.core.cache_manager` 继续可导入。若要兼容旧路径，必须保留 `app/core/cache_manager.py` 作为薄 wrapper，或批量更新全部 importer。

当前复核发现 `app.core.cache_manager` import 字符串仍有 16 处，涉及 API、core、tests 和 scripts。F 文档必须将兼容策略改成“旧模块薄 wrapper + 新 canonical package”，并为 wrapper 设退场条件。

### P1-3：主文档没有履行主文档导航职责

主文档开头只有审计入口、规范基准、日期、范围，见 `docs/reports/quality/backend-audit-2026-05-14.md:1` 到 `docs/reports/quality/backend-audit-2026-05-14.md:6`。它没有链接 A/B/C/E/F/G/H/I，也没有标注哪些子文档可执行、哪些阻塞、哪些待重测。

**修正要求**: 主文档新增“子文档索引与执行状态”章节：

| 子文档 | 主题 | 状态 | 阻塞项 | OpenSpec |
|--------|------|------|--------|----------|
| A | 日志 | 已修正关键事实 | 结构化日志深治理另行立项 | 待绑定 |
| B | 残留文件 | 已重扫 | 候选对象双判定不完整 | 待绑定 |
| C | API 迁移 | 待审批 | 删除判定、兼容路径 | 待创建 |
| E | DI | 待审批 | 生命周期分类 | 待创建 |
| F | Core 拆分 | 待审批 | 兼容 wrapper 设计 | 待创建 |
| G | 健康端点 | 阻塞 | 当前 URL 错误 | 待创建 |
| H | 策略域 | 待重测 | router_registry 事实 | 待创建 |
| I | 风控域 | 待重测 | router_registry 事实 | 待创建 |

## 五、P2 次要问题

### P2-1：E 的 DI 模板会改变服务生命周期

E 文档的迁移模板直接在 dependency 函数中 `return MyService(dep1=..., dep2=...)`，见 `docs/reports/quality/backend-singleton-to-di-2026-05-14.md:212` 与 `docs/reports/quality/backend-singleton-to-di-2026-05-14.md:216`。

这对轻量纯函数服务可以，但对 adapter、cache、connection-backed service、backtest engine 可能会改变缓存、连接复用和释放语义。

**修正要求**: 按生命周期分层：

| 类型 | 推荐方式 |
|------|----------|
| Stateless helper | request dependency 可直接创建 |
| Heavy service | lifespan 初始化，依赖函数读取 app.state |
| Adapter factory | factory 管理实例，测试用 dependency_overrides 注入 mock factory |
| Cache/connection-backed service | 显式 close 或 lifespan teardown |

### P2-2：A 的 logger 迁移模板会丢失模块名

A 定义了 `get_logger(name)`，见 `docs/reports/quality/backend-logging-fix-2026-05-14.md:93`。

但替换模板要求所有模块直接导入同一个 `logger`，见 `docs/reports/quality/backend-logging-fix-2026-05-14.md:102`。这会把原先 `logging.getLogger(__name__)` 的模块维度压平成统一 `mystocks` logger。

**修正要求**: 替换模板改成：

```python
from app.core.logging.logger import get_logger

logger = get_logger(__name__)
```

如需统一字段，可在 `get_logger(__name__)` 中 bind `component` 或 `module`。

### P2-3：指标口径需要区分实测值、历史快照、推断值和目标值

`architecture/STANDARDS.md` 要求审计和技术债报告必须区分实测值、历史基线、推断值和目标值，见 `architecture/STANDARDS.md:120` 到 `architecture/STANDARDS.md:123`。

主文档和子文档里的 `20+`、`80+`、`100+`、`1 天`、`2 周` 等数字需要补统计命令、扫描范围、日期和是否为估算。

## 六、建议修改后的执行流

### Step 1：先修文档事实

| 动作 | 产物 |
|------|------|
| 重测 health 路由表 | 更新 G 与主文档 |
| 重扫 residual 文件 | 更新 B |
| 重测 router_registry | 更新 C/H/I |
| 重扫 import/test 引用 | 更新 C/F/H/I |

### Step 2：再建 OpenSpec

每个跨模块方案至少包含：

| 文件 | 内容 |
|------|------|
| `proposal.md` | 为什么改、改什么、影响范围 |
| `design.md` | canonical 模块、兼容层、迁移顺序、回滚策略 |
| `tasks.md` | 可勾选任务，按风险分批 |
| `specs/*/spec.md` | 涉及 API 或能力变化时必须写 delta |

OpenSpec 触发边界：

| 变更类型 | 处理方式 |
|----------|----------|
| 仅修文档事实、补引用、补验收 URL | 技术债任务即可 |
| 仅清理已完成双判定的备份文件 | 技术债任务即可 |
| 修改 API 路由、删除端点、改变 OpenAPI | 必须 OpenSpec |
| 改 DI 生命周期、core 包结构、兼容 import 面 | 必须 OpenSpec |
| 删除仍可能被测试、文档或运行时字符串引用的对象 | 必须 OpenSpec 或显式审批 |

### Step 3：按最小批次执行

优先级建议：

| 批次 | 内容 | 负责人 | 审批者 | 预估 | 回滚触发 |
|------|------|--------|--------|------|----------|
| 1 | 修正文档事实与验收 URL | 文档维护者 | 主 CLI | S | 行号或 URL 复核失败 |
| 2 | 日志 print 清理 | 后端执行者 | 主 CLI | S | ruff 或服务启动失败 |
| 3 | 残留文件治理 | 后端执行者 | 主 CLI | M | 双判定表不完整 |
| 4 | 健康端点收敛 | 后端执行者 | OpenSpec 审批者 | M | OpenAPI diff 异常 |
| 5 | API/domain/core/DI 重构 | 后端执行者 | OpenSpec 审批者 | L | import smoke 失败 |

批次说明：

- 批次 1 不改代码，回滚方式是还原对应文档段落。
- 批次 2 和 3 只允许处理边界明确的技术债，不改变公开 API。
- 批次 4 和 5 必须先通过 OpenSpec 审批，再按 tasks 分批提交。
- 每批执行者负责记录命令输出，审批者负责确认是否进入下一批。

## 七、建议验收清单

| 检查项 | 建议命令或证据 | 通过标准 |
|--------|----------------|----------|
| Markdown 边界说明 | `python scripts/compliance/markdown_governance_gate.py --root-dir . --format text` | 相关文档通过 |
| OpenSpec 绑定 | `openspec list` 与对应 `openspec validate <change-id> --strict` | 每个跨模块方案有 approved change |
| 健康端点事实 | 导出 FastAPI OpenAPI 或检查 route table | URL 与文档一致 |
| 残留文件事实 | 重新扫描 `web/backend/app` | 文档列出的存在状态与当前工作树一致 |
| 删除判定 | 删除表含代码路径判定和功能树判定 | 不再出现仅凭“可删除”的清单 |
| API 兼容性 | import smoke tests 与 OpenAPI diff | 无意外删除路由 |
| 后端质量 | `ruff`、`mypy`、`pytest` 按仓库门禁执行 | 不新增回归 |

## 八、逐文档 Audit 结果

逐份 audit 后的结论：最终 review 原先已覆盖关键风险，但没有逐文档评分和执行判定。本节补齐该缺口。评分沿用本文件第二节的 5 个维度，每项 0 到 4 分，总分 20 分。

### 8.1 主文档：`backend-audit-2026-05-14.md`

| 维度 | 分数 | 结论 |
|------|------|------|
| 信息可达性 | 3/4 | 已补权威来源声明、子文档索引和复核报告入口 |
| 事实证据 | 3/4 | 已同步残留文件、健康端点、DI、Core、策略域和风控域当前复核事实 |
| 治理门禁 | 3/4 | 已明确删除判定、迁移收口和跨模块架构变化需回到 STANDARDS/OpenSpec |
| 验收可执行性 | 3/4 | 已把执行建议分流到 A/B/C/E/F/G/H/I 子文档和 Batch 记录 |
| 反模式控制 | 3/4 | 已标明主文档是审计快照，不是直接执行计划 |

**修正后 Score**: 15/20。  
**Verdict**: 可作为后端质量审计导航入口和 OpenSpec 前置材料，不能作为代码实施任务。  
**主要证据**:

- `docs/reports/quality/backend-audit-2026-05-14.md:1` 到 `docs/reports/quality/backend-audit-2026-05-14.md:6`
- `docs/reports/quality/backend-audit-2026-05-14.md:15` 到 `docs/reports/quality/backend-audit-2026-05-14.md:28`
- `docs/reports/quality/backend-audit-2026-05-14.md:215` 到 `docs/reports/quality/backend-audit-2026-05-14.md:228`
- `docs/reports/quality/backend-audit-2026-05-14.md:296` 到 `docs/reports/quality/backend-audit-2026-05-14.md:299`

### 8.2 A：`backend-logging-fix-2026-05-14.md`

| 维度 | 分数 | 结论 |
|------|------|------|
| 信息可达性 | 3/4 | 结构清楚，有来源和验收表 |
| 事实证据 | 3/4 | 已复核 `web/backend/app` 当前 `print()` 为 0，健康验收 URL 已修正 |
| 治理门禁 | 3/4 | 日志整改可作为技术债任务，深层结构化日志治理仍需任务绑定 |
| 验收可执行性 | 4/4 | 有 grep、PM2、curl 检查，且 `print()` 门禁可直接执行 |
| 反模式控制 | 3/4 | 已改为 `get_logger(__name__)` 口径，避免统一单例 logger 丢模块名 |

**修正后 Score**: 16/20。  
**Verdict**: 可作为日志治理门禁文档；结构化日志深治理仍应作为独立任务执行。  
**主要证据**:

- `docs/reports/quality/backend-logging-fix-2026-05-14.md:55`
- `docs/reports/quality/backend-logging-fix-2026-05-14.md:93`
- `docs/reports/quality/backend-logging-fix-2026-05-14.md:102`
- `docs/reports/quality/backend-logging-fix-2026-05-14.md:195`

### 8.3 B：`backend-residual-files-inventory-2026-05-14.md`

| 维度 | 分数 | 结论 |
|------|------|------|
| 信息可达性 | 3/4 | 清册结构可读 |
| 事实证据 | 3/4 | 已按当前工作树重扫，列出 0 个备份文件和 5 个剩余候选 |
| 治理门禁 | 3/4 | 已移除直接删除口径，补充双判定和 OpenSpec 边界 |
| 验收可执行性 | 3/4 | 有扫描范围、GitNexus 预检和候选判定模板 |
| 反模式控制 | 3/4 | 不再把 `_new.py`、compat shim 或旧路由目录按文件名删除 |

**修正后 Score**: 15/20。  
**Verdict**: 可作为当前事实清册和判定入口；不能作为删除实施计划。  
**主要证据**:

- `docs/reports/quality/backend-residual-files-inventory-2026-05-14.md:13` 到 `docs/reports/quality/backend-residual-files-inventory-2026-05-14.md:33`
- `docs/reports/quality/backend-residual-files-inventory-2026-05-14.md:54` 到 `docs/reports/quality/backend-residual-files-inventory-2026-05-14.md:84`

### 8.4 C：`api-flat-to-package-migration-2026-05-14.md`

| 维度 | 分数 | 结论 |
|------|------|------|
| 信息可达性 | 3/4 | 域拆分和阶段结构清楚 |
| 事实证据 | 3/4 | 已按当前 API 目录和 `router_registry.py` 重扫 flat/package 状态 |
| 治理门禁 | 3/4 | 已明确 API 路由、OpenAPI 和 canonical 变化必须先走 OpenSpec |
| 验收可执行性 | 3/4 | 已补 route table、OpenAPI diff、import smoke 和消费者扫描要求 |
| 反模式控制 | 3/4 | 不再按统一模板处理所有 flat 文件，区分 shim、facade、package 化域和旧目录 |

**修正后 Score**: 15/20。  
**Verdict**: 可作为 OpenSpec design 输入和事实复核入口，不能作为实施任务。  
**主要证据**:

- `docs/reports/quality/api-flat-to-package-migration-2026-05-14.md:14` 到 `docs/reports/quality/api-flat-to-package-migration-2026-05-14.md:32`
- `docs/reports/quality/api-flat-to-package-migration-2026-05-14.md:148` 到 `docs/reports/quality/api-flat-to-package-migration-2026-05-14.md:158`
- `docs/reports/quality/api-flat-to-package-migration-2026-05-14.md:226` 到 `docs/reports/quality/api-flat-to-package-migration-2026-05-14.md:248`

### 8.5 E：`backend-singleton-to-di-2026-05-14.md`

| 维度 | 分数 | 结论 |
|------|------|------|
| 信息可达性 | 3/4 | 问题、阶段、模板清楚 |
| 事实证据 | 3/4 | 已补 2026-05-17 当前扫描数量，并说明仓库已混用 getter、Depends、factory、lifespan 与 app.state |
| 治理门禁 | 3/4 | 已明确 DI lifecycle、初始化方式、测试 override 和跨模块依赖模式必须先走 OpenSpec |
| 验收可执行性 | 3/4 | 已从 `global _` 清零改为生命周期分类、override、lifespan、teardown 和 OpenSpec validate |
| 反模式控制 | 3/4 | 已禁止机械把所有 singleton / getter 改成请求级 `Depends()`，按生命周期分流 |

**修正后 Score**: 15/20。  
**Verdict**: 可作为 OpenSpec design 输入和生命周期分类入口，不能作为代码实施任务。  
**主要证据**:

- `docs/reports/quality/backend-singleton-to-di-2026-05-14.md:16` 到 `docs/reports/quality/backend-singleton-to-di-2026-05-14.md:26`
- `docs/reports/quality/backend-singleton-to-di-2026-05-14.md:168` 到 `docs/reports/quality/backend-singleton-to-di-2026-05-14.md:206`
- `docs/reports/quality/backend-singleton-to-di-2026-05-14.md:214` 到 `docs/reports/quality/backend-singleton-to-di-2026-05-14.md:219`
- `docs/reports/quality/backend-singleton-to-di-2026-05-14.md:264` 到 `docs/reports/quality/backend-singleton-to-di-2026-05-14.md:270`

### 8.6 F：`backend-core-split-plan-2026-05-14.md`

| 维度 | 分数 | 结论 |
|------|------|------|
| 信息可达性 | 3/4 | 结构详细，目标目录清楚 |
| 事实证据 | 3/4 | 已补当前 `core/` 文件数、功能子目录和高风险 import 引用数量 |
| 治理门禁 | 3/4 | 已明确 Core 拆分、canonical import、wrapper 退役和 logger 入口变化必须先走 OpenSpec |
| 验收可执行性 | 3/4 | 已补 import smoke、runtime smoke、wrapper 退场条件和 rollback 要求 |
| 反模式控制 | 3/4 | 已纠正 `core/__init__.py` 通用兼容误区，并保留 `app.core.logger` canonical 入口 |

**修正后 Score**: 15/20。  
**Verdict**: 可作为 OpenSpec design 输入和 Core 拆分事实复核入口，不能作为代码实施任务。  
**主要证据**:

- `docs/reports/quality/backend-core-split-plan-2026-05-14.md:13` 到 `docs/reports/quality/backend-core-split-plan-2026-05-14.md:26`
- `docs/reports/quality/backend-core-split-plan-2026-05-14.md:294` 到 `docs/reports/quality/backend-core-split-plan-2026-05-14.md:327`
- `docs/reports/quality/backend-core-split-plan-2026-05-14.md:331` 到 `docs/reports/quality/backend-core-split-plan-2026-05-14.md:376`
- `docs/reports/quality/backend-core-split-plan-2026-05-14.md:390` 到 `docs/reports/quality/backend-core-split-plan-2026-05-14.md:399`

### 8.7 G：`health-endpoint-consolidation-2026-05-14.md`

| 维度 | 分数 | 结论 |
|------|------|------|
| 信息可达性 | 3/4 | 端点清单易读 |
| 事实证据 | 3/4 | 已补 2026-05-17 装饰器级扫描、错误路径清零和当前 canonical 探针事实 |
| 治理门禁 | 3/4 | 已明确 canonical 变更、旧端点退役、OpenAPI 暴露面和探针切换必须先走 OpenSpec |
| 验收可执行性 | 3/4 | 已补 route table、OpenAPI diff、消费者矩阵、canonical curl 和 rollback 要求 |
| 反模式控制 | 3/4 | 已禁止直接删除所有分散端点，不再以 404 作为退役验收 |

**修正后 Score**: 15/20。  
**Verdict**: 可作为 OpenSpec design 输入和健康端点事实复核入口，不能作为代码实施任务。  
**主要证据**:

- `docs/reports/quality/health-endpoint-consolidation-2026-05-14.md:13` 到 `docs/reports/quality/health-endpoint-consolidation-2026-05-14.md:23`
- `docs/reports/quality/health-endpoint-consolidation-2026-05-14.md:29` 到 `docs/reports/quality/health-endpoint-consolidation-2026-05-14.md:39`
- `docs/reports/quality/health-endpoint-consolidation-2026-05-14.md:187` 到 `docs/reports/quality/health-endpoint-consolidation-2026-05-14.md:220`
- `docs/reports/quality/health-endpoint-consolidation-2026-05-14.md:224` 到 `docs/reports/quality/health-endpoint-consolidation-2026-05-14.md:234`

### 8.8 H：`backend-strategy-domain-governance-2026-05-14.md`

| 维度 | 分数 | 结论 |
|------|------|------|
| 信息可达性 | 3/4 | 策略域拆解清楚 |
| 事实证据 | 3/4 | 已补当前文件大小、package 文件数、router_registry 注册事实和消费者引用数量 |
| 治理门禁 | 3/4 | 已明确 canonical router、OpenAPI、shim、测试/前端路径和旧文件退役必须先走 OpenSpec |
| 验收可执行性 | 3/4 | 已补 endpoint parity、OpenAPI diff、消费者矩阵、import smoke、前端 API 调用和 rollback |
| 反模式控制 | 3/4 | 已禁止用“内容已合并”作为删除依据，并保留 shim/mock/router 兼容判断 |

**修正后 Score**: 15/20。  
**Verdict**: 可作为 OpenSpec design 输入和策略域事实复核入口，不能作为代码实施任务。  
**主要证据**:

- `docs/reports/quality/backend-strategy-domain-governance-2026-05-14.md:12` 到 `docs/reports/quality/backend-strategy-domain-governance-2026-05-14.md:26`
- `docs/reports/quality/backend-strategy-domain-governance-2026-05-14.md:57` 到 `docs/reports/quality/backend-strategy-domain-governance-2026-05-14.md:80`
- `docs/reports/quality/backend-strategy-domain-governance-2026-05-14.md:165` 到 `docs/reports/quality/backend-strategy-domain-governance-2026-05-14.md:172`
- `docs/reports/quality/backend-strategy-domain-governance-2026-05-14.md:176` 到 `docs/reports/quality/backend-strategy-domain-governance-2026-05-14.md:208`
- `docs/reports/quality/backend-strategy-domain-governance-2026-05-14.md:212` 到 `docs/reports/quality/backend-strategy-domain-governance-2026-05-14.md:222`

### 8.9 I：`backend-risk-domain-governance-2026-05-14.md`

| 维度 | 分数 | 结论 |
|------|------|------|
| 信息可达性 | 3/4 | 风控域候选对象清楚 |
| 事实证据 | 3/4 | 已补当前 shim、legacy API、risk package、service package、router_registry 和消费者引用事实 |
| 治理门禁 | 3/4 | 已明确 canonical router、OpenAPI、shim/compat 退役、service 合并和前端路径变化必须先走 OpenSpec |
| 验收可执行性 | 3/4 | 已补 endpoint parity、OpenAPI diff、消费者矩阵、import smoke、前端 API 调用和 rollback |
| 反模式控制 | 3/4 | 已禁止直接删除 `_new`、`_2`、shim 或 legacy API，要求双判定和兼容职责确认 |

**修正后 Score**: 15/20。  
**Verdict**: 可作为 OpenSpec design 输入和风控域事实复核入口，不能作为代码实施任务。  
**主要证据**:

- `docs/reports/quality/backend-risk-domain-governance-2026-05-14.md:12` 到 `docs/reports/quality/backend-risk-domain-governance-2026-05-14.md:32`
- `docs/reports/quality/backend-risk-domain-governance-2026-05-14.md:70` 到 `docs/reports/quality/backend-risk-domain-governance-2026-05-14.md:78`
- `docs/reports/quality/backend-risk-domain-governance-2026-05-14.md:123` 到 `docs/reports/quality/backend-risk-domain-governance-2026-05-14.md:135`
- `docs/reports/quality/backend-risk-domain-governance-2026-05-14.md:139` 到 `docs/reports/quality/backend-risk-domain-governance-2026-05-14.md:164`
- `docs/reports/quality/backend-risk-domain-governance-2026-05-14.md:168` 到 `docs/reports/quality/backend-risk-domain-governance-2026-05-14.md:177`

### 8.10 逐文档 Audit 总表

逐份分数使用第二节的 review 专用阈值。低于 9 分视为阻塞；9 到 13 分是草案可用但不可直接执行；14 分以上才可进入执行准备。

| 编号 | 文档 | Score | 逐份结论 |
|------|------|-------|----------|
| 主 | `backend-audit-2026-05-14.md` | 15/20 | 已补导航/事实/OpenSpec 边界，可作为审计入口 |
| A | `backend-logging-fix-2026-05-14.md` | 16/20 | 已修正关键事实，可作为日志门禁文档 |
| B | `backend-residual-files-inventory-2026-05-14.md` | 15/20 | 已重扫事实，可作为判定入口 |
| C | `api-flat-to-package-migration-2026-05-14.md` | 15/20 | 已复核事实，只能进入 OpenSpec |
| E | `backend-singleton-to-di-2026-05-14.md` | 15/20 | 已补生命周期分类，只能进入 OpenSpec |
| F | `backend-core-split-plan-2026-05-14.md` | 15/20 | 已补 wrapper/OpenSpec 边界，只能进入 OpenSpec |
| G | `health-endpoint-consolidation-2026-05-14.md` | 15/20 | 已补 route table/OpenAPI/OpenSpec 边界，只能进入 OpenSpec |
| H | `backend-strategy-domain-governance-2026-05-14.md` | 15/20 | 已补当前注册/消费者/OpenSpec 边界，只能进入 OpenSpec |
| I | `backend-risk-domain-governance-2026-05-14.md` | 15/20 | 已补当前注册/消费者/OpenSpec 边界，只能进入 OpenSpec |

## 九、最终结论

这组文档目前适合作为“问题发现材料”、审计导航入口和 OpenSpec 前置输入，不适合作为直接代码实施计划。  
最终版已完成三件事：

1. 修正当前代码事实，尤其是健康端点、残留文件、Core import 面、策略域和风控域 router_registry / consumer 事实。
2. 将 C/E/F/G/H/I 这类跨模块方案收敛为 OpenSpec design 输入，实施前必须先审批。
3. 把删除清单改成符合 `architecture/STANDARDS.md` 的候选判定表，不再作为直接删除指令。

后续如进入代码实施，应先为 C/E/F/G/H/I 建立或更新 OpenSpec proposal/design/tasks；未审批前不建议删除文件、端点或目录。

## 十、复核意见处理记录

本节记录 `docs/reports/quality/backend-audit-documents-review-2026-05-15-review.md` 对本文档提出的后续建议，以及本文件的吸收情况。

| 级别 | 复核意见 | 处理状态 | 落点 |
|------|----------|----------|------|
| Critical | 缺少 owner / approver assignment | 已吸收 | 第六节 Step 3 批次表新增 `负责人` 与 `审批者` |
| Medium | 5 个执行批次缺少时间或工作量估计 | 已吸收 | 第六节 Step 3 批次表新增 `预估` |
| Medium | 批次 2 到 5 缺少 rollback strategy | 已吸收 | 第六节 Step 3 批次表新增 `回滚触发` |
| Medium | OpenSpec 触发边界不够明确 | 已吸收 | 第六节 Step 2 新增 `OpenSpec 触发边界` |
| Low | 8/20 评分为非标准量表 | 已吸收 | 第二节新增评分说明，声明为 review 专用启发式评分 |
| Low | 逐文档分数缺少 pass / fail threshold | 已吸收 | 第二节新增 `分数阈值`，第八节总表前复述阈值 |

处理后状态：

- 外部复核确认的事实准确性结论保留，不重复展开。
- 所有复核建议均已回写到本文档。
- 本文档仍不替代 OpenSpec 审批、代码评审或 CI 门禁。

## 十一、Batch 1 文档事实修正记录

按第六节执行流，已先完成不改代码的 Batch 1：修正文档事实与验收 URL。此批次不删除文件、不改 API、不进入 OpenSpec 实施，只修正 Markdown 中会误导执行的事实口径。

| 文件 | 修正内容 |
|------|----------|
| `backend-audit-2026-05-14.md` | 新增权威来源声明、子文档索引、复核报告入口；修正健康端点事实；将“删除/合并”类立即行动改为复核和规划 |
| `backend-logging-fix-2026-05-14.md` | 将 logger canonical 导入面调整为 `app.core.logger`；保留 `get_logger(__name__)` 模块名；修正健康验收 URL |
| `backend-residual-files-inventory-2026-05-14.md` | 将执行性清理结论改为“待双判定”；移除 shell 删除命令；标记为需按当前工作树重扫 |
| `api-flat-to-package-migration-2026-05-14.md` | 补 OpenSpec 执行门禁；将 shim 删除动作改为先判定；修正 risk flat 文件退役口径 |
| `backend-singleton-to-di-2026-05-14.md` | 补生命周期分类，说明 Depends 只是一类入口形式，重型服务、adapter factory、cache/connection-backed 对象需分流处理 |
| `backend-core-split-plan-2026-05-14.md` | 修正 `cache_manager.py` 兼容策略，明确旧模块路径需要 thin wrapper；修正健康验收 URL |
| `health-endpoint-consolidation-2026-05-14.md` | 修正当前健康端点路径；将删除端点改为逐模块判定；修正验收 URL 与旧端点处理标准 |
| `backend-strategy-domain-governance-2026-05-14.md` | 标记 router_registry 双注册描述需重测；将删除清单改为删除候选和判定要求 |
| `backend-risk-domain-governance-2026-05-14.md` | 修正当前 router_registry 风控注册事实；将删除清单改为删除候选和判定要求 |

Batch 1 自审结果：

- 未发现本次改动文件仍引用错误的 `/health/readiness` 验收路径。
- 未发现本次改动文件仍使用根路径 `/health/services` 作为服务验收 URL。
- 未发现本次改动文件保留直接 `rm app/...` 删除命令。
- 未发现本次改动文件保留可执行误导口径。
- Markdown governance gate 仍因 `.planning/...` 既有历史文档缺边界说明返回失败；本次改动文件没有出现在失败列表中。

## 十二、Batch 2 日志 `print()` 门禁复核记录

按第六节执行流，已进入 Batch 2 的预检与门禁复核。由于 `architecture/STANDARDS.md` 要求代码修改前必须有明确执行审批，本批次先完成事实复核、影响分析和文档状态修正；未进行新的后端代码修改。

| 项 | 结果 |
|----|------|
| 当前扫描范围 | `web/backend/app/**/*.py` |
| 当前 `print()` 数量 | 0 |
| 已确认 logger facade | `web/backend/app/core/logger.py` 存在，导出 `logger`、`get_logger`、`StructuredLogger` |
| 文档修正范围 | 主文档、A 文档、本文档 |
| 本批次代码改动 | 无 |

GitNexus 预检结论：

| 目标 | 结论 |
|------|------|
| `scan_api_files` | LOW，直接上游为 `generate_coverage_report` |
| `scan_frontend_api_calls` | LOW，直接上游为 `generate_coverage_report` |
| `check_mock_support` | LOW，直接上游为 `generate_coverage_report` |
| `generate_coverage_report` in `web/backend/app/mock/coverage_report.py` | context 定位成功，文件级 impact 为 LOW |
| `check_api_mock_support` | LOW，直接上游为脚本文件 |
| `web/backend/app/mock/mock_data/factory.py` | LOW，有多个导入方；仅 `__main__` 演示块曾涉及 `print()` |
| `web/backend/app/schemas/base_schemas.py` | LOW，未发现上游依赖 |

Batch 2 自审结果：

- 当前代码已满足 A 文档的 `print()` 清零验收，不需要再执行机械替换。
- 主文档中“`app/core/logger.py` 不存在”和“`coverage_report.py` 仍有 30+ 处 `print()`”的旧快照已修正。
- A 文档中 Phase 1 已由“待修改代码”改为“已完成复核，门禁保留”。
- Markdown governance gate 仍因既有历史文档返回失败；本批次改动的三份文档没有出现在失败列表中。
- 若后续推进结构化日志深治理、`main.py` 日志初始化调整或跨模块 logging 统一，应作为独立任务，在明确审批后执行。

## 十三、Batch 3 残留文件清册重扫记录

按第六节执行流，已完成 B 文档的当前工作树重扫和文档修正。本批次只更新 Markdown，不删除文件、不移动目录、不修改 import 或路由注册。

| 项 | 结果 |
|----|------|
| 扫描范围 | `web/backend/app/**/*.py` 与残留特征目录 |
| `.bak` / `.backup` / `.old.py` / `.before_*` | 0 |
| `_new.py` 过渡文件 | 4 |
| `*_old/` 目录 | 1，`web/backend/app/api/monitoring_old/` |
| 排除对象 | `web/backend/app/api/auth_compat.py`，功能性兼容 shim |
| 文档修正范围 | 主文档、B 文档、本文档 |
| 本批次代码改动 | 无 |

GitNexus 预检结论：

| 目标 | 结论 |
|------|------|
| `web/backend/app/services/data_adapter_new.py` | LOW，未发现直接上游 |
| `web/backend/app/services/data_api_new.py` | LOW，直接上游为 `web/backend/app/services/__init__.py` |
| `web/backend/app/api/data/data_api_new.py` | LOW，未发现直接上游；文本证据显示被 wrapper 动态加载 |
| `web/backend/app/services/risk_management_new.py` | LOW，未发现直接上游；仍需核对 `services/__init__.py` 中导入路径 |
| `web/backend/app/api/monitoring_old/routes.py` | LOW，未发现直接上游 |

Batch 3 自审结果：

- B 文档已不再声称旧备份文件“当前存在”“已删除”或“可删除”。
- B 文档已移除直接删除命令和先确认后执行清理的口径。
- 主文档已同步为“当前备份文件扫描为 0，剩余候选需双判定”。
- Markdown governance gate 仍因既有历史文档返回失败；本批次改动的三份文档没有出现在失败列表中。
- 剩余候选对象仍不能执行删除；下一步是逐项补代码路径判定和功能树判定，涉及 API 或 canonical 变化时进入 OpenSpec。

## 十四、Batch 4 API flat/package 迁移文档复核记录

按第六节执行流，已完成 C 文档的当前 API 目录和路由注册事实复核。本批次只更新 Markdown，不调整 `router_registry.py`、不修改 API 文件、不改变 OpenAPI 暴露面。

| 项 | 结果 |
|----|------|
| 复核日期 | 2026-05-16 |
| 事实来源 | `web/backend/app/api/`、`web/backend/app/router_registry.py`、`web/backend/app/api/VERSION_MAPPING.py` |
| 当前备份/残留动作 | 无 |
| 当前 API 代码改动 | 无 |
| 文档修正范围 | 主文档、C 文档、本文档 |

当前 API flat/package 事实摘要：

| 域 | 当前结论 |
|----|----------|
| `data` / `trade` / `technical` | 已是 package 形态，不再按 flat-to-package 清理实施计划处理 |
| `market` / `strategy_management` / `system` / `risk_management` | 更像 shim 或 facade，需先判定兼容面和运行时 import 解析 |
| `announcement` | 仍有双前缀暴露风险，是 OpenSpec 候选，但需先做 route table、OpenAPI diff 和消费者扫描 |
| `strategy` / `risk` | 多入口 canonical 不明，分别交由 H/I 文档继续重测 |
| `monitoring_old/` | 仍需功能树判定，不在 C 文档直接下线 |

Batch 4 自审结果：

- C 文档已不再把所有域套用同一种 flat 入口处理模板。
- C 文档已明确 API 路由、OpenAPI 暴露面、canonical 切换和兼容导出面变化必须先走 OpenSpec。
- C 文档已把 `data`、`trade`、`technical` 从本轮 flat-to-package 清理实施计划中移出。
- Markdown governance gate 仍因既有历史文档返回失败；本批次改动的三份文档没有出现在失败列表中。

## 十五、Batch 5 Singleton 到 DI 文档复核记录

按第六节执行流，已完成 E 文档的当前 DI / singleton / lifecycle 事实复核。本批次只更新 Markdown，不修改 FastAPI dependency、service 初始化、router、lifespan 或测试 override。

| 项 | 结果 |
|----|------|
| 复核日期 | 2026-05-17 |
| 扫描范围 | `web/backend/app/**/*.py` |
| 顶层 `_xxx = None` 或 `_xxx: ... = None` | 108 |
| `def get_xxx(...)` 函数 | 200 |
| `Depends(...)` 代码近似命中 | 314 |
| `app.state` / `request.app.state` 引用 | 9 |
| lifespan / shutdown / on_event 相关代码命中 | 19 |
| 文档修正范围 | 主文档、E 文档、本文档 |
| 本批次代码改动 | 无 |

当前生命周期事实摘要：

| 观察 | 结论 |
|------|------|
| 仓库已有 314 处 `Depends(...)` 代码近似命中 | 不能把问题描述为“完全缺少 FastAPI DI” |
| 同时存在 singleton、getter、factory、lifespan、app.state | 治理重点是生命周期分类，不是统一模板替换 |
| 重型服务、cache、DB、adapter factory 可能持有连接、缓存或昂贵构造 | 禁止请求级重复创建，必须设计 close / teardown / override |
| DI lifecycle、初始化方式、测试 override 和跨模块依赖变化 | 必须先进入 OpenSpec proposal/design/tasks 审批 |

Batch 5 自审结果：

- E 文档已不再把所有 singleton / getter 机械迁移为请求级 `Depends()`。
- E 文档已补当前扫描数量和生命周期模型并存事实。
- E 文档已把后续执行入口收敛为 OpenSpec design 输入，不作为直接代码任务。
- 主文档长期优化项已同步为“先按生命周期分类，再用 Depends、factory、lifespan、app.state 或兼容 wrapper 分流处理”。
- Markdown governance gate 仍因既有历史文档返回失败；本批次改动的三份文档没有出现在失败列表中。

## 十六、Batch 6 Core 拆分文档复核记录

按第六节执行流，已完成 F 文档的当前 `core/` 结构、关键 import 面和兼容策略复核。本批次只更新 Markdown，不移动文件、不新增 package、不修改 import、不退役 wrapper。

| 项 | 结果 |
|----|------|
| 复核日期 | 2026-05-17 |
| 扫描范围 | `web/backend/app/core/`、`web/backend/app`、`tests`、`scripts`；文档引用不计入代码阻塞计数 |
| `core/` 顶层 `.py` 文件 | 65 |
| `core/` 功能子目录 | 3，`cache/`、`logging/`、`middleware/` |
| `core/` 全部 `.py` 文件 | 77 |
| `app.core.cache_manager` 代码/测试/脚本文本引用 | 10 |
| `app.core.database` 代码/测试/脚本文本引用 | 91 |
| `app.core.security` 代码/测试/脚本文本引用 | 54 |
| `app.core.logger` 代码/测试/脚本文本引用 | 5 |
| `app.core.socketio_manager` 代码/测试/脚本文本引用 | 2 |
| 文档修正范围 | 主文档、F 文档、本文档 |
| 本批次代码改动 | 无 |

当前 Core 拆分事实摘要：

| 观察 | 结论 |
|------|------|
| `core/__init__.py` 只能兼容 `from app.core import X` | 不能用它保证 `from app.core.cache_manager import X` 继续可导入 |
| `app.core.cache_manager` 和 `app.core.socketio_manager` 不是同名 package 化路径 | 需要旧顶层模块 thin wrapper，或 OpenSpec 批准一次性改完所有 importer |
| `app.core.database`、`app.core.security` 有大量引用 | 若转成同名 package，必须用 package `__init__.py` 保持公开 API 和测试 monkeypatch 路径 |
| `app.core.logger` 是当前标准入口 | 内部 logging 实现可以下沉，但 canonical wrapper 必须保留 |

Batch 6 自审结果：

- F 文档已不再声称当前 `core/` 是“68 个文件 + 3 个子目录，全部平铺”。
- F 文档已明确 Core 拆分、canonical import、wrapper 退役和 logger 入口变化必须先走 OpenSpec。
- F 文档已修正 `core/__init__.py` 通用兼容误区，补充旧模块 wrapper、同名 package `__init__`、import smoke 和 rollback 条件。
- 主文档长期优化项已同步为“先补 canonical import、旧模块 wrapper、import smoke 和 OpenSpec 设计，再按风险拆分”。
- Markdown governance gate 仍因既有历史文档返回失败；本批次改动的三份文档没有出现在失败列表中。

## 十七、Batch 7 健康端点收敛文档复核记录

按第六节执行流，已完成 G 文档的当前健康端点事实、错误路径和收敛门禁复核。本批次只更新 Markdown，不修改 FastAPI route、不删除端点、不改变 OpenAPI 暴露面。

| 项 | 结果 |
|----|------|
| 复核日期 | 2026-05-17 |
| 扫描范围 | `web/backend/app/**/*.py` |
| health-like route decorators | 46 |
| `/health/readiness` 代码文本命中 | 0 |
| `/health/services` 代码文本命中 | 1，位于 `api/health.py`，经 `/api` prefix 暴露为 `/api/health/services` |
| 已确认就绪探针 | `GET /health/ready`、`GET /api/health/ready` |
| 已确认服务探针 | `GET /api/health/services` |
| 文档修正范围 | 主文档、G 文档、本文档 |
| 本批次代码改动 | 无 |

当前健康端点事实摘要：

| 观察 | 结论 |
|------|------|
| `/health/ready` 和 `/api/health/ready` 已存在 | G 的阻塞点不再是 readiness 路径缺失 |
| `/health/readiness` 在当前代码中为 0 | 文档若提到该路径只能标记为历史误判 |
| health-like decorators 有 46 个 | 必须先生成真实 route table 和 OpenAPI diff，不能按文档样本直接删除 |
| 领域 smoke、metrics、SSE、adapter/database health 混杂 | 收敛前必须建立消费者矩阵和兼容期 |

Batch 7 自审结果：

- G 文档已修正 canonical 路径事实，保留 `/api/health/services`、`/api/health/detailed`、`/health/ready`、`/api/health/ready` 等当前入口。
- G 文档已把“删除所有分散端点”改成 route table、OpenAPI diff、消费者矩阵和 OpenSpec 前置。
- G 文档已移除“只剩 health.py 才算通过”的验收口径，不再以 404 作为旧端点退役验收。
- 主文档子文档索引已同步为“已补 route table/OpenAPI/OpenSpec 边界，只能作为 OpenSpec 输入”。
- Markdown governance gate 仍因既有历史文档返回失败；本批次改动的三份文档没有出现在失败列表中。

## 十八、Batch 8 策略域治理文档复核记录

按第六节执行流，已完成 H 文档的当前策略域文件、router_registry 注册和消费者引用复核。本批次只更新 Markdown，不修改 router_registry、不移动 API 文件、不删除 shim、不改变前端路径。

| 项 | 结果 |
|----|------|
| 复核日期 | 2026-05-17 |
| `api/strategy.py` | 存在，约 25KB / 742 行 |
| `api/strategy_mgmt.py` | 存在，约 29KB / 863 行 |
| `api/strategy_management.py` | 存在，101 bytes / 3 行，兼容 shim 候选 |
| `api/strategy_management/` | 存在，6 个 `.py` 文件 |
| 当前 strategy 相关注册 | `VERSION_MAPPING["strategy"]`、`strategy_mgmt.router`、`strategy_management.router`、`strategy_list_mock.router` |
| 直接 `strategy_management.router` include | 1 处 |
| `/api/v1/strategy` 代码/测试/前端/脚本文本引用 | 84 |
| `/api/strategy` 代码/测试/前端/脚本文本引用 | 120 |
| `/strategies` 代码/测试/前端/脚本文本引用 | 155 |
| 文档修正范围 | 主文档、H 文档、本文档 |
| 本批次代码改动 | 无 |

当前策略域事实摘要：

| 观察 | 结论 |
|------|------|
| 多个 strategy 入口仍存在且有大量消费者 | 不能直接收敛到单一 router |
| `strategy_management.router` 当前直接 include 1 次 | 旧“双 include”描述已降级为历史风险线索 |
| `strategy_management.py` 是小型 shim 候选 | 是否退役取决于 import 解析和兼容职责 |
| `/api/v1/strategy`、`/api/strategy`、`/strategies` 引用量高 | 必须先做前端/测试/脚本消费者矩阵和 OpenAPI diff |

Batch 8 自审结果：

- H 文档已补当前文件大小、package 文件数、router_registry 注册和消费者引用数量。
- H 文档已把路由注册简化改为 OpenSpec 候选，不再直接删除 `strategy.py`、`strategy_mgmt.py`、`strategy_management.py`、`strategy_management/` 或 `strategy_list_mock.py`。
- H 文档已要求 endpoint parity、OpenAPI diff、前端 API 调用、import smoke 和 rollback。
- 主文档子文档索引已同步为“已补当前注册/消费者/OpenSpec 边界，只能作为 OpenSpec 输入”。
- Markdown governance gate 仍因既有历史文档返回失败；本批次改动的三份文档没有出现在失败列表中。

## 十九、Batch 9 风控域治理文档复核记录

按第六节执行流，已完成 I 文档的当前风控域文件、router_registry 注册和消费者引用复核。本批次只更新 Markdown，不修改 router_registry、不移动 API 文件、不删除 shim、不合并 service。

| 项 | 结果 |
|----|------|
| 复核日期 | 2026-05-17 |
| `api/risk_management.py` | 存在，37 行，兼容 shim 候选 |
| `api/risk_management_core.py` | 存在，159 行，核心 API 候选 |
| `api/risk_management_v31.py` | 存在，22 行，v31 兼容候选 |
| `api/risk_management.py.bak` | 不存在 |
| `api/risk/` package | 6 个 `.py` 文件 |
| `api/risk_v31/` package | 3 个 `.py` 文件 |
| `services/risk_management_new.py` | 存在，297 行 |
| `services/risk_management_2.py` | 存在，643 行 |
| `services/risk_management/` package | 6 个 `.py` 文件 |
| 当前 risk 相关注册 | `from .api import risk` + `app.include_router(risk.router)` |
| `risk_management` 代码/测试/前端/脚本文本引用 | 108 |
| `app.api.risk` 代码/测试/前端/脚本文本引用 | 32 |
| `/api/v1/risk` 代码/测试/前端/脚本文本引用 | 45 |
| `/api/risk` 代码/测试/前端/脚本文本引用 | 54 |
| `/risk/` 代码/测试/前端/脚本文本引用 | 168 |
| 文档修正范围 | 主文档、I 文档、本文档 |
| 本批次代码改动 | 无 |

当前风控域事实摘要：

| 观察 | 结论 |
|------|------|
| `router_registry.py` 当前只注册 `risk.router` | I 的旧“多个 risk_management 直接注册”描述已修正 |
| `risk_management.py` 当前是小型兼容 shim 候选 | 不能按“主风控 API”直接删除或合并 |
| `risk_management_new.py` 和 `risk_management_2.py` 仍存在 | `_new`、`_2` 退役必须先做 service parity、consumer 和测试判定 |
| risk 相关前端/测试/API 路径引用量高 | 必须先做消费者矩阵和 OpenAPI diff |

Batch 9 自审结果：

- I 文档已补当前文件行数、package 文件数、router_registry 注册和消费者引用数量。
- I 文档已把 API/service 收敛改为 OpenSpec 候选，不再直接合并 `risk_management.py`、`risk_management_core.py`、`risk_management_v31.py`、`risk_v31/`、`risk_management_new.py` 或 `risk_management_2.py`。
- I 文档已要求 endpoint parity、OpenAPI diff、前端 API 调用、import smoke、v31 smoke 和 rollback。
- 主文档子文档索引已同步为“已补当前注册/消费者/OpenSpec 边界，只能作为 OpenSpec 输入”。
- Markdown governance gate 仍因既有历史文档返回失败；本批次改动的三份文档没有出现在失败列表中。
