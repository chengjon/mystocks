# 2026-05-14 AI Sentiment Runtime Path Fix Result

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Scope

This note records the follow-up result for the `07-高级分析与AI` runtime readiness review finding that `/ai/sentiment` generated `/api/api/v1/sentiment/market` in browser smoke.

It does not modify `FUNCTION_TREE`, does not reopen `7.3 情感分析` as a new feature line, and does not change the domain-level readiness status.

## Fix Summary

- Commit: `527a18cc5 fix(frontend): use canonical sentiment api client`
- Changed files:
  - `web/frontend/src/api/aiSentiment.ts`
  - `web/frontend/src/api/__tests__/aiSentiment.spec.ts`
- Root cause:
  - `aiSentiment.ts` used the legacy `request` wrapper with `/api/v1/sentiment/*` literals.
  - The canonical AI clients use `apiClient`, whose axios instance already has `baseURL: /api`.
  - Runtime composition produced `/api/api/v1/sentiment/*`.
- Resolution:
  - `aiSentiment.ts` now uses `apiClient`.
  - Sentiment endpoints now use `/v1/sentiment/*` literals so runtime requests resolve to `/api/v1/sentiment/*`.

## Verification

### Unit and Component

```bash
npm run test -- src/api/__tests__/aiSentiment.spec.ts --run
```

Result: `1 passed`.

```bash
npm run test -- src/api/__tests__/aiSentiment.spec.ts src/views/ai/__tests__/Sentiment.spec.ts --run
```

Result: `2 passed`, `3 tests passed`.

### Static Checks

```bash
npx eslint src/api/aiSentiment.ts
```

Result: `0 errors`.

```bash
git diff --check HEAD~1..HEAD
```

Result: no output.

Changed client literal count after fix:

- `/api/v1/sentiment`: `0`
- `/v1/sentiment`: `3`

### Runtime Smoke

Playwright Chromium was installed in the local browser cache:

```bash
npx playwright install chromium
```

Installed artifacts:

- `/root/.cache/ms-playwright/chromium-1200`
- `/root/.cache/ms-playwright/ffmpeg-1011`
- `/root/.cache/ms-playwright/chromium_headless_shell-1200`

PM2 services were online during the smoke:

- `mystocks-backend`: `online`, `http://localhost:8020`
- `mystocks-frontend`: `online`, `http://localhost:3020`

```bash
PLAYWRIGHT_EXTERNAL_FRONTEND=1 npm run test:e2e -- --project=chromium tests/e2e/ai-sentiment-workbench.spec.ts
```

Result: `2 passed (9.6s)`.

## Governance Interpretation

This closes the specific `7.3 情感分析` browser runtime path defect reported in `reports/governance/2026-05-14-ai-domain-runtime-readiness-review.md`.

It improves `07-高级分析与AI` runtime evidence, but it is not sufficient to upgrade the domain-level status by itself. The domain should remain `🧪 / 50%` until the remaining review findings are handled, including:

- `/ai/ml` smoke stability and timeout behavior;
- at least one governed ML model artifact or explicit external dependency decision;
- `7.2` production scheduler / persistence / audit boundary decisions;
- governance catalog and `FUNCTION_TREE` prefix alignment package.
