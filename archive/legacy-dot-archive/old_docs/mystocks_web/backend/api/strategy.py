"""
策略管理 API

提供策略CRUD、模型训练、回测执行等接口

Author: JohnC & Claude
Version: 1.0.0
Date: 2025-10-24
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from ..database import get_db
from ..models import Strategy, Model, Backtest
from ..schemas.strategy import (
    StrategyCreate,
    StrategyUpdate,
    StrategyResponse,
    ModelTrainConfig,
    ModelResponse,
    BacktestConfig,
    BacktestResponse,
)
from ...model import RandomForestModel, LightGBMModel

router = APIRouter(prefix="/api/v1/strategy", tags=["策略管理"])


# ============ 策略 CRUD ============


@router.get("/strategies", response_model=dict)
async def list_strategies(
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
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
    query = db.query(Strategy)

    if status:
        query = query.filter(Strategy.status == status)

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": [StrategyResponse.from_orm(item) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/strategies", response_model=StrategyResponse)
async def create_strategy(strategy: StrategyCreate, db: Session = Depends(get_db)):
    """
    创建新策略

    Args:
        strategy: 策略创建数据

    Returns:
        StrategyResponse: 创建的策略对象
    """
    db_strategy = Strategy(**strategy.dict())
    db.add(db_strategy)
    db.commit()
    db.refresh(db_strategy)

    return StrategyResponse.from_orm(db_strategy)


@router.get("/strategies/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(strategy_id: int, db: Session = Depends(get_db)):
    """获取策略详情"""
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()

    if not strategy:
        raise HTTPException(status_code=404, detail="策略不存在")

    return StrategyResponse.from_orm(strategy)


@router.put("/strategies/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(
    strategy_id: int, strategy_update: StrategyUpdate, db: Session = Depends(get_db)
):
    """更新策略"""
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()

    if not strategy:
        raise HTTPException(status_code=404, detail="策略不存在")

    for key, value in strategy_update.dict(exclude_unset=True).items():
        setattr(strategy, key, value)

    strategy.updated_at = datetime.now()
    db.commit()
    db.refresh(strategy)

    return StrategyResponse.from_orm(strategy)


@router.delete("/strategies/{strategy_id}")
async def delete_strategy(strategy_id: int, db: Session = Depends(get_db)):
    """删除策略"""
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()

    if not strategy:
        raise HTTPException(status_code=404, detail="策略不存在")

    db.delete(strategy)
    db.commit()

    return {"message": "策略已删除"}


# ============ 模型训练 ============


@router.post("/models/train")
async def train_model(
    config: ModelTrainConfig,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    启动模型训练任务

    Args:
        config: 训练配置

    Returns:
        {"task_id": "task_xxx", "model_id": 123}
    """
    # 创建模型记录
    db_model = Model(
        name=config.name,
        model_type=config.model_type,
        hyperparameters=config.hyperparameters,
        training_config=config.training_config,
        status="training",
        training_started_at=datetime.now(),
    )
    db.add(db_model)
    db.commit()
    db.refresh(db_model)

    # 后台任务训练模型
    task_id = f"train_{db_model.id}_{int(datetime.now().timestamp())}"
    background_tasks.add_task(
        train_model_task, model_id=db_model.id, config=config, db=db
    )

    return {"task_id": task_id, "model_id": db_model.id}


async def train_model_task(model_id: int, config: ModelTrainConfig, db: Session):
    """后台训练任务"""
    try:
        # 获取训练数据
        # X_train, y_train = load_training_data(config.training_config)

        # 创建模型实例
        if config.model_type == "random_forest":
            model = RandomForestModel(**config.hyperparameters)
        elif config.model_type == "lightgbm":
            model = LightGBMModel(**config.hyperparameters)
        else:
            raise ValueError(f"不支持的模型类型: {config.model_type}")

        # 训练模型（这里用模拟数据）
        # metrics = model.fit(X_train, y_train, **config.training_config)

        # 保存模型
        model_path = f"models/model_{model_id}.pkl"
        # model.save_model(model_path)

        # 更新数据库
        db_model = db.query(Model).filter(Model.id == model_id).first()
        db_model.status = "completed"
        db_model.model_path = model_path
        # db_model.performance_metrics = metrics
        db_model.training_completed_at = datetime.now()
        db.commit()

    except Exception:
        # 训练失败
        db_model = db.query(Model).filter(Model.id == model_id).first()
        db_model.status = "failed"
        db.commit()
        raise


@router.get("/models/training/{task_id}/status")
async def get_training_status(task_id: str, db: Session = Depends(get_db)):
    """
    查询训练状态

    Returns:
        {
            "status": "training" | "completed" | "failed",
            "progress": 75,
            "metrics": {...}
        }
    """
    # 从task_id解析model_id
    model_id = int(task_id.split("_")[1])

    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")

    # 计算进度（简化版本）
    progress = 100 if model.status == "completed" else 0
    if model.status == "training":
        # 根据时间估算进度
        elapsed = (datetime.now() - model.training_started_at).seconds
        progress = min(95, int(elapsed / 60 * 20))  # 假设5分钟完成

    return {
        "status": model.status,
        "progress": progress,
        "metrics": model.performance_metrics or {},
    }


