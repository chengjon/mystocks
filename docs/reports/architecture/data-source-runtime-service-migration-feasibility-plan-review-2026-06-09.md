# 数据源运行时服务化迁移可行性方案 — 审核报告

日期：2026-06-09
审核文档：`docs/reports/architecture/data-source-runtime-service-migration-feasibility-plan-2026-06-09.md`
审核视角：Matt Pocock 架构词汇（Module / Interface / Seam / Adapter / Depth）+ 仓库 STANDARDS.md + OpenSpec 治理规则

## 总评

方案的核心判断是对的——"先定义 seam，再换 adapter，不要直接搬 Docker"。这比常见错误（拆服务=开容器）高出一个层次。文档在 MCP 边界、协议分工、弹性层设计上投入了大量篇幅，这部分质量很高。

但文档与前序 review (`data-source-service-extraction-analysis-review-2026-06-09.md`) 之间的关系是**补充**而非**覆盖**。review 中标出的 HIGH 级问题，在这份可行性方案中有 4/7 已得到纠正，但仍有 3 个结构性缺陷。

## 已修正的 review 发现（值得肯定）

| 原 review 发现 | 可行性方案处理 | 判定 |
|---|---|---|
| Registry ownership 推迟到 Phase 4 太晚 | Phase 0 就明确 PostgreSQL=YAML 的真相源分工（第 96-105 行） | **已修正** |
| Pilot 范围模糊（REALTIME_QUOTES vs AkShare REST） | 明确推荐 AkShare REST/pull 为首个试点（第 543-551 行） | **已修正** |
| Rate limiting 被描述为已有能力 | 明确标注为目标能力（第 372 行注释），非当前默认主链 | **已修正** |
| OpenSpec affected specs 模糊 | 新增 `data-source-runtime-service`，避免重载 `03-adapter-pattern`（第 449-456 行） | **已修正** |

## 仍存在的阻塞性问题（3 个）

### HIGH-1: `DataSourceClient` interface 只画了名字，没定义 contract invariant

**位置**: 第 56-77 行

**问题**: 方案画了 `DataSourceClient → Local / Remote` 的 adapter 结构，但没有定义 interface 本身的 invariants。Matt Pocock 的核心观点是：interface 的价值不在方法签名，在于调用方能依赖的不变量。

**缺失内容**:

- 调用 `fetch()` 失败时返回什么？typed error code？还是 exception？
- 返回的 data 是否总带 `source` / `endpoint` / `freshness` / `staleness` metadata？
- 超时行为：是 timeout budget 透传还是 caller 无感知？
- cache hit 是否对调用方透明？还是调用方可以指定 `freshness_requirement`？
- config write（create/update/delete/version/rollback）是否在 `DataSourceClient` interface 上？还是走独立的 `DataSourceConfigClient`？

**影响**: 如果 Phase 1 只抽名字不定义 invariant，`RemoteDataSourceClient` 的行为会自然 drift 向"HTTP 语义"而非"DataSourceManagerV2 语义"，Phase 2 的 parity test 会变成补丁式修正。

**建议**: 在 Phase 0 OpenSpec 中增加 `DataSourceClient` interface specification，至少包含：方法列表、每个方法的 error mode、返回 metadata schema、cache 语义、timeout 语义、config 操作归属。

### HIGH-2: 运行时状态所有权（runtime state ownership）仍与业务存储混淆

**位置**: 第 48-54 行模块分布表、第 86-91 行功能归属表

**问题**: 方案说"数据源运行时"拥有 health、cache、circuit breaker、rate limit、metrics、call history。同时又引用 PostgreSQL、Redis、TDengine 作为外部服务。但没有回答：

- circuit breaker state 放哪里？进程内？Redis？如果放进程内，数据源服务重启后所有 breaker 都 reset，这是否符合预期？
- call history 放 PostgreSQL 还是数据源服务内部？如果是 PostgreSQL，数据源服务需要 DB 写权限，这扩大了它的存储边界。
- endpoint health 的 true source 是数据源服务进程内状态，还是 PostgreSQL 里的 health 表？如果两者都有，又是一套平行真相源。
- metrics 的 consumer 是谁？Prometheus 直接 scrape 数据源服务？还是后端 `/metrics` 聚合后再暴露？

**影响**: 这不是"以后再定"的问题——Phase 2 创建 Docker 容器时，必须决定它连不连 PostgreSQL、需不需要独立的 Redis namespace。如果这里模糊，容器要么变成"无状态 pass-through"（与目标矛盾），要么变成"隐式有状态"（运维风险）。

**建议**: 在 Phase 0 增加 Runtime State Ownership Matrix：

