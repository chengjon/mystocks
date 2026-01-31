"""
Backtest Repository Layer

提供回测数据的数据库访问接口，使用SQLAlchemy ORM操作PostgreSQL
"""

import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    ARRAY,
    JSON,
    TIMESTAMP,
    CheckConstraint,
    Column,
    Date,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship

from app.models.strategy_schemas import (
    BacktestExecuteRequest,
    BacktestResult,
    BacktestStatus,
    EquityCurvePoint,
    PerformanceMetrics,
    TradeRecord,
)

logger = logging.getLogger(__name__)
Base = declarative_base()


# ============================================================
# SQLAlchemy ORM Models
# ============================================================


class BacktestResultModel(Base):
    """回测结果表ORM模型"""

    __tablename__ = "backtest_results"

    backtest_id = Column(Integer, primary_key=True, autoincrement=True)
    strategy_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)

    # 回测配置
    symbols = Column(ARRAY(Text), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    initial_capital = Column(Numeric(15, 2), nullable=False)
    commission_rate = Column(Numeric(6, 4), nullable=False, default=0.0003)
    slippage_rate = Column(Numeric(6, 4), nullable=False, default=0.001)
    benchmark = Column(String(20), nullable=True)

    # 回测结果
    final_capital = Column(Numeric(15, 2), nullable=True)
    performance_metrics = Column(JSON, nullable=True)

    # 回测状态
    status = Column(String(20), nullable=False, default="pending")
    error_message = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    started_at = Column(TIMESTAMP, nullable=True)
    completed_at = Column(TIMESTAMP, nullable=True)

    # 关系
    equity_curves = relationship(
        "BacktestEquityCurveModel",
        back_populates="backtest",
        cascade="all, delete-orphan",
    )
    trades = relationship("BacktestTradeModel", back_populates="backtest", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'running', 'completed', 'failed')",
            name="chk_backtest_status",
        ),
        CheckConstraint("end_date >= start_date", name="chk_date_range"),
        Index("idx_backtest_results_strategy_id", "strategy_id"),
        Index("idx_backtest_results_user_id", "user_id"),
        Index("idx_backtest_results_status", "status"),
        Index("idx_backtest_results_created_at", "created_at"),
    )


class BacktestEquityCurveModel(Base):
    """权益曲线表ORM模型"""

    __tablename__ = "backtest_equity_curves"

    id = Column(Integer, primary_key=True, autoincrement=True)
    backtest_id = Column(
        Integer,
        ForeignKey("backtest_results.backtest_id", ondelete="CASCADE"),
        nullable=False,
    )
    trade_date = Column(Date, nullable=False)
    equity = Column(Numeric(15, 2), nullable=False)
    drawdown = Column(Numeric(5, 2), nullable=False)
    benchmark_equity = Column(Numeric(15, 2), nullable=True)

    # 关系
    backtest = relationship("BacktestResultModel", back_populates="equity_curves")

    __table_args__ = (
        UniqueConstraint("backtest_id", "trade_date", name="uq_backtest_trade_date"),
        Index("idx_equity_curves_backtest_id", "backtest_id"),
        Index("idx_equity_curves_trade_date", "trade_date"),
    )


