# Backend OpenSpec Issue Publication Review

> Reviewer: Claude (Matt Pocock triage skills perspective)
> Date: 2026-05-18
> Scope: `docs/reports/quality/backend-openspec-issue-publication-preflight-2026-05-18.md` and `docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/manifest.md`

## Verdict

**Publication blocked — 3 must-fix items, 2 should-fix items, 5 observations.**

The preflight and manifest structure is sound: dependency chains are consistent, label selection is correct per issue type, and no issue is prematurely `ready-for-agent`. The blockers are operational: missing triage labels on GitHub, a missing artifact with no evidence the generator works, and missing category labels on every issue.

---

## Must-Fix (blocks publication)

### M1. Triage labels do not exist on the repository

The GitHub repo `chengjon/mystocks` has only 9 default GitHub labels (`bug`, `enhancement`, `wontfix`, etc.). It does **not** have:

- `needs-triage`
- `needs-info`
- `ready-for-agent`
- `ready-for-human`

Every `gh issue create` command uses `--label ready-for-human` or `--label needs-triage`. Every single command will **fail** with `gh: Label "needs-triage" not found`.

**Fix**: create the 4 labels before running any manifest command:

```bash
gh label create needs-triage --repo chengjon/mystocks --description "Awaiting maintainer evaluation" --color FBCA04
gh label create needs-info --repo chengjon/mystocks --description "Waiting for more information from reporter" --color 0052CC
gh label create ready-for-agent --repo chengjon/mystocks --description "Fully specified, safe for AFK agent" --color 0E8A16
gh label create ready-for-human --repo chengjon/mystocks --description "Needs human judgment or implementation" --color B60205
```

### M2. Issue 2 references a missing artifact with no proof the generator works

Issue `02-refresh-route-openapi-evidence.md` requires `openapi-before.json` as a deliverable. But `scripts/generate_openapi.py` has not been successfully run — `openapi-before.json` does not exist in `docs/reports/quality/generated/`.

The acceptance criteria says "or the issue records why OpenAPI generation is blocked" — that is the correct fallback. But the manifest treats this issue as one that can move from `needs-triage` to `ready-for-agent`. If `generate_openapi.py` requires a running FastAPI app or has missing dependencies, this issue cannot be grabbed by an agent until the script is executable.

**Fix**:

1. Run `python scripts/generate_openapi.py --output docs/reports/quality/generated/openapi-before.json` locally first. Record the result.
2. If the script requires a running app, add a precondition to the issue body, or split the issue: one for route table refresh (agent-runnable) and one for OpenAPI generation (blocked).

### M3. Every issue is missing a category label

Per the triage skill: *"Every triaged issue should carry exactly one category label and one state label."* Issue 1 gets `ready-for-human` (state) but no category (`enhancement` or `bug`). Same for all 12 `needs-triage` issues.

The Matt Pocock triage state machine requires **exactly one category + one state**. The current drafts only assign state labels.

**Fix**: every `gh issue create` command needs a second `--label`:

- Issue 1: `--label ready-for-human --label enhancement`
- Issues 2, 8, 10, 11: `--label needs-triage --label enhancement` (evidence/build tasks)
- Issues 3, 4, 5, 9, 12: `--label needs-triage --label enhancement` (HITL decisions, still `enhancement` category)
- Issues 6, 7, 13: `--label needs-triage --label enhancement` (follow-up proposals / design drafts)

---

## Should-Fix (strongly recommended)

### S1. No issue is `ready-for-agent` — correct, but 3 issues are candidates and the manifest should note this

The preflight report correctly prevents premature `ready-for-agent`. But issues 2, 10, 11 are **evidence-only** tasks with clear verification commands — they are the strongest candidates for future `ready-for-agent` transition. The manifest should document this in a post-publish section:

```markdown
## Post-Triage Agent Readiness

After issue 1 approval and triage re-evaluation:
- Issue 2 can move to `ready-for-agent` if generate_openapi.py runs successfully
- Issue 10 can move to `ready-for-agent` after issue 1 approval
- Issue 11 can move to `ready-for-agent` after issue 1 approval
```

