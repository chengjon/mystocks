# 大文件拆分例外清单

> **历史文档说明**:
> 本文件是某阶段的历史文档、过程记录或专题材料，不是当前基线、当前系统总览或仓库共享规则的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内描述、背景、结论和上下文如未重新复核，应视为历史快照，不得直接当作当前事实。


> 生成日期: 2026-02-14
> 依据规范: architecture/standards/large_file_splitting_principles.md

## 说明

以下文件经过多轮自动化拆分后仍略超阈值（超标 5-99 行），属于边缘情况。
这些文件已经是拆分后的子模块，进一步拆分会导致过度碎片化，降低代码可读性。

## Python 源文件（阈值 800 行）

| 行数 | 超标 | 文件路径 | 原因 |
|------|------|---------|------|
| 899 | +99 | `./src/backtesting/advanced_backtest_engine.py` | 拆分后子模块，多个小型 dataclass/函数聚合，进一步拆分会过度碎片化 |
| 866 | +66 | `./web/backend/app/api/backup_recovery_secure/log_security_event.py` | 拆分后子模块，多个小型 dataclass/函数聚合，进一步拆分会过度碎片化 |
| 855 | +55 | `./web/backend/app/api/dashboard.py` | 拆分后子模块，多个小型 dataclass/函数聚合，进一步拆分会过度碎片化 |
| 851 | +51 | `./web/backend/app/api/notification.py` | 拆分后子模块，多个小型 dataclass/函数聚合，进一步拆分会过度碎片化 |
| 851 | +51 | `./web/backend/app/api/algorithms/get_algorithms_module.py` | 拆分后子模块，多个小型 dataclass/函数聚合，进一步拆分会过度碎片化 |
| 839 | +39 | `./src/advanced_analysis/market_panorama_analyzer.py` | 拆分后子模块，多个小型 dataclass/函数聚合，进一步拆分会过度碎片化 |
| 838 | +38 | `./src/advanced_analysis/capital_flow_analyzer/capital_flow_cluster.py` | 拆分后子模块，多个小型 dataclass/函数聚合，进一步拆分会过度碎片化 |
| 834 | +34 | `./web/backend/app/api/strategy_management/get_monitoring_db.py` | 拆分后子模块，多个小型 dataclass/函数聚合，进一步拆分会过度碎片化 |
| 829 | +29 | `./web/backend/app/api/tasks.py` | 拆分后子模块，多个小型 dataclass/函数聚合，进一步拆分会过度碎片化 |
| 824 | +24 | `./web/backend/app/api/indicators/indicator_cache.py` | 拆分后子模块，多个小型 dataclass/函数聚合，进一步拆分会过度碎片化 |
| 824 | +24 | `./src/advanced_analysis/sentiment_analyzer/sentiment_score.py` | 拆分后子模块，多个小型 dataclass/函数聚合，进一步拆分会过度碎片化 |
| 822 | +22 | `./web/backend/app/api/market/market_data_request.py` | 拆分后子模块，多个小型 dataclass/函数聚合，进一步拆分会过度碎片化 |
| 820 | +20 | `./src/advanced_analysis/technical_analyzer/technical_signal.py` | 拆分后子模块，多个小型 dataclass/函数聚合，进一步拆分会过度碎片化 |
| 817 | +17 | `./web/backend/app/api/stock_search/stock_search_result.py` | 拆分后子模块，多个小型 dataclass/函数聚合，进一步拆分会过度碎片化 |
| 807 | +7 | `./src/interfaces/adapters/efinance_adapter/efinance_data_source.py` | 拆分后子模块，多个小型 dataclass/函数聚合，进一步拆分会过度碎片化 |
| 807 | +7 | `./src/advanced_analysis/fundamental_analyzer.py` | 拆分后子模块，多个小型 dataclass/函数聚合，进一步拆分会过度碎片化 |
| 806 | +6 | `./src/advanced_analysis/trading_signals_analyzer/trading_signal.py` | 拆分后子模块，多个小型 dataclass/函数聚合，进一步拆分会过度碎片化 |
| 806 | +6 | `./src/advanced_analysis/chip_distribution_analyzer/chip_concentration.py` | 拆分后子模块，多个小型 dataclass/函数聚合，进一步拆分会过度碎片化 |
| 805 | +5 | `./src/routes/stocks_routes/check_use_mock_data.py` | 拆分后子模块，多个小型 dataclass/函数聚合，进一步拆分会过度碎片化 |

## 审批状态

- [ ] 技术负责人审批
- [ ] 记录到合规报告

## 后续计划

这些文件将在下一次功能迭代时随业务变更自然拆分，不单独安排拆分任务。
