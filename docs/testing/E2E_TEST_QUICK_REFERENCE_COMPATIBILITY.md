# E2E Test Quick Reference (Compatibility Entry)

> **使用说明**:
> 本文件是历史兼容 quick reference，不是当前 E2E 门禁或当前前端测试主线的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及测试执行流程、E2E 规范或协作约束，再结合 `docs/testing/TESTING_GUIDE.md`、`docs/testing/e2e/README.md` 与根目录 `AGENTS.md`。

该文件用于承接历史根目录引用 `E2E_TEST_QUICK_REFERENCE.md`，并作为兼容入口保留在 `docs/guides/`。

## 标准命令（2026-03）

```bash
cd /opt/claude/mystocks_spec/web/frontend
npm run test:e2e
npm run test:e2e:chromium
```

## 配置说明

- 标准 E2E：`web/frontend/playwright.config.js`（仅 `tests/e2e`）
- legacy 专项：`web/frontend/playwright.config.ts`
- 端口建议从 `web/frontend/.env` 读取：`FRONTEND_PORT=3020`、`BACKEND_PORT=8020`（备份 `3021/8021`）

## 详细文档

- `docs/testing/TESTING_GUIDE.md`
- `docs/testing/TESTING_EXAMPLES.md`
- `docs/testing/WEB_E2E_TEST_QUICK_REFERENCE_V2.md`
