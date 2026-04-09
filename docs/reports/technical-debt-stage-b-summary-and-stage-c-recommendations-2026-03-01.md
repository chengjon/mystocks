# MyStocks 技术负债治理阶段总结与下一阶段建议（供审核）

> **历史总结说明**:
> 本文件是阶段性总结、报告、状态、修复记录、验证结果或交付回执，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内统计值、完成状态、结论、验证结果和修复结论如未重新复核，应视为历史快照，不得直接当作当前事实。


> 文档日期：2026-03-01  
> 对应 OpenSpec 变更：`refactor-technical-debt-remediation-wave1`  
> 范围：Stage A + Stage B 已执行内容总结，及 Stage C 启动建议

---

## 一、上一阶段（Stage A + Stage B）技术负债修复总结

### 1.1 总体结论

本阶段已完成“**先止血，再降风险**”的核心目标：

- Stage A 已完成关键止血项（构建/类型失败语义对齐、no-new-debt 门禁）
- Stage B 已完成关键路径清偿项（前端 suppressions 减量、后端 trade API 占位替换、测试占位断言替换）
- OpenSpec 严格校验持续通过，可继续推进后续阶段

---

### 1.2 OpenSpec 任务完成状态快照（截至本次）

依据：`openspec/changes/refactor-technical-debt-remediation-wave1/tasks.md`

#### Stage A - Stop Bleeding
- ✅ 1.1 统一前端构建与类型检查门禁
- ⏳ 1.2 技术债基线文件 + CI 对比（进行中：已完成采集脚本与首次基线落盘，待接入 CI 对比后关闭）
- ✅ 1.3 新增债务阻断（no-new-debt）
- ⏳ 1.4 例外模板 + 双签审批（未完成）

#### Stage B - Risk Reduction
- ✅ 2.1 前端关键路径 suppressions 第一批/后续批次减量
- ✅ 2.2 已完成首批关键端点语义修复（trades 日期过滤/异常语义）；positions 仍有 TODO/模拟数据，纳入 Stage C 清偿
- ✅ 2.3 测试有效性治理第一批（assert True 替换）
- ⏳ 2.4 大文件热点治理（未完成）

#### Stage C / Rollout
- ⏳ 3.1 ~ 3.4 未启动
- ⏳ 4.1 ~ 4.3 未启动

---

### 1.3 已完成的核心修复（按类别）

#### A. 门禁与止血

1) 前端 build 语义修复（不再吞类型错误）
- 文件：`web/frontend/package.json`
- 结果：移除 `vue-tsc --noEmit || true` 的放行方式，构建遇类型错误将失败

2) no-new-debt 门禁落地
- 文件：`.github/workflows/typescript-type-check.yml`
- 结果：新增 gate，阻断新增：
  - `@ts-ignore/@ts-expect-error/@ts-nocheck/as any/# type: ignore`
  - 裸 `TODO/FIXME/HACK`（缺 owner/ttl/issue 元数据）

#### B. 前端 suppressions 减量（交易与分析链路）

已落地文件（核心）：
- `web/frontend/src/composables/useStrategy.ts`
- `web/frontend/src/composables/artdeco/useArtDecoApi.ts`
- `web/frontend/src/api/apiClient.ts`
- `web/frontend/src/api/types/common.ts`
- `web/frontend/src/api/adapters/marketAdapter.ts`
- `web/frontend/src/views/artdeco-pages/ArtDecoMarketQuotes.vue`
- `web/frontend/src/views/composables/useAdvancedAnalysis.ts`

典型成果：
- 移除多处 `as any`、`catch(any)`、动态 any 索引调用
- 采用 `unknown + 类型收窄`、显式接口类型、handler map

#### C. 后端 trade API 占位逻辑替换

文件：`web/backend/app/api/trade/routes.py`

已完成：
- `get_trades`：日期过滤从 TODO/pass 改为可执行逻辑（格式校验、区间校验、过滤）
- 修复异常透传：避免 400 校验错误被误包装为 500
- `get_statistics/get_portfolio`：由硬编码演示值改为可计算快照逻辑

