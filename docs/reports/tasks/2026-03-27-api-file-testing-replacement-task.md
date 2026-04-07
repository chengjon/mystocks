# API File-Level Testing 收口替代任务说明

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、执行清单或整改建议，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值、时间线和建议动作如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


## 2026-04-06 状态更新

- 本任务提出时用于替代旧的 `implement-api-file-level-testing` 包装任务。
- 截至 `2026-04-06`，`tests/api/file_tests` 主线 salvage 已通过隔离 worktree 微批次完成并并入 `origin/main`：
  - `#58` `218a8611e`
  - `#59` `b67eeeb35`
  - `#60` `96dac2ea7`
  - `#61` `6c1fa87b3`
  - `#62` `2c1eaae08`
- 因此，这份文档不再代表“待执行主线任务”，而是保留为历史替代任务说明。
- 当前正式收口结论见：
  - `reports/governance/2026-04-06-api-file-tests-salvage-closeout.md`
- 唯一残留项是 root dirty worktree 内的 `tests/api/file_tests/test_tradingview_api.py` 格式等价差异；该项属于 root-dirty hygiene，不属于未完成的 mainline salvage。

## 背景

原 `implement-api-file-level-testing` 任务包不适合直接续跑，原因是：

- 当前仓库已存在较完整的 file-level 测试框架：
  - `tests/api/file_tests/`
  - `tests/api/file_tests/run_file_tests.py`
  - 多个 `test_*_api.py`
- 但 CI 仍然通过 `.github/workflows/api-file-tests.yml` 中的 readiness gate 判断其是否为 placeholder/mock 状态
- 这意味着问题已从“是否建立框架”转变为“如何让现有框架真正收口并进入主线”

## 新任务目标

将 API file-level testing 从“框架存在但有跳过门禁”推进为“基于当前代码真实可执行、可纳入主线质量门禁”的测试能力。

## 为什么仍值得继续

- 它对当前项目仍有积极作用：
  - 补强 API 模块级测试治理
  - 与当前前端/E2E/CI 收口方向一致
  - 可减少未来接口回归风险
- 继续做不会天然导致功能倒退，但前提是必须基于当前框架现状重建任务，不沿用旧进度数字

## 不再沿用的旧口径

以下旧口径不再作为执行依据：

- “62 文件 / 566 endpoint”的固定历史统计
- 原 `33/51` checklist 的逐条机械续跑
- 基于 placeholder/mock 时代定义的 pass/fail 口径

## 建议新范围

### Stage 1：现状基线化

1. 盘点当前 `tests/api/file_tests/` 的真实覆盖文件数
2. 盘点哪些文件仍是 placeholder/mock 逻辑
3. 盘点 CI readiness gate 依赖的关键判断点

### Stage 2：CI 收口

1. 删除或替换 `.github/workflows/api-file-tests.yml` 中的 placeholder readiness gate
2. 让 workflow 基于真实可执行能力判定，而不是文本 grep
3. 确保失败时能输出可用报告，而不是简单跳过

### Stage 3：执行收口

1. 选取一组真实 API file tests 跑通
2. 补齐缺失 fixtures / conftest / 启动依赖
3. 定义当前真实 coverage 基线

## 明确不做

- 不追求一次性把历史所有 endpoint 数字对齐
- 不直接重写整个 file-tests 框架
- 不把这项任务与目录治理主线混做

## 建议输出物

- 一份“当前 file-level testing 真实基线报告”
- 一份“CI readiness gate 替换方案”
- 一份缩小后的执行 checklist

## 建议审批口径

`同意创建 API file-level testing 收口任务，并先完成现状基线化与 CI gate 收口方案`
