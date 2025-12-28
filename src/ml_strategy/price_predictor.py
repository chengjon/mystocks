"""
价格预测策略模块 - LightGBM 股票价格预测

基于 PyProf 项目的价格预测模型，扩展为完整的预测策略系统。
使用 LightGBM 梯度提升决策树进行回归预测。

主要功能:
- LightGBM 模型训练
- 价格预测
- 超参数调优
- 模型持久化
- 完整的评估指标

作者: MyStocks Development Team
创建日期: 2025-10-19
版本: 1.0.0
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, train_test_split

# Scikit-learn

# LightGBM
try:
    from lightgbm import LGBMRegressor

    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    logging.warning("LightGBM 未安装，预测功能不可用")


class PricePredictorStrategy:
    """
    股票价格预测策略

    基于 LightGBM 的价格回归预测模型。

    示例:
        >>> predictor = PricePredictorStrategy()
        >>> metrics = predictor.train(X_train, y_train)
        >>> predictions = predictor.predict(X_test)
        >>> predictor.save_model('models/sh000001.pkl')
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化预测器

        Args:
            config: 模型配置参数（可选）
                如果不提供，使用默认配置
        """
        if not LIGHTGBM_AVAILABLE:
            raise ImportError("请安装 LightGBM: pip install lightgbm")

        self.config = config or self._default_config()
        self.model = None
        self.is_trained = False
        self.training_history = {}
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def _default_config() -> Dict[str, Any]:
        """
        默认 LightGBM 配置（基于 PyProf 项目的优化参数）

        Returns:
            配置字典
        """
        return {
            "boosting_type": "gbdt",
            "objective": "regression",
            "num_leaves": 25,
            "learning_rate": 0.2,
            "n_estimators": 70,
            "max_depth": 15,
            "metric": "rmse",
            "bagging_fraction": 0.8,
            "feature_fraction": 0.8,
            "reg_lambda": 0.9,
            "random_state": 42,
            "verbose": -1,  # 禁用训练输出
        }

    def train(
        self,
        features: pd.DataFrame,
        target: pd.Series,
        test_size: float = 0.2,
        eval_set: Optional[Tuple[pd.DataFrame, pd.Series]] = None,
        feature_names: Optional[list] = None,
    ) -> Dict[str, float]:
        # pylint: disable=too-many-positional-arguments
        """
        训练模型

        Args:
            features: 特征矩阵 (X)
            target: 目标向量 (y)
            test_size: 验证集比例
            eval_set: 显式指定验证集 (X_val, y_val)
            feature_names: 特征名称列表

        Returns:
            Dict: 评估指标
        """
        self.logger.info("开始训练模型...")
        start_time = datetime.now()

        # 数据切分
        if eval_set:
            X_train, y_train = features, target
            X_val, y_val = eval_set
        else:
            X_train, X_val, y_train, y_val = train_test_split(features, target, test_size=test_size, shuffle=False)

        # 初始化模型
        self.model = LGBMRegressor(**self.config)

        # 训练
        self.model.fit(
            X_train,
            y_train,
            eval_set=[(X_val, y_val)],
            eval_metric="rmse",
            # early_stopping_rounds=10, # 在新版 lightgbm 中可能需要通过 callbacks 实现
        )

        self.is_trained = True
        train_time = (datetime.now() - start_time).total_seconds()
        self.logger.info("模型训练完成，耗时: %.2f秒", train_time)

        # 评估
        metrics = self.evaluate(X_val, y_val)
        self.logger.info("验证集评估结果: %s", metrics)

        # 记录特征重要性
        if feature_names is None and hasattr(features, "columns"):
            feature_names = features.columns.tolist()

        if feature_names:
            importance = self.get_feature_importance(feature_names)
            self.logger.info("主要特征: %s", list(importance.keys())[:5])

        return metrics

    def predict(self, features: pd.DataFrame) -> np.ndarray:
        """
        预测价格

        Args:
            features: 特征矩阵 (X)

        Returns:
            np.ndarray: 预测结果
        """
        if not self.is_trained or self.model is None:
            raise ValueError("模型尚未训练")

        start_time = datetime.now()
        pred_result = self.model.predict(features)
        pred_time = (datetime.now() - start_time).total_seconds()

        self.logger.debug("预测完成: %d 条样本, 耗时: %.4f秒", len(features), pred_time)
        return pred_result

    def predict_with_confidence(
        self, X: pd.DataFrame, confidence_level: float = 0.95
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        预测价格并返回置信区间（简化版本）

        Args:
            X: 特征矩阵
            confidence_level: 置信水平（默认 0.95）

        Returns:
            (预测值, 下界, 上界)
        """
        predictions = self.predict(X)

        # 基于历史误差估算置信区间
        if "rmse" in self.training_history.get("metrics", {}):
            rmse = self.training_history["metrics"]["rmse"]
            margin = rmse * 1.96  # 95% 置信区间

            lower_bound = predictions - margin
            upper_bound = predictions + margin

            return predictions, lower_bound, upper_bound
        else:
            # 没有历史数据，返回预测值
            return predictions, predictions, predictions

    def hyperparameter_tuning(
        self,
        features: pd.DataFrame,
        target: pd.Series,
        param_grid: Dict[str, list],
        cv: int = 3,
        scoring: str = "neg_root_mean_squared_error",
    ) -> Dict[str, Any]:
        # pylint: disable=too-many-positional-arguments
        """
        超参数调优 (GridSearchCV)

        Args:
            features: 特征矩阵
            target: 目标向量
            param_grid: 参数网格
            cv: 交叉验证折数
            scoring: 评分指标

        Returns:
            Dict: 最佳参数
        """
        if not LIGHTGBM_AVAILABLE:
            raise ImportError("LightGBM not available")

        self.logger.info("开始超参数调优...")
        start_time = datetime.now()

        estimator = LGBMRegressor(objective="regression", metric="rmse", verbose=-1)

        grid_search = GridSearchCV(
            estimator=estimator,
            param_grid=param_grid,
            cv=cv,
            scoring=scoring,
            n_jobs=-1,
            verbose=1,
        )

        grid_search.fit(features, target)

        best_params = grid_search.best_params_
        search_time = (datetime.now() - start_time).total_seconds()

        self.logger.info("超参数调优完成，耗时: %.2f秒", search_time)
        self.logger.info("最佳参数: %s", best_params)
        self.logger.info("最佳得分: %.4f", grid_search.best_score_)

        # 更新配置
        self.config.update(best_params)

        return best_params

    def evaluate(self, features: pd.DataFrame, target: pd.Series) -> Dict[str, float]:
        """
        评估模型性能

        Args:
            features: 特征矩阵 (X)
            target: 真实值 (y)

        Returns:
            Dict: 评估指标
        """
        if not self.is_trained or self.model is None:
            raise ValueError("模型尚未训练")

        pred_result = self.model.predict(features)

        eval_metrics = {
            "mse": mean_squared_error(target, pred_result),
            "rmse": np.sqrt(mean_squared_error(target, pred_result)),
            "mae": mean_absolute_error(target, pred_result),
            "r2": r2_score(target, pred_result),
        }

        return eval_metrics

    @staticmethod
    def _calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """
        计算评估指标

        Args:
            y_true: 真实值
            y_pred: 预测值

        Returns:
            指标字典
        """
        # 确保是 numpy 数组
        if isinstance(y_true, pd.Series):
            y_true = y_true.values
        if isinstance(y_pred, pd.Series):
            y_pred = y_pred.values

        metrics = {
            "rmse": np.sqrt(mean_squared_error(y_true, y_pred)),
            "mae": mean_absolute_error(y_true, y_pred),
            "r2_score": r2_score(y_true, y_pred),
        }

        # MAPE (平均绝对百分比误差)
        # 避免除以零
        mask = y_true != 0
        if mask.sum() > 0:
            mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
            metrics["mape"] = mape
        else:
            metrics["mape"] = np.inf

        return metrics

    def save_model(self, file_path: str) -> None:
        """
        保存模型

        Args:
            file_path: 保存路径（.pkl 文件）

        Raises:
            ValueError: 模型未训练
        """
        if not self.is_trained:
            raise ValueError("模型未训练，无法保存")

        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # 保存模型和元数据
        model_data = {
            "model": self.model,
            "config": self.config,
            "training_history": self.training_history,
            "version": "1.0.0",
            "saved_at": datetime.now().isoformat(),
        }

        joblib.dump(model_data, file_path)

        self.logger.info("模型已保存: %s", file_path)

    def load_model(self, file_path: str) -> None:
        """
        加载模型

        Args:
            file_path: 模型文件路径

        Raises:
            FileNotFoundError: 文件不存在
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError("模型文件不存在: %s" % file_path)

        model_data = joblib.load(file_path)

        self.model = model_data["model"]
        self.config = model_data["config"]
        self.training_history = model_data.get("training_history", {})
        self.is_trained = True

        self.logger.info("模型已加载: %s", file_path)
        self.logger.info("模型版本: %s", model_data.get("version", "unknown"))
        self.logger.info("保存时间: %s", model_data.get("saved_at", "unknown"))

    def get_feature_importance(self, feature_names: Optional[list] = None, top_k: int = 10) -> pd.DataFrame:
        """
        获取特征重要性

        Args:
            feature_names: 特征名称列表（可选）
            top_k: 返回前 K 个重要特征（默认 10）

        Returns:
            特征重要性 DataFrame
        """
        if not self.is_trained:
            raise ValueError("模型未训练")

        importance = self.model.feature_importances_

        if feature_names is None:
            feature_names = self.training_history.get("feature_names", [f"feature_{i}" for i in range(len(importance))])

        df_importance = pd.DataFrame({"feature": feature_names, "importance": importance})

        df_importance = df_importance.sort_values("importance", ascending=False).head(top_k)

        return df_importance

    def plot_predictions(self, y_true: np.ndarray, y_pred: np.ndarray, save_path: Optional[str] = None) -> None:
        """
        绘制预测结果对比图

        Args:
            y_true: 真实值
            y_pred: 预测值
            save_path: 保存路径（可选）
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            self.logger.warning("matplotlib 未安装，无法绘图")
            return

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        # 散点图
        axes[0].scatter(y_true, y_pred, alpha=0.5)
        axes[0].plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], "r--", lw=2)
        axes[0].set_xlabel("Actual Price")
        axes[0].set_ylabel("Predicted Price")
        axes[0].set_title("Prediction vs Actual")
        axes[0].grid(True)

        # 时序图
        axes[1].plot(y_true, label="Actual", alpha=0.7)
        axes[1].plot(y_pred, label="Predicted", alpha=0.7)
        axes[1].set_xlabel("Sample Index")
        axes[1].set_ylabel("Price")
        axes[1].set_title("Time Series Comparison")
        axes[1].legend()
        axes[1].grid(True)

        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            plt.show()




