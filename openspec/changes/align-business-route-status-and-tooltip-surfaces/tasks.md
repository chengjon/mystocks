## 1. Scope Lock

- [x] 1.1 Re-read `DESIGN.md`, `ARTDECO_FINTECH_UNIFIED_SPEC.md`, `ARTDECO_COMPONENT_GUIDE.md`, and the completed `align-artdeco-stateful-primitives-with-design` change before implementation
- [x] 1.2 Confirm this batch only targets active business-route surfaces on the current router mainline, including canonical route hosts that may live under `views/artdeco-pages/**`
- [x] 1.3 Confirm tooltip scope is limited to proven user-facing tooltip debt, not generic `title` props or chart-local tooltip styling

## 2. Status-Badge Alignment

- [x] 2.1 Replace repeated route-local `status-badge` implementations with `ArtDecoBadge.vue` where routed pages only need shared status semantics
- [x] 2.2 Remove route-local status badge style truth after the shared badge mapping is in place
- [x] 2.3 Keep semantic mappings explicit for routed pages such as active/inactive, success/danger, match/no-match, and live/offline

## 3. Overlay And Floating-Surface Alignment

- [x] 3.1 Audit route-local overlay/backdrop surfaces in active business routes
- [x] 3.2 Align eligible route-owned overlays, drawers, and modals to `--ad-overlay-*` tokens without rewriting their behavior contracts
- [x] 3.3 Normalize route-local elevated floating panels only where they already exist and can safely consume the active token contract

## 4. Tooltip Debt Handling

- [x] 4.1 Identify any true user-facing local tooltip implementations in active business routes
- [x] 4.2 Normalize only the confirmed tooltip debt; leave card/dialog titles and chart-local tooltip systems out of scope

## 5. Governance Synchronization

- [x] 5.1 Update ArtDeco governance docs only if routed-page ownership or route-vs-workbench boundaries need clarification after implementation
- [x] 5.2 Keep the routed-page batch from creating new shared truth outside `ArtDecoBadge.vue` and existing token files

## 6. Verification

- [x] 6.1 Run `npx vue-tsc --noEmit`
- [x] 6.2 Run `npm run build:no-types`
- [x] 6.3 Inspect at least one touched route in each changed domain family
- [x] 6.4 If router/layout/shared-shell behavior changes unexpectedly, expand verification to PM2 + Playwright

## 7. Exit Criteria

- [x] 7.1 Confirm active business routes no longer keep repeated local `status-badge` truth for the touched pages
- [x] 7.2 Confirm touched route-owned overlays use the active overlay token contract
- [x] 7.3 Confirm the batch stays inside active business-route scope and does not reopen broad artdeco-pages cleanup beyond canonical route hosts already used by the current router
