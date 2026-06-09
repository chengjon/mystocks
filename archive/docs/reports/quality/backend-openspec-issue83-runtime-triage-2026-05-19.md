# Backend OpenSpec Issue 83 Runtime Triage

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: historical runtime triage plus implementation-lane provenance; superseded for current runtime state by `codebase-map-task-completion-validity-2026-05-21.md`.

## Inputs

- Current GitHub issue state for #80 and #83
- Current checkout import smoke and collection smoke
- Commit-scoped runtime gate evidence from `bbb399071` when the root checkout lacks that report
- Core split and OpenSpec publication line summaries

## Findings

| Item | Result |
|---|---|
| GH #80 | `OPEN`, labels `enhancement` and `ready-for-human`; approval trail is present |
| GH #83 | `OPEN`, labels `enhancement` and `ready-for-agent`; evidence-package work only |
| Current HEAD | `6530c88f3 docs(codebase): record openspec execution evidence`; does **not** contain `bbb399071` |
| Remote branch | `origin/wip/root-dirty-20260403` points at `bbb399071df53c2ae6a1001f0b65ebf3e8baddea` |
| `ContractDriftIncidentListResponse` import | Passed |
| `app.main` import | Failed on bare `_data_lineage_responses` in `web/backend/app/api/data_lineage.py:43` via `router_registry` |
| `web/backend/tests/test_health_route_conflicts.py --collect-only -q --no-cov` | Failed on the same import chain during collection |
| Runtime gates `4.3` / `4.4` / `4.5` | Closed by existing commit-scoped runtime evidence in `bbb399071` for the implementation worktree; current checkout remains blocked by the stale import chain |
| issue15 | Remains unpublished until the #83 evidence result is reviewed |

## Conclusion

- The current checkout failure is still a stale-checkout / branch-divergence signal, because the local HEAD `6530c88f3` does not contain `bbb399071`.
- A separate implementation lane would be required if anyone wants to change backend source files for the bare `_data_lineage_responses` import.
- A separate implementation lane was executed on `2026-05-21` after user continuation approval. It removed the current-checkout runtime import blocker without changing #83's evidence-package scope.
- This report does not authorize OpenSpec proposal creation or issue publication.

## 2026-05-21 Supersession

This report is now historical triage evidence, not the current runtime state.
Later sequence-unblock evidence and the current validity review at HEAD
`f97f2eb57` show that `app.main` import, health collect-only, and minimal
OpenAPI smoke pass in clean current HEAD. The remaining governance issue is not
this import blocker; it is evidence adoption plus the separate PM2/backend
runtime, route/OpenAPI governance, Core Batch 2, and archive gates.

## Verification

- `gh issue view 80 --json number,state,labels,title,url,body`
- `gh issue view 83 --json number,state,labels,title,url,body`
- `git log -1 --oneline`
- `git ls-remote origin refs/heads/wip/root-dirty-20260403`
- `git merge-base --is-ancestor bbb399071 HEAD`
- `PYTHONPATH=web/backend python -c "from app.api.contract.schemas import ContractDriftIncidentListResponse; print(ContractDriftIncidentListResponse.__name__)"`
- `PYTHONPATH=web/backend python -c "from app.main import app; print(len(app.routes))"`
- `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py --collect-only -q --no-cov`

## 2026-05-20 Refresh

Fresh command results:

```text
git log -1 --oneline
6530c88f3 docs(codebase): record openspec execution evidence

git ls-remote origin refs/heads/wip/root-dirty-20260403
bbb399071df53c2ae6a1001f0b65ebf3e8baddea refs/heads/wip/root-dirty-20260403

git merge-base --is-ancestor bbb399071 HEAD
exit=1
```

```text
GH #80: OPEN, labels enhancement,ready-for-human
GH #83: OPEN, labels enhancement,ready-for-agent
```

```text
ContractDriftIncidentListResponse import: passed
app.main import: failed with ModuleNotFoundError: No module named '_data_lineage_responses'
test_health_route_conflicts.py collection: failed with the same import chain
```

Current source state:

```text
HEAD web/backend/app/api/data_lineage.py:43
from _data_lineage_responses import (

2d6682e81 web/backend/app/api/data_lineage.py:41
from ._data_lineage_responses import (

bbb399071 web/backend/app/api/data_lineage.py:41
from ._data_lineage_responses import (
```

## 2026-05-21 Separate Implementation-Lane Fix

Scope:

- `web/backend/app/api/data_lineage.py`
- `web/backend/app/api/_data_lineage_responses.py`

Implementation result:

- `data_lineage.py` now imports the companion module via package-relative import: `from ._data_lineage_responses import (...)`.
- `data_lineage.py` now imports the extracted request/response model names and `_AsyncpgLineageConnectionAdapter` from the companion module instead of relying on local definitions.
- `_data_lineage_responses.py` now owns the imports required by its extracted models and adapter: `asynccontextmanager`, `datetime`, `List`, `Optional`, `BaseModel`, and `Field`.
- #83 remains evidence-package work only; this source fix is recorded as a separate implementation-lane fix for the current checkout runtime blocker.

Fresh verification after the fix:

```text
pytest -o addopts= web/backend/tests/test_data_lineage_regressions.py -q --no-cov
1 passed

PYTHONPATH=web/backend python -c "from app.main import app; print(len(app.routes))"
548

pytest -o addopts= web/backend/tests/test_health_route_conflicts.py --collect-only -q --no-cov
112 tests collected

pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov
112 passed

python -m py_compile web/backend/app/api/data_lineage.py web/backend/app/api/_data_lineage_responses.py
exit=0

ruff check web/backend/app/api/data_lineage.py web/backend/app/api/_data_lineage_responses.py web/backend/tests/test_data_lineage_regressions.py
All checks passed!
```
