# Frontend Chromium Full-Suite Recovery 2026-05-07

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Summary

本批次目标是把此前因运行时真相漂移和局部数据归一化缺口导致的 Chromium E2E 失败面收敛到全绿。

实际结果：

- Chromium stable 子集：`10/10` 通过
- Chromium 全量项目：`295/295` 通过
- 对应代码提交：`4186a699a7be0d640dbed14f94c0787de804ad0b`
- 提交信息：`fix(frontend): align chromium runtime truth`

## Scope

本批次同时包含运行时修复与测试真相对齐。

核心改动点：

1. 公告明细归一化
   - `announcement_title -> title`
   - `announcement_type -> type`
   - 文件：
     - `web/frontend/src/views/announcement/composables/useAnnouncementMonitor.ts`
     - `web/frontend/src/views/announcement/__tests__/useAnnouncementMonitor.spec.ts`

2. 策略回测上下文标签保真
   - 保留已解析出的策略名称，避免在缺少 selected snapshot 时退化成 `策略 {id}`
   - 文件：
     - `web/frontend/src/views/artdeco-pages/strategy-tabs/backtestAnalysisViewModel.ts`
     - `web/frontend/src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoBacktestAnalysis.spec.ts`

3. Phase 3 / Phase 4 E2E 真相对齐
   - 风险、系统、回测、新闻等场景的错误文案、request provenance、统计值与运行时当前真相对齐
   - 文件：
     - `web/frontend/tests/e2e/phase3-mainline-matrix.spec.ts`
     - `web/frontend/tests/e2e/phase4-mainline-matrix.spec.ts`
     - `web/frontend/tests/e2e/risk-overview.spec.ts`
     - `web/frontend/tests/e2e/risk-pnl.spec.ts`
     - `web/frontend/tests/e2e/system-api-store-governance.spec.ts`

## Exact Commit File Set

`git show --name-only 4186a699a` 复核到的精确文件集如下：

- `web/frontend/src/views/announcement/__tests__/useAnnouncementMonitor.spec.ts`
- `web/frontend/src/views/announcement/composables/useAnnouncementMonitor.ts`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoBacktestAnalysis.spec.ts`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/backtestAnalysisViewModel.ts`
- `web/frontend/src/views/risk/__tests__/Alerts.spec.ts`
- `web/frontend/src/views/risk/__tests__/Overview.spec.ts`
- `web/frontend/tests/e2e/phase3-mainline-matrix.spec.ts`
- `web/frontend/tests/e2e/phase4-mainline-matrix.spec.ts`
- `web/frontend/tests/e2e/risk-overview.spec.ts`
- `web/frontend/tests/e2e/risk-pnl.spec.ts`
- `web/frontend/tests/e2e/system-api-store-governance.spec.ts`

## Verification

本批次关键验证命令与结果：

```bash
cd web/frontend && npm run test -- src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoBacktestAnalysis.spec.ts
# 12 passed

cd web/frontend && npm run test -- src/views/announcement/__tests__/useAnnouncementMonitor.spec.ts src/views/announcement/__tests__/AnnouncementMonitor.spec.ts
# 14 passed

cd web/frontend && npm run test -- src/views/risk/__tests__/Alerts.spec.ts src/views/risk/__tests__/Overview.spec.ts
# 11 passed

cd web/frontend && env PLAYWRIGHT_EXTERNAL_FRONTEND=1 npx playwright test --config playwright.config.js --project=chromium tests/e2e/phase3-mainline-matrix.spec.ts
# 52 passed

cd web/frontend && env PLAYWRIGHT_EXTERNAL_FRONTEND=1 npx playwright test --config playwright.config.js --project=chromium tests/e2e/phase4-mainline-matrix.spec.ts
# 38 passed

cd web/frontend && env PLAYWRIGHT_EXTERNAL_FRONTEND=1 npx playwright test --config playwright.config.js --project=chromium
# 295 passed
```

补充说明：

- 本次恢复确认此前的 Chromium 阻塞已经解除，失败面不再是浏览器缺失，而是运行时真相与测试口径漂移。
- 该批次已把已暴露的失败桶压到 `chromium 295/295` 全通过。

## Runtime Status At Verification Time

验收时服务状态：

- `mystocks-backend`: `http://localhost:8020`
- `mystocks-frontend`: `http://localhost:3020`
- `GET /health/ready` 返回 `status=ready`
- 前端根路径返回 `HTTP 200 OK`

## Conclusion

截至 `2026-05-07`，Chromium 全量 E2E 已恢复为可直接复用的绿色基线。

后续如果再次出现 Chromium 失败，应优先按以下顺序排查：

1. 运行时文案 / request provenance / stats 真相是否已漂移
2. 页面数据归一化字段是否与当前接口负载一致
3. 策略上下文同步逻辑是否把已验证标签回退成 fallback 文案
4. 最后才判断是否为浏览器或 Playwright 环境问题
