"""Indicator Calculation API Endpoints
技术指标计算API路由

Phase 4C Enhanced - 企业级技术指标计算服务
- 高性能缓存机制
- 增强参数验证
- 速率限制保护
- 完整错误处理
- 性能监控
- 批量计算优化
"""

import structlog
from fastapi import APIRouter, Depends

from app.api.auth import get_current_active_user
from app.core.exceptions import BusinessException, ForbiddenException, NotFoundException, ValidationException
from app.core.security import User
from app.schemas.indicator_request import (
    IndicatorConfigCreateRequest,
    IndicatorConfigUpdateRequest,
)
from app.schemas.indicator_response import (
    IndicatorConfigListResponse,
    IndicatorConfigResponse,
)


logger = structlog.get_logger()
router = APIRouter()


@router.post("/configs", response_model=IndicatorConfigResponse)
async def create_indicator_config(
    request: IndicatorConfigCreateRequest,
    current_user: User = Depends(get_current_active_user),
):
    """创建指标配置

    保存用户的常用指标组合配置,方便下次快速加载

    **请求示例**:
    ```json
    {
        "name": "我的常用配置",
        "indicators": [
            {"abbreviation": "SMA", "parameters": {"timeperiod": 20}},
            {"abbreviation": "RSI", "parameters": {"timeperiod": 14}}
        ]
    }
    ```
    """
    user_id = current_user.id

    try:
        from app.core.database import get_mysql_session
        from app.models.indicator_config import IndicatorConfiguration

        session = get_mysql_session()

        try:
            # 检查同名配置是否存在
            existing = (
                session.query(IndicatorConfiguration)
                .filter(
                    IndicatorConfiguration.user_id == user_id,
                    IndicatorConfiguration.name == request.name,
                )
                .first()
            )

            if existing:
                raise BusinessException(
                    detail=f"配置名称已存在: {request.name}",
                    status_code=409,
                    error_code="CONFIG_NAME_EXISTS",
                )

            # 创建新配置
            indicators_json = [
                {"abbreviation": ind.abbreviation, "parameters": ind.parameters} for ind in request.indicators
            ]

            new_config = IndicatorConfiguration(user_id=user_id, name=request.name, indicators=indicators_json)

            session.add(new_config)
            session.commit()
            session.refresh(new_config)

            logger.info(
                "Indicator config created",
                config_id=new_config.id,
                user_id=user_id,
                name=request.name,
            )

            return IndicatorConfigResponse(
                id=new_config.id,
                user_id=new_config.user_id,
                name=new_config.name,
                indicators=new_config.indicators,
                created_at=new_config.created_at,
                updated_at=new_config.updated_at,
                last_used_at=new_config.last_used_at,
            )

        finally:
            session.close()

    except (BusinessException, ValidationException, NotFoundException, ForbiddenException):
        raise
    except Exception as e:
        logger.error("Failed to create indicator config", exc_info=e)
        raise BusinessException(detail=f"创建配置失败: {e!s}", status_code=500, error_code="CONFIG_CREATION_FAILED")


@router.get("/configs", response_model=IndicatorConfigListResponse)
async def list_indicator_configs(current_user: User = Depends(get_current_active_user)):
    """获取用户的指标配置列表

    返回当前用户的所有已保存指标配置
    """
    user_id = current_user.id

    try:
        from app.core.database import get_mysql_session
        from app.models.indicator_config import IndicatorConfiguration

        session = get_mysql_session()

        try:
            # 查询用户所有配置,按最后使用时间倒序排列
            # MySQL不支持NULLS LAST,使用CASE WHEN处理NULL值
            from sqlalchemy import case

            configs = (
                session.query(IndicatorConfiguration)
                .filter(IndicatorConfiguration.user_id == user_id)
                .order_by(
                    case((IndicatorConfiguration.last_used_at.is_(None), 1), else_=0),
                    IndicatorConfiguration.last_used_at.desc(),
                    IndicatorConfiguration.updated_at.desc(),
                )
                .all()
            )

            config_list = [
                IndicatorConfigResponse(
                    id=cfg.id,
                    user_id=cfg.user_id,
                    name=cfg.name,
                    indicators=cfg.indicators,
                    created_at=cfg.created_at,
                    updated_at=cfg.updated_at,
                    last_used_at=cfg.last_used_at,
                )
                for cfg in configs
            ]

            logger.info("Listed indicator configs", user_id=user_id, count=len(config_list))

            return IndicatorConfigListResponse(total_count=len(config_list), configs=config_list)

        finally:
            session.close()

    except Exception as e:
        logger.error("Failed to list indicator configs", exc_info=e)
        raise BusinessException(
            detail=f"获取配置列表失败: {e!s}",
            status_code=500,
            error_code="CONFIG_LIST_RETRIEVAL_FAILED",
        )


