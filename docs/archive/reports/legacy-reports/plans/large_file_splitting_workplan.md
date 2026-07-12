# 大文件拆分工作计划（可执行版）

## 治理元数据

| 项目 | 内容 |
|------|------|
| 文档状态 | 修订待审核 (Revised, Pending Review) |
| 创建日期 | 2026-02-14 |
| 依据规范 | `architecture/standards/large_file_splitting_principles.md` v1.0 |
| 发布记录 | `reports/compliance/large_file_splitting_principles_v1.0_release.md` |
| 计划所有者 | 架构组 / Tech Lead |
| 扫描快照 | 2026-02-14（当前工作树） |

---

## 一、执行范围与排除范围

### 1.1 纳入范围
- Python 源文件：阈值 `> 800`。
- Python 测试文件：阈值 `> 1000`。
- Vue 文件：阈值 `> 500`。
- TypeScript 文件：阈值 `> 500`。

### 1.2 排除范围（本计划不拆分）
- `archived/**`。
- `docs/**`。
- `node_modules/**`。
- `scripts/dev/development/**`（重复/镜像目录，先清理）。
- `scripts/tests/testing/**`（重复/镜像目录，先清理）。
- `web/frontend/src/views/converted.archive/**`。
- `web/frontend/src/layouts/archive/**`。
- `web/frontend/archives/**`。
- `web/frontend/src/api/types/generated-types.ts`（自动生成，走例外流程）。
- `*.d.ts` 声明文件（类型声明工件，作为类型定义例外）。

---

## 二、基线清单（唯一执行来源）

> 不再手工维护 200+ 文件列表，统一使用扫描产物，避免计划与仓库状态漂移。

### 2.1 已生成产物
- `reports/plans/inventory/python_source_gt800.tsv`（71）
- `reports/plans/inventory/python_test_gt1000.tsv`（16）
- `reports/plans/inventory/vue_gt500.tsv`（107）
- `reports/plans/inventory/ts_gt500.tsv`（44）
- `reports/plans/large_file_splitting_backlog.tsv`（238）

### 2.2 当前统计（MUST SPLIT）

| 类别 | 阈值 | 文件数 | 最大行数 |
|------|------|--------|----------|
| Python 源 | > 800 | 81 | 4046 |
| Python 测试 | > 1000 | 16 | 2120 |
| Vue | > 500 | 104 | 1002 |
| TypeScript | > 500 | 44 | 2235 |
| **合计                    237** |  |

### 2.3 优先级分桶（已写入 backlog）

| Wave | 类别 | P0 | P1 | P2 | 合计 |
|------|------|----|----|----|------|
| Wave 1 | Python 源 | 6 | 13 | 62 | 81 |
| Wave 2 | Vue | 1 | 37 | 66 | 104 |
| Wave 3 | TypeScript | 1 | 6 | 37 | 44 |
| Wave 4 | Python 测试 | 1 | 2 | 13 | 16 |
| **总计** |  | **9** | **61** | **176** | **246** |

优先级定义：
- `P0`：超过阈值 2 倍以上。
- `P1`：超过阈值 1.5~2 倍。
- `P2`：超过阈值但不足 1.5 倍。

---

## 三、执行前置（Wave 0）

> 工期：1~2 天。未完成 Wave 0，不进入 Wave 1。

### 3.1 清理与归并
- 清理 `scripts/tests/testing/` 与 `scripts/dev/development/`（先比对后删除）。
- 合并大小写重复目录与重复组件（例如 `Strategy/` vs `strategy/`）。
- 确认 `src/components/navigation/DynamicSidebar.vue` 是否保留。

### 3.2 例外流程落地
- 新建例外记录：`reports/compliance/large_files_exceptions.md`。
- 记录 `generated-types.ts` 与 `klinecharts.d.ts` 的例外审批、到期时间、回顾周期。

### 3.3 基线报告
- 产出：`reports/compliance/splitting_baseline_report.md`。
- 内容：测试通过率、覆盖率、lint 状态、循环依赖、性能基线。

---

## 四、分 Wave 执行计划

## 4.1 Wave 1（Python 源文件）
- 工期：8~12 天。
- 输入：`reports/plans/inventory/python_source_gt800.tsv`。
- 执行顺序：`P0 -> P1 -> P2`。

