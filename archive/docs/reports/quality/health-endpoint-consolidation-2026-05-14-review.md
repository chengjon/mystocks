# Review: health-endpoint-consolidation-2026-05-14.md

**Type**: `.md` / `plan` | **Perspective**: completeness + consistency | **Date**: 2026-05-14 | **Reviewer**: Claude

## Executive Summary

Correctly identifies the health endpoint fragmentation problem and proposes consolidation to the canonical `health.py`. However, the document lists only **9** scattered endpoints when the actual count is **21** — more than half the problem is invisible.

## Evidence Verification

grep for `"/health"` in `web/backend/app/api/` (excluding health.py) found **21** scattered endpoints:

1. trade/routes.py (listed)
2. metrics.py (listed)
3. monitoring_old/routes.py (listed)
4. technical/routes.py (listed)
5. stock_ratings_api.py (listed)
6. advanced_analysis_api.py (listed)
7. wencai.py (listed)
8. announcement/routes.py (listed)
9. signal_monitoring/signal_history_response.py (listed)
10. data_quality.py (**NOT LISTED**)
11. pool_monitoring.py (**NOT LISTED**)
12. multi_source.py (**NOT LISTED**)
13. tdx.py (**NOT LISTED**)
14. dashboard.py (**NOT LISTED**)
15. advanced_analysis.py (**NOT LISTED**)
16. tasks.py (**NOT LISTED**)
17. backup_recovery_secure/cleanup_old_backups.py (**NOT LISTED**)
18. algorithms/get_algorithms_module.py (**NOT LISTED**)
19. market/health_check.py (**NOT LISTED**)
20. strategy_mgmt.py (**NOT LISTED**)
21. risk_v31/system.py (**NOT LISTED**)

## Findings

### Critical

| # | Section | Issue | Evidence | Recommendation |
|---|---------|-------|----------|----------------|
| 1 | §1.2 | Lists 9 scattered health endpoints; actual is 21. 13 endpoints are invisible in this document. | grep result above | Add all 13 missing files to §1.2 table and §3.2 deletion plan; revise §4 Step 1 from "1 day" to "2 days" |

### Medium

| # | Section | Issue | Evidence | Recommendation |
|---|---------|-------|----------|----------------|
| 2 | §二.3 | STANDARDS.md requires `/health/ready` but implementation uses `/health/readiness` — correctly noted but no fix proposed | Naming mismatch acknowledged | Propose either renaming the endpoint or updating STANDARDS.md |
| 3 | §3.3 | `check_module_health()` proposed without implementation detail | No specification of how module health is determined | Specify: registry pattern, per-module `health_check()` method, or simple import verification |

## Scoring

| Dimension | Score (1-5) |
|-----------|-------------|
| Technical Accuracy | 2 |
| Completeness | 2 |
| Codebase Alignment | 2 |
| Actionability | 3 |
| **Overall** | **2.3** |

## Verdict

**NEEDS_REVISION** — 13 of 21 scattered health endpoints are missing from this document. The consolidation plan cannot succeed with incomplete scope.
