# API File-Level Testing Closeout Tasks

> **使用说明**:
> 本文件用于记录当前 OpenSpec 变更的执行清单、操作步骤或协作约束，帮助跟踪实施过程。
> 其中勾选状态、执行顺序和局部说明仅代表任务推进视角，不应脱离 proposal、design、正式 specs、`architecture/STANDARDS.md` 与实际验证结果单独解读为最终事实。

## Closeout Checklist

- [x] 建立 `tests/api/file_tests/` 主线收口范围，并以 replacement task 重定义旧包装任务的边界
- [x] 完成 mainline salvage 微批次并并入 `origin/main`（#58-#62）
- [x] 确认唯一残留 `tests/api/file_tests/test_tradingview_api.py` 仅属 root-dirty hygiene，不再作为主线 salvage 未完成项
- [x] 发布 closeout 证据与替代任务说明：`reports/governance/2026-04-06-api-file-tests-salvage-closeout.md`、`docs/reports/tasks/2026-03-27-api-file-testing-replacement-task.md`
