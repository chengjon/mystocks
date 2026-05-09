## 1. Backend Evidence Source

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

- [ ] 1.1 Add focused tests for mapping miniQMT submission-attempt records into execution tracking rows.
- [ ] 1.2 Add focused tests for bridge-only terminal evidence remaining `review_required`.
- [ ] 1.3 Add a read-only execution tracking evidence service under `web/backend/app/services/trade/`.
- [ ] 1.4 Wire the execution tracking route to the evidence service while keeping response models stable.

## 2. Evidence Timeline
- [ ] 2.1 Add tests for bridge submission attempt timeline events.
- [ ] 2.2 Add tests for live bridge incident timeline events such as timeout, mismatch, auth failure, and bridge-only result.
- [ ] 2.3 Extend detail loading so evidence timeline includes miniQMT attempt and review incident evidence when available.

## 3. Safety Contract
- [ ] 3.1 Add tests proving broker acknowledgement is emitted only when broker lifecycle identity is present.
- [ ] 3.2 Keep `/api/v1/trade/execution-tracking/trigger` limited to external trigger intent and bridge receipt evidence.
- [ ] 3.3 Keep legacy `/api/v1/trade/execute` out of the execution tracking workbench dependency path.

## 4. Verification
- [ ] 4.1 Run `openspec validate connect-execution-tracking-to-miniqmt-evidence --strict`.
- [ ] 4.2 Run backend execution tracking tests.
- [ ] 4.3 Run frontend execution tracking unit and Chromium E2E smoke if response semantics or UI evidence text changes.
- [ ] 4.4 Confirm PM2 service status when frontend or backend runtime surfaces are touched.
