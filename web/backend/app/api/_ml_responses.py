"""ML API response examples and OpenAPI response specs."""

ML_MARKET_PATH_DESCRIPTION = "市场代码，支持 sh（上交所）或 sz（深交所）。"

ML_TDX_DATA_REQUEST_EXAMPLE = {"stock_code": "000001", "market": "sh"}

ML_FEATURE_GENERATION_REQUEST_EXAMPLE = {
    "stock_code": "000001",
    "market": "sh",
    "step": 10,
    "include_indicators": True,
}

ML_MODEL_TRAIN_REQUEST_EXAMPLE = {
    "stock_code": "000001",
    "market": "sh",
    "step": 10,
    "test_size": 0.2,
    "model_name": "a_share_lgbm_v1",
    "model_params": {"n_estimators": 100, "learning_rate": 0.1},
}

ML_MODEL_PREDICT_REQUEST_EXAMPLE = {
    "model_name": "a_share_lgbm_v1",
    "stock_code": "000001",
    "market": "sh",
    "days": 1,
}

ML_HYPERPARAMETER_SEARCH_REQUEST_EXAMPLE = {
    "stock_code": "000001",
    "market": "sh",
    "step": 10,
    "cv": 5,
    "param_grid": {
        "num_leaves": [15, 31],
        "n_estimators": [50, 100],
        "learning_rate": [0.05, 0.1],
    },
}

ML_MODEL_EVALUATION_REQUEST_EXAMPLE = {
    "model_name": "a_share_lgbm_v1",
    "stock_code": "000001",
    "market": "sh",
}


def _success_response_spec(status_code: int, description: str, example: object) -> dict[int, dict]:
    return {
        status_code: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        }
    }


def _error_response_spec(status_code: int, description: str, example: dict) -> dict[int, dict]:
    return {
        status_code: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        }
    }


ML_MODEL_LIST_RESPONSES = {
    **_success_response_spec(
        200,
        "已保存模型列表",
        {
            "total": 2,
            "models": [
                {
                    "name": "a_share_lgbm_v1",
                    "path": "./models/a_share_lgbm_v1.pkl",
                    "trained_at": "2026-04-05T09:30:00",
                    "test_rmse": 1.82,
                    "test_r2": 0.78,
                    "train_samples": 2400,
                    "test_samples": 600,
                    "feature_dim": 32,
                },
                {
                    "name": "hs300_xgboost_v2",
                    "path": "./models/hs300_xgboost_v2.pkl",
                    "trained_at": "2026-04-04T15:00:00",
                    "test_rmse": 2.11,
                    "test_r2": 0.73,
                    "train_samples": 1800,
                    "test_samples": 450,
                    "feature_dim": 28,
                },
            ],
        },
    ),
    **_error_response_spec(
        500,
        "模型列表查询失败",
        {"detail": "读取模型目录失败: [Errno 2] No such file or directory: './models'"},
    ),
}

ML_MODEL_DETAIL_RESPONSES = {
    **_success_response_spec(
        200,
        "模型详情",
        {
            "name": "a_share_lgbm_v1",
            "metadata": {
                "model_type": "lightgbm",
                "trained_at": "2026-04-05T09:30:00",
                "stock_scope": "A-share",
                "market": "sh",
                "metrics": {
                    "rmse": 1.82,
                    "r2": 0.78,
                    "step": 10,
                },
            },
            "training_history": [
                {"epoch": 1, "train_loss": 0.043, "val_loss": 0.051},
                {"epoch": 2, "train_loss": 0.039, "val_loss": 0.047},
            ],
            "feature_importance": [
                {"feature": "close", "importance": 0.31},
                {"feature": "volume", "importance": 0.18},
            ],
        },
    ),
    **_error_response_spec(
        404,
        "指定模型不存在",
        {"detail": "模型不存在: a_share_lgbm_v9"},
    ),
    **_error_response_spec(
        503,
        "模型服务当前不可用",
        {"detail": "ML prediction service unavailable: missing optional dependency"},
    ),
    **_error_response_spec(
        500,
        "模型详情查询失败",
        {"detail": "加载模型详情失败: metadata.json is corrupted"},
    ),
}

ML_TDX_STOCKS_RESPONSES = {
    **_success_response_spec(
        200,
        "指定市场可用股票代码列表",
        ["000001", "000002", "600519", "601318"],
    ),
    **_error_response_spec(
        500,
        "股票代码列表查询失败",
        {"detail": "读取通达信股票目录失败: market index unavailable"},
    ),
}

ML_TDX_DATA_RESPONSES = {
    **_success_response_spec(
        200,
        "通达信原始行情数据。",
        {
            "code": "000001",
            "market": "sh",
            "data": [
                {
                    "trade_date": "2026-04-07",
                    "open": 12.31,
                    "high": 12.58,
                    "low": 12.18,
                    "close": 12.45,
                    "volume": 18502340,
                    "amount": 229341122.0,
                }
            ],
            "total_records": 1,
        },
    ),
    **_error_response_spec(
        404,
        "指定股票没有可用行情数据。",
        {"detail": "未找到股票数据: sh000001"},
    ),
    **_error_response_spec(
        500,
        "通达信数据读取失败。",
        {"detail": "读取通达信数据失败: file corrupted"},
    ),
}