@router.get("/configs/{config_id}", response_model=IndicatorConfigResponse)
async def get_indicator_config(config_id: int, current_user: User = Depends(get_current_active_user)):
    """获取指定的指标配置详情

    - **config_id**: 配置ID
    """
    user_id = current_user.id

    try:
        from datetime import datetime

        from app.core.database import get_mysql_session
        from app.models.indicator_config import IndicatorConfiguration

        session = get_mysql_session()

        try:
            # 查询配置
            config = (
                session.query(IndicatorConfiguration)
                .filter(
                    IndicatorConfiguration.id == config_id,
                    IndicatorConfiguration.user_id == user_id,
                )
                .first()
            )

            if not config:
                raise NotFoundException(resource="配置", identifier=config_id)

            # 更新最后使用时间
            config.last_used_at = datetime.now()
            session.commit()
            session.refresh(config)

            logger.info("Got indicator config", config_id=config_id, user_id=user_id)

            return IndicatorConfigResponse(
                id=config.id,
                user_id=config.user_id,
                name=config.name,
                indicators=config.indicators,
                created_at=config.created_at,
                updated_at=config.updated_at,
                last_used_at=config.last_used_at,
            )

        finally:
            session.close()

    except (BusinessException, ValidationException, NotFoundException, ForbiddenException):
        raise
    except Exception as e:
        logger.error("Failed to get indicator config", exc_info=e)
        raise BusinessException(detail=f"获取配置失败: {e!s}", status_code=500, error_code="CONFIG_RETRIEVAL_FAILED")


@router.put("/configs/{config_id}", response_model=IndicatorConfigResponse)
async def update_indicator_config(
    config_id: int,
    request: IndicatorConfigUpdateRequest,
    current_user: User = Depends(get_current_active_user),
):
    """更新指标配置

    可以更新配置名称和/或指标列表

    - **config_id**: 配置ID
    """
    user_id = current_user.id

    try:
        from app.core.database import get_mysql_session
        from app.models.indicator_config import IndicatorConfiguration

        session = get_mysql_session()

        try:
            # 查询配置
            config = (
                session.query(IndicatorConfiguration)
                .filter(
                    IndicatorConfiguration.id == config_id,
                    IndicatorConfiguration.user_id == user_id,
                )
                .first()
            )

            if not config:
                raise NotFoundException(resource="配置", identifier=config_id)

            # 更新字段
            if request.name is not None:
                # 检查新名称是否与其他配置冲突
                existing = (
                    session.query(IndicatorConfiguration)
                    .filter(
                        IndicatorConfiguration.user_id == user_id,
                        IndicatorConfiguration.name == request.name,
                        IndicatorConfiguration.id != config_id,
                    )
                    .first()
                )

                if existing:
                    raise BusinessException(
                        detail=f"配置名称已存在: {request.name}",
                        status_code=409,
                        error_code="CONFIG_NAME_EXISTS",
                    )

                config.name = request.name

            if request.indicators is not None:
                indicators_json = [
                    {"abbreviation": ind.abbreviation, "parameters": ind.parameters} for ind in request.indicators
                ]
                config.indicators = indicators_json

            session.commit()
            session.refresh(config)

            logger.info("Updated indicator config", config_id=config_id, user_id=user_id)

            return IndicatorConfigResponse(
                id=config.id,
                user_id=config.user_id,
                name=config.name,
                indicators=config.indicators,
                created_at=config.created_at,
                updated_at=config.updated_at,
                last_used_at=config.last_used_at,
            )

        finally:
            session.close()

    except (BusinessException, ValidationException, NotFoundException, ForbiddenException):
        raise
    except Exception as e:
        logger.error("Failed to update indicator config", exc_info=e)
        raise BusinessException(detail=f"更新配置失败: {e!s}", status_code=500, error_code="CONFIG_UPDATE_FAILED")


@router.delete("/configs/{config_id}", status_code=204)
async def delete_indicator_config(config_id: int, current_user: User = Depends(get_current_active_user)):
    """删除指标配置

    - **config_id**: 配置ID
    """
    user_id = current_user.id

    try:
        from app.core.database import get_mysql_session
        from app.models.indicator_config import IndicatorConfiguration

        session = get_mysql_session()

        try:
            # 查询配置
            config = (
                session.query(IndicatorConfiguration)
                .filter(
                    IndicatorConfiguration.id == config_id,
                    IndicatorConfiguration.user_id == user_id,
                )
                .first()
            )

            if not config:
                raise NotFoundException(resource="配置", identifier=config_id)

            session.delete(config)
            session.commit()

            logger.info("Deleted indicator config", config_id=config_id, user_id=user_id)

            return  # 204 No Content

        finally:
            session.close()

    except (BusinessException, ValidationException, NotFoundException, ForbiddenException):
        raise
    except Exception as e:
        logger.error("Failed to delete indicator config", exc_info=e)
        raise BusinessException(detail=f"删除配置失败: {e!s}", status_code=500, error_code="CONFIG_DELETION_FAILED")
