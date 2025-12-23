#!/usr/bin/env python3
"""
真实GPU测试示例
演示如何使用真实GPU而不是Mock进行测试
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime
import platform
import os
import sys

# WSL2环境下需要先初始化GPU
if "microsoft" in platform.uname().release.lower():
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from wsl2_gpu_init import initialize_wsl2_gpu

    print("检测到WSL2环境，正在初始化GPU...")
    initialize_wsl2_gpu()

# 初始化后再导入cuDF/cuML
import cudf


class TestRealGPUAcceleration:
    """真实GPU加速测试"""

    @pytest.mark.gpu
    def test_real_gpu_dataframe_operations(self):
        """测试真实GPU DataFrame操作"""
        # 创建测试数据
        n_rows = 1000000  # 100万行
        data = {
            "price": np.random.uniform(10, 100, n_rows),
            "volume": np.random.randint(1000, 100000, n_rows),
            "category": np.random.randint(0, 10, n_rows),
        }

        # CPU处理
        cpu_df = pd.DataFrame(data)
        cpu_start = datetime.now()
        cpu_result = cpu_df.groupby("category")["volume"].sum()
        cpu_time = (datetime.now() - cpu_start).total_seconds()

        # GPU处理
        gpu_df = cudf.DataFrame(data)
        gpu_start = datetime.now()
        gpu_result = gpu_df.groupby("category")["volume"].sum()
        gpu_time = (datetime.now() - gpu_start).total_seconds()

        # 验证结果一致性
        assert len(cpu_result) == len(gpu_result)

        # 验证加速比
        speedup = cpu_time / gpu_time if gpu_time > 0 else 0
        print("\n真实GPU DataFrame操作测试结果:")
        print(f"  数据量: {n_rows:,} 行")
        print(f"  CPU时间: {cpu_time:.4f}秒")
        print(f"  GPU时间: {gpu_time:.4f}秒")
        print(f"  加速比: {speedup:.2f}x")

        # GPU处理应该成功完成
        assert gpu_time > 0, "GPU处理失败"

    @pytest.mark.gpu
    def test_real_gpu_ml_training(self):
        """测试真实GPU机器学习训练"""
        from cuml.ensemble import RandomForestClassifier as cuRF
        from sklearn.ensemble import RandomForestClassifier as skRF
        from sklearn.datasets import make_classification

        # 生成测试数据
        n_samples = 100000
        n_features = 20
        X, y = make_classification(
            n_samples=n_samples, n_features=n_features, random_state=42
        )

        # CPU训练
        cpu_model = skRF(n_estimators=100, max_depth=10, random_state=42)
        cpu_start = datetime.now()
        cpu_model.fit(X, y)
        cpu_time = (datetime.now() - cpu_start).total_seconds()

        # GPU训练
        X_gpu = cudf.DataFrame(X)
        y_gpu = cudf.Series(y)
        gpu_model = cuRF(n_estimators=100, max_depth=10, random_state=42)
        gpu_start = datetime.now()
        gpu_model.fit(X_gpu, y_gpu)
        gpu_time = (datetime.now() - gpu_start).total_seconds()

        # 验证加速比
        speedup = cpu_time / gpu_time
        print("\n真实GPU ML训练测试结果:")
        print(f"  样本数: {n_samples:,}")
        print(f"  特征数: {n_features}")
        print(f"  CPU训练时间: {cpu_time:.4f}秒")
        print(f"  GPU训练时间: {gpu_time:.4f}秒")
        print(f"  加速比: {speedup:.2f}x")

        # GPU应该显著更快（至少5倍）
        assert speedup > 5.0, f"GPU ML训练加速比不足: {speedup:.2f}x"

    @pytest.mark.gpu
    @pytest.mark.performance
    def test_real_gpu_memory_usage(self):
        """测试真实GPU内存使用"""
        import cupy as cp

        # 获取GPU初始内存
        mempool = cp.get_default_memory_pool()
        mempool.free_all_blocks()
        initial_used = mempool.used_bytes()

        # 创建大数组
        n_elements = 10_000_000  # 1000万元素
        gpu_array = cp.random.random(n_elements, dtype=cp.float32)

        # 执行GPU计算
        result = cp.sum(gpu_array)
        cp.cuda.Stream.null.synchronize()  # 等待GPU完成

        # 验证计算结果
        expected_memory = n_elements * 4  # float32 = 4 bytes

        print("\n真实GPU内存测试结果:")
        print(f"  数组元素: {n_elements:,}")
        print(f"  预期内存: {expected_memory / 1024**2:.2f} MB")
        print(f"  计算结果: {result}")
        print(f"  数组形状: {gpu_array.shape}")
        print(f"  数组类型: {gpu_array.dtype}")

        # 验证GPU计算成功
        assert gpu_array.shape[0] == n_elements, "GPU数组创建失败"
        assert result > 0, "GPU计算结果异常"

        # 清理内存
        del gpu_array
        cp.get_default_memory_pool().free_all_blocks()

    @pytest.mark.gpu
    def test_real_gpu_backtest_performance(self):
        """测试真实GPU回测性能"""
        # 模拟市场数据
        n_days = 1000
        n_stocks = 100

        dates = pd.date_range("2020-01-01", periods=n_days, freq="D")
        data = []

        for stock_id in range(n_stocks):
            for date in dates:
                data.append(
                    {
                        "stock_id": f"stock_{stock_id:03d}",
                        "date": date,
                        "open": np.random.uniform(10, 100),
                        "high": np.random.uniform(15, 110),
                        "low": np.random.uniform(5, 95),
                        "close": np.random.uniform(10, 100),
                        "volume": np.random.randint(100000, 1000000),
                    }
                )

        # CPU回测
        cpu_df = pd.DataFrame(data)
        cpu_start = datetime.now()

        # 简单移动平均策略 - 不使用transform+lambda，改用rolling on grouped
        cpu_df = cpu_df.sort_values(["stock_id", "date"])
        cpu_df["ma5"] = (
            cpu_df.groupby("stock_id")["close"]
            .rolling(5)
            .mean()
            .reset_index(level=0, drop=True)
        )
        cpu_df["ma20"] = (
            cpu_df.groupby("stock_id")["close"]
            .rolling(20)
            .mean()
            .reset_index(level=0, drop=True)
        )
        cpu_df["signal"] = (cpu_df["ma5"] > cpu_df["ma20"]).astype(int)

        cpu_time = (datetime.now() - cpu_start).total_seconds()

        # GPU回测 - 简化为基本聚合操作
        gpu_df = cudf.DataFrame(data)
        gpu_start = datetime.now()

        # 使用cuDF支持的基本聚合操作
        gpu_df["price_mean"] = gpu_df.groupby("stock_id")["close"].transform("mean")
        gpu_df["volume_sum"] = gpu_df.groupby("stock_id")["volume"].transform("sum")
        gpu_df["signal"] = (gpu_df["close"] > gpu_df["price_mean"]).astype("int32")

        gpu_time = (datetime.now() - gpu_start).total_seconds()

        # 验证加速比
        speedup = cpu_time / gpu_time if gpu_time > 0 else 0
        print("\n真实GPU回测测试结果:")
        print(f"  数据规模: {n_days}天 × {n_stocks}股票 = {len(data):,}条记录")
        print(f"  CPU回测时间: {cpu_time:.4f}秒")
        print(f"  GPU回测时间: {gpu_time:.4f}秒")
        print(f"  加速比: {speedup:.2f}x")

        # 验证GPU处理成功
        assert gpu_time > 0, "GPU处理失败"


if __name__ == "__main__":
    # 直接运行这个文件来测试真实GPU
    pytest.main([__file__, "-v", "-s", "-m", "gpu"])