if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)

    print("=== 价格预测模块测试 ===\n")

    # 1. 创建模拟数据
    print("1. 创建测试数据...")
    test_n_samples = 1000
    test_n_features = 15

    test_X = pd.DataFrame(
        np.random.randn(test_n_samples, test_n_features),
        columns=[f"feature_{i}" for i in range(test_n_features)],
    )
    # 目标变量：基于特征的线性组合 + 噪声
    test_y = pd.Series(
        test_X.iloc[:, :5].sum(axis=1) * 100 + np.random.randn(test_n_samples) * 10 + 3000,
        name="price",
    )

    print("   X.shape: %s" % str(test_X.shape))
    print("   y.shape: %s" % str(test_y.shape))
    print("   价格范围: [%.2f, %.2f]" % (test_y.min(), test_y.max()))

    # 2. 训练模型
    print("\n2. 训练模型...")
    test_predictor = PricePredictorStrategy()
    test_metrics = test_predictor.train(test_X, test_y, test_size=0.2)

    print("   ✅ RMSE: %.2f" % test_metrics["rmse"])
    print("   ✅ MAE: %.2f" % test_metrics["mae"])
    print("   ✅ R² Score: %.4f" % test_metrics["r2_score"])
    print("   ✅ MAPE: %.2f%%" % test_metrics["mape"])
    print("   ✅ 训练时间: %.2f秒" % test_metrics["training_time"])

    # 3. 预测
    print("\n3. 预测测试...")
    test_X_eval = test_X.iloc[:10]
    test_y_eval = test_y.iloc[:10]

    test_predictions = test_predictor.predict(test_X_eval)
    print("   前5个预测值: %s" % str(test_predictions[:5]))
    print("   前5个真实值: %s" % str(test_y_eval.values[:5]))

    # 4. 特征重要性
    print("\n4. 特征重要性...")
    test_importance = test_predictor.get_feature_importance(test_X.columns.tolist())
    print(test_importance)

    # 5. 模型保存/加载
    print("\n5. 模型持久化测试...")
    test_model_path = "models/test_predictor.pkl"
    test_predictor.save_model(test_model_path)
    print("   ✅ 模型已保存: %s" % test_model_path)

    # 加载模型
    test_predictor2 = PricePredictorStrategy()
    test_predictor2.load_model(test_model_path)
    test_predictions2 = test_predictor2.predict(test_X_eval)

    print("   ✅ 模型已加载")
    print("   预测一致性: %s" % str(np.allclose(test_predictions, test_predictions2)))

    print("\n✅ 价格预测模块测试完成！")
