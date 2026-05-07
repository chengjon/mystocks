## 1. OpenSpec

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

- [x] 1.1 Add `frontend-routing` delta for the AI sentiment workbench route and navigation label
- [x] 1.2 Add `ai-sentiment-workbench` capability delta for canonical page ownership and risk-wrapper rules
- [x] 1.3 Validate `add-ai-sentiment-workbench-entry` with `openspec validate --strict`

## 2. Frontend Routing And Navigation
- [x] 2.1 Add `/ai/sentiment` route and AI route metadata
- [x] 2.2 Add AI menu/navigation entry and page config entry
- [x] 2.3 Keep `/risk/news` reachable as a risk wrapper surface

## 3. Shared Workbench
- [x] 3.1 Add the canonical AI sentiment workbench page under `web/frontend/src/views/ai/`
- [x] 3.2 Add a shared workbench orchestration composable for announcement flow + sentiment APIs
- [x] 3.3 Split reusable sentiment/news workbench sections into page-local components

## 4. Risk Wrapper
- [x] 4.1 Refactor `web/frontend/src/views/risk/News.vue` into a risk-domain wrapper over shared workbench logic
- [x] 4.2 Add a clear jump path from the risk wrapper to `/ai/sentiment`
- [x] 4.3 Remove duplicate orchestration ownership from the risk wrapper

## 5. Verification And Governance
- [x] 5.1 Add or update frontend unit tests for route/page config and shared workbench behavior
- [x] 5.2 Add or update smoke coverage for `/ai/sentiment` and `/risk/news`
- [x] 5.3 Update `docs/FUNCTION_TREE.md` once AI-domain closure conditions are met
