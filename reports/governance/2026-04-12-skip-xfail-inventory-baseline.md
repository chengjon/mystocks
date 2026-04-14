# Skip/XFail Inventory Baseline

> **补充规范说明**:
> 本文件用于把 `skip_xfail_count` 基线从单一数字展开为可审计清单。
> 规则口径以 `architecture/STANDARDS.md` 与 `docs/standards/technical-debt-governance-charter-v1.md` 为准。

**Generated:** 2026-04-12  
**Related debt item:** `TD-007`

## 1. Purpose

本文件用于：

- 解释 `skip_xfail_count = 102` 的来源。
- 建立逐项 inventory 初稿。
- 为后续测试债治理提供可分配对象。

## 2. Metric Snapshot

| metric | measured | baseline | inferred | target | source_or_command |
| --- | --- | --- | --- | --- | --- |
| `skip_xfail_count` | `102` | `102` | `initial draft reviewed subset = 17` | `<=102` | `reports/analysis/tech-debt-baseline.json` + repo grep |
| `repo_grep_raw_hits` | `119` | `N/A` | `broader than baseline scope` | `N/A` | `rg -n "pytest\\.mark\\.(skip|xfail|skipif)|@pytest\\.mark\\.(skip|xfail|skipif)|pytest\\.(skip|xfail)\\(|test\\.skip\\(" tests web/backend/tests src/governance/tests` |

说明：

- `102` 仍是当前治理基线。
- `119` 是本轮更宽 grep 口径下的 raw hits，包含 Playwright `test.skip(...)` 与部分可能不进入既有基线统计的命中。
- 后续应补一轮“baseline counting rule” 说明，避免 raw grep 与治理基线混用。

## 3. Inventory Schema

| file | test_or_marker | kind | reason | scope | owner | retention_decision | next_action |
| --- | --- | --- | --- | --- | --- | --- | --- |

字段约束：

- `kind`: `skip` | `xfail` | `conditional-skip`
- `retention_decision`: `accepted-temporary` | `needs-owner` | `cleanup-candidate`

## 4. Initial Inventory

| file | test_or_marker | kind | reason | scope | owner | retention_decision | next_action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `src/governance/tests/test_gpu_validator.py` | `@pytest.mark.skipif(cudf is None)` | `conditional-skip` | GPU optional dependency absent in common environments | governance-gpu | `backend` | `accepted-temporary` | 保持条件门禁，但补 owner / issue / ttl 口径 |
| `web/backend/tests/conftest.py` | `pytest.skip(FastAPI app not available...)` | `skip` | 测试环境初始化失败时整批后端测试会被跳过 | backend-test-harness | `test` | `needs-owner` | 区分“环境故障”与“测试无意义”，补更细粒度 gate |
| `web/backend/tests/test_auth.py` | `pytest.skip(PostgreSQL test database...)` | `skip` | 测试依赖专用 PostgreSQL 实例 | backend-auth | `backend` | `accepted-temporary` | 记录测试 DB 前置条件并评估容器化替代 |
| `web/backend/tests/test_market_api.py` | `pytest.skip(TDengine driver not installed)` | `skip` | 可选驱动缺失 | backend-market | `backend` | `accepted-temporary` | 标准化依赖检测说明 |
| `web/backend/tests/test_cache_manager.py` | `pytest.skip(TDengine may not be running...)` | `skip` | 外部 TDengine 服务不可用会导致多处跳过 | backend-cache | `backend` | `needs-owner` | 合并为共享 fixture / marker，减少重复 skip 分支 |
| `web/backend/tests/test_performance_benchmarks.py` | `@pytest.mark.skip("缓存是前端代码...")` | `skip` | 测试文件内存在范围漂移，后端套件承载前端缓存断言 | backend-performance | `test` | `cleanup-candidate` | 将无效后端范围测试迁出或删除 |
| `tests/e2e/test_login.py` | `@pytest.mark.skip(reason="需要真实API连接")` | `skip` | 真实 API 依赖未由当前默认 E2E harness 保证 | e2e-login | `test` | `needs-owner` | 明确是否保留为 nightly / manual 套件 |
| `tests/e2e/test_risk.py` | `@pytest.mark.skip(reason="需要真实数据连接")` | `skip` | 真实数据链路依赖未封装 | e2e-risk | `test` | `needs-owner` | 归并到真实数据子集并补执行条件 |
| `tests/unit/adapters/test_akshare_adapter_real.py` | `pytest.skip(... under xdist ...)` | `skip` | xdist 下收集崩溃，属于环境兼容问题 | adapters-real | `backend` | `accepted-temporary` | 建 issue 复核 xdist 兼容性 |
| `tests/integration/test_postgresql_integration.py` | `pytest.skip(... allow_module_level=True)` | `skip` | 模块级依赖 PostgreSQL 配置 | integration-db | `backend` | `accepted-temporary` | 继续容器化 / fixture 化替代 |
| `tests/conftest.py` | `skip_ai / skip_performance / skip_security / skip_chaos markers` | `skip` | 通过显式 CLI flag 控制高成本测试族 | global-test-gates | `test` | `accepted-temporary` | 保持门禁，但补汇总台账 |
| `tests/e2e/auth.spec.ts` | `test.skip(...)` | `skip` | Playwright case 被长期跳过，未见对应治理上下文 | frontend-e2e-auth | `frontend-governance` | `cleanup-candidate` | 复核这 3 个 case 是否仍应长期跳过 |
| `tests/unit/test_config_validation.py` | `@pytest.mark.skip(...)` | `skip` | 多个配置校验点以“未实现 / 未定义字段”长期跳过 | config-validation | `backend` | `cleanup-candidate` | 将 4 个跳过项拆成真实 schema debt 或删除过时 case |
| `tests/test_database_manager.py` | `pytest.skip("load_table_config method not implemented")` | `skip` | 用“未实现”掩盖接口缺口 | database-manager | `backend` | `cleanup-candidate` | 先判定方法是否应存在，再决定补实现或删测试 |
| `tests/data_sources/test_query_builder.py` | `@pytest.mark.skipif(not QUERY_BUILDER_AVAILABLE)` | `conditional-skip` | query builder 为可选能力，存在环境依赖 | data-sources | `backend` | `accepted-temporary` | 继续保留条件门禁，但补 capability 说明 |
| `tests/unit/adapters/test_akshare_adapter.py` | `module-level skip under xdist` | `skip` | xdist 收集崩溃兼容 | adapters-akshare | `backend` | `accepted-temporary` | 建 issue 后统一归并 real-adapter xdist 兼容问题 |
| `tests/unit/adapters/test_financial_adapter_real.py` | `allow_module_level=True import skip` | `skip` | 真实适配器导入与外部依赖耦合 | adapters-financial | `backend` | `needs-owner` | 明确真实适配器测试运行入口 |

