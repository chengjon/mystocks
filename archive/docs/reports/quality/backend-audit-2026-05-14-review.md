# Review: backend-audit-2026-05-14.md

**Type**: `.md` / `plan` | **Perspective**: completeness + consistency | **Date**: 2026-05-14 | **Reviewer**: Claude

---

## Executive Summary

This main audit report provides a comprehensive assessment of the MyStocks backend against STANDARDS.md. The analysis structure is sound, covering red-line compliance, architecture layering, migration debt, and best-practice deviations. However, it contains **two significant factual errors** — the scattered health endpoint count is 21 (not 9), and a referenced core validation file does not exist — and several understated scope items that undermine the priority planning.

## Document Metadata

| Field | Value |
|-------|-------|
| Source | `docs/reports/quality/backend-audit-2026-05-14.md` |
| File Type | `.md` |
| Doc Type | `plan` (audit report with prioritized action plan) |
| Sections | 8 |
| Referenced Files | 40+ |
| Referenced Symbols | 0 |

## Evidence Verification

### Files Referenced

| File | Exists? | Location |
|------|---------|----------|
| `app/core/logger.py` | no | Does not exist — confirmed claim |
| `app/core/responses.py` | yes | `web/backend/app/core/responses.py` |
| `app/core/exceptions.py` | yes | `web/backend/app/core/exceptions.py` |
| `app/core/exception_handler.py` | yes | `web/backend/app/core/exception_handler.py` |
| `app/core/exception_handlers.py` | yes | `web/backend/app/core/exception_handlers.py` |
| `app/core/global_exception_handlers.py` | yes | `web/backend/app/core/global_exception_handlers.py` |
| `app/core/validation.py` | yes | `web/backend/app/core/validation.py` |
| `app/core/validators.py` | yes | `web/backend/app/core/validators.py` |
| `app/core/validation_messages.py` | yes | `web/backend/app/core/validation_messages.py` |
| `app/core/validation_models.py` | **no** | Does NOT exist in core/ — exists in `app/schema/validation_models.py` |
| `app/api/VERSION_MAPPING.py` | yes | `web/backend/app/api/VERSION_MAPPING.py` |
| `app/api/health.py` | yes | `web/backend/app/api/health.py` |
| `app/api/monitoring_old/` | yes | 2 files: `__init__.py` + `routes.py` |
| `app/schema/` | yes | 2 files: `__init__.py` + `validation_models.py` |
| `app/schemas/` | yes | 18 files |
| `app/router_registry.py` | yes | `web/backend/app/router_registry.py` (5.0K) |
| `api/strategy_management.py.backup` | **yes** | 28.5K — **exists contrary to sub-document B's claim** |
| `api/risk_management.py.bak` | **yes** | 74.6K — **exists contrary to sub-document B's claim** |
| `api/data_source_config.py.backup` | **yes** | 22.0K |
| `api/mystocks_complete.py.bak` | **yes** | 47.9K |
| `api/auth_compat.py` | yes | Functional compat shim |

### Claims Verified

| Claim | Status | Evidence |
|-------|--------|----------|
| "`app/core/logger.py` does not exist" | **confirmed** | `ls` returns not found |
| "30+ print() calls in mock/coverage_report.py" | **exaggerated** | Actual: 17 `print()` lines in that file |
| "monitoring_old/ old module directory exists" | **confirmed** | 2 files confirmed |
| "schema/ + schemas/ dual directories" | **confirmed** | schema/ (2 files) + schemas/ (18 files) |
| "60+ files in app/core/" | **confirmed** | 69 entries total; 65 .py files + 3 subdirs + __pycache__ |
| "20+ files using global singleton" | **confirmed** | 142 `global _` occurrences across backend |
| "structlog vs logging split" | **confirmed** | 170 structlog uses, 166 logging.getLogger uses |

## Checklist Results

### Completeness

| # | Check | Result | Notes |
|---|-------|--------|-------|
| C1 | Required sections | PASS | 8 sections covering assessment, compliance, layers, migration, best practices, positives, priorities, function tree |
| C2 | Edge cases | FAIL | Health endpoint fragmentation is 21 endpoints, not 9 — §5.5 significantly understates the problem |
| C3 | Implicit assumptions | FAIL | Assumes `validation_models.py` is in core/ but it's actually in `schema/` — §三 validation trio is wrong |
| C4 | Acceptance criteria | PASS | Each priority item has a clear action and impact scope |
| C5 | Missing roles/stakeholders | FAIL | No mention of `websocket_stability_manager.py` (20.7K) in core/ assessment |

### Consistency

| # | Check | Result | Notes |
|---|-------|--------|-------|
| N1 | Terminology | PASS | Consistent Chinese/English usage |
| N2 | Naming conventions | FAIL | §三 lists `validation_models.py` as a core validation file but it lives in `schema/` |
| N3 | Formatting | PASS | Markdown tables and headers used consistently |
| N4 | Cross-references | FAIL | Sub-document numbering skips D (A,B,C,E,F,G,H,I) — no explanation |
| N5 | Style consistency | PASS | Formal audit report style maintained |

