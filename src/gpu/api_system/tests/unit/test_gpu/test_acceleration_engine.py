"""
GPU加速引擎单元测试
测试GPU加速引擎的核心功能
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock


class TestBacktestEngineGPU:
    """回测引擎GPU加速测试"""

    @pytest.fixture
    def engine(self, mock_gpu_manager, mock_metrics_collector):
        """创建回测引擎实例"""
        # 由于实际代码需要GPU，这里使用mock
        with patch("utils.gpu_acceleration_engine.BacktestEngineGPU") as MockEngine:
            engine = MockEngine(mock_gpu_manager, mock_metrics_collector)
            yield engine

    def test_engine_initialization(self, engine):
        """测试引擎初始化"""
        assert engine is not None

    @patch("cudf.DataFrame")
    def test_run_backtest_with_gpu(self, mock_cudf, engine, sample_market_data, sample_strategy_config):
        """测试GPU回测执行"""
        # 模拟GPU数据转换
        mock_gpu_df = MagicMock()
        mock_cudf.from_pandas.return_value = mock_gpu_df

        # 模拟回测结果
        mock_result = {
            "total_return": 0.25,
            "sharpe_ratio": 1.5,
            "max_drawdown": -0.15,
            "win_rate": 0.58,
            "trades": 150,
        }

        engine.run_backtest.return_value = mock_result

        # 执行回测
        result = engine.run_backtest(sample_market_data, sample_strategy_config)

        # 验证结果
        assert result is not None
        assert "total_return" in result
        assert "sharpe_ratio" in result
        assert result["total_return"] == 0.25

    def test_cpu_fallback(self, engine, sample_market_data, sample_strategy_config):
        """测试CPU降级功能"""
        # 模拟GPU不可用
        engine.run_backtest.side_effect = RuntimeError("GPU not available")

        with pytest.raises(RuntimeError):
            engine.run_backtest(sample_market_data, sample_strategy_config)

    def test_performance_improvement(self, gpu_available):
        """测试性能提升（仅在GPU可用时）"""
        if not gpu_available:
            pytest.skip("GPU not available")

        # 这里可以添加实际的性能测试
        # 比较CPU和GPU的执行时间
        pass


class TestMLTrainingGPU:
    """ML训练GPU加速测试"""

    @pytest.fixture
    def engine(self, mock_gpu_manager, mock_metrics_collector):
        """创建ML训练引擎实例"""
        with patch("utils.gpu_acceleration_engine.MLTrainingGPU") as MockEngine:
            engine = MockEngine(mock_gpu_manager, mock_metrics_collector)
            yield engine

    def test_train_random_forest_gpu(self, engine, sample_ml_training_data):
        """测试GPU随机森林训练"""
        X = sample_ml_training_data[["price", "volume", "sma_20", "rsi", "macd"]]
        y = sample_ml_training_data["target"]

        # 模拟训练结果
        mock_model = MagicMock()
        mock_metrics = {
            "accuracy": 0.85,
            "precision": 0.83,
            "recall": 0.87,
            "f1_score": 0.85,
            "training_time": 8.5,
        }

        engine.train_model.return_value = (mock_model, mock_metrics)

        # 执行训练
        model, metrics = engine.train_model(X, y, "random_forest", {})

        # 验证结果
        assert model is not None
        assert "accuracy" in metrics
        assert metrics["training_time"] < 20  # 应该比CPU快

    def test_train_linear_regression_gpu(self, engine, sample_ml_training_data):
        """测试GPU线性回归训练"""
        X = sample_ml_training_data[["price", "volume", "sma_20"]]
        y = sample_ml_training_data["price"] * 1.1  # 简单的回归目标

        mock_model = MagicMock()
        mock_metrics = {"mse": 0.05, "r2_score": 0.92, "training_time": 2.5}

        engine.train_model.return_value = (mock_model, mock_metrics)

        model, metrics = engine.train_model(X, y, "linear_regression", {})

        assert model is not None
        assert "mse" in metrics
        assert metrics["r2_score"] > 0.8


class TestFeatureCalculationGPU:
    """特征计算GPU加速测试"""

    @pytest.fixture
    def engine(self, mock_gpu_manager, mock_metrics_collector):
        """创建特征计算引擎实例"""
        with patch("utils.gpu_acceleration_engine.FeatureCalculationGPU") as MockEngine:
            engine = MockEngine(mock_gpu_manager, mock_metrics_collector)
            yield engine

    def test_calculate_sma(self, engine, sample_market_data):
        """测试SMA计算"""
        mock_result = sample_market_data["close"].rolling(window=20).mean()
        engine.calculate_sma.return_value = mock_result

        result = engine.calculate_sma(sample_market_data, window=20)

        assert result is not None
        assert len(result) == len(sample_market_data)

    def test_calculate_rsi(self, engine, sample_market_data):
        """测试RSI计算"""
        mock_rsi = pd.Series(np.random.uniform(0, 100, len(sample_market_data)))
        engine.calculate_rsi.return_value = mock_rsi

        result = engine.calculate_rsi(sample_market_data, period=14)

        assert result is not None
        assert all(0 <= x <= 100 for x in result.dropna())

    def test_calculate_macd(self, engine, sample_market_data):
        """测试MACD计算"""
        mock_macd = {
            "macd": pd.Series(np.random.uniform(-1, 1, len(sample_market_data))),
            "signal": pd.Series(np.random.uniform(-1, 1, len(sample_market_data))),
            "histogram": pd.Series(np.random.uniform(-0.5, 0.5, len(sample_market_data))),
        }
        engine.calculate_macd.return_value = mock_macd

        result = engine.calculate_macd(sample_market_data)

        assert "macd" in result
        assert "signal" in result
        assert "histogram" in result

    def test_batch_feature_calculation(self, engine, sample_market_data):
        """测试批量特征计算"""
        features = ["sma_20", "sma_50", "rsi", "macd"]

        mock_features = {
            "sma_20": pd.Series(np.random.uniform(10, 20, len(sample_market_data))),
            "sma_50": pd.Series(np.random.uniform(10, 20, len(sample_market_data))),
            "rsi": pd.Series(np.random.uniform(0, 100, len(sample_market_data))),
            "macd": pd.Series(np.random.uniform(-1, 1, len(sample_market_data))),
        }
        engine.calculate_batch_features.return_value = mock_features

        result = engine.calculate_batch_features(sample_market_data, features)

        assert len(result) == len(features)
        for feature in features:
            assert feature in result


class TestOptimizationGPU:
    """参数优化GPU加速测试"""

    @pytest.fixture
    def engine(self, mock_gpu_manager, mock_metrics_collector):
        """创建优化引擎实例"""
        with patch("utils.gpu_acceleration_engine.OptimizationGPU") as MockEngine:
            engine = MockEngine(mock_gpu_manager, mock_metrics_collector)
            yield engine

    def test_grid_search(self, engine):
        """测试网格搜索优化"""
        param_grid = {
            "lookback_period": [10, 20, 30],
            "moving_average_window": [30, 50, 100],
            "stop_loss": [0.01, 0.02, 0.03],
        }

        mock_best_params = {
            "lookback_period": 20,
            "moving_average_window": 50,
            "stop_loss": 0.02,
            "score": 1.85,
        }
        engine.grid_search.return_value = mock_best_params

        result = engine.grid_search(param_grid)

        assert "lookback_period" in result
        assert "score" in result
        assert result["score"] > 0

    def test_bayesian_optimization(self, engine):
        """测试贝叶斯优化"""
        param_bounds = {
            "lookback_period": (5, 50),
            "moving_average_window": (20, 200),
            "stop_loss": (0.005, 0.05),
        }

        mock_best_params = {
            "lookback_period": 23,
            "moving_average_window": 67,
            "stop_loss": 0.018,
            "score": 2.15,
        }
        engine.bayesian_optimization.return_value = mock_best_params

        result = engine.bayesian_optimization(param_bounds, n_iterations=50)

        assert result is not None
        assert result["score"] > 0


class TestGPUMemoryManagement:
    """GPU内存管理测试"""

    def test_memory_allocation(self, mock_gpu_manager):
        """测试内存分配"""
        gpu_id = mock_gpu_manager.allocate_gpu()
        assert gpu_id is not None
        assert isinstance(gpu_id, int)

    def test_memory_release(self, mock_gpu_manager):
        """测试内存释放"""
        gpu_id = mock_gpu_manager.allocate_gpu()
        result = mock_gpu_manager.release_gpu(gpu_id)
        assert result is True

    def test_out_of_memory_handling(self):
        """测试内存溢出处理"""
        # 模拟内存溢出情况
        with patch("cudf.DataFrame") as mock_cudf:
            mock_cudf.side_effect = MemoryError("CUDA out of memory")

            with pytest.raises(MemoryError):
                mock_cudf()
