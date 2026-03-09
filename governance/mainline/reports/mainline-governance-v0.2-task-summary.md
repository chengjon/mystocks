# Mainline Governance v0.2 任务总结与使用手册

> 日期：2026-03-01
> 目标：将“目标明确、方向不变、防跑偏”从口头约定升级为机器可执行治理链路，并形成可持续复用的项目资产。

---

## 1. 本次更新总览（做了什么）

本次工作完成了从“规范文档”到“模板 + Schema + Gate 脚本 + CI + PR 入口模板”的闭环落地：

1. 治理规范升级到 v0.2（明确指标、阶段、状态机、配额）。
2. 任务卡模板与 Schema 对齐，支持结构化强约束。
3. 主线门禁脚本增强（空 diff 失败、治理元文件分母排除、副类型审批结构化）。
4. GitHub PR 工作流硬门禁化（所有 PR 触发）。
5. 新增最小 PR 模板，强制展示治理关键字段。

---

## 2. 关键成果与文件清单（可追踪）

### 2.1 规范层

- [governance/mainline/spec/ai-development-mainline-governance-spec.md](../spec/ai-development-mainline-governance-spec.md)
  - 版本 v0.2
  - 定义了：
    - Single Mainline 治理原则
    - 主线偏移率口径与阶段阈值
    - Stop Rules 状态机与恢复条件
    - 技术债配额策略

### 2.2 结构化输入层（任务卡）

- [governance/mainline/templates/ai-task-card.yaml](../templates/ai-task-card.yaml)
  - 任务卡模板（PR 级）。
- [governance/mainline/schemas/ai-task-card.schema.json](../schemas/ai-task-card.schema.json)
  - 机器校验 Schema。

### 2.3 执行门禁层（脚本）

- [governance/mainline/scripts/mainline_scope_gate.py](../scripts/mainline_scope_gate.py)
  - 核心能力：
    - Schema 校验
    - Feature 与 OpenSpec 审批绑定
    - scope/drift 校验
    - secondary budget 校验
    - phase 阈值校验

### 2.4 CI 门禁层

- [.github/workflows/mainline-governance.yml](../../../.github/workflows/mainline-governance.yml)
  - PR 事件触发主线门禁。
  - 自动解析任务卡路径。
  - 运行 gate 脚本并上传报告。
  - 写入 workflow summary。

### 2.5 PR 入口层（强制填写关键治理字段）

- [.github/pull_request_template.md](../../../.github/pull_request_template.md)
  - 强制展示：
    - `mainline_id`
    - `task_type`
    - `openspec_change_id`
    - `approval_status`
  - 并要求填写 `task_card_path`。

---

## 3. 治理链路使用方法（操作手册）

### 3.1 每个 PR 必做步骤

1. 在 `governance/mainline/task-cards/` 下创建任务卡：`pr-<PR号>.yaml`。
2. 按模板填写完整字段（尤其 mainline / classification / openspec / scope / delivery / governance）。
3. 发起 PR，按 PR 模板填写治理字段。
4. 等待 `Mainline Governance Gate` 执行。
5. 查看报告并处理 violation，直至通过。

### 3.2 本地手动验证（建议）

```bash
python governance/mainline/scripts/mainline_scope_gate.py \
  --task-card governance/mainline/task-cards/pr-<PR号>.yaml \
  --schema governance/mainline/schemas/ai-task-card.schema.json \
  --base-sha <base_sha> \
  --head-sha <head_sha> \
  --report governance/mainline/reports/mainline-governance-report.json \
  --fail-on-empty-diff
```

---

## 4. 常见失败原因与处置

1. 缺任务卡 / 路径错误：补齐 `governance/mainline/task-cards/pr-<PR号>.yaml`。
2. Schema 不通过：对照模板与 schema 修正字段类型和必填项。
3. Feature 未绑定 approved OpenSpec：补齐 `openspec.change_id` 并设置 `approval_status=approved`。
4. 主线偏移率超阈值：收缩改动到 `scope.allowed_paths` 或调整任务切片。
5. 副类型超预算 / 审批缺失：压缩 secondary 变更并补齐结构化审批字段。
6. 空 diff 失败：确认 base/head 选择正确。

---

## 5. 关键词 / 功能 / 方法索引（防沉没导航）

| 关键词 | 对应成果 | 快速入口 |
|---|---|---|
| 主线治理规范 | v0.2 执行规范 | `governance/mainline/spec/ai-development-mainline-governance-spec.md` |
| 任务卡模板 | 任务输入标准 | `governance/mainline/templates/ai-task-card.yaml` |
| 任务卡 Schema | 结构化校验规则 | `governance/mainline/schemas/ai-task-card.schema.json` |
| 主线门禁脚本 | 规则执行器 | `governance/mainline/scripts/mainline_scope_gate.py` |
| PR 硬门禁 | 合并前自动阻断 | `.github/workflows/mainline-governance.yml` |
| PR 必填治理字段 | 人机入口统一 | `.github/pull_request_template.md` |
| 门禁报告 | 可审计产物 | `governance/mainline/reports/mainline-governance-report.json` |

---

## 6. 如何让成果持续发挥作用（执行建议）

1. 把任务卡作为 PR 前置物（不是补文档）。
2. 把报告作为复盘输入（周度查看 drift 与 violations 趋势）。
3. 新成员 onboarding 先读 README + 规范 + 模板 + workflow。
4. 任何治理规则调整必须同步更新：规范文档、模板、schema、gate、workflow（五件套同改）。

---

## 7. 本次交付价值（面向未来）

本次不是新增一份文档，而是把治理抽象落成了可执行系统：

- 输入可校验（task card + schema）
- 过程可约束（gate）
- 合并可阻断（CI）
- 结果可审计（report + summary）
- 入口可统一（PR template）

这确保后续功能开发不会“做完即沉没”，而是持续积累为团队可复用、可追踪、可进化的工程能力。
