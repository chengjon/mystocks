# ArtDeco AI Sentiment Shape And Test Hardening Report

Date: 2026-05-31

Function Tree node: `artdeco-web-design-governance/ai-sentiment-shape-test-hardening`

Implementation commit: `99cdd453f test(web): harden ai sentiment header readiness`

## Scope

Prepared `/ai/sentiment` for a possible later ArtDeco route header shell migration.

Touched implementation surface:

- `web/frontend/tests/e2e/ai-sentiment-workbench.spec.ts`

Governance/report surface:

- `.governance/active-gates.json`
- `.governance/active-gates.md`
- `.governance/programs/artdeco-web-design-governance/nodes.json`
- `.governance/programs/artdeco-web-design-governance/cards/ai-sentiment-shape-test-hardening.yaml`
- `docs/reports/tasks/2026-05-31-artdeco-ai-sentiment-route-header-readiness-shape-brief.md`
- `docs/reports/tasks/2026-05-31-artdeco-ai-sentiment-shape-test-hardening-report.md`

## Result

Created the readiness shape brief:

- `docs/reports/tasks/2026-05-31-artdeco-ai-sentiment-route-header-readiness-shape-brief.md`

The brief recommends a later route header shell migration that targets `web/frontend/src/views/ai/components/AiSentimentHero.vue`, not `Sentiment.vue`, because the child component owns the current local header shell and is only used by the canonical `/ai/sentiment` page.

Hardened the existing E2E route test so the current header semantics are protected before any future migration:

- `REQ_ID: req-ai-sentiment-workbench-1` must remain inside `ai-sentiment-header`
- `DOMAIN: AI` must remain inside `ai-sentiment-header`
- `ENTRY: sentiment` must remain inside `ai-sentiment-header`
- `AI 工作台在线` must remain inside `ai-sentiment-header`
- `ai-sentiment-refresh` must remain inside `ai-sentiment-header`

## Compatibility Boundary

Not changed:

- `web/frontend/src/router/index.ts`
- `/ai/sentiment` route ownership
- backend API routes, OpenAPI/Pydantic schemas, or frontend API clients
- `useAiSentimentWorkbench`
- `Sentiment.vue`
- `AiSentimentHero.vue`
- AI sentiment child panel behavior
- `/risk/news` wrapper behavior
- shared AI sentiment business components

No route header shell migration was performed in this node.

## GitNexus Evidence

Pre-edit impact analysis for `web/frontend/src/views/ai/Sentiment.vue`:

- risk: LOW
- direct affected symbols: 1
- affected processes: 0

Staged scope gate:

- changed files: 6
- risk level: low
- affected processes: 0

GitNexus index note:

- Local `gitnexus analyze` was run, not `npx gitnexus analyze`.
- Analyze result: repository indexed successfully in 285.9s, `234,283 nodes`, `321,598 edges`, `2738 clusters`, `300 flows`.
- MCP metadata still reported stale `indexed_commit` after analyze; this is the same known MCP metadata residual observed in this route-header workline.

## Verification

Focused E2E:

```bash
npx playwright test tests/e2e/ai-sentiment-workbench.spec.ts -g "renders the canonical ai sentiment page" --project=chromium
```

Result:

- Chromium
- 1 test passed

Full AI sentiment E2E file:

```bash
npx playwright test tests/e2e/ai-sentiment-workbench.spec.ts --project=chromium
```

Result:

- Chromium
- 2 tests passed

Static and governance gates:

- `npx eslint tests/e2e/ai-sentiment-workbench.spec.ts --no-warn-ignored`: passed
- `npm run type-check`: exit code 0, 0 total errors, 0 structural syntax errors, 0 changed-file errors
- `openspec validate --all --strict`: 63 passed, 0 failed
- `ft-governance scope-check --files ...`: within active authorization
- `ft-governance validate --steward`: passed
- `git diff --cached --check`: passed

PM2:

- `mystocks-backend`: online, expected URL `http://localhost:8020`
- `mystocks-frontend`: online, expected URL `http://localhost:3020`

## Dirty Worktree Note

The repository contains unrelated dirty files. This node staged only the E2E test hardening, Function Tree node/card/active-gate files, shape brief, and this report.

Known unrelated file to keep unstaged:

- `.governance/programs/artdeco-web-design-governance/tree.md`

## Next Recommended Step

Ask for explicit approval of the shape brief before starting the later `route-header-shell-ai-sentiment` node.

If approved, the next implementation should:

1. create `route-header-shell-ai-sentiment`
2. add the RED assertion that `ai-sentiment-header` must have `artdeco-route-header`
3. migrate `AiSentimentHero.vue` to render `ArtDecoRouteHeader`
4. keep `Sentiment.vue`, router, APIs, clients, composables, panels, and `/risk/news` behavior unchanged
