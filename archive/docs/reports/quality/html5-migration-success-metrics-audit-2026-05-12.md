# HTML5 Migration Success Metrics Audit

Date: 2026-05-12
Change: `implement-html5-migration-experience-optimization`
Task focus: Success Metrics & Validation
Scope: Desktop-only, repo-local audit only

## Decision

The Success Metrics section remains mixed by design.

This batch records the current status of success metrics without changing implementation or inflating validation claims. Some repo-local technical metrics are closed, several metrics remain open because the evidence is incomplete, and several aspirational or mobile/post-launch metrics are de-scoped under the current Desktop-only scope.

## Evidence Checked

Commands:

```bash
sed -n '735,970p' openspec/changes/implement-html5-migration-experience-optimization/tasks.md
rg -n "Success Metrics|Functional Validation|Performance Validation|User Experience Validation|Business Impact|^- \\[[ x]\\] ✅|Repo-truth|de-scope|blocker" openspec/changes/implement-html5-migration-experience-optimization/tasks.md
```

Observed repo facts:

- Closed repo-local metrics include the 7-domain menu truth, IndexedDB storage/retrieval, first-screen load time, and selected Desktop-only de-scope decisions.
- Open functional metrics remain for PWA install/offline correctness and Web Worker performance quantification.
- Open performance metrics remain for bundle size `<= 2.5MB`, full Lighthouse `90+` including PWA dimension, test coverage `>= 60%`, and Web Vitals target closure.
- Open user-experience metrics remain for PWA install success rate, offline core-scenario coverage, notification acceptance rate, and WCAG 2.1 AA closure.
- Business impact metrics such as retention improvement, mobile usage improvement, technical-debt reduction percentage, and developer-efficiency improvement are not repo-local completion claims under the current evidence model.

## Gap Summary

The current Success Metrics section is not a single pass/fail gate. It mixes:

- Repo-local technical validations with concrete commands.
- External or cross-browser acceptance tasks.
- Product/telemetry metrics that require post-launch measurement.
- Historical mobile goals that are out of scope for Desktop-only.
- Aspirational percentages without a current baseline.

The remaining open metrics should not be closed by writing more docs. They require either real measurement, a formal scope change, or actual implementation/validation work.

## Task Disposition

Keep the existing metric statuses as-is.

Future closure conditions:

- PWA/offline metrics require service-worker-controlled route matrices and install/offline evidence.
- Worker metrics require real worker orchestration and benchmark data.
- Bundle, Lighthouse, coverage, and Web Vitals metrics require fresh measurement meeting the stated target or an approved target revision.
- UX and business metrics require telemetry, rollout, user acceptance, or post-launch measurement records.
