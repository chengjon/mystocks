# 规则自动化缺口扫描（2026-03-10）

> **历史分析说明**:
> 本文件是阶段性分析、审计、评估或复盘材料，不是当前基线、当前实施优先级或仓库共享规则的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内问题分级、差距判断、风险结论、审阅意见和建议动作如未重新复核，应视为历史分析结果，不得直接当作当前事实。


## 扫描范围

- 规则来源：`architecture/STANDARDS.md`
- 自动化入口：
  - `.github/workflows/`
  - `.pre-commit-config.yaml`
  - `.githooks/`
  - `tests/unit/scripts/`
  - `scripts/hooks/`
  - `scripts/compliance/`

---

## 已自动化的治理门禁 / 规则

| 规则名 | 自动化实现文件 |
|---|---|
| Mainline 任务卡 / 变更范围治理 | `.github/workflows/mainline-governance.yml`；`governance/mainline/scripts/mainline_scope_gate.py`；`.pre-commit-config.yaml`（`mainline-governance-reminder`） |
| 目录结构 / 根目录规模 / 命名 / `__init__.py` 合规 | `.github/workflows/directory-compliance.yml`；`scripts/hooks/check_directory_structure.py`；`scripts/hooks/check_file_naming.py`；`scripts/hooks/check_init_py.py` |
| 文档落位治理 | `.pre-commit-config.yaml`（`documentation-placement`）；`scripts/hooks/check-documentation-placement.sh` |
| 前端页面配置一致性（路由 / `pageConfig.ts`） | `.pre-commit-config.yaml`（`page-config-validator`）；`scripts/hooks/check-page-config.mjs`；`tests/unit/test_pre_commit_config.py` |
| 生产 Python 大文件 / 裸 `print()` 门禁 | `.github/workflows/code-quality.yml`；`.pre-commit-config.yaml`（`production-python-guardrails`）；`.githooks/pre-commit`；`scripts/compliance/production_python_guardrails.py`；`tests/unit/scripts/test_production_python_guardrails.py` |
| 增量目录治理本地门禁 | `.pre-commit-config.yaml`（`directory-governance`）；`.githooks/pre-commit`；`scripts/maintenance/check-structure.sh`；`scripts/maintenance/check_structure.py` |
| 路由 / Layout 变更强制 PM2 E2E 门禁 | `.github/workflows/frontend-testing.yml`（`route-layout-pm2-detect`、`Route/Layout PM2 Gate`）；`scripts/compliance/route_layout_pm2_gate.py`；`scripts/run_e2e_pm2.sh`；`tests/unit/scripts/test_route_layout_pm2_gate.py` |
| ArtDeco token 使用门禁 | `.pre-commit-config.yaml`（`artdeco-token-lint`）；`.github/workflows/frontend-testing.yml`（`Run ArtDeco token lint`）；`web/frontend/package.json`（`lint:artdeco`）；`tests/unit/scripts/test_artdeco_token_gate_integration.py` |
| `/health/ready` + App 启动期 readiness 门禁 | `.pre-commit-config.yaml`（`observability-readiness-gate`）；`.github/workflows/code-quality.yml`（`Observability Readiness Gate`）；`scripts/compliance/readiness_contract_gate.py`；`web/backend/app/main.py`；`web/backend/app/core/readiness.py`；`web/frontend/src/App.vue`；`web/frontend/src/composables/useBackendReadiness.ts`；`tests/unit/scripts/test_readiness_contract_gate.py` |
| `App.vue` 路由纯净度门禁 | `.pre-commit-config.yaml`（`app-route-purity-gate`）；`.github/workflows/frontend-testing.yml`（`App Route Purity Gate`）；`scripts/compliance/app_route_purity_gate.py`；`tests/unit/scripts/test_app_route_purity_gate.py` |
| 业务 Tab `Request ID / TRACE_ID` 增量显位门禁 | `.pre-commit-config.yaml`（`request-id-visibility-gate`）；`.github/workflows/frontend-testing.yml`（`Request ID Visibility Gate`）；`scripts/compliance/request_id_visibility_gate.py`；`web/frontend/src/views/artdeco-pages/_templates/ArtDecoPageTemplate.vue`；`tests/unit/scripts/test_request_id_visibility_gate.py` |
| 后端单例 `global ... = None` 门禁 | `.pre-commit-config.yaml`（`backend-singleton-none-guard`）；`.github/workflows/code-quality.yml`（`Backend Singleton None Guard`）；`.githooks/pre-commit`；`scripts/compliance/backend_singleton_none_guard.py`；`tests/unit/scripts/test_backend_singleton_none_guard.py` |
| `UnifiedResponse` API 响应契约门禁 | `.pre-commit-config.yaml`（`unified-response-contract-guard`）；`.github/workflows/code-quality.yml`（`UnifiedResponse Contract Guard`）；`.githooks/pre-commit`；`scripts/compliance/unified_response_contract_guard.py`；`tests/unit/scripts/test_unified_response_contract_guard.py` |
| Vue / TS / 测试文件大小阈值门禁 | `.pre-commit-config.yaml`（`frontend-test-file-size-guard`）；`.github/workflows/code-quality.yml`（`Frontend/Test File Size Guard`）；`.githooks/pre-commit`；`scripts/compliance/file_size_guardrail.py`；`tests/unit/scripts/test_file_size_guardrail.py` |
| PM2 一等公民门禁 | `.pre-commit-config.yaml`（`pm2-first-class-gate`）；`.github/workflows/code-quality.yml`（`PM2 First-Class Gate`）；`.githooks/pre-commit`；`scripts/compliance/pm2_first_class_gate.py`；`tests/unit/scripts/test_pm2_first_class_gate.py` |
| TypeScript 类型检查 | `.pre-commit-config.yaml`（`typescript-check`）；`.github/workflows/frontend-testing.yml`；`.github/workflows/typescript-type-check.yml` |
| 前端类型债基线门禁 | `.github/workflows/typescript-type-check.yml`；`reports/analysis/tech-debt-baseline.json` |
| 硬编码扫描 / 例外注册有效性 | `.pre-commit-config.yaml`（`hardcoding-runtime-scan`、`hardcoding-exception-validator`）；`.github/workflows/code-quality.yml`；`scripts/security/hardcoding_scan.py`；`scripts/security/validate_hardcoding_exceptions.py` |
| 视图迁移登记门禁 | `.pre-commit-config.yaml`（`views-migration-gate`）；`scripts/hooks/check-views-migration-table.py` |
| Pre-commit 配置自身结构回归 | `tests/unit/test_pre_commit_config.py` |

---

## 明显仍缺失自动化的规则候选

以下候选是“规范里已经明确写了，但当前没有看到同等强度的 CI / pre-commit / githook 自动化门禁”，适合作为下一批治理目标：

1. 重构后废弃导入 / 残留模块引用清理门禁
2. 分层依赖 / 循环依赖门禁（对应“单体骨架”规则）
3. Mock 驱动开发门禁（前端页面在后端未就绪时仍可独立验收）

---

## 本轮扫描的直接结论

1. 当前已经补齐了一批“仓库治理型”自动化：
   - mainline 治理
   - 目录治理
   - 生产 Python guardrails
   - 前端类型检查 / 类型债基线
   - 硬编码治理
   - 页面配置 / 迁移登记

2. 仍然缺口最大的，是 `architecture/STANDARDS.md` 里偏“运行时架构约束”的规则：
   - 废弃导入残留引用
   - 分层依赖 / 循环依赖门禁
   - Mock 驱动开发门禁

3. 其中最值得优先自动化的下一批建议顺序：
   1. 分层依赖 / 循环依赖门禁
   2. 废弃导入 / 残留模块引用清理门禁
   3. Mock 驱动开发门禁