@router.get("/models", response_model=List[ModelResponse])
async def list_models(
    model_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """获取模型列表"""
    query = db.query(Model)

    if model_type:
        query = query.filter(Model.model_type == model_type)
    if status:
        query = query.filter(Model.status == status)

    models = query.order_by(Model.created_at.desc()).all()

    return [ModelResponse.from_orm(m) for m in models]


@router.get("/models/{model_id}/metrics")
async def get_model_metrics(model_id: int, db: Session = Depends(get_db)):
    """获取模型性能指标"""
    model = db.query(Model).filter(Model.id == model_id).first()

    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")

    return {
        "model_id": model.id,
        "model_type": model.model_type,
        "metrics": model.performance_metrics or {},
        "training_time": (
            (model.training_completed_at - model.training_started_at).seconds
            if model.training_completed_at
            else None
        ),
    }


# ============ 回测执行 ============


@router.post("/backtest/run")
async def run_backtest(
    config: BacktestConfig,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    执行回测

    Args:
        config: 回测配置

    Returns:
        {"backtest_id": 123}
    """
    # 创建回测记录
    db_backtest = Backtest(
        name=config.name,
        strategy_id=config.strategy_id,
        start_date=config.start_date,
        end_date=config.end_date,
        initial_cash=config.initial_cash,
        commission_rate=config.commission_rate,
        stamp_tax_rate=config.stamp_tax_rate,
        slippage_rate=config.slippage_rate,
        status="pending",
        created_at=datetime.now(),
    )
    db.add(db_backtest)
    db.commit()
    db.refresh(db_backtest)

    # 后台任务执行回测
    background_tasks.add_task(
        run_backtest_task, backtest_id=db_backtest.id, config=config, db=db
    )

    return {"backtest_id": db_backtest.id}


async def run_backtest_task(backtest_id: int, config: BacktestConfig, db: Session):
    """后台回测任务"""
    try:
        # 更新状态为运行中
        db_backtest = db.query(Backtest).filter(Backtest.id == backtest_id).first()
        db_backtest.status = "running"
        db_backtest.started_at = datetime.now()
        db.commit()

        # 获取策略
        strategy = db.query(Strategy).filter(Strategy.id == config.strategy_id).first()

        # 执行回测（这里需要实际的策略和数据）
        # engine = BacktestEngine(
        #     strategy=strategy,
        #     data_provider=data_provider,
        #     start_date=config.start_date,
        #     end_date=config.end_date,
        #     init_cash=config.initial_cash,
        #     commission_rate=config.commission_rate,
        #     stamp_tax_rate=config.stamp_tax_rate,
        #     slippage_rate=config.slippage_rate
        # )
        # results = engine.run()

        # 保存结果（模拟）
        results = {
            "total_return": 0.15,
            "sharpe_ratio": 1.5,
            "max_drawdown": -0.12,
            "win_rate": 0.65,
        }

        db_backtest.status = "completed"
        db_backtest.results = results
        db_backtest.completed_at = datetime.now()
        db.commit()

    except Exception:
        db_backtest = db.query(Backtest).filter(Backtest.id == backtest_id).first()
        db_backtest.status = "failed"
        db.commit()
        raise


@router.get("/backtest/results")
async def list_backtest_results(
    strategy_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    """获取回测结果列表"""
    query = db.query(Backtest)

    if strategy_id:
        query = query.filter(Backtest.strategy_id == strategy_id)

    total = query.count()
    items = (
        query.order_by(Backtest.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": [BacktestResponse.from_orm(item) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/backtest/results/{backtest_id}")
async def get_backtest_result(backtest_id: int, db: Session = Depends(get_db)):
    """获取回测详细结果"""
    backtest = db.query(Backtest).filter(Backtest.id == backtest_id).first()

    if not backtest:
        raise HTTPException(status_code=404, detail="回测不存在")

    # 获取交易明细
    # trades = db.query(BacktestTrade)\
    #           .filter(BacktestTrade.backtest_id == backtest_id)\
    #           .all()

    return {
        **BacktestResponse.from_orm(backtest).dict(),
        # "trades": trades,
        # "daily_results": backtest.results.get('daily_results', [])
    }


@router.get("/backtest/results/{backtest_id}/chart-data")
async def get_backtest_chart_data(backtest_id: int, db: Session = Depends(get_db)):
    """获取回测图表数据"""
    backtest = db.query(Backtest).filter(Backtest.id == backtest_id).first()

    if not backtest:
        raise HTTPException(status_code=404, detail="回测不存在")

    # 提取图表数据
    results = backtest.results or {}

    return {
        "equity_curve": results.get("equity_curve", []),
        "drawdown_curve": results.get("drawdown_curve", []),
        "returns_distribution": results.get("returns_distribution", []),
    }
