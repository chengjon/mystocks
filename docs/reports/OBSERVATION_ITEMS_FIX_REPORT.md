# Observation Items Fix Report

> **历史总结说明**:
> 本文件是阶段性总结、报告、状态、修复记录、验证结果或交付回执，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内统计值、完成状态、结论、验证结果和修复结论如未重新复核，应视为历史快照，不得直接当作当前事实。


## 🎯 Summary
Addressed the observation items from the `WEB_END_TO_END_TEST_REPORT.md`:
1.  **Dayjs `advancedFormat` Warning**: `The requested module '/node_modules/dayjs/plugin/advancedFormat.js' does not provide an export`.
2.  **CSP Warning**: `The Content Security Policy directive 'frame-ancestors' is ignored when delivered via a <meta> element`.
3.  **Data Sync Service Error**: `data-sync-kline` failing with `SyntaxError`.

## 🛠 Fixes Implemented

### 1. Dayjs ESM Compatibility
-   **File**: `web/frontend/vite.config.ts`
-   **Action**: Updated `resolve.alias` configuration to explicitly map `dayjs/plugin/advancedFormat.js` (and other plugins) to their ESM counterparts (`dayjs/esm/plugin/...`).
-   **Reason**: The previous alias might have missed imports with explicit `.js` extensions, or absolute path resolution was inconsistent. Simplified to string-based aliases for robustness.

### 2. CSP Meta Tag Cleanup
-   **File**: `web/frontend/index.html`
-   **Action**: Removed `frame-ancestors 'none';` from the `<meta http-equiv="Content-Security-Policy" ... />` tag.
-   **Reason**: `frame-ancestors` directive is ignored in meta tags and generates browser console warnings. It should be served via HTTP headers if needed.

### 3. Data Sync Script Fix
-   **File**: `scripts/data_sync/sync_stock_kline.py`
-   **Action**: Fixed a syntax error in the `filters` dictionary where the closing quote was misplaced.
    -   **Before**: `["MAX(trade_date) as latest_date]"]` (SyntaxError)
    -   **After**: `["MAX(trade_date) as latest_date"]`
-   **Reason**: Typo causing the script to crash.

## 🔍 Verification
-   **Dayjs**: Aliases now cover both bare imports and `.js` extension imports for plugins.
-   **CSP**: The invalid directive is removed from `index.html`.
-   **Data Sync**: The syntax error is resolved, allowing the script to parse correctly.

## 🚀 Next Steps
-   Restart frontend development server to apply Vite config and HTML changes.
-   Restart PM2 services to pick up the python script fix (`pm2 restart data-sync-kline`).
