# MyStocks GPU 相关文件分布

> 更新时间: 2026-06-07 | 用途: GPU 相关文档与代码的当前分布全貌

---

## 一、核心设计/架构文档

| 文档 | 路径 | 行数 |
|------|------|------|
| GPU HAL 实现报告 | `docs/reports/PHASE_6_2_GPU_HAL_IMPLEMENTATION_REPORT.md` | 342 |
| Kernel 层完成报告 | `docs/reports/PHASE_6_2_3_KERNEL_LAYER_COMPLETION_REPORT.md` | 313 |
| 统一接口完成报告 | `docs/reports/PHASE_5_6_UNIFIED_INTERFACE_COMPLETION_REPORT.md` | 415 |
| 回测 API 文档 | `docs/reports/BACKTEST_API_DOCUMENTATION.md` | 523 |
| 性能基线 | `docs/reports/performance/PERFORMANCE_BASELINE.md` | 415 |
| 架构索引 | `docs/architecture/INDEX.md` | 309 |

## 二、量化交易 GPU 文档

| 文档 | 路径 | 行数 |
|------|------|------|
| 量化交易算法 API 规范 | `docs/api/QUANTITATIVE_TRADING_ALGORITHMS_API_SPEC.md` | 396 |
| 量化分析实现计划 | `docs/api/quantitative-analysis-implementation-plan.md` | 1,382 |
| 量化交易架构研究 | `docs/reports/quantitative_trading_architecture_research_summary.md` | 34 |
| 高级算法使用指南 | `docs/guides/quant-trading/advanced_algorithms_usage_guide.md` | 368 |
| 神经网络算法指南 | `docs/guides/quant-trading/neural_algorithms_usage_guide.md` | 428 |
| ML 交易系统完成报告 | `docs/reports/PHASE20_COMPLETE_ML_TRADING_SYSTEM_REPORT.md` | 293 |

## 三、src/gpu/api_system/ 专属文档

| 文档 | 路径 | 行数 |
|------|------|------|
| GPU API 系统总览 | `src/gpu/api_system/README.md` | 562 |
| GPU API 索引 | `src/gpu/api_system/INDEX.md` | 326 |
| WSL2 GPU 设置指南 | `src/gpu/api_system/WSL2_GPU_SETUP.md` | 303 |
| WSL2 GPU 完成报告 | `src/gpu/api_system/WSL2_GPU_COMPLETION.md` | 424 |
| WSL2 GPU 摘要 | `src/gpu/api_system/WSL2_GPU_SUMMARY.md` | 473 |
| 缓存优化指南 | `src/gpu/api_system/CACHE_OPTIMIZATION_GUIDE.md` | 575 |
| 测试快速入门 | `src/gpu/api_system/TESTING_QUICK_START.md` | 342 |
| 测试 README | `src/gpu/api_system/tests/README.md` | 308 |
| 项目完成报告 | `src/gpu/api_system/PROJECT_COMPLETION_REPORT.md` | 591 |
| 项目总结 | `src/gpu/api_system/PROJECT_SUMMARY.md` | 436 |
| 项目验证 | `src/gpu/api_system/PROJECT_VERIFICATION.md` | 369 |
| Phase4 交付物 | `src/gpu/api_system/PHASE4_DELIVERABLES.md` | 269 |

## 四、GPU 性能监控代码

| 文件 | 路径 | 行数 |
|------|------|------|
| GPU 集成管理器 | `src/monitoring/gpu_integration_manager.py` | 520 |
| GPU 性能优化器（主模块） | `src/monitoring/gpu_performance_optimizer/gpu_performance_optimizer.py` | 533 |
| GPU 性能优化器配置 | `src/monitoring/gpu_performance_optimizer/gpu_optimization_config.py` | 100 |
| GPU 性能优化器报告 | `src/monitoring/gpu_performance_optimizer/_gpu_performance_optimizer_reporting.py` | 56 |
| GPU 性能优化器入口 | `src/monitoring/gpu_performance_optimizer/main.py` | 91 |
| GPU 性能优化器包初始化 | `src/monitoring/gpu_performance_optimizer/__init__.py` | 10 |
| GPU 计算器（monitoring） | `src/monitoring/domain/calculator_gpu.py` | 381 |

