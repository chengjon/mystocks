# StockDetail root legacy archive

Archived by `B4.007-F3-D` after route-truth review.

- Source path: `web/frontend/src/views/StockDetail.vue`
- Archived path: `archive/web/frontend/src/views/root-legacy/stock-detail/StockDetail.vue`
- Route truth: no active router or menu entry imports this root legacy Vue file in the current frontend route source.
- Successor mapping: current stock detail drill-down belongs to the `detail` route family, including `graphics/:symbol` and `news/:symbol`.
- Config/E2E note: route-level `/stock-detail` and stock-detail API/test vocabulary may still exist in legacy tests; they are not evidence that this archived root file is active runtime source.
- Recovery: restore the archived Vue file to the source path and reintroduce a focused route/test entry before using it as an active runtime view.
