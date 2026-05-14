# 2026-05-14 AI ML Runtime Smoke Stability Result

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Scope

This note records the follow-up runtime smoke stability evidence for `/ai/ml` after the `07-高级分析与AI` runtime readiness review reported intermittent skeleton or navigation timeout behavior.

It is an evidence-only governance note. It does not modify `FUNCTION_TREE`, does not change the `07-高级分析与AI` domain status, and does not reopen `7.1 模型训练 / 预测推理` as a new implementation line.

## Environment

Playwright browser cache was available:

- `/root/.cache/ms-playwright/chromium-1200`
- `/root/.cache/ms-playwright/ffmpeg-1011`
- `/root/.cache/ms-playwright/chromium_headless_shell-1200`

PM2 services were online during the smoke:

- `mystocks-backend`: `online`, `http://localhost:8020`
- `mystocks-frontend`: `online`, `http://localhost:3020`

The smoke used the existing PM2 frontend instead of starting a separate dev server:

```bash
PLAYWRIGHT_EXTERNAL_FRONTEND=1
```

## Verification

### Targeted Single Run

```bash
PLAYWRIGHT_EXTERNAL_FRONTEND=1 npm run test:e2e -- --project=chromium tests/e2e/ai-ml-workbench.spec.ts
```

Result: `12 passed (23.6s)`.

Covered behaviors include:

- runtime status rendering;
- model training flow;
- prediction flow without trading semantics;
- disabled actions when runtime operations are unavailable;
- invalid training date range;
- blank training symbol;
- invalid numeric training ranges;
- prediction model scope mismatch;
- prediction trimming;
- blank prediction symbol;
- blank model id;
- no fallback to selected model after model id input is cleared;
- invalid or mismatched prediction horizon.

### Repeat Stability Run

```bash
PLAYWRIGHT_EXTERNAL_FRONTEND=1 npm run test:e2e -- --project=chromium tests/e2e/ai-ml-workbench.spec.ts --repeat-each=3
```

Result: `36 passed (1.2m)`.

## Governance Interpretation

This closes the specific `/ai/ml` browser smoke instability concern from the readiness review for the currently tested path and environment.

It improves `07-高级分析与AI` runtime evidence, but it is still not a standalone basis for upgrading the domain-level status. The domain should remain `🧪 / 50%` until the remaining readiness dimensions are governed, including:

- at least one governed ML model artifact or an explicit external dependency decision;
- `7.2` production scheduler / persistence / audit boundary decisions;
- governance catalog and `FUNCTION_TREE` prefix alignment package;
- final review that consolidates `7.1`, `7.2`, and `7.3` runtime evidence.
