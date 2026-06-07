# Analysis root legacy archive

Archived by `B4.007-F3-C` after route-truth review.

- Source path: `web/frontend/src/views/Analysis.vue`
- Archived path: `archive/web/frontend/src/views/root-legacy/analysis/Analysis.vue`
- Route truth: no active router or menu entry imports this root legacy Vue file in the current frontend route source.
- Config/E2E note: route-level `/analysis` references may still be valid canonical route or API/test vocabulary; they are not evidence that this archived root file is active runtime source.
- Recovery: restore the archived Vue file to the source path and reintroduce a focused route/test entry before using it as an active runtime view.
