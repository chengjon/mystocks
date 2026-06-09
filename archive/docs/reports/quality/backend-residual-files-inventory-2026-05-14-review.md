# Review: backend-residual-files-inventory-2026-05-14.md

**Type**: `.md` / `plan` | **Perspective**: completeness + consistency | **Date**: 2026-05-14 | **Reviewer**: Claude

## Executive Summary

This residual file inventory is thorough in listing backup and transitional files, but contains a **critical factual reversal** in section 4: it falsely claims 3 large backup files don't exist when they actually do, and understates the part-file count by one.

## Evidence Verification

### Claims Verified

| Claim | Status | Evidence |
|-------|--------|----------|
| 4 backup files in services/ | confirmed | All 4 exist: .bak2 (24.7K), .bak3 (23.8K), .before_schema_update (24.7K), .backup.20260130 (76.7K) |
| data_source_config.old.py + .backup | confirmed | Both exist (20.8K, 22.0K) |
| monitoring_old/ with 2 files | confirmed | __init__.py + routes.py |
| 4 _new.py files | confirmed | data_adapter_new.py (6.2K), data_api_new.py in services/ (940B), data_api_new.py in api/data/ (10.9K), risk_management_new.py (8.7K) |
| part1/part2/part3 files | **partially contradicted** | 6 files exist (not 5): algorithm repo has part1+2+3, market_data_service has part1+2+3 |
| "api/strategy_management.py.backup does not exist" | **CONTRADICTED** | File exists at 28.5K |
| "api/risk_management.py.bak does not exist" | **CONTRADICTED** | File exists at 74.6K |
| "api/mystocks_complete.py.bak does not exist" | **CONTRADICTED** | File exists at 47.9K |

## Findings

### Critical

| # | Section | Issue | Evidence | Recommendation |
|---|---------|-------|----------|----------------|
| 1 | §四 | Claims 3 backup files "do not exist" and "corrects" the main audit — but all 3 DO exist (strategy_management.py.backup 28.5K, risk_management.py.bak 74.6K, mystocks_complete.py.bak 47.9K). This adds 3 files to the cleanup scope and reverses the document's own conclusion. | `ls` confirms all 3 exist | Delete entire §四; add these 3 files to §二.1 immediate-delete list; update statistics from "6 files" to "9 files" |

### Medium

| # | Section | Issue | Evidence | Recommendation |
|---|---------|-------|----------|----------------|
| 2 | §2.5 | Claims 5 part files; actual is 6 — market_data_service has part3.py (1.3K) that's missing from the list | `ls .../market_data_service_methods/part*.py` shows part1+2+3 | Add part3.py to the list |
| 3 | §二.3 | Claims data_api_new.py exists in both locations as "duplicate" — but services/ version is only 940B (likely a re-export shim), not a real duplicate of the 10.9K api/data/ version | File size discrepancy | Clarify that the services/ version is a shim, not a full duplicate |

## Scoring

| Dimension | Score (1-5) |
|-----------|-------------|
| Technical Accuracy | 2 |
| Completeness | 3 |
| Codebase Alignment | 2 |
| Actionability | 4 |
| **Overall** | **2.8** |

## Verdict

**NEEDS_REVISION** — §四's false negations are a critical error that hides 150K+ of backup files from the cleanup plan.
