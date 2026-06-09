# Frontend View Checklist: Non-ArtDeco Path-Level Delta

Date: 2026-05-11

Scope: exact-path reconciliation for non-ArtDeco files under `web/frontend/src/views/**` that were not individually named in prior checklist docs.

This document is a read-only coverage delta. It does not approve deletion, archive movement, test retirement, or style relocation.

## Scan Input

Command used:

```bash
python - <<'PY'
from pathlib import Path
root = Path('web/frontend/src/views')
docs = '\n'.join(p.read_text(errors='ignore') for p in Path('docs/reports/quality/myweb-audit').glob('frontend-view-checklist-*.md'))
files = []
for p in sorted(root.rglob('*')):
    if p.is_file():
        rel = str(p)
        short = str(p.relative_to(root))
        if 'artdeco-pages/' in short:
            continue
        if rel not in docs and f'src/views/{short}' not in docs and f'views/{short}' not in docs and short not in docs:
            files.append(short)
print(len(files))
for f in files:
    print(f)
PY
```

Result: 108 non-ArtDeco paths were not explicitly mentioned by exact path in existing checklist documents.

Interpretation: this is not a finding that 108 files are unreviewed. Most files are already covered by directory-level decisions. This delta records the exact-path grouping so later mutation batches do not mistake them for orphaned assets.

## Delta Classification

| Group | Representative paths | Existing owner evidence | Lifecycle result |
| --- | --- | --- | --- |
| Root view sidecars | `.claude/*`, `TASK.md` | Root demo/sidecar checklist classifies these as non-page sidecars | `sidecar-agent-state` / `sidecar-task-note`; exclude from page archive |
| Root backup artifact | `PortfolioManagement.vue.artdeco.backup` | Top-level legacy checklist covers `PortfolioManagement.vue`; backup naming is temporary/compat artifact governed by STANDARDS cleanup rules | `candidate-review/temp-backup`; not deletion-approved |
| Root direct specs | `__tests__/{Analysis,BacktestAnalysis,...,Wencai,monitor}.spec.ts` | Top-level legacy checklist records root `views/__tests__/*` as direct owner specs | `guard-asset/root-view-lifecycle`; move only with owning page decision |
| AI nested composable spec | `ai/composables/__tests__/useMlWorkbench.spec.ts` | AI checklist covers `views/ai/*`, composables, styles, and tests | `active-test/ai-local-composable`; keep with `useMlWorkbench.ts` |
| Root composable helpers | `composables/tradingDashboardActions.ts`, `useEnhancedDashboard.ts`, `useSettings.ts`, `useTechnicalAnalysis.shortcuts.ts`, `useTechnicalAnalysis.types.ts` | `views/composables` checklist classifies active trade-terminal support and legacy root helpers | Split between `active-support/trade-terminal-local` and `candidate-review/legacy-root-support` |
| Demo sidecars and nested assets | `demo/.claude/*`, `demo/docs/*`, `demo/openstock/*`, `demo/pyprofiling/*`, `demo/stock-analysis/*`, `demo/styles/*` | Demo directory checklist covers shells, nested components/configs/docs/styles by sub-tree | `candidate-review/demo-*`; no child archive without parent shell decision |
| Market local support | `market/__node_tests__/*`, `market/composables/*`, `market/styles/*` | Market checklist covers active market pages, helper data, specs, and canonical/compat/static-shell split | `canonical-support-asset` or candidate style support tied to owning market page |
| Stocks local styles | `stocks/styles/{Concept,Portfolio,Watchlist}.scss` | Stocks checklist covers orphan/static-shell pages and style assets by domain | `candidate-support-asset/stocks-style`; govern with owning stocks page |
| Strategy local style | `strategy/styles/StrategyList.scss` | Strategy checklist covers active route wrappers and legacy strategy workbench assets | `canonical-support-asset/strategy-list-style`; govern with `StrategyList.vue` |
| Root style residuals | `styles/{Analysis,BacktestAnalysis,Dashboard,...}.scss/css` | `views/styles` checklist classifies direct imports, test-guarded styles, and residual style assets | Mixed `active-support`, `test-guarded-style`, and `candidate-review/legacy-style-asset`; no bulk archive |
| Trade-management support | `trade-management/config.ts`, `trade-management/components/styles/TradeHistoryTab.scss` | Trade-management components checklist covers local components as retained candidate/support assets | `candidate-support-asset/trade-management`; govern with component batch |
| Trading direct specs | `trading/__tests__/*.spec.ts` | Trading checklist covers all `views/trading/*` pages and direct guard status | `guard-asset/trading-legacy`; move only with owning page decision |
| Trading-decision direct specs | `trading-decision/__tests__/*.spec.ts` | Trading-decision checklist covers child components and guard status | `guard-asset/trading-decision-legacy`; move only with owning component decision |

## Required Handling Rules

- Exact-path absence in earlier docs is not archive evidence when a directory-level checklist already covers the lifecycle group.
- Test files are guard assets, not redundant pages. They must be retired or migrated in the same approved mutation batch as their owning pages/components.
- Styles and configs are support assets. They inherit the lifecycle of the owning page/component unless a separate style/config successor is recorded.
- Demo child components/configs/docs/styles cannot be archived independently from their parent demo shell.
- Backup files require explicit temp-backup disposition under `architecture/STANDARDS.md`; naming alone is not deletion approval.

## Archive Eligibility

Current eligibility: no path in this delta is `archive-approved`.

Blocking conditions:

- Many paths are tests or support assets coupled to already-reviewed page lifecycles.
- Several paths are covered by directory-level mainline/style guards.
- Demo nested assets still have parent shell ownership and possible absorption value.
- Root backup and sidecar files need tooling/cleanup-specific disposition, not page archive treatment.

## Governance Conclusion

This delta closes the remaining exact-path checklist gap for non-ArtDeco `views/**`. It confirms that the apparent 108-path gap is mostly documentation granularity, not unreviewed runtime ownership. The next governance phase should move from evidence expansion to mutation planning only after selecting a narrow approved batch, for example root demo/test sandbox triage or guard retirement for a single legacy directory.
