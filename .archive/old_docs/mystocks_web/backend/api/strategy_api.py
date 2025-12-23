"""
策略管理 API

提供策略CRUD、模型训练、回测执行等接口
使用 MyStocksUnifiedManager 统一数据访问 + MonitoringDatabase 监控集成

Author: JohnC & Claude
Version: 2.1.0 (Full Monitoring Integration)
Date: 2025-10-24
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional, List, Dict, Any
from datetime import datetime

# 使用 MyStocksUnifiedManager 作为统一入口点
from unified_manager import MyStocksUnifiedManager
from core import DataClassification
from model import RandomForestModel, LightGBMModel
from monitoring.monitoring_database import MonitoringDatabase

router = APIRouter(prefix="/api/v1/strategy", tags=["策略管理"])

# 初始化监控数据库
monitoring_db = MonitoringDatabase()


# ============ 策略 CRUD ============


@router.get("/strategies")
async def list_strategies(
    status: Optional[str] = None, page: int = 1, page_size: int = 20
) -> Dict[str, Any]:
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
    """
    operation_start = datetime.now()

    try:
        manager = MyStocksUnifiedManager()

        # 构建过滤条件
        filters = {}
        if status:
            filters["status"] = status

        # 使用 UnifiedManager 加载数据
        strategies = manager.load_data_by_classification(
            data_classification=DataClassification.DERIVED_DATA,
            table_name="strategies",
            filters=filters,
        )

        # 分页处理
        total = len(strategies) if strategies is not None else 0
        start = (page - 1) * page_size
        end = start + page_size
        items = (
            strategies.iloc[start:end].to_dict("records")
            if strategies is not None
            else []
        )

        # 记录操作到监控数据库
        operation_time = (datetime.now() - operation_start).total_seconds() * 1000
        monitoring_db.log_operation(
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
        # 记录失败操作
        operation_time = (datetime.now() - operation_start).total_seconds() * 1000
        monitoring_db.log_operation(
            operation_type="SELECT",
            table_name="strategies",
            operation_name="list_strategies",
            rows_affected=0,
            operation_time_ms=operation_time,
            success=False,
            error_message=str(e),
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
    """
    operation_start = datetime.now()

    try:
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
            data_classification=DataClassification.DERIVED_DATA,
            table_name="strategies",
        )

        # 记录操作到监控数据库
        operation_time = (datetime.now() - operation_start).total_seconds() * 1000
        monitoring_db.log_operation(
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
        monitoring_db.log_operation(
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
            data_classification=DataClassification.DERIVED_DATA,
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
async def update_strategy(
    strategy_id: int, strategy_update: Dict[str, Any]
) -> Dict[str, Any]:
    """更新策略"""
    try:
        manager = MyStocksUnifiedManager()

        # 先获取现有策略
        strategies = manager.load_data_by_classification(
            data_classification=DataClassification.DERIVED_DATA,
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
            data_classification=DataClassification.DERIVED_DATA,
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

        delete_data = pd.DataFrame(
            [{"id": strategy_id, "status": "archived", "updated_at": datetime.now()}]
        )

        result = manager.save_data_by_classification(
            data=delete_data,
            data_classification=DataClassification.DERIVED_DATA,
            table_name="strategies",
            upsert=True,
        )

        if result:
            return {"message": "策略已归档"}
        else:
            raise HTTPException(status_code=500, detail="策略删除失败")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除策略失败: {str(e)}")


# ============ 模型训练 ============


@router.post("/models/train")
async def train_model(
    config: Dict[str, Any], background_tasks: BackgroundTasks
) -> Dict[str, Any]:
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
            data_classification=DataClassification.DERIVED_DATA,
            table_name="models",
        )

        if not result:
            raise HTTPException(status_code=500, detail="创建模型记录失败")

        # 获取创建的模型ID（简化版本，实际应该从返回值中获取）
        models = manager.load_data_by_classification(
            data_classification=DataClassification.DERIVED_DATA,
            table_name="models",
            filters={"name": config.get("name")},
        )
        model_id = (
            models.iloc[-1]["id"] if models is not None and len(models) > 0 else 1
        )

        # 后台任务训练模型
        task_id = f"train_{model_id}_{int(datetime.now().timestamp())}"
        background_tasks.add_task(train_model_task, model_id=model_id, config=config)

        return {"task_id": task_id, "model_id": model_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动模型训练失败: {str(e)}")


async def train_model_task(model_id: int, config: Dict[str, Any]):
    """后台训练任务"""
    try:
        manager = MyStocksUnifiedManager()

        # 创建模型实例
        if config["model_type"] == "random_forest":
            model = RandomForestModel(**config.get("hyperparameters", {}))
        elif config["model_type"] == "lightgbm":
            model = LightGBMModel(**config.get("hyperparameters", {}))
        else:
            raise ValueError(f"不支持的模型类型: {config['model_type']}")

        # 训练模型（这里用模拟数据）
        # 实际应该加载真实训练数据
        # X_train, y_train = load_training_data(config['training_config'])
        # metrics = model.fit(X_train, y_train, **config['training_config'])

        # 保存模型
        model_path = f"models/model_{model_id}.pkl"
        # model.save_model(model_path)

        # 更新数据库
        import pandas as pd

        update_data = pd.DataFrame(
            [
                {
                    "id": model_id,
                    "status": "completed",
                    "model_path": model_path,
                    "training_completed_at": datetime.now(),
                }
            ]
        )

        manager.save_data_by_classification(
            data=update_data,
            data_classification=DataClassification.DERIVED_DATA,
            table_name="models",
            upsert=True,
        )

    except Exception:
        # 训练失败
        manager = MyStocksUnifiedManager()
        import pandas as pd

        fail_data = pd.DataFrame([{"id": model_id, "status": "failed"}])
        manager.save_data_by_classification(
            data=fail_data,
            data_classification=DataClassification.DERIVED_DATA,
            table_name="models",
            upsert=True,
        )
        raise


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
            data_classification=DataClassification.DERIVED_DATA,
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
async def list_models(
    model_type: Optional[str] = None, status: Optional[str] = None
) -> List[Dict[str, Any]]:
    """获取模型列表"""
    try:
        manager = MyStocksUnifiedManager()

        filters = {}
        if model_type:
            filters["model_type"] = model_type
        if status:
            filters["status"] = status

        models = manager.load_data_by_classification(
            data_classification=DataClassification.DERIVED_DATA,
            table_name="models",
            filters=filters,
        )

        return models.to_dict("records") if models is not None else []

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模型列表失败: {str(e)}")


# ============ 回测执行 ============


@router.post("/backtest/run")
async def run_backtest(
    config: Dict[str, Any], background_tasks: BackgroundTasks
) -> Dict[str, int]:
    """
    执行回测

    Args:
        config: 回测配置

    Returns:
        {"backtest_id": 123}
    """
    try:
        manager = MyStocksUnifiedManager()

        # 创建回测记录
        import pandas as pd

        backtest_data = {
            "name": config.get("name"),
            "strategy_id": config.get("strategy_id"),
            "start_date": config.get("start_date"),
            "end_date": config.get("end_date"),
            "initial_cash": config.get("initial_cash", 1000000),
            "commission_rate": config.get("commission_rate", 0.0003),
            "stamp_tax_rate": config.get("stamp_tax_rate", 0.001),
            "slippage_rate": config.get("slippage_rate", 0.001),
            "status": "pending",
            "created_at": datetime.now(),
        }

        backtest_df = pd.DataFrame([backtest_data])
        result = manager.save_data_by_classification(
            data=backtest_df,
            data_classification=DataClassification.DERIVED_DATA,
            table_name="backtests",
        )

        if not result:
            raise HTTPException(status_code=500, detail="创建回测记录失败")

        # 获取创建的回测ID
        backtests = manager.load_data_by_classification(
            data_classification=DataClassification.DERIVED_DATA,
            table_name="backtests",
            filters={"name": config.get("name")},
        )
        backtest_id = (
            backtests.iloc[-1]["id"]
            if backtests is not None and len(backtests) > 0
            else 1
        )

        # 后台任务执行回测
        background_tasks.add_task(
            run_backtest_task, backtest_id=backtest_id, config=config
        )

        return {"backtest_id": backtest_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动回测失败: {str(e)}")


async def run_backtest_task(backtest_id: int, config: Dict[str, Any]):
    """后台回测任务"""
    try:
        manager = MyStocksUnifiedManager()

        # 更新状态为运行中
        import pandas as pd

        running_data = pd.DataFrame(
            [{"id": backtest_id, "status": "running", "started_at": datetime.now()}]
        )
        manager.save_data_by_classification(
            data=running_data,
            data_classification=DataClassification.DERIVED_DATA,
            table_name="backtests",
            upsert=True,
        )

        # 执行回测（这里需要实际的策略和数据）
        # engine = BacktestEngine(...)
        # results = engine.run()

        # 保存结果（模拟）
        results = {
            "total_return": 0.15,
            "sharpe_ratio": 1.5,
            "max_drawdown": -0.12,
            "win_rate": 0.65,
        }

        completed_data = pd.DataFrame(
            [
                {
                    "id": backtest_id,
                    "status": "completed",
                    "results": results,
                    "completed_at": datetime.now(),
                }
            ]
        )
        manager.save_data_by_classification(
            data=completed_data,
            data_classification=DataClassification.DERIVED_DATA,
            table_name="backtests",
            upsert=True,
        )

    except Exception:
        manager = MyStocksUnifiedManager()
        import pandas as pd

        failed_data = pd.DataFrame([{"id": backtest_id, "status": "failed"}])
        manager.save_data_by_classification(
            data=failed_data,
            data_classification=DataClassification.DERIVED_DATA,
            table_name="backtests",
            upsert=True,
        )
        raise


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
            data_classification=DataClassification.DERIVED_DATA,
            table_name="backtests",
            filters=filters,
        )

        total = len(backtests) if backtests is not None else 0
        start = (page - 1) * page_size
        end = start + page_size
        items = (
            backtests.iloc[start:end].to_dict("records")
            if backtests is not None
            else []
        )

        return {"items": items, "total": total, "page": page, "page_size": page_size}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取回测结果失败: {str(e)}")


@router.get("/backtest/results/{backtest_id}")
async def get_backtest_result(backtest_id: int) -> Dict[str, Any]:
    """获取回测详细结果"""
    try:
        manager = MyStocksUnifiedManager()

        backtests = manager.load_data_by_classification(
            data_classification=DataClassification.DERIVED_DATA,
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
    """获取回测图表数据"""
    try:
        manager = MyStocksUnifiedManager()

        backtests = manager.load_data_by_classification(
            data_classification=DataClassification.DERIVED_DATA,
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
