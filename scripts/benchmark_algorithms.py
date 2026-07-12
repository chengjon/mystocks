#!/usr/bin/env python3
"""算法性能基准测试脚本

对比测试三个分类算法的性能：
- SVM (Support Vector Machine)
- Decision Tree (Random Forest)
- Naive Bayes (Gaussian)

测试维度：
- 训练时间
- 预测时间
- GPU vs CPU 性能对比
- 准确率对比

作者: MyStocks团队
日期: 2026-01-12
"""

import asyncio
import logging
import sys
import time
from typing import Any, Dict, List

import numpy as np
import pandas as pd


# 添加项目根目录到路径
project_root = "/opt/claude/mystocks_spec"
sys.path.insert(0, project_root)

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class AlgorithmBenchmark:
    """算法性能基准测试类"""

    def __init__(self):
        self.algorithms = {}
        self.results = {}

    async def setup_algorithms(self):
        """设置所有算法实例"""
        from src.algorithms.classification.decision_tree_algorithm import DecisionTreeAlgorithm
        from src.algorithms.classification.naive_bayes_algorithm import NaiveBayesAlgorithm
        from src.algorithms.classification.svm_algorithm import SVMAlgorithm
        from src.algorithms.metadata import AlgorithmFingerprint

        # SVM算法
        svm_metadata = AlgorithmFingerprint.from_config(
            {
                "name": "SVM_Benchmark",
                "description": "SVM algorithm benchmark",
                "algorithm_type": "classification",
                "gpu_enabled": True,
            },
        )
        self.algorithms["SVM"] = SVMAlgorithm(svm_metadata)

        # Decision Tree算法
        dt_metadata = AlgorithmFingerprint.from_config(
            {
                "name": "DecisionTree_Benchmark",
                "description": "Decision Tree algorithm benchmark",
                "algorithm_type": "classification",
                "gpu_enabled": True,
            },
        )
        self.algorithms["Decision Tree"] = DecisionTreeAlgorithm(dt_metadata)

        # Naive Bayes算法
        nb_metadata = AlgorithmFingerprint.from_config(
            {
                "name": "NaiveBayes_Benchmark",
                "description": "Naive Bayes algorithm benchmark",
                "algorithm_type": "classification",
                "gpu_enabled": True,
            },
        )
        self.algorithms["Naive Bayes"] = NaiveBayesAlgorithm(nb_metadata)

        logger.info(f"✓ 已设置 {len(self.algorithms)} 个算法进行基准测试")

    def generate_benchmark_data(self, n_samples: int = 5000, n_features: int = 20) -> pd.DataFrame:
        """生成基准测试数据"""
        np.random.seed(42)

        data = {}
        # 生成特征数据
        for i in range(n_features):
            data[f"feature_{i}"] = np.random.randn(n_samples)

        # 为Naive Bayes生成更合适的正值特征
        for i in range(5):  # 前5个特征为正值
            data[f"feature_{i}"] = np.abs(data[f"feature_{i}"])

        # 生成目标变量 (3分类问题)
        data["target"] = np.random.randint(0, 3, n_samples)

        df = pd.DataFrame(data)
        logger.info(f"✓ 生成基准测试数据: {n_samples} 个样本, {n_features} 个特征")
        return df

    async def benchmark_algorithm(self, name: str, data: pd.DataFrame, n_test_samples: int = 1000) -> Dict[str, Any]:
        """对单个算法进行基准测试"""
        logger.info(f"开始测试算法: {name}")

        algorithm = self.algorithms[name]
        results = {"algorithm": name}

        # 准备训练配置
        feature_cols = [col for col in data.columns if col.startswith("feature_")]
        config = {
            "feature_columns": feature_cols,
            "target_column": "target",
        }

        # 添加算法特定参数
        if name == "SVM":
            config["svm_params"] = {"C": 1.0, "kernel": "rbf", "random_state": 42}
        elif name == "Decision Tree":
            config["dt_params"] = {"max_depth": 10, "random_state": 42}
        elif name == "Naive Bayes":
            config["nb_params"] = {"var_smoothing": 1e-9}

        # 训练基准测试
        train_start = time.time()
        train_result = await algorithm.train(data, config)
        train_time = time.time() - train_start

        results.update(
            {
                "training_time": train_time,
                "training_accuracy": train_result.get("training_metrics", {}).get("accuracy", 0.0),
                "gpu_used_training": train_result.get("training_metrics", {}).get("gpu_used", False),
            },
        )

        # 准备测试数据
        test_data = data.sample(n=n_test_samples, random_state=42).reset_index(drop=True)

        # 预测基准测试
        predict_start = time.time()
        predict_result = await algorithm.predict(test_data, train_result)
        predict_time = time.time() - predict_start

        results.update(
            {
                "prediction_time": predict_time,
                "gpu_used_prediction": predict_result.get("gpu_used", False),
                "predictions_count": len(predict_result.get("predictions", [])),
            },
        )

        # 评估基准测试
        actual_labels = test_data["target"].values
        eval_start = time.time()
        eval_result = algorithm.evaluate(predict_result, actual_labels)
        eval_time = time.time() - eval_start

        results.update(
            {
                "evaluation_time": eval_time,
                "test_accuracy": eval_result.get("accuracy", 0.0),
                "precision": eval_result.get("precision", 0.0),
                "recall": eval_result.get("recall", 0.0),
                "f1_score": eval_result.get("f1_score", 0.0),
            },
        )

        logger.info(".4f")
        logger.info(".4f")
        logger.info(f"  - 测试准确率: {results['test_accuracy']:.4f}")

        return results

    async def run_full_benchmark(self, data_sizes: List[int] = None) -> Dict[str, Any]:
        """运行完整基准测试"""
        if data_sizes is None:
            data_sizes = [1000, 2500, 5000]

        logger.info("=" * 80)
        logger.info("算法性能基准测试")
        logger.info("=" * 80)

        all_results = {}

        for n_samples in data_sizes:
            logger.info(f"\n📊 测试数据集大小: {n_samples} 样本")
            logger.info("-" * 50)

            # 生成测试数据
            data = self.generate_benchmark_data(n_samples=n_samples)

            # 测试每个算法
            dataset_results = {}
            for algo_name in self.algorithms.keys():
                try:
                    result = await self.benchmark_algorithm(algo_name, data)
                    dataset_results[algo_name] = result
                except Exception as e:
                    logger.error(f"❌ {algo_name} 基准测试失败: {e}")
                    dataset_results[algo_name] = {"algorithm": algo_name, "error": str(e)}

            all_results[f"samples_{n_samples}"] = dataset_results

        return all_results

    def print_benchmark_summary(self, results: Dict[str, Any]):
        """打印基准测试摘要"""
        logger.info("\n" + "=" * 80)
        logger.info("基准测试摘要")
        logger.info("=" * 80)

        for dataset_key, dataset_results in results.items():
            sample_size = dataset_key.split("_")[1]
            logger.info(f"\n📊 数据集: {sample_size} 样本")

            # 创建比较表格
            header = ".4f"
            logger.info(header)
            logger.info("-" * len(header))

            for algo_name, result in dataset_results.items():
                if "error" in result:
                    logger.info("<15")
                else:
                    gpu_train = "✓" if result.get("gpu_used_training") else "✗"
                    gpu_pred = "✓" if result.get("gpu_used_prediction") else "✗"
                    logger.info("<15")

        logger.info("\n" + "=" * 80)
        logger.info("✅ 基准测试完成")
        logger.info("=" * 80)


async def main():
    """主函数"""
    try:
        # 创建基准测试实例
        benchmark = AlgorithmBenchmark()

        # 设置算法
        await benchmark.setup_algorithms()

        # 运行基准测试
        results = await benchmark.run_full_benchmark()

        # 打印摘要
        benchmark.print_benchmark_summary(results)

        logger.info("\n🎉 所有算法性能基准测试完成!")

    except Exception as e:
        logger.error(f"❌ 基准测试失败: {e}")
        import traceback

        logger.error(traceback.format_exc())
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
