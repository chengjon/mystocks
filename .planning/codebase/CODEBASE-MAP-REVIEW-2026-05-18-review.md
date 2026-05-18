# Review: CODEBASE-MAP-REVIEW-2026-05-18.md

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

**Type**: md / proposal (audit/review) | **Perspective**: completeness + consistency + feasibility + architecture | **Date**: 2026-05-18 | **Reviewer**: Claude

**Disposition**: Findings were absorbed into `.planning/codebase/CODEBASE-MAP-REVIEW-2026-05-18.md` in commit `19ca5521ad5cf03980388261efddd422f78eafa8` (`docs(codebase): incorporate review corrections`). This review remains a peer review artifact for the pre-correction snapshot and should not be read as an open issue list.

---

## Executive Summary

该报告是一份高质量的全仓库基线快照，在架构 seam 识别、迁移残留分类和 OpenSpec 发布对齐方面做了大量工作。所有 52 个 L1 文件引用和 12 个 L2 文档引用均存在。主要问题集中在两处事实性偏差（`*_new.py` 数量和 HEAD 时效性），以及 `spec_from_file_location` 反向加载的范围描述不完整。整体而言，报告作为 issue 15 输入基线的定位清晰、证据链可复核，判定为 **APPROVE_WITH_NOTES**。

## Document Metadata

| Field | Value |
|-------|-------|
| Source | `.planning/codebase/CODEBASE-MAP-REVIEW-2026-05-18.md` |
| File Type | .md |
| Doc Type | proposal (audit/review) |
| Sections | 10 + 2 appendices |
| Referenced Files | 52 found / 0 missing |
| Referenced Symbols | 18 found / 0 missing |
| Source Lines | 708 |

## Evidence Verification

### Files Referenced (PASS — all 52 exist)

抽样关键文件验证结果：

| File | Exists? | Location |
|------|---------|----------|
| `web/backend/app/core/config.py` | yes | confirmed |
| `web/backend/app/main.py` | yes | confirmed |
| `web/backend/app/app_factory.py` | yes | confirmed |
| `web/backend/app/services/__init__.py` | yes | confirmed |
| `web/backend/app/services/data_api_new.py` | yes | confirmed |
| `web/backend/app/api/data/data_api_new.py` | yes | confirmed |
| `web/backend/app/services/risk_management_new.py` | yes | confirmed |
| `web/backend/app/services/risk_management_2.py` | yes | confirmed |
| `web/backend/app/services/data_adapter_new.py` | yes | confirmed |
| `web/backend/app/schema/validation_models.py` | yes | confirmed |
| `architecture/STANDARDS.md` | yes | confirmed |
| `architecture/DOMAIN_BOUNDARIES.md` | yes | confirmed |
| `docs/reports/quality/generated/backend-fullpath-route-table.json` | yes | confirmed |
| `docs/reports/quality/backend-health-status-implementation-boundary-2026-05-18.md` | yes | confirmed |
| `docs/reports/quality/backend-health-status-openapi-stabilization-2026-05-18.md` | yes | confirmed |
| `docs/reports/quality/backend-health-status-residual-blockers-2026-05-18.md` | yes | confirmed |

其余 36 个文件引用（配置文件、目录、证据文档）均已验证存在。

### Functions/Classes Referenced

| Symbol | Found? | Location |
|--------|--------|----------|
| `CSRFTokenManager` (main.py) | yes | `web/backend/app/main.py:67` |
| `CSRFTokenManager` (app_factory.py) | yes | `web/backend/app/app_factory.py:103` |
| `IntegratedServices` | yes | `web/backend/app/services/__init__.py:16` |
| `DataApiService` | yes | `web/backend/app/api/data/data_api_new.py:17` |
| `spec_from_file_location` | yes | 5 files in `web/backend/app/services/` |
| `csrf_manager` (main.py) | yes | confirmed via Grep |
| `csrf_manager` (app_factory.py) | yes | confirmed via Grep |

### Claims Verified

