"""
Indicator Calculation API Endpoints
技术指标计算API路由
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
import numpy as np
import time
import structlog

from app.api.auth import get_current_active_user
from app.core.security import User
from app.schemas.indicator_request import (
    IndicatorCalculateRequest,
    IndicatorConfigCreateRequest,
    IndicatorConfigUpdateRequest,
)
from app.schemas.indicator_response import (
    IndicatorCalculateResponse,
    IndicatorRegistryResponse,
    IndicatorMetadata,
    OHLCVData,
    IndicatorResult,
    IndicatorValueOutput,
    IndicatorConfigResponse,
    IndicatorConfigListResponse,
    APIResponse,
    ErrorDetail,
)
from app.services.indicator_registry import get_indicator_registry, IndicatorCategory
from app.services.indicator_calculator import (
    get_indicator_calculator,
    InsufficientDataError,
    IndicatorCalculationError,
)
from app.services.data_service import (
    get_data_service,
    StockDataNotFoundError,
    InvalidDateRangeError,
)

logger = structlog.get_logger()

router = APIRouter()


@router.get("/registry", response_model=IndicatorRegistryResponse)
async def get_indicator_registry_endpoint():
    """
    获取指标注册表

    返回所有可用的技术指标及其元数据
    """
    try:
        registry = get_indicator_registry()
        all_indicators = registry.get_all_indicators()

        # 统计各分类指标数量
        categories = {}
        for category in IndicatorCategory:
            indicators_in_category = registry.get_indicators_by_category(category)
            categories[category.value] = len(indicators_in_category)

        # 转换为响应格式
        indicators_list = []
        for abbr, meta in all_indicators.items():
            # 确保enum值正确提取
            category_value = (
                meta["category"].value
                if hasattr(meta["category"], "value")
                else str(meta["category"])
            )
            panel_type_value = (
                meta["panel_type"].value
                if hasattr(meta["panel_type"], "value")
                else str(meta["panel_type"])
            )

            indicators_list.append(
                IndicatorMetadata(
                    abbreviation=abbr,
                    full_name=meta["full_name"],
                    chinese_name=meta["chinese_name"],
                    category=category_value,
                    description=meta["description"],
                    panel_type=panel_type_value,
                    parameters=meta.get("parameters", []),
                    outputs=meta["outputs"],
                    reference_lines=meta.get("reference_lines"),
                    min_data_points_formula=meta["min_data_points_formula"],
                )
            )

        return IndicatorRegistryResponse(
            total_count=len(all_indicators),
            categories=categories,
            indicators=indicators_list,
        )

    except Exception as e:
        logger.error("Failed to get indicator registry", exc_info=e)
        raise HTTPException(status_code=500, detail=f"获取指标注册表失败: {str(e)}")


@router.get("/registry/{category}", response_model=List[IndicatorMetadata])
async def get_indicators_by_category(category: str):
    """
    获取指定分类的指标

    - **category**: 指标分类 (trend, momentum, volatility, volume, candlestick)
    """
    try:
        # 验证分类
        try:
            indicator_category = IndicatorCategory(category)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"无效的指标分类: {category}. 有效分类: {[c.value for c in IndicatorCategory]}",
            )

        registry = get_indicator_registry()
        indicators = registry.get_indicators_by_category(indicator_category)

        # 转换为响应格式
        indicators_list = []
        for abbr, meta in indicators.items():
            # 确保enum值正确提取
            category_value = (
                meta["category"].value
                if hasattr(meta["category"], "value")
                else str(meta["category"])
            )
            panel_type_value = (
                meta["panel_type"].value
                if hasattr(meta["panel_type"], "value")
                else str(meta["panel_type"])
            )

            indicators_list.append(
                IndicatorMetadata(
                    abbreviation=abbr,
                    full_name=meta["full_name"],
                    chinese_name=meta["chinese_name"],
                    category=category_value,
                    description=meta["description"],
                    panel_type=panel_type_value,
                    parameters=meta.get("parameters", []),
                    outputs=meta["outputs"],
                    reference_lines=meta.get("reference_lines"),
                    min_data_points_formula=meta["min_data_points_formula"],
                )
            )

        return indicators_list

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get indicators for category {category}", exc_info=e)
        raise HTTPException(status_code=500, detail=f"获取分类指标失败: {str(e)}")


@router.post("/calculate", response_model=IndicatorCalculateResponse)
async def calculate_indicators(request: IndicatorCalculateRequest):
    """
    计算技术指标

    根据股票代码、日期范围和指标列表,计算技术指标值

    **请求示例**:
    ```json
    {
        "symbol": "600519.SH",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "indicators": [
            {"abbreviation": "SMA", "parameters": {"timeperiod": 20}},
            {"abbreviation": "RSI", "parameters": {"timeperiod": 14}}
        ],
        "use_cache": true
    }
    ```
    """
    start_time = time.time()

    try:
        logger.info(
            "Calculating indicators",
            symbol=request.symbol,
            start_date=str(request.start_date),
            end_date=str(request.end_date),
            indicator_count=len(request.indicators),
        )

        # Load OHLCV data from database via DataService
        data_service = get_data_service()

        # Convert date strings to datetime
        from datetime import datetime

        start_dt = datetime.combine(request.start_date, datetime.min.time())
        end_dt = datetime.combine(request.end_date, datetime.min.time())

        # Get OHLCV data
        df, ohlcv_data = data_service.get_daily_ohlcv(
            symbol=request.symbol, start_date=start_dt, end_date=end_dt
        )

        # Get symbol name
        symbol_name = data_service.get_symbol_name(request.symbol)

        # Extract dates from DataFrame
        dates = df["trade_date"].dt.strftime("%Y-%m-%d").tolist()

        # 计算指标
        calculator = get_indicator_calculator()

        # 验证数据质量
        is_valid, error_msg = calculator.validate_data_quality(ohlcv_data)
        if not is_valid:
            raise HTTPException(
                status_code=422, detail=f"OHLCV数据质量验证失败: {error_msg}"
            )

        # 批量计算指标
        indicator_specs = [
            {"abbreviation": ind.abbreviation, "parameters": ind.parameters}
            for ind in request.indicators
        ]

        results = calculator.calculate_multiple_indicators(indicator_specs, ohlcv_data)

        # 转换为响应格式
        indicator_results = []
        for abbr, result in results.items():
            if "error" in result:
                # 计算失败的指标
                indicator_results.append(
                    IndicatorResult(
                        abbreviation=abbr,
                        parameters=result["parameters"],
                        outputs=[],
                        panel_type="overlay",
                        reference_lines=None,
                        error=result["error"],
                    )
                )
            else:
                # 计算成功的指标
                outputs = []
                for output_name, values in result["values"].items():
                    # 将 NumPy 数组转换为 Python list (处理 NaN)
                    values_list = [
                        float(v) if not np.isnan(v) else None for v in values
                    ]

                    outputs.append(
                        IndicatorValueOutput(
                            output_name=output_name,
                            values=values_list,
                            display_name=f"{abbr}({result['parameters'].get('timeperiod', '')})",
                        )
                    )

                indicator_results.append(
                    IndicatorResult(
                        abbreviation=abbr,
                        parameters=result["parameters"],
                        outputs=outputs,
                        panel_type=result["panel_type"],
                        reference_lines=result.get("reference_lines"),
                        error=None,
                    )
                )

        # 计算耗时
        calculation_time_ms = (time.time() - start_time) * 1000

        return IndicatorCalculateResponse(
            symbol=request.symbol,
            symbol_name=symbol_name,
            start_date=str(request.start_date),
            end_date=str(request.end_date),
            ohlcv=OHLCVData(
                dates=dates,
                open=ohlcv_data["open"].tolist(),
                high=ohlcv_data["high"].tolist(),
                low=ohlcv_data["low"].tolist(),
                close=ohlcv_data["close"].tolist(),
                volume=ohlcv_data["volume"].tolist(),
                turnover=df["amount"].tolist() if "amount" in df.columns else [],
            ),
            indicators=indicator_results,
            calculation_time_ms=round(calculation_time_ms, 2),
            cached=request.use_cache if hasattr(request, "use_cache") else False,
        )

    except InvalidDateRangeError as e:
        logger.warning("Invalid date range", error=str(e))
        raise HTTPException(
            status_code=422,
            detail={"error_code": "INVALID_DATE_RANGE", "error_message": str(e)},
        )

    except StockDataNotFoundError as e:
        logger.warning("Stock data not found", error=str(e))
        raise HTTPException(
            status_code=404,
            detail={"error_code": "STOCK_DATA_NOT_FOUND", "error_message": str(e)},
        )

    except InsufficientDataError as e:
        logger.warning("Insufficient data for indicator calculation", error=str(e))
        raise HTTPException(
            status_code=422,
            detail={"error_code": "INSUFFICIENT_DATA", "error_message": str(e)},
        )

    except IndicatorCalculationError as e:
        logger.error("Indicator calculation error", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={"error_code": "CALCULATION_ERROR", "error_message": str(e)},
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error("Unexpected error in calculate_indicators", exc_info=e)
        raise HTTPException(status_code=500, detail=f"计算指标时发生错误: {str(e)}")


@router.post("/configs", response_model=IndicatorConfigResponse)
async def create_indicator_config(
    request: IndicatorConfigCreateRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    创建指标配置

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
        from datetime import datetime

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
                raise HTTPException(
                    status_code=409, detail=f"配置名称已存在: {request.name}"
                )

            # 创建新配置
            indicators_json = [
                {"abbreviation": ind.abbreviation, "parameters": ind.parameters}
                for ind in request.indicators
            ]

            new_config = IndicatorConfiguration(
                user_id=user_id, name=request.name, indicators=indicators_json
            )

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

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create indicator config", exc_info=e)
        raise HTTPException(status_code=500, detail=f"创建配置失败: {str(e)}")


@router.get("/configs", response_model=IndicatorConfigListResponse)
async def list_indicator_configs(current_user: User = Depends(get_current_active_user)):
    """
    获取用户的指标配置列表

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

            logger.info(
                "Listed indicator configs", user_id=user_id, count=len(config_list)
            )

            return IndicatorConfigListResponse(
                total_count=len(config_list), configs=config_list
            )

        finally:
            session.close()

    except Exception as e:
        logger.error("Failed to list indicator configs", exc_info=e)
        raise HTTPException(status_code=500, detail=f"获取配置列表失败: {str(e)}")


