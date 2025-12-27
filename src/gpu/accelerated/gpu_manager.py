#!/usr/bin/env python3
"""
GPU加速统一管理器
集成GPU组件到MyStocks项目的统一管理系统中
支持自动检测GPU环境并提供统一的GPU加速接口
"""

import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import pandas as pd

# GPU组件导入
from .price_predictor_gpu import GPUPricePredictor
from .feature_generator_gpu import GPUFeatureGenerator
from .data_processor_gpu import GPUDataProcessor, ProcessingConfig


@dataclass
class GPUConfig:
    """GPU配置"""

    gpu_enabled: bool = True
    n_jobs: int = 1
    chunk_size: int = 10000
    memory_limit_gb: float = 8.0
    enable_parallel_processing: bool = True
    enable_streaming: bool = True
    enable_distributed: bool = False


@dataclass
class GPUProcessingResult:
    """GPU处理结果"""

    processing_time: float
    data_size: int
    gpu_memory_usage: float
    speedup_factor: float
    results: Any
    errors: List[str]
    performance_metrics: Dict[str, float]


class GPUUnifiedManager:
    """GPU加速统一管理器"""

    def __init__(self, config: Optional[GPUConfig] = None):
        """初始化GPU统一管理器"""
        self.config = config or GPUConfig()
        self.logger = logging.getLogger(__name__)

        # 初始化GPU组件
        self.gpu_enabled = self._detect_gpu_environment()
        self.data_processor = GPUDataProcessor(
            gpu_enabled=self.gpu_enabled,
            n_jobs=self.config.n_jobs,
            chunk_size=self.config.chunk_size,
        )
        self.feature_generator = GPUFeatureGenerator(gpu_enabled=self.gpu_enabled)
        self.price_predictor = GPUPricePredictor(gpu_enabled=self.gpu_enabled)

        # 性能统计
        self.performance_stats = {
            "total_processing_time": 0.0,
            "total_data_processed": 0,
            "gpu_enabled_operations": 0,
            "cpu_fallback_operations": 0,
            "average_speedup": 1.0,
        }

        self.logger.info(f"GPU统一管理器初始化完成 - GPU加速: {self.gpu_enabled}")

    def _detect_gpu_environment(self) -> bool:
        """检测GPU环境是否可用"""
        try:
            import cupy as cp

            # 检查是否有GPU设备
            cp.cuda.Device(0)
            self.logger.info("✅ GPU环境检测成功")
            return True
        except Exception as e:
            self.logger.warning(f"⚠️  GPU环境检测失败: {e}, 将使用CPU模式")
            return False

    def process_data_with_gpu(
        self, data: pd.DataFrame, processing_config: Optional[ProcessingConfig] = None
    ) -> GPUProcessingResult:
        """使用GPU处理数据"""
        start_time = time.time()

        try:
            # 数据预处理
            processed_data = self.data_processor.preprocess(data=data, config=processing_config or ProcessingConfig())

            # 特征生成
            feature_data = self.feature_generator.generate_features(processed_data)

            processing_time = time.time() - start_time

            # 获取GPU内存使用情况
            gpu_memory = 0.0
            if self.gpu_enabled:
                try:
                    import cupy as cp

                    gpu_memory = cp.cuda.get_default_memory_pool().used_bytes() / 1024 / 1024
                except Exception:
                    gpu_memory = 0.0

            result = GPUProcessingResult(
                processing_time=processing_time,
                data_size=len(data),
                gpu_memory_usage=gpu_memory,
                speedup_factor=self._calculate_speedup_factor(data, processing_time),
                results=feature_data,
                errors=[],
                performance_metrics=self._collect_performance_metrics(),
            )

            self._update_performance_stats(result)

            self.logger.info(f"GPU数据处理完成 - 耗时: {processing_time:.4f}秒, 数据量: {len(data)}行")
            return result

        except Exception as e:
            error_msg = f"GPU数据处理失败: {str(e)}"
            self.logger.error(error_msg)

            result = GPUProcessingResult(
                processing_time=time.time() - start_time,
                data_size=len(data),
                gpu_memory_usage=0.0,
                speedup_factor=0.0,
                results=None,
                errors=[error_msg],
                performance_metrics={},
            )

            return result

    def generate_predictions_with_gpu(
        self,
        data: pd.DataFrame,
        model_type: str = "ridge",
        prediction_horizon: int = 1,
        training_horizon: Optional[int] = None,
    ) -> GPUProcessingResult:
        """使用GPU生成预测"""
        start_time = time.time()

        try:
            # 如果没有训练过，先训练模型
            if not self.price_predictor.is_fitted:
                training_data = data if training_horizon is None else data[-training_horizon:]
                self.logger.info("开始训练GPU预测模型...")
                self.price_predictor.train_models(training_data)
                self.logger.info("GPU模型训练完成")

            # 进行预测
            prediction_result = self.price_predictor.predict_price(
                data=data, model_name=model_type, prediction_horizon=prediction_horizon
            )

            processing_time = time.time() - start_time

            result = GPUProcessingResult(
                processing_time=processing_time,
                data_size=len(data),
                gpu_memory_usage=self._get_gpu_memory_usage(),
                speedup_factor=self._calculate_speedup_factor(data, processing_time),
                results=prediction_result,
                errors=[],
                performance_metrics={
                    "model_used": prediction_result.model_used,
                    "confidence_score": prediction_result.confidence_score,
                    "mse": prediction_result.error_metrics.get("mse", 0),
                    "r2_score": prediction_result.error_metrics.get("r2_score", 0),
                },
            )

            self._update_performance_stats(result)

            self.logger.info(f"GPU预测完成 - 模型: {model_type}, 预测价格: {prediction_result.predicted_price:.2f}")
            return result

        except Exception as e:
            error_msg = f"GPU预测失败: {str(e)}"
            self.logger.error(error_msg)

            result = GPUProcessingResult(
                processing_time=time.time() - start_time,
                data_size=len(data),
                gpu_memory_usage=0.0,
                speedup_factor=0.0,
                results=None,
                errors=[error_msg],
                performance_metrics={},
            )

            return result

    def batch_process_with_gpu(
        self, data_list: List[pd.DataFrame], operation: str = "process"
    ) -> List[GPUProcessingResult]:
        """批量GPU处理"""
        results = []

        self.logger.info(f"开始批量GPU处理 - 数据数量: {len(data_list)}, 操作: {operation}")

        for i, data in enumerate(data_list):
            try:
                if operation == "process":
                    result = self.process_data_with_gpu(data)
                elif operation == "predict":
                    result = self.generate_predictions_with_gpu(data)
                else:
                    raise ValueError(f"不支持的GPU操作: {operation}")

                results.append(result)

                # 进度日志
                if (i + 1) % 10 == 0:
                    self.logger.info(f"批量GPU处理进度: {i + 1}/{len(data_list)}")

            except Exception as e:
                self.logger.error(f"批量GPU处理中第{i + 1}个数据失败: {e}")

                error_result = GPUProcessingResult(
                    processing_time=0.0,
                    data_size=len(data),
                    gpu_memory_usage=0.0,
                    speedup_factor=0.0,
                    results=None,
                    errors=[f"批量处理失败: {str(e)}"],
                    performance_metrics={},
                )
                results.append(error_result)

        self.logger.info(f"批量GPU处理完成 - 成功: {len([r for r in results if not r.errors])}/{len(data_list)}")
        return results

    def optimize_hyperparameters_with_gpu(self, data: pd.DataFrame, model_type: str = "ridge") -> GPUProcessingResult:
        """使用GPU优化超参数"""
        start_time = time.time()

        try:
            optimization_result = self.price_predictor.optimize_hyperparameters(data=data, model_type=model_type)

            processing_time = time.time() - start_time

            result = GPUProcessingResult(
                processing_time=processing_time,
                data_size=len(data),
                gpu_memory_usage=self._get_gpu_memory_usage(),
                speedup_factor=self._calculate_speedup_factor(data, processing_time),
                results=optimization_result,
                errors=[],
                performance_metrics={
                    "best_params": optimization_result.get("best_params", {}),
                    "best_score": optimization_result.get("best_score", 0),
                    "model_type": model_type,
                },
            )

            self._update_performance_stats(result)

            self.logger.info(
                f"GPU超参数优化完成 - 模型: {model_type}, 最佳分数: {optimization_result.get('best_score', 0):.4f}"
            )
            return result

        except Exception as e:
            error_msg = f"GPU超参数优化失败: {str(e)}"
            self.logger.error(error_msg)

            result = GPUProcessingResult(
                processing_time=time.time() - start_time,
                data_size=len(data),
                gpu_memory_usage=0.0,
                speedup_factor=0.0,
                results=None,
                errors=[error_msg],
                performance_metrics={},
            )

            return result

    def benchmark_gpu_vs_cpu(self, data: pd.DataFrame, operation: str = "process") -> Dict:
        """GPU与CPU性能对比"""
        self.logger.info("开始GPU vs CPU性能对比测试")

        # GPU测试
        gpu_start = time.time()
        if operation == "process":
            gpu_result = self.process_data_with_gpu(data)
        elif operation == "predict":
            gpu_result = self.generate_predictions_with_gpu(data)
        elif operation == "optimize":
            gpu_result = self.optimize_hyperparameters_with_gpu(data)
        else:
            raise ValueError(f"不支持的操作类型: {operation}")

        gpu_time = time.time() - gpu_start

        # CPU测试
        self.logger.info("开始CPU性能测试...")
        cpu_start = time.time()

        if operation == "process":
            # 使用CPU版本的数据处理器
            from ..data_processor_gpu import DataProcessorCPU

            cpu_processor = DataProcessorCPU(gpu_enabled=False)
            cpu_result = cpu_processor.preprocess(data, ProcessingConfig())
        elif operation == "predict":
            # 使用CPU版本的价格预测器
            from ..price_predictor_gpu import PricePredictorCPU

            cpu_predictor = PricePredictorCPU(gpu_enabled=False)
            cpu_result = cpu_predictor.predict_price(data)
        elif operation == "optimize":
            # 使用CPU版本的超参数优化
            from ..price_predictor_gpu import PricePredictorCPU

            cpu_predictor = PricePredictorCPU(gpu_enabled=False)
            cpu_result = cpu_predictor.optimize_hyperparameters(data)
        else:
            raise ValueError(f"不支持的操作类型: {operation}")

        cpu_time = time.time() - cpu_start

        # 计算加速比
        speedup = cpu_time / gpu_time if gpu_time > 0 else 1.0

        benchmark_result = {
            "operation": operation,
            "gpu_time": gpu_time,
            "cpu_time": cpu_time,
            "speedup": speedup,
            "gpu_memory_usage": (gpu_result.gpu_memory_usage if hasattr(gpu_result, "gpu_memory_usage") else 0),
            "gpu_result": (gpu_result.results if hasattr(gpu_result, "results") else None),
            "cpu_result": cpu_result,
            "efficiency_metrics": {
                "gpu_efficiency": (1 / gpu_time) if gpu_time > 0 else 0,
                "cpu_efficiency": (1 / cpu_time) if cpu_time > 0 else 0,
                "memory_efficiency": ((1 / gpu_result.gpu_memory_usage) if gpu_result.gpu_memory_usage > 0 else 0),
            },
        }

        self.logger.info(f"性能对比完成 - GPU: {gpu_time:.4f}s, CPU: {cpu_time:.4f}s, 加速比: {speedup:.2f}x")
        return benchmark_result

    def _calculate_speedup_factor(self, data: pd.DataFrame, processing_time: float) -> float:
        """计算加速因子"""
        # 基于数据大小和时间的简单估算
        data_size = len(data)
        estimated_cpu_time = data_size * 0.001  # 假设CPU每毫秒处理1000行

        if processing_time > 0 and estimated_cpu_time > 0:
            return estimated_cpu_time / processing_time
        return 1.0

    def _get_gpu_memory_usage(self) -> float:
        """获取GPU内存使用情况"""
        if not self.gpu_enabled:
            return 0.0

        try:
            import cupy as cp

            return cp.cuda.get_default_memory_pool().used_bytes() / 1024 / 1024
        except Exception:
            return 0.0

    def _collect_performance_metrics(self) -> Dict[str, float]:
        """收集性能指标"""
        metrics = {}

        # 获取价格预测器性能
        price_performance = self.price_predictor.get_performance_summary()
        metrics.update(price_performance)

        # 添加GPU相关指标
        metrics["gpu_enabled"] = self.gpu_enabled
        metrics["n_jobs"] = self.config.n_jobs
        metrics["chunk_size"] = self.config.chunk_size

        return metrics

    def _update_performance_stats(self, result: GPUProcessingResult):
        """更新性能统计"""
        self.performance_stats["total_processing_time"] += result.processing_time
        self.performance_stats["total_data_processed"] += result.data_size

        if self.gpu_enabled and result.errors:
            self.performance_stats["gpu_enabled_operations"] += 1
        else:
            self.performance_stats["cpu_fallback_operations"] += 1

        # 计算平均加速比
        total_operations = (
            self.performance_stats["gpu_enabled_operations"] + self.performance_stats["cpu_fallback_operations"]
        )
        if total_operations > 0:
            self.performance_stats["average_speedup"] = self.performance_stats["total_processing_time"] / max(
                1, result.processing_time * total_operations
            )

    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能总结"""
        return {
            **self.performance_stats,
            "gpu_components_status": {
                "data_processor": {
                    "enabled": self.data_processor.gpu_enabled,
                    "chunks_processed": getattr(self.data_processor, "chunks_processed", 0),
                },
                "feature_generator": {
                    "enabled": self.feature_generator.gpu_enabled,
                    "features_generated": getattr(self.feature_generator, "features_generated", 0),
                },
                "price_predictor": {
                    "enabled": self.price_predictor.gpu_enabled,
                    "is_fitted": self.price_predictor.is_fitted,
                    "total_predictions": self.price_predictor.performance_stats["total_predictions"],
                },
            },
            "configuration": {
                "gpu_enabled": self.gpu_enabled,
                "n_jobs": self.config.n_jobs,
                "chunk_size": self.config.chunk_size,
                "memory_limit_gb": self.config.memory_limit_gb,
            },
        }

    def save_gpu_models(self, filepath: str):
        """保存GPU模型"""
        if self.price_predictor.is_fitted:
            self.price_predictor.save_model(filepath)
            self.logger.info(f"GPU模型已保存到: {filepath}")
        else:
            self.logger.warning("没有训练过的模型可以保存")

    def load_gpu_models(self, filepath: str):
        """加载GPU模型"""
        try:
            self.price_predictor.load_model(filepath)
            self.logger.info(f"GPU模型已从 {filepath} 加载")
        except Exception as e:
            self.logger.error(f"加载GPU模型失败: {e}")

    def generate_gpu_report(self) -> str:
        """生成GPU使用报告"""
        summary = self.get_performance_summary()

        report = f"""
