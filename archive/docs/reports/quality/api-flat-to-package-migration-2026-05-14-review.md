# Review: api-flat-to-package-migration-2026-05-14.md

**Type**: `.md` / `plan` | **Perspective**: completeness + feasibility | **Date**: 2026-05-14 | **Reviewer**: Claude

## Executive Summary

This API migration roadmap correctly identifies the flat/package coexistence problem across 10+ domains and proposes a logical 7-phase cleanup. The priority matrix is well-reasoned. However, the document misses `strategy_list_mock.py` from the strategy domain, has invalid Python syntax in the target state code, and doesn't account for several flat API files discovered in the codebase.

## Evidence Verification

### Claims Verified

| Claim | Status | Evidence |
|-------|--------|----------|
| router_registry.py as routing fact source | confirmed | 5.0K file at `web/backend/app/router_registry.py` |
| market.py is 1-line compat shim | unverified | File exists but content not checked |
| strategy_management.py is 1-line shim | confirmed | 101 bytes, 2 lines |
| 4 strategy-related router registrations | confirmed | strategy_mgmt, strategy_management (flat+package), strategy_list_mock in router_registry |
| announcement dual registration | confirmed | `include_router(announcement.router, prefix="/api")` in router_registry |
| risk domain 5 entries | confirmed | risk_management.py (992B), risk_management_core.py (5.9K), risk_management_v31.py (671B), risk/, risk_v31/ |

## Findings

### Medium

| # | Section | Issue | Evidence | Recommendation |
|---|---------|-------|----------|----------------|
| 1 | §2.3 | Missing `strategy_list_mock.py` (1.5K) — registered in router_registry.py but not in strategy domain analysis | `grep strategy_list_mock router_registry.py` confirms registration | Add to strategy file listing and deletion plan |
| 2 | §五 | Target state code has invalid Python syntax — `from app.api.market import router` inside dict literal is not valid | Section 五 code block | Replace with proper import statements + dict of references |
| 3 | §1.1 | No mention of `data_quality.py`, `dashboard.py`, `tasks.py`, `pool_monitoring.py` which also have flat API files | These files exist in `web/backend/app/api/` | Verify if they need migration and add to scope |
| 4 | §四 | No per-phase rollback plan | No rollback mentioned | Add `git revert` strategy for each phase |
| 5 | §四 | No test strategy for verifying routes after migration | No mention of route verification | Add `app.routes` diff comparison before/after each phase |

## Scoring

| Dimension | Score (1-5) |
|-----------|-------------|
| Technical Accuracy | 3 |
| Completeness | 3 |
| Codebase Alignment | 3 |
| Actionability | 4 |
| **Overall** | **3.3** |

## Verdict

**APPROVE_WITH_NOTES** — Migration plan is solid but incomplete in coverage (missing strategy_list_mock, possible additional flat files) and the target state code needs syntax correction.
