# Frontend Realtime Channel Registry

本表用于记录前端实时通道的消费策略，尤其是推送频率、合流策略和强制刷新语义。

| Channel | Transport | Consumer Entry | Coalescing | Force Refresh | Notes |
| --- | --- | --- | --- | --- | --- |
| `market:realtime:{symbol}` | menu-service WebSocket | `useRealtimeMarket.subscribeStock` | latest-only, default `200ms` | manual unsubscribe / resubscribe | 保留用户可见新鲜度，减少高频重绘 |
| `market:summary` | menu-service WebSocket | `useRealtimeMarket.subscribeMarketSummary` | latest-only, default `200ms` | manual unsubscribe / resubscribe | 面向概览卡片和监控视图 |
| `trading-signals` | unified websocket manager | `useTradingSignalsStore` | store-level update | `refresh()` allowed | 轮询 10s 作为 fallback |
| `risk-alerts` | unified websocket manager | `useRiskAlertsStore` | store-level update | `refresh()` allowed | 轮询 15s 作为 fallback |

## Pilot Constraint

- 只在 `useRealtimeMarket` 里做 shared helper 试点。
- 若后续要扩大到更多通道，优先复用 `streamCoalescer`，而不是复制节流逻辑。
