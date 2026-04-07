# Tasks: add-policy-driven-directory-governance

> **历史任务说明**:
> 本文件用于保留某次历史任务拆解、执行清单或阶段性待办，不代表当前仍需按原样执行。
> 其中的勾选状态、优先级和实施顺序仅对应当时上下文；继续沿用前应先对照 `architecture/STANDARDS.md`、当前需求、现行 specs 与实际仓库状态重新校准。


- [x] Add OpenSpec proposal, design, and spec for directory governance
- [x] Add machine-readable directory governance policy YAML
- [x] Add Python policy-driven directory checker CLI
- [x] Update `scripts/maintenance/check-structure.sh` to wrap the Python checker
- [x] Add focused unit tests for policy loading and rule evaluation
- [x] Validate the new change with targeted pytest and `openspec validate --strict`
