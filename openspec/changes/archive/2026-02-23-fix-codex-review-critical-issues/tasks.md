# Tasks: Fix Codex Review Critical Issues

> **历史任务说明**:
> 本文件用于保留某次历史任务拆解、执行清单或阶段性待办，不代表当前仍需按原样执行。
> 其中的勾选状态、优先级和实施顺序仅对应当时上下文；继续沿用前应先对照 `architecture/STANDARDS.md`、当前需求、现行 specs 与实际仓库状态重新校准。


## 1. Critical Problem Fix ✅

- [x] 1.1 修复 `DecisionModelsAnalyzer` 类缩进错误
  - [x] 1.1.1 重新缩进 `__init__` 方法到类内部
  - [x] 1.1.2 重新缩进 `analyze` 方法到类内部
  - [x] 1.1.3 重新缩进 `_get_financial_data` 方法到类内部
  - [x] 1.1.4 重新缩进 `_generate_mock_financial_data` 方法到类内部
  - [x] 1.1.5 语法检查: `python -m py_compile`
  - [x] 1.1.6 AST 结构验证

## 2. Medium Problem Fix ✅

- [x] 2.1 修复 README.md 失效链接
  - [x] 2.1.1 创建链接检查脚本 `scripts/tools/check_readme_links.py`
  - [x] 2.1.2 运行链接审计
  - [x] 2.1.3 更新 `REORGANIZATION_COMPLETION_REPORT.md` 链接
  - [x] 2.1.4 更新 `PROJECT_MODULES.md` 链接
  - [x] 2.1.5 删除 6 个不存在文件的链接 (VALUECELL, example)
  - [x] 2.1.6 更新 `IFLOW.md` 链接
  - [x] 2.1.7 验证所有本地链接有效

- [x] 2.2 修正 GPU 文档路径
  - [x] 2.2.1 批量替换 `gpu_api_system/` → `src/gpu/api_system/`
  - [x] 2.2.2 验证无错误路径引用

## 3. Documentation ✅

- [x] 3.1 创建修复提案文档
  - [x] 3.1.1 `docs/reports/Code_Review_Fix_Proposal_V3.1_Strict.md`
- [x] 3.2 创建修复完成报告
  - [x] 3.2.1 `docs/reports/Code_Review_Fix_Completion_Report_V3.1.md`
- [x] 3.3 创建 OpenSpec 变更提案
  - [x] 3.3.1 `openspec/changes/fix-codex-review-critical-issues/proposal.md`
  - [x] 3.3.2 `openspec/changes/fix-codex-review-critical-issues/tasks.md`
  - [x] 3.3.3 `openspec/changes/fix-codex-review-critical-issues/specs/code-quality/spec.md`

## 4. Verification ✅

- [x] 4.1 运行完整验证脚本
  - [x] 4.1.1 Critical 问题验证 (语法 + AST 结构)
  - [x] 4.1.2 Medium 问题验证 (链接检查 + GPU 路径)
- [x] 4.2 所有验证通过

---

**Status**: ✅ 全部完成 (2026-02-23)