## 5. Classification Rules

### accepted-temporary

适用于：

- 外部依赖或平台约束明确。
- 已能解释 skip 的环境原因。
- 适合作为条件门禁而不是永久逃逸。

### needs-owner

适用于：

- 原因存在但责任人或执行入口不清。
- 需要拆分“环境不可用”与“测试设计本身失真”。

### cleanup-candidate

适用于：

- 原因描述陈旧。
- 测试已明显超出所在套件职责。
- 长期 skip 但未见新的治理上下文。

## 6. Rollup Summary

| metric | value |
| --- | --- |
| `baseline_total` | `102` |
| `repo_grep_raw_hits` | `119` |
| `reviewed_in_draft` | `17` |
| `accepted_temporary_count` | `9` |
| `needs_owner_count` | `5` |
| `cleanup_candidate_count` | `3` |

### By Scope

| scope | count |
| --- | --- |
| `backend / db / external dependency` | `8` |
| `global test gating` | `1` |
| `frontend e2e` | `3` |
| `governance / gpu optional dependency` | `1` |
| `backend suite scope drift` | `1` |
| `config / schema legacy tests` | `2` |
| `adapter real-test import gates` | `2` |

### By Reason Bucket

| reason_bucket | count |
| --- | --- |
| `external service unavailable` | `5` |
| `optional dependency missing` | `4` |
| `real-data / real-api dependency` | `3` |
| `suite scope drift` | `1` |
| `explicit high-cost test gate` | `1` |
| `feature not implemented / stale expectation` | `3` |

## 7. Initial Priority Candidates

| rank | file | test_or_marker | reason | suggested_action |
| --- | --- | --- | --- | --- |
| 1 | `web/backend/tests/test_performance_benchmarks.py` | 2 direct skip markers | 后端套件里存在“前端缓存不在范围内”的明显漂移 | 迁出或删除无效 case |
| 2 | `tests/e2e/auth.spec.ts` | 3 `test.skip(...)` cases | 前端 E2E 存在长期跳过案例 | 逐个复核并恢复或删除 |
| 3 | `web/backend/tests/test_cache_manager.py` | repeated TDengine skip branches | 重复 skip 分支多，适合抽 shared fixture | 合并依赖探测逻辑 |
| 4 | `web/backend/tests/conftest.py` | app unavailable skip | 核心 harness 失败会掩盖整批测试 | 缩小 skip 爆炸半径 |
| 5 | `tests/e2e/test_login.py` | real API skip | 需明确是 nightly 还是废弃 | 归类到真实链路子集 |
| 6 | `tests/unit/test_config_validation.py` | 4 direct skip markers | 用长期 skip 承载 schema/feature debt | 拆为真实 debt item |
| 7 | `tests/test_database_manager.py` | not implemented skip | 可能是过时 API 预期 | 判定测试或实现谁该退场 |

## 8. Verification

建议命令：

```bash
rg -n "pytest\.mark\.(skip|xfail|skipif)|@pytest\.mark\.(skip|xfail|skipif)|pytest\.(skip|xfail)\(" tests web/backend/tests src/governance/tests
rg -n "\b(skip|xfail)\b" tests web/backend/tests src/governance/tests
awk -F: '{print $1}' /tmp/td007_skip_hits.txt | sed 's#/[^/]*$##' | sort | uniq -c | sort -nr
```

## 9. Exit Condition

`TD-007` 视为完成，当且仅当：

- `102` 的来源可解释。
- 每条记录都有 owner 或待分配结论。
- 至少形成一批 `cleanup-candidate`。
- 后续测试债治理可以直接按本清单切批次。