MyStocks GPU加速使用报告
==========================

🚀 GPU环境状态: {"✅ 启用" if self.gpu_enabled else "❌ 禁用"}

📊 性能统计:
  • 总处理时间: {summary["total_processing_time"]:.2f}秒
  • 总处理数据量: {summary["total_data_processed"]}行
  • GPU操作次数: {summary["gpu_enabled_operations"]}
  • CPU回退次数: {summary["cpu_fallback_operations"]}
  • 平均加速比: {summary["average_speedup"]:.2f}x

🔧 GPU组件状态:
  • 数据处理器: {"✅ 启用" if summary["gpu_components_status"]["data_processor"]["enabled"] else "❌ 禁用"}
  • 特征生成器: {"✅ 启用" if summary["gpu_components_status"]["feature_generator"]["enabled"] else "❌ 禁用"}
  • 价格预测器: {"✅ 启用" if summary["gpu_components_status"]["price_predictor"]["enabled"] else "❌ 禁用"}
  • 模型训练状态: {"✅ 已训练" if summary["gpu_components_status"]["price_predictor"]["is_fitted"] else "❌ 未训练"}
  • 总预测次数: {summary["gpu_components_status"]["price_predictor"]["total_predictions"]}

⚙️  配置信息:
  • 并行任务数: {summary["configuration"]["n_jobs"]}
  • 块大小: {summary["configuration"]["chunk_size"]}
  • 内存限制: {summary["configuration"]["memory_limit_gb"]}GB

