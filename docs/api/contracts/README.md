# API 契约管理

> **版本**: 1.0 | **更新日期**: 2026-07-12
> **维护者**: 后端架构
> **合并来源**: `CONTRACT_MANAGEMENT_API.md`（管理平台 REST API）+ `CONTRACT_TESTING_API.md`（测试框架 Python API）
> **源码级细节归档**: [archive/api-standalone-docs/contract-management-api-full.md](../../archive/api-standalone-docs/contract-management-api-full.md) + [archive/api-standalone-docs/contract-testing-api-full.md](../../archive/api-standalone-docs/contract-testing-api-full.md)

---

## 概览

MyStocks 契约管理体系包含三层：

| 层 | 组件 | 入口 |
|---|---|---|
| 规范层 | OpenAPI YAML 规范文件 | [market_api.yaml](market_api.yaml) |
| 管理层 | 契约管理平台 REST API | `POST /api/contracts/*` |
| 测试层 | 契约测试框架 Python API | `src.contract_testing` |

### 设计原则

1. **Schema First** — Pydantic 模型作为单一真相源
2. **Contract First** — 先更新契约，再修改代码
3. **语义化版本控制** — 遵循 SemVer (MAJOR.MINOR.PATCH)
4. **自动化验证** — 集成 CI/CD 流水线

---

## 规范文件

当前仓库维护一份主规范：

| 文件 | 用途 | 版本 |
|------|------|------|
| [market_api.yaml](market_api.yaml) | Market 模块完整 API 规范 | OpenAPI 3.1.0 |

其他模块规范按需添加到本目录，命名规则：`<module>_api.yaml`。

### 编辑规范

1. 修改前先运行 `bash scripts/dev/ci/validate_contracts.sh`
2. 检测破坏性变更：`bash scripts/dev/ci/detect_breaking_changes.sh`
3. PR 触发 `api-contract-validation.yml` 自动校验

---

## 契约管理平台 API

> 完整源码级文档见 [归档版本](../../archive/api-standalone-docs/contract-management-api-full.md)

提供契约版本管理、差异检测、验证和同步的 REST 接口。

### 端点清单

| # | 端点 | 方法 | 说明 |
|---|------|------|------|
| 1.1 | `/api/contracts/versions` | POST | 创建契约版本 |
| 1.2 | `/api/contracts/versions/{id}` | GET | 获取指定版本 |
| 1.3 | `/api/contracts/versions/{id}/activate` | POST | 获取当前激活版本 |
| 1.4 | `/api/contracts/versions` | GET | 列出所有版本 |
| 1.5 | `/api/contracts/versions/{id}` | PUT | 更新版本 |
| 1.6 | `/api/contracts/versions/{id}/activate` | POST | 激活指定版本 |
| 1.7 | `/api/contracts/versions/{id}` | DELETE | 删除版本 |
| 2.1 | `/api/contracts` | GET | 列出所有契约 |
| 3.1 | `/api/contracts/diff` | POST | 对比版本差异 |
| 4.1 | `/api/contracts/validate` | POST | 验证 OpenAPI 规范 |
| 5.1 | `/api/contracts/sync` | POST | 同步契约到代码 |

### 专属错误码

| 错误码 | HTTP | 说明 |
|--------|------|------|
| CONTRACT_VERSION_NOT_FOUND | 404 | 契约版本不存在 |
| CONTRACT_NOT_FOUND | 404 | 契约不存在或无激活版本 |
| CONTRACT_ALREADY_EXISTS | 409 | 版本已存在 |
| CONTRACT_VALIDATION_FAILED | 422 | 验证失败 |
| CONTRACT_DELETE_ACTIVE_VERSION | 409 | 不能删除激活版本 |
| CONTRACT_DIFF_FAILED | 500 | 差异检测失败 |
| CONTRACT_SYNC_FAILED | 500 | 同步失败 |

---

## 契约测试框架

> 完整源码级文档见 [归档版本](../../archive/api-standalone-docs/contract-testing-api-full.md)

Python 测试框架，提供 OpenAPI 规范验证、契约一致性检测和测试报告生成。

### 核心类

| 类 | 模块路径 | 用途 |
|---|---|---|
| `SpecificationValidator` | `src.contract_testing` | OpenAPI 规范加载、验证与解析 |
| `TestHooksManager` | `src.contract_testing` | 测试生命周期钩子管理 |
| `APIConsistencyChecker` | `src.contract_testing` | API 实现 vs 规范一致性检测 |
| `ContractTestEngine` | `src.contract_testing` | 测试编排引擎 |
| `ContractTestReportGenerator` | `src.contract_testing` | 多格式报告生成（JSON/Markdown/HTML） |

### 使用示例

```python
from src.contract_testing import (
    SpecificationValidator,
    ContractTestEngine,
    ContractTestReportGenerator,
)

# 1. 加载规范
validator = SpecificationValidator('openapi.json')

# 2. 运行测试
engine = ContractTestEngine('openapi.json')
engine.register_test_handler("GET /api/users", test_users)
results = engine.run_all()

# 3. 生成报告
generator = ContractTestReportGenerator()
generator.add_test_results(results)
generator.generate_html('report.html')
```

---

## 集成与联动

| 工作流 | 触发 | 作用 |
|--------|------|------|
| `api-contract-validation.yml` | PR | 契约语法校验 |
| `api-compliance-testing.yml` | PR | 契约合规测试 |
| `api-automation-discovery.yml` | push | 自动发现新 API |
| `contract-testing.yml` | PR | 契约测试对比 |

---

## 相关文档

- [API 契约管理手册](../index.md)
- [错误码与异常处理](../error-codes.md)
- [Apifox 使用指南](../apifox-guide.md)
- [API 集成指南](../integration.md)
- [架构红线](../../../architecture/STANDARDS.md)
