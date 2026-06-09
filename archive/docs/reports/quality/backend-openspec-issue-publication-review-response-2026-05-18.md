# Backend OpenSpec Issue Publication Review Response

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> Response to
> `docs/reports/quality/backend-openspec-issue-publication-review-2026-05-18.md`.
> GitHub triage labels were created and verified. No GitHub Issues were
> created, and no `gh issue create` command was executed.
> Later publication record: after explicit approval and runbook execution,
> issue 1 was created as `https://github.com/chengjon/mystocks/issues/80`.
> This response remains a pre-publication review response.

## Verdict

The publication review was substantially correct. The publication blockers were
operational rather than structural. This response fixes the draft package where
safe to do so and records remaining actions that require explicit human approval
or a real GitHub publication step.

Cross-line alignment from
`docs/reports/quality/cross-line-alignment-P3-impl-openspec-2026-05-18.md`
further narrows the package: the announcement, strategy, and risk canonical
router decision issues are already resolved by the P3 implementation line and
must not be published. Later G-line progress also superseded the original 08/09
health taxonomy and canonical-path drafts. The package was then compressed for
reviewability: it now has 3 publishable issues, 3 retained audit-only body
files, 2 publication-hold body files awaiting reclassification, and 7
superseded source bodies merged into bodies 14/15.

## Disposition

| Finding | Status | Resolution |
|---|---|---|
| M1: Triage labels do not exist on repository | Fixed | Created and verified `needs-triage`, `needs-info`, `ready-for-agent`, and `ready-for-human` on `chengjon/mystocks`. Added setup record in `docs/reports/quality/backend-openspec-label-setup-2026-05-18.md`. |
| M2: Issue 2 references missing `openapi-before.json` and generator was unverified | Fixed | Ran `python scripts/generate_openapi.py --output docs/reports/quality/generated/openapi-before.json`; it succeeded and produced valid OpenAPI 3.1.0 JSON with 501 paths. Added pre-publish verification note to issue 2. |
| M3: Issues missing category label | Fixed | Added `--label enhancement` to all 3 publishable `gh issue create` draft commands while keeping exactly one state label. |
| S1: Manifest should identify future `ready-for-agent` candidates | Fixed | Added `Post-Triage Agent Readiness` section for issue 14; issue 15 stays human/design-oriented and held G drafts 08/09 are not readiness candidates. |
| S2: Manifest should show parallel publication tracks | Fixed | Added Track A (C/G) and Track B (E/F) publication guidance. |
| O3: Decision issues do not mention context/governance doc updates | Fixed for decision issues | Publishable decision issue 12 requires a decision on `web/backend/CONTEXT.md`, `docs/FUNCTION_TREE.md`, or related governance document updates. Audit-only issues 3, 4, and 5 retain the historical criterion; issue 9 is held for reclassification. |
| O4: Issue 4 omits `strategy_management.py` | Superseded | Issue 4 already names `strategy_management.py`, and is now audit-only because P3 resolved the strategy canonical router decision. |
| O5: `generate_openapi.py` had not been tested | Fixed | Same as M2; command now has a recorded successful local run. |

## Cross-Line Alignment Disposition

| Draft issue | Aligned status |
|---|---|
| 1 | Updated to acknowledge P3-resolved C announcement/strategy/risk work and scope approval to remaining governance decisions. |
| 2 | Updated to reference existing route table and OpenAPI artifacts; remaining work is post-P3 regeneration/reconciliation and diffing. |
| 3 | Marked audit-only / do not publish; announcement canonical router resolved by P3-A1 and `243d40a8a`. |
| 4 | Marked audit-only / do not publish; strategy canonical router resolved by P3-A2 and `1241c4b7e`. |
| 5 | Marked audit-only / do not publish; risk canonical router resolved by P3-A3 and `243d40a8a`. |
| 8 | Publication hold; G-line evidence superseded the original taxonomy scope. |
| 9 | Publication hold; G-line evidence superseded the original canonical-path decision scope. |
| 14 | New compressed shared evidence package, merging original 02/10/11. |
| 15 | New compressed post-approval planning issue, merging original 06/07/12/13 and G residual-tail disposition. |

## Verification Evidence

### GitHub Label Check

`gh api repos/chengjon/mystocks/labels --paginate` showed existing labels:

```text
bug, documentation, duplicate, enhancement, good first issue, help wanted,
invalid, question, wontfix
```

Missing triage state labels:

```text
needs-triage, needs-info, ready-for-agent, ready-for-human
```

Labels were created and verified after human continuation approval. See:

```text
docs/reports/quality/backend-openspec-label-setup-2026-05-18.md
```

### OpenAPI Generation

Command executed locally:

```bash
python scripts/generate_openapi.py --output docs/reports/quality/generated/openapi-before.json
```

Result:

```text
exit code: 0
output: docs/reports/quality/generated/openapi-before.json
OpenAPI: 3.1.0
paths: 501
```

Non-blocking warning observed:

```text
Duplicate Operation ID redirect_to_canonical_api_strategy_mgmt__path__get
for function redirect_to_canonical at app/api/_strategy_mgmt_compat.py
```

## Remaining Publication Gate

Publication is still blocked until a human explicitly allows one of these
actions:

1. Publish issue 1 using the manifest command.
2. Replace `BLOCKED_BY_TODO` placeholders with real GitHub issue numbers as
   blockers are published.

The aligned draft package remains publication-ready for the 3 publishable
issues after those operational steps. The audit-only 03/04/05 body files must
remain unpublished unless a human explicitly asks to create historical tracking
issues. The held 08/09 body files must remain unpublished until a human
explicitly reclassifies them or replaces them with G-line residual-tail issues.
The superseded 02/06/07/10/11/12/13 body files must remain unpublished because
their scope is merged into bodies 14/15.