💡 使用建议:
  • 如果GPU操作失败频繁增加，建议检查GPU内存使用情况
  • 对于大数据集，适当增加chunk_size可以提高处理效率
  • 定期保存训练好的模型以避免重复训练

"""
        return report


# 集成到统一管理器的适配器
class MyStocksGPUAdapter:
    """MyStocks项目GPU适配器"""

    def __init__(self, unified_manager=None):
        self.gpu_manager = unified_manager or GPUUnifiedManager()
        self.logger = logging.getLogger(__name__)

    def enable_gpu_acceleration(self) -> bool:
        """启用GPU加速"""
        self.gpu_manager.gpu_enabled = True
        self.logger.info("GPU加速已启用")
        return True

    def disable_gpu_acceleration(self) -> bool:
        """禁用GPU加速"""
        self.gpu_manager.gpu_enabled = False
        self.logger.info("GPU加速已禁用")
        return True

    def is_gpu_available(self) -> bool:
        """检查GPU是否可用"""
        return self.gpu_manager.gpu_enabled

    def get_gpu_status(self) -> Dict[str, Any]:
        """获取GPU状态"""
        return {
            "gpu_available": self.gpu_manager.gpu_enabled,
            "gpu_models_trained": self.gpu_manager.price_predictor.is_fitted,
            "performance_summary": self.gpu_manager.get_performance_summary(),
        }


def main():
    """主函数 - 示例用法"""
    # 创建GPU统一管理器
    gpu_manager = GPUUnifiedManager()

    # 获取示例数据
    import yfinance as yf

    data = yf.download("AAPL", start="2023-01-01", end="2024-01-01")

    # 数据处理示例
    print("🚀 开始GPU数据处理示例...")
    process_result = gpu_manager.process_data_with_gpu(data)
    print(f"数据处理结果: {process_result.processing_time:.4f}秒")

    # 预测示例
    print("\n🎯 开始GPU预测示例...")
    predict_result = gpu_manager.generate_predictions_with_gpu(data)
    if predict_result.results:
        prediction = predict_result.results
        print(f"预测价格: {prediction.predicted_price:.2f}")
        print(f"置信度: {prediction.confidence_score:.2f}")

    # 性能对比
    print("\n📊 开始GPU vs CPU性能对比...")
    benchmark = gpu_manager.benchmark_gpu_vs_cpu(data, operation="predict")
    print(f"GPU时间: {benchmark['gpu_time']:.4f}s")
    print(f"CPU时间: {benchmark['cpu_time']:.4f}s")
    print(f"加速比: {benchmark['speedup']:.2f}x")

    # 生成报告
    print("\n📋 GPU使用报告:")
    print(gpu_manager.generate_gpu_report())


if __name__ == "__main__":
    main()
