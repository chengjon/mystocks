"""
Strategy Repository Layer

提供策略数据的数据库访问接口，使用SQLAlchemy ORM操作PostgreSQL
"""
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Text, Numeric, TIMESTAMP, ARRAY, CheckConstraint, Index, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.strategy_schemas import (
    StrategyConfig,
    StrategyCreateRequest,
    StrategyUpdateRequest,
    StrategyStatus,
    StrategyType,
    StrategyParameter
)

logger = logging.getLogger(__name__)
Base = declarative_base()


# ============================================================
# SQLAlchemy ORM Models
# ============================================================

class UserStrategyModel(Base):
    """用户策略表ORM模型"""
    __tablename__ = 'user_strategies'

    strategy_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    strategy_name = Column(String(100), nullable=False)
    strategy_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)

    # 策略参数 (JSON格式)
    parameters = Column(JSON, default=list)

    # 风险控制参数
    max_position_size = Column(Numeric(5, 4), nullable=False, default=0.1)
    stop_loss_percent = Column(Numeric(5, 2), nullable=True)
    take_profit_percent = Column(Numeric(5, 2), nullable=True)

    # 状态和元数据
    status = Column(String(20), nullable=False, default='draft')
    tags = Column(ARRAY(Text), default=list)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            "strategy_type IN ('momentum', 'mean_reversion', 'breakout', 'grid', 'custom')",
            name='chk_strategy_type'
        ),
        CheckConstraint(
            "status IN ('draft', 'active', 'paused', 'archived')",
            name='chk_status'
        ),
        CheckConstraint(
            "max_position_size > 0 AND max_position_size <= 1",
            name='chk_position_size'
        ),
        Index('idx_user_strategies_user_id', 'user_id'),
        Index('idx_user_strategies_status', 'status'),
        Index('idx_user_strategies_type', 'strategy_type'),
        Index('idx_user_strategies_created_at', 'created_at'),
    )


# ============================================================
# Repository Class
# ============================================================