#### D. 测试有效性提升

文件：`tests/api/file_tests/test_trade_routes_api.py`

已完成：
- 将多处 `assert True` 占位替换为真实结构/契约断言
- 当前该文件 `assert True` 已清零

---

### 1.4 验证证据（本阶段）

- `openspec validate refactor-technical-debt-remediation-wave1 --strict` ✅ 通过
- `pytest tests/api/file_tests/test_trade_routes_api.py -q -o addopts=''` ✅ 18 passed
- `grep "assert True" tests/api/file_tests/test_trade_routes_api.py` ✅ 无匹配
- 反证透明化：`web/backend/app/api/trade/routes.py:107-108,186` 仍存在 TODO/快照说明，已登记为 Stage C 条目。

说明：
- 前端全量 `type-check` 仍存在大量历史存量错误（基线债务），符合“分阶段治理、先止增后清偿”的预期，不属于本阶段新增回归。

---

## 二、下一阶段（Stage C）工作建议

### 2.1 目标

将“阶段性治理动作”升级为“可持续机制”，重点解决：
- 治理规则可执行但不够自动化
- 例外审批与到期回收尚未制度化
- 基线与 KPI 未形成周期性管理闭环

---

### 2.2 推荐执行顺序（建议 2~3 周）

#### 优先级 P0：先补齐 Stage A 遗留机制缺口

1) 完成 1.2：技术债基线文件化 + CI 对比
- 建议基线文件（示例）：`reports/analysis/tech-debt-baseline.json`
- 指标至少包含：
  - `frontend_type_errors`
  - `frontend_suppressions_count`
  - `skip_xfail_count`
  - `backend_todo_count`
  - `backend_placeholder_count`（mock/demo/hardcoded snapshot 等）
  - `test_placeholder_assert_count`

- 建议同步固化“采集口径定义”（避免执行歧义）：
  - `frontend_type_errors`
    - 统计范围：`web/frontend/src/**/*.{ts,tsx,vue}`
    - 统计方式：`npm --prefix web/frontend run type-check` 输出错误总数（按统一解析脚本提取）
    - 排除项：无（以类型检查真实输出为准）
  - `frontend_suppressions_count`
    - 统计范围：`web/frontend/src/**/*.{ts,tsx,vue}`
    - 统计模式：`@ts-ignore|@ts-expect-error|@ts-nocheck|\sas any\b|#\s*type:\s*ignore`
    - 排除项：`auto-imports.d.ts` 等生成文件单独计入 `generated_suppressions_count`（可选）
  - `skip_xfail_count`
    - 统计范围：`tests/**/*.py` + `web/backend/tests/**/*.py`
    - 统计模式：`@pytest.mark.skip|@pytest.mark.xfail|pytest\.skip\(|pytest\.xfail\(`
    - 说明：需区分“永久跳过”与“带 issue+ttl 的临时跳过”
  - `backend_todo_count`
    - 统计范围：`web/backend/app/**/*.py` + `src/**/*.py`
    - 统计模式：`TODO|FIXME|HACK`
    - 排除项：`docs/`、`archive/`、测试目录默认不纳入该指标
  - `backend_placeholder_count`
    - 统计范围：`web/backend/app/**/*.py` + `src/**/*.py`
    - 统计模式（建议组合）：`mock|demo|hardcoded|sample data|placeholder|NotImplementedError|pass\b`
    - 说明：仅计“业务路径代码”命中，注释类说明需二次判定避免误报
  - `test_placeholder_assert_count`
    - 统计范围：`tests/**/*.py` + `web/backend/tests/**/*.py`
    - 统计模式：`assert True`
    - 说明：允许在极少数显式 smoke test 中豁免，但必须带 `issue+ttl`

- 建议在 CI 中固化统一扫描命令（示例，可后续脚本化）：
  - `grep -RInE "@ts-ignore|@ts-expect-error|@ts-nocheck|\\sas any\\b" web/frontend/src`
  - `grep -RInE "TODO|FIXME|HACK" web/backend/app src`
  - `grep -RInE "mock|demo|hardcoded|placeholder|NotImplementedError|pass\\b" web/backend/app src`
  - `grep -RInE "assert True|@pytest.mark.skip|@pytest.mark.xfail|pytest\\.skip\\(|pytest\\.xfail\\(" tests web/backend/tests`

