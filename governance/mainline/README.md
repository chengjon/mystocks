# Mainline Governance

本目录是 AI 主线治理的唯一入口（专用目录）。

## 目录结构

```text
governance/mainline/
├── README.md
├── spec/
│   └── ai-development-mainline-governance-spec.md
├── templates/
│   └── ai-task-card.yaml
├── schemas/
│   └── ai-task-card.schema.json
├── scripts/
│   └── mainline_scope_gate.py
├── task-cards/
│   └── pr-<pr-number>.yaml
└── reports/
    └── mainline-governance-report.json
```

> 说明：GitHub Actions workflow 必须放在 `.github/workflows/`，因此 `mainline-governance.yml` 不在本目录内，但只引用本目录资源。

## 快速开始

### 1) 创建任务卡

复制模板并按 PR 号命名：

```bash
cp governance/mainline/templates/ai-task-card.yaml governance/mainline/task-cards/pr-1234.yaml
```

必须重点填写：

- `mainline.id`
- `classification.task_type`
- `classification.secondary_type`
- `scope.allowed_paths`
- `openspec.change_id`（Feature 必填）
- `openspec.approval_status`（Feature 必须为 `approved`）
- `delivery.six_line_summary`

### 2) 本地运行门禁（建议提交前）

```bash
python governance/mainline/scripts/mainline_scope_gate.py \
  --task-card governance/mainline/task-cards/pr-1234.yaml \
  --schema governance/mainline/schemas/ai-task-card.schema.json \
  --base-sha HEAD~1 \
  --head-sha HEAD \
  --report governance/mainline/reports/mainline-governance-report.json
```

### 3) PR 自动门禁（Phase A）

PR 创建/更新后，工作流自动执行：

- `.github/workflows/mainline-governance.yml`

门禁逻辑：

- 任务卡存在性与 schema 校验
- Feature 与 OpenSpec 审批绑定
- 白名单路径越界检测
- 主线偏移率阈值检测
- 主/副类型预算检测
- 六行摘要完整性校验

## 阶段阈值

- Phase A：`drift <= 5%`
- Phase B：`drift <= 2%`
- Phase C：`drift = 0%`

由任务卡中的 `governance.phase` 和 `mainline_drift_threshold_percent` 控制，schema 与 gate 双重校验。

## 规范文档

详细规则请看：

- `governance/mainline/spec/ai-development-mainline-governance-spec.md`
- `governance/mainline/reports/mainline-governance-v0.2-task-summary.md`

## 常见失败原因

- 缺少 `governance/mainline/task-cards/pr-<pr-number>.yaml`
- `feature` 任务未绑定已审批 OpenSpec
- 改动命中白名单外路径导致 drift 超阈值
- `secondary_type` 设置为非 `none` 但预算/审批字段不完整
- `delivery.six_line_summary` 任一字段为空
