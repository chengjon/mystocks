# MyStocks 技术负债深度审计报告

> **历史总结说明**:
> 本文件是阶段性总结、报告、状态、修复记录、验证结果或交付回执，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内统计值、完成状态、结论、验证结果和修复结论如未重新复核，应视为历史快照，不得直接当作当前事实。


**审计日期**: 2026-04-05
**方法**: 基于实际代码库探索与定向命令复核（非文档汇总）
**代码库支撑**: `.planning/codebase/` 7 个结构化文档

> 说明:
> - 本文档是 `2026-04-05` 的审计快照，不是长期门禁基线文件。
> - 当前硬门禁基线仍以 `reports/analysis/tech-debt-baseline.json` 与 `docs/standards/technical-debt-governance-charter-v1.md` 为准。
> - 文中所有“当前值”均指审计当日实测结果；未复测的历史数字会明确标注为历史快照。

---

## 审计边界与统计口径

- 除特别说明外，文件数量统计基于当前工作树 2026-04-05 的实际文件系统状态。
- Python 目录计数默认按 `*.py` 口径；前端目录计数按 `*.vue`、`*.ts`、`*.js` 等源码文件口径。
- Ruff 指标来自 `ruff check src/ web/backend/app/ --statistics`。
- 前端 TypeScript 技术债采用基线文件 `reports/analysis/tech-debt-baseline.json`，其中 `frontend_type_errors = 0`。
- 凡涉及“删除 / 归档 / 合并目录”的建议，必须同时满足 `architecture/STANDARDS.md` 的审批门禁，以及其中“清理 / 删除决策标准”的代码路径判定与功能树判定要求。

---

## 总体判断

项目在若干治理面向上已有明显改善，尤其是前端类型债基线已降到 0；但当前可维护性风险并未进入“收尾阶段”。最突出的债务集中在三类问题：

1. 适配器相关代码存在高比例镜像重复与方法碎片化，导致 Ruff `F821` 大量聚集。
2. 数据访问层、路由层与兼容 shim 并存，职责边界持续模糊。
3. 后端 API 与前端源码树仍保留明显的历史堆积，部分大文件和遗留目录尚未完成治理闭环。

结论上，这份仓库更接近“局部治理有进展，但核心结构债尚未出清”，而不是“主要技术债已清零”。

### 关键指标

| metric | measured | baseline | inferred | target | source_or_command |
|---|---|---|---|---|---|
| `ruff_f821_undefined_name` | `1173` | `N/A` | `N/A` | `下降并重新冻结基线` | `ruff check src/ web/backend/app/ --statistics` |
| `ruff_total_findings` | `1458` | `N/A` | `N/A` | `下降并重新冻结基线` | `ruff check src/ web/backend/app/ --statistics` |
| `adapter_f821_hotspot_share` | `836 / 1173` | `N/A` | `约 71.3%` | `显著下降` | `ruff --statistics + adapters/interfaces 路径归类` |
| `ruff_direct_auto_fix_floor` | `201` | `N/A` | `约 13.8%` | `优先消化可机械修复项` | `ruff --statistics 中带 [*] 项的保守汇总` |
| `frontend_type_errors` | `0` | `0` | `N/A` | `0` | `reports/analysis/tech-debt-baseline.json` |
| `python_large_files_over_800_lines` | `6` | `N/A` | `N/A` | `下降` | `按审计日文件行数复核` |
| `frontend_case_conflict_directories` | `3 pairs` | `N/A` | `Linux 部署风险高` | `0` | `前端目录大小写冲突盘点` |
| `tests_python_files` | `691` | `N/A` | `tests/ 全部文件数为 1136` | `转化为可度量覆盖率基线` | `tests/ 文件系统统计` |
| `mock_surface_size` | `N/A` | `N/A` | `规模仍较大，仅作为观察项` | `完成契约一致性校验` | `本次审计说明；不作为硬指标` |

---

## P0 — 关键问题

### 1. 适配器代码面存在高比例镜像重复与方法碎片化

`src/interfaces/adapters/` 与 `src/adapters/` 之间存在大面积镜像重复，但不应再表述为“完整 1:1 拷贝”。当前复核结果：

- `src/interfaces/adapters/` 有 73 个 `*.py`
- `src/adapters/` 有 101 个 `*.py`
- 两者相对路径重合的文件有 69 个

更严重的问题是，热点文件在两个目录里都以“脱离模块上下文的方法片段”形式存在，导致 `F821` 同时出现在实现层和接口镜像层。例如：

- `src/interfaces/adapters/akshare/misc_data/get_ths_industry_names.py`
- `src/adapters/akshare/misc_data/get_ths_industry_names.py`

这两个文件内容一致，且都以 `def get_ths_industry_names(self) -> pd.DataFrame:` 开头，文件内没有 `pd`、`ak`、`logger` 的本地导入。

**影响**:

- `src/interfaces/adapters/` 贡献 368 个 `F821`
- `src/adapters/` 贡献 468 个 `F821`
- 两者合计 836 个，占全部 `F821` 的约 71.3%

**修复建议**:

