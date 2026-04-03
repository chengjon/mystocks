# 技术债治理章程 v1（Technical Debt Governance Charter v1）

> 版本：v1.0  
> 生效日期：2026-03-01  
> 适用范围：MyStocks 全仓（`src/`、`web/backend/`、`web/frontend/`、`tests/`、`.github/workflows/`）

## 1. 目标与原则

### 1.1 目标
1. 控制新增技术债务，避免存量继续恶化。
2. 优先清理影响交易正确性、发布稳定性、可维护性的高风险债务。
3. 建立“可量化、可审计、可自动执行”的长期治理机制。

### 1.2 治理原则
- **Clean as You Code**：先冻结基线，新增债务零增长。
- **风险优先**：优先交易主链路与生产发布路径。
- **机制优先于口头约定**：以 CI 门禁和模板字段执行规则。
- **例外可追踪**：所有豁免必须有 owner、issue、TTL。

---

## 2. 阶段策略（A→B→C）

### Stage A：质量信号对齐与止血（1-2 周）
目标：统一质量信号，防止“build 绿但质量假绿”。

- 冻结基线：Type 错误数、suppression 数、skip/xfail 数。
- 对“新增”债务启用门禁（不要求一次性清零存量）。
- 建立 PR 统一字段与例外审批流程。

### Stage B：高风险存量清偿（2-4 周）
目标：消化核心路径存量债务。

- 清理交易主链路中的 placeholder/mock 实现。
- 消化核心路径的 suppressions（`@ts-ignore`、`as any` 等）。
- 把占位测试（如 `assert True`）替换为真实断言。

### Stage C：机制硬化与自动化（持续）
目标：将治理从“人工执行”升级为“自动强制”。

- 启用 TTL 到期自动失败。
- 启用“基线不增”硬门禁。
- 纳入周度治理看板和迭代配额（debt budget）。

---

## 3. 强制门禁规则（v1）

## 3.1 PR 必需检查（Required Checks）
以下检查任一失败，PR 不得合并：

1. 前端：`lint`、`type-check`、`unit test`、`build`。
2. 后端：`ruff` / `mypy` / `pytest`（按仓库既有 workflow）。
3. 结构性语法错误必须为 `0`。
4. 涉及前端路由、交互、页面壳或服务启动的任务，必须附 E2E 执行结果。
5. 涉及后端 API 契约的任务，必须通过 OpenAPI 生成校验与文档回归门禁。

## 3.2 新增债务阻断规则

1. 禁止新增无审批的：
   - `@ts-ignore`
   - `@ts-expect-error`
   - `as any`
   - `# type: ignore`（Python）
2. 禁止新增裸 `TODO/FIXME/HACK`（必须含 owner+issue+ttl）。
3. 禁止新增“永久 skip/xfail”测试（必须含 owner+issue+ttl）。

## 3.3 基线不增规则

1. Type 错误总量不得高于当前基线。
2. skip/xfail 总量不得高于当前基线。
3. suppression 总量不得高于当前基线。
4. OpenAPI 文档问题总量不得高于当前基线。
5. OpenAPI 已文档化端点数、示例覆盖端点数、错误响应文档端点数不得低于当前基线。

> 注：基线值由每次阶段性治理窗口冻结并公告；未公告前沿用上次基线。

## 3.4 E2E 报告口径（自 2026-03-08 起生效）

1. E2E 结果必须报告“实际执行套件”的真实通过情况，禁止继续使用固定 `18/18` 等历史文案充当当前基线。
2. 报告至少包含：
   - 执行命令
   - 浏览器项目（如 `chromium`）
   - 用例总数、通过数、失败数、跳过数
3. 若只执行 smoke/stable 子集，必须明确标注为子集验证，不得表述为“全量 E2E 已通过”。
4. 若执行全量 Playwright 套件，应用例枚举/实际执行结果作为当次报告基线；文档中的固定数字仅可作为历史快照，不得作为门禁常量。

---

## 4. 例外（豁免）流程

## 4.1 可申请场景
仅允许以下场景申请例外：
1. 生产故障紧急修复（P0/P1）。
2. 外部依赖阻塞（上游 bug、类型声明缺失）。
3. 大规模迁移中的阶段性兼容。

## 4.2 审批要求
例外必须满足：
- 双签：Tech Lead + 模块负责人。
- 必填字段：`reason`、`owner`、`issue`、`ttl`、`remediation_plan`。
- 到期自动失效：超过 TTL 不可继续放行。

## 4.3 例外注释规范（示例）

### TypeScript
```ts
// @ts-expect-error [debt-exception] owner=alice issue=MS-123 ttl=2026-03-15 reason="upstream type mismatch"
```

### Python
```python
# type: ignore  # [debt-exception] owner=bob issue=MS-456 ttl=2026-03-20 reason="legacy plugin typing"
```

### TODO
```ts
// TODO[debt-exception](owner=alice,issue=MS-789,ttl=2026-03-22): replace mock quote API with real adapter
```

---

## 5. 基线管理规范

## 5.1 基线类型
- Type 错误基线
- suppression 基线
- skip/xfail 基线
- OpenAPI 文档质量基线（`backend_api_documentation`）
- 大文件热点基线（按仓库既有例外清单）

## 5.2 冻结与更新
1. 冻结频率：每个治理阶段开始时冻结一次。
2. 更新规则：仅允许“下降或持平”；若需上调必须走例外审批并记录原因。
3. 记录位置：
   - CI Artifact/周报
   - 相关治理文档（`docs/`）
   - 技术债基线文件（`reports/analysis/tech-debt-baseline.json`）

---

## 6. 周度治理报告模板（v1）

每周固定输出以下内容：

## 6.1 概览
- 本周新增债务数
- 本周消化债务数
- 当前存量债务数
- 过期未清理例外数

## 6.2 关键指标（KPI）
1. 新增 Type 错误数（目标：`<= 0`）
2. 新增 suppression 数（目标：`<= 0`）
3. 新增 skip/xfail 数（目标：`<= 0`）
4. 例外合规率（目标：`100%`）
5. 到期清理率（目标：`>= 90%`）

## 6.3 热点与行动
- Top 10 热点文件（含路径）
- 下周治理任务（owner + deadline）
- 阻塞项与所需决策

---

## 7. 角色与职责

- **Tech Lead**：批准门禁策略与例外，主持阶段复盘。
- **模块负责人**：落实模块治理任务、跟踪到期项。
- **CI/工程效能负责人**：维护门禁脚本、看板与告警。
- **开发者**：提交符合规则的代码与例外说明。

---

## 8. 与现有规范的关系

- 本章程是 `architecture/STANDARDS.md` 在“技术债治理”维度的执行细化，不替代工程红线。
- 如与上位规范冲突，以 `architecture/STANDARDS.md` 为准。
- `CLAUDE.md`、`AGENTS.md` 可引用本章程作为执行指南。