This lets the maintainer see at a glance which issues are immediately actionable by agents after approval.

### S2. Manifest publication order mixes HITL decisions with evidence tasks

Current order: 1 → 2 → **10, 11** → 3 → 4 → 5 → 8 → 9 → 12 → 13 → 6 → 7

This is grouped by dependency chain, not execution priority. Issues 10, 11 (Core import matrix, singleton inventory) are prerequisites for long-pole E/F work, but they're sequenced before C/G decisions (issues 3-5) which don't depend on them. This creates an artificial serialization.

**Recommendation**: split the manifest into two publication tracks that can proceed in parallel:

- **Track A (C/G)**: 1 → 2 → 3, 4, 5 → 8 → 9 → 6, 7
- **Track B (E/F)**: 1 → 10, 11 → 12 → 13

Both tracks depend on issue 1, but are otherwise independent. Publishing both tracks lets agents pick up evidence tasks in parallel.

---

## Observations (informational)

### O1. Preflight checks are comprehensive and well-structured

The 9 preflight checks cover the right gates: file count, label correctness, no premature `ready-for-agent`, required body sections, dependency placeholders, and publication order. This is good practice for the project.

### O2. All 13 issue bodies follow correct `Blocked by` pattern

Every issue has an explicit `Blocked by` section. `BLOCKED_BY_TODO` placeholders are exactly right for the pre-publication state. The dependency chain is consistent: no issue references a dependency that hasn't been published yet.

### O3. No issue body mentions `web/backend/CONTEXT.md` updates

The issue-tracker config (`docs/agents/issue-tracker.md` line 6) requires backend audit issues to include updates to `web/backend/CONTEXT.md` or `FUNCTION_TREE.md`. The decision issues (03-05, 09, 12) should state whether CONTEXT.md needs updating as a deliverable. Currently none mention it.

### O4. `strategy_management.py` flat file (flagged in prior triage) still not in issue 4 scope

In the prior triage of `consolidate-backend-api-domain-routers`, `web/backend/app/api/strategy_management.py` was identified as a separate flat file existing alongside the `strategy_management/` package. Issue `04-decide-strategy-router.md` lists `strategy.py`, `strategy_mgmt.py`, `strategy_management/`, and `strategy_list_mock.py` but does **not** list `strategy_management.py`. If this is another shim or compatibility surface, the decision issue's scope is incomplete.

### O5. `generate_openapi.py` has not been tested

The preflight report verifies that referenced scripts exist but does not verify they actually work. Given that `openapi-before.json` is missing, this strongly suggests the script cannot run cleanly. The pre-publish step should execute both verification commands before green-lighting all 13 issues.

---

## Revised Publication Checklist

| Step | Action | Status |
|------|--------|--------|
| 0 | Create 4 triage labels on `chengjon/mystocks` | **Required** |
| 1 | Run `python scripts/generate_openapi.py --output docs/reports/quality/generated/openapi-before.json`; record result | **Required** |
| 2 | Add `--label enhancement` to all 13 `gh issue create` commands | **Required** |
| 3 | Verify `strategy_management.py` belongs in issue 4 scope; if not, document why | Recommended |
| 4 | Publish issue 1 (`ready-for-human` + `enhancement`) | After steps 0-2 |
| 5 | Replace `BLOCKED_BY_TODO: issue 1` with real issue number | After step 4 |
| 6 | Publish remaining 12 (`needs-triage` + `enhancement`) | After step 5 |
| 7 | Replace all remaining `BLOCKED_BY_TODO` placeholders | After step 6 |
| 8 | Schedule triage re-evaluation for issues 2, 10, 11 for agent-readiness | After approval |

---

## Summary

The preflight and manifest are well-engineered artifacts. The dependency topology is correct, the no-mutation boundaries are properly enforced, and the label choices match each issue's current readiness state. The publication blockers are all **operational infrastructure** (labels, script verification, category labels), not structural or logical problems in the drafts themselves. Once the 3 must-fix items are resolved, the 13-issue publication package is ready to ship.
