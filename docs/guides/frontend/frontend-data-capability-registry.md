# Frontend Data Capability Registry

本表记录前端数据能力的最小治理真相源，避免在视图、service、store、实时通道之间出现隐式耦合。

| Capability | Owner | Source of Truth | Endpoint | Cache | Refresh / Stale | Pilot Scope | Primary Consumers |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `technical-indicators` | frontend-platform | API | `GET /v1/technical-indicators` | memory, 5 min | force refresh allowed, stale after 300s | Yes | `ArtDecoTechnicalAnalysis.vue`, dashboard services |
| `trading-signals` | frontend-platform | Hybrid | `GET /api/trading/signals` + `trading-signals` WebSocket | memory, 1 min | poll fallback 10s, stale after 60s | Yes | trading panels, system inspector |
| `risk-alerts` | frontend-platform | Hybrid | `GET /api/risk/alerts` + `risk-alerts` WebSocket | memory, 30s | poll fallback 15s, stale after 30s | Yes | risk panels, system inspector |
| `user-watchlists` | frontend-platform | API | `GET /api/user/watchlists` | sessionStorage, 30 min | force refresh allowed, stale after 1800s | Yes | watchlist views, system inspector |

## Governance Notes

- 当前试点不引入新的 DataHub / TopicBus 运行时。
- 现有 `apiClient`、`PiniaStoreFactory`、WebSocket composable 仍是 canonical 路径。
- 新能力应先登记 capability，再决定是否需要 store policy、safe service variant 或 realtime coalescing。
