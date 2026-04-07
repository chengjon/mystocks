# Technical Debt Exception Template

> **设计方案说明**:
> 本文件是架构设计、界面设计、系统模型、规格定义或映射方案，不是当前仓库共享规则、当前实现边界或当前主线契约的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内结构分层、字段约定、模块职责、视觉规范和实施建议应结合当前代码与主线文档复核；若冲突，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


> 用途：当新增技术债标记（如 `@ts-ignore` / `as any` / `TODO`）因业务紧急需求无法当期清理时，必须使用本模板申请临时例外。
>
> 适用范围：PR/MR 流程中的 **临时例外**，非长期豁免。

## 1) Mandatory Metadata

- `owner`: 责任人（GitHub ID / 姓名）
- `issue`: 跟踪单号（Jira/GitHub Issue）
- `ttl`: 到期时间（ISO 日期，如 `2026-03-15`）
- `reason`: 为什么当前必须保留该技术债
- `remediation`: 到期前的清偿计划

## 2) In-code Annotation Format

在代码中新增抑制项时，必须附带如下标记（单行或紧邻注释）：

```text
[debt-exception] owner=<owner> issue=<issue> ttl=<yyyy-mm-dd> reason=<reason> remediation=<plan>
```

示例：

```ts
// [debt-exception] owner=alice issue=Q-1024 ttl=2026-03-15 reason=hotfix remediation=replace with typed adapter
// @ts-expect-error temporary mismatch during hotfix window
```

## 3) Dual-Approval Requirement (Two Signatures)

PR 描述中必须包含以下两行（缺一不可）：

```text
debt-exception-tech-lead-approved: yes
debt-exception-module-owner-approved: yes
```

## 4) PR Checklist

- [ ] 已填写 owner / issue / ttl / reason / remediation
- [ ] 已在代码旁添加 `[debt-exception] ...` 标记
- [ ] PR 描述含双签字段（Tech Lead + Module Owner）
- [ ] 例外项已在到期前排入修复计划

## 5) Expiration Policy

- 到达 TTL 后，例外项必须清理或续期。
- 续期必须重新走双签审批并更新 `reason` 与 `remediation`。
- 无有效 TTL 或无双签审批的例外项，CI 门禁应直接失败。