| Claim | Status | Evidence |
|-------|--------|----------|
| `pytest.ini` cov-fail-under=30 | confirmed | `pytest.ini:33` shows `--cov-fail-under=30` |
| `pyproject.toml` cov-fail-under=80 | confirmed | `pyproject.toml:92` shows `"--cov-fail-under=80"` |
| HTTPException=100, files=6 at HEAD `dc21371ba` | confirmed at that HEAD | Grep shows 100 across 6 files; current HEAD `8cd5097d0` also shows 100 |
| 12 frontend backup files | confirmed | 4 `.bak` + 7 `.backup` + 1 `.backup.20260130` (matches "含 .backup." criterion in appendix) |
| `web/backend/src/` is symlink to `src/` | confirmed | `web/backend/src -> /opt/claude/mystocks_spec/src` |
| 10 non-test composables | confirmed | Glob found 10 `.ts` files in `views/composables/` |
| 6 flat/package coexistence domains | confirmed | algorithms, backup_recovery_secure, indicators, signal_monitoring, stock_search, system — all verified |
| `src/README.md` claims "64+" files | confirmed stale | `src/README.md:127` contains the outdated count |
| `architecture/INDEX.md` last updated 2026-02-02 | confirmed | Line 10: `最后更新: 2026-02-02 22:10:38` |
| `*_new.py` in backend = 5 | **contradicted** | Only 4 found: `api/data/data_api_new.py`, `services/data_api_new.py`, `services/data_adapter_new.py`, `services/risk_management_new.py` |
| STANDARDS.md version = v3.1 | confirmed | Line 1: `V3.1` |
| HEAD `dc21371ba` exists | confirmed | Commit exists: `refactor(api): migrate HTTPException to BusinessException (batch 3)` |
| ruff target-version=py39 | confirmed | `pyproject.toml:143` shows `target-version = ['py39']` |

## Checklist Results

22 items PASS. FAIL/N/A rows below:

| # | Check | Result | Notes |
|---|-------|--------|-------|
| A8 | Implementation surface precision | FAIL | `*_new.py` count overstated (5 vs actual 4); `spec_from_file_location` pattern scope under-specified (doc mentions 1 file, actual is 5) |
| A9 | Named entities verified | FAIL | `*_new.py` count "backend 仍有 5 个" is factually incorrect — verified 4 via Glob |
| C1 | Required sections | PASS | All expected sections present |
| C2 | Edge cases | FAIL | Does not address `spec_from_file_location` pattern's full scope (5 files, not 1); `risk_management_2.py` mentioned in table but not in `_new.py` count |
| C3 | Implicit assumptions | FAIL | Document assumes HEAD `dc21371ba` is current; actual HEAD is `8cd5097d0` (one commit ahead). Artifact freshness guard section mentions this pattern but does not call out the specific HEAD advance |
| C4 | Acceptance criteria | PASS | Clear adoption review record with authorization boundary |
| N4 | Cross-references | FAIL | Section 9 comparison table row "backend 仍有 5 个" references a count that doesn't match live codebase |
| F1 | Technical risk | PASS | Key risks identified per concern with priority |
| F3 | Timeline realism | N/A | Document explicitly states it does not authorize implementation, so timeline estimates are not applicable |

## Findings

### Medium Issues

| # | Section | Issue | Impact | Evidence | Recommendation |
|---|---------|-------|--------|----------|----------------|
| 1 | Section 9, comparison table, row `*_new.py` | `*_new.py` count in backend stated as 5, actual is 4 | Undermines numeric claim credibility; consumers may search for a phantom 5th file | Glob `web/backend/**/*_new.py` returns: `api/data/data_api_new.py`, `services/data_api_new.py`, `services/data_adapter_new.py`, `services/risk_management_new.py` = 4 files. Searched full `web/backend/` tree. | Correct to "4 个" or expand search scope and document it |
| 2 | Section 8, P1 #1, table row `data_api_new.py` | `spec_from_file_location()` reverse-loading pattern described for 1 file, but affects 5 service files | Incomplete scope description may cause incomplete remediation plan | Grep found `spec_from_file_location` in: `market_api.py`, `trading_api.py`, `data_api_new.py`, `technical_pattern_detection_service.py`, `analysis_api.py` — all under `web/backend/app/services/` | Expand the P1 #1 table to list all 5 files using this pattern, or add a footnote noting the full scope |
| 3 | Throughout (artifact freshness) | Document references HEAD `dc21371ba` throughout; current HEAD is `8cd5097d0` (batch 4 exception migration) | Readers may treat stale HEAD data as current; the freshness guard section (line 375) describes the pattern but does not flag the specific HEAD advance | `git log --oneline -1 HEAD` = `8cd5097d0`; document consistently uses `dc21371ba`. HTTPException count happens to still be 100, but this is coincidence | Add a line in artifact freshness guard noting `8cd5097d0` is now HEAD; verify whether the batch 4 commit changed any of the cited counts |

