# B4.012-M1 Residual Dirty Domain Atlas No-Source Audit

Date: 2026-06-12

Mode: no-source audit, no deletion-retirement authorization, no source/test/runtime edits

## Scope

This audit starts the next governance domain after the B4.011 docs/archive and governance-card residual line closed.

Current baseline:

- Branch: `wip/root-dirty-20260403`
- HEAD: `022afee04 B4.011: close governance card residual retirement`
- FUNCTION_TREE active gates: none
- Staged files at audit start: none

This report is inventory only. It does not authorize or perform:

- source, test, runtime, route, API, OpenSpec, ST-HOLD, or `marketKlineData` edits
- deletion-retirement
- broad restore/reset/clean
- path migration
- staging of dirty files outside this audit evidence

## Dirty Distribution

Current total dirty entries: `735`

| Bucket | Count | Status mix | Risk | Initial decision |
| --- | ---: | --- | --- | --- |
| `tests` | 260 | `M 246`, `D 1`, `?? 13` | high | Needs dedicated test-domain audit before any preservation, deletion, or repair. Do not batch with source fixes. |
| `scripts` | 162 | `M 148`, `D 1`, `?? 13` | high | Needs script/tooling audit; distinguish generated tooling, one-off analysis scripts, and runtime tools. |
| `backend_source` | 116 | `M 104`, `D 4`, `?? 8` | high | Needs source-domain audit and GitNexus impact before implementation. |
| `frontend` | 86 | `M 64`, `?? 22` | high | Needs frontend-domain no-source review. Known external dirty line `web/frontend/src/layouts/archive/BaseLayout.vue` remains isolated. |
| `untracked_other` | 51 | `?? 51` | mixed/unknown | Needs provenance review; includes agent/plugin/zread/project-exchange/report artifacts. |
| `openspec` | 23 | `?? 23` | medium/high | Needs OpenSpec-specific no-source audit and `openspec` status checks before archive or deletion. |
| `other` | 21 | `M 21` | mixed | Needs governance/docs/config split. Includes root docs, task files, env/config. |
| `governance` | 10 | `M 1`, `?? 9` | medium | Candidate first small batch after this atlas; task-card residuals require node/owner mapping. |
| `deletion_candidates_other` | 4 | `D 4` | high | Needs deletion-retirement audit; no deletion acceptance by status alone. |
| `protected_docs` | 2 | `?? 2` | medium | Do not touch without docs/guides-specific authorization. |

## Samples

Representative samples, not full file lists:

### tests

- `scripts/tests/legacy/test_frontend_comprehensive.py`
- `scripts/tests/legacy/test_frontend_deep.py`
- `scripts/tests/test_add_python_headers.py`
- `scripts/tests/test_advanced_analysis_api_integration.py`
- `scripts/tests/test_check_api_health.py`

### scripts

- `scripts/ai_enhancer/advanced_enhancement.py`
- `scripts/ai_enhancer/analyzer.py`
- `scripts/ai_test_optimizer/main.py`
- `scripts/analyze_api_data_usage/api_analyzer.py`
- `scripts/analyze_dependencies.py`

### backend_source

- `src/adapters/akshare/legacy_market_data.py`
- `src/adapters/financial/financial_data_source.py`
- `src/application/bootstrap.py`
- `src/application/dto/trading_dto.py`
- `src/alternative_data/news_sentiment_analyzer.py`

### frontend

- `web/frontend/src/App.vue`
- `web/frontend/src/components.d.ts`
- `web/frontend/src/layouts/archive/BaseLayout.vue`
- `web/frontend/src/views/BacktestAnalysis.vue`
- `web/frontend/src/views/StrategyManagement.vue`

### openspec

- `openspec/changes/archive/2026-04-22-update-frontend-data-governance-with-fincept-patterns/`
- `openspec/changes/archive/2026-05-12-add-broker-acknowledgement-reconciliation-contract/`
- `openspec/changes/archive/2026-05-12-add-containerized-runtime-deployment-capability/`
- `openspec/changes/archive/2026-05-12-add-miniqmt-live-bridge-runtime-contract/`
- `openspec/changes/archive/2026-05-12-add-page-audit-orchestration-governance/`

## Risk Interpretation

- The remaining dirty worktree is not a docs-only cleanup problem anymore.
- The largest buckets are tests, scripts, backend source, and frontend. These require separate no-source audits and separate implementation authorizations.
- Deletion-retirement remains high-risk even for four apparently doc-oriented deleted paths.
- OpenSpec paths are policy-sensitive and need OpenSpec-specific validation before archive/delete/preserve decisions.
- Low-risk opportunistic cleanup is not appropriate because the current state is broad and cross-domain.

## Recommended Queue

Recommended order:

1. `B4.012-M2a governance/task-card residual audit`
   - Scope: `governance/**` dirty and untracked task-card artifacts only.
   - Reason: smallest bounded governance group after B4.011; likely low/medium risk but still needs node mapping.

2. `B4.012-M2b deletion-candidates-other no-source review`
   - Scope: four deleted paths outside the B4.011 docs reports flow:
     - `DELETION-CANDIDATES.md`
     - `docs/DOCUMENTATION_ARCHITECTURE_OPTIMIZATION_PROPOSAL.md`
     - `docs/plans/ABSOLUTE_LINK_INVENTORY.md`
     - `docs/plans/INDEX_INVENTORY.md`
   - Reason: explicit deletion-retirement candidate group; must not be accepted by status alone.

3. `B4.012-M2c OpenSpec archive/untracked provenance audit`
   - Scope: 23 `openspec/**` untracked archive/change paths.
   - Reason: policy-sensitive; requires OpenSpec status and validation before disposition.

4. `B4.012-M2d protected docs/guides audit`
   - Scope:
     - `docs/guides/DOCUMENTATION_FRAMEWORK.md`
     - `docs/guides/NEW_API_SOURCE_INTEGRATION_GUIDE.md`
   - Reason: protected docs tree; keep separate from source/test/script work.

5. High-risk implementation domains after the above:
   - frontend
   - backend source
   - scripts/tooling
   - tests

## Guardrails

- Do not mix source/test/frontend/script changes with governance/docs/openSpec disposition.
- Do not use broad `git add -A`, `git clean`, `git restore .`, or root reset.
- Do not delete by static unused or status-only evidence.
- Each follow-up node must define explicit allowed paths, forbidden paths, gates, and closeout criteria.
- GitNexus direct CLI and OPENDOG verification remain required before implementation commits.

## Decision

B4.012-M1 is evidence-prepared for the next residual dirty governance domain. The next safe action is to create a FUNCTION_TREE node for this atlas and prepare a narrow no-source follow-up for `B4.012-M2a governance/task-card residual audit`.