- 先走方案审批：这是核心架构调整，必须遵循 `architecture/STANDARDS.md` 的审批门禁。
- 明确 `src/interfaces/` 的目标形态：纯 Protocol/ABC，还是兼容层。
- 明确这些方法片段是“失效拆分产物”还是“需要组装机制的模块片段”；未判定前不要直接大规模删除。
- 一旦目标架构确定，收敛为单一真相源，并补齐模块级导入与上下文。

---

### 2. 前端大小写冲突目录已确认存在

以下目录在 Linux 上是不同路径，在不区分大小写的文件系统上会发生混淆：

| 大写 | 小写 | 风险 |
|------|------|------|
| `components/Charts/` | `components/charts/` | 模块解析失败 |
| `components/Common/` | `components/common/` | 模块解析失败 |
| `components/Market/` | `components/market/` | 模块解析失败 |

**修复建议**:

- 统一命名策略后一次性迁移，不要做半迁移状态。
- 迁移前先全局校验 import 路径与构建脚本引用。

---

## P1 — 高优先级

### 3. 数据访问层多头并存

当前至少存在四组相互重叠的数据访问职责：

| 目录 | 当前 `*.py` 数 | 说明 |
|------|----------------|------|
| `src/data_access/` | 18 | 主数据访问层 |
| `src/data_access_pkg/` | 5 | 含重复访问模块 |
| `src/database/` | 23 | 含服务、连接、shim 与迁移中命名 |
| `src/db_manager/` | 1 | 空壳目录 |

另有根级 `data_access.py` 使用 `from data_access_pkg import *`。

**问题**:

- 访问层边界不清，接口真相源不明确。
- `database_service_new.py` 这类命名说明迁移尚未闭环。
- wildcard import 增加依赖关系不透明度。

**修复建议**:

- 先形成数据访问层收敛方案，再实施目录合并。
- 收敛时同步梳理 shim、兼容导出和 import 路径。

---

### 4. 路由层不是“已确认死代码”，而是“遗留兼容面待判定”

路由定义当前分散在三个位置：

| 位置 | `*.py` 数 | 当前判断 |
|------|-----------|----------|
| `src/routes/` | 19 | 遗留/兼容面，非纯死代码 |
| `src/api/` | 5 | 遗留 API 面，仍需判定 |
| `web/backend/app/api/` | 205 | 现行 FastAPI 主路由层 |

此前将 `src/routes/`、`src/api/` 直接表述为“疑似死代码”过于激进。复核发现它们仍有实际引用，例如：

- `scripts/cicd_pipeline.sh` 仍执行 `from src.routes import *`
- `src/database/services/database_service.py` 仍直接导入 `src.routes.wencai_routes`
- `tests/api_contract_tests.py` 仍导入 `src.api.types.*`

**修复建议**:

- 按 `architecture/STANDARDS.md` 的“清理 / 删除决策标准”，先做代码路径判定和功能树判定。
- 在判定结果出来前，应表述为“遗留兼容层 / 待下线对象”，而不是“可删除死代码”。
- 若最终决定归档或删除，需补充判定依据、保留原因和迁移路径。

---

### 5. 测试数量与有效覆盖率不能等同

当前 `tests/` 下有：

- 691 个 Python 文件
- 1,136 个总文件

数量很大，但质量信号并不充分：

- `tests/test_api_endpoints.py` 仍是手动脚本风格，不是标准 pytest 用例
- `tests/contract/` 中混有 `contract_engine.py`、`report_generator.py` 这类框架代码
- 最近一次覆盖率数字 `0.16%` 来自 2026-01-03，已明显过时，不能作为当前基线

**修复建议**:

- 运行 `pytest --collect-only -q` 获取实际可收集用例数
- 运行 `pytest --cov=src --cov=web/backend/app --cov-report=term-missing` 冻结新覆盖率基线
- 把框架代码从 `tests/` 迁出或明确标注其角色

---

## P2 — 中优先级

### 6. 前端结构仍有明显历史堆积

已确认的问题包括：

- 顶层共有 8 个 `main*.js/ts` 入口文件，实际入口只有 `main.js`
- `views/artdeco-pages/` 当前有 156 个源码文件，规模已超过“单一页面簇”应有复杂度
- `views/converted.archive/` 仍保留 11 个文件
- `views/demo/` 仍保留 41 个文件
- `views/composables/` 有 17 个文件，放置位置不合理

**判断**:

- 这部分不一定都应删除，但至少需要分清“正式功能”“兼容保留”“实验/演示”“归档”四种状态。

---

### 7. 后端 API 热点文件仍然集中

`web/backend/app/api/` 当前有 205 个 Python 文件，且仍存在 6 个超过 800 行的 Python 热点：

- `web/backend/app/api/monitoring.py` — 1270 行
- `web/backend/app/api/strategy_management/get_monitoring_db.py` — 1242 行
- `web/backend/app/main.py` — 885 行
- `web/backend/app/api/auth.py` — 866 行
- `web/backend/app/api/strategy_mgmt.py` — 860 行
- `web/backend/app/api/monitoring_watchlists.py` — 846 行

