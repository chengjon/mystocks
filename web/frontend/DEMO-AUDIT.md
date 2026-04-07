# Demo Audit: views/demo/

**Created:** 2026-04-07
**Phase:** 03-structural-consolidation (Plan 03-02, Task 6)

## Verdict: KEEP — Active Code

`views/demo/` is **NOT a deletion target.** It has active routes, view consumers, and test coverage.

## Directory Structure

| Subdirectory | Contents |
|-------------|----------|
| demo/ | Root demo views (OpenStockDemo.vue, Wencai.vue, etc.) |
| demo/openstock/ | OpenStock demo components + config |
| demo/pyprofiling/ | PyProfiling demo components + styles |
| demo/stock-analysis/ | Stock analysis demo components |
| demo/composables/ | Demo-specific composables |
| demo/docs/ | Demo documentation |
| demo/styles/ | Demo shared styles |

Note: FreqtradeDemo.vue, TdxpyDemo.vue, and smart-data-test live in sibling view directories (`views/freqtrade-demo/`, `views/tdxpy-demo/`), not inside `views/demo/`.

## Active Routes (6 defined in router/index.js)

| Route Path | Route Name | Source |
|-----------|------------|--------|
| `/demo/openstock` | openstock-demo | router/index.js:128-129 |
| `/demo/pyprofiling` | pyprofiling-demo | router/index.js:134-135 |
| `/demo/freqtrade` | freqtrade-demo | router/index.js:140-141 |
| `/demo/stock-analysis` | stock-analysis-demo | router/index.js:146-147 |
| `/demo/tdxpy` | tdxpy-demo | router/index.js:152-153 |
| `/demo/smart-data-test` | smart-data-test | router/index.js:157-158 |

## Runtime Consumers

### Direct consumers of views/demo/ contents

| Consumer View | Imports From |
|--------------|-------------|
| OpenStockDemo.vue | `./demo/openstock/config`, `./demo/openstock/components` |

### Sibling view consumers (NOT importing from views/demo/)

| View | Imports From | Note |
|------|-------------|------|
| FreqtradeDemo.vue | `./freqtrade-demo/FreqOverviewTab.vue`, + 5 more tabs | Sibling `views/freqtrade-demo/` directory |
| TdxpyDemo.vue | `./tdxpy-demo/TdxOverviewTab.vue`, + 4 more tabs | Sibling `views/tdxpy-demo/` directory |

## Test Consumers

| Test File | What It Tests |
|-----------|--------------|
| tests/all-pages-accessibility.spec.ts | Tests 5 demo routes for accessibility |
| tests/menu-configuration.spec.js | Tests demo menu navigation |
| tests/unit/config/openstock-*-style-source.spec.ts | Style source validation for openstock components |
| tests/unit/config/pyprofiling-*-style-source.spec.ts | Style source validation for pyprofiling components |
| tests/unit/config/stock-analysis-*-style-source.spec.ts | Style source validation for stock-analysis components |

## Risk Assessment

| Action | Would Break |
|--------|------------|
| Delete demo/ | 6 routes, 1 direct consumer, 2 sibling consumers, 8+ test files |
| Delete without router update | Broken navigation, 404s |
| Delete without test update | 8+ test failures |

## Recommendation

**Keep views/demo/ as active code.** Do not delete, archive, or relocate.

If demo pages should be hidden from production, use feature flags or route guards — not directory deletion.

**STRU-05 status (demo portion):** Cannot complete. views/demo/ is active code with routes, views, and tests. Recommend updating REQUIREMENTS.md to mark STRU-05 demo portion as "not applicable — active code".
