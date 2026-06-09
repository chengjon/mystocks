# 技术债务分析报告 — MyStocks

> 生成日期: 2026-05-31 | 基线版本: 2026-05-04 (v1) | 治理阶段: Stage B (清理高风险库存)
> 方法论: tech-debt-checker skill v1.0 — 6 维度分类法 (D1–D6)
> 基线文件: `reports/analysis/tech-debt-baseline.json`
> 治理章程: `docs/standards/technical-debt-governance-charter-v1.md`

---

## 执行摘要

| 指标 | 状态 |
|------|------|
| 总体门禁 | ✅ PASS |
| D1 代码质量 | C (lint 问题多，大文件严重) |
| D3 测试质量 | B (skip/xfail 大幅改善，占位断言偏高) |
| D4 文档覆盖 | A (99.6% API 文档化) |
| D5 依赖健康 | A (0 过期依赖，0 CVE) |
| D6 过程/安全 | C (SAST 问题 1089 项，多为 S311/S101) |

**关键发现**: 所有门控指标通过或优于基线。skip/xfail 从基线 102 降至 17（改善 83%）。主要风险在 D1 代码质量：179 个 Python 大文件超标（top: test_health_route_conflicts.py 3192 行），Ruff lint 175 个问题（F821 占 76），以及 SAST 安全扫描 1089 个问题。前端 `all.ts`（2448 行）需优先拆分。

---

## D1: 代码质量

### 1.1 类型检查

