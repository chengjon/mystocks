# Deletion Evidence Gate

本页只说明如何操作删除治理门禁；规范口径仍以 [architecture/STANDARDS.md](../../../architecture/STANDARDS.md) 与机器工件为准。

## 拦截范围

- 已跟踪目录删除
- 不在已删目录内的 `>=3` 篇文档删除批次

## 执行位置

- staged 门禁：`.githooks/pre-commit` 与 `.pre-commit-config.yaml`
- worktree 门禁：`.claude/hooks/stop-deletion-evidence-gate.sh`
- 共享引擎：`scripts/compliance/deletion_evidence_gate.py`

两条门禁都调用同一套判定逻辑，不允许出现“pre-commit 通过、Stop hook 放行”的分叉。

## 唯一治理工件

- 正常删除证据：`governance/deletion-evidence.yaml`
- 紧急豁免：`governance/waivers/deletion-evidence-waivers.yaml`

要求：

- 必须是预先存在的机器可读 YAML
- 必须写明被删目录或被删文档的精确路径
- 不允许 wildcard、模糊父目录、近似匹配
- 同一次删除提交里新增的证据或豁免不算数；门禁只读取 `HEAD`

## 正常删除证据

`governance/deletion-evidence.yaml` 中，每个删除目标都要单独落一条精确记录。

```yaml
version: 1
entries:
  - path: docs/legacy/reports
    kind: directory
    status: approved
    owner: cli-governance
    code_path_verdict: safe_to_delete
    function_tree_verdict: 重复冗余
```

必填关键字段：

- `path`: 被删目录或文档的精确相对路径
- `kind`: `directory` 或 `document`
- `status`: 必须为 `approved`
- `owner`: 责任人
- `code_path_verdict`: 必须为 `safe_to_delete`
- `function_tree_verdict`: 只能是 `重复冗余` 或 `正式下线`

如果删除的是目录，证据应写目录路径本身。
如果删除的是目录外的 `>=3` 篇文档，证据应逐篇写 `kind: document` 的精确文件路径。

## 紧急豁免

仅在正常证据来不及预落盘时，才使用 `governance/waivers/deletion-evidence-waivers.yaml`。

```yaml
version: 1
waivers:
  - path: docs/legacy/old-runbook.md
    kind: document
    owner: cli-governance
    reason: urgent rollback cleanup
    ticket_or_context: task-2026-04-08
    approved_by_user: true
    approved_on: 2026-04-08
    expires_on: 2026-04-09
```

要求：

- 仍然必须是精确路径
- 仍然必须预先存在于 `HEAD`
- 必须带 `owner`、`reason`、`ticket_or_context`、`approved_by_user`、`approved_on`、`expires_on`
- 过期即失效

## 本地自检

查看 staged 删除：

```bash
python scripts/compliance/deletion_evidence_gate.py --root-dir . --format text --scope staged
```

查看当前 worktree 删除：

```bash
python scripts/compliance/deletion_evidence_gate.py --root-dir . --format text --scope worktree
```

如果需要机器输出：

```bash
python scripts/compliance/deletion_evidence_gate.py --root-dir . --format json --scope staged
```

## 操作顺序

1. 先在治理工件里落盘精确删除对象。
2. 让该证据或豁免先进入 `HEAD`。
3. 再提交目录删除或 `>=3` 文档删除。

反过来做会被门禁直接拦下。