**问题**:

- 热点仍集中在监控、认证、策略管理和应用入口。
- `main.py` 继续混合应用装配、CSRF 管理和 Socket.IO 初始化。

**修复建议**:

- 优先处理业务边界最清晰的热点文件，避免继续做机械拆分。
- 把“文件拆小”与“职责收敛”绑定，避免再产生 `part1.py` 风格碎片。

---

### 8. 根级 shim 与导入安全性仍需治理

当前仍存在典型兼容导出链：

```python
core.py         -> from core import *
src/core.py     -> from core import *
data_access.py  -> from data_access_pkg import *
```

**风险**:

- 裸导入和 wildcard import 使依赖方向不透明。
- 在 `sys.path` 不同的运行环境下存在循环导入与解析偏差风险。

---

### 9. 命名与拆分质量不足

- `src/calcu/` 命名截断
- `part1.py / part2.py / part3.py` 型拆分缺少语义边界
- `database_service_new.py` 暗示迁移长期停留在“过渡态”
- `src/database_optimization/` 与 `src/database/` 责任重叠

这类问题不一定立刻导致故障，但会显著提高维护成本和误判概率。

---

## P3 — 低优先级

### 10. Mock 基础设施仍需周期性校验

仓库中的 mock 代码面仍然不小，但其精确数量高度依赖统计口径（按目录、按文件名、按调用路径都会得到不同结果）。因此，本次不再将“mock 文件数”作为硬指标，而改为观察项：

- mock 仍与生产代码长期共存
- 当前更重要的是确认 mock 与 real 实现的契约一致性
- 若继续保留，应建立定期对照校验机制

### 11. Store 领域边界仍显模糊

- `market.ts` vs `marketData.ts`
- `trading.ts` vs `tradingData.ts`
- `dataAdapters.ts` 含数据转换逻辑，不像纯 store
- `baseStore.ts.bak` 这类备份残留会稀释源码树信号

---

## Ruff 问题分解

当前 `ruff check src/ web/backend/app/ --statistics` 结果如下：

| 规则 | 数量 | 备注 |
|------|------|------|
| F821 undefined-name | 1,173 | 当前首要问题 |
| W293 blank-line-whitespace | 95 | 可直接自动修复 |
| F841 unused-variable | 78 | 可直接自动修复 |
| W291 trailing-whitespace | 28 | 可直接自动修复 |
| F401 unused-import | 21 | 需按上下文判断 |
| F811 redefined-while-unused | 17 | 需人工审查 |
| E701 multiple-statements | 15 | 需人工确认后修复 |
| E722 bare-except | 13 | 应优先人工治理 |
| F601 multi-value-repeated-key-literal | 6 | 逻辑风险 |
| F823 undefined-local | 4 | 逻辑风险 |
| F403 undefined-local-with-import-star | 3 | wildcard import 相关 |
| E741 ambiguous-variable-name | 2 | 可读性问题 |
| E902 io-error | 2 | 环境/文件问题 |
| F402 import-shadowed-by-loop-var | 1 | 局部问题 |

**结论**:

- 当前能直接确认的“保守自动修复量”为 201 个（95 + 78 + 28），约占总问题 13.8%。
- 仅靠 `ruff --fix` 无法把问题总量从 1458 直接压到 200 左右；核心结构债必须先处理。

---

## 优先修复路线图

| 阶段 | 工作项 | 预期效果 |
|------|--------|---------|
| **Week 1** | 提交适配器层与数据访问层收敛方案，明确接口层、实现层、shim 的目标形态 | 防止继续在错误架构上修补 |
| **Week 2** | 对 `src/routes/`、`src/api/` 做代码路径判定和功能树判定，形成遗留兼容面清单 | 为后续归档/删除提供依据 |
| **Week 3** | 统一前端大小写目录，治理适配器层高频 `F821` 热点，重新冻结 Ruff 基线 | 降低部署风险，压缩首要噪音 |
| **Week 4** | 执行 `pytest --collect-only` 与 `pytest --cov`，补齐测试基线和覆盖率基线 | 把“测试多”转化为“测试可度量” |
| **持续** | 拆分后端 >800 行热点文件，优先按职责收敛而非机械分片 | 提升长期可维护性 |

---

## 代码库映射文档

本次审计参考的 7 个结构化文档位于 `.planning/codebase/`：

| 文档 | 行数 | 内容 |
|------|------|------|
| STACK.md | 79 | 技术栈、依赖、构建命令 |
| INTEGRATIONS.md | 63 | 外部集成、数据库、数据源 |
| ARCHITECTURE.md | 81 | 系统设计、数据流、分层 |
| STRUCTURE.md | 129 | 目录结构、关键位置 |
| CONVENTIONS.md | 78 | 编码规范、质量门禁 |
| TESTING.md | 81 | 测试框架、结构、质量 |
| CONCERNS.md | 150 | 技术负债与已知问题 |

---

**报告生成**: 2026-04-05
**下次审计**: 建议在完成 Week 2 判定后复审，而不是按自然月固定滚动
**基线版本**: v2.0
