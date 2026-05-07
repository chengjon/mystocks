# Change: add-ai-sentiment-workbench-entry

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Why
`7.3 情感分析` 当前已经具备后端情感分析 API 和风险域公告/舆情工作台，但缺少 AI 域独立入口与统一前端真相源。现状使 `新闻情感` 和 `舆情监控` 继续依附 `/risk/news`，无法作为 `07-高级分析与AI` 的独立闭环能力治理。

## What Changes
- Add a dedicated AI-domain route at `/ai/sentiment`
- Add a visible AI navigation entry for the sentiment workbench
- Introduce a canonical AI sentiment workbench page with shared orchestration
- Keep `/risk/news` as a risk-domain wrapper that reuses the shared workbench instead of owning separate orchestration
- Preserve the existing sentiment backend contract and announcement/news flow sources for this MVP

## Impact
- Affected specs:
  - `frontend-routing`
  - `ai-sentiment-workbench`
- Affected code:
  - `web/frontend/src/router/index.ts`
  - `web/frontend/src/config/menu.config.js`
  - `web/frontend/src/config/pageConfig.ts`
  - `web/frontend/src/views/risk/News.vue`
  - `web/frontend/src/views/ai/`