P0 文件（必须先完成）：
- `scripts/dev/ci/quant_strategy_validation.py` (4046)
- `scripts/dev/technical_debt_analyzer.py` (2337)
- `web/backend/app/services/data_adapter.py` (2016)
- `src/advanced_analysis/decision_models_analyzer.py` (1659)

## 4.2 Wave 2（Vue 文件）
- 工期：9~14 天。
- 输入：`reports/plans/inventory/vue_gt500.tsv`。
- 执行顺序：`P0 -> P1 -> P2`。

P0 文件：
- `web/frontend/src/views/StockAnalysisDemo.vue` (1002)

约束：
- ArtDeco 页面 Tab 仅拆分为子组件，不拆分为独立路由。

## 4.3 Wave 3（TypeScript 文件）
- 工期：4~6 天。
- 输入：`reports/plans/inventory/ts_gt500.tsv`。
- 执行顺序：`P0 -> P1 -> P2`。

P0 文件：
- `web/frontend/src/api/types/common.ts` (2235)

## 4.4 Wave 4（Python 测试文件）
- 工期：3~4 天。
- 输入：`reports/plans/inventory/python_test_gt1000.tsv`。
- 执行顺序：`P0 -> P1 -> P2`。

P0 文件：
- `tests/ai/test_ai_assisted_testing.py` (2120)

说明：
- 测试目标路径统一来自 inventory 实际扫描结果，覆盖 `tests/**` 与 `scripts/tests/**` 的真实文件。

## 4.5 Wave 5（总体验收）
- 工期：2~3 天。
- 内容：全量回归、性能比对、最终合规报告。
- 产出：`reports/compliance/large_file_splitting_final_report.md`。

---

## 五、单文件标准作业流程（SOP）

每个 backlog 条目按以下流程执行：
1. 读取目标文件并识别职责边界。
2. 设计目标结构（模块边界、依赖方向、命名）。
3. 拆分实现并更新 import/export。
4. 运行文件级与模块级测试。
5. 运行质量门与依赖门。
6. 更新 `reports/plans/large_file_splitting_backlog.tsv` 对应行状态。
7. 小步提交。

建议状态流转：
- `TODO -> IN_PROGRESS -> DONE -> VERIFIED`

---

## 六、质量门（强制）

## 6.1 后端
- `pytest`
- `pytest --cov=./src --cov-report term-missing`
- `ruff check .`
- `mypy .`
- `pylint --disable=all --enable=R0401 <target_module_or_package>`

## 6.2 前端
- `cd web/frontend && npm run test`
- `cd web/frontend && npm run test:coverage`
- `cd web/frontend && npm run lint`
- `cd web/frontend && npm run type-check`
- `cd web/frontend && npm run test:e2e`
- `madge --circular --extensions js,ts,vue web/frontend/src`

## 6.3 性能门（强制）
- 前端：Playwright 指标对比，关键指标退化不超过 10%。
- 后端：Locust 指标对比，P95 退化不超过 10%。

---

## 七、交付与里程碑

| 里程碑 | 条件 | 交付物 |
|--------|------|--------|
| M0 | Wave 0 完成 | `splitting_baseline_report.md` + `large_files_exceptions.md` |
| M1 | Wave 1 完成 | Python 源文件达标报告 |
| M2 | Wave 2 完成 | Vue 达标报告 |
| M3 | Wave 3 完成 | TS 达标报告 |
| M4 | Wave 4 完成 | 测试文件达标报告 |
| M5 | Wave 5 完成 | `large_file_splitting_final_report.md` |

总体工期：**27~41 天**（按当前 238 文件测算）。

---

## 八、执行命令（复现扫描）

> 每次进入新 Wave 前必须重扫，避免在变化中的仓库执行过期清单。

```bash
# 重新生成 inventory + backlog（单一入口）
scripts/dev/tools/generate_large_file_splitting_inventory.sh

# 产物：
# reports/plans/inventory/*.tsv
# reports/plans/large_file_splitting_backlog.tsv

# 快速核验总数
wc -l reports/plans/inventory/python_source_gt800.tsv
wc -l reports/plans/inventory/python_test_gt1000.tsv
wc -l reports/plans/inventory/vue_gt500.tsv
wc -l reports/plans/inventory/ts_gt500.tsv
```
