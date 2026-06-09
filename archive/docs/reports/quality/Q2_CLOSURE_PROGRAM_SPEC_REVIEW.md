# Q2 Optimization Closure Program — Spec Delta 审核报告

> 审核日期：2026-04-25
> 审核范围：`openspec/changes/plan-q2-optimization-closure-program/` 全部文件
> 审核方式：逐文件审读 + 与 Q2 评估报告 + 现有 base spec 交叉比对
> 审核结论：**PASS WITH SUGGESTIONS** — 整体设计扎实，6 处建议均为非阻塞项

---

## 1. 总体评价

这个 OpenSpec 变更提案是我近期审核的同类工作中质量最高的一批。proposal → design → tasks → specs 的层级清晰，四个关键决策（closure program 定位、single-CLI 优先、multi-CLI 延迟但不否决、data quality 和 trading safety 提升为一等 spec）都经过了深思熟虑。

spec delta 本身的写作质量也很高——场景结构完整（WHEN/THEN/AND），没有模糊的 SHALL 声明，且每个 delta 都能追溯到 Q2 评估报告中的具体发现。

以下按优先级列出建议。

---

## 2. 需关注项（非阻塞，但值得在 apply 前考虑）

### S1. 实时链路 canonicalization 跨 spec 的依赖关系未显式声明

**涉及文件**: `architecture-governance/spec.md` delta + `api-integration/spec.md` delta

architecture-governance 新增了 "Realtime Delivery Truth Registry"（后端真相注册表），api-integration 新增了 "Canonical Realtime Transport Selection"（前端传输选择策略）。两者逻辑互补——registry 记录哪个是 canonical，selection policy 决定前端用哪个——但 delta 中没有互相引用。

**建议**: 在两个 delta 的 requirement 描述中各加一句 cross-reference，例如：
- architecture-governance 的 truth registry 场景增加：`AND the registry SHALL be consistent with the canonical transport selection policy defined in api-integration`
- api-integration 的 selection policy 场景增加：`AND the selection SHALL align with the realtime delivery truth registry`

**风险等级**: 低。不声明也能工作，但声明后可以避免两个 spec 产生不一致的 canonical 判定。

---

### S2. trading-execution-safety 缺少审计保留周期与存储保障

**涉及文件**: `trading-execution-safety/spec.md`

"Trading Audit Minimum Fields" 要求审计记录包含 request identity、actor identity、execution path、decision outcome、timestamp 五个字段，但没有涉及：
- 审计记录的**保留周期**（Q2 评估报告原文明确提到"必记字段和保留周期"）
- 审计记录的**存储保障**（是否要求持久化到数据库而非仅内存/日志）

**建议**: 在 "Trading Audit Minimum Fields" requirement 下补充一个场景：

```
#### Scenario: Audit record retention
- **WHEN** a trading audit record is created
- **THEN** the record SHALL be persisted to durable storage
- **AND** the minimum retention period SHALL be defined by the trading safety contract
```

或者将保留周期作为 "Trading Domain Safety Contract" requirement 的一部分，让不同 classification（simulated/experimental/production-eligible）对应不同保留要求。

**风险等级**: 中。没有保留周期约束，审计数据可能在日志轮转后丢失，使审计约束形同虚设。

---

### S3. trading-execution-safety 缺少资金敞口限制与风控前置约束

**涉及文件**: `trading-execution-safety/spec.md`

Q2 评估报告的 P0 第 2 项和 P1 第 5 项都提到了"风控前置约束"和"交易专属红线"。当前 spec 覆盖了幂等、确认、审计三个维度，但没有覆盖：
- 单笔/单日**资金敞口限制**
- 下单前的**风控检查点**（如持仓集中度、止损距离检查）

**建议**: 考虑增加一个 requirement：

```
### Requirement: Trading Pre-Execution Risk Gate
Safety-sensitive trading paths SHALL define pre-execution risk gates
that block submissions exceeding configured capital or exposure thresholds.

#### Scenario: Capital threshold is exceeded
- **WHEN** a trading submission would exceed the configured capital or exposure threshold
- **THEN** the execution path SHALL block the submission
- **AND** it SHALL record the blocking decision as an audit event
```

**风险等级**: 中。当前交易执行层尚未开发完成，这个 requirement 可以在 domain trading 接口设计阶段一并考虑。但如果不在 spec 层面先声明，实现时容易遗漏。

---

### S4. data-quality-governance 与双库架构的关系未声明

**涉及文件**: `data-quality-governance/spec.md`

Q2 评估报告明确将 TDengine + PostgreSQL 双库列为 P2 待复核项，且 zread 文档已详细描述了双库路由机制。新 spec 定义了"Canonical Data Quality Model"和"Data Quality Component Classification"，但没有提及：
- 质量检查是否需要区分 TDengine 和 PostgreSQL 各自的数据质量特征
- 时间对齐（temporal alignment）在双库场景下的跨库一致性要求

