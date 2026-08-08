# 测试手册

> **版本**: 1.0 | **更新日期**: 2026-07-12
> **维护者**: QA
> **文档类型**: 手册主页
> **上游入口**: [CORE.md](../CORE.md) → 测试角色

---

## 本手册范围

覆盖测试策略、E2E 执行、CI/CD 管道联动、质量门禁。

---

## 快速入口

| 场景 | 文档 | 简介 |
|------|------|------|
| 测试策略 | [testing/TEST_STRATEGY.md](../testing/TEST_STRATEGY.md) | 三层测试架构、覆盖率目标 |
| E2E 指南 | [testing/E2E_TEST_GUIDE.md](../testing/E2E_TEST_GUIDE.md) | Playwright 配置、用例编写、浏览器矩阵 |
| E2E CI/CD 架构 | [testing/e2e/e2e-testing-ci-cd-architecture.md](../testing/e2e/e2e-testing-ci-cd-architecture.md) | 三层测试 + tmux + lnav |
| CI/CD 总览 | [operations/ci-cd/ARCHITECTURE.md](../operations/ci-cd/ARCHITECTURE.md) | 36 workflow、三层管道、本地 CI |
| 质量门禁 | [operations/ci-cd/QUALITY_GATE_MANAGEMENT.md](../operations/ci-cd/QUALITY_GATE_MANAGEMENT.md) | 门禁管理、阈值、P0 质量门禁 |
| 冒烟测试 | [operations/ci-cd/ARCHITECTURE.md](../operations/ci-cd/ARCHITECTURE.md) | `smoke_test.py` 23 用例 |
| 治理门禁 | [operations/ci-cd/LOCAL_CI_INTEGRATION.md](../operations/ci-cd/LOCAL_CI_INTEGRATION.md) | pre-commit hooks 20 步 + 本地 CI 脚本 |

---

## 三层测试架构

```
Layer 1: Mock 单元测试 (tests/unit/)       → 快速反馈，pytest + unittest.mock
Layer 2: API 集成测试 (tests/integration/)  → requests + pytest
Layer 3: E2E 流程测试 (tests/e2e/)          → Playwright，多浏览器
```

对应 CI 本地命令：
```bash
# Layer 1
pytest tests/unit/

# Layer 2
pytest tests/integration/

# Layer 3
cd web/frontend && npm run test:e2e

# 全量
python3 tests/ci/run_pipeline.py
```

---

## CI 联动

| 触发 | workflow | 文档 |
|------|----------|------|
| PR → main/develop | `p0-quality-gate.yml` | [QUALITY_GATE_MANAGEMENT.md](../operations/ci-cd/QUALITY_GATE_MANAGEMENT.md) |
| push/PR | `ci-cd.yml` | [ARCHITECTURE.md](../operations/ci-cd/ARCHITECTURE.md) |
| 仅类型变更 | `python-type-check.yml` / `typescript-type-check.yml` | [CICD_TYPE_CHECK_INTEGRATION_GUIDE.md](../operations/ci-cd/CICD_TYPE_CHECK_INTEGRATION_GUIDE.md) |
| 月度审查 | `cicd-monthly-review.yml` | [CICD_CONTINUOUS_OPTIMIZATION.md](../operations/ci-cd/CICD_CONTINUOUS_OPTIMIZATION.md) |

---

## 验证命令速查

```bash
# 类型检查
mypy src/ --no-error-summary
cd web/frontend && npx vue-tsc --noEmit

# 代码质量
ruff check src/
black --check .
cd web/frontend && npx stylelint "src/**/*.{vue,scss,css}"

# 安全扫描
bandit -r src/
pip-audit  # 原 safety 升级

# 覆盖率
pytest --cov=src --cov-report=html
```

---

> 跨手册链接：开发入口 [dev/](../dev/index.md) · 运维入口 [ops/](../ops/index.md)