@router.get("/configs/{config_id}", response_model=IndicatorConfigResponse)
async def get_indicator_config(
    config_id: int, current_user: User = Depends(get_current_active_user)
):
    """
    获取指定的指标配置详情

    - **config_id**: 配置ID
    """
    user_id = current_user.id

    try:
        from app.core.database import get_mysql_session
        from app.models.indicator_config import IndicatorConfiguration
        from datetime import datetime

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
                raise HTTPException(
                    status_code=404, detail=f"配置不存在: ID={config_id}"
                )

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

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get indicator config", exc_info=e)
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")


@router.put("/configs/{config_id}", response_model=IndicatorConfigResponse)
async def update_indicator_config(
    config_id: int,
    request: IndicatorConfigUpdateRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    更新指标配置

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
                raise HTTPException(
                    status_code=404, detail=f"配置不存在: ID={config_id}"
                )

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
                    raise HTTPException(
                        status_code=409, detail=f"配置名称已存在: {request.name}"
                    )

                config.name = request.name

            if request.indicators is not None:
                indicators_json = [
                    {"abbreviation": ind.abbreviation, "parameters": ind.parameters}
                    for ind in request.indicators
                ]
                config.indicators = indicators_json

            session.commit()
            session.refresh(config)

            logger.info(
                "Updated indicator config", config_id=config_id, user_id=user_id
            )

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

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update indicator config", exc_info=e)
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")


@router.delete("/configs/{config_id}", status_code=204)
async def delete_indicator_config(
    config_id: int, current_user: User = Depends(get_current_active_user)
):
    """
    删除指标配置

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
                raise HTTPException(
                    status_code=404, detail=f"配置不存在: ID={config_id}"
                )

            session.delete(config)
            session.commit()

            logger.info(
                "Deleted indicator config", config_id=config_id, user_id=user_id
            )

            return None  # 204 No Content

        finally:
            session.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete indicator config", exc_info=e)
        raise HTTPException(status_code=500, detail=f"删除配置失败: {str(e)}")
