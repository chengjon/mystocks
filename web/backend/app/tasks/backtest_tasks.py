"""
Backtest Celery Tasks

回测异步任务定义
"""

import logging
from datetime import datetime
from decimal import Decimal

from app.backtest.backtest_engine import BacktestEngine
from app.backtest.events import ProgressEvent
from app.core.celery_app import celery_app, get_progress_callback

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.tasks.backtest_tasks.run_backtest")
def run_backtest_task(self, backtest_id: int, strategy_config: dict, backtest_config: dict):
    """
    执行回测任务

    Args:
        backtest_id: 回测任务ID
        strategy_config: 策略配置
        backtest_config: 回测配置

    Returns:
        回测结果字典
    """
    logger.info("开始执行回测任务 %(backtest_id)s")

    try:
        # 更新任务状态
        self.update_state(
            state="STARTED",
            meta={
                "backtest_id": backtest_id,
                "progress": 0,
                "message": "正在初始化回测引擎...",
            },
        )

        # 转换日期字符串为 datetime 对象
        if isinstance(backtest_config.get("start_date"), str):
            backtest_config["start_date"] = datetime.strptime(backtest_config["start_date"], "%Y-%m-%d")
        if isinstance(backtest_config.get("end_date"), str):
            backtest_config["end_date"] = datetime.strptime(backtest_config["end_date"], "%Y-%m-%d")

        # 添加 backtest_id 到配置
        backtest_config["backtest_id"] = backtest_id

        # 获取数据源
        # TODO: 根据环境选择数据源（Mock/Real/Composite）
        from app.services.data_service import get_data_source

        data_source = get_data_source()

        # 定义进度回调
        def progress_callback(progress_event: ProgressEvent):
            """进度回调 - 更新 Celery 任务状态"""
            self.update_state(
                state="PROGRESS",
                meta={
                    "backtest_id": backtest_id,
                    "progress": progress_event.progress,
                    "current_date": progress_event.current_date.isoformat(),
                    "message": progress_event.message,
                },
            )

            # 尝试发送到 WebSocket
            ws_callback = get_progress_callback(str(backtest_id))
            if ws_callback:
                try:
                    ws_callback(progress_event.to_dict())
                except Exception as e:
                    logger.warning("WebSocket推送失败: %(e)s")

        # 创建回测引擎
        engine = BacktestEngine(
            strategy_config=strategy_config,
            backtest_config=backtest_config,
            data_source=data_source,
            progress_callback=progress_callback,
        )

        # 执行回测
        results = engine.run()

        logger.info("回测任务 %(backtest_id)s 完成")

        # 更新数据库中的回测结果
        _save_backtest_results(backtest_id, results)

        return results

    except Exception as e:
        logger.error("回测任务 {backtest_id} 失败: {str(e)}", exc_info=True)

        # 更新任务状态为失败
        self.update_state(
            state="FAILURE",
            meta={
                "backtest_id": backtest_id,
                "error": str(e),
                "message": f"回测失败: {str(e)}",
            },
        )

        # 更新数据库中的回测状态
        _update_backtest_status(backtest_id, "failed", str(e))

        raise


def _save_backtest_results(backtest_id: int, results: dict):
    """保存回测结果到数据库"""
    try:
        from app.core.database import SessionLocal
        from app.repositories.backtest_repository import BacktestRepository

        db = SessionLocal()
        try:
            repo = BacktestRepository(db)

            # 保存主要结果
            repo.save_backtest_results(
                backtest_id=backtest_id,
                final_capital=Decimal(str(results["final_capital"])),
                performance_metrics=results["performance_metrics"],
            )

            # 保存资金曲线
            if results.get("equity_curve"):
                equity_curve = [
                    {
                        "trade_date": datetime.fromisoformat(point["trade_date"]),
                        "equity": Decimal(str(point["equity"])),
                        "drawdown": Decimal(str(point["drawdown"])),
                    }
                    for point in results["equity_curve"]
                ]
                repo.save_equity_curve(backtest_id, equity_curve)

            # 保存交易记录
            if results.get("trades"):
                trades = [
                    {
                        "symbol": trade["symbol"],
                        "trade_date": (
                            trade["trade_date"]
                            if isinstance(trade["trade_date"], datetime)
                            else datetime.fromisoformat(trade["trade_date"])
                        ),
                        "action": trade["action"],
                        "price": Decimal(str(trade["price"])),
                        "quantity": trade["quantity"],
                        "amount": Decimal(str(trade["amount"])),
                        "commission": Decimal(str(trade["commission"])),
                        "profit_loss": Decimal(str(trade.get("profit_loss", 0))) if trade.get("profit_loss") else None,
                    }
                    for trade in results["trades"]
                ]
                repo.save_trades(backtest_id, trades)

            db.commit()
            logger.info("回测结果已保存: backtest_id=%(backtest_id)s")

        finally:
            db.close()

    except Exception as e:
        logger.error("保存回测结果失败: {str(e)}")
        raise


def _update_backtest_status(backtest_id: int, status: str, error_message: str = None):
    """更新回测状态"""
    try:
        from app.core.database import SessionLocal
        from app.repositories.backtest_repository import BacktestRepository

        db = SessionLocal()
        try:
            repo = BacktestRepository(db)
            repo.update_backtest_status(backtest_id, status, error_message)
            db.commit()
        finally:
            db.close()

    except Exception as e:
        logger.error("更新回测状态失败: {str(e)}")
