# 股票指标计算体系优化方案 (V2.2)

根据对 `docs/` 文档和代码库 `web/backend/app/services/` 的深度分析，当前系统处于 **V1向V2过渡** 的关键阶段。V2的基础设施（元数据、依赖图、执行调度）已就绪，但核心的"业务闭环能力"（存储、定时任务、全面覆盖）尚待完善。

## 1. 现状评估

| 维度 | V1 (Legacy) | V2 (Current Target) | 评估结论 |
|------|-------------|---------------------|----------|
| **核心代码** | `IndicatorCalculator` | `services/indicators/` | **混合状态**。V1是全功能单体，V2是高扩展架构骨架。 |
| **指标覆盖** | ~24个 (TA-Lib全封装) | ~4个 (Verified Impl) | **覆盖率倒挂**。V1远强于V2，需加速迁移。 |
| **调度能力** | 无 (同步串行) | `SmartScheduler` (并发图) | **定义偏差**。V2实现了"执行调度"，但缺失"任务调度"(Cron)。 |
| **数据持久化** | 无 (内存计算) | 无 (设计中) | **严重缺失**。无法保存历史计算结果，阻碍回测和分析。 |
| **扩展性** | 低 (需修改核心类) | 高 (插件式注册) | **V2优势明显**。V2设计符合长期发展需求。 |

**关键发现**:
- 代码中已存在 `SmartScheduler`，它实现了依赖图解析和线程池并发，这对应了Gap分析中的"计算引擎优化"，但未实现"每日定时任务"。
- `IndicatorRegistry` 已经定义了绝大多数指标的元数据，这为迁移提供了极好的基础。

## 2. 优化方案 (V2.2 Roadmap)

本方案旨在补齐V2的"最后一公里"，使其具备生产能力，并逐步替代V1。

### Phase 1: 数据持久化 (P0 - 关键路径)
**目标**: 计算结果落地，不再"算完即焚"。

1.  **数据库设计 (PostgreSQL + TimescaleDB/TDengine)**
    *   利用现有的 `IndicatorResult` 数据类，映射到 DB Schema。
    *   创建 `indicator_data` 超级表（时序数据）和 `indicator_tasks` 表（任务状态）。

2.  **Repository层实现**
    *   新建 `web/backend/app/repositories/indicator_repo.py`。
    *   实现 `save_batch(results: List[IndicatorResult])`。
    *   实现 `get_history(code, indicator, start, end)`，优先查库，未命中再计算。

### Phase 2: 任务调度体系 (P0 - 自动化)
**目标**: 实现"每日自动计算"和"补录数据"。

1.  **引入任务框架**
    *   使用 `APScheduler` (轻量级) 或复用项目现有的 Task 机制。
    *   **Cron Job**: `02:00` 触发全市场日线计算。

2.  **调度器集成**
    *   编写 `BatchCalculationJob`：
        *   Step 1: 获取当日收盘数据。
        *   Step 2: 构建指标清单 (从 `IndicatorRegistry` 获取)。
        *   Step 3: 调用 `SmartScheduler.calculate()` (利用现有的并发能力)。
        *   Step 4: 调用 `IndicatorRepository.save_batch()`。

### Phase 3: 指标全量迁移 (P1 - 核心能力)
**目标**: 将V1的24+个指标逻辑移植到V2插件体系。

1.  **通用适配器 (Generic Adapter)**
    *   与其通过一个个手写类文件迁移，不如实现一个 `TalibIndicatorAdapter` 类。
    *   该类继承 `IndicatorInterface`，根据 `registry` 中的元数据动态映射到 `talib` 函数。
    *   **收益**: 一次性迁移 90% 的标准 TA-Lib 指标，无需创建几十个文件。

2.  **特殊指标定制**
    *   仅对逻辑复杂、非标准 TA-Lib 的指标（如自定义策略指标）编写独立 Plugin Class。

### Phase 4: 服务接口升级 (P2 - 对外赋能)
**目标**: 提供统一的 API 网关。

1.  **API 路由重构**
    *   新建 `api/v1/indicators.py`。
    *   废弃旧的 `calculate_indicator` 端点。
    *   新增 `/batch_calculate` (触发任务)、`/history` (查库)、`/stream` (WebSocket)。

## 3. 立即执行的 Action Items

基于当前文件结构，建议优先执行以下代码变更：

1.  **创建通用适配器** (`web/backend/app/services/indicators/adapters.py`):
    *   利用 `web/backend/app/services/indicator_calculator.py` 中的逻辑，将其封装为符合 `IndicatorInterface` 的通用类，快速提升V2覆盖率。
2.  **连接数据库**:
    *   在 `SmartScheduler` 的流程中注入 `Repository`，在 `mark_computed` 后异步写入数据库。

```python
# 示例：通用适配器逻辑
class TalibGenericIndicator(IndicatorInterface):
    def __init__(self, abbreviation: str):
        super().__init__()
        self.meta = get_indicator_registry().get_indicator(abbreviation)
        self.ABBREVIATION = abbreviation

    def calculate(self, data: OHLCVData, params: Dict) -> IndicatorResult:
        # 复用 V1 Calculator 的 _call_talib_function 逻辑
        # ...
        return self._create_success_result(params, result)
```
