# 股票指标计算与管理体系 (V2.2) 优化与整合报告

## 1. 摘要 (Summary)
本项目对原有的股票指标计算体系进行了深度优化，完成了从 V1（单体计算类）向 V2（标准化插件架构）的全面平滑过渡。通过引入“通用适配器”模式，成功将 V1 中积累的 20 余个成熟指标即时迁移至 V2 架构；同时补齐了 V2 体系在**数据持久化**、**任务自动化调度**以及**元数据动态管理**方面的核心短板。目前系统已具备生产级全市场指标计算与历史回溯能力。

## 2. 详细内容 (Detailed Content)

### 2.1 架构设计
系统采用分层解耦的插件化架构，主要分为以下四层：
*   **应用接口层**：集成于 FastAPI 生命周期中，提供 RESTful API 与 WebSocket 实时流支持。
*   **计算引擎层 (SmartScheduler)**：基于依赖图分析指标关联性，支持多线程并行计算与智能结果缓存。
*   **适配转换层 (TalibGenericIndicator)**：核心桥接模块，将底层的 TA-Lib 函数包装成 V2 标准接口。
*   **持久化层 (IndicatorRepository)**：基于 PostgreSQL/TimescaleDB 的高效存储方案，支持大批量指标结果的 Upsert 操作。

### 2.2 核心功能特性
1.  **高覆盖率迁移**：通过 `TalibGenericIndicator` 适配并激活了 SMA, MACD, RSI, BBANDS 等 23 个标准技术指标。
2.  **数据闭环能力**：通过 `IndicatorData` 模型实现时序存储，彻底解决了 V1 算完即焚的问题。
3.  **智能调度**：`SmartScheduler` 自动处理指标间的计算顺序，最大化并行效率。
4.  **任务自动化**：内置 `daily_calculation` 任务，支持通过 Cron 表达式触发全市场计算流程。

### 2.3 关键模块说明
*   **`IndicatorRegistry` (元数据中心)**：管理指标参数约束、类型与输出定义。
*   **`IndicatorRepository` (持久化仓库)**：负责结果入库与计算任务状态追踪。
*   **`IndicatorDefaults` (初始化加载器)**：启动时自动同步 V1 配置至 V2，并注册插件。
*   **`DailyCalculationJob` (批处理作业)**：编排“数据查询-计算-入库”的完整业务流。

## 3. 相关文件 (Related Files)

| 模块 | 文件路径 | 职能描述 |
| :--- | :--- | :--- |
| **模型** | `web/backend/app/models/indicator_data.py` | 定义指标结果与任务的 DB 表结构 |
| **仓库** | `web/backend/app/repositories/indicator_repo.py` | 实现 Upsert 批量入库逻辑 |
| **适配器** | `web/backend/app/services/indicators/talib_adapter.py` | V1 逻辑到 V2 接口的桥接器 |
| **初始化** | `web/backend/app/services/indicators/defaults.py` | 元数据自动迁移加载器 |
| **作业** | `web/backend/app/services/indicators/jobs/daily_calculation.py` | 每日批量计算业务逻辑 |
| **任务** | `web/backend/app/tasks/indicator_tasks.py` | 任务管理器函数封装 |
| **脚本** | `scripts/init_indicator_schedule.py` | 自动化调度初始化工具 |

## 4. 附录 (Appendix)

### 4.1 启用自动化调度
管理员可通过以下命令快速启用每日凌晨 2:00 的全市场指标刷新任务：
```bash
python3 scripts/init_indicator_schedule.py
```

### 4.2 开发调用示例
在业务代码中计算并保存指标：
```python
from app.services.indicators import create_scheduler
from app.repositories.indicator_repo import IndicatorRepository

# 1. 实例化调度器与仓库
scheduler = create_scheduler()
repo = IndicatorRepository()

# 2. 计算指定指标 (示例：MACD)
indicators = [{"abbreviation": "MACD", "params": {}}]
results = scheduler.calculate(indicators, ohlcv_data)

# 3. 保存至数据库
repo.save_results(stock_code, ohlcv_data.timestamps, [r.result for r in results if r.success])
```
