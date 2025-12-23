"""
机器学习模块端到端集成测试

测试完整的数据流:
1. 读取通达信二进制文件
2. 生成特征
3. 训练模型
4. 价格预测
5. 模型评估

作者: MyStocks Development Team
创建日期: 2025-10-19
"""

import pytest
import pandas as pd
import numpy as np
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.adapters.tdx_adapter import TdxDataSource
from src.ml_strategy.feature_engineering import RollingFeatureGenerator
from src.ml_strategy.price_predictor import PricePredictorStrategy


class TestMLIntegration:
    """机器学习模块集成测试类"""

    @pytest.fixture
    def test_day_file(self):
        """测试数据文件路径"""
        return os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "temp/pyprof/data/sh000001.day"
        )

    @pytest.fixture
    def sample_data(self):
        """生成模拟数据（如果测试文件不存在）"""
        n_samples = 500
        df = pd.DataFrame(
            {
                "open": np.random.rand(n_samples) * 100 + 3000,
                "high": np.random.rand(n_samples) * 100 + 3100,
                "low": np.random.rand(n_samples) * 100 + 2900,
                "close": np.random.rand(n_samples) * 100 + 3000,
                "vol": np.random.rand(n_samples) * 1e8,
                "amount": np.random.rand(n_samples) * 1e11,
            }
        )
        return df

    def test_end_to_end_prediction_with_real_data(self, test_day_file):
        """端到端测试：使用真实数据"""
        if not os.path.exists(test_day_file):
            pytest.skip(f"测试文件不存在: {test_day_file}")

        print("\n=== 端到端测试：真实数据 ===")

        # 1. 读取数据
        print("步骤 1: 读取通达信数据文件...")
        tdx = TdxDataSource()
        df = tdx.read_day_file(test_day_file)

        assert not df.empty, "数据读取失败"
        assert len(df) > 100, "数据量不足"
        print(f"   ✅ 读取 {len(df)} 条记录")

        # 2. 特征工程
        print("步骤 2: 生成特征...")
        generator = RollingFeatureGenerator(window_size=10)
        X, y = generator.prepare_ml_data(df, target_col="close", forecast_horizon=1)

        assert len(X) == len(y), "X 和 y 长度不匹配"
        assert X.shape[1] == 15, "特征数量不正确"
        print(f"   ✅ 生成特征: X={X.shape}, y={y.shape}")

        # 3. 训练模型
        print("步骤 3: 训练预测模型...")
        predictor = PricePredictorStrategy()
        metrics = predictor.train(X, y, test_size=0.2)

        assert metrics["r2_score"] > 0.5, "模型性能太差"
        print(
            f"   ✅ 训练完成: RMSE={metrics['rmse']:.2f}, R²={metrics['r2_score']:.4f}"
        )

        # 4. 预测
        print("步骤 4: 价格预测...")
        X_test = X.iloc[-10:]
        y_test = y.iloc[-10:]
        predictions = predictor.predict(X_test)

        assert len(predictions) == len(X_test), "预测结果数量不匹配"
        print(f"   ✅ 预测完成: {len(predictions)} 条")

        # 5. 评估
        print("步骤 5: 模型评估...")
        eval_metrics = predictor.evaluate(X_test, y_test)
        print(f"   ✅ 评估 RMSE: {eval_metrics['rmse']:.2f}")

        # 6. 特征重要性
        print("步骤 6: 特征重要性分析...")
        importance = predictor.get_feature_importance(top_k=5)
        assert len(importance) <= 5, "特征重要性数量错误"
        print("   ✅ Top 5 特征:")
        print(importance.to_string(index=False))

        print("\n✅ 端到端测试通过（真实数据）")

    def test_end_to_end_prediction_with_sample_data(self, sample_data):
        """端到端测试：使用模拟数据"""
        print("\n=== 端到端测试：模拟数据 ===")

        df = sample_data

        # 1. 特征工程
        print("步骤 1: 生成特征...")
        generator = RollingFeatureGenerator(window_size=10)
        X, y = generator.prepare_ml_data(df, target_col="close", forecast_horizon=1)

        assert len(X) > 100, "数据量不足"
        print(f"   ✅ 特征: X={X.shape}, y={y.shape}")

        # 2. 训练模型
        print("步骤 2: 训练模型...")
        predictor = PricePredictorStrategy()
        metrics = predictor.train(X, y, test_size=0.2)

        assert "rmse" in metrics, "缺少 RMSE 指标"
        assert "r2_score" in metrics, "缺少 R² 指标"
        print(f"   ✅ RMSE={metrics['rmse']:.2f}, R²={metrics['r2_score']:.4f}")

        # 3. 模型保存/加载
        print("步骤 3: 模型持久化...")
        model_path = "models/test_integration.pkl"
        predictor.save_model(model_path)

        predictor2 = PricePredictorStrategy()
        predictor2.load_model(model_path)

        # 验证预测一致性
        X_test = X.iloc[:10]
        pred1 = predictor.predict(X_test)
        pred2 = predictor2.predict(X_test)

        assert np.allclose(pred1, pred2), "加载后预测结果不一致"
        print("   ✅ 模型保存/加载成功")

        print("\n✅ 端到端测试通过（模拟数据）")

    def test_different_feature_types(self, sample_data):
        """测试不同类型的特征生成"""
        print("\n=== 测试不同特征类型 ===")

        df = sample_data

        # 1. 聚合特征
        print("测试聚合特征...")
        generator_agg = RollingFeatureGenerator(window_size=10)
        X_agg, y_agg = generator_agg.prepare_ml_data(
            df, target_col="close", feature_type="aggregate"
        )
        print(f"   ✅ 聚合特征: X={X_agg.shape}")

        # 2. 原始滚动特征
        print("测试原始滚动特征...")
        generator_raw = RollingFeatureGenerator(window_size=5)
        X_raw, y_raw = generator_raw.prepare_ml_data(
            df, target_col="close", feature_type="raw"
        )
        print(f"   ✅ 原始特征: X={X_raw.shape}")

        # 3. 训练对比
        print("对比不同特征的预测性能...")
        predictor_agg = PricePredictorStrategy()
        metrics_agg = predictor_agg.train(X_agg, y_agg, test_size=0.2)

        predictor_raw = PricePredictorStrategy()
        metrics_raw = predictor_raw.train(X_raw, y_raw, test_size=0.2)

        print(f"   聚合特征 RMSE: {metrics_agg['rmse']:.2f}")
        print(f"   原始特征 RMSE: {metrics_raw['rmse']:.2f}")

        print("\n✅ 不同特征类型测试通过")

    def test_prediction_with_confidence(self, sample_data):
        """测试置信区间预测"""
        print("\n=== 测试置信区间预测 ===")

        df = sample_data
        generator = RollingFeatureGenerator(window_size=10)
        X, y = generator.prepare_ml_data(df)

        predictor = PricePredictorStrategy()
        predictor.train(X, y, test_size=0.2)

        X_test = X.iloc[:5]
        predictions, lower, upper = predictor.predict_with_confidence(X_test)

        assert len(predictions) == len(lower) == len(upper), "置信区间长度不匹配"
        assert (lower <= predictions).all(), "下界应 <= 预测值"
        assert (predictions <= upper).all(), "预测值应 <= 上界"

        print(f"   ✅ 预测: {predictions[:3]}")
        print(f"   ✅ 下界: {lower[:3]}")
        print(f"   ✅ 上界: {upper[:3]}")

        print("\n✅ 置信区间预测测试通过")

    def test_performance_metrics(self, sample_data):
        """测试性能指标"""
        print("\n=== 测试性能指标 ===")

        df = sample_data
        generator = RollingFeatureGenerator(window_size=10)
        X, y = generator.prepare_ml_data(df)

        # 测试训练时间
        import time

        predictor = PricePredictorStrategy()

        start_time = time.time()
        metrics = predictor.train(X, y, test_size=0.2)
        training_time = time.time() - start_time

        print(f"   训练时间: {training_time:.2f} 秒")
        print(f"   样本数量: {len(X)}")
        print(f"   特征数量: {X.shape[1]}")

        # 验证性能要求
        assert training_time < 10, "训练时间过长（> 10秒）"
        assert metrics["training_time"] > 0, "训练时间记录错误"

        print("\n✅ 性能指标测试通过")


if __name__ == "__main__":
    # 直接运行测试
    pytest.main([__file__, "-v", "-s"])
