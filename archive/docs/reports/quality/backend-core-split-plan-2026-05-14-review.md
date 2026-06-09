# Review: backend-core-split-plan-2026-05-14.md

**Type**: `.md` / `plan` | **Perspective**: completeness + consistency | **Date**: 2026-05-14 | **Reviewer**: Claude

## Executive Summary

Comprehensive 13-domain categorization of 65 core/ files with detailed merge and migration plans. However, references `validation_models.py` (which doesn't exist in core/), misses `websocket_stability_manager.py` (20.7K), and proposes moving `config.py` to `boot/settings.py` which would create confusing import duality.

## Evidence Verification

| Claim | Status | Evidence |
|-------|--------|----------|
| "68 files + 3 subdirectories" | **contradicted** | Actual: 65 .py files + 3 subdirs (cache/, logging/, middleware/) + __pycache__ = 69 entries |
| `validation_models.py` in core validation trio | **contradicted** | Does NOT exist in core/; `validation_messages.py` does (8.4K). `validation_models.py` is in `schema/` |
| §一 tree completeness | **incomplete** | Missing `websocket_stability_manager.py` (20.7K) from listing |
| File sizes for validation merge | **understated** | Claims validation.py ~150 lines (actual ~200+) and validators.py ~120 lines (actual ~350+) |

## Findings

### Critical

| # | Section | Issue | Evidence | Recommendation |
|---|---------|-------|----------|----------------|
| 1 | §二, §四.2 | References `validation_models.py` as a core validation file — file does NOT exist in core/. The actual file is `validation_messages.py`. | `ls web/backend/app/core/validation_models.py` fails; `validation_messages.py` exists (8.4K) | Replace all references to `validation_models.py` with `validation_messages.py` |

### Medium

| # | Section | Issue | Evidence | Recommendation |
|---|---------|-------|----------|----------------|
| 2 | §一, §二 | Missing `websocket_stability_manager.py` (20.7K) from categorization and migration plan | File exists in core/ | Add to WebSocket/Socket.IO domain (category 4) |
| 3 | §三 | Proposes moving `config.py` to `boot/settings.py` — creates import duality since `from app.core.config import settings` is used everywhere | Re-export helps but canonical path confusion remains | Keep `config.py` at core/ top level; only move files with clear functional boundaries |
| 4 | §三 | Proposed merged `routes.py` for strategy domain would be 1500+ lines, violating STANDARDS.md 800-line limit | strategy.py (741 lines) + strategy_mgmt.py (862 lines) = 1603 lines merged | Split into multiple route files within the package |

## Scoring

| Dimension | Score (1-5) |
|-----------|-------------|
| Technical Accuracy | 2 |
| Completeness | 3 |
| Codebase Alignment | 3 |
| Actionability | 3 |
| **Overall** | **2.8** |

## Verdict

**NEEDS_REVISION** — Wrong filename (`validation_models.py`), missing file (`websocket_stability_manager.py`), and questionable `config.py` relocation. After corrections, this would be APPROVE_WITH_NOTES.
