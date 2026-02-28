# Change: Fix Codex Review Critical Issues

## Why

修复 Codex 代码审查报告 (`reviews/review-20260223-031831-9e70a2.md`) 中的 3 个问题，确保代码质量和文档可维护性。

**Critical 问题**: `DecisionModelsAnalyzer` 类缩进错误导致类结构损坏，影响分析器初始化和运行时行为。

**Medium 问题**: README.md 包含 14 个失效链接和错误 GPU 文档路径，影响用户导航和文档可维护性。

## What Changes

- **Critical**: 修复 `src/advanced_analysis/decision_models_analyzer.py` 类缩进错误
  - 重新缩进 4 个方法到类内部 (`__init__`, `analyze`, `_get_financial_data`, `_generate_mock_financial_data`)
  - 修复约 200 行代码缩进

- **Medium**: 修复 README.md 失效链接 (14 → 0)
  - 更新 8 个链接路径 (REORGANIZATION_COMPLETION_REPORT.md, PROJECT_MODULES.md, GPU 路径等)
  - 删除 6 个不存在文件的链接 (VALUECELL 报告、example 链接等)

- **Medium**: 修正 GPU 文档路径
  - 批量替换 `gpu_api_system/` → `src/gpu/api_system/`

- **工具**: 创建 README 链接验证工具
  - 新增 `scripts/tools/check_readme_links.py` 脚本
  - 支持本地链接验证、失效链接报告、正确退出码

## Impact

- **Affected specs**: `code-quality` (新增)
- **Affected code**:
  - `src/advanced_analysis/decision_models_analyzer.py` (Critical)
  - `README.md` (Medium)
  - 新增 `scripts/tools/check_readme_links.py`

- **Breaking changes**: 无

- **Migration required**: 无

## Related

- **Codex Review**: `reviews/review-20260223-031831-9e70a2.md`
- **Fix Proposal**: `docs/reports/Code_Review_Fix_Proposal_V3.1_Strict.md`
- **Completion Report**: `docs/reports/Code_Review_Fix_Completion_Report_V3.1.md`
- **User Feedback Issues**: 8 个问题已分离到 `optimize-web-menu-accessibility` 变更

## Status

✅ **已完成** - 所有修复已执行并通过验证
