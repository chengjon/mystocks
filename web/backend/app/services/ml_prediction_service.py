"""
机器学习预测服务
使用 LightGBM 进行股票价格预测
"""
import os
import pickle
import json
from pathlib import Path
from typing import Dict, Tuple, Optional, List
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

try:
    from lightgbm import LGBMRegressor
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    LGBMRegressor = None


class MLPredictionService:
    """
    机器学习预测服务

    功能：
    1. 模型训练
    2. 模型预测
    3. 模型评估
    4. 模型保存和加载
    5. 超参数搜索
    """

    def __init__(self, model_dir: str = "./models"):
        """
        初始化服务

        Args:
            model_dir: 模型保存目录
        """
        if not LIGHTGBM_AVAILABLE:
            raise ImportError("LightGBM 未安装，请运行: pip install lightgbm")

        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)

        self.model = None
        self.model_metadata = {}
        self.training_history = []

    def create_model(
        self,
        num_leaves: int = 25,
        learning_rate: float = 0.2,
        n_estimators: int = 70,
        max_depth: int = 15,
        **kwargs
    ) -> LGBMRegressor:
        """
        创建 LightGBM 模型

        Args:
            num_leaves: 叶子节点数
            learning_rate: 学习率
            n_estimators: 树的数量
            max_depth: 最大深度
            **kwargs: 其他参数

        Returns:
            LGBMRegressor: 模型实例
        """
        default_params = {
            'boosting_type': 'gbdt',
            'objective': 'regression',
            'metric': 'rmse',
            'bagging_fraction': 0.8,
            'feature_fraction': 0.8,
            'reg_lambda': 0.9,
            'verbose': -1
        }

        # 合并参数
        params = {
            'num_leaves': num_leaves,
            'learning_rate': learning_rate,
            'n_estimators': n_estimators,
            'max_depth': max_depth,
            **default_params,
            **kwargs
        }

        model = LGBMRegressor(**params)
        return model

    def train(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        test_size: float = 0.2,
        random_state: int = 123,
        model_params: dict = None
    ) -> Dict:
        """
        训练模型

        Args:
            X: 特征矩阵
            y: 目标变量
            test_size: 测试集比例
            random_state: 随机种子
            model_params: 模型参数

        Returns:
            Dict: 训练结果（包含评估指标）
        """
        # 分割数据
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

        # 创建模型
        if model_params:
            self.model = self.create_model(**model_params)
        else:
            self.model = self.create_model()

        # 训练模型
        self.model.fit(X_train, y_train)

        # 预测
        y_pred_train = self.model.predict(X_train)
        y_pred_test = self.model.predict(X_test)

        # 评估
        metrics = {
            'train_rmse': float(np.sqrt(mean_squared_error(y_train, y_pred_train))),
            'test_rmse': float(np.sqrt(mean_squared_error(y_test, y_pred_test))),
            'train_mae': float(mean_absolute_error(y_train, y_pred_train)),
            'test_mae': float(mean_absolute_error(y_test, y_pred_test)),
            'train_r2': float(r2_score(y_train, y_pred_train)),
            'test_r2': float(r2_score(y_test, y_pred_test)),
            'train_samples': int(len(X_train)),
            'test_samples': int(len(X_test)),
            'feature_dim': int(X.shape[1]),
            'trained_at': datetime.now().isoformat()
        }

        # 保存元数据
        self.model_metadata = {
            'model_params': self.model.get_params(),
            'metrics': metrics,
            'feature_names': list(X.columns)
        }

        # 记录训练历史
        self.training_history.append(metrics)

        return metrics

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        使用模型进行预测

        Args:
            X: 特征矩阵

        Returns:
            np.ndarray: 预测结果
        """
        if self.model is None:
            raise ValueError("模型尚未训练，请先调用 train() 方法")

        predictions = self.model.predict(X)
        return predictions

    def save_model(self, model_name: str) -> str:
        """
        保存模型

        Args:
            model_name: 模型名称

        Returns:
            str: 模型文件路径
        """
        if self.model is None:
            raise ValueError("模型尚未训练，无法保存")

        # 创建模型目录
        model_path = self.model_dir / model_name
        model_path.mkdir(parents=True, exist_ok=True)

        # 保存模型
        model_file = model_path / "model.pkl"
        with open(model_file, 'wb') as f:
            pickle.dump(self.model, f)

        # 保存元数据
        metadata_file = model_path / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.model_metadata, f, indent=2, ensure_ascii=False)

        # 保存训练历史
        history_file = model_path / "history.json"
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(self.training_history, f, indent=2)

        return str(model_file)

    def load_model(self, model_name: str) -> bool:
        """
        加载模型

        Args:
            model_name: 模型名称

        Returns:
            bool: 是否加载成功
        """
        model_path = self.model_dir / model_name
        model_file = model_path / "model.pkl"

        if not model_file.exists():
            return False

        # 加载模型
        with open(model_file, 'rb') as f:
            self.model = pickle.load(f)

        # 加载元数据
        metadata_file = model_path / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                self.model_metadata = json.load(f)

        # 加载训练历史
        history_file = model_path / "history.json"
        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                self.training_history = json.load(f)

        return True

    def hyperparameter_search(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        param_grid: dict = None,
        cv: int = 5
    ) -> Dict:
        """
        超参数搜索

        Args:
            X: 特征矩阵
            y: 目标变量
            param_grid: 参数网格
            cv: 交叉验证折数

        Returns:
            Dict: 最佳参数和评分
        """
        if param_grid is None:
            param_grid = {
                'num_leaves': [5, 10, 15, 20, 25],
                'n_estimators': [10, 40, 70, 100, 130],
                'learning_rate': [0.01, 0.1, 0.2]
            }

        # 创建基础模型
        base_model = self.create_model()

        # 网格搜索
        grid_search = GridSearchCV(
            base_model,
            param_grid=param_grid,
            cv=cv,
            scoring='neg_mean_squared_error',
            n_jobs=-1,
            verbose=1
        )

        # 执行搜索
        grid_search.fit(X, y)

        # 最佳参数
        best_params = grid_search.best_params_
        best_score = -grid_search.best_score_  # 转换回 MSE

        result = {
            'best_params': best_params,
            'best_mse': float(best_score),
            'best_rmse': float(np.sqrt(best_score)),
            'cv_results': {
                'mean_test_scores': grid_search.cv_results_['mean_test_score'].tolist(),
                'std_test_scores': grid_search.cv_results_['std_test_score'].tolist()
            }
        }

        # 使用最佳参数更新模型
        self.model = grid_search.best_estimator_

        return result

    def get_feature_importance(self, top_k: int = 20) -> List[Dict]:
        """
        获取特征重要性

        Args:
            top_k: 返回前 K 个重要特征

        Returns:
            List[Dict]: 特征重要性列表
        """
        if self.model is None:
            raise ValueError("模型尚未训练")

        feature_names = self.model_metadata.get('feature_names', [])
        importances = self.model.feature_importances_

        # 创建特征重要性列表
        feature_importance = [
            {'feature': name, 'importance': float(imp)}
            for name, imp in zip(feature_names, importances)
        ]

        # 按重要性排序
        feature_importance.sort(key=lambda x: x['importance'], reverse=True)

        # 返回前 K 个
        return feature_importance[:top_k]

    def evaluate_model(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """
        评估模型

        Args:
            X: 特征矩阵
            y: 真实值

        Returns:
            Dict: 评估指标
        """
        if self.model is None:
            raise ValueError("模型尚未训练")

        # 预测
        y_pred = self.model.predict(X)

        # 计算指标
        metrics = {
            'rmse': float(np.sqrt(mean_squared_error(y, y_pred))),
            'mae': float(mean_absolute_error(y, y_pred)),
            'r2': float(r2_score(y, y_pred)),
            'samples': int(len(X))
        }

        return metrics

    def list_saved_models(self) -> List[Dict]:
        """
        列出已保存的模型

        Returns:
            List[Dict]: 模型列表
        """
        models = []

        for model_path in self.model_dir.iterdir():
            if model_path.is_dir():
                metadata_file = model_path / "metadata.json"

                if metadata_file.exists():
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)

                    models.append({
                        'name': model_path.name,
                        'path': str(model_path),
                        'trained_at': metadata.get('metrics', {}).get('trained_at', 'unknown'),
                        'test_rmse': metadata.get('metrics', {}).get('test_rmse', 0),
                        'test_r2': metadata.get('metrics', {}).get('test_r2', 0)
                    })

        # 按训练时间排序
        models.sort(key=lambda x: x['trained_at'], reverse=True)

        return models
