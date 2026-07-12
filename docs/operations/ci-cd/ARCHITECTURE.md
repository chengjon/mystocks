# MyStocks CI/CD 体系架构

> 本文件是 CI/CD 体系的权威索引，与代码库事实对齐。
> 最后核对: 2026-07-12 | workflow 总数: 36 | CI 专题文档: 11

## 文档分布（三处）

| 位置 | 文档数 | 用途 |
|------|--------|------|
| `docs/operations/ci-cd/` | 11 | CI/CD 专题文档（核心，文档收敛到此家族） |
| `docs/api/` | 2 | API 契约/部署相关 CI/CD |
| `docs/testing/e2e/` | 1 | E2E 测试的 CI/CD 架构（三层测试） |

## 三层管道架构

```
┌───────────────────────────────────────────────────────────────────┐
│                       MyStocks CI/CD Pipeline                      │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐    ┌───────────────────┐    ┌───────────────┐   │
│  │  Layer 1     │    │   Layer 2         │    │   Layer 3     │   │
│  │  本地开发     │───→│  GitHub Actions   │───→│  部署/监控    │   │
│  │  pre-commit  │    │  36个workflow     │    │  PM2/Grafana  │   │
│  └──────────────┘    └───────────────────┘    └───────────────┘   │
│         │                     │                       │            │
│         ▼                     ▼                       ▼            │
│  • Black 格式化        • P0质量门禁            • deploy.yml       │
│  • Ruff lint           • 类型检查              • 健康检查         │
│  • MyPy 类型检查       • smoke-test.yml        • cicd_monitor     │
│  • Bandit 安全扫描     • E2E/Playwright        • Prometheus/Grafana│
│  • local_ci_check.sh   • 安全/合规扫描         • 回滚机制         │
│  • smoke_test.py       • 覆盖率/性能                              │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

## Layer 1: 本地开发

### pre-commit hooks (`.pre-commit-config.yaml`)

执行顺序: Black → Ruff selective fix → Ruff final check → MyPy → Bandit → Safety

| Hook | 作用 | 触发 |
|------|------|------|
| Black | Python 格式化 | 提交 .py 文件 |
| Ruff | Lint + selective fix | 提交 .py 文件 |
| MyPy | 静态类型检查 | 提交 src/ 核心文件 |
| Bandit | 安全漏洞扫描 | 提交源代码 |
| Safety | 依赖安全检查 | requirements 变更 |

### 本地 CI 脚本 (`scripts/dev/ci/`)

| 脚本 | 用途 |
|------|------|
| `local_ci_check.sh` | 快速质量验证（格式+类型+安全+单测+策略验证） |
| `cicd_monitor_integration.py` | CI/CD 监控集成（Prometheus 指标采集） |
| `compare_contracts.py` | API 契约对比 |
| `validate_contracts.sh` | API 契约验证 |
| `detect_breaking_changes.sh` | 检测破坏性变更 |
| `data_security_check.py` | 数据安全检查 |
| `quant_strategy_validation.py` | 量化策略验证 |
| `artdeco_trading_center_validation.py` | ArtDeco 交易中心验证 |

### 冒烟测试 (新增)

| 脚本 | 用例数 | 耗时 |
|------|--------|------|
| `smoke_test.py` | 23 (2服务+1登录+15API+5页面) | 6s |
| `scripts/ci/run_local_ci.py --quick` | 4 (服务+冒烟) | 19s |
| `scripts/ci/run_local_ci.py` | 7 (服务+lint+format+单测+冒烟) | 38s |

### Python CI 管道 (`tests/ci/`)

| 文件 | 用途 |
|------|------|
| `run_pipeline.py` | 管道运行器，导出 `get_ci_check_steps()` 和 `get_full_pipeline_steps()` |
| `test_continuous_integration.py` | CI 管理器核心 (705行): PipelineConfig → PipelineStep → TestSuite |
| `_continuous_integration_tail.py` | CI 管理器扩展 mixin (200行) |

```
get_ci_check_steps():
  1. ruff lint
  2. ruff format --check
  3. mypy type-check
  4. pytest tests/unit

get_full_pipeline_steps():
  5. pytest tests/integration
  6. E2E tests (Playwright)
