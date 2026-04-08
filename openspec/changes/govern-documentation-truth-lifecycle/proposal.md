# Change: Govern documentation truth and lifecycle

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。


## Why

The repository now contains a large documentation surface with mixed roles:

- canonical guidance and rules
- active implementation guides
- historical reports, plans, and verification notes
- legacy snapshots that still look like current truth

Editing header metadata one file at a time can reduce immediate misreads, but it does not solve the
root problem. The root problem is that the repository does not yet define a top-down documentation
system that answers:

- which documents are canonical truth by concern
- which documents are only supporting branches
- which documents are historical evidence
- which documents should be archived
- which documents should be deleted instead of continuously rewritten

This change establishes that system first, then drives cleanup from canonical trunk documents
outward. The default remediation for invalid or stale historical material should become
`archive/delete based on canonical trunks`, not endless manual wording edits.

## Core Principles

- **Trunk-first, not leaf-first**: build and govern canonical mainline documents before touching
  minor stale leaves.
- **Delete invalid/stale docs aggressively**: the default way to prevent misread is removal after
  replacement and link cleanup, not endless patching.
- **Keep only current, architecturally truthful docs**: one concern, one active truth source; no
  parallel documentation universes.
- **AI-friendly structure**: hierarchy, scope boundaries, lifecycle class, and obsolescence status
  must be obvious enough that AI can follow the same rules as humans.

## What Changes

- Add a dedicated `documentation-governance` OpenSpec capability for documentation truth-source and
  lifecycle governance.
- Define canonical documentation trunks for governance rules, capability specs, API contract truth,
  operations runbooks, testing guidance, and historical evidence.
- Define lifecycle classes and decision states for retained documents: canonical, supporting,
  report, plan, generated/reference, archive candidate, delete candidate.
- Require trunk-first retention and deletion decisions so stale documents are removed based on
  canonical replacements instead of preserved indefinitely.
- Define a cluster-based cleanup workflow so documentation is governed by document family / subtree,
  not by ad hoc file-by-file edits.
- Plan machine-readable inventory and audit tooling so future AI work can identify valid trunks and
  invalid historical branches automatically.
- Make trunk-first deletion the normal cleanup path for invalid/stale documentation once canonical
  replacements are established.

## Scope

### In Scope

- Documentation truth-source architecture for repository-facing docs
- Documentation lifecycle rules: keep, merge, archive, delete
- Canonical trunk map for `docs/`, `openspec/`, API contract truth, runbooks, and test guidance
- Inventory / decision-register workflow for large document families
- Cluster-based cleanup waves, starting from the highest-risk documentation areas
- Governance automation requirements for new-document admission and stale-document audits

### Out of Scope

- Immediate full-repository document migration in this proposal
- Rewriting every historical report to add disclaimers
- Runtime code or API behavior changes
- Deleting documents before canonical replacements and link updates are defined

## Impact

- Affected specs: `documentation-governance` (new)
- Related specs to align during implementation: `directory-governance`, `file-organization`
- Expected implementation outputs:
  - canonical documentation system map
  - documentation inventory and decision register
  - governance manifest / audit tooling
  - phased cleanup batches for high-risk documentation clusters

## Risks and Mitigations

- **Risk: deleting documents without clear replacement will remove still-useful context**
  - **Mitigation**: require trunk mapping, inbound-link review, and documented keep/archive/delete
    decisions before deletion.
- **Risk: governance scope becomes too broad and stalls execution**
  - **Mitigation**: execute by subtree clusters with bounded waves and explicit exit criteria.
- **Risk: new documentation continues to sprawl while legacy cleanup is in progress**
  - **Mitigation**: add admission rules and audit tooling early, before large cleanup waves.
- **Risk: AI continues to misread non-canonical docs during the transition**
  - **Mitigation**: publish the canonical trunk map first and route future cleanup decisions through
    it.
