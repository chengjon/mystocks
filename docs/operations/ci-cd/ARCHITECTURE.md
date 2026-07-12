# MyStocks CI/CD 体系架构

## 文档分布

CI/CD 相关文档分布在三个位置：

| 位置 | 说明 | 文档数 |
|------|------|--------|
| `docs/operations/ci-cd/` | CI/CD 专题文档（核心） | 10 |
| `docs/api/` | API/部署相关 CI/CD | 2 |
| `docs/testing/` | 测试 CI/CD 架构 | 1 |

## 三层管道架构

```
┌──────────────────────────────────────────────────────────────────┐
│                       MyStocks CI/CD Pipeline                     │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌──────────────────┐    ┌────────────────┐   │
│  │  Layer 1    │    │   Layer 2        │    │   Layer 3      │   │
│  │  本地开发    │───→│  GitHub Actions  │───→│  部署/监控     │   │
│  │  pre-commit │    │  远程CI管道       │    │  PM2/Prometheus│   │
│  └─────────────┘    └──────────────────┘    └────────────────┘   │
│         │                    │                      │             │
│         ▼                    ▼                      ▼             │
│  • ruff lint          • P0质量门禁           • deploy.yml        │
│  • black format       • 类型检查             • 健康检查          │
│  • 单元测试            • smoke_test.py        • cicd_monitor     │
│  • smoke_test.py      • E2E/Playwright        • 监控告警          │
│  • pre-commit hooks   • 安全扫描/合规                               │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## 现有 CI 基础设施

### 1. 本地 CI 管道 (Python)

核心: `tests/ci/run_pipeline.py` + `test_continuous_integration.py`

```
get_ci_check_steps() → 基础检查:
  1. ruff lint
  2. ruff format
  3. mypy type-check
  4. pytest unit tests

get_full_pipeline_steps() → 完整管道:
  5. pytest integration tests
  6. E2E tests (Playwright)
  7. 冒烟测试 (smoke_test.py)  ← 新增
```

运行: `python3 tests/ci/run_pipeline.py`

### 2. 冒烟测试

```
smoke_test.py (23个用例, 6秒)
├── 2 服务进程检查 (PM2)
├── 1 登录验证
├── 15 后端API
└── 5 前端页面
```

运行: `python3 smoke_test.py`

### 3. GitHub Actions 工作流

主干流程:

| 工作流 | 触发 | 用途 |
|--------|------|------|
| `ci-cd.yml` | push/PR → main/develop | 主干CI管道 |
| `p0-quality-gate.yml` | PR → main/develop | 质量门禁(阻止合并) |
| `smoke-test.yml` | push/PR → main/develop | 冒烟测试(新增) |
| `deploy.yml` | develop自动 / main手动 | 部署管道 |

其他工作流 (31个):

| 类别 | 工作流 |
|------|--------|
| 治理/合规 | `mainline-governance.yml`, `directory-compliance.yml`, `deletion-waiver-audit.yml`, `cicd-monthly-review.yml` |
| 类型检查 | `python-type-check.yml`, `typescript-type-check.yml` |
| 测试矩阵 | `comprehensive-testing.yml`, `test-coverage.yml`, `coverage-expansion.yml`, `contract-testing.yml`, `e2e-testing.yml`, `e2e-tests.yml`, `e2e-tests-enhanced.yml`, `e2e-test.yml`, `api-file-tests.yml`, `api-contract-validation.yml`, `api-compliance-testing.yml`, `api-automation-discovery.yml`, `frontend-testing.yml`, `data-sync-testing.yml`, `performance-testing.yml`, `playwright.yml`, `visual-testing.yml`, `visual-baseline-update.yml`, `ai-test-optimization.yml`, `code-quality.yml`, `monitoring-validation.yml` |
| 安全 | `security-testing.yml`, `security-enhancement.yml` |
| 策略验证 | `quantum-strategy-validation.yml`, `quant-strategy-validation.yml` |

### 4. 监控集成

`scripts/dev/ci/cicd_monitor_integration.py` — CI/CD 监控集成工具
- Prometheus 指标采集
- Grafana 监控面板
- 告警通知

## 文档索引

### docs/operations/ci-cd/ (核心 CI/CD 文档)

| 文件 | 用途 |
|------|------|
| `ARCHITECTURE.md` | 本文件 — CI/CD 体系架构总览 |
| `LOCAL_CI_INTEGRATION.md` | 本地开发环境 CI 集成 (pre-commit) |
| `MYSTOCKS_CI_CD_OPTIMIZATION_SYSTEM.md` | 企业级 CI/CD 优化体系 |
| `MYSTOCKS_CI_CD_DAILY_APPLICATION.md` | CI/CD 日常应用规划 |
| `CICD_CONTINUOUS_OPTIMIZATION.md` | 持续优化指南 |
| `CICD_TYPE_CHECK_INTEGRATION_GUIDE.md` | 类型检查集成 |
| `CICD_TYPE_CHECK_QUICK_REFERENCE.md` | 类型检查快速参考 |
| `PYTHON_QUALITY_ASSURANCE_WORKFLOW.md` | Python 代码质量保证 |
| `PYTHON_QUALITY_TOOLS_QUICK_REFERENCE.md` | Python 质量工具参考 |
| `QUALITY_GATE_MANAGEMENT.md` | 质量门禁管理 |

### docs/api/ (API/部署 CI/CD)

| 文件 | 用途 |
|------|------|
| `CI_CD_INTEGRATION_GUIDE.md` | CI/CD 集成总指南 (pre-commit + 告警) |
| `CI_CD_Validation_Extension_Guide.md` | CI/CD 校验扩展 (安全/质量/集成/性能) |

### docs/testing/ (测试 CI/CD)

| 文件 | 用途 |
|------|------|
| `e2e/e2e-testing-ci-cd-architecture.md` | E2E 测试的 CI/CD 架构 (三层测试) |

## 快速运行

```bash
# 冒烟测试 (推荐用于快速验证)
python3 smoke_test.py

# 本地 CI 管道 (完整)
python3 tests/ci/run_pipeline.py

# 监控集成
python3 scripts/dev/ci/cicd_monitor_integration.py
```