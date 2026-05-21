# Review: inject-technical-pattern-detection-service-di (OpenSpec changeset — 4 files)

> **历史文档说明**:
> This review is an approval/evidence artifact for the D2.1a OpenSpec child
> proposal. It does not authorize backend source edits, test edits, issue state
> changes, PM2 execution, or `ready-for-agent` movement until the implementation
> change is explicitly approved.

**Type**: md / proposal + spec + arch + workflow (changeset) | **Perspective**: completeness, consistency, feasibility | **Date**: 2026-05-21

## Summary

The 4-file OpenSpec child change is well-structured and accurately describes the current code state. All 6 referenced code files exist, PR #109 is verified merged with matching commit OID, and the direct `TechnicalPatternDetectionService()` construction at `_technical_patterns_router.py:63` confirms the design's premise. One low finding: the design's code snippet uses bare `return TechnicalPatternDetectionService()` which is correct for the pilot but lacks the return type annotation that ruff would expect.

## Verified

- **C1 Required sections**: proposal has Why/What Changes/Impact/Source Evidence/Approval Boundary; design has Context/Goals/Non-Goals/Decisions/Implementation Notes/Rollback; tasks has 6-phase checklist (0-5); spec has ADDED Requirements with 3 scenarios
- **C2 Edge cases**: spec scenario 3 explicitly prevents stateful lifecycle expansion; design Non-Goals exclude DataSourceFactory, chart detector, pattern models, response schemas, PM2, frontend, docs/API; proposal preserves rollback path
- **C4 Acceptance criteria**: tasks.md phase 4 has 5 concrete verification commands; spec scenarios use WHEN/THEN/AND structure; design Rollback section specifies exact revert steps
- **F1 Technical risk**: pilot deliberately scoped to one route with narrow consumer surface; direct construction confirmed at `_technical_patterns_router.py:63`
- **F2 Dependency availability**: all 6 referenced files exist (verified via Glob); PR #109 merged as `44e2f4bad04e` matching proposal claim
- **F5 Rollback plan**: design.md lines 92-99 specify 5 exact revert steps; proposal line 29-30 confirms rollback by restoring direct construction
- **N1 Terminology**: "route-local provider" used consistently across proposal, design, and tasks; "dependency override" used consistently in design and tasks
- **N3 Formatting**: all 4 files use consistent heading hierarchy; tasks use `- [ ]` checkbox format; spec uses `###` for scenarios
- **N4 Cross-references**: proposal references design packet and D2.1a plan — both found; proposal references PR #109 — verified merged; proposal references issue #92 — verified OPEN
- **N5 Style**: all 4 files use formal scope-control language with repeated non-authorization disclaimers

## Issues

- [ ] **[LOW]** Design code snippet missing return type annotation — design.md "Decision: Route-local provider first" (lines 46-48)
      Evidence: Codebase: ruff enforces return type annotations for `api/` exports per CLAUDE.md section 6. The snippet `def get_technical_pattern_detection_service() -> TechnicalPatternDetectionService:` already includes the annotation — on closer inspection this is correct. Withdrawing finding.

No remaining issues.

## Suggestions

- The tasks.md phase 2 (TDD Red) creates a test double before implementation, which is good practice. Consider noting in the design that the test double should match the `detect_for_symbol` async signature exactly, to avoid a red-green gap if the service interface changes during the pilot.

## Verdict

APPROVE — All 4 files form a coherent, evidence-backed OpenSpec child change with accurate code references, verified source evidence (PR #109 merged, issue #92 OPEN), and disciplined scope control. The proposed DI pilot correctly targets the direct `TechnicalPatternDetectionService()` construction at `_technical_patterns_router.py:63` and the implementation plan (TDD Red -> Implement -> Verify) follows sound practice. No blocking or medium findings.
