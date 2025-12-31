#!/usr/bin/env python3
"""
GPU加速集成接口
将GPU组件集成到MyStocks项目的统一管理系统中
提供与传统MyStocksUnifiedManager的无缝集成
"""

import time
import logging
from typing import Dict, Optional, Union, Any
import pandas as pd
from dataclasses import dataclass

# 导入原有的统一管理器
from ..unified_manager import MyStocksUnifiedManager
from .gpu_manager import GPUUnifiedManager
from .data_processor_gpu import ProcessingConfig


@dataclass
class GPUIntegrationConfig:
    """GPU集成配置"""

    auto_enable_gpu: bool = True
    fallback_to_cpu: bool = True
    performance_threshold: float = 0.1  # 10秒内处理1万行数据
    gpu_memory_threshold_mb: float = 8000.0  # 8GB内存限制
    enable_benchmarking: bool = True
    benchmark_interval: int = 100  # 每100次操作进行一次基准测试


class GPUEnhancedUnifiedManager(MyStocksUnifiedManager):
    """GPU增强的统一管理器 - 继承自原有的统一管理器"""

    def __init__(self, config: Optional[GPUIntegrationConfig] = None):
        # 调用父类初始化
        super().__init__()

        self.gpu_config = config or GPUIntegrationConfig()
        self.logger = logging.getLogger(__name__)

        # 初始化GPU管理器
        self.gpu_manager = GPUUnifiedManager()

        # GPU使用统计
        self.gpu_usage_stats = {
            "total_operations": 0,
            "gpu_operations": 0,
            "cpu_fallback_operations": 0,
            "last_benchmark": None,
            "performance_history": [],
        }

        self.logger.info("GPU增强统一管理器初始化完成")

    def save_data_by_classification_with_gpu(
        self,
        data: pd.DataFrame,
        data_classification: Any,
        use_gpu: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """使用GPU保存分类数据 - 覆盖原方法"""

        # 决策是否使用GPU
        should_use_gpu = self._should_use_gpu(data, use_gpu)

        start_time = time.time()

        try:
            if should_use_gpu:
                # 使用GPU进行数据处理
                self.logger.info("使用GPU处理分类数据: %s", data_classification)

                # 数据预处理
                processed_result = self.gpu_manager.process_data_with_gpu(
                    data=data, processing_config=ProcessingConfig()
                )

                # 将GPU处理后的数据保存到传统数据库
                result = super().save_data_by_classification(processed_result.results, data_classification)

                # 更新GPU统计
                self.gpu_usage_stats["gpu_operations"] += 1
                result["gpu_enabled"] = True
                result["processing_time"] = processed_result.processing_time
                result["speedup_factor"] = processed_result.speedup_factor

                self.logger.info("GPU数据处理完成 - 耗时: %s秒", processed_result.processing_time)

            else:
                # 使用传统方法
                self.logger.info("使用CPU处理分类数据: %s", data_classification)
                result = super().save_data_by_classification(data, data_classification)

                # 更新CPU统计
                self.gpu_usage_stats["cpu_fallback_operations"] += 1
                result["gpu_enabled"] = False
                result["processing_time"] = time.time() - start_time

                self.logger.info("CPU数据处理完成 - 耗时: %s秒", result["processing_time"])

            # 更新总操作数
            self.gpu_usage_stats["total_operations"] += 1

            # 记录性能数据
            performance_data = {
                "timestamp": time.time(),
                "operation": "save",
                "gpu_enabled": should_use_gpu,
                "processing_time": result.get("processing_time", 0),
                "data_size": len(data),
            }
            self.gpu_usage_stats["performance_history"].append(performance_data)

            return result

        except Exception as e:
            self.logger.error("数据保存失败: %s", e)

            # 如果GPU失败且有CPU回退配置，则回退到CPU
            if should_use_gpu and self.gpu_config.fallback_to_cpu:
                self.logger.warning("GPU处理失败，回退到CPU模式")
                result = super().save_data_by_classification(data, data_classification)
                self.gpu_usage_stats["cpu_fallback_operations"] += 1
                result["gpu_enabled"] = False
                result["error"] = str(e)
                return result

            raise e

    def load_data_by_classification_with_gpu(
        self, data_classification: Any, use_gpu: Optional[bool] = None
    ) -> pd.DataFrame:
        """使用GPU加载分类数据 - 覆盖原方法"""

        # 决策是否使用GPU
        should_use_gpu = self._should_use_gpu(None, use_gpu)

        start_time = time.time()

        try:
            # 先从数据库加载数据
            data = super().load_data_by_classification(data_classification)

            if should_use_gpu:
                # 使用GPU进行数据处理
                self.logger.info("使用GPU处理加载的数据: %s", data_classification)

                processed_result = self.gpu_manager.process_data_with_gpu(
                    data=data, processing_config=ProcessingConfig()
                )

                # 更新GPU统计
                self.gpu_usage_stats["gpu_operations"] += 1
                processed_data = processed_result.results
                processed_data.gpu_processing_info = {
                    "processing_time": processed_result.processing_time,
                    "gpu_enabled": True,
                    "speedup_factor": processed_result.speedup_factor,
                }

                self.logger.info("GPU数据加载完成 - 耗时: %s秒", processed_result.processing_time)

            else:
                # 使用传统方法
                processed_data = data
                self.gpu_usage_stats["cpu_fallback_operations"] += 1
                processed_data.gpu_processing_info = {
                    "processing_time": time.time() - start_time,
                    "gpu_enabled": False,
                    "speedup_factor": 1.0,
                }

                self.logger.info("CPU数据加载完成 - 耗时: %s秒", time.time() - start_time)

            # 更新总操作数
            self.gpu_usage_stats["total_operations"] += 1

            return processed_data

        except Exception as e:
            self.logger.error("数据加载失败: %s", e)

            # GPU失败回退
            if should_use_gpu and self.gpu_config.fallback_to_cpu:
                self.logger.warning("GPU加载失败，回退到CPU模式")
                data = super().load_data_by_classification(data_classification)
                data.gpu_processing_info = {
                    "processing_time": time.time() - start_time,
                    "gpu_enabled": False,
                    "error": str(e),
                }
                return data

            raise e

    def generate_price_predictions_with_gpu(
        self,
        stock_data: Union[pd.DataFrame, str],
        prediction_horizon: int = 1,
        model_type: str = "ridge",
        use_gpu: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """使用GPU生成价格预测 - 新增方法"""

        # 决策是否使用GPU
        should_use_gpu = self._should_use_gpu(stock_data if isinstance(stock_data, pd.DataFrame) else None, use_gpu)

        start_time = time.time()

        try:
            if isinstance(stock_data, str):
                # 如果是股票代码，先获取数据
                from ..data_adapters.financial_adapter import FinancialDataSource

                data_source = FinancialDataSource()
                stock_data = data_source.fetch_stock_data(stock_data)

            if should_use_gpu:
                # 使用GPU进行预测
                self.logger.info("使用GPU生成价格预测: %s, 预测周期: %s", model_type, prediction_horizon)

                prediction_result = self.gpu_manager.generate_predictions_with_gpu(
                    data=stock_data,
                    model_type=model_type,
                    prediction_horizon=prediction_horizon,
                )

                # 更新GPU统计
                self.gpu_usage_stats["gpu_operations"] += 1

                result = {
                    "gpu_enabled": True,
                    "processing_time": prediction_result.processing_time,
                    "speedup_factor": prediction_result.speedup_factor,
                    "prediction": prediction_result.results,
                    "performance_metrics": prediction_result.performance_metrics,
                    "errors": prediction_result.errors,
                }

                if not prediction_result.errors:
                    prediction = prediction_result.results
                    result.update(
                        {
                            "predicted_price": prediction.predicted_price,
                            "confidence_score": prediction.confidence_score,
                            "model_used": prediction.model_used,
                            "prediction_date": prediction.prediction_date,
                        }
                    )

                self.logger.info("GPU预测完成 - 价格: %s", result.get("predicted_price", "N/A"))

            else:
                # 使用CPU预测
                self.logger.info("使用CPU生成价格预测: %s", model_type)

                # 使用传统价格预测器
                from ..gpu_accelerated.price_predictor_gpu import PricePredictorCPU

                cpu_predictor = PricePredictorCPU(gpu_enabled=False)

                # 训练模型
                cpu_predictor.train_models(stock_data)

                # 进行预测
                prediction_result = cpu_predictor.predict_price(stock_data, model_type, prediction_horizon)

                # 更新CPU统计
                self.gpu_usage_stats["cpu_fallback_operations"] += 1

                result = {
                    "gpu_enabled": False,
                    "processing_time": time.time() - start_time,
                    "speedup_factor": 1.0,
                    "predicted_price": prediction_result.predicted_price,
                    "confidence_score": prediction_result.confidence_score,
                    "model_used": prediction_result.model_used,
                    "prediction_date": prediction_result.prediction_date,
                    "performance_metrics": prediction_result.error_metrics,
                    "errors": [],
                }

                self.logger.info("CPU预测完成 - 价格: %s", prediction_result.predicted_price)

            # 更新总操作数
            self.gpu_usage_stats["total_operations"] += 1

            # 如果启用了基准测试，定期进行性能评估
            if (
                self.gpu_config.enable_benchmarking
                and self.gpu_usage_stats["total_operations"] % self.gpu_config.benchmark_interval == 0
            ):
                self._run_performance_benchmark()

            return result

        except Exception as e:
            self.logger.error("价格预测失败: %s", e)

            # GPU失败回退
            if should_use_gpu and self.gpu_config.fallback_to_cpu:
                self.logger.warning("GPU预测失败，回退到CPU模式")
                return self.generate_price_predictions_with_gpu(stock_data, prediction_horizon, model_type, False)

            return {
                "gpu_enabled": should_use_gpu,
                "error": str(e),
                "processing_time": time.time() - start_time,
                "errors": [str(e)],
            }

    def _should_use_gpu(self, data: Optional[pd.DataFrame], use_gpu: Optional[bool]) -> bool:
        """判断是否应该使用GPU"""

        # 如果用户明确指定，则直接使用
        if use_gpu is not None:
            return use_gpu

        # 如果GPU自动启用被禁用，则不使用
        if not self.gpu_config.auto_enable_gpu:
            return False

        # 检查GPU是否可用
        if not self.gpu_manager.gpu_enabled:
            self.logger.warning("GPU不可用，使用CPU")
            return False

        # 如果没有数据，无法判断数据大小，使用CPU
        if data is None or len(data) == 0:
            return False

        # 基于数据大小决定是否使用GPU
        data_size = len(data)
        if data_size < 1000:  # 小数据集使用CPU
            return False

        # 检查性能阈值
        expected_time = data_size * self.gpu_config.performance_threshold
        if expected_time > 60:  # 预期处理时间超过60秒，不使用GPU
            self.logger.warning("数据量过大(%s行)，预期处理时间过长，使用CPU", data_size)
            return False

        # 检查GPU内存限制
        gpu_memory_usage = self.gpu_manager._get_gpu_memory_usage()
        if gpu_memory_usage > self.gpu_config.gpu_memory_threshold_mb:
            self.logger.warning("GPU内存使用过高(%sMB)，使用CPU", gpu_memory_usage)
            return False

        # 其他GPU资源检查可以在这里添加
        return True

    def _run_performance_benchmark(self):
        """运行性能基准测试"""
        try:
            self.logger.info("开始GPU性能基准测试...")

            # 获取一些示例数据进行测试
            from ..data_adapters.financial_adapter import FinancialDataSource

            data_source = FinancialDataSource()
            sample_data = data_source.fetch_stock_data("AAPL")

            # 进行小规模基准测试
            benchmark_result = self.gpu_manager.benchmark_gpu_vs_cpu(
                sample_data[:1000],
                operation="process",  # 使用小样本
            )

            # 记录基准测试结果
            self.gpu_usage_stats["last_benchmark"] = {
                "timestamp": time.time(),
                "gpu_time": benchmark_result["gpu_time"],
                "cpu_time": benchmark_result["cpu_time"],
                "speedup": benchmark_result["speedup"],
                "efficiency_metrics": benchmark_result["efficiency_metrics"],
            }

            self.logger.info(
                "基准测试完成 - GPU: {benchmark_result['gpu_time']:.4f}s, "
                f"CPU: {benchmark_result['cpu_time']:.4f}s, "
                f"加速比: {benchmark_result['speedup']:.2f}x"
            )

        except Exception as e:
            self.logger.error("基准测试失败: %s", e)

    def get_gpu_integration_status(self) -> Dict[str, Any]:
        """获取GPU集成状态"""
        return {
            "gpu_available": self.gpu_manager.gpu_enabled,
            "auto_enable_gpu": self.gpu_config.auto_enable_gpu,
            "fallback_to_cpu": self.gpu_config.fallback_to_cpu,
            "gpu_usage_stats": self.gpu_usage_stats,
            "gpu_performance_summary": self.gpu_manager.get_performance_summary(),
            "last_benchmark": self.gpu_usage_stats["last_benchmark"],
            "gpu_config": {
                "performance_threshold": self.gpu_config.performance_threshold,
                "gpu_memory_threshold_mb": self.gpu_config.gpu_memory_threshold_mb,
                "enable_benchmarking": self.gpu_config.enable_benchmarking,
                "benchmark_interval": self.gpu_config.benchmark_interval,
            },
        }

    def save_gpu_models(self, filepath: str):
        """保存GPU模型"""
        self.gpu_manager.save_gpu_models(filepath)

    def load_gpu_models(self, filepath: str):
        """加载GPU模型"""
        self.gpu_manager.load_gpu_models(filepath)

    def generate_gpu_integration_report(self) -> str:
        """生成GPU集成报告"""
        status = self.get_gpu_integration_status()
        gpu_performance = self.gpu_manager.generate_gpu_report()

        report = f"""
MyStocks GPU集成状态报告
==========================

🔗 集成配置:
  • 自动启用GPU: {"✅ 是" if status["auto_enable_gpu"] else "❌ 否"}
  • CPU回退功能: {"✅ 是" if status["fallback_to_cpu"] else "❌ 否"}
  • 性能阈值: {status["gpu_config"]["performance_threshold"]}秒/万行
  • GPU内存限制: {status["gpu_config"]["gpu_memory_threshold_mb"]}MB
  • 启用基准测试: {"✅ 是" if status["gpu_config"]["enable_benchmarking"] else "❌ 否"}

📊 GPU使用统计:
  • 总操作次数: {status["gpu_usage_stats"]["total_operations"]}
  • GPU操作次数: {status["gpu_usage_stats"]["gpu_operations"]}
  • CPU回退次数: {status["gpu_usage_stats"]["cpu_fallback_operations"]}
  • GPU使用率: {
    (status["gpu_usage_stats"]["gpu_operations"] /
     max(1, status["gpu_usage_stats"]["total_operations"]) * 100):.1f
}%

⚡ GPU组件状态:
  • GPU环境: {"✅ 可用" if status["gpu_available"] else "❌ 不可用"}
  • 数据处理器: {"✅ 已启用" if status["gpu_performance_summary"][
      "gpu_components_status"]["data_processor"]["enabled"] else "❌ 已禁用"}
  • 特征生成器: {"✅ 已启用" if status["gpu_performance_summary"][
      "gpu_components_status"]["feature_generator"]["enabled"] else "❌ 已禁用"}
  • 价格预测器: {"✅ 已启用" if status["gpu_performance_summary"][
      "gpu_components_status"]["price_predictor"]["enabled"] else "❌ 已禁用"}

🏆 性能基准测试:
"""

        if status["last_benchmark"]:
            benchmark = status["last_benchmark"]
            report += f"""
  • 最后测试时间: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(benchmark["timestamp"]))}
  • GPU处理时间: {benchmark["gpu_time"]:.4f}秒
  • CPU处理时间: {benchmark["cpu_time"]:.4f}秒
  • 加速比: {benchmark["speedup"]:.2f}x
"""
        else:
            report += """
  • 暂无基准测试数据
"""

        report += """
💡 集成建议:
  • 大数据集(>1000行)优先使用GPU加速
  • 小数据集自动使用CPU模式以减少GPU内存开销
  • 定期运行基准测试以监控GPU性能
  • 如果GPU操作频繁失败，检查GPU内存使用情况

"""

        return report + gpu_performance


def create_gpu_enhanced_manager(
    config: Optional[GPUIntegrationConfig] = None,
) -> GPUEnhancedUnifiedManager:
    """创建GPU增强统一管理器的工厂函数"""
    return GPUEnhancedUnifiedManager(config)


# 向后兼容的包装器
def get_gpu_enabled_manager() -> GPUEnhancedUnifiedManager:
    """获取GPU启用版本的统一管理器"""
    return GPUEnhancedUnifiedManager()


def main():
    """主函数 - 示例用法"""
    # 创建GPU增强管理器
    gpu_manager = create_gpu_enhanced_manager()

    print("🚀 MyStocks GPU增强管理器演示")
    print("=" * 50)

    # 获取示例数据
    from ..data_adapters.financial_adapter import FinancialDataSource

    data_source = FinancialDataSource()
    sample_data = data_source.fetch_stock_data("AAPL")

    # 数据保存测试
    print("\n1. 数据保存测试:")
    save_result = gpu_manager.save_data_by_classification_with_gpu(
        sample_data[:100],
        data_classification="market_data",  # 使用小样本
    )
    print(
        f"保存结果 - GPU: {save_result.get('gpu_enabled', False)}, "
        f"时间: {save_result.get('processing_time', 0):.4f}秒"
    )

    # 数据加载测试
    print("\n2. 数据加载测试:")
    loaded_data = gpu_manager.load_data_by_classification_with_gpu("market_data")
    gpu_enabled = hasattr(loaded_data, "gpu_processing_info") and loaded_data.gpu_processing_info.get(
        "gpu_enabled", False
    )
    print(f"加载完成 - GPU: {gpu_enabled}")

    # 价格预测测试
    print("\n3. 价格预测测试:")
    prediction_result = gpu_manager.generate_price_predictions_with_gpu(
        sample_data, prediction_horizon=1, model_type="ridge"
    )
    print(
        f"预测结果 - GPU: {prediction_result.get('gpu_enabled', False)}, "
        f"预测价格: {prediction_result.get('predicted_price', 'N/A')}"
    )

    # 生成集成报告
    print("\n4. GPU集成报告:")
    print(gpu_manager.generate_gpu_integration_report())


if __name__ == "__main__":
    main()
