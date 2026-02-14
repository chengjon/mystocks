"""
策略管理 API - Week 1 Architecture Compliant

提供策略CRUD、模型训练、回测执行等接口
使用 MyStocksUnifiedManager 统一数据访问 + MonitoringDatabase 监控集成

Author: JohnC & Claude
Version: 2.1.0 (Full Monitoring Integration)
Date: 2025-10-24
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog
from fastapi import APIRouter, BackgroundTasks, HTTPException

logger = structlog.get_logger(__name__)

# 添加项目根目录到路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.mock.unified_mock_data import get_mock_data_manager
from src.core import DataClassification
from src.monitoring.monitoring_database import MonitoringDatabase

# 使用 MyStocksUnifiedManager 作为统一入口点
from unified_manager import MyStocksUnifiedManager

# 注意: backtest, model 模块需要确保存在
try:
    from app.backtest.backtest_engine import BacktestEngine
    from model import LightGBMModel, RandomForestModel
except ImportError:
    BacktestEngine = None
    RandomForestModel = None
    LightGBMModel = None

# GPU加速回测引擎（新功能 - 2025-12-26）
try:
    from src.gpu.acceleration.backtest_engine_gpu import BacktestEngineGPU
    from src.utils.gpu_utils import GPUResourceManager

    GPU_BACKTEST_AVAILABLE = True
except ImportError:
    GPU_BACKTEST_AVAILABLE = False
    BacktestEngineGPU = None
    GPUResourceManager = None

router = APIRouter(prefix="/api/v1/strategy", tags=["策略管理-Week1"])

# 延迟初始化监控数据库（避免导入时需要完整环境变量）
monitoring_db = None

@router.get("/backtest/results/{backtest_id}")
async def get_backtest_result(backtest_id: int) -> Dict[str, Any]:
    """获取回测详细结果"""
    try:
        manager = MyStocksUnifiedManager()

        backtests = manager.load_data_by_classification(
            classification=DataClassification.MODEL_OUTPUT,
            table_name="backtests",
            filters={"id": backtest_id},
        )

        if backtests is None or len(backtests) == 0:
            raise HTTPException(status_code=404, detail="回测不存在")

        return backtests.iloc[0].to_dict()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取回测结果失败: {str(e)}")


@router.get("/backtest/results/{backtest_id}/chart-data")
async def get_backtest_chart_data(backtest_id: int) -> Dict[str, List]:
    """
    获取回测图表数据

    获取指定回测任务的可视化图表数据，包括资金曲线、回撤曲线和收益分布等。
    该端点专门为前端图表组件（如ECharts）提供格式化的时序数据。

    **功能说明**:
    - 提取回测结果中的时序数据
    - 生成资金曲线（Equity Curve）数据点
    - 计算回撤曲线（Drawdown Curve）数据
    - 统计收益分布（Returns Distribution）直方图
    - 返回前端图表库可直接使用的数据格式
    - 支持多种图表类型的数据输出

    **使用场景**:
    - 回测结果页面的可视化展示
    - 生成资金曲线图（折线图）
    - 绘制回撤曲线图（面积图）
    - 展示收益分布直方图
    - 导出图表数据用于报告
    - 对比多个回测结果

    **路径参数**:
    - backtest_id: 回测任务ID（整数）
      - 必需参数
      - 通过 /backtest/run 接口返回的ID
      - 对应数据库中的回测记录

    **返回值**:
    - equity_curve: 资金曲线数据（数组）
      - 每个元素: [timestamp, equity_value]
      - 时间戳: ISO 8601格式或Unix时间戳
      - 资金价值: 账户总资产（浮点数）
    - drawdown_curve: 回撤曲线数据（数组）
      - 每个元素: [timestamp, drawdown_percentage]
      - 回撤百分比: 负值，如-0.15表示15%回撤
    - returns_distribution: 收益分布数据（数组）
      - 每个元素: [return_range, frequency]
      - 收益区间: 如"-2%到-1%"
      - 频率: 该区间的交易次数

    **示例**:
    ```bash
    # 获取回测图表数据
    curl -X GET "http://localhost:8000/api/v1/strategy/backtest/results/123/chart-data"
    ```

    **响应示例**:
    ```json
    {
      "equity_curve": [
        ["2024-01-01T00:00:00", 1000000],
        ["2024-01-02T00:00:00", 1005230],
        ["2024-01-03T00:00:00", 1012450],
        ["2024-01-04T00:00:00", 1008900]
      ],
      "drawdown_curve": [
        ["2024-01-01T00:00:00", 0],
        ["2024-01-02T00:00:00", 0],
        ["2024-01-03T00:00:00", 0],
        ["2024-01-04T00:00:00", -0.0035]
      ],
      "returns_distribution": [
        ["-3% to -2%", 5],
        ["-2% to -1%", 12],
        ["-1% to 0%", 45],
        ["0% to 1%", 78],
        ["1% to 2%", 42],
        ["2% to 3%", 8]
      ]
    }
    ```

    **回测不存在响应**:
    ```json
    {
      "detail": "回测不存在"
    }
    ```

    **注意事项**:
    - 该端点仅返回图表数据，不包含完整回测结果
    - 数据格式已针对前端图表库优化（ECharts、Chart.js等）
    - equity_curve数据点数量取决于回测周期和频率
    - 如果回测尚未完成，部分字段可能为空数组
    - 建议先调用 /backtest/results/{id} 检查回测状态
    - 大数据量时可能需要前端分页或采样展示
    """
    try:
        manager = MyStocksUnifiedManager()

        backtests = manager.load_data_by_classification(
            classification=DataClassification.MODEL_OUTPUT,
            table_name="backtests",
            filters={"id": backtest_id},
        )

        if backtests is None or len(backtests) == 0:
            raise HTTPException(status_code=404, detail="回测不存在")

        backtest = backtests.iloc[0].to_dict()
        results = backtest.get("results") or {}

        return {
            "equity_curve": results.get("equity_curve", []),
            "drawdown_curve": results.get("drawdown_curve", []),
            "returns_distribution": results.get("returns_distribution", []),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取图表数据失败: {str(e)}")


