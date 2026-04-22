# Testing Guidance

> **导航说明**:
> 本文件是 `docs/testing/` 的 canonical guidance trunk，用于测试策略、E2E 执行、环境准备与质量复盘导航。
> 它不是当前测试门禁基线、实时通过率或共享规则本身；这些口径以 `architecture/STANDARDS.md` 与实际验证结果为准。

## Start Here

- 测试策略与流程：
  [`测试策略与规范.md`](/opt/claude/mystocks_spec/docs/testing/测试策略与规范.md)
- 前端运行门禁与交付收口：
  [`e2e/README.md`](/opt/claude/mystocks_spec/docs/testing/e2e/README.md),
  [`PR_GATE_QUICK_REFERENCE.md`](/opt/claude/mystocks_spec/docs/guides/frontend/PR_GATE_QUICK_REFERENCE.md),
  [`PM2_INTEGRATION_TEST_WORKFLOW.md`](/opt/claude/mystocks_spec/docs/guides/pm2/PM2_INTEGRATION_TEST_WORKFLOW.md)
- E2E 执行与调试：
  [`E2E_TEST_GUIDE.md`](/opt/claude/mystocks_spec/docs/testing/E2E_TEST_GUIDE.md),
  [`E2E_TEST_DEBUG_METHODS.md`](/opt/claude/mystocks_spec/docs/testing/E2E_TEST_DEBUG_METHODS.md),
  [`e2e/README.md`](/opt/claude/mystocks_spec/docs/testing/e2e/README.md)
- 环境准备与常见问题：
  [`TEST_ENVIRONMENT_REQUIREMENTS.md`](/opt/claude/mystocks_spec/docs/testing/TEST_ENVIRONMENT_REQUIREMENTS.md),
  [`常见测试问题与解决方案.md`](/opt/claude/mystocks_spec/docs/testing/常见测试问题与解决方案.md)
- 复盘与分析：
  [`BUGFIX-signals-500-error-retrospective.md`](/opt/claude/mystocks_spec/docs/testing/BUGFIX-signals-500-error-retrospective.md),
  [`技术债务分析报告.md`](/opt/claude/mystocks_spec/docs/testing/技术债务分析报告.md),
  [`测试价值分析报告.md`](/opt/claude/mystocks_spec/docs/testing/测试价值分析报告.md)

## Reader Routing

- 若问题是测试门禁、E2E 报告口径或类型债基线：
  先看 [`architecture/STANDARDS.md`](/opt/claude/mystocks_spec/architecture/STANDARDS.md)
- 若问题是“前端运行门禁核查与回归清单”或要找统一命令入口：
  先看 [`PR_GATE_QUICK_REFERENCE.md`](/opt/claude/mystocks_spec/docs/guides/frontend/PR_GATE_QUICK_REFERENCE.md)
  再看 [`e2e/README.md`](/opt/claude/mystocks_spec/docs/testing/e2e/README.md)
- 若问题是具体测试执行：
  先看 [`E2E_TEST_GUIDE.md`](/opt/claude/mystocks_spec/docs/testing/E2E_TEST_GUIDE.md) 与 [`e2e/README.md`](/opt/claude/mystocks_spec/docs/testing/e2e/README.md)
- 若问题是 PM2 正式门禁、容器 smoke 或本地复现 CI 交付摘要：
  先看 [`PM2_INTEGRATION_TEST_WORKFLOW.md`](/opt/claude/mystocks_spec/docs/guides/pm2/PM2_INTEGRATION_TEST_WORKFLOW.md)
- 若问题是历史阶段性计划：
  `phase4-plan.md`、`test-system-plan.md` 与 `test-system-analysis.md` 只作为 plan/supporting material，不应被视为当前 trunk
- 若需要历史中文测试资料：
  改为从归档目录查看 [`archive/docs/testing/legacy-cn-2026-04-08/`](/opt/claude/mystocks_spec/archive/docs/testing/legacy-cn-2026-04-08/)

## Supporting Compatibility Entries

- [`INDEX.md`](/opt/claude/mystocks_spec/docs/testing/INDEX.md) 仅作为旧链接兼容索引保留
- [`TESTING_GUIDE.md`](/opt/claude/mystocks_spec/docs/testing/TESTING_GUIDE.md),
  [`TESTING_EXAMPLES.md`](/opt/claude/mystocks_spec/docs/testing/TESTING_EXAMPLES.md),
  [`E2E_TEST_QUICK_REFERENCE_COMPATIBILITY.md`](/opt/claude/mystocks_spec/docs/testing/E2E_TEST_QUICK_REFERENCE_COMPATIBILITY.md)
  继续作为 compatibility/supporting docs 保留

## Governance Status

- `docs/testing/README.md` 保留为唯一 testing trunk
- `docs/testing/legacy-cn/` 已迁出 active tree，避免历史资料继续混入当前 guidance
- 后续 cleanup 应围绕 active testing families 执行，而不是继续堆积根级索引与历史快照
