# Review: backend-singleton-to-di-2026-05-14.md

**Type**: `.md` / `plan` | **Perspective**: completeness + feasibility | **Date**: 2026-05-14 | **Reviewer**: Claude

## Executive Summary

Thorough analysis of 41 singleton instances across 30+ modules with a practical migration template. The phased approach is well-structured, but the opening "32 modules" claim is inconsistent with the 41-entry detailed table, and the FastAPI lifespan API usage is outdated for the project's FastAPI 0.114+ version.

## Evidence Verification

| Claim | Status | Evidence |
|-------|--------|----------|
| "32 modules using global singleton" | partially correct | 142 `global _` occurrences; ~30 unique files with singletons; 41 instances listed in detailed table |
| Services layer has 12 singletons | confirmed | Table lists AnnouncementService, EmailService, BacktestEngine, etc. |
| Core layer has 8 singletons | confirmed | CacheManager, AsyncCacheManager, DB singletons |
| Adapters layer has 5 singletons | confirmed | cninfo, eastmoney, eastmoney_enhanced, akshare_extension, tqlex |

## Findings

### Medium

| # | Section | Issue | Evidence | Recommendation |
|---|---------|-------|----------|----------------|
| 1 | §一 | Header says "32 modules" but table lists 41 instances (#1-#41). Misleading — should say "30+ modules, 41 instances" | Table has entries up to #41 | Correct the count |
| 2 | §三.2 | Uses deprecated `@app.on_event("startup")` — FastAPI 0.114+ uses lifespan context managers | Project uses FastAPI 0.114+ per CLAUDE.md | Replace with `async with lifespan(app):` pattern |
| 3 | §六 | Verification says `grep -c "global _" ... <= 0` as final target — unrealistic for phased migration; no per-phase targets | Single binary target | Add per-phase targets (e.g., Phase 1: reduce from 142 to ~120) |

### Low

| # | Section | Issue | Recommendation |
|---|---------|-------|----------------|
| 4 | §五 | No discussion of coexistence period where both `global` singletons and `Depends()` factories exist | Add transition guidance |

## Scoring

| Dimension | Score (1-5) |
|-----------|-------------|
| Technical Accuracy | 3 |
| Completeness | 3 |
| Codebase Alignment | 4 |
| Actionability | 4 |
| **Overall** | **3.5** |

## Verdict

**APPROVE_WITH_NOTES** — Migration template is valuable. Fix the module count, update the FastAPI lifespan API, and add per-phase verification targets.
