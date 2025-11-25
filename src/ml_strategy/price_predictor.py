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

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
import logging
from datetime import datetime

# Scikit-learn
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib

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
        X: pd.DataFrame,
        y: pd.Series,
        test_size: float = 0.2,
        random_state: int = 42,
        validation_split: bool = True,
    ) -> Dict[str, float]:
        """
        训练模型

        Args:
            X: 特征矩阵
            y: 目标变量
            test_size: 测试集比例（默认 0.2）
            random_state: 随机种子（默认 42）
            validation_split: 是否分割验证集（默认 True）

        Returns:
            评估指标字典
                - rmse: 均方根误差
                - mae: 平均绝对误差
                - r2_score: 决定系数
                - mape: 平均绝对百分比误差

        Raises:
            ValueError: 输入数据无效
        """
        # 验证输入
        if X.empty or y.empty:
            raise ValueError("输入数据不能为空")

        if len(X) != len(y):
            raise ValueError(f"X 和 y 长度不匹配: {len(X)} vs {len(y)}")

        self.logger.info(f"开始训练模型: X={X.shape}, y={y.shape}")

        # 数据分割
        if validation_split:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state
            )
            self.logger.info(f"数据分割: 训练集={len(X_train)}, 测试集={len(X_test)}")
        else:
            X_train, y_train = X, y
            X_test, y_test = X, y
            self.logger.info(f"未分割数据，使用全部数据训练: {len(X_train)} 条")

        # 创建并训练模型
        start_time = datetime.now()
        self.model = LGBMRegressor(**self.config)

        self.model.fit(
            X_train,
            y_train,
            eval_set=[(X_test, y_test)] if validation_split else None,
            eval_metric="rmse",
        )

        training_time = (datetime.now() - start_time).total_seconds()
        self.is_trained = True

        # 预测
        y_pred = self.model.predict(X_test)

        # 计算评估指标
        metrics = self._calculate_metrics(y_test, y_pred)
        metrics["training_time"] = training_time
        metrics["train_samples"] = len(X_train)
        metrics["test_samples"] = len(X_test)

        # 保存训练历史
        self.training_history = {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "config": self.config,
            "feature_count": X.shape[1],
            "feature_names": list(X.columns),
        }

        self.logger.info(
            f"训练完成: RMSE={metrics['rmse']:.2f}, "
            f"R²={metrics['r2_score']:.4f}, "
            f"耗时={training_time:.2f}秒"
        )

        return metrics

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        预测价格

        Args:
            X: 特征矩阵

        Returns:
            预测结果数组

        Raises:
            ValueError: 模型未训练
        """
        if not self.is_trained:
            raise ValueError("模型未训练，请先调用 train() 方法")

        if X.empty:
            raise ValueError("输入数据不能为空")

        self.logger.info(f"开始预测: {len(X)} 条记录")

        predictions = self.model.predict(X)

        self.logger.info(
            f"预测完成: 预测范围=[{predictions.min():.2f}, {predictions.max():.2f}]"
        )

        return predictions

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
        X: pd.DataFrame,
        y: pd.Series,
        param_grid: Optional[Dict[str, list]] = None,
        cv: int = 5,
        scoring: str = "neg_mean_squared_error",
    ) -> Dict[str, Any]:
        """
        超参数调优（网格搜索）

        Args:
            X: 特征矩阵
            y: 目标变量
            param_grid: 参数网格（可选）
            cv: 交叉验证折数（默认 5）
            scoring: 评分指标（默认 neg_mean_squared_error）

        Returns:
            调优结果字典
                - best_params: 最佳参数
                - best_score: 最佳得分
                - cv_results: 交叉验证结果

        Example:
            >>> param_grid = {
            ...     'num_leaves': [15, 25, 35],
            ...     'n_estimators': [50, 70, 100],
            ...     'learning_rate': [0.1, 0.2, 0.3]
            ... }
            >>> results = predictor.hyperparameter_tuning(X, y, param_grid)
        """
        if param_grid is None:
            # 默认参数网格
            param_grid = {
                "num_leaves": [15, 25, 35],
                "n_estimators": [50, 70, 100],
                "learning_rate": [0.1, 0.2, 0.3],
            }

        self.logger.info(
            f"开始超参数调优: CV={cv}, 参数组合={np.prod([len(v) for v in param_grid.values()])}"
        )

        start_time = datetime.now()

        # 创建基础模型
        base_model = LGBMRegressor(**self.config)

        # 网格搜索
        grid_search = GridSearchCV(
            base_model,
            param_grid=param_grid,
            cv=cv,
            scoring=scoring,
            n_jobs=-1,
            verbose=0,
        )

        grid_search.fit(X, y)

        tuning_time = (datetime.now() - start_time).total_seconds()

        # 更新配置为最佳参数
        self.config.update(grid_search.best_params_)

        results = {
            "best_params": grid_search.best_params_,
            "best_score": -grid_search.best_score_,  # 转为正数（RMSE）
            "cv_results": grid_search.cv_results_,
            "tuning_time": tuning_time,
        }

        self.logger.info(
            f"调优完成: 最佳 RMSE={results['best_score']:.2f}, "
            f"耗时={tuning_time:.2f}秒"
        )
        self.logger.info(f"最佳参数: {results['best_params']}")

        return results

    def evaluate(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """
        评估模型性能

        Args:
            X: 特征矩阵
            y: 真实值

        Returns:
            评估指标字典
        """
        if not self.is_trained:
            raise ValueError("模型未训练")

        y_pred = self.predict(X)
        metrics = self._calculate_metrics(y, y_pred)

        self.logger.info(
            f"评估结果: RMSE={metrics['rmse']:.2f}, R²={metrics['r2_score']:.4f}"
        )

        return metrics

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

        self.logger.info(f"模型已保存: {file_path}")

    def load_model(self, file_path: str) -> None:
        """
        加载模型

        Args:
            file_path: 模型文件路径

        Raises:
            FileNotFoundError: 文件不存在
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"模型文件不存在: {file_path}")

        model_data = joblib.load(file_path)

        self.model = model_data["model"]
        self.config = model_data["config"]
        self.training_history = model_data.get("training_history", {})
        self.is_trained = True

        self.logger.info(f"模型已加载: {file_path}")
        self.logger.info(f"模型版本: {model_data.get('version', 'unknown')}")
        self.logger.info(f"保存时间: {model_data.get('saved_at', 'unknown')}")

    def get_feature_importance(
        self, feature_names: Optional[list] = None, top_k: int = 10
    ) -> pd.DataFrame:
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
            feature_names = self.training_history.get(
                "feature_names", [f"feature_{i}" for i in range(len(importance))]
            )

        df_importance = pd.DataFrame(
            {"feature": feature_names, "importance": importance}
        )

        df_importance = df_importance.sort_values("importance", ascending=False).head(
            top_k
        )

        return df_importance

    def plot_predictions(
        self, y_true: np.ndarray, y_pred: np.ndarray, save_path: Optional[str] = None
    ) -> None:
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
        axes[0].plot(
            [y_true.min(), y_true.max()], [y_true.min(), y_true.max()], "r--", lw=2
        )
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
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
            self.logger.info(f"预测图表已保存: {save_path}")
        else:
            plt.show()


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)

    print("=== 价格预测模块测试 ===\n")

    # 1. 创建模拟数据
    print("1. 创建测试数据...")
    n_samples = 1000
    n_features = 15

    X = pd.DataFrame(
        np.random.randn(n_samples, n_features),
        columns=[f"feature_{i}" for i in range(n_features)],
    )
    # 目标变量：基于特征的线性组合 + 噪声
    y = pd.Series(
        X.iloc[:, :5].sum(axis=1) * 100 + np.random.randn(n_samples) * 10 + 3000,
        name="price",
    )

    print(f"   X.shape: {X.shape}")
    print(f"   y.shape: {y.shape}")
    print(f"   价格范围: [{y.min():.2f}, {y.max():.2f}]")

    # 2. 训练模型
    print("\n2. 训练模型...")
    predictor = PricePredictorStrategy()
    metrics = predictor.train(X, y, test_size=0.2)

    print(f"   ✅ RMSE: {metrics['rmse']:.2f}")
    print(f"   ✅ MAE: {metrics['mae']:.2f}")
    print(f"   ✅ R² Score: {metrics['r2_score']:.4f}")
    print(f"   ✅ MAPE: {metrics['mape']:.2f}%")
    print(f"   ✅ 训练时间: {metrics['training_time']:.2f}秒")

    # 3. 预测
    print("\n3. 预测测试...")
    X_test = X.iloc[:10]
    y_test = y.iloc[:10]

    predictions = predictor.predict(X_test)
    print(f"   前5个预测值: {predictions[:5]}")
    print(f"   前5个真实值: {y_test.values[:5]}")

    # 4. 特征重要性
    print("\n4. 特征重要性...")
    importance = predictor.get_feature_importance(top_k=5)
    print(importance)

    # 5. 模型保存/加载
    print("\n5. 模型持久化测试...")
    model_path = "models/test_predictor.pkl"
    predictor.save_model(model_path)
    print(f"   ✅ 模型已保存: {model_path}")

    # 加载模型
    predictor2 = PricePredictorStrategy()
    predictor2.load_model(model_path)
    predictions2 = predictor2.predict(X_test)

    print(f"   ✅ 模型已加载")
    print(f"   预测一致性: {np.allclose(predictions, predictions2)}")

    # 6. 超参数调优（可选，耗时较长）
    print("\n6. 超参数调优测试（跳过，可手动启用）...")
    # 取消注释以下代码来运行调优
    # param_grid = {
    #     'num_leaves': [20, 25],
    #     'n_estimators': [60, 70]
    # }
    # tuning_results = predictor.hyperparameter_tuning(X, y, param_grid, cv=3)
    # print(f"   最佳参数: {tuning_results['best_params']}")
    # print(f"   最佳得分: {tuning_results['best_score']:.2f}")

    print("\n✅ 价格预测模块测试完成！")
