"""Backtest chart-data route (migrated from deleted get_backtest_result.py)."""
from typing import Any, Dict, List

from fastapi import APIRouter, Path
from src.core import DataClassification
from unified_manager import MyStocksUnifiedManager
from app.core.responses import UnifiedResponse, create_success_response
from app.core.exceptions import BusinessException

router = APIRouter(tags=["策略管理-Week1"])


@router.get(
    "/backtest/results/{backtest_id}/chart-data",
    summary="获取回测图表数据",
    description="返回指定回测的可视化图表数据（资金曲线、回撤曲线、收益分布），供前端 ECharts 等图表库直接使用。",
    response_model=UnifiedResponse[Dict[str, Any]],
)
async def get_backtest_chart_data(backtest_id: int = Path(..., description="回测ID", ge=1)) -> Dict[str, List]:
    """获取回测图表数据"""
    try:
        manager = MyStocksUnifiedManager()
        backtests = manager.load_data_by_classification(
            classification=DataClassification.MODEL_OUTPUT,
            table_name="backtests",
            filters={"id": backtest_id},
        )
        if backtests is None or len(backtests) == 0:
            raise BusinessException(detail="回测不存在", status_code=404)
        backtest = backtests.iloc[0].to_dict()
        results = backtest.get("results") or {}
        return create_success_response(data={
            "equity_curve": results.get("equity_curve", []),
            "drawdown_curve": results.get("drawdown_curve", []),
            "returns_distribution": results.get("returns_distribution", []),
        }, message="获取图表数据成功")
    except BusinessException:
        raise
    except Exception as e:
        raise BusinessException(detail=f"获取图表数据失败: {str(e)}", status_code=500)
