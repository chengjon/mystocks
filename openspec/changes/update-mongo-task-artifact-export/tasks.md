## 1. Implementation

> **使用说明**:
> 本文件用于记录当前 OpenSpec 变更的执行清单、操作步骤或协作约束，帮助跟踪实施过程。
> 其中勾选状态、执行顺序和局部说明仅代表任务推进视角，不应脱离 proposal、design、正式 specs、`architecture/STANDARDS.md` 与实际验证结果单独解读为最终事实。


- [x] 1.1 Modify the collaboration specification so `TASK.md` / `TASK-REPORT.md` become exported snapshots rather than authoritative hand-authored task sources for active Mongo-backed work.
- [x] 1.2 Add a minimal task-artifact export command surface to `coordctl` / `maestro_collab`.
- [x] 1.3 Implement markdown renderers for exported `TASK.md` and `TASK-REPORT.md` snapshots from Mongo control-plane records.
- [x] 1.4 Add focused unit tests for export commands and snapshot content.
- [x] 1.5 Update Mongo / Symphony guidance to describe the Mongo-only source-of-truth model and exported-markdown compatibility role.
- [x] 1.6 Run focused validation for the modified runtime and documentation files.