## Findings

### Critical Issues

| # | Section | Issue | Impact | Evidence | Recommendation |
|---|---------|-------|--------|----------|----------------|
| 1 | §5.5 | Lists 9 scattered health endpoints; actual count is **21** | HIGH — more than half the problem is invisible, leading to incomplete cleanup plan | `grep -rn '"/health"' web/backend/app/api/ --include="*.py" \| grep -v health.py` returns 21 endpoints including data_quality.py, pool_monitoring.py, multi_source.py, tdx.py, dashboard.py, tasks.py, backup_recovery_secure/, algorithms/, market/health_check.py, strategy_mgmt.py, advanced_analysis.py, risk_v31/system.py | Update count to 21 and add the 13 missing files to the health endpoint consolidation plan (sub-document G) |
| 2 | §三 | Lists `validation_models.py` as one of 3 core validation files alongside `validation.py` and `validators.py` | HIGH — wrong file referenced; `validation_models.py` lives in `schema/` not `core/`. The actual third core validation file is `validation_messages.py` | `ls web/backend/app/core/validation_models.py` fails; `ls web/backend/app/core/validation_messages.py` succeeds (8.4K) | Correct the file reference to `validation_messages.py` and verify all sub-documents that inherit this claim |

### Medium Issues

| # | Section | Issue | Impact | Evidence | Recommendation |
|---|---------|-------|--------|----------|----------------|
| 3 | §2.2 | Claims "30+ print() calls" in `mock/coverage_report.py`; actual count is ~17 | MED — exaggerates violation severity, undermines credibility | `grep -rn "print(" web/backend/app/mock/coverage_report.py \| wc -l` = 17 | Correct to "~17" |
| 4 | §三 | States "60+ files 全平铺" but core/ already has 3 subdirectories (cache/, logging/, middleware/) | MED — "全部平铺" is misleading since subdirectories exist | `ls web/backend/app/core/` shows cache/, logging/, middleware/ subdirs | Correct to "60+ files, mostly flat with 3 existing subdirectories" |
| 5 | §三 | Does not mention `websocket_stability_manager.py` (20.7K) or `_socketio_manager_singleton.py` (718B) in core | MED — significant files omitted from assessment | `ls web/backend/app/core/websocket_stability_manager.py` = 20.7K | Add to core assessment |
| 6 | §四 | Sub-document letter sequence skips D (A, B, C, then E, F, G, H, I) | MED — confusing gap in document numbering | Document §七 references sub-documents by letter | Add explanation for missing D or renumber |
| 7 | §八 | FUNCTION_TREE.md comparison table claims domain 07 "高级分析与AI" is "50% 实验性质" but no evidence provided | MED — unsubstantiated percentage | No cross-reference verification possible within this document's scope | Add evidence or remove the percentage |

### Low Issues

| # | Section | Issue | Evidence | Recommendation |
|---|---------|-------|----------|----------------|
| 8 | §2.4 | Lists `auth_compat.py` as residual but notes it's "功能性兼容 shim" — contradicts its placement in the residual/deprecated table | File exists and is functional | Move to a separate "compat shims to evaluate" category |
| 9 | §四 | No mention of `market_v2.py` flat file in market data migration status | Listed in §四 table but not discussed in detail | Add to sub-document C's scope |

## Strengths

- Comprehensive 8-section structure covering compliance, architecture, migration debt, and best practices
- Positive findings section (§六) balances the audit with deserved credit for VERSION_MAPPING, health probes, Request ID tracing, Prometheus metrics
- Priority classification into immediate/short-term/long-term is actionable
- FUNCTION_TREE.md domain mapping (§八) provides useful business-context alignment

## Scoring

| Dimension | Score (1-5) | Evidence |
|-----------|-------------|----------|
| Technical Accuracy | 3 | Health endpoint count 2.3x understated; wrong validation filename; print count inflated |
| Completeness | 3 | Missing core files, incomplete health endpoint inventory |
| Codebase Alignment | 3 | Most file references correct but 2 critical errors and several omissions |
| Actionability | 4 | Clear priority table with action items and impact scopes |
| Terminology Consistency | 4 | Consistent terminology with one filename error |
| **Overall** | **3.4** | |

## Verdict

**NEEDS_REVISION**

Two critical factual errors must be corrected before this document can be trusted as a basis for action: (1) the health endpoint fragmentation is 21 endpoints, not 9 — the sub-document G inherits this undercount and will leave 13 endpoints unconsolidated; (2) `validation_models.py` is not in core/ — all sub-documents (especially F) that inherit this reference need correction. After fixing these, the audit would be APPROVE_WITH_NOTES.
