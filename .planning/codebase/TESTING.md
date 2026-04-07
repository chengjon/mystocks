# Testing

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或专题文档，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 当前执行口径请优先遵循 `architecture/STANDARDS.md`、根目录 `AGENTS.md`，并结合当前代码实现与主线治理文档使用。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码或主线文档冲突，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、当前代码与主线治理文档为准。


**Last mapped**: 2026-04-05

## Test Framework

- **Python**: pytest with coverage (pytest-cov)
- **Frontend**: Vitest + Playwright (E2E)
- **Contract**: Schemathesis (API contract testing)
- **Chaos**: Custom resilience framework

## Test Structure

```
tests/                              # 908 Python test files
├── chaos/                          # 混沌/弹性测试
│   ├── test_resilience_framework.py
│   ├── test_fault_injection.py
│   ├── _resilience_framework_support.py
│   └── _fault_injection_support.py
├── ci/                             # CI 集成测试
│   ├── test_continuous_integration.py
│   └── run_pipeline.py
├── contract/                       # 契约测试
│   ├── test_contract_executor.py   # ⚠️ 混合框架代码和测试
│   ├── test_contract_validator.py
│   ├── test_contract_generator.py
│   ├── contract_engine.py          # ⚠️ 框架代码在 tests/ 中
│   └── report_generator.py        # ⚠️ 非测试文件
├── api/file_tests/                 # API 文件测试
│   └── test_strategy_list_mock_api.py
├── unit/                           # 单元测试
│   └── storage/database/           # 数据库单元测试
├── test_api_endpoints.py           # ⚠️ 手动脚本，非 pytest
├── test_factory_smart.py
├── test_security_xss_csrf.py
└── [其他独立测试文件]
```

Frontend tests:
```
web/frontend/src/
├── stores/__tests__/               # Store 测试
│   ├── auth-guard.spec.ts
│   └── store-factory.spec.ts
├── views/artdeco-pages/*/          # 组件级 spec 文件
│   └── __tests__/*.spec.ts
└── tests/                          # 前端测试目录
```

## Test Quality Concerns

### Quantity vs Quality
- **908 test files** is a large number, but quality varies:
  - `tests/test_api_endpoints.py` — manual script using `requests` library with `print()` statements, no `assert`, no pytest markers
  - `tests/contract/test_contract_executor.py` — mixes framework infrastructure (`TestExecutionMode` enum, `TestCase` dataclass) with actual tests
  - Framework code (`contract_engine.py`, `report_generator.py`) lives in `tests/` directory

### Coverage Gap
- Last measured: **0.16%** (2026-01-03) — likely stale
- File count suggests high coverage, but **real coverage unknown** without running `pytest --cov`
- Core modules (data_access, adapters, core) previously had 0% test coverage

### Test File Naming
- Python: `test_*.py` and `*_test.py` conventions
- Frontend: `*.spec.ts` convention
- Non-test files in `tests/` dilute the count

## E2E Testing

- **Playwright** configured with 6 different config files in `config/playwright/`
- Historical baseline: 18/18 passed (Phase 6)
- Per governance charter: E2E results must report actual execution suite, not historical numbers

## Recommendations

1. Run `pytest --co -q` to get actual test case count (vs file count)
2. Run `pytest --cov=src --cov=web/backend --cov-report=term-missing` for real coverage
3. Move framework code out of `tests/` into `src/` or `conftest.py`
4. Convert manual scripts (`test_api_endpoints.py`) to proper pytest tests
5. Validate all 908 files are collected by pytest (`pytest --collect-only`)
