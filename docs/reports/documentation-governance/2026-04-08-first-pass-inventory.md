# Documentation Governance First-Pass Inventory

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **历史治理报告说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 在 2026-04-08 的首轮盘点结果，属于治理执行证据，不是仓库共享规则或当前能力真相源。
> 若涉及共享规则、审批门禁或删除判定，请优先回到 `architecture/STANDARDS.md`、`docs/README.md`、`docs/overview/documentation-system.md` 与相关 OpenSpec 变更。

## Scope

本轮只做高风险文档树的 inventory，不做大规模 rewrite / archive / delete：

- `docs/api/`
- `docs/reports/`
- `docs/guides/`
- `docs/overview/`
- `docs/operations/`
- `docs/testing/`

## Measurement Method

- Measured at: `2026-04-08`
- Command:

```bash
python -c "from collections import Counter; from pathlib import Path; from scripts.governance.audit_documentation_system import build_report; import json; report=build_report(Path('.').resolve()); prefixes=['docs/api/','docs/reports/','docs/guides/','docs/overview/','docs/operations/','docs/testing/']; result={}; \
for prefix in prefixes: \
    classified=[item for item in report['classifications'] if item['path'].startswith(prefix)]; \
    unclassified=[item for item in report['findings']['unclassified'] if item['path'].startswith(prefix)]; \
    result[prefix]={'classified':len(classified),'unclassified':len(unclassified),'by_lifecycle':dict(Counter(item['lifecycle'] for item in classified))}; \
print(json.dumps(result, ensure_ascii=False, indent=2))"
```

## Measured Inventory Snapshot

| Subtree | Classified | Unclassified | Measured lifecycle mix | Current inventory verdict |
|---|---:|---:|---|---|
| `docs/api/` | 70 | 145 | `canonical=1`, `supporting=66`, `delete_candidate=3` | Active navigation exists, but legacy/API-note sprawl is still large |
| `docs/reports/` | 339 | 667 | `canonical=1`, `report=338` | Historical evidence trunk exists, but subtrees remain largely unclassified |
| `docs/guides/` | 0 | 250 | none | No canonical guide taxonomy yet; this is the biggest unresolved truth-routing gap |
| `docs/overview/` | 2 | 13 | `canonical=1`, `supporting=1` | New docs trunk exists, but old overview indexes still overlap |
| `docs/operations/` | 23 | 16 | `canonical=1`, `supporting=22` | Runbook trunk exists and is mostly alignable |
| `docs/testing/` | 11 | 20 | `canonical=1`, `supporting=10` | Testing trunk exists, but legacy/compatibility leaves remain |

## Cluster Notes

### 1. `docs/api/`

- Canonical navigation trunk exists: `docs/api/README.md`
- Actual contract truth remains outside markdown: FastAPI routes + Pydantic schema + exported OpenAPI
- Current measured blocked delete candidates are limited to `docs/api/legacy-cn/`
- Inventory conclusion:
  - keep `docs/api/README.md` as trunk
  - treat `docs/api/legacy-cn/` as a bounded cleanup cluster
  - defer broad delete until inbound links are audited

### 2. `docs/reports/`

- Canonical historical evidence trunk exists: `docs/reports/README.md`
- Measured classified volume is high, but unclassified volume is also high
- This subtree should be treated as evidence storage, not live truth
- Inventory conclusion:
  - keep the reports trunk
  - partition subtrees into retained evidence vs archive batches before any rewrites

### 3. `docs/guides/`

- This is the highest unresolved trunk problem after `docs/api/`
- Measured result is `0 classified / 250 unclassified`
- Existing `docs/guides/README.md` and `docs/guides/INDEX.md` act as broad historical catch-all entrypoints, not concern-specific trunks
- Inventory conclusion:
  - block subtree-wide cleanup until guide families are mapped to canonical replacements
  - split guide governance by concern instead of treating `docs/guides/` as one active truth tree

### 4. `docs/overview/`

- New trunk map exists through `docs/README.md` and `docs/overview/documentation-system.md`
- `docs/overview/README.md` still overlaps with old “docs root index” behavior
- Inventory conclusion:
  - retain for now as supporting
  - converge remaining overview indexes into the new docs trunk

### 5. `docs/operations/`

- `docs/operations/README.md` is already a workable canonical runbook entrypoint
- Remaining issue is subtree classification depth, not missing mainline
- Inventory conclusion:
  - keep trunk
  - defer cleanup to bounded runbook classification wave

### 6. `docs/testing/`

- `docs/testing/README.md` is already the testing guidance trunk
- Legacy and compatibility leaves remain alongside active guidance
- Inventory conclusion:
  - keep trunk
  - classify compatibility docs and `legacy-cn` as separate cleanup families

## First-Pass Risk Ranking

1. `docs/guides/`
   - reason: no trunk classification coverage yet; broad historical catch-all behavior remains
2. `docs/api/`
   - reason: easy to misread as contract truth; measured delete-candidate cluster already exists
3. `docs/reports/`
   - reason: large historical volume still lives in active tree and remains highly searchable
4. `docs/overview/`
   - reason: overlap with new docs entrypoint
5. `docs/testing/`
   - reason: compatibility leaves and legacy material remain mixed with active guidance
6. `docs/operations/`
   - reason: trunk exists; remaining problem is mostly subtree classification

## Next Action

下一步执行以 `2026-04-08-decision-register.md` 为准：

1. lock canonical replacements per cluster
2. mark blocked clusters with no replacement
3. route cleanup waves from those decisions