```

## Layer 2: GitHub Actions (36 个 workflow)

### 主干流程 (4个)

| 工作流 | 触发 | 用途 |
|--------|------|------|
| `ci-cd.yml` | push/PR → main/develop | 主干 CI 管道 |
| `ci-cd-with-type-checking.yml` | push/PR | 带类型检查的 CI 管道 |
| `p0-quality-gate.yml` | PR → main/develop | P0 质量门禁（阻止合并） |
| `smoke-test.yml` | push/PR → main/develop | 冒烟测试（新增） |

### 部署 (1个)

| 工作流 | 触发 | 用途 |
|--------|------|------|
| `deploy.yml` | develop自动 / main手动审批 | 部署到 staging/production |

### 治理/合规 (4个)

| 工作流 | 用途 |
|--------|------|
| `mainline-governance.yml` | 主线治理 |
| `directory-compliance.yml` | 目录结构合规 |
| `deletion-waiver-audit.yml` | 删除豁免审计 |
| `cicd-monthly-review.yml` | CI/CD 月度审查 |

### 类型检查 (2个)

| 工作流 | 用途 |
|--------|------|
| `python-type-check.yml` | Python 类型检查 |
| `typescript-type-check.yml` | TypeScript 类型检查 |

### 测试矩阵 (21个)

| 工作流 | 用途 |
|--------|------|
| `comprehensive-testing.yml` | 综合测试 |
| `test-coverage.yml` | 测试覆盖率 |
| `coverage-expansion.yml` | 覆盖率扩展 |
| `contract-testing.yml` | 契约测试 |
| `e2e-testing.yml` / `e2e-tests.yml` / `e2e-tests-enhanced.yml` / `e2e-test.yml` | E2E 测试（4个变体） |
| `api-file-tests.yml` | API 文件级测试 |
| `api-contract-validation.yml` | API 契约验证 |
| `api-compliance-testing.yml` | API 合规测试 |
| `api-automation-discovery.yml` | API 自动化发现 |
| `frontend-testing.yml` | 前端测试 |
| `data-sync-testing.yml` | 数据同步测试 |
| `performance-testing.yml` | 性能测试 |
| `playwright.yml` | Playwright 浏览器测试 |
| `visual-testing.yml` | 视觉回归测试 |
| `visual-baseline-update.yml` | 视觉基线更新 |
| `ai-test-optimization.yml` | AI 测试优化 |
| `code-quality.yml` | 代码质量 |
| `monitoring-validation.yml` | 监控验证 |

### 安全 (2个)

| 工作流 | 用途 |
|--------|------|
| `security-testing.yml` | 安全测试 |
| `security-enhancement.yml` | 安全增强 |

### 策略验证 (2个)

| 工作流 | 用途 |
|--------|------|
| `quantum-strategy-validation.yml` | 量子策略验证 |
| `quant-strategy-validation.yml` | 量化策略验证 |

## Layer 3: 部署与监控

### 部署 (`deploy.yml`)

```
develop push → staging (自动)
main push    → production (手动审批 + confirm_deployment)
```

### 监控 (`scripts/dev/ci/cicd_monitor_integration.py`)

- Prometheus 指标采集 (`localhost:9090`)
- Grafana 监控面板 (`localhost:3000`)
- 告警通知

## 单元测试守护 CI 基础设施

`tests/unit/scripts/` 下有专门验证 CI/CD 基础设施本身的测试：

| 测试文件 | 用途 |
|----------|------|
| `test_ci_workflow_runtime_setup.py` | 验证 workflow 运行时依赖 |
| `test_repository_hygiene_paths.py` | 校验 CI/CD 文档收敛到 `operations/ci-cd/` 家族 |
| `test_deletion_waiver_audit_workflow.py` | 验证删除豁免审计 workflow |
| `test_deletion_evidence_gate.py` | 删除证据门禁 |
| `test_deletion_evidence_gate_integration.py` | 删除证据门禁集成测试 |
| `test_stop_deletion_evidence_gate_hook.py` | 删除证据门禁 hook |

## 文档索引

### docs/operations/ci-cd/ (核心，11个)

| 文件 | 用途 |
|------|------|
| `ARCHITECTURE.md` | **本文件** — 体系架构总览 |
| `INDEX.md` | 文档索引 |
| `LOCAL_CI_INTEGRATION.md` | 本地开发 CI 集成 (pre-commit) |
| `MYSTOCKS_CI_CD_OPTIMIZATION_SYSTEM.md` | 企业级 CI/CD 优化体系 |
| `MYSTOCKS_CI_CD_DAILY_APPLICATION.md` | CI/CD 日常应用 |
| `CICD_CONTINUOUS_OPTIMIZATION.md` | 持续优化 |
| `CICD_TYPE_CHECK_INTEGRATION_GUIDE.md` | 类型检查集成 |
| `CICD_TYPE_CHECK_QUICK_REFERENCE.md` | 类型检查速查 |
| `PYTHON_QUALITY_ASSURANCE_WORKFLOW.md` | Python 质量保证 |
| `PYTHON_QUALITY_TOOLS_QUICK_REFERENCE.md` | Python 质量工具 |
| `QUALITY_GATE_MANAGEMENT.md` | 质量门禁管理 |

### docs/api/ (2个)

| 文件 | 用途 |
|------|------|
| `CI_CD_INTEGRATION_GUIDE.md` | CI/CD 集成总指南 (pre-commit + 告警，523行) |
| `CI_CD_Validation_Extension_Guide.md` | 校验扩展 (安全/质量/集成/性能/AI，583行) |

### docs/testing/e2e/ (1个)

| 文件 | 用途 |
|------|------|
| `e2e-testing-ci-cd-architecture.md` | E2E 测试 CI/CD 架构 (三层测试：Mock单测→API集成→Playwright E2E) |

## 快速运行

```bash
# 冒烟测试（最快验证）
python3 smoke_test.py

# 本地 CI（快速模式）
python3 scripts/ci/run_local_ci.py --quick

# 本地 CI（完整模式）
python3 scripts/ci/run_local_ci.py

# 现有 Python CI 管道
python3 tests/ci/run_pipeline.py

# pre-commit 全量检查
pre-commit run --all-files

# 本地 CI 脚本 (scripts/dev/ci/)
bash scripts/dev/ci/local_ci_check.sh
```