ML_FEATURE_GENERATION_RESPONSES = {
    **_success_response_spec(
        200,
        "特征生成结果。",
        {
            "success": True,
            "message": "特征生成成功",
            "total_samples": 2380,
            "feature_dim": 32,
            "step": 10,
            "feature_columns": ["open", "high", "low", "close", "volume", "ma5", "rsi14"],
            "metadata": {
                "total_samples": 2380,
                "feature_dim": 32,
                "step": 10,
                "feature_columns": ["open", "high", "low", "close", "volume", "ma5", "rsi14"],
            },
        },
    ),
    **_error_response_spec(
        404,
        "指定股票没有可用于生成特征的历史数据。",
        {"detail": "未找到股票数据: sh000001"},
    ),
    **_error_response_spec(
        500,
        "特征工程处理失败。",
        {"detail": "特征生成失败: insufficient rows for rolling window"},
    ),
}

ML_MODEL_TRAIN_RESPONSES = {
    **_success_response_spec(
        200,
        "模型训练结果。",
        {
            "success": True,
            "message": "模型 a_share_lgbm_v1 训练成功",
            "model_name": "a_share_lgbm_v1",
            "metrics": {
                "train_rmse": 1.24,
                "test_rmse": 1.82,
                "train_r2": 0.86,
                "test_r2": 0.78,
                "step": 10,
            },
        },
    ),
    **_error_response_spec(
        404,
        "指定股票没有可用于训练的数据。",
        {"detail": "未找到股票数据: sh000001"},
    ),
    **_error_response_spec(
        503,
        "机器学习预测服务当前不可用。",
        {"detail": "ML prediction service unavailable: missing optional dependency"},
    ),
    **_error_response_spec(
        500,
        "模型训练或保存失败。",
        {"detail": "LightGBM training failed: invalid feature matrix"},
    ),
}

ML_MODEL_PREDICT_RESPONSES = {
    **_success_response_spec(
        200,
        "模型预测结果。",
        {
            "success": True,
            "message": "预测成功",
            "model_name": "a_share_lgbm_v1",
            "stock_code": "000001",
            "predictions": [
                {"date": "T+1", "predicted_price": 12.88, "confidence": None},
            ],
        },
    ),
    **_error_response_spec(
        400,
        "当前样本量不足，无法构造预测窗口。",
        {"detail": "数据不足，无法进行预测"},
    ),
    **_error_response_spec(
        404,
        "模型或股票数据不存在。",
        {"detail": "模型不存在: a_share_lgbm_v1"},
    ),
    **_error_response_spec(
        503,
        "机器学习预测服务当前不可用。",
        {"detail": "ML prediction service unavailable: missing optional dependency"},
    ),
    **_error_response_spec(
        500,
        "预测执行失败。",
        {"detail": "prediction failed: model metadata missing"},
    ),
}

ML_HYPERPARAMETER_SEARCH_RESPONSES = {
    **_success_response_spec(
        200,
        "超参数搜索结果。",
        {
            "success": True,
            "message": "超参数搜索完成",
            "best_params": {"num_leaves": 31, "n_estimators": 100, "learning_rate": 0.1},
            "best_rmse": 1.71,
            "best_mse": 2.92,
            "cv_results": {
                "mean_test_score": [-1.94, -1.71],
                "params": [
                    {"num_leaves": 15, "n_estimators": 50, "learning_rate": 0.05},
                    {"num_leaves": 31, "n_estimators": 100, "learning_rate": 0.1},
                ],
            },
        },
    ),
    **_error_response_spec(
        404,
        "指定股票没有可用于搜索的数据。",
        {"detail": "未找到股票数据: sh000001"},
    ),
    **_error_response_spec(
        503,
        "机器学习预测服务当前不可用。",
        {"detail": "ML prediction service unavailable: missing optional dependency"},
    ),
    **_error_response_spec(
        500,
        "超参数搜索执行失败。",
        {"detail": "grid search failed: cv split error"},
    ),
}

ML_MODEL_EVALUATION_RESPONSES = {
    **_success_response_spec(
        200,
        "模型评估结果。",
        {
            "success": True,
            "message": "评估完成",
            "model_name": "a_share_lgbm_v1",
            "metrics": {
                "rmse": 1.82,
                "mse": 3.31,
                "mae": 1.24,
                "r2": 0.78,
            },
        },
    ),
    **_error_response_spec(
        404,
        "模型或股票数据不存在。",
        {"detail": "模型不存在: a_share_lgbm_v1"},
    ),
    **_error_response_spec(
        503,
        "机器学习预测服务当前不可用。",
        {"detail": "ML prediction service unavailable: missing optional dependency"},
    ),
    **_error_response_spec(
        500,
        "模型评估执行失败。",
        {"detail": "model evaluation failed: feature mismatch"},
    ),
}