**建议**: 在 "Canonical Data Quality Model" 的场景中增加：

```
- **AND** it SHALL identify storage-specific quality concerns
      when data spans multiple storage engines
```

**风险等级**: 低。双库策略本身是 P2 待复核项，当前不声明不会阻塞 Phase C 的启动。

---

### S5. function-tree-governance 的 "safety-sensitive" 定义边界

**涉及文件**: `function-tree-governance/spec.md`

"Criteria-Backed Completion Semantics" 的第二个场景提到 "trading, risk, or similarly safety-sensitive capability"，但 "similarly safety-sensitive" 是开放性表述。

**建议**: 考虑在 design.md 或 spec 中给出一个判定规则（而非穷举列表），例如：
- 涉及资金操作、持仓变更、风控决策的能力域为 safety-sensitive
- 或者：凡是在 trading-execution-safety spec 中声明为 production-eligible 的路径所关联的功能树节点

**风险等级**: 低。当前项目中 trading 和 risk 是唯一明确的安全敏感域，边界争议不大。

---

### S6. code-quality 的 "Closure Wave Evidence Contract" 位置可商榷

**涉及文件**: `code-quality/spec.md`

新增的 "Closure Wave Evidence Contract" 是一个跨领域治理要求，与 code-quality spec 中已有的技术债、构建门禁、测试有效性等纯质量关注点不在同一抽象层。它更像 `architecture-governance` 的职责。

**建议**: 如果后续有架构治理 spec 的大版本更新，可考虑将此 requirement 迁移到 `architecture-governance`。当前放在 code-quality 不会造成功能问题，只是概念归属上的轻微不匹配。

**风险等级**: 极低。不影响执行。

---

## 3. 做得好的地方（确认要点）

以下是我认为这个提案中特别值得保留的设计决策，不建议修改：

### 3.1 Proposal 的四个 Decision 都很扎实

- "Treat Q2 As A Closure Program, Not A Feature Grab" — 精准对齐了评估报告的结论：问题不在缺少能力，而在收敛不够
- "Single-CLI First" — 对跨领域 truth-setting 工作来说这是正确的风险控制
- "Multi-CLI Is Deferred, Not Rejected Forever" — 避免了"永远单线程"的过度约束
- "Data Quality And Trading Safety Need First-Class Specs" — 新建两个独立 spec 是正确的分域决策

### 3.2 Design 的 Phase Model 与 Proposal 严格对齐

Phase A→E 的顺序与 tasks.md 的 7 个 section 完全映射，没有出现"design 里提了但 tasks 里没有"或反过来。

### 3.3 Trading Safety 的三分类设计

simulated / experimental / production-eligible 三级分类非常实用。它避免了"要么生产要么不算"的二元判断，给了未完成实现一个合理的归属。

### 3.4 Closure Evidence 的双视角设计

code-quality delta 的 "Closure Wave Evidence Contract" 同时定义了"提交完成声明时需要什么证据"和"审查者检查时看什么证据"两个场景，有效防止了自说自话。

### 3.5 Delta 格式的场景结构

所有 delta 都严格遵循 WHEN/THEN/AND 的场景结构，且没有出现"SHALL be appropriate"或"SHALL be reasonable"这类不可测试的表述。

---

## 4. 与 Q2 评估报告的覆盖度矩阵

| 评估报告条目 | 对应 spec delta | 覆盖状态 |
|---|---|---|
| P0-1: 统一实时主链路 | architecture-governance (truth registry) + api-integration (transport selection) | 已覆盖 |
| P0-2: 交易安全契约先行 | trading-execution-safety (全部 4 requirement) | 已覆盖，缺资金敞口限制（S3） |
| P1-3: 收敛应用层边界 | architecture-governance (backend composition SoT) | 已覆盖 |
| P1-4: 统一数据质量模块 | data-quality-governance (全部 3 requirement) | 已覆盖 |
| P1-5: 交易适配器实现 | 未映射（正确：这是实现决策，不是治理 spec） | 正确未纳入 |
| P1-6: 量化功能树完成度 | function-tree-governance (criteria-backed completion) | 已覆盖 |
| P2-7: 双库策略复核 | 未映射（正确：P2 待压测后再决定） | 正确未纳入 |
| P2-8: 观测性绑定 | 未映射（可能需要在后续补充） | 建议关注 |
| 7a: 交易适配器方向 | 未映射（正确：实现决策） | 正确未纳入 |

**P2-8（观测性与业务链路绑定）** 未出现在任何 delta 中。这不是阻塞项（评估报告自己也将它列为 P2），但如果后续有观测性相关的 spec 更新，应补齐。

---

## 5. 最终判定

**PASS WITH SUGGESTIONS**

6 个 spec delta 可以进入 apply 阶段。S1–S6 均为非阻塞建议，其中 S2（审计保留周期）和 S3（风控前置约束）建议在 apply 前或 Phase D 启动前补入，其余可按需处理。