```text
| 状态               | 存储位置     | Owner                 | 重启后行为     |
|--------------------|-------------|-----------------------|---------------|
| circuit breaker    | 进程内       | data-source runtime   | reset to closed |
| rate limit token   | 进程内       | data-source runtime   | reset to initial |
| cache L1           | 进程内       | data-source runtime   | cold start    |
| cache L2           | Redis       | shared                | preserved     |
| call history       | PostgreSQL  | main backend          | preserved     |
| endpoint health    | 进程内 + health API | data-source runtime | recalculated |
| metrics            | Prometheus pull | data-source runtime | reset         |
| registry           | PostgreSQL  | data-source runtime (write), main backend (facade) | preserved |
```

### HIGH-3: 与 `optimize-data-source-v2` 的依赖关系未定义

**位置**: 第 465 行提及但未展开

**问题**: `openspec/changes/optimize-data-source-v2/tasks.md` 显示该 change 仍在执行中，且 repo-truth 注记明确指出多个 V2 组件（SmartRouter、BatchProcessor、CircuitBreaker 主链包装、metrics 全局 REGISTRY 合并）**尚未完成**。

方案引用 `DataSourceManagerV2` 作为 `LocalDataSourceClient` 的底层，但如果 V2 的 SmartRouter 没有接入、熔断没有包装到主链、BatchProcessor 没有切到主路径，那 `LocalDataSourceClient` 实际包装的是一个**半完成**的 V2 runtime。

这意味着：

- Phase 1 的"行为不变"承诺可能建立在未稳定的行为上
- 如果 V2 change 继续推进并改变了 `DataSourceManagerV2` 的内部行为，Phase 1 的 seam 可能需要返工
- 如果 V2 change 被放弃，Phase 1 的 seam 包装的就是一个不会再被优化的 runtime

**建议**: 在 Phase 0 明确以下三种关系之一：

1. **依赖完成**: `extract-data-source-runtime-service` 等待 V2 指定的 N 个关键 task 完成后再启动
2. **接续**: V2 剩余 task 合并到新 change 的 Phase 1/Phase 2 中执行
3. **替代**: V2 未完成部分作废，新 change 重新设计对应能力

## 中等级别问题（2 个）

### MED-1: ELTDX MCP 借鉴部分篇幅过大，主链路设计密度不足

**位置**: 第 156-263 行（约 100 行）

**观察**: 方案花了约 15% 的篇幅讨论 MCP 三种接入形态（stdio / standalone / mounted）和 SSE 兼容性部署约束。MCP 本身已被明确限定为"可选诊断工具入口"，不是核心 seam。但 MCP 的边界描述比 `DataSourceClient` interface 本身还要详细。

**建议**: 压缩 MCP 部分为 Phase 5 的 implementation guidance，Phase 0 只需记录"MCP 仅限诊断/工具入口，不进热路径"这一原则性决策。

### MED-2: 验收矩阵缺少可执行的验证命令

**位置**: 第 657-666 行

**观察**: 每个阶段的验收描述是"方向正确"的（例如 "remote contract parity"），但没有映射到具体的验证命令或测试套件。项目有 `pytest`、`stylelint`、`vue-tsc` 等已有验证路径（STANDARDS.md 第 4.2 节），验收矩阵应衔接这些。

**建议**: 至少为 Phase 1 和 Phase 2 列出：

- 现有哪些 test suites 必须继续 pass
- 需要新增哪些 contract test files
- Docker smoke 的具体命令（参考项目已有的 `scripts/run_e2e_pm2.sh`）

## 低级别问题（1 个）

### LOW-1: 缺少 STANDARDS.md 治理节奏对齐声明

方案涉及拆分服务、迁移 registry 真相源、退役旧配置路径。这些都属于 STANDARDS.md 三、迁移收口规则的管辖范围。方案应在 Phase 0 显式声明将遵守哪些 STANDARDS.md 约束（单一真相源、迁移必须带收口条件、退出条件等）。

## 最终判定

| 维度 | 评分 |
|---|---|
| 方向正确性 | **强** — "先 seam 后容器"的思路正确 |
| 技术深度 | **中** — 弹性层和协议分工深入，但 interface invariant 和 state ownership 欠缺 |
| 仓库约束一致性 | **中** — 已遵守 OpenSpec 流程，但 STANDARDS.md 迁移规则和 V2 依赖未显式声明 |
| 可执行性 | **弱** — Phase 0 的决策清单尚未闭合，缺 interface spec 和 state matrix |

**建议**: 批准方向，**暂不批准进入 OpenSpec proposal**。在创建 OpenSpec change 前，补齐：

1. `DataSourceClient` interface specification（invariants、error modes、metadata schema）
2. Runtime State Ownership Matrix
3. 与 `optimize-data-source-v2` 的依赖/接续/替代关系声明

这三项补齐后，方案即可进入 Phase 0 OpenSpec 创建。
