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
from app.api.strategy_management._strategy_management_task_tail import run_backtest_task, train_model_task
from app.schemas.backtest_schemas import BacktestRequest
from app.api.strategy_management.monitoring_adapter import MonitoringAdapter, MonitoringFallback
from src.core import DataClassification
from src.monitoring.monitoring_database import MonitoringDatabase

# 使用 MyStocksUnifiedManager 作为统一入口点
from unified_manager import MyStocksUnifiedManager

router = APIRouter(prefix="/api/v1/strategy", tags=["策略管理-Week1"])

# 延迟初始化监控数据库（避免导入时需要完整环境变量）
monitoring_db = None

def get_monitoring_db():
    """获取监控数据库实例（延迟初始化）"""
    global monitoring_db
    if monitoring_db is None:
        try:
            real_monitoring_db = MonitoringDatabase()

            monitoring_db = MonitoringAdapter(real_monitoring_db)

        except Exception:
            logger.warning("MonitoringDatabase initialization failed, using fallback: %(e)s")

            monitoring_db = MonitoringFallback()
    return monitoring_db


@router.get("/strategies")
async def list_strategies(status: Optional[str] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """
    获取策略列表

    Args:
        status: 过滤状态 ('draft', 'active', 'archived')
        page: 页码
        page_size: 每页数量

    Returns:
        {
            "items": [...],
            "total": 100,
            "page": 1,
            "page_size": 20
        }

    支持Mock数据模式切换
    """
    operation_start = datetime.now()
    use_mock = os.getenv("USE_MOCK_DATA", "false").lower() == "true"

    try:
        if use_mock:
            try:
                mock_manager = get_mock_data_manager()
                strategies_data = mock_manager.get_data("strategy", action="list")
                strategies = strategies_data.get("strategies", [])

                if status:
                    strategies = [s for s in strategies if s.get("status") == status]

                total = len(strategies)
                start = (page - 1) * page_size
                end = start + page_size
                items = strategies[start:end]

                return {"items": items, "total": total, "page": page, "page_size": page_size}
            except Exception as mock_error:
                # 避免递归重入：Mock 失败后直接降级到真实数据库路径
                logger.warning("Mock数据获取失败，降级到真实数据库: %(e)s", e=str(mock_error))

        # 使用真实数据库 - 通过UnifiedManager访问（符合项目架构）
        manager = MyStocksUnifiedManager()

        filters = {}
        if status:
            # is_active字段映射：active/active策略，inactive/inactive策略
            filters["is_active"] = status == "active"

        try:
            # 使用 UnifiedManager 加载数据（表已在table_config.yaml中注册）
            strategies_df = manager.load_data_by_classification(
                classification=DataClassification.MODEL_OUTPUTS,
                table_name="strategy_definition",
                filters=filters,
            )

            total = len(strategies_df) if strategies_df is not None else 0
            start = (page - 1) * page_size
            end = start + page_size

            if strategies_df is not None and len(strategies_df) > 0:
                paginated_df = strategies_df.iloc[start:end]
                items = paginated_df.to_dict("records")
            else:
                items = []

        except Exception as db_error:
            # 数据库查询失败，记录错误并返回空结果
            logger.error("数据库查询失败: %(e)s", e=str(db_error))
            items = []
            total = 0

        # 记录操作到监控数据库
        operation_time = (datetime.now() - operation_start).total_seconds() * 1000
        get_monitoring_db().log_operation(
            operation_type="SELECT",
            table_name="strategies",
            operation_name="list_strategies",
            rows_affected=len(items),
            operation_time_ms=operation_time,
            success=True,
            details=f"status={status}, page={page}, page_size={page_size}",
        )

        return {"items": items, "total": total, "page": page, "page_size": page_size}

    except Exception as e:
        operation_time = (datetime.now() - operation_start).total_seconds() * 1000
        get_monitoring_db().log_operation(
            operation_type="SELECT",
            table_name="strategies",
            operation_name="list_strategies",
            rows_affected=0,
            operation_time_ms=operation_time,
            success=False,
            details=str(e),
        )
        raise HTTPException(status_code=500, detail=f"获取策略列表失败: {str(e)}")


@router.post("/strategies")
async def create_strategy(strategy_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    创建新策略

    Args:
        strategy_data: 策略创建数据

    Returns:
        创建的策略对象

    支持Mock数据模式切换
    """
    operation_start = datetime.now()

    try:
        # 检查是否使用Mock数据
        use_mock = os.getenv("USE_MOCK_DATA", "false").lower() == "true"

        if use_mock:
            # 使用Mock数据 - 直接返回模拟结果
            mock_strategy = {
                "id": f"mock_strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "name": strategy_data.get("name", "Mock策略"),
                "description": strategy_data.get("description", "Mock策略描述"),
                "strategy_type": strategy_data.get("strategy_type", "technical"),
                "parameters": strategy_data.get("parameters", {}),
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "status": strategy_data.get("status", "draft"),
                "is_mock": True,
            }
            return mock_strategy
        else:
            # 使用真实数据库
            manager = MyStocksUnifiedManager()

            # 添加时间戳
            strategy_data["created_at"] = datetime.now()
            strategy_data["updated_at"] = datetime.now()
            strategy_data["status"] = strategy_data.get("status", "draft")

            # 使用 UnifiedManager 保存数据
            import pandas as pd

            strategy_df = pd.DataFrame([strategy_data])

            result = manager.save_data_by_classification(
                data=strategy_df,
                classification=DataClassification.MODEL_OUTPUT,
                table_name="strategies",
            )

            # 记录操作到监控数据库
            operation_time = (datetime.now() - operation_start).total_seconds() * 1000
            get_monitoring_db().log_operation(
                operation_type="INSERT",
                table_name="strategies",
                operation_name="create_strategy",
                rows_affected=1 if result else 0,
                operation_time_ms=operation_time,
                success=result,
                details=f"strategy_type={strategy_data.get('strategy_type')}",
            )

        if result:
            return {"message": "策略创建成功", "data": strategy_data}
        else:
            raise HTTPException(status_code=500, detail="策略创建失败")

    except Exception as e:
        # 记录失败操作
        operation_time = (datetime.now() - operation_start).total_seconds() * 1000
        get_monitoring_db().log_operation(
            operation_type="INSERT",
            table_name="strategies",
            operation_name="create_strategy",
            rows_affected=0,
            operation_time_ms=operation_time,
            success=False,
            error_message=str(e),
        )
        raise HTTPException(status_code=500, detail=f"创建策略失败: {str(e)}")


@router.get("/strategies/{strategy_id}")
async def get_strategy(strategy_id: int) -> Dict[str, Any]:
    """获取策略详情"""
    try:
        manager = MyStocksUnifiedManager()

        strategies = manager.load_data_by_classification(
            classification=DataClassification.MODEL_OUTPUT,
            table_name="strategies",
            filters={"id": strategy_id},
        )

        if strategies is None or len(strategies) == 0:
            raise HTTPException(status_code=404, detail="策略不存在")

        return strategies.iloc[0].to_dict()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取策略失败: {str(e)}")


@router.put("/strategies/{strategy_id}")
async def update_strategy(strategy_id: int, strategy_update: Dict[str, Any]) -> Dict[str, Any]:
    """更新策略"""
    try:
        manager = MyStocksUnifiedManager()

        # 先获取现有策略
        strategies = manager.load_data_by_classification(
            classification=DataClassification.MODEL_OUTPUT,
            table_name="strategies",
            filters={"id": strategy_id},
        )

        if strategies is None or len(strategies) == 0:
            raise HTTPException(status_code=404, detail="策略不存在")

        # 更新数据
        strategy_update["updated_at"] = datetime.now()
        strategy_update["id"] = strategy_id

        import pandas as pd

        updated_df = pd.DataFrame([strategy_update])

        result = manager.save_data_by_classification(
            data=updated_df,
            classification=DataClassification.MODEL_OUTPUT,
            table_name="strategies",
            upsert=True,
        )

        if result:
            return {"message": "策略更新成功"}
        else:
            raise HTTPException(status_code=500, detail="策略更新失败")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新策略失败: {str(e)}")


@router.delete("/strategies/{strategy_id}")
async def delete_strategy(strategy_id: int) -> Dict[str, str]:
    """删除策略"""
    try:
        manager = MyStocksUnifiedManager()

        # 注意：实际实现中应该使用软删除（更新status为archived）
        # 而不是真正删除数据
        import pandas as pd

        delete_data = pd.DataFrame([{"id": strategy_id, "status": "archived", "updated_at": datetime.now()}])

        result = manager.save_data_by_classification(
            data=delete_data,
            classification=DataClassification.MODEL_OUTPUT,
            table_name="strategies",
            upsert=True,
        )

        if result:
            return {"message": "策略已归档"}
        else:
            raise HTTPException(status_code=500, detail="策略删除失败")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除策略失败: {str(e)}")


@router.post("/models/train")
async def train_model(config: Dict[str, Any], background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    启动模型训练任务

    Args:
        config: 训练配置

    Returns:
        {"task_id": "task_xxx", "model_id": 123}
    """
    try:
        manager = MyStocksUnifiedManager()

        # 创建模型记录
        import pandas as pd

        model_data = {
            "name": config.get("name"),
            "model_type": config.get("model_type"),
            "hyperparameters": config.get("hyperparameters"),
            "training_config": config.get("training_config"),
            "status": "training",
            "training_started_at": datetime.now(),
            "created_at": datetime.now(),
        }

        model_df = pd.DataFrame([model_data])
        result = manager.save_data_by_classification(
            data=model_df,
            classification=DataClassification.MODEL_OUTPUT,
            table_name="models",
        )

        if not result:
            raise HTTPException(status_code=500, detail="创建模型记录失败")

        # 获取创建的模型ID（简化版本，实际应该从返回值中获取）
        models = manager.load_data_by_classification(
            classification=DataClassification.MODEL_OUTPUT,
            table_name="models",
            filters={"name": config.get("name")},
        )
        model_id = models.iloc[-1]["id"] if models is not None and len(models) > 0 else 1

        # 后台任务训练模型
        task_id = f"train_{model_id}_{int(datetime.now().timestamp())}"
        background_tasks.add_task(train_model_task, model_id=model_id, config=config)

        return {"task_id": task_id, "model_id": model_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动模型训练失败: {str(e)}")


@router.get("/models/training/{task_id}/status")
async def get_training_status(task_id: str) -> Dict[str, Any]:
    """
    查询训练状态

    Returns:
        {
            "status": "training" | "completed" | "failed",
            "progress": 75,
            "metrics": {...}
        }
    """
    try:
        # 从task_id解析model_id
        model_id = int(task_id.split("_")[1])

        manager = MyStocksUnifiedManager()
        models = manager.load_data_by_classification(
            classification=DataClassification.MODEL_OUTPUT,
            table_name="models",
            filters={"id": model_id},
        )

        if models is None or len(models) == 0:
            raise HTTPException(status_code=404, detail="模型不存在")

        model = models.iloc[0].to_dict()

        # 计算进度
        status = model.get("status")
        progress = 100 if status == "completed" else 0
        if status == "training":
            elapsed = (datetime.now() - model["training_started_at"]).seconds
            progress = min(95, int(elapsed / 60 * 20))  # 假设5分钟完成

        return {
            "status": status,
            "progress": progress,
            "metrics": model.get("performance_metrics") or {},
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取训练状态失败: {str(e)}")


@router.get("/models")
async def list_models(model_type: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """获取模型列表"""
    try:
        manager = MyStocksUnifiedManager()

        filters = {}
        if model_type:
            filters["model_type"] = model_type
        if status:
            filters["status"] = status

        models = manager.load_data_by_classification(
            classification=DataClassification.MODEL_OUTPUT,
            table_name="models",
            filters=filters,
        )

        return models.to_dict("records") if models is not None else []

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模型列表失败: {str(e)}")


@router.post("/backtest/run")
async def run_backtest(request: BacktestRequest, background_tasks: BackgroundTasks) -> Dict[str, int]:
    """
    执行回测

    Args:
        request: 回测请求参数

    Returns:
        {"backtest_id": 123}
    """
    try:
        manager = MyStocksUnifiedManager()

        # 创建回测记录
        import pandas as pd

        # Extract config from request
        config = request.parameters.copy()
        config["symbols"] = request.symbols
        config["start_date"] = (
            request.start_date.isoformat() if hasattr(request.start_date, "isoformat") else str(request.start_date)
        )
        config["end_date"] = (
            request.end_date.isoformat() if hasattr(request.end_date, "isoformat") else str(request.end_date)
        )
        config["initial_cash"] = request.initial_capital
        config["strategy_type"] = request.strategy_name  # Or from parameters if needed

        backtest_data = {
            "name": f"{request.strategy_name}_Backtest",  # Generate a name
            "strategy_id": config.get("strategy_id"),  # If existing strategy
            "start_date": config["start_date"],
            "end_date": config["end_date"],
            "initial_cash": request.initial_capital,
            "commission_rate": config.get("commission_rate", 0.0003),
            "stamp_tax_rate": config.get("stamp_tax_rate", 0.001),
            "slippage_rate": config.get("slippage_rate", 0.001),
            "status": "pending",
            "created_at": datetime.now(),
        }

        backtest_df = pd.DataFrame([backtest_data])
        result = manager.save_data_by_classification(
            data=backtest_df,
            classification=DataClassification.MODEL_OUTPUT,
            table_name="backtests",
        )

        if not result:
            raise HTTPException(status_code=500, detail="创建回测记录失败")

        # 获取创建的回测ID
        backtests = manager.load_data_by_classification(
            classification=DataClassification.MODEL_OUTPUT,
            table_name="backtests",
            filters={"name": backtest_data["name"]},
        )
        backtest_id = backtests.iloc[-1]["id"] if backtests is not None and len(backtests) > 0 else 1

        # 后台任务执行回测
        background_tasks.add_task(run_backtest_task, backtest_id=backtest_id, config=config)

        return {"backtest_id": backtest_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动回测失败: {str(e)}")


@router.get("/backtest/results")
async def list_backtest_results(
    strategy_id: Optional[int] = None, page: int = 1, page_size: int = 20
) -> Dict[str, Any]:
    """获取回测结果列表"""
    try:
        manager = MyStocksUnifiedManager()

        filters = {}
        if strategy_id:
            filters["strategy_id"] = strategy_id

        backtests = manager.load_data_by_classification(
            classification=DataClassification.MODEL_OUTPUT,
            table_name="backtests",
            filters=filters,
        )

        total = len(backtests) if backtests is not None else 0
        start = (page - 1) * page_size
        end = start + page_size
        items = backtests.iloc[start:end].to_dict("records") if backtests is not None else []

        return {"items": items, "total": total, "page": page, "page_size": page_size}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取回测结果失败: {str(e)}")
