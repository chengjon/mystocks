# Large File Exception Registry (ArtDeco 3.1)

This document tracks files temporarily allowed to exceed limits and the current progress of governance.

| Category | File Path | Current Lines | Status | Strategy |
| :--- | :--- | :--- | :--- | :--- |
| **Backend** | `web/backend/app/api/data.py` | ~1200 | 🚩 Pending | Wave 4: Vertical Slicing |
| **Core** | `src/core/unified_manager.py` | ~900 | 🚩 Pending | Wave 5: DDD Domain Refactor |
| **Frontend** | `web/frontend/src/api/types/common.ts` | 25 | ✅ Slimmed | Barrel Export Implementation |
| **Test** | `web/frontend/tests/api-automation.spec.js` | 6 | ✅ Slimmed | Suite Migration to `legacy-suite.js` |
| **Ops** | `scripts/tests/web-usability-runner.js` | 30 | ✅ Slimmed | Core Migration to `runner-core.js` |
| **Ops** | `scripts/tests/web-usability/runner-core.js` | 142 | ✅ Slimmed | Split into `scripts/tests/web-usability/core/*.js` modules |
| **3rd Party** | `scripts/dev/**` | 70 files >1000 lines | ✅ Exception Approved | Third-party/generated artifacts (Playwright, Puppeteer, jsdom, Babel, etc.); no manual split, monthly inventory review only |

---
**Last Updated**: 2026-02-23
