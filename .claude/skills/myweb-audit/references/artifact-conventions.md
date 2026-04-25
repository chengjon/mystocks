# Artifact Conventions

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

Use these conventions when an audit run writes files instead of responding inline.

## Default Output Root

Unless the user explicitly requests another location, use:

`docs/reports/quality/myweb-audit/[audit-run-id]/`

Example:

`docs/reports/quality/myweb-audit/audit-20260425-01/`

## Recommended Layout

```text
docs/reports/quality/myweb-audit/[audit-run-id]/
├── manifests/
│   └── [batch-id]-manifest.yaml
├── pages/
│   ├── [module]-[route-key]-audit.md
│   └── ...
├── batches/
│   └── [module]-batch-[nn]-audit.md
├── findings/
│   ├── [batch-id]-raw-findings.yaml
│   └── [batch-id]-merged-findings.yaml
└── closeout/
    └── [audit-run-id]-closeout.md
```

## File Format Guidance

- manifest: YAML
- raw findings: YAML or JSON matching `findings-schema.json`
- merged findings: YAML or JSON matching the consolidated structure described in `findings-schema-example.md`
- page and batch reports: Markdown
- closeout checklist result: Markdown

## Write Order

When files are emitted, write them in this order:

1. manifest
2. raw findings
3. merged findings
4. page reports
5. batch report
6. closeout checklist result

## Resumability Notes

- This layout is intended to make partial runs easy to inspect manually.
- Cross-session recovery is still a future enhancement; do not imply full resumability unless the workflow explicitly supports it.
- If a run stays inline only, no files are required.
