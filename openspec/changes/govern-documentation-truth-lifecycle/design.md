# Design: govern-documentation-truth-lifecycle

> **设计方案说明**:
> 本文件用于记录某项变更的设计思路、结构拆分、实现取舍或技术路径，属于方案设计层材料。
> 它不是共享规则正文，也不直接代表当前仓库已落地状态；落地判断应结合 `architecture/STANDARDS.md`、对应 proposal/tasks、审批结果与实际代码验证。


## Overview

This design adds a documentation governance layer above existing directory hygiene.

`integrate-repository-hygiene` already establishes lifecycle directories such as `docs/`,
`reports/`, and `archive/`. That solves the question of where files should live by lifecycle.

This change solves a different and higher-order question:

1. Which documentation trunks are authoritative for a given concern?
2. Which documents are only supporting branches or historical evidence?
3. When should stale documents be archived versus deleted?
4. How should AI and humans make those decisions consistently at scale?

The intended outcome is a repository where documentation is navigated from a small set of canonical
trunks, and legacy material is governed by subtree / family decisions rather than endless
file-by-file edits.

## Goals

- Define a canonical documentation trunk system by concern.
- Make documentation truth-source precedence explicit and enforceable.
- Prefer delete/archive decisions for invalid historical material over perpetual manual relabeling.
- Make cleanup executable in bounded clusters such as `docs/api/`, `docs/reports/`, and
  `docs/guides/`.
- Add machine-readable audit support so future AI work can distinguish canonical docs from stale
  branches.

## Core Principles

### 1. Trunk-first, not leaf-first

The system must build and protect canonical documentation trunks first. Cleanup starts by defining
the valid mainline for a concern, not by editing random stale leaves.

### 2. Delete invalid/stale docs aggressively

Once a canonical replacement exists and link/update guards pass, stale or redundant material should
be deleted instead of being kept alive through repeated wording changes.

### 3. Keep only current, architecturally truthful docs

Only canonical trunks may present current truth. Supporting docs may explain or operationalize that
truth. Reports and plans cannot remain as parallel live universes for the same concern.

### 4. AI-friendly hierarchy

The structure must be simple enough that an AI can answer four questions reliably:

- What is the canonical trunk?
- What is only support material?
- What is historical evidence?
- What is obsolete and should not be used?

## Non-Goals

- This change does not immediately rewrite or migrate the full repository.
- This change does not redefine runtime/API truth outside the rules already in
  `architecture/STANDARDS.md`.
- This change does not require every historical report to remain accessible in active trees.

## Canonical Trunk Model

The repository SHALL treat the following as the canonical trunks for their concerns:

| Concern | Canonical trunk | Notes |
|---|---|---|
| Repository-wide engineering rules | `architecture/STANDARDS.md` | Shared governance truth |
| Current capability truth | `openspec/specs/` | What is currently governed as built / required |
| Approved pending change truth | `openspec/changes/<change-id>/` | Proposed deltas before implementation |
| API contract truth | `FastAPI routes + Pydantic Schema + /openapi.json` | Markdown API notes cannot override this |
| Operations / runbooks | `docs/operations/` | Active operational procedures |
| Testing guidance | `docs/testing/` | Active test strategy / runbook area |
| Historical evidence | `docs/reports/` or `archive/docs/` | Not current truth |

Additional indexes may route readers to these trunks, but indexes are navigational aids, not a
parallel truth layer.

## Lifecycle Classes

Each retained document family should be classified into one of these lifecycle classes:

- `canonical`: authoritative active trunk document
- `supporting`: active helper document beneath a canonical trunk
- `report`: historical evidence or verification output
- `plan`: future-facing planning material
- `generated_reference`: generated listing, export, or reference artifact
- `archive_candidate`: historical material to move out of active trees
- `delete_candidate`: redundant material that should be removed once guards pass

The important distinction is that only `canonical` documents are allowed to present current truth.

## Trunk-First Decision Workflow

Every cleanup decision must start from the canonical trunk, not from the stale file itself.

For each document cluster:

1. Identify the canonical trunk for that concern.
2. Map every retained branch document back to that trunk.
3. Assign one decision status:
   - `keep-canonical`
   - `keep-supporting`
   - `merge-into-trunk`
   - `archive`
   - `delete`
   - `needs-replacement`
4. Only then execute migration, archive, or deletion.

### Deletion Gate

A document may be deleted only when all of the following are true:

- a canonical replacement or canonical trunk already exists
- inbound references / indexes / README links have been updated or explicitly retired
- the document is not needed for audit retention, active migration, or compatibility communication
- the decision register marks it `delete`

If any of these are missing, the document is not deleted yet.

### Default Action Bias

When a stale document has a valid canonical replacement and no retention obligation, the default
action bias is `delete`, not `rewrite`. `archive` is reserved for materials that still need
historical retention or audit access.

## Why Delete/Archive Beats Mass Header Editing

Manual relabeling is only a transition tactic. It is not the target system.

At repository scale:

- editing thousands of old reports does not reduce documentation volume
- historical noise remains searchable and continues to distract readers and AI
- stale trees still look alive even if individual files carry warning banners

The better steady state is:

- keep a small active canonical surface
- archive retained evidence
- delete redundant stale branches
- make the active hierarchy explicit enough that AI can infer scope and obsolescence correctly

## Cluster-Based Execution Model

Cleanup should run by high-risk document clusters, not by random file order.

Recommended wave order:

1. `docs/api/`
   - highest risk of being mistaken for current API truth
2. `docs/reports/`
   - large evidence surface, should become clearly historical
3. `docs/guides/`
   - active guidance vs stale feature notes must be separated
4. `docs/overview/`, `docs/operations/`, `docs/testing/`
   - ensure top-level navigation points to the right trunks

Within each wave:

- define the canonical trunk
- produce inventory and decision register
- update indexes
- archive/delete bounded batches

## Tooling Model

The implementation should introduce lightweight governance tooling:

- a machine-readable documentation taxonomy / governance manifest
- an audit command that classifies docs by subtree and lifecycle
- inventory output that flags:
  - unclassified documents
  - duplicate truths
  - historical reports in active trees
  - delete candidates without replacement mapping

The tooling should guide humans and AI; it should not perform broad destructive moves by default.

## Recommended Implementation Outputs

- `docs/overview/documentation-system.md`
  - canonical trunk map and precedence rules
- `docs/README.md` or equivalent canonical docs index
  - navigation entrypoint to active trunks
- `config/governance/documentation-taxonomy.yaml`
  - machine-readable lifecycle and trunk definitions
- `scripts/governance/audit_documentation_system.py`
  - audit inventory and decision support
- `docs/reports/documentation-governance/`
  - inventory, decision register, cleanup wave reports

## Validation Strategy

- `openspec validate govern-documentation-truth-lifecycle --strict`
- Verify canonical trunks are explicitly named and non-overlapping.
- Verify tasks include inventory, decision register, and bounded cleanup waves.
- During implementation, verify each delete batch updates inbound indexes before removal.

## Rollout Guidance

- Do not continue mass manual disclaimer edits once this change is approved.
- Publish the canonical trunk map first.
- Run subtree inventory second.
- Execute cleanup in bounded waves with path-specific commits.
- Prefer delete/archive decisions over long-term historical-file rewriting.
