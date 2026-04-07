# Large File Exception Registry (ArtDeco 3.1)

> **历史文档说明**:
> 本文件是某阶段的历史文档、过程记录或专题材料，不是当前基线、当前系统总览或仓库共享规则的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内描述、背景、结论和上下文如未重新复核，应视为历史快照，不得直接当作当前事实。


This document tracks files temporarily allowed to exceed limits and the current progress of governance.

| Category | File Path | Current Lines | Status | Strategy |
| :--- | :--- | :--- | :--- | :--- |
| **Backend** | `web/backend/app/api/data.py` | ~1200 | 🚩 Pending | Wave 4: Vertical Slicing |
| **Core** | `src/core/unified_manager.py` | ~900 | 🚩 Pending | Wave 5: DDD Domain Refactor |
| **Frontend** | `web/frontend/src/api/types/common.ts` | 25 | ✅ Slimmed | Barrel Export Implementation |
| **Test** | `web/frontend/tests/api-automation.spec.js` | 6 | ✅ Slimmed | Suite Migration to `legacy-suite.js` |
| **Ops** | `scripts/tests/web-usability-runner.js` | 30 | ✅ Slimmed | Core Migration to `runner-core.js` |
| **Ops** | `scripts/tests/web-usability/runner-core.js` | 142 | ✅ Slimmed | Split into `scripts/tests/web-usability/core/*.js` modules |
| **Archive** | `web/frontend/src/views/converted.archive/market-quotes.vue` | 1141 | ✅ Governed | Archived page; route-detached, TS-excluded, only reactivated after migration to active ArtDeco page |
| **Archive** | `web/frontend/src/views/converted.archive/market-data.vue` | 978 | ✅ Governed | Archived page; route-detached, TS-excluded, only reactivated after migration to active ArtDeco page |
| **Archive** | `web/frontend/src/views/converted.archive/backtest-management.vue` | 863 | ✅ Governed | Archived page; route-detached, TS-excluded, only reactivated after migration to active ArtDeco page |
| **Archive** | `web/frontend/src/views/converted.archive/setting.vue` | 829 | ✅ Governed | Archived page; route-detached, TS-excluded, only reactivated after migration to active ArtDeco page |
| **Archive** | `web/frontend/src/views/converted.archive/trading-management.vue` | 741 | ✅ Governed | Archived page; route-detached, TS-excluded, only reactivated after migration to active ArtDeco page |
| **Archive** | `web/frontend/src/views/converted.archive/dashboard.vue` | 605 | ✅ Governed | Archived page; route-detached, TS-excluded, only reactivated after migration to active ArtDeco page |
| **3rd Party** | `scripts/dev/**` | 70 files >1000 lines | ✅ Exception Approved | Third-party/generated artifacts (Playwright, Puppeteer, jsdom, Babel, etc.); no manual split, monthly inventory review only |

---
**Last Updated**: 2026-03-08
