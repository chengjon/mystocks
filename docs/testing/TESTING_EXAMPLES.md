# Testing Examples (Compatibility Entry)

> **使用说明**:
> 本文件是历史兼容示例入口，不是当前测试基线、当前命令全集或仓库共享规则的唯一事实来源。
> 执行前请优先核对 `docs/testing/TESTING_GUIDE.md`、`docs/testing/e2e/README.md` 与 `architecture/STANDARDS.md` 中的当前口径。

该文档用于承接历史引用路径 `docs/guides/TESTING_EXAMPLES.md`。

## 示例 1：StrategyManagement 链路 E2E（推荐）

```bash
cd /opt/claude/mystocks_spec/web/frontend
npm run test:e2e:strategy-chain
# 或手动指定（仅 Chromium）:
npm run test:e2e:chromium -- tests/e2e/strategy-management-chain.spec.ts
```

## 示例 2：标准 E2E 全量（按标准入口）

```bash
cd /opt/claude/mystocks_spec/web/frontend
npm run test:e2e
```

## 示例 3：仅 Chromium

```bash
cd /opt/claude/mystocks_spec/web/frontend
npm run test:e2e:chromium
```

## 示例 4：历史 PM2 综合用例（legacy）

```bash
cd /opt/claude/mystocks_spec/web/frontend
npm run test:e2e:comprehensive
```

## 说明

- 标准 E2E 配置：`web/frontend/playwright.config.js`（`tests/e2e`）。
- legacy 脚本默认使用 `web/frontend/playwright.config.ts`。
- 推荐通过 `.env` 统一端口：`FRONTEND_PORT=3020`、`BACKEND_PORT=8020`（备份 `3021/8021`）。