class StrategyRepository:
    """策略数据仓库

    提供策略数据的CRUD操作，封装数据库访问逻辑
    """

    def __init__(self, db_session: Session):
        """初始化仓库

        Args:
            db_session: SQLAlchemy数据库会话
        """
        self.db = db_session

    def create_strategy(self, request: StrategyCreateRequest) -> StrategyConfig:
        """创建新策略

        Args:
            request: 策略创建请求

        Returns:
            创建的策略配置对象

        Raises:
            SQLAlchemyError: 数据库操作失败
        """
        try:
            # 转换Pydantic模型为ORM模型
            strategy_orm = UserStrategyModel(
                user_id=request.user_id,
                strategy_name=request.strategy_name,
                strategy_type=request.strategy_type.value,
                description=request.description,
                parameters=[param.dict() for param in request.parameters],
                max_position_size=request.max_position_size,
                stop_loss_percent=request.stop_loss_percent,
                take_profit_percent=request.take_profit_percent,
                status=request.status.value,
                tags=request.tags or []
            )

            # 保存到数据库
            self.db.add(strategy_orm)
            self.db.commit()
            self.db.refresh(strategy_orm)

            logger.info(f"创建策略成功: strategy_id={strategy_orm.strategy_id}, name={strategy_orm.strategy_name}")

            # 转换为Pydantic响应模型
            return self._orm_to_pydantic(strategy_orm)

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"创建策略失败: {str(e)}")
            raise

    def get_strategy(self, strategy_id: int) -> Optional[StrategyConfig]:
        """根据ID获取策略

        Args:
            strategy_id: 策略ID

        Returns:
            策略配置对象，不存在时返回None
        """
        try:
            strategy_orm = self.db.query(UserStrategyModel).filter(
                UserStrategyModel.strategy_id == strategy_id
            ).first()

            if strategy_orm is None:
                logger.warning(f"策略不存在: strategy_id={strategy_id}")
                return None

            return self._orm_to_pydantic(strategy_orm)

        except SQLAlchemyError as e:
            logger.error(f"查询策略失败: strategy_id={strategy_id}, error={str(e)}")
            raise

    def list_strategies(
        self,
        user_id: int,
        status: Optional[StrategyStatus] = None,
        strategy_type: Optional[StrategyType] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[StrategyConfig], int]:
        """获取策略列表

        Args:
            user_id: 用户ID
            status: 状态筛选（可选）
            strategy_type: 类型筛选（可选）
            page: 页码（从1开始）
            page_size: 每页数量

        Returns:
            (策略列表, 总数)元组
        """
        try:
            # 构建查询
            query = self.db.query(UserStrategyModel).filter(
                UserStrategyModel.user_id == user_id
            )

            # 状态筛选
            if status:
                query = query.filter(UserStrategyModel.status == status.value)

            # 类型筛选
            if strategy_type:
                query = query.filter(UserStrategyModel.strategy_type == strategy_type.value)

            # 获取总数
            total_count = query.count()

            # 分页查询
            offset = (page - 1) * page_size
            strategies_orm = query.order_by(
                UserStrategyModel.created_at.desc()
            ).offset(offset).limit(page_size).all()

            # 转换为Pydantic模型
            strategies = [self._orm_to_pydantic(s) for s in strategies_orm]

            logger.info(f"查询策略列表: user_id={user_id}, total={total_count}, page={page}/{(total_count + page_size - 1) // page_size}")

            return strategies, total_count

        except SQLAlchemyError as e:
            logger.error(f"查询策略列表失败: user_id={user_id}, error={str(e)}")
            raise

    def update_strategy(
        self,
        strategy_id: int,
        request: StrategyUpdateRequest
    ) -> Optional[StrategyConfig]:
        """更新策略

        Args:
            strategy_id: 策略ID
            request: 更新请求（仅包含需要更新的字段）

        Returns:
            更新后的策略配置，策略不存在时返回None

        Raises:
            SQLAlchemyError: 数据库操作失败
        """
        try:
            strategy_orm = self.db.query(UserStrategyModel).filter(
                UserStrategyModel.strategy_id == strategy_id
            ).first()

            if strategy_orm is None:
                logger.warning(f"策略不存在: strategy_id={strategy_id}")
                return None

            # 仅更新非None字段
            update_data = request.dict(exclude_unset=True)

            # 处理枚举类型
            if 'status' in update_data and update_data['status'] is not None:
                update_data['status'] = update_data['status'].value
            if 'strategy_type' in update_data and update_data['strategy_type'] is not None:
                update_data['strategy_type'] = update_data['strategy_type'].value

            # 处理parameters字段（转换为dict列表）
            if 'parameters' in update_data and update_data['parameters'] is not None:
                update_data['parameters'] = [param.dict() for param in update_data['parameters']]

            # 应用更新
            for key, value in update_data.items():
                if hasattr(strategy_orm, key):
                    setattr(strategy_orm, key, value)

            strategy_orm.updated_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(strategy_orm)

            logger.info(f"更新策略成功: strategy_id={strategy_id}, updated_fields={list(update_data.keys())}")

            return self._orm_to_pydantic(strategy_orm)

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"更新策略失败: strategy_id={strategy_id}, error={str(e)}")
            raise

    def delete_strategy(self, strategy_id: int) -> bool:
        """删除策略

        Args:
            strategy_id: 策略ID

        Returns:
            True表示删除成功，False表示策略不存在

        Raises:
            SQLAlchemyError: 数据库操作失败
        """
        try:
            result = self.db.query(UserStrategyModel).filter(
                UserStrategyModel.strategy_id == strategy_id
            ).delete()

            self.db.commit()

            if result > 0:
                logger.info(f"删除策略成功: strategy_id={strategy_id}")
                return True
            else:
                logger.warning(f"策略不存在: strategy_id={strategy_id}")
                return False

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"删除策略失败: strategy_id={strategy_id}, error={str(e)}")
            raise

    def get_strategies_by_status(
        self,
        user_id: int,
        status: StrategyStatus
    ) -> List[StrategyConfig]:
        """根据状态获取所有策略（不分页）

        Args:
            user_id: 用户ID
            status: 策略状态

        Returns:
            策略列表
        """
        try:
            strategies_orm = self.db.query(UserStrategyModel).filter(
                UserStrategyModel.user_id == user_id,
                UserStrategyModel.status == status.value
            ).order_by(UserStrategyModel.created_at.desc()).all()

            return [self._orm_to_pydantic(s) for s in strategies_orm]

        except SQLAlchemyError as e:
            logger.error(f"查询策略失败: user_id={user_id}, status={status}, error={str(e)}")
            raise

    # ============================================================
    # Private Helper Methods
    # ============================================================

    def _orm_to_pydantic(self, strategy_orm: UserStrategyModel) -> StrategyConfig:
        """将ORM模型转换为Pydantic模型

        Args:
            strategy_orm: SQLAlchemy ORM模型实例

        Returns:
            Pydantic StrategyConfig模型
        """
        # 转换parameters (从dict列表到StrategyParameter对象列表)
        parameters = []
        if strategy_orm.parameters:
            for param_dict in strategy_orm.parameters:
                parameters.append(StrategyParameter(**param_dict))

        return StrategyConfig(
            strategy_id=strategy_orm.strategy_id,
            user_id=strategy_orm.user_id,
            strategy_name=strategy_orm.strategy_name,
            strategy_type=StrategyType(strategy_orm.strategy_type),
            description=strategy_orm.description,
            parameters=parameters,
            max_position_size=float(strategy_orm.max_position_size),
            stop_loss_percent=float(strategy_orm.stop_loss_percent) if strategy_orm.stop_loss_percent else None,
            take_profit_percent=float(strategy_orm.take_profit_percent) if strategy_orm.take_profit_percent else None,
            status=StrategyStatus(strategy_orm.status),
            tags=strategy_orm.tags or [],
            created_at=strategy_orm.created_at,
            updated_at=strategy_orm.updated_at
        )
