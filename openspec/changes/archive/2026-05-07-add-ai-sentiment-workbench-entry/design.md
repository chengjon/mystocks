## Context

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

The repository already exposes:
- sentiment analysis APIs under `web/backend/app/api/v1/analysis/sentiment.py`
- a risk-domain announcement/news workbench under `web/frontend/src/views/risk/News.vue`

The missing part is not a new algorithm or a new backend aggregate API. The missing part is an AI-domain canonical entry and a stable shared orchestration layer that prevents `risk/news` and the future AI surface from drifting into parallel implementations.

## Goals
- Establish `/ai/sentiment` as the canonical AI-domain sentiment workbench route
- Create a dual-column AI workbench that combines announcement/news monitoring and sentiment analysis surfaces
- Make the AI workbench orchestration the single frontend truth source for this capability
- Keep `/risk/news` as a risk-domain wrapper with risk-specific framing and a jump path into the AI workbench

## Non-Goals
- Rebuilding the sentiment scoring algorithm
- Persisting the current in-memory sentiment history model
- Introducing a new backend aggregate endpoint for the workbench
- Removing or redirecting `/risk/news`
- Expanding the broader ML domain beyond this sentiment workbench line

## Decisions
- Decision: introduce a new frontend capability entry at `/ai/sentiment`
  - Rationale: this closes the AI-domain truth gap without reclassifying risk-domain routing as the canonical home of sentiment analysis
- Decision: keep the current backend sentiment endpoints as the MVP contract
  - Rationale: the repo-local gap is domain entry and shared orchestration, not backend contract absence
- Decision: use a shared, view-local workbench orchestration layer
  - Rationale: `Sentiment.vue` becomes the canonical page while `News.vue` becomes a wrapper instead of duplicating fetch state
- Decision: preserve `/risk/news` as a wrapper instead of redirecting it
  - Rationale: risk-domain navigation remains valid, but ownership of the capability shifts to the AI domain

## Risks / Trade-offs
- Risk: `News.vue` currently contains self-owned request state and fetch logic
  - Mitigation: migrate that orchestration into a shared composable and keep `News.vue` focused on wrapper framing
- Risk: menu, page-config, and route metadata may drift if updated separately
  - Mitigation: update routing, menu config, and page config in the same batch and verify through route/page config tests
- Risk: the AI workbench may look like a full news platform if scope expands
  - Mitigation: keep the MVP centered on the existing announcement/news flow plus the three current sentiment endpoints

## Migration Plan
1. Add the OpenSpec route and capability deltas
2. Add the AI route, menu entry, and page config entry
3. Build the canonical AI workbench page and shared orchestration
4. Convert `News.vue` into a risk wrapper over shared workbench pieces
5. Verify routing, wrapper reuse, and sentiment contract stability

## Open Questions
- None for MVP scope after approval of the AI route, dual-column workbench, and risk-wrapper boundary