## 五、src/gpu/ 核心代码子系统

| 子系统 | 路径 | Python 文件数 | 代码行数 |
|--------|------|---------------|----------|
| GPU 加速数据处理 | `src/gpu/accelerated/` | 11 | 5,531 |
| GPU 特征/ML/回测 | `src/gpu/acceleration/` | 15 | 3,075 |
| GPU API 系统 | `src/gpu/api_system/` | 48 | 12,659 |
| GPU 硬件抽象/内核 | `src/gpu/core/` | 15 | 6,085 |
| **合计** | **src/gpu/** | **89** | **27,350** |

## 六、src/gpu/ 外部 GPU 相关代码

| 文件 | 路径 | 行数 | 说明 |
|------|------|------|------|
| GPU 验证器 | `src/governance/engine/gpu_validator.py` | 194 | 治理层 GPU 校验 |
| GPU 风险计算器（垫片） | `src/governance/risk_management/calculators/gpu_calculator.py` | 2 | 重导出 |
| GPU 风险计算器（垫片） | `src/governance/risk_management/calculators/gpu_calculator/gpu_risk_calculator.py` | 2 | 重导出 |
| GPU 验证器测试 | `src/governance/tests/test_gpu_validator.py` | 67 | 测试 |
| GPU 计算器（infrastructure） | `src/infrastructure/calculation/gpu_calculator.py` | 70 | 基础设施层 |
| GPU 性能优化器（垫片） | `src/monitoring/gpu_performance_optimizer.py` | 2 | 重导出 |

## 七、src/gpu/ 外部消费者

共 11 个文件从 `src.gpu` 导入：

| 域 | 文件 | 路径 |
|----|------|------|
| 算法 | 贝叶斯网络 | `src/algorithms/bayesian/bayesian_network_algorithm.py` |
| 算法 | 决策树 | `src/algorithms/classification/decision_tree_algorithm.py` |
| 算法 | 朴素贝叶斯 | `src/algorithms/classification/naive_bayes_algorithm.py` |
| 算法 | SVM | `src/algorithms/classification/svm_algorithm.py` |
| 算法 | HMM | `src/algorithms/markov/hmm_algorithm.py` |
| 算法 | 神经网络 | `src/algorithms/neural/neural_network_algorithm.py` |
| 算法 | N-gram | `src/algorithms/ngram/ngram_algorithm.py` |
| 治理 | GPU 风险核心 | `src/governance/risk_management/calculators/gpu_calculator/gpu_risk_calculator_methods/core.py` |
| 治理 | GPU 风险浓度 | `src/governance/risk_management/calculators/gpu_calculator/gpu_risk_calculator_methods/get_concentration_level.py` |
| 治理 | GPU 风险工具 | `src/governance/risk_management/calculators/gpu_calculator/utils.py` |
| 高级分析 | 模块入口 | `src/advanced_analysis/__init__.py` |

## 八、ML 训练/预测设计

| 文档 | 路径 | 行数 |
|------|------|------|
| ML 训练预测运行时设计 | `docs/superpowers/specs/2026-05-08-ml-training-prediction-runtime-design.md` | 707 |

## 九、待清理项

| 类型 | 文件 | 说明 |
|------|------|------|
| 重复文件对 | `src/gpu/accelerated/data_processor_gpu.py` (855行) | 与 `_fixed` 版本重复 |
| 重复文件对 | `src/gpu/accelerated/data_processor_gpu_fixed.py` (2行) | 仅 2 行，疑似残留 |
| 垫片 | `src/gpu/api_system/services/backtest_service.py` (2行) | 重导出 |
| 垫片 | `src/monitoring/gpu_performance_optimizer.py` (2行) | 重导出 |
| 垫片 | `src/governance/risk_management/calculators/gpu_calculator.py` (2行) | 重导出 |
| 垫片 | `src/governance/risk_management/calculators/gpu_calculator/gpu_risk_calculator.py` (2行) | 重导出 |