| 指标 | 当前值 | 基线值 | 变化 | 状态 |
|------|--------|--------|------|------|
| 前端类型错误 (vue-tsc) | 0 | 0 | — | ✅ 门控通过 |
| 前端抑制标记 (@ts-ignore 等) | 0 | 1 | ↓1 | ✅ 改善 |
| 后端类型抑制 (# type:ignore) | 30 | — | 新增监测 | ℹ️ 观察 |

### 1.2 静态分析 (Ruff Lint)

**检测范围**: `src/` + `web/backend/app/`

| 指标 | 当前值 | 基线值 | 变化 | 状态 |
|------|--------|--------|------|------|
| Ruff 问题总数 | 175 (65 文件) | ~42 | ↑ | ⚠️ 需关注 |
| 可自动修复 | 10 | — | — | — |

**按规则分类 (Top 10)**:

| 规则 | 数量 | 说明 |
|------|------|------|
| F821 | 76 | 未定义名称 |
| F401 | 21 | 导入未使用 |
| invalid-syntax | 17 | 语法错误 |
| E701 | 15 | 单行多条语句 |
| E722 | 12 | 裸 except |
| F811 | 10 | 重复定义 |
| PT028 | 9 | pytest fixture 参数问题 |
| F601 | 6 | 字典键重复 |
| F823 | 4 | 未定义名称 (行号引用) |
| F403 | 3 | 通配符导入 |

**热点文件 (Lint)**:

| 文件 | 问题数 | Top 规则 |
|------|--------|----------|
| `src/adapters/__init__.py` | 15 | F401(未使用导入) |
| `src/monitoring/alerts.py` | 11 | F821(未定义名称) |
| `src/gpu/backtrace_engine.py` | 9 | F401(未使用导入) |
| `src/adapters/fetch_write.py` | 9 | F821(未定义名称) |
| `src/monitoring/stats_health.py` | 9 | F821(未定义名称) |
| `src/ml_strategy/technical_analysis.py` | 7 | F821(未定义名称) |
| `src/ml_strategy/naive_bayes_trading_strategy.py` | 6 | invalid-syntax |
| `src/monitoring/audit_system.py` | 5 | F811+invalid-syntax |
| `src/data_access/data_api_new.py` | 5 | F821(未定义名称) |
| `web/backend/app/api/_alerts_responses.py` | 5 | F821(未定义名称) |

### 1.3 安全扫描 (Ruff S-rules)

**检测范围**: `src/` + `web/backend/app/` + `tests/`

| 指标 | 当前值 |
|------|--------|
| 安全问题总数 | 1089 (197 文件) |

**按规则分类 (Top 5)**:

| 规则 | 数量 | 说明 | 风险等级 |
|------|------|------|----------|
| S311 | 576 | 使用 random 模块（非加密安全） | 中 |
| S101 | 269 | 测试中使用 assert | 低（仅测试） |
| S608 | 101 | SQL 注入风险 | 高 |
| S110 | 58 | try-except-pass（吞异常） | 中 |
| S324 | 18 | hashlib 不安全算法 | 中 |

> **注**: S101(269) 全部在 `tests/` 目录，属于正常测试实践。S311(576) 主要在非安全敏感的随机数场景。S608(101) SQL 注入风险需人工审查。

### 1.4 大文件 (超出行数限制)

**Python 文件 (>500 行，限制 800)**: 179 个文件超标

| Top 15 文件 | 行数 | 限制 | 超出 |
|-------------|------|------|------|
| `tests/e2e/test_health_route_conflicts.py` | 3192 | 800 | +2392 |
| `web/backend/app/main.py` | 894 | 800 | +94 |
| `tests/unit/test_api_documentation_validation.py` | 859 | 800 | +59 |
| `src/ml_strategy/technical_analysis_service.py` | 838 | 800 | +38 |
| `src/monitoring/monitoring_service.py` | 788 | 500 | — |
| `src/core/database_table_manager/core.py` | 778 | 500 | — |
| `src/monitoring/monitoring_database/core.py` | 734 | 500 | — |
| `src/data_access/data_access.py` | 720 | 500 | — |
| `src/ml_strategy/backtest_service.py` | 717 | 500 | — |
| `src/core/config_manager.py` | 693 | 500 | — |
| `src/gpu/gpu_backtest_service.py` | 680 | 500 | — |
| `src/adapters/akshare_adapter.py` | 664 | 500 | — |
| `src/ml_strategy/ml_strategy_service.py` | 657 | 500 | — |
| `src/monitoring/alert_manager.py` | 645 | 500 | — |
| `web/backend/app/services/monitoring_service.py` | 628 | 500 | — |

**前端文件 (>500 行，限制 500)**: 33 个文件超标

| Top 15 文件 | 行数 | 限制 | 超出 |
|-------------|------|------|------|
| `web/frontend/src/api/all.ts` | 2448 | 500 | +1948 |
| `web/frontend/src/views/artdeco-pages/ArtDecoStrategyManagement.vue` | 1033 | 500 | +533 |
| `web/frontend/tests/auth-guard.spec.ts` | 982 | 500 | +482 |
| `web/frontend/src/viewmodels/backtestAnalysisViewModel.ts` | 967 | 500 | +467 |
| `web/frontend/src/views/market/Screener.vue` | 908 | 500 | +408 |
| `web/frontend/src/views/data/MarketOverview.vue` | 877 | 500 | +377 |
| `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue` | 859 | 500 | +359 |
| `web/frontend/src/views/strategy/StrategyDashboard.vue` | 826 | 500 | +326 |
| `web/frontend/src/stores/market.ts` | 812 | 500 | +312 |
| `web/frontend/src/views/risk/RiskDashboard.vue` | 798 | 500 | +298 |
| `web/frontend/src/views/trade/TradeDashboard.vue` | 787 | 500 | +287 |
| `web/frontend/src/views/risk/RiskWarning.vue` | 773 | 500 | +273 |
| `web/frontend/src/api/strategy.ts` | 766 | 500 | +266 |
| `web/frontend/src/views/data/DataDashboard.vue` | 763 | 500 | +263 |
| `web/frontend/src/views/system/SystemSettings.vue` | 752 | 500 | +252 |

---

## D2: 架构与设计

> 本次未进行专项架构分析（无自动化工具）。基于大文件数量和 lint 分布的间接评估：

- **179 个 Python 大文件** 暗示可能存在 God Class / 模块职责过度集中
- **F821(76 个未定义名称)** 暗示可能存在循环导入或模块依赖问题
- `app/main.py`(894 行) 暗示 FastAPI 路由注册可能需拆分
- **all.ts(2448 行)** 是明确的聚合文件，需按领域拆分

---

## D3: 测试质量

| 指标 | 当前值 | 基线值 | 变化 | 状态 |
|------|--------|--------|------|------|
| skip/xfail 数量 | 17 | 102 | ↓83% | ✅ 门控通过 |
| 占位断言 (pass in tests) | 220 | 0 | ↑220 | ⚠️ 待确认 |
| skip/xfail 含 debt-exception 注解 | 15/17 | — | — | ✅ 合规 |

**skip/xfail 改善分析**: 基线 102 → 当前 17，改善 83%。其中 15 个已有 debt-exception 注解（含 owner/issue/ttl），仅 2 个缺少注解。

**占位断言说明**: 基线值为 0，当前 220。基线生成时可能使用了不同的 grep 模式（仅匹配 `pass` 独占行 vs 匹配含 `pass` 的所有行），需确认测量口径一致性后才能判定是否为真实回归。

---

## D4: 文档覆盖

| 指标 | 当前值 | 基线值 | 变化 | 状态 |
|------|--------|--------|------|------|
| API 端点总数 | 498 | 498 | — | — |
| 已文档化 | 99.6% | 99.6% | — | ✅ 门控通过 |
| 含示例 | 99.8% | 99.8% | — | ✅ |
| 含错误响应 | 100% | 100% | — | ✅ |
| 文档问题 | 2 | 2 | — | ✅ |

> D4 本次未重测，沿用基线数据。API 文档覆盖率维持在 99.6% 以上。

---

## D5: 依赖健康

| 指标 | 当前值 | 状态 |
|------|--------|------|
| 过期依赖 (npm outdated) | 0 | ✅ 所有已安装依赖均为当前版本 |
| CVE 漏洞 | 0 | ✅ |
| node_modules 缺失 | 多个 | ℹ️ 需 `npm install` |

**可选升级 (非过期，但有新主版本)**:

| 包 | 当前 | 最新 | 风险 |
|---|------|------|------|
| echarts | 5.6 | 6.1 | 高（主版本） |
| pinia | 2.3 | 3.0 | 高（主版本） |
| vue-router | 4.6 | 5.1 | 高（主版本） |
| klinecharts | 9.8 | 10.0-beta2 | 高（beta） |

> 主版本升级非技术债，属于架构决策，需通过 OpenSpec 变更流程。

---

## D6: 过程与安全

| 指标 | 当前值 | 基线值 | 变化 | 状态 |
|------|--------|--------|------|------|
| TODO | 23 | — | — | ℹ️ |
| XXX | 7 | — | — | ℹ️ |
| TODO/FIXME/HACK/XXX 合计 | 30 | 30 | — | ✅ 无增长 |
| SAST 高危 (S608 SQL注入) | 101 | — | 新增监测 | 🔴 需审查 |
| SAST 中危 (S311+S110+S324) | 652 | — | 新增监测 | ⚠️ |
| 代码中的硬编码密钥 | 0 | — | — | ✅ |
| debt-exception 注解 | 0 | — | — | ℹ️ |

---

## 热点文件 (Top 10)

按问题密度排序（lint 问题数 × 严重性权重 / 文件行数）：

| 排名 | 文件 | Lint 问题 | SAST 问题 | 行数 | 综合风险 |
|------|------|-----------|-----------|------|----------|
| 1 | `src/gpu/backtrace_engine.py` | 9 (F401) | — | ~600 | 高 |
| 2 | `src/adapters/fetch_write.py` | 9 (F821) | — | ~500 | 高 |
| 3 | `src/monitoring/stats_health.py` | 9 (F821) | — | ~400 | 高 |
| 4 | `src/monitoring/alerts.py` | 11 (F821) | — | ~700 | 中高 |
| 5 | `src/adapters/__init__.py` | 15 (F401) | — | ~200 | 中高 |
| 6 | `src/ml_strategy/naive_bayes_trading_strategy.py` | 6 (syntax) | — | ~300 | 中 |
| 7 | `src/ml_strategy/technical_analysis.py` | 7 (F821) | — | ~500 | 中 |
| 8 | `web/backend/app/api/_alerts_responses.py` | 5 (F821) | — | ~200 | 中 |
| 9 | `web/backend/app/main.py` | — | — | 894 | 中(体量) |
| 10 | `web/frontend/src/api/all.ts` | — | — | 2448 | 中(体量) |

---

## 治理优先级

### P0 — 必须立即处理

无（所有门控指标均通过）

### P1 — 当前迭代修复

1. **修复 10 个可自动修复的 Ruff 问题**: `ruff check --fix src/ web/backend/app/`
2. **审查 101 个 S608 SQL 注入风险**: 确认参数化查询覆盖率
3. **为 2 个无注解的 skip/xfail 添加 debt-exception 注解**
4. **拆分 `all.ts`(2448→<500 行)**: 按业务域拆分为多个 API 模块文件

### P2 — 下一迭代规划

1. **修复 F821(76 个未定义名称)**: 逐一确认是真实错误还是导入链问题
2. **修复 invalid-syntax(17 个)**: 特别是 `naive_bayes_trading_strategy.py`
3. **拆分大文件 Top 5**: `test_health_route_conflicts.py`(3192), `app/main.py`(894), `ArtDecoStrategyManagement.vue`(1033), `backtestAnalysisViewModel.ts`(967), `Screener.vue`(908)
4. **减少 # type:ignore 抑制(当前 30 个)**: 逐个替换为精确类型注解
5. **清理 S110(58 个 try-except-pass)**: 添加适当的异常日志或处理

### P3 — 待办事项

1. **S311(576 个 random 使用)**: 评估非安全场景是否可接受
2. **占位断言(220 个)**: 确认测量口径后制定减少计划
3. **179 个 Python 大文件**: 按优先级逐步拆分至 <500 行
4. **33 个前端大文件**: 按优先级逐步拆分至 <500 行
5. **评估主版本依赖升级**: echarts 6.x / pinia 3.x / vue-router 5.x（需 OpenSpec 流程）

---

## 门禁判定

| 门控指标 | 基线 | 当前 | 判定 |
|----------|------|------|------|
| frontend_type_errors | 0 | 0 | ✅ PASS |
| frontend_suppressions | 1 | 0 | ✅ PASS (改善) |
| skip_xfail_count | 102 | 17 | ✅ PASS (改善 83%) |
| api_docs_issues | 2 | 2 | ✅ PASS |

**综合门禁**: ✅ **PASS** — 所有门控指标均在基线以内

---

## 债务例外清单

当前代码中 **15 个** skip/xfail 标记已包含 debt-exception 注解：

| 状态 | 数量 | 说明 |
|------|------|------|
| 含完整注解 | 15 | 含 owner/issue/ttl |
| 缺少注解 | 2 | 需补充 |
| 已过期 | 0 | — |

> 代码中未发现 `debt-exception` 注解用于抑制 TS 类型或 lint 问题。

---

## 测量命令 (可复现)

```bash
# D1.1: 前端类型检查
cd web/frontend && ./node_modules/.bin/vue-tsc --noEmit

# D1.2: 前端抑制标记
grep -rn '@ts-ignore\|@ts-expect-error\|@ts-nocheck' web/frontend/src/

# D1.3: Ruff lint
ruff check src/ web/backend/app/ 2>&1

# D1.4: Ruff 安全扫描
ruff check --select S src/ web/backend/app/ tests/ 2>&1

# D1.5: 后端类型抑制
grep -rn '# type:ignore\|# type: ignore' src/ web/backend/app/

# D1.6: 大文件扫描 (Python >500 行)
find src/ web/backend/app/ tests/ -name '*.py' -exec sh -c 'lines=$(wc -l < "$1"); [ "$lines" -gt 500 ] && echo "$lines $1"' _ {} \; | sort -rn | head -20

# D1.7: 大文件扫描 (前端 >500 行)
find web/frontend/src/ web/frontend/tests/ -name '*.vue' -o -name '*.ts' | while read f; do lines=$(wc -l < "$f"); [ "$lines" -gt 500 ] && echo "$lines $f"; done | sort -rn | head -20

# D3.1: skip/xfail
grep -rn '@pytest.mark.skip\|@pytest.mark.xfail' tests/ | wc -l

# D3.2: 占位断言
grep -rn '^\s*pass\s*$' tests/ | wc -l

# D5.1: 依赖健康
cd web/frontend && npm outdated 2>&1

# D6.1: TODO/FIXME/HACK/XXX
grep -rn 'TODO\|FIXME\|HACK\|XXX' src/ web/backend/ | wc -l

# D6.2: 硬编码密钥
grep -rn 'password\s*=\s*["\x27]' src/ web/backend/ || echo "无硬编码密钥"
```

---

**报告生成**: tech-debt-checker skill v1.0 | 测量工具: vue-tsc, ruff 0.11.x, grep, npm, find