2) 完成 1.4：例外模板 + 双签审批
- 建议模板：`docs/guides/templates/tech-debt-exemption.md`
- 必填字段：owner / issue / ttl / reason / remediation_plan
- 审批策略：Tech Lead + 模块负责人

#### 优先级 P1：启动 Stage C 机制硬化

3) 完成 3.1：TTL 到期自动失效
- 在 CI 增加过期检测，过期条目直接 fail

4) 完成 3.2：周报模板落地
- 输出字段：新增债务、消化债务、存量债务、过期项、风险热点
- 同步要求：每轮周报/阶段复盘同时产出 `reports/analysis/tech-debt-baseline-drift-report.json`，区分 `gated drift` 与 `observed drift`

5) 完成 3.3：KPI 门禁化
- no-new-debt
- 基线不增（允许下降）
- 例外合规率
- 到期清理率

6) 完成 3.4：治理回顾机制
- 每迭代固定复盘
- 基线更新默认只降不升

#### 优先级 P2：试点与推广（Stage 4）

7) 完成 4.1~4.3
- 试点两周（前端交易链路 + 后端交易 API）
- 评估误伤率与交付影响
- 通过评审后分阶段扩展全仓

---

### 2.3 下一阶段 Top 债务热点（建议排期）

前端 suppressions 仍有较大存量（`web/frontend/src`）：
- `views/artdeco-pages/ArtDecoTradingCenter.vue`
- `components/market/composables/useProKLineChart.ts`
- `components/market/IndicatorSelector.vue`
- `views/composables/useTechnicalAnalysis.ts`
- `api/adapters/strategyAdapter.ts`

建议策略：
- 先“业务关键路径 + 高频改动文件”
- 生成产物/测试文件单独归类治理，避免与生产路径混治

---

## 三、审核重点（请你重点看这 4 项）

1) Stage B 收官范围是否认可（尤其 2.1/2.2/2.3）
2) Stage C 顺序是否同意按 P0→P1→P2 推进
3) 基线文件字段是否要增加（如 `backend_todo_count`）
4) 例外审批是否采用“强双签 + TTL 强制”

---

## 四、审批后拟执行动作

若你审核通过，我将按以下顺序立即执行：
1. 完成 1.2 的 CI 对比接入（基线采集已落地）
2. 落地例外模板 + 双签流程（1.4）
3. 实现 TTL 到期自动失败（3.1）
4. 更新 OpenSpec tasks 与阶段性周报
5. 生成并归档 baseline drift 复核结果，避免把口径修正误判为阶段回归

---

## 五、Stage C 1.2 执行进展（进行中）

已新增基线采集脚本：
- `scripts/dev/quality_gate/collect_tech_debt_baseline.py`

默认输出基线文件：
- `reports/analysis/tech-debt-baseline.json`

执行命令：
- `python scripts/dev/quality_gate/collect_tech_debt_baseline.py`

本次生成基线快照（UTC 2026-03-01）：
- `frontend_type_errors`: 182
- `frontend_suppressions_count`: 68
- `skip_xfail_count`: 234
- `backend_todo_count`: 54
- `backend_placeholder_count`: 2876
- `test_placeholder_assert_count`: 298

补充字段：
- `generated_suppressions_count`: 2
- `type_check_exit_code`: 2
- `type_check_command`: `npm --prefix web/frontend run type-check`

说明：
- 以上值用于冻结当前观测快照，后续 CI 需按“新增不增量”策略比较。
- `frontend_type_errors = 182` 是当前观测值，不等于“已批准门禁基线”。在 SoT 迁移完成前，治理基线仍以现行规则为准。
- `backend_placeholder_count` 当前口径已做收窄，但仍可能受语义噪声影响，建议在 1.4 例外治理后继续白名单细化。