### Low Issues

| # | Section | Issue | Evidence | Recommendation |
|---|---------|-------|----------|----------------|
| 4 | Section 3, Python table | `mock/` listed as 43 files / 6,912 lines, but appendix B says mock count "66 → 43" is due to different counting criteria | Document acknowledges the discrepancy but does not specify what the two criteria are | Add a one-line note defining the counting criteria (e.g., "43 = files directly in `src/mock/`; 66 = all mock-related files across `src/`") |
| 5 | Section 4, Health row | `/health/readiness` described as "intentionally absent" but no rationale given | Lines 211, 225 | Add brief rationale for intentional absence (e.g., readiness probe uses `/health/ready` instead) |

## Strengths

- **Evidence chain discipline**: Every concern includes specific file paths, line references, and HEAD-anchored counts. The artifact freshness guard pattern (line 375) is a strong practice.
- **Authorization boundary clarity**: The document explicitly states what it does NOT authorize (code changes, issue creation, OpenSpec proposals). The adoption review record (line 621) is thorough.
- **Scope precision on F821**: Correctly identifies that "F821=0" was previously reported without scope qualification, and provides per-scope breakdown (src=0, tests=291, scripts=240, web/backend/app=61).
- **Architectural prioritization**: Reordering from quality/hygiene-first to service seam/API migration/CSRF/schema-first (per Matt Pocock methodology) adds genuine analytical value.
- **Orphan classification**: Three-way classification (scanner-reported / false-positive-by-import-chain / actual-deletion-candidate) prevents the common error of treating scanner output as deletion authorization.
- **Migration closure evidence criteria**: The 9-field closure record template (line 411-423) provides an actionable, verifiable standard for future API migration work.

## Recommendations

1. **Correct `*_new.py` count** from 5 to 4, or if the 5th file exists outside `web/backend/`, document the expanded search scope.
2. **Expand `spec_from_file_location` scope** in P1 #1 to list all 5 affected service files (`market_api.py`, `trading_api.py`, `data_api_new.py`, `technical_pattern_detection_service.py`, `analysis_api.py`), not just `data_api_new.py`.
3. **Update artifact freshness guard** to note that HEAD has advanced to `8cd5097d0` since the report's live counts were captured, and verify whether batch 4 exception migration altered any cited metrics.
4. **Define mock counting criteria** in a one-line footnote for the 43 vs 66 discrepancy.
5. **Add readiness-absence rationale** for the `/health/readiness` intentional absence.

## Scoring

| Dimension | Score (1-5) | Evidence |
|-----------|-------------|----------|
| Technical Accuracy | 4 | HTTPException count, F821 scope split, pytest config conflict all verified; `*_new.py` count off by 1 |
| Completeness | 4 | 10 sections + 2 appendices covering stack, architecture, structure, testing, concerns, changes; `spec_from_file_location` scope incomplete |
| Codebase Alignment | 5 | All 52 file refs and 18 symbol refs verified against live codebase; 6 flat/package domains confirmed |
| Actionability | 5 | Clear priority levels, authorization boundary, adoption record, closure evidence criteria template |
| Terminology Consistency | 4 | "canonical", "seam", "closure" used consistently; mock counting criteria undefined |
| **Overall** | **4.4** | Weighted: Feasibility 2x (4), Actionability 2x (5) |

## Verdict
**APPROVE_WITH_NOTES** — 报告作为 issue 15 输入基线的质量充分，证据链可复核。三处中等偏差（`*_new.py` 数量、`spec_from_file_location` 范围、HEAD 时效性）均为可快速修正的事实性问题，不影响架构 seam 识别和优先级判断的有效性。建议修正后再行替换旧 `.planning/codebase/` 文档。
