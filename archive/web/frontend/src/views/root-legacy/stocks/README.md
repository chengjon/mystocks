# Stocks root legacy archive

Archived by `B4.007-F3-D` after route-truth review.

- Source path: `web/frontend/src/views/Stocks.vue`
- Archived path: `archive/web/frontend/src/views/root-legacy/stocks/Stocks.vue`
- Route truth: no active router or menu entry imports this root legacy Vue file in the current frontend route source.
- Successor mapping: current stock list and screening workflows belong to the `/watchlist/*` route family and data-domain stock API surfaces.
- Config/E2E note: route-level `/stocks` and stock API/test vocabulary may still be valid canonical route or API/test vocabulary; they are not evidence that this archived root file is active runtime source.
- Recovery: restore the archived Vue file to the source path and reintroduce a focused route/test entry before using it as an active runtime view.