class BacktestTradeModel(Base):
    """交易记录表ORM模型"""

    __tablename__ = "backtest_trades"

    trade_id = Column(Integer, primary_key=True, autoincrement=True)
    backtest_id = Column(
        Integer,
        ForeignKey("backtest_results.backtest_id", ondelete="CASCADE"),
        nullable=False,
    )
    symbol = Column(String(20), nullable=False)
    trade_date = Column(Date, nullable=False)
    action = Column(String(10), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    commission = Column(Numeric(10, 2), nullable=False)
    profit_loss = Column(Numeric(15, 2), nullable=True)

    # 关系
    backtest = relationship("BacktestResultModel", back_populates="trades")

    __table_args__ = (
        CheckConstraint("action IN ('buy', 'sell')", name="chk_action"),
        Index("idx_backtest_trades_backtest_id", "backtest_id"),
        Index("idx_backtest_trades_symbol", "symbol"),
        Index("idx_backtest_trades_date", "trade_date"),
    )


# ============================================================
# Repository Class
# ============================================================


class BacktestRepository:
    """回测数据仓库

    提供回测结果、权益曲线和交易记录的CRUD操作
    """

    def __init__(self, db_session: Session):
        """初始化仓库

        Args:
            db_session: SQLAlchemy数据库会话
        """
        self.db = db_session

    def create_backtest(self, request: BacktestExecuteRequest) -> BacktestResult:
        """创建新回测任务

        Args:
            request: 回测执行请求

        Returns:
            创建的回测结果对象（初始状态为pending）

        Raises:
            SQLAlchemyError: 数据库操作失败
        """
        try:
            backtest_orm = BacktestResultModel(
                strategy_id=request.strategy_id,
                user_id=request.user_id,
                symbols=request.symbols,
                start_date=request.start_date,
                end_date=request.end_date,
                initial_capital=request.initial_capital,
                commission_rate=request.commission_rate,
                slippage_rate=request.slippage_rate,
                benchmark=request.benchmark,
                status="pending",
            )

            self.db.add(backtest_orm)
            self.db.commit()
            self.db.refresh(backtest_orm)

            logger.info("创建回测任务成功: backtest_id={backtest_orm.backtest_id}, strategy_id={request.strategy_id}"")

            return self._orm_to_pydantic(backtest_orm)

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error("创建回测任务失败: {str(e)}"")
            raise

    def get_backtest(self, backtest_id: int) -> Optional[BacktestResult]:
        """根据ID获取回测结果

        Args:
            backtest_id: 回测ID

        Returns:
            回测结果对象，不存在时返回None
        """
        try:
            backtest_orm = (
                self.db.query(BacktestResultModel).filter(BacktestResultModel.backtest_id == backtest_id).first()
            )

            if backtest_orm is None:
                logger.warning("回测不存在: backtest_id=%(backtest_id)s"")
                return None

            return self._orm_to_pydantic(backtest_orm)

        except SQLAlchemyError as e:
            logger.error("查询回测失败: backtest_id=%(backtest_id)s, error={str(e)}"")
            raise

    def list_backtests(
        self,
        user_id: int,
        strategy_id: Optional[int] = None,
        status: Optional[BacktestStatus] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[BacktestResult], int]:
        """获取回测列表

        Args:
            user_id: 用户ID
            strategy_id: 策略ID筛选（可选）
            status: 状态筛选（可选）
            page: 页码（从1开始）
            page_size: 每页数量

        Returns:
            (回测列表, 总数)元组
        """
        try:
            query = self.db.query(BacktestResultModel).filter(BacktestResultModel.user_id == user_id)

            if strategy_id:
                query = query.filter(BacktestResultModel.strategy_id == strategy_id)

            if status:
                query = query.filter(BacktestResultModel.status == status.value)

            total_count = query.count()

            offset = (page - 1) * page_size
            backtests_orm = query.order_by(BacktestResultModel.created_at.desc()).offset(offset).limit(page_size).all()

            backtests = [self._orm_to_pydantic(b) for b in backtests_orm]

            logger.info("查询回测列表: user_id=%(user_id)s, total=%(total_count)s, page=%(page)s"")

            return backtests, total_count

        except SQLAlchemyError as e:
            logger.error("查询回测列表失败: user_id=%(user_id)s, error={str(e)}"")
            raise

    def update_backtest_status(
        self,
        backtest_id: int,
        status: BacktestStatus,
        error_message: Optional[str] = None,
    ) -> Optional[BacktestResult]:
        """更新回测状态

        Args:
            backtest_id: 回测ID
            status: 新状态
            error_message: 错误消息（失败时提供）

        Returns:
            更新后的回测结果，回测不存在时返回None
        """
        try:
            backtest_orm = (
                self.db.query(BacktestResultModel).filter(BacktestResultModel.backtest_id == backtest_id).first()
            )

            if backtest_orm is None:
                logger.warning("回测不存在: backtest_id=%(backtest_id)s"")
                return None

            backtest_orm.status = status.value
            backtest_orm.error_message = error_message

            # 更新时间戳
            if status == BacktestStatus.RUNNING:
                backtest_orm.started_at = datetime.utcnow()
            elif status in [BacktestStatus.COMPLETED, BacktestStatus.FAILED]:
                backtest_orm.completed_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(backtest_orm)

            logger.info("更新回测状态: backtest_id=%(backtest_id)s, status={status.value}"")

            return self._orm_to_pydantic(backtest_orm)

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error("更新回测状态失败: backtest_id=%(backtest_id)s, error={str(e)}"")
            raise

    def save_backtest_results(
        self,
        backtest_id: int,
        final_capital: float,
        performance_metrics: PerformanceMetrics,
    ) -> Optional[BacktestResult]:
        """保存回测结果

        Args:
            backtest_id: 回测ID
            final_capital: 最终资金
            performance_metrics: 绩效指标

        Returns:
            更新后的回测结果
        """
        try:
            backtest_orm = (
                self.db.query(BacktestResultModel).filter(BacktestResultModel.backtest_id == backtest_id).first()
            )

            if backtest_orm is None:
                logger.warning("回测不存在: backtest_id=%(backtest_id)s"")
                return None

            backtest_orm.final_capital = final_capital
            backtest_orm.performance_metrics = performance_metrics.dict()
            backtest_orm.status = "completed"
            backtest_orm.completed_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(backtest_orm)

            logger.info("保存回测结果成功: backtest_id=%(backtest_id)s"")

            return self._orm_to_pydantic(backtest_orm)

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error("保存回测结果失败: backtest_id=%(backtest_id)s, error={str(e)}"")
            raise

    def save_equity_curve(self, backtest_id: int, equity_curve: List[EquityCurvePoint]) -> bool:
        """保存权益曲线数据

        Args:
            backtest_id: 回测ID
            equity_curve: 权益曲线数据点列表

        Returns:
            True表示保存成功
        """
        try:
            # 批量插入权益曲线数据
            equity_models = [
                BacktestEquityCurveModel(
                    backtest_id=backtest_id,
                    trade_date=point.date,
                    equity=point.equity,
                    drawdown=point.drawdown,
                    benchmark_equity=point.benchmark_equity,
                )
                for point in equity_curve
            ]

            self.db.bulk_save_objects(equity_models)
            self.db.commit()

            logger.info("保存权益曲线成功: backtest_id=%(backtest_id)s, points={len(equity_curve)}"")

            return True

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error("保存权益曲线失败: backtest_id=%(backtest_id)s, error={str(e)}"")
            raise

    def get_equity_curve(self, backtest_id: int) -> List[EquityCurvePoint]:
        """获取权益曲线数据

        Args:
            backtest_id: 回测ID

        Returns:
            权益曲线数据点列表
        """
        try:
            curves_orm = (
                self.db.query(BacktestEquityCurveModel)
                .filter(BacktestEquityCurveModel.backtest_id == backtest_id)
                .order_by(BacktestEquityCurveModel.trade_date)
                .all()
            )

            return [
                EquityCurvePoint(
                    date=curve.trade_date,
                    equity=float(curve.equity),
                    drawdown=float(curve.drawdown),
                    benchmark_equity=float(curve.benchmark_equity) if curve.benchmark_equity else None,
                )
                for curve in curves_orm
            ]

        except SQLAlchemyError as e:
            logger.error("获取权益曲线失败: backtest_id=%(backtest_id)s, error={str(e)}"")
            raise

    def save_trades(self, backtest_id: int, trades: List[TradeRecord]) -> bool:
        """保存交易记录

        Args:
            backtest_id: 回测ID
            trades: 交易记录列表

        Returns:
            True表示保存成功
        """
        try:
            trade_models = [
                BacktestTradeModel(
                    backtest_id=backtest_id,
                    symbol=trade.symbol,
                    trade_date=trade.date,
                    action=trade.action,
                    price=trade.price,
                    quantity=trade.quantity,
                    amount=trade.amount,
                    commission=trade.commission,
                    profit_loss=trade.profit_loss,
                )
                for trade in trades
            ]

            self.db.bulk_save_objects(trade_models)
            self.db.commit()

            logger.info("保存交易记录成功: backtest_id=%(backtest_id)s, trades={len(trades)}"")

            return True

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error("保存交易记录失败: backtest_id=%(backtest_id)s, error={str(e)}"")
            raise

    def get_trades(self, backtest_id: int) -> List[TradeRecord]:
        """获取交易记录

        Args:
            backtest_id: 回测ID

        Returns:
            交易记录列表
        """
        try:
            trades_orm = (
                self.db.query(BacktestTradeModel)
                .filter(BacktestTradeModel.backtest_id == backtest_id)
                .order_by(BacktestTradeModel.trade_date)
                .all()
            )

            return [
                TradeRecord(
                    symbol=trade.symbol,
                    date=trade.trade_date,
                    action=trade.action,
                    price=float(trade.price),
                    quantity=trade.quantity,
                    amount=float(trade.amount),
                    commission=float(trade.commission),
                    profit_loss=float(trade.profit_loss) if trade.profit_loss else None,
                )
                for trade in trades_orm
            ]

        except SQLAlchemyError as e:
            logger.error("获取交易记录失败: backtest_id=%(backtest_id)s, error={str(e)}"")
            raise

    def delete_backtest(self, backtest_id: int) -> bool:
        """删除回测（级联删除权益曲线和交易记录）

        Args:
            backtest_id: 回测ID

        Returns:
            True表示删除成功，False表示回测不存在
        """
        try:
            result = self.db.query(BacktestResultModel).filter(BacktestResultModel.backtest_id == backtest_id).delete()

            self.db.commit()

            if result > 0:
                logger.info("删除回测成功: backtest_id=%(backtest_id)s"")
                return True
            else:
                logger.warning("回测不存在: backtest_id=%(backtest_id)s"")
                return False

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error("删除回测失败: backtest_id=%(backtest_id)s, error={str(e)}"")
            raise

    # ============================================================
    # Private Helper Methods
    # ============================================================

    def _orm_to_pydantic(self, backtest_orm: BacktestResultModel) -> BacktestResult:
        """将ORM模型转换为Pydantic模型

        Args:
            backtest_orm: SQLAlchemy ORM模型实例

        Returns:
            Pydantic BacktestResult模型
        """
        # 转换performance_metrics
        performance_metrics = None
        if backtest_orm.performance_metrics:
            performance_metrics = PerformanceMetrics(**backtest_orm.performance_metrics)

        # 获取权益曲线和交易记录（如果已加载）
        equity_curve = []
        if backtest_orm.equity_curves:
            equity_curve = [
                EquityCurvePoint(
                    date=curve.trade_date,
                    equity=float(curve.equity),
                    drawdown=float(curve.drawdown),
                    benchmark_equity=float(curve.benchmark_equity) if curve.benchmark_equity else None,
                )
                for curve in backtest_orm.equity_curves
            ]

        trades = []
        if backtest_orm.trades:
            trades = [
                TradeRecord(
                    symbol=trade.symbol,
                    date=trade.trade_date,
                    action=trade.action,
                    price=float(trade.price),
                    quantity=trade.quantity,
                    amount=float(trade.amount),
                    commission=float(trade.commission),
                    profit_loss=float(trade.profit_loss) if trade.profit_loss else None,
                )
                for trade in backtest_orm.trades
            ]

        return BacktestResult(
            backtest_id=backtest_orm.backtest_id,
            strategy_id=backtest_orm.strategy_id,
            user_id=backtest_orm.user_id,
            symbols=backtest_orm.symbols,
            start_date=backtest_orm.start_date,
            end_date=backtest_orm.end_date,
            initial_capital=float(backtest_orm.initial_capital),
            commission_rate=float(backtest_orm.commission_rate),
            slippage_rate=float(backtest_orm.slippage_rate),
            benchmark=backtest_orm.benchmark,
            final_capital=float(backtest_orm.final_capital) if backtest_orm.final_capital else None,
            performance_metrics=performance_metrics,
            equity_curve=equity_curve,
            trades=trades,
            status=BacktestStatus(backtest_orm.status),
            error_message=backtest_orm.error_message,
            created_at=backtest_orm.created_at,
            started_at=backtest_orm.started_at,
            completed_at=backtest_orm.completed_at,
        )
