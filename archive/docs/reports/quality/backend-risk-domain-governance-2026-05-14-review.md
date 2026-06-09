# Review: backend-risk-domain-governance-2026-05-14.md

**Type**: `.md` / `plan` | **Perspective**: completeness + consistency | **Date**: 2026-05-14 | **Reviewer**: Claude

## Executive Summary

Identifies the risk domain's multi-entry-point problem correctly, but the package structure descriptions are completely wrong — both `risk/` and `risk_v31/` are shown as 2-file packages when they actually contain 6 and 4 files respectively. The proposed single `routes.py` target is unrealistic given the actual package sizes.

## Evidence Verification

| Claim | Status | Evidence |
|-------|--------|----------|
| risk_management.py exists | confirmed | 992B (likely a shim) |
| risk_management_core.py exists | confirmed | 5.9K |
| risk_management_v31.py exists | confirmed | 671B (likely a shim) |
| risk/ = __init__.py + routes.py | **CONTRADICTED** | Actual: __init__.py + _shared.py (6.5K) + alerts.py (34.3K) + metrics.py (23.4K) + stop_loss.py (22.2K) + v31.py (16.2K) = 6 files |
| risk_v31/ = __init__.py + routes.py | **CONTRADICTED** | Actual: __init__.py + alerts.py (4.5K) + stop_loss.py (5.0K) + system.py (1.9K) = 4 files |
| 3 service versions | confirmed | risk_management_new.py, risk_management_2.py, risk_management/ package (6 files) |

## Findings

### Critical

| # | Section | Issue | Evidence | Recommendation |
|---|---------|-------|----------|----------------|
| 1 | §1.1 | risk/ package structure completely wrong — shows 2 files, actual is 6 files totaling 100K+ | `ls web/backend/app/api/risk/` shows 6 files | Correct the tree listing; reassess merge complexity given actual package size |
| 2 | §1.1 | risk_v31/ package structure wrong — shows 2 files, actual is 4 files | `ls web/backend/app/api/risk_v31/` shows 4 files | Correct the tree listing |

### Medium

| # | Section | Issue | Evidence | Recommendation |
|---|---------|-------|----------|----------------|
| 3 | §1.1 | risk_management.py (992B) and risk_management_v31.py (671B) are very small — likely shims, not "完整 API" | Tiny file sizes suggest re-export shims | Verify content before classifying as "complete implementations" |
| 4 | §三 | Proposes single `risk/routes.py` — but risk/ already has 5 content files totaling 100K+. A single routes.py would be enormous | alerts.py alone is 34.3K | Keep the existing multi-file package structure; merge flat files INTO the existing package |
| 5 | §一 | Service layer table shows `risk_management/` as "..." without listing its 6 well-organized files | risk_alerts.py, risk_base.py, risk_calculator.py, risk_dashboard.py, risk_monitoring.py, risk_settings.py | Document the existing canonical service structure |
| 6 | §五 | Delete list includes `api/risk_v31/` but doesn't note risk_v31/system.py has a `/health` endpoint needing migration | grep found health endpoint in risk_v31/system.py | Add health endpoint migration as a prerequisite |

## Scoring

| Dimension | Score (1-5) |
|-----------|-------------|
| Technical Accuracy | 2 |
| Completeness | 2 |
| Codebase Alignment | 2 |
| Actionability | 3 |
| **Overall** | **2.3** |

## Verdict

**NEEDS_REVISION** — The package structures for both risk/ and risk_v31/ are factually wrong, making the migration plan's scope and complexity assessment unreliable. After correcting the file listings, the proposed single-file target should be abandoned in favor of the existing multi-file package pattern.
