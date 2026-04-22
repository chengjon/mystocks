# Frontend Data Governance Inspector

开发期治理面板挂载在既有 `/system/api` 页面内，不新增路由。

## Purpose

- 查看后端 readiness / request id
- 查看试点 capability 与 store policy 快照
- 查看关键 store 的加载、错误、最近抓取时间与 stale 状态
- 查看 realtime channel 的合流策略与连接语义

## Access

- `import.meta.env.DEV === true`
- 或浏览器中设置 `localStorage['mystocks:developer-mode'] = 'true'`

## Verification Workflow

1. 打开 `/system/api`
2. 检查 readiness 是否返回 request id
3. 检查 capability 表与文档登记一致
4. 检查 store runtime state 是否能反映 `loading/error/lastFetch/isStale`
5. 检查 realtime registry 是否显示 channel 与 coalescing 策略
6. 运行 `python scripts/compliance/frontend_data_access_report.py --strict`，确认视图层没有绕过既有 service/store 治理边界

## Current Scope

- 只覆盖 `technical-indicators`、`trading-signals`、`risk-alerts`、`user-watchlists`
- 当前 inspector 为迁移辅助面板，不作为用户功能承诺
