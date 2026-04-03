## 1. Spec Reconciliation
- [ ] 1.1 Update `frontend-routing` spec with canonical dashboard route truth and DealingRoom compatibility semantics
- [ ] 1.2 Update `file-organization` spec to block deprecating active route-bound pages

## 2. Repo Truth Alignment
- [ ] 2.1 Update governed frontend page inventory so `/dashboard` is canonical and `DealingRoom` is treated as a legacy alias or display label
- [ ] 2.2 If compatibility is required, add or preserve a `/dealing-room` alias/redirect to the canonical dashboard shell
- [ ] 2.3 Align generated page-config truth with the reconciled canonical naming

## 3. Restructure Unblock
- [ ] 3.1 Update `restructure-frontend-directory` task `8.6` to remove the unsafe deprecation assumption
- [ ] 3.2 Confirm `TradingDashboard.vue` remains exclusive to `/trade/terminal` until a separate approved change says otherwise
- [ ] 3.3 Run route smoke validation for `/`, `/dashboard`, and any retained `/dealing-room` alias
